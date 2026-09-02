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
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ACTOR = ROOT / "scripts/run_e2_r17_actor_pool.py"
EXPECTED_ACTOR_SHA = "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
EXPECTED_SUITE_SHA = "a7ddee258ddc22cee3efe22bad44046faa20ba9d49762c98a66a843c2c9533a3"
EXPECTED_COMPAT_SPLIT_SHA = "6ac03fd07391b2671e2e3cecd975395adff6c9fbd622751195a5a46b6a39af1c"
EXPECTED_COMPAT_META_SHA = "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f"
EXPECTED_MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
EXPECTED_INITIAL_SKILL_SHA = "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
EXPECTED_RUNTIME_FREEZE_SHA = "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e"
EXPECTED_RUNTIME_QUAL_SHA = "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b"
EXPECTED_RUNTIME_COMPAT_STATUS = "PASS_SEMANTIC_TRANSFER_V1_RUNTIME_COMPAT_R1"


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def import_actor_module() -> Any:
    spec = importlib.util.spec_from_file_location("e2_r17_actor_stage_a_preflight", ACTOR)
    req(spec is not None and spec.loader is not None, "cannot load generic actor module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_scope_guards(actor: Any, split: dict[str, Any], all_tasks: list[str], heldout: list[str]) -> dict[str, bool]:
    synthetic = {
        "status": "AUTHORIZED_E1",
        "authority": {"scientific_experiment": True, "e1_a": True, "e1_b": False},
        "contract_sha256": "0" * 64,
        "execution_scope": {
            "allowed_modes": ["e1"],
            "allowed_task_ids": all_tasks,
            "exact_k": 8,
            "allow_noninitial_skill": False,
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(synthetic, handle)
        auth_path = Path(handle.name)
    try:
        actor.validate_authority(mode="e1", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=8)
        wrong_k_rejected = False
        try:
            actor.validate_authority(mode="e1", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=4)
        except RuntimeError:
            wrong_k_rejected = True
        heldout_rejected = False
        try:
            actor.validate_authority(mode="e1", authorization=auth_path, task_ids=[heldout[0]], split=split, k=8)
        except RuntimeError:
            heldout_rejected = True
        wrong_mode_rejected = False
        try:
            actor.validate_authority(mode="e0", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=8)
        except RuntimeError:
            wrong_mode_rejected = True
        return {
            "valid_e1_k8_scope_passes": True,
            "wrong_k_rejected": wrong_k_rejected,
            "heldout_task_rejected": heldout_rejected,
            "wrong_mode_rejected": wrong_mode_rejected,
        }
    finally:
        auth_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-compat-audit", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--runtime-venv", type=Path, required=True)
    parser.add_argument("--runtime-freeze", type=Path, required=True)
    parser.add_argument("--runtime-qualification", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--contract-output", type=Path, required=True)
    parser.add_argument("--preflight-output", type=Path, required=True)
    args = parser.parse_args()

    req(not args.contract_output.exists(), "Stage-A contract output already exists")
    req(not args.preflight_output.exists(), "Stage-A preflight output already exists")
    req(not args.run_root.exists(), "Stage-A run root must not exist before authorization")

    audit = load(args.runtime_compat_audit)
    identity = load(args.identity)
    suite_manifest_path = args.suite_root / "suite_manifest.json"
    split_path = args.suite_root / "r17_split_manifest.json"
    meta_path = args.suite_root / "r17_controlled_metadata.json"
    split = load(split_path)
    suite_manifest = load(suite_manifest_path)
    runtime_q = load(args.runtime_qualification)
    initial_skill = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    runtime_python = args.runtime_venv / "bin/python"

    for path in (
        args.runtime_compat_audit,
        args.identity,
        suite_manifest_path,
        split_path,
        meta_path,
        ACTOR,
        initial_skill,
        runtime_python,
        args.runtime_freeze,
        args.runtime_qualification,
    ):
        req(path.is_file(), f"missing Stage-A bound artifact: {path}")

    req(audit["status"] == EXPECTED_RUNTIME_COMPAT_STATUS, "runtime-compat audit not passing")
    req(audit["provider_calls_scientific"] == 0 and audit["new_test_outcomes_accessed"] is False, "runtime-compat audit crossed science boundary")
    req(sha(ACTOR) == EXPECTED_ACTOR_SHA, "generic actor SHA drift")
    req(sha(suite_manifest_path) == EXPECTED_SUITE_SHA, "suite manifest drift")
    req(sha(split_path) == EXPECTED_COMPAT_SPLIT_SHA, "compat split drift")
    req(sha(meta_path) == EXPECTED_COMPAT_META_SHA, "compat metadata drift")
    req(sha(args.runtime_freeze) == EXPECTED_RUNTIME_FREEZE_SHA, "runtime freeze drift")
    req(sha(args.runtime_qualification) == EXPECTED_RUNTIME_QUAL_SHA, "runtime qualification drift")
    req(sha(initial_skill) == EXPECTED_INITIAL_SKILL_SHA, "initial skill drift")
    req(runtime_q["status"] == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification not passing")
    req(runtime_q["venv_root"] == str(args.runtime_venv), "runtime venv drift")

    head = subprocess.run(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    req(head == EXPECTED_MINDMEMOS_COMMIT, "MindMemOS commit drift")

    req(identity["status"] == "PASS" and len(identity["models"]) == 1, "identity qualification invalid")
    model = identity["models"][0]
    req(model["requested_model"] == "deepseek-v4-pro", "requested model drift")
    req(model["resolved_model"] == "deepseek-v4-pro-ga-260813", "exact resolved model drift")
    req(model["provider_retry_limit"] == 0 and model["thinking_requested"] == "disabled", "identity flags drift")

    streams = {str(k): list(map(str, v)) for k, v in split["e1_update_streams"].items()}
    heldout = list(map(str, split["e1_common_heldout_probe"]))
    all_tasks = [task for tasks in streams.values() for task in tasks]
    req(len(streams) == 12 and all(len(tasks) == 8 for tasks in streams.values()), "Stage-A stream shape drift")
    req(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "Stage-A task uniqueness drift")
    req(len(heldout) == 18 and set(all_tasks).isdisjoint(heldout), "Stage-A heldout separation drift")
    req(suite_manifest["provider_calls"] == 0 and suite_manifest["scientific_outcomes_accessed"] is False, "suite crossed provider/outcome boundary")

    actor_help = subprocess.run([str(runtime_python), str(ACTOR), "--help"], capture_output=True, text=True, check=False)
    req(actor_help.returncode == 0, "generic actor cannot import/parse under frozen runtime")
    actor = import_actor_module()
    guard_checks = check_scope_guards(actor, split, all_tasks, heldout)
    req(all(guard_checks.values()), f"actor execution-scope guard preflight failed: {guard_checks}")

    runtime_smoke = subprocess.run(
        [
            str(runtime_python),
            "-c",
            "from mindmemos_eval.skills.agents import ReactAgentFactory; from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv; import openpyxl",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    req(runtime_smoke.returncode == 0, "Stage-A frozen runtime smoke failed")

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    contract = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-contract",
        "created_at_utc": created_at,
        "status": "FROZEN_SEMANTIC_TRANSFER_V1_STAGE_A_PENDING_REVIEW",
        "scientific_role": "search-pool acquisition and equal-dose support qualification only",
        "runtime_compat_audit": {"path": str(args.runtime_compat_audit), "sha256": sha(args.runtime_compat_audit)},
        "model_identity": {
            "path": str(args.identity),
            "sha256": sha(args.identity),
            "requested": "deepseek-v4-pro",
            "resolved": "deepseek-v4-pro-ga-260813",
        },
        "suite": {
            "root": str(args.suite_root),
            "suite_manifest_sha256": sha(suite_manifest_path),
            "split_manifest_sha256": sha(split_path),
            "metadata_sha256": sha(meta_path),
            "streams": list(streams.keys()),
            "allowed_task_ids": all_tasks,
            "heldout_task_ids_forbidden": heldout,
        },
        "mindmemos": {
            "root": str(args.mindmemos_root),
            "commit": head,
            "initial_skill_path": str(initial_skill),
            "initial_skill_sha256": sha(initial_skill),
        },
        "runtime": {
            "venv_root": str(args.runtime_venv),
            "python_executable": str(runtime_python),
            "freeze_path": str(args.runtime_freeze),
            "freeze_sha256": sha(args.runtime_freeze),
            "qualification_path": str(args.runtime_qualification),
            "qualification_sha256": sha(args.runtime_qualification),
        },
        "bound_code": {
            "actor": {"path": "scripts/run_e2_r17_actor_pool.py", "sha256": sha(ACTOR)},
        },
        "actor": {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "k": 8,
            "prefix_ks": [1, 2, 4, 8],
            "temperature": 0,
            "thinking": "disabled",
            "provider_retry_limit": 0,
            "max_turns": 10,
            "max_output_tokens": 8192,
            "concurrency": 1,
        },
        "budget": {
            "actor_rollouts": 768,
            "max_provider_calls": 7680,
            "provider_calls_per_rollout_limit": 10,
        },
        "equal_dose_support": {
            "required_mixed_pools_per_stream": 4,
            "streams_required": 12,
            "treated_mixed_pools_per_stream": 4,
            "treated_pool_selection": "lowest SHA256(semantic-transfer-mrw4-v1|stream_id|task_id) among mixed pools",
            "stage_b_treated_pool_ids_must_be_frozen_before_updater": True,
            "failure_status": "HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
        },
        "run_root": str(args.run_root),
        "exactly_once": {
            "completed_rollout_replay": False,
            "automatic_retry": False,
            "replacement_sampling": False,
            "resume_requires_separate_adjudication": True,
        },
        "authority": {
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
        },
        "partial_effect_read": False,
        "scientific_scores_read": False,
    }
    write_json(args.contract_output, contract)
    contract_sha = sha(args.contract_output)

    preflight = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_STAGE_A_ACTUAL_PATH_PREFLIGHT",
        "contract_path": str(args.contract_output),
        "contract_sha256": contract_sha,
        "provider_calls": 0,
        "scientific_execution": False,
        "new_test_outcomes_accessed": False,
        "run_root_exists": args.run_root.exists(),
        "actor_help_under_frozen_runtime_pass": True,
        "runtime_import_smoke_pass": True,
        "execution_scope_guard_checks": guard_checks,
        "stream_count": 12,
        "task_count": 96,
        "heldout_forbidden_count": 18,
        "exact_k": 8,
        "max_provider_calls": 7680,
        "updater_authority": False,
        "heldout_evaluation_authority": False,
        "authority": {
            "mint_stage_a_authorization": False,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False,
        },
        "next_gate": "INDEPENDENT_PREEXECUTION_REVIEW_BEFORE_SINGLE_USE_STAGE_A_AUTHORIZATION",
    }
    req(preflight["run_root_exists"] is False, "preflight unexpectedly created run root")
    write_json(args.preflight_output, preflight)
    print(json.dumps({"contract_status": contract["status"], "contract_sha256": contract_sha, "preflight_status": preflight["status"], "scope_guards": guard_checks, "next_gate": preflight["next_gate"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
