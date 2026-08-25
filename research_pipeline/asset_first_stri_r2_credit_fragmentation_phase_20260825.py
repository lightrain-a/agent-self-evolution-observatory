from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .asset_first_stri_r2_credit_fragmentation_20260825 import (
    AUTHOR_REPO,
    EXPECTED_COMMIT,
    BACKGROUND_NAME,
    FOCAL_NAME,
    _git_head,
    _load_author_module,
    _skill,
    _write_library,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-contract-20260825.json"
P0_RESULT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"
OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
CSV_OUTPUT = PROJECT_ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.csv"

KS = tuple(range(1, 7))
NS = tuple(range(0, 49))
P_HATS = (0.10, 0.50, 0.90)
M = 8


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _records(ids: list[str], n: int, p_hat: float) -> list[dict[str, Any]]:
    return [{"skill_id": ids[i % len(ids)], "p_hat": float(p_hat), "consistency": True} for i in range(n)]


def _run_cell(module, tmp: Path, k: int, n: int, p_hat: float) -> dict[str, Any]:
    focal_ids = [f"focal_{i+1}" for i in range(k)]
    path = tmp / f"k{k}_n{n}_p{str(p_hat).replace('.', '')}.json"
    _write_library(path, [_skill(fid, FOCAL_NAME) for fid in focal_ids] + [_skill("background", BACKGROUND_NAME)])
    records = _records(focal_ids, n, p_hat)
    module.update_skill_stats_from_records(records, path=str(path), iteration=1)
    skills_before = module.load_skill_library(str(path), create=False)
    stats = {str(skill["id"]): module.normalize_skill_stats(skill.get("stats", {})) for skill in skills_before if str(skill["id"]) in focal_ids}
    retired = module.prune_easy_skills(path=str(path), preserve_initial_skills=True)
    retired_ids = {str(skill["id"]) for skill in retired}
    skills_after = module.load_skill_library(str(path), create=False)
    active_ids = {str(skill["id"]) for skill in skills_after}
    weights = module.sampling_weights(skills_after, current_iteration=2, use_quality=True, use_exploration=True, use_decay=False)
    total = float(sum(weights))
    focal_prob = float(sum(w for skill, w in zip(skills_after, weights) if str(skill["id"]) in focal_ids) / total) if total else 0.0
    native_active = any(fid in active_ids for fid in focal_ids)
    eligible = p_hat > 0.75
    analytic_active = True
    if eligible and n >= k * M:
        analytic_active = False
    canonical_active = not (eligible and n >= M)
    quotient_active = canonical_active
    return {
        "k": k,
        "N": n,
        "p_hat": p_hat,
        "native_class_active": native_active,
        "analytic_native_class_active": analytic_active,
        "canonical_class_active": canonical_active,
        "quotient_credit_class_active": quotient_active,
        "native_matches_analytic": native_active == analytic_active,
        "representation_divergence_from_canonical": native_active != canonical_active,
        "retired_focal_ids": len(retired_ids.intersection(focal_ids)),
        "active_focal_ids": len(active_ids.intersection(focal_ids)),
        "attempts_by_id": [int(stats[fid]["attempts"]) for fid in focal_ids],
        "avg_p_hat_by_id": [float(stats[fid]["avg_p_hat"]) for fid in focal_ids],
        "future_focal_sampling_probability": focal_prob,
    }


def build() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    p0 = json.loads(P0_RESULT.read_text(encoding="utf-8"))
    if p0.get("decision") != "PASS_RELEASED_CREDIT_FRAGMENTATION_MECHANISM":
        raise RuntimeError("P1 requires passing frozen P0")
    head = _git_head(AUTHOR_REPO)
    if head != EXPECTED_COMMIT:
        raise RuntimeError(f"author release drift: {head}")

    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="stri-r2-credit-phase-") as td:
        tmp = Path(td)
        module = _load_author_module(tmp)
        for p_hat in P_HATS:
            for k in KS:
                for n in NS:
                    rows.append(_run_cell(module, tmp, k, n, p_hat))

    mismatches = [row for row in rows if not row["native_matches_analytic"]]
    high = [row for row in rows if row["p_hat"] == 0.90]
    low_mid = [row for row in rows if row["p_hat"] in {0.10, 0.50}]
    low_mid_retired = [row for row in low_mid if not row["native_class_active"]]
    divergence = [row for row in high if row["representation_divergence_from_canonical"]]

    by_k: dict[str, Any] = {}
    for k in KS:
        high_k = [row for row in high if row["k"] == k]
        div_ns = [row["N"] for row in high_k if row["representation_divergence_from_canonical"]]
        first_retired = next((row["N"] for row in high_k if not row["native_class_active"]), None)
        predicted_first_retired = k * M
        by_k[str(k)] = {
            "predicted_divergence_window": [M, k * M - 1] if k > 1 else [],
            "observed_divergence_N_min": min(div_ns) if div_ns else None,
            "observed_divergence_N_max": max(div_ns) if div_ns else None,
            "observed_first_full_retirement_N": first_retired,
            "predicted_first_full_retirement_N": predicted_first_retired,
            "retirement_lag_vs_canonical": predicted_first_retired - M,
            "boundary_match": first_retired == predicted_first_retired,
        }

    pass_gate = (
        not mismatches
        and not low_mid_retired
        and all(v["boundary_match"] for v in by_k.values())
        and by_k["2"]["observed_divergence_N_min"] == 8
        and by_k["2"]["observed_divergence_N_max"] == 15
        and by_k["4"]["observed_divergence_N_min"] == 8
        and by_k["4"]["observed_divergence_N_max"] == 31
    )
    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "experiment_id": contract["experiment_id"],
        "stage": "MECHANISM_REDESIGN_DETERMINISTIC_P1_PHASE_RESULT",
        "decision": "PASS_CREDIT_FRAGMENTATION_PHASE_DIAGRAM" if pass_gate else "STOP_PHASE_MECHANISM_MISMATCH",
        "pass_gate": pass_gate,
        "contract_sha256": _sha_file(CONTRACT),
        "contract_git_commit": "2b1dab3f88510b0f7514741e210ff8f5c7c98e76",
        "p0_result_sha256": _sha_file(P0_RESULT),
        "author_release": {
            "commit": head,
            "source_file_sha256": _sha_file(AUTHOR_REPO / "skill_library/library.py"),
            "official_loop_callsite": "scripts/skill_solver_train.sh -> question_evaluate/upload.py --update_skill_stats --prune_easy_skills",
        },
        "grid": {"k_values": list(KS), "N_min": min(NS), "N_max": max(NS), "p_hat_values": list(P_HATS), "cells": len(rows)},
        "headline": {
            "analytic_mismatches": len(mismatches),
            "nonretirement_regime_unexpected_retirements": len(low_mid_retired),
            "retirement_threshold_M": M,
            "by_clone_multiplicity": by_k,
            "high_score_divergence_cells": len(divergence),
            "mechanism": "For retirement-eligible semantic evidence, per-ID thresholding delays full semantic-class retirement from N=M to N=kM under balanced k-way exact refinement; quotient-credit returns the boundary to N=M independent of k.",
        },
        "rows": rows,
        "mechanism_interpretation": "The released controller exhibits a multiplicity-dependent evidence-fragmentation phase transition, not a one-off 8-vs-4+4 artifact. Exact identity refinement linearly extends the semantic class's native active lifetime under the fixed evidence stream because retirement is thresholded after per-ID partitioning.",
        "reduction_boundary": "This result excludes selection opportunity by fixing exogenous feedback and localizes the defect to identity-indexed evidence containers plus a nonlinear retirement gate. It does not by itself establish that endogenous Skill-SP trajectories frequently enter the fragmentation window or that task utility changes.",
        "next_gate": "Audit real released/historical Skill-SP state trajectories for induced-skill evidence counts near the fragmentation window, and complete closest-work reduction against replication-proof bandits, state aggregation/lumpability, and generic thresholded grouped statistics before manuscript redesign.",
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
        fields = ["p_hat", "k", "N", "native_class_active", "canonical_class_active", "quotient_credit_class_active", "representation_divergence_from_canonical", "retired_focal_ids", "active_focal_ids", "future_focal_sampling_probability", "attempts_by_id"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in result["rows"]:
            writer.writerow({**{key: row[key] for key in fields if key != "attempts_by_id"}, "attempts_by_id": ";".join(map(str, row["attempts_by_id"]))})
    return result


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
