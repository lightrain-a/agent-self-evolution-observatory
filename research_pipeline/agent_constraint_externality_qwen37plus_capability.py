from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import urllib.error
import urllib.request
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
    PROVIDER_ID,
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

ADDENDUM_ID = "AGENT-CONSTRAINT-EXTERNALITY-QWEN37PLUS-CAPABILITY-ADDENDUM-A1"
EXECUTION_ID = "QWEN37PLUS-CAPABILITY-A1"
REQUESTED_MODEL = "qwen3.7-plus-2026-05-26"
ALLOWED_ALIAS = "qwen3.7-plus"
CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
TOOL_CAP_FAILURE_MESSAGE = "Tool-call cap exceeded."
TOOL_CAP = 12
ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
FLASH_RESULT = GENERATED / "agent-constraint-externality-qwen-capability-continuation-r1-result-20260901.json"
INTERFACE_QUALIFICATION = GENERATED / "agent-constraint-externality-appworld-interface-qualification-r1-20260901.json"
CREDENTIAL_REUSE = GENERATED / "agent-constraint-externality-credential-reuse-authorization-r1-20260901.json"
ADDENDUM_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-addendum-a1-20260901.json"
PROVIDER_SNAPSHOT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-provider-snapshot-a1-20260901.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-a1-20260901.json"
TOOLCAP_SCHEMA = "ace-qwen37plus-toolcap-measurement-a1-v1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def enumerate_units(model_id: str = ALLOWED_ALIAS) -> list[EpisodeUnit]:
    units = [
        EpisodeUnit(
            namespace="capability-a1",
            key=(model_id, family_id, repeat),
            stage="CAPABILITY_CALIBRATION_A1",
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in CAPABILITY_FAMILIES
        for repeat in REPEATS
    ]
    if len(units) != 8 or len({u.unit_id for u in units}) != 8:
        raise RunnerError("A1 capability panel must contain exactly eight unique units.")
    return units


def require_parent_state() -> dict[str, Any]:
    flash = read_json(FLASH_RESULT)
    if flash.get("status") != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise RunnerError("A1 escalation requires the sealed Qwen3.7-Flash floor stop.")
    gate = flash.get("gate", {})
    if gate.get("target_success_rate") != 0.0 or gate.get("tool_loop_completion_rate") != 0.125:
        raise RunnerError("Flash floor evidence drifted from the sealed adjudication.")
    if flash.get("authority", {}).get("f0") is not False:
        raise RunnerError("F0 must remain closed before A1 capability escalation.")
    interface = read_json(INTERFACE_QUALIFICATION)
    if interface.get("status") != "APPWORLD_INTERFACE_RECOVERY_QUALIFICATION_PASS":
        raise RunnerError("A1 requires the repaired AppWorld measurement interface.")
    credential = read_json(CREDENTIAL_REUSE)
    if credential.get("status") != "EXISTING_CREDENTIAL_REUSE_USER_AUTHORIZED":
        raise RunnerError("Existing credential reuse is not authorized.")
    if credential.get("credential_value_persisted") is not False:
        raise RunnerError("Credential authorization must not persist a secret.")
    return flash


def build_addendum(*, catalog_sha256: str | None = None, catalog_model_count: int | None = None) -> dict[str, Any]:
    flash = require_parent_state()
    payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-addendum-a1-v1",
        "object_id": OBJECT_ID,
        "addendum_id": ADDENDUM_ID,
        "status": "QWEN37PLUS_CAPABILITY_A1_AUTHORIZED",
        "change_boundary": {
            "prior_model": "qwen3.7-flash",
            "prior_verdict": "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
            "prior_valid_capability_measurements": flash.get("valid_capability_measurements"),
            "f0_executed": False,
            "f0_scientific_outcomes_observed": 0,
            "post_floor_sequential_escalation": True,
            "not_claimed_as_original_zero-outcome_prereg": True,
        },
        "candidate": {
            "requested_model": REQUESTED_MODEL,
            "allowed_alias": ALLOWED_ALIAS,
            "candidate_count": 1,
            "fallback_candidates": [],
            "exact_snapshot_preferred": True,
            "alias_allowed_only_if_exact_unavailable": True,
        },
        "panel_reuse": {
            "family_ids": list(CAPABILITY_FAMILIES),
            "repeats_per_family": 2,
            "episodes": 8,
            "same_panel_as_flash": True,
            "item_dropping": False,
            "item_replacement": False,
            "threshold_change": False,
            "harness_change": False,
            "tool_cap_change": False,
            "temperature_change": False,
            "reason": "Fixed capability panel is reused prospectively for a stronger model; prior item outcomes are not used to select, drop, replace, or alter tasks or thresholds.",
        },
        "frozen_gate": {
            "tool_loop_completion_rate_min": 0.75,
            "target_success_rate_min": 0.50,
            "target_success_rate_max": 0.875,
            "non_target_preservation_rate_min": 0.85,
            "malformed_tool_calls_required": 0,
            "tool_call_cap": TOOL_CAP,
            "temperature": 0,
            "provider_max_retries": 0,
            "application_retry": False,
            "replacement": False,
        },
        "selection_rationale": [
            "STRONGER_SAME_GENERATION_CAPABILITY_TIER_AFTER_CLEAR_FLASH_FLOOR",
            "FUNCTION_CALLING_AND_AGENT_TOOL_USE_SUPPORT",
            "PREFER_REPRODUCIBLE_SNAPSHOT_WHEN_PROVIDER_EXPOSES_IT",
            "AVOID_JUMPING_DIRECTLY_TO_MAX_TIER_BEFORE_CAPABILITY_GATE",
        ],
        "forbidden_rationale": "EXPECTED_TO_PRODUCE_THE_PAPER_HYPOTHESIS",
        "catalog_evidence": {
            "catalog_sha256": catalog_sha256,
            "catalog_model_count": catalog_model_count,
            "exact_snapshot_available": False if catalog_sha256 else None,
            "allowed_alias_available": True if catalog_sha256 else None,
        },
        "authority": {
            "catalog_query": True,
            "capability_calibration_a1": True,
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "second_additional_model": False,
            "method": False,
            "paper_claim": False,
        },
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def capture_provider_snapshot(*, api_key: str, base_url: str, opener: Any = urllib.request.urlopen) -> dict[str, Any]:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": "Bearer " + api_key},
        method="GET",
    )
    try:
        with opener(request, timeout=60.0) as response:
            raw = response.read()
        catalog = json.loads(raw.decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RunnerError(f"A1 model catalog transport failed without retry: {type(exc).__name__}") from exc
    except json.JSONDecodeError as exc:
        raise RunnerError("A1 model catalog parse failed without retry.") from exc
    ids = {
        item.get("id") for item in catalog.get("data", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    exact = REQUESTED_MODEL in ids
    alias = ALLOWED_ALIAS in ids
    if exact:
        resolved = REQUESTED_MODEL
    elif alias:
        resolved = ALLOWED_ALIAS
    else:
        raise RunnerError("Neither frozen Qwen3.7-Plus snapshot nor allowed alias is available.")
    payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-provider-snapshot-a1-v1",
        "object_id": OBJECT_ID,
        "provider": PROVIDER_ID,
        "base_url": base_url.rstrip("/"),
        "requested_model": REQUESTED_MODEL,
        "allowed_alias": ALLOWED_ALIAS,
        "requested_model_available": exact,
        "allowed_alias_available": alias,
        "resolved_request_model": resolved,
        "catalog_model_count": len(ids),
        "catalog_response_sha256": sha256_value(catalog),
        "catalog_provider_request_count": 1,
        "max_retries": 0,
        "secrets_persisted": False,
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
            raise RunnerError("Unexpected A1 tool-cap measurement schema.")
        claimed = row.get("content_sha256")
        unsigned = dict(row)
        unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RunnerError("A1 tool-cap measurement hash mismatch.")
        if row["unit_id"] in seen:
            raise RunnerError("Duplicate A1 tool-cap measurement.")
        seen.add(row["unit_id"])
    return rows


def _append_toolcap(path: Path, *, unit: EpisodeUnit, evaluation: dict[str, Any], receipt_count: int) -> None:
    existing = {row["unit_id"] for row in _toolcap_rows(path)}
    if unit.unit_id in existing:
        raise RunnerError("Refusing duplicate A1 tool-cap measurement.")
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
        "provider_reexecution": False,
        "retry": False,
        "replacement": False,
        "evaluation": evaluation,
    }
    row["content_sha256"] = sha256_value(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def execute(*, appworld_root: Path, protected_bundle: Path, runtime_root: Path, ledger_path: Path, toolcap_path: Path, resolved_model: str, api_key: str, base_url: str) -> None:
    if resolved_model not in {REQUESTED_MODEL, ALLOWED_ALIAS}:
        raise RunnerError("A1 model replacement is forbidden.")
    provider = TypicalResponsesClient(api_key, base_url)
    spec = load_protected_spec(protected_bundle)
    families = {f["family_id"]: f for f in spec["families"]}
    units = enumerate_units(resolved_model)
    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    failure_rows = {row["unit_id"]: row for row in ledger.rows() if row["event"] == "FAILURE"}
    for unit in units:
        family = families[unit.family_id]
        state = states.get(unit.unit_id)
        if state == "COMPLETION":
            continue
        if state == "FAILURE":
            row = failure_rows.get(unit.unit_id, {})
            if not (
                row.get("failure_class") == "RunnerError"
                and row.get("message") == TOOL_CAP_FAILURE_MESSAGE
                and row.get("retry_attempted") is False
            ):
                raise RunnerError(f"A1 cannot continue past non-toolcap failure {unit.unit_id}.")
            if unit.unit_id not in {r["unit_id"] for r in _toolcap_rows(toolcap_path)}:
                raise RunnerError(f"A1 prior tool-cap failure lacks frozen-boundary measurement: {unit.unit_id}")
            continue
        if state is not None:
            raise RunnerError(f"A1 cannot replay non-terminal unit {unit.unit_id}: {state}")
        arm = next(a for a in family["arms"] if a["coupling_level"] == "LOW")
        task_id = "acea1" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(appworld_root, unit_root, family=family, arm=arm, task_id=task_id)
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-qwen37plus-capability-a1",
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
                    model=resolved_model,
                    base_url=base_url,
                    result_evaluator=lambda arm=arm, world=world: world.save_and_evaluate(arm),
                )
            except RunnerError as exc:
                if str(exc) != TOOL_CAP_FAILURE_MESSAGE:
                    raise
                evaluation = world.save_and_evaluate(arm)
                failure = next(
                    row for row in reversed(ledger.rows())
                    if row["unit_id"] == unit.unit_id and row["event"] == "FAILURE"
                )
                _append_toolcap(toolcap_path, unit=unit, evaluation=evaluation, receipt_count=len(failure.get("provider_receipts", [])))
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(units)


def adjudicate(*, ledger_path: Path, toolcap_path: Path, resolved_model: str, catalog_request_count: int = 1) -> dict[str, Any]:
    ledger = AppendOnlyLedger(ledger_path)
    units = enumerate_units(resolved_model)
    ledger.assert_all_terminal(units)
    rows = ledger.rows()
    failures = [row for row in rows if row["event"] == "FAILURE"]
    invalid = [
        row for row in failures
        if not (
            row.get("failure_class") == "RunnerError"
            and row.get("message") == TOOL_CAP_FAILURE_MESSAGE
            and row.get("retry_attempted") is False
        )
    ]
    if invalid:
        result: dict[str, Any] = {
            "schema_version": "ace-qwen37plus-capability-result-a1-v1",
            "object_id": OBJECT_ID,
            "execution_id": EXECUTION_ID,
            "status": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
            "failure_units": [row["unit_id"] for row in invalid],
            "valid_capability_measurements": len(units) - len(invalid),
            "scientific_outcomes_observed": 0,
            "authority": {"f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
        }
        result["content_sha256"] = sha256_value(result)
        return result
    toolcap = {row["unit_id"]: row for row in _toolcap_rows(toolcap_path)}
    missing = [row["unit_id"] for row in failures if row["unit_id"] not in toolcap]
    if missing:
        raise RunnerError("A1 tool-cap failures lack measurements: " + ", ".join(missing))
    completion_rows = [row for row in rows if row["event"] == "COMPLETION"]
    if len(completion_rows) + len(failures) != 8:
        raise RunnerError("A1 adjudication requires eight terminal units.")
    measurements: list[dict[str, Any]] = []
    resolved_models: set[str] = set()
    agent_requests = 0
    for row in completion_rows:
        receipts = row["provider_receipts"]
        agent_requests += len(receipts)
        resolved_models.update(receipt["resolved_model"] for receipt in receipts)
        evaluation = row["result"]["evaluation"]
        measurements.append({
            "tool_loop_completed": True,
            "target_success": bool(evaluation["target_success"]),
            "non_target_preservation": float(evaluation["non_target_preservation"]),
            "malformed_tool_calls": 0,
        })
    for row in failures:
        receipts = row.get("provider_receipts", [])
        agent_requests += len(receipts)
        resolved_models.update(receipt["resolved_model"] for receipt in receipts)
        evaluation = toolcap[row["unit_id"]]["evaluation"]
        measurements.append({
            "tool_loop_completed": False,
            "target_success": bool(evaluation["target_success"]),
            "non_target_preservation": float(evaluation["non_target_preservation"]),
            "malformed_tool_calls": 0,
        })
    if resolved_models != {resolved_model}:
        raise RunnerError("A1 resolved-model identity drifted during capability calibration.")
    gate = capability_gate(measurements)
    result = {
        "schema_version": "ace-qwen37plus-capability-result-a1-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": gate["verdict"],
        "gate": gate,
        "requested_model": REQUESTED_MODEL,
        "resolved_model": resolved_model,
        "valid_capability_measurements": 8,
        "agent_episode_count": 8,
        "agent_model_request_count": agent_requests,
        "catalog_provider_request_count": catalog_request_count,
        "provider_request_total": catalog_request_count + agent_requests,
        "tool_cap_incomplete_measurements": len(failures),
        "scientific_outcomes_observed": 0,
        "f0_executed": False,
        "authority": {
            "f0": False,
            "f0_reason": "A1 capability result requires separate human F0 authorization even if PASS.",
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "second_additional_model": False,
            "method": False,
            "paper_claim": False,
        },
        "ledger_sha256": sha256_file(ledger_path),
        "toolcap_measurement_sha256": sha256_file(toolcap_path) if toolcap_path.exists() else None,
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--protected-bundle", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--toolcap-ledger", type=Path, required=True)
    parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT)
    parser.add_argument("--snapshot-output", type=Path, default=PROVIDER_SNAPSHOT_OUTPUT)
    parser.add_argument("--addendum-output", type=Path, default=ADDENDUM_OUTPUT)
    args = parser.parse_args()

    require_parent_state()
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "")
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not api_key:
        raise RunnerError("AA_API_KEY is not configured.")
    if not args.snapshot_output.is_file() or not args.addendum_output.is_file():
        raise RunnerError("A1 scientific execution requires the pre-provider frozen snapshot and addendum.")
    snapshot = read_json(args.snapshot_output)
    claimed_snapshot = snapshot.get("content_sha256")
    unsigned_snapshot = dict(snapshot)
    unsigned_snapshot.pop("content_sha256", None)
    if claimed_snapshot != sha256_value(unsigned_snapshot):
        raise RunnerError("Frozen A1 provider snapshot content hash mismatch.")
    if snapshot.get("requested_model_available") is not False:
        raise RunnerError("Frozen A1 evidence no longer represents exact-snapshot unavailability.")
    if snapshot.get("allowed_alias_available") is not True:
        raise RunnerError("Frozen A1 allowed alias was not available at prereg freeze.")
    if snapshot.get("resolved_request_model") != ALLOWED_ALIAS:
        raise RunnerError("Frozen A1 provider snapshot did not resolve the unique allowed alias.")
    if snapshot.get("base_url") != base_url:
        raise RunnerError("A1 provider base URL drifted from the frozen snapshot.")
    addendum = read_json(args.addendum_output)
    claimed_addendum = addendum.get("content_sha256")
    unsigned_addendum = dict(addendum)
    unsigned_addendum.pop("content_sha256", None)
    if claimed_addendum != sha256_value(unsigned_addendum):
        raise RunnerError("Frozen A1 addendum content hash mismatch.")
    if addendum.get("status") != "QWEN37PLUS_CAPABILITY_A1_AUTHORIZED":
        raise RunnerError("Frozen A1 addendum is not authorized.")
    resolved_model = snapshot["resolved_request_model"]
    execute(
        appworld_root=args.appworld_root,
        protected_bundle=args.protected_bundle,
        runtime_root=args.runtime_root,
        ledger_path=args.ledger,
        toolcap_path=args.toolcap_ledger,
        resolved_model=resolved_model,
        api_key=api_key,
        base_url=base_url,
    )
    result = adjudicate(
        ledger_path=args.ledger,
        toolcap_path=args.toolcap_ledger,
        resolved_model=resolved_model,
        catalog_request_count=1,
    )
    write_json(args.result_output, result)
    print(json.dumps({
        "status": result["status"],
        "resolved_model": resolved_model,
        "valid_capability_measurements": result.get("valid_capability_measurements"),
        "provider_request_total": result.get("provider_request_total"),
        "f0_authorized": result.get("authority", {}).get("f0", False),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
