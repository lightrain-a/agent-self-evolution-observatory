from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef, canonical_sha256


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    # Provider response identifiers are never required for a public failure receipt.
    import re

    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", text)
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:2000]


def _load_ref(path: Path) -> TrajectoryRef:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ref = TrajectoryRef(**payload)
    ref.validate()
    trajectory = Path(ref.trajectory_path)
    if not trajectory.exists() or file_sha256(trajectory) != ref.trajectory_sha256:
        raise RuntimeError(f"stored trajectory receipt failed content-address check: {path}")
    return ref


def _quarantine_partial(workdir: Path) -> Path | None:
    if not workdir.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = workdir.with_name(f"{workdir.name}.incomplete-{stamp}")
    suffix = 0
    while candidate.exists():
        suffix += 1
        candidate = workdir.with_name(f"{workdir.name}.incomplete-{stamp}-{suffix}")
    workdir.rename(candidate)
    return candidate


@dataclass(frozen=True)
class ActorRolloutConfig:
    requested_model: str
    required_resolved_model: str
    max_turns: int
    skill_source: str
    skill_pre_sha256: str
    failure_family: str | None
    experiment_mode: str
    contract_sha256: str | None = None
    authorization_sha256: str | None = None


async def run_actor_rollout(
    *,
    env: Any,
    case: Any,
    rollout_index: int,
    agent_factory: Any,
    adapter: Any,
    config: ActorRolloutConfig,
    evaluator_sources: Sequence[Path],
) -> TrajectoryRef:
    """Run or resume one content-addressed SpreadsheetBench actor rollout."""

    workdir = Path(env.case_workdir(case, rollout_index))
    ref_path = workdir / "r17_trajectory_ref.json"
    raw_path = workdir / "r17_trajectory.json"
    if ref_path.exists():
        ref = _load_ref(ref_path)
        ledger = getattr(adapter, "provider_budget_ledger", None)
        unit_id = getattr(adapter, "provider_budget_unit_id", None)
        if ref.provider_budget_claim_count:
            if ledger is None or not unit_id:
                raise RuntimeError("budgeted trajectory ref cannot be reused without its bound provider budget ledger")
            if ref.provider_budget_unit_id != str(unit_id):
                raise RuntimeError("budgeted trajectory ref unit id drift on resume")
            snapshot = ledger.snapshot()
            observed = int(snapshot.unit_claimed.get(str(unit_id), 0))
            if observed != int(ref.provider_budget_unit_claimed_after or -1):
                raise RuntimeError(
                    f"provider budget ledger/ref drift on resume: unit={unit_id}; "
                    f"ledger={observed}; ref={ref.provider_budget_unit_claimed_after}"
                )
            if snapshot.total_claimed < int(ref.provider_budget_total_claimed_after or -1):
                raise RuntimeError("provider budget total counter regressed below completed trajectory ref")
        return ref
    quarantined = _quarantine_partial(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    env.setup_case(case, workdir)
    input_path = workdir / env.input_name
    messages = env.build_messages(case)
    prompt_sha = canonical_sha256(
        {
            "system_prompt": env.system_prompt(),
            "messages": messages,
            "skill_pre_sha256": config.skill_pre_sha256,
            "max_turns": config.max_turns,
            "requested_model": config.requested_model,
            "required_resolved_model": config.required_resolved_model,
        }
    )
    golden = env._workbook(case.data["src_dir"], "golden")
    verifier_sha = canonical_sha256(
        {
            "evaluator_source_sha256": {str(path): file_sha256(path) for path in evaluator_sources},
            "golden_workbook_sha256": file_sha256(golden),
            "answer_position": env.answer_position(case),
        }
    )
    started_at = time.time()
    technical_error: str | None = None
    try:
        agent, _ = agent_factory.build(workdir, env.system_prompt())
        agent_result = await agent.run(messages)
        score, score_message = env.score(case, workdir)
    except Exception as exc:  # noqa: BLE001 - persist exact failed unit for resume
        technical_error = _safe_error(exc)
        failure = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-actor-rollout-technical-failure",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "case_id": case.id,
            "rollout_index": rollout_index,
            "workdir": str(workdir),
            "error": technical_error,
            "quarantined_previous_partial": str(quarantined) if quarantined else None,
            "adapter_receipts": adapter.public_receipts(),
            "provider_budget_claims": adapter.public_budget_claims() if hasattr(adapter, "public_budget_claims") else [],
            "provider_retry_limit": 0,
            "scientific_outcome": False,
        }
        atomic_json(workdir / "r17_technical_failure.json", failure)
        raise RuntimeError(technical_error) from exc

    ended_at = time.time()
    output_path = workdir / env.output_name
    output_sha = file_sha256(output_path) if output_path.exists() else None
    receipts = adapter.public_receipts()
    if not receipts:
        raise RuntimeError("actor rollout completed without provider receipts")
    budget_claims = adapter.public_budget_claims() if hasattr(adapter, "public_budget_claims") else []
    if getattr(adapter, "provider_budget_ledger", None) is not None and len(budget_claims) != len(receipts):
        raise RuntimeError("successful budgeted rollout must bind exactly one pre-I/O budget claim per provider receipt")
    observed = {str(row.get("resolved_model") or "") for row in receipts}
    if observed != {config.required_resolved_model}:
        raise RuntimeError(f"actor rollout contains resolved-model drift: {sorted(observed)}")
    raw_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-rollout",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "case_id": case.id,
        "split": case.split,
        "rollout_index": rollout_index,
        "score": float(score),
        "score_message": score_message,
        "finished": bool(agent_result.finished),
        "turns": int(agent_result.turns),
        "messages": agent_result.messages,
        "workdir": str(workdir),
        "input_sha256": file_sha256(input_path),
        "output_sha256": output_sha,
        "prompt_sha256": prompt_sha,
        "skill_source": config.skill_source,
        "skill_pre_sha256": config.skill_pre_sha256,
        "verifier_sha256": verifier_sha,
        "requested_model": config.requested_model,
        "resolved_model": config.required_resolved_model,
        "adapter_receipts": receipts,
        "adapter_receipt_bundle_sha256": adapter.receipt_bundle_sha256,
        "provider_budget_claims": budget_claims,
        "provider_budget_claim_bundle_sha256": canonical_sha256(budget_claims) if budget_claims else None,
        "provider_retry_limit": 0,
        "hidden_provider_retry_used": False,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": ended_at - started_at,
        "failure_family": config.failure_family if float(score) < 1.0 else None,
        "experiment_mode": config.experiment_mode,
        "contract_sha256": config.contract_sha256,
        "authorization_sha256": config.authorization_sha256,
        "quarantined_previous_partial": str(quarantined) if quarantined else None,
    }
    atomic_json(raw_path, raw_payload)
    provider_call_id_sha = canonical_sha256([row["response_id_sha256"] for row in receipts])
    ref = TrajectoryRef(
        task_id=str(case.id),
        rollout_index=rollout_index,
        score=float(score),
        trajectory_path=str(raw_path.resolve()),
        trajectory_sha256=file_sha256(raw_path),
        input_sha256=file_sha256(input_path),
        prompt_sha256=prompt_sha,
        skill_pre_sha256=config.skill_pre_sha256,
        verifier_sha256=verifier_sha,
        requested_model=config.requested_model,
        resolved_model=config.required_resolved_model,
        provider_call_id_sha256=provider_call_id_sha,
        evidence_tokens=sum(int(row.get("total_tokens") or 0) for row in receipts),
        technical_status="COMPLETED",
        failure_code=config.failure_family if float(score) < 1.0 else None,
        provider_budget_unit_id=(str(budget_claims[-1]["unit_id"]) if budget_claims else None),
        provider_budget_claim_count=len(budget_claims),
        provider_budget_claim_bundle_sha256=(canonical_sha256(budget_claims) if budget_claims else None),
        provider_budget_unit_claimed_after=(int(budget_claims[-1]["unit_call_index"]) if budget_claims else None),
        provider_budget_total_claimed_after=(int(budget_claims[-1]["total_claimed_after"]) if budget_claims else None),
    )
    ref.validate()
    atomic_json(ref_path, asdict(ref))
    return ref


