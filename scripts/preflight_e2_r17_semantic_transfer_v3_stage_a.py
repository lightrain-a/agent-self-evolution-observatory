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

CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A"


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


def dotenv_value(path: Path, key: str) -> str | None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() != key:
            continue
        value = v.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value
    return None


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
    req(not args.output.exists(), "V3 preflight output already exists")
    contract = load(args.contract)
    contract_sha = sha(args.contract)
    req(contract.get("status") == CONTRACT_STATUS, "V3 contract status invalid")
    req(contract.get("authority", {}).get("stage_a_provider_execution") is False, "draft V3 contract cannot self-authorize")

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        req(path.is_file(), f"missing bound code: {label}")
        req(sha(path) == item["sha256"], f"bound code SHA drift: {label}")

    env_file = Path(contract["env_file_path"]).resolve()
    req(env_file.is_file(), "contract-bound env file missing")
    req((dotenv_value(env_file, "ARK_BASE_URL") or "https://ark.cn-beijing.volces.com/api/plan/v3").rstrip("/") == "https://ark.cn-beijing.volces.com/api/plan/v3", "contract-bound env file is not Ark Plan route")
    req(bool((dotenv_value(env_file, "ARK_API_KEY") or "").strip()), "contract-bound env file lacks ARK_API_KEY")

    identity_policy = contract.get("model_identity_policy") or {}
    req(identity_policy.get("requested_model") == "deepseek-v4-pro", "model identity requested-name drift")
    req(identity_policy.get("required_resolved_model") == "deepseek-v4-pro-ga-260813", "model identity exact suffix policy drift")
    req(identity_policy.get("fresh_requalification_required_before_authorization") is True, "fresh identity requirement missing")
    req(identity_policy.get("provider_retry_limit") == 0 and identity_policy.get("thinking") == "disabled", "identity runtime policy drift")

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
    req(len(all_tasks) == 160 and len(set(all_tasks)) == 160, "V3 update task shape invalid")
    req(len(heldout) == 20 and len(set(heldout)) == 20 and set(all_tasks).isdisjoint(heldout), "V3 heldout separation invalid")

    exact_once = contract.get("exact_once_acquisition") or {}
    req(exact_once.get("required") is True, "V3 exact-once acquisition policy missing")
    unit_manifest_raw = str(exact_once.get("unit_manifest_path") or "")
    unit_manifest_path = Path(unit_manifest_raw) if Path(unit_manifest_raw).is_absolute() else ROOT / unit_manifest_raw
    req(unit_manifest_path.is_file() and sha(unit_manifest_path) == exact_once.get("unit_manifest_sha256"), "V3 exact-once unit manifest drift")
    unit_manifest = load(unit_manifest_path)
    req([str(value) for value in unit_manifest.get("ordered_task_ids") or []] == all_tasks, "V3 exact-once unit universe/order drift")
    req(int(exact_once.get("unit_count") or 0) == 160, "V3 exact-once unit cardinality drift")
    req(Path(str(exact_once.get("claim_root") or "")).resolve() == (Path(contract["run_root"]) / "checkpoints/stage_a_task_claims").resolve(), "V3 exact-once claim root drift")
    req(exact_once.get("attempt_before_any_provider_io") is True, "V3 exact-once burn timing drift")
    req(exact_once.get("attempt_marker_immutable") is True and exact_once.get("sealed_receipt_after_frozen_k8_pool") is True, "V3 exact-once marker semantics drift")
    req(exact_once.get("replay_allowed") is False and exact_once.get("ambiguous_recollection_allowed") is False, "V3 exact-once replay policy drift")
    req(exact_once.get("replacement_sampling_allowed") is False, "V3 exact-once replacement-sampling policy drift")

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
    req(not run_root.exists(), "V3 run root already exists")
    req(not lease_path.exists(), "V3 global lease already exists")

    actor_path = ROOT / contract["bound_code"]["actor"]["path"]
    actor_source = actor_path.read_text(encoding="utf-8")
    req("primary_failure_family" not in actor_source, "V3 actor reintroduced legacy family metadata")
    req("metadata[task_id][\"semantic_type\"]" not in actor_source, "V3 actor reads hidden semantic label")
    req("metadata[task_id][\"matched_skeleton\"]" not in actor_source, "V3 actor reads hidden skeleton label")
    actor = import_module(actor_path, "semantic_transfer_v3_actor_preflight")
    # Synthetic authorization exists only in a private temporary file and is
    # used to exercise the exact V3-actor scope checks without provider I/O.
    synthetic = {
        "status": "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A",
        "authority": {
            "stage_a_provider_execution": True,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "contract_sha256": contract_sha,
        "mindmemos_commit": contract["mindmemos"]["commit"],
        "execution_scope": {
            "allowed_modes": ["e1"],
            "allowed_task_ids": all_tasks,
            "exact_k": 8,
            "exact_prefix_ks": [1, 2, 4, 8],
            "exact_concurrency": contract["actor"]["concurrency"],
            "required_run_root": contract["run_root"],
            "runner_lease_required": True,
            "allow_noninitial_skill": False,
            "required_skill_pre_sha256": contract["mindmemos"]["initial_skill_sha256"],
            "required_resolved_model": "deepseek-v4-pro-ga-260813",
            "identity_artifact_sha256": "f" * 64,
            "suite_manifest_sha256": contract["suite"]["suite_manifest_sha256"],
            "split_manifest_sha256": contract["suite"]["split_manifest_sha256"],
            "max_turns": contract["actor"]["max_turns"],
            "max_output_tokens": contract["actor"]["max_output_tokens"],
            "provider_budget": {
                "required": True,
                "total_limit": contract["budget"]["max_provider_calls"],
                "per_unit_limit": contract["budget"]["provider_calls_per_rollout_limit"],
            },
            "exact_once_acquisition": {
                "required": True,
                "unit_manifest_path": exact_once["unit_manifest_path"],
                "unit_manifest_sha256": exact_once["unit_manifest_sha256"],
                "unit_count": 160,
                "required_claim_root": exact_once["claim_root"],
                "attempt_before_any_provider_io": True,
                "replay_allowed": False,
                "ambiguous_recollection_allowed": False,
            },
            "global_lease_path": contract["global_lease_path"],
        },
        "fresh_model_identity": {"path": "synthetic-identity.json", "sha256": "f" * 64},
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
        req(all(guards.values()), f"V3 actor scope guards failed: {guards}")
        runner_path = ROOT / contract["bound_code"]["stage_a_runner"]["path"]
        exact_scope = actor.validate_exact_once_acquisition_scope(
            authorization_payload=synthetic,
            run_root=Path(contract["run_root"]),
            requested_task_ids=all_tasks[:8],
        )
        req(exact_scope is not None and Path(exact_scope["claim_root"]).resolve() == Path(exact_once["claim_root"]).resolve(), "actor exact-once scope preflight failed")
        guards["actor_exact_once_scope_valid"] = True
        runner = import_module(runner_path, "semantic_transfer_v3_stage_a_runner_preflight")
        runner.verify_authorization_scope(contract, synthetic, all_tasks, heldout)
        guards["runner_exact_authorization_schema"] = True
    finally:
        synthetic_path.unlink(missing_ok=True)

    # Import the actual V3 control-plane modules under the frozen runtime/Python
    # parser so syntax/import failures are caught before review/authorization.
    runner_path = ROOT / contract["bound_code"]["stage_a_runner"]["path"]
    adjudicator_path = ROOT / contract["bound_code"]["equal_dose_adjudicator"]["path"]
    authorizer_path = ROOT / contract["bound_code"]["authorization_minter"]["path"]
    stage_b_order_path = ROOT / contract["bound_code"]["stage_b_order_helper"]["path"]
    for path in (runner_path, adjudicator_path, authorizer_path, stage_b_order_path):
        check = subprocess.run([str(runtime_python), "-m", "py_compile", str(path)], capture_output=True, text=True, check=False)
        req(check.returncode == 0, f"V3 bound code compile failed: {path.name}")
    stage_b_order = import_module(stage_b_order_path, "semantic_transfer_v3_stage_b_order_preflight")
    sample_order = stage_b_order.update_pool_order("synthetic-stream", 0, [f"task-{i}" for i in range(8)])
    req(len(sample_order) == 8 and len(set(sample_order)) == 8, "Stage-B common update order helper invalid")
    guards["stage_b_arm_blind_task_order_valid"] = True

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_PREFLIGHT",
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "provider_calls": 0,
        "scientific_execution": False,
        "new_test_outcomes_accessed": False,
        "run_root_exists": False,
        "global_lease_exists": False,
        "stream_count": 20,
        "task_count": 160,
        "heldout_forbidden_count": 20,
        "env_file_path": str(env_file),
        "ark_plan_route_verified_without_exposing_key": True,
        "fresh_identity_qualified": False,
        "fresh_identity_required_before_authorization": True,
        "required_resolved_model": identity_policy["required_resolved_model"],
        "runtime_import_smoke_pass": True,
        "scope_guard_checks": guards,
        "bound_code_compile_pass": True,
        "exactly_once": contract["exactly_once"],
        "exact_once_acquisition": exact_once,
        "stage_b_ordering_prospectively_frozen": True,
        "authority": {
            "mint_stage_a_authorization": False,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False
        },
        "next_gate": "FRESH_GPT56_SOL_EXTREME_WEB_REVIEW_AND_FRESH_IDENTITY_BEFORE_SINGLE_USE_STAGE_A_AUTHORIZATION"
    }
    atomic_json(args.output, payload)
    print(json.dumps({"status": payload["status"], "contract_sha256": contract_sha, "scope_guard_checks": guards, "next_gate": payload["next_gate"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
