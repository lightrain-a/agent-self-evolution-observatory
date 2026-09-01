#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_evidence_window_v2 import (
    ExactMatchedEvidenceBlockRenderer,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import BlindedEvidenceUnit, run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    project,
    project_stream,
    validate_mixed_cloned_pair,
)

PILOT_STREAM_ID = "v31-provider-runtime-pilot"
ARMS = ("win_a", "win_b", "mrw")
FORBIDDEN_VISIBLE_MARKERS = (
    "PROJECTION:",
    "ROLE:",
    "SOURCE_ROLLOUT_INDEX:",
    "SOURCE_TRAJECTORY_SHA256:",
    "ACTING_WINNER_INDEX:",
    "POOL_ID:",
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_sha(payload: Any) -> str:
    return sha_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_PROVIDER_RUNTIME_PILOT", "pilot contract not frozen")
    require(auth.get("status") == "AUTHORIZED_PROVIDER_RUNTIME_PILOT", "pilot authorization status invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract SHA mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("provider_runtime_pilot") is True, "provider runtime pilot authority absent")
    require(authority.get("scientific_experiment") is False, "runtime pilot cannot have scientific-effect authority")
    require(authority.get("e1_b") is False, "runtime pilot cannot authorize E1-B")
    require(authority.get("paper_promotion") is False, "runtime pilot cannot authorize paper promotion")
    scope = auth.get("execution_scope") or {}
    require(scope.get("arms") == list(ARMS), "runtime pilot arm scope drift")
    require(scope.get("heldout_evaluation") is False, "runtime pilot must forbid held-out evaluation")
    require(scope.get("max_provider_calls") == int(contract["budget"]["max_provider_calls"]), "runtime pilot budget drift")
    require(scope.get("max_provider_calls_per_arm") == int(contract["budget"]["max_provider_calls_per_arm"]), "per-arm budget drift")
    runtime = contract["runtime"]
    require(scope.get("runtime_python_executable") == runtime["python_executable"], "runtime python authorization drift")
    require(scope.get("runtime_freeze_sha256") == runtime["freeze_sha256"], "runtime freeze authorization drift")
    return contract, auth


def validate_updater_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    runtime = contract["runtime"]
    venv = Path(runtime["venv_root"])
    runtime_python = Path(runtime["python_executable"])
    freeze_path = Path(runtime["freeze_path"])
    require(venv.is_dir(), "updater runtime venv missing")
    require(runtime_python.is_file(), "updater runtime python missing")
    require(runtime_python == venv / "bin/python", "updater runtime python is not exact venv/bin/python")
    require(freeze_path.is_file(), "updater runtime freeze missing")
    require(sha_file(freeze_path) == runtime["freeze_sha256"], "updater runtime freeze SHA drift")

    qualification_path = ROOT / runtime["qualification_path"]
    require(qualification_path.is_file(), "updater runtime qualification missing")
    require(sha_file(qualification_path) == runtime["qualification_sha256"], "updater runtime qualification SHA drift")
    qualification = load_json(qualification_path)
    require(qualification.get("status") == runtime["required_status"], "updater runtime qualification status drift")
    qualified_runtime = qualification.get("runtime") or {}
    require(qualified_runtime.get("venv_root") == str(venv), "updater runtime qualification venv drift")
    require(qualified_runtime.get("python_executable") == str(runtime_python), "updater runtime qualification python drift")
    require(qualified_runtime.get("freeze_sha256") == runtime["freeze_sha256"], "updater runtime qualification freeze drift")
    override = qualification.get("post_lock_compatibility_override") or {}
    require(override.get("present") is True, "updater runtime compatibility override declaration missing")
    require(override.get("package") == "tiktoken", "unexpected updater runtime compatibility override")
    require(override.get("qualified_runtime_version") == "0.11.0", "updater runtime tokenizer override drift")

    mind_root = Path(contract["mindmemos"]["root"])
    smoke = (
        "import sys, importlib.metadata; "
        f"root={str(mind_root)!r}; "
        "[sys.path.insert(0, root+'/'+p) for p in ['src/mindmemos','src/mindmemos_sdk','src/mindmemos_eval']]; "
        "from mindmemos.pipelines.skill.evolution import SkillEvolver; "
        "from qdrant_client import AsyncQdrantClient; "
        "import omegaconf, tiktoken; "
        "assert importlib.metadata.version('tiktoken') == '0.11.0'; "
        "print('UPDATER_RUNTIME_SMOKE_PASS')"
    )
    runtime_env = os.environ.copy()
    runtime_env["VIRTUAL_ENV"] = str(venv)
    runtime_env["PATH"] = str(venv / "bin") + os.pathsep + runtime_env.get("PATH", "")
    runtime_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    checked = subprocess.run(
        [str(runtime_python), "-c", smoke],
        cwd=ROOT,
        env=runtime_env,
        capture_output=True,
        text=True,
        check=False,
    )
    require(checked.returncode == 0 and "UPDATER_RUNTIME_SMOKE_PASS" in checked.stdout, "dedicated updater runtime entrypoint smoke failed")
    return runtime_python, runtime_env


def bind_mindmemos(root: Path) -> None:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    for source in reversed([root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))


def load_selected_pools(contract: dict[str, Any]) -> list[SearchPool]:
    rows = contract["historical_inputs"]["selected_pools"]
    require(len(rows) == 8, "runtime pilot must bind exactly eight pools")
    pools: list[SearchPool] = []
    for row in rows:
        path = Path(row["path"])
        require(path.is_file(), f"historical pool missing: {path}")
        require(sha_file(path) == row["sha256"], f"historical pool SHA drift: {path}")
        pool = load_frozen_pool(path)
        require(pool.task_id == row["task_id"], "historical pool task binding drift")
        pools.append(pool)
    require([pool.task_id for pool in pools] == [row["task_id"] for row in rows], "historical pilot pool order drift")
    return pools


def evidence_units(
    pools: list[SearchPool],
    *,
    final_block_cap_tokens: int,
    transcript_max_chars: int,
) -> tuple[list[BlindedEvidenceUnit], list[BlindedEvidenceUnit], list[dict[str, Any]]]:
    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=final_block_cap_tokens)
    wins: list[BlindedEvidenceUnit] = []
    mrws: list[BlindedEvidenceUnit] = []
    receipts: list[dict[str, Any]] = []
    for pool in pools:
        win_packet = project(pool, ProjectionName.WINNER_ONLY)
        mrw_packet = project(pool, ProjectionName.MIXED_REJECTED_WITNESS)
        validate_mixed_cloned_pair(pool, win_packet, mrw_packet)
        by_index = {row.rollout_index: row for row in pool.trajectories}
        win_index = win_packet.slots[0].rollout_index
        mrw_index = mrw_packet.slots[0].rollout_index
        win_ref = by_index[win_index]
        mrw_ref = by_index[mrw_index]
        win_payload = load_json(Path(win_ref.trajectory_path))
        mrw_payload = load_json(Path(mrw_ref.trajectory_path))
        require(sha_file(Path(win_ref.trajectory_path)) == win_ref.trajectory_sha256, "WIN trajectory SHA drift")
        require(sha_file(Path(mrw_ref.trajectory_path)) == mrw_ref.trajectory_sha256, "MRW trajectory SHA drift")
        win_text = canonical_trajectory_text(win_payload)
        mrw_text = canonical_trajectory_text(mrw_payload)
        win_block, mrw_block, matched = renderer.render_pair(win_text, mrw_text)
        win_tokens = len(renderer.encoding.encode(win_block))
        mrw_tokens = len(renderer.encoding.encode(mrw_block))
        require(win_tokens == mrw_tokens == matched.matched_final_block_tokens, "provider-visible token parity failed")
        require(len(f"[user] {win_block}") <= transcript_max_chars, "WIN evidence would be downstream-truncated")
        require(len(f"[user] {mrw_block}") <= transcript_max_chars, "MRW evidence would be downstream-truncated")
        for visible in (win_block, mrw_block):
            for marker in FORBIDDEN_VISIBLE_MARKERS:
                require(marker not in visible, f"arm/provenance marker leaked into model-visible evidence: {marker}")
        if not pool.mixed_pool:
            require(win_block == mrw_block, "nonmixed WIN/MRW evidence must be byte-identical")
        wins.append(
            BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=win_index,
                source_trajectory_sha256=win_ref.trajectory_sha256,
                source_score=float(win_ref.score),
                evidence_text=win_block,
                evidence_sha256=sha_text(win_block),
                evidence_tokens=win_tokens,
            )
        )
        mrws.append(
            BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=mrw_index,
                source_trajectory_sha256=mrw_ref.trajectory_sha256,
                source_score=float(mrw_ref.score),
                evidence_text=mrw_block,
                evidence_sha256=sha_text(mrw_block),
                evidence_tokens=mrw_tokens,
            )
        )
        receipts.append(
            {
                "task_id": pool.task_id,
                "pool_id": pool.pool_id,
                "mixed_pool": pool.mixed_pool,
                "win_source_index": win_index,
                "mrw_source_index": mrw_index,
                "win_evidence_sha256": sha_text(win_block),
                "mrw_evidence_sha256": sha_text(mrw_block),
                "matched_final_tokens": win_tokens,
                "matched_window": matched.to_dict(),
            }
        )
    return wins, mrws, receipts


