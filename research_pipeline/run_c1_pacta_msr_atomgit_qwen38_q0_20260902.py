#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_provider import _message_text_from_jsonl
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file, sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import parse_action

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q0-contract-20260902.json"
UPSTREAM = ROOT / "generated/agent-constraint-externality-codingplan-qwen38-provider-qualification-c1-20260902.json"
ATOMCODE = Path("/home/wyt/.local/bin/atomcode")
AUTH = Path("/home/wyt/.atomcode/auth.toml")
SYNC_CONFIG = Path("/home/wyt/.atomcode/config.toml")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q0-20260902-v1")
PROFILE = "AtomGit-qwen3.8-27b"
MODEL = "qwen3.8-27b"
CONTEXT_WINDOW = 262144
FIRST_BUDGETS = (512, 1024, 2048, 4096)
SOURCE_BUDGETS = (4096, 16384, 32768)
SYSTEM_PROMPT = (
    "You are a text-only model inside a controlled offline research qualification. "
    "Native tools are unavailable. Follow the EXPERIMENTAL_CONVERSATION supplied by the user and return only the next assistant message requested by that conversation. "
    "Do not inspect files, execute commands, or claim that an action ran."
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_config(path: Path, max_tokens: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            f'default_provider = "{PROFILE}"',
            f'default_model = "{PROFILE}"',
            "auto_update = false",
            "lsp.enabled = false",
            "subagent.enabled = false",
            "tools.todo.enabled = false",
            "",
            "[provider_accounts.AtomGit]",
            'provider = "openai"',
            'base_url = "https://llm-api.atomgit.com/v1"',
            "",
            f'[models."{PROFILE}"]',
            'account = "AtomGit"',
            f'model = "{MODEL}"',
            f'context_window = {CONTEXT_WINDOW}',
            f'max_tokens = {max_tokens}',
            'retry_max_attempts = 1',
            'system_prompt = ' + json.dumps(SYSTEM_PROMPT, ensure_ascii=False),
            "",
            "[coding]",
            "max_rounds = 1",
            "",
            "[network.proxy]",
            'mode = "follow_system"',
            "",
            "[datalog]",
            "enabled = false",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")
    os.chmod(path, 0o600)


def serialize_messages(messages: list[dict[str, str]]) -> str:
    payload = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (
        "EXPERIMENTAL_CONVERSATION_JSON:\n"
        + payload
        + "\n\nReturn exactly the next assistant message for this conversation. Do not add meta-commentary about AtomCode."
    )


def call(root: Path, phase: str, index: int, messages: list[dict[str, str]], max_tokens: int, label: str) -> dict[str, Any]:
    config = root / "configs" / f"max-{max_tokens}.toml"
    if not config.exists():
        write_config(config, max_tokens)
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
        "prompt_sha256": sha256_text(prompt),
        "config_sha256": sha256_file(config),
        "flags": ["--no-tools", "--ephemeral", "--no-telemetry", "--output-format=jsonl"],
        "provider_retries": 0,
        "authorization_material_persisted": False,
    }
    req_sha = atomic_bytes(request_path, (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
    fd, prompt_name = tempfile.mkstemp(prefix="c1-atomgit-q0-", suffix=".txt", dir="/tmp")
    prompt_path = Path(prompt_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(prompt)
            handle.flush(); os.fsync(handle.fileno())
        cmd = [
            str(ATOMCODE), "--config", str(config), "--provider", PROFILE,
            "--no-tools", "--ephemeral", "--no-telemetry", "--output-format", "jsonl",
            "-C", str(workdir), "--prompt-file", str(prompt_path),
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True, timeout=300, check=False)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""; err = exc.stderr or ""
        if isinstance(out, bytes): out = out.decode(errors="replace")
        if isinstance(err, bytes): err = err.decode(errors="replace")
        atomic_bytes(stdout_path, out.encode()); atomic_bytes(stderr_path, err.encode())
        row = {**safe, "request_sha256": req_sha, "pass": False, "failure": "TIMEOUT", "returncode": 124}
        atomic_json(root / phase / "calls" / f"{stem}.json", row)
        return row
    finally:
        prompt_path.unlink(missing_ok=True)
    stdout_sha = atomic_bytes(stdout_path, completed.stdout.encode())
    stderr_sha = atomic_bytes(stderr_path, completed.stderr.encode())
    base = {**safe, "request_sha256": req_sha, "stdout_sha256": stdout_sha, "stderr_sha256": stderr_sha, "returncode": completed.returncode, "persisted_before_parse": True}
    if completed.returncode != 0:
        row = {**base, "pass": False, "failure": "ATOMCODE_NONZERO", "stderr_tail_sha256": sha256_text(completed.stderr[-1000:])}
        atomic_json(root / phase / "calls" / f"{stem}.json", row)
        return row
    try:
        text, meta = _message_text_from_jsonl(completed.stdout)
        started = meta["started"]; usage = meta["usage"]
        started_model = str(started.get("model", ""))
        identity = started_model in {MODEL, PROFILE}
        row = {
            **base, "pass": identity and bool(text.strip()), "parse_status": "JSONL_PARSED",
            "started_model": started_model, "model_identity_pass": identity,
            "assistant_text": text, "assistant_text_sha256": sha256_text(text),
            "usage": usage, "codingplan_requests": 1,
        }
    except Exception as exc:
        row = {**base, "pass": False, "parse_status": "JSONL_PARSE_FAILED", "failure": f"{type(exc).__name__}:{exc}"}
    atomic_json(root / phase / "calls" / f"{stem}.json", row)
    return row


def first_action_fixtures() -> list[dict[str, Any]]:
    rows = []
    for i in range(1, 21):
        marker = f"ATOMGIT_Q0_MARKER_{i:02d}"
        messages = [
            {"role": "system", "content": "You are a MiniSWEAgent-compatible coding agent. On each turn return exactly one bash command inside one ```bash fenced block. Do not execute it yourself."},
            {"role": "user", "content": f"Synthetic qualification task only. Your first action should inspect the marker {marker}. Return one simple read-only bash command now."},
        ]
        rows.append({"fixture_id": f"first-{i:02d}", "messages": messages})
    return rows


def long_command(fid: str, n: int) -> str:
    payload = "\n".join(f"{fid}_LINE_{i:04d}_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for i in range(1, n + 1))
    return f"cat <<'EOF' > /tmp/{fid}.txt\n{payload}\nEOF"


def long_fixtures() -> list[dict[str, Any]]:
    rows = []
    for h in (0, 12, 24):
        for n in (160, 320):
            fid = f"atomgit_qwen38_long_h{h}_l{n}"
            expected = long_command(fid, n)
            messages = [{"role": "system", "content": "Transport qualification only. Return exactly one fenced bash block containing the exact command requested. No prose, compression, loops, substitutions, or explanation."}]
            filler = "SYNTHETIC_CONTEXT_" + ("0123456789abcdef" * 64)
            for j in range(h):
                messages.append({"role": "user", "content": filler + f"_USER_{j}"})
                messages.append({"role": "assistant", "content": f"ACK_{j}"})
            messages.append({"role": "user", "content": "Return this command exactly, byte-for-byte inside one ```bash fence:\n\n" + expected})
            rows.append({"fixture_id": fid, "history_pairs": h, "line_count": n, "expected": expected, "expected_sha256": sha256_text(expected), "messages": messages})
    return rows


def identity(root: Path) -> dict[str, Any]:
    if (root / "identity-result.json").exists(): raise RuntimeError("identity exists; no overwrite")
    rows = []
    for i in range(1, 4):
        messages = [{"role": "user", "content": f"Non-scientific identity qualification {i}. Reply with exactly IDENTITY_OK_{i}."}]
        row = call(root, "identity", i, messages, 512, f"identity-{i}")
        exact = row.get("assistant_text", "").strip() == f"IDENTITY_OK_{i}"
        row["exact_text_pass"] = exact; row["pass"] = bool(row.get("pass")) and exact
        atomic_json(root / "identity" / "adjudicated" / f"{i:04d}.json", row)
        rows.append(row)
    passed = len(rows) == 3 and all(r.get("pass") for r in rows)
    result = {"schema_version": 1, "created_at_utc": now(), "status": "ATOMGIT_QWEN38_IDENTITY_PASS" if passed else "STOP_ATOMGIT_QWEN38_IDENTITY", "pass": passed, "qualified": sum(bool(r.get("pass")) for r in rows), "total": 3, "rows": rows, "scientific_source_tasks_used": 0}
    atomic_json(root / "identity-result.json", result); return result


def first_action(root: Path) -> dict[str, Any]:
    if json.loads((root / "identity-result.json").read_text()).get("pass") is not True: raise RuntimeError("identity not passed")
    if (root / "first-action-result.json").exists(): raise RuntimeError("first-action exists; no overwrite")
    chosen = None; budget_results = []
    for budget in FIRST_BUDGETS:
        rows = []
        for i, fx in enumerate(first_action_fixtures(), 1):
            row = call(root, f"first-action-{budget}", i, fx["messages"], budget, fx["fixture_id"])
            try:
                action = parse_action(str(row.get("assistant_text") or "")); parsed = True
            except Exception as exc:
                action = ""; parsed = False; row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
            row["action_parse_pass"] = parsed; row["action_sha256"] = sha256_text(action) if action else ""; row["pass"] = bool(row.get("pass")) and parsed
            atomic_json(root / f"first-action-{budget}" / "adjudicated" / f"{i:04d}.json", row); rows.append(row)
        ok = len(rows) == 20 and all(r.get("pass") for r in rows)
        budget_results.append({"budget": budget, "qualified": sum(bool(r.get("pass")) for r in rows), "total": 20, "pass": ok})
        if ok: chosen = budget; break
    result = {"schema_version": 1, "created_at_utc": now(), "status": "ATOMGIT_QWEN38_FIRST_ACTION_PASS" if chosen else "STOP_ATOMGIT_QWEN38_FIRST_ACTION", "pass": chosen is not None, "first_decision_budget": chosen, "budget_results": budget_results, "scientific_source_tasks_used": 0}
    atomic_json(root / "first-action-result.json", result); return result


def source_budget(root: Path) -> dict[str, Any]:
    if json.loads((root / "first-action-result.json").read_text()).get("pass") is not True: raise RuntimeError("first action not passed")
    if (root / "source-budget-result.json").exists(): raise RuntimeError("source budget exists; no overwrite")
    chosen = None; budget_results = []
    for budget in SOURCE_BUDGETS:
        rows = []
        for i, fx in enumerate(long_fixtures(), 1):
            row = call(root, f"source-budget-{budget}", i, fx["messages"], budget, fx["fixture_id"])
            try:
                action = parse_action(str(row.get("assistant_text") or "")); parsed = True
            except Exception as exc:
                action = ""; parsed = False; row["action_parse_failure"] = f"{type(exc).__name__}:{exc}"
            exact = parsed and action == fx["expected"]
            row.update({"action_parse_pass": parsed, "exact_action_match": exact, "expected_action_sha256": fx["expected_sha256"], "action_sha256": sha256_text(action) if action else "", "history_pairs": fx["history_pairs"], "line_count": fx["line_count"]})
            row["pass"] = bool(row.get("pass")) and exact
            atomic_json(root / f"source-budget-{budget}" / "adjudicated" / f"{i:04d}.json", row); rows.append(row)
        ok = len(rows) == 6 and all(r.get("pass") for r in rows)
        budget_results.append({"budget": budget, "qualified": sum(bool(r.get("pass")) for r in rows), "total": 6, "pass": ok})
        if ok: chosen = budget; break
    result = {"schema_version": 1, "created_at_utc": now(), "status": "ATOMGIT_QWEN38_SOURCE_BUDGET_PASS" if chosen else "STOP_ATOMGIT_QWEN38_SOURCE_BUDGET", "pass": chosen is not None, "source_trajectory_budget": chosen, "budget_results": budget_results, "scientific_source_tasks_used": 0}
    atomic_json(root / "source-budget-result.json", result); return result


def sampling(root: Path) -> dict[str, Any]:
    first = json.loads((root / "first-action-result.json").read_text()); budget = int(first["first_decision_budget"])
    if (root / "sampling-diagnostic.json").exists(): raise RuntimeError("sampling exists; no overwrite")
    fixtures = first_action_fixtures()[:2]; rows = []
    for fi, fx in enumerate(fixtures, 1):
        actions = []
        for rep in range(1, 7):
            idx = (fi - 1) * 6 + rep
            row = call(root, "sampling", idx, fx["messages"], budget, f"sampling-{fi}-{rep}")
            try: action = parse_action(str(row.get("assistant_text") or ""))
            except Exception: action = "PARSE_FAIL"
            actions.append(action); rows.append({"fixture": fi, "replicate": rep, "action": action, "action_sha256": sha256_text(action), "model_identity_pass": row.get("model_identity_pass"), "codingplan_requests": row.get("codingplan_requests")})
    per = []
    for fi in (1, 2):
        a = [r["action"] for r in rows if r["fixture"] == fi]; per.append({"fixture": fi, "unique_action_count": len(set(a)), "actions": a})
    result = {"schema_version": 1, "created_at_utc": now(), "status": "DIAGNOSTIC_ONLY", "pass_requirement": False, "first_decision_budget": budget, "per_fixture": per, "rows": rows, "scientific_source_tasks_used": 0}
    atomic_json(root / "sampling-diagnostic.json", result); return result


def prepare(root: Path) -> dict[str, Any]:
    if root.exists(): raise RuntimeError("Q0 root exists; no overwrite")
    if not ATOMCODE.is_file() or not AUTH.is_file() or not SYNC_CONFIG.is_file(): raise RuntimeError("STOP_ATOMCODE_LOGIN_OR_BINARY_MISSING")
    root.mkdir(parents=True)
    version = subprocess.run([str(ATOMCODE), "--version"], text=True, capture_output=True, check=True).stdout.strip()
    upstream_sha = sha256_file(UPSTREAM) if UPSTREAM.is_file() else ""
    contract_sha = sha256_file(CONTRACT)
    configs = {}
    for budget in sorted(set(FIRST_BUDGETS + SOURCE_BUDGETS)):
        p = root / "configs" / f"max-{budget}.toml"; write_config(p, budget); configs[str(budget)] = sha256_file(p)
    result = {"schema_version": 1, "created_at_utc": now(), "status": "ATOMGIT_QWEN38_Q0_PREPARE_PASS", "atomcode_version": version, "atomcode_binary_sha256": sha256_file(ATOMCODE), "auth_present": True, "auth_mode": oct(AUTH.stat().st_mode & 0o777), "sync_config_sha256": sha256_file(SYNC_CONFIG), "upstream_provider_qualification_sha256": upstream_sha, "contract_sha256": contract_sha, "experiment_config_sha256": configs, "scientific_source_tasks_used": 0, "writer_calls": 0, "binder_calls": 0, "shadow_calls": 0, "final_measurement_calls": 0}
    atomic_json(root / "prepare.json", result); return result


def close(root: Path) -> dict[str, Any]:
    ids = json.loads((root / "identity-result.json").read_text()); first = json.loads((root / "first-action-result.json").read_text()); source = json.loads((root / "source-budget-result.json").read_text()); samp = json.loads((root / "sampling-diagnostic.json").read_text())
    passed = ids.get("pass") is True and first.get("pass") is True and source.get("pass") is True
    result = {"schema_version": 1, "created_at_utc": now(), "status": "ATOMGIT_QWEN38_Q0_PASS" if passed else "STOP_ATOMGIT_QWEN38_Q0", "pass": passed, "model_condition": "AtomGit CodingPlan / AtomCode-mediated Qwen3.8-27B", "resolved_model": MODEL, "first_decision_budget": first.get("first_decision_budget"), "source_trajectory_budget": source.get("source_trajectory_budget"), "sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9", "sampling_diagnostic": samp.get("per_fixture"), "scientific_source_tasks_used": 0, "future_task_executions": 0, "writer_calls": 0, "binder_calls": 0, "shadow_calls": 0, "final_measurement_calls": 0, "other_models_used": 0, "next_if_pass": "Prospective AtomGit Qwen3.8 source acquisition on the already frozen ten fresh PACTA-MSR units; no model shopping."}
    atomic_json(root / "q0-closure.json", result); return result


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", type=Path, default=DEFAULT_ROOT); ap.add_argument("--phase", choices=("prepare", "identity", "first-action", "source-budget", "sampling", "close"), required=True); a = ap.parse_args()
    fn = {"prepare": prepare, "identity": identity, "first-action": first_action, "source-budget": source_budget, "sampling": sampling, "close": close}[a.phase]
    result = fn(a.root); print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__": main()
