from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    evaluate_arm_from_materialized_state,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
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
from research_pipeline.agent_constraint_externality_qwen37plus_capability import (
    ALLOWED_ALIAS,
    ADDENDUM_OUTPUT,
    PROVIDER_SNAPSHOT_OUTPUT,
    REQUESTED_MODEL,
    TOOL_CAP,
    TOOL_CAP_FAILURE_MESSAGE,
    read_json,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec
from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
R2_LEDGER = ROOT / "runtimes/agent-constraint-externality-qwen37plus-capability-r2-20260901/ledger.jsonl"
R2_WORLD_ROOT = ROOT / "runtimes/agent-constraint-externality-qwen37plus-capability-r2-20260901/worlds"
V2_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v2-20260902.bundle"
V2_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r2-20260902.json"
R2_ROOT_CAUSE = GENERATED / "agent-constraint-externality-capability-r2-root-cause-audit-20260902.json"
R2_VOID = GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r2-20260902.json"
OLD_R3_CONTRACT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r3-contract-20260902.json"
FG_REVALIDATION = GENERATED / "agent-constraint-externality-qwen37plus-r2-fg-v2-revalidation-20260902.json"
PARTIAL_CONTRACT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r3-partial-contract-20260902.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r3-partial-20260902.json"
EXECUTION_ID = "QWEN37PLUS-CAPABILITY-R3-PARTIAL-SUBSTRATE-V2"
FG_FAMILIES = ("ACE-FG-05", "ACE-FG-06")
TNF_FAMILIES = ("ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
TOOLCAP_SCHEMA = "ace-qwen37plus-toolcap-measurement-r3-partial-v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _verified_json(path: Path, status: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise RunnerError(f"Required artifact missing: {path}")
    payload = read_json(path)
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RunnerError(f"Content hash mismatch: {path}")
    if payload.get("object_id") != OBJECT_ID:
        raise RunnerError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RunnerError(f"Unexpected status in {path}: {payload.get('status')}")
    return payload


def _r2_completion_rows() -> dict[str, dict[str, Any]]:
    ledger = AppendOnlyLedger(R2_LEDGER)
    rows = {}
    for row in ledger.rows():
        if row.get("event") == "COMPLETION" and any(fid in row.get("unit_id", "") for fid in FG_FAMILIES):
            rows[row["unit_id"]] = row
    expected = {
        f"capability:{ALLOWED_ALIAS}|{fid}|{repeat}"
        for fid in FG_FAMILIES for repeat in REPEATS
    }
    if set(rows) != expected:
        raise RunnerError("R2 does not contain exactly four terminal FG completions.")
    return rows


def build_fg_revalidation() -> dict[str, Any]:
    spec = load_protected_spec(V2_BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    completions = _r2_completion_rows()
    rows: list[dict[str, Any]] = []
    for family_id in FG_FAMILIES:
        family = families[family_id]
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        for repeat in REPEATS:
            unit_id = f"capability:{ALLOWED_ALIAS}|{family_id}|{repeat}"
            unit_root = R2_WORLD_ROOT / unit_id.replace(":", "_").replace("|", "_")
            task_id = "acer2" + family_id.lower().replace("-", "") + f"r{repeat}_1"
            source = unit_root / "data/tasks" / task_id / "dbs"
            changes = unit_root / "experiments/outputs/ace-qwen37plus-capability-r2/tasks" / task_id / "dbs"
            with tempfile.TemporaryDirectory(prefix="ace-r3-fg-revalidation-") as directory:
                evaluation = evaluate_arm_from_materialized_state(
                    arm=arm,
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=Path(directory),
                )
            if not evaluation["target_success"] or evaluation["non_target_preservation"] != 1.0:
                raise RunnerError(f"FG V2 semantic revalidation failed for {unit_id}.")
            completion = completions[unit_id]
            receipts = completion.get("provider_receipts", [])
            if not receipts or {r.get("resolved_model") for r in receipts} != {ALLOWED_ALIAS}:
                raise RunnerError(f"FG R2 model lineage invalid for {unit_id}.")
            rows.append({
                "unit_id": unit_id,
                "family_id": family_id,
                "repeat": repeat,
                "source_execution": "QWEN37PLUS-CAPABILITY-R2-AUTH-SUBSTRATE-RECOVERY",
                "provider_reexecution": False,
                "v2_measurement_only_revalidation": True,
                "tool_loop_completed": True,
                "target_success": True,
                "non_target_preservation": 1.0,
                "malformed_tool_calls": 0,
                "inherited_agent_model_request_count": len(receipts),
                "r2_ledger_sha256": sha256_file(R2_LEDGER),
            })
    payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-r2-fg-v2-revalidation-v1",
        "object_id": OBJECT_ID,
        "status": "R2_FG_V2_MEASUREMENT_REVALIDATION_PASS",
        "model": ALLOWED_ALIAS,
        "preserved_unit_count": 4,
        "provider_requests_added": 0,
        "reason_preservable": (
            "V2 discoverability/task-locator repair changes only TNF. FG task text and execution substrate are unchanged, "
            "and all four R2 FG final states pass the stricter V2 recipient-plus-two-attachment semantic evaluator."
        ),
        "rows": rows,
        "v2_bundle_sha256": sha256_file(V2_BUNDLE),
        "r2_root_cause_audit_sha256": sha256_file(R2_ROOT_CAUSE),
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_partial_contract(revalidation: dict[str, Any]) -> dict[str, Any]:
    _verified_json(V2_QUAL, "CAPABILITY_SUBSTRATE_V2_PUBLIC_REACHABILITY_PASS")
    _verified_json(R2_VOID, "QWEN37PLUS_R2_VOID_SUBSTRATE_DISCOVERABILITY_INVALID")
    old = _verified_json(OLD_R3_CONTRACT, "QWEN37PLUS_CAPABILITY_R3_AUTHORIZED_AFTER_SUBSTRATE_V2")
    rerun_units = [f"capability:{ALLOWED_ALIAS}|{fid}|{repeat}" for fid in TNF_FAMILIES for repeat in REPEATS]
    preserved_units = [row["unit_id"] for row in revalidation["rows"]]
    payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-r3-partial-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": "QWEN37PLUS_CAPABILITY_R3_PARTIAL_AUTHORIZED",
        "supersedes_full_r3_execution_contract_sha256": sha256_file(OLD_R3_CONTRACT),
        "supersession_reason": "USER_AUTHORIZED_ONLY_CORRECTION_AFFECTED_UNITS_TO_RERUN",
        "model": ALLOWED_ALIAS,
        "preserved_units": preserved_units,
        "rerun_units": rerun_units,
        "preserved_unit_count": 4,
        "rerun_unit_count": 4,
        "final_gate_measurement_count": 8,
        "fg_revalidation_artifact_sha256": sha256_file(FG_REVALIDATION),
        "active_protected_bundle_sha256": sha256_file(V2_BUNDLE),
        "tool_call_cap": TOOL_CAP,
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "model_switch": False,
        "threshold_change": False,
        "f0_authorized": False,
        "invariants": {
            "fg_provider_reexecution": False,
            "tnf_only_scientific_rerun": True,
            "same_four_capability_families": True,
            "same_repeats": True,
            "same_model": True,
            "same_gate": True,
            "same_tool_call_cap": True,
        },
        "old_r3_same_eight_unit_panel": bool(old.get("same_eight_unit_panel")),
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def _toolcap_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen: set[str] = set()
    for row in rows:
        if row.get("schema_version") != TOOLCAP_SCHEMA:
            raise RunnerError("Unexpected R3-partial tool-cap schema.")
        claimed = row.get("content_sha256")
        unsigned = dict(row); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RunnerError("R3-partial tool-cap hash mismatch.")
        if row["unit_id"] in seen:
            raise RunnerError("Duplicate R3-partial tool-cap measurement.")
        seen.add(row["unit_id"])
    return rows


def _append_toolcap(path: Path, unit: EpisodeUnit, evaluation: dict[str, Any], receipt_count: int) -> None:
    if unit.unit_id in {row["unit_id"] for row in _toolcap_rows(path)}:
        raise RunnerError("Duplicate R3-partial tool-cap measurement.")
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


def tnf_units() -> list[EpisodeUnit]:
    return [
        EpisodeUnit(
            namespace="capability",
            key=(ALLOWED_ALIAS, family_id, repeat),
            stage="CAPABILITY_CALIBRATION_R3_PARTIAL_TNF",
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in TNF_FAMILIES for repeat in REPEATS
    ]


def execute_tnf(*, appworld_root: Path, runtime_root: Path, ledger_path: Path, toolcap_path: Path, api_key: str, base_url: str) -> None:
    contract = _verified_json(PARTIAL_CONTRACT, "QWEN37PLUS_CAPABILITY_R3_PARTIAL_AUTHORIZED")
    if contract.get("rerun_units") != [unit.unit_id for unit in tnf_units()]:
        raise RunnerError("R3-partial rerun set drifted from frozen contract.")
    spec = load_protected_spec(V2_BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    provider = TypicalResponsesClient(api_key, base_url)
    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    failures = {row["unit_id"]: row for row in ledger.rows() if row["event"] == "FAILURE"}
    for unit in tnf_units():
        state = states.get(unit.unit_id)
        if state == "COMPLETION":
            continue
        if state == "FAILURE":
            row = failures.get(unit.unit_id, {})
            if not (row.get("failure_class") == "RunnerError" and row.get("message") == TOOL_CAP_FAILURE_MESSAGE and row.get("retry_attempted") is False):
                raise RunnerError(f"R3-partial cannot continue past non-toolcap failure {unit.unit_id}.")
            if unit.unit_id not in {r["unit_id"] for r in _toolcap_rows(toolcap_path)}:
                raise RunnerError(f"R3-partial tool-cap failure lacks measurement: {unit.unit_id}")
            continue
        if state is not None:
            raise RunnerError(f"R3-partial cannot replay non-terminal unit {unit.unit_id}: {state}")
        family = families[unit.family_id]
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        task_id = "acer3p" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(appworld_root, unit_root, family=family, arm=arm, task_id=task_id)
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-qwen37plus-capability-r3-partial",
            seed=1100 + int(unit.repeat or 0),
            allowed_apps=set(family["fixture"]["apps"]),
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
                )
            except RunnerError as exc:
                if str(exc) != TOOL_CAP_FAILURE_MESSAGE:
                    raise
                evaluation = world.save_and_evaluate(arm)
                failure = next(row for row in reversed(ledger.rows()) if row["unit_id"] == unit.unit_id and row["event"] == "FAILURE")
                _append_toolcap(toolcap_path, unit, evaluation, len(failure.get("provider_receipts", [])))
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(tnf_units())


def adjudicate(*, ledger_path: Path, toolcap_path: Path) -> dict[str, Any]:
    revalidation = _verified_json(FG_REVALIDATION, "R2_FG_V2_MEASUREMENT_REVALIDATION_PASS")
    ledger = AppendOnlyLedger(ledger_path)
    ledger.assert_all_terminal(tnf_units())
    rows = ledger.rows()
    failures = [row for row in rows if row["event"] == "FAILURE"]
    invalid = [row for row in failures if not (row.get("failure_class") == "RunnerError" and row.get("message") == TOOL_CAP_FAILURE_MESSAGE and row.get("retry_attempted") is False)]
    if invalid:
        result = {
            "schema_version": "ace-qwen37plus-capability-r3-partial-result-v1",
            "object_id": OBJECT_ID,
            "execution_id": EXECUTION_ID,
            "status": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
            "failure_units": [row["unit_id"] for row in invalid],
            "authority": {"f0": False},
        }
        result["content_sha256"] = sha256_value(result)
        return result
    toolcap = {row["unit_id"]: row for row in _toolcap_rows(toolcap_path)}
    measurements = [
        {
            "tool_loop_completed": bool(row["tool_loop_completed"]),
            "target_success": bool(row["target_success"]),
            "non_target_preservation": float(row["non_target_preservation"]),
            "malformed_tool_calls": int(row["malformed_tool_calls"]),
        }
        for row in revalidation["rows"]
    ]
    inherited_requests = sum(int(row["inherited_agent_model_request_count"]) for row in revalidation["rows"])
    new_requests = 0
    new_completion_count = 0
    for row in rows:
        if row["event"] == "COMPLETION":
            receipts = row.get("provider_receipts", [])
            if {r.get("resolved_model") for r in receipts} != {ALLOWED_ALIAS}:
                raise RunnerError("R3-partial model identity drifted.")
            new_requests += len(receipts)
            evaluation = row["result"]["evaluation"]
            measurements.append({
                "tool_loop_completed": True,
                "target_success": bool(evaluation["target_success"]),
                "non_target_preservation": float(evaluation["non_target_preservation"]),
                "malformed_tool_calls": 0,
            })
            new_completion_count += 1
        elif row["event"] == "FAILURE":
            receipts = row.get("provider_receipts", [])
            if {r.get("resolved_model") for r in receipts} != {ALLOWED_ALIAS}:
                raise RunnerError("R3-partial model identity drifted in failure receipt.")
            new_requests += len(receipts)
            evaluation = toolcap[row["unit_id"]]["evaluation"]
            measurements.append({
                "tool_loop_completed": False,
                "target_success": bool(evaluation["target_success"]),
                "non_target_preservation": float(evaluation["non_target_preservation"]),
                "malformed_tool_calls": 0,
            })
    if len(measurements) != 8:
        raise RunnerError("R3-partial final gate requires four preserved FG plus four TNF measurements.")
    gate = capability_gate(measurements)
    result: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-r3-partial-result-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": gate["verdict"],
        "gate": gate,
        "requested_model": REQUESTED_MODEL,
        "resolved_model": ALLOWED_ALIAS,
        "valid_capability_measurements": 8,
        "preserved_fg_measurements": 4,
        "rerun_tnf_measurements": 4,
        "new_tnf_completion_count": new_completion_count,
        "new_tnf_tool_cap_incomplete_count": len(failures),
        "inherited_fg_agent_model_request_count": inherited_requests,
        "new_agent_model_request_count": new_requests,
        "provider_requests_added_by_fg_revalidation": 0,
        "provider_request_total_new": new_requests,
        "model_selection_evidence_agent_request_total": inherited_requests + new_requests,
        "f0_executed": False,
        "scientific_outcomes_observed": 0,
        "fg_revalidation_sha256": sha256_file(FG_REVALIDATION),
        "partial_contract_sha256": sha256_file(PARTIAL_CONTRACT),
        "ledger_sha256": sha256_file(ledger_path),
        "toolcap_measurement_sha256": sha256_file(toolcap_path) if toolcap_path.exists() else None,
        "authority": {
            "f0": False,
            "f0_reason": "Capability result never self-authorizes F0; separate human authorization is required even if PASS.",
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "second_model": False,
            "method": False,
            "paper_claim": False,
        },
    }
    result["content_sha256"] = sha256_value(result)
    return result


def prepare_artifacts() -> None:
    revalidation = build_fg_revalidation()
    write_json(FG_REVALIDATION, revalidation)
    contract = build_partial_contract(revalidation)
    write_json(PARTIAL_CONTRACT, contract)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--appworld-root", type=Path, default=ROOT / "cache/substrates/appworld-official-20260831")
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--toolcap-ledger", type=Path)
    parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT)
    args = parser.parse_args()
    prepare_artifacts()
    if args.prepare_only:
        print(json.dumps({"status": "R3_PARTIAL_PREPARED", "fg_preserved": 4, "tnf_rerun": 4, "provider_calls": 0}, sort_keys=True))
        return
    if not args.runtime_root or not args.ledger or not args.toolcap_ledger:
        raise RunnerError("Scientific execution requires runtime-root, ledger, and toolcap-ledger.")
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "").strip()
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not api_key:
        raise RunnerError("AA_API_KEY is not configured.")
    snapshot = _verified_json(PROVIDER_SNAPSHOT_OUTPUT)
    if snapshot.get("resolved_request_model") != ALLOWED_ALIAS or snapshot.get("base_url") != base_url:
        raise RunnerError("Frozen Qwen3.7-Plus provider identity/base URL drifted.")
    _verified_json(ADDENDUM_OUTPUT, "QWEN37PLUS_CAPABILITY_A1_AUTHORIZED")
    execute_tnf(
        appworld_root=args.appworld_root,
        runtime_root=args.runtime_root,
        ledger_path=args.ledger,
        toolcap_path=args.toolcap_ledger,
        api_key=api_key,
        base_url=base_url,
    )
    result = adjudicate(ledger_path=args.ledger, toolcap_path=args.toolcap_ledger)
    write_json(args.result_output, result)
    print(json.dumps({
        "status": result["status"],
        "preserved_fg": result.get("preserved_fg_measurements"),
        "rerun_tnf": result.get("rerun_tnf_measurements"),
        "new_provider_requests": result.get("provider_request_total_new"),
        "f0_authorized": result.get("authority", {}).get("f0", False),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
