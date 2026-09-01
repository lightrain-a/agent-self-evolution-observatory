from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    DEFAULT_BASE_URL,
    OBJECT_ID,
    PROVIDER_ID,
    REQUESTED_MODEL,
    AppendOnlyLedger,
    EpisodeUnit,
    RunnerError,
    TypicalResponsesClient,
    canonical_bytes,
    run_episode,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec
from research_pipeline.config import DEFAULT_ENV_FILE, load_env_file

CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
CAPABILITY_TOOL_CAP = 12
M1_PATH = Path("generated/agent-constraint-externality-m1-runner-qualification-v1-20260901.json")


def enumerate_capability_units(model_id: str = REQUESTED_MODEL) -> list[EpisodeUnit]:
    units = [
        EpisodeUnit(
            namespace="capability",
            key=(model_id, family_id, repeat),
            stage="CAPABILITY_CALIBRATION",
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in CAPABILITY_FAMILIES
        for repeat in REPEATS
    ]
    if len(units) != 8 or len({unit.unit_id for unit in units}) != 8:
        raise RunnerError("Capability enumeration is not exactly eight unique units.")
    return units


def resolve_model_id(
    available_model_ids: set[str], *, snapshot_unavailable: bool
) -> str:
    if REQUESTED_MODEL in available_model_ids:
        return REQUESTED_MODEL
    if snapshot_unavailable and ALLOWED_ALIAS in available_model_ids:
        return ALLOWED_ALIAS
    raise RunnerError("Frozen Qwen snapshot/allowed alias is unavailable; STOP.")


def capture_model_snapshot(
    *,
    api_key: str,
    base_url: str,
    opener: Any = urllib.request.urlopen,
) -> dict[str, Any]:
    if not api_key.strip():
        raise RunnerError("AA_API_KEY is not configured.")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": "Bearer " + api_key},
        method="GET",
    )
    try:
        with opener(request, timeout=60.0) as response:
            raw = response.read()
        payload = json.loads(raw.decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RunnerError(
            f"Model catalog transport failed without retry: {type(exc).__name__}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RunnerError("Model catalog parse failed without retry.") from exc
    data = payload.get("data", [])
    if not isinstance(data, list):
        raise RunnerError("Model catalog lacked a data list.")
    model_ids = {
        item.get("id") for item in data
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    snapshot_unavailable = REQUESTED_MODEL not in model_ids
    resolved_model = resolve_model_id(
        model_ids, snapshot_unavailable=snapshot_unavailable
    )
    return {
        "schema_version": "ace-qwen-provider-model-snapshot-v1",
        "object_id": OBJECT_ID,
        "provider": PROVIDER_ID,
        "base_url": base_url.rstrip("/"),
        "catalog_provider_request_count": 1,
        "max_retries": 0,
        "requested_model": REQUESTED_MODEL,
        "requested_model_available": REQUESTED_MODEL in model_ids,
        "allowed_alias": ALLOWED_ALIAS,
        "allowed_alias_available": ALLOWED_ALIAS in model_ids,
        "snapshot_unavailable": snapshot_unavailable,
        "resolved_request_model": resolved_model,
        "catalog_response_sha256": sha256_value(payload),
        "catalog_model_count": len(model_ids),
        "secrets_persisted": False,
    }


def capability_gate(completions: list[dict[str, Any]]) -> dict[str, Any]:
    if len(completions) != 8:
        raise RunnerError("Capability adjudication requires all eight terminal completions.")
    tool_loop_rate = sum(item["tool_loop_completed"] for item in completions) / 8
    target_rate = sum(item["target_success"] for item in completions) / 8
    nt_values = [item["non_target_preservation"] for item in completions]
    nt_rate = sum(nt_values) / len(nt_values)
    malformed = sum(item.get("malformed_tool_calls", 0) for item in completions)
    if malformed:
        verdict = "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP"
    elif tool_loop_rate < 0.75 or target_rate < 0.50 or nt_rate < 0.85:
        verdict = "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP"
    elif target_rate > 0.875:
        verdict = "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP"
    else:
        verdict = "CAPABILITY_CALIBRATION_PASS"
    return {
        "object_id": OBJECT_ID,
        "verdict": verdict,
        "tool_loop_completion_rate": tool_loop_rate,
        "target_success_rate": target_rate,
        "non_target_preservation_rate": nt_rate,
        "malformed_tool_call_count": malformed,
        "thresholds": {
            "tool_loop_completion_min": 0.75,
            "target_success_min": 0.50,
            "target_success_max": 0.875,
            "non_target_preservation_min": 0.85,
            "malformed_tool_calls_required": 0,
        },
    }


def require_m1_pass(path: Path = M1_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "M1_RUNNER_QUALIFICATION_PASS":
        raise RunnerError("Real provider use requires M1_RUNNER_QUALIFICATION_PASS.")
    if payload.get("real_scientific_provider_calls") != 0:
        raise RunnerError("M1 artifact crossed the zero-real-call boundary.")
    return payload


def adjudicate_capability_ledger(
    *,
    ledger_path: Path,
    model_snapshot: dict[str, Any],
) -> dict[str, Any]:
    resolved_model = model_snapshot["resolved_request_model"]
    ledger = AppendOnlyLedger(ledger_path)
    units = enumerate_capability_units(resolved_model)
    states = ledger.states()
    unknown = [
        unit_id for unit_id, state in states.items()
        if state == "UNKNOWN_AFTER_DISPATCH"
    ]
    if unknown:
        raise RunnerError(
            "Capability contains UNKNOWN_AFTER_DISPATCH; manual adjudication required."
        )
    rows = ledger.rows()
    failures = [row for row in rows if row["event"] == "FAILURE"]
    completion_rows = [row for row in rows if row["event"] == "COMPLETION"]
    if failures:
        gate = {
            "object_id": OBJECT_ID,
            "verdict": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
            "failure_units": [row["unit_id"] for row in failures],
        }
    else:
        ledger.assert_all_terminal(units)
        if len(completion_rows) != 8:
            raise RunnerError("Capability ledger must contain eight completions.")
        completions: list[dict[str, Any]] = []
        resolved_identities: set[str] = set()
        provider_requests = 0
        for row in completion_rows:
            result = row["result"]
            evaluation = result["evaluation"]
            receipts = row["provider_receipts"]
            provider_requests += len(receipts)
            resolved_identities.update(receipt["resolved_model"] for receipt in receipts)
            completions.append({
                "tool_loop_completed": result["tool_call_count"] > 0,
                "target_success": bool(evaluation["target_success"]),
                "non_target_preservation": float(
                    evaluation["non_target_preservation"]
                ),
                "malformed_tool_calls": 0,
            })
        if len(resolved_identities) != 1:
            raise RunnerError("Provider resolved-model identity drifted across capability.")
        gate = capability_gate(completions)
        gate["resolved_model_identities"] = sorted(resolved_identities)
        gate["agent_model_request_count"] = provider_requests
    result = {
        "schema_version": "ace-qwen-capability-adjudication-v1",
        "object_id": OBJECT_ID,
        "status": gate["verdict"],
        "gate": gate,
        "provider_snapshot": model_snapshot,
        "agent_episode_count": 8,
        "catalog_provider_request_count": 1,
        "updater_model_request_count": 0,
        "provider_request_total": (
            1 + int(gate.get("agent_model_request_count", 0))
        ),
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "provider_side_deterministic_replay_guaranteed": False,
        "ledger_sha256": sha256_file(ledger_path),
        "f0_backbone": (
            resolved_model
            if gate["verdict"] == "CAPABILITY_CALIBRATION_PASS"
            else None
        ),
        "authority": {
            "f0": gate["verdict"] == "CAPABILITY_CALIBRATION_PASS",
            "second_model": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "p1": False,
            "method": False,
            "paper_claim": False,
        },
    }
    result["content_sha256"] = sha256_value(result)
    return result


def write_capability_artifacts(
    result: dict[str, Any],
    *,
    result_path: Path,
    snapshot_path: Path,
    manifest_path: Path,
) -> None:
    for path, payload in ((snapshot_path, result["provider_snapshot"]), (result_path, result)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    manifest = {
        "schema_version": "ace-qwen-capability-manifest-v1",
        "object_id": OBJECT_ID,
        "status": result["status"],
        "files": {
            str(path): {"sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in (snapshot_path, result_path)
        },
        "provider_request_total": result["provider_request_total"],
        "agent_episode_count": result["agent_episode_count"],
        "updater_model_request_count": 0,
        "authority": result["authority"],
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def execute_capability(
    *,
    appworld_root: Path,
    protected_bundle: Path,
    runtime_root: Path,
    ledger_path: Path,
    resolved_model: str,
    snapshot_unavailable: bool,
) -> None:
    require_m1_pass()
    load_env_file(DEFAULT_ENV_FILE)
    if resolved_model == ALLOWED_ALIAS and not snapshot_unavailable:
        raise RunnerError("Alias requires persisted proof that snapshot is unavailable.")
    if resolved_model not in {REQUESTED_MODEL, ALLOWED_ALIAS}:
        raise RunnerError("Model replacement is forbidden.")
    api_key = os.getenv("AA_API_KEY", "")
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    provider = TypicalResponsesClient(api_key, base_url)
    spec = load_protected_spec(protected_bundle)
    families = {family["family_id"]: family for family in spec["families"]}
    ledger = AppendOnlyLedger(ledger_path)
    units = enumerate_capability_units(resolved_model)
    for unit in units:
        family = families[unit.family_id]
        arm = next(arm for arm in family["arms"] if arm["coupling_level"] == "LOW")
        task_id = "acecap" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(
            appworld_root, unit_root, family=family, arm=arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-capability",
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
                model=resolved_model,
                base_url=base_url,
                result_evaluator=lambda arm=arm, world=world: world.save_and_evaluate(arm),
            )
        finally:
            world.close()
    ledger.assert_all_terminal(units)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--protected-bundle", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--model-snapshot-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    args = parser.parse_args()

    require_m1_pass()
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.getenv("AA_API_KEY", "")
    base_url = os.getenv("AA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    snapshot = capture_model_snapshot(
        api_key=api_key,
        base_url=base_url,
    )
    args.model_snapshot_output.parent.mkdir(parents=True, exist_ok=True)
    args.model_snapshot_output.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    resolved_model = snapshot["resolved_request_model"]
    try:
        execute_capability(
            appworld_root=args.appworld_root,
            protected_bundle=args.protected_bundle,
            runtime_root=args.runtime_root,
            ledger_path=args.ledger,
            resolved_model=resolved_model,
            snapshot_unavailable=bool(snapshot["snapshot_unavailable"]),
        )
    except Exception:
        if not args.ledger.exists():
            raise
        states = AppendOnlyLedger(args.ledger).states()
        if (
            any(state == "UNKNOWN_AFTER_DISPATCH" for state in states.values())
            or "FAILURE" not in states.values()
        ):
            raise
    result = adjudicate_capability_ledger(
        ledger_path=args.ledger,
        model_snapshot=snapshot,
    )
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    write_capability_artifacts(
        result,
        result_path=args.result_output,
        snapshot_path=args.model_snapshot_output,
        manifest_path=args.manifest_output,
    )
    print(json.dumps({
        "status": result["status"],
        "provider": PROVIDER_ID,
        "model": resolved_model,
        "episode_count": result["agent_episode_count"],
        "provider_request_total": result["provider_request_total"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
