#!/usr/bin/env python3
"""Prospective AtomGit Qwen3.8 native source-trajectory acquisition for PACTA-MSR T0."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import Container
from research_pipeline.c1_pacta_msr_atomgit_qwen38_source_runtime import (
    ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
    PACTA_FIRST_DECISION_BUDGET,
    PROVIDER_ID,
    SAMPLING_CONTROL,
    SOURCE_MAX_COMPLETION_TOKENS,
    execute_trajectory,
)
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import MODEL, PROFILE, write_config

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json"
POOL_SHA = "2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e"
RUNTIME = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-runtime-20260902-v1/normalization-qualification.json")
RUNTIME_SHA = "7b876c9dc31e964868fa1c5cff3cd5ab3510e57162e65368023102822d933a01"
Q0_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0v2-timeout-20260902-v1")
Q0_CLOSURE = Q0_ROOT / "q0-closure.json"
Q0_CLOSURE_SHA = "19ec9c078b2c4a6f3ec77eee181b47a4f7cc082a516eff0074feace7a74e6f70"
Q0_SOURCE_BUDGET = Q0_ROOT / "source-budget-result.json"
Q0_SOURCE_BUDGET_SHA = "8eead97e1a3b39a701886a24a4597e2ce607ee50580803a5655c7ac4087c4198"
Q0_PROVIDER_CONFIG = Q0_ROOT / "configs/max-16384.toml"
Q0_PROVIDER_CONFIG_SHA = "e5ef4b1e626cf0379e000922dec76f8121e54d1f2c7596e0b87f75d742722671"
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
CONFIG = OFFICIAL / "third_party/src/minisweagent/config/extra/swebench.yaml"
CONFIG_SHA = "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41"
DEFAULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-source-20260902-v1")
ORDER_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-SOURCE-ACQUIRE-v1"
SMOKE_TASK = (
    "Non-scientific runtime qualification only. Create /testbed/runtime_smoke_marker.py containing exactly "
    "print('ATOMGIT_MSR_SMOKE_OK'), run it and observe ATOMGIT_MSR_SMOKE_OK, then submit completion using the "
    "normal MiniSWEAgent completion command. Do not modify any other file."
)
SMOKE_MARKER = "ATOMGIT_MSR_SMOKE_OK"
SMOKE_STEP_LIMIT = 16
SOURCE_INPUT_TOKEN_HARD_CAP = 30_000_000
SOURCE_OUTPUT_TOKEN_HARD_CAP = 1_000_000


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def verify() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for path, expected, label in (
        (POOL, POOL_SHA, "fresh pool"),
        (RUNTIME, RUNTIME_SHA, "runtime qualification"),
        (Q0_CLOSURE, Q0_CLOSURE_SHA, "Q0 closure"),
        (Q0_SOURCE_BUDGET, Q0_SOURCE_BUDGET_SHA, "Q0 source budget"),
        (Q0_PROVIDER_CONFIG, Q0_PROVIDER_CONFIG_SHA, "Q0 provider config"),
        (CONFIG, CONFIG_SHA, "official MiniSWEAgent config"),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"STOP_ATOMGIT_T0_INPUT_HASH_DRIFT:{label}")
    head = subprocess.run(
        ["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise RuntimeError("STOP_ATOMGIT_T0_CARRIER_COMMIT_DRIFT")

    q0 = load(Q0_CLOSURE)
    if (
        q0.get("status") != "ATOMGIT_QWEN38_Q0_PASS_AFTER_TIMEOUT_REPAIR"
        or q0.get("pass") is not True
        or q0.get("resolved_model") != MODEL
        or q0.get("first_decision_budget") != PACTA_FIRST_DECISION_BUDGET
        or q0.get("source_trajectory_budget") != SOURCE_MAX_COMPLETION_TOKENS
        or q0.get("atomcode_subprocess_timeout_seconds") != ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS
    ):
        raise RuntimeError("STOP_ATOMGIT_T0_Q0_NOT_QUALIFIED")
    source_budget = load(Q0_SOURCE_BUDGET)
    if source_budget.get("qualified") != 6 or source_budget.get("pass") is not True:
        raise RuntimeError("STOP_ATOMGIT_T0_SOURCE_BUDGET_NOT_QUALIFIED")

    pool = load(POOL)
    runtime = load(RUNTIME)
    if pool.get("candidate_count") != 10:
        raise RuntimeError("STOP_ATOMGIT_T0_POOL_GEOMETRY")
    if (
        runtime.get("status") != "MSR_20_RUNTIME_READY"
        or runtime.get("source_qualified") != 10
        or runtime.get("future_qualified") != 10
    ):
        raise RuntimeError("STOP_ATOMGIT_T0_RUNTIME_SUPPORT")
    by_runtime = {row["instance_id"]: row for row in runtime["rows"]}
    rows: list[dict[str, Any]] = []
    for unit in pool["units"]:
        rr = by_runtime.get(unit["source_task_id"])
        if (
            not rr
            or rr.get("role") != "source"
            or not rr.get("exact_base_normalization_pass")
            or not rr.get("digest_ref")
        ):
            raise RuntimeError("STOP_ATOMGIT_T0_SOURCE_RUNTIME_MISSING:" + unit["source_task_id"])
        rows.append({**unit, "digest_ref": rr["digest_ref"]})
    if len(rows) != 10 or len({row["source_task_id"] for row in rows}) != 10:
        raise RuntimeError("STOP_ATOMGIT_T0_SOURCE_GEOMETRY")
    return rows, q0


def schedule(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: (sha_text(ORDER_SALT + "|" + row["unit_id"]), row["unit_id"]))
    out = []
    for sequence, unit in enumerate(ordered, 1):
        out.append(
            {
                "sequence": sequence,
                "unit_id": unit["unit_id"],
                "source_task_id": unit["source_task_id"],
                "future_task_id": unit["future_task_id"],
                "repository": unit["task_family"],
                "task_sha256": unit["source_task_sha256"],
                "base_commit": unit["source_base_commit"],
                "digest_ref": unit["digest_ref"],
                "order_key": sha_text(ORDER_SALT + "|" + unit["unit_id"]),
                "logical_attempts": 1,
                "selected_memory": "",
                "future_task_executed": False,
            }
        )
    return out


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("AtomGit T0 root exists; no overwrite")
    rows, _ = verify()
    sched = schedule(rows)
    root.mkdir(parents=True)
    provider_config = root / "provider-config.toml"
    write_config(provider_config, SOURCE_MAX_COMPLETION_TOKENS)
    if sha256_file(provider_config) != Q0_PROVIDER_CONFIG_SHA:
        raise RuntimeError("STOP_ATOMGIT_T0_PROVIDER_CONFIG_BYTES_DRIFT")
    provider_workdir = root / "empty-provider-workdir"
    provider_workdir.mkdir(parents=True, exist_ok=True)
    contract = {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-SOURCE-T0-20260902",
        "status": "FROZEN_BEFORE_SOURCE_POLICY",
        "model_condition": "AtomGit CodingPlan / AtomCode-mediated Qwen3.8-27B",
        "provider_id": PROVIDER_ID,
        "profile": PROFILE,
        "resolved_model": MODEL,
        "sampling_control": SAMPLING_CONTROL,
        "source_max_completion_tokens": SOURCE_MAX_COMPLETION_TOKENS,
        "pacta_first_decision_budget": PACTA_FIRST_DECISION_BUDGET,
        "atomcode_subprocess_timeout_seconds": ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
        "provider_config_sha256": sha256_file(provider_config),
        "q0_closure_sha256": Q0_CLOSURE_SHA,
        "fresh_pool_sha256": POOL_SHA,
        "runtime_qualification_sha256": RUNTIME_SHA,
        "scheduled_source_units": 10,
        "logical_attempts_per_source": 1,
        "provider_wrapper_retries": 0,
        "replacement": False,
        "top_up": False,
        "environment_command_timeout_seconds": 60,
        "step_limit": 250,
        "smoke": {
            "non_scientific": True,
            "step_limit": SMOKE_STEP_LIMIT,
            "marker": SMOKE_MARKER,
            "must_pass_before_source": True,
        },
        "source_input_token_hard_cap": SOURCE_INPUT_TOKEN_HARD_CAP,
        "source_output_token_hard_cap": SOURCE_OUTPUT_TOKEN_HARD_CAP,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "probe_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
        "forbidden": [
            "replacement source",
            "future task execution",
            "writer",
            "binder",
            "MSR probe",
            "shadow",
            "gate",
            "final",
            "model switch",
        ],
    }
    atomic_json(root / "contract.json", contract)
    atomic_json(
        root / "acquisition-schedule.json",
        {
            "schema_version": 1,
            "created_at_utc": now(),
            "status": "FROZEN",
            "order_salt": ORDER_SALT,
            "schedule": sched,
            "scheduled_count": 10,
            "replacement": False,
            "top_up": False,
            "future_task_executions": 0,
        },
    )
    return {
        "status": "ATOMGIT_MSR_SOURCE_SCHEDULE_FROZEN",
        "scheduled": 10,
        "contract_sha256": sha256_file(root / "contract.json"),
        "schedule_sha256": sha256_file(root / "acquisition-schedule.json"),
        "provider_config_sha256": sha256_file(provider_config),
    }


def prelaunch(root: Path) -> dict[str, Any]:
    if not (root / "contract.json").is_file():
        raise RuntimeError("prepare first")
    if (root / "prelaunch-qualification.json").exists():
        raise RuntimeError("prelaunch exists; no overwrite")
    rows = []
    for item in load(root / "acquisition-schedule.json")["schedule"]:
        qualification_root = root / "prelaunch" / item["source_task_id"]
        container = None
        passed = False
        error = None
        try:
            container = Container(item["digest_ref"], item["base_commit"], qualification_root)
            passed = True
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            if container is not None:
                container.cleanup()
        rows.append(
            {
                "source_task_id": item["source_task_id"],
                "pass": passed,
                "error": error,
                "normalization_path": str(qualification_root / "exact-base-normalization.json") if passed else None,
                "normalization_sha256": sha256_file(qualification_root / "exact-base-normalization.json") if passed else None,
            }
        )
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS" if all(row["pass"] for row in rows) else "HOLD_ATOMGIT_MSR_SOURCE_PRELAUNCH",
        "qualified": sum(row["pass"] for row in rows),
        "total": 10,
        "rows": rows,
        "provider_calls": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "prelaunch-qualification.json", result)
    return result


def smoke(root: Path) -> dict[str, Any]:
    if load(root / "prelaunch-qualification.json").get("status") != "ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS":
        raise RuntimeError("prelaunch not passed")
    if (root / "smoke-result.json").exists() or (root / "smoke").exists():
        raise RuntimeError("smoke exists; no retry/overwrite")
    first = load(root / "acquisition-schedule.json")["schedule"][0]
    config = yaml.safe_load(CONFIG.read_text())
    smoke_config = copy.deepcopy(config)
    smoke_config["agent"]["step_limit"] = SMOKE_STEP_LIMIT
    run = execute_trajectory(
        instance="ATOMGIT_MSR_NONSCIENTIFIC_SMOKE",
        task=SMOKE_TASK,
        digest_ref=first["digest_ref"],
        unit_root=root / "smoke",
        config=smoke_config,
        provider_config_path=root / "provider-config.toml",
        provider_workdir=root / "empty-provider-workdir",
        base_commit=first["base_commit"],
    )
    journal = root / "smoke" / "step-journal.jsonl"
    journal_rows = [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]
    actions = [str(row.get("parsed_action") or "") for row in journal_rows if row.get("parsed_action")]
    marker_seen = False
    for path in (root / "smoke" / "raw").glob("observation-*.json"):
        try:
            observation = json.loads(path.read_text())
        except Exception:
            continue
        if SMOKE_MARKER in str(observation.get("output") or ""):
            marker_seen = True
            break
    marker_file_action = any("runtime_smoke_marker.py" in action for action in actions)
    passed = (
        run.get("failure_layer") is None
        and run.get("terminal_status") == "Submitted"
        and 2 <= int(run.get("provider_logical_calls") or 0) <= SMOKE_STEP_LIMIT
        and marker_file_action
        and marker_seen
    )
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_MSR_MULTISTEP_SMOKE_PASS" if passed else "STOP_ATOMGIT_MSR_MULTISTEP_SMOKE",
        "pass": passed,
        "terminal_status": run.get("terminal_status"),
        "provider_calls": run.get("provider_logical_calls"),
        "marker_file_action": marker_file_action,
        "marker_observation_seen": marker_seen,
        "run_sha256": sha256_file(root / "smoke" / "run.json"),
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "smoke-result.json", result)
    return result


def acquire(root: Path) -> dict[str, Any]:
    if load(root / "smoke-result.json").get("status") != "ATOMGIT_MSR_MULTISTEP_SMOKE_PASS":
        raise RuntimeError("smoke not passed")
    rows, _ = verify()
    by_source = {row["source_task_id"]: row for row in rows}
    config = yaml.safe_load(CONFIG.read_text())
    results: list[dict[str, Any]] = []
    stop_reason = None
    for item in load(root / "acquisition-schedule.json")["schedule"]:
        unit = by_source[item["source_task_id"]]
        run = execute_trajectory(
            instance=unit["source_task_id"],
            task=unit["source_task"],
            digest_ref=item["digest_ref"],
            unit_root=root / f"source-{unit['source_task_id']}",
            config=config,
            provider_config_path=root / "provider-config.toml",
            provider_workdir=root / "empty-provider-workdir",
            base_commit=item["base_commit"],
        )
        results.append(run)
        append(root / "acquisition-journal.jsonl", run)
        print(
            json.dumps(
                {
                    "source": unit["source_task_id"],
                    "validity": run["validity_status"],
                    "terminal": run["terminal_status"],
                    "logical_calls": run["provider_logical_calls"],
                    "codingplan_requests": run["codingplan_requests"],
                }
            ),
            flush=True,
        )
        if run.get("failure_layer") is not None:
            stop_reason = f"{unit['source_task_id']}:{run['failure_layer']}"
            break
        if sum(int(row.get("input_tokens") or 0) for row in results) > SOURCE_INPUT_TOKEN_HARD_CAP:
            stop_reason = "SOURCE_INPUT_TOKEN_HARD_CAP"
            break
        if sum(int(row.get("output_tokens") or 0) for row in results) > SOURCE_OUTPUT_TOKEN_HARD_CAP:
            stop_reason = "SOURCE_OUTPUT_TOKEN_HARD_CAP"
            break
    valid = [row for row in results if row["validity_status"] == "TRAJECTORY_BACKED_VALID"]
    if len(results) == 10 and len(valid) == 10:
        decision = "ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED"
    elif len(valid) >= 8:
        decision = "ATOMGIT_MSR_SOURCE_POOL_PARTIAL_STOP"
    else:
        decision = "HOLD_ATOMGIT_MSR_SOURCE_SUPPORT_INSUFFICIENT"
    audit = {
        "schema_version": 1,
        "created_at_utc": now(),
        "decision": decision,
        "rows": results,
        "attempted": len(results),
        "valid": len(valid),
        "valid_repositories": len({by_source[row["source_task_id"]]["task_family"] for row in valid}),
        "stop_reason": stop_reason,
        "codingplan_requests": sum(int(row.get("codingplan_requests") or 0) for row in results),
        "input_tokens": sum(int(row.get("input_tokens") or 0) for row in results),
        "output_tokens": sum(int(row.get("output_tokens") or 0) for row in results),
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "probe_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
        "claim_authority": "NO_MSR_METHOD_EFFECT_EVIDENCE",
    }
    atomic_json(root / "support-audit.json", audit)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--phase", choices=("prepare", "prelaunch", "smoke", "acquire"), required=True)
    args = parser.parse_args()
    fn = {
        "prepare": prepare,
        "prelaunch": prelaunch,
        "smoke": smoke,
        "acquire": acquire,
    }[args.phase]
    result = fn(args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