def freeze_nested_pools(
    *,
    task_dir: Path,
    trajectories: Sequence[TrajectoryRef],
    prefix_ks: Sequence[int] = (1, 2, 4, 8),
) -> dict[int, SearchPool]:
    ordered = tuple(sorted(trajectories, key=lambda row: row.rollout_index))
    if [row.rollout_index for row in ordered] != list(range(len(ordered))):
        raise ValueError("nested pool trajectories must be exactly indexed 0..K-1")
    pools: dict[int, SearchPool] = {}
    for k in sorted(set(int(value) for value in prefix_ks)):
        if k < 1 or k > len(ordered):
            continue
        pool = SearchPool.freeze(ordered[:k])
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-frozen-search-pool",
            "pool_id": pool.pool_id,
            "task_id": pool.task_id,
            "k": pool.k,
            "search_topology": pool.search_topology,
            "acting_winner_index": pool.winner.rollout_index,
            "acting_success": pool.acting_success,
            "precommitted_success": pool.precommitted_success,
            "rescue_event": pool.rescue_event,
            "trajectories": [asdict(row) for row in pool.trajectories],
        }
        atomic_json(task_dir / f"pool_k{k}.json", payload)
        pools[k] = pool
    return pools


def load_frozen_pool(path: Path) -> SearchPool:
    payload = json.loads(path.read_text(encoding="utf-8"))
    trajectories = tuple(TrajectoryRef(**row) for row in payload["trajectories"])
    pool = SearchPool(
        pool_id=payload["pool_id"],
        task_id=payload["task_id"],
        k=int(payload["k"]),
        trajectories=trajectories,
        search_topology=payload.get("search_topology", "parallel_best_of_k"),
    )
    pool.validate()
    return pool


__all__ = [
    "ActorRolloutConfig",
    "atomic_json",
    "file_sha256",
    "freeze_nested_pools",
    "load_frozen_pool",
    "run_actor_rollout",
]
