#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
import scripts.run_e2_r17_e1_a_pool_support as legacy

ACTOR = ROOT / "scripts/run_e2_r17_actor_pool.py"
EXPECTED_CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V2_STAGE_A_V5"
EXPECTED_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V2_STAGE_A_V5"
EXPECTED_IDENTITY_STATUS = "PASS_CURRENT_REVIEW_TRANCHE"


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
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def acquire_exclusive_file(path: Path, payload: dict[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"exclusive scientific lineage object already exists: {path}") from exc
    os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
    os.fsync(fd)
    return fd


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    contract_sha = sha_file(contract_path)
    auth_sha = sha_file(auth_path)
    require(contract.get("status") == EXPECTED_CONTRACT_STATUS, "Stage-A V5 contract status invalid")
    require(auth.get("status") == EXPECTED_AUTH_STATUS, "Stage-A V5 authorization status invalid")
    require(auth.get("contract_sha256") == contract_sha, "authorization does not bind exact Stage-A V5 contract")
    authority = auth.get("authority") or {}
    require(authority.get("stage_a_provider_execution") is True, "Stage-A provider execution authority absent")
    for forbidden in ("stage_b_learning_execution", "updater", "heldout_evaluation", "analyzer", "second_backbone", "public_benchmark", "paper_promotion"):
        require(authority.get(forbidden) is False, f"Stage-A authorization overbroad: {forbidden}")
    return contract, auth, contract_sha, auth_sha


def verify_bound_code(contract: dict[str, Any]) -> None:
    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / str(item["path"])
        require(path.is_file(), f"missing bound code: {label}")
        require(sha_file(path) == str(item["sha256"]), f"bound code drift: {label}")


def verify_authorization_scope(contract: dict[str, Any], auth: dict[str, Any], all_tasks: list[str], heldout: list[str]) -> None:
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "authorization mode scope must be exactly e1")
    require(set(map(str, scope.get("allowed_task_ids") or [])) == set(all_tasks), "authorization task scope drift")
    require(int(scope.get("exact_k") or 0) == 8, "authorization exact K drift")
    require(scope.get("required_resolved_model") == "deepseek-v4-pro-ga-260813", "authorization exact model identity drift")
    fresh_identity = auth.get("fresh_model_identity") or {}
    require(bool(fresh_identity.get("path")) and bool(fresh_identity.get("sha256")), "authorization fresh identity binding missing")
    require(scope.get("identity_artifact_sha256") == fresh_identity.get("sha256"), "authorization fresh identity SHA drift")
    require(scope.get("required_skill_pre_sha256") == contract["mindmemos"]["initial_skill_sha256"], "authorization initial skill drift")
    require(scope.get("suite_manifest_sha256") == contract["suite"]["suite_manifest_sha256"], "authorization suite SHA drift")
    require(scope.get("split_manifest_sha256") == contract["suite"]["split_manifest_sha256"], "authorization split SHA drift")
    require(int(scope.get("max_turns") or 0) == int(contract["actor"]["max_turns"]), "authorization max_turns drift")
    require(int(scope.get("max_output_tokens") or 0) == int(contract["actor"]["max_output_tokens"]), "authorization max_output_tokens drift")
    provider = scope.get("provider_budget") or {}
    require(provider.get("required") is True, "authorization must require provider budget ledger")
    require(int(provider.get("total_limit") or 0) == int(contract["budget"]["max_provider_calls"]), "authorization total provider budget drift")
    require(int(provider.get("per_unit_limit") or 0) == int(contract["budget"]["provider_calls_per_rollout_limit"]), "authorization per-unit provider budget drift")
    require(set(heldout).isdisjoint(scope.get("allowed_task_ids") or []), "authorization accidentally includes heldout task")
    require(scope.get("global_lease_path") == contract["global_lease_path"], "authorization global lease path drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()

    contract, auth, contract_sha, auth_sha = validate_contract_auth(args.contract, args.authorization)
    verify_bound_code(contract)
    bound_env = Path(contract["env_file_path"]).resolve()
    require(bound_env.is_file(), "contract-bound env file missing")
    require(args.env_file.resolve() == bound_env, "Stage-A V5 env-file path drift")

    suite_root = Path(contract["suite"]["root"])
    split_path = suite_root / "r17_split_manifest.json"
    metadata_path = suite_root / "r17_controlled_metadata.json"
    suite_manifest = suite_root / "suite_manifest.json"
    for path, expected in (
        (suite_manifest, contract["suite"]["suite_manifest_sha256"]),
        (split_path, contract["suite"]["split_manifest_sha256"]),
        (metadata_path, contract["suite"]["metadata_sha256"]),
    ):
        require(path.is_file() and sha_file(path) == expected, f"suite binding drift: {path.name}")
    split = load_json(split_path)
    streams = {str(k): [str(x) for x in v] for k, v in split["e1_update_streams"].items()}
    stream_ids = list(contract["suite"]["streams"])
    require(list(streams) == stream_ids, "Stage-A V5 stream ordering drift")
    all_tasks = [task for stream_id in stream_ids for task in streams[stream_id]]
    require(len(all_tasks) == 144 and len(set(all_tasks)) == 144, "Stage-A V5 task set drift")
    heldout = [str(x) for x in split["e1_common_heldout_probe"]]
    require(len(heldout) == 18 and len(set(heldout)) == 18 and set(all_tasks).isdisjoint(heldout), "Stage-A heldout separation drift")
    verify_authorization_scope(contract, auth, all_tasks, heldout)

    fresh_identity = auth.get("fresh_model_identity") or {}
    identity_path_raw = Path(str(fresh_identity.get("path") or ""))
    identity_path = identity_path_raw if identity_path_raw.is_absolute() else ROOT / identity_path_raw
    require(identity_path.is_file() and sha_file(identity_path) == fresh_identity.get("sha256"), "fresh model identity binding drift")
    identity = load_json(identity_path)
    require(identity.get("status") == EXPECTED_IDENTITY_STATUS, "fresh model identity adjudication not passing")
    model_row = (identity.get("requested_and_resolved") or {}).get("deepseek-v4-pro") or {}
    require(model_row.get("resolved") == "deepseek-v4-pro-ga-260813", "exact resolved DeepSeek identity drift")
    require(model_row.get("thinking") == "disabled" and model_row.get("provider_retry_limit") is not None and int(model_row["provider_retry_limit"]) == 0, "fresh identity runtime flags drift")

    runtime_python, runtime_env = legacy.validate_runtime(contract)
    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    initial_skill = Path(contract["mindmemos"]["initial_skill_path"])
    require(initial_skill.is_file() and sha_file(initial_skill) == contract["mindmemos"]["initial_skill_sha256"], "initial skill drift")

    run_root = Path(contract["run_root"])
    summary_path = run_root / "summary/stage_a_pool_freeze_summary.json"
    require(not run_root.exists(), "Stage-A V5 run root already exists; resume requires separate adjudication")
    require(not summary_path.exists(), "Stage-A V5 terminal summary already exists")

    global_lease_path = Path(contract["global_lease_path"])
    lease_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v2-stage-a-global-lineage-lease",
        "status": "RUNNING_STAGE_A_V5",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pid": os.getpid(),
        "pgid": os.getpgrp(),
        "hostname": socket.gethostname(),
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "run_root": str(run_root),
        "exactly_once": True,
        "partial_effect_read": False,
    }
    lease_fd = acquire_exclusive_file(global_lease_path, lease_payload)
    os.close(lease_fd)

    local_lock = run_root / ".exclusive.lock"
    lock_fd: int | None = None
    success = False
    try:
        run_root.mkdir(parents=True, exist_ok=False)
        lock_fd = acquire_exclusive_file(
            local_lock,
            {
                "pid": os.getpid(),
                "pgid": os.getpgrp(),
                "hostname": socket.gethostname(),
                "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "contract_sha256": contract_sha,
                "authorization_sha256": auth_sha,
            },
        )
        manifest_path = run_root / "checkpoints/completed_streams.jsonl"
        failure_root = run_root / "checkpoints/failures"
        summary_root = run_root / "summary/streams"
        budget_ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
        provider_budget = ProviderBudgetLedger(
            path=budget_ledger_path,
            contract_sha256=contract_sha,
            authorization_sha256=auth_sha,
            total_limit=int(contract["budget"]["max_provider_calls"]),
            per_unit_limit=int(contract["budget"]["provider_calls_per_rollout_limit"]),
            allow_create=True,
        )

        # First-run-only runner: no inherited/completed stream is accepted at start.
        require(not manifest_path.exists(), "first-run Stage-A V5 unexpectedly has a completed-stream manifest")
        completed_rows: dict[str, dict[str, Any]] = {}
        for stream_id in stream_ids:
            output = summary_root / f"{stream_id}.json"
            command = [
                str(runtime_python),
                str(ACTOR),
                "--env-file", str(args.env_file),
                "--suite-root", str(suite_root),
                "--mindmemos-root", str(mind_root),
                "--run-root", str(run_root),
                "--identity", str(identity_path),
                "--authorization", str(args.authorization),
                "--mode", "e1",
                "--model", "deepseek-v4-pro",
                "--stream-id", stream_id,
                "--k", "8",
                "--prefix-ks", "1,2,4,8",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", str(contract["actor"]["concurrency"]),
                "--provider-budget-ledger", str(budget_ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["budget"]["provider_calls_per_rollout_limit"]),
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, env=runtime_env, capture_output=True, text=True)
            if result.returncode != 0:
                failure = {
                    "schema_version": "1.0",
                    "artifact_type": "e2-r17-semantic-transfer-stage-a-stream-failure",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "stream_id": stream_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-3000:],
                    "stderr_tail": result.stderr[-3000:],
                    "provider_relaunch_authorized": False,
                    "partial_effect_read": False,
                    "instruction": "Fail closed. Preserve global lease and run root. Do not resume without separate adjudication/authorization.",
                }
                atomic_json(failure_root / f"{stream_id}.json", failure)
                raise RuntimeError(f"Stage-A V5 stream failed: {stream_id}")
            require(output.is_file(), f"Stage-A actor returned success without output: {stream_id}")
            row = {
                "stream_id": stream_id,
                "summary_path": str(output),
                "summary_sha256": sha_file(output),
                "task_ids": streams[stream_id],
                "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            append_jsonl(manifest_path, row)
            completed_rows[stream_id] = row

        # Only after all 18 streams have completed do we open/validate stream summaries.
        require(len(completed_rows) == 18, "Stage-A V5 did not complete all streams")
        total_rollouts = 0
        total_provider_receipts = 0
        for stream_id in stream_ids:
            row = completed_rows[stream_id]
            legacy.verify_stream_receipt(row, run_root, provider_budget)
            stream_summary = load_json(Path(row["summary_path"]))
            require(stream_summary.get("status") == "COMPLETED", f"stream summary status invalid: {stream_id}")
            require(stream_summary.get("contract_sha256") == contract_sha, f"stream contract binding drift: {stream_id}")
            require(stream_summary.get("authorization_sha256") == auth_sha, f"stream authorization binding drift: {stream_id}")
            require(stream_summary.get("resolved_model") == "deepseek-v4-pro-ga-260813", f"stream model identity drift: {stream_id}")
            require(int(stream_summary.get("k") or 0) == 8, f"stream K drift: {stream_id}")
            tasks = stream_summary.get("tasks") or []
            require(len(tasks) == 8, f"stream task cardinality drift: {stream_id}")
            total_rollouts += 8 * len(tasks)
            total_provider_receipts += sum(int(task.get("provider_calls") or 0) for task in tasks)

        require(total_rollouts == 1152, f"Stage-A V5 rollout count drift: {total_rollouts}")
        snapshot = provider_budget.snapshot()
        require(snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]), "provider budget exceeded")
        require(snapshot.total_claimed >= total_provider_receipts, "provider receipts exceed pre-I/O claims")
        # Ensure forbidden heldout namespace was never created.
        touched_heldout = [task_id for task_id in heldout if (run_root / "cases" / task_id).exists()]
        require(not touched_heldout, f"Stage-A V5 touched forbidden heldout tasks: {touched_heldout}")

        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-semantic-transfer-v2-stage-a-pool-freeze-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "COMPLETED_ALL_144_POOLS_PENDING_EQUAL_DOSE_ADJUDICATION",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "model_identity_sha256": sha_file(identity_path),
            "mindmemos_commit": head,
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "runtime_qualification_sha256": contract["runtime"]["qualification_sha256"],
            "streams": 18,
            "tasks": 144,
            "actor_rollouts": total_rollouts,
            "provider_receipts": total_provider_receipts,
            "provider_budget": snapshot.to_dict(),
            "updater_calls": 0,
            "heldout_evaluations": 0,
            "partial_effect_read": False,
            "scientific_scores_read": False,
            "support_inspected": False,
            "stage_b_authority": False,
            "paper_promotion_authority": False,
            "completed_stream_manifest_path": str(manifest_path),
            "completed_stream_manifest_sha256": sha_file(manifest_path),
        }
        atomic_json(summary_path, final)

        terminal_lease = {
            **lease_payload,
            "status": "COMPLETED_STAGE_A_V5_PENDING_EQUAL_DOSE_ADJUDICATION",
            "sealed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "summary_path": str(summary_path),
            "summary_sha256": sha_file(summary_path),
            "provider_budget_total_claimed": snapshot.total_claimed,
        }
        atomic_json(global_lease_path, terminal_lease)
        success = True
        print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        if success:
            local_lock.unlink(missing_ok=True)
        # On failure the global lease intentionally remains RUNNING and the
        # local lock remains present; neither is automatically cleared.


if __name__ == "__main__":
    raise SystemExit(main())
