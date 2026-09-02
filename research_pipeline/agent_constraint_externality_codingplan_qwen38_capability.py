from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
from research_pipeline.agent_constraint_externality_codingplan_qwen38_provider import (
    ATOMCODE_PROVIDER_PROFILE,
    BRIDGE_SCHEMA,
    CONTEXT_WINDOW,
    MAX_OUTPUT_TOKENS,
    PROVIDER_ID,
    RESOLVED_MODEL,
    RETRY_MAX_ATTEMPTS,
    SAMPLING_CONTROL,
    AtomCodeCodingPlanQwen38Client,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    AppendOnlyLedger,
    EpisodeUnit,
    RunnerError,
    function_calls,
    run_episode,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
ACTIVE_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V4_CONTRACT = GENERATED / "agent-constraint-externality-capability-substrate-v4-contract-20260902.json"
PLUS_R5 = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r5-partial-20260902.json"
DEEPSEEK_R4_VOID = GENERATED / "agent-constraint-externality-codingplan-deepseek-a2-r4-schedule-wakeup-void-20260902.json"
PROVIDER_QUAL = GENERATED / "agent-constraint-externality-codingplan-qwen38-provider-qualification-c1-20260902.json"
ADDENDUM = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-addendum-c1-20260902.json"
RESULT = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-result-c1-20260902.json"
EXECUTION_ID = "CODINGPLAN-QWEN38-27B-CAPABILITY-C1"
CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
TOOL_CAP = 16
TOOL_CAP_FAILURE_MESSAGE = "Tool-call cap exceeded."


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def units() -> list[EpisodeUnit]:
    rows = [
        EpisodeUnit(
            namespace="capability",
            key=(RESOLVED_MODEL, family_id, repeat),
            stage="CODINGPLAN_QWEN38_CAPABILITY_C1",
            family_id=family_id,
            repeat=repeat,
        )
        for family_id in CAPABILITY_FAMILIES
        for repeat in REPEATS
    ]
    if len(rows) != 8 or len({row.unit_id for row in rows}) != 8:
        raise RunnerError("CodingPlan Qwen38 C1 requires exactly eight unique capability units.")
    return rows


def build_provider_qualification(*, runtime_root: Path) -> dict[str, Any]:
    provider = AtomCodeCodingPlanQwen38Client(
        config_path=runtime_root / "atomcode-codingplan-config.toml",
        workdir=runtime_root / "atomcode-empty-workdir",
        timeout_seconds=180,
    )
    tools = [
        {
            "type": "function",
            "name": "read_alpha",
            "description": "Read synthetic alpha state.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "type": "function",
            "name": "read_beta",
            "description": "Read synthetic beta state.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    ]
    receipt = provider.create_response(
        model=RESOLVED_MODEL,
        instructions="Complete the task using tools. Preserve unrelated state.",
        input_items=[
            {
                "role": "user",
                "content": (
                    "Synthetic provider qualification only. Read both independent alpha and beta states now. "
                    "Do not finish until both proposed actions are returned in the same decision."
                ),
            }
        ],
        tools=tools,
        temperature=0.0,
    )
    calls = function_calls(receipt.output)
    names = [call["name"] for call in calls]
    if names != ["read_alpha", "read_beta"]:
        raise RunnerError(
            "CodingPlan Qwen38 provider qualification requires two parallel synthetic actions."
        )
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-provider-qualification-c1-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_QWEN38_PROVIDER_QUALIFICATION_PASS",
        "provider": PROVIDER_ID,
        "atomcode_provider_profile": ATOMCODE_PROVIDER_PROFILE,
        "resolved_model": RESOLVED_MODEL,
        "context_window": CONTEXT_WINDOW,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "retry_max_attempts": RETRY_MAX_ATTEMPTS,
        "sampling_control": SAMPLING_CONTROL,
        "bridge_schema": BRIDGE_SCHEMA,
        "live_probe": {
            "codingplan_requests": 1,
            "parallel_action_count": len(calls),
            "action_names": names,
            "native_atomcode_tool_calls_observed": 0,
            "scientific_episode": False,
            "usage": receipt.usage,
            "receipt": receipt.safe_dict(),
            "receipt_sha256": sha256_value(receipt.safe_dict()),
        },
        "scientific_outcomes_observed": 0,
        "f0_authorized": False,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def build_addendum(provider_qualification: dict[str, Any]) -> dict[str, Any]:
    v4 = read_json(V4_CONTRACT)
    plus = read_json(PLUS_R5)
    deepseek_void = read_json(DEEPSEEK_R4_VOID)
    if v4.get("status") != "CAPABILITY_SUBSTRATE_V4_TOOL_BUDGET_QUALIFIED":
        raise RunnerError("CodingPlan Qwen38 C1 requires qualified AppWorld substrate V4.")
    if plus.get("status") != "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP":
        raise RunnerError("CodingPlan Qwen38 C1 requires sealed Qwen3.7-Plus ceiling result.")
    if deepseek_void.get("status") != "CODINGPLAN_DEEPSEEK_A2_R4_VOID_ATOMCODE_SCHEDULE_WAKEUP_LEAK":
        raise RunnerError("CodingPlan Qwen38 C1 requires sealed DeepSeek bridge-interface void.")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-addendum-c1-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": "CODINGPLAN_QWEN38_CAPABILITY_C1_AUTHORIZED",
        "selection_boundary": "POST_QWEN37PLUS_CEILING_AND_CODINGPLAN_DEEPSEEK_INTERFACE_VOID",
        "selection_reason": [
            "USER_REQUESTED_CODINGPLAN_PROVIDER_EVALUATION",
            "QWEN38_27B_IS_SMALLER_THAN_CEILING_QWEN37PLUS_TIER",
            "LIVE_JSON_ACTION_BRIDGE_QUALIFIED_WITH_ZERO_NATIVE_ATOMCODE_TOOL_CALLS",
            "262K_CONTEXT_AND_65K_OUTPUT_ALLOW_LARGE_TOOL_SCHEMA_PER_REQUEST",
            "REQUEST_LIMITED_PLAN_FAVORS_PARALLEL_ACTIONS_PER_MODEL_TURN",
            "NOT_SELECTED_FOR_EXPECTED_EXTERNALITY_EFFECT",
        ],
        "provider_qualification_sha256": provider_qualification["content_sha256"],
        "deepseek_interface_void_sha256": sha256_file(DEEPSEEK_R4_VOID),
        "active_substrate": {
            "bundle_path": str(ACTIVE_BUNDLE.relative_to(ROOT)),
            "bundle_sha256": sha256_file(ACTIVE_BUNDLE),
            "v4_contract_sha256": sha256_file(V4_CONTRACT),
        },
        "model": {
            "provider": PROVIDER_ID,
            "atomcode_provider_profile": ATOMCODE_PROVIDER_PROFILE,
            "resolved_model": RESOLVED_MODEL,
            "context_window": CONTEXT_WINDOW,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "retry_max_attempts": RETRY_MAX_ATTEMPTS,
            "sampling_control": SAMPLING_CONTROL,
            "bridge_schema": BRIDGE_SCHEMA,
        },
        "panel": {
            "family_ids": list(CAPABILITY_FAMILIES),
            "repeats": list(REPEATS),
            "episodes": 8,
            "tool_call_cap": TOOL_CAP,
            "reuse_other_model_measurements": False,
        },
        "gate": {
            "tool_loop_completion_min": 0.75,
            "target_success_min": 0.50,
            "target_success_max": 0.875,
            "non_target_preservation_min": 0.85,
            "malformed_tool_calls_required": 0,
        },
        "request_efficiency": {
            "one_atomcode_invocation_must_equal_one_codingplan_request": True,
            "parallel_independent_tool_calls_encouraged_per_turn": True,
            "token_budget_is_not_primary_constraint": True,
            "five_hour_request_limit_user_reported": 500,
        },
        "authority": {
            "capability_c1": True,
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed": 0,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def append_toolcap(
    path: Path, unit: EpisodeUnit, evaluation: dict[str, Any], receipts: int
) -> None:
    row: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-toolcap-c1-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "unit_id": unit.unit_id,
        "family_id": unit.family_id,
        "classification": "CAPABILITY_TOOL_LOOP_INCOMPLETE_AT_FROZEN_CAP",
        "tool_loop_completed": False,
        "tool_call_cap": TOOL_CAP,
        "provider_receipt_count": receipts,
        "evaluation": evaluation,
        "retry": False,
        "replacement": False,
    }
    row["content_sha256"] = sha256_value(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def toolcap_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def execute(
    *, appworld_root: Path, runtime_root: Path, ledger_path: Path, toolcap_path: Path
) -> None:
    spec = load_protected_spec(ACTIVE_BUNDLE)
    families = {row["family_id"]: row for row in spec["families"]}
    provider = AtomCodeCodingPlanQwen38Client(
        config_path=runtime_root / "atomcode-codingplan-config.toml",
        workdir=runtime_root / "atomcode-empty-workdir",
        timeout_seconds=240,
    )
    ledger = AppendOnlyLedger(ledger_path)
    states = ledger.states()
    for unit in units():
        state = states.get(unit.unit_id)
        if state is not None:
            raise RunnerError(
                f"CodingPlan Qwen38 C1 refuses replay of existing state {state}: {unit.unit_id}"
            )
        family = families[unit.family_id]
        arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        task_id = "acecpq38" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
        unit_root = runtime_root / "worlds" / unit.unit_id.replace(":", "_").replace("|", "_")
        materialized = prepare_appworld_runtime_root(
            appworld_root, unit_root, family=family, arm=arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-codingplan-qwen38-capability-c1",
            seed=3100 + int(unit.repeat or 0),
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
                    model=RESOLVED_MODEL,
                    base_url=provider.base_url,
                    result_evaluator=lambda arm=arm, world=world: world.save_and_evaluate(arm),
                    max_tool_calls=TOOL_CAP,
                )
            except RunnerError as exc:
                if str(exc) != TOOL_CAP_FAILURE_MESSAGE:
                    raise
                evaluation = world.save_and_evaluate(arm)
                failure = next(
                    row
                    for row in reversed(ledger.rows())
                    if row["unit_id"] == unit.unit_id and row["event"] == "FAILURE"
                )
                append_toolcap(
                    toolcap_path,
                    unit,
                    evaluation,
                    len(failure.get("provider_receipts", [])),
                )
        finally:
            world.close()
        states = ledger.states()
    ledger.assert_all_terminal(units())


def adjudicate(*, ledger_path: Path, toolcap_path: Path) -> dict[str, Any]:
    ledger = AppendOnlyLedger(ledger_path)
    ledger.assert_all_terminal(units())
    rows = ledger.rows()
    terminals = [row for row in rows if row["event"] in {"COMPLETION", "FAILURE"}]
    if len(terminals) != 8:
        raise RunnerError("CodingPlan Qwen38 C1 adjudication requires eight terminal units.")
    toolcaps = {row["unit_id"]: row for row in toolcap_rows(toolcap_path)}
    measurements: list[dict[str, Any]] = []
    requests = 0
    input_tokens = 0
    output_tokens = 0
    cached_tokens = 0
    completions = 0
    malformed = 0
    for row in terminals:
        receipts = row.get("provider_receipts", [])
        requests += len(receipts)
        for receipt in receipts:
            if receipt.get("provider") != PROVIDER_ID or receipt.get("resolved_model") != RESOLVED_MODEL:
                raise RunnerError("CodingPlan Qwen38 provider/model identity drifted.")
            usage = receipt.get("usage", {})
            input_tokens += int(usage.get("input_tokens", 0))
            output_tokens += int(usage.get("output_tokens", 0))
            cached_tokens += int(usage.get("cached_tokens", 0))
        if row["event"] == "COMPLETION":
            evaluation = row["result"]["evaluation"]
            measurements.append(
                {
                    "tool_loop_completed": True,
                    "target_success": bool(evaluation["target_success"]),
                    "non_target_preservation": float(evaluation["non_target_preservation"]),
                    "malformed_tool_calls": 0,
                }
            )
            completions += 1
        else:
            if row.get("failure_class") == "MalformedToolCallError":
                malformed += 1
            if row["unit_id"] not in toolcaps:
                raise RunnerError(
                    "CodingPlan Qwen38 non-toolcap failure requires interface adjudication."
                )
            evaluation = toolcaps[row["unit_id"]]["evaluation"]
            measurements.append(
                {
                    "tool_loop_completed": False,
                    "target_success": bool(evaluation["target_success"]),
                    "non_target_preservation": float(evaluation["non_target_preservation"]),
                    "malformed_tool_calls": 0,
                }
            )
    gate = capability_gate(measurements)
    result: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-result-c1-v1",
        "object_id": OBJECT_ID,
        "execution_id": EXECUTION_ID,
        "status": gate["verdict"],
        "gate": gate,
        "provider": PROVIDER_ID,
        "resolved_model": RESOLVED_MODEL,
        "sampling_control": SAMPLING_CONTROL,
        "bridge_schema": BRIDGE_SCHEMA,
        "valid_capability_measurements": 8,
        "completion_count": completions,
        "tool_cap_incomplete_count": len(toolcaps),
        "malformed_tool_call_failures": malformed,
        "codingplan_request_total": requests,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
        },
        "request_efficiency": {
            "requests_per_episode": requests / 8.0,
            "five_hour_request_limit_user_reported": 500,
            "fraction_of_one_window": requests / 500.0,
        },
        "scientific_outcomes_observed": 0,
        "f0_executed": False,
        "authority": {
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "paper_claim": False,
        },
        "ledger_sha256": sha256_file(ledger_path),
        "toolcap_sha256": sha256_file(toolcap_path) if toolcap_path.is_file() else None,
        "provider_qualification_sha256": sha256_file(PROVIDER_QUAL),
        "addendum_sha256": sha256_file(ADDENDUM),
        "deepseek_interface_void_sha256": sha256_file(DEEPSEEK_R4_VOID),
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--appworld-root",
        type=Path,
        default=ROOT / "cache/substrates/appworld-official-20260831",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=ROOT / "runtimes/agent-constraint-externality-codingplan-qwen38-capability-c1-20260902",
    )
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--toolcap-ledger", type=Path)
    parser.add_argument("--result-output", type=Path, default=RESULT)
    args = parser.parse_args()
    if args.prepare:
        runtime_root = args.runtime_root
        if PROVIDER_QUAL.exists() or ADDENDUM.exists():
            raise RunnerError("CodingPlan Qwen38 C1 prepare artifacts already exist; refusing overwrite.")
        provider_qualification = build_provider_qualification(
            runtime_root=runtime_root / "provider-qualification"
        )
        addendum = build_addendum(provider_qualification)
        write_json(PROVIDER_QUAL, provider_qualification)
        write_json(ADDENDUM, addendum)
        print(
            json.dumps(
                {
                    "provider_status": provider_qualification["status"],
                    "addendum_status": addendum["status"],
                    "model": RESOLVED_MODEL,
                    "context_window": CONTEXT_WINDOW,
                    "max_output_tokens": MAX_OUTPUT_TOKENS,
                    "retry_max_attempts": RETRY_MAX_ATTEMPTS,
                    "probe_requests": provider_qualification["live_probe"]["codingplan_requests"],
                },
                sort_keys=True,
            )
        )
        return
    if args.execute:
        if not PROVIDER_QUAL.is_file() or not ADDENDUM.is_file():
            raise RunnerError(
                "CodingPlan Qwen38 C1 execution requires frozen provider qualification and addendum."
            )
        qual = read_json(PROVIDER_QUAL)
        addendum = read_json(ADDENDUM)
        if qual.get("status") != "CODINGPLAN_QWEN38_PROVIDER_QUALIFICATION_PASS":
            raise RunnerError("CodingPlan Qwen38 provider qualification is not PASS.")
        if addendum.get("status") != "CODINGPLAN_QWEN38_CAPABILITY_C1_AUTHORIZED":
            raise RunnerError("CodingPlan Qwen38 C1 addendum is not authorized.")
        runtime_root = args.runtime_root
        ledger_path = args.ledger or runtime_root / "ledger.jsonl"
        toolcap_path = args.toolcap_ledger or runtime_root / "toolcap-measurements.jsonl"
        execute(
            appworld_root=args.appworld_root,
            runtime_root=runtime_root,
            ledger_path=ledger_path,
            toolcap_path=toolcap_path,
        )
        result = adjudicate(ledger_path=ledger_path, toolcap_path=toolcap_path)
        write_json(args.result_output, result)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "codingplan_requests": result["codingplan_request_total"],
                    "requests_per_episode": result["request_efficiency"]["requests_per_episode"],
                    "f0_authorized": False,
                },
                sort_keys=True,
            )
        )
        return
    raise SystemExit("Choose --prepare or --execute")


if __name__ == "__main__":
    main()
