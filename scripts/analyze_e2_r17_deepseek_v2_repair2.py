#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_quarantine, validate_valid_rows

T_CRITICAL_095_DF11 = 1.7958848187036691
ALPHA = 0.05
EPSILON = 1.0 / 18.0
BOOTSTRAP_SEED = 1718
BOOTSTRAP_REPS = 100000
ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)


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
    require(contract.get("status") == "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION", "DeepSeek V2 Repair2 contract not frozen")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION", "DeepSeek V2 run incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "MRW summary binding drift")
    require(summary.get("mrw_executed") is True and summary.get("primary_control") == "win_c", "DeepSeek V2 summary treatment/control drift")
    require(summary.get("inference_performed") is False, "runner must not perform DeepSeek V2 inference")
    require(int(summary.get("replicates_per_stream")) == len(REPLICATES), "replicate count drift")

    prior = contract["v1_identifiability_hold"]
    prior_path = Path(prior["path"])
    require(prior_path.is_file() and sha_file(prior_path) == prior["sha256"], "V1 identifiability artifact drift")
    require(load_json(prior_path).get("status") == "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY", "V1 HOLD provenance drift")

    valid_path = Path(summary["valid_replicate_manifest"])
    require(valid_path.is_file() and sha_file(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(str(valid_path) == str(contract["valid_replicate_manifest"]["path"]), "valid manifest path drift")
    valid_map = rows_by(valid_path, "unit_id")
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows(list(valid_map.values()), streams=contract["streams"], quarantine=quarantine, require_complete=True)
    heldout = [str(x) for x in contract["heldout"]["task_ids"]]
    stream_rows: list[dict[str, Any]] = []
    differences: list[float] = []
    for stream_id in contract["streams"]:
        replicate_rows: list[dict[str, Any]] = []
        replicate_diffs: list[float] = []
        for replicate in REPLICATES:
            unit_id = f"{stream_id}/rep{replicate}"
            require(unit_id in valid_map, f"valid manifest missing pair: {unit_id}")
            valid_pair = valid_map[unit_id]
            arm_scores: dict[str, list[float]] = {}
            for arm in ARMS:
                arm_binding = valid_pair["arms"][arm]
                state_root = Path(arm_binding["state_root"])
                checkpoint_path = state_root / "checkpoints/update_completed.json"
                require(checkpoint_path.is_file(), f"missing update checkpoint: {unit_id}/{arm}")
                checkpoint = load_json(checkpoint_path)
                require(sha_file(Path(checkpoint["skill_post_path"])) == arm_binding["skill_sha256"], f"skill SHA drift: {unit_id}/{arm}")
                require(sha_file(Path(checkpoint["update_receipt_path"])) == arm_binding["update_receipt_sha256"], f"receipt SHA drift: {unit_id}/{arm}")
                manifest_path = Path(arm_binding["eval_manifest_path"])
                require(manifest_path.is_file() and sha_file(manifest_path) == arm_binding["eval_manifest_sha256"], f"eval manifest drift: {unit_id}/{arm}")
                manifest = rows_by(manifest_path, "task_id")
                require(set(manifest) == set(heldout), f"heldout completion mismatch: {stream_id}/rep{replicate}/{arm}")
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
                    require(score in (0.0, 1.0), "DeepSeek V2 endpoint score must be binary")
                    scores.append(score)
                arm_scores[arm] = scores
            j_win = statistics.fmean(arm_scores["win_c"])
            j_mrw = statistics.fmean(arm_scores["mrw"])
            diff = j_mrw - j_win
            replicate_diffs.append(diff)
            replicate_rows.append({
                "replicate": replicate,
                "j_win_c": j_win,
                "j_mrw": j_mrw,
                "difference_mrw_minus_win_c": diff,
                "win_c_successes": int(sum(arm_scores["win_c"])),
                "mrw_successes": int(sum(arm_scores["mrw"])),
            })
        stream_diff = statistics.fmean(replicate_diffs)
        differences.append(stream_diff)
        stream_rows.append({
            "stream_id": stream_id,
            "replicate_differences": replicate_diffs,
            "mean_difference_mrw_minus_win_c": stream_diff,
            "replicates": replicate_rows,
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
        "artifact_type": "e2-r17-deepseek-v2-repair2-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha_file(args.run_summary),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha_file(valid_path),
        "runtime_reliability": summary.get("runtime_reliability"),
        "repair1_quarantined_patch_apply_failures": summary.get("repair1_quarantined_patch_apply_failures"),
        "v1_identifiability_hold_path": str(prior_path),
        "v1_identifiability_hold_sha256": prior["sha256"],
        "replicates_per_stream": len(REPLICATES),
        "scientific_unit": "12 stream-level effects; each stream effect averages four independent contemporaneous WIN-C/MRW replicate pairs, each evaluated on the same 18 deterministic-workbook-verifier probes",
        "primary_estimand": "mean_s[(1/4) sum_r (J_sr(MRW)-J_sr(WIN-C))] over the 12 frozen streams",
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
        "historical_win_a_win_b_role": "V1 nuisance-variance/sample-size prior only; excluded from the primary V2 estimand and decision rule",
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
