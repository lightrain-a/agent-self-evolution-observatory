from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = Path(__file__).resolve().parent
body = (PAPER / "stri-20260816-narrow-body.tex").read_text(encoding="utf-8")
tables = (PAPER / "stri-20260816-tables.tex").read_text(encoding="utf-8")
wrapper = (PAPER / "stri-20260816-generic-wrapper.tex").read_text(encoding="utf-8")
bib = (PAPER / "stri-20260816-references.bib").read_text(encoding="utf-8")
sources = json.loads((PAPER / "stri-20260816-sources.json").read_text(encoding="utf-8"))
data = json.loads((ROOT / "generated" / "asset-first-stri-narrow-paper-table-data-20260816.json").read_text(encoding="utf-8"))
p0a = json.loads((ROOT / "generated" / "asset-first-stri-qwen3-merge-split-p0a-result-20260816.json").read_text(encoding="utf-8"))
final_review = json.loads((ROOT / "generated" / "asset-first-stri-narrow-final-review-20260816.json").read_text(encoding="utf-8"))
collision = json.loads((ROOT / "generated" / "asset-first-stri-narrow-collision-review-20260816.json").read_text(encoding="utf-8"))
log_path = PAPER / "stri-20260816-generic-wrapper.log"
log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""

checks: dict[str, bool] = {}
errors: list[str] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks[name] = bool(condition)
    if not condition:
        errors.append(name + (f": {detail}" if detail else ""))

# Canonical mechanism rows.
expected = {
    "Skill-SP API-Bank Level-1 full": (314, 183, 2.0),
    "Skill-SP Level-1 frozen calibration tools": (47, 33, 2.0),
    "Skill-SP Level-1 tool-disjoint heldout tools": (52, 38, 2.0),
    "Skill-SP API-Bank Level-3": (34, 0, 1.0),
    "Skill-SP logical first-party compiler validation": (128, 127, 1.0),
}
regimes = {str(row["regime"]): row for row in data["table_3_support_regime_boundary"]}
for regime, (covered, multi, rstar) in expected.items():
    row = regimes.get(regime, {})
    check(f"data_{regime}_covered", int(row.get("covered_rows", -1)) == covered)
    check(f"data_{regime}_multi", int(row.get("multi_membership_rows", -1)) == multi)
    check(f"data_{regime}_rstar", abs(float(row.get("R_star", -99)) - rstar) < 1e-12)

# Required paper literals are intentionally exact for high-load-bearing results.
for literal in [
    "314", "183", "47", "33", "52", "38", "34", "127/128", "R^*=2", "R^*=1",
    "14/24", "5/24", "8/24", "16/source",
    "INCONCLUSIVE\\_\\allowbreak PROPOSER\\_\\allowbreak QUALIFICATION\\_\\allowbreak FAILED",
]:
    check(f"paper_literal_{literal}", literal in body or literal in tables, literal)

# P0-A must remain an invalid/inconclusive support event, not a dynamic result.
check("p0a_decision", p0a.get("decision") == "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED")
check("p0a_no_scientific_result", p0a.get("scientific_result_available") is False)
check("p0a_no_protocol_update", p0a.get("protocol_valid_for_scientific_update") is False)
counts = p0a.get("generation_counts", {})
check("p0a_skill003_14", counts.get("skill_003", {}).get("contract_valid") == 14)
check("p0a_skill004_5", counts.get("skill_004", {}).get("contract_valid") == 5)
check("p0a_skill015_8", counts.get("skill_015", {}).get("contract_valid") == 8)

# Claim-boundary language must be present; common accidental overclaims must be absent.
required_boundaries = [
    "We \\textbf{do not} claim that a positive certificate causes task failure",
    "STRI-Cert is computationally novel relative to linear programming",
    "Support-Quotient Control has been empirically validated",
    "no dynamic witness statistic is scientifically admissible",
]
for text in required_boundaries:
    check(f"boundary_{text[:24]}", text in body)

forbidden_positive_patterns = {
    "sqc_success": r"\b(SQC|Support-Quotient Control)\s+(outperforms|improves|achieves|solves|removes)\b",
    "dynamic_supported": r"\b(dynamic STRI|dynamic propagation)\s+(is\s+)?(supported|confirmed|validated)\b",
    "downstream_harm_claim": r"\b(static|STRI|R\^\*)\b.{0,80}\b(causes|reduces|degrades)\b.{0,40}\b(success|utility|performance)\b",
    "overlap_always_harmful": r"\boverlap\b.{0,40}\b(always|necessarily)\b.{0,40}\b(harmful|bad|failure)\b",
}
for name, pattern in forbidden_positive_patterns.items():
    check(f"forbidden_{name}", re.search(pattern, body, flags=re.I | re.S) is None, pattern)

# Bibliography/source ledger consistency.
bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
cite_keys: set[str] = set()
for group in re.findall(r"\\cite(?:p|t)?\{([^}]+)\}", body):
    cite_keys.update(k.strip() for k in group.split(",") if k.strip())
ledger_keys = {str(e["key"]) for e in sources.get("entries", [])}
check("all_cites_in_bib", cite_keys <= bib_keys, str(sorted(cite_keys - bib_keys)))
check("all_cites_in_ledger", cite_keys <= ledger_keys, str(sorted(cite_keys - ledger_keys)))
check("bib_entries_have_ledger", bib_keys <= ledger_keys, str(sorted(bib_keys - ledger_keys)))
check("all_11_entries_cited", len(cite_keys) == 11 and cite_keys == bib_keys, f"cites={len(cite_keys)} bib={len(bib_keys)}")
check("ledger_zero_authority", sources.get("scientific_authority") is False)

# Build health.
check("latex_log_present", bool(log))
check("no_undefined_citations", "Citation" not in log or "undefined" not in log.lower())
check("no_undefined_references", "There were undefined references" not in log)
check("no_overfull_boxes", "Overfull" not in log)
check("bibliography_declared", "\\bibliography{stri-20260816-references}" in wrapper)

# Figure reproducibility / nonempty artifacts.
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
for filename in ["stri-overview.pdf", "stri-rstar-boundary.pdf", "stri-factor2-witnesses.pdf", "stri-ablation-robustness.pdf"]:
    path = PAPER / "figures" / filename
    check(f"figure_{filename}_exists", path.is_file() and path.stat().st_size > 1000)

# Independent review gates for the narrow claim scope.
check("final_review_ready", final_review.get("verdict") == "READY_NARROW_ICLR")
check("collision_survives", collision.get("verdict") == "SURVIVES_NARROWLY")

result = {
    "schema_version": "1.0",
    "paper_id": "STRI",
    "status": "PASS" if not errors else "FAIL",
    "checks_passed": sum(checks.values()),
    "checks_total": len(checks),
    "errors": errors,
    "citation_keys": sorted(cite_keys),
    "figure_sha256": {
        name: sha(PAPER / "figures" / name)
        for name in ["stri-overview.pdf", "stri-rstar-boundary.pdf", "stri-factor2-witnesses.pdf", "stri-ablation-robustness.pdf"]
        if (PAPER / "figures" / name).exists()
    },
    "review_state": {
        "final_premortem": final_review.get("verdict"),
        "narrow_collision": collision.get("verdict"),
    },
    "scientific_authority": False,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 1)
