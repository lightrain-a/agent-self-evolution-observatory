#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

T_CRITICAL_095_DF11 = 1.7958848187036691
ALPHA = 0.05
EPSILON = 1.0 / 18.0
BOOTSTRAP_SEED = 1718
BOOTSTRAP_REPS = 100000
ARMS = ("win_c", "mrw")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row[key])] = row
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position)); hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    frac = position - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def bootstrap_ci_95(differences: list[float]) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    means = [statistics.fmean(differences[rng.randrange(n)] for _ in range(n)) for _ in range(BOOTSTRAP_REPS)]
    return quantile(means, 0.025), quantile(means, 0.975)


def paired_t_ci_90(differences: list[float]) -> tuple[float, float, float, float]:
    n = len(differences)
    mean = statistics.fmean(differences)
    sd = statistics.stdev(differences) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else float("nan")
    half = T_CRITICAL_095_DF11 * se
    return mean, sd, mean - half, mean + half


def exact_sign_flip_p(differences: list[float], *, direction: str) -> float:
    observed = statistics.fmean(differences)
    values = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
        values.append(statistics.fmean(sign * value for sign, value in zip(signs, differences)))
    tol = 1e-15
    if direction == "positive":
        return sum(value >= observed - tol for value in values) / len(values)
    if direction == "negative":
        return sum(value <= observed + tol for value in values) / len(values)
    raise ValueError(direction)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract); auth = load_json(args.authorization); summary = load_json(args.run_summary)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    require(contract.get("status") == "FROZEN_E1_B_MRW_CONTEMPORANEOUS_FULL", "MRW contract not frozen")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_PENDING_SEPARATE_MRW_ADJUDICATION", "MRW run incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "MRW summary binding drift")
    require(summary.get("mrw_executed") is True and summary.get("primary_control") == "win_c", "MRW summary treatment/control drift")
    require(summary.get("mrw_inference_performed") is False, "runner must not perform MRW inference")

    gate = contract["negative_control_gate"]
    gate_path = Path(gate["path"])
    require(gate_path.is_file() and sha_file(gate_path) == gate["sha256"], "negative-control gate artifact drift")
    gate_payload = load_json(gate_path)
    require(gate_payload.get("status") == "PASS_NEGATIVE_CONTROL_EQUIVALENCE_READY_FOR_MRW_CONTRACT", "negative-control equivalence no longer passes")

    run_root = Path(contract["run_root"])
    heldout = [str(x) for x in contract["heldout"]["task_ids"]]
    stream_rows: list[dict[str, Any]] = []
    differences: list[float] = []
    for stream_id in contract["streams"]:
        arm_scores: dict[str, list[float]] = {}
        for arm in ARMS:
            state_root = run_root / "states" / stream_id / arm
            manifest_path = state_root / "checkpoints/completed_eval_tasks.jsonl"
            require(manifest_path.is_file(), f"missing eval manifest: {stream_id}/{arm}")
            manifest = rows_by(manifest_path, "task_id")
            require(set(manifest) == set(heldout), f"heldout completion mismatch: {stream_id}/{arm}")
            scores: list[float] = []
            for task_id in heldout:
                row = manifest[task_id]
                require(sha_file(Path(row["summary_path"])) == row["summary_sha256"], "eval summary SHA drift")
                ref_path = Path(row["trajectory_ref_path"])
                require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], "trajectory-ref SHA drift")
                ref = load_json(ref_path)
                trajectory = Path(ref["trajectory_path"])
                require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], "trajectory SHA drift")
                score = float(ref["score"])
                require(score in (0.0, 1.0), "MRW endpoint score must be binary")
                scores.append(score)
            arm_scores[arm] = scores
        j_win = statistics.fmean(arm_scores["win_c"])
        j_mrw = statistics.fmean(arm_scores["mrw"])
        diff = j_mrw - j_win
        differences.append(diff)
        stream_rows.append({
            "stream_id": stream_id,
            "j_win_c": j_win,
            "j_mrw": j_mrw,
            "difference_mrw_minus_win_c": diff,
            "win_c_successes": int(sum(arm_scores["win_c"])),
            "mrw_successes": int(sum(arm_scores["mrw"])),
        })

    require(len(differences) == 12, "MRW causal analysis requires exactly 12 paired stream units")
    mean, sd, tost_low, tost_high = paired_t_ci_90(differences)
    bootstrap_low, bootstrap_high = bootstrap_ci_95(differences)
    p_positive = exact_sign_flip_p(differences, direction="positive")
    p_negative = exact_sign_flip_p(differences, direction="negative")
    equivalent = tost_low > -EPSILON and tost_high < EPSILON
    # A statistically positive but TOST-equivalent effect is practically null by
    # the predeclared 1/18 margin and must not be promoted as a method GO.
    superiority = mean > 0 and p_positive <= ALPHA and bootstrap_low > 0 and not equivalent
    harmful = mean < 0 and p_negative <= ALPHA and not equivalent

    if superiority:
        status = "GO_MRW_CAUSAL_EFFECT_SUPPORTED"
        interpretation = "Contemporaneous exact-same-pool MRW improves future frozen-skill utility over fresh WIN-C under the preregistered paired superiority rule."
    elif equivalent:
        status = "STOP_MRW_PRACTICALLY_NULL"
        interpretation = "MRW and contemporaneous WIN-C are practically equivalent within the preregistered ±1/18 margin; the central MRW repair is stopped as practically null on this controlled substrate."
    elif harmful:
        status = "STOP_MRW_HARMFUL"
        interpretation = "MRW is significantly harmful relative to contemporaneous WIN-C under the preregistered negative-direction sign-flip test; the central MRW repair is stopped."
    else:
        status = "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
        interpretation = "MRW superiority is not established and practical equivalence is not established; the causal result remains inconclusive without changing the frozen experiment post hoc."

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-b-mrw-contemporaneous-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha_file(args.run_summary),
        "negative_control_gate_path": str(gate_path),
        "negative_control_gate_sha256": gate["sha256"],
        "scientific_unit": "12 paired stream-level learned states; 18 held-out probes are repeated measurements within each state",
        "primary_estimand": "mean_s[J_s(MRW)-J_s(WIN-C)] over the 12 frozen streams",
        "n_pairs": 12,
        "mean_difference": mean,
        "median_difference": statistics.median(differences),
        "sd_difference": sd,
        "positive_streams": sum(value > 0 for value in differences),
        "zero_streams": sum(value == 0 for value in differences),
        "negative_streams": sum(value < 0 for value in differences),
        "primary_superiority": {
            "alpha": ALPHA,
            "exact_one_sided_sign_flip_p": p_positive,
            "mean_positive": mean > 0,
            "paired_bootstrap_95_ci": [bootstrap_low, bootstrap_high],
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_reps": BOOTSTRAP_REPS,
            "pass": superiority,
        },
        "practical_null": {
            "epsilon": EPSILON,
            "paired_t_90_ci": [tost_low, tost_high],
            "t_critical_0_95_df11": T_CRITICAL_095_DF11,
            "paired_tost_equivalence_pass": equivalent,
        },
        "harm_check": {
            "exact_one_sided_negative_sign_flip_p": p_negative,
            "significantly_harmful": harmful,
        },
        "per_stream": stream_rows,
        "historical_win_a_win_b_role": "secondary bridge/stability evidence only; excluded from the primary MRW estimand and decision rule",
        "interpretation": interpretation,
        "authority": {
            "central_mechanism_adjudicated": status in {"GO_MRW_CAUSAL_EFFECT_SUPPORTED", "STOP_MRW_PRACTICALLY_NULL", "STOP_MRW_HARMFUL"},
            "prepare_public_benchmark_contract": status == "GO_MRW_CAUSAL_EFFECT_SUPPORTED",
            "execute_public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "GO_MRW_CAUSAL_EFFECT_SUPPORTED" else (3 if status.startswith("STOP_") else 4)


if __name__ == "__main__":
    raise SystemExit(main())
