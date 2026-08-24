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
        "revision": "STANFORD-R3-O5-NO-MEMORY-20260824",
        "base_review": matrix["matrix_id"],
        "stanford_r2_score": paper["r2"]["score"],
        "stanford_r2_verdict": paper["r2"]["verdict"],
        "paper_only_revision": False,
        "new_experiment": True,
        "new_provider_calls": 64,
        "new_rollouts": 32,
        "claim_expansion": False,
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
                },
                "boundary": "Finite 4x4 descriptive decomposition plus a four-source non-monotonic magnitude check only; no general predictor of transfer-effect magnitude.",
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
                "revision_status": "DEFERRED_SCIENTIFIC_REOPEN_REQUIRED",
                "action": "No cross-model, live-loop, or corruption-sweep execution added.",
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
                    "evidence": "All 16 frozen source-future cells are exposed: 84.1% of centered signed-effect variation is source-by-future interaction, future task 164 is a joint ceiling, write divergence magnitude is not a monotonic downstream-effect proxy, and a fresh 32-call no-memory control locates the two memory branches relative to omission without pseudoreplication.",
                },
                "E5_negative_failure_cases": {
                    "status": "PASS_VISIBLE_NEGATIVES",
                    "evidence": "Two F0 failure-arm provider incompletions remain selection debt; F1D p=0.311 and initial terminal p=0.160 remain visible non-passing tests; the first O5 32-call attempt is retained as an execution-validator failure with zero scientific authority before a frozen one-for-one recovery.",
                },
                "E6_efficiency_cost_scale": {
                    "status": "PASS_ACCOUNTED",
                    "evidence": {
                        "inference_only": True,
                        "known_directly_countable_requests": accounting["known_requests_excluding_unresolved_low_level_call_count_for_f1_action_existence"] + o5["execution_accounting"]["o5_total_provider_calls_consumed"],
                        "o5_provider_calls_consumed": o5["execution_accounting"]["o5_total_provider_calls_consumed"],
                        "o5_scientifically_usable_calls": o5["execution_accounting"]["recovery_scientifically_usable_units"],
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
            "manuscript_qa_sha256": sha(HERE / "manuscript-qa.json"),
            "paper_pdf_sha256": sha(HERE / "paper.pdf"),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    (HERE / "stanford-r3-o5-revision-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
