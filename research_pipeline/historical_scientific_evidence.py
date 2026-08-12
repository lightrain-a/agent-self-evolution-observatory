from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SOURCE = Path(__file__).with_name("paper_first_post_c2_evidence_20260812.json")
EXPECTED_F0_SHA256 = "d455869a34877fe3fd6c76d933cd2d6afa153d4bbd9813d71f89c5d16beafffe"
EXPECTED_DIAGNOSIS_SHA256 = "e82eaa2a217454d21279b1b97d7ab3e814f3c0d3963fb31f2baa791e9d1de6b1"

POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "historical_evidence_is_non_authorizing": True,
    "original_experiment_decision_is_immutable": True,
    "posthoc_evidence_cannot_be_relabelled_preregistered": True,
    "method_level_negative_does_not_auto_falsify_principle": True,
    "retrospective_principle_certificate_forbidden": True,
    "historical_scope_evidence_may_inform_future_prechecks": True,
    "cross_surface_evidence_cannot_rescue_closed_paper_or_method": True,
    "new_experiment_requires_fresh_paper_first_authority": True,
}


def _load_source() -> dict[str, Any]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def build_historical_scientific_evidence_registry() -> dict[str, Any]:
    authority = _load_source()
    scienceworld = authority.get("scienceworld_parent_evidence") or {}
    f0_sha = str(scienceworld.get("f0_sha256") or "")
    diagnosis_sha = str(scienceworld.get("diagnosis_sha256") or "")
    decision = str(scienceworld.get("f0_decision") or "")
    if f0_sha != EXPECTED_F0_SHA256:
        raise ValueError(f"ScienceWorld F0 provenance mismatch: {f0_sha}")
    if diagnosis_sha != EXPECTED_DIAGNOSIS_SHA256:
        raise ValueError(f"ScienceWorld diagnosis provenance mismatch: {diagnosis_sha}")
    if decision != "SYMMETRIC_F0_HOLD":
        raise ValueError(f"ScienceWorld frozen decision changed: {decision}")

    record = {
        "evidence_id": "scienceworld-correction-closure-decision-context-posthoc-v1",
        "experiment_id": "SCIENCEWORLD-CORRECTION-CLOSURE-SYMMETRIC-F0",
        "domain": "ScienceWorld",
        "phase": "F0",
        "original_decision": decision,
        "original_decision_preserved": True,
        "evidence_timing": "post-hoc",
        "evidence_class": "method-level-negative",
        "diagnosis": "post-hoc-omitted-condition",
        "affected_scientific_layer": "method-realization",
        "omitted_condition": "trajectory-conditioned policy decision-context closure",
        "scope_refinement": str(scienceworld.get("scope_refinement_candidate") or ""),
        "scope_refinement_recorded": True,
        "active_principle_belief_update_allowed": False,
        "principle_falsified": False,
        "retrospective_principle_certificate_allowed": False,
        "execution_authorized": False,
        "scale_up_authorized": False,
        "reusable_precheck": (
            "Before treating a persistent update, replay branch, or correction as behaviorally available, verify recurrence of the complete policy decision context "
            "(not observation/state alone) and verify that the intended state-action intervention is actually realized after the update changes the trajectory."
        ),
        "paper_relationship": {
            "paper_id": str(authority.get("paper_id") or "trajectory-mediated-memory-effect-transport"),
            "role": "cross-surface experimental-validity boundary evidence only",
            "can_rescue_closed_formulation": False,
            "can_reopen_closed_method": False,
            "can_authorize_new_paper_problem": False,
            "future_use": "precheck candidate for a fresh novelty/method/experiment-blueprint cycle only",
            "source_rule": str(scienceworld.get("cross_surface_rule") or ""),
        },
        "provenance": {
            "source_host": str(authority.get("source_host") or ""),
            "f0": {
                "path": str(scienceworld.get("f0_path") or ""),
                "sha256": f0_sha,
            },
            "posthoc_diagnosis": {
                "path": str(scienceworld.get("diagnosis_path") or ""),
                "sha256": diagnosis_sha,
            },
            "registry_source": "research_pipeline/paper_first_post_c2_evidence_20260812.json",
        },
        "authority_note": str(scienceworld.get("principle_authority") or ""),
    }
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "summary": {
            "records": 1,
            "posthoc_records": 1,
            "method_level_negative_records": 1,
            "active_principle_belief_updates": 0,
            "execution_authorized": 0,
        },
        "records": [record],
    }
