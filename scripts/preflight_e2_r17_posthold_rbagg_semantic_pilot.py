#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
STATUS = "FROZEN_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT"
PASS = "PASS_RBAGG_SEMANTIC_PILOT_ZERO_PROVIDER_PREFLIGHT"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "semantic-pilot preflight already exists")
    contract = load_json(args.contract)
    contract_sha = sha_file(args.contract)
    require(contract.get("status") == STATUS, "semantic-pilot contract status drift")
    require(contract.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent HOLD drift")
    require(contract.get("parent_status_changed") is False, "contract changes parent result")
    require(all(value is False for value in (contract.get("authority") or {}).values()), "contract must have zero execution authority")

    checks: dict[str, bool] = {}
    for label, binding in (contract.get("bound_files") or {}).items():
        path = resolve(str(binding["path"]))
        checks[f"file:{label}"] = path.is_file() and sha_file(path) == str(binding["sha256"])
    require(checks and all(checks.values()), "one or more semantic-pilot bound-file checks failed")

    closeout = load_json(resolve(contract["inputs"]["parent_closeout_path"]))
    review = load_json(resolve(contract["inputs"]["review_adjudication_path"]))
    support = load_json(resolve(contract["inputs"]["pool_support_path"]))
    split = load_json(resolve(contract["inputs"]["split_manifest_path"]))
    parent_contract = load_json(resolve(contract["inputs"]["parent_repair2_contract_path"]))
    require(closeout.get("status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "parent closeout not HOLD")
    require(review.get("status") == "PASS_DUAL_REVIEW_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_PROPOSAL_ONLY", "dual review not passing")
    require(review.get("authority", {}).get("provider_io") is False, "review artifact self-authorizes provider I/O")
    require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "pool support not passing")
    require(contract["inputs"]["parent_closeout_sha256"] == sha_file(resolve(contract["inputs"]["parent_closeout_path"])), "parent closeout binding drift")
    require(contract["inputs"]["review_adjudication_sha256"] == sha_file(resolve(contract["inputs"]["review_adjudication_path"])), "review binding drift")
    require(contract["inputs"]["pool_support_sha256"] == sha_file(resolve(contract["inputs"]["pool_support_path"])), "support binding drift")
    require(contract["inputs"]["split_manifest_sha256"] == sha_file(resolve(contract["inputs"]["split_manifest_path"])), "split binding drift")
    require(contract["inputs"]["parent_repair2_contract_sha256"] == sha_file(resolve(contract["inputs"]["parent_repair2_contract_path"])), "parent contract binding drift")

    fixed_stream = contract["pilot"]["fixed_stream"]
    task_ids = list(split["e1_update_streams"][fixed_stream])
    require(fixed_stream == "e1-agj-00", "fixed pilot stream drift")
    require(task_ids == contract["pilot"]["task_ids"] and len(task_ids) == 8, "pilot task order/cardinality drift")
    pool_root = Path(parent_contract["e1_a_pool_root"])
    for task_id in task_ids:
        pool_path = pool_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.is_file(), f"missing pilot pool: {task_id}")
        require(sha_file(pool_path) == support["pool_sha256"][task_id] == contract["pilot"]["pool_sha256"][task_id], f"pilot pool SHA drift: {task_id}")

    rb_root = Path(contract["reasoningbank"]["root"])
    rb_head = subprocess.run(["git", "-C", str(rb_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(rb_head == contract["reasoningbank"]["commit"], "ReasoningBank commit drift")
    mind_root = Path(contract["mindmemos"]["root"])
    mind_head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(mind_head == contract["mindmemos"]["commit"], "MindMemOS commit drift")

    # Environment route check only; no provider call.
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkSettings
    load_env_file(Path(contract["env_file"]))
    settings = ArkSettings.from_env(required=True)
    require(settings.base_url.rstrip("/") == contract["model"]["route"], "Ark route drift in zero-provider preflight")

    run_root = Path(contract["run_root"])
    require(not run_root.exists(), "semantic-pilot run root must be absent before authorization")
    require(int(contract["provider_budget"]["total_limit"]) == 11 and int(contract["provider_budget"]["per_unit_limit"]) == 11, "provider budget drift")
    require(int(contract["pilot"]["aggregation_calls"]) == 8, "aggregation call count drift")
    require(int(contract["pilot"]["mindmemos_nominal_calls"]) == 2 and int(contract["pilot"]["mindmemos_hard_max_calls"]) == 3, "MindMemOS pilot call bounds drift")
    require(int(contract["pilot"]["heldout_evaluations"]) == 0, "pilot heldout must be zero")
    require(contract["pilot"]["pilot_skill_scientific_inclusion"] is False, "pilot skill must be excluded")
    require(contract["exactly_once"]["automatic_retry"] is False and contract["exactly_once"]["authorized_runs"] == 1, "exactly-once semantics drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PASS,
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "fixed_stream": fixed_stream,
        "task_count": 8,
        "bound_file_checks": len(checks),
        "all_bound_file_checks_pass": True,
        "pool_sha_checks": 8,
        "reasoningbank_commit": rb_head,
        "mindmemos_commit": mind_head,
        "route": contract["model"]["route"],
        "required_resolved_model": contract["model"]["required_resolved_model"],
        "run_root_absent": True,
        "provider_calls": 0,
        "provider_claims": 0,
        "heldout_evaluations": 0,
        "scientific_effectiveness_evaluated": False,
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "authority": {
            "mint_single_use_semantic_pilot_authorization": True,
            "provider_io": False,
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "paper_promotion": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
