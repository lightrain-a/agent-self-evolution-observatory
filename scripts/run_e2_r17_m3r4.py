#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import ActorRolloutConfig, file_sha256, run_actor_rollout
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_m3r4_execution_guard import (
    MEASUREMENT_AUTH_STATUS,
    PLAN_ROUTE,
    load_json,
    validate_execution_authorization,
)
from research_pipeline.e2_r17_m3r4_execution_plan import (
    REQUIRED_RESOLVED_MODEL,
    STATE_BINDINGS,
    TASK_IDS,
    logical_units,
    sha256_file,
    state_binding_map,
    structural_provider_budget,
    validate_state_bindings,
)
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_mindmemos(root: Path):
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def validate_static_execution_inputs(contract: dict[str, Any]) -> dict[str, Any]:
    validate_state_bindings()
    suite = contract["suite"]
    suite_root = Path(suite["root"])
    if sha256_file(suite_root / "suite_manifest.json") != suite["suite_manifest_sha256"]:
        raise RuntimeError("M3R4 suite manifest drift")
    if sha256_file(suite_root / "r17_split_manifest.json") != suite["split_manifest_sha256"]:
        raise RuntimeError("M3R4 split manifest drift")
    mindmemos = contract["mindmemos"]
    mindmemos_root = Path(mindmemos["root"])
    observed_commit = __import__("subprocess").check_output(
        ["git", "-C", str(mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if observed_commit != mindmemos["commit"]:
        raise RuntimeError("M3R4 MindMemOS commit drift")
    actor_runtime = contract["actor_runtime"]
    actor_python = Path(actor_runtime["python_executable"])
    if not actor_python.is_file():
        raise RuntimeError("M3R4 actor Python missing")
    freeze_path = Path(actor_runtime["freeze_path"])
    if not freeze_path.is_file() or sha256_file(freeze_path) != actor_runtime["freeze_sha256"]:
        raise RuntimeError("M3R4 actor runtime freeze drift")
    qualification_path = _resolve_repo_path(actor_runtime["qualification_path"])
    if not qualification_path.is_file() or sha256_file(qualification_path) != actor_runtime["qualification_sha256"]:
        raise RuntimeError("M3R4 actor runtime qualification drift")
    order_info = contract["logical_unit_order"]
    order_path = _resolve_repo_path(order_info["path"])
    if not order_path.is_file() or sha256_file(order_path) != order_info["sha256"]:
        raise RuntimeError("M3R4 order manifest drift")
    order = load_json(order_path)
    expected_rows = [row.__dict__ for row in logical_units()]
    if order.get("logical_units") != expected_rows:
        raise RuntimeError("M3R4 execution order differs from frozen code/manifest")
    if order.get("logical_units_sha256") != order_info["logical_units_sha256"]:
        raise RuntimeError("M3R4 logical-unit sequence SHA drift")
    state_map = state_binding_map()
    for row in contract["states"]:
        state_id = row["state_id"]
        if state_id not in state_map or row != state_map[state_id].__dict__:
            raise RuntimeError(f"M3R4 state contract binding drift: {state_id}")
    return {
        "suite_root": suite_root,
        "mindmemos_root": mindmemos_root,
        "actor_python": actor_python,
        "order_path": order_path,
        "order": order,
    }


def preflight_without_provider(*, contract: dict[str, Any], authorization: dict[str, Any], output: Path) -> dict[str, Any]:
    static = validate_static_execution_inputs(contract)
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(static["mindmemos_root"])
    del ReactAgentFactory  # import path qualification only
    with tempfile.TemporaryDirectory(prefix="e2-r17-m3r4-preflight-") as temp_dir:
        env = SpreadsheetBenchEnv(static["suite_root"], Path(temp_dir))
        cases = {case.id: case for case in env.load_cases("all")}
    missing = [task_id for task_id in TASK_IDS if task_id not in cases]
    if missing:
        raise RuntimeError(f"M3R4 preflight tasks absent from SpreadsheetBenchEnv: {missing}")
    metadata_rows = load_json(static["suite_root"] / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}
    missing_meta = [task_id for task_id in TASK_IDS if task_id not in metadata]
    if missing_meta:
        raise RuntimeError(f"M3R4 preflight task metadata missing: {missing_meta}")
    run_root = Path(contract["run_root"])
    lease = Path(contract["lineage_lease_path"])
    if run_root.exists() or lease.exists():
        raise RuntimeError("M3R4 preflight requires absent scientific run root and lease")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-actual-path-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_M3R4_ACTUAL_PATH_ZERO_PROVIDER_PREFLIGHT",
        "contract_sha256": authorization["contract_sha256"],
        "authorization_status": authorization["status"],
        "logical_units_checked": 72,
        "tasks_checked": 18,
        "states_checked": 2,
        "actor_replicates_checked": 2,
        "actor_factory_imported": True,
        "spreadsheet_env_cases_resolved": True,
        "provider_budget_ledger_created": False,
        "provider_calls": 0,
        "scientific_outcomes_read": False,
        "run_root_created": False,
        "lineage_lease_created": False,
        "provider_io": False,
        "next_gate": "SEPARATE_MEASUREMENT_AUTHORIZATION_ONLY",
    }
    atomic_json(output, payload)
    return payload


def acquire_lease(path: Path, *, contract_sha: str, authorization_sha: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "scientific_object": "E2-R17-M3R4-FROZEN-STATE-ACTOR-LOCALIZATION-20260904",
        "status": "RUNNING_M3R4",
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "completed_logical_units": 0,
        "scientific_outcomes_read": False,
    }
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return payload


async def run_measurement(*, contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract, authorization = validate_execution_authorization(
        contract_path=contract_path,
        authorization_path=authorization_path,
        stop_before_provider_io=False,
    )
    if authorization.get("status") != MEASUREMENT_AUTH_STATUS:
        raise RuntimeError("M3R4 scientific runner requires measurement authorization")
    static = validate_static_execution_inputs(contract)
    run_root = Path(contract["run_root"])
    lease_path = Path(contract["lineage_lease_path"])
    if run_root.exists() or lease_path.exists():
        raise RuntimeError("M3R4 scientific run root/lease already exists; automatic resume/replay forbidden")
    contract_sha = sha256_file(contract_path)
    authorization_sha = sha256_file(authorization_path)
    lease = acquire_lease(lease_path, contract_sha=contract_sha, authorization_sha=authorization_sha)
    run_root.mkdir(parents=True, exist_ok=False)
    completed_manifest = run_root / "completed_units.jsonl"
    ledger_path = run_root / "provider_budget.sqlite3"
    budget = structural_provider_budget()
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=authorization_sha,
        total_limit=budget["hard_max_provider_calls_structural"],
        per_unit_limit=budget["max_provider_calls_per_logical_unit"],
        allow_create=True,
    )

    fresh_identity = contract["fresh_model_identity"]
    identity_path = _resolve_repo_path(fresh_identity["path"])
    identity = load_json(identity_path)
    model_row = identity["requested_and_resolved"][contract["actor"]["requested_model"]]
    requested_model = str(model_row["requested"])
    resolved_model = str(model_row["resolved"])
    if resolved_model != REQUIRED_RESOLVED_MODEL:
        raise RuntimeError("M3R4 resolved model drift after authorization")

    load_env_file(Path(contract["env_file"]))
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_ROUTE or source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("M3R4 runner refuses non-Ark-Plan route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(static["mindmemos_root"])
    metadata_rows = load_json(static["suite_root"] / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}
    cases_by_unit: dict[str, Any] = {}
    state_map = state_binding_map()
    evaluator_sources = [
        static["mindmemos_root"] / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        static["mindmemos_root"] / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]

    try:
        for unit in logical_units():
            unit_root = run_root / "units" / f"{unit.order_index:02d}_{unit.state_id}_rep{unit.actor_replicate}_{unit.task_id}"
            if unit_root.exists():
                raise RuntimeError(f"M3R4 unit path already exists before execution: {unit.unit_id}")
            # A fresh env object and run root per logical unit is a load-bearing
            # support for the declared within-task/cross-task independence model.
            env = SpreadsheetBenchEnv(static["suite_root"], unit_root)
            cases = {case.id: case for case in env.load_cases("all")}
            case = cases[unit.task_id]
            cases_by_unit[unit.unit_id] = True
            state = state_map[unit.state_id]
            skill_path = Path(state.skill_path)
            skill_source = skill_path.parent
            if file_sha256(skill_path) != state.skill_sha256:
                raise RuntimeError(f"M3R4 skill drift at unit {unit.unit_id}")
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=requested_model,
                required_resolved_model=resolved_model,
                max_output_tokens=contract["actor"]["max_output_tokens"],
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=ledger,
                provider_budget_unit_id=unit.unit_id,
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=contract["actor"]["max_turns"],
                skill_sources=[skill_source],
                python_path=str(static["actor_python"]),
            )
            config = ActorRolloutConfig(
                requested_model=requested_model,
                required_resolved_model=resolved_model,
                max_turns=contract["actor"]["max_turns"],
                skill_source=str(skill_source),
                skill_pre_sha256=state.skill_sha256,
                failure_family=str(metadata[unit.task_id]["primary_failure_family"]),
                experiment_mode="m3r4",
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
            )
            ref = await run_actor_rollout(
                env=env,
                case=case,
                rollout_index=unit.actor_replicate - 1,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )
            trajectory_path = Path(ref.trajectory_path)
            trajectory_payload = load_json(trajectory_path)
            provider_calls = len(trajectory_payload.get("adapter_receipts") or [])
            # No score/effect field is copied into the completion manifest. The
            # persisted trajectory necessarily contains the verifier outcome, but
            # the measurement runner does not aggregate/read it scientifically.
            append_jsonl(
                completed_manifest,
                {
                    "order_index": unit.order_index,
                    "round_index": unit.round_index,
                    "unit_id": unit.unit_id,
                    "task_id": unit.task_id,
                    "state_id": unit.state_id,
                    "actor_replicate": unit.actor_replicate,
                    "state_sha256": state.skill_sha256,
                    "trajectory_ref_path": str(trajectory_path),
                    "trajectory_ref_sha256": sha256_file(trajectory_path),
                    "provider_calls": provider_calls,
                },
            )
            lease["completed_logical_units"] = unit.order_index + 1
            atomic_json(lease_path, lease)

        rows = [json.loads(line) for line in completed_manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
        expected_ids = [unit.unit_id for unit in logical_units()]
        if [row["unit_id"] for row in rows] != expected_ids:
            raise RuntimeError("M3R4 completion manifest order drift")
        snapshot = ledger.snapshot().to_dict()
        lease.update(
            {
                "status": "COMPLETED_M3R4_MEASUREMENT",
                "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "completed_logical_units": 72,
                "scientific_outcomes_read": False,
                "completed_manifest_path": str(completed_manifest),
                "completed_manifest_sha256": sha256_file(completed_manifest),
                "provider_budget": snapshot,
            }
        )
        atomic_json(lease_path, lease)
        summary = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-m3r4-measurement-run-summary",
            "status": "COMPLETED_M3R4_MEASUREMENT_OUTCOME_EMBARGOED",
            "contract_sha256": contract_sha,
            "authorization_sha256": authorization_sha,
            "completed_logical_units": 72,
            "completed_manifest_path": str(completed_manifest),
            "completed_manifest_sha256": sha256_file(completed_manifest),
            "provider_budget": snapshot,
            "scores_read": False,
            "partial_effect_read": False,
            "analysis_authorized": False,
            "python_version": platform.python_version(),
        }
        atomic_json(run_root / "run_summary.json", summary)
        return summary
    except BaseException as exc:
        lease.update(
            {
                "status": "FAIL_CLOSED_M3R4_INCOMPLETE_RUNNER_EXIT",
                "failed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "error_type": type(exc).__name__,
                "scientific_outcomes_read": False,
                "automatic_retry_authorized": False,
            }
        )
        atomic_json(lease_path, lease)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--stop-before-provider-io", action="store_true")
    parser.add_argument("--preflight-output", type=Path)
    args = parser.parse_args()

    contract, authorization = validate_execution_authorization(
        contract_path=args.contract,
        authorization_path=args.authorization,
        stop_before_provider_io=args.stop_before_provider_io,
    )
    if args.stop_before_provider_io:
        if args.preflight_output is None:
            raise SystemExit("--preflight-output is required with --stop-before-provider-io")
        payload = preflight_without_provider(contract=contract, authorization=authorization, output=args.preflight_output)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.preflight_output is not None:
        raise SystemExit("--preflight-output is allowed only with --stop-before-provider-io")
    summary = asyncio.run(run_measurement(contract_path=args.contract, authorization_path=args.authorization))
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
