from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
AUTHOR_GUIDE_ABSTRACT_DEADLINE_AOE = "2026-09-18"
AUTHOR_GUIDE_FULL_PAPER_DEADLINE_AOE = "2026-09-25"
OTHER_OFFICIAL_ABSTRACT_DEADLINE_AOE = "2026-09-11"
OTHER_OFFICIAL_FULL_PAPER_DEADLINE_AOE = "2026-09-16"
OPERATIONAL_SAFE_ABSTRACT_DEADLINE_AOE = "2026-09-11"
OPERATIONAL_SAFE_FULL_PAPER_DEADLINE_AOE = "2026-09-16"

FINAL_REVIEW = "generated/asset-first-stri-narrow-final-review-20260816.json"
COHERENCE = "generated/asset-first-stri-narrow-paper-coherence-20260816.json"
SUBMISSION_QA = "generated/asset-first-stri-submission-qa-20260816.json"
REDUCTION = "generated/asset-first-skill-taxonomy-representation-invariance-reduction-20260816.json"
PAPER_DESIGN = "generated/asset-first-stri-narrow-paper-design-20260816.json"
PAPER_QUALITY_V2 = "generated/asset-first-stri-paper-quality-v2-20260816.json"
CURRENT_SOURCE = "generated/asset-first-stri-current-source-review-20260816.json"
OFFICIAL_FINAL_STATE = "generated/asset-first-stri-iclr2027-final-state-20260816.json"
OFFICIAL_SUBMISSION_QA = "generated/asset-first-stri-iclr2027-submission-qa-20260816.json"
SUPPLEMENT_STATE = "generated/asset-first-stri-iclr2027-supplement-state-20260816.json"
OPENREVIEW_READINESS = "generated/asset-first-stri-iclr2027-openreview-readiness-20260816.json"
P0E_PRINCIPLE_DISPOSITION = "generated/asset-first-stri-skillrl-final-policy-p0e-principle-disposition-20260817.json"
P0E_DIAGNOSIS = "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
PUBLIC_TEX_SOURCE = "paper_drafts/stri-20260816-iclr2027-main.tex"
PUBLIC_DOWNLOADS = {
    "tex": "downloads/STRI-ICLR2027.tex",
    "pdf": "downloads/STRI-ICLR2027.pdf",
    "source_zip": "downloads/STRI-ICLR2027-source.zip",
}

SOURCE_ARTIFACTS = {
    "final_review": FINAL_REVIEW,
    "coherence": COHERENCE,
    "submission_qa": SUBMISSION_QA,
    "reduction": REDUCTION,
    "paper_design": PAPER_DESIGN,
    "paper_quality_v2": PAPER_QUALITY_V2,
    "current_source_review": CURRENT_SOURCE,
    "official_final_state": OFFICIAL_FINAL_STATE,
    "official_submission_qa": OFFICIAL_SUBMISSION_QA,
    "supplement_state": SUPPLEMENT_STATE,
    "openreview_readiness": OPENREVIEW_READINESS,
    "skillrl_p0e_principle_disposition": P0E_PRINCIPLE_DISPOSITION,
    "skillrl_p0e_diagnosis": P0E_DIAGNOSIS,
}

