"""Outcome-blind adjudication for the fresh P1 Q3 implementation qualification."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    MODEL,
    PID_NAMESPACE,
    ROOT,
    canonical_json,
    sha256_file,
    utcnow,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q3 import (
    ACQUISITION,
    ARMS,
    CONTRACT,
    FIXTURES,
    INDEX,
    PARSER_QUALIFICATION,
    PRIOR_ADJUDICATION,
    RUNTIME_OUTPUT,
    TREATMENTS,
    load_payload,
)

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-adjudication-20260830.json"


def request_contents_nonblank(requests: list[dict[str, Any]]) -> bool:
    return bool(requests) and all(
        bool(message.get("content")) and str(message["content"]).strip() != ""
        for request in requests
        for message in request.get("input", [])
    ) and all(bool(request.get("input")) for request in requests)


def summarize_run(receipt: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    responses = run.get("model_responses") or []
    requests = run.get("R1_model_visible_requests") or []
    runtime = run.get("runtime") or {}
    base_receipt = (runtime.get("receipt") or {}).get("base_commit_receipt") or {}
    outcome = run.get("R4_terminal_outcome") or {}
    checks = {
        "identity_matches_index": (
            run.get("run_id") == receipt["run_id"]
            and run.get("instance_id") == receipt["instance_id"]
        ),
        "no_provider_runtime_or_implementation_failure": (
            run.get("failure") is None
            and run.get("execution_status") != "IMPLEMENTATION_FAILURE"
        ),
        "no_blank_model_visible_request_content": request_contents_nonblank(requests),
        "all_responses_resolve_to_exact_model": (
            bool(responses)
            and all(row.get("resolved_model") == MODEL for row in responses)
        ),
        "provider_config_exact": (
            (run.get("provider") or {}).get("model") == MODEL
            and (run.get("provider") or {}).get("base_url") == BASE_URL
            and (run.get("provider") or {}).get("temperature") == 0.0
            and (run.get("provider") or {}).get("max_output_tokens") == "omitted"
            and (run.get("provider") or {}).get("seed") == "omitted"
            and (run.get("provider") or {}).get("top_p") == "omitted"
        ),
        "fresh_base_state_receipt_valid": base_receipt.get("returncode") == 0,
        "runtime_namespace_and_platform_exact": (
            runtime.get("pid_namespace") == PID_NAMESPACE
            and runtime.get("platform") == "linux/amd64"
        ),
        "valid_swebench_evaluator_output": outcome.get("valid") is True,
        "evaluator_inputs_not_model_visible": (
            (run.get("scientific_boundary") or {}).get("gold_patch_model_visible") is False
            and (run.get("scientific_boundary") or {}).get("test_patch_model_visible") is False
            and (run.get("scientific_boundary") or {}).get("evaluator_script_model_visible") is False
        ),
    }
    return {
        "ordinal": receipt["ordinal"],
        "selection_rank": receipt["selection_rank"],
        "instance_id": receipt["instance_id"],
        "arm": receipt["arm"],
        "run_id": receipt["run_id"],
        "run_file_sha256": receipt["file_sha256"],
        "exit_status": run.get("exit_status", run.get("execution_status")),
        "resolved": outcome.get("resolved"),
        "task_outcome_affects_implementation_qualification": False,
        "selected_memory": run.get("selected_memory"),
        "first_R1": copy.deepcopy(requests[0]) if requests else None,
        "checks": checks,
        "implementation_pass": all(checks.values()),
    }


def paired_invariants(
    summaries: list[dict[str, Any]],
) -> dict[str, dict[str, bool]]:
    by_key = {(row["instance_id"], row["arm"]): row for row in summaries}
    result = {}
    for instance_id in sorted({row["instance_id"] for row in summaries}):
        rows = {arm: by_key.get((instance_id, arm)) for arm in ARMS}
        complete = all(rows.values())
        result[instance_id] = {
            "all_five_arms_present": complete,
            "A_B_selected_memory_equal": bool(
                complete and rows["A"]["selected_memory"] == rows["B"]["selected_memory"]
            ),
            "A_B_first_R1_equal": bool(
                complete
                and canonical_json(rows["A"]["first_R1"])
                == canonical_json(rows["B"]["first_R1"])
            ),
            "B_E_selected_memory_equal": bool(
                complete and rows["B"]["selected_memory"] == rows["E"]["selected_memory"]
            ),
            "B_E_first_R1_equal": bool(
                complete
                and canonical_json(rows["B"]["first_R1"])
                == canonical_json(rows["E"]["first_R1"])
            ),
        }
    return result


def adjudicate(
    *, index_path: Path = INDEX, output: Path = OUTPUT,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q3 adjudication: {output}")
    index = load_payload(index_path)
    contract = load_payload(CONTRACT)
    runtime = load_payload(RUNTIME_OUTPUT)
    parser_qualification = load_payload(PARSER_QUALIFICATION)
    acquisition = load_payload(ACQUISITION)
    completed = index.get("completed_runs") or []
    journal = index.get("run_journal") or []
    summaries = []
    artifact_checks = []
    for receipt in completed:
        path = (ROOT / receipt["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise RuntimeError("Q3 run path escapes repository")
        actual_sha = sha256_file(path)
        run = load_payload(path)
        hash_pass = actual_sha == receipt["file_sha256"]
        artifact_checks.append({
            "run_id": receipt["run_id"],
            "expected_sha256": receipt["file_sha256"],
            "actual_sha256": actual_sha,
            "pass": hash_pass,
        })
        summary = summarize_run(receipt, run)
        summary["checks"]["run_file_hash_matches_index"] = hash_pass
        summary["implementation_pass"] = all(summary["checks"].values())
        summaries.append(summary)
    pairs = paired_invariants(summaries)
    expected_order = [
        (rank, instance_id, arm)
        for rank, instance_id in (
            (5, "sphinx-doc__sphinx-9230"), (6, "django__django-11880")
        )
        for arm in ARMS
    ]
    actual_order = [
        (row.get("selection_rank"), row.get("instance_id"), row.get("arm"))
        for row in completed
    ]
    journal_order = [
        (row.get("selection_rank"), row.get("instance_id"), row.get("arm"))
        for row in journal
    ]
    qualification_checks = {
        "contract_and_fixture_bindings_exact": (
            index["contract_sha256"] == sha256_file(CONTRACT)
            and index["fixtures_sha256"] == sha256_file(FIXTURES)
            and index["treatment_manifest_sha256"] == sha256_file(TREATMENTS)
            and index["prior_adjudication_sha256"] == sha256_file(PRIOR_ADJUDICATION)
            and contract["bindings"]["q3_fixtures_sha256"] == sha256_file(FIXTURES)
            and contract["bindings"]["treatment_manifest_sha256"]
            == sha256_file(TREATMENTS)
            and contract["bindings"]["prior_adjudication_sha256"]
            == sha256_file(PRIOR_ADJUDICATION)
        ),
        "official_parser_qualification_exact_and_passed": (
            index["parser_qualification_sha256"] == sha256_file(PARSER_QUALIFICATION)
            and parser_qualification["decision"] == "P1_Q3_PARSERS_QUALIFIED"
            and parser_qualification["all_cases_exact"] is True
            and parser_qualification["case_count"] == 14
            and parser_qualification["scientific_boundary"]["q3_task_outcome_observed"]
            is False
        ),
        "fixed_image_acquisition_exact_and_passed": (
            index["fixed_image_acquisition_sha256"] == sha256_file(ACQUISITION)
            and acquisition["decision"] == "P1_Q3_FIXED_IMAGES_READY"
            and acquisition["all_blobs_sha256_verified"] is True
            and acquisition["all_images_imported_by_exact_digest"] is True
            and acquisition["scientific_boundary"]["q3_task_outcome_observed"] is False
        ),
        "runtime_qualification_exact_and_passed": (
            index["runtime_qualification_sha256"] == sha256_file(RUNTIME_OUTPUT)
            and runtime["decision"] == "P1_Q3_RUNTIME_QUALIFIED"
            and runtime["scientific_boundary"]["q3_task_outcome_observed"] is False
            and runtime["frozen_input_verification"]["official_parser_qualification"]["pass"]
            is True
            and runtime["frozen_input_verification"]["fixed_image_acquisition"]["pass"]
            is True
        ),
        "all_ten_started_once_in_frozen_order": (
            len(journal) == 10
            and journal_order == expected_order
            and all(row.get("attempt_count") == 1 for row in journal)
            and all(row.get("status") == "persisted" for row in journal)
        ),
        "all_ten_persisted_once_in_frozen_order": (
            index.get("execution_complete") is True
            and len(completed) == 10
            and actual_order == expected_order
            and len({row["run_id"] for row in completed}) == 10
            and all(row.get("attempt_count") == 1 for row in completed)
        ),
        "all_run_artifacts_hash_valid": (
            len(artifact_checks) == 10 and all(row["pass"] for row in artifact_checks)
        ),
        "all_runs_implementation_valid": (
            len(summaries) == 10 and all(row["implementation_pass"] for row in summaries)
        ),
        "A_B_and_B_E_pair_invariants_hold": (
            len(pairs) == 2
            and all(all(checks.values()) for checks in pairs.values())
        ),
        "negative_task_outcomes_excluded_from_qualification": True,
        "automatic_retry_and_replacement_forbidden": (
            index.get("automatic_retry") == "forbidden"
            and index.get("replacement_sampling") == "forbidden"
        ),
    }
    implementation_qualified = all(qualification_checks.values())
    decision = (
        "P1_Q3_IMPLEMENTATION_QUALIFIED_FULL_P1_PLANNING_GATE_OPEN_EXECUTION_UNAUTHORIZED"
        if implementation_qualified
        else "P1_Q3_IMPLEMENTATION_UNQUALIFIED_FULL_P1_HOLD"
    )
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-ADJUDICATION-20260830",
        "created_at_utc": utcnow(),
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "index": str(index_path.relative_to(ROOT)),
        "index_sha256": sha256_file(index_path),
        "runtime_qualification_sha256": sha256_file(RUNTIME_OUTPUT),
        "artifact_checks": artifact_checks,
        "run_summaries": summaries,
        "paired_invariants": pairs,
        "qualification_checks": qualification_checks,
        "implementation_qualified": implementation_qualified,
        "descriptive_task_outcomes": {
            "resolved_count": sum(row["resolved"] is True for row in summaries),
            "unresolved_count": sum(row["resolved"] is False for row in summaries),
            "missing_or_invalid_count": sum(row["resolved"] is None for row in summaries),
            "used_for_implementation_qualification": False,
        },
        "decision": decision,
        "authorization": {
            "separate_full_p1_planning_gate_open": implementation_qualified,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
            "original_ten_runs_reclassified": False,
        },
        "credential_material_present": False,
        "scientific_boundary": {
            "old_ten_runs_immutable": True,
            "q2_runs_immutable": True,
            "prior_negative_evidence_preserved": True,
            "q3_is_prospective_implementation_qualification_only": True,
            "negative_task_outcome_does_not_fail_qualification": True,
        },
    }
    file_sha = write_json(output, payload)
    return {
        "decision": decision,
        "implementation_qualified": implementation_qualified,
        "file_sha256": file_sha,
        "resolved_count": payload["descriptive_task_outcomes"]["resolved_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(adjudicate(index_path=args.index, output=args.output), sort_keys=True))


if __name__ == "__main__":
    main()
