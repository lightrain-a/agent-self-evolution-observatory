#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
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

from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_evidence_window import MatchedEvidenceWindowRenderer
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_reasoningbank_style import render_rb_style_aggregation_prompt
from research_pipeline.e2_r17_rbagg_mindmemos_updater import run_rbagg_update
from research_pipeline.e2_r17_rbagg_posthold import (
    build_rb_aggregated_session_evidence,
    normalize_rb_memory_items,
    parse_rb_memory_items,
)
from research_pipeline.ark_provider import ArkSettings

CONTRACT_STATUS = "FROZEN_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT"
AUTH_STATUS = "AUTHORIZED_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT_EXACTLY_ONCE"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def acquire_lock(run_root: Path, *, contract_sha: str, authorization_sha: str) -> Path:
    run_root.mkdir(parents=True, exist_ok=False)
    lock = run_root / ".exclusive.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schema_version": "1.0",
                "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-exclusive-lock",
                "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "pid": os.getpid(),
                "pgid": os.getpgrp(),
                "contract_sha256": contract_sha,
                "authorization_sha256": authorization_sha,
            },
            handle,
            sort_keys=True,
        )
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return lock


def resolve_bound_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def validate_contract(contract_path: Path, authorization_path: Path) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    contract = load_json(contract_path)
    auth = load_json(authorization_path)
    contract_sha = sha_file(contract_path)
    auth_sha = sha_file(authorization_path)
    require(contract.get("status") == CONTRACT_STATUS, "RB semantic-pilot contract status drift")
    require(auth.get("status") == AUTH_STATUS, "RB semantic-pilot authorization status drift")
    require(auth.get("contract_sha256") == contract_sha, "RB semantic-pilot authorization contract drift")
    require(auth.get("single_use") is True, "RB semantic-pilot authorization is not single-use")
    require(auth.get("runner_sha256") == sha_file(Path(__file__)), "RB semantic-pilot authorization runner drift")
    preflight_path = resolve_bound_path(str(contract["preflight_path"]))
    require(preflight_path.is_file(), "RB semantic-pilot preflight artifact missing")
    require(auth.get("preflight_sha256") == sha_file(preflight_path), "RB semantic-pilot preflight binding drift")
    require(all(value is False for value in (contract.get("authority") or {}).values()), "semantic-pilot contract must retain zero execution authority")
    authority = auth.get("authority") or {}
    require(authority.get("semantic_provider_pilot") is True and authority.get("provider_io") is True, "semantic-pilot provider authority missing")
    for key in ("heldout_evaluation", "rbagg_full_diagnostic", "scientific_effectiveness_inference", "paper_promotion", "public_benchmark", "second_backbone"): 
        require(authority.get(key) is False, f"semantic-pilot authorization overbroad: {key}")
    require(contract.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent HOLD drift")
    require(contract.get("parent_status_changed") is False, "contract attempts to change parent result")
    require(contract.get("pilot", {}).get("fixed_stream") == "e1-agj-00", "pilot stream drift")
    require(int(contract.get("provider_budget", {}).get("total_limit", -1)) == 11, "pilot total provider budget drift")
    require(int(contract.get("provider_budget", {}).get("per_unit_limit", -1)) == 11, "pilot unit provider budget drift")
    require(int(contract.get("pilot", {}).get("heldout_evaluations", -1)) == 0, "pilot heldout must be zero")
    require(contract.get("exactly_once", {}).get("authorized_runs") == 1, "pilot exactly-once run count drift")
    require(contract.get("exactly_once", {}).get("automatic_retry") is False, "pilot automatic retry must be false")
    require(contract.get("exactly_once", {}).get("pilot_skill_scientific_inclusion") is False, "pilot skill must remain quarantined")

    for label, binding in (contract.get("bound_files") or {}).items():
        path = resolve_bound_path(str(binding["path"]))
        require(path.is_file(), f"missing bound file before semantic pilot: {label}: {path}")
        require(sha_file(path) == str(binding["sha256"]), f"bound file SHA drift before semantic pilot: {label}")

    review = load_json(resolve_bound_path(contract["inputs"]["review_adjudication_path"]))
    require(review.get("status") == "PASS_DUAL_REVIEW_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_PROPOSAL_ONLY", "RB review adjudication not passing")
    require(review.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "review parent status drift")
    require(review.get("authority", {}).get("provider_io") is False, "review artifact unexpectedly self-authorizes provider I/O")

    return contract, auth, contract_sha, auth_sha


async def run(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth, contract_sha, auth_sha = validate_contract(args.contract, args.authorization)
    run_root = Path(contract["run_root"])
    require(not run_root.exists(), "semantic-pilot run root already exists; exactly-once execution forbids replay")

    env_file = Path(contract["env_file"])
    load_env_file(env_file)
    raw_settings = ArkSettings.from_env(required=True)
    settings = ArkSettings(
        api_key=raw_settings.api_key,
        base_url=raw_settings.base_url,
        default_model=raw_settings.default_model,
        timeout_seconds=max(180.0, raw_settings.timeout_seconds),
        max_retries=0,
    )
    require(settings.base_url.rstrip("/") == contract["model"]["route"], "Ark route drift")

    support_path = resolve_bound_path(contract["inputs"]["pool_support_path"])
    split_path = resolve_bound_path(contract["inputs"]["split_manifest_path"])
    parent_contract_path = resolve_bound_path(contract["inputs"]["parent_repair2_contract_path"])
    support = load_json(support_path)
    split = load_json(split_path)
    parent_contract = load_json(parent_contract_path)
    require(sha_file(support_path) == contract["inputs"]["pool_support_sha256"], "pool support SHA drift")
    require(sha_file(split_path) == contract["inputs"]["split_manifest_sha256"], "split SHA drift")
    require(sha_file(parent_contract_path) == contract["inputs"]["parent_repair2_contract_sha256"], "parent contract SHA drift")

    fixed_stream = contract["pilot"]["fixed_stream"]
    task_ids = list(split["e1_update_streams"][fixed_stream])
    require(len(task_ids) == 8, "semantic-pilot stream must contain eight tasks")
    require(task_ids == contract["pilot"]["task_ids"], "semantic-pilot task order drift")
    pool_root = Path(parent_contract["e1_a_pool_root"])
    for task_id in task_ids:
        pool_path = pool_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.is_file(), f"missing frozen semantic-pilot pool: {task_id}")
        require(sha_file(pool_path) == contract["pilot"]["pool_sha256"][task_id] == support["pool_sha256"][task_id], f"semantic-pilot pool SHA drift: {task_id}")

    rb_root = Path(contract["reasoningbank"]["root"])
    observed_rb_head = subprocess.run(
        ["git", "-C", str(rb_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(observed_rb_head == contract["reasoningbank"]["commit"], "ReasoningBank commit drift")

    # All static and environment bindings above must pass before exactly-once
    # execution state is created. From this point onward any failure consumes the
    # single-use attempt and may not be automatically relaunched.
    lock = acquire_lock(run_root, contract_sha=contract_sha, authorization_sha=auth_sha)

    ledger = ProviderBudgetLedger(
        path=run_root / "checkpoints/provider_budget.sqlite3",
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=11,
        per_unit_limit=11,
        allow_create=True,
    )
    require(ledger.snapshot().total_claimed == 0, "provider claims existed before semantic pilot")

    start = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-run-start",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "STARTED_EXACTLY_ONCE",
        "pid": os.getpid(),
        "pgid": os.getpgrp(),
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "fixed_stream": contract["pilot"]["fixed_stream"],
        "provider_claims_before_start": 0,
        "heldout_evaluations": 0,
        "scientific_effectiveness_evaluated": False,
    }
    atomic_json(run_root / "checkpoints/run_start_receipt.json", start)

    renderer = MatchedEvidenceWindowRenderer(cap_tokens=3072)

    aggregator = MindMemOSArkPlanChatAdapter(
        settings=settings,
        requested_model=contract["model"]["requested_model"],
        required_resolved_model=contract["model"]["required_resolved_model"],
        max_parse_attempts=1,
        record_dir=run_root / "provider_calls/aggregation",
        provider_budget_ledger=ledger,
        provider_budget_unit_id=f"{fixed_stream}/rbagg-semantic-pilot",
    )
    updater = MindMemOSArkPlanChatAdapter(
        settings=settings,
        requested_model=contract["model"]["requested_model"],
        required_resolved_model=contract["model"]["required_resolved_model"],
        max_parse_attempts=2,
        record_dir=run_root / "provider_calls/mindmemos",
        provider_budget_ledger=ledger,
        provider_budget_unit_id=f"{fixed_stream}/rbagg-semantic-pilot",
    )

    pools = []
    aggregates = []
    aggregation_rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        pool_path = pool_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.is_file() and sha_file(pool_path) == support["pool_sha256"][task_id], f"frozen pool drift: {task_id}")
        pool = load_frozen_pool(pool_path)
        source_payloads = []
        source_shas = []
        for trajectory in pool.trajectories:
            trajectory_path = Path(trajectory.trajectory_path)
            require(trajectory_path.is_file() and sha_file(trajectory_path) == trajectory.trajectory_sha256, f"trajectory drift: {task_id}/{trajectory.rollout_index}")
            source_payloads.append(load_json(trajectory_path))
            source_shas.append(trajectory.trajectory_sha256)
        rb_system, rb_user, rb_receipt = render_rb_style_aggregation_prompt(
            trajectory_payloads=source_payloads,
            trajectory_sha256s=source_shas,
            reasoningbank_root=rb_root,
            renderer=renderer,
        )

        def parser(text: str):
            return parse_rb_memory_items(text)

        response = await aggregator.chat(
            task=f"rbagg-aggregate-{task_id}",
            messages=[{"role": "system", "content": rb_system}, {"role": "user", "content": rb_user}],
            format_parser=parser,
            feedback_on_parse_error=False,
            model=contract["model"]["requested_model"],
            max_completion_tokens=int(contract["reasoningbank"]["aggregator_max_output_tokens"]),
            temperature=float(contract["reasoningbank"]["aggregator_temperature"]),
            thinking="disabled",
        )
        require(response.parsed is not None, f"RB aggregation parser returned none: {task_id}")
        normalized = normalize_rb_memory_items(response.parsed)
        aggregate = build_rb_aggregated_session_evidence(
            task_id=task_id,
            pool_id=pool.pool_id,
            acting_score=float(pool.acting_success),
            raw_memory_items=normalized,
            aggregation_receipt=rb_receipt.to_dict(),
        )
        aggregate_path = run_root / "aggregates" / f"{task_id}.json"
        aggregate_payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-task-aggregate",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "task_id": task_id,
            "pool_id": pool.pool_id,
            "pool_sha256": sha_file(pool_path),
            "acting_score": float(pool.acting_success),
            "memory_item_count": aggregate.memory_item_count,
            "memory_items_markdown": aggregate.memory_items_markdown,
            "memory_items_sha256": aggregate.memory_items_sha256,
            "aggregation_receipt": rb_receipt.to_dict(),
            "provider_response_sha256": sha_text(response.content),
            "resolved_model": response.model,
            "scientific_effectiveness_evaluated": False,
        }
        atomic_json(aggregate_path, aggregate_payload)
        aggregation_rows.append(
            {
                "task_id": task_id,
                "aggregate_path": str(aggregate_path.resolve()),
                "aggregate_sha256": sha_file(aggregate_path),
                "memory_items_sha256": aggregate.memory_items_sha256,
                "memory_item_count": aggregate.memory_item_count,
                "acting_score": float(pool.acting_success),
            }
        )
        pools.append(pool)
        aggregates.append(aggregate)

    require(len(aggregator.public_receipts()) == 8, "semantic pilot must make exactly eight aggregation calls")
    initial_path = Path(parent_contract["initial_skill"]["path"])
    require(initial_path.is_file() and sha_file(initial_path) == parent_contract["initial_skill"]["sha256"], "initial skill drift")
    update = await run_rbagg_update(
        stream_id=fixed_stream,
        pools=pools,
        aggregates=aggregates,
        initial_skill_md=initial_path.read_text(encoding="utf-8"),
        initial_skill_sha256=parent_contract["initial_skill"]["sha256"],
        run_dir=run_root / "update",
        llm_adapter=updater,
        mindmemos_commit=parent_contract["mindmemos"]["commit"],
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        transcript_max_chars=int(parent_contract["updater"]["transcript_max_chars"]),
    )
    updater_receipt = load_json(Path(update.update_receipt_path))
    updater_calls = len(updater.public_receipts())
    require(updater_calls in (2, 3), f"MindMemOS semantic-pilot calls outside frozen 2/3 path: {updater_calls}")
    require(updater_receipt.get("new_first_party_trajectory_summaries") == 0, "semantic pilot unexpectedly used trajectory summarization")
    require(updater_receipt.get("precomputed_summary_consumed_count") == 8, "semantic pilot did not consume all eight aggregates")
    require(update.evolved and len(update.new_version_ids) == 1, "semantic pilot did not mint exactly one skill version")

    all_receipts = aggregator.public_receipts() + updater.public_receipts()
    require(len(all_receipts) == 8 + updater_calls, "provider receipt count drift")
    require(all(row.get("resolved_model") == contract["model"]["required_resolved_model"] for row in all_receipts), "resolved model drift in semantic pilot")
    require(all(row.get("hidden_provider_retry_used") is False for row in all_receipts), "hidden provider retry detected")
    require(all(int(row.get("provider_retry_limit", -1)) == 0 for row in all_receipts), "provider retry limit drift")
    require(all(str(row.get("provider_status")) == "completed" for row in all_receipts), "non-completed provider status in successful semantic pilot")

    snapshot = ledger.snapshot()
    require(snapshot.total_claimed == len(all_receipts), "provider budget claim/receipt mismatch")
    require(snapshot.total_claimed <= 11, "semantic-pilot provider budget exceeded")

    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_RBAGG_SINGLE_STREAM_SEMANTIC_PROVIDER_PILOT",
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "fixed_stream": fixed_stream,
        "task_count": 8,
        "aggregation_calls": 8,
        "aggregation_parse_successes": 8,
        "aggregation_item_counts": {row["task_id"]: row["memory_item_count"] for row in aggregation_rows},
        "mindmemos_calls": updater_calls,
        "mindmemos_nominal_path": updater_calls == 2,
        "mindmemos_visible_apply_correction_used": updater_calls == 3,
        "total_provider_calls": len(all_receipts),
        "provider_budget_total_limit": 11,
        "provider_budget_total_claimed": snapshot.total_claimed,
        "resolved_model": contract["model"]["required_resolved_model"],
        "hidden_provider_retry_used": False,
        "first_party_trajectory_summary_calls": 0,
        "precomputed_summaries_consumed": 8,
        "new_skill_versions": 1,
        "skill_post_path": update.skill_post_path,
        "skill_post_sha256": update.skill_post_sha256,
        "pilot_skill_scientific_inclusion": False,
        "pilot_skill_quarantined": True,
        "heldout_evaluations": 0,
        "scientific_effectiveness_evaluated": False,
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "aggregation_rows": aggregation_rows,
        "provider_budget_snapshot": snapshot.to_dict(),
        "exclusive_lock_path": str(lock.resolve()),
        "authority": {
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "paper_promotion": False,
            "public_benchmark": False,
            "second_backbone": False,
        },
        "next_gate": "SEPARATE_POST_PILOT_ADJUDICATION_BEFORE_ANY_FULL_RBAGG_DIAGNOSTIC",
    }
    summary_path = run_root / "summary/rbagg_semantic_pilot_summary.json"
    atomic_json(summary_path, summary)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--authorization", type=Path, required=True)
    args = ap.parse_args()
    payload = asyncio.run(run(args))
    print(json.dumps({k: payload[k] for k in ["status", "fixed_stream", "aggregation_calls", "mindmemos_calls", "total_provider_calls", "heldout_evaluations", "next_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
