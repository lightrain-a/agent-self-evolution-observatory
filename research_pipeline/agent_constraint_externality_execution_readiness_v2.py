from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_confirmatory_preexec import sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "generated/agent-constraint-externality-confirmatory-execution-proposal-20260904.json"
FREEZE = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-freeze-20260904.json"
AUDIT = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-audit-20260904.json"
CLOSEOUT = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-closeout-20260904.json"
OUTPUT = ROOT / "generated/agent-constraint-externality-confirmatory-execution-readiness-v2-20260905.json"


class ReadinessError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReadinessError(f"missing readiness input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_all_false(name: str, payload: dict[str, Any]) -> None:
    bad = [k for k, v in payload.get("authority", {}).items() if bool(v)]
    if bad:
        raise ReadinessError(f"{name} unexpectedly grants authority: {bad}")


def build() -> dict[str, Any]:
    proposal = load(PROPOSAL)
    freeze = load(FREEZE)
    audit = load(AUDIT)
    closeout = load(CLOSEOUT)

    if proposal.get("status") != "READY_FOR_SEPARATE_EXECUTION_AUTHORITY_GATE":
        raise ReadinessError("parent execution proposal is not at the authority gate")
    if freeze.get("status") != "ZERO_PROVIDER_PREEXEC_FREEZE_COMPLETE_EXECUTION_AUTHORITY_CLOSED":
        raise ReadinessError("preexec freeze is not closed/pass-ready")
    if audit.get("status") != "PASS_PREEXEC_CONSISTENCY_EXECUTION_AUTHORITY_CLOSED" or audit.get("failed_checks") != []:
        raise ReadinessError("preexec audit did not pass")
    if closeout.get("status") != "PREEXEC_DESIGN_DETAILS_FROZEN_PROVIDER_AND_EXECUTION_AUTHORITY_CLOSED":
        raise ReadinessError("preexec closeout is not closed/pass-ready")
    for name, payload in (("proposal", proposal), ("freeze", freeze), ("audit", audit), ("closeout", closeout)):
        _assert_all_false(name, payload)

    stages = [
        {
            "stage": "PROVIDER_READINESS_CHECK",
            "scientific_outcome": False,
            "purpose": "verify provider credit/interface availability without touching a scientific case",
            "opens_only": "SEPARATE_HUMAN_AUTHORITY",
            "failure_action": "STOP_NO_SCIENTIFIC_DISPATCH",
        },
        {
            "stage": "GATE0_DIRECT_ACTOR_CAPABILITY",
            "scientific_outcome": False,
            "purpose": "qualify the exact clean direct actor/runtime on the frozen capability contract",
            "failure_action": "STOP_BEFORE_GATE1",
        },
        {
            "stage": "GATE1_DIRECT_SFQ_A0",
            "scientific_outcome": False,
            "purpose": "qualify a normal semantic repair-opportunity regime on the frozen fresh development set",
            "failure_action": "STOP_SOURCE_SUBSTRATE_NO_CHALLENGE_VERSION_FISHING",
        },
        {
            "stage": "DEVELOPMENT_REPEAT_QUALIFICATION",
            "scientific_outcome": False,
            "families": 6,
            "R_candidates": [2, 3],
            "purpose": "freeze repeat count from within-condition stability only",
            "failure_action": "STOP_IF_R3_STILL_UNSTABLE_OR_ANY_TECHNICAL_INVALIDITY",
        },
        {
            "stage": "PRECISION_N_STAR_FREEZE",
            "scientific_outcome": False,
            "new_actor_episodes": 0,
            "N_candidates": [12, 16, 20, 24],
            "purpose": "choose N* from conservative development dispersion without emitting/using effect mean or sign",
            "failure_action": "PRECISION_QUALIFICATION_STOP_N24_INSUFFICIENT",
        },
        {
            "stage": "CONFIRMATORY_RESERVE_FREEZE",
            "scientific_outcome": False,
            "reserve_family_ids": 24,
            "stable_order_salt": "ACE-CONFIRMATORY-PANEL-ORDER-20260904-V1",
            "purpose": "freeze reserve IDs/order before any topology/collateral outcome",
        },
        {
            "stage": "CONFIRMATORY_SOURCE_AND_REPAIR",
            "scientific_outcome": False,
            "purpose": "establish valid semantic source failures and freeze exactly one repair artifact per reserve candidate before topology treatment",
            "forbidden": ["topology outcome readout", "collateral outcome readout", "repair regeneration after topology outcome"],
        },
        {
            "stage": "TARGET_ONLY_VERIFICATION",
            "surface_id": "TARGET_ONLY_VERIFICATION_V1",
            "scientific_outcome": False,
            "purpose": "determine pre-topology repair-uptake eligibility on the common snapshot using exact frozen repair bytes",
            "uptake_delta_min": 0.50,
            "post_topology_target_outcomes_may_change_eligibility": False,
        },
        {
            "stage": "CONFIRMATORY_PANEL_FREEZE",
            "scientific_outcome": False,
            "purpose": "select first N* eligible families under frozen stable-hash order",
            "insufficient_support_action": "STOP_DO_NOT_SHRINK_N",
            "post_topology_backfill_allowed": False,
        },
        {
            "stage": "SHAM_ARTIFACT_AND_SUBSET_FREEZE",
            "scientific_outcome": False,
            "default_subset_families": 8,
            "topology_extremes": ["INDEPENDENT", "HIGH"],
            "purpose": "freeze sham update/subset before collateral outcomes to falsify generic persistent-context insertion",
        },
        {
            "stage": "RQ1_RQ2_LOCKED_PANEL_EXECUTION",
            "scientific_outcome": True,
            "scientific_unit": "family",
            "arms": ["INDEPENDENT", "LOW", "HIGH"],
            "branches": ["NO_UPDATE", "REAL_REPAIR"],
            "collect_once_analyze_sequentially": True,
            "post_treatment_target_filtering": False,
            "purpose": "collect the full prequalified matched panel once; first adjudicate RQ1, then conditionally interpret RQ2 on the same frozen outcomes",
        },
        {
            "stage": "RQ1_ANALYSIS_GATE",
            "new_actor_episodes": 0,
            "scientific_outcome": True,
            "primary": "pooled UE = CRR_REAL_REPAIR - CRR_NO_UPDATE on full prequalified panel",
            "co_report": "topology-specific target-repair retention",
            "failure_action": "STOP_RQ2_CLAIM_AND_ALL_DOWNSTREAM_MECHANISM_DERIVED_CLAIMS",
        },
        {
            "stage": "RQ2_ANALYSIS_IF_RQ1_PASS",
            "new_actor_episodes": 0,
            "scientific_outcome": True,
            "primary": "UE_HIGH - UE_INDEPENDENT",
            "uses_same_locked_panel_outcomes": True,
            "failure_action": "STOP_TOPOLOGY_MECHANISM_AND_RQ3_RQ4",
        },
        {
            "stage": "RQ3_HELDOUT_PREDICTION_IF_RQ1_RQ2_PASS",
            "scientific_outcome": True,
            "H_candidates": [12, 16],
            "offline_zero_extra_actor_baselines": ["Random", "Same-App", "resource-count-only", "distance-only", "ExposureRank", "oracle-upper-bound"],
            "failure_action": "STOP_PREDICTION_DO_NOT_OPEN_GTCC",
        },
        {
            "stage": "RQ4_GTCC_IF_RQ1_RQ2_RQ3_PASS",
            "scientific_outcome": True,
            "M_candidates": [8, 12, 16],
            "policies": ["Always Commit", "Target-Only Validation", "Random-k", "Same-App-k", "GTCC"],
            "budget_matched": ["Random-k", "Same-App-k", "GTCC"],
            "full_check_role": "small prespecified oracle upper bound only",
            "failure_action": "STOP_GTCC_NOVELTY_IF_PRACTICALLY_EQUIVALENT_TO_RANDOM_K_OR_SAME_APP_K",
        },
    ]

    payload = {
        "schema_version": 2,
        "object_id": "AGENT-CONSTRAINT-EXTERNALITY-CONFIRMATORY-EXECUTION-READINESS-V2-20260905",
        "recorded_date": "2026-09-05",
        "status": "EXECUTION_SEQUENCE_MECHANICALLY_CLOSED_AUTHORITY_FALSE",
        "scientific_object": "AGENT-CONSTRAINT-EXTERNALITY-20260831",
        "parent_statuses": {
            "execution_proposal": proposal["status"],
            "preexec_freeze": freeze["status"],
            "preexec_audit": audit["status"],
            "preexec_closeout": closeout["status"],
        },
        "provenance": {
            "proposal_file_sha256": sha256_file(PROPOSAL),
            "freeze_file_sha256": sha256_file(FREEZE),
            "freeze_content_sha256": freeze.get("content_sha256"),
            "audit_file_sha256": sha256_file(AUDIT),
            "audit_content_sha256": audit.get("content_sha256"),
            "closeout_file_sha256": sha256_file(CLOSEOUT),
            "closeout_content_sha256": closeout.get("content_sha256"),
        },
        "execution_sequence": stages,
        "mechanical_invariants": {
            "target_only_verification_precedes_topology": True,
            "N_star_effect_direction_blind": True,
            "R_star_within_condition_stability_only": True,
            "R_greater_than_3_forbidden": True,
            "post_topology_target_filtering_forbidden": True,
            "post_topology_backfill_forbidden": True,
            "rq1_rq2_data_collected_once": True,
            "rq2_analysis_requires_rq1_pass": True,
            "rq3_requires_rq1_rq2_pass": True,
            "rq4_requires_rq1_rq2_rq3_pass": True,
            "nested_episodes_never_count_as_independent_family_n": True,
        },
        "authority": {
            "provider_readiness_check": False,
            "provider_execution": False,
            "gate0": False,
            "gate1": False,
            "development_repeat_qualification": False,
            "confirmatory_source_and_repair": False,
            "target_only_verification": False,
            "rq1_rq2_execution": False,
            "rq1_analysis": False,
            "rq2_analysis": False,
            "rq3": False,
            "rq4": False,
            "secondary_actor": False,
            "external_updater": False,
            "paper_claim": False,
        },
        "scientific_provider_calls_created": 0,
        "scientific_outcomes_created": 0,
        "next_legal_action": "EXPLICIT_SEPARATE_HUMAN_AUTHORITY_FOR_PROVIDER_READINESS_ONLY; SCIENTIFIC DISPATCH REMAINS CLOSED",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def check(payload: dict[str, Any]) -> None:
    if payload["status"] != "EXECUTION_SEQUENCE_MECHANICALLY_CLOSED_AUTHORITY_FALSE":
        raise ReadinessError("readiness status mismatch")
    if any(bool(v) for v in payload["authority"].values()):
        raise ReadinessError("readiness artifact unexpectedly grants authority")
    stages = [x["stage"] for x in payload["execution_sequence"]]
    required_order = [
        "PROVIDER_READINESS_CHECK",
        "GATE0_DIRECT_ACTOR_CAPABILITY",
        "GATE1_DIRECT_SFQ_A0",
        "DEVELOPMENT_REPEAT_QUALIFICATION",
        "PRECISION_N_STAR_FREEZE",
        "CONFIRMATORY_RESERVE_FREEZE",
        "CONFIRMATORY_SOURCE_AND_REPAIR",
        "TARGET_ONLY_VERIFICATION",
        "CONFIRMATORY_PANEL_FREEZE",
        "SHAM_ARTIFACT_AND_SUBSET_FREEZE",
        "RQ1_RQ2_LOCKED_PANEL_EXECUTION",
        "RQ1_ANALYSIS_GATE",
        "RQ2_ANALYSIS_IF_RQ1_PASS",
        "RQ3_HELDOUT_PREDICTION_IF_RQ1_RQ2_PASS",
        "RQ4_GTCC_IF_RQ1_RQ2_RQ3_PASS",
    ]
    if stages != required_order:
        raise ReadinessError(f"execution sequence mismatch: {stages}")
    if payload["scientific_provider_calls_created"] != 0 or payload["scientific_outcomes_created"] != 0:
        raise ReadinessError("readiness construction created scientific work")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    check(payload)
    if args.check:
        if not OUTPUT.is_file():
            raise ReadinessError(f"missing readiness output: {OUTPUT}")
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if existing != payload:
            raise ReadinessError("readiness output differs from deterministic rebuild")
    else:
        OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "content_sha256": payload["content_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
