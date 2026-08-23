from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Protocol

from .ark_provider import ArkResponseStateError
from .posttrain_strategy_intervention import (
    ARM_PRE_STRATEGY,
    ARMS,
    BOUNDARY_MARKER,
    InterventionPrompts,
    compose_segmented_prompts,
)

DEFAULT_MODEL = "deepseek-v4-pro"


class ProviderClient(Protocol):
    def respond(self, prompt: str, **kwargs: Any) -> dict[str, Any]: ...


class ToolExecutor(Protocol):
    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class AgentLoopBudget:
    max_provider_calls: int = 6
    max_output_tokens_per_call: int = 1200
    max_reported_output_tokens: int = 7200

    def validate(self) -> None:
        if self.max_provider_calls < 1:
            raise ValueError("max_provider_calls must be >= 1")
        if self.max_output_tokens_per_call < 1:
            raise ValueError("max_output_tokens_per_call must be >= 1")
        if self.max_reported_output_tokens < self.max_output_tokens_per_call:
            raise ValueError("max_reported_output_tokens must cover at least one call")


TOOLS = [
    {
        "type": "function",
        "name": "inspect_workspace",
        "description": "Inspect a declared file or small state artifact inside the isolated task workspace; task_interface.json documents the bounded training/evaluation interface.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_training",
        "description": (
            "Request one orchestrator-controlled training experiment. The orchestrator, not the model, "
            "executes the GPU process and returns whether a real parameter update was independently verified."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["sft", "rl"]},
                "stage": {"type": "string"},
                "config": {
                    "type": "object",
                    "properties": {
                        "lr": {"type": "number", "exclusiveMinimum": 0.0, "maximum": 0.01},
                        "steps": {"type": "integer", "minimum": 1, "maximum": 2},
                        "examples": {"type": "integer", "minimum": 1, "maximum": 8},
                        "max_seq_tokens": {"type": "integer", "minimum": 64, "maximum": 512},
                        "rl_rollouts": {"type": "integer", "minimum": 1, "maximum": 3},
                        "rl_max_new_tokens": {"type": "integer", "minimum": 16, "maximum": 64},
                    },
                    "additionalProperties": False,
                },
                "rationale": {"type": "string"},
            },
            "required": ["method", "stage", "config", "rationale"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_evaluation",
        "description": "Request the frozen AIME evaluator on a declared local model/checkpoint.",
        "parameters": {
            "type": "object",
            "properties": {
                "model_ref": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 1},
            },
            "required": ["model_ref", "limit"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "finish",
        "description": "Finish the current autonomous segment when no further tool action is needed.",
        "parameters": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
            "additionalProperties": False,
        },
    },
]


def _parse_call_arguments(call: dict[str, Any]) -> dict[str, Any]:
    raw = call.get("arguments")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        parsed = json.loads(raw or "{}")
        if not isinstance(parsed, dict):
            raise ValueError("function arguments must decode to an object")
        return parsed
    raise ValueError("function call arguments missing")


def _validate_tool_arguments(name: str, arguments: dict[str, Any]) -> None:
    """Fail closed on API-visible paths or command-like training configs.

    The paid model is intentionally not a shell agent.  ``inspect_workspace`` is confined to a
    relative task-workspace path, and training configuration is declarative rather than a raw
    command/script surface.  The executor must apply its own allow-list as a second boundary.
    """

    if name == "inspect_workspace":
        raw_path = str(arguments.get("path") or "").strip()
        path = PurePosixPath(raw_path)
        if not raw_path or path.is_absolute() or ".." in path.parts:
            raise ValueError("inspect_workspace path must remain inside the declared task workspace")
    if name == "run_training":
        config = arguments.get("config")
        if not isinstance(config, dict):
            raise ValueError("run_training config must be a declarative object")
        forbidden = {"command", "cmd", "shell", "script", "argv"}
        bad = sorted(forbidden.intersection(str(key).strip().lower() for key in config))
        if bad:
            raise ValueError("raw command/script fields are forbidden in run_training config:" + ",".join(bad))


def _usage_output_tokens(response: dict[str, Any]) -> int:
    usage = response.get("usage") or {}
    if not isinstance(usage, dict):
        return 0
    try:
        return int(usage.get("output_tokens") or 0)
    except (TypeError, ValueError):
        return 0


def _render_turn_prompt(base: InterventionPrompts, transcript: list[dict[str, Any]], phase2_injected: bool) -> str:
    if not transcript:
        return base.phase1_prompt
    rendered = [base.phase1_prompt, "\n## Tool transcript"]
    for row in transcript:
        rendered.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
    if phase2_injected:
        rendered.extend(
            [
                "\n## Verified continuation after parameter-update boundary",
                base.phase2_prompt,
                (
                    "The boundary has been independently verified by the orchestrator. Continue from the current "
                    "checkpoint. Do not claim that a strategy was enacted unless subsequent tool results show it."
                ),
            ]
        )
    else:
        rendered.append(
            "\nThe first independently verified successful parameter update has not occurred yet; continue phase 1."
        )
    return "\n".join(rendered)


