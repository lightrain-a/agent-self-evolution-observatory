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
from research_pipeline.c1_pacta_msr_atomgit_qwen38_fresh2_source_runtime import (
    ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
    PACTA_FIRST_DECISION_BUDGET,
    PROVIDER_ID,
    SAMPLING_CONTROL,
    SOURCE_MAX_COMPLETION_TOKENS,
    execute_trajectory,
)
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import MODEL, PROFILE, write_config

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-pool-20260903.json"
POOL_SHA = "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"
RUNTIME = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-runtime-clean-20260903-v1/normalization-qualification.json")
RUNTIME_SHA = "ead533dadbfa1d71072e6c3774d37ed5be8509134955375821a99645de386615"
Q02_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q02-source-budget-closure-20260902.json"
Q02_CLOSURE_SHA = "c41ebc9df5a28b1e6f2643195be2cdfd170318de5577ef2aff3b1891819959b6"
Q02_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q02-budget-20260902-v1")
Q02_RESULT = Q02_ROOT / "q02-result.json"
Q02_RESULT_SHA = "c4c7c05f4e14d82fa8ef7d0d0ea2c31a8888295f96eb810b649150da1577b7ce"
Q02_PROVIDER_CONFIG = Q02_ROOT / "configs/max-32768.toml"
Q02_PROVIDER_CONFIG_SHA = "b159fc7559d8989409d3695677997b0e876befacce4bb726f09815e621f8b8a3"
FROZEN_SCHEDULE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-source-schedule-20260903.json"
FROZEN_SCHEDULE_SHA = "c82bd0dcf9f7299add53d9dc5f58f37832dd2c042d8ccfd9da600b6f97b147d2"
PROBE_SPECS = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-probe-specs-20260903.json"
PROBE_SPECS_SHA = "3b98bd26f31824168196cda6fcf60ba448ae2bbd7579456f413b51f1bcdf9bd6"
EXECUTION_CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-source-execution-contract-20260903.json"
EXECUTION_CONTRACT_SHA = "6c09b358be0f65ea097b2df0129fdd54a99be63ad0fe93ae6a06d853bf38f68a"
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
CONFIG = OFFICIAL / "third_party/src/minisweagent/config/extra/swebench.yaml"
CONFIG_SHA = "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41"
DEFAULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-source-20260903-v1")
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


