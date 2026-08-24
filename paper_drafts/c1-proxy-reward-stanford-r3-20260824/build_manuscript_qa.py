from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"
DIAG = json.loads((HERE / "existing-evidence-diagnostics.json").read_text())


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
    checks["provider_missingness_explicit"] = all(x in all_text for x in ["two", "failure-arm", "selection limitation"]) and "ArkResponseStateError" in all_text
    checks["no_memory_boundary_explicit"] = "not memory versus omission" in all_text and "no no-memory arm" in all_text
    checks["semantic_claim_not_expanded"] = "not an embedding" in all_text or "not embedding" in all_text
    checks["interaction_not_predictor"] = "not a predictive transfer model" in all_text or "not a learned predictor" in all_text
    checks["single_writer_domain_boundary"] = "Replication across writer families and task domains" in limits
    checks["live_loop_boundary_preserved"] = "live browser navigation" in limits and "remains unexecuted" in limits
    checks["inference_only_accounting"] = "inference-only" in setup and "no parameter training" in setup
    accounting = DIAG["execution_accounting"]
    checks["execution_accounting_complete"] = (
        accounting["f0_writer_requests"] == 12
        and accounting["f0c_writer_requests"] == 32
        and accounting["f1_action_existence_aligned_paired_units"] == 12
        and accounting["f1d_policy_calls"] == 96
        and accounting["f2_initial_total_calls"] == 108
        and accounting["f2r1_confirmatory_policy_calls"] == 256
        and accounting["known_requests_excluding_unresolved_low_level_call_count_for_f1_action_existence"] == 504
        and all(x in setup for x in ["96 policy calls", "96 primary memory-conditioned calls plus 12 no-memory calls", "504 directly countable"])
    )
    checks["diagnostic_zero_new_calls"] = "No provider calls" in DIAG["analysis_scope"]
    checks["system_E1_main_comparison"] = checks["terminal_effect_bound"]
    checks["system_E2_simplification_control"] = "0.105" in all_text and "0.0078" in all_text
    checks["system_E3_mechanism_analysis"] = "7 of 12" in all_text and checks["writer_jaccard_bound"] and checks["controlled_structural_diagnostic_bound"]
    checks["system_E4_robustness_boundary"] = checks["interaction_diagnostic_bound"] and checks["write_terminal_nonmonotonic_diagnostic"] and checks["no_memory_boundary_explicit"]
    checks["system_E5_negative_failure"] = all(x in all_text for x in ["0.311", "0.160", "ArkResponseStateError"])
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
        "revision": "STANFORD-R3-EXISTING-EVIDENCE-20260824",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "abstract_words_approx": approx_words(abstract),
        "pdf_pages_total": pages,
        "main_text_pages": conclusion_page,
        "references_begin_page": references_page,
        "main_text_page_boundary": f"Conclusion appears on PDF page {conclusion_page}; references begin on PDF page {references_page}.",
        "checks": checks,
        "diagnostic_sha256": sha(HERE / "existing-evidence-diagnostics.json"),
        "paper_pdf_sha256": sha(pdf),
        "main_tex_sha256": sha(SRC / "main.tex"),
        "scientific_authority": False,
        "experiment_authority": False,
        "claim_expansion": False,
        "new_provider_calls": 0,
        "new_rollouts": 0,
    }
    (HERE / "manuscript-qa.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
