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
    original = {row["id"]: row for row in paper["objections"]}
    interaction = diag["terminal_heterogeneity"]["two_way_centered_effect_decomposition"]
    structural = diag["strategy_prompt_control"]

    receipt = {
        "schema_version": "1.0",
        "receipt_type": "paper-only-stanford-r3-revision",
        "paper_id": PAPER_ID,
        "paper_code": paper["code"],
        "revision": "STANFORD-R3-EXISTING-EVIDENCE-20260824",
        "base_review": matrix["matrix_id"],
        "stanford_r2_score": paper["r2"]["score"],
        "stanford_r2_verdict": paper["r2"]["verdict"],
        "paper_only_revision": True,
        "new_experiment": False,
        "new_provider_calls": 0,
        "new_rollouts": 0,
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
                },
                "boundary": "Finite 4x4 descriptive decomposition only; no general predictor of transfer-effect magnitude.",
            },
            "PROXY-O5": {
                "original_disposition": original["PROXY-O5"]["d"],
                "revision_status": "DEFERRED_SCIENTIFIC_REOPEN_REQUIRED",
                "action": "No no-memory terminal arm added; current estimand remains failure-conditioned versus success-conditioned memory.",
            },
            "PROXY-O6": {
                "original_disposition": original["PROXY-O6"]["d"],
                "revision_status": "DEFERRED_SCIENTIFIC_REOPEN_REQUIRED",
                "action": "No cross-model, live-loop, or corruption-sweep execution added.",
            },
        },
        "system_paper_requirements": {
            "abstract_words_approx": qa["abstract_words_approx"],
            "main_text_pages": 8,
            "related_work_moved_before_method_results": True,
            "experimental_setup_section_added": True,
            "execution_accounting_added": True,
            "strongest_simple_control_explicit": True,
            "mechanism_diagnostic_added": True,
            "heterogeneity_diagnostic_added": True,
            "failure_and_scope_boundaries_preserved": True,
            "manuscript_qa_status": qa["status"],
        },
        "artifact_bindings": {
            "diagnostic_sha256": sha(HERE / "existing-evidence-diagnostics.json"),
            "manuscript_qa_sha256": sha(HERE / "manuscript-qa.json"),
            "paper_pdf_sha256": sha(HERE / "paper.pdf"),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    (HERE / "stanford-r3-revision-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
