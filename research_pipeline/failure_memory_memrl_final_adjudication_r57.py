#!/usr/bin/env python3
"""Build the final R57 adjudication for the prospective B1 full350 L2 experiment.

This artifact records only complete-run, post-gate evidence.  R54/R55/R56 runtime
artifacts remain content-addressed on the qualified execution host; their file
and internal receipt hashes are bound below.  The post-confirmatory behavioral
diagnostics are explicitly descriptive and cannot upgrade the preregistered
terminal-success estimand.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
OUTPUT = pathlib.Path("generated/d2-failure-memory-provenance-r57-full350-l2-final-adjudication.json")


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R57-FULL350-L2-FINAL-ADJUDICATION",
        "recorded_date": "2026-09-02",
        "status": "L2_PROVENANCE_ONLY_COMPLETE_QUALIFIED_CONTENT_SUFFICIENCY_LOW_TERMINAL_VALUE",
        "role": "FINAL_COMPLETE_RUN_ADJUDICATION_FOR_R53_R56_PROSPECTIVE_FULL350_AB_LINEAGE",
        "evidence_bindings": {
            "R53_source_build": {
                "remote_path": "/data/wyt/b1-memrl-r53-full350-execution/source-build/source-build-receipt.json",
                "file_sha256": "64b64cb2ca170482fafe4bb89db96071e896d1a952dc6c9a8002093849a000b0",
                "receipt_sha256": "ce15c57e9c1274d1b40aca49850c7b0cbb5a8fe0656314d8bdfca3d7024e95c7",
                "completed_ledger_sha256": "e98ea4e910bed5bf32b56dfc321879842385b920f10636b97c0f850a5316c06a",
                "trace_jsonl_sha256": "8a0bdb536f6130d0984abbf459a2c45f6e66008a447255cbfd85ad4b5acd5798",
            },
            "R54v2_fresh_support": {
                "remote_path": "/data/wyt/b1-memrl-r53-full350-execution/fresh-support-r54v2/fresh-support-qualification-r54v2-receipt.json",
                "file_sha256": "650e145a491f09555e40aa8c81c8598d8e1e2dc9febd906857fb8a3202f3aca3",
                "receipt_sha256": "032c79998165700d5405d2d56bd30cf2dfe044b9f9ec97d2e51461a429514c42",
                "selection_file_sha256": "39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c",
                "selection_receipt_sha256": "7d75b4d79a7b83ad8e3d452d4a232d66c1137acc91484e51356160a95a385776",
                "frozen_retrieval_file_sha256": "fc906765f2f94b053996bef2d7a085b6a2534b0922f2929da253390d3b855b72",
                "frozen_retrieval_receipt_sha256": "03a891c3c0c8e7fb9de02e41a052d2d1c3481b61f9c4c02655078bb709982ab8",
            },
            "R55_fresh_utilization": {
                "remote_path": "/data/wyt/b1-memrl-r53-full350-execution/fresh-utilization-r55/utilization-qualification-receipt.json",
                "file_sha256": "261a99e3830983f1676bda6d8a199dec1b34e24331d0060f94421c93c7059bd0",
                "receipt_sha256": "122c3cb1b3f1a16418a54e3b137e8aa75d91084c0cfe5fae17c7e2f1ce515d2e",
                "completed_arms_sha256": "fe6f7e7cf8f9184201e98d431e05b2d2e5687153254265e8eee4664b36b0296e",
            },
            "R56_fresh_AB": {
                "remote_path": "/data/wyt/b1-memrl-r53-full350-execution/fresh-ab-r56/ab-identification-receipt.json",
                "file_sha256": "1b631575d78eeb0beb7c38669ea01611a0ed165e0ea0109e8b0289dbc1ada0f1",
                "receipt_sha256": "738a807debc5dbc83cfa7bb573a07df2bdd6bd131e3b6a27a1fdd438d44fcdcc",
                "frozen_plan_file_sha256": "cf6ab33fba9f072d851977f33367988587dd2f673944ca67c703a11102c78984",
                "frozen_plan_sha256": "8103868d5fbbc598df4752ccee9fa9719861528c44d69e3bdeadd9f3248e61c3",
                "completed_arms_sha256": "b96f350ba4006055d4c090ddfe677dec6aea14507ecb4cf2a15a0540667f318c",
            },
        },
        "gate_results": {
            "source_build": {
                "complete": True,
                "source_tasks": 350,
                "success_memories": 176,
                "failure_memories": 174,
                "external_provider_calls": 0,
            },
            "fresh_support": {
                "candidate_clusters": 108,
                "eligible_clusters": 106,
                "primary_selected": 32,
                "utilization_selected": 8,
                "both_source_provenance_polarities_retrievable": True,
                "validation_treatment_outcomes_observed": 0,
            },
            "utilization": {
                "status": "UTILIZATION_QUALIFICATION_PASS",
                "complete_units": 8,
                "arm_runs": 40,
                "u1_specific_first_action_units": 5,
                "u2_vs_u0_divergence_units": 3,
                "promotion_rule_satisfied": True,
                "terminal_success_used_for_promotion": False,
                "primary_confirmatory_outcomes_observed": 0,
            },
            "AB_confirmatory": {
                "status": "FRESH_AB_IDENTIFICATION_ESTIMATE_COMPLETE",
                "complete_units": 32,
                "arm_runs": 64,
                "execution_failures": 0,
                "historical_pooling": False,
            },
        },
        "primary_terminal_result": {
            "A_content_only_successes": 15,
            "A_content_only_total": 32,
            "A_content_only_rate": 0.46875,
            "B_raw_provenance_successes": 16,
            "B_raw_provenance_total": 32,
            "B_raw_provenance_rate": 0.5,
            "estimand": "B_raw_provenance - A_content_only",
            "paired_effect": 0.03125,
            "B_only_success": 1,
            "A_only_success": 0,
            "discordant_pairs": 1,
            "preregistered_ci95_paired_cluster_bootstrap": [0.0, 0.09375],
            "preregistered_exact_two_sided_signflip_p": 1.0,
            "preregistered_effect_relevance_floor_abs": 0.15,
            "effect_relevance_floor_met": False,
        },
        "postconfirmatory_descriptive_mechanism": {
            "inferential_authority": False,
            "first_executable_action_diff_clusters": 9,
            "first_executable_action_diff_fraction": 0.28125,
            "step_count_diff_clusters": 7,
            "step_count_diff_fraction": 0.21875,
            "terminal_outcome_diff_clusters": 1,
            "terminal_outcome_diff_fraction": 0.03125,
            "sole_terminal_discordant_task_id": "252",
            "sole_terminal_discordance_direction": "A_fail_B_success",
            "task_252_A_steps": 16,
            "task_252_B_steps": 8,
            "task_252_R39_adapter_audit": {
                "retrieval_membership_preserved": True,
                "retrieval_order_preserved": True,
                "actionable_content_identical": True,
                "only_executor_visible_difference": "source_outcome_success",
                "similarity_q_score_role_and_ids_hidden_from_executor": True,
            },
            "interpretation": "Executor-visible provenance can perturb local action selection and trajectory length, but those perturbations rarely translate into terminal utility on this qualified fresh OSInteraction surface.",
        },
        "scientific_adjudication": {
            "L2_identification_status": "IDENTIFIED_ON_QUALIFIED_FULL350_FRESH_SURFACE",
            "terminal_provenance_effect_status": "NO_STATISTICALLY_DETECTABLE_OR_PREREGISTERED_PRACTICALLY_RELEVANT_EFFECT",
            "content_sufficiency_interpretation": "RESULT_IS_CONSISTENT_WITH_A_QUALIFIED_CONTENT_SUFFICIENCY_REGIME_AT_THE_TERMINAL_ENDPOINT",
            "behavioral_channel_interpretation": "PROVENANCE_IS_BEHAVIORALLY_LEGIBLE_BUT_LOW_TERMINAL_VALUE_IN_THIS_SETTING",
            "zero_effect_proof": False,
            "bootstrap_caution": "The preregistered percentile bootstrap interval is reported as frozen, but sparse discordance (1/32) means it must not be rhetorically upgraded into a proof that all population effects are below 9.375 percentage points.",
            "generalization_boundary": "The conclusion is conditional on the frozen Qwen2.5-7B-Instruct, MemRL/OSInteraction substrate, full350 source construction, native retrieval threshold 0.5, fresh supported cluster selection, and exact R39 A/B information projection.",
        },
        "forbidden_claims": {
            "provenance_has_exactly_zero_effect": True,
            "provenance_is_never_used_by_the_executor": True,
            "PSMG_efficacy_identified": True,
            "C_D_governance_estimand_identified": True,
            "historical_L1_writer_effect_upgraded_to_L2": True,
            "cross_model_or_cross_substrate_generalization": True,
        },
        "remaining_scientific_scope": {
            "C_D_status": "NOT_EXECUTED",
            "PSMG_efficacy_status": "NOT_IDENTIFIED",
            "recommended_next_evidence": [
                "replicate the same frozen A/B estimand on a second model backbone",
                "run source-faithful transport in a system with an authentic provenance channel if available",
                "treat any PSMG controller as a new prospectively operationalized method experiment",
            ],
        },
    }
    out["receipt_sha256"] = digest(out)
    return out


def main() -> None:
    out = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "receipt_sha256": out["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