def run_deepseek_tool_loop(
    *,
    client: ProviderClient,
    executor: ToolExecutor,
    arm: str,
    base_prompt: str,
    strategy_instruction: str,
    execution_control_instruction: str,
    conflict_free_strategy_instruction: str,
    budget: AgentLoopBudget | None = None,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Run a bounded provider/tool loop suitable for a later DeepSeek L1 probe.

    This function does not itself grant scientific authority.  The model never receives a raw
    server shell.  GPU training and evaluation are requested through orchestrator tools whose
    receipts can independently attest to parameter updates and evaluator identity.
    """

    normalized_arm = str(arm or "").strip().upper()
    if normalized_arm not in ARMS:
        raise ValueError(f"unsupported intervention arm:{normalized_arm}")
    chosen_budget = budget or AgentLoopBudget()
    chosen_budget.validate()
    prompts = compose_segmented_prompts(
        base_prompt=base_prompt,
        arm=normalized_arm,
        strategy_instruction=strategy_instruction,
        execution_control_instruction=execution_control_instruction,
        conflict_free_strategy_instruction=conflict_free_strategy_instruction,
    )

    transcript: list[dict[str, Any]] = []
    provider_receipts: list[dict[str, Any]] = []
    calls = 0
    reported_output_tokens = 0
    boundary_reached = False
    phase2_injected = False
    finished = False
    final_summary = ""

    while calls < chosen_budget.max_provider_calls and not finished:
        prompt = _render_turn_prompt(prompts, transcript, phase2_injected)
        calls += 1
        try:
            response = client.respond(
                prompt,
                model=model,
                max_output_tokens=chosen_budget.max_output_tokens_per_call,
                temperature=0.0,
                tools=TOOLS,
                thinking="disabled",
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError:
            # A provider response object already exists.  Fail closed here so the caller may GET/poll
            # the same receipt; never create another paid generation implicitly.
            raise

        used = _usage_output_tokens(response)
        reported_output_tokens += used
        usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
        provider_receipts.append(
            {
                "response_id": response.get("response_id"),
                "status": response.get("status"),
                "requested_model": response.get("requested_model") or model,
                "resolved_model": response.get("resolved_model") or model,
                "reported_input_tokens": int(usage.get("input_tokens") or 0),
                "reported_output_tokens": used,
                "reported_total_tokens": int(usage.get("total_tokens") or 0),
            }
        )
        if reported_output_tokens > chosen_budget.max_reported_output_tokens:
            raise RuntimeError("DeepSeek tool-loop reported output-token budget exceeded")

        function_calls = response.get("function_calls") or []
        if not function_calls:
            text = str(response.get("text") or "").strip()
            transcript.append({"kind": "assistant_text", "text": text})
            if boundary_reached:
                finished = True
                final_summary = text
                break
            raise RuntimeError("provider returned no tool call before the verified parameter-update boundary")

        for raw_call in function_calls:
            if not isinstance(raw_call, dict):
                raise ValueError("invalid function call payload")
            name = str(raw_call.get("name") or "").strip()
            if name not in {tool["name"] for tool in TOOLS}:
                raise ValueError(f"unsupported tool call:{name}")
            arguments = _parse_call_arguments(raw_call)
            _validate_tool_arguments(name, arguments)
            if name == "finish":
                if not boundary_reached:
                    raise RuntimeError("agent attempted to finish before verified parameter-update boundary")
                final_summary = str(arguments.get("summary") or "").strip()
                transcript.append({"kind": "finish", "arguments": arguments})
                finished = True
                break

            result = executor.execute(name, arguments)
            if not isinstance(result, dict):
                raise ValueError("tool executor must return a dict receipt")
            transcript.append(
                {
                    "kind": "tool_result",
                    "tool": name,
                    "arguments": arguments,
                    "result": result,
                }
            )
            if name == "run_training" and result.get("parameter_update_verified") is True:
                boundary_reached = True
                if not phase2_injected:
                    phase2_injected = True
                    transcript.append(
                        {
                            "kind": "boundary",
                            "marker": BOUNDARY_MARKER,
                            "verification": "orchestrator_parameter_update_verified",
                        }
                    )
                    # Freeze the first update as the intervention boundary.  Do not process a second
                    # model-selected tool call from the same pre-boundary provider response.
                    break

    stop_reason = "finished" if finished else "provider_call_budget_exhausted"
    if not finished and calls >= chosen_budget.max_provider_calls:
        raise RuntimeError("DeepSeek tool-loop provider-call budget exhausted")

    return {
        "arm": normalized_arm,
        "model": model,
        "provider_calls": calls,
        "reported_output_tokens": reported_output_tokens,
        "boundary_reached": boundary_reached,
        "phase2_injected": phase2_injected,
        "finished": finished,
        "stop_reason": stop_reason,
        "final_summary": final_summary,
        "transcript": transcript,
        "provider_receipts": provider_receipts,
        "scientific_authority": False,
        "paid_probe_authorized_by_this_function": False,
        "pre_strategy_present_in_initial_prompt": normalized_arm == ARM_PRE_STRATEGY,
    }
