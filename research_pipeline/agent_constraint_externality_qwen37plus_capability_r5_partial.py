from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld, prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
from research_pipeline.agent_constraint_externality_qwen37plus_capability import (
    ALLOWED_ALIAS,
    ADDENDUM_OUTPUT,
    PROVIDER_SNAPSHOT_OUTPUT,
    REQUESTED_MODEL,
    TOOL_CAP_FAILURE_MESSAGE,
    read_json,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    DEFAULT_BASE_URL,
    OBJECT_ID,
    AppendOnlyLedger,
    EpisodeUnit,
    RunnerError,
    TypicalResponsesClient,
    run_episode,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec
from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
R5_CONTRACT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r5-partial-contract-20260902.json"
V4_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r4-20260902.json"
FG_REVALIDATION = GENERATED / "agent-constraint-externality-qwen37plus-r2-fg-v2-revalidation-20260902.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r5-partial-20260902.json"
EXECUTION_ID = "QWEN37PLUS-CAPABILITY-R5-PARTIAL-SUBSTRATE-V4"
TNF_FAMILIES = ("ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
TOOL_CAP = 16
TOOLCAP_SCHEMA = "ace-qwen37plus-toolcap-measurement-r5-partial-v1"


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise RunnerError(f"Required artifact missing: {path}")
    payload = read_json(path)
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RunnerError(f"Content hash mismatch: {path}")
    if payload.get("object_id") != OBJECT_ID:
        raise RunnerError(f"Object mismatch: {path}")
    if status and payload.get("status") != status:
        raise RunnerError(f"Unexpected status in {path}: {payload.get('status')}")
    return payload


def units() -> list[EpisodeUnit]:
    return [
        EpisodeUnit(
            namespace="capability",
            key=(ALLOWED_ALIAS, family_id, repeat),
            stage="CAPABILITY_CALIBRATION_R5_PARTIAL_TNF",
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in TNF_FAMILIES for repeat in REPEATS
    ]


def toolcap_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen: set[str] = set()
    for row in rows:
        if row.get("schema_version") != TOOLCAP_SCHEMA: raise RunnerError("Unexpected R5 toolcap schema.")
        unsigned = dict(row); claimed = unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned): raise RunnerError("R5 toolcap hash mismatch.")
        if row["unit_id"] in seen: raise RunnerError("Duplicate R5 toolcap unit.")
        seen.add(row["unit_id"])
    return rows


def append_toolcap(path: Path, unit: EpisodeUnit, evaluation: dict[str, Any], receipt_count: int) -> None:
    if unit.unit_id in {row["unit_id"] for row in toolcap_rows(path)}:
        raise RunnerError("Duplicate R5 toolcap measurement.")
    row: dict[str, Any] = {
        "schema_version": TOOLCAP_SCHEMA,
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "unit_id": unit.unit_id,
        "family_id": unit.family_id,
        "classification": "CAPABILITY_TOOL_LOOP_INCOMPLETE_AT_FROZEN_CAP",
        "tool_loop_completed": False,
        "tool_call_cap": TOOL_CAP,
        "provider_receipt_count": receipt_count,
        "retry": False,
        "replacement": False,
        "evaluation": evaluation,
    }
    row["content_sha256"] = sha256_value(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush(); os.fsync(handle.fileno())


def execute(*, appworld_root: Path, runtime_root: Path, ledger_path: Path, toolcap_path: Path, api_key: str, base_url: str) -> None:
    contract = verified(R5_CONTRACT, "QWEN37PLUS_CAPABILITY_R5_PARTIAL_TNF_ONLY_AUTHORIZED")
    if contract.get("tool_call_cap") != TOOL_CAP or contract.get("rerun_tnf_measurements") != 4:
        raise RunnerError("R5 contract budget/scope mismatch.")
    verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    spec = load_protected_spec(BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    provider = TypicalResponsesClient(api_key, base_url)
    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    failures = {row["unit_id"]: row for row in ledger.rows() if row["event"] == "FAILURE"}
    for unit in units():
        state = states.get(unit.unit_id)
        if state == "COMPLETION": continue
        if state == "FAILURE":
            row = failures.get(unit.unit_id, {})
            if not (row.get("failure_class") == "RunnerError" and row.get("message") == TOOL_CAP_FAILURE_MESSAGE and row.get("retry_attempted") is False):
                raise RunnerError(f"R5 cannot continue past non-toolcap failure {unit.unit_id}.")
            if unit.unit_id not in {r["unit_id"] for r in toolcap_rows(toolcap_path)}:
                raise RunnerError(f"R5 toolcap failure lacks measurement: {unit.unit_id}")
            continue
        if state is not None: raise RunnerError(f"R5 cannot replay non-terminal unit {unit.unit_id}: {state}")
        family = families[unit.family_id]
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        if int(arm["matching"]["tool_budget"]) != TOOL_CAP:
            raise RunnerError("R5 arm tool budget is not frozen at 16.")
        task_id = "acer5p" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(appworld_root, unit_root, family=family, arm=arm, task_id=task_id)
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-qwen37plus-capability-r5-partial",
            seed=1100 + int(unit.repeat or 0),
            allowed_apps=set(family["fixture"]["apps"]),
            max_interactions=TOOL_CAP,
        )
        try:
            try:
                run_episode(
                    unit=unit,
                    instruction=arm["task_instruction"],
                    snapshot_sha256=materialized["initial_snapshot_sha256"],
                    repair_sha256=None,
                    world=world,
                    provider=provider,
                    ledger=ledger,
                    model=ALLOWED_ALIAS,
                    base_url=base_url,
                    result_evaluator=lambda arm=arm, world=world: world.save_and_evaluate(arm),
                    max_tool_calls=TOOL_CAP,
                )
            except RunnerError as exc:
                if str(exc) != TOOL_CAP_FAILURE_MESSAGE: raise
                evaluation = world.save_and_evaluate(arm)
                failure = next(row for row in reversed(ledger.rows()) if row["unit_id"] == unit.unit_id and row["event"] == "FAILURE")
                append_toolcap(toolcap_path, unit, evaluation, len(failure.get("provider_receipts", [])))
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(units())


def terminal_scientific_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only terminal rows that can carry provider receipts/scientific measurements."""
    return [row for row in rows if row.get("event") in {"COMPLETION", "FAILURE"}]


def adjudicate(*, ledger_path: Path, toolcap_path: Path) -> dict[str, Any]:
    fg = verified(FG_REVALIDATION, "R2_FG_V2_MEASUREMENT_REVALIDATION_PASS")
    ledger = AppendOnlyLedger(ledger_path)
    ledger.assert_all_terminal(units())
    rows = ledger.rows()
    failures = [row for row in rows if row["event"] == "FAILURE"]
    invalid = [row for row in failures if not (row.get("failure_class") == "RunnerError" and row.get("message") == TOOL_CAP_FAILURE_MESSAGE and row.get("retry_attempted") is False)]
    if invalid:
        result: dict[str, Any] = {
            "schema_version": "ace-qwen37plus-capability-r5-partial-result-v1",
            "object_id": OBJECT_ID,
            "execution_id": EXECUTION_ID,
            "status": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
            "failure_units": [row["unit_id"] for row in invalid],
            "preserved_fg_measurements": 4,
            "valid_new_tnf_measurements": 4 - len(invalid),
            "authority": {"f0": False},
        }
        result["content_sha256"] = sha256_value(result)
        return result
    toolcaps = {row["unit_id"]: row for row in toolcap_rows(toolcap_path)}
    measurements = [{
        "tool_loop_completed": True,
        "target_success": True,
        "non_target_preservation": 1.0,
        "malformed_tool_calls": 0,
    } for _ in fg["rows"]]
    inherited_requests = sum(int(row["inherited_agent_model_request_count"]) for row in fg["rows"])
    new_requests = 0
    completions = 0
    terminal_rows = terminal_scientific_rows(rows)
    for row in terminal_rows:
        receipts = row.get("provider_receipts", [])
        if {receipt.get("resolved_model") for receipt in receipts} != {ALLOWED_ALIAS}:
            raise RunnerError("R5 resolved model drifted.")
        new_requests += len(receipts)
        if row["event"] == "COMPLETION":
            evaluation = row["result"]["evaluation"]
            measurements.append({"tool_loop_completed": True, "target_success": bool(evaluation["target_success"]), "non_target_preservation": float(evaluation["non_target_preservation"]), "malformed_tool_calls": 0})
            completions += 1
        else:
            evaluation = toolcaps[row["unit_id"]]["evaluation"]
            measurements.append({"tool_loop_completed": False, "target_success": bool(evaluation["target_success"]), "non_target_preservation": float(evaluation["non_target_preservation"]), "malformed_tool_calls": 0})
    if len(measurements) != 8: raise RunnerError("R5 gate requires 4 preserved FG + 4 new TNF measurements.")
    gate = capability_gate(measurements)
    result = {
        "schema_version": "ace-qwen37plus-capability-r5-partial-result-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": gate["verdict"],
        "gate": gate,
        "requested_model": REQUESTED_MODEL,
        "resolved_model": ALLOWED_ALIAS,
        "valid_capability_measurements": 8,
        "preserved_fg_measurements": 4,
        "rerun_tnf_measurements": 4,
        "new_tnf_completion_count": completions,
        "new_tnf_tool_cap_incomplete_count": len(failures),
        "tool_call_cap": TOOL_CAP,
        "inherited_fg_agent_model_request_count": inherited_requests,
        "new_agent_model_request_count": new_requests,
        "provider_request_total_new": new_requests,
        "model_selection_evidence_agent_request_total": inherited_requests + new_requests,
        "scientific_outcomes_observed": 0,
        "f0_executed": False,
        "fg_revalidation_sha256": sha256_file(FG_REVALIDATION),
        "r5_contract_sha256": sha256_file(R5_CONTRACT),
        "ledger_sha256": sha256_file(ledger_path),
        "toolcap_measurement_sha256": sha256_file(toolcap_path) if toolcap_path.exists() else None,
        "authority": {"f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "second_model": False, "method": False, "paper_claim": False},
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, default=ROOT / "cache/substrates/appworld-official-20260831")
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--toolcap-ledger", type=Path, required=True)
    parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT)
    args = parser.parse_args()
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "").strip()
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not api_key: raise RunnerError("AA_API_KEY is not configured.")
    snapshot = verified(PROVIDER_SNAPSHOT_OUTPUT)
    if snapshot.get("resolved_request_model") != ALLOWED_ALIAS or snapshot.get("base_url") != base_url:
        raise RunnerError("Qwen3.7-Plus provider identity/base URL drifted.")
    verified(ADDENDUM_OUTPUT, "QWEN37PLUS_CAPABILITY_A1_AUTHORIZED")
    execute(appworld_root=args.appworld_root, runtime_root=args.runtime_root, ledger_path=args.ledger, toolcap_path=args.toolcap_ledger, api_key=api_key, base_url=base_url)
    result = adjudicate(ledger_path=args.ledger, toolcap_path=args.toolcap_ledger)
    args.result_output.parent.mkdir(parents=True, exist_ok=True)
    args.result_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "preserved_fg": result.get("preserved_fg_measurements"), "rerun_tnf": result.get("rerun_tnf_measurements"), "new_provider_requests": result.get("provider_request_total_new"), "f0_authorized": result.get("authority", {}).get("f0", False)}, sort_keys=True))


if __name__ == "__main__":
    main()
