from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_mcnemar_two_sided_unidirectional(k: int) -> float:
    if k <= 0:
        return 1.0
    return min(1.0, 2.0 * (0.5 ** k))


def zero_event_upper(n: int, alpha: float, two_sided: bool) -> float:
    tail = alpha / 2.0 if two_sided else alpha
    return 1.0 - tail ** (1.0 / n)


def run(analysis_path: pathlib.Path, panel_path: pathlib.Path) -> dict:
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    if analysis.get("outcome") != "STOP_FIXED_POLICY_DYNAMIC_BRIDGE" or analysis.get("qualified") is not True:
        raise ValueError("not-qualified-stop")
    n = int(analysis.get("qualified_units") or 0)
    if n != 24:
        raise ValueError("unexpected-unit-count")
    local_tasks = panel.get("local_causal_tasks") or []
    task_clusters = len(local_tasks)
    if task_clusters != 12:
        raise ValueError("unexpected-task-clusters")

    min_sig = next(k for k in range(1, n + 1) if exact_mcnemar_two_sided_unidirectional(k) < 0.05)
    requested_effect = 0.125
    requested_flips = math.ceil(requested_effect * n - 1e-12)
    return {
        "schema_version": "1.0",
        "artifact_kind": "post-negative-statistical-resolution-audit",
        "experiment_id": analysis.get("experiment_id"),
        "input_analysis_path": str(analysis_path),
        "input_analysis_sha256": sha(analysis_path),
        "input_panel_path": str(panel_path),
        "input_panel_sha256": sha(panel_path),
        "experimental_stop_rule_valid": True,
        "experimental_stop_outcome": analysis.get("outcome"),
        "persistent_principle_dead_end_statistically_certified": False,
        "reason": "The frozen experiment validly maps this sample to STOP, but it did not preregister an equivalence/non-inferiority margin, power target, or clustered-task inference sufficient to turn a null endpoint contrast into a persistent population-level principle dead end.",
        "paired_units": n,
        "task_clusters": task_clusters,
        "decode_seeds_per_task": 2,
        "observed_B_vs_A_endpoint_discordances": int(round((analysis.get("metrics") or {}).get("paired_disagreement", {}).get("B_vs_A", 0) * n)),
        "observed_C_vs_A_endpoint_discordances": int(round((analysis.get("metrics") or {}).get("paired_disagreement", {}).get("C_vs_A", 0) * n)),
        "registered_go_effect_floor": requested_effect,
        "registered_go_effect_floor_equivalent_unidirectional_flips": requested_flips,
        "two_sided_exact_mcnemar_p_at_effect_floor_if_all_flips_one_direction": exact_mcnemar_two_sided_unidirectional(requested_flips),
        "minimum_unidirectional_discordances_for_two_sided_mcnemar_p_lt_0_05": min_sig,
        "corresponding_minimum_detectable_signed_rate_difference_under_best_case_directionality": min_sig / n,
        "zero_discordance_upper_bounds": {
            "assuming_24_independent_units_one_sided_95pct": zero_event_upper(24, 0.05, False),
            "assuming_24_independent_units_two_sided_95pct": zero_event_upper(24, 0.05, True),
            "conservative_12_task_clusters_one_sided_95pct": zero_event_upper(12, 0.05, False),
            "conservative_12_task_clusters_two_sided_95pct": zero_event_upper(12, 0.05, True),
        },
        "interpretation": {
            "what_is_decided": "The preregistered C4 realization fails its GO rule and satisfies its STOP rule under a competent final policy and valid controls.",
            "what_is_not_decided": "The data do not, under a preregistered equivalence/power analysis, establish that every scientifically meaningful nonzero endpoint-transport effect in this scoped population is absent.",
            "why_no_more_seeds_now": "This audit blocks overclaiming a persistent principle dead end; it does not reopen the frozen experiment or authorize post-hoc sample-size expansion.",
            "relation_to_same_information_screen": "The trajectory-only residual is separately weakened by the matched C placebo. Statistical-resolution uncertainty at the endpoint does not create a novel trajectory claim.",
        },
        "recommended_principle_layer_disposition": "REGISTERED_REALIZATION_STOP_PRINCIPLE_NOT_PERSISTENT_DEAD_END",
        "reopen_condition": "Only a new predeclared paper contract with an explicit equivalence/effect margin, task-cluster inference/power plan, independent support qualification, and matched B/C/D controls could test a population-level endpoint-transport dead end. Do not add seeds to the current frozen P0-E run.",
        "new_gpu_authorized": False,
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "method": False, "full_experiment": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=pathlib.Path, required=True)
    ap.add_argument("--panel", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = run(a.analysis, a.panel)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
