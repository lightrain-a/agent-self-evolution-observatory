#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_text_bridge_20260903 as q03
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file, sha256_text

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q06-downstream-estimand-contract-20260903.json"
Q03_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q03-text-bridge-20260903-v1")
Q03_PREPARE = Q03_ROOT / "prepare.json"
Q03_RESULT = Q03_ROOT / "q03-result.json"
Q03_PREPARE_SHA = "79793f7c1b5f72be7981f2bc7f131870eeef6853dc4f394f69be95df883e93e9"
Q03_RESULT_SHA = "14860b1a6494dd2d3e39557e57ad5d6605946917071c4f2811e67ca3260b63b4"
Q03_CLOSURE_SHA = "077383ca894abc1c3986e01ef90b16628d2580a3058d66c2838a63796208fdac"
Q05_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q05-downstream-budget-closure-20260903.json"
Q05_CLOSURE_SHA = "5ed5205f5b68aa2f5ab6f7a254509335e13b46378204bef8ba97568be4b67b51"
ORIGINAL_P0 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-p0-execution-contract-20260902.json"
ORIGINAL_P0_SHA = "5bc3daf779dd7facd45881080d846ccdf847814fecc6150e8b0d4fcc0db46f32"
FRESH3_SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-split-20260903.json"
FRESH3_SPLIT_SHA = "d71f48910e531e62de2d056342c0c17ce17872503f089a29b16182fca3c1b2d9"
FRESH3_PROBES = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-probe-specs-20260903.json"
FRESH3_PROBES_SHA = "19f119fdb80e58427809a565d515900a14455394e79c31126645521702940c97"
FRESH3_SCHEDULE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-source-schedule-20260903.json"
FRESH3_SCHEDULE_SHA = "2e78838a46b3a37c09e07e2f0abdf0d9eb82d271e53d91245a41306d0e5b273f"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q06-downstream-estimand-20260903-v1")
ACTION_BUDGETS = (2048, 4096, 8192, 16384, 32768)
SAMPLING_FIXTURE_IDS = ("q03-first-01", "q03-first-02")
SAMPLING_REPS = 6


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _messages_sha(fx: dict[str, Any]) -> str:
    return sha256_text(json.dumps(fx["messages"], ensure_ascii=False, sort_keys=True))


