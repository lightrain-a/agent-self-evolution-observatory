#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q04_plain_text_bridge_20260903 as q04
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file, sha256_text

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q05-downstream-budget-contract-20260903.json"
Q04_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q04-plain-text-bridge-20260903-v1")
Q04_PREPARE = Q04_ROOT / "prepare.json"
Q04_RESULT = Q04_ROOT / "q04-result.json"
Q04_PREPARE_SHA = "acbec282380d6e3d87708fe268bf2ea5c875bff145933ba8d14a07b28420e8d0"
Q04_RESULT_SHA = "30e898fde3e83fa1332ac153d125cd2d3618f5b7f786c4cb3e79cb4082f3bbcb"
Q04_CONTRACT_SHA = "94e7c9f8b39ca06817958432355aee038adf73f926e34ecf941e26aa9baa137a"
Q03_CLOSURE_SHA = "077383ca894abc1c3986e01ef90b16628d2580a3058d66c2838a63796208fdac"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q05-downstream-budget-20260903-v1")
WRITER_BUDGETS = (4096, 8192)
BINDER_BUDGETS = (512, 1024, 2048, 4096)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _messages_sha(fx: dict[str, Any]) -> str:
    return sha256_text(json.dumps(fx["messages"], ensure_ascii=False, sort_keys=True))


def verify_parent() -> dict[str, Any]:
    if sha256_file(Q04_PREPARE) != Q04_PREPARE_SHA:
        raise RuntimeError("STOP_Q05_Q04_PREPARE_HASH_DRIFT")
    if sha256_file(Q04_RESULT) != Q04_RESULT_SHA:
        raise RuntimeError("STOP_Q05_Q04_RESULT_HASH_DRIFT")
    if sha256_file(q04.CONTRACT) != Q04_CONTRACT_SHA:
        raise RuntimeError("STOP_Q05_Q04_CONTRACT_HASH_DRIFT")
    if sha256_file(q04.Q03_CLOSURE) != Q03_CLOSURE_SHA:
        raise RuntimeError("STOP_Q05_Q03_CLOSURE_HASH_DRIFT")
    prep = json.loads(Q04_PREPARE.read_text())
    result = json.loads(Q04_RESULT.read_text())
    if prep.get("status") != "ATOMGIT_QWEN38_Q04_PLAIN_TEXT_BRIDGE_PREPARE_PASS" or prep.get("fixture_count") != 12:
        raise RuntimeError("STOP_Q05_Q04_PREPARE_VERDICT_DRIFT")
    if result.get("status") != "HOLD_ATOMGIT_QWEN38_Q04_PLAIN_TEXT_BRIDGE_UNQUALIFIED":
        raise RuntimeError("STOP_Q05_Q04_RESULT_VERDICT_DRIFT")
    rows = result.get("rows") or []
    if len(rows) != 5:
        raise RuntimeError("STOP_Q05_Q04_FAILURE_GEOMETRY_DRIFT")
    failed = rows[-1]
    if (
        failed.get("fixture_id") != "q04-writer-05"
        or failed.get("output_truncation") is not True
        or failed.get("tool_event_count") != 0
        or int((failed.get("usage") or {}).get("completion_tokens") or 0) != 2048
    ):
        raise RuntimeError("STOP_Q05_Q04_FAILURE_LAYER_DRIFT")
    expected = {row["fixture_id"]: row for row in prep["fixtures"]}
    current = q04.fixtures()
    if len(current) != 12:
        raise RuntimeError("STOP_Q05_FIXTURE_GEOMETRY_DRIFT")
    for fx in current:
        row = expected.get(fx["fixture_id"])
        if not row or _messages_sha(fx) != row["messages_sha256"]:
            raise RuntimeError("STOP_Q05_FIXTURE_MESSAGE_DRIFT:" + fx["fixture_id"])
    return {
        "q04_prepare_sha256": Q04_PREPARE_SHA,
        "q04_result_sha256": Q04_RESULT_SHA,
        "q04_contract_sha256": Q04_CONTRACT_SHA,
        "q03_closure_sha256": Q03_CLOSURE_SHA,
        "fixture_messages_sha256": {fx["fixture_id"]: _messages_sha(fx) for fx in current},
    }


def _make_phase(root: Path, kind: str, budget: int) -> Path:
    phase = root / f"{kind}-{budget}"
    if phase.exists():
        raise RuntimeError(f"STOP_Q05_PHASE_EXISTS:{kind}:{budget}")
    phase.mkdir(parents=True)
    (phase / "empty-workdir").mkdir()
    q04.write_config(phase / "configs" / f"max-{budget}.toml", budget)
    return phase


