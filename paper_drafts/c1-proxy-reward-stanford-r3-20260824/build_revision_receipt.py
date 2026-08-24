from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    matrix = json.loads((REPO / "generated/stanford-r2-objection-matrix.json").read_text())
    paper = matrix["papers"][PAPER_ID]
    qa = json.loads((HERE / "manuscript-qa.json").read_text())
    diag = json.loads((HERE / "existing-evidence-diagnostics.json").read_text())
    o5 = json.loads((HERE / "o5-manuscript-evidence.json").read_text())
    o6 = json.loads((HERE / "o6-final-evidence.json").read_text())
    o6_reduction = json.loads((HERE / "o6-full-bank-corruption-reduction.json").read_text())
    chronology = json.loads((HERE / "f2r1-chronology-receipt.json").read_text())
    blind_repair = json.loads((HERE / "blind-review-20260824/repair-receipt.json").read_text())
    post_repair_review = json.loads((HERE / "blind-review-20260824/post-repair-validation-receipt.json").read_text())
    original = {row["id"]: row for row in paper["objections"]}
    interaction = diag["terminal_heterogeneity"]["two_way_centered_effect_decomposition"]
    write_terminal = diag["terminal_heterogeneity"]["write_to_terminal_magnitude_diagnostic"]
    structural = diag["strategy_prompt_control"]
    accounting = diag["execution_accounting"]

    receipt = {
        "schema_version": "1.0",
        "receipt_type": "stanford-r3-targeted-experiment-revision",
        "paper_id": PAPER_ID,
        "paper_code": paper["code"],
        "revision": "STANFORD-R3-BLIND-REVIEW-PROVENANCE-REPAIR-20260824",
        "base_review": matrix["matrix_id"],
        "stanford_r2_score": paper["r2"]["score"],
        "stanford_r2_verdict": paper["r2"]["verdict"],
        "paper_only_revision": False,
        "new_experiment": True,
        "new_provider_calls_exact": None,
        "new_provider_calls_observable_lower_bound": o5["execution_accounting"]["o5_total_provider_calls_consumed"] + o6["execution_accounting"]["o6_provider_posts_observable_lower_bound"],
        "new_scientifically_usable_provider_calls": o5["execution_accounting"]["recovery_scientifically_usable_units"] + o6["execution_accounting"]["repair_4096_writer_calls"] + o6["execution_accounting"]["stage2_terminal_calls"],
        "new_terminal_rollouts": o5["execution_accounting"]["recovery_scientifically_usable_units"] + o6["execution_accounting"]["stage2_terminal_calls"],
        "claim_expansion": False,
        "latest_paper_only_repair": {
            "trigger": "blind independent ICLR review after O5/O6 completion",
            "review_calls": blind_repair["review_calls"],
            "review_calls_are_scientific_evidence": blind_repair["review_calls_are_scientific_evidence"],
            "strict_recommendation_before_repair": blind_repair["strict_review"]["recommendation"],
            "strict_score_before_repair": blind_repair["strict_review"]["score_1_to_10"],
            "evidence_chain_valid": blind_repair["evidence_review"]["evidence_chain_valid"],
            "extra_experiment_needed_before_submission": blind_repair["evidence_review"]["extra_experiment_needed_before_submission"],
            "selected_repair_class": blind_repair["selected_repair"]["class"],
            "new_scientific_provider_calls": blind_repair["selected_repair"]["new_scientific_provider_calls"],
            "new_rollouts": blind_repair["selected_repair"]["new_rollouts"],
            "claim_expansion": blind_repair["selected_repair"]["claim_expansion"],
            "post_repair_validation": {
                "status": post_repair_review["status"],
                "recommendation": post_repair_review["post_repair_strict_review"]["recommendation"],
                "score_1_to_10": post_repair_review["post_repair_strict_review"]["score_1_to_10"],
                "confidence_1_to_5": post_repair_review["post_repair_strict_review"]["confidence_1_to_5"],
                "recommendation_change": post_repair_review["recommendation_change"],
                "score_change": post_repair_review["score_change"],
                "current_narrow_claim_evidence_sufficient": post_repair_review["post_repair_strict_review"]["current_narrow_claim_evidence_sufficient"],
                "decision": post_repair_review["decision"],
                "review_calls_are_scientific_evidence": post_repair_review["review_calls_are_scientific_evidence"],
            },
        },
        "objections": {
            "PROXY-O1": {
                "original_disposition": original["PROXY-O1"]["d"],
                "revision_status": "PRESERVED_RESOLVED",
                "action": "No novelty expansion; keep the identical-trajectory reward-conditioned writer-branch boundary.",
            },
            "PROXY-O2": {
                "original_disposition": original["PROXY-O2"]["d"],
                "revision_status": "ADDRESSED_WITH_EXISTING_EVIDENCE",
                "evidence": {
                    "f0_operation_slot_change_rate": diag["writer_structure"]["strategy_slot_set_change_rate"],
                    "f0_mean_slot_jaccard_distance": diag["writer_structure"]["mean_strategy_slot_jaccard_distance"],
                    "f0c_between_reward_modes_slot_distance": structural["mean_between_reward_modes_slot_distance"],
                    "f0c_within_mode_rewording_slot_distance": structural["mean_within_mode_rewording_slot_distance"],
                    "f0c_structural_excess": structural["mean_between_minus_within_slot_distance"],
                },
                "boundary": "Structural/operation-slot evidence only; no embedding-semantic equivalence claim.",
            },
            "PROXY-O3": {
                "original_disposition": original["PROXY-O3"]["d"],
                "revision_status": "PRESERVED_PERMANENT_CLAIM_BOUNDARY",
                "action": "No re-POST, no imputation; 4/4 claims remain conditional on paired completion.",
            },
            "PROXY-O4": {
                "original_disposition": original["PROXY-O4"]["d"],
                "revision_status": "ADDRESSED_WITH_EXISTING_EVIDENCE",
                "evidence": {
                    "source_main_share": interaction["source_main_share"],
                    "future_main_share": interaction["future_main_share"],
                    "source_future_interaction_share": interaction["source_future_interaction_share"],
                    "zero_effect_cells": diag["terminal_heterogeneity"]["zero_effect_cells"],
                    "top_two_squared_effect_mass_share": diag["terminal_heterogeneity"]["top_two_share_of_squared_effect_mass"],
                    "future_task_164_joint_ceiling": next(row["all_cells_joint_ceiling"] for row in diag["terminal_heterogeneity"]["future_task_breakdown"] if row["task_id"] == "164"),
                    "write_token_distance_vs_source_mean_effect_pearson_descriptive": write_terminal["pearson_token_distance_vs_source_mean_absolute_effect"],
                    "write_slot_distance_vs_source_mean_effect_pearson_descriptive": write_terminal["pearson_slot_distance_vs_source_mean_absolute_effect"],
                    "near_matched_write_divergence_sources": ["23", "25"],
                    "f2r1_chronology_status": chronology["status"],
                    "initial_terminal_gate_pass": chronology["initial_stage"]["gate_pass"],
                    "confirmatory_terminal_gate_pass": chronology["confirmatory_stage"]["gate_pass"],
                    "same_4x4_support": chronology["relationship"]["same_4x4_support"],
                    "source_selection_changed": chronology["relationship"]["source_selection_changed"],
                    "future_task_selection_changed": chronology["relationship"]["future_task_selection_changed"],
                    "effect_floor_changed": chronology["relationship"]["effect_floor_changed"],
                    "alpha_changed": chronology["relationship"]["alpha_changed"],
                    "initial_vs_confirmatory_cells_exposed": len(chronology["cell_comparison"]),
                },
                "boundary": "Finite 4x4 descriptive decomposition plus a four-source non-monotonic magnitude check only; no general predictor of transfer-effect magnitude. F2R1 is explicitly documented as a targeted uniform same-support replication after an initial non-pass, not as the first outcome-blind terminal experiment; no source/future selection or gate relaxation occurred.",
            },
            "PROXY-O5": {
                "original_disposition": original["PROXY-O5"]["d"],
                "revision_status": "ADDRESSED_WITH_FRESH_EXECUTION",
                "evidence": {
                    "fresh_no_memory_calls": o5["execution_accounting"]["recovery_scientifically_usable_units"],
                    "old_exploratory_calls_reused": o5["execution_accounting"]["old_exploratory_no_memory_calls_reused"],
                    "future_task_rates": {row["future_task"]: row["no_memory_rate"] for row in o5["fresh_no_memory_by_future_task"]},
                    "point_estimate_geometry_counts": o5["point_estimate_geometry_counts"],
                    "source22_future388": o5["selected_cell_diagnostics"]["source22_future388"],
                    "source25_future387": o5["selected_cell_diagnostics"]["source25_future387"],
                },
                "boundary": "Secondary branch-location control only: four source-independent no-memory baselines are shared across source comparisons, no global p-value is added, and the primary F2R1 two-arm gate remains unchanged.",
            },
            "PROXY-O6": {
                "original_disposition": original["PROXY-O6"]["d"],
                "revision_status": "PARTIALLY_ADDRESSED_WITH_CROSS_WRITER_EXECUTION_AND_CORRUPTION_REDUCTION",
                "evidence": {
                    "writer_stage_complete_pairs": o6["writer_stage"]["complete_pairs"],
                    "writer_stage_mean_token_jaccard_distance": o6["writer_stage"]["mean_token_jaccard_distance"],
                    "terminal_stage_calls": o6["terminal_stage"]["complete_calls"],
                    "terminal_mean_absolute_success_rate_difference": o6["terminal_stage"]["mean_absolute_success_rate_difference"],
                    "terminal_permutation_p": o6["terminal_stage"]["permutation_p"],
                    "terminal_effect_floor": o6["terminal_stage"]["effect_floor"],
                    "terminal_effect_floor_shortfall": o6["terminal_stage"]["effect_floor_shortfall"],
                    "terminal_joint_gate_pass": o6["terminal_stage"]["joint_gate_pass"],
                    "cells_nonzero_in_both_writers": o6["cross_writer_comparison"]["cells_nonzero_in_both_writers"],
                    "same_direction_among_nonzero_both": o6["cross_writer_comparison"]["same_direction_among_nonzero_both"],
                    "opposite_direction_among_nonzero_both": o6["cross_writer_comparison"]["opposite_direction_among_nonzero_both"],
                    "full_bank_corruption_reduction_status": o6_reduction["status"],
                    "released_retriever_top_k": o6_reduction["released_mechanism_facts"]["default_top_k"],
                    "released_retriever_threshold": o6_reduction["released_mechanism_facts"]["default_similarity_threshold"],
                    "multi_memory_interaction_identifiable_under_released_mechanism": o6_reduction["symbolic_factorization"]["multi_memory_interaction_identifiable_under_released_top1_mechanism"],
                    "corruption_sweep_new_provider_calls": o6_reduction["economy_decision"]["new_provider_calls_authorized"],
                },
                "boundary": "The write-time state divergence replicates with GLM-5.3 on all four frozen sources, but terminal writer invariance is not established because the preregistered 0.15 practical-effect floor is missed despite p=0.00012 and two cellwise direction reversals. The proposed full-bank corruption-mask interaction sweep is stopped by matched simplification: released ReasoningBank retrieves top-1 from label-invariant task-description embeddings, so only the retrieved source's corruption bit can affect an episode. Source-faithful retrieval-wrapper/live-browser transport remains distinct and environment-blocked rather than being claimed as covered.",
            },
        },
        "system_paper_requirements": {
            "abstract_words_approx": qa["abstract_words_approx"],
            "main_text_pages": qa["main_text_pages"],
            "related_work_moved_before_method_results": True,
            "experimental_setup_section_added": True,
            "execution_accounting_added": True,
            "strongest_simple_control_explicit": True,
            "mechanism_diagnostic_added": True,
            "heterogeneity_diagnostic_added": True,
            "write_to_terminal_nonmonotonic_diagnostic_added": True,
            "failure_and_scope_boundaries_preserved": True,
            "experiment_program_E1_E6": {
                "E1_main_comparison": {
                    "status": "PASS",
                    "evidence": "F2R1 fully crossed 4x4 terminal confirmation: mean absolute success-rate difference 0.15625, within-cell permutation p=0.00074.",
                },
                "E2_component_or_simplification": {
                    "status": "PASS",
                    "evidence": "F0C stronger same-mode semantic-preserving prompt rewording: paired excess 0.105, exact p=0.0078.",
                },
                "E3_mechanism_aligned": {
                    "status": "PASS",
                    "evidence": "Identical-trajectory write intervention changes all four complete paired memories; deterministic operation-slot audit and 7/12 aligned next-action witness expose intermediate state/behavior changes.",
                },
                "E4_robustness_transfer_boundary": {
                    "status": "PASS_FINITE_BOUNDARY",
                    "evidence": "All 16 initial and confirmatory source-future cells are exposed side by side. The initial 3-rollout/cell F2 is a committed non-pass (0.145833, p=0.160128); F2R1 then uniformly increases replication depth to 8 on the identical 4x4 support while retaining the same 0.15/p<0.05 dual gate and prohibiting source/future selection after outcomes. A fresh no-memory control locates branches without pseudoreplication; GLM-5.3 reproduces 4/4 write-time divergence but its 256-call terminal replication misses the frozen 0.15 effect floor (0.140625, p=0.00012) and reverses direction in two of six cells nonzero under both writers. A source-code-bound reduction further shows that the released top-1 task-description retriever makes a multi-bit full-bank corruption interaction unidentifiable: nonretrieved mask bits are causally inert.",
                },
                "E5_negative_failure_cases": {
                    "status": "PASS_VISIBLE_NEGATIVES",
                    "evidence": "Two F0 failure-arm provider incompletions remain selection debt; F1D p=0.311 and initial terminal p=0.160 remain visible non-passing tests; O5 retains its execution-invalid first attempt; the parent GLM writer attempt is retained as output-cap/concurrency execution debt; and the complete GLM terminal replication remains a real preregistered non-pass because 0.140625 < 0.15 despite p=0.00012.",
                },
                "E6_efficiency_cost_scale": {
                    "status": "PASS_ACCOUNTED",
                    "evidence": {
                        "inference_only": True,
                        "known_provider_posts_observable_lower_bound": accounting["known_requests_excluding_unresolved_low_level_call_count_for_f1_action_existence"] + o5["execution_accounting"]["o5_total_provider_calls_consumed"] + o6["execution_accounting"]["o6_provider_posts_observable_lower_bound"],
                        "exact_total_reconstructible": False,
                        "o5_provider_calls_consumed": o5["execution_accounting"]["o5_total_provider_calls_consumed"],
                        "o5_scientifically_usable_calls": o5["execution_accounting"]["recovery_scientifically_usable_units"],
                        "o6_provider_posts_observable_lower_bound": o6["execution_accounting"]["o6_provider_posts_observable_lower_bound"],
                        "o6_repair_writer_calls": o6["execution_accounting"]["repair_4096_writer_calls"],
                        "o6_stage2_terminal_calls": o6["execution_accounting"]["stage2_terminal_calls"],
                        "f1_action_existence_aligned_paired_units": accounting["f1_action_existence_aligned_paired_units"],
                        "training_runs": accounting["training_runs"],
                        "local_gpu_finetuning_runs": accounting["local_gpu_finetuning_runs"],
                    },
                },
            },
            "manuscript_qa_status": qa["status"],
        },
        "artifact_bindings": {
            "diagnostic_sha256": sha(HERE / "existing-evidence-diagnostics.json"),
            "o5_evidence_sha256": sha(HERE / "o5-manuscript-evidence.json"),
            "o6_evidence_sha256": sha(HERE / "o6-final-evidence.json"),
            "o6_full_bank_reduction_sha256": sha(HERE / "o6-full-bank-corruption-reduction.json"),
            "f2r1_chronology_receipt_sha256": sha(HERE / "f2r1-chronology-receipt.json"),
            "blind_review_repair_receipt_sha256": sha(HERE / "blind-review-20260824/repair-receipt.json"),
            "post_repair_blind_review_validation_receipt_sha256": sha(HERE / "blind-review-20260824/post-repair-validation-receipt.json"),
            "manuscript_qa_sha256": sha(HERE / "manuscript-qa.json"),
            "paper_pdf_sha256": sha(HERE / "paper.pdf"),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    (HERE / "stanford-r3-o6-revision-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
