from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

OUTPUT = "generated/asset-first-stri-skillrl-final-policy-p0e-supplement-receipt-20260817.json"
CONTRACT = "generated/asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json"
PANEL = "generated/asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json"
MODEL_MANIFEST = "generated/asset-first-stri-skillrl-final-policy-p0e-model-manifest-static-20260816.json"
DIAGNOSIS = "generated/asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json"
SCREEN = "generated/asset-first-stri-skillrl-final-policy-p0e-same-information-screen-20260817.json"
STAT_AUDIT = "generated/asset-first-stri-skillrl-final-policy-p0e-statistical-resolution-audit-20260817.json"
PRINCIPLE = "generated/asset-first-stri-skillrl-final-policy-p0e-principle-disposition-20260817.json"

SOURCES = {
    "contract": CONTRACT,
    "panel": PANEL,
    "model_manifest": MODEL_MANIFEST,
    "qualified_stop_diagnosis": DIAGNOSIS,
    "same_information_screen": SCREEN,
    "statistical_resolution_audit": STAT_AUDIT,
    "principle_disposition": PRINCIPLE,
}


def _load(root: Path, rel: str) -> dict[str, Any]:
    value = json.loads((root / rel).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {rel}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_receipt(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    contract = _load(project_root, CONTRACT)
    panel = _load(project_root, PANEL)
    diagnosis = _load(project_root, DIAGNOSIS)
    screen = _load(project_root, SCREEN)
    stat = _load(project_root, STAT_AUDIT)
    principle = _load(project_root, PRINCIPLE)

    qual = diagnosis.get("qualification") or {}
    endpoint = diagnosis.get("endpoint_result") or {}
    trajectory = diagnosis.get("trajectory_result") or {}
    btraj = trajectory.get("B_displacement_clone_vs_A") or {}
    ctraj = trajectory.get("C_identity_placebo_vs_A") or {}
    dtraj = trajectory.get("D_exact_quotient_vs_A") or {}

    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "artifact_kind": "anonymous-sanitized-skillrl-p0e-receipt",
        "experiment_id": str(diagnosis.get("experiment_id") or ""),
        "role": "Optional C4 downstream-boundary evidence only; N1-N3 remain the paper claims.",
        "frozen_protocol": {
            "pre_outcome_freeze_commit": str((diagnosis.get("frozen_control_receipts") or {}).get("pre_outcome_freeze_commit") or ""),
            "contract_sha256": _sha(project_root / CONTRACT),
            "panel_sha256": _sha(project_root / PANEL),
            "model_manifest_sha256": _sha(project_root / MODEL_MANIFEST),
            "panel_units": int((panel.get("summary") or {}).get("causal_units") or qual.get("paired_units") or 0),
            "causal_arms": ["A_pristine", "B_displacement_clone", "C_identity_placebo", "D_exact_quotient"],
        },
        "competence_calibration": {
            "outcome": str(qual.get("calibration_outcome") or ""),
            "pristine_success": int(qual.get("calibration_pristine_success") or 0),
            "episodes": 24,
            "success_rate": float(qual.get("calibration_pristine_success_rate") or 0.0),
            "success_family_count": int(qual.get("calibration_success_family_count") or 0),
        },
        "paired_causal_result": {
            "formal_outcome": str(endpoint.get("formal_outcome") or ""),
            "paired_units": int(qual.get("paired_units") or 0),
            "arm_episodes": int(qual.get("arm_episodes") or 0),
            "success_rate": dict(endpoint.get("success_rate") or {}),
            "paired_disagreement": dict(endpoint.get("paired_disagreement") or {}),
            "B_vs_A_mcnemar_p": endpoint.get("B_vs_A_mcnemar_p"),
            "family_replicated_flip_count": int(endpoint.get("family_replicated_flip_count") or 0),
        },
        "trajectory_boundary": {
            "B_vs_A_response_sequence_disagreement": int(btraj.get("response_sequence_disagreement") or 0),
            "B_vs_A_action_sequence_disagreement": int(btraj.get("projected_action_sequence_disagreement") or 0),
            "B_vs_A_first_action_divergence_median_step": btraj.get("first_action_divergence_median_step"),
            "C_vs_A_response_sequence_disagreement": int(ctraj.get("response_sequence_disagreement") or 0),
            "C_vs_A_action_sequence_disagreement": int(ctraj.get("projected_action_sequence_disagreement") or 0),
            "C_vs_A_first_action_divergence_median_step": ctraj.get("first_action_divergence_median_step"),
            "D_vs_A_exact_trajectory_units": int(dtraj.get("exact_trajectory_match_count") or dtraj.get("trajectory_exact_match_count") or qual.get("paired_units") or 0),
            "same_information_screen_verdict": str(screen.get("verdict") or ""),
            "any_simple_B_over_C_dominance_supported": bool(screen.get("any_simple_B_over_C_dominance_supported", False)),
        },
        "statistical_resolution": {
            "paired_units": int(stat.get("paired_units") or 0),
            "task_clusters": int(stat.get("task_clusters") or 0),
            "registered_go_effect_floor": stat.get("registered_go_effect_floor"),
            "effect_floor_unidirectional_flips": int(stat.get("registered_go_effect_floor_equivalent_unidirectional_flips") or 0),
            "two_sided_exact_mcnemar_p_at_effect_floor": stat.get("two_sided_exact_mcnemar_p_at_effect_floor_if_all_flips_one_direction"),
            "minimum_unidirectional_discordances_for_p_lt_0_05": int(stat.get("minimum_unidirectional_discordances_for_two_sided_mcnemar_p_lt_0_05") or 0),
            "persistent_principle_dead_end_statistically_certified": bool(stat.get("persistent_principle_dead_end_statistically_certified", False)),
            "reason": str(stat.get("reason") or ""),
        },
        "final_disposition": {
            "experimental_stop_valid": bool(principle.get("experimental_stop_valid", False)),
            "experimental_realization": str(principle.get("experimental_realization_disposition") or ""),
            "principle_disposition": str(principle.get("principle_disposition") or ""),
            "persistent_principle_dead_end_certified": bool(principle.get("persistent_principle_dead_end_certified", False)),
            "broader_STRI_N1_N2_N3_unchanged": bool(principle.get("broader_STRI_N1_N2_N3_unchanged", False)),
            "stage2_locked": bool(principle.get("stage2_confirmation_locked", True)),
            "new_gpu_authorized": bool(principle.get("new_gpu_authorized", False)),
        },
        "claim_boundary": {
            "supports": "A qualified sample-level STOP of the frozen exact-clone-to-final-success C4 realization.",
            "does_not_support": [
                "population-level absence of every downstream effect",
                "a persistent principle dead end",
                "an active recovery mechanism",
                "expansion or invalidation of N1-N3",
                "post-hoc seed/model/task expansion",
            ],
        },
        "source_sha256": {key: _sha(project_root / rel) for key, rel in SOURCES.items()},
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def write_receipt(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    state = build_receipt(project_root)
    target = project_root / OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_receipt(), ensure_ascii=False, indent=2))
