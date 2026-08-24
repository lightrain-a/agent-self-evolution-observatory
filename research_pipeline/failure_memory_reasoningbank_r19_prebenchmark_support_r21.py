#!/usr/bin/env python3
"""Fresh pre-benchmark support gate for the authorized B1/R19 experiment.

This gate performs no model completion and no browser action. It verifies the
local executor/evaluator aliases and tokenizers, performs one official Shopping
reset, resets R19 task 353, constructs its native evaluator, and closes the
environment before any step. Failure is pre-outcome support failure and blocks
all R19 benchmark execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.failure_memory_reasoningbank_l2b_execute_r18 import configure_environment, reset_shopping
from research_pipeline.failure_memory_reasoningbank_r19_execution_authority_r21 import require_authority

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPECTED_R19_CONTRACT_SHA = "ed803f0958002ab2095563a56cff6328a054ff4c4d7bd9fc18fc97bb3bdc3282"
EXPECTED_R21_AUTHORITY_RECEIPT_SHA = None  # bound at runtime by explicit --authority-receipt
EXPECTED_EXECUTOR_MANIFEST = "5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
SMOKE_TASK = "353"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def registry(base: str) -> dict[str, str]:
    with urllib.request.urlopen(base.rstrip("/") + "/api/tags", timeout=5) as r:
        obj = json.load(r)
    return {str(x["name"]): str(x.get("digest") or "") for x in obj.get("models", [])}


def tokenizer_rows() -> list[dict[str, Any]]:
    import tiktoken
    out = []
    for name in ["gpt-4", "gpt-4-1106-preview"]:
        enc = tiktoken.encoding_for_model(name)
        out.append({"model_name": name, "encoding": enc.name, "lookup_pass": True})
    return out


def execute(a: argparse.Namespace) -> dict[str, Any]:
    authority = require_authority(a.authority)
    if sha(a.contract) != EXPECTED_R19_CONTRACT_SHA:
        raise RuntimeError("R19 contract SHA drift")
    contract = load(a.contract)
    authority_receipt = load(a.authority_receipt)
    if authority_receipt.get("status") != "R19_EXTERNAL_HUMAN_BOUNDED_SCIENTIFIC_EXECUTION_AUTHORITY_VALID":
        raise RuntimeError("R21 authority receipt invalid")
    if authority_receipt.get("authority_artifact_sha256") != authority.get("artifact_sha256"):
        raise RuntimeError("authority artifact mismatch")
    if contract["execution_gate"]["R19_schedule_analysis_and_budgets_frozen"] is not True:
        raise RuntimeError("R19 contract not frozen")

    tags = registry(a.ollama_base)
    needed = ["b1-qwen25-32b-l2b-executor:latest", "gpt-4:latest", "gpt-4-1106-preview:latest"]
    if any(tags.get(k) != EXPECTED_EXECUTOR_MANIFEST for k in needed):
        raise RuntimeError("executor/evaluator alias manifest drift")
    toks = tokenizer_rows()

    reset = reset_shopping(a.reset_base, a.shopping_base, poll_seconds=a.reset_poll, timeout_seconds=a.reset_timeout)
    configure_environment(a.shopping_base, a.reset_base, a.playwright_browsers)
    sys.path.insert(0, str(a.rb_webarena_root))
    from agents.legacy.dynamic_prompting import Flags, _get_action_space
    from browsergym.experiments import EnvArgs

    flags = Flags(
        use_html=False, use_ax_tree=True, use_thinking=True, use_error_logs=True,
        use_memory=False, use_history=True, use_diff=False, use_past_error_logs=True,
        use_action_history=True, multi_actions=True, use_abstract_example=True,
        use_concrete_example=True, use_screenshot=False, enable_chat=True,
        demo_mode="default", action_space="bid",
    )
    action_set = _get_action_space(flags)
    env_args = EnvArgs(
        task_name=f"webarena.{SMOKE_TASK}", task_seed=0, max_steps=30,
        headless=True, viewport={"width": 1500, "height": 1280}, slow_mo=30,
    )
    a.smoke_root.mkdir(parents=True, exist_ok=True)
    env = None
    try:
        env = env_args.make_env(action_mapping=action_set.to_python_code, exp_dir=a.smoke_root)
        obs, info = env.reset(seed=0)
        task = env.unwrapped.task
        evaluator = getattr(task, "evaluator", None)
        if evaluator is None:
            raise RuntimeError("native evaluator missing after reset")
        evaluator_class = type(evaluator).__name__
        current_url = str(getattr(env.unwrapped.page, "url", ""))
        if not current_url.startswith(a.shopping_base.rstrip("/")):
            raise RuntimeError("smoke task did not reset onto Shopping")
    finally:
        if env is not None:
            env.close()

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PREBENCHMARK-SUPPORT-R21",
        "recorded_at": now(),
        "status": "R19_PREBENCHMARK_ZERO_COMPLETION_SUPPORT_GATE_PASS",
        "bindings": {
            "r19_contract_sha256": EXPECTED_R19_CONTRACT_SHA,
            "r21_authority_receipt_sha256": sha(a.authority_receipt),
            "authority_artifact_sha256": authority["artifact_sha256"],
            "executor_manifest_digest": "sha256:" + EXPECTED_EXECUTOR_MANIFEST,
        },
        "alias_registry": {
            "all_three_aliases_present_and_manifest_identical": True,
            "required_aliases": needed,
            "model_completions": 0,
        },
        "tokenizers": toks,
        "live_support": {
            "shopping_reset_complete": True,
            "shopping_health_http": reset["health_http"],
            "smoke_task_id": SMOKE_TASK,
            "smoke_task_is_in_R19_cohort": SMOKE_TASK in contract["cohort"]["downstream_task_ids"],
            "environment_reset": True,
            "native_evaluator_constructed": True,
            "native_evaluator_class": evaluator_class,
            "browser_actions": 0,
            "evaluator_calls": 0,
            "scientific_terminal_outcomes": 0,
            "endpoint_redacted": True,
        },
        "gate": {
            "zero_completion_alias_tokenizer_preflight_pass": True,
            "live_reset_zero_action_evaluator_construction_pass": True,
            "synthetic_support_completions_remaining": 2,
            "benchmark_execution_permitted_after_this_receipt_alone": False,
        },
        "scientific_verdict": "NO_VERDICT_SUPPORT_GATE_ONLY",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--authority-receipt", type=Path, required=True)
    p.add_argument("--contract", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json"))
    p.add_argument("--rb-webarena-root", type=Path, required=True)
    p.add_argument("--playwright-browsers", type=Path, required=True)
    p.add_argument("--shopping-base", required=True)
    p.add_argument("--reset-base", required=True)
    p.add_argument("--ollama-base", default="http://127.0.0.1:11444")
    p.add_argument("--smoke-root", type=Path, required=True)
    p.add_argument("--reset-poll", type=float, default=2.0)
    p.add_argument("--reset-timeout", type=int, default=300)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-prebenchmark-support-r21.json"))
    a = p.parse_args()
    out = execute(a)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "task": SMOKE_TASK, "model_completions": 0, "browser_actions": 0, "evaluator_calls": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
