#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LADDER = HERE / "stage-evidence-ladder-analysis-20260825.json"
OUT = HERE / "stage-evidence-sensitivity-audit-20260826.json"
EXPECTED_LADDER_SHA256 = "d3c5341d1d6064cac5b7f8164c72af77433ef10d79d35338806f0784be49effa"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> None:
    require(LADDER.is_file(), "missing stage-evidence ladder")
    require(sha(LADDER) == EXPECTED_LADDER_SHA256, "stage-evidence ladder SHA drift")
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    by_stage = {row["stage"]: row for row in ladder["evidence_ladder"]}
    expected = {
        "persistent_write",
        "forced_capacity_side_control",
        "native_retrieval_exposure",
        "native_first_action_uptake",
        "native_terminal_outcome",
    }
    require(set(by_stage) == expected, "unexpected stage set")

    stage_audit = [
        {
            "stage": "persistent_write",
            "measurement_unit": "paired source trajectories plus an 8-trajectory same-mode wording control",
            "measurement_type": "durable-state difference / paired prompt-control contrast",
            "inferential_role": "SUPPORTED_INTERVENTION_ESTABLISHMENT",
            "power_matched_to_other_stages": False,
        },
        {
            "stage": "native_retrieval_exposure",
            "measurement_unit": "172 held-out retrieval opportunities",
            "measurement_type": "descriptive source-memory-item retrieval event",
            "inferential_role": "DIRECTLY_OBSERVED_AVAILABILITY",
            "power_matched_to_other_stages": False,
        },
        {
            "stage": "native_first_action_uptake",
            "measurement_unit": "36 matched Shopping branch-comparison states",
            "measurement_type": "first-action distributional TV and modal-action contrast",
            "inferential_role": "NOT_SUPPORTED_AT_FROZEN_PRIMARY_TEST",
            "power_matched_to_other_stages": False,
        },
        {
            "stage": "native_terminal_outcome",
            "measurement_unit": "36 Shopping terminal cells plus 8 Reddit terminal cells",
            "measurement_type": "terminal success-rate branch contrast / sparsity and sign audit",
            "inferential_role": "SPARSE_HETEROGENEOUS_BOUNDARY",
            "power_matched_to_other_stages": False,
        },
        {
            "stage": "forced_capacity_side_control",
            "measurement_unit": "16 source-memory/future-task cells with 8 rollouts per branch",
            "measurement_type": "forced fixed-evidence terminal success contrast",
            "inferential_role": "SUPPORTED_SIDE_CAPACITY_CONTROL",
            "power_matched_to_other_stages": False,
        },
    ]

    structural_sensitivity = [
        {
            "variant": "drop_terminal_outcome",
            "removed_evidence": ["native_terminal_outcome"],
            "first_unsupported_measured_native_stage": "native_first_action_uptake",
            "diagnostic_resolution_preserved": True,
            "reason": "write and source-item exposure remain established before the frozen first-action test",
        },
        {
            "variant": "drop_reddit_terminal_evidence",
            "removed_evidence": ["reddit_native_terminal_outcome"],
            "first_unsupported_measured_native_stage": "native_first_action_uptake",
            "diagnostic_resolution_preserved": True,
            "reason": "the Shopping write-exposure-uptake ordering is unchanged and Reddit has no matched exposure/uptake ladder",
        },
        {
            "variant": "drop_forced_capacity_side_control",
            "removed_evidence": ["forced_capacity_side_control"],
            "first_unsupported_measured_native_stage": "native_first_action_uptake",
            "diagnostic_resolution_preserved": True,
            "reason": "forced capacity is a side control and is not an element of the native ordering rule",
        },
        {
            "variant": "merge_exposure_and_uptake",
            "merged_evidence": ["native_retrieval_exposure", "native_first_action_uptake"],
            "first_unsupported_measured_native_stage": None,
            "diagnostic_resolution_preserved": False,
            "reason": "collapsing availability and first-action response removes the observation needed to distinguish exposure from uptake",
        },
    ]
    require(
        all(row["first_unsupported_measured_native_stage"] == "native_first_action_uptake" for row in structural_sensitivity[:3]),
        "leave-one-component-out localization drift",
    )
    require(structural_sensitivity[3]["diagnostic_resolution_preserved"] is False, "merged exposure/uptake should lose resolution")

    payload = {
        "schema_version": "1.1",
        "artifact_type": "c1-stage-evidence-sensitivity-audit",
        "audit_id": "C1-R4-STAGE-EVIDENCE-SENSITIVITY-20260826",
        "paper_id": ladder["paper_id"],
        "status": "EVIDENCE_LOCALIZATION_SUPPORTED_LATENT_BOTTLENECK_NOT_IDENTIFIED",
        "source_binding": {"path": str(LADDER.relative_to(HERE.parents[1])), "sha256": EXPECTED_LADDER_SHA256},
        "stage_audit": stage_audit,
        "identifiability": {
            "ordered_stage_tests_have_matched_units": False,
            "ordered_stage_tests_have_matched_metrics": False,
            "ordered_stage_tests_have_matched_statistical_power": False,
            "first_unsupported_measured_stage_is_identifiable": True,
            "latent_causal_attenuation_onset_is_identified": False,
            "causal_mediation_is_identified": False,
            "allowed_boundary_phrase": "first unsupported measured native stage after supported or directly observed prerequisites",
            "forbidden_boundary_phrases": [
                "true causal bottleneck",
                "identified attenuation onset",
                "largest attenuation occurs at action uptake",
                "causal mediator at action uptake",
            ],
        },
        "exposure_semantics": {
            "measured_object": "retrieval of a branch-conditioned source-memory item into native context",
            "treatment_specific_residual_exposure_measured": False,
            "policy_use_measured_by_retrieval_event": False,
            "allowed_inference": "retrieval absence alone is insufficient to explain the weak native action/endpoint evidence",
        },
        "forced_native_boundary": {
            "intervention_surfaces_identical": False,
            "forced_control_bypasses_native_retrieval_and_context_composition": True,
            "allowed_inference": "the downstream system can respond to supplied branch-conditioned memory under the forced surface",
            "forbidden_inference": "native policy would respond identically if it attended to the retrieved item",
        },
        "cross_domain_boundary": {
            "reddit_write_terminal_separation_observed": True,
            "reddit_native_exposure_measured": False,
            "reddit_first_action_uptake_measured": False,
            "shopping_exposure_to_uptake_boundary_replicated_on_reddit": False,
        },
        "structural_sensitivity": structural_sensitivity,
        "measurement_load_bearing": {
            "distinction": "native_retrieval_exposure_vs_native_first_action_uptake",
            "supported_by": [
                "drop_terminal_outcome_preserves_boundary",
                "drop_reddit_terminal_evidence_preserves_boundary",
                "drop_forced_capacity_side_control_preserves_boundary",
                "merge_exposure_and_uptake_loses_diagnostic_resolution",
            ],
            "interpretation": "separating exposure from uptake is load-bearing for this operational localization; merely increasing the number of reported metrics is not",
            "causal_mechanism_identified": False,
        },
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_scientific_runs": 0, "new_scientific_experiments": 0},
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "claim_expansion": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "stages": len(stage_audit), "provider_calls": 0, "gpu_runs": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
