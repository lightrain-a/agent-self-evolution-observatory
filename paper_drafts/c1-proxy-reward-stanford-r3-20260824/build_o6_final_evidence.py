#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
SOURCE_TASKS = ["21", "22", "23", "25"]
FUTURE_TASKS = ["164", "385", "387", "388"]


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return obj


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign(v: float) -> int:
    return 1 if v > 0 else (-1 if v < 0 else 0)


def geometry(ps: float, pf: float, p0: float) -> str:
    lo, hi = min(ps, pf), max(ps, pf)
    if lo < p0 < hi:
        return "BASELINE_BETWEEN_ARMS"
    ds, df = abs(ps - p0), abs(pf - p0)
    if abs(ds - df) < 1e-12:
        return "EQUIDISTANT"
    return "BASELINE_CLOSER_TO_SUCCESS" if ds < df else "BASELINE_CLOSER_TO_FAILURE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage1-failure", required=True, type=Path)
    ap.add_argument("--stage1-r1", required=True, type=Path)
    ap.add_argument("--stage2", required=True, type=Path)
    ap.add_argument("--stage2-contract", required=True, type=Path)
    ap.add_argument("--original-f2r1", required=True, type=Path)
    ap.add_argument("--o5", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    failure = load(args.stage1_failure)
    stage1 = load(args.stage1_r1)
    stage2 = load(args.stage2)
    contract = load(args.stage2_contract)
    original = load(args.original_f2r1)
    o5 = load(args.o5)

    if failure.get("status") != "STAGE1_STOP_OUTPUT_CAP_CENSORING_PLUS_CONCURRENCY_RACE":
        raise RuntimeError("unexpected parent Stage-1 failure status")
    if stage1.get("status") != "STAGE1_R1_PASS_READY_FOR_SEPARATE_STAGE2_CONTRACT":
        raise RuntimeError("Stage-1 R1 handoff is not a pass")
    if stage2.get("status") != "O6_STAGE2_COMPLETE" or int(stage2["summary"]["complete_primary_calls"]) != 256:
        raise RuntimeError("Stage-2 is not a complete 256-call result")
    if stage2["summary"]["provider_failures"] != 0:
        raise RuntimeError("Stage-2 has missing scientific units")
    if contract["terminal_gate"]["min_mean_absolute_success_rate_difference"] != 0.15 or contract["terminal_gate"]["alpha"] != 0.05:
        raise RuntimeError("Stage-2 gate drift")
    if stage1["summary"]["complete_pairs"] != 4 or stage1["summary"]["exact_content_changed_pairs"] != 4 or stage1["summary"]["title_set_changed_pairs"] != 4:
        raise RuntimeError("Stage-1 write gate drift")

    old_map = {(str(r["source_memory_task"]), str(r["future_task"])): r for r in original["cell_results"]}
    new_map = {(str(r["source_memory_task"]), str(r["future_task"])): r for r in stage2["cell_results"]}
    expected = {(s, f) for s in SOURCE_TASKS for f in FUTURE_TASKS}
    if set(old_map) != expected or set(new_map) != expected:
        raise RuntimeError("4x4 support drift")

    p0 = {str(r["future_task"]): float(r["no_memory_rate"]) for r in o5["fresh_no_memory_by_future_task"]}
    if set(p0) != set(FUTURE_TASKS):
        raise RuntimeError("O5 no-memory support drift")

    cell_rows = []
    both_nonzero = 0
    same_nonzero_direction = 0
    opposite_nonzero_direction = 0
    geometry_counts: dict[str, int] = {}
    for s in SOURCE_TASKS:
        for f in FUTURE_TASKS:
            old = old_map[(s, f)]
            new = new_map[(s, f)]
            old_signed = float(old["signed_failure_minus_success"])
            new_signed = float(new["signed_failure_minus_success"])
            if sign(old_signed) and sign(new_signed):
                both_nonzero += 1
                if sign(old_signed) == sign(new_signed):
                    same_nonzero_direction += 1
                else:
                    opposite_nonzero_direction += 1
            g = geometry(float(new["success_memory_rate"]), float(new["failure_memory_rate"]), p0[f])
            geometry_counts[g] = geometry_counts.get(g, 0) + 1
            cell_rows.append({
                "source_memory_task": s,
                "future_task": f,
                "original_writer_signed_failure_minus_success": old_signed,
                "glm53_writer_signed_failure_minus_success": new_signed,
                "original_writer_absolute_difference": float(old["absolute_rate_difference"]),
                "glm53_writer_absolute_difference": float(new["absolute_rate_difference"]),
                "glm53_success_memory_rate": float(new["success_memory_rate"]),
                "glm53_failure_memory_rate": float(new["failure_memory_rate"]),
                "shared_no_memory_rate": p0[f],
                "glm53_no_memory_geometry": g,
            })

    observed = float(stage2["summary"]["observed_mean_absolute_success_rate_difference"])
    p_value = float(stage2["summary"]["permutation_p_ge_observed"])
    old_observed = float(original["summary"]["observed_mean_absolute_success_rate_difference"])
    floor = float(contract["terminal_gate"]["min_mean_absolute_success_rate_difference"])
    alpha = float(contract["terminal_gate"]["alpha"])
    parent_lower = int(failure["execution_concurrency_failure"]["provider_post_count_observable_lower_bound"])
    o6_lower = parent_lower + int(stage1["execution_accounting"]["r1_4096_provider_calls"]) + int(stage2["summary"]["requested_primary_calls"])

    selected = {}
    for s, f in [("21", "387"), ("22", "388"), ("23", "387"), ("25", "387")]:
        selected[f"source{s}_future{f}"] = next(r for r in cell_rows if r["source_memory_task"] == s and r["future_task"] == f)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "o6-cross-writer-final-evidence",
        "paper_id": PAPER_ID,
        "objection_id": "PROXY-O6",
        "status": "O6_CROSS_WRITER_BOUNDARY_COMPLETE",
        "bindings": {
            "stage1_failure_sha256": sha(args.stage1_failure),
            "stage1_r1_sha256": sha(args.stage1_r1),
            "stage2_result_sha256": sha(args.stage2),
            "stage2_contract_sha256": sha(args.stage2_contract),
            "original_f2r1_sha256": sha(args.original_f2r1),
            "o5_evidence_sha256": sha(args.o5),
        },
        "writer_stage": {
            "writer": "GLM-5.3",
            "complete_pairs": int(stage1["summary"]["complete_pairs"]),
            "exact_content_changed_pairs": int(stage1["summary"]["exact_content_changed_pairs"]),
            "title_set_changed_pairs": int(stage1["summary"]["title_set_changed_pairs"]),
            "mean_token_jaccard_distance": float(stage1["summary"]["mean_token_jaccard_distance"]),
            "gate_pass": bool(stage1["summary"]["stage1_gate_pass"]),
            "interpretation": "The reward-conditioned write-time state divergence replicates on all four frozen source trajectories with a second writer family after one preregistered output-cap operationalization repair.",
        },
        "terminal_stage": {
            "complete_calls": int(stage2["summary"]["complete_primary_calls"]),
            "provider_failures": int(stage2["summary"]["provider_failures"]),
            "provider_status_counts": stage2["summary"]["provider_status_counts"],
            "mean_absolute_success_rate_difference": observed,
            "mean_signed_failure_minus_success": float(stage2["summary"]["mean_signed_failure_minus_success"]),
            "permutation_p": p_value,
            "effect_floor": floor,
            "alpha": alpha,
            "effect_floor_shortfall": round(floor - observed, 6),
            "permutation_gate_pass": p_value < alpha,
            "effect_floor_gate_pass": observed >= floor,
            "joint_gate_pass": bool(stage2["summary"]["gate_pass"]),
            "decision": stage2["decision"],
            "interpretation": "The second-writer terminal replication is statistically separated under the frozen permutation test but misses the preregistered minimum practical effect by 0.009375, so writer-level downstream generalization is not established.",
        },
        "cross_writer_comparison": {
            "original_writer_mean_absolute_effect": old_observed,
            "glm53_writer_mean_absolute_effect": observed,
            "absolute_effect_difference_glm53_minus_original": round(observed - old_observed, 6),
            "relative_glm53_to_original": round(observed / old_observed, 6),
            "cells_nonzero_in_both_writers": both_nonzero,
            "same_direction_among_nonzero_both": same_nonzero_direction,
            "opposite_direction_among_nonzero_both": opposite_nonzero_direction,
            "same_direction_fraction_among_nonzero_both": round(same_nonzero_direction / both_nonzero, 6) if both_nonzero else None,
            "cell_rows": cell_rows,
            "selected_cells": selected,
            "interpretation": "The writer swap changes both magnitude and cellwise direction. The downstream effect is therefore not writer-invariant even though the upstream write-time divergence itself replicates.",
        },
        "o5_shared_baseline_descriptive_reuse": {
            "new_provider_calls": 0,
            "justification": "No-memory contains no writer-produced memory object; downstream policy, future tasks, evidence packets, evaluator, and rollout depth are unchanged, so the already-frozen four O5 future-task baselines are writer-independent descriptive controls.",
            "geometry_counts": dict(sorted(geometry_counts.items())),
            "global_p_value": None,
        },
        "execution_accounting": {
            "initial_2200_stage_provider_posts_exact": None,
            "initial_2200_stage_provider_posts_observable_lower_bound": parent_lower,
            "initial_2200_stage_scientific_authority": False,
            "repair_4096_writer_calls": int(stage1["execution_accounting"]["r1_4096_provider_calls"]),
            "stage2_terminal_calls": int(stage2["summary"]["requested_primary_calls"]),
            "o6_provider_posts_observable_lower_bound": o6_lower,
            "o6_exact_total_provider_posts_reconstructible": False,
            "training_runs": 0,
            "gpu_runs": 0,
        },
        "claim_boundary": {
            "write_channel_cross_writer_supported_on_four_sources": True,
            "terminal_cross_writer_generalization_supported": False,
            "writer_invariant_effect_size_supported": False,
            "writer_invariant_effect_direction_supported": False,
            "domain_generalization_supported": False,
            "live_loop_supported": False,
            "corruption_mask_interaction_supported": False,
        },
        "next_scientific_action": "STOP_CROSS_WRITER_EXPANSION_AT_FROZEN_GATE; retain live-loop as environment support debt and full-memory-bank corruption-mask interaction as separate optional future scope rather than using it to rescue the failed writer-generalization gate.",
        "scientific_authority": False,
        "experiment_authority": False,
        "claim_expansion_authority": False,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "writer_stage": payload["writer_stage"],
        "terminal_stage": payload["terminal_stage"],
        "cross_writer_comparison": {k: v for k, v in payload["cross_writer_comparison"].items() if k not in {"cell_rows", "selected_cells"}},
        "geometry_counts": payload["o5_shared_baseline_descriptive_reuse"]["geometry_counts"],
        "execution_accounting": payload["execution_accounting"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
