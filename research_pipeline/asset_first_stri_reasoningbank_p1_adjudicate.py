"""Adjudicate the frozen ReasoningBank P1 minimal pilot without reruns."""

from __future__ import annotations

import argparse
import collections
import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    AGENT_PATH, MODEL, ROOT, canonical_json, load_agent_default, load_config,
    sha256_file, sha256_text, utcnow, write_json,
)

INDEX_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-index-20260829.json"
MANIFEST_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
CONTRACT_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-contract-20260829.json"
OUTPUT_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-adjudication-20260829.json"
REPAIR_CODE_PATH = ROOT / "research_pipeline/asset_first_stri_reasoningbank_p1_core.py"
DECISION = "P1_MINIMAL_PILOT_EXECUTION_COMPLETE_IMPLEMENTATION_UNQUALIFIED_FULL_P1_HOLD"
TRANSIENT = {"created_at_utc", "finished_at_utc", "response_id_sha256", "started_at_utc", "usage"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(value: Any) -> str:
    return sha256_text(canonical_json(value))


def _payload_valid(value: dict[str, Any]) -> bool:
    expected = value.get("payload_sha256")
    payload = {key: item for key, item in value.items() if key != "payload_sha256"}
    return expected == _sha(payload)


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items() if key not in TRANSIENT}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    return value


def _r2(run: dict[str, Any]) -> Any:
    return _clean(run.get("R2_first_behavioral_decision"))


def _r3(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "requests": run.get("R1_model_visible_requests") or [],
        "responses": _clean(run.get("model_responses") or []),
        "messages": run.get("messages") or [],
        "actions": _clean(run.get("R3_actions") or []),
    }


def _r4(run: dict[str, Any]) -> dict[str, Any]:
    outcome = run.get("R4_terminal_outcome") or {}
    keys = (
        "evaluator", "swebench_wheel_sha256", "eval_script_sha256",
        "test_patch_sha256", "log_parser", "status_map", "FAIL_TO_PASS",
        "PASS_TO_PASS", "valid", "resolved", "all_fail_to_pass", "all_pass_to_pass",
    )
    return {key: copy.deepcopy(outcome.get(key)) for key in keys}


