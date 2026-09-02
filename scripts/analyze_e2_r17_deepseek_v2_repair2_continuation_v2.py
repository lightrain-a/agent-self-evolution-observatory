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

ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)
CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
EXECUTION_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
AUDIT_STATUS = "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SINGLE_USE_ANALYSIS"
ANALYSIS_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2_ANALYSIS"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
T_CRITICAL_095_DF11 = 1.7958848187036691
ALPHA = 0.05
EPSILON = 1.0 / 18.0
BOOTSTRAP_SEED = 1718
BOOTSTRAP_REPS = 100000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        value = str(row[key])
        require(value not in out, f"duplicate {key}={value}: {path}")
        out[value] = row
    return out


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"analysis output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
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
    values = [
        statistics.fmean(sign * value for sign, value in zip(signs, differences))
        for signs in itertools.product((-1.0, 1.0), repeat=len(differences))
    ]
    tolerance = 1e-15
    if direction == "positive":
        return sum(value >= observed - tolerance for value in values) / len(values)
    if direction == "negative":
        return sum(value <= observed + tolerance for value in values) / len(values)
    raise ValueError(direction)


def validate_gate(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str]:
    require(not args.output.exists(), "single-use analysis output already exists")
    for path in (args.contract, args.execution_authorization, args.analysis_authorization, args.completion_audit, args.run_summary):
        require(path.is_file(), f"missing bound artifact: {path}")
    contract = load(args.contract)
    execution_auth = load(args.execution_authorization)
    analysis_auth = load(args.analysis_authorization)
    audit = load(args.completion_audit)
    summary = load(args.run_summary)
    contract_sha = sha(args.contract)
    execution_auth_sha = sha(args.execution_authorization)
    audit_sha = sha(args.completion_audit)
    summary_sha = sha(args.run_summary)

    require(contract.get("status") == CONTRACT_STATUS, "V2 contract status drift")
    require(execution_auth.get("status") == EXECUTION_AUTH_STATUS, "V2 execution authorization status drift")
    require(execution_auth.get("contract_sha256") == contract_sha, "execution authorization/contract drift")
    require((execution_auth.get("authority") or {}).get("analyzer") is False, "execution authorization unexpectedly permits analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "V2 terminal summary incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == execution_auth_sha, "summary binding drift")
    require(summary.get("inference_performed") is False, "execution runner performed inference")

    require(audit.get("status") == AUDIT_STATUS, "completion audit not passing")
    require(audit.get("scientific_scores_read") is False, "completion audit crossed score boundary")
    require(audit.get("partial_effect_read") is False and audit.get("analyzer_run") is False, "completion audit crossed effect boundary")
    require(audit.get("contract_sha256") == contract_sha, "audit contract drift")
    require(audit.get("execution_authorization_sha256") == execution_auth_sha, "audit execution authorization drift")
    require(audit.get("run_summary_sha256") == summary_sha, "audit summary drift")
    require(int(audit.get("paired_replicate_units", -1)) == 48, "audit pair count drift")
    require(int(audit.get("learned_states", -1)) == 96, "audit state count drift")
    require(int(audit.get("heldout_rollout_units", -1)) == 1728, "audit heldout count drift")
    require(audit.get("duplicate_v1_excluded") is True, "duplicate V1 exclusion missing")
    require(audit.get("old_429_partial_attempt_excluded") is True, "old 429 partial exclusion missing")

    require(analysis_auth.get("status") == ANALYSIS_AUTH_STATUS, "analysis authorization status drift")
    require(analysis_auth.get("single_use") is True, "analysis authorization is not single-use")
    require(analysis_auth.get("contract_sha256") == contract_sha, "analysis authorization contract drift")
    require(analysis_auth.get("execution_authorization_sha256") == execution_auth_sha, "analysis authorization execution binding drift")
    require(analysis_auth.get("completion_audit_sha256") == audit_sha, "analysis authorization audit drift")
    require(analysis_auth.get("run_summary_sha256") == summary_sha, "analysis authorization summary drift")
    require(analysis_auth.get("analyzer_sha256") == sha(Path(__file__)), "analysis authorization analyzer-code drift")
    require(Path(str(analysis_auth.get("analysis_output_path"))) == args.output, "analysis output path not authorized")
    stats = analysis_auth.get("statistical_contract") or {}
    require(stats.get("analysis_unit") == "stream_mean_of_four_paired_replicate_differences", "analysis unit drift")
    require(int(stats.get("n_streams", -1)) == 12 and int(stats.get("replicates_per_stream", -1)) == 4, "analysis cardinality contract drift")
    require(int(stats.get("heldout_tasks_per_state", -1)) == 18, "heldout analysis contract drift")
    require(float(stats.get("alpha", -1)) == ALPHA, "alpha drift")
    require(int(stats.get("bootstrap_reps", -1)) == BOOTSTRAP_REPS and int(stats.get("bootstrap_seed", -1)) == BOOTSTRAP_SEED, "bootstrap contract drift")
    require(abs(float(stats.get("equivalence_margin", -1)) - EPSILON) < 1e-15, "equivalence margin drift")
    require(abs(float(stats.get("t_critical_0_95_df11", -1)) - T_CRITICAL_095_DF11) < 1e-15, "TOST critical value drift")
    authority = analysis_auth.get("authority") or {}
    require(authority.get("analyzer") is True and authority.get("read_complete_deepseek_v2_effect_once") is True, "analysis authority missing")
    for forbidden in ("scientific_experiment", "provider_io", "updater", "heldout_evaluation", "gpt_scientific_execution", "kimi_scientific_execution", "qwen_scientific_execution", "public_benchmark", "second_backbone", "paper_promotion", "submission"):
        require(authority.get(forbidden) is False, f"analysis authorization overbroad: {forbidden}")
    return contract, summary, audit, contract_sha, execution_auth_sha


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--execution-authorization", type=Path, required=True)
    ap.add_argument("--analysis-authorization", type=Path, required=True)
    ap.add_argument("--completion-audit", type=Path, required=True)
    ap.add_argument("--run-summary", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    contract, summary, audit, contract_sha, execution_auth_sha = validate_gate(args)
    valid_path = Path(str(summary["valid_replicate_manifest"]))
    require(valid_path.is_file() and sha(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(sha(valid_path) == audit["valid_replicate_manifest_sha256"], "valid manifest differs from full integrity audit")
    valid = rows_by(valid_path, "unit_id")
    expected_units = {f"{stream}/rep{rep}" for stream in contract["streams"] for rep in REPLICATES}
    require(set(valid) == expected_units, "analysis unit set drift")
    heldout = [str(x) for x in contract["heldout"]["task_ids"]]

    stream_rows: list[dict[str, Any]] = []
    stream_differences: list[float] = []
    replicate_differences: list[float] = []
    all_arm_scores: dict[str, list[float]] = {arm: [] for arm in ARMS}

    # FIRST SCIENTIFIC SCORE ACCESS: all integrity and single-use authorization checks above have passed.
    for stream_id in contract["streams"]:
        reps: list[dict[str, Any]] = []
        per_stream_diffs: list[float] = []
        for replicate in REPLICATES:
            unit_id = f"{stream_id}/rep{replicate}"
            pair = valid[unit_id]
            arm_scores: dict[str, list[float]] = {}
            for arm in ARMS:
                binding = pair["arms"][arm]
                manifest_path = Path(str(binding["eval_manifest_path"]))
                require(manifest_path.is_file() and sha(manifest_path) == binding["eval_manifest_sha256"], f"eval manifest drift: {unit_id}/{arm}")
                manifest = rows_by(manifest_path, "task_id")
                require(set(manifest) == set(heldout), f"heldout set drift: {unit_id}/{arm}")
                scores: list[float] = []
                for task_id in heldout:
                    row = manifest[task_id]
                    ref_path = Path(str(row["trajectory_ref_path"]))
                    require(ref_path.is_file() and sha(ref_path) == row["trajectory_ref_sha256"], f"trajectory-ref drift: {unit_id}/{arm}/{task_id}")
                    ref = load(ref_path)
                    trajectory = Path(str(ref["trajectory_path"]))
                    require(trajectory.is_file() and sha(trajectory) == ref["trajectory_sha256"], f"trajectory drift: {unit_id}/{arm}/{task_id}")
                    score = float(ref["score"])
                    require(score in (0.0, 1.0), f"non-binary endpoint score: {unit_id}/{arm}/{task_id}")
                    scores.append(score)
                    all_arm_scores[arm].append(score)
                arm_scores[arm] = scores
            j_win = statistics.fmean(arm_scores["win_c"])
            j_mrw = statistics.fmean(arm_scores["mrw"])
            diff = j_mrw - j_win
            replicate_differences.append(diff)
            per_stream_diffs.append(diff)
            reps.append({
                "replicate": replicate,
                "source": pair["source"],
                "j_win_c": j_win,
                "j_mrw": j_mrw,
                "difference_mrw_minus_win_c": diff,
                "win_c_successes": int(sum(arm_scores["win_c"])),
                "mrw_successes": int(sum(arm_scores["mrw"])),
            })
        stream_diff = statistics.fmean(per_stream_diffs)
        stream_differences.append(stream_diff)
        stream_rows.append({
            "stream_id": stream_id,
            "replicate_differences": per_stream_diffs,
            "mean_difference_mrw_minus_win_c": stream_diff,
            "replicates": reps,
        })

    require(len(stream_differences) == 12 and len(replicate_differences) == 48, "scientific analysis cardinality drift")
    require(len(all_arm_scores["win_c"]) == len(all_arm_scores["mrw"]) == 864, "arm score cardinality drift")

    mean, sd, tost_low, tost_high = paired_t_ci_90(stream_differences)
    bootstrap_low, bootstrap_high = bootstrap_ci_95(stream_differences)
    p_positive = exact_sign_flip_p(stream_differences, direction="positive")
    p_negative = exact_sign_flip_p(stream_differences, direction="negative")
    equivalent = tost_low > -EPSILON and tost_high < EPSILON
    superiority = mean > 0 and p_positive <= ALPHA and bootstrap_low > 0 and not equivalent
    harmful = mean < 0 and p_negative <= ALPHA and not equivalent

    if superiority:
        status = "GO_MRW_CAUSAL_EFFECT_SUPPORTED"
        interpretation = "Contemporaneous exact-same-pool MRW improves future frozen-skill utility over WIN-C under the preregistered paired superiority rule."
    elif equivalent:
        status = "STOP_MRW_PRACTICALLY_NULL"
        interpretation = "MRW and contemporaneous WIN-C are practically equivalent within the preregistered ±1/18 margin."
    elif harmful:
        status = "STOP_MRW_HARMFUL"
        interpretation = "MRW is significantly harmful relative to contemporaneous WIN-C under the preregistered negative-direction sign-flip test."
    else:
        status = "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
        interpretation = "MRW superiority and practical equivalence are both unestablished under the frozen design."

    win_mean = statistics.fmean(all_arm_scores["win_c"])
    mrw_mean = statistics.fmean(all_arm_scores["mrw"])
    positive_streams = sum(x > 0 for x in stream_differences)
    zero_streams = sum(x == 0 for x in stream_differences)
    negative_streams = sum(x < 0 for x in stream_differences)
    positive_reps = sum(x > 0 for x in replicate_differences)
    zero_reps = sum(x == 0 for x in replicate_differences)
    negative_reps = sum(x < 0 for x in replicate_differences)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v2-scientific-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "execution_authorization_sha256": execution_auth_sha,
        "analysis_authorization_path": str(args.analysis_authorization),
        "analysis_authorization_sha256": sha(args.analysis_authorization),
        "completion_audit_path": str(args.completion_audit),
        "completion_audit_sha256": sha(args.completion_audit),
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha(args.run_summary),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha(valid_path),
        "protocol_integrity": {
            "paired_units": "48/48",
            "learned_states": "96/96",
            "heldout_units": "1728/1728",
            "duplicate_v1_excluded": True,
            "old_429_partial_attempt_excluded": True,
            "pair29_recovery_admitted": True,
            "global_lineage_exactly_once": True,
            "provider_budget_binding_pass": audit["provider_budget_binding_pass"],
        },
        "descriptive_arm_utility": {
            "win_c_mean": win_mean,
            "mrw_mean": mrw_mean,
            "win_c_successes": int(sum(all_arm_scores["win_c"])),
            "mrw_successes": int(sum(all_arm_scores["mrw"])),
            "n_per_arm": 864,
        },
        "replicate_level_differences": replicate_differences,
        "per_stream": stream_rows,
        "n_streams": 12,
        "n_replicate_pairs": 48,
        "mean_difference": mean,
        "median_difference": statistics.median(stream_differences),
        "sd_difference": sd,
        "direction_counts": {
            "streams_positive": positive_streams,
            "streams_zero": zero_streams,
            "streams_negative": negative_streams,
            "replicates_positive": positive_reps,
            "replicates_zero": zero_reps,
            "replicates_negative": negative_reps,
        },
        "primary_superiority": {
            "alpha": ALPHA,
            "exact_one_sided_sign_flip_p": p_positive,
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
        "interpretation": interpretation,
        "authority": {
            "deepseek_v2_single_model_adjudicated": True,
            "execute_second_backbone": False,
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
