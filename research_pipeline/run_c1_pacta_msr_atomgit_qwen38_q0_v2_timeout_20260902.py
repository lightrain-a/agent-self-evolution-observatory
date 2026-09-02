#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_provider import _message_text_from_jsonl
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import parse_action
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import (
    ATOMCODE,
    AUTH,
    MODEL,
    PROFILE,
    SYNC_CONFIG,
    first_action_fixtures,
    long_fixtures,
    serialize_messages,
    write_config,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q0-v2-timeout-contract-20260902.json"
PARENT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0-20260902-v1")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0v2-timeout-20260902-v1")
SOURCE_BUDGET = 16384
FIRST_BUDGET = 2048
TIMEOUT_SECONDS = 900
EXPECTED_PARENT = {
    "identity-result.json": "7e6798231fe2000fb2828d76b96be664f2c6906b97befdaf5dfe3cd4cc9e8b00",
    "first-action-result.json": "eb9f1513859ac3169da11ff0668d9c26088f4b1643312784b4e7eae2ce50aa4a",
    "source-budget-result.json": "e554de18ae89086c915796aa4004f8578ab26a05acaa0d9641d61b6a5ae028be",
    "configs/max-16384.toml": "e5ef4b1e626cf0379e000922dec76f8121e54d1f2c7596e0b87f75d742722671",
    "configs/max-2048.toml": "a61663e13ebd5e1f3116eb663c09c513d01172a58846a7edaad5721c5957b54d",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verify_parent() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_PARENT.items():
        path = PARENT_ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"STOP_Q0V2_PARENT_MISSING:{relative}")
        digest = sha256_file(path)
        observed[relative] = digest
        if digest != expected:
            raise RuntimeError(f"STOP_Q0V2_PARENT_HASH_DRIFT:{relative}:{digest}")
    parent_source = json.loads((PARENT_ROOT / "source-budget-result.json").read_text())
    if parent_source.get("status") != "STOP_ATOMGIT_QWEN38_SOURCE_BUDGET":
        raise RuntimeError("STOP_Q0V2_PARENT_VERDICT_DRIFT")
    first = json.loads((PARENT_ROOT / "first-action-result.json").read_text())
    if first.get("status") != "ATOMGIT_QWEN38_FIRST_ACTION_PASS" or first.get("first_decision_budget") != FIRST_BUDGET:
        raise RuntimeError("STOP_Q0V2_FIRST_ACTION_PARENT_DRIFT")
    return observed


