from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def subset(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {k: d.get(k) for k in keys}


def run(project: pathlib.Path) -> dict[str, Any]:
    root = project / "generated/research-data/runs/stri-skillrl-final-policy-p0e-postnegative-20260817"
    diagnosis = project / "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
    screen = project / "generated/asset-first-stri-skillrl-final-policy-p0e-same-information-screen-20260817.json"
    stat = project / "generated/asset-first-stri-skillrl-final-policy-p0e-statistical-resolution-audit-20260817.json"
    files = {
        "design_critic": root / "doubao-v2.review.json",
        "principle_falsifier": root / "deepseek-v2.review.json",
        "operationalization_current_source": root / "web-current-source.review.json",
        "principle_advocate": root / "principle-advocate-compact.review.json",
        "meta_adjudicator": root / "meta-adjudicator-v2.review.json",
    }
    rows = {k: load(v) for k, v in files.items()}
    dsha, ssha = sha(diagnosis), sha(screen)
    for role in ("design_critic", "principle_falsifier", "principle_advocate"):
        if rows[role].get("reviewed_diagnosis_sha256") != dsha:
            raise ValueError(f"stale-{role}")
    if rows["principle_advocate"].get("reviewed_same_information_screen_sha256") != ssha:
        raise ValueError("stale-principle-advocate-screen")
    meta_inputs = rows["meta_adjudicator"].get("input_receipts") or {}
    if (meta_inputs.get("diagnosis") or {}).get("sha256") != dsha or (meta_inputs.get("screen") or {}).get("sha256") != ssha:
        raise ValueError("stale-meta")

    web = rows["operationalization_current_source"]
    stat_payload = load(stat)
    if web.get("new_problem_verdict") != "NO_NEW_PROBLEM":
        raise ValueError("web-new-problem-not-reduced")
    if stat_payload.get("persistent_principle_dead_end_statistically_certified") is not False:
        raise ValueError("stat-dead-end-not-blocked")

    role_payloads = {
        "design_critic": {
            "source_sha256": sha(files["design_critic"]),
            **subset(rows["design_critic"], ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "strongest_alternative_explanation", "strongest_reduction_of_candidate", "reviewer_model"]),
        },
        "operationalization_critic_current_source": {
            "source_sha256": sha(files["operationalization_current_source"]),
            **subset(web, ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "strongest_alternative_explanation", "strongest_reduction_of_candidate", "required_revision_to_diagnosis"]),
            "revision_applied_in_current_diagnosis": "does not distinguish" in str(load(diagnosis).get("principled_interpretation", {}).get("strongest_opposite_cause") or ""),
            "collision_sources": list(web.get("collision_sources") or []),
        },
        "principle_falsifier": {
            "source_sha256": sha(files["principle_falsifier"]),
            **subset(rows["principle_falsifier"], ["verdict", "confidence", "primary_failure_layer", "new_problem_verdict", "strongest_alternative_explanation", "strongest_reduction_of_candidate", "reviewer_model"]),
        },
        "principle_advocate": {
            "source_sha256": sha(files["principle_advocate"]),
            **subset(rows["principle_advocate"], ["verdict", "confidence", "strongest_case_against_dead_end", "is_that_case_supported_by_current_evidence", "specific_missing_precondition_if_any", "does_same_information_placebo_absorb_semantic_specificity", "does_zero_endpoint_disagreement_validly_reject_registered_endpoint_transport", "is_any_allowed_non_rescue_explanation_sufficient_to_keep_the_scoped_prediction_unresolved", "reviewer_model"]),
        },
        "meta_adjudicator": {
            "source_sha256": sha(files["meta_adjudicator"]),
            **subset(rows["meta_adjudicator"], ["verdict", "confidence", "checks", "dead_end_scope", "counter_explanation_type", "current_paper_effect", "new_problem_disposition", "required_revision", "reviewer_model"]),
            "numeric_reason_source_of_truth": "generated/asset-first-stri-skillrl-final-policy-p0e-statistical-resolution-audit-20260817.json",
            "normalization_note": "The meta review repeated the advocate's imprecise phrase 'maximum possible discordant pairs is 6'. Canonical synthesis instead uses the deterministic audit: 6 is the minimum unidirectional discordance count needed for two-sided exact McNemar p<0.05; the 3/24=0.125 registered effect floor itself gives p=0.25 under best-case directionality.",
        },
    }
    return {
        "schema_version": "1.0",
        "artifact_kind": "portable-five-role-post-negative-review-panel",
        "experiment_id": "STRI-SKILLRL-FINAL-POLICY-COMPETENCY-P0E-20260816",
        "inputs": {
            "diagnosis_sha256": dsha,
            "same_information_screen_sha256": ssha,
            "statistical_resolution_audit_sha256": sha(stat),
        },
        "role_policy": ["design-critic", "operationalization-critic", "principle-advocate", "principle-falsifier", "meta-adjudicator"],
        "roles": role_payloads,
        "failed_or_nonvoting_attempts": [
            {"requested": "glm-5.2/glm-5.3 post-negative review", "disposition": "NONVOTING_LENGTH_TRUNCATION"},
            {"requested": "kimi-k3 large-context principle advocate", "disposition": "NONVOTING_NETWORK_TIMEOUT"},
            {"requested": "deepseek-v4-flash large-context principle advocate", "disposition": "NONVOTING_REASONING_LENGTH_TRUNCATION"},
            {"requested": "minimax-m3 large-context meta-adjudicator", "disposition": "NONVOTING_REASONING_LENGTH_TRUNCATION"},
        ],
        "consensus": {
            "experimental_STOP_FIXED_POLICY_DYNAMIC_BRIDGE_valid": True,
            "semantic_specificity_failure_layer_supported": True,
            "endpoint_transport_failure_layer_supported_as_sample_level_STOP": True,
            "active_recovery_mechanism_identified": False,
            "same_information_trajectory_residual_survives": False,
            "persistent_principle_dead_end_certified": False,
            "principle_layer_disposition": "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED",
            "reason_dead_end_not_certified": "No preregistered equivalence/effect-margin plus task-cluster power/inference plan establishes persistent population-level dead-end resolution.",
            "broader_STRI_N1_N2_N3_unchanged": True,
            "stage2_locked": True,
            "new_gpu_authorized": False,
            "new_problem_disposition": "NO_NEW_PROBLEM_AFTER_CURRENT_SOURCE_AND_SAME_INFORMATION_REDUCTION",
        },
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = run(a.project)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
