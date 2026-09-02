#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
EXECUTION_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
AUDIT_STATUS = "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SINGLE_USE_ANALYSIS"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
ANALYSIS_AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2_ANALYSIS"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--execution-authorization", type=Path, required=True)
    ap.add_argument("--completion-audit", type=Path, required=True)
    ap.add_argument("--run-summary", type=Path, required=True)
    ap.add_argument("--analyzer", type=Path, required=True)
    ap.add_argument("--analysis-output", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    require(not args.output.exists(), "analysis authorization already exists")
    require(not args.analysis_output.exists(), "analysis output already exists")
    for path in (args.contract, args.execution_authorization, args.completion_audit, args.run_summary, args.analyzer):
        require(path.is_file(), f"missing bound artifact: {path}")

    contract = load(args.contract)
    execution_auth = load(args.execution_authorization)
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
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == execution_auth_sha, "terminal summary binding drift")
    require(summary.get("inference_performed") is False, "execution runner performed inference")

    require(audit.get("status") == AUDIT_STATUS, "full integrity audit not passing")
    require(audit.get("scientific_scores_read") is False, "integrity audit crossed score boundary")
    require(audit.get("partial_effect_read") is False and audit.get("analyzer_run") is False, "integrity audit crossed effect boundary")
    require(audit.get("contract_sha256") == contract_sha, "audit contract drift")
    require(audit.get("execution_authorization_sha256") == execution_auth_sha, "audit execution-authorization drift")
    require(audit.get("run_summary_sha256") == summary_sha, "audit summary drift")
    require(int(audit.get("paired_replicate_units", -1)) == 48, "audit pair cardinality drift")
    require(int(audit.get("learned_states", -1)) == 96, "audit learned-state cardinality drift")
    require(int(audit.get("heldout_rollout_units", -1)) == 1728, "audit heldout cardinality drift")
    require(audit.get("duplicate_v1_excluded") is True, "duplicate V1 exclusion not proved")
    require(audit.get("old_429_partial_attempt_excluded") is True, "old 429 partial exclusion not proved")
    require(audit.get("global_lineage_exactly_once") is True, "global lineage exactly-once not proved")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v2-analysis-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": ANALYSIS_AUTH_STATUS,
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "execution_authorization_path": str(args.execution_authorization),
        "execution_authorization_sha256": execution_auth_sha,
        "completion_audit_path": str(args.completion_audit),
        "completion_audit_sha256": audit_sha,
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": summary_sha,
        "valid_replicate_manifest_path": audit["valid_replicate_manifest_path"],
        "valid_replicate_manifest_sha256": audit["valid_replicate_manifest_sha256"],
        "analyzer_path": str(args.analyzer),
        "analyzer_sha256": sha(args.analyzer),
        "analysis_output_path": str(args.analysis_output),
        "single_use": True,
        "statistical_contract": {
            "analysis_unit": "stream_mean_of_four_paired_replicate_differences",
            "n_streams": 12,
            "replicates_per_stream": 4,
            "heldout_tasks_per_state": 18,
            "effect": "J_MRW_minus_J_WIN_C",
            "alpha": 0.05,
            "superiority_test": "exact_one_sided_sign_flip_over_12_stream_differences",
            "bootstrap": "paired_stream_bootstrap",
            "bootstrap_reps": 100000,
            "bootstrap_seed": 1718,
            "equivalence_margin": 0.05555555555555555,
            "equivalence_test": "paired_t_90_ci_within_plus_minus_1_over_18",
            "t_critical_0_95_df11": 1.7958848187036691,
            "decision_order": ["superiority", "practical_null", "harm", "hold"],
        },
        "authority": {
            "analyzer": True,
            "read_complete_deepseek_v2_effect_once": True,
            "scientific_experiment": False,
            "provider_io": False,
            "updater": False,
            "heldout_evaluation": False,
            "gpt_scientific_execution": False,
            "kimi_scientific_execution": False,
            "qwen_scientific_execution": False,
            "public_benchmark": False,
            "second_backbone": False,
            "paper_promotion": False,
            "submission": False,
        },
        "interpretation_boundary": (
            "Single-use authorization to read the complete integrity-audited DeepSeek V2 Repair2 sample exactly once. "
            "It preserves the preregistered stream-level paired statistics and grants no provider, updater, evaluator, "
            "second-backbone, public-benchmark, paper-promotion, or submission authority."
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
