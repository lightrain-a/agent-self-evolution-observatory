#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

PREOUTCOME_SEAL_COMMIT = "dc3e5c4b297c4598b65669e5e68c7d7a2d9cff2d"
EXPECTED_PLAN_MD_SHA256 = "42e7ca7cc8d954a514308443915e0de81d649d5b1e8060d5da3be0536b02ade6"
EXPECTED_PLAN_JSON_SHA256 = "1ae5fd159dda44d06ee72ae052257d0dd694793e10297b944cd533e6e76e4d92"
EXPECTED_REPLAY_RECEIPT_SHA256 = "2bac711b6ebec8b77568bdca3cd0ea47d62d2dde52add8e34f44493703ff88d7"
EXPECTED_B10_RESULT_SHA256 = "e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6"
EXPECTED_STATES = 36
EXPECTED_N = 4
PERMUTATION_REPETITIONS = 100000
PERMUTATION_SEED = 20260824
ALPHA = 0.05
BOOTSTRAP_REPETITIONS = 10000
BOOTSTRAP_SEED = 20260904


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def within_collision(values: list[str]) -> float:
    n = len(values)
    require(n >= 2, "within-collision requires n>=2")
    counts = Counter(values)
    return sum(count * (count - 1) for count in counts.values()) / (n * (n - 1))


def between_collision(a: list[str], b: list[str]) -> float:
    require(a and b, "between-collision requires nonempty samples")
    ca, cb = Counter(a), Counter(b)
    return sum(ca[key] * cb[key] for key in (set(ca) | set(cb))) / (len(a) * len(b))


def collision_mmd2_u(success: list[str], failure: list[str]) -> tuple[float, float, float, float]:
    ws = within_collision(success)
    wf = within_collision(failure)
    cross = between_collision(success, failure)
    u = ws + wf - 2.0 * cross
    return u, ws, wf, cross


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def quantile_linear(sorted_values: list[float], q: float) -> float:
    require(sorted_values, "quantile requires values")
    require(0.0 <= q <= 1.0, "q outside [0,1]")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = q * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def state_stratified_permutation_p(cells: list[dict[str, Any]], observed_mean: float) -> tuple[float, int]:
    pools = [cell["success_actions"] + cell["failure_actions"] for cell in cells]
    rng = random.Random(PERMUTATION_SEED)
    greater_equal = 0
    for _ in range(PERMUTATION_REPETITIONS):
        permuted_u = []
        for pool in pools:
            shuffled = list(pool)
            rng.shuffle(shuffled)
            u, _, _, _ = collision_mmd2_u(shuffled[:EXPECTED_N], shuffled[EXPECTED_N:])
            permuted_u.append(u)
        if mean(permuted_u) >= observed_mean - 1e-15:
            greater_equal += 1
    return (greater_equal + 1) / (PERMUTATION_REPETITIONS + 1), greater_equal


