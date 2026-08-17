from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any

import requests

from .config import DEFAULT_ENV_FILE, load_env_file

DEFAULT_ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
ARK_MODELS = (
    "ark-code-latest",
    "doubao-seed-2.0-lite",
    "doubao-seed-2.0-mini",
    "glm-5.2",
    "glm-5.3",
    "kimi-k2.7-code",
    "deepseek-v4-pro",
    "minimax-m3",
    "doubao-seed-evolving",
    "kimi-k3",
    "doubao-seed-2.1-turbo",
    "deepseek-v4-flash",
)


@dataclass(frozen=True, slots=True)
class ArkSettings:
    api_key: str
    base_url: str = DEFAULT_ARK_BASE_URL
    default_model: str = "ark-code-latest"
    timeout_seconds: float = 120.0
    max_retries: int = 2

    @classmethod
    def from_env(cls, *, required: bool = True) -> "ArkSettings":
        load_env_file(DEFAULT_ENV_FILE)
        api_key = os.getenv("ARK_API_KEY", "").strip()
        if required and not api_key:
            raise RuntimeError("ARK_API_KEY is not configured in the ignored server .env")
        return cls(
            api_key=api_key,
            base_url=os.getenv("ARK_BASE_URL", DEFAULT_ARK_BASE_URL).rstrip("/"),
            default_model=os.getenv("ARK_DEFAULT_MODEL", "ark-code-latest").strip() or "ark-code-latest",
            timeout_seconds=float(os.getenv("ARK_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("ARK_MAX_RETRIES", "2")),
        )

    def safe_summary(self) -> dict[str, Any]:
        return {
            "configured": bool(self.api_key),
            "base_url": self.base_url,
            "default_model": self.default_model,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "api_key_in_output": False,
        }


class ArkResponseStateError(RuntimeError):
    """A provider response object exists, but it has no auditable assistant output yet."""

    def __init__(self, message: str, payload: dict[str, Any], requested_model: str) -> None:
        super().__init__(message)
        self.response_id = str(payload.get("id") or "")
        self.response_status = str(payload.get("status") or "unknown")
        self.requested_model = requested_model
        self.resolved_model = str(payload.get("model") or requested_model)
        incomplete = payload.get("incomplete_details") or {}
        self.incomplete_reason = str(incomplete.get("reason") or "") if isinstance(incomplete, dict) else ""

    def receipt(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "status": self.response_status,
            "requested_model": self.requested_model,
            "resolved_model": self.resolved_model,
            "incomplete_reason": self.incomplete_reason,
        }


class ArkResponsesClient:
    def __init__(self, settings: ArkSettings | None = None) -> None:
        self.settings = settings or ArkSettings.from_env()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        })

    @property
    def endpoint(self) -> str:
        return self.settings.base_url + "/responses"

    @staticmethod
    def output_text(payload: dict[str, Any]) -> str:
        chunks: list[str] = []
        for item in payload.get("output") or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    text = str(part.get("text") or "").strip()
                    if text:
                        chunks.append(text)
        return "\n".join(chunks).strip()

    @staticmethod
    def function_calls(payload: dict[str, Any]) -> list[dict[str, Any]]:
        return [item for item in payload.get("output") or [] if isinstance(item, dict) and item.get("type") == "function_call"]

    def retrieve_response(self, response_id: str) -> dict[str, Any]:
        """Retrieve one existing Responses API object without creating a new provider request."""
        response_id = str(response_id or "").strip()
        if not response_id:
            raise ValueError("response_id is required")
        response = self.session.get(
            f"{self.endpoint}/{response_id}",
            timeout=self.settings.timeout_seconds,
        )
        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:500]
            raise RuntimeError(f"Ark retrieve HTTP {response.status_code}: {detail}")
        payload = response.json()
        return {
            "response_id": payload.get("id") or response_id,
            "status": payload.get("status"),
            "requested_model": None,
            "resolved_model": payload.get("model"),
            "text": self.output_text(payload),
            "function_calls": self.function_calls(payload),
            "usage": payload.get("usage") or {},
            "incomplete_details": payload.get("incomplete_details") or {},
        }

    def poll_response(
        self,
        response_id: str,
        *,
        max_polls: int = 1,
        interval_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """Poll an existing response using GET only; never submits another generation POST."""
        if max_polls < 1:
            raise ValueError("max_polls must be >= 1")
        result: dict[str, Any] = {}
        for index in range(max_polls):
            result = self.retrieve_response(response_id)
            result["poll_count"] = index + 1
            status = str(result.get("status") or "unknown")
            if status not in {"queued", "in_progress"}:
                return result
            if index + 1 < max_polls and interval_seconds > 0:
                time.sleep(interval_seconds)
        return result

    def respond(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_output_tokens: int = 4096,
        temperature: float | None = None,
        tools: list[dict[str, Any]] | None = None,
        thinking: str | None = None,
        store: bool | None = None,
    ) -> dict[str, Any]:
        requested_model = model or self.settings.default_model
        body: dict[str, Any] = {
            "model": requested_model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        }
        if temperature is not None:
            body["temperature"] = temperature
        if store is not None:
            body["store"] = bool(store)
        if tools:
            body["tools"] = tools
        if thinking:
            body["thinking"] = {"type": thinking}
        last_error = ""
        retry_attempt = 0
        thinking_compatibility_fallback = False
        while True:
            try:
                response = self.session.post(self.endpoint, json=body, timeout=self.settings.timeout_seconds)
                if response.status_code >= 400:
                    try:
                        detail = response.json()
                    except Exception:
                        detail = response.text[:500]
                    detail_text = str(detail).lower()
                    unsupported_disabled_thinking = bool(
                        response.status_code == 400
                        and body.get("thinking") == {"type": "disabled"}
                        and not thinking_compatibility_fallback
                        and "thinking.type" in detail_text
                        and "not supported" in detail_text
                    )
                    if unsupported_disabled_thinking:
                        body.pop("thinking", None)
                        thinking_compatibility_fallback = True
                        continue
                    raise RuntimeError(f"Ark HTTP {response.status_code}: {detail}")
                payload = response.json()
                text = self.output_text(payload)
                calls = self.function_calls(payload)
                if not text and not calls:
                    status = str(payload.get("status") or "unknown")
                    incomplete = payload.get("incomplete_details") or {}
                    reason = incomplete.get("reason") if isinstance(incomplete, dict) else None
                    usage = payload.get("usage") or {}
                    output_details = usage.get("output_tokens_details") or {} if isinstance(usage, dict) else {}
                    reasoning_tokens = output_details.get("reasoning_tokens") if isinstance(output_details, dict) else None
                    output_tokens = usage.get("output_tokens") if isinstance(usage, dict) else None
                    resolved_model = payload.get("model") or requested_model
                    response_id = str(payload.get("id") or "")
                    if status == "incomplete":
                        raise ArkResponseStateError(
                            "Ark response incomplete before assistant output"
                            f"; response_id={response_id or 'missing'}"
                            f"; reason={reason or 'unknown'}"
                            f"; requested_model={requested_model}"
                            f"; resolved_model={resolved_model}"
                            f"; output_tokens={output_tokens}"
                            f"; reasoning_tokens={reasoning_tokens}",
                            payload,
                            requested_model,
                        )
                    raise ArkResponseStateError(
                        "Ark response contained neither assistant output_text nor function_call"
                        f"; response_id={response_id or 'missing'}"
                        f"; status={status}; requested_model={requested_model}; resolved_model={resolved_model}",
                        payload,
                        requested_model,
                    )
                return {
                    "requested_model": requested_model,
                    "resolved_model": payload.get("model") or requested_model,
                    "text": text,
                    "function_calls": calls,
                    "usage": payload.get("usage") or {},
                    "response_id": payload.get("id"),
                    "status": payload.get("status"),
                    "thinking_requested": thinking,
                    "thinking_effective": None if thinking_compatibility_fallback else thinking,
                    "thinking_compatibility_fallback": thinking_compatibility_fallback,
                }
            except ArkResponseStateError:
                # The provider already created a response object. Re-POSTing the prompt here would
                # create a second generation request and destroy receipt-level auditability.
                raise
            except Exception as error:
                last_error = str(error)
                if retry_attempt >= self.settings.max_retries:
                    break
                time.sleep(min(2 ** retry_attempt, 4))
                retry_attempt += 1
        raise RuntimeError(last_error)


def extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("model output contains no JSON object")
    payload = json.loads(candidate[start:end + 1])
    if not isinstance(payload, dict):
        raise ValueError("model JSON output is not an object")
    return payload
