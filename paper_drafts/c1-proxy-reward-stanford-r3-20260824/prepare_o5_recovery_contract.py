#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
OBJECTION_ID = "PROXY-O5"
AUTHORITY_TYPE = "human-c1-proxy-reward-stanford-repair-experiment-program"
EXPECTED_DESIGN_SHA256 = "4ba22e9dee9a753e6a2cf6e136259c0763f12f9503aef2ccc75285571b2817a9"
EXPECTED_FAILED_CONTRACT_SHA256 = "614c3f0e335f0bfed0bf86ad72ed31eb319e32693356ff4d5cef6aa4dd1e129f"
EXPECTED_REQUESTED_MODEL = "doubao-seed-2.0-mini"
EXPECTED_RESOLVED_MODEL = "doubao-seed-2-0-mini-260215"
EXPECTED_SOURCE_MESSAGE_SHA256 = "7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62"
EXPECTED_INPUT_SHA256 = {
    "support": "b64635594251ac8f74251ea68b39a0c0c03b689b0708366be9c68ff193edd7ce",
    "parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "task_config": "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6",
    "evaluator": "f78eb61554c811f9411e7d72e0bdf2b5baa27379cbf632ade7fe49ce51a3f30d",
}
FUTURE_TASKS = ["164", "385", "387", "388"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def safe_historical_alias_audit(receipts_root: Path) -> dict[str, Any]:
    rows = []
    for path in sorted(receipts_root.rglob("*.json")):
        try:
            row = load(path)
        except Exception:
            continue
        request = row.get("request") or {}
        response = row.get("response") or {}
        rows.append({
            "requested_model": request.get("requested_model"),
            "resolved_model": response.get("resolved_model"),
            "status": response.get("status"),
        })
    require(len(rows) == 256, f"expected 256 historical F2R1 receipts, found {len(rows)}")
    requested = collections.Counter(str(r["requested_model"]) for r in rows)
    resolved = collections.Counter(str(r["resolved_model"]) for r in rows)
    statuses = collections.Counter(str(r["status"]) for r in rows)
    require(requested == collections.Counter({EXPECTED_REQUESTED_MODEL: 256}), f"historical requested-model mapping drift: {requested}")
    require(resolved == collections.Counter({EXPECTED_RESOLVED_MODEL: 256}), f"historical resolved-model mapping drift: {resolved}")
    return {
        "historical_receipts": 256,
        "requested_model_counts": dict(requested),
        "resolved_model_counts": dict(resolved),
        "provider_status_counts": dict(statuses),
        "interpretation": "The versioned resolved model is the exact historical F2R1 provider resolution for all 256 receipts, not a model substitution.",
        "scientific_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile PROXY-O5 recovery after execution-layer resolved-model validator mismatch.")
    ap.add_argument("--master-authority", required=True, type=Path)
    ap.add_argument("--failed-run", required=True, type=Path)
    ap.add_argument("--historical-receipts-root", required=True, type=Path)
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    ap.add_argument("--analysis", required=True, type=Path)
    ap.add_argument("--input-root", required=True, type=Path)
    ap.add_argument("--env-file", required=True, type=Path)
    ap.add_argument("--run-root", required=True, type=Path)
    args = ap.parse_args()

    master = load(args.master_authority)
    require(master.get("authority_type") == AUTHORITY_TYPE, "master authority type mismatch")
    require(master.get("decision") == "approve", "master authority is not approved")
    require(master.get("reviewed_by") in {"user", "human-user"}, "master authority reviewer mismatch")
    require(master.get("paper_id") == PAPER_ID, "master authority paper mismatch")
    require(master.get("source_message_sha256") == EXPECTED_SOURCE_MESSAGE_SHA256, "master authority source-message mismatch")
    future = master.get("future_repair_experiments") or {}
    require(future.get("human_program_authorized") is True, "future repair experiments not human-authorized")
    require(future.get("automatic_execution_without_frozen_subcontract") is False, "master authority must remain fail-closed")
    require(future.get("requires_per_experiment_preregistration") is True, "recovery requires preregistration")
    require(future.get("requires_budget_and_stop_rule") is True, "recovery requires budget/stop rule")
    require(future.get("outcome_driven_scope_expansion_authorized") is False, "outcome-driven scope expansion forbidden")
    require(master.get("claim_expansion_authorized") is False, "claim expansion forbidden")

    failed_contract_path = args.failed_run / "o5-execution-contract.json"
    failed_result_path = args.failed_run / "o5-result.json"
    require(failed_contract_path.is_file(), "failed execution contract missing")
    require(failed_result_path.is_file(), "failed public result missing")
    require(sha256(failed_contract_path) == EXPECTED_FAILED_CONTRACT_SHA256, "failed execution contract SHA drift")
    failed_result = load(failed_result_path)
    summary = failed_result.get("summary") or {}
    require(failed_result.get("status") == "O5_NO_MEMORY_INCOMPLETE", "failed run status mismatch")
    require(int(summary.get("requested_provider_calls") or 0) == 32, "failed run request count mismatch")
    require(int(summary.get("complete_provider_calls") or 0) == 0, "failed run unexpectedly has scientific completions")
    require(int(summary.get("provider_or_runtime_failures") or 0) == 32, "failed run failure count mismatch")

    stage_root = args.failed_run / "private/stages"
    stages = [load(path) for path in sorted(stage_root.glob("*.json"))]
    require(len(stages) == 32, f"expected 32 failed stages, found {len(stages)}")
    signatures = collections.Counter((row.get("status"), row.get("error_type"), row.get("error")) for row in stages)
    expected_sig = ("provider_or_runtime_failure", "RuntimeError", f"resolved model drift: {EXPECTED_RESOLVED_MODEL}")
    require(signatures == collections.Counter({expected_sig: 32}), f"failed-run signature not uniform validator mismatch: {signatures}")

    alias_audit = safe_historical_alias_audit(args.historical_receipts_root)
    require(sha256(args.design) == EXPECTED_DESIGN_SHA256, "O5 design SHA drift")
    require(args.runner.is_file() and args.analysis.is_file(), "runner/analysis missing")
    require(args.env_file.is_file(), "provider env file missing")

    input_paths = {
        "support": args.input_root / "generated/d2-proxy-reward-terminal-fixed-evidence-support.json",
        "parquet": args.input_root / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet",
        "task_config": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json",
        "evaluator": args.input_root / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py",
        "vendor": args.input_root / "generated/research-data/paper-yield-d5-c01/vendor",
    }
    for key in EXPECTED_INPUT_SHA256:
        require(input_paths[key].is_file(), f"missing frozen input: {key}")
        require(sha256(input_paths[key]) == EXPECTED_INPUT_SHA256[key], f"frozen input SHA drift: {key}")
    require(input_paths["vendor"].is_dir(), "historical vendor runtime missing")

    failure_receipt = {
        "schema_version": "1.0",
        "receipt_type": "execution-failure-asset",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "failed_experiment_id": failed_result.get("experiment_id"),
        "status": "EXECUTION_VALIDATOR_MISMATCH_ZERO_SCIENTIFIC_AUTHORITY",
        "failed_contract_sha256": EXPECTED_FAILED_CONTRACT_SHA256,
        "provider_calls_consumed": 32,
        "scientifically_complete_units": 0,
        "diagnosis": "The new O5 harness incorrectly required resolved_model to equal the requested alias. Historical F2R1 resolves all 256 requests to the provider's versioned model name, so the validator rejected valid provider completions after POST.",
        "historical_alias_audit": alias_audit,
        "repair": {
            "changed_layer": "execution-validator-and-receipt-persistence-only",
            "allow_exact_historical_resolved_model": EXPECTED_RESOLVED_MODEL,
            "archive_provider_response_before_local_validation": True,
            "scientific_contract_changed": False,
            "model_requested_changed": False,
            "task_support_changed": False,
            "evaluator_changed": False,
            "claim_boundary_changed": False,
        },
        "scientific_authority": False,
        "principle_update_authority": False,
    }
    atomic_json(args.failed_run / "o5-execution-failure-receipt.json", failure_receipt)

    run_root = args.run_root.resolve()
    contract = {
        "schema_version": "1.0",
        "experiment_id": "D2-PROXY-O5-NO-MEMORY-RECOVERY-R1",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "status": "FROZEN_BEFORE_PROVIDER_CALLS",
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_root": str(run_root),
        "recovery_of": {
            "run_root": str(args.failed_run.resolve()),
            "failed_contract_sha256": EXPECTED_FAILED_CONTRACT_SHA256,
            "failure_receipt_path": str((args.failed_run / "o5-execution-failure-receipt.json").resolve()),
            "failure_receipt_sha256": sha256(args.failed_run / "o5-execution-failure-receipt.json"),
            "failure_layer": "execution-validator",
            "prior_scientific_authority": False,
        },
        "human_authority": {
            "path": str(args.master_authority.resolve()),
            "sha256": sha256(args.master_authority),
            "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA256,
            "program_repair_authorized": True,
        },
        "design": {"path": str(args.design.resolve()), "sha256": EXPECTED_DESIGN_SHA256},
        "code": {
            "runner": {"path": str(args.runner.resolve()), "sha256": sha256(args.runner)},
            "analysis": {"path": str(args.analysis.resolve()), "sha256": sha256(args.analysis)},
        },
        "historical_alias_audit": alias_audit,
        "source_artifacts": {
            key: {"path": str(input_paths[key].resolve()), "sha256": EXPECTED_INPUT_SHA256[key]}
            for key in EXPECTED_INPUT_SHA256
        },
        "vendor_path": str(input_paths["vendor"].resolve()),
        "provider_env_file": str(args.env_file.resolve()),
        "future_tasks": FUTURE_TASKS,
        "condition": "no_memory",
        "rollouts_per_future_task": 8,
        "expected_provider_calls": 32,
        "model": {
            "requested": EXPECTED_REQUESTED_MODEL,
            "expected_resolved": EXPECTED_RESOLVED_MODEL,
            "temperature": 0.2,
            "max_output_tokens": 900,
            "thinking": "disabled",
            "allow_thinking_compatibility_fallback": False,
            "provider_retries": 0,
            "store": True,
            "substitution_allowed": False,
        },
        "missingness_policy": {
            "provider_retries": 0,
            "regenerate_failed_units": False,
            "impute_failed_units": False,
            "replace_future_task": False,
            "interpretation_if_any_provider_failure": "Report incomplete recovery without top-up. Any further generation requires another frozen recovery contract.",
        },
        "analysis_contract": load(args.design)["analysis_contract"],
        "claim_boundary": load(args.design)["claim_boundary"],
        "recovery_budget": {
            "new_provider_call_ceiling": 32,
            "reason": "One-for-one rerun because all prior 32 POSTs were rendered scientifically unusable by an execution-layer validator bug; no prior outcome entered analysis.",
            "stop_after_this_attempt": True,
        },
        "authority": {
            "scientific_reopen_authority": True,
            "experiment_authority": True,
            "provider_call_authority": True,
            "gpu_authority": False,
            "claim_expansion_authority": False,
            "submission_authority": False,
        },
    }
    atomic_json(run_root / "o5-recovery-contract.json", contract)
    receipt = {
        "schema_version": "1.0",
        "receipt_type": "scoped-experiment-recovery-authorization",
        "paper_id": PAPER_ID,
        "objection_id": OBJECTION_ID,
        "experiment_id": contract["experiment_id"],
        "status": "O5_RECOVERY_R1_AUTHORIZED_BY_MASTER_PROGRAM",
        "master_authority_sha256": sha256(args.master_authority),
        "frozen_design_sha256": EXPECTED_DESIGN_SHA256,
        "failed_contract_sha256": EXPECTED_FAILED_CONTRACT_SHA256,
        "recovery_contract_sha256": sha256(run_root / "o5-recovery-contract.json"),
        "runner_sha256": contract["code"]["runner"]["sha256"],
        "analysis_sha256": contract["code"]["analysis"]["sha256"],
        "provider_call_ceiling": 32,
        "scientific_contract_changed": False,
        "authority": contract["authority"],
    }
    atomic_json(run_root / "o5-recovery-authorization-receipt.json", receipt)
    print(json.dumps({
        "status": receipt["status"],
        "failure_receipt": str(args.failed_run / "o5-execution-failure-receipt.json"),
        "recovery_contract": str(run_root / "o5-recovery-contract.json"),
        "recovery_contract_sha256": receipt["recovery_contract_sha256"],
        "provider_call_ceiling": 32,
        "historical_alias_audit": alias_audit,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
