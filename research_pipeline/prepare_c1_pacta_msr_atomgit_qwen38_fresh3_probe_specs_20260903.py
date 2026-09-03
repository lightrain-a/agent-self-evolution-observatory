#!/usr/bin/env python3
"""Freeze deterministic, branch-blind MSR probe commands for the fresh3 pool.

This stage is intentionally runtime-independent and provider-free. It sees only the
already-frozen future task text and freezes the exact read-only command bytes before
any fresh3 source trajectory is acquired.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
POOL_SHA = "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-probe-specs-20260903.json"
TOKEN_SALT = "C1-PACTA-MSR-FRESH3-PROBE-TOKEN-v1"
STOP = {
    "about", "after", "again", "also", "another", "argument", "because", "before", "being",
    "between", "both", "bug", "calling", "case", "change", "changes", "code", "could", "current",
    "describe", "does", "doesn", "error", "expected", "false", "feature", "file", "files", "fix",
    "format", "from", "good", "have", "into", "issue", "letters", "like", "method", "more", "need",
    "none", "only", "other", "plus", "problem", "python", "same", "should", "system", "test", "tests",
    "that", "their", "then", "there", "these", "this", "true", "using", "value", "values", "want",
    "when", "where", "which", "with", "working", "would", "your",
}
LEX = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.-]{2,}\b")
BACKTICK = re.compile(r"`([^`\n]{2,120})`")
CODEBLOCK = re.compile(r"```(?:[A-Za-z0-9_+.-]+)?\s*\n(.*?)```", re.S)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def normalize_token(value: str) -> str:
    value = value.strip().strip("()[]{}:,;")
    if value.endswith("()"):
        value = value[:-2]
    return value[:100]


def candidates(task: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    seen: set[str] = set()

    def add(priority: int, text: str, *, code: bool = False) -> None:
        for raw in LEX.findall(text):
            token = normalize_token(raw)
            low = token.lower()
            minlen = 3 if code else 4
            if len(token) < minlen or low in STOP or low in seen:
                continue
            seen.add(low)
            out.append((priority, token))

    for raw in BACKTICK.findall(task):
        add(0, raw, code=True)
    for raw in CODEBLOCK.findall(task):
        codeish = " ".join(
            token for token in LEX.findall(raw)
            if any(c in token for c in "_.-") or any(c.isupper() for c in token[1:])
        )
        add(0, codeish, code=True)
    title = next((line.strip() for line in task.splitlines() if line.strip()), "")
    add(1, title)
    for raw in CODEBLOCK.findall(task):
        add(2, raw, code=True)
    add(3, task)
    return out


def compile_tokens(task: str, task_sha: str) -> list[str]:
    ranked = sorted(
        candidates(task),
        key=lambda row: (row[0], sha(TOKEN_SALT + "|" + task_sha + "|" + row[1].lower()), row[1].lower(), row[1]),
    )
    if len(ranked) < 3:
        raise RuntimeError("STOP_FRESH3_MSR_PROBE_TOKEN_SUPPORT_INSUFFICIENT")
    return [row[1] for row in ranked[:3]]


def compile_command(tokens: list[str]) -> str:
    if len(tokens) != 3:
        raise ValueError("exactly three tokens required")
    expr = " ".join("-e " + shlex.quote(token) for token in tokens)
    return f"git status --short; git grep -n -I {expr} -- . | head -n 80; git ls-files | head -n 40"


def prepare() -> dict[str, Any]:
    if sha256_file(POOL) != POOL_SHA:
        raise RuntimeError("fresh3 pool drift")
    pool = json.loads(POOL.read_text())
    rows = []
    for unit in pool["units"]:
        tokens = compile_tokens(unit["future_task"], unit["future_task_sha256"])
        command = compile_command(tokens)
        rows.append({
            "unit_id": unit["unit_id"],
            "future_task_id": unit["future_task_id"],
            "future_task_sha256": unit["future_task_sha256"],
            "future_base_commit": unit["future_base_commit"],
            "tokens": tokens,
            "command": command,
            "command_sha256": sha(command),
            "probe_timeout_seconds": 60,
            "provider_calls": 0,
            "future_task_executions": 0,
            "branch_blind": True,
            "memory_blind": True,
            "read_only": True,
            "runtime_binding": "DEFERRED_UNTIL_FRESH3_20_RUNTIME_READY",
        })
    if len(rows) != 10 or len({row["future_task_id"] for row in rows}) != 10:
        raise RuntimeError("fresh3 probe geometry drift")
    return {
        "schema_version": 1,
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-PROBE-SPECS-20260903",
        "status": "FRESH3_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME",
        "fresh_pool_sha256": POOL_SHA,
        "token_salt": TOKEN_SALT,
        "selection_priority": [
            "explicit_inline_or_codeish_block",
            "issue_title",
            "other_code_block",
            "full_task_fallback",
        ],
        "rows": rows,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
    }


def main() -> None:
    if OUT.exists():
        raise RuntimeError("fresh3 probe specs already exist; no overwrite")
    result = prepare()
    atomic_json(OUT, result)
    print(json.dumps({"status": result["status"], "specs": len(result["rows"]), "sha256": sha256_file(OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
