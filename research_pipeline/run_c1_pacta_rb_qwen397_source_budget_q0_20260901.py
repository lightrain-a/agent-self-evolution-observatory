#!/usr/bin/env python3
"""Prospective non-scientific qualification of the full-source trajectory output budget.

This object does not use any of the remaining SWE-bench source tasks.  It only
checks whether the frozen Qwen397 provider can emit long MiniSWEAgent-style bash
actions without truncation when max_completion_tokens=4096.  The PACTA
first-decision budget remains 512 and is outside this qualification object.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL, atomic_bytes, atomic_json, canonical, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import initial_messages, parse_action

MODEL = "qwen3.5-397b-a17b"
SOURCE_OUTPUT_BUDGET = 4096
FIRST_DECISION_BUDGET = 512
FIXTURE_COUNT = 12
Q0 = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2")
Q0_BINDING_SHA256 = "0a538aa4ca3e24a3ad025d647d01c0b8b0c97f36749d8e549f42ca797e6fb100"
Q0_QUALIFICATION_SHA256 = "71873bea7325ff9e35ded143d9fb6cc28a3cd98d93d472d82e2fabc2877947fe"
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
CONFIG = OFFICIAL / "third_party/src/minisweagent/config/extra/swebench.yaml"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-source-budget-q0-20260901-v1")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def require_key() -> str:
    key = os.environ.get("AA_API_KEY", "")
    if not key:
        raise RuntimeError("STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED")
    return key


def verify_parent() -> dict[str, Any]:
    binding = Q0 / "provider-binding.json"
    qualification = Q0 / "qualification-result.json"
    if sha256_file(binding) != Q0_BINDING_SHA256:
        raise RuntimeError("Q0 provider binding hash drift")
    if sha256_file(qualification) != Q0_QUALIFICATION_SHA256:
        raise RuntimeError("Q0 qualification hash drift")
    b = json.loads(binding.read_text())
    q = json.loads(qualification.read_text())
    if not b.get("identity_pass") or b.get("requested_model") != MODEL or b.get("resolved_model") != MODEL:
        raise RuntimeError("Q0 model binding drift")
    if q.get("decision") != "Q0_PROVIDER_ACTION_INTERFACE_QUALIFIED" or q.get("frozen_output_token_budget") != FIRST_DECISION_BUDGET:
        raise RuntimeError("Q0 first-decision qualification drift")
    return {"binding": b, "qualification": q}


def make_expected_command(fixture_id: str, line_count: int) -> str:
    lines = [f"{fixture_id}_LINE_{i:04d}_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for i in range(1, line_count + 1)]
    payload = "\n".join(lines)
    return f"cat <<'EOF' > /tmp/{fixture_id}.txt\n{payload}\nEOF"


def fixtures(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Cross action size with accumulated context.  Largest command is deliberately
    # well above what the historical 512-token source episode could carry.
    for history_pairs in (0, 4, 12, 24):
        for line_count in (80, 160, 320):
            fixture_id = f"qwen397_source_budget_h{history_pairs}_l{line_count}"
            expected = make_expected_command(fixture_id, line_count)
            task = (
                "Synthetic non-scientific full-source action-budget qualification. "
                "Do not inspect or modify a scientific task. Follow the interactive shell envelope only."
            )
            messages = initial_messages(task, config)
            filler = "SYNTHETIC_OBSERVATION_" + ("0123456789abcdef" * 64)
            for index in range(history_pairs):
                messages.append({"role": "assistant", "content": f"THOUGHT: synthetic history {index}.\n\n```bash\nprintf SYNTHETIC_{index}\n```"})
                messages.append({"role": "user", "content": filler + f"_{index}"})
            messages.append({
                "role": "user",
                "content": (
                    "Qualification step: return exactly ONE fenced bash action. The bash action inside the fence must be "
                    "EXACTLY the command below, byte-for-byte after trimming the outer fence. Do not shorten, compress, "
                    "replace with a loop, or omit any payload line. A THOUGHT paragraph outside the fence is allowed.\n\n"
                    + expected
                ),
            })
            rows.append({
                "fixture_id": fixture_id,
                "history_pairs": history_pairs,
                "line_count": line_count,
                "expected_action": expected,
                "expected_action_sha256": sha256_text(expected),
                "messages": messages,
            })
    if len(rows) != FIXTURE_COUNT:
        raise AssertionError("fixture cardinality drift")
    return rows


def call_one(key: str, root: Path, index: int, fixture: dict[str, Any]) -> dict[str, Any]:
    packet = {
        "model": MODEL,
        "messages": fixture["messages"],
        "stream": False,
        "n": 1,
        "max_completion_tokens": SOURCE_OUTPUT_BUDGET,
        "temperature": 0.0,
        "enable_thinking": False,
        "enable_search": False,
    }
    safe = {
        "endpoint": AA_BASE_URL + "/chat/completions",
        "method": "POST",
        "body": packet,
        "authorization_material_persisted": False,
        "transport_attempt": 1,
        "provider_retries": 0,
    }
    raw_root = root / "raw"
    req_path = raw_root / f"request-{index:04d}.json"
    res_path = raw_root / f"response-{index:04d}.json"
    req_sha = atomic_bytes(req_path, (canonical(safe) + "\n").encode())
    request = urllib.request.Request(
        AA_BASE_URL + "/chat/completions",
        data=canonical(packet).encode(),
        method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    status = None
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            status = int(response.status)
            raw = response.read()
    except urllib.error.HTTPError as error:
        status = int(error.code)
        raw = error.read()
    res_sha = atomic_bytes(res_path, raw)
    base = {
        "fixture_id": fixture["fixture_id"],
        "history_pairs": fixture["history_pairs"],
        "line_count": fixture["line_count"],
        "status_code": status,
        "request_path": str(req_path),
        "request_sha256": req_sha,
        "response_path": str(res_path),
        "response_sha256": res_sha,
        "persisted_before_parse": True,
        "requested_model": MODEL,
        "max_completion_tokens": SOURCE_OUTPUT_BUDGET,
        "provider_retries": 0,
    }
    if status is None or not 200 <= status < 300:
        row = {**base, "pass": False, "parse_status": "NOT_PARSED_HTTP_ERROR", "failure": f"HTTP_{status}"}
        atomic_json(root / "calls" / f"{index:04d}.json", row)
        return row
    try:
        payload = json.loads(raw.decode())
        choice = payload["choices"][0]
        content = str(choice["message"]["content"])
        action = parse_action(content)
        resolved = str(payload.get("model") or "")
        finish_reason = str(choice.get("finish_reason") or "")
        exact = action == fixture["expected_action"]
        passed = resolved == MODEL and finish_reason == "stop" and exact
        row = {
            **base,
            "pass": passed,
            "parse_status": "PARSED",
            "resolved_model": resolved,
            "model_drift": resolved != MODEL,
            "finish_reason": finish_reason,
            "action_sha256": sha256_text(action),
            "expected_action_sha256": fixture["expected_action_sha256"],
            "exact_action_match": exact,
            "usage": payload.get("usage") if isinstance(payload.get("usage"), dict) else {},
            "response_id": str(payload.get("id") or ""),
            "content_chars": len(content),
            "action_chars": len(action),
        }
    except Exception as error:
        row = {**base, "pass": False, "parse_status": "PARSE_FAILED", "failure": f"{type(error).__name__}: {error}"}
    atomic_json(root / "calls" / f"{index:04d}.json", row)
    return row


def run(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError(f"qualification root exists; no overwrite/retry: {root}")
    verify_parent()
    key = require_key()
    config = yaml.safe_load(CONFIG.read_text())
    rowspec = fixtures(config)
    root.mkdir(parents=True)
    contract = {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-RB-QWEN397-SOURCE-BUDGET-Q0-20260901",
        "non_scientific": True,
        "model": MODEL,
        "source_trajectory_output_budget_candidate": SOURCE_OUTPUT_BUDGET,
        "pacta_first_decision_budget_unchanged": FIRST_DECISION_BUDGET,
        "fixture_count": FIXTURE_COUNT,
        "fixture_grid": {"history_pairs": [0, 4, 12, 24], "payload_lines": [80, 160, 320]},
        "pass_rule": "12/12 HTTP success, persisted-before-parse, exact model, finish_reason=stop, exactly one fenced bash action, exact expected action bytes after fence trimming",
        "scientific_source_tasks_used": 0,
        "v5_source_task_replayed": False,
        "provider_retries": 0,
        "fallback": False,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
    }
    atomic_json(root / "contract.json", contract)
    rows = []
    for index, fixture in enumerate(rowspec, 1):
        row = call_one(key, root, index, fixture)
        rows.append(row)
        print(json.dumps({"fixture": row["fixture_id"], "pass": row["pass"], "finish_reason": row.get("finish_reason"), "status": row["status_code"]}), flush=True)
        # Fixed pacing is part of infrastructure qualification, not an adaptive retry.
        if index < FIXTURE_COUNT:
            time.sleep(2.0)
    passed = len(rows) == FIXTURE_COUNT and all(row.get("pass") for row in rows)
    prompt_tokens = sum(int((row.get("usage") or {}).get("prompt_tokens") or 0) for row in rows)
    completion_tokens = sum(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "decision": "SOURCE_TRAJECTORY_BUDGET_4096_QUALIFIED" if passed else "STOP_SOURCE_TRAJECTORY_BUDGET_4096_UNQUALIFIED",
        "pass": passed,
        "source_trajectory_output_budget": SOURCE_OUTPUT_BUDGET if passed else None,
        "pacta_first_decision_budget": FIRST_DECISION_BUDGET,
        "rows": rows,
        "qualified": sum(bool(row.get("pass")) for row in rows),
        "total": FIXTURE_COUNT,
        "provider_calls": len(rows),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "scientific_source_tasks_used": 0,
        "v5_source_task_replayed": False,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
        "claim_authority": "NO_NEW_PACTA_EFFECT_EVIDENCE",
    }
    atomic_json(root / "qualification-result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    result = run(args.root)
    print(json.dumps({"decision": result["decision"], "qualified": result["qualified"], "total": result["total"], "provider_calls": result["provider_calls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
