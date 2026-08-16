from __future__ import annotations

from typing import Any, Iterable


SCHEMA_VERSION = "2.0"

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
}

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

    if not claims:
        blockers.append("paper-quality-claims-missing")
    if not baselines:
        blockers.append("paper-quality-baselines-missing")
    if not analyses:
        blockers.append("paper-quality-analyses-missing")
    if not outputs:
        blockers.append("paper-quality-planned-outputs-missing")

    claim_ids = _ids(claims)
    baseline_ids = _ids(baselines)
    ablation_ids = _ids(ablations)
    analysis_ids = _ids(analyses)
    output_ids = _ids(outputs)

    for collection, rows in (("claim", claims), ("baseline", baselines), ("ablation", ablations), ("analysis", analyses), ("output", outputs)):
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

    baseline_by_id = {str(row.get("id")): row for row in baselines if _text(row.get("id"))}
    ablation_by_id = {str(row.get("id")): row for row in ablations if _text(row.get("id"))}
    analysis_by_id = {str(row.get("id")): row for row in analyses if _text(row.get("id"))}

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
        if any(item not in baseline_ids for item in linked_baselines):
            blockers.append(f"paper-quality-claim-baseline-link-invalid:{cid}")
        if any(item not in ablation_ids for item in linked_ablations):
            blockers.append(f"paper-quality-claim-ablation-link-invalid:{cid}")
        if any(item not in analysis_ids for item in linked_analyses):
            blockers.append(f"paper-quality-claim-analysis-link-invalid:{cid}")
        if not linked_outputs or any(item not in output_ids for item in linked_outputs):
            blockers.append(f"paper-quality-claim-output-link-invalid:{cid}")

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

    if archetype in {"method", "system"} and method_components > 1:
        if not any(_text(row.get("ablation_type")) == "component" for row in ablations):
            blockers.append("paper-quality-multi-component-method-without-component-ablation")
    if archetype == "theory_certificate":
        if not any(_text(row.get("role")) == "analytical_simplification" for row in baselines):
            blockers.append("paper-quality-theory-certificate-analytical-baseline-missing")
        if not any(_text(row.get("ablation_type")) == "assumption_boundary" for row in ablations):
            blockers.append("paper-quality-theory-certificate-boundary-stress-missing")

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
        },
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
    }


def audit_manuscript_evidence_completion(quality: dict[str, Any] | None, completion: dict[str, Any] | None, *, method_components: int = 0) -> dict[str, Any]:
    plan = audit_paper_evidence_plan(quality, method_components=method_components)
    completion = completion if isinstance(completion, dict) else {}
    blockers = list(plan.get("blockers") or [])

    required_ids = {
        "baseline": _ids(_rows((quality or {}).get("baselines"))),
        "ablation": _ids(_rows((quality or {}).get("ablations"))),
        "analysis": _ids(_rows((quality or {}).get("analyses"))),
        "output": _ids(_rows((quality or {}).get("planned_outputs"))),
    }
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

    claim_rows = _rows((quality or {}).get("claims"))
    claim_completion = completion.get("claims") if isinstance(completion.get("claims"), dict) else {}
    for row in claim_rows:
        cid = _text(row.get("id"))
        if not cid:
            continue
        state = claim_completion.get(cid) if isinstance(claim_completion.get(cid), dict) else {}
        if _text(state.get("status")) not in {"SUPPORTED", "SUPPORTED_NARROWLY", "REFUTED", "INCONCLUSIVE"}:
            blockers.append(f"paper-quality-claim-adjudication-missing:{cid}")
        if not _list_text(state.get("evidence_ids")):
            blockers.append(f"paper-quality-claim-evidence-trace-missing:{cid}")

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
        },
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
    }
