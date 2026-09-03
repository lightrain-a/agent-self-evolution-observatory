from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v5_build import load_cases
from research_pipeline.agent_constraint_externality_sq0_v5_live import _unit_id

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
RESULT = GENERATED / "agent-constraint-externality-sq0-v5-mimo25pro-result-20260903.json"
CONTRACT = GENERATED / "agent-constraint-externality-sq0-v5-mimo25pro-execution-contract-20260903.json"
V2_VOID = GENERATED / "agent-constraint-externality-sq0-v2-harness-contamination-void-20260903.json"
RUNTIME = ROOT / "runtimes/agent-constraint-externality-sq0-v5-mimo25pro-20260903"
LEDGER = RUNTIME / "ledger.jsonl"
CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v5-final-closeout-20260903.json"
ROOT_CAUSE = GENERATED / "agent-constraint-externality-sq0-v5-final-root-cause-20260903.json"
FAILED_CASE = "SQ0V5-TNF-01"
FAILED_TOOL = "read_file"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"Content hash mismatch: {path}")
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    result = _verified(RESULT, "SQ0_V5_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP")
    contract = _verified(CONTRACT, "SQ0_V5_MIMO25PRO_EXECUTION_AUTHORIZED")
    v2_void = _verified(V2_VOID, "SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION")
    if contract.get("execution_policy", {}).get("failure_to_pass_disposition") != "STOP_SQ0_DEVELOPMENT_NO_V6":
        raise RuntimeError("V5 final stop rule drifted.")
    if result.get("non_semantic_failure_units") != [_unit_id(FAILED_CASE)]:
        raise RuntimeError("V5 invalid unit drifted.")
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    dispatch = [r for r in rows if r.get("event") == "DISPATCH"]
    completion = [r for r in rows if r.get("event") == "COMPLETION"]
    failure = [r for r in rows if r.get("event") == "FAILURE"]
    if len(dispatch) != 7 or len(completion) != 6 or len(failure) != 1:
        raise RuntimeError("V5 terminal ledger shape drifted.")
    f = failure[0]
    if f.get("case_id") != FAILED_CASE or f.get("failure_class") != "HARNESS_OR_PROVIDER_INTERFACE_STOP" or f.get("message") != FAILED_TOOL or f.get("retry_attempted") is not False:
        raise RuntimeError("V5 failure classification drifted.")
    expected_ids = {_unit_id(c["case_id"]) for c in load_cases()}
    dispatched_ids = {r["unit_id"] for r in dispatch}
    terminal_ids = {r["unit_id"] for r in completion + failure}
    undispatched = sorted(expected_ids - dispatched_ids)
    if len(terminal_ids) != 7 or len(undispatched) != 5:
        raise RuntimeError("V5 audited terminal/undispatched counts drifted.")
    if any(r.get("kind") != "FG_SEMANTIC_V5" for r in completion):
        raise RuntimeError("V5 pre-contamination completions are not exactly six FG cases.")
    if not all(r.get("tool_loop_completed") and r.get("usable_target_failure") and not r.get("target_success") and not r.get("non_semantic_failure") for r in completion):
        raise RuntimeError("V5 completed FG semantic-failure evidence drifted.")
    failed_dispatch = next(r for r in dispatch if r["unit_id"] == f["unit_id"])
    before = failed_dispatch.get("codingplan_window_before", {})
    after = f.get("codingplan_window_after", {})
    failed_window_delta = None
    if before.get("next_reset_at") == after.get("next_reset_at"):
        failed_window_delta = int(after["used"]) - int(before["used"])
    if failed_window_delta != 3:
        raise RuntimeError("V5 failed-unit CodingPlan account-window delta drifted.")
    progress_path = RUNTIME / "episodes/sq0v5-tnf-01/bridge-progress.json"
    progress = _read(progress_path)
    if progress.get("tool_call_count") != 3 or progress.get("status") != "CLOSED_STATE_SAVED":
        raise RuntimeError("V5 failed-unit AppWorld progress drifted.")
    v2_root = v2_void.get("root_cause", {})
    if v2_root.get("classification") != "ATOMCODE_NATIVE_TOOL_SCHEMA_CONTAMINATION":
        raise RuntimeError("Historical V2 contamination lineage drifted.")

    root: dict[str, Any] = {
        "schema_version": "ace-sq0-v5-final-root-cause-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V5_RECURRENT_ATOMCODE_NATIVE_READ_FILE_CONTAMINATION_FINAL_STOP",
        "development_iteration": 5,
        "final_calibration_iteration": True,
        "failed_case_id": FAILED_CASE,
        "failed_unit_id": f["unit_id"],
        "failure_class": f["failure_class"],
        "attempted_native_tool": FAILED_TOOL,
        "appworld_tool_calls_before_native_attempt": 3,
        "codingplan_account_window_requests_in_failed_unit": failed_window_delta,
        "retry_attempted": False,
        "historical_collision": {
            "artifact": str(V2_VOID.relative_to(ROOT)),
            "status": v2_void["status"],
            "root_cause_classification": v2_root["classification"],
            "same_native_tool_family": True,
        },
        "diagnosis": [
            "The official AtomCode signed runtime again exposed or elicited the native read_file tool inside a long AppWorld-only task despite an MCP-only scientific instruction and a client permission guard.",
            "The guard correctly prevented the native tool from becoming AppWorld scientific evidence, but the attempted tool invalidates the qualification by the prospectively frozen non-semantic-failure rule.",
            "The zero-request MCP Q1 establishes that AppWorld tools were mounted before dispatch; it does not prove that native coding tools are absent from the model-visible tool schema during a long live turn.",
            "This recurs the earlier SQ0-V2 native read_file contamination class, so another difficulty calibration iteration would conflate target-failure calibration with unresolved transport isolation.",
        ],
        "scientific_interpretation_boundary": (
            "The six completed fresh FG cases are retained as development observations and all six were usable semantic target failures, "
            "but the V5 qualification as a whole is invalid. No inference about the final 12-case failure rate or F0-R1 readiness is permitted."
        ),
        "future_transport_requirement_if_research_is_reopened": (
            "Use a provider/runtime in which non-AppWorld native coding tools are absent from the model-visible tool schema, rather than merely denied after model selection; qualify that transport prospectively on fresh non-scientific cases before any new source-failure calibration."
        ),
        "provider_requests_added": 0,
        "scientific_effects_observed": 0,
        "authority": {"sq0": False, "sq0_v6": False, "f0_r1": False, "probe": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    root["content_sha256"] = sha256_value(root)

    closeout: dict[str, Any] = {
        "schema_version": "ace-sq0-v5-final-closeout-v1",
        "object_id": OBJECT_ID,
        "status": "SQ0_V5_FINAL_CALIBRATION_INVALID_STOP_NO_V6",
        "verdict": result["status"],
        "result_artifact": str(RESULT.relative_to(ROOT)),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["content_sha256"],
        "ledger_sha256": sha256_file(LEDGER),
        "planned_case_count": 12,
        "scientific_completion_count": 6,
        "terminal_failure_count": 1,
        "terminal_case_count": 7,
        "true_never_dispatched_case_count": 5,
        "raw_result_remaining_undispatched_case_count": result.get("remaining_undispatched_case_count"),
        "raw_result_accounting_clarification": (
            "The frozen adjudicator computed CASE_COUNT-completion_count and therefore reported 6; one of those six is actually the terminal failed TNF-01 unit. "
            "The append-only ledger proves 7 terminal units and 5 never-dispatched units. This clarification does not alter the invalid-stop verdict."
        ),
        "completed_usable_target_failure_count": 6,
        "completed_target_success_count": 0,
        "completed_case_failure_rate": 1.0,
        "qualification_rate_inference_allowed": False,
        "invalid_unit": f["unit_id"],
        "failure_class": f["failure_class"],
        "attempted_native_tool": FAILED_TOOL,
        "accounting": {
            "completed_case_scientific_model_round_count": int(result.get("scientific_model_round_count", 0)),
            "completed_case_appworld_tool_call_total": int(result.get("appworld_tool_call_total", 0)),
            "completed_case_prompt_tokens_total": int(result.get("prompt_tokens_total", 0)),
            "completed_case_completion_tokens_total": int(result.get("completion_tokens_total", 0)),
            "failed_unit_appworld_tool_calls_before_stop": 3,
            "failed_unit_account_window_request_delta": failed_window_delta,
            "failed_unit_scientific_model_round_count": "NOT_CANONICALLY_RECORDED_IN_FAILURE_ROW_DO_NOT_INFER",
        },
        "undispatched_unit_ids": undispatched,
        "root_cause_content_sha256": root["content_sha256"],
        "failure_to_pass_disposition": "STOP_SQ0_DEVELOPMENT_NO_V6",
        "development_only": True,
        "confirmatory_reuse": False,
        "scientific_effects_observed": 0,
        "authority": {"sq0": False, "sq0_v6": False, "f0_r1": False, "probe": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    closeout["content_sha256"] = sha256_value(closeout)
    return closeout, root


def main() -> None:
    closeout, root = build()
    CLOSEOUT.write_text(json.dumps(closeout, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ROOT_CAUSE.write_text(json.dumps(root, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": closeout["status"],
        "terminal_cases": closeout["terminal_case_count"],
        "never_dispatched": closeout["true_never_dispatched_case_count"],
        "invalid_unit": closeout["invalid_unit"],
        "native_tool": closeout["attempted_native_tool"],
        "sq0_v6_authorized": False,
        "f0_r1_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
