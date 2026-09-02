from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from research_pipeline.agent_constraint_externality_codingplan_provider import (
    ACTION_POLICY_INSTRUCTIONS,
    SYSTEM_PROMPT,
    _extract_json_object,
    _message_text_from_jsonl,
    _tool_prompt,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    MalformedToolCallError,
    ProviderCallError,
    ProviderReceipt,
    sha256_value,
)

PROVIDER_ID = "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_HEADLESS_V1"
PROVIDER_BASE_URL = "https://llm-api.atomgit.com/v1"
BRIDGE_SCHEMA = "ace-atomcode-json-action-bridge-v2"
ATOMCODE_PROVIDER_PROFILE = "AtomGit-qwen3.8-27b"
RESOLVED_MODEL = "qwen3.8-27b"
CONTEXT_WINDOW = 262144
MAX_OUTPUT_TOKENS = 65536
RETRY_MAX_ATTEMPTS = 1
SAMPLING_CONTROL = "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"


def write_experiment_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f'default_provider = "{ATOMCODE_PROVIDER_PROFILE}"',
                f'default_model = "{ATOMCODE_PROVIDER_PROFILE}"',
                'auto_update = false',
                'lsp.enabled = false',
                'subagent.enabled = false',
                'tools.todo.enabled = false',
                '',
                '[provider_accounts.AtomGit]',
                'provider = "openai"',
                f'base_url = "{PROVIDER_BASE_URL}"',
                '',
                f'[models."{ATOMCODE_PROVIDER_PROFILE}"]',
                'account = "AtomGit"',
                f'model = "{RESOLVED_MODEL}"',
                f'context_window = {CONTEXT_WINDOW}',
                f'max_tokens = {MAX_OUTPUT_TOKENS}',
                f'retry_max_attempts = {RETRY_MAX_ATTEMPTS}',
                'system_prompt = ' + json.dumps(SYSTEM_PROMPT, ensure_ascii=False),
                '',
                '[coding]',
                'max_rounds = 1',
                '',
                '[network.proxy]',
                'mode = "follow_system"',
                '',
            ]
        ),
        encoding="utf-8",
    )


class AtomCodeCodingPlanQwen38Client:
    provider_id = PROVIDER_ID
    base_url = "atomcode://atomgit-codingplan/qwen3.8-27b"

    def __init__(
        self,
        *,
        config_path: Path,
        workdir: Path,
        atomcode_binary: str = "atomcode",
        timeout_seconds: float = 180.0,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.config_path = config_path
        self.workdir = workdir
        self.atomcode_binary = atomcode_binary
        self.timeout_seconds = timeout_seconds
        self._runner = runner
        self.request_count = 0
        write_experiment_config(config_path)
        workdir.mkdir(parents=True, exist_ok=True)

    def create_response(
        self,
        *,
        model: str,
        instructions: str,
        input_items: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        temperature: float,
    ) -> ProviderReceipt:
        del temperature
        if model != RESOLVED_MODEL:
            raise ProviderCallError(f"CodingPlan Qwen model replacement forbidden: {model}")
        prompt, alias_to_name = _tool_prompt(
            instructions=instructions,
            input_items=input_items,
            tools=tools,
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            prefix="ace-codingplan-qwen38-",
            delete=False,
        ) as handle:
            prompt_path = Path(handle.name)
            handle.write(prompt)
        command = [
            self.atomcode_binary,
            "--config",
            str(self.config_path),
            "--provider",
            ATOMCODE_PROVIDER_PROFILE,
            "--no-tools",
            "--ephemeral",
            "--no-telemetry",
            "--output-format",
            "jsonl",
            "-C",
            str(self.workdir),
            "--prompt-file",
            str(prompt_path),
        ]
        self.request_count += 1
        started_ns = time.time_ns()
        try:
            completed = self._runner(
                command,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise ProviderCallError(
                f"CodingPlan Qwen transport failed without retry: {type(exc).__name__}"
            ) from exc
        finally:
            prompt_path.unlink(missing_ok=True)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout)[-1000:]
            raise ProviderCallError(
                "CodingPlan Qwen AtomCode invocation failed without retry: "
                + detail.replace("\n", " ")[:800]
            )
        text, metadata = _message_text_from_jsonl(completed.stdout)
        parsed = _extract_json_object(text)
        output: list[dict[str, Any]] = []
        decision = parsed.get("decision")
        if decision == "act":
            calls = parsed.get("actions")
            if not isinstance(calls, list) or not calls:
                raise MalformedToolCallError(
                    "CodingPlan Qwen decision=act must contain a non-empty actions list."
                )
            for index, call in enumerate(calls):
                if (
                    not isinstance(call, dict)
                    or not isinstance(call.get("action_id"), str)
                    or not isinstance(call.get("arguments"), dict)
                ):
                    raise MalformedToolCallError(
                        "CodingPlan Qwen action must contain action_id:string and arguments:object."
                    )
                action_id = call["action_id"]
                if action_id not in alias_to_name:
                    raise MalformedToolCallError(
                        f"CodingPlan Qwen returned unknown action alias: {action_id}"
                    )
                output.append(
                    {
                        "type": "function_call",
                        "name": alias_to_name[action_id],
                        "arguments": json.dumps(
                            call["arguments"], ensure_ascii=False, sort_keys=True
                        ),
                        "call_id": f"cpq38-{self.request_count}-{index + 1}",
                    }
                )
        elif decision == "finish":
            message = parsed.get("message", "")
            if not isinstance(message, str):
                raise MalformedToolCallError(
                    "CodingPlan Qwen final message must be a string."
                )
            output.append(
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": message}],
                }
            )
        else:
            raise MalformedToolCallError(
                "CodingPlan Qwen bridge decision must be act or finish."
            )
        usage_row = metadata["usage"]
        started = metadata["started"]
        started_model = str(started.get("model", ""))
        if started_model not in {RESOLVED_MODEL, ATOMCODE_PROVIDER_PROFILE}:
            raise ProviderCallError(
                f"CodingPlan Qwen resolved model drift: {started_model}"
            )
        input_tokens = int(usage_row.get("prompt_tokens", 0))
        output_tokens = int(usage_row.get("completion_tokens", 0))
        total_tokens = int(usage_row.get("total_tokens", 0)) or (
            input_tokens + output_tokens
        )
        return ProviderReceipt(
            response_id=f"atomcode-qwen38-{started_ns}",
            requested_model=model,
            resolved_model=RESOLVED_MODEL,
            provider=PROVIDER_ID,
            base_url=self.base_url,
            output=output,
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cached_tokens": int(usage_row.get("cached_tokens", 0)),
                "codingplan_requests": 1,
            },
            capability_snapshot={
                "atomcode_provider_profile": ATOMCODE_PROVIDER_PROFILE,
                "resolved_model": RESOLVED_MODEL,
                "context_window": CONTEXT_WINDOW,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "retry_max_attempts": RETRY_MAX_ATTEMPTS,
                "sampling_control": SAMPLING_CONTROL,
                "bridge_schema": BRIDGE_SCHEMA,
                "native_custom_function_tools": False,
                "text_json_tool_bridge": True,
                "prompt_sha256": sha256_value(prompt),
            },
        )