def completed_manifest(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["arm"])] = row
    return rows


def verify_completed(row: dict[str, Any], *, contract_sha: str, auth_sha: str) -> None:
    receipt_path = Path(row["update_receipt_path"])
    skill_path = Path(row["skill_post_path"])
    require(receipt_path.is_file() and skill_path.is_file(), f"completed arm artifact missing: {row['arm']}")
    require(sha_file(receipt_path) == row["update_receipt_sha256"], f"completed receipt SHA drift: {row['arm']}")
    require(sha_file(skill_path) == row["skill_post_sha256"], f"completed skill SHA drift: {row['arm']}")
    receipt = load_json(receipt_path)
    require(receipt.get("contract_sha256") == contract_sha, f"completed arm contract drift: {row['arm']}")
    require(receipt.get("authorization_sha256") == auth_sha, f"completed arm authorization drift: {row['arm']}")
    require(receipt.get("causal_purity_mode") == "arm_blinded_selected_evidence", f"completed arm not V3.1 blinded: {row['arm']}")
    require(receipt.get("arm_metadata_visible_in_transcript") is False, f"arm metadata visible: {row['arm']}")


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_auth(args.contract, args.authorization)
    runtime_python, runtime_env = validate_updater_runtime(contract)
    require(Path(sys.executable) == runtime_python, "provider runtime pilot must itself run under contract venv python")
    os.environ.update({"VIRTUAL_ENV": runtime_env["VIRTUAL_ENV"], "PATH": runtime_env["PATH"]})

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file(), f"bound code missing: {label}")
        require(sha_file(path) == item["sha256"], f"bound code SHA drift: {label}")

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.check_output(["git", "-C", str(mind_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    require(not subprocess.check_output(["git", "-C", str(mind_root), "status", "--short"], text=True).strip(), "MindMemOS checkout dirty")
    bind_mindmemos(mind_root)

    identity_path = ROOT / contract["model_identity"]["path"]
    require(sha_file(identity_path) == contract["model_identity"]["sha256"], "pilot model identity SHA drift")
    identity = load_json(identity_path)
    require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "pilot model identity not current-pass")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]
    requested = str(model_row["requested"])
    resolved = str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"], "pilot updater resolved-model drift")

    pools = load_selected_pools(contract)
    initial_skill_path = mind_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    require(sha_file(initial_skill_path) == contract["initial_skill"]["sha256"], "initial skill SHA drift")
    initial_skill = initial_skill_path.read_text(encoding="utf-8")
    initial_sha = sha_file(initial_skill_path)

    win_units, mrw_units, evidence_receipts = evidence_units(
        pools,
        final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),
        transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
    )
    win_unit_bundle_sha = canonical_sha([unit.__dict__ for unit in win_units])
    require(win_unit_bundle_sha == canonical_sha([unit.__dict__ for unit in win_units]), "WIN-A/WIN-B evidence bundle instability")

    win_stream = project_stream(
        stream_id=PILOT_STREAM_ID,
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.WINNER_ONLY,
    )
    mrw_stream = project_stream(
        stream_id=PILOT_STREAM_ID,
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.MIXED_REJECTED_WITNESS,
    )

    load_env_file(args.env_file)
    raw = ArkSettings.from_env(required=True)
    require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "pilot refuses non-Ark-Plan route")
    settings = ArkSettings(
        api_key=raw.api_key,
        base_url=raw.base_url,
        default_model=raw.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )

    run_root = Path(contract["run_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    lock_path = run_root / ".exclusive.lock"
    lock_handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("provider runtime pilot exclusive lock already held; inspect state before any resume") from exc
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(json.dumps({"pid": os.getpid(), "contract_sha256": sha_file(args.contract), "authorization_sha256": sha_file(args.authorization), "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}, sort_keys=True))
    lock_handle.flush()
    os.fsync(lock_handle.fileno())

    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)
    ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["budget"]["max_provider_calls_per_arm"]),
        allow_create=not ledger_path.exists(),
    )
    manifest_path = run_root / "checkpoints/completed_arms.jsonl"
    completed = completed_manifest(manifest_path)
    for row in completed.values():
        verify_completed(row, contract_sha=contract_sha, auth_sha=auth_sha)

    arms = {
        "win_a": (win_stream, win_units),
        "win_b": (win_stream, win_units),
        "mrw": (mrw_stream, mrw_units),
    }
    rows: list[dict[str, Any]] = []
    run_success = False
    try:
        for arm in ARMS:
            if arm in completed:
                rows.append(completed[arm])
                continue
            stream, units = arms[arm]
            arm_dir = run_root / "arms" / arm
            if arm_dir.exists() and any(arm_dir.rglob("*")):
                raise RuntimeError(f"partial ambiguous arm exists without completed manifest: {arm}; do not auto-rerun")
            adapter = MindMemOSArkPlanChatAdapter(
                settings=settings,
                requested_model=requested,
                required_resolved_model=resolved,
                max_parse_attempts=int(contract["updater"]["max_parse_attempts"]),
                record_dir=arm_dir / "provider_calls",
                provider_budget_ledger=ledger,
                provider_budget_unit_id=f"{PILOT_STREAM_ID}/{arm}",
            )
            result = await run_projection_update(
                stream=stream,
                pools=pools,
                initial_skill_md=initial_skill,
                run_dir=arm_dir,
                llm_adapter=adapter,
                mindmemos_commit=head,
                contract_sha256=contract_sha,
                authorization_sha256=auth_sha,
                transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
                blinded_evidence_units=units,
            )
            receipts = adapter.public_receipts()
            claims = adapter.public_budget_claims()
            require(len(receipts) == len(claims) == result.provider_calls, f"provider claim/receipt mismatch: {arm}")
            require(all(row["provider_retry_limit"] == 0 for row in receipts), f"hidden retry limit drift: {arm}")
            require(all(float(row["temperature_requested"]) == 0.0 for row in receipts), f"temperature drift: {arm}")
            require(all((row["thinking_requested"] or "disabled") == "disabled" for row in receipts), f"thinking drift: {arm}")
            row = {
                "arm": arm,
                "status": "COMPLETED",
                "update_receipt_path": result.update_receipt_path,
                "update_receipt_sha256": result.update_receipt_sha256,
                "skill_post_path": result.skill_post_path,
                "skill_post_sha256": result.skill_post_sha256,
                "provider_calls": result.provider_calls,
                "provider_total_tokens": result.provider_total_tokens,
                "parse_error_calls": sum(int(bool(item.get("parse_error"))) for item in receipts),
                "wall_time_seconds_sum": sum(float(item.get("wall_time_seconds") or 0.0) for item in receipts),
                "prompt_sha256": [item["prompt_sha256"] for item in receipts],
                "budget_claim_count": len(claims),
                "budget_claim_bundle_sha256": canonical_sha(claims),
            }
            verify_completed(row, contract_sha=contract_sha, auth_sha=auth_sha)
            append_jsonl(manifest_path, row)
            completed[arm] = row
            rows.append(row)

        require(set(completed) == set(ARMS), "runtime pilot did not complete all three arms")
        win_a = completed["win_a"]
        win_b = completed["win_b"]
        # The initial evidence treatment is exactly identical. Hosted stochasticity may
        # make later prompts differ, so only evidence bundle identity is a hard pre-call invariant.
        budget_snapshot = ledger.snapshot()
        require(budget_snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]), "runtime pilot provider budget exceeded")
        summary = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-v31-provider-runtime-pilot-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "PASS_RUNTIME_MEASURABILITY",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "historical_only": True,
            "scientific_effectiveness_evaluated": False,
            "heldout_evaluation_calls": 0,
            "new_actor_rollouts": 0,
            "updater_arms": list(ARMS),
            "win_a_win_b_pre_provider_evidence_byte_identical": True,
            "win_evidence_bundle_sha256": win_unit_bundle_sha,
            "evidence_receipts": evidence_receipts,
            "arms": [completed[arm] for arm in ARMS],
            "provider_budget": budget_snapshot.to_dict(),
            "total_provider_calls": sum(int(completed[arm]["provider_calls"]) for arm in ARMS),
            "total_provider_tokens": sum(int(completed[arm]["provider_total_tokens"]) for arm in ARMS),
            "total_parse_error_calls": sum(int(completed[arm]["parse_error_calls"]) for arm in ARMS),
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "model_identity_sha256": contract["model_identity"]["sha256"],
            "authority": {"execute_e1_b": False, "paper_promotion": False, "submission": False},
        }
        summary_path = run_root / "summary/provider_runtime_pilot_summary.json"
        atomic_json(summary_path, summary)
        run_success = True
        return summary
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
        if run_success:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()
    payload = asyncio.run(main_async(args))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_RUNTIME_MEASURABILITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
