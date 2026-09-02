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

ACTOR = ROOT / "scripts/run_e2_r18_actor_pool_stage_a.py"
EXPECTED_AUTH_STATUS = "AUTHORIZED_E2_R18_DIAGNOSTIC_VALUE_STAGE_A"
EXPECTED_CONTRACT_STATUS = "FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def manifest_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["stream_id"])] = row
    return rows


def verify_stream_receipt(
    row: dict[str, Any],
    run_root: Path,
    provider_budget_ledger: ProviderBudgetLedger | None = None,
) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.exists(), f"missing completed stream summary: {summary_path}")
    require(sha_file(summary_path) == row["summary_sha256"], f"completed stream summary SHA drift: {row['stream_id']}")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED", f"stream summary not completed: {row['stream_id']}")
    tasks = summary.get("tasks") or []
    require(len(tasks) == 8, f"completed stream does not contain eight tasks: {row['stream_id']}")
    for task in tasks:
        task_id = str(task["task_id"])
        task_dir = run_root / "cases" / task_id
        for k in (1, 2, 4, 8):
            pool = task_dir / f"pool_k{k}.json"
            require(pool.exists(), f"missing frozen K={k} pool for {task_id}")
        for rollout in range(8):
            ref = task_dir / f"rollout_{rollout}" / "r17_trajectory_ref.json"
            require(ref.exists(), f"missing trajectory ref {task_id}/{rollout}")
            ref_payload = load_json(ref)
            trajectory = Path(ref_payload["trajectory_path"])
            require(trajectory.exists(), f"missing trajectory bound by {ref}")
            require(sha_file(trajectory) == ref_payload["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{rollout}")
            if provider_budget_ledger is not None:
                unit_id = f"{task_id}/rollout_{rollout}"
                require(ref_payload.get("provider_budget_unit_id") == unit_id, f"provider budget unit id drift: {unit_id}")
                claim_count = int(ref_payload.get("provider_budget_claim_count") or 0)
                require(claim_count >= 1, f"completed R18 Stage A rollout lacks provider budget claims: {unit_id}")
                raw = load_json(trajectory)
                claims = raw.get("provider_budget_claims") or []
                require(len(claims) == claim_count, f"provider budget claim count drift: {unit_id}")
                claim_sha = hashlib.sha256(
                    json.dumps(claims, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                require(claim_sha == ref_payload.get("provider_budget_claim_bundle_sha256"), f"provider budget claim SHA drift: {unit_id}")
                snapshot = provider_budget_ledger.snapshot()
                unit_claimed = int(snapshot.unit_claimed.get(unit_id, 0))
                require(
                    unit_claimed == int(ref_payload.get("provider_budget_unit_claimed_after") or -1),
                    f"provider budget ledger/ref unit count drift: {unit_id}",
                )
                require(
                    snapshot.total_claimed >= int(ref_payload.get("provider_budget_total_claimed_after") or -1),
                    f"provider budget total counter regressed: {unit_id}",
                )


def acquire_lock(path: Path, *, contract_sha: str, authorization_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(
            f"exclusive lock already exists: {path}; inspect process/checkpoints before any resume"
        ) from exc
    payload = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
    }
    os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
    os.fsync(fd)
    return fd



def acquire_global_lease(path: Path, *, contract_sha: str, authorization_sha: str, prereg_sha: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r18-stage-a-global-lineage-lease",
        "status": "RUNNING_R18_STAGE_A",
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "preregistration_sha256": prereg_sha,
    }
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"R18 global lineage lease already exists: {path}") from exc
    try:
        os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")); os.fsync(fd)
    finally:
        os.close(fd)

def seal_global_lease(path: Path, *, contract_sha: str, authorization_sha: str, prereg_sha: str) -> None:
    atomic_json(path, {
        "schema_version": "1.0",
        "artifact_type": "e2-r18-stage-a-global-lineage-lease",
        "status": "COMPLETED_R18_STAGE_A",
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "preregistration_sha256": prereg_sha,
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

def validate_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    runtime = contract.get("runtime") or {}
    venv = Path(str(runtime.get("venv_root") or ""))
    python = Path(str(runtime.get("python_executable") or ""))
    freeze = Path(str(runtime.get("freeze_path") or ""))
    qualification = Path(str(runtime.get("qualification_path") or ""))
    require(venv.is_dir(), f"frozen runtime venv missing: {venv}")
    require(python.is_file(), f"frozen runtime python missing: {python}")
    require(python == venv / "bin/python", "runtime python must be exact venv/bin/python")
    require(freeze.is_file(), f"runtime freeze missing: {freeze}")
    require(sha_file(freeze) == runtime.get("freeze_sha256"), "runtime freeze SHA drift")
    require(qualification.is_file(), f"runtime qualification artifact missing: {qualification}")
    require(sha_file(qualification) == runtime.get("qualification_sha256"), "runtime qualification SHA drift")
    q = load_json(qualification)
    require(q.get("status") == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification status invalid")
    require(q.get("venv_root") == str(venv), "runtime qualification venv drift")
    require(q.get("freeze_sha256") == runtime.get("freeze_sha256"), "runtime qualification freeze drift")
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = str(venv / "bin") + os.pathsep + env.get("PATH", "")
    smoke = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import openpyxl,pydantic; "
                "assert openpyxl.__version__ == '3.1.5'; "
                "from mindmemos_eval.skills.agents import ReactAgentFactory; "
                "from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv"
            ),
        ],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    require(smoke.returncode == 0, "frozen full MindMemOS runtime import smoke failed")
    return python, env


def validate_contract_and_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == EXPECTED_CONTRACT_STATUS, "R18 Stage A contract is not frozen")
    require(auth.get("status") == EXPECTED_AUTH_STATUS, "R18 Stage A authorization status invalid")
    require(auth.get("authority", {}).get("scientific_experiment") is True, "E1-A scientific authority false")
    require(auth.get("authority", {}).get("r18_stage_a_pool_support") is True, "R18 Stage A authority bit false")
    for forbidden in ("updater", "heldout_evaluation", "analyzer", "paper_promotion", "second_backbone", "public_benchmark"):
        require(auth.get("authority", {}).get(forbidden) is False, f"R18 Stage A authorization overbroad: {forbidden}")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization does not bind exact R18 Stage A contract")
    preflight_path = Path(str(auth.get("actual_path_preflight_path") or ""))
    require(preflight_path.is_file(), "R18 Stage A execution authorization lacks actual-path preflight")
    require(sha_file(preflight_path) == auth.get("actual_path_preflight_sha256"), "R18 Stage A preflight SHA drift")
    preflight = load_json(preflight_path)
    require(preflight.get("status") == "PASS_R18_STAGE_A_ACTUAL_PATH_12_OF_12_ZERO_PROVIDER", "R18 Stage A preflight not passing")
    require(preflight.get("contract_sha256") == sha_file(contract_path), "R18 Stage A preflight contract drift")
    require(preflight.get("provider_calls") == 0 and preflight.get("provider_claims") == 0, "R18 Stage A preflight crossed provider boundary")
    return contract, auth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()

    contract, auth = validate_contract_and_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        require(path.exists() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    identity = ROOT / contract["model_identity"]["path"]
    require(identity.exists() and sha_file(identity) == contract["model_identity"]["sha256"], "model identity artifact drift")
    identity_payload = load_json(identity)
    require(identity_payload.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "actor model identity adjudication not passing")

    suite_root = Path(contract["suite"]["root"])
    split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"], "suite manifest drift")
    require(sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "split manifest drift")
    require(sha_file(suite_root / "r17_controlled_metadata.json") == contract["suite"]["metadata_sha256"], "controlled metadata drift")
    split = load_json(split_path)
    streams = split["e3_future_streams"]
    frozen_stream_ids = list(contract["streams"])
    require(list(streams.keys()) == frozen_stream_ids, "stream ordering/content drift from frozen contract")
    all_tasks = [str(task) for stream_id in frozen_stream_ids for task in streams[stream_id]]
    require(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "R18 Stage A must bind 96 unique untouched future tasks")
    scope = auth.get("execution_scope") or {}
    require(set(scope.get("allowed_task_ids") or []) == set(all_tasks), "authorization task scope does not equal frozen 96 tasks")
    require(scope.get("allowed_modes") == ["e1"], "authorization mode scope must be exactly e1")
    require(int(scope.get("exact_k")) == 8, "authorization must bind exact K=8")
    runtime = contract.get("runtime") or {}
    require(
        scope.get("runtime_python_executable") == runtime.get("python_executable"),
        "authorization runtime python drift",
    )
    require(scope.get("runtime_freeze_sha256") == runtime.get("freeze_sha256"), "authorization runtime freeze drift")
    require(
        scope.get("runtime_qualification_sha256") == runtime.get("qualification_sha256"),
        "authorization runtime qualification drift",
    )

    runtime_python, runtime_env = validate_runtime(contract)

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    initial_skill = mind_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    require(sha_file(initial_skill) == contract["mindmemos"]["initial_skill_sha256"], "initial skill drift")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["global_lineage_lease"]["path"])
    acquire_global_lease(lease_path, contract_sha=contract_sha, authorization_sha=auth_sha, prereg_sha=contract["preregistration"]["sha256"])
    lock_path = run_root / ".exclusive.lock"
    manifest_path = run_root / "checkpoints/completed_streams.jsonl"
    summary_root = run_root / "summary/streams"
    failure_root = run_root / "checkpoints/failures"
    budget_ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    lock_fd = acquire_lock(lock_path, contract_sha=contract_sha, authorization_sha=auth_sha)
    provider_budget_ledger = ProviderBudgetLedger(
        path=budget_ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["actor"]["max_turns"]),
        allow_create=not budget_ledger_path.exists(),
    )
    success = False
    try:
        completed = manifest_rows(manifest_path)
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        for stream_id in frozen_stream_ids:
            if stream_id in completed:
                continue
            output = summary_root / f"{stream_id}.json"
            command = [
                str(runtime_python),
                str(ACTOR),
                "--env-file", str(args.env_file),
                "--suite-root", str(suite_root),
                "--mindmemos-root", str(mind_root),
                "--run-root", str(run_root),
                "--identity", str(identity),
                "--authorization", str(args.authorization),
                "--mode", "e1",
                "--model", contract["actor"]["requested_model"],
                "--stream-id", stream_id,
                "--k", "8",
                "--prefix-ks", "1,2,4,8",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", str(contract["actor"]["concurrency"]),
                "--provider-budget-ledger", str(budget_ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["actor"]["max_turns"]),
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, env=runtime_env, capture_output=True, text=True)
            if result.returncode != 0:
                failure = {
                    "schema_version": "1.0",
                    "artifact_type": "e2-r18-stage-a-stream-technical-failure",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "stream_id": stream_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                    "provider_relaunch_authorized": False,
                    "instruction": "Inspect process, lock, rollout refs, technical failures and completed manifests before any resume. Do not blindly relaunch.",
                }
                atomic_json(failure_root / f"{stream_id}.json", failure)
                raise RuntimeError(f"R18 Stage A stream failed: {stream_id}; stale lock intentionally preserved")
            require(output.exists(), f"actor stream returned success without summary: {stream_id}")
            summary = load_json(output)
            require(summary.get("status") == "COMPLETED", f"actor stream summary not completed: {stream_id}")
            require(summary.get("authorization_sha256") == auth_sha, "actor stream authorization SHA drift")
            require(summary.get("contract_sha256") == contract_sha, "actor stream contract SHA drift")
            row = {
                "stream_id": stream_id,
                "summary_path": str(output),
                "summary_sha256": sha_file(output),
                "task_ids": [str(v) for v in streams[stream_id]],
                "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            verify_stream_receipt(row, run_root, provider_budget_ledger)
            append_jsonl(manifest_path, row)
            completed[stream_id] = row

        require(len(completed) == 12, "R18 Stage A did not complete all 12 streams")
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        mixed = 0
        exposed_streams = 0
        family_mixed: dict[str, int] = {}
        stream_rows: list[dict[str, Any]] = []
        metadata = {str(r["id"]): r for r in load_json(suite_root / "r17_controlled_metadata.json")}
        total_provider_calls = 0
        total_rollouts = 0
        for stream_id in frozen_stream_ids:
            stream_mixed = 0
            stream_calls = 0
            for task_id in streams[stream_id]:
                pool = load_json(run_root / "cases" / task_id / "pool_k8.json")
                scores = [float(row["score"]) for row in pool["trajectories"]]
                is_mixed = min(scores) < 1.0 and max(scores) >= 1.0
                stream_mixed += int(is_mixed)
                mixed += int(is_mixed)
                family = str(metadata[task_id]["primary_failure_family"])
                family_mixed[family] = family_mixed.get(family, 0) + int(is_mixed)
                total_rollouts += len(scores)
                for trajectory in pool["trajectories"]:
                    raw = load_json(Path(trajectory["trajectory_path"]))
                    stream_calls += len(raw.get("adapter_receipts") or [])
            total_provider_calls += stream_calls
            qualifies = stream_mixed >= int(contract["support_gate"]["mixed_pools_per_exposed_stream_minimum"])
            exposed_streams += int(qualifies)
            stream_rows.append({
                "stream_id": stream_id,
                "mixed_pools": stream_mixed,
                "qualifies_as_exposed_stream": qualifies,
                "provider_calls": stream_calls,
            })

        require(total_rollouts == 768, f"unexpected frozen rollout count: {total_rollouts}")
        require(total_provider_calls <= int(contract["budget"]["max_provider_calls"]), "provider receipt count hard ceiling exceeded")
        provider_budget_snapshot = provider_budget_ledger.snapshot()
        require(
            provider_budget_snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]),
            "provider budget claim hard ceiling exceeded",
        )
        require(
            provider_budget_snapshot.total_claimed >= total_provider_calls,
            "provider receipts exceed fail-closed pre-I/O budget claims",
        )
        supported_families = sum(int(value > 0) for value in family_mixed.values())
        support = {
            "mixed_pool_count": mixed,
            "mixed_pool_total": 96,
            "exposed_stream_count": exposed_streams,
            "stream_total": 12,
            "stream_rows": stream_rows,
            "family_mixed_counts": dict(sorted(family_mixed.items())),
            "supported_families": supported_families,
            "primary_hard_gate_pass": (
                mixed >= int(contract["support_gate"]["mixed_pool_count_minimum"])
                and exposed_streams >= int(contract["support_gate"]["exposed_stream_minimum"])
            ),
            "family_generalization_gate_pass": supported_families >= int(contract["support_gate"]["supported_families_minimum"]),
        }
        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r18-stage-a-pool-freeze-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "COMPLETED_ALL_96_UNTOUCHED_FUTURE_POOLS_READY_FOR_PREDICTION_FREEZE",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "model_identity_sha256": sha_file(identity),
            "mindmemos_commit": head,
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "runtime_qualification_sha256": contract["runtime"]["qualification_sha256"],
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": total_rollouts,
            "provider_calls": total_provider_calls,
            "provider_budget": provider_budget_snapshot.to_dict(),
            "support": support,
            "updater_calls": 0,
            "provider_pool_stage_complete": True,
            "mixed_pool_count_by_stream": {row["stream_id"]: row["mixed_pools"] for row in stream_rows},
            "heldout_evaluations": 0,
            "scientific_effect_read": False,
            "r18_stage_b_authority": False,
            "paper_promotion_authority": False,
        }
        atomic_json(run_root / "summary/r18_stage_a_pool_freeze_summary.json", final)
        seal_global_lease(lease_path, contract_sha=contract_sha, authorization_sha=auth_sha, prereg_sha=contract["preregistration"]["sha256"])
        success = True
        print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        os.close(lock_fd)
        if success:
            lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