def _run_panel(root: Path, kind: str, budget: int, fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    phase = _make_phase(root, kind, budget)
    rows: list[dict[str, Any]] = []
    for index, original in enumerate(fixtures, 1):
        fx = copy.deepcopy(original)
        fx["max_tokens"] = budget
        row = q04.call(phase, index, fx)
        row["q05_budget"] = budget
        row["q05_panel_kind"] = kind
        rows.append(row)
        print(json.dumps({"kind": kind, "budget": budget, "fixture": fx["fixture_id"], "pass": row.get("pass"), "returncode": row.get("returncode"), "truncation": row.get("output_truncation")}, sort_keys=True), flush=True)
        if not row.get("pass"):
            break
    passed = len(rows) == len(fixtures) and all(bool(row.get("pass")) for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "kind": kind,
        "budget": budget,
        "pass": passed,
        "attempted": len(rows),
        "qualified": sum(bool(row.get("pass")) for row in rows),
        "required": len(fixtures),
        "native_tool_runtime_events": sum(int(row.get("tool_event_count") or 0) for row in rows),
        "codingplan_requests": sum(int(row.get("codingplan_requests") or 0) for row in rows),
        "input_tokens": sum(int((row.get("usage") or {}).get("prompt_tokens") or 0) for row in rows),
        "output_tokens": sum(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in rows),
        "rows": rows,
        "scientific_source_tasks_used_as_fixtures": 0,
    }
    atomic_json(phase / "result.json", result)
    return result


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q0.5 root exists; no overwrite")
    parent = verify_parent()
    root.mkdir(parents=True)
    writer = q04.writer_fixtures()
    binder = q04.binder_fixtures()
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q05_DOWNSTREAM_BUDGET_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "parent": parent,
        "writer_budgets": list(WRITER_BUDGETS),
        "binder_budgets": list(BINDER_BUDGETS),
        "writer_fixture_ids": [fx["fixture_id"] for fx in writer],
        "binder_fixture_ids": [fx["fixture_id"] for fx in binder],
        "fresh3_source_outcomes_used_for_design": False,
        "scientific_source_tasks_used_as_fixtures": 0,
        "writer_scientific_calls": 0,
        "binder_scientific_calls": 0,
    }
    atomic_json(root / "prepare.json", result)
    return result


def run(root: Path) -> dict[str, Any]:
    if not (root / "prepare.json").is_file():
        raise RuntimeError("prepare first")
    if (root / "q05-result.json").exists():
        raise RuntimeError("Q0.5 result exists; no overwrite")
    verify_parent()
    writer_selected = None
    binder_selected = None
    writer_results: list[dict[str, Any]] = []
    binder_results: list[dict[str, Any]] = []
    writer_fixtures = q04.writer_fixtures()
    binder_fixtures = q04.binder_fixtures()
    for budget in WRITER_BUDGETS:
        res = _run_panel(root, "writer", budget, writer_fixtures)
        writer_results.append({k: res[k] for k in ["budget", "pass", "attempted", "qualified", "required", "native_tool_runtime_events", "codingplan_requests", "input_tokens", "output_tokens"]})
        if res["pass"]:
            writer_selected = budget
            break
    if writer_selected is not None:
        for budget in BINDER_BUDGETS:
            res = _run_panel(root, "binder", budget, binder_fixtures)
            binder_results.append({k: res[k] for k in ["budget", "pass", "attempted", "qualified", "required", "native_tool_runtime_events", "codingplan_requests", "input_tokens", "output_tokens"]})
            if res["pass"]:
                binder_selected = budget
                break
    passed = writer_selected is not None and binder_selected is not None
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q05_DOWNSTREAM_BUDGET_PASS" if passed else "HOLD_ATOMGIT_QWEN38_Q05_DOWNSTREAM_BUDGET_UNQUALIFIED",
        "pass": passed,
        "writer_selected_max_tokens": writer_selected,
        "binder_selected_max_tokens": binder_selected,
        "writer_results": writer_results,
        "binder_results": binder_results,
        "fresh3_source_outcomes_used_for_design": False,
        "scientific_source_tasks_used_as_fixtures": 0,
        "writer_scientific_calls": 0,
        "binder_scientific_calls": 0,
        "claim_authority": "NO_MSR_METHOD_EFFECT_EVIDENCE",
    }
    atomic_json(root / "q05-result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("prepare", "run"), required=True)
    args = parser.parse_args()
    result = {"prepare": prepare, "run": run}[args.phase](args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
