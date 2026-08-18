from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from pace_bench.core.types import GenerationRequest, GenerationResult

from .ark_provider import ArkResponsesClient, ArkSettings


class PaceArkProvider:
    """PACE-Bench ModelProvider adapter for the project's audited Ark Responses API.

    The benchmark owns prompts, seeds, strategy, verifier budget, and Box2D truth.
    This adapter only transports one PACE GenerationRequest to Ark and maps the
    provider receipt back into PACE's GenerationResult schema.
    """

    name = "pace-ark-responses"

    def __init__(
        self,
        *,
        model: str,
        max_output_tokens_cap: int = 8192,
        thinking: str | None = "disabled",
    ) -> None:
        self.model = str(model)
        self.max_output_tokens_cap = max(256, int(max_output_tokens_cap))
        self.thinking = thinking
        self.client = ArkResponsesClient(ArkSettings.from_env())
        receipt_path = os.getenv("PACE_ARK_RECEIPT_JSONL", "").strip() or os.getenv("PACE_ARK_RECEIPT_PATH", "").strip()
        self.receipt_path = Path(receipt_path) if receipt_path else None

    def _append_receipt(self, row: dict[str, Any]) -> None:
        if self.receipt_path is None:
            return
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def generate(self, request: GenerationRequest) -> GenerationResult:
        prompt = request.prompt
        if request.system_prompt:
            prompt = f"SYSTEM INSTRUCTION:\n{request.system_prompt}\n\nUSER REQUEST:\n{request.prompt}"
        started = time.perf_counter()
        receipt = self.client.respond(
            prompt,
            model=self.model,
            max_output_tokens=min(int(request.max_tokens), self.max_output_tokens_cap),
            temperature=float(request.temperature),
            thinking=self.thinking,
            store=False,
        )
        usage = receipt.get("usage") or {}
        input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or usage.get("completion_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or (input_tokens + output_tokens))
        resolved = str(receipt.get("resolved_model") or self.model)
        latency = time.perf_counter() - started
        self._append_receipt({
            "attempt": request.metadata.get("attempt"),
            "request_metadata": dict(request.metadata),
            "requested_model": receipt.get("requested_model") or self.model,
            "resolved_model": resolved,
            "response_id": receipt.get("response_id"),
            "status": receipt.get("status"),
            "latency_seconds": latency,
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": total_tokens,
            "thinking_effective": receipt.get("thinking_effective"),
            "thinking_compatibility_fallback": bool(receipt.get("thinking_compatibility_fallback")),
            "prompt_or_code_in_receipt": False,
            "api_key_in_receipt": False,
        })
        return GenerationResult(
            text=str(receipt.get("text") or ""),
            model=resolved,
            latency_seconds=latency,
            token_usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
            },
            raw={
                "response_id": receipt.get("response_id"),
                "status": receipt.get("status"),
                "requested_model": receipt.get("requested_model") or self.model,
                "resolved_model": resolved,
                "thinking_requested": receipt.get("thinking_requested"),
                "thinking_effective": receipt.get("thinking_effective"),
                "thinking_compatibility_fallback": bool(receipt.get("thinking_compatibility_fallback")),
            },
        )

    def close(self) -> None:
        close = getattr(self.client.session, "close", None)
        if callable(close):
            close()
