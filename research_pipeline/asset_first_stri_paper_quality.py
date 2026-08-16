from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_quality_gate import audit_manuscript_evidence_completion


OUTPUT = "generated/asset-first-stri-paper-quality-v2-20260816.json"
REDUCTION = "generated/asset-first-skill-taxonomy-representation-invariance-reduction-20260816.json"
COHERENCE = "generated/asset-first-stri-narrow-paper-coherence-20260816.json"
FINAL_REVIEW = "generated/asset-first-stri-narrow-final-review-20260816.json"


def build_stri_quality_contract() -> dict[str, Any]:
    return {
        "schema_version": "2.0",
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
            },
        ],
        "baselines": [
            {"id": "B-RAW-OVERLAP", "role": "simple_control", "evidence_type": "empirical", "target_claim_ids": ["N1", "N3"], "purpose": "Name-level overlap/Jaccard control on the same released inventories.", "matched_dimensions": ["released inventory", "support observations", "system version"]},
            {"id": "B-DEDUP", "role": "same_information_simplification", "evidence_type": "empirical", "target_claim_ids": ["N1", "N3"], "purpose": "Test whether ordinary exact/semantic deduplication absorbs the claimed representation effect.", "matched_dimensions": ["released inventory", "support observations", "system version", "support information"]},
            {"id": "B-ANALYTICAL", "role": "analytical_simplification", "evidence_type": "analytical", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Compare against minimum-package pruning and arbitrary nonnegative package-mass reductions under the identical frozen support matrix.", "matched_dimensions": []},
        ],
        "ablations": [
            {"id": "A-REDUCTION-TOURNAMENT", "ablation_type": "representation", "target_claim_ids": ["N1", "N3"], "purpose": "Remove individual reduction operators (dedup/pruning/reweighting/witness handling) to identify which part changes the conclusion.", "decision_rule": "A component receives explanatory credit only when removing it changes a preregistered support-sensitive conclusion while support information and inventory are fixed."},
            {"id": "A-TAXONOMY-PERTURB", "ablation_type": "assumption_boundary", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Apply support-preserving split/merge/clone/paraphrase perturbations to test representation invariance and its boundary.", "decision_rule": "The certificate claim is narrowed if support-preserving taxonomy edits materially change the certified operational conclusion; raw-overlap instability alone is expected."},
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
    }


def build_stri_completion() -> dict[str, Any]:
    existing_reduction = [REDUCTION]
    existing_coherence = [COHERENCE]
    return {
        "evidence": [
            {"id": "B-RAW-OVERLAP", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "B-DEDUP", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "B-ANALYTICAL", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "A-REDUCTION-TOURNAMENT", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "A-TAXONOMY-PERTURB", "status": "PLANNED", "artifact_refs": []},
            {"id": "AN-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction},
            {"id": "AN-RULEOUT", "status": "PLANNED", "artifact_refs": []},
            {"id": "AN-FAILURE", "status": "PLANNED", "artifact_refs": []},
            {"id": "AN-SENSITIVITY", "status": "PLANNED", "artifact_refs": []},
            {"id": "AN-UNCERTAINTY", "status": "PLANNED", "artifact_refs": []},
            {"id": "O-MAIN", "status": "PASS", "artifact_refs": existing_reduction},
            {"id": "O-ABLATION", "status": "PLANNED", "artifact_refs": []},
            {"id": "O-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction},
            {"id": "O-FAILURE", "status": "PLANNED", "artifact_refs": []},
            {"id": "O-SENSITIVITY", "status": "PLANNED", "artifact_refs": []},
        ],
        "claims": {
            "N1": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "A-REDUCTION-TOURNAMENT", "O-MAIN"]},
            "N2": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-ANALYTICAL", "O-MAIN"]},
            "N3": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "AN-MECHANISM", "O-MECHANISM"]},
        },
    }


def build_asset_first_stri_paper_quality(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    quality = build_stri_quality_contract()
    completion = build_stri_completion()
    audit = audit_manuscript_evidence_completion(quality, completion, method_components=0)
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
            "priority": ["A-TAXONOMY-PERTURB", "AN-RULEOUT", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY", "O-ABLATION", "O-FAILURE", "O-SENSITIVITY"],
            "interpretation": "The prior 59/59 manuscript QA and 50/50 format QA remain valid mechanical checks, but they cannot establish top-tier scientific completeness. STRI is held until claim-matched baseline/ablation/mechanism/failure/sensitivity evidence is completed or the affected claims are narrowed.",
            "gpu_rescue_required": False,
            "cheap_first": "Prefer CPU/released-artifact taxonomy perturbation, reduction ablations, uncertainty, and sensitivity before reopening any dynamic GPU lane.",
        },
        "source_artifacts": [REDUCTION, COHERENCE, FINAL_REVIEW],
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