def verify_parent() -> dict[str, Any]:
    for path, expected, label in (
        (Q03_PREPARE, Q03_PREPARE_SHA, "q03 prepare"),
        (Q03_RESULT, Q03_RESULT_SHA, "q03 result"),
        (q03.ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-text-bridge-closure-20260903.json", Q03_CLOSURE_SHA, "q03 closure"),
        (Q05_CLOSURE, Q05_CLOSURE_SHA, "q05 closure"),
        (ORIGINAL_P0, ORIGINAL_P0_SHA, "original p0"),
        (FRESH3_SPLIT, FRESH3_SPLIT_SHA, "fresh3 split"),
        (FRESH3_PROBES, FRESH3_PROBES_SHA, "fresh3 probes"),
        (FRESH3_SCHEDULE, FRESH3_SCHEDULE_SHA, "fresh3 source schedule"),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError("STOP_Q06_PARENT_HASH_DRIFT:" + label)
    prep = json.loads(Q03_PREPARE.read_text())
    result = json.loads(Q03_RESULT.read_text())
    q05 = json.loads(Q05_CLOSURE.read_text())
    p0 = json.loads(ORIGINAL_P0.read_text())
    if prep.get("status") != "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PREPARE_PASS" or prep.get("fixture_count") != 12:
        raise RuntimeError("STOP_Q06_Q03_PREPARE_DRIFT")
    if result.get("status") != "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS" or result.get("qualified") != 12:
        raise RuntimeError("STOP_Q06_Q03_RESULT_DRIFT")
    if q05.get("status") != "ATOMGIT_QWEN38_Q05_DOWNSTREAM_BUDGET_PASS" or q05.get("writer_selected_max_tokens") != 4096 or q05.get("binder_selected_max_tokens") != 2048:
        raise RuntimeError("STOP_Q06_Q05_DRIFT")
    if p0.get("pilot_count") != 8 or p0.get("shadow", {}).get("blocks_per_branch") != 2 or p0.get("shadow", {}).get("samples_per_block") != 6:
        raise RuntimeError("STOP_Q06_ORIGINAL_P0_GEOMETRY_DRIFT")
    expected_messages = {row["fixture_id"]: row["messages_sha256"] for row in prep["fixtures"]}
    fixtures = q03.fixtures()
    if len(fixtures) != 12:
        raise RuntimeError("STOP_Q06_FIXTURE_GEOMETRY_DRIFT")
    for fx in fixtures:
        if _messages_sha(fx) != expected_messages.get(fx["fixture_id"]):
            raise RuntimeError("STOP_Q06_Q03_FIXTURE_MESSAGE_DRIFT:" + fx["fixture_id"])
    return {
        "q03_prepare_sha256": Q03_PREPARE_SHA,
        "q03_result_sha256": Q03_RESULT_SHA,
        "q03_closure_sha256": Q03_CLOSURE_SHA,
        "q05_closure_sha256": Q05_CLOSURE_SHA,
        "original_p0_sha256": ORIGINAL_P0_SHA,
        "fresh3_split_sha256": FRESH3_SPLIT_SHA,
        "fresh3_probe_specs_sha256": FRESH3_PROBES_SHA,
        "fresh3_source_schedule_sha256": FRESH3_SCHEDULE_SHA,
        "fixture_messages_sha256": expected_messages,
    }


def _bind_budget(root: Path, budget: int) -> None:
    q03.MAX_TOKENS = budget
    root.mkdir(parents=True, exist_ok=False)
    q03.write_config(root / "config.toml")


def _run_budget(root: Path, budget: int) -> dict[str, Any]:
    phase = root / f"action-{budget}"
    _bind_budget(phase, budget)
    rows: list[dict[str, Any]] = []
    for index, fx in enumerate(q03.fixtures(), 1):
        row = q03.call_fixture(phase, index, copy.deepcopy(fx))
        rows.append(row)
        print(json.dumps({"budget": budget, "fixture": fx["fixture_id"], "pass": row.get("pass"), "returncode": row.get("returncode"), "truncation": row.get("output_truncation"), "tool_events": row.get("tool_event_count")}, sort_keys=True), flush=True)
        if not row.get("pass"):
            break
    passed = len(rows) == 12 and all(bool(row.get("pass")) for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "budget": budget,
        "pass": passed,
        "attempted": len(rows),
        "qualified": sum(bool(row.get("pass")) for row in rows),
        "required": 12,
        "native_tool_runtime_events": sum(int(row.get("tool_event_count") or 0) for row in rows),
        "codingplan_requests": sum(int(row.get("codingplan_requests") or 0) for row in rows),
        "input_tokens": sum(int((row.get("usage") or {}).get("prompt_tokens") or 0) for row in rows),
        "output_tokens": sum(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in rows),
    }
    atomic_json(phase / "result.json", result)
    return result


def _run_sampling(root: Path, budget: int) -> dict[str, Any]:
    phase = root / "sampling"
    _bind_budget(phase, budget)
    by_id = {fx["fixture_id"]: fx for fx in q03.fixtures()}
    rows: list[dict[str, Any]] = []
    index = 0
    for fixture_id in SAMPLING_FIXTURE_IDS:
        for rep in range(1, SAMPLING_REPS + 1):
            index += 1
            row = q03.call_fixture(phase, index, copy.deepcopy(by_id[fixture_id]))
            rows.append({
                "fixture_id": fixture_id,
                "replicate": rep,
                "pass": bool(row.get("pass")),
                "action_sha256": row.get("action_sha256") or "",
                "assistant_message_sha256": row.get("assistant_message_sha256") or "",
                "tool_event_count": int(row.get("tool_event_count") or 0),
                "codingplan_requests": int(row.get("codingplan_requests") or 0),
                "usage": row.get("usage") or {},
            })
    all_valid = len(rows) == 12 and all(row["pass"] for row in rows)
    per = []
    for fixture_id in SAMPLING_FIXTURE_IDS:
        actions = [row["action_sha256"] for row in rows if row["fixture_id"] == fixture_id]
        per.append({"fixture_id": fixture_id, "replicates": len(actions), "unique_action_count": len(set(actions)), "action_sha256": actions})
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "Q06_SAMPLING_DIAGNOSTIC_VALID" if all_valid else "STOP_Q06_SAMPLING_TRANSPORT_INVALID",
        "pass": all_valid,
        "selected_action_budget": budget,
        "per_fixture": per,
        "rows": rows,
        "diversity_is_descriptive_not_gate": True,
        "native_tool_runtime_events": sum(row["tool_event_count"] for row in rows),
        "codingplan_requests": sum(row["codingplan_requests"] for row in rows),
    }
    atomic_json(phase / "result.json", result)
    return result


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q0.6 root exists; no overwrite")
    parent = verify_parent()
    root.mkdir(parents=True)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q06_DOWNSTREAM_ESTIMAND_PREPARE_PASS",
        "contract_sha256": sha256_file(CONTRACT),
        "parent": parent,
        "action_budget_candidates": list(ACTION_BUDGETS),
        "sampling_fixture_ids": list(SAMPLING_FIXTURE_IDS),
        "sampling_replicates_per_fixture": SAMPLING_REPS,
        "fresh3_source_terminal_outcomes_used_to_choose_parameters": False,
        "fresh3_source_artifacts_used_as_fixtures": False,
        "scientific_writer_calls": 0,
        "scientific_binder_calls": 0,
        "scientific_shadow_calls": 0,
        "scientific_final_calls": 0,
    }
    atomic_json(root / "prepare.json", result)
    return result


