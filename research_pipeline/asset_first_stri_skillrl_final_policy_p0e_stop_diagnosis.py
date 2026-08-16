from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics
from collections import defaultdict
from typing import Any

ARMS = (
    "A_pristine",
    "B_displacement_clone",
    "C_identity_placebo",
    "D_exact_quotient",
)
EXPERIMENT_ID = "STRI-SKILLRL-FINAL-POLICY-COMPETENCY-P0E-20260816"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_action_divergence(a: list[str], b: list[str]) -> int | None:
    n = min(len(a), len(b))
    for idx in range(n):
        if a[idx] != b[idx]:
            return idx + 1
    if len(a) != len(b):
        return n + 1
    return None


def _arm_vs_a(groups: dict[str, dict[str, dict[str, Any]]], arm: str) -> dict[str, Any]:
    action_diff = 0
    response_diff = 0
    step_diff_nonzero = 0
    endpoint_diff = 0
    step_deltas: list[int] = []
    first_divergences: list[int] = []
    successful_action_diff = 0
    failed_action_diff = 0
    successful_response_diff = 0
    failed_response_diff = 0
    successful_n = 0
    failed_n = 0
    successful_outcome_equivalent_divergences: list[dict[str, Any]] = []

    for unit_id, g in groups.items():
        a, x = g["A_pristine"], g[arm]
        ad = a["projected_actions_sha256"] != x["projected_actions_sha256"]
        rd = a["response_sha256s"] != x["response_sha256s"]
        ed = int(a["won"]) != int(x["won"])
        delta = int(x["steps"]) - int(a["steps"])
        fd = _first_action_divergence(list(a["projected_actions"]), list(x["projected_actions"]))
        action_diff += int(ad)
        response_diff += int(rd)
        endpoint_diff += int(ed)
        step_diff_nonzero += int(delta != 0)
        step_deltas.append(delta)
        if fd is not None:
            first_divergences.append(fd)
        if int(a["won"]) == 1:
            successful_n += 1
            successful_action_diff += int(ad)
            successful_response_diff += int(rd)
            if ad and int(x["won"]) == 1:
                successful_outcome_equivalent_divergences.append({
                    "unit_id": unit_id,
                    "task_family": a["task_family"],
                    "first_action_divergence_step": fd,
                    "A_steps": a["steps"],
                    "arm_steps": x["steps"],
                })
        else:
            failed_n += 1
            failed_action_diff += int(ad)
            failed_response_diff += int(rd)

    n = len(groups)
    return {
        "units": n,
        "response_sequence_disagreement": response_diff,
        "response_sequence_disagreement_rate": response_diff / n,
        "projected_action_sequence_disagreement": action_diff,
        "projected_action_sequence_disagreement_rate": action_diff / n,
        "step_count_difference_nonzero": step_diff_nonzero,
        "step_count_difference_nonzero_rate": step_diff_nonzero / n,
        "mean_step_delta": sum(step_deltas) / n,
        "step_delta_range": [min(step_deltas), max(step_deltas)],
        "first_action_divergence_count": len(first_divergences),
        "first_action_divergence_median_step": statistics.median(first_divergences) if first_divergences else None,
        "first_action_divergence_range": [min(first_divergences), max(first_divergences)] if first_divergences else None,
        "endpoint_disagreement": endpoint_diff,
        "successful_stratum": {
            "n": successful_n,
            "action_sequence_disagreement": successful_action_diff,
            "response_sequence_disagreement": successful_response_diff,
            "endpoint_disagreement": sum(
                int(g["A_pristine"]["won"]) != int(g[arm]["won"])
                for g in groups.values()
                if int(g["A_pristine"]["won"]) == 1
            ),
            "successful_outcome_equivalent_action_divergences": successful_outcome_equivalent_divergences,
        },
        "failed_stratum": {
            "n": failed_n,
            "action_sequence_disagreement": failed_action_diff,
            "response_sequence_disagreement": failed_response_diff,
            "endpoint_disagreement": sum(
                int(g["A_pristine"]["won"]) != int(g[arm]["won"])
                for g in groups.values()
                if int(g["A_pristine"]["won"]) == 0
            ),
        },
    }


