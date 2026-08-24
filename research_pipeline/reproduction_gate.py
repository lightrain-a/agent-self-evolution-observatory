from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "reproduction_is_required_only_when_implementation_is_decisive_for_novelty": True,
    "minimal_sufficient_verification_precedes_full_retraining": True,
    "source_inspection_may_close_structural_questions_but_not_empirical_performance_questions": True,
    "missing_source_faithful_assets_is_support_hold_not_scientific_negative": True,
    "local_substitutes_cannot_silently_change_the_scientific_object": True,
    "reproduction_receipt_has_zero_scientific_authority": True,
    "reproduction_score_cannot_authorize_problem_method_experiment_p0_or_gpu": True,
}

VALID_MODES = {"SOURCE_INSPECTION", "MINIMAL_EXECUTION", "FULL_REPLICATION"}


def build_reproduction_contract(
    *, candidate_id: str, implementation_decisive_for_novelty: bool,
    paper_ref: str = "", implementation_ref: str = "", question: str = "",
    minimal_target: str = "", verification_mode: str = "SOURCE_INSPECTION",
    source_faithful_assets_available: bool | None = None,
    artifact_refs: list[str] | None = None, result: str = "",
    full_retraining_required: bool = False, reason: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": str(candidate_id),
        "implementation_decisive_for_novelty": bool(implementation_decisive_for_novelty),
        "paper_ref": str(paper_ref),
        "implementation_ref": str(implementation_ref),
        "question": str(question),
        "minimal_target": str(minimal_target),
        "verification_mode": str(verification_mode).upper(),
        "source_faithful_assets_available": source_faithful_assets_available,
        "artifact_refs": [str(x) for x in (artifact_refs or []) if str(x)],
        "result": str(result).upper(),
        "full_retraining_required": bool(full_retraining_required),
        "reason": str(reason),
        "scientific_authority": False,
        "problem_gate_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def evaluate_reproduction_contract(contract: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    decisive = contract.get("implementation_decisive_for_novelty") is True
    if not decisive:
        status = "NOT_REQUIRED"
    else:
        for key in ("paper_ref", "question", "minimal_target"):
            if not str(contract.get(key) or "").strip():
                blockers.append(f"missing:{key}")
        mode = str(contract.get("verification_mode") or "").upper()
        if mode not in VALID_MODES:
            blockers.append("invalid-verification-mode")
        if contract.get("full_retraining_required") is True and mode != "FULL_REPLICATION":
            blockers.append("full-retraining-flag-requires-full-replication-mode")
        available = contract.get("source_faithful_assets_available")
        result = str(contract.get("result") or "").upper()
        refs = [str(x) for x in contract.get("artifact_refs") or [] if str(x)]
        if available is False:
            status = "HOLD_SOURCE_FAITHFUL_ASSETS_UNAVAILABLE"
        elif blockers:
            status = "HOLD_REPRODUCTION_REQUIRED"
        elif available is not True:
            status = "HOLD_REPRODUCTION_REQUIRED"
        elif not refs:
            status = "HOLD_REPRODUCTION_REQUIRED"
        elif result == "SHARPENED_BOUNDARY":
            status = "REPRODUCTION_SHARPENED_BOUNDARY"
        elif result == "CONFIRMED_PAPER_ONLY_BOUNDARY":
            status = "REPRODUCTION_CONFIRMED_PAPER_ONLY_BOUNDARY"
        else:
            status = "HOLD_REPRODUCTION_REQUIRED"
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": contract.get("candidate_id"),
        "status": status,
        "blockers": blockers,
        "required_for_problem_qualification": decisive,
        "qualification_satisfied": status in {"NOT_REQUIRED", "REPRODUCTION_SHARPENED_BOUNDARY", "REPRODUCTION_CONFIRMED_PAPER_ONLY_BOUNDARY"},
        "support_hold": status == "HOLD_SOURCE_FAITHFUL_ASSETS_UNAVAILABLE",
        "machine_actionable": False,
        "scientific_authority": False,
        "problem_gate_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def reproduction_from_candidate(candidate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = candidate.get("closest_work_reproduction")
    if not isinstance(raw, dict):
        contract = build_reproduction_contract(
            candidate_id=str(candidate.get("candidate_id") or candidate.get("id") or ""),
            implementation_decisive_for_novelty=False,
        )
    else:
        contract = build_reproduction_contract(
            candidate_id=str(candidate.get("candidate_id") or candidate.get("id") or ""),
            implementation_decisive_for_novelty=raw.get("implementation_decisive_for_novelty") is True,
            paper_ref=str(raw.get("paper_ref") or ""),
            implementation_ref=str(raw.get("implementation_ref") or ""),
            question=str(raw.get("question") or ""),
            minimal_target=str(raw.get("minimal_target") or ""),
            verification_mode=str(raw.get("verification_mode") or "SOURCE_INSPECTION"),
            source_faithful_assets_available=raw.get("source_faithful_assets_available"),
            artifact_refs=list(raw.get("artifact_refs") or []),
            result=str(raw.get("result") or ""),
            full_retraining_required=raw.get("full_retraining_required") is True,
            reason=str(raw.get("reason") or ""),
        )
    return contract, evaluate_reproduction_contract(contract)


def run_three_case_local_falsifier(project_root: Path) -> dict[str, Any]:
    cases: list[tuple[str, dict[str, Any], str]] = []

    skillsp_path = project_root / "generated" / "skillsp-bootstrap-gap-principle-readjudication-20260817.json"
    skillsp = json.loads(skillsp_path.read_text(encoding="utf-8"))
    skill_counter = ((skillsp.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    skill_refs = [str(x) for x in skill_counter.get("evidence_refs") or []]
    cases.append(("skillsp-bootstrap", build_reproduction_contract(
        candidate_id=str(skillsp.get("candidate_id") or "SKILLSP"),
        implementation_decisive_for_novelty=True,
        paper_ref="arXiv:2607.22529",
        implementation_ref=next((x for x in skill_refs if x.startswith("first-party-repo:")), ""),
        question="Do the compared arms assign the same constraint-construction responsibility to the model and scaffold?",
        minimal_target="Inspect the released logical-generation path and freeze who constructs hidden solutions, clues, constraints, and uniqueness checks.",
        verification_mode="SOURCE_INSPECTION",
        source_faithful_assets_available=bool(any(x.startswith("first-party-repo:") for x in skill_refs)),
        artifact_refs=[str(skillsp_path.relative_to(project_root))] + skill_refs[:4],
        result="SHARPENED_BOUNDARY" if skill_counter.get("same_information_reduction_verified") is True else "",
        reason=str(skill_counter.get("statement") or ""),
    ), "REPRODUCTION_SHARPENED_BOUNDARY"))

    comfy_path = project_root / "generated" / "comfyclaw-prompt-only-refinement-principle-readjudication-20260818.json"
    comfy = json.loads(comfy_path.read_text(encoding="utf-8"))
    comfy_counter = ((comfy.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    comfy_refs = [str(x) for x in comfy_counter.get("evidence_refs") or []]
    cases.append(("comfyclaw-action-surface", build_reproduction_contract(
        candidate_id=str(comfy.get("candidate_id") or "COMFYCLAW"),
        implementation_decisive_for_novelty=True,
        paper_ref="arXiv:2607.01709",
        implementation_ref="primary/source implementation evidence",
        question="Is the closed-loop treatment actually prompt-only, or does it expose a richer executable workflow-edit surface?",
        minimal_target="Verify the intervention surface and localized verifier feedback before attributing the prompt-only gap to a new evolution mechanism.",
        verification_mode="SOURCE_INSPECTION",
        source_faithful_assets_available=bool(comfy_refs),
        artifact_refs=[str(comfy_path.relative_to(project_root))] + comfy_refs[:4],
        result="SHARPENED_BOUNDARY" if comfy_counter.get("counter_prediction_observed") is True else "",
        reason=str(comfy_counter.get("statement") or ""),
    ), "REPRODUCTION_SHARPENED_BOUNDARY"))

    lopd_path = project_root / "generated" / "lopd-fixed-budget-continuation-hold-20260818.json"
    lopd = json.loads(lopd_path.read_text(encoding="utf-8"))
    diag = lopd.get("support_diagnosis") or {}
    release = lopd.get("release_audit") or {}
    cases.append(("lopd-fixed-budget", build_reproduction_contract(
        candidate_id=str(lopd.get("candidate_id") or "LOPD"),
        implementation_decisive_for_novelty=True,
        paper_ref=str(lopd.get("primary_ref") or ""),
        implementation_ref=str(release.get("official_repository") or ""),
        question="Can fixed J*K decomposition arms be instantiated with the source-faithful trained compressor object?",
        minimal_target=str((lopd.get("memory_projection") or {}).get("required_unit") or "source-faithful fixed-budget arms"),
        verification_mode="MINIMAL_EXECUTION",
        source_faithful_assets_available=diag.get("source_faithful_execution_available") is True,
        artifact_refs=[str(lopd_path.relative_to(project_root))],
        result="",
        reason=str(diag.get("reason") or ""),
    ), "HOLD_SOURCE_FAITHFUL_ASSETS_UNAVAILABLE"))

    results = []
    matches = 0
    for name, contract, expected in cases:
        audit = evaluate_reproduction_contract(contract)
        match = audit.get("status") == expected
        matches += int(match)
        results.append({"case": name, "expected": expected, "status": audit.get("status"), "match": match, "scientific_authority": False})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if matches == len(cases) else "FAIL",
        "cases": len(cases),
        "matched": matches,
        "results": results,
        "full_retraining_cases": sum(contract.get("verification_mode") == "FULL_REPLICATION" for _, contract, _ in cases),
        "scientific_authority": False,
    }


def build_reproduction_gate_state(project_root: Path) -> dict[str, Any]:
    replay = run_three_case_local_falsifier(project_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "REPRODUCTION_GATE_INSTALLED" if replay.get("status") == "PASS" else "REPRODUCTION_GATE_REPLAY_FAILED",
        "policy": dict(POLICY),
        "local_falsifier": replay,
        "summary": {
            "local_cases": int(replay.get("cases") or 0),
            "matched_cases": int(replay.get("matched") or 0),
            "full_retraining_cases": int(replay.get("full_retraining_cases") or 0),
            "automatic_scientific_authority": 0,
        },
        "scientific_authority": False,
    }
