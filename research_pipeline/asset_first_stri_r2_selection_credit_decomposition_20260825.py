from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .asset_first_stri_r2_credit_fragmentation_20260825 import (
    AUTHOR_REPO,
    BACKGROUND_NAME,
    EXPECTED_COMMIT,
    FOCAL_NAME,
    _git_head,
    _load_author_module,
    _skill,
    _write_library,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT_ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-contract-20260825.json"
NOVELTY = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-novelty-reduction-20260825.json"
OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json"
CSV_OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.csv"

FOCAL_MEMBERS = ("focal_a", "focal_b")
FEEDBACK = tuple({"p_hat": 0.90, "consistency": True} for _ in range(8))


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _feedback_hash() -> str:
    return _canonical_sha(list(FEEDBACK))


def _native_selection(module, tmp: Path, *, split: bool) -> dict[str, Any]:
    path = tmp / ("selection_split.json" if split else "selection_canonical.json")
    focal_ids = list(FOCAL_MEMBERS) if split else ["focal"]
    _write_library(path, [_skill(fid, FOCAL_NAME) for fid in focal_ids] + [_skill("background", BACKGROUND_NAME)])
    skills = module.load_skill_library(str(path), create=False)
    weights = module.sampling_weights(skills, current_iteration=1, use_quality=True, use_exploration=True, use_decay=False)
    total = float(sum(weights))
    probs = {str(skill["id"]): float(weight / total) for skill, weight in zip(skills, weights)}
    focal_prob = float(sum(probs.get(fid, 0.0) for fid in focal_ids))
    return {
        "mode": "native",
        "identity_probabilities": probs,
        "focal_semantic_probability": focal_prob,
        "source_function": "sampling_weights",
    }


def _quotient_selection(module, tmp: Path) -> dict[str, Any]:
    # The released scoring function is evaluated on one representative per semantic class;
    # exact member IDs then share the conserved focal class mass without increasing it.
    ref = _native_selection(module, tmp, split=False)
    focal_mass = ref["focal_semantic_probability"]
    background_mass = ref["identity_probabilities"]["background"]
    member_mass = focal_mass / len(FOCAL_MEMBERS)
    return {
        "mode": "quotient",
        "identity_probabilities": {FOCAL_MEMBERS[0]: member_mass, FOCAL_MEMBERS[1]: member_mass, "background": background_mass},
        "focal_semantic_probability": focal_mass,
        "source_function": "sampling_weights on semantic-class representatives + exact mass conservation",
        "canonical_reference_probability": focal_mass,
    }


def _records(ids: list[str]) -> list[dict[str, Any]]:
    return [{"skill_id": ids[i % len(ids)], **evidence} for i, evidence in enumerate(FEEDBACK)]


def _stats(module, path: Path, ids: list[str]) -> dict[str, Any]:
    skills = module.load_skill_library(str(path), create=False)
    out = {}
    for skill in skills:
        sid = str(skill["id"])
        if sid in ids:
            out[sid] = module.normalize_skill_stats(skill.get("stats", {}))
    return out


def _native_credit(module, tmp: Path, name: str, *, split: bool) -> dict[str, Any]:
    path = tmp / f"credit_{name}.json"
    focal_ids = list(FOCAL_MEMBERS) if split else ["focal"]
    _write_library(path, [_skill(fid, FOCAL_NAME) for fid in focal_ids] + [_skill("background", BACKGROUND_NAME)])
    records = _records(focal_ids)
    module.update_skill_stats_from_records(records, path=str(path), iteration=1)
    pre = _stats(module, path, focal_ids)
    retired = module.prune_easy_skills(path=str(path), preserve_initial_skills=True)
    retired_ids = {str(skill["id"]) for skill in retired}
    active_ids = {str(skill["id"]) for skill in module.load_skill_library(str(path), create=False)}
    return {
        "mode": "native",
        "semantic_feedback_sha256": _feedback_hash(),
        "feedback_records": len(records),
        "pre_prune_stats": pre,
        "retired_focal_ids": sorted(retired_ids.intersection(focal_ids)),
        "active_focal_ids": sorted(active_ids.intersection(focal_ids)),
        "focal_semantic_class_retired": all(fid in retired_ids for fid in focal_ids),
        "focal_semantic_class_active": any(fid in active_ids for fid in focal_ids),
    }


def _quotient_credit(module, tmp: Path, name: str) -> dict[str, Any]:
    # Aggregate the identical semantic evidence onto one class representative and apply
    # the same released update + pruning functions once; project the class lifecycle
    # decision back to both exact member IDs.
    rep = _native_credit(module, tmp, name + "_classrep", split=False)
    retired = rep["focal_semantic_class_retired"]
    return {
        "mode": "quotient",
        "semantic_feedback_sha256": rep["semantic_feedback_sha256"],
        "feedback_records": rep["feedback_records"],
        "class_representative_stats": rep["pre_prune_stats"]["focal"],
        "projected_retired_focal_ids": list(FOCAL_MEMBERS) if retired else [],
        "projected_active_focal_ids": [] if retired else list(FOCAL_MEMBERS),
        "focal_semantic_class_retired": retired,
        "focal_semantic_class_active": not retired,
        "source_functions": ["update_skill_stats_from_records", "prune_easy_skills"],
    }


def build() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    novelty = json.loads(NOVELTY.read_text(encoding="utf-8"))
    if novelty.get("gate", {}).get("decision") != contract["required_novelty_gate_decision"]:
        raise RuntimeError("novelty gate does not authorize P2 decomposition")
    head = _git_head(AUTHOR_REPO)
    if head != EXPECTED_COMMIT:
        raise RuntimeError(f"author release drift: {head}")

    with tempfile.TemporaryDirectory(prefix="stri-r2-selection-credit-2x2-") as td:
        tmp = Path(td)
        module = _load_author_module(tmp)
        defaults = module.prune_easy_skills.__defaults__
        observed_defaults = {
            "min_attempts": int(defaults[1]),
            "avg_p_hat_threshold": float(defaults[2]),
            "too_easy_rate_threshold": float(defaults[3]),
        }
        if observed_defaults != {"min_attempts": 8, "avg_p_hat_threshold": 0.75, "too_easy_rate_threshold": 0.6}:
            raise RuntimeError(f"released prune defaults drift: {observed_defaults}")

        canonical_selection = _native_selection(module, tmp, split=False)
        split_native_selection = _native_selection(module, tmp, split=True)
        split_quotient_selection = _quotient_selection(module, tmp)

        canonical_credit = _native_credit(module, tmp, "canonical", split=False)
        native_credit = _native_credit(module, tmp, "split_native", split=True)
        quotient_credit = _quotient_credit(module, tmp, "split_quotient")

        cells: dict[str, Any] = {}
        for s_name, selection in (("native", split_native_selection), ("quotient", split_quotient_selection)):
            for c_name, credit in (("native", native_credit), ("quotient", quotient_credit)):
                key = f"S_{s_name}__C_{c_name}"
                selection_match = abs(float(selection["focal_semantic_probability"]) - float(canonical_selection["focal_semantic_probability"])) <= 1e-12
                lifecycle_match = bool(credit["focal_semantic_class_retired"]) == bool(canonical_credit["focal_semantic_class_retired"])
                cells[key] = {
                    "selection_mode": s_name,
                    "credit_mode": c_name,
                    "focal_semantic_selection_probability": selection["focal_semantic_probability"],
                    "selection_matches_canonical": selection_match,
                    "focal_semantic_class_retired_after_feedback": credit["focal_semantic_class_retired"],
                    "post_credit_lifecycle_matches_canonical": lifecycle_match,
                    "feedback_sha256": credit["semantic_feedback_sha256"],
                    "both_invariance_endpoints_match_canonical": selection_match and lifecycle_match,
                }

    expected = contract["frozen_cell_predictions"]
    cell_match = all(
        cells[key]["selection_matches_canonical"] is bool(pred["initial_selection_matches_canonical"])
        and cells[key]["post_credit_lifecycle_matches_canonical"] is bool(pred["post_credit_lifecycle_matches_canonical"])
        for key, pred in expected.items()
    )
    same_feedback = len({cell["feedback_sha256"] for cell in cells.values()}) == 1
    numerical_gate = (
        abs(canonical_selection["focal_semantic_probability"] - 0.5) <= 1e-12
        and abs(split_native_selection["focal_semantic_probability"] - (2.0 / 3.0)) <= 1e-12
        and abs(split_quotient_selection["focal_semantic_probability"] - 0.5) <= 1e-12
        and canonical_credit["focal_semantic_class_retired"] is True
        and native_credit["focal_semantic_class_retired"] is False
        and quotient_credit["focal_semantic_class_retired"] is True
        and canonical_credit["pre_prune_stats"]["focal"]["attempts"] == 8
        and sorted(stats["attempts"] for stats in native_credit["pre_prune_stats"].values()) == [4, 4]
        and quotient_credit["class_representative_stats"]["attempts"] == 8
    )
    pass_gate = bool(cell_match and same_feedback and numerical_gate)

    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "experiment_id": contract["experiment_id"],
        "stage": "MECHANISM_REDESIGN_DETERMINISTIC_P2_DECOMPOSITION_RESULT",
        "decision": "PASS_TWO_CHANNEL_SELECTION_CREDIT_DECOMPOSITION" if pass_gate else "STOP_TWO_CHANNEL_DECOMPOSITION_FAILED",
        "pass_gate": pass_gate,
        "contract_sha256": _sha_file(CONTRACT),
        "contract_git_commit": "96ff2fcce40dabb817b2c12c3986eb5ca6b51e6a",
        "novelty_reduction_sha256": _sha_file(NOVELTY),
        "author_release": {
            "commit": head,
            "source_file": "skill_library/library.py",
            "source_file_sha256": _sha_file(AUTHOR_REPO / "skill_library/library.py"),
            "observed_pruning_defaults": observed_defaults,
        },
        "canonical_reference": {
            "selection": canonical_selection,
            "credit": canonical_credit,
        },
        "split_factor_realizations": {
            "native_selection": split_native_selection,
            "quotient_selection": split_quotient_selection,
            "native_credit": native_credit,
            "quotient_credit": quotient_credit,
        },
        "cells": cells,
        "headline": {
            "canonical_focal_selection_probability": canonical_selection["focal_semantic_probability"],
            "split_native_focal_selection_probability": split_native_selection["focal_semantic_probability"],
            "split_quotient_focal_selection_probability": split_quotient_selection["focal_semantic_probability"],
            "canonical_retired_after_eight_feedback": canonical_credit["focal_semantic_class_retired"],
            "split_native_credit_retired_after_eight_feedback": native_credit["focal_semantic_class_retired"],
            "split_quotient_credit_retired_after_eight_feedback": quotient_credit["focal_semantic_class_retired"],
            "selection_only_repair_cell": cells["S_quotient__C_native"],
            "credit_only_repair_cell": cells["S_native__C_quotient"],
            "both_repaired_cell": cells["S_quotient__C_quotient"],
        },
        "mechanism_decomposition": {
            "selection_channel": "Exact identity refinement changes immediate semantic selection mass under released per-ID normalization (0.5 canonical versus 2/3 native split); semantic quotient mass conservation restores 0.5.",
            "credit_channel": "With selection absent from feedback generation and the same eight semantic feedback values, per-ID evidence partition prevents retirement while semantic quotient-credit restores canonical retirement.",
            "orthogonality_result": "Fixing selection alone leaves the lifecycle defect; fixing credit alone leaves the immediate selection defect; quotienting both restores both canonical semantic endpoints.",
        },
        "claim_boundary": "Deterministic two-channel controller decomposition on the released Skill-SP controller. It establishes stage separation, not endogenous prevalence, downstream utility, cross-system generality, or task-general behavioral propagation.",
        "next_gate": "Paper-design-only R2 story synthesis plus natural-prevalence qualification design. No model/agent/GPU experiment is authorized by this result.",
        "new_model_calls": 0,
        "new_agent_runs": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["result_canonical_sha256"] = _canonical_sha(result)
    return result


def write_outputs() -> dict[str, Any]:
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "cell", "selection_mode", "credit_mode", "focal_semantic_selection_probability",
            "selection_matches_canonical", "focal_semantic_class_retired_after_feedback",
            "post_credit_lifecycle_matches_canonical", "both_invariance_endpoints_match_canonical", "feedback_sha256",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for key, cell in result["cells"].items():
            writer.writerow({"cell": key, **cell})
    return result


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