def _blank_positions(run: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for request_i, request in enumerate(run.get("R1_model_visible_requests") or [], 1):
        for message_i, message in enumerate(request.get("input") or []):
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                result.append({"request_index": request_i, "message_index": message_i, "role": message.get("role")})
    return result


def _safe_failure(failure: Any) -> dict[str, Any] | None:
    if not isinstance(failure, dict):
        return None
    error = ((failure.get("detail") or {}).get("error") or {})
    return {
        "failure_layer": failure.get("failure_layer"),
        "error_type": failure.get("error_type"),
        "status_code": failure.get("status_code"),
        "provider_error_code": error.get("code"),
        "provider_error_type": error.get("type"),
        "provider_error_param": error.get("param"),
        "credential_material_present": bool(failure.get("credential_material_present")),
    }


def _summary(run: dict[str, Any], path: str, file_sha: str, file_valid: bool) -> dict[str, Any]:
    actions = run.get("R3_actions") or []
    responses = run.get("model_responses") or []
    r0 = run.get("R0_representation_retrieval_state") or {}
    r2 = _r2(run)
    r4 = run.get("R4_terminal_outcome") or {}
    counts = collections.Counter(str(row.get("type")) for row in actions)
    first_request = (run.get("R1_model_visible_requests") or [None])[0]
    return {
        "run_id": run.get("run_id"), "instance_id": run.get("instance_id"), "arm": r0.get("arm"),
        "artifact": {
            "path": path, "file_sha256": file_sha, "file_sha256_valid": file_valid,
            "payload_sha256": run.get("payload_sha256"), "payload_sha256_valid": _payload_valid(run),
        },
        "R0": {
            "state_sha256": _sha(r0), "selected_memory_sha256": run.get("selected_memory_sha256"),
            "eligible_case_count": len(r0.get("eligible_cases") or []),
            "selected_case": r0.get("selected_case"), "top_k": r0.get("top_k"),
        },
        "R1": {
            "first_request_sha256": _sha(first_request),
            "request_count": len(run.get("R1_model_visible_requests") or []),
            "blank_content_positions": _blank_positions(run),
        },
        "R2": {
            "state_sha256": _sha(r2), "type": (r2 or {}).get("type"),
            "action_sha256": sha256_text(str((r2 or {}).get("action") or "")),
            "observation_sha256": sha256_text(str((r2 or {}).get("model_visible_observation") or "")),
            "returncode": (r2 or {}).get("returncode"), "timed_out": (r2 or {}).get("timed_out"),
        },
        "R3": {
            "trajectory_sha256": _sha(_r3(run)), "action_count": len(actions),
            "shell_action_count": counts.get("shell", 0),
            "format_error_count": counts.get("format_error", 0),
            "timed_out_steps": [int(row.get("step") or 0) for row in actions if row.get("timed_out") is True],
            "response_count": len(responses),
            "all_resolved_models_exact": all(row.get("resolved_model") == MODEL for row in responses),
            "empty_response_text_steps": [
                i for i, row in enumerate(responses, 1) if not str(row.get("text") or "").strip()
            ],
        },
        "R4": {
            "outcome_sha256": _sha(_r4(run)), "valid": r4.get("valid"),
            "resolved": r4.get("resolved"), "all_fail_to_pass": r4.get("all_fail_to_pass"),
            "all_pass_to_pass": r4.get("all_pass_to_pass"),
            "status_map_sha256": _sha(r4.get("status_map") or {}),
        },
        "exit_status": run.get("exit_status", run.get("execution_status")),
        "failure": _safe_failure(run.get("failure")),
        "resource_accounting": copy.deepcopy(run.get("resource_accounting") or {}),
        "runtime_checks": {
            "base_state_valid": (((run.get("runtime") or {}).get("receipt") or {}).get("base_commit_receipt", {}).get("returncode") == 0),
            "pid_namespace": (run.get("runtime") or {}).get("pid_namespace"),
            "platform": (run.get("runtime") or {}).get("platform"),
        },
        "scientific_boundary": copy.deepcopy(run.get("scientific_boundary") or {}),
    }


def _pair(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    first_left = (left.get("R1_model_visible_requests") or [None])[0]
    first_right = (right.get("R1_model_visible_requests") or [None])[0]
    memory_equal = left.get("selected_memory") == right.get("selected_memory")
    r1_equal = canonical_json(first_left) == canonical_json(first_right)
    r2_equal = canonical_json(_r2(left)) == canonical_json(_r2(right))
    r3_equal = canonical_json(_r3(left)) == canonical_json(_r3(right))
    r4_equal = canonical_json(_r4(left)) == canonical_json(_r4(right))
    if not memory_equal:
        divergence = "R0_SELECTED_MEMORY"
    elif not r1_equal:
        divergence = "R1"
    elif not r2_equal:
        divergence = "R2"
    elif not r3_equal:
        divergence = "R3"
    elif not r4_equal:
        divergence = "R4"
    else:
        divergence = "NONE"
    return {
        "arms": [
            (left.get("R0_representation_retrieval_state") or {}).get("arm"),
            (right.get("R0_representation_retrieval_state") or {}).get("arm"),
        ],
        "R0_selected_memory_equal": memory_equal,
        "R1_first_request_byte_equal": r1_equal,
        "R2_equal_excluding_timestamps": r2_equal,
        "R3_equal_under_preregistered_canonicalization": r3_equal,
        "R4_equal": r4_equal,
        "resolved_equal": (
            (left.get("R4_terminal_outcome") or {}).get("resolved")
            == (right.get("R4_terminal_outcome") or {}).get("resolved")
        ),
        "exit_status_equal": left.get("exit_status") == right.get("exit_status"),
        "first_model_visible_divergence": divergence,
    }


def build_adjudication(
    *, index_path: Path = INDEX_PATH, manifest_path: Path = MANIFEST_PATH,
    contract_path: Path = CONTRACT_PATH, adjudicated_at_utc: str | None = None,
) -> dict[str, Any]:
    index, manifest, contract = _load(index_path), _load(manifest_path), _load(contract_path)
    runs: dict[tuple[str, str], dict[str, Any]] = {}
    summaries, file_checks = [], []
    for index_row in index.get("completed_runs") or []:
        path = ROOT / str(index_row["path"])
        actual_sha, run = sha256_file(path), _load(path)
        arm = str((run.get("R0_representation_retrieval_state") or {}).get("arm"))
        key = (str(run.get("instance_id")), arm)
        if key in runs:
            raise ValueError(f"duplicate pilot run: {key}")
        runs[key] = run
        file_valid = actual_sha == index_row.get("file_sha256")
        file_checks.append(file_valid)
        summaries.append(_summary(run, str(path.relative_to(ROOT)), actual_sha, file_valid))

    instances = sorted({instance for instance, _ in runs})
    expected = {(instance, arm) for instance in instances for arm in "ABCDE"}
    all_present = (
        index.get("execution_complete") is True
        and index.get("planned_run_count") == 10
        and len(runs) == 10 and set(runs) == expected
    )
    manifest_alignment = all(
        runs[instance, arm].get("R0_representation_retrieval_state") == manifest["arms"][arm]["R0"]
        and runs[instance, arm].get("selected_memory") == manifest["arms"][arm]["R0"]["selected_memory"]
        for instance, arm in expected
    )
    b_items = manifest["arms"]["B"]["R0"]["eligible_cases"][0]["memory_items"]
    c_items = manifest["arms"]["C"]["R0"]["eligible_cases"][0]["memory_items"]
    treatment_checks = {
        "manifest_payload_sha256_valid": _payload_valid(manifest),
        "run_R0_and_selected_memory_match_manifest": manifest_alignment,
        "five_R0_treatment_hashes_distinct": len({
            manifest["arms"][arm]["treatment_sha256"] for arm in "ABCDE"
        }) == 5,
        "A_B_selected_memory_equal": (
            manifest["arms"]["A"]["R0"]["selected_memory"]
            == manifest["arms"]["B"]["R0"]["selected_memory"]
        ),
        "B_E_selected_memory_equal": (
            manifest["arms"]["B"]["R0"]["selected_memory"]
            == manifest["arms"]["E"]["R0"]["selected_memory"]
        ),
        "C_is_B_item_order_reversal": c_items == list(reversed(b_items)),
        "D_is_preregistered_top1_first_fragment": (
            manifest["arms"]["D"]["R0"]["top_k"] == 1
            and len(manifest["arms"]["D"]["R0"]["eligible_cases"]) == 2
            and manifest["arms"]["D"]["R0"]["selected_memory"] == b_items[0]
        ),
    }
    pair_specs = {
        "A_vs_B": ("A", "B"), "A_vs_E": ("A", "E"), "B_vs_E": ("B", "E"),
        "A_vs_C": ("A", "C"), "A_vs_D": ("A", "D"),
    }
    comparisons = {
        instance: {
            name: _pair(runs[instance, left], runs[instance, right])
            for name, (left, right) in pair_specs.items()
        }
        for instance in instances
    }

    provider_failures = [
        row for row in summaries if (row.get("failure") or {}).get("failure_layer") == "provider"
    ]
    diagnosed = [
        row for row in provider_failures
        if row["R3"]["timed_out_steps"] and row["R1"]["blank_content_positions"]
        and (row.get("failure") or {}).get("provider_error_code") == "MissingParameter"
        and (row.get("failure") or {}).get("provider_error_param") == "input.content"
    ]
    config, official_template = load_config(), str(load_agent_default("timeout_template"))
    diagnosis_complete = (
        len(provider_failures) == 3 and len(diagnosed) == 3
        and "timeout_template" not in config["agent"] and bool(official_template.strip())
    )
    boundary = {
        "gold_patch_model_visible": False, "test_patch_model_visible": False,
        "evaluator_script_model_visible": False,
    }
    ab_equal = all(
        comparisons[instance]["A_vs_B"]["R0_selected_memory_equal"]
        and comparisons[instance]["A_vs_B"]["R1_first_request_byte_equal"]
        for instance in instances
    )
    be_equal = all(
        comparisons[instance]["B_vs_E"]["R0_selected_memory_equal"]
        and comparisons[instance]["B_vs_E"]["R1_first_request_byte_equal"]
        for instance in instances
    )
    qualification_checks = {
        "all_10_planned_runs_persisted_without_replacement": all_present,
        "all_index_file_sha256_values_valid": all(file_checks),
        "index_payload_sha256_valid": _payload_valid(index),
        "all_run_payload_sha256_values_valid": all(
            row["artifact"]["payload_sha256_valid"] for row in summaries
        ),
        "treatments_match_frozen_manifest": all(treatment_checks.values()),
        "resolved_model_exact_for_all_completed_provider_responses": all(
            row["R3"]["all_resolved_models_exact"] for row in summaries
        ),
        "fresh_base_state_receipts_valid": all(
            row["runtime_checks"]["base_state_valid"] for row in summaries
        ),
        "all_evaluator_outputs_valid": all(row["R4"]["valid"] is True for row in summaries),
        "evaluator_only_content_absent_from_model_requests": all(
            row["scientific_boundary"] == boundary for row in summaries
        ),
        "A_B_selected_memory_and_first_R1_equal_per_task": ab_equal,
        "B_E_selected_memory_and_first_R1_equal_per_task": be_equal,
        "no_blank_model_visible_message_content": all(
            not row["R1"]["blank_content_positions"] for row in summaries
        ),
        "no_terminal_provider_or_implementation_failure": all(
            not row.get("failure") for row in summaries
        ),
    }
    implementation_qualified = all(qualification_checks.values())

    by_instance = {}
    for instance in instances:
        rows = [row for row in summaries if row["instance_id"] == instance]
        by_instance[instance] = {
            "submitted_count": sum(row["exit_status"] == "Submitted" for row in rows),
            "provider_failure_count": sum(
                (row.get("failure") or {}).get("failure_layer") == "provider" for row in rows
            ),
            "valid_evaluator_count": sum(row["R4"]["valid"] is True for row in rows),
            "resolved_count": sum(row["R4"]["resolved"] is True for row in rows),
            "all_five_R4_outcomes_equal": len({row["R4"]["outcome_sha256"] for row in rows}) == 1,
        }

    state = {
        "schema_version": 1,
        "adjudication_id": "E1-STRI-REASONINGBANK-P1-MINIMAL-PILOT-ADJUDICATION-20260829",
        "adjudicated_at_utc": adjudicated_at_utc or utcnow(),
        "decision": DECISION, "execution_complete": all_present,
        "implementation_qualified": implementation_qualified,
        "scientific_population_claim_authorized": False,
        "full_p1_authorized": False, "reruns_or_replacements_performed": False,
        "bindings": {
            "minimal_pilot_index": str(index_path.relative_to(ROOT)),
            "minimal_pilot_index_file_sha256": sha256_file(index_path),
            "treatment_manifest": str(manifest_path.relative_to(ROOT)),
            "treatment_manifest_file_sha256": sha256_file(manifest_path),
            "minimal_pilot_contract": str(contract_path.relative_to(ROOT)),
            "minimal_pilot_contract_file_sha256": sha256_file(contract_path),
            "repair_code": str(REPAIR_CODE_PATH.relative_to(ROOT)),
            "repair_code_sha256": sha256_file(REPAIR_CODE_PATH),
            "frozen_official_agent_path": str(AGENT_PATH),
            "frozen_official_agent_sha256": sha256_file(AGENT_PATH),
        },
        "treatment_checks": treatment_checks, "qualification_checks": qualification_checks,
        "failure_adjudication": {
            "observed_terminal_provider_failure_count": len(provider_failures),
            "affected_runs": [row["run_id"] for row in diagnosed],
            "observed_chain": [
                "shell action exceeded the frozen 60-second environment timeout",
                "compatibility harness rendered a blank timeout observation because YAML omitted an official AgentConfig default",
                "the next serialized request contained a blank user content item",
                "Ark rejected that request with HTTP 400 MissingParameter input.content",
            ],
            "causal_chain_confirmed_from_persisted_runs_and_frozen_source": diagnosis_complete,
            "failure_layer": "implementation_compatibility_layer",
            "not_attributed_to": [
                "hf-mirror acquisition", "fixed OCI image digest",
                "resolved DeepSeek-Pro identity", "SWE-bench evaluator validity",
                "ReasoningBank scientific mechanism",
            ],
        },
        "repair_receipt": {
            "status": "CODE_REPAIRED_WITHOUT_RETROSPECTIVE_REQUALIFICATION",
            "repair": (
                "Load frozen official AgentConfig.timeout_template when YAML omits it "
                "and reject an empty rendered timeout observation."
            ),
            "official_default_template_sha256": sha256_text(official_template),
            "treatment_changed": False, "model_or_sampling_changed": False,
            "source_or_evaluation_cases_changed": False,
            "historical_run_artifacts_changed": False, "rerun_performed": False,
            "qualification_restored": False,
            "test": (
                "ReasoningBankP1FrozenRuntimeTest."
                "test_timeout_uses_nonempty_frozen_agent_default_when_yaml_omits_it"
            ),
        },
        "run_summaries": sorted(
            summaries, key=lambda row: (row["instance_id"], "ABCDE".index(row["arm"]))
        ),
        "comparisons": comparisons,
        "descriptive_outcomes": {
            "all_runs": {
                "planned": 10, "persisted": len(summaries),
                "submitted": sum(row["exit_status"] == "Submitted" for row in summaries),
                "provider_failures": len(provider_failures),
                "resolved": sum(row["R4"]["resolved"] is True for row in summaries),
                "valid_evaluators": sum(row["R4"]["valid"] is True for row in summaries),
            },
            "by_instance": by_instance,
            "model_visible_equivalence": {
                "A_B_first_R1_equal_on_both_tasks": ab_equal,
                "B_E_first_R1_equal_on_both_tasks": be_equal,
                "A_B_first_behavioral_decision_equal_on_any_task": any(
                    comparisons[instance]["A_vs_B"]["R2_equal_excluding_timestamps"]
                    for instance in instances
                ),
                "B_E_first_behavioral_decision_equal_on_any_task": any(
                    comparisons[instance]["B_vs_E"]["R2_equal_excluding_timestamps"]
                    for instance in instances
                ),
            },
        },
        "scientific_interpretation": {
            "authorized_descriptive_observations": [
                "A/B and B/E selected memory and first serialized request are equal on both tasks.",
                "Those equal first requests diverge at R2 on both tasks under unseeded execution.",
                "All five pytest arms resolve; all five sympy arms remain unresolved.",
                "The observed ten-run sample has no R4 treatment difference.",
            ],
            "claim_ceiling": (
                "The fixed DeepSeek-Pro pilot confirms R1 reunion/placebo equivalence "
                "and immediate stochastic R2 divergence, but no population claim."
            ),
            "why_no_mechanism_claim": (
                "Three sympy arms terminated through a compatibility-layer "
                "timeout-observation bug, making the global pilot implementation-unqualified."
            ),
            "D_is_not_a_performance_advantage": True,
            "B_E_exit_difference_is_instability_evidence_not_case_id_effect": True,
        },
        "next_authority": {
            "full_p1": "HOLD", "automatic_retry": "FORBIDDEN",
            "replacement_task": "FORBIDDEN", "paper_result_claim": "HOLD",
            "possible_future_action": (
                "A new independently preregistered qualification pilot may use the repaired "
                "harness but cannot replace or relabel these ten runs."
            ),
        },
        "credential_material_present": False,
    }
    errors = validate_adjudication(state)
    if errors:
        raise ValueError("invalid P1 pilot adjudication: " + "; ".join(errors))
    return state


def validate_adjudication(state: dict[str, Any]) -> list[str]:
    errors = []
    if state.get("decision") != DECISION:
        errors.append("decision mismatch")
    if state.get("execution_complete") is not True:
        errors.append("execution must be complete")
    if state.get("implementation_qualified") is not False:
        errors.append("pilot must remain implementation-unqualified")
    if state.get("scientific_population_claim_authorized") is not False:
        errors.append("population claim must remain unauthorized")
    if state.get("full_p1_authorized") is not False:
        errors.append("full P1 must remain closed")
    if state.get("reruns_or_replacements_performed") is not False:
        errors.append("no rerun or replacement allowed")
    checks = state.get("qualification_checks") or {}
    if checks.get("all_10_planned_runs_persisted_without_replacement") is not True:
        errors.append("ten-run persistence failed")
    if checks.get("no_blank_model_visible_message_content") is not False:
        errors.append("blank timeout observations must remain visible")
    if checks.get("no_terminal_provider_or_implementation_failure") is not False:
        errors.append("terminal compatibility failures must remain visible")
    failure = state.get("failure_adjudication") or {}
    if failure.get("observed_terminal_provider_failure_count") != 3:
        errors.append("expected three terminal provider errors")
    if failure.get("causal_chain_confirmed_from_persisted_runs_and_frozen_source") is not True:
        errors.append("timeout-to-empty-content chain not confirmed")
    repair = state.get("repair_receipt") or {}
    if (
        repair.get("historical_run_artifacts_changed") is not False
        or repair.get("rerun_performed") is not False
        or repair.get("qualification_restored") is not False
    ):
        errors.append("repair cannot rewrite or requalify history")
    runs = state.get("run_summaries") or []
    if len(runs) != 10 or {row.get("arm") for row in runs} != set("ABCDE"):
        errors.append("run summary coverage mismatch")
    for instance, rows in (state.get("comparisons") or {}).items():
        for pair in ("A_vs_B", "B_vs_E"):
            row = rows.get(pair) or {}
            if (
                row.get("R0_selected_memory_equal") is not True
                or row.get("R1_first_request_byte_equal") is not True
                or row.get("first_model_visible_divergence") != "R2"
            ):
                errors.append(f"{instance} {pair} ladder mismatch")
    return errors


def write_adjudication(output_path: Path = OUTPUT_PATH) -> dict[str, Any]:
    state = build_adjudication()
    write_json(output_path, state)
    return _load(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    result = write_adjudication(args.output)
    print(json.dumps({
        "decision": result["decision"],
        "payload_sha256": result["payload_sha256"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
