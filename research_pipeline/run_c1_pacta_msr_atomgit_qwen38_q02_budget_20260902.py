#!/usr/bin/env python3
"""Q0.2 source-output budget qualification for AtomGit/AtomCode Qwen3.8.

Two non-scientific panels are required:
A) exact long-action transport regression;
B) realistic synthetic MiniSWEAgent multi-turn next-action envelopes.
No real PACTA source or future task is reachable from this runner.
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

import yaml

from research_pipeline.agent_constraint_externality_codingplan_provider import _message_text_from_jsonl
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import initial_messages, parse_action, render
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import (
    ATOMCODE,
    AUTH,
    MODEL,
    PROFILE,
    SYNC_CONFIG,
    long_fixtures,
    serialize_messages,
    write_config,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q02-source-budget-contract-20260902.json"
Q0V2_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0v2-timeout-20260902-v1")
T0_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-t0-source-closeout-20260902.json"
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
CONFIG = OFFICIAL / "third_party/src/minisweagent/config/extra/swebench.yaml"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q02-budget-20260902-v1")

BUDGETS = (32768, 65536)
TIMEOUT_SECONDS = 900
FIRST_DECISION_BUDGET = 2048
REALISTIC_HISTORY_PAIRS = (18, 24, 30, 36, 42, 48)
SAMPLING_CONTROL = "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"
EXPECTED = {
    "base_q0_runner": "11c5da1d954db4cfb45695b785d2db231744b9ab8174c08af1e4e75fa68df439",
    "q0v2_runner": "fdad87f8168285de71d5770a156a8f768dd2a02374871a94a3621fa673b433f3",
    "q0v2_closure": "19ec9c078b2c4a6f3ec77eee181b47a4f7cc082a516eff0074feace7a74e6f70",
    "q0v2_source_budget": "8eead97e1a3b39a701886a24a4597e2ce607ee50580803a5655c7ac4087c4198",
    "q0v2_sampling": "6398f0d9a5d29888a0003fc7783f7a41732d3e38cf396ea13f80b46ee2ef3b64",
    "failed_t0_closeout": "1796b9739e85065405d70f2f1f5e60376a38d2f66bc048bea99f57cbed388db4",
    "official_config": "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def verify_parent() -> dict[str, str]:
    observed = {
        "base_q0_runner": sha256_file(ROOT / "research_pipeline/run_c1_pacta_msr_atomgit_qwen38_q0_20260902.py"),
        "q0v2_runner": sha256_file(ROOT / "research_pipeline/run_c1_pacta_msr_atomgit_qwen38_q0_v2_timeout_20260902.py"),
        "q0v2_closure": sha256_file(Q0V2_ROOT / "q0-closure.json"),
        "q0v2_source_budget": sha256_file(Q0V2_ROOT / "source-budget-result.json"),
        "q0v2_sampling": sha256_file(Q0V2_ROOT / "sampling-diagnostic.json"),
        "failed_t0_closeout": sha256_file(T0_CLOSEOUT),
        "official_config": sha256_file(CONFIG),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"STOP_Q02_PARENT_DRIFT:{observed}")
    q0 = json.loads((Q0V2_ROOT / "q0-closure.json").read_text())
    if (
        q0.get("pass") is not True
        or q0.get("resolved_model") != MODEL
        or q0.get("first_decision_budget") != FIRST_DECISION_BUDGET
        or q0.get("atomcode_subprocess_timeout_seconds") != TIMEOUT_SECONDS
    ):
        raise RuntimeError("STOP_Q02_PARENT_Q0_DRIFT")
    t0 = json.loads(T0_CLOSEOUT.read_text())
    if t0.get("status") != "HOLD_ATOMGIT_MSR_SOURCE_SUPPORT_INSUFFICIENT_REAL_TASK_OUTPUT_TRUNCATION":
        raise RuntimeError("STOP_Q02_T0_FAILURE_CLASS_DRIFT")
    return observed


def synthetic_output(fixture: int, step: int) -> str:
    marker = f"SYNQ02_F{fixture:02d}_S{step:02d}"
    rows = [
        f"{i:03d} src/synthetic_module_{fixture}.py:{100+i}: def synthetic_handler_{i}(state, value): # {marker} branch_{i%7}"
        for i in range(1, 31)
    ]
    rows.extend(
        [
            f"TRACE {marker} candidate={i} status={'mismatch' if i % 3 == 0 else 'consistent'} expected=normalized_{i%5} observed=variant_{i%4}"
            for i in range(1, 11)
        ]
    )
    return "\n".join(rows)


def realistic_fixtures() -> list[dict[str, Any]]:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    fixtures: list[dict[str, Any]] = []
    for fixture_id, history_pairs in enumerate(REALISTIC_HISTORY_PAIRS, 1):
        task = (
            f"Synthetic qualification task Q02-{fixture_id}: a toy parser/registry implementation has an inconsistent "
            "normalization path between direct lookup, registered aliases, and delayed object construction. Diagnose the "
            "next useful repository inspection step. This is synthetic transport qualification; do not submit completion "
            "and do not assume any hidden tests."
        )
        messages = initial_messages(task, cfg)
        variables = {"task": task, "selected_memory": ""}
        for step in range(1, history_pairs + 1):
            command = (
                f"grep -rn \"SYNQ02_F{fixture_id:02d}_S{step:02d}\" src/ synthetic/ 2>/dev/null | head -40"
                if step % 3
                else f"nl -ba src/synthetic_module_{fixture_id}.py | sed -n '{80+step},{150+step}p'"
            )
            assistant = (
                f"THOUGHT: Synthetic history step {step}. I need to distinguish alias normalization from object-name "
                "propagation without editing files yet.\n\n```bash\n" + command + "\n```"
            )
            messages.append({"role": "assistant", "content": assistant})
            obs = {"output": synthetic_output(fixture_id, step), "returncode": 0, "timeout": False}
            user = render(cfg["agent"]["action_observation_template"], variables, output=obs)
            messages.append({"role": "user", "content": user})
        final_note = (
            "The synthetic evidence remains deliberately ambiguous: direct lookup, alias registration, and delayed "
            "construction disagree in different branches. Choose exactly one next read-only bash diagnostic command. "
            "Do not edit files and do not submit completion yet."
        )
        messages.append({"role": "user", "content": final_note})
        serialized = serialize_messages(messages)
        fixtures.append(
            {
                "fixture_id": f"q02-realistic-h{history_pairs}",
                "history_pairs": history_pairs,
                "messages": messages,
                "serialized_chars": len(serialized),
                "messages_sha256": sha256_text(serialized),
            }
        )
    if len(fixtures) != 6:
        raise AssertionError("realistic fixture geometry")
    return fixtures


def invoke(
    root: Path,
    phase: str,
    index: int,
    messages: list[dict[str, str]],
    budget: int,
    label: str,
) -> dict[str, Any]:
    config = root / "configs" / f"max-{budget}.toml"
    if not config.exists():
        write_config(config, budget)
    workdir = root / "empty-workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    prompt = serialize_messages(messages)
    stem = f"{index:04d}__{re.sub(r'[^A-Za-z0-9_.-]+','_',label)[:120]}"
    req_path = root / phase / "raw" / f"{stem}.request.json"
    stdout_path = root / phase / "raw" / f"{stem}.stdout.jsonl"
    stderr_path = root / phase / "raw" / f"{stem}.stderr.txt"
    safe = {
        "schema_version": 1,
        "created_at_utc": now(),
        "phase": phase,
        "label": label,
        "profile": PROFILE,
        "resolved_model_expected": MODEL,
        "max_tokens": budget,
        "atomcode_subprocess_timeout_seconds": TIMEOUT_SECONDS,
        "prompt_sha256": sha256_text(prompt),
        "config_sha256": sha256_file(config),
        "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
        "provider_retries": 0,
        "authorization_material_persisted": False,
    }
    req_sha = atomic_bytes(req_path, (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
    fd, prompt_name = tempfile.mkstemp(prefix="c1-q02-", suffix=".txt", dir="/tmp")
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
        stdout_sha = atomic_bytes(stdout_path, out.encode())
        stderr_sha = atomic_bytes(stderr_path, err.encode())
        row = {
            **safe,
            "request_sha256": req_sha,
            "stdout_sha256": stdout_sha,
            "stderr_sha256": stderr_sha,
            "returncode": 124,
            "failure": "TIMEOUT",
            "pass": False,
            "output_truncation_event": '"kind":"output_truncation"' in out,
            "max_rounds_event": '"stop_reason":"MaxRounds"' in out or '"max rounds' in out,
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
        "output_truncation_event": '"kind":"output_truncation"' in completed.stdout,
        "max_rounds_event": '"stop_reason":"MaxRounds"' in completed.stdout or '"max rounds' in completed.stdout,
    }
    if completed.returncode != 0:
        row = {**base, "pass": False, "failure": "ATOMCODE_NONZERO"}
        atomic_json(root / phase / "calls" / f"{stem}.json", row)
        return row
    try:
        text, meta = _message_text_from_jsonl(completed.stdout)
        started = meta["started"]
        usage = meta["usage"]
        model = str(started.get("model", ""))
        row = {
            **base,
            "pass": model in {MODEL, PROFILE} and bool(text.strip()),
            "parse_status": "JSONL_PARSED",
            "started_model": model,
            "model_identity_pass": model in {MODEL, PROFILE},
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
        raise RuntimeError("Q0.2 root exists; no overwrite")
    if not ATOMCODE.is_file() or not AUTH.is_file() or not SYNC_CONFIG.is_file():
        raise RuntimeError("STOP_Q02_ATOMCODE_LOGIN_OR_BINARY_MISSING")
    parent_hashes = verify_parent()
    root.mkdir(parents=True)
    configs = {}
    for budget in BUDGETS:
        p = root / "configs" / f"max-{budget}.toml"
        write_config(p, budget)
        configs[str(budget)] = sha256_file(p)
    realistic = realistic_fixtures()
    manifest = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q02_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "parent_hashes": parent_hashes,
        "candidate_budgets": list(BUDGETS),
        "timeout_seconds": TIMEOUT_SECONDS,
        "config_sha256": configs,
        "transport_fixture_count": len(long_fixtures()),
        "realistic_fixture_count": len(realistic),
        "realistic_fixtures": [
            {
                "fixture_id": x["fixture_id"],
                "history_pairs": x["history_pairs"],
                "serialized_chars": x["serialized_chars"],
                "messages_sha256": x["messages_sha256"],
            }
            for x in realistic
        ],
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "prepare.json", manifest)
    return manifest


def run_candidate(root: Path, budget: int) -> dict[str, Any]:
    phase_root = root / f"budget-{budget}"
    if phase_root.exists():
        raise RuntimeError(f"Q0.2 budget {budget} phase exists; no retry/overwrite")
    panel_a: list[dict[str, Any]] = []
    for i, fx in enumerate(long_fixtures(), 1):
        row = invoke(root, f"budget-{budget}/panel-a", i, fx["messages"], budget, fx["fixture_id"])
        try:
            action = parse_action(str(row.get("assistant_text") or ""))
            parse_ok = True
        except Exception as exc:
            action = ""
            parse_ok = False
            row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
        exact = parse_ok and action == fx["expected"]
        row.update(
            {
                "fixture_id": fx["fixture_id"],
                "action_parse_pass": parse_ok,
                "exact_action_match": exact,
                "expected_action_sha256": fx["expected_sha256"],
                "action_sha256": sha256_text(action) if action else "",
            }
        )
        row["pass"] = bool(row.get("pass")) and exact and not row.get("output_truncation_event") and not row.get("max_rounds_event") and int(row.get("codingplan_requests") or 0) == 1
        atomic_json(root / f"budget-{budget}/panel-a/adjudicated/{i:04d}.json", row)
        panel_a.append(row)
        print(json.dumps({"budget": budget, "panel": "A", "fixture": fx["fixture_id"], "pass": row["pass"], "failure": row.get("failure")}, sort_keys=True), flush=True)
    a_pass = len(panel_a) == 6 and all(x.get("pass") for x in panel_a)
    panel_b: list[dict[str, Any]] = []
    if a_pass:
        for i, fx in enumerate(realistic_fixtures(), 1):
            row = invoke(root, f"budget-{budget}/panel-b", i, fx["messages"], budget, fx["fixture_id"])
            try:
                action = parse_action(str(row.get("assistant_text") or ""))
                parse_ok = True
            except Exception as exc:
                action = ""
                parse_ok = False
                row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
            usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
            completion = int(usage.get("completion_tokens") or 0)
            row.update(
                {
                    "fixture_id": fx["fixture_id"],
                    "history_pairs": fx["history_pairs"],
                    "serialized_chars": fx["serialized_chars"],
                    "action_parse_pass": parse_ok,
                    "action_sha256": sha256_text(action) if action else "",
                    "completion_tokens": completion,
                    "strictly_below_budget": 0 < completion < budget,
                }
            )
            row["pass"] = bool(row.get("pass")) and parse_ok and 0 < completion < budget and not row.get("output_truncation_event") and not row.get("max_rounds_event") and int(row.get("codingplan_requests") or 0) == 1
            atomic_json(root / f"budget-{budget}/panel-b/adjudicated/{i:04d}.json", row)
            panel_b.append(row)
            print(json.dumps({"budget": budget, "panel": "B", "fixture": fx["fixture_id"], "pass": row["pass"], "completion_tokens": completion, "failure": row.get("failure")}, sort_keys=True), flush=True)
    b_pass = a_pass and len(panel_b) == 6 and all(x.get("pass") for x in panel_b)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "budget": budget,
        "panel_a_pass": a_pass,
        "panel_a_qualified": sum(bool(x.get("pass")) for x in panel_a),
        "panel_a_total": 6,
        "panel_b_executed": a_pass,
        "panel_b_pass": b_pass,
        "panel_b_qualified": sum(bool(x.get("pass")) for x in panel_b),
        "panel_b_total": 6 if a_pass else 0,
        "pass": a_pass and b_pass,
        "scientific_source_tasks_used": 0,
    }
    atomic_json(root / f"budget-{budget}/result.json", result)
    return result


def run(root: Path) -> dict[str, Any]:
    if json.loads((root / "prepare.json").read_text()).get("status") != "ATOMGIT_QWEN38_Q02_PREPARE_PASS":
        raise RuntimeError("Q0.2 prepare not passed")
    if (root / "q02-result.json").exists():
        raise RuntimeError("Q0.2 result exists; no overwrite")
    rows = []
    selected = None
    for budget in BUDGETS:
        result = run_candidate(root, budget)
        rows.append(result)
        if result["pass"]:
            selected = budget
            break
    status = "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS" if selected is not None else "STOP_ATOMGIT_QWEN38_Q02_SOURCE_BUDGET"
    out = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": status,
        "pass": selected is not None,
        "selected_source_budget": selected,
        "first_decision_budget_unchanged": FIRST_DECISION_BUDGET,
        "invocation_timeout_seconds": TIMEOUT_SECONDS,
        "candidate_results": rows,
        "scientific_source_tasks_used": 0,
        "retired_source_pool_reused": False,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_measurement_calls": 0,
    }
    atomic_json(root / "q02-result.json", out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--phase", choices=("prepare", "run"), required=True)
    args = ap.parse_args()
    result = prepare(args.root) if args.phase == "prepare" else run(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
