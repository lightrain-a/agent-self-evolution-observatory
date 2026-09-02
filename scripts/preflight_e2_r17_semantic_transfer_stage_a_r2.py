#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V1_STAGE_A_R2"


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


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    req(spec is not None and spec.loader is not None, f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "R2 preflight output already exists")
    contract = load(args.contract)
    contract_sha = sha(args.contract)
    req(contract.get("status") == CONTRACT_STATUS, "R2 contract status invalid")
    req(contract.get("authority", {}).get("stage_a_provider_execution") is False, "draft R2 contract cannot self-authorize")

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        req(path.is_file(), f"missing bound code: {label}")
        req(sha(path) == item["sha256"], f"bound code SHA drift: {label}")

    identity_path = ROOT / contract["model_identity"]["path"]
    req(identity_path.is_file() and sha(identity_path) == contract["model_identity"]["sha256"], "identity wrapper drift")
    identity = load(identity_path)
    req(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "identity wrapper status invalid")
    model = (identity.get("requested_and_resolved") or {}).get("deepseek-v4-pro") or {}
    req(model.get("resolved") == "deepseek-v4-pro-ga-260813", "identity exact suffix drift")
    retry_limit = model.get("provider_retry_limit")
    req(model.get("thinking") == "disabled" and retry_limit is not None and int(retry_limit) == 0, "identity runtime flags drift")

    suite_root = Path(contract["suite"]["root"])
    suite_manifest = suite_root / "suite_manifest.json"
    split_path = suite_root / "r17_split_manifest.json"
    meta_path = suite_root / "r17_controlled_metadata.json"
    for path, expected in (
        (suite_manifest, contract["suite"]["suite_manifest_sha256"]),
        (split_path, contract["suite"]["split_manifest_sha256"]),
        (meta_path, contract["suite"]["metadata_sha256"]),
    ):
        req(path.is_file() and sha(path) == expected, f"suite artifact drift: {path.name}")
    split = load(split_path)
    streams = {str(k): [str(x) for x in v] for k, v in split["e1_update_streams"].items()}
    req(list(streams) == list(contract["suite"]["streams"]), "stream ordering drift")
    all_tasks = [task for stream_id in streams for task in streams[stream_id]]
    heldout = [str(x) for x in split["e1_common_heldout_probe"]]
    req(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "R2 update task shape invalid")
    req(len(heldout) == 18 and len(set(heldout)) == 18 and set(all_tasks).isdisjoint(heldout), "R2 heldout separation invalid")

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    req(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    initial_skill = Path(contract["mindmemos"]["initial_skill_path"])
    req(initial_skill.is_file() and sha(initial_skill) == contract["mindmemos"]["initial_skill_sha256"], "initial skill drift")

    runtime = contract["runtime"]
    runtime_python = Path(runtime["python_executable"])
    runtime_freeze = Path(runtime["freeze_path"])
    runtime_qual = ROOT / runtime["qualification_path"] if not Path(runtime["qualification_path"]).is_absolute() else Path(runtime["qualification_path"])
    req(runtime_python.is_file(), "runtime python missing")
    req(runtime_freeze.is_file() and sha(runtime_freeze) == runtime["freeze_sha256"], "runtime freeze drift")
    req(runtime_qual.is_file() and sha(runtime_qual) == runtime["qualification_sha256"], "runtime qualification drift")
    runtime_q = load(runtime_qual)
    req(runtime_q.get("status") == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification status invalid")
    smoke = subprocess.run(
        [str(runtime_python), "-c", "import openpyxl; from mindmemos_eval.skills.agents import ReactAgentFactory; from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv"],
        capture_output=True,
        text=True,
        check=False,
    )
    req(smoke.returncode == 0, "runtime import smoke failed")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["global_lease_path"])
    req(not run_root.exists(), "R2 run root already exists")
    req(not lease_path.exists(), "R2 global lease already exists")

    actor_path = ROOT / contract["bound_code"]["actor"]["path"]
    actor = import_module(actor_path, "semantic_transfer_r2_actor_preflight")
    # Synthetic authorization exists only in a private temporary file and is
    # used to exercise the exact generic-actor scope checks without provider I/O.
    synthetic = {
        "status": "AUTHORIZED_E1",
        "authority": {"scientific_experiment": True, "e1_a": True, "e1_b": False},
        "contract_sha256": contract_sha,
        "mindmemos_commit": contract["mindmemos"]["commit"],
        "execution_scope": {
            "allowed_modes": ["e1"],
            "allowed_task_ids": all_tasks,
            "exact_k": 8,
            "allow_noninitial_skill": False,
            "required_skill_pre_sha256": contract["mindmemos"]["initial_skill_sha256"],
            "required_resolved_model": "deepseek-v4-pro-ga-260813",
            "identity_artifact_sha256": contract["model_identity"]["sha256"],
            "suite_manifest_sha256": contract["suite"]["suite_manifest_sha256"],
            "split_manifest_sha256": contract["suite"]["split_manifest_sha256"],
            "max_turns": contract["actor"]["max_turns"],
            "max_output_tokens": contract["actor"]["max_output_tokens"],
            "provider_budget": {"required": True, "total_limit": 7680, "per_unit_limit": 10},
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(synthetic, handle)
        synthetic_path = Path(handle.name)
    try:
        actor.validate_authority(mode="e1", authorization=synthetic_path, task_ids=all_tasks[:8], split=split, k=8)
        guards = {"valid_scope": True, "wrong_k_rejected": False, "heldout_rejected": False, "wrong_mode_rejected": False}
        try:
            actor.validate_authority(mode="e1", authorization=synthetic_path, task_ids=all_tasks[:8], split=split, k=4)
        except RuntimeError:
            guards["wrong_k_rejected"] = True
        try:
            actor.validate_authority(mode="e1", authorization=synthetic_path, task_ids=[heldout[0]], split=split, k=8)
        except RuntimeError:
            guards["heldout_rejected"] = True
        try:
            actor.validate_authority(mode="e0", authorization=synthetic_path, task_ids=all_tasks[:8], split=split, k=8)
        except RuntimeError:
            guards["wrong_mode_rejected"] = True
        req(all(guards.values()), f"generic actor scope guards failed: {guards}")
    finally:
        synthetic_path.unlink(missing_ok=True)

    # Import the actual R2 control-plane modules under the frozen runtime/Python
    # parser so syntax/import failures are caught before review/authorization.
    runner_path = ROOT / contract["bound_code"]["stage_a_runner"]["path"]
    adjudicator_path = ROOT / contract["bound_code"]["equal_dose_adjudicator"]["path"]
    authorizer_path = ROOT / contract["bound_code"]["authorization_minter"]["path"]
    for path in (runner_path, adjudicator_path, authorizer_path):
        check = subprocess.run([str(runtime_python), "-m", "py_compile", str(path)], capture_output=True, text=True, check=False)
        req(check.returncode == 0, f"R2 bound code compile failed: {path.name}")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v1-stage-a-r2-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_STAGE_A_R2_PREFLIGHT",
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "provider_calls": 0,
        "scientific_execution": False,
        "new_test_outcomes_accessed": False,
        "run_root_exists": False,
        "global_lease_exists": False,
        "stream_count": 12,
        "task_count": 96,
        "heldout_forbidden_count": 18,
        "identity_wrapper_status": identity["status"],
        "required_resolved_model": model["resolved"],
        "runtime_import_smoke_pass": True,
        "scope_guard_checks": guards,
        "bound_code_compile_pass": True,
        "exactly_once": contract["exactly_once"],
        "authority": {
            "mint_stage_a_authorization": False,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False
        },
        "next_gate": "INDEPENDENT_PREEXECUTION_REVIEW_OF_R2_BEFORE_SINGLE_USE_AUTHORIZATION"
    }
    atomic_json(args.output, payload)
    print(json.dumps({"status": payload["status"], "contract_sha256": contract_sha, "scope_guard_checks": guards, "next_gate": payload["next_gate"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
