from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "2.1"

PAPER_ARCHETYPES = {"method", "system", "empirical_analysis", "theory_certificate"}
CLAIM_TYPES = {"performance", "mechanism", "system", "robustness", "cost", "empirical_analysis", "theory", "negative"}
BASELINE_ROLES = {
    "current_system",
    "direct_competitor",
    "same_information_simplification",
    "simple_control",
    "oracle_upper_bound",
    "analytical_simplification",
    "null_control",
}
ABLATION_TYPES = {
    "component",
    "mechanism",
    "information_budget",
    "representation",
    "assumption_boundary",
    "positive_control",
    "negative_control",
}
ANALYSIS_TYPES = {
    "mechanism",
    "failure",
    "sensitivity",
    "robustness",
    "efficiency",
    "alternative_explanation",
    "stratified",
    "uncertainty",
    "scaling",
    "human_evaluation",
}
VISUAL_TYPES = {
    "multi_panel",
    "bar",
    "line",
    "scatter",
    "heatmap",
    "matrix",
    "distribution",
    "flow",
    "case_panel",
    "table_figure",
}
VISUAL_ROLES = {
    "overview",
    "main_comparison",
    "ablation",
    "mechanism",
    "boundary",
    "failure",
    "sensitivity",
    "uncertainty",
    "scaling",
    "cost",
    "human_evaluation",
    "qualitative_case",
    "traceability",
}
VISUAL_PLACEMENTS = {"main", "appendix", "supplement"}

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "paper_quality_is_claim_evidence_not_prose_quality": True,
    "baseline_presence_without_role_is_insufficient": True,
    "empirical_superiority_requires_empirical_matched_baseline": True,
    "multi_component_method_requires_component_ablation": True,
    "mechanism_claim_requires_ruling_out_test": True,
    "failure_and_sensitivity_analysis_are_submission_evidence": True,
    "theory_certificate_may_waive_component_ablation_only_with_explicit_non_applicability": True,
    "paper_ready_requires_completed_evidence_not_planned_evidence": True,
    "failed_or_inconclusive_experiments_remain_visible_evidence": True,
    "visual_evidence_requires_reviewer_question_and_takeaway": True,
    "multi_panel_visuals_may_cover_multiple_evidence_roles": True,
    "quantitative_visuals_require_versioned_data_and_figure_qa": True,
    "negative_failure_or_boundary_evidence_must_be_visually_exposed": True,
    "manuscript_ready_requires_visual_artifact_data_script_caption_binding": True,
    "paper_ready_content_addressed_mode_rejects_missing_stale_or_path_traversal_artifacts": True,
    "claim_adjudication_may_reference_only_registered_completed_evidence_ids": True,
    "manuscript_claims_must_read_from_claim_ledger": True,
    "claim_ledger_preserves_refuted_and_inconclusive_rows": True,
    "claim_ledger_has_zero_scientific_authority": True,
    "quality_gate_cannot_authorize_method_experiment_p0_or_gpu": True,
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _rows(value: Any) -> list[dict[str, Any]]:
    return [row for row in (value or []) if isinstance(row, dict)] if isinstance(value, list) else []


def _ids(rows: Iterable[dict[str, Any]]) -> set[str]:
    return {_text(row.get("id")) for row in rows if _text(row.get("id"))}


