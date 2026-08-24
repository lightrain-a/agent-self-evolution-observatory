#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "failed_contract": "614c3f0e335f0bfed0bf86ad72ed31eb319e32693356ff4d5cef6aa4dd1e129f",
    "failure_receipt": "bbffdc6be72addef2e71e6e32984888cfdcb950091380245d5b77a2731d93572",
    "recovery_contract": "525ff843676f4246c5945704b87e133cb3326ee7e84cd4e7328e1d40088a90c8",
    "result": "13d890bbf13b4eb77ea4161817af1d9260b2ef369bb9292fd240b94a266da379",
    "analysis": "1f3080a5f0d02530f6b04ebe7d24a2a890ef5fa35165ea62e84cb8401affa996",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--failed-run", required=True, type=Path)
    ap.add_argument("--recovery-run", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    paths = {
        "failed_contract": args.failed_run / "o5-execution-contract.json",
        "failure_receipt": args.failed_run / "o5-execution-failure-receipt.json",
        "recovery_contract": args.recovery_run / "o5-recovery-contract.json",
        "result": args.recovery_run / "o5-result.json",
        "analysis": args.recovery_run / "o5-analysis.json",
    }
    for key, path in paths.items():
        require(path.is_file(), f"missing O5 source artifact: {key}")
        require(sha(path) == EXPECTED[key], f"O5 source artifact SHA drift: {key}")

    failure = load(paths["failure_receipt"])
    result = load(paths["result"])
    analysis = load(paths["analysis"])
    recovery = load(paths["recovery_contract"])

    require(failure.get("status") == "EXECUTION_VALIDATOR_MISMATCH_ZERO_SCIENTIFIC_AUTHORITY", "unexpected O5 first-attempt failure classification")
    require(int(failure.get("provider_calls_consumed") or 0) == 32, "first-attempt call count drift")
    require(int(failure.get("scientifically_complete_units") or 0) == 0, "first-attempt scientific count must remain zero")
    require(result.get("status") == "O5_NO_MEMORY_COMPLETE", "O5 recovery not complete")
    rs = result.get("summary") or {}
    require(int(rs.get("requested_provider_calls") or 0) == 32, "O5 recovery request count drift")
    require(int(rs.get("complete_provider_calls") or 0) == 32, "O5 recovery completion count drift")
    require(int(rs.get("provider_or_runtime_failures") or 0) == 0, "O5 recovery has failures")
    require(int(rs.get("old_exploratory_no_memory_calls_reused") or 0) == 0, "old no-memory calls entered O5 estimator")
    require(analysis.get("fresh_no_memory_calls") == 32, "O5 analysis fresh-call count drift")
    require(analysis.get("old_exploratory_no_memory_calls_in_estimator") == 0, "O5 analysis reused exploratory calls")
    require(analysis.get("global_p_value") is None and analysis.get("global_gate") is None, "O5 must remain a descriptive secondary control")

    comparisons = analysis["cell_relative_comparisons"]
    by_key = {(row["source_memory_task"], row["future_task"]): row for row in comparisons}
    selected = {
        "source22_future388": by_key[("22", "388")],
        "source25_future387": by_key[("25", "387")],
        "source21_future388": by_key[("21", "388")],
        "source21_future385": by_key[("21", "385")],
    }

    payload = {
        "schema_version": "1.0",
        "artifact_type": "o5-manuscript-evidence-projection",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "objection_id": "PROXY-O5",
        "status": "O5_FRESH_NO_MEMORY_CONTROL_COMPLETE",
        "source_bindings": {key: {"path": str(path), "sha256": EXPECTED[key]} for key, path in paths.items()},
        "execution_accounting": {
            "first_attempt_provider_calls_execution_invalid": 32,
            "first_attempt_scientifically_usable_units": 0,
            "recovery_provider_calls": 32,
            "recovery_scientifically_usable_units": 32,
            "o5_total_provider_calls_consumed": 64,
            "old_exploratory_no_memory_calls_reused": 0,
            "old_exploratory_no_memory_calls_excluded": 12,
            "training_runs": 0,
            "gpu_runs": 0,
        },
        "fresh_no_memory_by_future_task": analysis["no_memory_by_future_task"],
        "point_estimate_geometry_counts": analysis["point_estimate_geometry_counts"],
        "selected_cell_diagnostics": selected,
        "all_cell_comparisons": comparisons,
        "main_interpretation": (
            "The fresh no-memory baseline does not induce a uniform ordering of success-label and failure-label memory. "
            "Across the 16 frozen source-by-future comparisons, eight are equidistant at the point estimate, six place omission closer to the success-memory branch, and two place omission closer to the failure-memory branch. "
            "Some cells therefore isolate one reward-conditioned branch as the deviation from omission, while others place both memory branches away from omission in the same direction."
        ),
        "claim_boundary": {
            "secondary_branch_location_control_only": True,
            "primary_f2r1_two_arm_gate_unchanged": True,
            "no_global_p_value": True,
            "shared_future_task_baseline_not_independent_across_sources": True,
            "does_not_show_success_memory_uniformly_good": True,
            "does_not_show_failure_memory_uniformly_bad": True,
            "does_not_create_three_arm_factorial_claim": True,
            "cross_model_claim_supported": False,
            "live_loop_claim_supported": False,
        },
        "failure_asset": {
            "status": failure["status"],
            "diagnosis": failure["diagnosis"],
            "historical_alias_audit": failure["historical_alias_audit"],
            "repair": failure["repair"],
        },
        "recovery_contract": {
            "experiment_id": recovery["experiment_id"],
            "recovery_budget": recovery["recovery_budget"],
            "authority": recovery["authority"],
        },
        "scientific_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "execution_accounting": payload["execution_accounting"],
        "no_memory": payload["fresh_no_memory_by_future_task"],
        "geometry": payload["point_estimate_geometry_counts"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
