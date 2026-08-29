from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.e2_r17_provider_budget import ProviderBudgetClaim, ProviderBudgetLedger

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODEL = "deepseek-v4-pro"
# Historical default retained only for backward-compatible callers. Every new
# E2-R17 execution tranche must pass its freshly qualified resolved identity.
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _safe_task_name(task: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", task).strip("-")
    return cleaned or "call"


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
    call_index: int
    created_at_utc: str
    task: str
    attempt: int
    requested_model: str
    resolved_model: str
    prompt_sha256: str
    response_sha256: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    response_id_sha256: str
    provider_status: str
    thinking_requested: str | None
    temperature_requested: float
    provider_retry_limit: int
    message_count: int
    wall_time_seconds: float
    parse_error: str = ""
    record_path: str | None = None
    hidden_provider_retry_used: bool = False
    provider_budget_claim_id: int | None = None
    provider_budget_unit_call_index: int | None = None
    provider_budget_total_claimed_after: int | None = None


class MindMemOSArkPlanChatAdapter:
    """Async MindMemOS ``LLMClient.chat`` adapter over Ark Plan Responses.

    Provider retries are disabled. Parse-correction attempts are explicit and are
    counted separately because they are part of the frozen SkillEvolver updater
    policy, not part of acting compute K. When ``record_dir`` is supplied, every
    updater call is written atomically with the full prompt and response text;
    raw provider response identifiers are never persisted.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str = REQUESTED_MODEL,
        required_resolved_model: str = REQUIRED_RESOLVED_MODEL,
        max_parse_attempts: int = 3,
        record_dir: Path | str | None = None,
        provider_budget_ledger: ProviderBudgetLedger | None = None,
        provider_budget_unit_id: str | None = None,
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("R17 adapter refuses non-Plan Ark route")
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
        self.max_parse_attempts = max(1, int(max_parse_attempts))
        self.record_dir = Path(record_dir) if record_dir is not None else None
        if (provider_budget_ledger is None) != (provider_budget_unit_id is None):
            raise ValueError("provider budget ledger and unit id must be supplied together")
        self.provider_budget_ledger = provider_budget_ledger
        self.provider_budget_unit_id = str(provider_budget_unit_id) if provider_budget_unit_id is not None else None
        self.provider_budget_claims: list[ProviderBudgetClaim] = []
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
            started = time.monotonic()
            result = self._respond(prompt, target=target, kwargs=kwargs)
            wall_time_seconds = time.monotonic() - started
            content = str(result.get("text") or "")
            resolved = str(result.get("resolved_model") or "")
            usage = result.get("usage") or {}
            receipt = CallReceipt(
                call_index=len(self.receipts),
                created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                task=task,
                attempt=attempt,
                requested_model=target,
                resolved_model=resolved,
                prompt_sha256=_sha(prompt),
                response_sha256=_sha(content),
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
                response_id_sha256=_sha(str(result.get("response_id") or "")),
                provider_status=str(result.get("status") or ""),
                thinking_requested=result.get("thinking_requested") or kwargs.get("thinking") or "disabled",
                temperature_requested=float(result.get("temperature_requested", 0.0)),
                provider_retry_limit=self.settings.max_retries,
                message_count=len(convo),
                wall_time_seconds=wall_time_seconds,
                provider_budget_claim_id=result.get("provider_budget_claim_id"),
                provider_budget_unit_call_index=result.get("provider_budget_unit_call_index"),
                provider_budget_total_claimed_after=result.get("provider_budget_total_claimed_after"),
            )
            parsed: Any = None
            if format_parser is not None:
                try:
                    parsed = format_parser(content)
                except Exception as exc:
                    last_error = exc
                    receipt.parse_error = f"{type(exc).__name__}: {exc}"
                    self._persist_call(
                        receipt=receipt,
                        messages=convo,
                        prompt=prompt,
                        content=content,
                        result=result,
                        parser_applied=True,
                        parsed=None,
                    )
                    self.receipts.append(receipt)
                    if feedback_on_parse_error and attempt + 1 < max_attempts:
                        convo.append({"role": "assistant", "content": content})
                        convo.append(
                            {
                                "role": "user",
                                "content": (
                                    "Your previous reply could not be applied:\n"
                                    f"{exc}\n\nFix exactly that problem and resend the COMPLETE corrected output "
                                    "in the same format as before. Do not apologize or add commentary."
                                ),
                            }
                        )
                    continue
            self._persist_call(
                receipt=receipt,
                messages=convo,
                prompt=prompt,
                content=content,
                result=result,
                parser_applied=format_parser is not None,
                parsed=parsed,
            )
            self.receipts.append(receipt)
            if resolved != self.required_resolved_model:
                raise RuntimeError(
                    f"resolved-model-drift:requested={target};required={self.required_resolved_model};observed={resolved}"
                )
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
                    "prompt_sha256": receipt.prompt_sha256,
                    "response_sha256": receipt.response_sha256,
                    "status": result.get("status"),
                    "thinking_requested": result.get("thinking_requested"),
                    "thinking_effective": result.get("thinking_effective"),
                    "record_path": receipt.record_path,
                },
            )
        assert last_error is not None
        raise last_error

    def _persist_call(
        self,
        *,
        receipt: CallReceipt,
        messages: list[dict[str, Any]],
        prompt: str,
        content: str,
        result: dict[str, Any],
        parser_applied: bool,
        parsed: Any,
    ) -> None:
        if self.record_dir is None:
            return
        filename = f"{receipt.call_index:03d}-{_safe_task_name(receipt.task)}-attempt{receipt.attempt}.json"
        path = self.record_dir / filename
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-mindmemos-updater-provider-call",
            "created_at_utc": receipt.created_at_utc,
            "task": receipt.task,
            "attempt": receipt.attempt,
            "messages": messages,
            "prompt": prompt,
            "prompt_sha256": receipt.prompt_sha256,
            "response_text": content,
            "response_sha256": receipt.response_sha256,
            "requested_model": receipt.requested_model,
            "resolved_model": receipt.resolved_model,
            "usage": result.get("usage") or {},
            "provider_status": result.get("status"),
            "response_id_sha256": receipt.response_id_sha256,
            "thinking_requested": result.get("thinking_requested") or receipt.thinking_requested,
            "thinking_effective": result.get("thinking_effective"),
            "temperature_requested": receipt.temperature_requested,
            "provider_retry_limit": self.settings.max_retries,
            "hidden_provider_retry_used": False,
            "wall_time_seconds": receipt.wall_time_seconds,
            "provider_budget_claim_id": receipt.provider_budget_claim_id,
            "provider_budget_unit_call_index": receipt.provider_budget_unit_call_index,
            "provider_budget_total_claimed_after": receipt.provider_budget_total_claimed_after,
            "parser_applied": parser_applied,
            "parse_error": receipt.parse_error,
            "parsed_type": type(parsed).__name__ if parsed is not None else None,
            "parsed_sha256": _sha(str(parsed)) if parsed is not None else None,
            "private_credentials_included": False,
            "raw_response_id_included": False,
        }
        _atomic_json(path, payload)
        receipt.record_path = str(path.resolve())

    def _respond(self, prompt: str, *, target: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        budget_claim: ProviderBudgetClaim | None = None
        if self.provider_budget_ledger is not None:
            assert self.provider_budget_unit_id is not None
            budget_claim = self.provider_budget_ledger.claim(self.provider_budget_unit_id)
            self.provider_budget_claims.append(budget_claim)
        max_output_tokens = int(kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 4096)
        temperature = kwargs.get("temperature")
        if temperature is None:
            # SkillEvolver's first-party summary/patch calls do not currently pass
            # an explicit temperature. Future E2-R17 causal tranches freeze that
            # otherwise provider-defined default to zero; historical receipts are
            # never regenerated under this rule.
            temperature = 0.0
        thinking = kwargs.get("thinking") or "disabled"
        try:
            result = self.client.respond(
                prompt,
                model=target,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                thinking=thinking,
                allow_thinking_compatibility_fallback=False,
            )
            result["thinking_requested"] = thinking
            result["temperature_requested"] = float(temperature)
            result.setdefault("thinking_effective", thinking)
            if budget_claim is not None:
                result["provider_budget_claim_id"] = budget_claim.claim_id
                result["provider_budget_unit_call_index"] = budget_claim.unit_call_index
                result["provider_budget_total_claimed_after"] = budget_claim.total_claimed_after
            return result
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=3, interval_seconds=1.0)
            if not polled.get("text"):
                raise
            result = {
                "requested_model": target,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "thinking_requested": thinking,
                "thinking_effective": thinking,
                "get_poll_recovery": True,
            }
            if budget_claim is not None:
                result["provider_budget_claim_id"] = budget_claim.claim_id
                result["provider_budget_unit_call_index"] = budget_claim.unit_call_index
                result["provider_budget_total_claimed_after"] = budget_claim.total_claimed_after
            return result

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(receipt) for receipt in self.receipts]

    def public_budget_claims(self) -> list[dict[str, Any]]:
        return [claim.to_dict() for claim in self.provider_budget_claims]

    @property
    def receipt_bundle_sha256(self) -> str:
        raw = json.dumps(self.public_receipts(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return _sha(raw)
