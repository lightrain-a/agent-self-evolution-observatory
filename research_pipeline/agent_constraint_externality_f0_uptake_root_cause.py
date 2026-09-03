from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
CAPABILITY_RESULT = GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-result-20260903.json"
SOURCE_CLOSEOUT = GENERATED / "agent-constraint-externality-f0-source-closeout-mimo25pro-20260903.json"
ADJUDICATION = GENERATED / "agent-constraint-externality-f0-adjudication-mimo25pro-20260903.json"
PROTOCOL = GENERATED / "agent-constraint-externality-f0-frozen-protocol-20260831.json"
OUTPUT = GENERATED / "agent-constraint-externality-f0-uptake-root-cause-20260903.json"

CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
F0_FAMILIES = (
    "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
    "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, *, status: str | None = None, verdict: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"status mismatch: {path}: {payload.get('status')}")
    if verdict is not None and payload.get("verdict") != verdict:
        raise RuntimeError(f"verdict mismatch: {path}: {payload.get('verdict')}")
    claimed = payload.get("content_sha256")
    if claimed:
        unsigned = dict(payload)
        unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"content hash mismatch: {path}")
    return payload


def _row(families: dict[str, dict[str, Any]], family_id: str, *, source: bool) -> dict[str, Any]:
    family = families[family_id]
    if source:
        arm = next(row for row in family["arms"] if row["coupling_level"] == "INDEPENDENT")
        instruction = family["target_instruction"]
        constraints = [row for row in arm["constraints"] if row["role"] == "TARGET"]
        kind = "F0_TARGET_ISOLATED_SOURCE"
    else:
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        instruction = arm["task_instruction"]
        constraints = arm["constraints"]
        kind = "CAPABILITY_LOW_FULL_CONSTRAINT_TASK"
    return {
        "family_id": family_id,
        "kind": kind,
        "instruction_word_count": len(instruction.split()),
        "constraint_count": len(constraints),
        "target_constraint_count": sum(row["role"] == "TARGET" for row in constraints),
        "non_target_constraint_count": sum(row["role"] == "NON_TARGET" for row in constraints),
        "app_count": len(family["fixture"]["apps"]),
        "tool_call_cap": int(arm["matching"]["tool_budget"]),
    }


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def build() -> dict[str, Any]:
    capability = _verified(CAPABILITY_RESULT, status="CAPABILITY_CALIBRATION_PASS")
    source = _verified(SOURCE_CLOSEOUT, status="F0_UPDATE_UPTAKE_FAIL_SOURCE_CLOSEOUT", verdict="F0_UPDATE_UPTAKE_FAIL")
    adjudication = _verified(ADJUDICATION, verdict="F0_UPDATE_UPTAKE_FAIL")
    protocol = _read(PROTOCOL)
    if source["source_target_success_count"] != 8 or source["source_target_failure_count"] != 0:
        raise RuntimeError("F0 source outcome drifted from frozen 8/8 success closeout")
    if source["eligible_repair_family_count"] != 0 or source["probe_episode_count"] != 0:
        raise RuntimeError("F0 uptake-fail boundary drifted")
    if adjudication.get("further_execution_authority") is not False:
        raise RuntimeError("F0 adjudication unexpectedly permits more execution")

    spec = load_protected_spec(BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    capability_rows = [_row(families, family_id, source=False) for family_id in CAPABILITY_FAMILIES]
    source_rows = [_row(families, family_id, source=True) for family_id in F0_FAMILIES]

    capability_success_min = float(capability["gate"]["thresholds"]["target_success_min"])
    source_min_eligible = int(protocol["source_phase"]["minimum_eligible_repair_families"])
    panel_size = 8
    maximum_failures_at_capability_min_if_same_panel = panel_size - int(capability_success_min * panel_size)
    if maximum_failures_at_capability_min_if_same_panel >= source_min_eligible:
        raise RuntimeError("Expected a structural failure-opportunity mismatch but arithmetic no longer shows one")

    payload: dict[str, Any] = {
        "schema_version": "ace-f0-uptake-root-cause-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY",
        "f0_verdict": "F0_UPDATE_UPTAKE_FAIL",
        "classification": "SOURCE_FAILURE_OPPORTUNITY_DESIGN_MISMATCH",
        "not_classified_as": [
            "COUPLING_EXTERNALITY_MECHANISM_FAILURE",
            "APPWORLD_API_SUBSTRATE_FAILURE",
            "MIMO25PRO_CAPABILITY_FAILURE",
        ],
        "observed": {
            "selected_backbone_capability_target_success_rate": capability["gate"]["target_success_rate"],
            "selected_backbone_capability_tool_loop_completion_rate": capability["gate"]["tool_loop_completion_rate"],
            "f0_source_target_success_count": source["source_target_success_count"],
            "f0_source_target_failure_count": source["source_target_failure_count"],
            "eligible_repair_family_count": source["eligible_repair_family_count"],
            "updater_model_request_count": source["updater_model_request_count"],
            "probe_episode_count": source["probe_episode_count"],
            "scientific_effects_observed": 0,
        },
        "arithmetic_mismatch": {
            "capability_target_success_min": capability_success_min,
            "capability_panel_size": panel_size,
            "maximum_target_failures_when_only_meeting_capability_success_min_if_same_panel": maximum_failures_at_capability_min_if_same_panel,
            "f0_minimum_eligible_repair_families": source_min_eligible,
            "failure_shortfall_even_at_capability_success_floor": source_min_eligible - maximum_failures_at_capability_min_if_same_panel,
            "selected_backbone_capability_target_failures": 1,
            "interpretation": "The capability PASS interval does not guarantee enough target failures to instantiate the preregistered F0 repair stage; at the capability success floor it permits at most four failures while F0 requires at least six repairs.",
        },
        "structural_comparison": {
            "capability_rows": capability_rows,
            "f0_source_rows": source_rows,
            "capability_means": {
                "instruction_word_count": _mean(capability_rows, "instruction_word_count"),
                "constraint_count": _mean(capability_rows, "constraint_count"),
                "non_target_constraint_count": _mean(capability_rows, "non_target_constraint_count"),
                "app_count": _mean(capability_rows, "app_count"),
                "tool_call_cap": _mean(capability_rows, "tool_call_cap"),
            },
            "f0_source_means": {
                "instruction_word_count": _mean(source_rows, "instruction_word_count"),
                "constraint_count": _mean(source_rows, "constraint_count"),
                "non_target_constraint_count": _mean(source_rows, "non_target_constraint_count"),
                "app_count": _mean(source_rows, "app_count"),
                "tool_call_cap": _mean(source_rows, "tool_call_cap"),
            },
            "key_difference": "F0 source removes both non-target constraints but retains the same 16-call tool budget, making source failure availability an unqualified variable rather than a consequence of capability PASS.",
        },
        "prospective_repair_design_requirements": {
            "current_f0_mandatory_stop": True,
            "current_f0_source_families_may_not_be_rewritten_and_replayed": True,
            "new_execution_requires_new_prospective_contract": True,
            "dedicated_source_failure_qualification_required": True,
            "source_failure_qualification_must_precede_decisive_probe_execution": True,
            "source_failure_qualification_must_be_disjoint_from_decisive_probe_outcomes": True,
            "recommended_design_direction": "Predeclare source/probe paired instances in which the source instance provides a calibrated target-failure opportunity while the decisive probe instances preserve the matched coupling manipulation; qualify failure availability on a separate discovery/qualification split without reading any decisive probe effect.",
            "do_not_fix_by": [
                "LOWERING_THE_SIX_REPAIR_THRESHOLD_POST_OUTCOME",
                "MANUALLY_EDITING_CURRENT_SOURCE_TASKS_AND_REPLAYING",
                "SWITCHING_BACKBONE_POST_F0_OUTCOME_WITHIN_THE_SAME_CONFIRMATORY_RUN",
                "GENERATING_SYNTHETIC_REPAIRS_WITHOUT_OBSERVED_TARGET_FAILURE",
            ],
        },
        "authority": {
            "current_f0": False,
            "probe": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
            "prospective_redesign_only": True,
        },
        "lineage": {
            "capability_result_artifact": str(CAPABILITY_RESULT.relative_to(ROOT)),
            "capability_result_content_sha256": capability["content_sha256"],
            "source_closeout_artifact": str(SOURCE_CLOSEOUT.relative_to(ROOT)),
            "source_closeout_content_sha256": source["content_sha256"],
            "f0_adjudication_artifact": str(ADJUDICATION.relative_to(ROOT)),
            "f0_adjudication_content_sha256": adjudication["content_sha256"],
            "frozen_protocol_artifact": str(PROTOCOL.relative_to(ROOT)),
            "frozen_protocol_file_sha256": sha256_file(PROTOCOL),
            "v4_bundle_artifact": str(BUNDLE.relative_to(ROOT)),
            "v4_bundle_sha256": sha256_file(BUNDLE),
        },
        "provider_requests_added_by_diagnosis": 0,
        "scientific_outcomes_added_by_diagnosis": 0,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "classification": payload["classification"],
        "capability_max_failures_at_success_floor": payload["arithmetic_mismatch"]["maximum_target_failures_when_only_meeting_capability_success_min_if_same_panel"],
        "f0_minimum_repairs": payload["arithmetic_mismatch"]["f0_minimum_eligible_repair_families"],
        "f0_source_successes": payload["observed"]["f0_source_target_success_count"],
        "provider_requests_added": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