def call(root: Path, phase: str, index: int, messages: list[dict[str, str]], max_tokens: int, label: str) -> dict[str, Any]:
    config = root / "configs" / f"max-{max_tokens}.toml"
    if not config.exists():
        write_config(config, max_tokens)
    parent_config = PARENT_ROOT / "configs" / f"max-{max_tokens}.toml"
    if not parent_config.is_file() or sha256_file(config) != sha256_file(parent_config):
        raise RuntimeError(f"STOP_Q0V2_CONFIG_BYTES_DRIFT:{max_tokens}")
    workdir = root / "empty-workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    prompt = serialize_messages(messages)
    stem = f"{index:04d}__{re.sub(r'[^A-Za-z0-9_.-]+','_',label)[:120]}"
    request_path = root / phase / "raw" / f"{stem}.request.json"
    stdout_path = root / phase / "raw" / f"{stem}.stdout.jsonl"
    stderr_path = root / phase / "raw" / f"{stem}.stderr.txt"
    safe = {
        "schema_version": 1,
        "created_at_utc": now(),
        "phase": phase,
        "label": label,
        "profile": PROFILE,
        "resolved_model_expected": MODEL,
        "max_tokens": max_tokens,
        "atomcode_subprocess_timeout_seconds": TIMEOUT_SECONDS,
        "prompt_sha256": sha256_text(prompt),
        "config_sha256": sha256_file(config),
        "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
        "provider_retries": 0,
        "authorization_material_persisted": False,
    }
    req_sha = atomic_bytes(request_path, (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
    fd, prompt_name = tempfile.mkstemp(prefix="c1-atomgit-q0v2-", suffix=".txt", dir="/tmp")
    prompt_path = Path(prompt_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(prompt)
            handle.flush()
            os.fsync(handle.fileno())
        cmd = [
            str(ATOMCODE), "--config", str(config), "--provider", PROFILE,
            "--no-tools", "--ephemeral", "--no-telemetry", "--output-format", "jsonl",
            "-C", str(workdir), "--prompt-file", str(prompt_path),
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True, timeout=TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
        atomic_bytes(stdout_path, out.encode())
        atomic_bytes(stderr_path, err.encode())
        row = {**safe, "request_sha256": req_sha, "pass": False, "failure": "TIMEOUT", "returncode": 124}
        atomic_json(root / phase / "calls" / f"{stem}.json", row)
        return row
    finally:
        prompt_path.unlink(missing_ok=True)
    stdout_sha = atomic_bytes(stdout_path, completed.stdout.encode())
    stderr_sha = atomic_bytes(stderr_path, completed.stderr.encode())
    base = {
        **safe,
        "request_sha256": req_sha,
        "stdout_sha256": stdout_sha,
        "stderr_sha256": stderr_sha,
        "returncode": completed.returncode,
        "persisted_before_parse": True,
    }
    if completed.returncode != 0:
        row = {**base, "pass": False, "failure": "ATOMCODE_NONZERO", "stderr_tail_sha256": sha256_text(completed.stderr[-1000:])}
        atomic_json(root / phase / "calls" / f"{stem}.json", row)
        return row
    try:
        text, meta = _message_text_from_jsonl(completed.stdout)
        started = meta["started"]
        usage = meta["usage"]
        started_model = str(started.get("model", ""))
        identity = started_model in {MODEL, PROFILE}
        row = {
            **base,
            "pass": identity and bool(text.strip()),
            "parse_status": "JSONL_PARSED",
            "started_model": started_model,
            "model_identity_pass": identity,
            "assistant_text": text,
            "assistant_text_sha256": sha256_text(text),
            "usage": usage,
            "codingplan_requests": 1,
        }
    except Exception as exc:
        row = {**base, "pass": False, "parse_status": "JSONL_PARSE_FAILED", "failure": f"{type(exc).__name__}:{exc}"}
    atomic_json(root / phase / "calls" / f"{stem}.json", row)
    return row


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q0-v2 root exists; no overwrite")
    if not ATOMCODE.is_file() or not AUTH.is_file() or not SYNC_CONFIG.is_file():
        raise RuntimeError("STOP_Q0V2_ATOMCODE_LOGIN_OR_BINARY_MISSING")
    parent = verify_parent()
    root.mkdir(parents=True)
    for budget in (FIRST_BUDGET, SOURCE_BUDGET):
        p = root / "configs" / f"max-{budget}.toml"
        write_config(p, budget)
        if sha256_file(p) != EXPECTED_PARENT[f"configs/max-{budget}.toml"]:
            raise RuntimeError(f"STOP_Q0V2_CONFIG_REPRODUCTION_DRIFT:{budget}")
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q0V2_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "parent_hashes": parent,
        "atomcode_version": subprocess.run([str(ATOMCODE), "--version"], text=True, capture_output=True, check=True).stdout.strip(),
        "atomcode_binary_sha256": sha256_file(ATOMCODE),
        "timeout_seconds": TIMEOUT_SECONDS,
        "source_budget": SOURCE_BUDGET,
        "first_decision_budget_inherited": FIRST_BUDGET,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
    }
    atomic_json(root / "prepare.json", result)
    return result


def source_budget(root: Path) -> dict[str, Any]:
    if not (root / "prepare.json").is_file():
        raise RuntimeError("prepare first")
    if (root / "source-budget-result.json").exists() or (root / "source-budget-16384").exists():
        raise RuntimeError("Q0-v2 source budget phase exists; no retry/overwrite")
    rows: list[dict[str, Any]] = []
    for index, fx in enumerate(long_fixtures(), 1):
        row = call(root, "source-budget-16384", index, fx["messages"], SOURCE_BUDGET, fx["fixture_id"])
        try:
            action = parse_action(str(row.get("assistant_text") or ""))
            parsed = True
        except Exception as exc:
            action = ""
            parsed = False
            row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
        exact = parsed and action == fx["expected"]
        row.update({
            "fixture_id": fx["fixture_id"],
            "action_parse_pass": parsed,
            "exact_action_match": exact,
            "expected_action_sha256": fx["expected_sha256"],
            "action_sha256": sha256_text(action) if action else "",
            "history_pairs": fx["history_pairs"],
            "line_count": fx["line_count"],
        })
        row["pass"] = bool(row.get("pass")) and exact
        atomic_json(root / "source-budget-16384" / "adjudicated" / f"{index:04d}.json", row)
        rows.append(row)
        print(json.dumps({"fixture": fx["fixture_id"], "pass": row["pass"], "failure": row.get("failure"), "returncode": row.get("returncode")}), flush=True)
    passed = len(rows) == 6 and all(r.get("pass") for r in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_SOURCE_BUDGET_16384_TIMEOUT_REPAIR_PASS" if passed else "STOP_ATOMGIT_QWEN38_SOURCE_BUDGET_16384_AFTER_TIMEOUT_REPAIR",
        "pass": passed,
        "source_trajectory_budget": SOURCE_BUDGET if passed else None,
        "timeout_seconds": TIMEOUT_SECONDS,
        "qualified": sum(bool(r.get("pass")) for r in rows),
        "total": 6,
        "rows": rows,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
    }
    atomic_json(root / "source-budget-result.json", result)
    return result


def sampling(root: Path) -> dict[str, Any]:
    source = json.loads((root / "source-budget-result.json").read_text())
    if source.get("pass") is not True:
        raise RuntimeError("source budget repair not passed")
    if (root / "sampling-diagnostic.json").exists() or (root / "sampling").exists():
        raise RuntimeError("sampling phase exists; no retry/overwrite")
    rows: list[dict[str, Any]] = []
    for fixture_index, fx in enumerate(first_action_fixtures()[:2], 1):
        for replicate in range(1, 7):
            index = (fixture_index - 1) * 6 + replicate
            row = call(root, "sampling", index, fx["messages"], FIRST_BUDGET, f"sampling-{fixture_index}-{replicate}")
            try:
                action = parse_action(str(row.get("assistant_text") or ""))
                parse_pass = True
            except Exception:
                action = "PARSE_FAIL"
                parse_pass = False
            result_row = {
                "fixture": fixture_index,
                "replicate": replicate,
                "action": action,
                "action_sha256": sha256_text(action),
                "parse_pass": parse_pass,
                "model_identity_pass": row.get("model_identity_pass"),
                "codingplan_requests": row.get("codingplan_requests"),
                "usage": row.get("usage") or {},
            }
            atomic_json(root / "sampling" / "adjudicated" / f"{index:04d}.json", result_row)
            rows.append(result_row)
    per = []
    for fixture_index in (1, 2):
        actions = [r["action"] for r in rows if r["fixture"] == fixture_index]
        per.append({
            "fixture": fixture_index,
            "unique_action_count": len(set(actions)),
            "parse_pass_count": sum(r["parse_pass"] for r in rows if r["fixture"] == fixture_index),
            "actions": actions,
        })
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "DIAGNOSTIC_ONLY",
        "pass_requirement": False,
        "first_decision_budget": FIRST_BUDGET,
        "provider_sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9",
        "per_fixture": per,
        "rows": rows,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "sampling-diagnostic.json", result)
    return result


def close(root: Path) -> dict[str, Any]:
    source = json.loads((root / "source-budget-result.json").read_text())
    if source.get("pass") is not True:
        passed = False
        sampling_summary = None
    else:
        sampling_result = json.loads((root / "sampling-diagnostic.json").read_text())
        passed = True
        sampling_summary = sampling_result.get("per_fixture")
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q0_PASS_AFTER_TIMEOUT_REPAIR" if passed else "STOP_ATOMGIT_QWEN38_Q0_AFTER_TIMEOUT_REPAIR",
        "pass": passed,
        "model_condition": "AtomGit CodingPlan / AtomCode-mediated Qwen3.8-27B",
        "resolved_model": MODEL,
        "first_decision_budget": FIRST_BUDGET,
        "source_trajectory_budget": source.get("source_trajectory_budget"),
        "atomcode_subprocess_timeout_seconds": TIMEOUT_SECONDS,
        "sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9",
        "sampling_diagnostic": sampling_summary,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
        "other_models_used": 0,
        "next_if_pass": "Prospective AtomGit Qwen3.8 source acquisition on the already frozen ten fresh PACTA-MSR units; no model shopping.",
    }
    atomic_json(root / "q0-closure.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("prepare", "source-budget", "sampling", "close"), required=True)
    args = parser.parse_args()
    fn = {
        "prepare": prepare,
        "source-budget": source_budget,
        "sampling": sampling,
        "close": close,
    }[args.phase]
    result = fn(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
