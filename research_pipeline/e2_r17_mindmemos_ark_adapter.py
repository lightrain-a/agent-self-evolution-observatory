from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"


def _flatten_messages(messages: list[dict[str, Any]]) -> str:
    """Render MindMemOS chat messages into a deterministic Responses prompt.

    This adapter changes transport only. Role boundaries and content are preserved
    explicitly; SkillEvolver prompts, parsers, and update semantics remain first-party.
    """
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role") or "user").upper()
        content = message.get("content")
        text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, sort_keys=True)
        parts.append(f"<{role}>\n{text}\n</{role}>")
    return "\n".join(parts)


@dataclass
class AdapterUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class AdapterChatResponse:
    finish_reason: str
    content: str
    model: str
    usage: AdapterUsage = field(default_factory=AdapterUsage)
    parsed: Any = None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class CallReceipt:
    task: str
    attempt: int
    requested_model: str
    resolved_model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    response_id_sha256: str
    parse_error: str = ""


class MindMemOSArkPlanChatAdapter:
    """Minimal async MindMemOS ``LLMClient.chat`` adapter over Ark Plan Responses.

    Provider retries are disabled. Parse-correction attempts are explicit and are
    counted separately because they are part of the frozen SkillEvolver updater
    policy, not part of the acting compute intervention K.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str = REQUESTED_MODEL,
        required_resolved_model: str = REQUIRED_RESOLVED_MODEL,
        max_parse_attempts: int = 3,
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("R17 adapter refuses non-Plan Ark route")
        self.settings = ArkSettings(
            api_key=raw.api_key,
            base_url=raw.base_url,
            default_model=raw.default_model,
            timeout_seconds=180.0,
            max_retries=0,
        )
        self.client = ArkResponsesClient(self.settings)
        self.requested_model = requested_model
        self.required_resolved_model = required_resolved_model
        self.max_parse_attempts = max(1, int(max_parse_attempts))
        self.receipts: list[CallReceipt] = []

    async def chat(
        self,
        task: str,
        messages: list[dict[str, Any]],
        format_parser: Callable[[str], Any] | None = None,
        *,
        model: str | None = None,
        feedback_on_parse_error: bool = False,
        **kwargs: Any,
    ) -> AdapterChatResponse:
        target = model or self.requested_model
        convo = list(messages)
        max_attempts = self.max_parse_attempts if format_parser is not None else 1
        last_error: Exception | None = None
        for attempt in range(max_attempts):
            prompt = _flatten_messages(convo)
            result = self._respond(prompt, target=target, kwargs=kwargs)
            content = str(result.get("text") or "")
            resolved = str(result.get("resolved_model") or "")
            if resolved != self.required_resolved_model:
                raise RuntimeError(f"resolved-model-drift:{resolved}")
            usage = result.get("usage") or {}
            receipt = CallReceipt(
                task=task,
                attempt=attempt,
                requested_model=target,
                resolved_model=resolved,
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
                response_id_sha256=self._sha(str(result.get("response_id") or "")),
            )
            parsed: Any = None
            if format_parser is not None:
                try:
                    parsed = format_parser(content)
                except Exception as exc:
                    last_error = exc
                    receipt.parse_error = f"{type(exc).__name__}: {exc}"
                    self.receipts.append(receipt)
                    if feedback_on_parse_error and attempt + 1 < max_attempts:
                        convo.append({"role": "assistant", "content": content})
                        convo.append({
                            "role": "user",
                            "content": (
                                "Your previous reply could not be applied:\n"
                                f"{exc}\n\nFix exactly that problem and resend the COMPLETE corrected output "
                                "in the same format as before. Do not apologize or add commentary."
                            ),
                        })
                    continue
            self.receipts.append(receipt)
            return AdapterChatResponse(
                finish_reason=str(result.get("status") or "completed"),
                content=content,
                model=resolved,
                usage=AdapterUsage(
                    prompt_tokens=usage.get("input_tokens"),
                    completion_tokens=usage.get("output_tokens"),
                    total_tokens=usage.get("total_tokens"),
                ),
                parsed=parsed,
                raw_response={
                    "response_id_sha256": receipt.response_id_sha256,
                    "status": result.get("status"),
                    "thinking_requested": result.get("thinking_requested"),
                    "thinking_effective": result.get("thinking_effective"),
                },
            )
        assert last_error is not None
        raise last_error

    def _respond(self, prompt: str, *, target: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        max_output_tokens = int(kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 4096)
        temperature = kwargs.get("temperature")
        thinking = kwargs.get("thinking") or "disabled"
        try:
            return self.client.respond(
                prompt,
                model=target,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                thinking=thinking,
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=3, interval_seconds=1.0)
            if not polled.get("text"):
                raise
            return {
                "requested_model": target,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "thinking_requested": thinking,
                "thinking_effective": thinking,
            }

    @staticmethod
    def _sha(text: str) -> str:
        import hashlib
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def public_receipts(self) -> list[dict[str, Any]]:
        return [receipt.__dict__.copy() for receipt in self.receipts]