def _list_text(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _claim_requires_empirical_baseline(claim_type: str) -> bool:
    return claim_type in {"performance", "mechanism", "system", "robustness", "cost", "empirical_analysis"}


def _claim_requires_mechanism_analysis(claim_type: str) -> bool:
    return claim_type in {"mechanism", "system"}


def audit_paper_evidence_plan(quality: dict[str, Any] | None, *, method_components: int = 0) -> dict[str, Any]:
    quality = quality if isinstance(quality, dict) else {}
    blockers: list[str] = []
    warnings: list[str] = []

    version = _text(quality.get("schema_version"))
    archetype = _text(quality.get("paper_archetype"))
    if version != SCHEMA_VERSION:
        blockers.append("paper-quality-schema-version-missing-or-stale")
    if archetype not in PAPER_ARCHETYPES:
        blockers.append("paper-quality-archetype-invalid")

    claims = _rows(quality.get("claims"))
    baselines = _rows(quality.get("baselines"))
    ablations = _rows(quality.get("ablations"))
    analyses = _rows(quality.get("analyses"))
    outputs = _rows(quality.get("planned_outputs"))
    visualizations = _rows(quality.get("visualizations"))

    if not claims:
        blockers.append("paper-quality-claims-missing")
    if not baselines:
        blockers.append("paper-quality-baselines-missing")
    if not analyses:
        blockers.append("paper-quality-analyses-missing")
    if not outputs:
        blockers.append("paper-quality-planned-outputs-missing")
    if not visualizations:
        blockers.append("paper-quality-visualizations-missing")

    claim_ids = _ids(claims)
    baseline_ids = _ids(baselines)
    ablation_ids = _ids(ablations)
    analysis_ids = _ids(analyses)
    output_ids = _ids(outputs)
    visualization_ids = _ids(visualizations)
    evidence_ids = baseline_ids | ablation_ids | analysis_ids | output_ids

    for collection, rows in (("claim", claims), ("baseline", baselines), ("ablation", ablations), ("analysis", analyses), ("output", outputs), ("visualization", visualizations)):
        seen: set[str] = set()
        for index, row in enumerate(rows):
            row_id = _text(row.get("id"))
            if not row_id:
                blockers.append(f"paper-quality-{collection}-id-missing:{index}")
            elif row_id in seen:
                blockers.append(f"paper-quality-{collection}-id-duplicate:{row_id}")
            seen.add(row_id)

    for index, row in enumerate(baselines):
        bid = _text(row.get("id")) or str(index)
        role = _text(row.get("role"))
        evidence_type = _text(row.get("evidence_type"))
        targets = _list_text(row.get("target_claim_ids"))
        if role not in BASELINE_ROLES:
            blockers.append(f"paper-quality-baseline-role-invalid:{bid}")
        if evidence_type not in {"empirical", "analytical"}:
            blockers.append(f"paper-quality-baseline-evidence-type-invalid:{bid}")
        if not _text(row.get("purpose")):
            blockers.append(f"paper-quality-baseline-purpose-missing:{bid}")
        if not targets or any(target not in claim_ids for target in targets):
            blockers.append(f"paper-quality-baseline-claim-link-invalid:{bid}")
        if evidence_type == "empirical" and not _list_text(row.get("matched_dimensions")):
            blockers.append(f"paper-quality-empirical-baseline-matching-missing:{bid}")

    for index, row in enumerate(ablations):
        aid = _text(row.get("id")) or str(index)
        kind = _text(row.get("ablation_type"))
        targets = _list_text(row.get("target_claim_ids"))
        if kind not in ABLATION_TYPES:
            blockers.append(f"paper-quality-ablation-type-invalid:{aid}")
        if not _text(row.get("purpose")) or not _text(row.get("decision_rule")):
            blockers.append(f"paper-quality-ablation-diagnostic-incomplete:{aid}")
        if not targets or any(target not in claim_ids for target in targets):
            blockers.append(f"paper-quality-ablation-claim-link-invalid:{aid}")

    for index, row in enumerate(analyses):
        xid = _text(row.get("id")) or str(index)
        kind = _text(row.get("analysis_type"))
        targets = _list_text(row.get("target_claim_ids"))
        if kind not in ANALYSIS_TYPES:
            blockers.append(f"paper-quality-analysis-type-invalid:{xid}")
        if not _text(row.get("purpose")) or not _text(row.get("decision_rule")):
            blockers.append(f"paper-quality-analysis-diagnostic-incomplete:{xid}")
        if not targets or any(target not in claim_ids for target in targets):
            blockers.append(f"paper-quality-analysis-claim-link-invalid:{xid}")

    for index, row in enumerate(visualizations):
        vid = _text(row.get("id")) or str(index)
        visual_type = _text(row.get("visual_type"))
        placement = _text(row.get("placement"))
        roles = _list_text(row.get("panel_roles"))
        targets = _list_text(row.get("target_claim_ids"))
        source_evidence = _list_text(row.get("source_evidence_ids"))
        quantitative = row.get("quantitative")
        uncertainty_required = row.get("uncertainty_required")
        negative_visible = row.get("negative_or_failure_visible")
        if visual_type not in VISUAL_TYPES:
            blockers.append(f"paper-quality-visual-type-invalid:{vid}")
        if placement not in VISUAL_PLACEMENTS:
            blockers.append(f"paper-quality-visual-placement-invalid:{vid}")
        if not roles or any(role not in VISUAL_ROLES for role in roles):
            blockers.append(f"paper-quality-visual-role-invalid:{vid}")
        if not targets or any(target not in claim_ids for target in targets):
            blockers.append(f"paper-quality-visual-claim-link-invalid:{vid}")
        if not source_evidence or any(item not in evidence_ids for item in source_evidence):
            blockers.append(f"paper-quality-visual-evidence-link-invalid:{vid}")
        if not _text(row.get("reviewer_question")) or not _text(row.get("takeaway")):
            blockers.append(f"paper-quality-visual-question-or-takeaway-missing:{vid}")
        if not isinstance(quantitative, bool):
            blockers.append(f"paper-quality-visual-quantitative-flag-missing:{vid}")
        if quantitative is True and not isinstance(uncertainty_required, bool):
            blockers.append(f"paper-quality-visual-uncertainty-plan-missing:{vid}")
        if not isinstance(negative_visible, bool):
            blockers.append(f"paper-quality-visual-negative-failure-flag-missing:{vid}")

    baseline_by_id = {str(row.get("id")): row for row in baselines if _text(row.get("id"))}
    ablation_by_id = {str(row.get("id")): row for row in ablations if _text(row.get("id"))}
    analysis_by_id = {str(row.get("id")): row for row in analyses if _text(row.get("id"))}
    visual_by_id = {str(row.get("id")): row for row in visualizations if _text(row.get("id"))}

    for index, row in enumerate(claims):
        cid = _text(row.get("id")) or str(index)
        claim_type = _text(row.get("claim_type"))
        if claim_type not in CLAIM_TYPES:
            blockers.append(f"paper-quality-claim-type-invalid:{cid}")
        if not _text(row.get("statement")):
            blockers.append(f"paper-quality-claim-statement-missing:{cid}")
        if not _text(row.get("why_better_or_why_matters")):
            blockers.append(f"paper-quality-claim-why-missing:{cid}")
        alternative_explanations = _list_text(row.get("alternative_explanations"))
        if claim_type in {"performance", "mechanism", "system", "empirical_analysis"} and not alternative_explanations:
            blockers.append(f"paper-quality-alternative-explanations-missing:{cid}")

        linked_baselines = _list_text(row.get("baseline_ids"))
        linked_ablations = _list_text(row.get("ablation_ids"))
        linked_analyses = _list_text(row.get("analysis_ids"))
        linked_outputs = _list_text(row.get("output_ids"))
        linked_visuals = _list_text(row.get("visualization_ids"))
        if any(item not in baseline_ids for item in linked_baselines):
            blockers.append(f"paper-quality-claim-baseline-link-invalid:{cid}")
        if any(item not in ablation_ids for item in linked_ablations):
            blockers.append(f"paper-quality-claim-ablation-link-invalid:{cid}")
        if any(item not in analysis_ids for item in linked_analyses):
            blockers.append(f"paper-quality-claim-analysis-link-invalid:{cid}")
        if not linked_outputs or any(item not in output_ids for item in linked_outputs):
            blockers.append(f"paper-quality-claim-output-link-invalid:{cid}")
        if not linked_visuals or any(item not in visualization_ids for item in linked_visuals):
            blockers.append(f"paper-quality-claim-visual-link-invalid:{cid}")
        elif not any(_text(visual_by_id[item].get("placement")) == "main" for item in linked_visuals if item in visual_by_id):
            blockers.append(f"paper-quality-claim-without-main-visual:{cid}")

        if _claim_requires_empirical_baseline(claim_type):
            empirical = [baseline_by_id[item] for item in linked_baselines if item in baseline_by_id and baseline_by_id[item].get("evidence_type") == "empirical"]
            if not empirical:
                blockers.append(f"paper-quality-empirical-claim-without-empirical-baseline:{cid}")
        if claim_type in {"performance", "mechanism", "system"}:
            roles = {_text(baseline_by_id[item].get("role")) for item in linked_baselines if item in baseline_by_id}
            if not roles.intersection({"same_information_simplification", "direct_competitor", "current_system"}):
                blockers.append(f"paper-quality-strong-baseline-role-missing:{cid}")
        if _claim_requires_mechanism_analysis(claim_type):
            analysis_types = {_text(analysis_by_id[item].get("analysis_type")) for item in linked_analyses if item in analysis_by_id}
            if "mechanism" not in analysis_types:
                blockers.append(f"paper-quality-mechanism-analysis-missing:{cid}")
            if "alternative_explanation" not in analysis_types:
                blockers.append(f"paper-quality-ruling-out-analysis-missing:{cid}")
            if not _list_text(row.get("ruling_out_experiments")):
                blockers.append(f"paper-quality-ruling-out-experiments-missing:{cid}")
        if claim_type in {"performance", "system", "cost"} and not _text(row.get("expected_advantage_region")):
            blockers.append(f"paper-quality-where-better-missing:{cid}")

    analysis_types = {_text(row.get("analysis_type")) for row in analyses}
    if "failure" not in analysis_types:
        blockers.append("paper-quality-failure-analysis-missing")
    if "sensitivity" not in analysis_types and "robustness" not in analysis_types:
        blockers.append("paper-quality-sensitivity-or-robustness-analysis-missing")
    if any(_claim_requires_empirical_baseline(_text(row.get("claim_type"))) for row in claims) and "uncertainty" not in analysis_types:
        blockers.append("paper-quality-uncertainty-analysis-missing")
    if archetype == "system":
        if "scaling" not in analysis_types:
            blockers.append("paper-quality-system-scaling-analysis-missing")
        if "human_evaluation" not in analysis_types:
            warnings.append("paper-quality-system-human-evaluation-recommended")

    if archetype in {"method", "system"} and method_components > 1:
        if not any(_text(row.get("ablation_type")) == "component" for row in ablations):
            blockers.append("paper-quality-multi-component-method-without-component-ablation")
    if archetype == "theory_certificate":
        if not any(_text(row.get("role")) == "analytical_simplification" for row in baselines):
            blockers.append("paper-quality-theory-certificate-analytical-baseline-missing")
        if not any(_text(row.get("ablation_type")) == "assumption_boundary" for row in ablations):
            blockers.append("paper-quality-theory-certificate-boundary-stress-missing")

    main_visuals = [row for row in visualizations if _text(row.get("placement")) == "main"]
    main_visual_roles = {role for row in main_visuals for role in _list_text(row.get("panel_roles"))}
    if len(main_visuals) < 3:
        blockers.append("paper-quality-main-visual-count-below-three")
    required_visual_roles = {
        "method": {"main_comparison", "ablation", "mechanism", "failure", "sensitivity"},
        "system": {"overview", "main_comparison", "failure", "sensitivity", "scaling"},
        "empirical_analysis": {"main_comparison", "mechanism", "failure", "sensitivity"},
        "theory_certificate": {"boundary", "mechanism", "failure", "sensitivity"},
    }.get(archetype, set())
    for role in sorted(required_visual_roles - main_visual_roles):
        blockers.append(f"paper-quality-main-visual-role-missing:{role}")
    if archetype == "method" and "overview" not in main_visual_roles:
        warnings.append("paper-quality-method-overview-visual-recommended")
    if archetype == "system" and "human_evaluation" not in main_visual_roles:
        warnings.append("paper-quality-system-human-evaluation-visual-recommended")
    needs_negative_visible = archetype in PAPER_ARCHETYPES and (
        archetype == "theory_certificate"
        or any(_claim_requires_empirical_baseline(_text(row.get("claim_type"))) for row in claims)
    )
    if needs_negative_visible and not any(row.get("negative_or_failure_visible") is True for row in main_visuals):
        blockers.append("paper-quality-main-visual-negative-or-failure-evidence-missing")
    uncertainty_analyses = {_text(row.get("id")) for row in analyses if _text(row.get("analysis_type")) == "uncertainty"}
    for row in main_visuals:
        if row.get("quantitative") is True and row.get("uncertainty_required") is True:
            if not uncertainty_analyses.intersection(_list_text(row.get("source_evidence_ids"))):
                blockers.append(f"paper-quality-visual-uncertainty-evidence-link-missing:{_text(row.get('id'))}")

    required_output_kinds = {"main_comparison", "ablation", "mechanism", "failure", "sensitivity"}
    output_kinds = {_text(row.get("output_type")) for row in outputs}
    if archetype in {"method", "system"}:
        for kind in sorted(required_output_kinds):
            if kind not in output_kinds:
                blockers.append(f"paper-quality-required-output-missing:{kind}")
    elif archetype in {"empirical_analysis", "theory_certificate"}:
        for kind in ("main_comparison", "mechanism", "failure", "sensitivity"):
            if kind not in output_kinds:
                blockers.append(f"paper-quality-required-output-missing:{kind}")
        if "ablation" not in output_kinds:
            warnings.append("paper-quality-explicit-ablation-output-recommended")

    passed = not blockers
    return {
        "schema_version": SCHEMA_VERSION,
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "status": "PASS_PAPER_EVIDENCE_PLAN" if passed else "REPAIR_PAPER_EVIDENCE_PLAN",
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "summary": {
            "paper_archetype": archetype,
            "claims": len(claims),
            "baselines": len(baselines),
            "ablations": len(ablations),
            "analyses": len(analyses),
            "planned_outputs": len(outputs),
            "visualizations": len(visualizations),
            "main_visualizations": len(main_visuals),
            "main_visual_roles": sorted(main_visual_roles),
        },
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
    }


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _completion_file_refs(completion: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for row in _rows(completion.get("evidence")):
        refs.update(_list_text(row.get("artifact_refs")))
    for row in _rows(completion.get("visualizations")):
        for key in ("artifact_refs", "data_refs", "script_refs"):
            refs.update(_list_text(row.get(key)))
    refs.update(_list_text(completion.get("manuscript_refs")))
    return refs


def audit_content_addressed_completion(
    completion: dict[str, Any] | None,
    source_sha256: dict[str, Any] | None,
    project_root: Path | None,
) -> dict[str, Any]:
    completion = completion if isinstance(completion, dict) else {}
    registry = source_sha256 if isinstance(source_sha256, dict) else {}
    blockers: list[str] = []
    refs = sorted(_completion_file_refs(completion))
    root = project_root.resolve() if isinstance(project_root, Path) else None
    if not refs:
        blockers.append("paper-quality-content-addressed-artifact-refs-missing")
    if root is None:
        blockers.append("paper-quality-content-addressed-project-root-missing")
    for ref in refs:
        rel = Path(ref)
        if rel.is_absolute() or ".." in rel.parts:
            blockers.append(f"paper-quality-artifact-ref-unsafe:{ref}")
            continue
        expected = _text(registry.get(ref)).lower()
        if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
            blockers.append(f"paper-quality-artifact-digest-missing-or-invalid:{ref}")
            continue
        if root is None:
            continue
        target = (root / rel).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            blockers.append(f"paper-quality-artifact-ref-escapes-root:{ref}")
            continue
        if not target.is_file():
            blockers.append(f"paper-quality-artifact-file-missing:{ref}")
            continue
        actual = _sha256(target)
        if actual != expected:
            blockers.append(f"paper-quality-artifact-digest-mismatch:{ref}")
    return {
        "required": True,
        "passed": not blockers,
        "status": "PASS_CONTENT_ADDRESSED_COMPLETION" if not blockers else "HOLD_CONTENT_ADDRESSED_COMPLETION",
        "blockers": sorted(set(blockers)),
        "summary": {"referenced_files": len(refs), "registered_digests": len(registry)},
    }


def audit_manuscript_evidence_completion(
    quality: dict[str, Any] | None,
    completion: dict[str, Any] | None,
    *,
    method_components: int = 0,
    source_sha256: dict[str, Any] | None = None,
    project_root: Path | None = None,
    require_content_addressed: bool = False,
) -> dict[str, Any]:
    plan = audit_paper_evidence_plan(quality, method_components=method_components)
    completion = completion if isinstance(completion, dict) else {}
    blockers = list(plan.get("blockers") or [])

    required_ids = {
        "baseline": _ids(_rows((quality or {}).get("baselines"))),
        "ablation": _ids(_rows((quality or {}).get("ablations"))),
        "analysis": _ids(_rows((quality or {}).get("analyses"))),
        "output": _ids(_rows((quality or {}).get("planned_outputs"))),
    }
    visual_specs = _rows((quality or {}).get("visualizations"))
    completed = _rows(completion.get("evidence"))
    completed_by_id = {_text(row.get("id")): row for row in completed if _text(row.get("id"))}

    for kind, ids in required_ids.items():
        for item_id in sorted(ids):
            row = completed_by_id.get(item_id) or {}
            status = _text(row.get("status"))
            artifact_refs = _list_text(row.get("artifact_refs"))
            if status not in {"PASS", "FAIL", "INCONCLUSIVE", "NOT_APPLICABLE"}:
                blockers.append(f"paper-quality-evidence-not-completed:{kind}:{item_id}")
                continue
            if status == "NOT_APPLICABLE":
                if not _text(row.get("justification")):
                    blockers.append(f"paper-quality-not-applicable-without-justification:{kind}:{item_id}")
            elif not artifact_refs:
                blockers.append(f"paper-quality-completed-evidence-without-artifact:{kind}:{item_id}")

    visual_completion = _rows(completion.get("visualizations"))
    visual_completion_by_id = {_text(row.get("id")): row for row in visual_completion if _text(row.get("id"))}
    for spec in visual_specs:
        vid = _text(spec.get("id"))
        if not vid:
            continue
        row = visual_completion_by_id.get(vid) or {}
        status = _text(row.get("status"))
        if status not in {"PASS", "FAIL", "INCONCLUSIVE", "NOT_APPLICABLE"}:
            blockers.append(f"paper-quality-visual-not-completed:{vid}")
            continue
        if status == "NOT_APPLICABLE":
            if not _text(row.get("justification")):
                blockers.append(f"paper-quality-visual-not-applicable-without-justification:{vid}")
            continue
        if not _list_text(row.get("artifact_refs")):
            blockers.append(f"paper-quality-visual-artifact-missing:{vid}")
        if not _list_text(row.get("script_refs")):
            blockers.append(f"paper-quality-visual-script-missing:{vid}")
        if not _text(row.get("caption_ref")):
            blockers.append(f"paper-quality-visual-caption-binding-missing:{vid}")
        if spec.get("quantitative") is True and not _list_text(row.get("data_refs")):
            blockers.append(f"paper-quality-visual-data-binding-missing:{vid}")
        review = row.get("visual_review") if isinstance(row.get("visual_review"), dict) else {}
        for check in ("caption_claim_aligned", "legible_labels", "legend_or_direct_labels", "non_deceptive_scale", "source_data_versioned"):
            if review.get(check) is not True:
                blockers.append(f"paper-quality-visual-review-failed:{vid}:{check}")
        if spec.get("uncertainty_required") is True and review.get("uncertainty_visible") is not True:
            blockers.append(f"paper-quality-visual-review-failed:{vid}:uncertainty_visible")
        if spec.get("negative_or_failure_visible") is True and review.get("negative_or_failure_visible") is not True:
            blockers.append(f"paper-quality-visual-review-failed:{vid}:negative_or_failure_visible")

    claim_rows = _rows((quality or {}).get("claims"))
    claim_completion = completion.get("claims") if isinstance(completion.get("claims"), dict) else {}
    registered_evidence_ids = set().union(*required_ids.values())
    claim_ledger: list[dict[str, Any]] = []
    for row in claim_rows:
        cid = _text(row.get("id"))
        if not cid:
            continue
        state = claim_completion.get(cid) if isinstance(claim_completion.get(cid), dict) else {}
        adjudication_status = _text(state.get("status"))
        if adjudication_status not in {"SUPPORTED", "SUPPORTED_NARROWLY", "REFUTED", "INCONCLUSIVE"}:
            blockers.append(f"paper-quality-claim-adjudication-missing:{cid}")
        claim_evidence_ids = _list_text(state.get("evidence_ids"))
        linked_evidence_ids = set(
            _list_text(row.get("baseline_ids"))
            + _list_text(row.get("ablation_ids"))
            + _list_text(row.get("analysis_ids"))
            + _list_text(row.get("output_ids"))
        )
        trace_rows: list[dict[str, Any]] = []
        trace_complete = bool(claim_evidence_ids)
        if not claim_evidence_ids:
            blockers.append(f"paper-quality-claim-evidence-trace-missing:{cid}")
        else:
            for evidence_id in claim_evidence_ids:
                registered = evidence_id in registered_evidence_ids
                linked = evidence_id in linked_evidence_ids
                completed_row = completed_by_id.get(evidence_id) or {}
                completion_status = _text(completed_row.get("status"))
                completed_ok = completion_status in {"PASS", "FAIL", "INCONCLUSIVE", "NOT_APPLICABLE"}
                trace_rows.append({
                    "evidence_id": evidence_id,
                    "registered": registered,
                    "linked_to_claim": linked,
                    "completion_status": completion_status,
                    "completed": completed_ok,
                })
                if not registered:
                    blockers.append(f"paper-quality-claim-evidence-id-unregistered:{cid}:{evidence_id}")
                elif not linked:
                    blockers.append(f"paper-quality-claim-evidence-id-not-linked:{cid}:{evidence_id}")
                elif evidence_id not in completed_by_id:
                    blockers.append(f"paper-quality-claim-evidence-id-not-completed:{cid}:{evidence_id}")
                trace_complete = trace_complete and registered and linked and completed_ok
        manuscript_surface = {
            "SUPPORTED": "AFFIRMATIVE_SUPPORTED",
            "SUPPORTED_NARROWLY": "AFFIRMATIVE_NARROW_ONLY",
            "REFUTED": "NEGATIVE_OR_REFUTED_ONLY",
            "INCONCLUSIVE": "INCONCLUSIVE_ONLY",
        }.get(adjudication_status, "UNADJUDICATED")
        claim_ledger.append({
            "claim_id": cid,
            "claim_type": _text(row.get("claim_type")),
            "claim_text": _text(row.get("statement") or row.get("claim") or row.get("claim_text") or row.get("text")),
            "adjudication_status": adjudication_status,
            "manuscript_surface": manuscript_surface,
            "affirmative_claim_allowed": adjudication_status in {"SUPPORTED", "SUPPORTED_NARROWLY"} and trace_complete,
            "must_preserve_negative_or_inconclusive": adjudication_status in {"REFUTED", "INCONCLUSIVE"},
            "evidence_ids": claim_evidence_ids,
            "evidence_trace": trace_rows,
            "trace_complete": trace_complete,
            "scientific_authority": False,
        })

    content_addressed = {"required": False, "passed": True, "status": "NOT_REQUIRED", "blockers": [], "summary": {"referenced_files": 0, "registered_digests": 0}}
    if require_content_addressed:
        content_addressed = audit_content_addressed_completion(completion, source_sha256, project_root)
        blockers.extend(content_addressed.get("blockers") or [])

    passed = not blockers
    return {
        "schema_version": SCHEMA_VERSION,
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "status": "PASS_MANUSCRIPT_EVIDENCE" if passed else "HOLD_MANUSCRIPT_EVIDENCE_INCOMPLETE",
        "blockers": sorted(set(blockers)),
        "plan": plan,
        "summary": {
            **(plan.get("summary") or {}),
            "completed_evidence_rows": len(completed),
            "claim_adjudications": len(claim_completion),
            "completed_visualizations": len(visual_completion),
            "content_addressed_required": bool(require_content_addressed),
            "content_addressed_referenced_files": int((content_addressed.get("summary") or {}).get("referenced_files") or 0),
        },
        "claim_ledger": claim_ledger,
        "content_addressed_completion": content_addressed,
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
    }