POLICY = {
    "asset_first_track_is_separate_from_canonical_problem_gate": True,
    "asset_first_ready_cannot_mutate_canonical_generator_or_queue": True,
    "asset_first_ready_is_not_canonical_problem_gate_pass": True,
    "paper_ready_requires_final_review": True,
    "paper_ready_requires_claim_coherence": True,
    "paper_ready_requires_submission_qa": True,
    "paper_ready_requires_current_source_survival": True,
    "paper_ready_requires_superseding_reduction_state": True,
    "paper_ready_requires_paper_quality_v2": True,
    "paper_ready_requires_visual_evidence_contract": True,
    "paper_quality_receipt_is_content_addressed": True,
    "mechanical_and_format_qa_cannot_substitute_for_scientific_evidence_completeness": True,
    "dynamic_p0_is_not_required_for_the_narrow_claim_scope": True,
    "dynamic_qualification_failure_is_not_positive_or_negative_narrow_evidence": True,
    "optional_c4_realization_stop_cannot_expand_or_invalidate_n1_n2_n3": True,
    "persistent_principle_dead_end_requires_statistical_resolution_beyond_realization_stop": True,
    "paper_ready_does_not_authorize_method_p0_or_gpu": True,
    "official_submission_ready_requires_iclr2027_format_qa": True,
    "official_submission_ready_requires_anonymous_supplement_reproduction": True,
    "public_downloads_are_anonymous_submission_assets": True,
    "human_author_signoff_cannot_be_auto_authorized": True,
    "abstract_deadline_freezes_author_membership": True,
    "full_paper_deadline_freezes_title": True,
    "official_deadline_source_conflict_must_be_visible": True,
    "deadline_source_conflict_fails_safe_to_earliest_published_official_date": True,
    "human_deadline_verification_cannot_be_auto_authorized": True,
}