def run(root: Path) -> dict[str, Any]:
    if not (root / "prepare.json").is_file():
        raise RuntimeError("prepare first")
    if (root / "q06-result.json").exists():
        raise RuntimeError("Q0.6 result exists; no overwrite")
    verify_parent()
    selected = None
    budget_results = []
    for budget in ACTION_BUDGETS:
        res = _run_budget(root, budget)
        budget_results.append(res)
        if res["pass"]:
            selected = budget
            break
    sampling = None
    if selected is not None:
        sampling = _run_sampling(root, selected)
    passed = selected is not None and sampling is not None and sampling.get("pass") is True
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q06_DOWNSTREAM_ESTIMAND_PASS" if passed else "HOLD_ATOMGIT_QWEN38_Q06_DOWNSTREAM_ESTIMAND_UNQUALIFIED",
        "pass": passed,
        "selected_action_max_tokens": selected,
        "writer_max_tokens": 4096,
        "binder_max_tokens": 2048,
        "provider_sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9",
        "budget_results": [{k: r[k] for k in ["budget", "pass", "attempted", "qualified", "required", "native_tool_runtime_events", "codingplan_requests", "input_tokens", "output_tokens"]} for r in budget_results],
        "sampling_diagnostic": None if sampling is None else {"status": sampling["status"], "per_fixture": sampling["per_fixture"], "native_tool_runtime_events": sampling["native_tool_runtime_events"], "codingplan_requests": sampling["codingplan_requests"]},
        "estimand": "empirical provider-managed first-action distributions conditional on one content-addressed realized writer draw per branch and one content-addressed realized binder draw per branch/context; no temperature-equivalence claim",
        "fresh3_source_terminal_outcomes_used_to_choose_parameters": False,
        "fresh3_source_artifacts_used_as_fixtures": False,
        "scientific_writer_calls": 0,
        "scientific_binder_calls": 0,
        "scientific_shadow_calls": 0,
        "scientific_final_calls": 0,
        "claim_authority": "NO_MSR_METHOD_EFFECT_EVIDENCE",
    }
    atomic_json(root / "q06-result.json", result)
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
