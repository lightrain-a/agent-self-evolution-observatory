from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LocalOpenAIReactReceipt:
    call_index: int
    created_at_utc: str
    requested_model: str
    resolved_model: str
    request_sha256: str
    message_sha256: str
    tool_schema_sha256: str
    response_message_sha256: str
    response_id_sha256: str
    provider_status: str
    finish_reason: str
    system_fingerprint: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    temperature_requested: float
    top_p_requested: float
    seed_requested: int
    max_output_tokens: int
    enable_thinking: bool
    parallel_tool_calls: bool
    tool_call_id_policy: str
    provider_retry_limit: int
    hidden_provider_retry_used: bool
    wall_time_seconds: float


class LocalOpenAIReactLLM:
    """Narrow MindMemOS LLMCallable adapter for a frozen local vLLM endpoint.

    This adapter is intentionally unsuitable for the historical hosted E2-R17
    contracts.  It exists for a separately versioned evaluator qualification and
    measurement-repair protocol: fixed model identity, greedy decoding, explicit
    seed, thinking disabled, no SDK retries, and content-addressed public receipts.
    """

    def __init__(
        self,
        *,
        base_url: str,
        requested_model: str,
        required_resolved_model: str,
        max_output_tokens: int = 4096,
        seed: int = 1717,
        timeout_seconds: float = 300.0,
    ) -> None:
        if not base_url.startswith("http://127.0.0.1:"):
            raise RuntimeError("local E2-R17 adapter accepts loopback vLLM endpoints only")
        self.client = OpenAI(
            base_url=base_url.rstrip("/") + "/v1",
            api_key="local-e2-r17",
            timeout=timeout_seconds,
            max_retries=0,
        )
        self.base_url = base_url.rstrip("/")
        self.requested_model = str(requested_model)
        self.required_resolved_model = str(required_resolved_model)
        self.max_output_tokens = int(max_output_tokens)
        self.seed = int(seed)
        self.provider_budget_ledger = None
        self.provider_budget_unit_id = None
        self.receipts: list[LocalOpenAIReactReceipt] = []

    async def __call__(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(self._complete, messages, tools or [])

    def _complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        request_payload = {
            "model": self.requested_model,
            "messages": messages,
            "tools": tools or None,
            "tool_choice": "auto" if tools else None,
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": self.seed,
            "max_tokens": self.max_output_tokens,
            "parallel_tool_calls": False,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        request_sha256 = _canonical_sha(request_payload)
        started = time.monotonic()
        response = self.client.chat.completions.create(
            model=self.requested_model,
            messages=messages,
            tools=tools or None,
            tool_choice="auto" if tools else None,
            temperature=0.0,
            top_p=1.0,
            seed=self.seed,
            max_tokens=self.max_output_tokens,
            parallel_tool_calls=False,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        elapsed = time.monotonic() - started
        resolved = str(response.model or "")
        if resolved != self.required_resolved_model:
            raise RuntimeError(
                "resolved-model-drift:"
                f"requested={self.requested_model};"
                f"required={self.required_resolved_model};observed={resolved}"
            )
        if not response.choices:
            raise RuntimeError("local vLLM returned no completion choice")
        choice = response.choices[0]
        message = choice.message.model_dump(exclude_none=True)
        message["role"] = "assistant"
        for index, call in enumerate(message.get("tool_calls") or []):
            stable_material = f"{request_sha256}:{index}".encode("utf-8")
            call["id"] = f"call_{hashlib.sha256(stable_material).hexdigest()[:24]}"
        usage = response.usage
        receipt = LocalOpenAIReactReceipt(
            call_index=len(self.receipts),
            created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            requested_model=self.requested_model,
            resolved_model=resolved,
            request_sha256=request_sha256,
            message_sha256=_canonical_sha(messages),
            tool_schema_sha256=_canonical_sha(tools),
            response_message_sha256=_canonical_sha(message),
            response_id_sha256=hashlib.sha256(str(response.id or "").encode("utf-8")).hexdigest(),
            provider_status="completed",
            finish_reason=str(choice.finish_reason or ""),
            system_fingerprint=response.system_fingerprint,
            prompt_tokens=int(usage.prompt_tokens if usage else 0),
            completion_tokens=int(usage.completion_tokens if usage else 0),
            total_tokens=int(usage.total_tokens if usage else 0),
            temperature_requested=0.0,
            top_p_requested=1.0,
            seed_requested=self.seed,
            max_output_tokens=self.max_output_tokens,
            enable_thinking=False,
            parallel_tool_calls=False,
            tool_call_id_policy="sha256(request_payload):tool_index",
            provider_retry_limit=0,
            hidden_provider_retry_used=False,
            wall_time_seconds=elapsed,
        )
        self.receipts.append(receipt)
        return message

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(row) for row in self.receipts]

    def public_budget_claims(self) -> list[dict[str, Any]]:
        return []

    @property
    def receipt_bundle_sha256(self) -> str:
        return _canonical_sha(self.public_receipts())


__all__ = ["LocalOpenAIReactLLM", "LocalOpenAIReactReceipt"]
