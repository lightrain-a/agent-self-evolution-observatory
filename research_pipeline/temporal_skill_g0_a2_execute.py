from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings
from research_pipeline.experiment_authority import acquire_authority, release_authority

PAPER_ID = core.PAPER_ID
DATA_ROOT = core.DATA_ROOT
OWNER_ID = PAPER_ID + ":TEMP-O4-G0-A2"
PLAN = PROJECT_ROOT / "generated/temporal-skill-g0-a2-neutrality-plan-20260824.json"
STAGE = PROJECT_ROOT / "generated/temporal-skill-g0-a2-stage-contract-20260824.json"
AUTH = PROJECT_ROOT / "generated/temporal-skill-g0-a2-human-authorization-20260824.json"
OUTPUT = core.REPLAY_ROOT / "20260824-g0-a2-neutrality-deepseek" / "results.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_auth(auth: dict[str, Any], plan: dict[str, Any], stage: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checks = [
        (auth.get("status") == "HUMAN_EXECUTION_AUTHORITY_RECORDED", "status"),
        (bool(auth.get("scientific_reopen_authorized")), "scientific-reopen"),
        (bool(auth.get("execution_authorized")), "execution"),
        (bool(auth.get("provider_spend_authorized")), "provider-spend"),
        (auth.get("bound_plan_body_sha256") == plan["plan_body_sha256"], "plan-hash"),
        (auth.get("bound_stage_contract_sha256") == stage["stage_contract_sha256"], "stage-hash"),
        (auth.get("bound_executor_sha256") == sha_file(Path(__file__)), "executor-hash"),
        (auth.get("bound_core_runner_sha256") == sha_file(Path(core.__file__)), "core-runner-hash"),
        (not bool(auth.get("outcome_driven_stopping_authorized")), "outcome-stopping"),
        (bool((auth.get("bounded_budget") or {}).get("resume_missing_only")), "resume-missing-only"),
        (not bool((auth.get("bounded_budget") or {}).get("reruns_allowed")), "reruns-forbidden"),
        (int((auth.get("bounded_budget") or {}).get("model_calls_upper_bound") or -1) == len(plan["rows"]), "budget"),
    ]
    for ok, name in checks:
        if not ok:
            errors.append(name)
    supplied = auth.get("authorization_sha256")
    if supplied:
        body = {k: v for k, v in auth.items() if k != "authorization_sha256"}
        if supplied != core.canonical_sha(body):
            errors.append("self-hash")
    return errors


def progress(output: Path, plan: dict[str, Any], stage_name: str, status: str, note: str = "") -> dict[str, Any]:
    rows = core.load_csv_rows(output.parent / "results.csv")
    payload = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "plan_body_sha256": plan["plan_body_sha256"],
        "stage": stage_name, "status": status, "checkpoint_rows": len(rows), "planned_rows": len(plan["rows"]),
        "remaining_rows": len(plan["rows"]) - len(rows), "note": note,
        "results_csv": str(output.parent / "results.csv"), "results_jsonl": str(output.parent / "results.jsonl"),
        "raw_dir": str(output.parent / "raw"),
    }
    core.atomic_json(output.parent / "checkpoint.json", payload)
    return payload


def pilot_gate(output: Path, stage: dict[str, Any]) -> dict[str, Any]:
    rows = core.load_csv_rows(output.parent / "results.csv")
    required = stage["pilot"]["row_keys"]
    missing = [k for k in required if k not in rows]
    invalid = [k for k in required if k in rows and rows[k].get("runtime_valid") != "True"]
    drift = [k for k in required if k in rows and rows[k].get("resolved_model") != rows[k].get("required_resolved_model")]
    raw_missing = [k for k in required if k in rows and not Path(rows[k].get("raw_receipt_path") or "").exists()]
    result = {
        "schema_version": "1.0", "gate": "TEMP-O4-G0-A2-PILOT-RUNTIME-INTEGRITY",
        "pass": not (missing or invalid or drift or raw_missing), "pilot_calls": len(required),
        "missing": missing, "runtime_invalid": invalid, "model_drift": drift, "raw_missing": raw_missing,
        "scientific_outcomes_inspected_for_promotion": False,
    }
    core.atomic_json(output.parent / "pilot-gate.json", result)
    return result