AUTHORITY = {
    "canonical_problem_gate": False,
    "canonical_generator": False,
    "canonical_queue": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def build_asset_first_stri_public_status(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    values = {key: _load(project_root / rel) for key, rel in SOURCE_ARTIFACTS.items()}
    final = values["final_review"]
    coherence = values["coherence"]
    qa = values["submission_qa"]
    reduction = values["reduction"]
    design = values["paper_design"]
    paper_quality = values["paper_quality_v2"]
    current = values["current_source_review"]
    official_final = values["official_final_state"]
    official_qa = values["official_submission_qa"]
    supplement = values["supplement_state"]
    openreview = values["openreview_readiness"]
    p0e_principle = values["skillrl_p0e_principle_disposition"]
    p0e_diagnosis = values["skillrl_p0e_diagnosis"]

    claims = coherence.get("claims") if isinstance(coherence.get("claims"), dict) else {}
    claim_ids = ("N1", "N2", "N3")
    supported = [claim_id for claim_id in claim_ids if (claims.get(claim_id) or {}).get("status") == "SUPPORTED"]
    qa_passed = int(qa.get("checks_passed") or 0)
    qa_total = int(qa.get("checks_total") or 0)
    official_qa_passed = int(official_qa.get("checks_passed") or 0)
    official_qa_total = int(official_qa.get("checks_total") or 0)
    supplement_tests = str((supplement.get("isolated_verification") or {}).get("unit_tests") or "")
    download_sha256 = {key: _sha(project_root / rel) for key, rel in PUBLIC_DOWNLOADS.items()}
    expected_pdf_sha256 = str((((official_final.get("delivery") or {}).get("pdf") or {}).get("sha256")) or "")
    expected_source_zip_sha256 = str((((official_final.get("delivery") or {}).get("source_zip") or {}).get("sha256")) or "")
    expected_tex_sha256 = _sha(project_root / PUBLIC_TEX_SOURCE)
    public_downloads_ready = (
        all(len(value) == 64 for value in download_sha256.values())
        and download_sha256["pdf"] == expected_pdf_sha256
        and download_sha256["source_zip"] == expected_source_zip_sha256
        and download_sha256["tex"] == expected_tex_sha256
    )
    quality_sources = [str(rel) for rel in (paper_quality.get("source_artifacts") or []) if str(rel)]
    quality_source_sha = paper_quality.get("source_sha256") if isinstance(paper_quality.get("source_sha256"), dict) else {}
    quality_plan_summary = ((((paper_quality.get("audit") or {}).get("plan") or {}).get("summary")) or {})
    paper_quality_source_binding = (
        bool(quality_sources)
        and set(quality_source_sha) == set(quality_sources)
        and all(
            len(str(quality_source_sha.get(rel) or "")) == 64
            and _sha(project_root / rel) == str(quality_source_sha.get(rel) or "")
            for rel in quality_sources
        )
    )

    gates = {
        "final_review": final.get("verdict") == "READY_NARROW_ICLR",
        "claim_coherence": coherence.get("status") == "READY_NARROW_ICLR_CLAIMS_COHERENT" and len(supported) == len(claim_ids),
        "submission_qa": qa.get("status") == "PASS" and qa_total > 0 and qa_passed == qa_total,
        "current_source": current.get("verdict") == "SURVIVES_NARROWLY",
        "superseding_reduction": reduction.get("status") == "NARROW_PAPER_READY_AFTER_DYNAMIC_QUALIFICATION_HOLD",
        "paper_design": str(design.get("submission_readiness") or "").startswith("READY_NARROW_ICLR"),
        "paper_quality_v2": paper_quality.get("paper_quality_gate_passed") is True and paper_quality.get("status") == "PASS_MANUSCRIPT_EVIDENCE",
        "paper_quality_source_binding": paper_quality_source_binding,
        "official_iclr2027_format": official_final.get("status") == "READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW" and official_qa.get("status") == "PASS" and official_qa_total > 0 and official_qa_passed == official_qa_total,
        "anonymous_supplement": supplement.get("status") == "PASS" and (supplement.get("isolated_verification") or {}).get("fresh_extract_manifest") == "PASS" and (supplement.get("isolated_verification") or {}).get("reproduce_py") == "PASS",
        "public_download_assets": public_downloads_ready,
        "openreview_machine_handoff": openreview.get("status") == "MACHINE_READY_HUMAN_SIGNOFF_REQUIRED",
    }
    ready = all(gates.values())
    artifacts = {
        key: {"path": rel, "sha256": _sha(project_root / rel), "present": bool(values[key])}
        for key, rel in SOURCE_ARTIFACTS.items()
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "STRI",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "title": str(coherence.get("title") or design.get("recommended_title") or "Skill-Taxonomy Representation Invariance"),
        "status": "READY_NARROW_ICLR" if ready else "HOLD_ASSET_FIRST_PAPER_NOT_READY",
        "submission_status": str(official_final.get("status") or "NOT_READY") if ready else "HOLD_PAPER_QUALITY_V2",
        "track": "ASSET_FIRST_PAPER_READY" if ready else "ASSET_FIRST_PAPER_QUALITY_REPAIR",
        "gates": gates,
        "claims": {
            claim_id: {
                "status": str((claims.get(claim_id) or {}).get("status") or "UNKNOWN"),
                "object": str((claims.get(claim_id) or {}).get("object") or ""),
                "forbidden": str((claims.get(claim_id) or {}).get("forbidden") or ""),
            }
            for claim_id in claim_ids
        },
        "summary": {
            "paper_ready": 1 if ready else 0,
            "claims_supported": len(supported),
            "claims_total": len(claim_ids),
            "qa_checks_passed": qa_passed,
            "qa_checks_total": qa_total,
            "official_qa_checks_passed": official_qa_passed,
            "official_qa_checks_total": official_qa_total,
            "main_text_pages": int(official_qa.get("main_text_pages") or 0),
            "main_text_page_limit": int(official_qa.get("main_text_page_limit") or 0),
            "supplement_ready": 1 if gates["anonymous_supplement"] else 0,
            "supplement_unit_tests": supplement_tests,
            "human_signoff_pending": 1 if openreview.get("status") == "MACHINE_READY_HUMAN_SIGNOFF_REQUIRED" else 0,
            "new_gpu_evidence_required": 1 if official_final.get("new_gpu_evidence_required_for_current_claim_scope") is True else 0,
            "final_review_confidence": float(final.get("confidence") or 0.0),
            "paper_quality_v2_passed": 1 if gates["paper_quality_v2"] and gates["paper_quality_source_binding"] else 0,
            "paper_quality_source_binding": 1 if gates["paper_quality_source_binding"] else 0,
            "paper_quality_evidence_debt": len(((paper_quality.get("evidence_debt") or {}).get("missing_or_incomplete_ids") or [])),
            "paper_quality_missing_ids": list(((paper_quality.get("evidence_debt") or {}).get("missing_or_incomplete_ids") or [])),
            "paper_quality_visualizations": int(quality_plan_summary.get("visualizations") or 0),
            "paper_quality_main_visualizations": int(quality_plan_summary.get("main_visualizations") or 0),
            "paper_quality_main_visual_roles": list(quality_plan_summary.get("main_visual_roles") or []),
            "skillrl_p0e_experimental_stop_valid": 1 if p0e_principle.get("experimental_stop_valid") is True else 0,
            "skillrl_p0e_principle_dead_end": 1 if p0e_principle.get("persistent_principle_dead_end_certified") is True else 0,
            "skillrl_p0e_stage2_locked": 1 if p0e_principle.get("stage2_confirmation_locked") is True else 0,
            "skillrl_p0e_new_gpu_authorized": 1 if p0e_principle.get("new_gpu_authorized") is True else 0,
            "skillrl_p0e_calibration_success": int((p0e_diagnosis.get("qualification") or {}).get("calibration_pristine_success") or 0),
            "skillrl_p0e_paired_units": int((p0e_diagnosis.get("qualification") or {}).get("paired_units") or 0),
            "canonical_problem_gate_pass_added": 0,
            "canonical_generator_candidates_added": 0,
            "canonical_queue_candidates_added": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "submission_handoff": {
            "recorded_author_guide_abstract_deadline_aoe": str((official_final.get("official_deadlines_aoe") or {}).get("abstract") or ""),
            "recorded_author_guide_full_paper_deadline_aoe": str((official_final.get("official_deadlines_aoe") or {}).get("full_paper") or ""),
            "official_source_conflict": True,
            "official_source_conflict_status": "HUMAN_VERIFICATION_REQUIRED",
            "conflicting_official_dates": {
                "author_guidelines": {"abstract": AUTHOR_GUIDE_ABSTRACT_DEADLINE_AOE, "full_paper": AUTHOR_GUIDE_FULL_PAPER_DEADLINE_AOE},
                "dates_cfp_conference_pages": {"abstract": OTHER_OFFICIAL_ABSTRACT_DEADLINE_AOE, "full_paper": OTHER_OFFICIAL_FULL_PAPER_DEADLINE_AOE},
            },
            "operational_safe_abstract_deadline_aoe": OPERATIONAL_SAFE_ABSTRACT_DEADLINE_AOE,
            "operational_safe_full_paper_deadline_aoe": OPERATIONAL_SAFE_FULL_PAPER_DEADLINE_AOE,
            "author_membership_freezes_at_abstract_deadline": True,
            "title_freezes_at_full_paper_deadline": True,
            "deadline_source_verified_on": "2026-08-17",
            "deadline_human_action": "Confirm the live OpenReview/ICLR deadline before submission; until resolved, plan against the earlier published official dates.",
            "pdf_sha256": str((((official_final.get("delivery") or {}).get("pdf") or {}).get("sha256")) or ""),
            "source_zip_sha256": str((((official_final.get("delivery") or {}).get("source_zip") or {}).get("sha256")) or ""),
            "supplement_zip_sha256": str((((official_final.get("delivery") or {}).get("supplement_zip") or {}).get("sha256")) or ""),
            "downloads": dict(PUBLIC_DOWNLOADS),
            "download_sha256": download_sha256,
            "human_action": "author-list/profile/quota/dual-submission/ethics/AI-use signoff and OpenReview upload only",
        },
        "claim_boundary": {
            "dynamic_p0": "Qwen3 qualification failure is excluded from narrow evidence; the separate SkillRL P0-E fixed-policy bridge is a qualified C4 realization STOP only",
            "skillrl_p0e": {
                "experimental_realization": str(p0e_principle.get("experimental_realization_disposition") or "UNKNOWN"),
                "principle_disposition": str(p0e_principle.get("principle_disposition") or "UNKNOWN"),
                "persistent_principle_dead_end_certified": bool(p0e_principle.get("persistent_principle_dead_end_certified", False)),
                "stage2_locked": bool(p0e_principle.get("stage2_confirmation_locked", True)),
                "new_gpu_authorized": bool(p0e_principle.get("new_gpu_authorized", False)),
                "broader_n1_n2_n3_unchanged": bool(p0e_principle.get("broader_STRI_N1_N2_N3_unchanged", False)),
            },
            "downstream_utility": "not claimed for the frozen N1-N3 scope; the P0-E sample-level endpoint STOP is not a population-level no-effect theorem",
            "solver_novelty": "STRI-Cert is not claimed as a computationally novel LP solver",
            "repair_method": "no claim that Support-Quotient Control has been empirically validated",
        },
        "source_artifacts": artifacts,
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def validate_asset_first_stri_public_status(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    authority = state.get("authority") or {}
    gates = state.get("gates") or {}

    if state.get("scientific_authority") is not False:
        errors.append("asset-first paper-ready projection must have zero scientific authority")
    for key, expected in POLICY.items():
        if policy.get(key) is not expected:
            errors.append(f"asset-first policy mismatch:{key}")
    if any(authority.get(key) is not False for key in AUTHORITY):
        errors.append("asset-first paper-ready projection cannot authorize canonical or execution state")
    if any(int(summary.get(key) or 0) != 0 for key in (
        "canonical_problem_gate_pass_added",
        "canonical_generator_candidates_added",
        "canonical_queue_candidates_added",
        "method_authorized",
        "experiment_authorized",
        "p0_authorized",
        "gpu_authorized",
    )):
        errors.append("asset-first paper-ready projection leaked canonical/execution authority")
    p0e = (state.get("claim_boundary") or {}).get("skillrl_p0e") or {}
    expected_p0e_summary = (1, 0, 1, 0, 18, 24)
    actual_p0e_summary = tuple(int(summary.get(key) or 0) for key in (
        "skillrl_p0e_experimental_stop_valid",
        "skillrl_p0e_principle_dead_end",
        "skillrl_p0e_stage2_locked",
        "skillrl_p0e_new_gpu_authorized",
        "skillrl_p0e_calibration_success",
        "skillrl_p0e_paired_units",
    ))
    if actual_p0e_summary != expected_p0e_summary:
        errors.append(f"SkillRL P0-E public summary drift:{actual_p0e_summary}")
    if (
        p0e.get("experimental_realization") != "STOP_FIXED_POLICY_DYNAMIC_BRIDGE"
        or p0e.get("principle_disposition") != "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED"
        or p0e.get("persistent_principle_dead_end_certified") is not False
        or p0e.get("stage2_locked") is not True
        or p0e.get("new_gpu_authorized") is not False
        or p0e.get("broader_n1_n2_n3_unchanged") is not True
    ):
        errors.append("SkillRL P0-E claim boundary drift")

    ready = state.get("status") == "READY_NARROW_ICLR"
    if ready:
        if not all(gates.get(key) is True for key in (
            "final_review", "claim_coherence", "submission_qa", "current_source", "superseding_reduction", "paper_design", "paper_quality_v2", "paper_quality_source_binding",
            "official_iclr2027_format", "anonymous_supplement", "public_download_assets", "openreview_machine_handoff",
        )):
            errors.append("READY_NARROW_ICLR requires every cross-validated paper-ready/submission gate")
        if int(summary.get("paper_ready") or 0) != 1:
            errors.append("READY_NARROW_ICLR must expose paper_ready=1")
        if (int(summary.get("claims_supported") or 0), int(summary.get("claims_total") or 0)) != (3, 3):
            errors.append("READY_NARROW_ICLR requires N1/N2/N3 supported")
        if int(summary.get("qa_checks_total") or 0) <= 0 or int(summary.get("qa_checks_passed") or 0) != int(summary.get("qa_checks_total") or 0):
            errors.append("READY_NARROW_ICLR requires complete submission QA")
        if state.get("submission_status") != "READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW":
            errors.append("READY_NARROW_ICLR official submission status is stale")
        if int(summary.get("official_qa_checks_total") or 0) <= 0 or int(summary.get("official_qa_checks_passed") or 0) != int(summary.get("official_qa_checks_total") or 0):
            errors.append("READY_NARROW_ICLR requires complete official ICLR format QA")
        pages = int(summary.get("main_text_pages") or 0)
        page_limit = int(summary.get("main_text_page_limit") or 0)
        if pages <= 0 or page_limit <= 0 or pages > page_limit:
            errors.append("READY_NARROW_ICLR violates official ICLR main-text page gate")
        if int(summary.get("supplement_ready") or 0) != 1 or "PASS" not in str(summary.get("supplement_unit_tests") or ""):
            errors.append("READY_NARROW_ICLR requires verified anonymous supplement reproduction")
        if int(summary.get("human_signoff_pending") or 0) != 1:
            errors.append("machine-ready STRI must remain pending human author signoff")
        if int(summary.get("new_gpu_evidence_required") or 0) != 0:
            errors.append("current narrow STRI submission cannot require a new GPU rescue")
        handoff = state.get("submission_handoff") or {}
        deadline_conflict = handoff.get("conflicting_official_dates") or {}
        if (
            handoff.get("recorded_author_guide_abstract_deadline_aoe") != AUTHOR_GUIDE_ABSTRACT_DEADLINE_AOE
            or handoff.get("recorded_author_guide_full_paper_deadline_aoe") != AUTHOR_GUIDE_FULL_PAPER_DEADLINE_AOE
            or handoff.get("official_source_conflict") is not True
            or handoff.get("official_source_conflict_status") != "HUMAN_VERIFICATION_REQUIRED"
            or (deadline_conflict.get("author_guidelines") or {}).get("abstract") != AUTHOR_GUIDE_ABSTRACT_DEADLINE_AOE
            or (deadline_conflict.get("author_guidelines") or {}).get("full_paper") != AUTHOR_GUIDE_FULL_PAPER_DEADLINE_AOE
            or (deadline_conflict.get("dates_cfp_conference_pages") or {}).get("abstract") != OTHER_OFFICIAL_ABSTRACT_DEADLINE_AOE
            or (deadline_conflict.get("dates_cfp_conference_pages") or {}).get("full_paper") != OTHER_OFFICIAL_FULL_PAPER_DEADLINE_AOE
            or handoff.get("operational_safe_abstract_deadline_aoe") != OPERATIONAL_SAFE_ABSTRACT_DEADLINE_AOE
            or handoff.get("operational_safe_full_paper_deadline_aoe") != OPERATIONAL_SAFE_FULL_PAPER_DEADLINE_AOE
            or handoff.get("author_membership_freezes_at_abstract_deadline") is not True
            or handoff.get("title_freezes_at_full_paper_deadline") is not True
        ):
            errors.append("READY_NARROW_ICLR official deadline conflict/fail-safe policy drift")
        for key in ("pdf_sha256", "source_zip_sha256", "supplement_zip_sha256"):
            if len(str(handoff.get(key) or "")) != 64:
                errors.append(f"READY_NARROW_ICLR submission handoff digest invalid:{key}")
        downloads = handoff.get("downloads") or {}
        download_sha256 = handoff.get("download_sha256") or {}
        if downloads != PUBLIC_DOWNLOADS:
            errors.append("READY_NARROW_ICLR public download URLs are stale")
        for key in PUBLIC_DOWNLOADS:
            if len(str(download_sha256.get(key) or "")) != 64:
                errors.append(f"READY_NARROW_ICLR public download digest invalid:{key}")
        for key, row in (state.get("source_artifacts") or {}).items():
            if row.get("present") is not True or len(str(row.get("sha256") or "")) != 64:
                errors.append(f"READY_NARROW_ICLR source artifact missing/digest invalid:{key}")
    elif int(summary.get("paper_ready") or 0) != 0:
        errors.append("non-ready asset-first state must expose paper_ready=0")
    return sorted(set(errors))
