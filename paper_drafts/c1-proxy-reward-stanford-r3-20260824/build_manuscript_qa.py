from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = HERE / "source"
DIAG = json.loads((HERE / "existing-evidence-diagnostics.json").read_text())
O5 = json.loads((HERE / "o5-manuscript-evidence.json").read_text())
O6 = json.loads((HERE / "o6-final-evidence.json").read_text())
O6_REDUCTION = json.loads((HERE / "o6-full-bank-corruption-reduction.json").read_text())
CHRONOLOGY = json.loads((HERE / "f2r1-chronology-receipt.json").read_text())
EXPANSION = json.loads((HERE / "baseline-aligned-expansion-evidence.json").read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approx_words(text: str) -> int:
    text = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"[$\\{}]", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def main() -> None:
    abstract = (SRC / "sections/00_abstract.tex").read_text()
    intro = (SRC / "sections/01_intro.tex").read_text()
    related = (SRC / "sections/05_related.tex").read_text()
    mechanism = (SRC / "sections/02_mechanism.tex").read_text()
    setup = (SRC / "sections/02b_setup.tex").read_text()
    f0 = (SRC / "sections/03_f0.tex").read_text()
    control = (SRC / "sections/03a_prompt_control.tex").read_text()
    downstream = (SRC / "sections/04_variance_protocol.tex").read_text()
    limits = (SRC / "sections/06_limitations_conclusion.tex").read_text()
    appendix = (SRC / "sections/07_appendix.tex").read_text()
    main_tex = (SRC / "main.tex").read_text()
    main_text = "\n".join([abstract, intro, related, mechanism, setup, f0, control, downstream, limits])
    all_text = main_text + "\n" + appendix

    e = EXPANSION["experiments"]
    acct = EXPANSION["execution_accounting"]
    cb = EXPANSION["claim_boundary"]
    checks: dict[str, bool] = {}

    checks["abstract_150_220"] = 150 <= approx_words(abstract) <= 220
    checks["transport_boundary_title"] = "\\title{Reward Errors Become Persistent State: Write-Time Causality and Transport Boundaries in Agent Memory}" in main_tex
    checks["identification_transport_decomposition"] = all(x in intro for x in ["identification-and-transport decomposition", "forced downstream swaps", "negative transport boundary"])
    checks["no_research_os_process_language_main"] = all(x not in main_text for x in ["\\section{F0:", "\\section{C4:", "reviewer-requested", "Stanford-targeted", "Post-ready"])
    checks["system_section_order"] = [main_tex.index(x) for x in ["sections/01_intro", "sections/05_related", "sections/02_mechanism", "sections/02b_setup", "sections/03_f0", "sections/03a_prompt_control", "sections/04_variance_protocol", "sections/06_limitations_conclusion"]] == sorted(main_tex.index(x) for x in ["sections/01_intro", "sections/05_related", "sections/02_mechanism", "sections/02b_setup", "sections/03_f0", "sections/03a_prompt_control", "sections/04_variance_protocol", "sections/06_limitations_conclusion"])
    checks["experimental_setup_present"] = "\\section{Experimental Setup}" in setup

    checks["original_write_bound"] = (
        abs(DIAG["writer_structure"]["mean_token_jaccard_distance"] - 0.734789) < 1e-9
        and DIAG["execution_accounting"]["f0_writer_provider_failures"] == 2
        and all(x in all_text for x in ["0.735", "conditional on paired completion", "task 24", "task 47"])
    )
    checks["breadth_write_20_pair_bound"] = (
        EXPANSION["status"] == "BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP"
        and e["B2_write_breadth"]["combined_complete_pairs"] == 20
        and e["B2_write_breadth"]["combined_exact_content_change_rate"] == 1.0
        and e["B2_write_breadth"]["combined_title_set_change_rate"] == 1.0
        and abs(e["B2_write_breadth"]["new_mean_token_jaccard_distance"] - 0.65757) < 1e-9
        and abs(e["B2_write_breadth"]["pooled_20_pair_mean_token_jaccard_distance"] - 0.673014) < 1e-9
        and e["B2_write_breadth"]["new_distinct_intent_templates"] == 11
        and all(x in all_text for x in ["20/20", "0.65757", "0.673014", "11 intent-template"])
    )
    checks["prompt_rewording_control_bound"] = all(x in all_text for x in ["0.700", "0.595", "0.105", "0.0078"])
    checks["controlled_structural_diagnostic_bound"] = all(x in all_text for x in ["0.556", "0.247", "0.309"])

    checks["f2r1_chronology_bound"] = (
        CHRONOLOGY["status"] == "CHRONOLOGY_AND_UNIFORM_REPLICATION_VERIFIED"
        and CHRONOLOGY["relationship"]["confirmatory_was_designed_after_initial_nonpass"] is True
        and CHRONOLOGY["relationship"]["same_4x4_support"] is True
        and CHRONOLOGY["relationship"]["source_selection_changed"] is False
        and CHRONOLOGY["relationship"]["future_task_selection_changed"] is False
        and CHRONOLOGY["relationship"]["effect_floor_changed"] is False
        and CHRONOLOGY["relationship"]["alpha_changed"] is False
        and all(x in all_text for x in ["0.145833", "0.160128", "0.15625", "0.00074", "same-support"])
    )
    checks["forced_swap_not_native_transport"] = all(x in main_text for x in ["forced memory-swap", "forced-intervention sensitivity", "not retrieval probability", "not source-faithful retrieval transport"])

    checks["original_bank_retrieval_audit_bound"] = (
        e["B1_original_bank_exact_retrieval"]["shopping_heldout_tasks"] == 188
        and e["B1_original_bank_exact_retrieval"]["threshold_hits"] == 8
        and abs(e["B1_original_bank_exact_retrieval"]["hit_rate"] - 0.04255319) < 1e-12
        and e["B1_original_bank_exact_retrieval"]["original_frozen_future_hits"] == 0
        and all(x in all_text for x in ["8 of 188", "4.26\\%", "none of the four forced-terminal futures"])
    )
    checks["expanded_bank_retrieval_audit_bound"] = (
        e["B3_expanded_bank_exact_retrieval"]["source_memory_count"] == 20
        and e["B3_expanded_bank_exact_retrieval"]["shopping_heldout_tasks"] == 172
        and e["B3_expanded_bank_exact_retrieval"]["threshold_hits"] == 125
        and abs(e["B3_expanded_bank_exact_retrieval"]["hit_rate"] - 0.72674419) < 1e-12
        and e["B3_expanded_bank_exact_retrieval"]["offline_eligible_tasks"] == 36
        and e["B3_expanded_bank_exact_retrieval"]["eligible_intent_templates"] == 13
        and all(x in all_text for x in ["125 of 172", "72.7\\%", "36", "13 intent-template"])
    )
    checks["native_transport_negative_bound"] = (
        e["B4_native_retrieval_matched_branch_transport"]["complete_calls"] == 288
        and abs(e["B4_native_retrieval_matched_branch_transport"]["mean_absolute_success_rate_difference"] - 0.020833) < 1e-9
        and abs(e["B4_native_retrieval_matched_branch_transport"]["permutation_p"] - 0.428866) < 1e-9
        and e["B4_native_retrieval_matched_branch_transport"]["gate_pass"] is False
        and e["B4_native_retrieval_matched_branch_transport"]["zero_cells"] == 34
        and e["B4_native_retrieval_matched_branch_transport"]["joint_floor_cells"] == 18
        and e["B4_native_retrieval_matched_branch_transport"]["joint_ceiling_cells"] == 16
        and all(x in all_text for x in ["0.02083", "0.4289", "34/36", "eighteen", "sixteen"])
    )
    checks["native_no_memory_floor_fail_bound"] = (
        e["B5_native_support_no_memory"]["complete_calls"] == 144
        and abs(e["B5_native_support_no_memory"]["mean_absolute_memory_presence_effect"] - 0.045139) < 1e-9
        and abs(e["B5_native_support_no_memory"]["permutation_p"] - 0.00147) < 1e-9
        and e["B5_native_support_no_memory"]["gate_pass"] is False
        and e["B5_native_support_no_memory"]["geometry_counts"] == {"CLOSER_TO_FAILURE": 1, "CLOSER_TO_SUCCESS": 1, "EQUIDISTANT": 34}
        and all(x in all_text for x in ["0.04514", "0.00147", "0.15 practical", "34/36"])
    )
    checks["experiment_ladder_present"] = all(x in downstream for x in ["Experimental ladder", "Write breadth", "Native branch transport", "DeepSeek policy transfer"])

    checks["o5_original_branch_location_preserved"] = (
        O5["status"] == "O5_FRESH_NO_MEMORY_CONTROL_COMPLETE"
        and O5["point_estimate_geometry_counts"] == {"BASELINE_CLOSER_TO_FAILURE": 2, "BASELINE_CLOSER_TO_SUCCESS": 6, "EQUIDISTANT": 8}
        and all(x in appendix for x in ["22/388", "25/387", "no new global significance test"])
    )
    checks["o6_cross_writer_boundary"] = (
        O6["status"] == "O6_CROSS_WRITER_BOUNDARY_COMPLETE"
        and O6["writer_stage"]["complete_pairs"] == 4
        and abs(O6["writer_stage"]["mean_token_jaccard_distance"] - 0.737482) < 1e-9
        and O6["terminal_stage"]["complete_calls"] == 256
        and abs(O6["terminal_stage"]["mean_absolute_success_rate_difference"] - 0.140625) < 1e-9
        and abs(O6["terminal_stage"]["permutation_p"] - 0.00012) < 1e-9
        and O6["terminal_stage"]["joint_gate_pass"] is False
        and all(x in all_text for x in ["0.737", "0.140625", "0.00012", "two of six"])
    )
    checks["cross_policy_support_stop_not_null"] = (
        e["B6_cross_policy_support_stop"]["scientifically_usable_calls"] == 0
        and e["B6_cross_policy_support_stop"]["provider_posts_parent"] == 1
        and e["B6_cross_policy_support_stop"]["provider_posts_r1"] == 1
        and e["B6_cross_policy_support_stop"]["failure_reason"] == "length/no assistant text"
        and e["B6_cross_policy_support_stop"]["B7_executed"] is False
        and cb["cross_policy_terminal_transfer_status"] == "SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS"
        and all(x in all_text for x in ["900-token", "2,200-token", "zero scientific units", "not a scientific null"])
    )

    checks["top1_retrieval_contract_preserved"] = (
        O6_REDUCTION["released_mechanism_facts"]["default_top_k"] == 1
        and abs(O6_REDUCTION["released_mechanism_facts"]["default_similarity_threshold"] - 0.3) < 1e-12
        and O6_REDUCTION["released_mechanism_facts"]["reward_conditioned_memory_document_used_in_retrieval_embedding"] is False
        and all(x in all_text for x in ["all-MiniLM-L6-v2", "top-$1$", "threshold 0.3"])
    )
    checks["live_transport_boundary_preserved"] = all(x in limits for x in ["unavailable live endpoints", "live end-to-end or population transport"])
    checks["semantic_diagnostics_bounded"] = all(x in limits for x in ["Token Jaccard", "operation slots", "bounded diagnostics"])
    checks["corruption_decomposition_demoted"] = all(x in appendix for x in ["Bounded corruption-rate consequence", "not an empirical corruption sweep"])

    checks["execution_accounting_expansion"] = (
        acct["new_provider_posts"] == 498
        and acct["new_scientifically_usable_provider_completions"] == 464
        and acct["new_scientifically_usable_writer_calls"] == 32
        and acct["new_scientifically_usable_terminal_rollouts"] == 432
        and acct["cross_policy_support_failure_posts"] == 2
        and acct["updated_full_paper_observable_provider_posts_lower_bound"] == 1339
        and all(x in appendix for x in ["498 observable POSTs", "464 are scientifically usable", "432 terminal rollouts", "at least 1,339"])
    )
    checks["inference_only_accounting"] = (
        "inference-only" in setup
        and "no training or local GPU fine-tuning" in setup
        and acct["training_runs"] == 0 and acct["gpu_runs"] == 0
    )
    checks["claim_boundary_matrix"] = (
        cb["write_channel_breadth_supported"] is True
        and cb["forced_swap_terminal_sensitivity_supported"] is True
        and cb["native_retrieval_matched_branch_transport_supported"] is False
        and cb["native_memory_presence_practical_effect_supported"] is False
        and cb["cross_policy_terminal_transfer_supported"] is None
        and cb["live_browser_transport_supported"] is False
        and all(x in limits for x in ["writer-invariant effects are not established", "not a scientific null", "local to the released ReasoningBank mechanism"])
    )

    story_text = (REPO / "paper-story-reward-memory.js").read_text()
    reader_text = (REPO / "paper-reader-data.js").read_text()
    checks["paper_story_expansion_current"] = all(x in story_text for x in ["20/20", "72.7", "0.02083", "0.04514", "support stop"])
    checks["paper_reader_expansion_current"] = all(x in reader_text for x in ["20/20", "125/172", "0.02083", "0.04514"])

    pdf = HERE / "paper.pdf"
    pdfinfo = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", pdfinfo, re.M).group(1))
    checks["compiled_pdf_present"] = pdf.exists() and pages >= 1
    page_text = {page: subprocess.check_output(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"], text=True) for page in range(1, pages + 1)}

    def heading_page(label: str) -> int | None:
        target = re.sub(r"[^a-z]", "", label.lower())
        for page, text in page_text.items():
            for line in text.splitlines():
                if re.sub(r"[^a-z]", "", line.lower()) == target:
                    return page
        return None

    conclusion_page = heading_page("Conclusion")
    references_page = heading_page("References")
    checks["main_text_within_nine_pages"] = conclusion_page is not None and conclusion_page <= 9
    checks["references_not_before_conclusion"] = references_page is not None and conclusion_page is not None and references_page >= conclusion_page
    checks["expanded_pdf_reasonable_total_pages"] = pages <= 17

    payload = {
        "schema_version": "1.1",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "ICLR-BASELINE-ALIGNED-EXPERIMENT-EXPANSION-20260824",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "abstract_words_approx": approx_words(abstract),
        "pdf_pages_total": pages,
        "main_text_pages": conclusion_page,
        "references_begin_page": references_page,
        "main_text_page_boundary": f"Conclusion appears on PDF page {conclusion_page}; references begin on PDF page {references_page}.",
        "checks": checks,
        "diagnostic_sha256": sha(HERE / "existing-evidence-diagnostics.json"),
        "o5_evidence_sha256": sha(HERE / "o5-manuscript-evidence.json"),
        "o6_evidence_sha256": sha(HERE / "o6-final-evidence.json"),
        "o6_full_bank_reduction_sha256": sha(HERE / "o6-full-bank-corruption-reduction.json"),
        "f2r1_chronology_receipt_sha256": sha(HERE / "f2r1-chronology-receipt.json"),
        "baseline_aligned_expansion_evidence_sha256": sha(HERE / "baseline-aligned-expansion-evidence.json"),
        "paper_story_reward_memory_sha256": sha(REPO / "paper-story-reward-memory.js"),
        "paper_reader_data_sha256": sha(REPO / "paper-reader-data.js"),
        "paper_pdf_sha256": sha(pdf),
        "main_tex_sha256": sha(SRC / "main.tex"),
        "scientific_authority": False,
        "experiment_authority": False,
        "claim_expansion": False,
        "new_provider_calls_exact": acct["new_provider_posts"],
        "new_scientifically_usable_provider_calls": acct["new_scientifically_usable_provider_completions"],
        "new_scientifically_usable_writer_calls": acct["new_scientifically_usable_writer_calls"],
        "new_terminal_rollouts": acct["new_scientifically_usable_terminal_rollouts"],
        "cross_policy_support_failure_posts": acct["cross_policy_support_failure_posts"],
        "prior_full_paper_observable_provider_posts_lower_bound": acct["prior_full_paper_observable_provider_posts_lower_bound"],
        "updated_full_paper_observable_provider_posts_lower_bound": acct["updated_full_paper_observable_provider_posts_lower_bound"],
        "training_runs": 0,
        "gpu_runs": 0,
    }
    (HERE / "manuscript-qa.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
