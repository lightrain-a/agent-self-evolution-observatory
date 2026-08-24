from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"
DIAG = json.loads((HERE / "existing-evidence-diagnostics.json").read_text())
O5 = json.loads((HERE / "o5-manuscript-evidence.json").read_text())
O6 = json.loads((HERE / "o6-final-evidence.json").read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approx_words(text: str) -> int:
    text = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"[$\\{}]", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def main() -> None:
    abstract = (SRC / "sections/00_abstract.tex").read_text()
    intro = (SRC / "sections/01_intro.tex").read_text()
    setup = (SRC / "sections/02b_setup.tex").read_text()
    f0 = (SRC / "sections/03_f0.tex").read_text()
    control = (SRC / "sections/03a_prompt_control.tex").read_text()
    downstream = (SRC / "sections/04_variance_protocol.tex").read_text()
    limits = (SRC / "sections/06_limitations_conclusion.tex").read_text()
    appendix = (SRC / "sections/07_appendix.tex").read_text()
    main_tex = (SRC / "main.tex").read_text()
    all_text = "\n".join([abstract, intro, setup, f0, control, downstream, limits, appendix])

    checks = {}
    checks["abstract_150_220"] = 150 <= approx_words(abstract) <= 220
    order = [main_tex.index(x) for x in [
        "sections/01_intro", "sections/05_related", "sections/02_mechanism", "sections/02b_setup",
        "sections/03_f0", "sections/03a_prompt_control", "sections/04_variance_protocol", "sections/06_limitations_conclusion"
    ]]
    checks["system_section_order"] = order == sorted(order)
    checks["experimental_setup_present"] = "\\section{Experimental Setup}" in setup
    checks["writer_jaccard_bound"] = "0.735" in all_text and abs(DIAG["writer_structure"]["mean_token_jaccard_distance"] - 0.734789) < 1e-9
    checks["controlled_structural_diagnostic_bound"] = all(x in all_text for x in ["0.556", "0.247", "0.309"])
    checks["interaction_diagnostic_bound"] = "84.1\\%" in all_text and abs(DIAG["terminal_heterogeneity"]["two_way_centered_effect_decomposition"]["source_future_interaction_share"] - 0.84058) < 1e-9
    wt = DIAG["terminal_heterogeneity"]["write_to_terminal_magnitude_diagnostic"]
    checks["write_terminal_nonmonotonic_diagnostic"] = all(x in all_text for x in ["0.031", "0.156", "not a monotonic proxy"]) and abs(wt["pearson_token_distance_vs_source_mean_absolute_effect"] + 0.729606) < 1e-6
    checks["terminal_effect_bound"] = "0.15625" in all_text and "0.00074" in all_text
    checks["provider_missingness_explicit"] = (
        DIAG["execution_accounting"]["f0_writer_provider_failures"] == 2
        and DIAG["claim_boundary"]["provider_missingness_resolved"] is False
        and all(x in all_text for x in ["failure-label arm", "ArkResponseStateError", "do not extrapolate"])
    )
    checks["no_memory_boundary_explicit"] = (
        O5["execution_accounting"]["recovery_scientifically_usable_units"] == 32
        and all(x in all_text for x in ["source-independent no-memory", "not an independent $4\\times4\\times3$ factorial"])
    )
    checks["o5_fresh_no_memory_control"] = (
        O5["status"] == "O5_FRESH_NO_MEMORY_CONTROL_COMPLETE"
        and O5["execution_accounting"]["recovery_scientifically_usable_units"] == 32
        and O5["execution_accounting"]["old_exploratory_no_memory_calls_reused"] == 0
        and O5["point_estimate_geometry_counts"] == {"BASELINE_CLOSER_TO_FAILURE": 2, "BASELINE_CLOSER_TO_SUCCESS": 6, "EQUIDISTANT": 8}
        and all(x in all_text for x in ["22/388", "25/387", "no new global $p$-value"])
    )
    checks["o6_cross_writer_boundary"] = (
        O6["status"] == "O6_CROSS_WRITER_BOUNDARY_COMPLETE"
        and O6["writer_stage"]["complete_pairs"] == 4
        and abs(O6["writer_stage"]["mean_token_jaccard_distance"] - 0.737482) < 1e-9
        and O6["terminal_stage"]["complete_calls"] == 256
        and abs(O6["terminal_stage"]["mean_absolute_success_rate_difference"] - 0.140625) < 1e-9
        and abs(O6["terminal_stage"]["permutation_p"] - 0.00012) < 1e-9
        and O6["terminal_stage"]["permutation_gate_pass"] is True
        and O6["terminal_stage"]["effect_floor_gate_pass"] is False
        and O6["terminal_stage"]["joint_gate_pass"] is False
        and O6["cross_writer_comparison"]["same_direction_among_nonzero_both"] == 4
        and O6["cross_writer_comparison"]["opposite_direction_among_nonzero_both"] == 2
        and all(x in all_text for x in ["0.737", "0.140625", "0.00012", "0.009375", "two reverse"])
    )
    checks["semantic_claim_not_expanded"] = "not an embedding" in all_text or "not embedding" in all_text
    checks["interaction_not_predictor"] = "predictive transfer model" in all_text and "84.1\\%" in all_text
    checks["writer_generalization_boundary"] = (
        O6["claim_boundary"]["terminal_cross_writer_generalization_supported"] is False
        and O6["claim_boundary"]["writer_invariant_effect_direction_supported"] is False
        and "writer-invariant downstream magnitude or direction" in limits
        and checks["o6_cross_writer_boundary"]
    )
    checks["live_loop_boundary_preserved"] = "live browser navigation" in limits and "remains unexecuted" in limits
    checks["inference_only_accounting"] = (
        "inference-only" in setup
        and "no training or local GPU fine-tuning" in setup
        and O6["execution_accounting"]["training_runs"] == 0
        and O6["execution_accounting"]["gpu_runs"] == 0
    )
    accounting = DIAG["execution_accounting"]
    checks["execution_accounting_complete"] = (
        accounting["f0_writer_requests"] == 12
        and accounting["f0c_writer_requests"] == 32
        and accounting["f1_action_existence_aligned_paired_units"] == 12
        and accounting["f1d_policy_calls"] == 96
        and accounting["f2_initial_total_calls"] == 108
        and accounting["f2r1_confirmatory_policy_calls"] == 256
        and accounting["known_requests_excluding_unresolved_low_level_call_count_for_f1_action_existence"] == 504
        and O5["execution_accounting"]["o5_total_provider_calls_consumed"] == 64
        and O5["execution_accounting"]["first_attempt_scientifically_usable_units"] == 0
        and O5["execution_accounting"]["recovery_scientifically_usable_units"] == 32
        and O6["execution_accounting"]["initial_2200_stage_provider_posts_observable_lower_bound"] == 9
        and O6["execution_accounting"]["repair_4096_writer_calls"] == 8
        and O6["execution_accounting"]["stage2_terminal_calls"] == 256
        and O6["execution_accounting"]["o6_provider_posts_observable_lower_bound"] == 273
        and all(x in setup for x in ["108 initial-terminal calls", "64 O5 calls", "832 requests", "at least 841"])
    )
    checks["diagnostic_zero_new_calls"] = "No provider calls" in DIAG["analysis_scope"]
    checks["system_E1_main_comparison"] = checks["terminal_effect_bound"]
    checks["system_E2_simplification_control"] = "0.105" in all_text and "0.0078" in all_text
    checks["system_E3_mechanism_analysis"] = "7 of 12" in all_text and checks["writer_jaccard_bound"] and checks["controlled_structural_diagnostic_bound"]
    checks["system_E4_robustness_boundary"] = checks["interaction_diagnostic_bound"] and checks["write_terminal_nonmonotonic_diagnostic"] and checks["no_memory_boundary_explicit"] and checks["o5_fresh_no_memory_control"] and checks["o6_cross_writer_boundary"]
    checks["system_E5_negative_failure"] = all(x in all_text for x in ["0.311", "0.160", "ArkResponseStateError", "zero scientific authority", "0.140625", "below the preregistered 0.15 floor"])
    checks["system_E6_efficiency_cost_scale"] = checks["execution_accounting_complete"] and checks["inference_only_accounting"]

    pdf = HERE / "paper.pdf"
    pdfinfo = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", pdfinfo, re.M).group(1))
    checks["compiled_pdf_present"] = pdf.exists() and pages >= 1
    page_text = {
        page: subprocess.check_output(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"], text=True)
        for page in range(1, pages + 1)
    }
    def heading_page(label: str) -> int | None:
        target = re.sub(r"[^a-z]", "", label.lower())
        for page, text in page_text.items():
            for line in text.splitlines():
                normalized = re.sub(r"[^a-z]", "", line.lower())
                if normalized == target:
                    return page
        return None

    conclusion_page = heading_page("Conclusion")
    references_page = heading_page("References")
    checks["main_text_within_nine_pages"] = conclusion_page is not None and conclusion_page <= 9
    checks["references_not_before_conclusion"] = references_page is not None and conclusion_page is not None and references_page >= conclusion_page

    payload = {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "STANFORD-R3-O6-CROSS-WRITER-20260824",
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
        "paper_pdf_sha256": sha(pdf),
        "main_tex_sha256": sha(SRC / "main.tex"),
        "scientific_authority": False,
        "experiment_authority": False,
        "claim_expansion": False,
        "new_provider_calls_exact": None,
        "new_provider_calls_observable_lower_bound": O5["execution_accounting"]["o5_total_provider_calls_consumed"] + O6["execution_accounting"]["o6_provider_posts_observable_lower_bound"],
        "new_scientifically_usable_provider_calls": O5["execution_accounting"]["recovery_scientifically_usable_units"] + O6["execution_accounting"]["repair_4096_writer_calls"] + O6["execution_accounting"]["stage2_terminal_calls"],
        "new_terminal_rollouts": O5["execution_accounting"]["recovery_scientifically_usable_units"] + O6["execution_accounting"]["stage2_terminal_calls"],
    }
    (HERE / "manuscript-qa.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
