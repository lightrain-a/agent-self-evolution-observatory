from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha_text(raw)


def _responses_tools(chat_tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in chat_tools or []:
        if item.get("type") != "function":
            raise ValueError("E2-R17 actor accepts function tools only")
        function = item.get("function") or {}
        name = str(function.get("name") or "")
        if not name:
            raise ValueError("tool function name is required")
        out.append(
            {
                "type": "function",
                "name": name,
                "description": str(function.get("description") or ""),
                "parameters": function.get("parameters") or {"type": "object", "properties": {}},
            }
        )
    return out


def _render_messages(messages: list[dict[str, Any]]) -> str:
    """Render a tool-use transcript without dropping role or call identity.

    Ark Plan's Responses endpoint accepts a text input plus native tools.  The
    first-party MindMemOS ReAct loop stores Chat-Completions-shaped messages, so
    this adapter serializes the complete conversation deterministically on every
    turn.  Tool calls and tool outputs remain explicitly paired by call id.
    """

    chunks: list[str] = [
        "The following is the complete conversation transcript. Respect the role tags, "
        "continue from the latest message, and use the supplied native functions when needed."
    ]
    for index, message in enumerate(messages):
        role = str(message.get("role") or "user").upper()
        content = message.get("content")
        if content is not None:
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False, sort_keys=True)
            chunks.append(f"<{role} index={index}>\n{content}\n</{role}>")
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            arguments = function.get("arguments") or "{}"
            if not isinstance(arguments, str):
                arguments = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
            chunks.append(
                "<ASSISTANT_FUNCTION_CALL "
                f"id={call.get('id', '')} name={function.get('name', '')}>\n"
                f"{arguments}\n</ASSISTANT_FUNCTION_CALL>"
            )
        if role == "TOOL":
            chunks.append(
                "<FUNCTION_RESULT_BINDING "
                f"call_id={message.get('tool_call_id', '')} name={message.get('name', '')}/>"
            )
    return "\n\n".join(chunks)


@dataclass(frozen=True)
class ArkPlanReactReceipt:
    call_index: int
    created_at_utc: str
    requested_model: str
    resolved_model: str
    prompt_sha256: str
    tool_schema_sha256: str
    response_id_sha256: str
    provider_status: str
    function_call_names: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    thinking_requested: str | None
    get_poll_recovery: bool
    provider_retry_limit: int
    hidden_provider_retry_used: bool = False


class ArkPlanReactLLM:
    """MindMemOS ``LLMCallable`` adapter over Ark Plan Responses API.

    The adapter is intentionally narrow: one requested/resolved model pair,
    provider retry zero, deterministic transcript rendering, native function
    calls, and public receipts with response identifiers hashed.  Scientific
    runners should instantiate one adapter per rollout so receipt attribution is
    unambiguous and requests sessions are not shared across concurrent rollouts.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str,
        required_resolved_model: str,
        max_output_tokens: int = 4096,
        temperature: float | None = 0,
        thinking: str | None = "disabled",
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
        self.settings = ArkSettings(
            api_key=raw.api_key,
            base_url=raw.base_url,
            default_model=raw.default_model,
            timeout_seconds=max(180.0, raw.timeout_seconds),
            max_retries=0,
        )
        self.client = ArkResponsesClient(self.settings)
        self.requested_model = requested_model
        self.required_resolved_model = required_resolved_model
        self.max_output_tokens = int(max_output_tokens)
        self.temperature = temperature
        self.thinking = thinking
        self.receipts: list[ArkPlanReactReceipt] = []

    async def __call__(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = _render_messages(messages)
        response_tools = _responses_tools(tools)
        result = await asyncio.to_thread(self._respond, prompt, response_tools)
        raw_calls = result.get("function_calls") or []
        tool_calls = []
        for index, call in enumerate(raw_calls):
            call_id = str(call.get("call_id") or call.get("id") or f"call_{index}")
            arguments = call.get("arguments") or "{}"
            if not isinstance(arguments, str):
                arguments = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
            tool_calls.append(
                {
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": str(call.get("name") or ""),
                        "arguments": arguments,
                    },
                }
            )
        message: dict[str, Any] = {
            "role": "assistant",
            "content": str(result.get("text") or "") or None,
        }
        if tool_calls:
            message["tool_calls"] = tool_calls
        return message

    def _respond(self, prompt: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            result = self.client.respond(
                prompt,
                model=self.requested_model,
                max_output_tokens=self.max_output_tokens,
                temperature=self.temperature,
                tools=tools or None,
                thinking=self.thinking,
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            if not polled.get("text") and not polled.get("function_calls"):
                raise
            result = {
                "requested_model": self.requested_model,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "function_calls": polled.get("function_calls") or [],
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "get_poll_recovery": True,
            }
        resolved = str(result.get("resolved_model") or "")
        if resolved != self.required_resolved_model:
            raise RuntimeError(
                f"resolved-model-drift: requested={self.requested_model}; "
                f"required={self.required_resolved_model}; observed={resolved}"
            )
        usage = result.get("usage") or {}
        calls = result.get("function_calls") or []
        receipt = ArkPlanReactReceipt(
            call_index=len(self.receipts),
            created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            requested_model=self.requested_model,
            resolved_model=resolved,
            prompt_sha256=_sha_text(prompt),
            tool_schema_sha256=_canonical_sha(tools),
            response_id_sha256=_sha_text(str(result.get("response_id") or "")),
            provider_status=str(result.get("status") or ""),
            function_call_names=tuple(str(call.get("name") or "") for call in calls),
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            thinking_requested=self.thinking,
            get_poll_recovery=bool(result.get("get_poll_recovery", False)),
            provider_retry_limit=self.settings.max_retries,
        )
        self.receipts.append(receipt)
        return result

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(receipt) for receipt in self.receipts]

    @property
    def receipt_bundle_sha256(self) -> str:
        return _canonical_sha(self.public_receipts())


__all__ = [
    "ArkPlanReactLLM",
    "ArkPlanReactReceipt",
    "PLAN_BASE_URL",
]
