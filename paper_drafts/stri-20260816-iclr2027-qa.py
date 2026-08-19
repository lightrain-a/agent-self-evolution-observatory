from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = Path(__file__).resolve().parent
MAIN = PAPER / "stri-20260816-iclr2027-main.tex"
BODY = PAPER / "stri-20260816-narrow-body.tex"
AUX = PAPER / "stri-20260816-iclr2027-main.aux"
LOG = PAPER / "stri-20260816-iclr2027-main.log"
PDF = PAPER / "stri-20260816-iclr2027-main.pdf"
BIB = PAPER / "stri-20260816-references.bib"
FORMAT = ROOT / "generated" / "asset-first-stri-iclr2027-format-state-20260816.json"
STYLE = PAPER / "iclr2027-official"

fmt = json.loads(FORMAT.read_text(encoding="utf-8"))
main = MAIN.read_text(encoding="utf-8")
body = BODY.read_text(encoding="utf-8")
aux = AUX.read_text(encoding="utf-8", errors="replace")
log = LOG.read_text(encoding="utf-8", errors="replace")
bib = BIB.read_text(encoding="utf-8")

checks: dict[str, bool] = {}
errors: list[str] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    checks[name] = bool(ok)
    if not ok:
        errors.append(name + (f": {detail}" if detail else ""))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Official-style provenance.
for filename, expected in fmt["official_style"]["files"].items():
    path = STYLE / filename
    check(f"style_{filename}_exists", path.is_file())
    if path.is_file():
        check(f"style_{filename}_sha", sha(path) == expected, sha(path))
check("style_unmodified_flag", fmt["official_style"].get("modified_after_download") is False)
check("official_initial_page_limit_9", fmt["format_rules"].get("initial_main_text_pages_max") == 9)
check("double_blind_rule", fmt["format_rules"].get("double_blind") is True)
check("ai_statement_required_rule", fmt["format_rules"].get("ai_use_statement_required") is True)

# Submission source and anonymity.
check("official_style_loaded", "\\usepackage{iclr2027_conference,times}" in main)
check("official_bst_loaded", "\\bibliographystyle{iclr2027_conference}" in main)
active_lines = [line for line in main.splitlines() if not line.lstrip().startswith("%")]
check("finalcopy_disabled", not any("\\iclrfinalcopy" in line for line in active_lines))
check("source_author_anonymous", "\\author{Anonymous Authors}" in main)
check("ai_use_statement_present", "\\subsection*{AI use statement}" in main)
check("repro_statement_present", "\\subsection*{Reproducibility statement}" in main)
check("body_single_paragraph_abstract", "\\begin{abstract}" in body and "\\end{abstract}" in body and "\n\n" not in body.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0])

# Exact page-limit check. The label is placed immediately after a clearpage that flushes all main-text floats.
m = re.search(r"\\newlabel\{stri:post-main-page\}\{\{[^}]*\}\{(\d+)\}", aux)
post_main_page = int(m.group(1)) if m else -1
main_text_pages = post_main_page - 1 if post_main_page > 0 else -1
check("post_main_label_found", m is not None)
check("main_text_pages_positive", main_text_pages > 0, str(main_text_pages))
check("main_text_pages_le_9", 0 < main_text_pages <= 9, str(main_text_pages))

# Build and bibliography health.
check("pdf_exists", PDF.is_file() and PDF.stat().st_size > 10000)
check("no_overfull_boxes", "Overfull" not in log)
check("no_undefined_citations", not re.search(r"Citation .* undefined|There were undefined citations", log))
check("no_undefined_references", "There were undefined references" not in log)
check("official_line_numbers_present", "Under review as a conference paper at ICLR 2027" in subprocess.check_output(["pdftotext", str(PDF), "-"], text=True))

pdf_text = subprocess.check_output(["pdftotext", str(PDF), "-"], text=True)
check("pdf_anonymous_banner", "Anonymous authors" in pdf_text and "Paper under double-blind review" in pdf_text)
check("pdf_ai_statement", "AI USE STATEMENT" in pdf_text and "generative AI" in pdf_text)
check("pdf_repro_statement", re.search(r"R\s*EPRODUCIBILITY STATEMENT", pdf_text, flags=re.I) is not None)
forbidden_identity_patterns = [
    r"\bwyt\b", r"lightrain", r"agent-self-evolution", r"Jimmy", r"222\.20", r"10\.42", r"hf_[A-Za-z0-9]{20,}", r"@users\.noreply\.github\.com"
]
for pattern in forbidden_identity_patterns:
    check(f"anonymous_no_{pattern}", re.search(pattern, pdf_text, flags=re.I) is None, pattern)

# Citations must use natbib commands and resolve to the bibliography.
cite_keys: set[str] = set()
for group in re.findall(r"\\cite(?:p|t)?\{([^}]+)\}", body):
    cite_keys.update(key.strip() for key in group.split(",") if key.strip())
bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
check("natbib_citations_present", "\\citep{" in body)
check("no_plain_cite_remaining", "\\cite{" not in body)
check("all_citations_in_bib", cite_keys <= bib_keys, str(sorted(cite_keys - bib_keys)))
check("all_bib_entries_cited", cite_keys == bib_keys, f"cites={len(cite_keys)} bib={len(bib_keys)}")

# Claim boundaries and the generalized target-conditioned audit remain locked while formatting changes.
for phrase in [
    "Proposition 1 (quotient-factorization characterization)",
    "Corollary 1 (identity-local normalization is clone-sensitive)",
    "Proposition 2 (semantic-first construction handles arbitrary overlap)",
    "R^*(A;q)",
    "D^*(A;q)",
    "representation-independent semantic target",
    "induction-time admission path would store a literal exact text duplicate",
    "$1/30+1/30$",
    "questioner message builder does not expose package ID",
    "$7/120=0.0583$",
    "We \\textbf{do not} infer task failure or longitudinal utility",
    "claim a new LP algorithm",
    "present a validated dynamic repair",
    "not a population-level no-effect theorem",
]:
    check(f"claim_boundary_{phrase[:24]}", phrase in body)

# Total pages are informational; references and mandatory/recommended statements are outside the initial main-text limit.
pdfinfo = subprocess.check_output(["pdfinfo", str(PDF)], text=True)
mt = re.search(r"^Pages:\s+(\d+)$", pdfinfo, flags=re.M)
total_pages = int(mt.group(1)) if mt else -1

result = {
    "schema_version": "1.0",
    "paper_id": "STRI",
    "status": "PASS" if not errors else "FAIL",
    "checks_passed": sum(checks.values()),
    "checks_total": len(checks),
    "errors": errors,
    "main_text_pages": main_text_pages,
    "main_text_page_limit": 9,
    "post_main_page": post_main_page,
    "total_pdf_pages": total_pages,
    "citation_count": len(cite_keys),
    "official_style_sha256": {
        filename: sha(STYLE / filename)
        for filename in fmt["official_style"]["files"]
        if (STYLE / filename).is_file()
    },
    "scientific_authority": False,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 1)