def append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def verify() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for path, expected, label in (
        (POOL, POOL_SHA, "fresh2 pool"),
        (RUNTIME, RUNTIME_SHA, "fresh2 runtime-clean qualification"),
        (Q02_CLOSURE, Q02_CLOSURE_SHA, "Q0.2 closure"),
        (Q02_RESULT, Q02_RESULT_SHA, "Q0.2 result"),
        (Q02_PROVIDER_CONFIG, Q02_PROVIDER_CONFIG_SHA, "Q0.2 provider config"),
        (FROZEN_SCHEDULE, FROZEN_SCHEDULE_SHA, "frozen fresh2 source schedule"),
        (PROBE_SPECS, PROBE_SPECS_SHA, "frozen fresh2 probe specs"),
        (EXECUTION_CONTRACT, EXECUTION_CONTRACT_SHA, "fresh2 source execution contract"),
        (CONFIG, CONFIG_SHA, "official MiniSWEAgent config"),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"STOP_FRESH2_SOURCE_INPUT_HASH_DRIFT:{label}")
    head = subprocess.run(
        ["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise RuntimeError("STOP_FRESH2_SOURCE_CARRIER_COMMIT_DRIFT")

    q02 = load(Q02_CLOSURE)
    if (
        q02.get("status") != "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS"
        or q02.get("resolved_model") != MODEL
        or q02.get("selected_source_budget") != SOURCE_MAX_COMPLETION_TOKENS
        or q02.get("first_decision_budget") != PACTA_FIRST_DECISION_BUDGET
        or q02.get("invocation_timeout_seconds") != ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS
    ):
        raise RuntimeError("STOP_FRESH2_SOURCE_Q02_NOT_QUALIFIED")
    q02_result = load(Q02_RESULT)
    if (
        q02_result.get("status") != "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS"
        or q02_result.get("pass") is not True
        or q02_result.get("selected_source_budget") != SOURCE_MAX_COMPLETION_TOKENS
    ):
        raise RuntimeError("STOP_FRESH2_SOURCE_Q02_RESULT_INVALID")

    pool = load(POOL)
    runtime = load(RUNTIME)
    frozen_schedule = load(FROZEN_SCHEDULE)
    probes = load(PROBE_SPECS)
    if pool.get("candidate_count") != 10 or pool.get("repository_count") != 10:
        raise RuntimeError("STOP_FRESH2_SOURCE_POOL_GEOMETRY")
    if (
        runtime.get("status") != "FRESH2_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN"
        or runtime.get("qualified") != 20
        or runtime.get("source_qualified") != 10
        or runtime.get("future_qualified") != 10
    ):
        raise RuntimeError("STOP_FRESH2_SOURCE_RUNTIME_SUPPORT")
    if frozen_schedule.get("status") != "FRESH2_SOURCE_SCHEDULE_FROZEN_PRE_SOURCE_OUTCOME" or len(frozen_schedule.get("rows") or []) != 10:
        raise RuntimeError("STOP_FRESH2_SOURCE_SCHEDULE_INVALID")
    if probes.get("status") != "FRESH2_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME" or len(probes.get("rows") or []) != 10:
        raise RuntimeError("STOP_FRESH2_SOURCE_PROBE_SPECS_INVALID")

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
            raise RuntimeError("STOP_FRESH2_SOURCE_RUNTIME_MISSING:" + unit["source_task_id"])
        rows.append({**unit, "digest_ref": rr["digest_ref"]})
    if len(rows) != 10 or len({row["source_task_id"] for row in rows}) != 10:
        raise RuntimeError("STOP_FRESH2_SOURCE_GEOMETRY")
    return rows, q02


def schedule(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source = {row["source_task_id"]: row for row in rows}
    frozen = load(FROZEN_SCHEDULE)
    out: list[dict[str, Any]] = []
    for item in frozen["rows"]:
        unit = by_source.get(item["source_task_id"])
        if unit is None:
            raise RuntimeError("STOP_FRESH2_SOURCE_SCHEDULE_POOL_MISMATCH:" + item["source_task_id"])
        if (
            item.get("unit_id") != unit["unit_id"]
            or item.get("source_task_sha256") != unit["source_task_sha256"]
            or item.get("source_base_commit") != unit["source_base_commit"]
            or item.get("logical_attempts") != 1
            or item.get("replacement") is not False
            or item.get("future_task_executed") is not False
        ):
            raise RuntimeError("STOP_FRESH2_SOURCE_SCHEDULE_ROW_DRIFT:" + item["source_task_id"])
        out.append(
            {
                "sequence": item["sequence"],
                "unit_id": unit["unit_id"],
                "source_task_id": unit["source_task_id"],
                "future_task_id": unit["future_task_id"],
                "repository": unit["task_family"],
                "task_sha256": unit["source_task_sha256"],
                "base_commit": unit["source_base_commit"],
                "digest_ref": unit["digest_ref"],
                "order_key": item["order_key"],
                "logical_attempts": 1,
                "selected_memory": "",
                "future_task_executed": False,
                "replacement": False,
            }
        )
    if [row["sequence"] for row in out] != list(range(1, 11)):
        raise RuntimeError("STOP_FRESH2_SOURCE_SEQUENCE_DRIFT")
    return out


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("AtomGit T0 root exists; no overwrite")
    rows, _ = verify()
    sched = schedule(rows)
    root.mkdir(parents=True)
    provider_config = root / "provider-config.toml"
    write_config(provider_config, SOURCE_MAX_COMPLETION_TOKENS)
    if sha256_file(provider_config) != Q02_PROVIDER_CONFIG_SHA:
        raise RuntimeError("STOP_FRESH2_SOURCE_PROVIDER_CONFIG_BYTES_DRIFT")
    provider_workdir = root / "empty-provider-workdir"
    provider_workdir.mkdir(parents=True, exist_ok=True)
    contract = {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-SOURCE-T0-20260903",
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
        "q02_closure_sha256": Q02_CLOSURE_SHA,
        "q02_result_sha256": Q02_RESULT_SHA,
        "fresh_pool_sha256": POOL_SHA,
        "runtime_qualification_sha256": RUNTIME_SHA,
        "frozen_source_schedule_sha256": FROZEN_SCHEDULE_SHA,
        "frozen_probe_specs_sha256": PROBE_SPECS_SHA,
        "execution_contract_sha256": EXECUTION_CONTRACT_SHA,
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
            "frozen_schedule_sha256": FROZEN_SCHEDULE_SHA,
            "schedule": sched,
            "scheduled_count": 10,
            "replacement": False,
            "top_up": False,
            "future_task_executions": 0,
        },
    )
    return {
        "status": "FRESH2_ATOMGIT_MSR_SOURCE_EXECUTION_PREPARED",
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
        "status": "FRESH2_ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS" if all(row["pass"] for row in rows) else "HOLD_FRESH2_ATOMGIT_MSR_SOURCE_PRELAUNCH",
        "qualified": sum(row["pass"] for row in rows),
        "total": 10,
        "rows": rows,
        "provider_calls": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "prelaunch-qualification.json", result)
    return result


def smoke(root: Path) -> dict[str, Any]:
    if load(root / "prelaunch-qualification.json").get("status") != "FRESH2_ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS":
        raise RuntimeError("prelaunch not passed")
    if (root / "smoke-result.json").exists() or (root / "smoke").exists():
        raise RuntimeError("smoke exists; no retry/overwrite")
    first = load(root / "acquisition-schedule.json")["schedule"][0]
    config = yaml.safe_load(CONFIG.read_text())
    smoke_config = copy.deepcopy(config)
    smoke_config["agent"]["step_limit"] = SMOKE_STEP_LIMIT
    run = execute_trajectory(
        instance="FRESH2_ATOMGIT_MSR_NONSCIENTIFIC_SMOKE",
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
        "status": "FRESH2_ATOMGIT_MSR_MULTISTEP_SMOKE_PASS" if passed else "STOP_FRESH2_ATOMGIT_MSR_MULTISTEP_SMOKE",
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
    if load(root / "smoke-result.json").get("status") != "FRESH2_ATOMGIT_MSR_MULTISTEP_SMOKE_PASS":
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
        decision = "FRESH2_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED"
        pool_retired = False
    else:
        decision = "HOLD_FRESH2_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE"
        pool_retired = len(results) > 0
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
        "pool_retired": pool_retired,
        "replacement": False,
        "top_up": False,
        "source_gate": "all 10 provenance-valid; any consumed-invalid or incomplete consumed epoch retires the entire fresh2 pool",
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
