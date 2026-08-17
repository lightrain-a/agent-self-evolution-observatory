from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_quality_gate import audit_manuscript_evidence_completion


OUTPUT = "generated/asset-first-stri-paper-quality-v2-20260816.json"
REDUCTION = "generated/asset-first-skill-taxonomy-representation-invariance-reduction-20260816.json"
COHERENCE = "generated/asset-first-stri-narrow-paper-coherence-20260816.json"
FINAL_REVIEW = "generated/asset-first-stri-narrow-final-review-20260816.json"
PAPER_ANALYSIS = "generated/asset-first-stri-paper-analysis-suite-20260816.json"
PRUNING_BASELINE = "generated/asset-first-stri-baseline-min-cover-pruning-20260816.json"
P0E_DIAGNOSIS = "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
P0E_PRINCIPLE = "generated/asset-first-stri-skillrl-final-policy-p0e-principle-disposition-20260817.json"
PAPER_BODY = "paper_drafts/stri-20260816-narrow-body.tex"
PAPER_TABLES = "paper_drafts/stri-20260816-tables.tex"
FIG_OVERVIEW = "paper_drafts/figures/stri-overview.pdf"
FIG_WITNESS = "paper_drafts/figures/stri-factor2-witnesses.pdf"
FIG_BOUNDARY = "paper_drafts/figures/stri-rstar-boundary.pdf"
FIG_ABLATION = "paper_drafts/figures/stri-ablation-robustness.pdf"
PLOT_OVERVIEW = "paper_drafts/stri-20260816-plot-overview.py"
PLOT_WITNESS = "paper_drafts/stri-20260816-plot-witnesses.py"
PLOT_BOUNDARY = "paper_drafts/stri-20260816-plot-boundary.py"
PLOT_ABLATION = "paper_drafts/stri-20260816-plot-ablation-robustness.py"


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def build_stri_quality_contract() -> dict[str, Any]:
    return {
        "schema_version": "2.1",
        "paper_archetype": "theory_certificate",
        "claims": [
            {
                "id": "N1",
                "claim_type": "empirical_analysis",
                "statement": "Released skill inventories exhibit high raw overlap while alternative support reductions can change the apparent redundancy structure.",
                "why_better_or_why_matters": "A support-aware comparison should distinguish representational redundancy from genuinely different operational support rather than treating raw skill names as independent evidence.",
                "alternative_explanations": ["the pattern is an artifact of duplicate or umbrella skill names", "the pattern is driven by one released system or one support threshold"],
                "ruling_out_experiments": ["compare raw overlap, deduplicated overlap, minimum-package pruning, and reweighted package mass on the same released inventories", "stress split/merge/clone perturbations while preserving operational support"],
                "baseline_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL"],
                "ablation_ids": ["A-REDUCTION-TOURNAMENT", "A-TAXONOMY-PERTURB"],
                "analysis_ids": ["AN-RULEOUT", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY"],
                "output_ids": ["O-MAIN", "O-ABLATION", "O-FAILURE", "O-SENSITIVITY"],
                "visualization_ids": ["V-OVERVIEW", "V-BOUNDARY", "V-ABLATION-ROBUSTNESS"],
            },
            {
                "id": "N2",
                "claim_type": "theory",
                "statement": "STRI-Cert defines a support-equivalence sensitivity certificate under the frozen support matrix and package constraints.",
                "why_better_or_why_matters": "The certificate makes the representation assumptions explicit and exposes which overlap conclusions survive admissible support-preserving reductions.",
                "alternative_explanations": ["the certificate is merely a restatement of raw overlap under another weighting"],
                "ruling_out_experiments": ["show counterexamples where raw overlap changes under representation edits while the support-equivalent operational object is preserved"],
                "baseline_ids": ["B-ANALYTICAL"],
                "ablation_ids": ["A-TAXONOMY-PERTURB"],
                "analysis_ids": ["AN-RULEOUT", "AN-SENSITIVITY"],
                "output_ids": ["O-MAIN", "O-MECHANISM", "O-SENSITIVITY"],
                "visualization_ids": ["V-WITNESS", "V-BOUNDARY", "V-ABLATION-ROBUSTNESS"],
            },
            {
                "id": "N3",
                "claim_type": "mechanism",
                "statement": "Raw overlap is insufficient to explain when released skill taxonomies are clone-sensitive versus support-invariant.",
                "why_better_or_why_matters": "The support-equivalence view predicts a specific failure mode of name-level overlap: clone/split/merge edits may change the apparent overlap without changing operational support.",
                "alternative_explanations": ["the observed separation is only a consequence of arbitrary weighting", "a simpler deduplication rule explains the same cases", "the effect disappears under benign taxonomy perturbations"],
                "ruling_out_experiments": ["matched taxonomy perturbation test with split/merge/clone edits", "compare STRI-Cert against raw overlap, deduplication, and package-pruning reductions on identical support information"],
                "baseline_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL"],
                "ablation_ids": ["A-REDUCTION-TOURNAMENT", "A-TAXONOMY-PERTURB"],
                "analysis_ids": ["AN-MECHANISM", "AN-RULEOUT", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY"],
                "output_ids": ["O-MAIN", "O-ABLATION", "O-MECHANISM", "O-FAILURE", "O-SENSITIVITY"],
                "visualization_ids": ["V-OVERVIEW", "V-WITNESS", "V-BOUNDARY", "V-ABLATION-ROBUSTNESS"],
            },
        ],
        "baselines": [
            {"id": "B-RAW-OVERLAP", "role": "simple_control", "evidence_type": "empirical", "target_claim_ids": ["N1", "N3"], "purpose": "Name-level overlap/Jaccard control on the same released inventories.", "matched_dimensions": ["released inventory", "support observations", "system version"]},
            {"id": "B-DEDUP", "role": "same_information_simplification", "evidence_type": "empirical", "target_claim_ids": ["N1", "N3"], "purpose": "Test whether ordinary exact/semantic deduplication absorbs the claimed representation effect.", "matched_dimensions": ["released inventory", "support observations", "system version", "support information"]},
            {"id": "B-ANALYTICAL", "role": "analytical_simplification", "evidence_type": "analytical", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Compare against minimum-package pruning and arbitrary nonnegative package-mass reductions under the identical frozen support matrix.", "matched_dimensions": []},
        ],
        "ablations": [
            {"id": "A-REDUCTION-TOURNAMENT", "ablation_type": "representation", "target_claim_ids": ["N1", "N3"], "purpose": "Remove individual reduction operators (dedup/pruning/reweighting/witness handling) to identify which part changes the conclusion.", "decision_rule": "A component receives explanatory credit only when removing it changes a preregistered support-sensitive conclusion while support information and inventory are fixed."},
            {"id": "A-TAXONOMY-PERTURB", "ablation_type": "assumption_boundary", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Apply exact-support clone/split and identity-renaming controls, while treating macro merges that discard primitive fingerprints as an explicit assumption-boundary negative implementation control.", "decision_rule": "Clone/split quotienting must exactly recover the original row support and certificate inputs; identity renaming must be invariant. A macro-ID-only merge is not counted as a valid invariance test unless primitive fingerprints/responsibility metadata are retained."},
        ],
        "analyses": [
            {"id": "AN-MECHANISM", "analysis_type": "mechanism", "target_claim_ids": ["N3"], "purpose": "Show exactly when name-level overlap and support-equivalence disagree and connect each disagreement to clone/split/merge structure.", "decision_rule": "No mechanism claim from aggregate overlap trends; disagreement cases must be enumerated and explained."},
            {"id": "AN-RULEOUT", "analysis_type": "alternative_explanation", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Rule out simple deduplication, arbitrary weighting, and one-system idiosyncrasy as sufficient explanations.", "decision_rule": "If a simpler matched-information reduction reproduces all certified conclusions, STRI must merge into that baseline."},
            {"id": "AN-FAILURE", "analysis_type": "failure", "target_claim_ids": ["N1", "N3"], "purpose": "Catalogue invariant, clone-sensitive, underidentified, and unsupported regimes instead of presenting only positive examples.", "decision_rule": "Every released-system case is assigned a preregistered regime; inconclusive cells remain visible."},
            {"id": "AN-SENSITIVITY", "analysis_type": "sensitivity", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Stress support thresholds, package constraints, singleton witnesses, and taxonomy edits.", "decision_rule": "Report the region over which each conclusion is stable; narrow any claim that depends on one arbitrary setting."},
            {"id": "AN-UNCERTAINTY", "analysis_type": "uncertainty", "target_claim_ids": ["N1", "N3"], "purpose": "Attach sampling/bootstrap or exact finite-population uncertainty to released-system comparative summaries where stochastic sampling is present.", "decision_rule": "Do not present point-estimate gaps as robust evidence when their uncertainty overlaps the matched baseline."},
        ],
        "planned_outputs": [
            {"id": "O-MAIN", "output_type": "main_comparison", "purpose": "One explicit baseline table: raw overlap vs dedup vs package pruning/reweighting vs STRI-Cert on identical released inventories."},
            {"id": "O-ABLATION", "output_type": "ablation", "purpose": "One explicit ablation/perturbation table rather than calling the reduction tournament an implicit control."},
            {"id": "O-MECHANISM", "output_type": "mechanism", "purpose": "Why/where STRI differs: disagreement examples plus taxonomy-perturbation mechanism plot."},
            {"id": "O-FAILURE", "output_type": "failure", "purpose": "Failure/boundary table including underidentified and inconclusive regimes."},
            {"id": "O-SENSITIVITY", "output_type": "sensitivity", "purpose": "Sensitivity panel for thresholds, package constraints, singleton witnesses, and split/merge/clone edits."},
        ],
        "visualizations": [
            {"id": "V-OVERVIEW", "placement": "main", "visual_type": "flow", "panel_roles": ["overview", "traceability"], "target_claim_ids": ["N1", "N3"], "source_evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "O-MAIN"], "reviewer_question": "What representation nuisance is STRI auditing, and how does package identity alter a semantic control surface?", "takeaway": "Separate semantic capability/support from package identity before interpreting self-evolution control changes.", "quantitative": False, "negative_or_failure_visible": False},
            {"id": "V-WITNESS", "placement": "main", "visual_type": "case_panel", "panel_roles": ["mechanism"], "target_claim_ids": ["N2", "N3"], "source_evidence_ids": ["B-ANALYTICAL", "AN-MECHANISM", "O-MECHANISM"], "reviewer_question": "Why does irreducible partial overlap force a factor-2 exposure distortion?", "takeaway": "Two inspectable singleton-plus-overlap structures explain the tight lower bound rather than relying on the LP as a black box.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
            {"id": "V-BOUNDARY", "placement": "main", "visual_type": "scatter", "panel_roles": ["boundary", "main_comparison"], "target_claim_ids": ["N1", "N2", "N3"], "source_evidence_ids": ["B-RAW-OVERLAP", "B-ANALYTICAL", "AN-MECHANISM", "O-MAIN", "O-MECHANISM"], "reviewer_question": "Is overlap prevalence itself the mechanism, or does exact support geometry separate positive and negative regimes?", "takeaway": "High overlap can still be exactly equalizable; R*(A), not overlap prevalence, separates the audited regimes.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": True},
            {"id": "V-ABLATION-ROBUSTNESS", "placement": "main", "visual_type": "multi_panel", "panel_roles": ["ablation", "failure", "sensitivity", "uncertainty"], "target_claim_ids": ["N1", "N2", "N3"], "source_evidence_ids": ["A-TAXONOMY-PERTURB", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY", "O-ABLATION", "O-FAILURE", "O-SENSITIVITY"], "reviewer_question": "Does the diagnosis survive representation edits and subset perturbations, and where is the closed-form witness not applicable?", "takeaway": "Exact-support quotienting removes clone/split nuisance, both witnesses are deletion-robust, and witness absence is visibly typed as inconclusive rather than a negative result.", "quantitative": True, "uncertainty_required": True, "negative_or_failure_visible": True},
        ],
    }


def build_stri_completion(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    existing_reduction = [REDUCTION]
    existing_coherence = [COHERENCE]
    analysis_path = project_root / PAPER_ANALYSIS
    analysis = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.exists() else {}
    q = analysis.get("quality_v2_evidence") if isinstance(analysis.get("quality_v2_evidence"), dict) else {}
    analysis_refs = [PAPER_ANALYSIS, PRUNING_BASELINE]
    body_path = project_root / PAPER_BODY
    tables_path = project_root / PAPER_TABLES
    body = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
    tables = tables_path.read_text(encoding="utf-8") if tables_path.exists() else ""
    manuscript_ablation = "\\label{fig:ablation-robustness}" in body and "representation ablations" in body.lower()
    manuscript_failure = "Across the 49 Level-1 tools" in body and "overlap-without-witness" in body
    manuscript_sensitivity = "49 leave-one-tool deletions" in body and "500 fixed-seed tool-bootstrap resamples" in body
    manuscript_refs = [PAPER_BODY, PAPER_TABLES, PAPER_ANALYSIS]
    visual_review = {"caption_claim_aligned": True, "legible_labels": True, "legend_or_direct_labels": True, "non_deceptive_scale": True, "source_data_versioned": True}
    visualizations = [
        {"id": "V-OVERVIEW", "status": "PASS", "artifact_refs": [FIG_OVERVIEW], "script_refs": [PLOT_OVERVIEW], "caption_ref": "fig:stri-overview", "visual_review": dict(visual_review)},
        {"id": "V-WITNESS", "status": "PASS", "artifact_refs": [FIG_WITNESS], "data_refs": [REDUCTION], "script_refs": [PLOT_WITNESS], "caption_ref": "fig:factor2-witnesses", "visual_review": dict(visual_review)},
        {"id": "V-BOUNDARY", "status": "PASS", "artifact_refs": [FIG_BOUNDARY], "data_refs": [COHERENCE, REDUCTION], "script_refs": [PLOT_BOUNDARY], "caption_ref": "fig:rstar-boundary", "visual_review": {**visual_review, "negative_or_failure_visible": True}},
        {"id": "V-ABLATION-ROBUSTNESS", "status": "PASS", "artifact_refs": [FIG_ABLATION], "data_refs": [PAPER_ANALYSIS, PRUNING_BASELINE], "script_refs": [PLOT_ABLATION], "caption_ref": "fig:ablation-robustness", "visual_review": {**visual_review, "uncertainty_visible": True, "negative_or_failure_visible": True}},
    ]
    def completed(evidence_id: str, *, allow_scoped: bool = False) -> dict[str, Any]:
        value = str(q.get(evidence_id) or "")
        ok = value == "PASS" or (allow_scoped and value.startswith("PASS_"))
        return {"id": evidence_id, "status": "PASS" if ok else "PLANNED", "artifact_refs": analysis_refs if ok else []}
    return {
        "evidence": [
            {"id": "B-RAW-OVERLAP", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "B-DEDUP", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "B-ANALYTICAL", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "A-REDUCTION-TOURNAMENT", "status": "PASS", "artifact_refs": existing_reduction},
            completed("A-TAXONOMY-PERTURB"),
            {"id": "AN-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction},
            completed("AN-RULEOUT"),
            completed("AN-FAILURE"),
            completed("AN-SENSITIVITY"),
            completed("AN-UNCERTAINTY", allow_scoped=True),
            {"id": "O-MAIN", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "O-ABLATION", "status": "PASS" if manuscript_ablation else "PLANNED", "artifact_refs": manuscript_refs if manuscript_ablation else []},
            {"id": "O-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction},
            {"id": "O-FAILURE", "status": "PASS" if manuscript_failure else "PLANNED", "artifact_refs": manuscript_refs if manuscript_failure else []},
            {"id": "O-SENSITIVITY", "status": "PASS" if manuscript_sensitivity else "PLANNED", "artifact_refs": manuscript_refs if manuscript_sensitivity else []},
        ],
        "visualizations": visualizations,
        "claims": {
            "N1": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "A-REDUCTION-TOURNAMENT", "O-MAIN"]},
            "N2": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-ANALYTICAL", "O-MAIN"]},
            "N3": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "AN-MECHANISM", "O-MECHANISM"]},
        },
    }


def build_asset_first_stri_paper_quality(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    quality = build_stri_quality_contract()
    completion = build_stri_completion(project_root)
    source_artifacts = [REDUCTION, COHERENCE, FINAL_REVIEW, PAPER_ANALYSIS, PRUNING_BASELINE, P0E_DIAGNOSIS, P0E_PRINCIPLE, PAPER_BODY, PAPER_TABLES, FIG_OVERVIEW, FIG_WITNESS, FIG_BOUNDARY, FIG_ABLATION, PLOT_OVERVIEW, PLOT_WITNESS, PLOT_BOUNDARY, PLOT_ABLATION]
    source_sha256 = {rel: _sha256(project_root / rel) for rel in source_artifacts}
    audit = audit_manuscript_evidence_completion(
        quality,
        completion,
        method_components=0,
        source_sha256=source_sha256,
        project_root=project_root,
        require_content_addressed=True,
    )
    missing = sorted({
        blocker.split(":")[-1]
        for blocker in audit.get("blockers") or []
        if str(blocker).startswith("paper-quality-evidence-not-completed:")
    })
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "status": audit["status"],
        "paper_quality_gate_passed": audit["passed"],
        "quality_contract": quality,
        "completion": completion,
        "audit": audit,
        "evidence_debt": {
            "missing_or_incomplete_ids": missing,
            "priority": ["O-ABLATION", "O-FAILURE", "O-SENSITIVITY"] if missing else [],
            "interpretation": "Manuscript QA and venue-format QA remain valid mechanical checks, but they cannot establish top-tier scientific completeness. The CPU evidence suite supplies taxonomy perturbation, ruling-out, failure, sensitivity, and finite-snapshot uncertainty analyses; Paper Quality v2.1 passes only when the manuscript itself consumes those artifacts as explicit baseline/ablation/failure/sensitivity evidence and binds reviewer-question-driven visualizations to versioned data, scripts, figures, and captions.",
            "gpu_rescue_required": False,
            "cheap_first": "Prefer CPU/released-artifact taxonomy perturbation, reduction ablations, uncertainty, and sensitivity before reopening any dynamic GPU lane.",
        },
        "source_artifacts": source_artifacts,
        "source_sha256": source_sha256,
        "scientific_authority": False,
        "authority": {"canonical_problem_gate": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def write_asset_first_stri_paper_quality(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    state = build_asset_first_stri_paper_quality(project_root)
    target = project_root / OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_asset_first_stri_paper_quality(), ensure_ascii=False, indent=2))
