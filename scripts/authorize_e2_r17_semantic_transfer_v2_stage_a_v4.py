#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V2_STAGE_A_V4"
EXPECTED_PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V2_STAGE_A_V4_PREFLIGHT"
EXPECTED_REVIEW_VERDICT = "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--fresh-identity", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    req(not args.output.exists(), "Stage-A V4 authorization already exists")
    contract = load(args.contract)
    preflight = load(args.preflight)
    fresh_identity = load(args.fresh_identity)
    summary_path = args.review_root / "summary.json"
    deepseek_path = args.review_root / "deepseek-v4-pro.json"
    kimi_path = args.review_root / "kimi-k3.json"
    for path in (summary_path, deepseek_path, kimi_path):
        req(path.is_file(), f"missing independent review artifact: {path}")
    summary = load(summary_path)
    deepseek = load(deepseek_path)
    kimi = load(kimi_path)
    contract_sha = sha(args.contract)

    req(contract.get("status") == EXPECTED_CONTRACT_STATUS, "Stage-A V4 contract not frozen")
    req(preflight.get("status") == EXPECTED_PREFLIGHT_STATUS, "Stage-A V4 preflight not passing")
    req(preflight.get("contract_sha256") == contract_sha, "preflight contract binding drift")
    req(preflight.get("provider_calls") == 0 and preflight.get("scientific_execution") is False, "preflight crossed science boundary")
    req(summary.get("contract_sha256") == contract_sha, "review summary contract binding drift")
    req(summary.get("all_pass_to_separate_stage_a_authorization") is True, "dual review did not pass")
    req(summary.get("stage_b_authority") is False and summary.get("paper_claim_authority") is False, "dual review authority overbroad")

    req(fresh_identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "fresh model identity adjudication not passing")
    identity_row = (fresh_identity.get("requested_and_resolved") or {}).get("deepseek-v4-pro") or {}
    req(identity_row.get("resolved") == "deepseek-v4-pro-ga-260813", "fresh DeepSeek resolved identity drift")
    req(identity_row.get("thinking") == "disabled" and int(identity_row.get("provider_retry_limit") or -1) == 0, "fresh identity runtime flags drift")
    contract_created = datetime.fromisoformat(str(contract["created_at_utc"]))
    identity_created = datetime.fromisoformat(str(fresh_identity["created_at_utc"]))
    req(identity_created > contract_created, "fresh identity must be qualified after Stage-A V4 contract freeze")

    for model, row in (("deepseek-v4-pro", deepseek), ("kimi-k3", kimi)):
        req(row.get("status") == "COMPLETED", f"review not completed: {model}")
        review = row.get("review") or {}
        req(review.get("contract_sha256_acknowledged") == contract_sha, f"review contract acknowledgement drift: {model}")
        req(review.get("verdict") == EXPECTED_REVIEW_VERDICT, f"review verdict not PASS: {model}")
        req(review.get("execution_recommendation") == "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION", f"review execution recommendation not PASS: {model}")
        req(review.get("remaining_blockers") == [], f"review has blockers: {model}")
        req(review.get("stage_b_authority") is False and review.get("paper_claim_authority") is False, f"review authority overbroad: {model}")
        req(row.get("scientific_authority") is False and row.get("experiment_authority") is False, f"review receipt incorrectly has authority: {model}")

    suite = contract["suite"]
    suite_root = Path(suite["root"])
    split_path = suite_root / "r17_split_manifest.json"
    req(split_path.is_file() and sha(split_path) == suite["split_manifest_sha256"], "authorization split binding drift")
    split = load(split_path)
    req(list(split["e1_update_streams"].keys()) == list(suite["streams"]), "authorization stream ordering drift")
    all_tasks = [str(task) for stream_id in suite["streams"] for task in split["e1_update_streams"][stream_id]]
    heldout = [str(task) for task in split["e1_common_heldout_probe"]]
    req(len(all_tasks) == 144 and len(set(all_tasks)) == 144, "authorization Stage-A task shape drift")
    req(len(heldout) == 18 and len(set(heldout)) == 18 and set(all_tasks).isdisjoint(heldout), "authorization heldout separation drift")
    lease_path = Path(contract["global_lease_path"])
    req(not lease_path.exists(), "global Stage-A V4 lineage lease already exists")
    req(not Path(contract["run_root"]).exists(), "Stage-A V4 run root already exists")

    authority = {
        "stage_a_provider_execution": True,
        "stage_b_learning_execution": False,
        "updater": False,
        "heldout_evaluation": False,
        "analyzer": False,
        "second_backbone": False,
        "public_benchmark": False,
        "paper_promotion": False,
        "submission": False,
    }
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v2-stage-a-v4-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "AUTHORIZED_SEMANTIC_TRANSFER_V2_STAGE_A_V4",
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "preflight_path": str(args.preflight),
        "preflight_sha256": sha(args.preflight),
        "review_summary_path": str(summary_path),
        "review_summary_sha256": sha(summary_path),
        "review_receipts": {
            "deepseek-v4-pro": {"path": str(deepseek_path), "sha256": sha(deepseek_path)},
            "kimi-k3": {"path": str(kimi_path), "sha256": sha(kimi_path)},
        },
        "fresh_model_identity": {
            "path": str(args.fresh_identity),
            "sha256": sha(args.fresh_identity),
            "status": fresh_identity["status"],
            "created_at_utc": fresh_identity["created_at_utc"],
            "requested_model": "deepseek-v4-pro",
            "resolved_model": identity_row["resolved"]
        },
        "mindmemos_commit": contract["mindmemos"]["commit"],
        "single_use": True,
        "exactly_once": True,
        "automatic_retry": False,
        "authority": authority,
        "execution_scope": {
            "allowed_modes": ["e1"],
            "allowed_task_ids": all_tasks,
            "exact_k": 8,
            "allow_noninitial_skill": False,
            "required_skill_pre_sha256": contract["mindmemos"]["initial_skill_sha256"],
            "required_resolved_model": "deepseek-v4-pro-ga-260813",
            "identity_artifact_sha256": sha(args.fresh_identity),
            "suite_manifest_sha256": suite["suite_manifest_sha256"],
            "split_manifest_sha256": suite["split_manifest_sha256"],
            "max_turns": contract["actor"]["max_turns"],
            "max_output_tokens": contract["actor"]["max_output_tokens"],
            "runtime_python_executable": contract["runtime"]["python_executable"],
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "runtime_qualification_sha256": contract["runtime"]["qualification_sha256"],
            "provider_budget": {
                "required": True,
                "total_limit": contract["budget"]["max_provider_calls"],
                "per_unit_limit": contract["budget"]["provider_calls_per_rollout_limit"],
            },
            "global_lease_path": contract["global_lease_path"],
        },
        "interpretation_boundary": (
            "Single-use authority for Stage-A search-pool acquisition only. It authorizes no updater, no learned-state evaluation, "
            "no heldout access, no treatment-effect read, no Stage B, and no paper claim. Any failure leaves the run fail-closed and requires separate resume adjudication."
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "contract_sha256": contract_sha,
        "review_summary_sha256": payload["review_summary_sha256"],
        "allowed_tasks": len(all_tasks),
        "authority": authority,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
