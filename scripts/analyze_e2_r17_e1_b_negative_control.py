#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

T_CRITICAL_095_DF11 = 1.7958848187036691
BOOTSTRAP_SEED = 1717
BOOTSTRAP_REPS = 100000
ALPHA = 0.05
EPSILON = 1.0 / 18.0
ARMS = ("win_a", "win_b")


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
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line); rows[str(row[key])] = row
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position)); hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    frac = position - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def bootstrap_ci(differences: list[float]) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    means = [statistics.fmean(differences[rng.randrange(n)] for _ in range(n)) for _ in range(BOOTSTRAP_REPS)]
    return quantile(means, 0.05), quantile(means, 0.95)


def paired_t_ci_90(differences: list[float]) -> tuple[float, float, float, float]:
    n = len(differences); mean = statistics.fmean(differences)
    sd = statistics.stdev(differences) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else float("nan")
    half = T_CRITICAL_095_DF11 * se
    return mean, sd, mean - half, mean + half


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract); auth = load_json(args.authorization); summary = load_json(args.run_summary)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    require(contract.get("status") == "FROZEN_E1_B_NEGATIVE_CONTROL_FULL", "negative-control contract not frozen")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION", "negative-control run incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "negative-control summary binding drift")
    require(summary.get("mrw_executed") is False and summary.get("negative_control_inference_performed") is False, "run summary violates negative-control-only boundary")

    run_root = Path(contract["run_root"])
    heldout = contract["heldout"]["task_ids"]
    stream_rows = []
    differences = []
    for stream_id in contract["streams"]:
        arm_scores: dict[str, list[float]] = {}
        for arm in ARMS:
            state_root = run_root / "states" / stream_id / arm
            manifest = rows_by(state_root / "checkpoints/completed_eval_tasks.jsonl", "task_id")
            require(set(manifest) == set(heldout), f"heldout completion mismatch: {stream_id}/{arm}")
            scores = []
            for task_id in heldout:
                row = manifest[task_id]
                require(sha_file(Path(row["summary_path"])) == row["summary_sha256"], "eval summary SHA drift")
                ref_path = Path(row["trajectory_ref_path"])
                require(sha_file(ref_path) == row["trajectory_ref_sha256"], "trajectory-ref SHA drift")
                ref = load_json(ref_path)
                trajectory = Path(ref["trajectory_path"])
                require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], "trajectory SHA drift")
                score = float(ref["score"])
                require(score in (0.0, 1.0), "negative-control endpoint score must be binary")
                scores.append(score)
            arm_scores[arm] = scores
        ja = statistics.fmean(arm_scores["win_a"]); jb = statistics.fmean(arm_scores["win_b"]); diff = jb - ja
        differences.append(diff)
        stream_rows.append({"stream_id":stream_id,"j_win_a":ja,"j_win_b":jb,"difference_win_b_minus_win_a":diff,"win_a_successes":int(sum(arm_scores["win_a"])),"win_b_successes":int(sum(arm_scores["win_b"]))})

    require(len(differences) == 12, "negative-control requires exactly 12 paired stream units")
    mean, sd, ci_low, ci_high = paired_t_ci_90(differences)
    boot_low, boot_high = bootstrap_ci(differences)
    equivalent = ci_low > -EPSILON and ci_high < EPSILON
    status = "PASS_NEGATIVE_CONTROL_EQUIVALENCE_READY_FOR_MRW_CONTRACT" if equivalent else "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY"
    payload = {
        "schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-adjudication","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,
        "contract_sha256":contract_sha,"authorization_sha256":auth_sha,"run_summary_path":str(args.run_summary),"run_summary_sha256":sha_file(args.run_summary),
        "scientific_unit":"12 paired stream-level learned states; 18 probes are repeated measurements, not 216 independent units per arm",
        "epsilon":EPSILON,"alpha":ALPHA,"n_pairs":12,"difference_definition":"J_s(WIN-B)-J_s(WIN-A)","mean_difference":mean,"sd_difference":sd,
        "paired_t_90_ci":[ci_low,ci_high],"t_critical_0_95_df11":T_CRITICAL_095_DF11,"paired_tost_equivalence_pass":equivalent,
        "bootstrap":{"seed":BOOTSTRAP_SEED,"reps":BOOTSTRAP_REPS,"interval":"90% paired bootstrap robustness","ci":[boot_low,boot_high],"controls_primary_gate":False},
        "per_stream":stream_rows,
        "interpretation":("Identical-treatment hosted updater+evaluation variability is practically equivalent within one held-out probe of success rate; MRW may now be separately contracted." if equivalent else "Identical-treatment variability is not demonstrated equivalent within the preregistered margin. MRW remains unauthorized; this is a nuisance-control HOLD, not evidence for or against the R17 mechanism."),
        "authority":{"prepare_mrw_contract":equivalent,"execute_mrw":False,"paper_promotion":False,"submission":False},
        "central_mechanism_adjudicated":False
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if equivalent else 3


if __name__ == "__main__":
    raise SystemExit(main())
