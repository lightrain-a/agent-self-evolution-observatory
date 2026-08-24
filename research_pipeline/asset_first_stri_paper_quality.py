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
REVIEWER_EXTENSIONS = "generated/asset-first-stri-reviewer-extensions-20260819.json"
OFFLINE_COMPLETION_ANALYSIS = "generated/asset-first-stri-offline-completion-analysis-20260824.json"
OFFLINE_COMPLETION_ANALYSIS_CODE = "research_pipeline/asset_first_stri_offline_completion_analysis_20260824.py"
OFFLINE_COMPLETION_ANALYSIS_TEST = "research_pipeline/test_asset_first_stri_offline_completion_analysis_20260824.py"
TARGET_NULL_ANALYSIS = "generated/asset-first-stri-target-null-analysis-20260824.json"
TARGET_NULL_ANALYSIS_CODE = "research_pipeline/asset_first_stri_target_null_analysis_20260824.py"
WITNESS_PEELING = "generated/asset-first-stri-witness-peeling-20260824.json"
WITNESS_PEELING_CODE = "research_pipeline/asset_first_stri_witness_peeling_20260824.py"
SUPPORT_EDIT_RADIUS = "generated/asset-first-stri-support-edit-radius-20260824.json"
SUPPORT_EDIT_RADIUS_CODE = "research_pipeline/asset_first_stri_support_edit_radius_20260824.py"
STRUCTURAL_ENRICHMENT_TEST = "research_pipeline/test_asset_first_stri_target_null_analysis_20260824.py"
PRACTICAL_BASELINES = "generated/asset-first-stri-practical-baselines-20260824.json"
PRACTICAL_BASELINES_CSV = "generated/asset-first-stri-practical-baselines-20260824.csv"
PRACTICAL_BASELINES_CODE = "research_pipeline/asset_first_stri_practical_baselines_20260824.py"
PRACTICAL_BASELINES_TEST = "research_pipeline/test_asset_first_stri_practical_baselines_20260824.py"
SKILLRL_BUDGET_BASELINES = "generated/asset-first-stri-skillrl-budget-baselines-20260824.json"
SKILLRL_BUDGET_BASELINES_CSV = "generated/asset-first-stri-skillrl-budget-baselines-20260824.csv"
SKILLRL_BUDGET_BASELINES_CODE = "research_pipeline/asset_first_stri_skillrl_budget_baselines_20260824.py"
SKILLRL_BUDGET_BASELINES_TEST = "research_pipeline/test_asset_first_stri_skillrl_budget_baselines_20260824.py"
SKILLROUTER_RELEVANCE = "generated/asset-first-stri-skillrouter-relevance-analogue-20260824.json"
SKILLROUTER_RELEVANCE_CSV = "generated/asset-first-stri-skillrouter-relevance-analogue-20260824.csv"
SKILLROUTER_RELEVANCE_CODE = "research_pipeline/asset_first_stri_skillrouter_relevance_analogue_20260824.py"
SKILLROUTER_RELEVANCE_TEST = "research_pipeline/test_asset_first_stri_skillrouter_relevance_analogue_20260824.py"
SKILLSBENCH_SUPPORT_QUAL = "generated/asset-first-stri-skillsbench-support-qualification-20260824.json"
SKILLSBENCH_SUPPORT_QUAL_CSV = "generated/asset-first-stri-skillsbench-support-qualification-20260824.csv"
SKILLSBENCH_SUPPORT_QUAL_CODE = "research_pipeline/asset_first_stri_skillsbench_support_qualification_20260824.py"
SKILLSBENCH_SUPPORT_QUAL_TEST = "research_pipeline/test_asset_first_stri_skillsbench_support_qualification_20260824.py"
CONTROLLER_AUDIT = "generated/asset-first-stri-released-controller-clone-audit-20260819.json"
CONTROLLER_AUDIT_CODE = "research_pipeline/asset_first_stri_released_controller_clone_audit.py"
CONTROLLER_AUDIT_TEST = "research_pipeline/test_asset_first_stri_released_controller_clone_audit.py"
DYNAMIC_QUALIFICATION = "generated/asset-first-stri-autoskill-p19-substrate-qualification-20260819.json"
DYNAMIC_CONTRACT = "generated/asset-first-stri-autoskill-p19-dynamic-f0-contract-v2-20260819.json"
DYNAMIC_PLAN = "generated/asset-first-stri-autoskill-p19-stage3-plan-20260819.json"
DYNAMIC_RESULT = "generated/asset-first-stri-autoskill-p19-stage3-result-20260819.json"
DYNAMIC_RUN_MANIFEST = "generated/asset-first-stri-autoskill-p19-stage3-run-manifest-20260819.json"
MEDIATOR_V1_CONTRACT = "generated/asset-first-stri-autoskill-p19-mediator-isolation-contract-20260819.json"
MEDIATOR_V1_DIAGNOSIS = "generated/asset-first-stri-autoskill-p19-mediator-isolation-v1-diagnosis-20260819.json"
MEDIATOR_V2_CONTRACT = "generated/asset-first-stri-autoskill-p19-mediator-isolation-v2-contract-20260819.json"
MEDIATOR_V2_RESULT = "generated/asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json"
CERTIFICATE_CODE = "research_pipeline/asset_first_stri_certificate.py"
CERTIFICATE_TEST = "research_pipeline/test_asset_first_stri_certificate.py"
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
                "statement": "Released skill controllers can assign different semantic control solely because equivalent implementation content is represented by different package identities; in one bounded frozen AutoSkill substrate, that representation change propagates to executed behavior.",
                "why_better_or_why_matters": "Skill-SP shows the released controller-input distribution shift and exact quotient restoration; AutoSkill P19 independently shows a frozen identity split changing the semantic retrieval set and a mechanical downstream behavior across 18 fresh runs, with ID-placebo and quotient controls restoring the original pattern and a matched mediator add-back isolating the crowded-out post-checkout skill.",
                "alternative_explanations": ["the apparent change is only a name-level statistic and does not reach the released controller input distribution", "literal exact clones are accepted by the author induction path", "the dynamic difference is only an ID-token perturbation or executor randomness", "the pattern is driven by one support threshold"],
                "ruling_out_experiments": ["rerun the author's released sampling-weight function on a same-state sampler-input clone and compare actual questioner prompt-mixture mass", "verify the author induction duplicate filter rejects the literal exact text clone", "compare released identity normalization against quotient-conserved class mass on the same frozen support and prompt strings", "freeze AutoSkill P19 and compare original, split4, ID-placebo, and semantic-quotient arms under the same prompt/executor with zero judge calls", "under the split representation, compare post-checkout mediator add-back against a matched cleanup add-back with the same five-slot/three-semantic-class structure"],
                "baseline_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL"],
                "ablation_ids": ["A-REDUCTION-TOURNAMENT", "A-TAXONOMY-PERTURB"],
                "analysis_ids": ["AN-RULEOUT", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY", "AN-DYNAMIC-CONSEQUENCE"],
                "output_ids": ["O-MAIN", "O-ABLATION", "O-FAILURE", "O-SENSITIVITY", "O-DYNAMIC"],
                "visualization_ids": ["V-OVERVIEW", "V-BOUNDARY", "V-ABLATION-ROBUSTNESS"],
            },
            {
                "id": "N2",
                "claim_type": "theory",
                "statement": "Exact-refinement STRI is equivalent to quotient factorization of semantic-class mass; R*(A;q) exactly decides target realizability by package-first mass, while a semantic-first row-stochastic implementation factorization realizes any covered target after changing the action basis.",
                "why_better_or_why_matters": "The quotient characterization exposes a general failure class for positive identity-local normalization, the primal/dual certificate identifies when package-first retuning is insufficient, and the semantic-first construction supplies the corresponding design boundary without claiming downstream validation or a new optimization algorithm.",
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
                "statement": "STRI has two separable boundaries: identity-local normalization violates exact-refinement invariance, while after quotienting the neutral residual is not determined by overlap count alone and is exactly characterized by target realizability in the package support cone.",
                "why_better_or_why_matters": "This separation yields an exact allocation-level repair for known pure multiplicity nuisance, a fail-closed impossibility certificate for package-first retuning, and a semantic-first constructive escape when the action interface can select semantic intent before implementation.",
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
            {"id": "AN-MECHANISM", "analysis_type": "mechanism", "target_claim_ids": ["N3"], "purpose": "Separate clone-multiplicity nuisance from support-cone target-realizability boundaries and enumerate where overlap count gives the wrong qualitative conclusion.", "decision_rule": "No causal claim from aggregate overlap trends; positive and negative boundary cases must be explicitly enumerated."},
            {"id": "AN-RULEOUT", "analysis_type": "alternative_explanation", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Rule out simple deduplication, arbitrary weighting, and one-system idiosyncrasy as sufficient explanations.", "decision_rule": "If a simpler matched-information reduction reproduces all certified conclusions, STRI must merge into that baseline."},
            {"id": "AN-FAILURE", "analysis_type": "failure", "target_claim_ids": ["N1", "N3"], "purpose": "Catalogue invariant, clone-sensitive, underidentified, and unsupported regimes instead of presenting only positive examples.", "decision_rule": "Every released-system case is assigned a preregistered regime; inconclusive cells remain visible."},
            {"id": "AN-SENSITIVITY", "analysis_type": "sensitivity", "target_claim_ids": ["N1", "N2", "N3"], "purpose": "Stress practical package-weight baselines, calibration-to-heldout transfer, retrieval-budget controls, an external expert relevance analogue, support misspecification, exact edit radius, rewiring, target rays, package-mass constraints, and sparse witnesses.", "decision_rule": "Require the Level-1 residual to survive strongest same-information package weighting and no-refit heldout transfer; require SkillRL identity effects to vanish under placebo/quotient or sufficient capacity; keep external relevance labels explicitly separate from executable support."},
            {"id": "AN-UNCERTAINTY", "analysis_type": "uncertainty", "target_claim_ids": ["N1", "N3"], "purpose": "Attach sampling/bootstrap or exact finite-population uncertainty to released-system comparative summaries where stochastic sampling is present.", "decision_rule": "Do not present point-estimate gaps as robust evidence when their uncertainty overlaps the matched baseline."},
            {"id": "AN-DYNAMIC-CONSEQUENCE", "analysis_type": "mechanism", "target_claim_ids": ["N1"], "purpose": "Test whether a semantics-preserving identity split propagates through a released retrieval budget into fresh executed behavior and whether the crowded-out post-checkout skill specifically mediates that behavior under a frozen task and executor.", "decision_rule": "Support only if Stage-3 gives original>=5/6, split<=1/6, ID-placebo=3/3, quotient-control=3/3 with all runs valid and Fisher<=0.05, and fresh mediator isolation gives post-checkout add-back=3/3 versus matched cleanup add-back=0/3 with exact one-sided Fisher<=0.05; otherwise retain only the strongest passed substrate-local subclaim."},
        ],
        "planned_outputs": [
            {"id": "O-MAIN", "output_type": "main_comparison", "purpose": "One explicit baseline table: raw overlap vs dedup vs package pruning/reweighting vs STRI-Cert on identical released inventories."},
            {"id": "O-ABLATION", "output_type": "ablation", "purpose": "One explicit ablation/perturbation table rather than calling the reduction tournament an implicit control."},
            {"id": "O-MECHANISM", "output_type": "mechanism", "purpose": "Why/where STRI differs: disagreement examples plus taxonomy-perturbation mechanism plot."},
            {"id": "O-FAILURE", "output_type": "failure", "purpose": "Failure/boundary table including underidentified and inconclusive regimes."},
            {"id": "O-SENSITIVITY", "output_type": "sensitivity", "purpose": "Sensitivity panel for thresholds, package constraints, singleton witnesses, and split/merge/clone edits."},
            {"id": "O-DYNAMIC", "output_type": "mechanism_result", "purpose": "Compact AutoSkill P19 result establishing the bounded representation-to-retrieval-to-mediator-to-behavior chain with ID-placebo, quotient, and matched mediator controls."},
        ],
        "visualizations": [
            {"id": "V-OVERVIEW", "placement": "main", "visual_type": "flow", "panel_roles": ["overview", "traceability"], "target_claim_ids": ["N1", "N3"], "source_evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "O-MAIN"], "reviewer_question": "What representation nuisance is STRI auditing, and how does package identity alter a semantic control surface?", "takeaway": "Separate semantic capability/support from package identity before interpreting self-evolution control changes.", "quantitative": False, "negative_or_failure_visible": False},
            {"id": "V-WITNESS", "placement": "main", "visual_type": "case_panel", "panel_roles": ["mechanism"], "target_claim_ids": ["N2", "N3"], "source_evidence_ids": ["B-ANALYTICAL", "AN-MECHANISM", "O-MECHANISM"], "reviewer_question": "Why does irreducible partial overlap force a factor-2 exposure distortion?", "takeaway": "Two inspectable singleton-plus-overlap structures explain the tight lower bound rather than relying on the LP as a black box.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
            {"id": "V-BOUNDARY", "placement": "main", "visual_type": "scatter", "panel_roles": ["boundary", "main_comparison"], "target_claim_ids": ["N1", "N2", "N3"], "source_evidence_ids": ["B-RAW-OVERLAP", "B-ANALYTICAL", "AN-MECHANISM", "O-MAIN", "O-MECHANISM"], "reviewer_question": "Can overlap prevalence alone determine whether the neutral target is package-first realizable?", "takeaway": "No: a 99.2% overlap regime is exactly realizable, while lower-overlap Level-1 regimes have R*(A)=2; support geometry is needed to decide the audited cases.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": True},
            {"id": "V-ABLATION-ROBUSTNESS", "placement": "main", "visual_type": "multi_panel", "panel_roles": ["ablation", "failure", "sensitivity", "uncertainty"], "target_claim_ids": ["N1", "N2", "N3"], "source_evidence_ids": ["A-TAXONOMY-PERTURB", "AN-FAILURE", "AN-SENSITIVITY", "AN-UNCERTAINTY", "O-ABLATION", "O-FAILURE", "O-SENSITIVITY"], "reviewer_question": "Is the residual a fragile artifact of one clone example, one sparse witness, uniform q, concentrated package weights, or a few support cells?", "takeaway": "The same frozen support object has a 22-addition/71-deletion exact edit radius, survives 200 degree-preserving rewirings and 22 disjoint sparse witnesses, and remains residual over seven representation-independent target rays and every feasible tested max-share constraint.", "quantitative": True, "uncertainty_required": True, "negative_or_failure_visible": True},
        ],
    }


def build_stri_completion(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    existing_reduction = [REDUCTION]
    existing_coherence = [COHERENCE]
    analysis_path = project_root / PAPER_ANALYSIS
    analysis = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.exists() else {}
    q = analysis.get("quality_v2_evidence") if isinstance(analysis.get("quality_v2_evidence"), dict) else {}
    controller_refs = [CONTROLLER_AUDIT, CONTROLLER_AUDIT_CODE, CONTROLLER_AUDIT_TEST]
    dynamic_refs = [DYNAMIC_QUALIFICATION, DYNAMIC_CONTRACT, DYNAMIC_PLAN, DYNAMIC_RESULT, DYNAMIC_RUN_MANIFEST, MEDIATOR_V1_CONTRACT, MEDIATOR_V1_DIAGNOSIS, MEDIATOR_V2_CONTRACT, MEDIATOR_V2_RESULT]
    certificate_refs = [CERTIFICATE_CODE, CERTIFICATE_TEST]
    offline_refs = [OFFLINE_COMPLETION_ANALYSIS, OFFLINE_COMPLETION_ANALYSIS_CODE, OFFLINE_COMPLETION_ANALYSIS_TEST]
    structural_refs = [TARGET_NULL_ANALYSIS, TARGET_NULL_ANALYSIS_CODE, WITNESS_PEELING, WITNESS_PEELING_CODE, SUPPORT_EDIT_RADIUS, SUPPORT_EDIT_RADIUS_CODE, STRUCTURAL_ENRICHMENT_TEST]
    breadth_refs = [PRACTICAL_BASELINES, PRACTICAL_BASELINES_CSV, PRACTICAL_BASELINES_CODE, PRACTICAL_BASELINES_TEST, SKILLRL_BUDGET_BASELINES, SKILLRL_BUDGET_BASELINES_CSV, SKILLRL_BUDGET_BASELINES_CODE, SKILLRL_BUDGET_BASELINES_TEST, SKILLROUTER_RELEVANCE, SKILLROUTER_RELEVANCE_CSV, SKILLROUTER_RELEVANCE_CODE, SKILLROUTER_RELEVANCE_TEST, SKILLSBENCH_SUPPORT_QUAL, SKILLSBENCH_SUPPORT_QUAL_CSV, SKILLSBENCH_SUPPORT_QUAL_CODE, SKILLSBENCH_SUPPORT_QUAL_TEST]
    analysis_refs = [PAPER_ANALYSIS, REVIEWER_EXTENSIONS, PRUNING_BASELINE, *offline_refs, *structural_refs, *breadth_refs, *controller_refs, *dynamic_refs, *certificate_refs]
    offline_path = project_root / OFFLINE_COMPLETION_ANALYSIS
    offline = json.loads(offline_path.read_text(encoding="utf-8")) if offline_path.exists() else {}
    support_stress = offline.get("support_misspecification_sensitivity") if isinstance(offline.get("support_misspecification_sensitivity"), dict) else {}
    scale = offline.get("rstar_solver_scalability") if isinstance(offline.get("rstar_solver_scalability"), dict) else {}
    support_aggregate = support_stress.get("aggregate") if isinstance(support_stress.get("aggregate"), dict) else {}
    scale_summary = scale.get("summary") if isinstance(scale.get("summary"), list) else []
    offline_completion_pass = (
        offline.get("scientific_authority") is False
        and ((offline.get("scientific_boundary") or {}).get("claim_expansion") is False)
        and ((offline.get("scientific_boundary") or {}).get("model_calls") == 0)
        and ((offline.get("scientific_boundary") or {}).get("gpu_runs") == 0)
        and ((support_stress.get("base") or {}).get("decision") == "RESIDUAL")
        and ((support_stress.get("base") or {}).get("R_star") == 2.0)
        and int(support_aggregate.get("minimum_changed_cells_for_valid_class_flip") or 0) == 22
        and any(int(row.get("rows") or 0) == 16384 and int(row.get("packages") or 0) == 96 for row in scale_summary if isinstance(row, dict))
    )
    target_null_path = project_root / TARGET_NULL_ANALYSIS
    target_null = json.loads(target_null_path.read_text(encoding="utf-8")) if target_null_path.exists() else {}
    target_summary = ((target_null.get("target_ray_sensitivity") or {}).get("summary") or {})
    share_summary = ((target_null.get("max_share_sensitivity") or {}).get("summary") or {})
    null_summary = ((target_null.get("degree_preserving_null_ensemble") or {}).get("summary") or {})
    witness_path = project_root / WITNESS_PEELING
    witness = json.loads(witness_path.read_text(encoding="utf-8")) if witness_path.exists() else {}
    witness_summary = ((witness.get("witness_peeling") or {}).get("summary") or {})
    edit_path = project_root / SUPPORT_EDIT_RADIUS
    edit = json.loads(edit_path.read_text(encoding="utf-8")) if edit_path.exists() else {}
    edit_radius = edit.get("support_edit_radius") if isinstance(edit.get("support_edit_radius"), dict) else {}
    structural_enrichment_pass = (
        ((target_null.get("scientific_boundary") or {}).get("claim_expansion") is False)
        and ((target_null.get("scientific_boundary") or {}).get("model_calls") == 0)
        and ((target_null.get("scientific_boundary") or {}).get("gpu_runs") == 0)
        and int(target_summary.get("targets") or 0) == 7
        and target_summary.get("all_tested_targets_residual") is True
        and abs(float(target_summary.get("neutral_R_star") or -99.0) - 2.0) <= 1e-12
        and int(share_summary.get("valid_constraints") or 0) == 9
        and share_summary.get("all_valid_constraints_residual") is True
        and int(null_summary.get("residual_draws", 0)) == 200
        and int(null_summary.get("equalizable_draws", -1)) == 0
        and abs(float(null_summary.get("minimum_R_star") or -99.0) - 2.0) <= 1e-12
        and abs(float(null_summary.get("maximum_R_star") or -99.0) - 2.0) <= 1e-12
        and ((witness.get("scientific_boundary") or {}).get("model_calls") == 0)
        and ((witness.get("scientific_boundary") or {}).get("gpu_runs") == 0)
        and int(witness_summary.get("peeling_rounds_before_equalizable") or 0) == 22
        and int(witness_summary.get("pairwise_disjoint_witness_rows_removed") or 0) == 66
        and int(witness_summary.get("unique_tools_spanned") or 0) == 19
        and abs(float(witness_summary.get("final_R_star") or -99.0) - 1.0) <= 1e-12
        and ((edit.get("scientific_boundary") or {}).get("model_calls") == 0)
        and ((edit.get("scientific_boundary") or {}).get("gpu_runs") == 0)
        and int(edit_radius.get("minimum_additions_to_equalizable") or 0) == 22
        and int(edit_radius.get("minimum_deletions_to_equalizable") or 0) == 71
        and abs(float((edit_radius.get("addition_solution") or {}).get("mip_gap", -1.0))) <= 1e-12
        and abs(float((edit_radius.get("deletion_solution") or {}).get("mip_gap", -1.0))) <= 1e-12
        and abs(float((edit_radius.get("addition_solution") or {}).get("verified_R_star") or -99.0) - 1.0) <= 1e-12
        and abs(float((edit_radius.get("deletion_solution") or {}).get("verified_R_star") or -99.0) - 1.0) <= 1e-12
    )
    practical_path = project_root / PRACTICAL_BASELINES
    practical = json.loads(practical_path.read_text(encoding="utf-8")) if practical_path.exists() else {}
    practical_head = practical.get("headline") if isinstance(practical.get("headline"), dict) else {}
    transfer = practical.get("calibration_to_heldout") if isinstance(practical.get("calibration_to_heldout"), dict) else {}
    transfer_rows = {str(row.get("baseline")): row for row in (transfer.get("results") or []) if isinstance(row, dict)}
    skillrl_budget_path = project_root / SKILLRL_BUDGET_BASELINES
    skillrl_budget = json.loads(skillrl_budget_path.read_text(encoding="utf-8")) if skillrl_budget_path.exists() else {}
    skillrl_head = skillrl_budget.get("headline") if isinstance(skillrl_budget.get("headline"), dict) else {}
    router_path = project_root / SKILLROUTER_RELEVANCE
    router = json.loads(router_path.read_text(encoding="utf-8")) if router_path.exists() else {}
    router_head = router.get("headline") if isinstance(router.get("headline"), dict) else {}
    skillsbench_path = project_root / SKILLSBENCH_SUPPORT_QUAL
    skillsbench = json.loads(skillsbench_path.read_text(encoding="utf-8")) if skillsbench_path.exists() else {}
    skillsbench_summary = skillsbench.get("summary") if isinstance(skillsbench.get("summary"), dict) else {}
    experimental_breadth_pass = (
        practical.get("new_model_calls") == 0 and practical.get("new_gpu_runs") == 0 and practical.get("claim_expansion") is False
        and abs(float(practical_head.get("level1_exact_R_star") or -99.0) - 2.0) <= 1e-12
        and abs(float(practical_head.get("level1_uniform_ratio") or -99.0) - 2.0) <= 1e-12
        and float(practical_head.get("level1_inverse_support_ratio") or 0.0) > 90.0
        and float(practical_head.get("level1_nnls_ratio") or 0.0) > 5.0
        and float(practical_head.get("level1_nnls_cv") or 99.0) < float(practical_head.get("level1_uniform_cv") or -99.0)
        and transfer.get("no_heldout_refit") is True
        and abs(float(((transfer_rows.get("exact_rstar") or {}).get("heldout_metrics") or {}).get("distortion_ratio") or -99.0) - 2.0) <= 1e-12
        and skillrl_budget.get("new_model_calls") == 0 and skillrl_budget.get("new_gpu_runs") == 0 and skillrl_budget.get("claim_expansion") is False
        and int(skillrl_head.get("top_k_6_official_targets_changed") or 0) == 11
        and int(skillrl_head.get("top_k_6_official_targets_reduced") or 0) == 5
        and int(skillrl_head.get("top_k_6_non_dynamic_placebo_semantic_changes", -1)) == 0
        and int(skillrl_head.get("top_k_6_quotient_semantic_changes", -1)) == 0
        and int(skillrl_head.get("top_k_13_official_semantic_changes", -1)) == 0
        and router.get("new_model_calls") == 0 and router.get("new_gpu_runs") == 0 and router.get("claim_expansion") is False
        and int(router_head.get("core_rows") or 0) == 75
        and (int(router_head.get("core_single") or 0), int(router_head.get("core_multi") or 0)) == (24, 51)
        and abs(float(router_head.get("core_uniform_ratio") or -99.0) - 7.0) <= 1e-12
        and abs(float(router_head.get("core_R_star") or -99.0) - 1.0) <= 1e-12
        and abs(float(router_head.get("graded_ge_1_uniform_ratio") or -99.0) - 21.0) <= 1e-12
        and abs(float(router_head.get("graded_ge_1_R_star") or -99.0) - 1.0) <= 1e-12
        and "retrieval acceptability" in str(router.get("scientific_boundary") or "")
        and skillsbench.get("decision") == "STOP_AS_EXACT_SUPPORT_SUBSTRATE"
        and int(skillsbench_summary.get("tasks") or 0) == 87
        and int(skillsbench_summary.get("required_skills_empty_tasks") or 0) == 75
        and int(skillsbench_summary.get("required_vs_task_local_mismatch_tasks") or 0) == 79
        and int(skillsbench_summary.get("task_local_skill_files") or 0) == 232
        and skillsbench.get("new_model_calls") == 0 and skillsbench.get("new_gpu_runs") == 0 and skillsbench.get("claim_expansion") is False
    )
    dynamic_path = project_root / DYNAMIC_RESULT
    dynamic = json.loads(dynamic_path.read_text(encoding="utf-8")) if dynamic_path.exists() else {}
    mediator_path = project_root / MEDIATOR_V2_RESULT
    mediator = json.loads(mediator_path.read_text(encoding="utf-8")) if mediator_path.exists() else {}
    groups = dynamic.get("groups") if isinstance(dynamic.get("groups"), dict) else {}
    gates = dynamic.get("frozen_gates") if isinstance(dynamic.get("frozen_gates"), dict) else {}
    mediator_groups = mediator.get("groups") if isinstance(mediator.get("groups"), dict) else {}
    mediator_stats = mediator.get("statistics") if isinstance(mediator.get("statistics"), dict) else {}
    dynamic_pass = (
        dynamic.get("decision") == "GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION"
        and all(bool(gates.get(k)) for k in ("A_ge_5_of_6", "B_le_1_of_6", "C_eq_3_of_3", "D_eq_3_of_3", "zero_invalid_runs", "fisher_p_le_0_05"))
        and (groups.get("A_original") or {}).get("destructive_signature_positive") == 6
        and (groups.get("B_split4") or {}).get("destructive_signature_positive") == 0
        and (groups.get("C_id_placebo") or {}).get("destructive_signature_positive") == 3
        and (groups.get("D_quotient_control") or {}).get("destructive_signature_positive") == 3
        and mediator.get("decision") == "GO_MEDIATOR_ISOLATION_P19"
        and mediator.get("all_executions_valid") is True
        and (mediator_groups.get("E_post_addback") or {}).get("positive") == 3
        and (mediator_groups.get("F_cleanup_control") or {}).get("positive") == 0
        and mediator_stats.get("gate_pass_exact") is True
    )
    body_path = project_root / PAPER_BODY
    tables_path = project_root / PAPER_TABLES
    body = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
    tables = tables_path.read_text(encoding="utf-8") if tables_path.exists() else ""
    manuscript_ablation = "\\label{fig:ablation-robustness}" in body and "representation ablations" in body.lower()
    manuscript_failure = all(marker in body for marker in ("Across 49 tools", "overlap-without-witness", "equalizable", "Package-wide support overstatement"))
    manuscript_sensitivity = all(marker in body for marker in ("1,387", "366 valid deletions", "127/595", "184 tool-block", "49/56", "Exact neutral-target MILPs require at least 22 added cells", "71 deletions", "200 degree-preserving bipartite rewirings", "7/7 frozen target rays", "max-share", "22 pairwise-disjoint three-row witnesses", "19 tools"))
    manuscript_breadth = all(marker in (body + tables) for marker in ("98.33", "NNLS", "Heldout", "without refitting", "SkillRouter", "75 scored queries", "11/12 targets", "k=13", "non-dynamic-ID duplicate", "retrieval-relevance analogue", "79/87 rows disagree"))
    manuscript_dynamic = all(marker in body for marker in ("AutoSkill: dynamic behavioral propagation", "6/6 original", "0/6 split", "3/3 placebo", "3/3 quotient", "0.00108", "matched cleanup add-back", "1/20"))
    manuscript_scale = all(marker in body for marker in ("E6: conditional solver cost", "16{,}384\\times96", "0.765", "32,768 inequalities", "24.25 MiB", "host-load-dependent"))
    manuscript_refs = [PAPER_BODY, PAPER_TABLES, PAPER_ANALYSIS, REVIEWER_EXTENSIONS, *offline_refs, *structural_refs, *breadth_refs]
    visual_review = {"caption_claim_aligned": True, "legible_labels": True, "legend_or_direct_labels": True, "non_deceptive_scale": True, "source_data_versioned": True}
    visualizations = [
        {"id": "V-OVERVIEW", "status": "PASS", "artifact_refs": [FIG_OVERVIEW], "script_refs": [PLOT_OVERVIEW], "caption_ref": "fig:stri-overview", "visual_review": dict(visual_review)},
        {"id": "V-WITNESS", "status": "PASS", "artifact_refs": [FIG_WITNESS], "data_refs": [REDUCTION], "script_refs": [PLOT_WITNESS], "caption_ref": "fig:factor2-witnesses", "visual_review": dict(visual_review)},
        {"id": "V-BOUNDARY", "status": "PASS", "artifact_refs": [FIG_BOUNDARY], "data_refs": [COHERENCE, REDUCTION, SKILLRL_BUDGET_BASELINES, SKILLROUTER_RELEVANCE], "script_refs": [PLOT_BOUNDARY], "caption_ref": "fig:rstar-boundary", "visual_review": {**visual_review, "negative_or_failure_visible": True, "budget_boundary_visible": True, "external_analogue_visible": True}},
        {"id": "V-ABLATION-ROBUSTNESS", "status": "PASS", "artifact_refs": [FIG_ABLATION], "data_refs": [PAPER_ANALYSIS, TARGET_NULL_ANALYSIS, WITNESS_PEELING, SUPPORT_EDIT_RADIUS], "script_refs": [PLOT_ABLATION], "caption_ref": "fig:ablation-robustness", "visual_review": {**visual_review, "uncertainty_visible": True, "negative_or_failure_visible": True}},
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
            {"id": "AN-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction + controller_refs},
            completed("AN-RULEOUT"),
            completed("AN-FAILURE"),
            {"id": "AN-SENSITIVITY", "status": "PASS" if completed("AN-SENSITIVITY")["status"] == "PASS" and offline_completion_pass and structural_enrichment_pass and experimental_breadth_pass and manuscript_sensitivity and manuscript_breadth else "PLANNED", "artifact_refs": analysis_refs if completed("AN-SENSITIVITY")["status"] == "PASS" and offline_completion_pass and structural_enrichment_pass and experimental_breadth_pass and manuscript_sensitivity and manuscript_breadth else []},
            completed("AN-UNCERTAINTY", allow_scoped=True),
            {"id": "AN-DYNAMIC-CONSEQUENCE", "status": "PASS" if dynamic_pass else "PLANNED", "artifact_refs": dynamic_refs if dynamic_pass else []},
            {"id": "O-MAIN", "status": "PASS", "artifact_refs": existing_reduction + controller_refs},
            {"id": "O-ABLATION", "status": "PASS" if manuscript_ablation else "PLANNED", "artifact_refs": manuscript_refs if manuscript_ablation else []},
            {"id": "O-MECHANISM", "status": "PASS", "artifact_refs": existing_coherence + existing_reduction + controller_refs},
            {"id": "O-FAILURE", "status": "PASS" if manuscript_failure else "PLANNED", "artifact_refs": manuscript_refs if manuscript_failure else []},
            {"id": "O-SENSITIVITY", "status": "PASS" if manuscript_sensitivity and manuscript_breadth and offline_completion_pass and structural_enrichment_pass and experimental_breadth_pass and manuscript_scale else "PLANNED", "artifact_refs": manuscript_refs if manuscript_sensitivity and manuscript_breadth and offline_completion_pass and structural_enrichment_pass and experimental_breadth_pass and manuscript_scale else []},
            {"id": "O-DYNAMIC", "status": "PASS" if dynamic_pass and manuscript_dynamic else "PLANNED", "artifact_refs": [PAPER_BODY, *dynamic_refs] if dynamic_pass and manuscript_dynamic else []},
        ],
        "visualizations": visualizations,
        "claims": {
            "N1": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "A-REDUCTION-TOURNAMENT", "AN-DYNAMIC-CONSEQUENCE", "O-MAIN", "O-DYNAMIC"]},
            "N2": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-ANALYTICAL", "O-MAIN"]},
            "N3": {"status": "SUPPORTED_NARROWLY", "evidence_ids": ["B-RAW-OVERLAP", "B-DEDUP", "B-ANALYTICAL", "AN-MECHANISM", "O-MECHANISM"]},
        },
    }


def build_asset_first_stri_paper_quality(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    quality = build_stri_quality_contract()
    completion = build_stri_completion(project_root)
    source_artifacts = [REDUCTION, COHERENCE, FINAL_REVIEW, PAPER_ANALYSIS, REVIEWER_EXTENSIONS, OFFLINE_COMPLETION_ANALYSIS, OFFLINE_COMPLETION_ANALYSIS_CODE, OFFLINE_COMPLETION_ANALYSIS_TEST, TARGET_NULL_ANALYSIS, TARGET_NULL_ANALYSIS_CODE, WITNESS_PEELING, WITNESS_PEELING_CODE, SUPPORT_EDIT_RADIUS, SUPPORT_EDIT_RADIUS_CODE, STRUCTURAL_ENRICHMENT_TEST, PRACTICAL_BASELINES, PRACTICAL_BASELINES_CSV, PRACTICAL_BASELINES_CODE, PRACTICAL_BASELINES_TEST, SKILLRL_BUDGET_BASELINES, SKILLRL_BUDGET_BASELINES_CSV, SKILLRL_BUDGET_BASELINES_CODE, SKILLRL_BUDGET_BASELINES_TEST, SKILLROUTER_RELEVANCE, SKILLROUTER_RELEVANCE_CSV, SKILLROUTER_RELEVANCE_CODE, SKILLROUTER_RELEVANCE_TEST, SKILLSBENCH_SUPPORT_QUAL, SKILLSBENCH_SUPPORT_QUAL_CSV, SKILLSBENCH_SUPPORT_QUAL_CODE, SKILLSBENCH_SUPPORT_QUAL_TEST, CONTROLLER_AUDIT, CONTROLLER_AUDIT_CODE, CONTROLLER_AUDIT_TEST, DYNAMIC_QUALIFICATION, DYNAMIC_CONTRACT, DYNAMIC_PLAN, DYNAMIC_RESULT, DYNAMIC_RUN_MANIFEST, MEDIATOR_V1_CONTRACT, MEDIATOR_V1_DIAGNOSIS, MEDIATOR_V2_CONTRACT, MEDIATOR_V2_RESULT, CERTIFICATE_CODE, CERTIFICATE_TEST, PRUNING_BASELINE, P0E_DIAGNOSIS, P0E_PRINCIPLE, PAPER_BODY, PAPER_TABLES, FIG_OVERVIEW, FIG_WITNESS, FIG_BOUNDARY, FIG_ABLATION, PLOT_OVERVIEW, PLOT_WITNESS, PLOT_BOUNDARY, PLOT_ABLATION]
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
            "interpretation": "Manuscript QA and venue-format QA remain valid mechanical checks, but they cannot establish top-tier scientific completeness. The frozen-data evidence suite now includes exact support-edit radii, degree-preserving structural controls, target-ray and package-mass sensitivity, sparse-witness redundancy, taxonomy perturbation, ruling-out, failure, and finite-snapshot uncertainty analyses; Paper Quality v2.1 passes only when the manuscript itself consumes those artifacts and binds reviewer-question-driven visualizations to versioned data, scripts, figures, and captions.",
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
