#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_STATUS = "PASS_REPAIR2_V3_FULL_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS"
AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_V3_ANALYSIS"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"


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
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--execution-authorization", type=Path, required=True)
    parser.add_argument("--completion-audit", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--analyzer", type=Path, required=True)
    parser.add_argument("--analysis-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "analysis authorization already exists; single-use mint required")
    require(not args.analysis_output.exists(), "scientific analysis already exists")
    for path in (
        args.contract,
        args.execution_authorization,
        args.completion_audit,
        args.run_summary,
        args.analyzer,
    ):
        require(path.is_file(), f"missing bound artifact: {path}")

    contract = load_json(args.contract)
    execution_auth = load_json(args.execution_authorization)
    audit = load_json(args.completion_audit)
    summary = load_json(args.run_summary)
    contract_sha = sha_file(args.contract)
    execution_auth_sha = sha_file(args.execution_authorization)
    summary_sha = sha_file(args.run_summary)
    audit_sha = sha_file(args.completion_audit)

    require(contract.get("status") == "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V3", "V3 contract status drift")
    require(execution_auth.get("status") == "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_V3", "V3 execution authorization status drift")
    require(execution_auth.get("contract_sha256") == contract_sha, "execution authorization contract drift")
    require(execution_auth.get("authority", {}).get("analyzer") is False, "execution authorization unexpectedly permits analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "V3 run incomplete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract drift")
    require(summary.get("authorization_sha256") == execution_auth_sha, "summary authorization drift")
    require(audit.get("status") == AUDIT_STATUS, "completion audit not passing")
    require(audit.get("scientific_scores_read") is False, "completion audit crossed score boundary")
    require(audit.get("partial_effect_read") is False and audit.get("analyzer_run") is False, "completion audit crossed effect boundary")
    require(audit.get("contract_sha256") == contract_sha, "audit contract drift")
    require(audit.get("execution_authorization_sha256") == execution_auth_sha, "audit execution authorization drift")
    require(audit.get("run_summary_sha256") == summary_sha, "audit summary drift")
    require(int(audit.get("paired_replicate_units", -1)) == 48, "audit pair cardinality drift")
    require(int(audit.get("learned_states", -1)) == 96, "audit state cardinality drift")
    require(int(audit.get("heldout_rollout_units", -1)) == 1728, "audit heldout cardinality drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-analysis-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUTH_STATUS,
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
        "analyzer_sha256": sha_file(args.analyzer),
        "analysis_output_path": str(args.analysis_output),
        "single_use": True,
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
            "Single-use authorization to analyze only the fully complete, integrity-audited "
            "DeepSeek V2 Repair2 V3 sample. It grants no provider, updater, evaluator, "
            "second-model, public-benchmark, paper, or submission authority."
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