def build_results(output: Path, plan: dict[str, Any], auth: dict[str, Any], assets: dict[str, Any]) -> dict[str, Any]:
    raw_by_key = {}
    for path in (output.parent / "raw").glob("*.json"):
        row = read_json(path)
        raw_by_key[core.row_key(row)] = row
    ordered = [raw_by_key[core.row_key(row)] for row in plan["rows"] if core.row_key(row) in raw_by_key]
    result = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "run_id": "TEMP-O4-G0-A2-NEUTRALITY-20260824",
        "plan_body_sha256": plan["plan_body_sha256"], "authorization_sha256": auth["authorization_sha256"],
        "executor_sha256": sha_file(Path(__file__)), "core_runner_sha256": sha_file(Path(core.__file__)),
        "asset_hashes": assets["hashes"], "rows": ordered, "rows_total": len(ordered),
        "runtime_valid_rows": sum(bool(r.get("runtime_valid")) for r in ordered),
        "status": "completed" if len(ordered) == len(plan["rows"]) else "partial",
    }
    result["scientific_result_available"] = result["status"] == "completed" and result["runtime_valid_rows"] == len(ordered)
    result["result_body_sha256"] = core.canonical_sha({k: v for k, v in result.items() if k != "result_body_sha256"})
    core.atomic_json(output, result)
    return result


def execute(stage_name: str) -> dict[str, Any]:
    plan = read_json(PLAN); stage = read_json(STAGE); auth = read_json(AUTH)
    errors = validate_auth(auth, plan, stage)
    if errors:
        raise RuntimeError("authorization invalid: " + ",".join(errors))
    assets = core.load_assets()
    if {r["endpoint_id"] for r in plan["rows"]} != set(assets["endpoints"]):
        raise RuntimeError("endpoint inventory mismatch")
    core.recover_orphan_raw(OUTPUT, plan)
    existing = core.load_csv_rows(OUTPUT.parent / "results.csv")
    bad = [k for k, r in existing.items() if r.get("runtime_valid") != "True"]
    if bad:
        raise RuntimeError("runtime-invalid checkpoint requires adjudication: " + bad[0])
    if stage_name == "full":
        gate_path = OUTPUT.parent / "pilot-gate.json"
        if not gate_path.exists() or not read_json(gate_path).get("pass"):
            raise RuntimeError("pilot gate not passed")
        target = {core.row_key(r) for r in plan["rows"]}
    else:
        target = set(stage["pilot"]["row_keys"])
    raw = ArkSettings.from_env(required=True)
    if raw.base_url.rstrip("/") != plan["model_identity"]["required_plan_base_url"].rstrip("/"):
        raise RuntimeError("not on frozen Ark Plan route")
    client = ArkResponsesClient(ArkSettings(api_key=raw.api_key, base_url=raw.base_url, default_model=raw.default_model, timeout_seconds=180.0, max_retries=0))
    run_id = f"TEMP-O4-G0-A2-{stage_name.upper()}-20260824"
    authority = acquire_authority(DATA_ROOT, OWNER_ID, plan["plan_body_sha256"], "temporal-skill-g0-a2-executor", f"A2-{stage_name}", run_id)
    outcome = "runner-exception"
    try:
        progress(OUTPUT, plan, stage_name, "running")
        index = {core.row_key(r): i for i, r in enumerate(plan["rows"])}
        for plan_row in plan["rows"]:
            key = core.row_key(plan_row)
            if key not in target or key in core.load_csv_rows(OUTPUT.parent / "results.csv"):
                continue
            row = core.run_one(client, assets, plan_row)
            core.persist_checkpoint(OUTPUT, row, index[key])
            progress(OUTPUT, plan, stage_name, "running", "last=" + key)
            if not row.get("runtime_valid"):
                outcome = row.get("failure_kind") or "runtime-invalid"
                progress(OUTPUT, plan, stage_name, "stopped", outcome)
                return {"status": "stopped", "reason": outcome, "unit_key": key}
        if stage_name == "pilot":
            gate = pilot_gate(OUTPUT, stage); outcome = "pilot-pass" if gate["pass"] else "pilot-fail"
            progress(OUTPUT, plan, stage_name, outcome)
            return {"status": outcome, "pilot_gate": gate}
        result = build_results(OUTPUT, plan, auth, assets); outcome = "completed" if result["scientific_result_available"] else "partial"
        progress(OUTPUT, plan, stage_name, outcome)
        return {"status": outcome, "rows_total": result["rows_total"], "output": str(OUTPUT)}
    finally:
        release_authority(DATA_ROOT, OWNER_ID, authority["authority_id"], outcome)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", choices=["pilot", "full"], default="pilot"); ap.add_argument("--validate-only", action="store_true"); args = ap.parse_args()
    plan = read_json(PLAN); stage = read_json(STAGE)
    if args.validate_only:
        auth = read_json(AUTH) if AUTH.exists() else {}
        print(json.dumps({"plan_sha": plan["plan_body_sha256"], "stage_sha": stage["stage_contract_sha256"], "executor_sha": sha_file(Path(__file__)), "authorization_errors": validate_auth(auth, plan, stage) if auth else ["missing-auth"], "checkpoint_rows": len(core.load_csv_rows(OUTPUT.parent / "results.csv"))}, indent=2)); return
    print(json.dumps(execute(args.stage), ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
