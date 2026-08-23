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
    checks["terminal_effect_bound"] = "0.15625" in all_text and "0.00074" in all_text
    checks["provider_missingness_explicit"] = all(x in all_text for x in ["two", "failure-arm", "selection limitation"]) and "ArkResponseStateError" in all_text
    checks["no_memory_boundary_explicit"] = "not memory versus omission" in all_text and "no no-memory arm" in all_text
    checks["semantic_claim_not_expanded"] = "not an embedding" in all_text or "not embedding" in all_text
    checks["interaction_not_predictor"] = "not a predictive transfer model" in all_text or "not a learned predictor" in all_text
    checks["single_writer_domain_boundary"] = "Replication across writer families and task domains" in limits
    checks["live_loop_boundary_preserved"] = "live browser navigation" in limits and "remains unexecuted" in limits
    checks["inference_only_accounting"] = "inference-only" in setup and "no parameter training" in setup
    checks["diagnostic_zero_new_calls"] = "No provider calls" in DIAG["analysis_scope"]

    pdf = HERE / "paper.pdf"
    pdfinfo = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", pdfinfo, re.M).group(1))
    checks["compiled_pdf_present"] = pdf.exists() and pages >= 1

    payload = {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "STANFORD-R3-EXISTING-EVIDENCE-20260824",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "abstract_words_approx": approx_words(abstract),
        "pdf_pages_total": pages,
        "main_text_page_boundary": "Conclusion ends on PDF page 8; references/appendix occupy subsequent pages in the compiled candidate.",
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
