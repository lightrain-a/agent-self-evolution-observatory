#!/usr/bin/env python3
"""Seal B1's post-R19 fresh-confirmatory reopen gate without opening outcomes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PARENTS = {
    "r19_stop": Path("generated/d2-failure-memory-provenance-l2b-r19-public-stop-r32.json"),
    "same_asset_feasibility": Path("generated/d2-failure-memory-provenance-l2b-r33-replacement-feasibility.json"),
    "external_release_recheck": Path("generated/d2-failure-memory-provenance-r34-external-substrate-release-recheck.json"),
    "psmg_design": Path("generated/d2-failure-memory-provenance-psmg-method-design-r27.json"),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    r32 = _load(PARENTS["r19_stop"])
    r33 = _load(PARENTS["same_asset_feasibility"])
    r34 = _load(PARENTS["external_release_recheck"])
    r27 = _load(PARENTS["psmg_design"])

    if r32["status"] != "R19_CONFIRMATORY_EXECUTION_STOPPED_RETRY_EXHAUSTED_NO_VERDICT":
        raise RuntimeError("R19 stop status drift")
    if r32["current_R19"]["resume_permitted"] or r32["interim_policy"]["claim_update_allowed"]:
        raise RuntimeError("R19 unexpectedly resumable or inferentially open")
    if r33["same_asset_capacity"]["fully_unexposed_templates_remaining"] != 27:
        raise RuntimeError("same-asset residual capacity drift")
    if r33["same_asset_capacity"]["can_supply_medium_variance_80pct_reference_n"]:
        raise RuntimeError("27-unit remainder unexpectedly satisfies frozen planning reference")
    if r34["adjudication"]["replacement_execution_ready_now"]:
        raise RuntimeError("external replacement unexpectedly execution-ready")
    if r27["status"] != "PREOUTCOME_METHOD_DESIGN_FROZEN_NO_NEW_EXECUTION_AUTHORITY":
        raise RuntimeError("PSMG design status drift")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R35-FRESH-CONFIRMATORY-REOPEN-GATE",
        "recorded_date": "2026-08-24",
        "status": "WAIT_FOR_NEW_PROVENANCE_BEARING_SUBSTRATE_NO_CONFIRMATORY_EXECUTION_AUTHORITY",
        "role": "ZERO_OUTCOME_CANONICAL_REOPEN_GATE_AFTER_R19_STOP",
        "scientific_relationship": "R19_REMAINS_STOPPED_R33_NOT_CONFIRMATORY_R34_WAIT_PSMG_DESIGN_FROZEN",
        "parent_bindings": {
            name: {"path": str(path), "sha256": _sha(path)} for name, path in PARENTS.items()
        },
        "paper_story": {
            "closed_design_loop": "phenomenon -> causal identification -> PSMG provenance-separated governance",
            "phenomenon_evidence_preserved": True,
            "causal_identification_ladder_preserved": True,
            "PSMG_design_frozen": True,
            "PSMG_effect_validated": False,
            "fresh_confirmatory_evidence_still_required_for_provenance_only_and_governance_effect_claims": True,
            "experiment_volume_is_not_a_gate_relaxation_reason": True,
        },
        "hard_non_reopen_rules": {
            "resume_R19": False,
            "retry_R19_sequence29_or_later": False,
            "pool_R19_partial_outcomes_into_future_sample": False,
            "use_R19_partial_outcomes_for_cohort_endpoint_threshold_model_or_analysis_selection": False,
            "treat_same_asset_27_as_fresh_confirmatory_cohort": False,
            "lower_confirmatory_ambition_only_to_fit_same_asset_27": False,
            "execute_PSMG_as_R19_rescue": False,
            "relax_construct_match_or_support_gate_to_add_experiment_volume": False,
        },
        "same_asset_27_adjudication": {
            "fully_unexposed_templates": 27,
            "medium_variance_two_sided_80pct_reference_n": 32,
            "prior_confirmatory_task_ambition": 35,
            "approx_power_at_task_sd_0_30": 0.738302,
            "fresh_confirmatory_eligible_under_current_gate": False,
            "status": "INVENTORY_ONLY_NOT_FRESH_CONFIRMATORY",
            "separately_authorized_lower_power_exploratory_design_possible_in_principle": True,
            "such_exploratory_design_may_upgrade_B1_confirmatory_claims": False,
        },
        "fresh_substrate_reopen_gate": {
            "ordered_stages": [
                {
                    "id": "G1_RELEASE",
                    "criterion": "FIRST_PARTY_OR_SOURCE_FAITHFUL_RELEASE_CONTENT_ADDRESSED",
                    "requires": [
                        "first-party repository or source-faithful artifact release",
                        "immutable commit/content hash pinned before scientific outcomes",
                        "third-party reimplementation cannot substitute for paper-specific artifact when construct fidelity is unresolved",
                    ],
                    "passed_now": False,
                    "current_blocker": "SMA_CODE_COMING_SOON_AND_IBM_PAPER_SPECIFIC_ARTIFACT_NOT_RELEASED",
                },
                {
                    "id": "G2_PROVENANCE_SCHEMA",
                    "criterion": "NATIVE_OR_AUDITABLE_MEMORY_GENERATING_SOURCE_OUTCOME_PROVENANCE",
                    "requires": [
                        "source outcome/provenance is stored as a separable field tied to memory generation",
                        "field is not merely post-use reward or later retrieval utility",
                        "provenance can be audited without inferring it from generated memory wording",
                    ],
                    "passed_now": False,
                    "current_blocker": "FIRST_PARTY_SCHEMA_NOT_AVAILABLE_FOR_RUNTIME_INSPECTION",
                },
                {
                    "id": "G3_EXACT_INFORMATION",
                    "criterion": "PROVENANCE_CAN_VARY_WITH_ACTIONABLE_INFORMATION_HELD_FIXED",
                    "requires": [
                        "actionable memory bytes/content support held fixed across provenance arms",
                        "retrieval candidates/budget/order and executor-visible non-provenance information held fixed",
                        "TRS/utility/verification evidence held fixed unless it is the prospectively declared treatment",
                        "no writer-mode bundle is relabeled as provenance-only",
                    ],
                    "passed_now": False,
                    "current_blocker": "NO_RELEASED_SCHEMA_OR_RUNTIME_TO_VERIFY_EXACT_INFORMATION_SWITCH",
                },
                {
                    "id": "G4_FRESH_CAPACITY",
                    "criterion": "PROSPECTIVELY_FROZEN_INDEPENDENT_UNITS_WITH_ADEQUATE_CONFIRMATORY_CAPACITY",
                    "requires": [
                        "new task/template universe selected without R19 partial outcomes",
                        "independent inference units frozen before treatment outcomes",
                        "sample size justified prospectively by the frozen estimand and variance/power plan",
                        "supply scarcity alone cannot justify shrinking the target",
                        "under the existing medium-variance reference, fewer than 32 independent tasks does not meet the prior two-sided 80% planning reference",
                    ],
                    "passed_now": False,
                    "current_blocker": "NO_QUALIFIED_NEW_SUBSTRATE_CAPACITY_CENSUS_EXISTS",
                },
                {
                    "id": "G5_SUPPORT_AND_PREREGISTRATION",
                    "criterion": "PREBENCHMARK_SUPPORT_RELIABILITY_AND_COMPLETE_ANALYSIS_CONTRACT",
                    "requires": [
                        "runtime/evaluator/reset support validated before benchmark treatment outcomes",
                        "support retry and stopping policy frozen before exposure",
                        "primary endpoint, estimand, schedule, exclusion, pooling and interval/test rules frozen",
                        "PSMG validation arms and strongest same-information non-provenance controller frozen if governance efficacy is tested",
                    ],
                    "passed_now": False,
                    "current_blocker": "NO_NEW_SUBSTRATE_RUNTIME_OR_CONFIRMATORY_CONTRACT_EXISTS",
                },
                {
                    "id": "G6_AUTHORITY",
                    "criterion": "NEW_EXPLICIT_SCIENTIFIC_AND_EXECUTION_AUTHORITY",
                    "requires": [
                        "new experiment explicitly named/scoped",
                        "scientific execution authority granted independently of R19",
                        "model/browser/evaluator/GPU authority granted only as actually required",
                        "claim authority remains post-outcome and gate-bound",
                    ],
                    "passed_now": False,
                    "current_blocker": "NO_NEW_EXPERIMENT_AUTHORITY_REQUESTED_OR_GRANTED",
                },
            ],
            "all_stages_required": True,
            "gate_pass_now": False,
            "qualified_substrate_now": None,
            "current_action": "WAIT_AND_BOUNDEDLY_RECHECK_EXTERNAL_FIRST_PARTY_RELEASES_ONLY",
        },
        "candidate_watch": {
            "priority_1": {
                "name": "Spatial Memory Agent (SMA)",
                "trigger": "FIRST_PARTY_CODE_RELEASE",
                "current_state": "WAIT_RELEASE",
                "why": "verified source experience and reward are explicit at memory-writing time, making it the strongest current process-provenance candidate",
            },
            "priority_2": {
                "name": "Trajectory-Informed Memory Generation for Self-Improving Agent Systems (IBM Research)",
                "trigger": "FIRST_PARTY_CODE_OR_SOURCE_FAITHFUL_ARTIFACT_RELEASE",
                "current_state": "WAIT_RELEASE_AND_PRECONSOLIDATION_SCHEMA_AUDIT",
                "why": "strong trajectory/outcome construct match but writer/consolidation can confound exact-information provenance",
            },
            "rejected_for_current_B1": {
                "name": "MutMem / HOM-AIMOS",
                "state": "STOP_CONSTRUCT_MISMATCH",
                "why": "post-use reward feedback is not the memory-generating source-trajectory provenance object",
            },
        },
        "future_confirmatory_design_boundary": {
            "minimum_identification_arms": [
                "content-only provenance-hidden baseline",
                "raw provenance-tag exact-information arm",
            ],
            "if_PSMG_efficacy_is_tested": [
                "PSMG executor-blind provenance governance",
                "strongest same-information content/relevance/verification-only controller without provenance",
            ],
            "same_units_may_be_reused_after_outcome_to_select_method_or_hyperparameters": False,
            "R19_partial_prefix_may_enter_analysis": False,
            "fresh_confirmatory_must_be_a_new_experiment_object": True,
        },
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
        "scientific_verdict": "NO_VERDICT_WAITING_FOR_QUALIFIED_NEW_SUBSTRATE",
    }


def main() -> None:
    out = Path("generated/d2-failure-memory-provenance-r35-fresh-confirmatory-reopen-gate.json")
    payload = build()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "gate_pass": False, "current_action": payload["fresh_substrate_reopen_gate"]["current_action"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
