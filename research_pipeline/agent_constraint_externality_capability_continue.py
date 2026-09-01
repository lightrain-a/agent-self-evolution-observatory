from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_capability_execute import (
    capability_gate,
    enumerate_capability_units,
)
from research_pipeline.agent_constraint_externality_capability_measurement_recover import (
    HISTORICAL_UNIT_ID,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    DEFAULT_BASE_URL,
    OBJECT_ID,
    AppendOnlyLedger,
    RunnerError,
    TypicalResponsesClient,
    run_episode,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec
from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

CONTINUATION_ID = "CAPABILITY-INTERFACE-RECOVERY-CONTINUATION-R1"
QUALIFICATION_PATH = Path(
    "generated/agent-constraint-externality-appworld-interface-qualification-r1-20260901.json"
)
CONTRACT_PATH = Path(
    "generated/agent-constraint-externality-capability-continuation-r1-contract-20260901.json"
)
CREDENTIAL_REUSE_AUTHORIZATION_PATH = Path(
    "generated/agent-constraint-externality-credential-reuse-authorization-r1-20260901.json"
)


def load_recovery(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("object_id") != OBJECT_ID:
        raise RunnerError("Measurement-recovery object mismatch.")
    if payload.get("status") != "HISTORICAL_MEASUREMENT_RECOVERY_PASS":
        raise RunnerError("Historical unit is not validly measurement-recovered.")
    if payload.get("unit_id") != HISTORICAL_UNIT_ID:
        raise RunnerError("Unexpected recovered capability unit.")
    if payload.get("resolved_model") != ALLOWED_ALIAS:
        raise RunnerError("Recovered unit model identity drifted.")
    if payload.get("provider_requests_added_by_recovery") != 0:
        raise RunnerError("Measurement-only recovery unexpectedly used provider requests.")
    if payload.get("agent_reexecution") is not False:
        raise RunnerError("Recovered unit was re-executed instead of measured offline.")
    if payload.get("valid_capability_measurements") != 1:
        raise RunnerError("Recovery artifact does not represent exactly one valid unit.")
    return payload


def remaining_capability_units() -> list[Any]:
    units = [
        unit
        for unit in enumerate_capability_units(ALLOWED_ALIAS)
        if unit.unit_id != HISTORICAL_UNIT_ID
    ]
    if len(units) != 7 or HISTORICAL_UNIT_ID in {unit.unit_id for unit in units}:
        raise RunnerError("Continuation must contain exactly the seven never-dispatched units.")
    return units


def require_recovery_qualification(path: Path = QUALIFICATION_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "APPWORLD_INTERFACE_RECOVERY_QUALIFICATION_PASS":
        raise RunnerError("Capability continuation requires interface recovery qualification PASS.")
    if payload.get("provider_reexecution_authorized") is not False:
        raise RunnerError("Interface qualification artifact unexpectedly authorized reexecution.")
    return payload


def require_continuation_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "CAPABILITY_CONTINUATION_AUTHORIZED_CREDENTIAL_ROTATION_REQUIRED":
        raise RunnerError("Capability continuation contract is not in the expected gated state.")
    if payload.get("model") != ALLOWED_ALIAS:
        raise RunnerError("Capability continuation contract model drifted.")
    if payload.get("remaining_units") != 7:
        raise RunnerError("Capability continuation contract must authorize exactly seven units.")
    if payload.get("replay_recovered_unit") is not False:
        raise RunnerError("Continuation contract must forbid recovered-unit replay.")
    if payload.get("f0_authorized") is not False:
        raise RunnerError("F0 must remain closed during capability continuation.")
    return payload


def require_rotated_credential(
    contract: dict[str, Any], env_path: Path = DEFAULT_ENV_FILE
) -> None:
    if not env_path.is_file():
        raise RunnerError("Credential env file is unavailable.")
    boundary = int(contract["credential_env_mtime_must_be_gt"])
    if int(env_path.stat().st_mtime) <= boundary:
        raise RunnerError("CREDENTIAL_ROTATION_REQUIRED: env file predates the frozen rotation boundary.")


def require_credential_authorization(
    contract: dict[str, Any],
    *,
    env_path: Path = DEFAULT_ENV_FILE,
    reuse_authorization_path: Path = CREDENTIAL_REUSE_AUTHORIZATION_PATH,
) -> str:
    """Permit either a rotated credential or an explicit non-scientific reuse override."""
    if not env_path.is_file():
        raise RunnerError("Credential env file is unavailable.")
    boundary = int(contract["credential_env_mtime_must_be_gt"])
    if int(env_path.stat().st_mtime) > boundary:
        return "ROTATED_CREDENTIAL"
    if not reuse_authorization_path.is_file():
        raise RunnerError(
            "CREDENTIAL_ROTATION_REQUIRED: no explicit existing-credential reuse authorization."
        )
    payload = json.loads(reuse_authorization_path.read_text(encoding="utf-8"))
    if payload.get("object_id") != OBJECT_ID:
        raise RunnerError("Credential-reuse authorization object mismatch.")
    if payload.get("status") != "EXISTING_CREDENTIAL_REUSE_USER_AUTHORIZED":
        raise RunnerError("Credential-reuse authorization is not active.")
    if payload.get("existing_credential_reuse_authorized") is not True:
        raise RunnerError("Credential-reuse authorization is not explicit.")
    if payload.get("credential_value_persisted") is not False:
        raise RunnerError("Credential-reuse artifact must not persist the credential value.")
    if payload.get("scientific_protocol_changed") is not False:
        raise RunnerError("Credential reuse may not modify the scientific protocol.")
    if payload.get("model_changed") is not False or payload.get("thresholds_changed") is not False:
        raise RunnerError("Credential reuse may not change model or thresholds.")
    if payload.get("replay_recovered_unit_authorized") is not False:
        raise RunnerError("Credential reuse must not authorize recovered-unit replay.")
    if payload.get("f0_authorized") is not False:
        raise RunnerError("Credential reuse must not authorize F0.")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RunnerError("Credential-reuse authorization content hash mismatch.")
    return "EXISTING_CREDENTIAL_USER_AUTHORIZED"


def execute_remaining_capability(
    *,
    appworld_root: Path,
    protected_bundle: Path,
    runtime_root: Path,
    ledger_path: Path,
    recovery_path: Path,
) -> None:
    require_recovery_qualification()
    contract = require_continuation_contract()
    recovery = load_recovery(recovery_path)
    require_credential_authorization(contract)
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "")
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if base_url != contract["base_url"]:
        raise RunnerError("Provider base URL drifted from continuation contract.")
    provider = TypicalResponsesClient(api_key, base_url)
    spec = load_protected_spec(protected_bundle)
    families = {family["family_id"]: family for family in spec["families"]}
    ledger = AppendOnlyLedger(ledger_path)
    units = remaining_capability_units()
    states = ledger.states()
    for unit in units:
        state = states.get(unit.unit_id)
        if state == "COMPLETION":
            continue
        if state is not None:
            raise RunnerError(
                f"Continuation cannot replay/replace non-completed unit {unit.unit_id}: {state}"
            )
        family = families[unit.family_id]
        arm = next(arm for arm in family["arms"] if arm["coupling_level"] == "LOW")
        task_id = "acecap" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(
            appworld_root, unit_root, family=family, arm=arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-capability-continuation-r1",
            seed=1100 + int(unit.repeat or 0),
            allowed_apps=set(family["fixture"]["apps"]),
        )
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
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(units)
    if recovery.get("valid_capability_measurements") != 1:
        raise RunnerError("Recovered-unit validity changed during continuation.")


def adjudicate_continuation(
    *,
    recovery_path: Path,
    continuation_ledger_path: Path,
) -> dict[str, Any]:
    recovery = load_recovery(recovery_path)
    ledger = AppendOnlyLedger(continuation_ledger_path)
    units = remaining_capability_units()
    ledger.assert_all_terminal(units)
    rows = ledger.rows()
    failures = [row for row in rows if row["event"] == "FAILURE"]
    if failures:
        result: dict[str, Any] = {
            "schema_version": "ace-qwen-capability-continuation-r1-v1",
            "object_id": OBJECT_ID,
            "continuation_id": CONTINUATION_ID,
            "status": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
            "failure_units": [row["unit_id"] for row in failures],
            "recovery_artifact_sha256": sha256_file(recovery_path),
            "continuation_ledger_sha256": sha256_file(continuation_ledger_path),
            "f0_backbone": None,
            "authority": {"f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False},
        }
        result["content_sha256"] = sha256_value(result)
        return result
    completion_rows = [row for row in rows if row["event"] == "COMPLETION"]
    if len(completion_rows) != 7:
        raise RunnerError("Continuation adjudication requires seven completion rows.")
    completions: list[dict[str, Any]] = [{
        "tool_loop_completed": bool(recovery["tool_loop_completed"]),
        "target_success": bool(recovery["evaluation"]["target_success"]),
        "non_target_preservation": float(recovery["evaluation"]["non_target_preservation"]),
        "malformed_tool_calls": 0,
    }]
    resolved_models = {recovery["resolved_model"]}
    continuation_agent_requests = 0
    for row in completion_rows:
        result = row["result"]
        evaluation = result["evaluation"]
        receipts = row["provider_receipts"]
        continuation_agent_requests += len(receipts)
        resolved_models.update(receipt["resolved_model"] for receipt in receipts)
        completions.append({
            "tool_loop_completed": result["tool_call_count"] > 0,
            "target_success": bool(evaluation["target_success"]),
            "non_target_preservation": float(evaluation["non_target_preservation"]),
            "malformed_tool_calls": 0,
        })
    if resolved_models != {ALLOWED_ALIAS}:
        raise RunnerError("Resolved-model identity drifted during capability continuation.")
    gate = capability_gate(completions)
    result: dict[str, Any] = {
        "schema_version": "ace-qwen-capability-continuation-r1-v1",
        "object_id": OBJECT_ID,
        "continuation_id": CONTINUATION_ID,
        "status": gate["verdict"],
        "gate": gate,
        "resolved_model_identities": sorted(resolved_models),
        "valid_capability_measurements": 8,
        "recovered_measurements": 1,
        "newly_executed_measurements": 7,
        "historical_agent_model_requests": int(recovery["historical_provider_request_count"]),
        "continuation_agent_model_requests": continuation_agent_requests,
        "catalog_provider_requests_historical": 1,
        "provider_requests_added_by_measurement_recovery": 0,
        "provider_request_total_across_lineage": (
            1 + int(recovery["historical_provider_request_count"]) + continuation_agent_requests
        ),
        "recovery_artifact_sha256": sha256_file(recovery_path),
        "continuation_ledger_sha256": sha256_file(continuation_ledger_path),
        "f0_backbone": ALLOWED_ALIAS if gate["verdict"] == "CAPABILITY_CALIBRATION_PASS" else None,
        "authority": {
            "f0": False,
            "f0_reason": "Capability continuation does not itself grant F0 execution authority.",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--protected-bundle", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--recovery", type=Path, required=True)
    parser.add_argument("--result-output", type=Path, required=True)
    args = parser.parse_args()
    execute_remaining_capability(
        appworld_root=args.appworld_root,
        protected_bundle=args.protected_bundle,
        runtime_root=args.runtime_root,
        ledger_path=args.ledger,
        recovery_path=args.recovery,
    )
    result = adjudicate_continuation(
        recovery_path=args.recovery,
        continuation_ledger_path=args.ledger,
    )
    args.result_output.parent.mkdir(parents=True, exist_ok=True)
    args.result_output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
