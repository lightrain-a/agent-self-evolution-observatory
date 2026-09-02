#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PASS = "PASS_RBAGG_SINGLE_STREAM_SEMANTIC_PROVIDER_PILOT"
AUDIT_PASS = "PASS_RBAGG_SEMANTIC_PILOT_INTEGRITY_FULL_DIAGNOSTIC_STILL_HOLD"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--authorization", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "semantic-pilot audit already exists")
    root = args.run_root
    summary_path = root / "summary/rbagg_semantic_pilot_summary.json"
    start_path = root / "checkpoints/run_start_receipt.json"
    ledger_path = root / "checkpoints/provider_budget.sqlite3"
    update_receipt_path = root / "update/update_receipt.json"
    skill_path = root / "update/skill_post/SKILL.md"
    lock_path = root / ".exclusive.lock"
    for path in (summary_path, start_path, ledger_path, update_receipt_path, skill_path, lock_path, args.contract, args.authorization):
        require(path.is_file(), f"missing semantic-pilot artifact: {path}")

    summary = load_json(summary_path)
    start = load_json(start_path)
    update = load_json(update_receipt_path)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)
    require(summary.get("status") == PASS, "semantic-pilot summary not PASS")
    require(summary.get("contract_sha256") == contract_sha, "summary contract drift")
    require(summary.get("authorization_sha256") == auth_sha, "summary authorization drift")
    require(start.get("contract_sha256") == contract_sha and start.get("authorization_sha256") == auth_sha, "start receipt binding drift")
    require(summary.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent status drift")
    require(summary.get("parent_status_changed") is False, "pilot changed parent status")
    require(summary.get("pilot_skill_scientific_inclusion") is False and summary.get("pilot_skill_quarantined") is True, "pilot skill quarantine drift")
    require(summary.get("heldout_evaluations") == 0 and summary.get("scientific_effectiveness_evaluated") is False, "pilot crossed effectiveness boundary")
    require(summary.get("aggregation_calls") == 8 and summary.get("aggregation_parse_successes") == 8, "aggregation cardinality drift")
    require(summary.get("mindmemos_calls") == 2 and summary.get("mindmemos_nominal_path") is True, "pilot did not use nominal MindMemOS path")
    require(summary.get("mindmemos_visible_apply_correction_used") is False, "unexpected correction path")
    require(summary.get("first_party_trajectory_summary_calls") == 0, "unexpected first-party trajectory summaries")
    require(summary.get("precomputed_summaries_consumed") == 8 and summary.get("new_skill_versions") == 1, "summary consumption/version drift")
    require(summary.get("resolved_model") == "deepseek-v4-pro-ga-260813", "resolved model drift")
    require(summary.get("hidden_provider_retry_used") is False, "hidden retry reported")
    require(summary.get("total_provider_calls") == 10, "provider call count drift")
    require(sha_file(skill_path) == summary.get("skill_post_sha256") == update.get("skill_post_sha256"), "pilot skill SHA drift")

    aggregate_files = sorted((root / "aggregates").glob("*.json"))
    agg_call_files = sorted((root / "provider_calls/aggregation").glob("*.json"))
    updater_call_files = sorted((root / "provider_calls/mindmemos").glob("*.json"))
    require(len(aggregate_files) == 8 and len(agg_call_files) == 8 and len(updater_call_files) == 2, "pilot file cardinality drift")

    provider_rows = []
    for role, files, expected_temp in (("aggregation", agg_call_files, 0.7), ("mindmemos", updater_call_files, 0.0)):
        for path in files:
            row = load_json(path)
            require(row.get("provider_status") == "completed", f"provider call not completed: {path}")
            require(row.get("resolved_model") == "deepseek-v4-pro-ga-260813", f"provider model drift: {path}")
            require(row.get("provider_retry_limit") == 0 and row.get("hidden_provider_retry_used") is False, f"retry drift: {path}")
            require(abs(float(row.get("temperature_requested")) - expected_temp) < 1e-12, f"temperature drift: {path}")
            provider_rows.append({
                "role": role,
                "path": str(path),
                "sha256": sha_file(path),
                "task": row.get("task"),
                "resolved_model": row.get("resolved_model"),
                "provider_status": row.get("provider_status"),
                "temperature_requested": row.get("temperature_requested"),
                "prompt_tokens": (row.get("usage") or {}).get("input_tokens"),
                "completion_tokens": (row.get("usage") or {}).get("output_tokens"),
                "total_tokens": (row.get("usage") or {}).get("total_tokens"),
                "wall_time_seconds": row.get("wall_time_seconds"),
                "parse_error": row.get("parse_error"),
            })
    require(len(provider_rows) == 10, "provider metadata rows drift")
    require(all(not row.get("parse_error") for row in provider_rows), "parse error present in successful pilot")

    with sqlite3.connect(f"file:{ledger_path}?mode=ro", uri=True) as con:
        metadata = dict(con.execute("SELECT key,value FROM metadata").fetchall())
        claims = con.execute("SELECT unit_id, unit_call_index FROM claims ORDER BY claim_id").fetchall()
    require(metadata.get("contract_sha256") == contract_sha and metadata.get("authorization_sha256") == auth_sha, "ledger binding drift")
    require(metadata.get("total_limit") == "11" and metadata.get("per_unit_limit") == "11", "ledger limit drift")
    require(len(claims) == 10, "ledger claim count drift")
    require([int(index) for _, index in claims] == list(range(1, 11)), "ledger claim sequence drift")
    require(len({str(unit) for unit, _ in claims}) == 1, "pilot used more than one provider-budget unit")

    forbidden = []
    for path in root.rglob("*"):
        if path.is_file() and any(token in path.name.lower() for token in ("heldout", "evaluation_summary", "scientific_effect")):
            forbidden.append(str(path))
    require(not forbidden, f"heldout/effect artifacts found in semantic pilot: {forbidden[:3]}")

    aggregate_inventory = [{"path": str(path), "sha256": sha_file(path)} for path in aggregate_files]
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-integrity-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUDIT_PASS,
        "run_root": str(root),
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "summary_path": str(summary_path),
        "summary_sha256": sha_file(summary_path),
        "run_start_receipt_sha256": sha_file(start_path),
        "provider_budget_ledger_sha256": sha_file(ledger_path),
        "update_receipt_sha256": sha_file(update_receipt_path),
        "skill_post_sha256": sha_file(skill_path),
        "exclusive_lock_sha256": sha_file(lock_path),
        "aggregate_inventory": aggregate_inventory,
        "provider_call_inventory": provider_rows,
        "aggregation_calls": 8,
        "mindmemos_calls": 2,
        "total_provider_calls": 10,
        "provider_claims": 10,
        "provider_budget_limit": 11,
        "all_provider_calls_completed": True,
        "all_provider_calls_exact_model": True,
        "hidden_provider_retry_used": False,
        "parse_failures": 0,
        "visible_apply_correction_used": False,
        "heldout_evaluations": 0,
        "scientific_effectiveness_evaluated": False,
        "pilot_skill_scientific_inclusion": False,
        "pilot_skill_quarantined": True,
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "authority": {
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "paper_promotion": False,
            "public_benchmark": False,
            "second_backbone": False,
        },
        "next_gate": "FULL_DIAGNOSTIC_REQUIRES_NEW_POST_PILOT_DESIGN_REVIEW_CONTRACT_AND_AUTHORIZATION",
    }
    atomic_json(args.output, payload)
    print(json.dumps({k: payload[k] for k in ("status", "total_provider_calls", "provider_claims", "heldout_evaluations", "pilot_skill_quarantined", "next_gate")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
