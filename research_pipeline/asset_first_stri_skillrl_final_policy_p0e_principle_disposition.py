from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

from research_pipeline.failure_asset_library import build_failure_asset_library
from research_pipeline.principle_adjudication import (
    COMMON_FAILURE_UPDATE_RULES,
    COMMON_FALSIFICATION_REQUIRES,
    adjudicate_experiment_evidence,
    audit_principle_certificate,
)

PRINCIPLE_ID = "stri-c4-exact-clone-final-success-transport-v1"
PREDICTION_ID = "C4-ENDPOINT-TRANSPORT"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def certificate_config() -> dict[str, Any]:
    return {
        "pre_experiment": {
            "principle_certificate": {
                "principle_id": PRINCIPLE_ID,
                "primitives": [
                    "semantic-displacement treatment under fixed-budget SkillRL retrieval",
                    "same-information fresh-identity placebo",
                    "exact semantic quotient negative control",
                    "paired ALFWorld terminal success",
                ],
                "mechanism": "If the exact-clone semantic representation change has a semantic-specific downstream consequence under the fixed author final RL policy, B should alter paired terminal success beyond identity placebo C, while D should restore A.",
                "scope_conditions": [
                    "Jianwen/Alfworld-7B-RL at revision 2ce16cb90e6357892dde201928279d4513d35c59",
                    "frozen P0-E local_causal valid_unseen panel: 12 tasks x 2 decode seeds",
                    "B exact-content fresh-ID displacement, C exact-content identity placebo, D exact semantic quotient",
                    "final ALFWorld won is the endpoint truth",
                ],
                "assumptions": [
                    {"id": "A-support", "statement": "The reference final RL policy supplies non-degenerate endpoint support.", "observable_check": "Stage-0 competence calibration is GO with 18/24 success across >=3 families."},
                    {"id": "A-treatment", "statement": "B changes semantic retrieval support while C changes prompt identity without changing the semantic set.", "observable_check": "Representation replay and local-unit invariants validate B/C."},
                    {"id": "A-quotient", "statement": "D restores A representation and stochastic realization.", "observable_check": "A/D prompt identity plus response coupling yields 24/24 exact trajectories."},
                    {"id": "A-truth", "statement": "ALFWorld won is independent endpoint truth.", "observable_check": "Endpoint is environment info.won."},
                ],
                "predictions": [
                    {"id": PREDICTION_ID, "role": "mechanism-test", "statement": "On a qualified run, B should produce a semantic-specific terminal-success effect beyond C under the preregistered GO rule, while D remains A-equivalent.", "observable": "Paired A/B/C/D ALFWorld won across 24 frozen local units."},
                    {"id": "C4-QUOTIENT-RESTORATION", "role": "boundary-test", "statement": "Exact quotienting D should restore A trajectory and endpoint.", "observable": "A/D prompt-response-action-step-outcome equality."},
                ],
                "operationalization": [
                    {"concept": "semantic-specific treatment", "measure": "B semantic-set displacement relative to A", "validity_check": "B semantic set differs from A and C semantic set equals A on every unit."},
                    {"concept": "matched identity nuisance", "measure": "C prompt/identity perturbation with unchanged semantic set", "validity_check": "C changes prompt identity without semantic-set change."},
                    {"concept": "downstream transport", "measure": "paired final-success disagreement and success-rate contrast", "validity_check": "Stage-0 competence GO and environment won truth."},
                    {"concept": "exact restoration", "measure": "D versus A full trajectory and endpoint equality", "validity_check": "24/24 realized equality."},
                ],
                "falsification": {
                    "prediction_ids": [PREDICTION_ID],
                    "requires": list(COMMON_FALSIFICATION_REQUIRES),
                    "contradiction_rule": "A qualified run may STOP the registered experimental realization under the frozen STOP gate. Persistent principle-dead-end certification additionally requires preregistered statistical resolution/equivalence adequate for the population-level claim.",
                },
                "failure_update_rules": dict(COMMON_FAILURE_UPDATE_RULES),
            }
        }
    }