def fixed_state_bootstrap(values: list[float]) -> dict[str, float | int]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    boot = []
    for _ in range(BOOTSTRAP_REPETITIONS):
        boot.append(mean([values[rng.randrange(n)] for _ in range(n)]))
    boot.sort()
    return {
        "repetitions": BOOTSTRAP_REPETITIONS,
        "seed": BOOTSTRAP_SEED,
        "percentile_2_5": quantile_linear(boot, 0.025),
        "percentile_97_5": quantile_linear(boot, 0.975),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-provider exact-match collision/MMD2 diagnostic for historical C1 B10 first actions.")
    parser.add_argument("--plan-md", required=True, type=Path)
    parser.add_argument("--plan-json", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--b10-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    require(sha(args.plan_md) == EXPECTED_PLAN_MD_SHA256, "pre-outcome markdown plan SHA drift")
    require(sha(args.plan_json) == EXPECTED_PLAN_JSON_SHA256, "pre-outcome machine plan SHA drift")
    require(sha(args.replay_receipt) == EXPECTED_REPLAY_RECEIPT_SHA256, "raw replay receipt SHA drift")
    require(sha(args.b10_result) == EXPECTED_B10_RESULT_SHA256, "B10 result SHA drift")

    plan = load(args.plan_json)
    replay = load(args.replay_receipt)
    b10 = load(args.b10_result)
    require(plan.get("status") == "FROZEN_BEFORE_COLLISION_MMD2_OUTCOME_OPENING", "plan was not frozen before outcome")
    require(replay.get("status") == "PASS_B10_FIRST_ACTION_RAW_REPLAY", "raw replay qualification did not pass")
    require(b10.get("status") == "B10_EXECUTION_COMPLETE", "historical B10 result incomplete")

    m2 = plan.get("m2_zero_provider_collision_diagnostic") or {}
    randomization = m2.get("randomization_test") or {}
    bootstrap_spec = m2.get("descriptive_bootstrap") or {}
    require(m2.get("status") == "FROZEN_NOT_YET_OPENED", "M2-Z plan status drift")
    require(m2.get("states") == EXPECTED_STATES and m2.get("draws_per_branch_per_state") == EXPECTED_N, "M2-Z geometry drift")
    require(randomization.get("repetitions") == PERMUTATION_REPETITIONS, "permutation repetitions drift")
    require(randomization.get("seed") == PERMUTATION_SEED, "permutation seed drift")
    require(abs(float(randomization.get("alpha")) - ALPHA) < 1e-15, "alpha drift")
    require(bootstrap_spec.get("repetitions") == BOOTSTRAP_REPETITIONS and bootstrap_spec.get("seed") == BOOTSTRAP_SEED, "bootstrap spec drift")

    raw_cells = b10.get("cell_results") or []
    require(len(raw_cells) == EXPECTED_STATES, f"expected {EXPECTED_STATES} B10 cells")
    cells = []
    for raw in raw_cells:
        state = int(raw["future_task"])
        success = [str(x) for x in raw.get("success") or []]
        failure = [str(x) for x in raw.get("failure") or []]
        require(len(success) == EXPECTED_N and len(failure) == EXPECTED_N, f"4+4 geometry drift at state {state}")
        u, ws, wf, cross = collision_mmd2_u(success, failure)
        cells.append(
            {
                "future_task": state,
                "selected_source_task": raw.get("selected_source_task"),
                "intent_template_id": raw.get("intent_template_id"),
                "success_actions": success,
                "failure_actions": failure,
                "success_frequency": dict(sorted(Counter(success).items())),
                "failure_frequency": dict(sorted(Counter(failure).items())),
                "within_success_collision": ws,
                "within_failure_collision": wf,
                "between_branch_collision": cross,
                "collision_mmd2_u": u,
                "historical_empirical_tv": raw.get("success_failure_tv"),
            }
        )

    u_values = [float(cell["collision_mmd2_u"]) for cell in cells]
    observed_mean = mean(u_values)
    observed_median = statistics.median(u_values)
    p_value, greater_equal = state_stratified_permutation_p(cells, observed_mean)
    bootstrap = fixed_state_bootstrap(u_values)
    support = observed_mean > 0.0 and p_value < ALPHA

    if support:
        decision = "D1_SUPPORTED_STOCHASTICITY_ADJUSTED_SEPARATION_POSTHOC"
        paper_action = "The replay-qualified historical panel supports positive S/F first-action distribution separation under the frozen collision statistic. Any primary stochasticity-controlled claim still requires explicit post-hoc labeling or a fresh prospective replicate."
    else:
        decision = "D2_STOCHASTICITY_ADJUSTED_SEPARATION_NOT_SUPPORTED"
        paper_action = "Retain first-action uptake as the first unsupported measured native stage. The collision diagnostic does not establish equality or a zero effect and does not justify significance-chasing top-up."

    summary = {
        "states": EXPECTED_STATES,
        "draws_per_branch_per_state": EXPECTED_N,
        "mean_collision_mmd2_u": observed_mean,
        "median_collision_mmd2_u": observed_median,
        "mean_within_success_collision": mean([float(cell["within_success_collision"]) for cell in cells]),
        "mean_within_failure_collision": mean([float(cell["within_failure_collision"]) for cell in cells]),
        "mean_between_branch_collision": mean([float(cell["between_branch_collision"]) for cell in cells]),
        "positive_u_states": sum(value > 1e-15 for value in u_values),
        "zero_u_states": sum(abs(value) <= 1e-15 for value in u_values),
        "negative_u_states": sum(value < -1e-15 for value in u_values),
        "one_sided_randomization_p": p_value,
        "randomization_ge_count": greater_equal,
        "alpha": ALPHA,
        "support_rule_pass": support,
        "fixed_state_bootstrap_95": [bootstrap["percentile_2_5"], bootstrap["percentile_97_5"]],
    }

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-b10-zero-provider-collision-mmd2-diagnostic",
        "date": "2026-09-04",
        "status": "M2Z_ZERO_PROVIDER_COLLISION_MMD2_COMPLETE",
        "paper_id": b10.get("paper_id"),
        "experiment_id": b10.get("experiment_id"),
        "preoutcome_design_binding": {
            "seal_commit": PREOUTCOME_SEAL_COMMIT,
            "plan_md": {"path": str(args.plan_md), "sha256": EXPECTED_PLAN_MD_SHA256},
            "plan_json": {"path": str(args.plan_json), "sha256": EXPECTED_PLAN_JSON_SHA256},
            "raw_replay_receipt": {"path": str(args.replay_receipt), "sha256": EXPECTED_REPLAY_RECEIPT_SHA256},
            "b10_result": {"path": str(args.b10_result), "sha256": EXPECTED_B10_RESULT_SHA256},
        },
        "estimand": {
            "scientific_unit": "frozen matched Shopping branch-comparison state",
            "kernel": "exact match: k(a,b)=1[a==b]",
            "per_state": "unbiased two-sample MMD2/collision U-statistic",
            "finite_sample_negative_values_allowed": True,
            "no_memory_used_in_primary": False,
            "provider_repeats_nested_within_state": True,
        },
        "inference": {
            "primary_statistic": "mean collision_mmd2_u over 36 states",
            "permutation_repetitions": PERMUTATION_REPETITIONS,
            "permutation_seed": PERMUTATION_SEED,
            "alpha": ALPHA,
            "support_rule": "observed mean U > 0 and one-sided p < 0.05",
            "bootstrap": bootstrap,
            "bootstrap_role": "descriptive fixed-state uncertainty only",
        },
        "summary": summary,
        "decision": decision,
        "paper_action": paper_action,
        "interpretation_boundary": [
            "post-hoc zero-provider diagnostic on prospectively collected historical B10 draws",
            "not an independent prospective replication",
            "no equality or zero-effect conclusion from non-support",
            "no population generalization beyond the frozen 36-state panel",
            "no adaptive top-up based on this p-value",
        ],
        "cells": cells,
        "execution": {"new_provider_calls": 0, "new_gpu_runs": 0, "historical_success_failure_draws_read": EXPECTED_STATES * EXPECTED_N * 2},
        "authority": {"claim_expansion": False, "prospective_replication": False, "submission": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": summary, "decision": decision, "new_provider_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
