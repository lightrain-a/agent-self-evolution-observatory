#!/usr/bin/env python3
"""Q0.1 transport-only timeout amendment for AtomGit/AtomCode Qwen3.8.

Only the six frozen non-scientific long-action fixtures at 16,384 output tokens
are requalified with a 900-second AtomCode invocation ceiling. If that passes,
the already-planned provider-managed sampling diagnostic is run at the frozen
2,048 first-decision budget with the original 300-second invocation ceiling.
No real C1 source/future task is reachable from this runner.
"""
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
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q0_20260902 as parent

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q01-timeout-contract-20260902.json"
PARENT_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0-20260902-v1")
PARENT_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q0-v1-closure-20260902.json"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q01-timeout-20260902-v1")

PROFILE = parent.PROFILE
MODEL = parent.MODEL
ATOMCODE = parent.ATOMCODE
AUTH = parent.AUTH
SYNC_CONFIG = parent.SYNC_CONFIG
SOURCE_BUDGET = 16384
FIRST_DECISION_BUDGET = 2048
SOURCE_TIMEOUT_SECONDS = 900
SAMPLING_TIMEOUT_SECONDS = 300

EXPECTED = {
    "parent_runner": "11c5da1d954db4cfb45695b785d2db231744b9ab8174c08af1e4e75fa68df439",
    "identity_result": "7e6798231fe2000fb2828d76b96be664f2c6906b97befdaf5dfe3cd4cc9e8b00",
    "first_action_result": "eb9f1513859ac3169da11ff0668d9c26088f4b1643312784b4e7eae2ce50aa4a",
    "source_budget_result": "e554de18ae89086c915796aa4004f8578ab26a05acaa0d9641d61b6a5ae028be",
    "parent_closure": "39b75c139fb37e7281e37613bd1d13603f1379256c4c3649230e0c32719a6643",
    "parent_config_16384": "e5ef4b1e626cf0379e000922dec76f8121e54d1f2c7596e0b87f75d742722671",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verify_parent() -> dict[str, Any]:
    observed = {
        "parent_runner": sha256_file(ROOT / "research_pipeline/run_c1_pacta_msr_atomgit_qwen38_q0_20260902.py"),
        "identity_result": sha256_file(PARENT_RUN / "identity-result.json"),
        "first_action_result": sha256_file(PARENT_RUN / "first-action-result.json"),
        "source_budget_result": sha256_file(PARENT_RUN / "source-budget-result.json"),
        "parent_closure": sha256_file(PARENT_CLOSURE),
        "parent_config_16384": sha256_file(PARENT_RUN / "configs/max-16384.toml"),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"STOP_Q01_PARENT_DRIFT:{observed}")
    identity = json.loads((PARENT_RUN / "identity-result.json").read_text())
    first = json.loads((PARENT_RUN / "first-action-result.json").read_text())
    source = json.loads((PARENT_RUN / "source-budget-result.json").read_text())
    if identity.get("pass") is not True or first.get("first_decision_budget") != FIRST_DECISION_BUDGET:
        raise RuntimeError("STOP_Q01_PARENT_QUALIFICATION_DRIFT")
    b16384 = next((x for x in source.get("budget_results", []) if x.get("budget") == SOURCE_BUDGET), None)
    if b16384 != {"budget": 16384, "pass": False, "qualified": 5, "total": 6}:
        raise RuntimeError("STOP_Q01_PARENT_16384_GEOMETRY_DRIFT")
    return observed


def write_config(root: Path, max_tokens: int) -> Path:
    p = root / "configs" / f"max-{max_tokens}.toml"
    parent.write_config(p, max_tokens)
    return p


def call(
    root: Path,
    phase: str,
    index: int,
    messages: list[dict[str, str]],
    max_tokens: int,
    label: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    config = root / "configs" / f"max-{max_tokens}.toml"
    if not config.exists():
        write_config(root, max_tokens)
    workdir = root / "empty-workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    prompt = parent.serialize_messages(messages)
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
        "invocation_timeout_seconds": timeout_seconds,
        "prompt_sha256": sha256_text(prompt),
        "config_sha256": sha256_file(config),
        "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
        "provider_retries": 0,
        "authorization_material_persisted": False,
    }
    req_sha = atomic_bytes(
        request_path,
        (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(),
    )
    fd, prompt_name = tempfile.mkstemp(prefix="c1-atomgit-q01-", suffix=".txt", dir="/tmp")
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
        completed = subprocess.run(
            cmd, text=True, capture_output=True, timeout=timeout_seconds, check=False
        )
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
        atomic_bytes(stdout_path, out.encode())
        atomic_bytes(stderr_path, err.encode())
        row = {
            **safe,
            "request_sha256": req_sha,
            "pass": False,
            "failure": "TIMEOUT",
            "returncode": 124,
        }
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
        row = {
            **base,
            "pass": False,
            "failure": "ATOMCODE_NONZERO",
            "stderr_tail_sha256": sha256_text(completed.stderr[-1000:]),
        }
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
        row = {
            **base,
            "pass": False,
            "parse_status": "JSONL_PARSE_FAILED",
            "failure": f"{type(exc).__name__}:{exc}",
        }
    atomic_json(root / phase / "calls" / f"{stem}.json", row)
    return row


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q0.1 root exists; no overwrite")
    if not ATOMCODE.is_file() or not AUTH.is_file() or not SYNC_CONFIG.is_file():
        raise RuntimeError("STOP_ATOMCODE_LOGIN_OR_BINARY_MISSING")
    parent_hashes = verify_parent()
    root.mkdir(parents=True)
    c16384 = write_config(root, SOURCE_BUDGET)
    c2048 = write_config(root, FIRST_DECISION_BUDGET)
    if sha256_file(c16384) != EXPECTED["parent_config_16384"]:
        raise RuntimeError("STOP_Q01_CONFIG_16384_DRIFT")
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q01_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "parent_hashes": parent_hashes,
        "source_budget": SOURCE_BUDGET,
        "source_timeout_seconds": SOURCE_TIMEOUT_SECONDS,
        "first_decision_budget": FIRST_DECISION_BUDGET,
        "sampling_timeout_seconds": SAMPLING_TIMEOUT_SECONDS,
        "config_16384_sha256": sha256_file(c16384),
        "config_2048_sha256": sha256_file(c2048),
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
    if json.loads((root / "prepare.json").read_text()).get("status") != "ATOMGIT_QWEN38_Q01_PREPARE_PASS":
        raise RuntimeError("Q0.1 prepare not passed")
    if (root / "source-budget-result.json").exists() or (root / "source-budget-16384").exists():
        raise RuntimeError("Q0.1 source-budget phase exists; no retry/overwrite")
    rows = []
    for i, fx in enumerate(parent.long_fixtures(), 1):
        row = call(
            root,
            "source-budget-16384",
            i,
            fx["messages"],
            SOURCE_BUDGET,
            fx["fixture_id"],
            SOURCE_TIMEOUT_SECONDS,
        )
        try:
            action = parse_action(str(row.get("assistant_text") or ""))
            parsed = True
        except Exception as exc:
            action = ""
            parsed = False
            row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
        exact = parsed and action == fx["expected"]
        row.update(
            {
                "action_parse_pass": parsed,
                "exact_action_match": exact,
                "expected_action_sha256": fx["expected_sha256"],
                "action_sha256": sha256_text(action) if action else "",
                "history_pairs": fx["history_pairs"],
                "line_count": fx["line_count"],
            }
        )
        row["pass"] = bool(row.get("pass")) and exact
        atomic_json(root / "source-budget-16384" / "adjudicated" / f"{i:04d}.json", row)
        rows.append(row)
        print(
            json.dumps(
                {
                    "fixture": fx["fixture_id"],
                    "pass": row["pass"],
                    "failure": row.get("failure"),
                    "model": row.get("started_model"),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    passed = len(rows) == 6 and all(r.get("pass") for r in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q01_SOURCE_BUDGET_PASS" if passed else "STOP_ATOMGIT_QWEN38_Q01_SOURCE_BUDGET",
        "pass": passed,
        "source_trajectory_budget": SOURCE_BUDGET if passed else None,
        "invocation_timeout_seconds": SOURCE_TIMEOUT_SECONDS,
        "qualified": sum(bool(r.get("pass")) for r in rows),
        "total": 6,
        "rows": rows,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "source-budget-result.json", result)
    return result


def sampling(root: Path) -> dict[str, Any]:
    source = json.loads((root / "source-budget-result.json").read_text())
    if source.get("pass") is not True:
        raise RuntimeError("Q0.1 source budget not passed")
    if (root / "sampling-diagnostic.json").exists() or (root / "sampling").exists():
        raise RuntimeError("Q0.1 sampling phase exists; no retry/overwrite")
    fixtures = parent.first_action_fixtures()[:2]
    rows = []
    for fi, fx in enumerate(fixtures, 1):
        for rep in range(1, 7):
            idx = (fi - 1) * 6 + rep
            row = call(
                root,
                "sampling",
                idx,
                fx["messages"],
                FIRST_DECISION_BUDGET,
                f"sampling-{fi}-{rep}",
                SAMPLING_TIMEOUT_SECONDS,
            )
            try:
                action = parse_action(str(row.get("assistant_text") or ""))
            except Exception:
                action = "PARSE_FAIL"
            rows.append(
                {
                    "fixture": fi,
                    "replicate": rep,
                    "action": action,
                    "action_sha256": sha256_text(action),
                    "model_identity_pass": row.get("model_identity_pass"),
                    "codingplan_requests": row.get("codingplan_requests"),
                    "transport_failure": row.get("failure"),
                }
            )
    per = []
    for fi in (1, 2):
        actions = [r["action"] for r in rows if r["fixture"] == fi]
        per.append(
            {
                "fixture": fi,
                "unique_action_count": len(set(actions)),
                "parse_fail_count": sum(a == "PARSE_FAIL" for a in actions),
                "actions": actions,
            }
        )
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "DIAGNOSTIC_ONLY",
        "pass_requirement": False,
        "first_decision_budget": FIRST_DECISION_BUDGET,
        "invocation_timeout_seconds": SAMPLING_TIMEOUT_SECONDS,
        "per_fixture": per,
        "rows": rows,
        "scientific_source_tasks_used": 0,
    }
    atomic_json(root / "sampling-diagnostic.json", result)
    return result


def close(root: Path) -> dict[str, Any]:
    source = json.loads((root / "source-budget-result.json").read_text())
    sampling_doc = json.loads((root / "sampling-diagnostic.json").read_text()) if (root / "sampling-diagnostic.json").exists() else None
    passed = source.get("pass") is True and sampling_doc is not None
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q0_PASS_AFTER_TIMEOUT_AMENDMENT" if passed else "STOP_ATOMGIT_QWEN38_Q01",
        "pass": passed,
        "model_condition": "AtomGit CodingPlan / AtomCode-mediated Qwen3.8-27B",
        "resolved_model": MODEL,
        "first_decision_budget": FIRST_DECISION_BUDGET,
        "source_trajectory_budget": SOURCE_BUDGET if passed else None,
        "source_invocation_timeout_seconds": SOURCE_TIMEOUT_SECONDS,
        "sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9",
        "sampling_diagnostic": None if sampling_doc is None else sampling_doc.get("per_fixture"),
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
        "other_models_used": 0,
        "next_if_pass": "Prospective AtomGit Qwen3.8 source acquisition on the already-frozen ten fresh PACTA-MSR units; no model shopping.",
    }
    atomic_json(root / "q01-closure.json", result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--phase", choices=("prepare", "source-budget", "sampling", "close"), required=True)
    a = ap.parse_args()
    fn = {"prepare": prepare, "source-budget": source_budget, "sampling": sampling, "close": close}[a.phase]
    result = fn(a.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
