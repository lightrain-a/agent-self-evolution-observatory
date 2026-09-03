from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
from research_pipeline.agent_constraint_externality_qwen37plus_capability import TOOL_CAP_FAILURE_MESSAGE
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

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V4_CONTRACT = GENERATED / "agent-constraint-externality-capability-substrate-v4-contract-20260902.json"
V4_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r4-20260902.json"
TRANSPORT_Q0_FAIL = GENERATED / "agent-constraint-externality-signed-no-tools-json-action-q0-failure-20260903.json"
OLD_FLASH_VOID = GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r1-20260901.json"
MODEL_ID = "qwen3.7-flash"
MODEL_PROFILE = MODEL_ID
PROVIDER = PROVIDER_ID
BASE_URL_FROZEN = "https://api.aa.com.cn/api/v1"
TOOL_CALL_CAP = 16
CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
EXECUTION_ID = "DIRECT-QWEN37FLASH-CAPABILITY-V4-R1"
STAGE = "DIRECT_QWEN37FLASH_CAPABILITY_V4_R1"
CATALOG_OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-catalog-v4-r1-20260903.json"
AUTH_OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-v4-r1-authorization-20260903.json"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-capability-v4-r1-contract-20260903.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-direct-qwen37flash-capability-v4-r1-result-20260903.json"
TOOLCAP_SCHEMA = "ace-direct-qwen37flash-v4-r1-toolcap-v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise RunnerError(f"Required artifact missing: {path}")
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RunnerError(f"Object mismatch: {path}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload)
        unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RunnerError(f"Content hash mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RunnerError(f"Unexpected status in {path}: {payload.get('status')}")
    return payload


def units() -> list[EpisodeUnit]:
    rows = [
        EpisodeUnit(
            namespace="capability",
            key=(MODEL_ID, family_id, repeat),
            stage=STAGE,
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in CAPABILITY_FAMILIES
        for repeat in REPEATS
    ]
    if len(rows) != 8 or len({row.unit_id for row in rows}) != 8:
        raise RunnerError("Direct Flash V4 requires exactly eight unique capability units.")
    return rows


def capture_catalog(api_key: str, base_url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": "Bearer " + api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise RunnerError(f"Direct provider catalog failed without retry: {type(exc).__name__}") from exc
    rows = payload.get("data", [])
    ids = sorted({str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("id")})
    if MODEL_ID not in ids:
        raise RunnerError(f"Frozen direct candidate {MODEL_ID} is absent from provider catalog.")
    result: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-v4-r1-catalog-v1",
        "object_id": OBJECT_ID,
        "status": "DIRECT_QWEN37FLASH_CATALOG_V4_R1_PASS",
        "provider": PROVIDER,
        "base_url": base_url.rstrip("/"),
        "model_id": MODEL_ID,
        "model_available": True,
        "catalog_model_count": len(ids),
        "catalog_response_sha256": sha256_value(payload),
        "catalog_provider_request_count": 1,
        "max_retries": 0,
        "secrets_persisted": False,
    }
    result["content_sha256"] = sha256_value(result)
    return result


def freeze() -> dict[str, Any]:
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "").strip()
    base_url = os.getenv("AA_BASE_URL", BASE_URL_FROZEN).rstrip("/")
    if not api_key:
        raise RunnerError("AA_API_KEY is not configured.")
    if base_url != BASE_URL_FROZEN:
        raise RunnerError("Direct provider base URL drifted from frozen value.")
    transport = verified(
        TRANSPORT_Q0_FAIL,
        "SIGNED_NO_TOOLS_JSON_ACTION_Q0_FAIL_CODING_PERSONA_CONTAMINATION",
    )
    void = verified(OLD_FLASH_VOID, "CAPABILITY_RESULTS_VOID_SUBSTRATE_INVALID")
    v4_contract = verified(V4_CONTRACT, "CAPABILITY_SUBSTRATE_V4_TOOL_BUDGET_QUALIFIED")
    v4_qual = verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    if v4_contract.get("tool_budget_rule", {}).get("resolved_tool_call_cap") != TOOL_CALL_CAP:
        raise RunnerError("V4 tool-call cap drifted.")
    if v4_qual.get("tool_call_cap") != TOOL_CALL_CAP:
        raise RunnerError("V4 reachability qualification cap drifted.")
    affected = void.get("affected_results", [])
    if not any(row.get("model") == MODEL_ID for row in affected if isinstance(row, dict)):
        raise RunnerError("Historical Flash result is not explicitly voided by substrate invalidation.")
    catalog = capture_catalog(api_key, base_url)
    write_json(CATALOG_OUTPUT, catalog)
    authorization: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-v4-r1-human-authorization-v1",
        "object_id": OBJECT_ID,
        "status": "USER_CONTINUE_AUTHORIZED_DIRECT_QWEN37FLASH_V4_REQUALIFICATION",
        "authorization_source": "USER_CONTINUE_AFTER_CODINGPLAN_TRANSPORT_FAILURE",
        "candidate_selection_boundary": "POST_CODINGPLAN_SCIENTIFIC_ACTOR_REJECTION_PRE_DIRECT_FLASH_V4_SCIENTIFIC_DISPATCH",
        "model_id": MODEL_ID,
        "selection_reason": "SAME_GENERATION_LOWER_TIER_THAN_VALID_DIRECT_QWEN37PLUS_CEILING; HISTORICAL_FLASH_OUTCOMES_VOIDED_BY_SUBSTRATE_INVALIDITY",
        "forbidden_selection_reason": "EXPECTED_EXTERNALITY_EFFECT",
        "authority": {
            "direct_flash_capability_v4_r1": True,
            "new_source_failure_qualification": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed_by_this_authorization": 0,
    }
    authorization["content_sha256"] = sha256_value(authorization)
    write_json(AUTH_OUTPUT, authorization)
    contract: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-capability-v4-r1-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": "DIRECT_QWEN37FLASH_CAPABILITY_V4_R1_AUTHORIZED",
        "provider": PROVIDER,
        "base_url": base_url,
        "model_id": MODEL_ID,
        "harness": "APPWORLD_DIRECT_FUNCTION_CALLING_V4",
        "panel": {
            "family_ids": list(CAPABILITY_FAMILIES),
            "repeats": list(REPEATS),
            "episode_count": 8,
            "coupling_arm": "LOW",
            "historical_invalid_flash_measurements_reused": False,
        },
        "execution": {
            "temperature": 0,
            "provider_max_retries": 0,
            "application_retry": False,
            "replacement": False,
            "tool_call_cap": TOOL_CALL_CAP,
            "durable_dispatch_before_first_model_request": True,
            "unknown_after_dispatch_replay": False,
        },
        "gate": {
            "tool_loop_completion_min": 0.75,
            "target_success_min": 0.50,
            "target_success_max": 0.875,
            "non_target_preservation_min": 0.85,
            "malformed_tool_calls_required": 0,
        },
        "substrate": {
            "bundle": str(BUNDLE.relative_to(ROOT)),
            "bundle_sha256": sha256_file(BUNDLE),
            "v4_contract_content_sha256": v4_contract["content_sha256"],
            "v4_qualification_content_sha256": v4_qual["content_sha256"],
        },
        "lineage": {
            "transport_failure_content_sha256": transport["content_sha256"],
            "historical_flash_void_content_sha256": void["content_sha256"],
            "catalog_content_sha256": catalog["content_sha256"],
            "authorization_content_sha256": authorization["content_sha256"],
        },
        "authority": {
            "capability_v4_r1": True,
            "source_failure_qualification": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed": 0,
    }
    contract["content_sha256"] = sha256_value(contract)
    write_json(CONTRACT_OUTPUT, contract)
    return {"catalog": catalog, "authorization": authorization, "contract": contract}


def toolcap_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen: set[str] = set()
    for row in rows:
        if row.get("schema_version") != TOOLCAP_SCHEMA:
            raise RunnerError("Unexpected Flash V4 toolcap schema.")
        unsigned = dict(row)
        claimed = unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise RunnerError("Flash V4 toolcap content hash mismatch.")
        if row["unit_id"] in seen:
            raise RunnerError("Duplicate Flash V4 toolcap measurement.")
        seen.add(row["unit_id"])
    return rows


def append_toolcap(path: Path, unit: EpisodeUnit, evaluation: dict[str, Any], receipt_count: int) -> None:
    if unit.unit_id in {row["unit_id"] for row in toolcap_rows(path)}:
        raise RunnerError("Duplicate Flash V4 toolcap unit.")
    row: dict[str, Any] = {
        "schema_version": TOOLCAP_SCHEMA,
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "unit_id": unit.unit_id,
        "family_id": unit.family_id,
        "classification": "CAPABILITY_TOOL_LOOP_INCOMPLETE_AT_FROZEN_CAP",
        "tool_loop_completed": False,
        "tool_call_cap": TOOL_CALL_CAP,
        "provider_receipt_count": receipt_count,
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


def execute(*, runtime_root: Path, ledger_path: Path, toolcap_path: Path) -> None:
    contract = verified(CONTRACT_OUTPUT, "DIRECT_QWEN37FLASH_CAPABILITY_V4_R1_AUTHORIZED")
    if contract.get("execution", {}).get("tool_call_cap") != TOOL_CALL_CAP:
        raise RunnerError("Flash V4 contract tool cap drifted.")
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "").strip()
    base_url = os.getenv("AA_BASE_URL", BASE_URL_FROZEN).rstrip("/")
    if not api_key or base_url != BASE_URL_FROZEN:
        raise RunnerError("Direct provider credential/base URL unavailable or drifted.")
    verified(CATALOG_OUTPUT, "DIRECT_QWEN37FLASH_CATALOG_V4_R1_PASS")
    spec = load_protected_spec(BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    provider = TypicalResponsesClient(api_key, base_url)
    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    failures = {row["unit_id"]: row for row in ledger.rows() if row["event"] == "FAILURE"}
    for unit in units():
        state = states.get(unit.unit_id)
        if state == "COMPLETION":
            continue
        if state == "FAILURE":
            row = failures.get(unit.unit_id, {})
            if not (
                row.get("failure_class") == "RunnerError"
                and row.get("message") == TOOL_CAP_FAILURE_MESSAGE
                and row.get("retry_attempted") is False
                and unit.unit_id in {item["unit_id"] for item in toolcap_rows(toolcap_path)}
            ):
                raise RunnerError(f"Cannot continue past non-toolcap Flash V4 failure: {unit.unit_id}")
            continue
        if state is not None:
            raise RunnerError(f"Refusing replay of dispatched Flash V4 unit {unit.unit_id}: {state}")
        family = families[unit.family_id]
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        if int(arm["matching"]["tool_budget"]) != TOOL_CALL_CAP:
            raise RunnerError("Flash V4 family tool budget drifted from 16.")
        task_id = "aceflashv4" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        if unit_root.exists():
            raise RunnerError(f"Refusing overwrite of Flash V4 unit runtime: {unit_root}")
        materialized = prepare_appworld_runtime_root(
            APPWORLD_ROOT,
            unit_root,
            family=family,
            arm=arm,
            task_id=task_id,
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-direct-qwen37flash-capability-v4-r1",
            seed=1100 + int(unit.repeat or 0),
            allowed_apps=set(family["fixture"]["apps"]),
            max_interactions=TOOL_CALL_CAP,
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
                    model=MODEL_ID,
                    base_url=base_url,
                    result_evaluator=lambda arm=arm, world=world: world.save_and_evaluate(arm),
                    max_tool_calls=TOOL_CALL_CAP,
                )
            except RunnerError as exc:
                if str(exc) != TOOL_CAP_FAILURE_MESSAGE:
                    raise
                evaluation = world.save_and_evaluate(arm)
                failure = next(
                    row for row in reversed(ledger.rows())
                    if row["unit_id"] == unit.unit_id and row["event"] == "FAILURE"
                )
                append_toolcap(toolcap_path, unit, evaluation, len(failure.get("provider_receipts", [])))
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(units())


def adjudicate(*, ledger_path: Path, toolcap_path: Path) -> dict[str, Any]:
    ledger = AppendOnlyLedger(ledger_path)
    ledger.assert_all_terminal(units())
    rows = ledger.rows()
    terminal = [row for row in rows if row["event"] in {"COMPLETION", "FAILURE"}]
    if len(terminal) != 8:
        raise RunnerError("Flash V4 adjudication requires exactly eight terminal rows.")
    toolcaps = {row["unit_id"]: row for row in toolcap_rows(toolcap_path)}
    measurements: list[dict[str, Any]] = []
    provider_requests = 0
    resolved: set[str] = set()
    completion_count = 0
    toolcap_count = 0
    for row in terminal:
        receipts = row.get("provider_receipts", [])
        provider_requests += len(receipts)
        resolved.update(str(receipt.get("resolved_model")) for receipt in receipts if receipt.get("resolved_model"))
        if row["event"] == "COMPLETION":
            evaluation = row["result"]["evaluation"]
            measurements.append({
                "tool_loop_completed": True,
                "target_success": bool(evaluation["target_success"]),
                "non_target_preservation": float(evaluation["non_target_preservation"]),
                "malformed_tool_calls": 0,
            })
            completion_count += 1
        else:
            if row.get("failure_class") != "RunnerError" or row.get("message") != TOOL_CAP_FAILURE_MESSAGE:
                result = {
                    "schema_version": "ace-direct-qwen37flash-capability-v4-r1-result-v1",
                    "object_id": OBJECT_ID,
                    "execution_id": EXECUTION_ID,
                    "status": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
                    "failure_unit": row["unit_id"],
                    "authority": {"source_failure_qualification": False, "f0_r1": False, "p1": False},
                }
                result["content_sha256"] = sha256_value(result)
                return result
            if row["unit_id"] not in toolcaps:
                raise RunnerError("Flash V4 toolcap failure lacks measurement.")
            evaluation = toolcaps[row["unit_id"]]["evaluation"]
            measurements.append({
                "tool_loop_completed": False,
                "target_success": bool(evaluation["target_success"]),
                "non_target_preservation": float(evaluation["non_target_preservation"]),
                "malformed_tool_calls": 0,
            })
            toolcap_count += 1
    if resolved != {MODEL_ID}:
        raise RunnerError(f"Flash V4 resolved model drifted: {sorted(resolved)}")
    gate = capability_gate(measurements)
    result: dict[str, Any] = {
        "schema_version": "ace-direct-qwen37flash-capability-v4-r1-result-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": gate["verdict"],
        "provider": PROVIDER,
        "model_id": MODEL_ID,
        "harness": "APPWORLD_DIRECT_FUNCTION_CALLING_V4",
        "gate": gate,
        "valid_capability_measurements": 8,
        "agent_episode_count": 8,
        "completion_count": completion_count,
        "tool_cap_incomplete_count": toolcap_count,
        "agent_model_request_count": provider_requests,
        "catalog_provider_request_count": 1,
        "provider_request_total": provider_requests + 1,
        "tool_call_cap": TOOL_CALL_CAP,
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "scientific_outcomes_observed": 0,
        "f0_executed": False,
        "ledger_sha256": sha256_file(ledger_path),
        "toolcap_measurement_sha256": sha256_file(toolcap_path) if toolcap_path.exists() else None,
        "contract_content_sha256": verified(CONTRACT_OUTPUT)["content_sha256"],
        "authority": {
            "source_failure_qualification": gate["verdict"] == "CAPABILITY_CALIBRATION_PASS",
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--toolcap-ledger", type=Path)
    parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT)
    args = parser.parse_args()
    if args.freeze:
        artifacts = freeze()
        print(json.dumps({
            "catalog_status": artifacts["catalog"]["status"],
            "authorization_status": artifacts["authorization"]["status"],
            "contract_status": artifacts["contract"]["status"],
            "model_id": MODEL_ID,
            "tool_call_cap": TOOL_CALL_CAP,
            "scientific_dispatch_count": 0,
        }, sort_keys=True))
        return
    if args.runtime_root is None or args.ledger is None or args.toolcap_ledger is None:
        raise SystemExit("--runtime-root, --ledger, and --toolcap-ledger are required unless --freeze is used")
    execute(runtime_root=args.runtime_root.resolve(), ledger_path=args.ledger.resolve(), toolcap_path=args.toolcap_ledger.resolve())
    result = adjudicate(ledger_path=args.ledger.resolve(), toolcap_path=args.toolcap_ledger.resolve())
    write_json(args.result_output.resolve(), result)
    print(json.dumps({
        "status": result["status"],
        "target_success_rate": result.get("gate", {}).get("target_success_rate"),
        "tool_loop_completion_rate": result.get("gate", {}).get("tool_loop_completion_rate"),
        "provider_request_total": result.get("provider_request_total"),
        "source_failure_qualification_authorized": result.get("authority", {}).get("source_failure_qualification", False),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