def diagnose(
    *,
    project: pathlib.Path,
    calibration_analysis: pathlib.Path,
    causal_aggregate: pathlib.Path,
    causal_analysis: pathlib.Path,
) -> dict[str, Any]:
    contract = project / "generated/asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json"
    panel = project / "generated/asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json"
    model_manifest = project / "generated/asset-first-stri-skillrl-final-policy-p0e-model-manifest-20260816.json"
    pre_review = project / "generated/asset-first-stri-skillrl-final-policy-p0e-review-20260816.json"
    p0d_dead_end = project / "generated/asset-first-stri-skillrl-p0d-dead-end-diagnosis-20260816.json"
    narrow_design = project / "generated/asset-first-stri-narrow-paper-design-20260816.json"
    final_state = project / "generated/asset-first-stri-iclr2027-final-state-20260816.json"

    cal = load(calibration_analysis)
    agg = load(causal_aggregate)
    ana = load(causal_analysis)
    if cal.get("outcome") != "GO_COMPETENT_POLICY_SUPPORT" or cal.get("qualified_support") is not True:
        raise ValueError("calibration-not-qualified-go")
    if agg.get("status") != "COMPLETE" or agg.get("completed_units") != 24 or agg.get("rows") != 96:
        raise ValueError("causal-aggregate-not-complete")
    if ana.get("outcome") != "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" or ana.get("qualified") is not True:
        raise ValueError("causal-analysis-not-qualified-stop")
    if ana.get("qualification_errors"):
        raise ValueError("qualified-stop-has-qualification-errors")

    raw = pathlib.Path(str(agg["raw_rows_path"]))
    rows = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines() if line.strip()]
    groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        groups[str(row["unit_id"])][str(row["arm"])] = row
    if len(groups) != 24 or any(set(g) != set(ARMS) for g in groups.values()):
        raise ValueError("paired-unit-integrity")

    B = _arm_vs_a(groups, "B_displacement_clone")
    C = _arm_vs_a(groups, "C_identity_placebo")
    D = _arm_vs_a(groups, "D_exact_quotient")
    b_vs_c_action = sum(
        g["B_displacement_clone"]["projected_actions_sha256"] != g["C_identity_placebo"]["projected_actions_sha256"]
        for g in groups.values()
    )
    b_vs_c_response = sum(
        g["B_displacement_clone"]["response_sha256s"] != g["C_identity_placebo"]["response_sha256s"]
        for g in groups.values()
    )
    b_vs_c_steps = sum(
        int(g["B_displacement_clone"]["steps"]) != int(g["C_identity_placebo"]["steps"])
        for g in groups.values()
    )

    family = defaultdict(lambda: {"units": 0, "A_success": 0, "B_action_diff": 0, "C_action_diff": 0})
    for g in groups.values():
        f = str(g["A_pristine"]["task_family"])
        family[f]["units"] += 1
        family[f]["A_success"] += int(g["A_pristine"]["won"])
        family[f]["B_action_diff"] += int(g["A_pristine"]["projected_actions_sha256"] != g["B_displacement_clone"]["projected_actions_sha256"])
        family[f]["C_action_diff"] += int(g["A_pristine"]["projected_actions_sha256"] != g["C_identity_placebo"]["projected_actions_sha256"])

    narrow = load(narrow_design)
    final = load(final_state)
    current_claim_ids = [str(x.get("id")) for x in narrow.get("submission_claims") or []]
    if current_claim_ids != ["N1", "N2", "N3"]:
        raise ValueError(f"unexpected-current-claim-scope:{current_claim_ids}")
    if "downstream utility harm" not in [str(x) for x in final.get("claims_forbidden") or []]:
        raise ValueError("final-paper-does-not-forbid-downstream-harm")

    metrics = ana["metrics"]
    payload = {
        "schema_version": "1.0",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "experiment_id": EXPERIMENT_ID,
        "artifact_kind": "qualified-true-negative-principled-dead-end-diagnosis",
        "disposition": "QUALIFIED_TRUE_NEGATIVE_ENDPOINT_BRIDGE",
        "diagnosis_layers": ["semantic-specificity-collapse", "endpoint-transport-failure"],
        "scientific_belief_update_allowed": True,
        "belief_update_scope": "Reject only C4 exact-clone downstream final-success transport under the single author final RL policy and frozen ALFWorld panel. N1/N2/N3 static STRI claims remain unchanged.",
        "mechanism_rejected": False,
        "c4_endpoint_bridge_rejected": True,
        "stage2_confirmation_locked": True,
        "scale_up_allowed": False,
        "frozen_control_receipts": {
            "pre_outcome_freeze_commit": "8b7714c719c6d6f4271ec8b588c1aca212c25099",
            "contract_sha256": sha(contract),
            "panel_sha256": sha(panel),
            "model_manifest_sha256": sha(model_manifest),
            "independent_pre_execution_review_sha256": sha(pre_review),
            "p0d_dead_end_sha256": sha(p0d_dead_end),
        },
        "evidence_receipts": {
            "calibration_analysis_path": str(calibration_analysis),
            "calibration_analysis_sha256": sha(calibration_analysis),
            "calibration_evidence_manifest_sha256": cal.get("evidence_manifest_sha256"),
            "causal_aggregate_path": str(causal_aggregate),
            "causal_aggregate_sha256": sha(causal_aggregate),
            "causal_raw_path": str(raw),
            "causal_raw_sha256": sha(raw),
            "causal_analysis_path": str(causal_analysis),
            "causal_analysis_sha256": sha(causal_analysis),
            "causal_evidence_manifest_sha256": ana.get("evidence_manifest_sha256"),
        },
        "qualification": {
            "calibration_outcome": cal.get("outcome"),
            "calibration_pristine_success": cal.get("metrics", {}).get("pristine_success_count"),
            "calibration_pristine_success_rate": cal.get("metrics", {}).get("pristine_success_rate"),
            "calibration_success_family_count": cal.get("metrics", {}).get("families_with_success_count"),
            "causal_qualified": ana.get("qualified"),
            "causal_qualification_errors": ana.get("qualification_errors"),
            "paired_units": agg.get("completed_units"),
            "arm_episodes": agg.get("rows"),
            "gpu_hours": agg.get("gpu_hours"),
            "within_budget": agg.get("within_budget"),
        },
        "endpoint_result": {
            "formal_outcome": ana.get("outcome"),
            "success_rate": metrics.get("success_rate"),
            "B_vs_A_mcnemar_p": metrics.get("B_vs_A_mcnemar_p"),
            "paired_disagreement": metrics.get("paired_disagreement"),
            "B_vs_A_disagreement_minus_C_vs_A": metrics.get("B_vs_A_disagreement_minus_C_vs_A"),
            "family_replicated_flip_count": metrics.get("family_replicated_flip_count"),
            "families_with_B_vs_A_flip": metrics.get("families_with_B_vs_A_flip"),
        },
        "trajectory_result": {
            "B_displacement_clone_vs_A": B,
            "C_identity_placebo_vs_A": C,
            "D_exact_quotient_vs_A": D,
            "B_vs_C": {
                "projected_action_sequence_disagreement": b_vs_c_action,
                "response_sequence_disagreement": b_vs_c_response,
                "step_count_difference_nonzero": b_vs_c_steps,
            },
            "by_family": dict(sorted(family.items())),
        },
        "principled_interpretation": {
            "treatment_manipulation_reached_behavior": True,
            "evidence": "B changes response sequences in 23/24 and projected action sequences in 11/24 units, with median first action divergence at step 7, while endpoint disagreement remains 0/24.",
            "semantic_specificity_supported": False,
            "semantic_specificity_reason": "Identity placebo C changes projected action sequences in 15/24 units, more often than B (11/24), yet also has 0/24 endpoint disagreement. Thus trajectory sensitivity is not specific to semantic displacement.",
            "endpoint_transport_supported": False,
            "endpoint_transport_reason": "A/B/C/D all achieve 18/24 final success with zero endpoint disagreement despite substantial B/C trajectory divergence. In successful A units, B has 5 and C has 9 action-trajectory divergences with the same successful endpoint. This identifies terminal paired equivalence under the perturbations, not a specific active-recovery mechanism.",
            "exact_quotient_restoration_supported": True,
            "exact_quotient_reason": "D has zero response, action, step-count, or endpoint disagreement with A on all 24 units.",
            "strongest_opposite_cause": "The same-information identity placebo shows that generic fresh-identity/order/prompt perturbation is sufficient to induce trajectory variance at least as strongly as semantic displacement, while terminal outcomes remain paired-equivalent. The experiment does not distinguish whether that endpoint equivalence arises from prompt-conditioned policy sensitivity, multiple task-successful action paths, environmental redundancy, active recovery, or a mixture of these mechanisms.",
        },
        "paper_scope_effect": {
            "current_submission_claims": current_claim_ids,
            "current_submission_unchanged": True,
            "reason": "The frozen narrow STRI design explicitly bounds N1-N3 to control-plane representation sensitivity and exact support geometry, lists C4 as optional/non-rescuing, and forbids downstream utility-harm claims.",
            "current_final_state_status": final.get("status"),
            "new_gpu_evidence_required_for_current_claim_scope": final.get("new_gpu_evidence_required_for_current_claim_scope"),
        },
        "forbidden_repairs": [
            "run Stage-2 confirmation after local STOP",
            "add seeds until B-vs-A becomes significant",
            "select easier or more displacement-sensitive tasks after outcomes",
            "switch to another policy/checkpoint after outcomes",
            "relax the preregistered endpoint GO/STOP thresholds",
            "replace final success with post-hoc trajectory divergence and call C4 rescued",
            "reinterpret generic placebo-dominated trajectory sensitivity as semantic-displacement-specific evidence",
        ],
        "allowed_next_step": "Layered post-negative differential diagnosis and novelty/reduction review. Any surviving trajectory/equifinality question must be a new paper contract with a new scientific estimand, not a repair of C4.",
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--calibration-analysis", type=pathlib.Path, required=True)
    ap.add_argument("--causal-aggregate", type=pathlib.Path, required=True)
    ap.add_argument("--causal-analysis", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = diagnose(
        project=a.project,
        calibration_analysis=a.calibration_analysis,
        causal_aggregate=a.causal_aggregate,
        causal_analysis=a.causal_analysis,
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
