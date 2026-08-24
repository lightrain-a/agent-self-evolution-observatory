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
target_null = json.loads((ROOT / "generated" / "asset-first-stri-target-null-analysis-20260824.json").read_text(encoding="utf-8"))
witness_peeling = json.loads((ROOT / "generated" / "asset-first-stri-witness-peeling-20260824.json").read_text(encoding="utf-8"))
support_edit = json.loads((ROOT / "generated" / "asset-first-stri-support-edit-radius-20260824.json").read_text(encoding="utf-8"))
log_paths = [PAPER / "stri-20260816-generic-wrapper.log", PAPER / "stri-20260816-iclr2027-main.log"]
log_path = next((path for path in log_paths if path.exists()), log_paths[0])
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
    "1,387", "366", "127/595", "R^*_{0.75}=4/3",
    "Proposition 1 (quotient-factorization characterization)", "Corollary 1 (identity-local normalization is clone-sensitive)",
    "Proposition 2 (semantic-first construction handles arbitrary overlap)",
    "R^*(A;q)", "D^*(A;q)", "\\operatorname{cone}(A)", "2/15", "2/16=1/8", "7/120=0.0583", "restores prompt TV exactly to zero", "threshold 0.33", "all five observed specific--generic support-overlap pairs",
    "200 degree-preserving bipartite rewirings", "22 pairwise-disjoint three-row witnesses", "21.0\\% of Level-1", "71 deletions",
    "6/6", "0/6", "3/3", "p=0.00108",
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
    "representation-independent semantic target",
    "not a claim that the induction path would admit a literal duplicate",
    "package ID is absent from the questioner message",
    "neither supports population utility, safety, or regret",
    "not a new LP, cone theorem, or fairness objective",
    "not a population-level no-effect theorem",
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
check("all_current_entries_cited", len(cite_keys) == 21 and cite_keys == bib_keys == ledger_keys, f"cites={len(cite_keys)} bib={len(bib_keys)} ledger={len(ledger_keys)}")
check("ledger_zero_authority", sources.get("scientific_authority") is False)

# Stanford-round experiment-enrichment checks: all are offline structural controls on frozen support.
target_summary = target_null["target_ray_sensitivity"]["summary"]
share_summary = target_null["max_share_sensitivity"]["summary"]
null_summary = target_null["degree_preserving_null_ensemble"]["summary"]
peel_summary = witness_peeling["witness_peeling"]["summary"]
edit_radius = support_edit["support_edit_radius"]
check("target_rays_7", target_summary.get("targets") == 7)
check("target_rays_all_residual", target_summary.get("all_tested_targets_residual") is True)
check("target_neutral_rstar_2", abs(float(target_summary.get("neutral_R_star", -99)) - 2.0) < 1e-12)
check("max_share_9_valid", share_summary.get("valid_constraints") == 9)
check("max_share_all_residual", share_summary.get("all_valid_constraints_residual") is True)
check("degree_null_200", null_summary.get("residual_draws") == 200 and null_summary.get("equalizable_draws") == 0)
check("degree_null_exact_rstar_2", abs(float(null_summary.get("minimum_R_star", -99)) - 2.0) < 1e-12 and abs(float(null_summary.get("maximum_R_star", -99)) - 2.0) < 1e-12)
check("witness_peeling_22", peel_summary.get("peeling_rounds_before_equalizable") == 22)
check("witness_peeling_66_rows", peel_summary.get("pairwise_disjoint_witness_rows_removed") == 66)
check("witness_peeling_final_equalizable", abs(float(peel_summary.get("final_R_star", -99)) - 1.0) < 1e-12)
check("support_edit_min_add_22", edit_radius.get("minimum_additions_to_equalizable") == 22)
check("support_edit_min_delete_71", edit_radius.get("minimum_deletions_to_equalizable") == 71)
check("support_edit_add_gap_zero", abs(float(edit_radius.get("addition_solution", {}).get("mip_gap", -1))) < 1e-12)
check("support_edit_delete_gap_zero", abs(float(edit_radius.get("deletion_solution", {}).get("mip_gap", -1))) < 1e-12)
check("support_edit_both_verify_equalizable", abs(float(edit_radius.get("addition_solution", {}).get("verified_R_star", -99)) - 1.0) < 1e-12 and abs(float(edit_radius.get("deletion_solution", {}).get("verified_R_star", -99)) - 1.0) < 1e-12)
check("new_controls_zero_calls", target_null.get("scientific_boundary", {}).get("model_calls") == 0 and target_null.get("scientific_boundary", {}).get("gpu_runs") == 0 and witness_peeling.get("scientific_boundary", {}).get("model_calls") == 0 and witness_peeling.get("scientific_boundary", {}).get("gpu_runs") == 0 and support_edit.get("scientific_boundary", {}).get("model_calls") == 0 and support_edit.get("scientific_boundary", {}).get("gpu_runs") == 0)

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
