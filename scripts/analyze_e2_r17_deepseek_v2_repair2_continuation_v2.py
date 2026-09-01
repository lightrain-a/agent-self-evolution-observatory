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

from research_pipeline.e2_r17_repair2_manifest import ARMS, REPLICATES, validate_quarantine
from research_pipeline.e2_r17_repair2_continuation_v2_manifest import (
    EXPECTED_SOURCE_PAIRS,
    rows_by,
    validate_valid_rows_v2,
)

T_CRITICAL_095_DF11 = 1.7958848187036691
ALPHA = 0.05
EPSILON = 1.0 / 18.0
BOOTSTRAP_SEED = 1718
BOOTSTRAP_REPS = 100000
AUDIT_STATUS = "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS"
AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2_ANALYSIS"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
EXECUTION_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


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
    values = [statistics.fmean(sign * value for sign, value in zip(signs, differences)) for signs in itertools.product((-1.0, 1.0), repeat=len(differences))]
    tolerance = 1e-15
    if direction == "positive":
        return sum(value >= observed - tolerance for value in values) / len(values)
    if direction == "negative":
        return sum(value <= observed + tolerance for value in values) / len(values)
    raise ValueError(direction)


def validate_analysis_gate(
    *,
    contract_path: Path,
    execution_authorization_path: Path,
    analysis_authorization_path: Path,
    completion_audit_path: Path,
    run_summary_path: Path,
    output_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str, str]:
    require(not output_path.exists(), "Continuation V2 scientific adjudication already exists; analyzer is single-use")
    contract = load_json(contract_path)
    execution_auth = load_json(execution_authorization_path)
    analysis_auth = load_json(analysis_authorization_path)
    audit = load_json(completion_audit_path)
    summary = load_json(run_summary_path)
    contract_sha = sha_file(contract_path)
    execution_auth_sha = sha_file(execution_authorization_path)
    audit_sha = sha_file(completion_audit_path)
    summary_sha = sha_file(run_summary_path)

    require(contract.get("status") == CONTRACT_STATUS, "Continuation V2 contract status drift")
    require(execution_auth.get("status") == EXECUTION_AUTH_STATUS, "Continuation V2 execution authorization status drift")
    require(execution_auth.get("contract_sha256") == contract_sha, "execution authorization contract drift")
    require(execution_auth.get("authority", {}).get("analyzer") is False, "execution authorization unexpectedly permits analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "Continuation V2 summary incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == execution_auth_sha, "summary execution binding drift")
    require(summary.get("inference_performed") is False, "runner performed scientific inference")

    # Full integrity is validated before any score-bearing artifact is opened.
    require(audit.get("status") == AUDIT_STATUS, "completion audit not passing")
    require(audit.get("scientific_scores_read") is False, "completion audit crossed score boundary")
    require(audit.get("partial_effect_read") is False and audit.get("analyzer_run") is False, "completion audit crossed effect boundary")
    require(audit.get("contract_sha256") == contract_sha, "audit contract drift")
    require(audit.get("execution_authorization_sha256") == execution_auth_sha, "audit execution authorization drift")
    require(audit.get("run_summary_sha256") == summary_sha, "audit summary drift")
    require(int(audit.get("paired_replicate_units", -1)) == 48, "audit pair count drift")
    require(int(audit.get("learned_states", -1)) == 96, "audit state count drift")
    require(int(audit.get("heldout_rollout_units", -1)) == 1728, "audit heldout count drift")
    require(audit.get("global_lineage_lease_complete_pass") is True, "terminal global lineage lease not proven")

    require(analysis_auth.get("status") == AUTH_STATUS, "analysis authorization status drift")
    require(analysis_auth.get("single_use") is True, "analysis authorization is not single-use")
    require(analysis_auth.get("contract_sha256") == contract_sha, "analysis authorization contract drift")
    require(analysis_auth.get("execution_authorization_sha256") == execution_auth_sha, "analysis authorization execution binding drift")
    require(analysis_auth.get("completion_audit_sha256") == audit_sha, "analysis authorization audit drift")
    require(analysis_auth.get("run_summary_sha256") == summary_sha, "analysis authorization summary drift")
    require(analysis_auth.get("analyzer_sha256") == sha_file(Path(__file__)), "analysis authorization analyzer-code drift")
    require(Path(analysis_auth.get("analysis_output_path", "")) == output_path, "analysis output path not authorized")
    authority = analysis_auth.get("authority") or {}
    require(authority.get("analyzer") is True and authority.get("read_complete_deepseek_v2_effect_once") is True, "analysis authority missing")
    for forbidden in (
        "scientific_experiment",
        "provider_io",
        "updater",
        "heldout_evaluation",
        "gpt_scientific_execution",
        "kimi_scientific_execution",
        "qwen_scientific_execution",
        "public_benchmark",
        "second_backbone",
        "paper_promotion",
        "submission",
    ):
        require(authority.get(forbidden) is False, f"analysis authorization overbroad: {forbidden}")

    return contract, summary, audit, contract_sha, execution_auth_sha


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--execution-authorization", type=Path, required=True)
    parser.add_argument("--analysis-authorization", type=Path, required=True)
    parser.add_argument("--completion-audit", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract, summary, audit, contract_sha, execution_auth_sha = validate_analysis_gate(
        contract_path=args.contract,
        execution_authorization_path=args.execution_authorization,
        analysis_authorization_path=args.analysis_authorization,
        completion_audit_path=args.completion_audit,
        run_summary_path=args.run_summary,
        output_path=args.output,
    )

    valid_path = Path(summary["valid_replicate_manifest"])
    require(valid_path.is_file() and sha_file(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(sha_file(valid_path) == audit["valid_replicate_manifest_sha256"], "valid manifest differs from completion audit")
    valid_map = rows_by(valid_path, "unit_id")
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    valid_rows = list(valid_map.values())
    validate_valid_rows_v2(valid_rows, streams=contract["streams"], quarantine=quarantine, require_complete=True)
    require(audit.get("source_pair_counts") == dict(EXPECTED_SOURCE_PAIRS), "analysis source counts differ from frozen audit")

    heldout = [str(task) for task in contract["heldout"]["task_ids"]]
    stream_rows: list[dict[str, Any]] = []
    differences: list[float] = []
    replicate_differences: list[float] = []

    # First score access occurs only below, after the separate full-integrity audit
    # and single-use analysis authorization have both been validated.
    for stream_id in contract["streams"]:
        per_stream_replicates: list[dict[str, Any]] = []
        per_stream_differences: list[float] = []
        for replicate in REPLICATES:
            unit_id = f"{stream_id}/rep{replicate}"
            require(unit_id in valid_map, f"missing valid pair: {unit_id}")
            valid_pair = valid_map[unit_id]
            arm_scores: dict[str, list[float]] = {}
            for arm in ARMS:
                arm_binding = valid_pair["arms"][arm]
                manifest_path = Path(arm_binding["eval_manifest_path"])
                require(manifest_path.is_file() and sha_file(manifest_path) == arm_binding["eval_manifest_sha256"], f"eval manifest drift: {unit_id}/{arm}")
                manifest = rows_by(manifest_path, "task_id")
                require(set(manifest) == set(heldout), f"heldout set drift: {unit_id}/{arm}")
                scores: list[float] = []
                for task_id in heldout:
                    row = manifest[task_id]
                    ref_path = Path(row["trajectory_ref_path"])
                    require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref drift: {unit_id}/{arm}/{task_id}")
                    ref = load_json(ref_path)
                    trajectory = Path(ref["trajectory_path"])
                    require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory drift: {unit_id}/{arm}/{task_id}")
                    score = float(ref["score"])
                    require(score in (0.0, 1.0), "DeepSeek V2 endpoint score must be binary")
                    scores.append(score)
                arm_scores[arm] = scores
            j_win = statistics.fmean(arm_scores["win_c"])
            j_mrw = statistics.fmean(arm_scores["mrw"])
            difference = j_mrw - j_win
            replicate_differences.append(difference)
            per_stream_differences.append(difference)
            per_stream_replicates.append(
                {
                    "replicate": replicate,
                    "source": valid_pair["source"],
                    "j_win_c": j_win,
                    "j_mrw": j_mrw,
                    "difference_mrw_minus_win_c": difference,
                    "win_c_successes": int(sum(arm_scores["win_c"])),
                    "mrw_successes": int(sum(arm_scores["mrw"])),
                }
            )
        stream_difference = statistics.fmean(per_stream_differences)
        differences.append(stream_difference)
        stream_rows.append(
            {
                "stream_id": stream_id,
                "replicate_differences": per_stream_differences,
                "mean_difference_mrw_minus_win_c": stream_difference,
                "replicates": per_stream_replicates,
            }
        )

    require(len(differences) == 12 and len(replicate_differences) == 48, "scientific cardinality drift")
    mean, sd, tost_low, tost_high = paired_t_ci_90(differences)
    bootstrap_low, bootstrap_high = bootstrap_ci_95(differences)
    p_positive = exact_sign_flip_p(differences, direction="positive")
    p_negative = exact_sign_flip_p(differences, direction="negative")
    equivalent = tost_low > -EPSILON and tost_high < EPSILON
    superiority = mean > 0 and p_positive <= ALPHA and bootstrap_low > 0 and not equivalent
    harmful = mean < 0 and p_negative <= ALPHA and not equivalent

    if equivalent:
        status = "STOP_MRW_PRACTICALLY_NULL"
        interpretation = "MRW and contemporaneous WIN-C are practically equivalent within the preregistered ±1/18 margin."
    elif superiority:
        status = "GO_MRW_CAUSAL_EFFECT_SUPPORTED"
        interpretation = "Contemporaneous exact-same-pool MRW improves future frozen-skill utility over fresh WIN-C under the preregistered paired superiority rule."
    elif harmful:
        status = "STOP_MRW_HARMFUL"
        interpretation = "MRW is significantly harmful relative to contemporaneous WIN-C under the preregistered negative-direction sign-flip test."
    else:
        status = "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
        interpretation = "MRW superiority and practical equivalence are both unestablished under the frozen design."

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v2-scientific-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "execution_authorization_sha256": execution_auth_sha,
        "analysis_authorization_path": str(args.analysis_authorization),
        "analysis_authorization_sha256": sha_file(args.analysis_authorization),
        "completion_audit_path": str(args.completion_audit),
        "completion_audit_sha256": sha_file(args.completion_audit),
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha_file(args.run_summary),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha_file(valid_path),
        "protocol_integrity": {
            "paired_units": "48/48",
            "learned_states": "96/96",
            "heldout_units": "1728/1728",
            "source_pair_counts": dict(EXPECTED_SOURCE_PAIRS),
            "quarantine_exclusion_pass": True,
            "pair29_recovery_measurements": audit["pair29_recovery_measurements"],
            "attempt_uniqueness_pass": audit["provider_claim_uniqueness_pass"],
            "provider_budget_binding_pass": audit["provider_budget_binding_pass"],
            "global_lineage_lease_complete_pass": audit["global_lineage_lease_complete_pass"],
        },
        "provider_claims_by_source": audit["provider_claims_by_source"],
        "technical_failures": 0,
        "runtime_reliability_by_source": audit["runtime_reliability_by_source"],
        "repair1_quarantined_patch_apply_failures": audit["repair1_quarantined_patch_apply_failures"],
        "replicate_level_differences": replicate_differences,
        "per_stream": stream_rows,
        "n_streams": 12,
        "n_replicate_pairs": 48,
        "mean_difference": mean,
        "median_difference": statistics.median(differences),
        "sd_difference": sd,
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
