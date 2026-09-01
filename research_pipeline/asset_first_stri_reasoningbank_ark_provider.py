from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .ark_provider import ArkSettings
from .config import load_env_file


CANONICAL_SECRET_FILE = Path("/home/wyt/code/agent-self-evolution-observatory/.env")


class ArkCompatibilityError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, detail: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

    def safe_receipt(self) -> dict[str, Any]:
        return {
            "error_type": type(self).__name__,
            "message": str(self),
            "status_code": self.status_code,
            "detail": self.detail,
            "credential_material_present": False,
        }


@dataclass(frozen=True, slots=True)
class ArkReasoningBankSettings:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float = 120.0
    max_retries: int = 2

    @classmethod
    def from_env_file(
        cls,
        env_file: Path = CANONICAL_SECRET_FILE,
        *,
        required: bool = True,
    ) -> "ArkReasoningBankSettings":
        load_env_file(env_file)
        settings = ArkSettings.from_env(required=required)
        return cls(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.default_model,
            timeout_seconds=settings.timeout_seconds,
            max_retries=settings.max_retries,
        )

    @property
    def endpoint(self) -> str:
        return self.base_url.rstrip("/") + "/responses"

    def safe_summary(self) -> dict[str, Any]:
        return {
            "configured": bool(self.api_key),
            "base_url": self.base_url,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "secret_file": str(CANONICAL_SECRET_FILE),
            "secret_value_exported": False,
        }


class ArkReasoningBankClient:
    """Minimal Responses-API adapter preserving ReasoningBank message/tool semantics."""

    def __init__(
        self,
        settings: ArkReasoningBankSettings,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
            }
        )

    @staticmethod
    def output_text_raw(payload: dict[str, Any]) -> str:
        chunks: list[str] = []
        for item in payload.get("output") or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    value = str(part.get("text") or "")
                    if value:
                        chunks.append(value)
        return "\n".join(chunks)

    @classmethod
    def output_text(cls, payload: dict[str, Any]) -> str:
        """Compatibility view retained for existing callers and receipts."""
        return cls.output_text_raw(payload).strip()

    @staticmethod
    def function_calls(payload: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            item
            for item in payload.get("output") or []
            if isinstance(item, dict) and item.get("type") == "function_call"
        ]

    @classmethod
    def normalize(cls, payload: dict[str, Any], requested_model: str) -> dict[str, Any]:
        return {
            "response_id": str(payload.get("id") or ""),
            "status": str(payload.get("status") or "unknown"),
            "requested_model": requested_model,
            "resolved_model": str(payload.get("model") or requested_model),
            "text": cls.output_text(payload),
            "raw_text": cls.output_text_raw(payload),
            "function_calls": cls.function_calls(payload),
            "usage": payload.get("usage") or {},
            "incomplete_details": payload.get("incomplete_details") or {},
            "raw_payload_sha256": hashlib.sha256(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "response_metadata": {
                key: payload.get(key)
                for key in (
                    "created_at",
                    "completed_at",
                    "error",
                    "incomplete_details",
                    "model",
                    "object",
                    "parallel_tool_calls",
                    "service_tier",
                    "status",
                    "temperature",
                    "top_p",
                    "top_k",
                    "seed",
                    "stop",
                )
                if key in payload
            },
        }

    @staticmethod
    def _safe_error_detail(response: Any) -> Any:
        try:
            detail = response.json()
        except Exception:
            detail = str(getattr(response, "text", ""))[:800]
        if isinstance(detail, dict):
            redacted = json.loads(json.dumps(detail))
            for key in ("api_key", "authorization", "Authorization", "token"):
                if key in redacted:
                    redacted[key] = "<redacted>"
            return redacted
        return detail

    def create_response(
        self,
        *,
        input_items: str | list[dict[str, Any]],
        instructions: str | None = None,
        model: str | None = None,
        max_output_tokens: int | None = 512,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        seed: int | None = None,
        stop: list[str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        text: dict[str, Any] | None = None,
        previous_response_id: str | None = None,
        store: bool | None = True,
        thinking: str | None = None,
    ) -> dict[str, Any]:
        requested_model = model or self.settings.model
        body: dict[str, Any] = {
            "model": requested_model,
            "input": input_items,
        }
        if max_output_tokens is not None:
            body["max_output_tokens"] = max_output_tokens
        optional = {
            "instructions": instructions,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "seed": seed,
            "stop": stop,
            "tools": tools,
            "tool_choice": tool_choice,
            "text": text,
            "previous_response_id": previous_response_id,
            "store": store,
        }
        body.update({key: value for key, value in optional.items() if value is not None})
        if thinking is not None:
            body["thinking"] = {"type": thinking}

        attempts = 0
        while True:
            try:
                response = self.session.post(
                    self.settings.endpoint,
                    json=body,
                    timeout=self.settings.timeout_seconds,
                )
            except requests.RequestException as error:
                if attempts >= self.settings.max_retries:
                    raise ArkCompatibilityError(
                        f"Ark transport failure after {attempts + 1} attempt(s): {type(error).__name__}",
                        detail={"transport_error": type(error).__name__},
                    ) from error
                time.sleep(min(2**attempts, 4))
                attempts += 1
                continue
            if response.status_code >= 500 and attempts < self.settings.max_retries:
                time.sleep(min(2**attempts, 4))
                attempts += 1
                continue
            if response.status_code >= 400:
                raise ArkCompatibilityError(
                    f"Ark HTTP {response.status_code}",
                    status_code=response.status_code,
                    detail=self._safe_error_detail(response),
                )
            try:
                payload = response.json()
            except Exception as error:
                raise ArkCompatibilityError(
                    "Ark returned non-JSON success response",
                    status_code=response.status_code,
                ) from error
            normalized = self.normalize(payload, requested_model)
            headers = getattr(response, "headers", {}) or {}
            normalized["response_headers"] = {
                str(key).lower(): str(value)
                for key, value in headers.items()
                if str(key).lower().startswith(("x-ratelimit-", "x-usage-", "x-quota-"))
                or str(key).lower() == "retry-after"
            }
            normalized["transport_attempts"] = attempts + 1
            return normalized

    def continue_function_call(
        self,
        *,
        previous_response_id: str,
        call_id: str,
        output: str,
        instructions: str | None = None,
        model: str | None = None,
        max_output_tokens: int = 512,
    ) -> dict[str, Any]:
        return self.create_response(
            input_items=[
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output,
                }
            ],
            instructions=instructions,
            model=model,
            max_output_tokens=max_output_tokens,
            previous_response_id=previous_response_id,
            store=True,
        )
