from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
ROOT_CAUSE = GENERATED / "agent-constraint-externality-f0-uptake-root-cause-20260903.json"
SELECTION = GENERATED / "agent-constraint-externality-capability-backbone-selection-final-20260903.json"
CURRENT_F0 = GENERATED / "agent-constraint-externality-f0-source-closeout-mimo25pro-20260903.json"
OUTPUT = GENERATED / "agent-constraint-externality-f0-r1-source-failure-qualification-proposal-20260903.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verified(path: Path, status: str) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise RuntimeError(f"unexpected artifact: {path}")
    claimed = payload.get("content_sha256")
    if claimed:
        unsigned = dict(payload)
        unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RuntimeError(f"content hash mismatch: {path}")
    return payload


def build() -> dict[str, Any]:
    root_cause = _verified(ROOT_CAUSE, "CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY")
    selection = _verified(SELECTION, "CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS")
    current = _verified(CURRENT_F0, "F0_UPDATE_UPTAKE_FAIL_SOURCE_CLOSEOUT")
    if current["eligible_repair_family_count"] != 0 or current["probe_episode_count"] != 0:
        raise RuntimeError("current F0 boundary drifted")
    payload: dict[str, Any] = {
        "schema_version": "ace-f0-r1-source-failure-qualification-proposal-v1",
        "object_id": OBJECT_ID,
        "status": "PROSPECTIVE_F0_R1_SOURCE_FAILURE_QUALIFICATION_PROPOSAL_ONLY",
        "motivation": "Separate general tool capability from the distinct prerequisite that a target-local source episode must actually yield enough usable target failures for automatic repair generation.",
        "selected_backbone_policy": {
            "retain_selected_backbone": True,
            "selected_backbone": selection["selected_backbone"],
            "reason": "MiMo 2.5 Pro passed the frozen general capability gate. The current F0 stop was caused by source-failure opportunity, not backbone capability or coupling-mechanism evidence.",
            "no_post_f0_backbone_switch": True,
        },
        "estimand_boundary": {
            "mechanism_question_unchanged": True,
            "conditional_population": "TARGET_FAILURES_THAT_YIELD_FROZEN_TARGET_LOCAL_REPAIRS",
            "primary_contrast": "UE_HIGH_MINUS_UE_INDEPENDENT_WITHIN_REPAIR_FAMILY",
            "current_f0_contributes_mechanism_effect_samples": 0,
        },
        "sq0_source_failure_qualification": {
            "purpose": "Calibrate target-local challenge difficulty before any new decisive F0-R1 probe execution.",
            "new_unobserved_instances_required": True,
            "reuse_current_f0_source_instances": False,
            "suggested_qualification_instance_count": 12,
            "family_balance": {"FG_like": 6, "TNF_like": 6},
            "target_only": True,
            "non_target_constraints_visible": False,
            "coupling_label_visible": False,
            "probe_outcomes_visible": False,
            "challenge_recipe_requirement": "The target-local challenge transformation must be defined outcome-blind and must not alter non-target topology. The same frozen target-local challenge recipe must later be present in every source/probe member of a confirmatory family.",
            "usable_target_failure_definition": [
                "terminal scientific episode",
                "no provider/interface/harness/malformed-tool failure",
                "target evaluator false",
                "durable target-relevant tool trajectory available for updater input",
            ],
            "suggested_admission_window": {
                "usable_target_failure_rate_min": 0.75,
                "usable_target_failure_rate_max": 0.90,
                "rationale": "Below 0.75 repeats the repair-opportunity shortage; a near-1.0 failure rate risks a challenge beyond the selected backbone's practically repairable regime.",
            },
            "scientific_claim_authority": False,
        },
        "f0_r1_confirmatory_design": {
            "new_unobserved_confirmatory_families_required": True,
            "reuse_current_ACE_FG_01_to_04_or_ACE_TNF_01_to_04_as_confirmatory_families": False,
            "suggested_family_count": 8,
            "source_per_family": 1,
            "source_is_target_only": True,
            "probe_arms": ["INDEPENDENT", "LOW", "HIGH"],
            "probe_branches": ["NO_UPDATE", "UPDATE"],
            "probe_seeds": [1201, 1202, 1203],
            "same_target_local_challenge_across_source_and_all_probe_arms": True,
            "same_update_bytes_across_all_update_replays": True,
            "minimum_usable_repair_families": 6,
            "probe_execution_only_after_all_source_results_and_repair_bytes_are_frozen_and_content_addressed": True,
            "partial_probe_effects_readable_during_execution": False,
            "primary_metric_and_adjudication_should_remain_unchanged_unless_a_new_contract_explicitly_justifies_a_change": True,
        },
        "design_guardrails": {
            "do_not_lower_six_repair_threshold_using_current_outcome": True,
            "do_not_modify_and_replay_current_f0_source_instances": True,
            "do_not_generate_repair_without_observed_target_failure": True,
            "do_not_read_or_optimize_on_decisive_probe_outcomes_during_source_qualification": True,
            "do_not_treat_current_f0_update_uptake_fail_as_mechanism_not_supported": True,
            "current_f0_remains_immutable": True,
        },
        "next_high_information_step": "Build only the new SQ0 target-challenge qualification set and statically audit source/probe target-local equivalence before requesting any new model execution authority.",
        "authority": {
            "design_only": True,
            "sq0_execution": False,
            "f0_r1_execution": False,
            "current_f0": False,
            "probe": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "paper_claim": False,
        },
        "lineage": {
            "root_cause_artifact": str(ROOT_CAUSE.relative_to(ROOT)),
            "root_cause_content_sha256": root_cause["content_sha256"],
            "selected_backbone_artifact": str(SELECTION.relative_to(ROOT)),
            "selected_backbone_content_sha256": selection["content_sha256"],
            "current_f0_source_closeout_artifact": str(CURRENT_F0.relative_to(ROOT)),
            "current_f0_source_closeout_content_sha256": current["content_sha256"],
        },
        "provider_requests": 0,
        "scientific_outcomes_observed": 0,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "selected_backbone": payload["selected_backbone_policy"]["selected_backbone"]["model_id"],
        "suggested_sq0_instances": payload["sq0_source_failure_qualification"]["suggested_qualification_instance_count"],
        "suggested_f0_r1_families": payload["f0_r1_confirmatory_design"]["suggested_family_count"],
        "execution_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