def run(project: pathlib.Path, diagnosis_path: pathlib.Path, screen_path: pathlib.Path, stat_path: pathlib.Path, review_panel_path: pathlib.Path) -> dict[str, Any]:
    diagnosis, screen, stat, review_panel = map(load, (diagnosis_path, screen_path, stat_path, review_panel_path))
    if diagnosis.get("disposition") != "QUALIFIED_TRUE_NEGATIVE_ENDPOINT_BRIDGE":
        raise ValueError("diagnosis-not-qualified-experimental-stop")
    if screen.get("verdict") != "NO_SEMANTIC_SPECIFIC_TRAJECTORY_RESIDUAL_IN_SIMPLE_SAME_INFORMATION_SCREEN":
        raise ValueError("same-information-screen-not-reduced")
    if stat.get("persistent_principle_dead_end_statistically_certified") is not False:
        raise ValueError("statistical-resolution-does-not-block-dead-end")
    if stat.get("experimental_stop_rule_valid") is not True:
        raise ValueError("experimental-stop-not-valid")
    inputs = review_panel.get("inputs") or {}
    if inputs.get("diagnosis_sha256") != sha(diagnosis_path) or inputs.get("same_information_screen_sha256") != sha(screen_path) or inputs.get("statistical_resolution_audit_sha256") != sha(stat_path):
        raise ValueError("portable-review-panel-content-address-mismatch")
    consensus = review_panel.get("consensus") or {}
    required_consensus = {
        "experimental_STOP_FIXED_POLICY_DYNAMIC_BRIDGE_valid": True,
        "persistent_principle_dead_end_certified": False,
        "principle_layer_disposition": "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED",
        "broader_STRI_N1_N2_N3_unchanged": True,
        "stage2_locked": True,
        "new_gpu_authorized": False,
        "new_problem_disposition": "NO_NEW_PROBLEM_AFTER_CURRENT_SOURCE_AND_SAME_INFORMATION_REDUCTION",
    }
    for key, expected in required_consensus.items():
        if consensus.get(key) != expected:
            raise ValueError(f"portable-review-panel-consensus:{key}")

    cert = audit_principle_certificate(certificate_config())
    if cert.get("passed") is not True:
        raise ValueError("principle-certificate-invalid:" + ",".join(cert.get("blockers") or []))

    # The experimental realization is a valid STOP, but the principle-level falsifier
    # is deliberately NOT marked triggered because no preregistered equivalence/power
    # plan established population-level dead-end resolution.
    evidence = {
        "registered_prediction_id": PREDICTION_ID,
        "assumptions_hold": True,
        "scope_conditions_hold": True,
        "operationalization_valid": True,
        "experiment_identifiable": True,
        "optimization_adequate": True,
        "independent_truth": True,
        "matched_baseline": True,
        "protocol_validity": True,
        "falsifier_triggered": False,
        "statistical_resolution_precondition": False,
        "omitted_condition_discovered": False,
        "assumption_violation_discovered": False,
    }
    adjudication = adjudicate_experiment_evidence("true-negative", cert, evidence)
    if adjudication.get("verdict") != "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED" or adjudication.get("dead_end_certified") is not False:
        raise ValueError("principle-layer-did-not-remain-unresolved:" + str(adjudication.get("verdict")))

    iteration = {
        "nodes": [{
            "idea_id": "skill-taxonomy-representation-invariance:C4-exact-clone-endpoint-transport",
            "diagnosis": "true-negative",
            "diagnosis_layer": "method-realization",
            "artifact_dir": str(pathlib.Path(str((diagnosis.get("evidence_receipts") or {})["causal_analysis_path"])).parent),
        }]
    }
    library = build_failure_asset_library(iteration, principle_layer={"adjudications": [adjudication]})
    if (library.get("summary") or {}).get("principle_dead_ends") != 0:
        raise ValueError("failure-library-incorrectly-certified-principle-dead-end")

    return {
        "schema_version": "1.0",
        "artifact_kind": "post-negative-scoped-principle-disposition",
        "principle_id": PRINCIPLE_ID,
        "principle_scope": "C4 exact-clone final-success transport only",
        "experimental_realization_disposition": "STOP_FIXED_POLICY_DYNAMIC_BRIDGE",
        "experimental_stop_valid": True,
        "persistent_principle_dead_end_certified": False,
        "principle_disposition": "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED",
        "reason": "The frozen experiment validly STOPs this C4 realization and same-information trajectory residuals do not survive C placebo, but the design did not preregister statistical equivalence/power/cluster resolution sufficient for persistent population-level principle-dead-end certification.",
        "broader_STRI_N1_N2_N3_unchanged": True,
        "stage2_confirmation_locked": True,
        "new_problem_disposition": "NO_NEW_PROBLEM_AFTER_CURRENT_SOURCE_AND_SAME_INFORMATION_REDUCTION",
        "new_gpu_authorized": False,
        "receipts": {
            "diagnosis": {"path": str(diagnosis_path), "sha256": sha(diagnosis_path)},
            "same_information_screen": {"path": str(screen_path), "sha256": sha(screen_path)},
            "statistical_resolution_audit": {"path": str(stat_path), "sha256": sha(stat_path)},
            "portable_five_role_review_panel": {"path": str(review_panel_path), "sha256": sha(review_panel_path), "role_policy": review_panel.get("role_policy"), "consensus": consensus},
        },
        "principle_certificate_audit": cert,
        "principle_evidence": evidence,
        "principle_adjudication": adjudication,
        "failure_asset_library_snapshot": library,
        "reopen_condition": stat.get("reopen_condition"),
        "forbidden_repairs": diagnosis.get("forbidden_repairs"),
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--diagnosis", type=pathlib.Path, required=True)
    ap.add_argument("--screen", type=pathlib.Path, required=True)
    ap.add_argument("--statistical-audit", type=pathlib.Path, required=True)
    ap.add_argument("--review-panel", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = run(a.project, a.diagnosis, a.screen, a.statistical_audit, a.review_panel)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
