from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .config import load_env_file

DIANMING_BASE_URL = "https://api.aa.com.cn/api/v1"
DIANMING_CHAT_ENDPOINT = "/chat/completions"
DIANMING_SECRET_FILE = Path(
    "/data/wyt/e1-stri-reasoningbank-runtime/secrets/dianming-qwen.env"
)
MODEL = "qwen3-coder-next"


class QwenProviderError(RuntimeError):
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
class QwenChatSettings:
    api_key: str
    base_url: str = DIANMING_BASE_URL
    model: str = MODEL
    timeout_seconds: float = 120.0
    max_retries: int = 0

    @classmethod
    def from_env_file(
        cls,
        env_file: Path = DIANMING_SECRET_FILE,
        *,
        required: bool = True,
    ) -> "QwenChatSettings":
        if env_file.is_file():
            load_env_file(env_file)
        api_key = os.getenv("DIANMING_API_KEY", "").strip()
        if required and not api_key:
            raise RuntimeError(
                "DIANMING_API_KEY is not configured in the dedicated ignored mode-0600 secret file"
            )
        return cls(
            api_key=api_key,
            base_url=os.getenv("DIANMING_BASE_URL", DIANMING_BASE_URL).rstrip("/"),
            model=os.getenv("DIANMING_QWEN_MODEL", MODEL).strip() or MODEL,
            timeout_seconds=float(os.getenv("DIANMING_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("DIANMING_MAX_RETRIES", "0")),
        )

    @property
    def endpoint(self) -> str:
        return self.base_url.rstrip("/") + DIANMING_CHAT_ENDPOINT

    def safe_summary(self) -> dict[str, Any]:
        return {
            "configured": bool(self.api_key),
            "base_url": self.base_url,
            "endpoint": self.endpoint,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "secret_file": str(DIANMING_SECRET_FILE),
            "secret_value_exported": False,
        }


class QwenChatClient:
    """Minimal exactly-once Chat-Completions adapter for qwen3-coder-next."""

    def __init__(
        self,
        settings: QwenChatSettings,
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
    def _safe_error_detail(response: Any) -> Any:
        try:
            detail = response.json()
        except Exception:
            detail = str(getattr(response, "text", ""))[:800]
        if isinstance(detail, dict):
            result = json.loads(json.dumps(detail))

            def redact(value: Any) -> None:
                if isinstance(value, dict):
                    for key, child in list(value.items()):
                        if str(key).lower() in {"api_key", "authorization", "token", "access_token"}:
                            value[key] = "<redacted>"
                        else:
                            redact(child)
                elif isinstance(value, list):
                    for child in value:
                        redact(child)

            redact(result)
            return result
        return detail

    @staticmethod
    def _messages(
        input_items: str | list[dict[str, Any]],
        instructions: str | None,
    ) -> list[dict[str, Any]]:
        if isinstance(input_items, str):
            messages: list[dict[str, Any]] = [{"role": "user", "content": input_items}]
        elif isinstance(input_items, list):
            messages = json.loads(json.dumps(input_items, ensure_ascii=False))
        else:
            raise TypeError("input_items must be a string or a Chat messages list")
        if instructions:
            messages.insert(0, {"role": "system", "content": instructions})
        for row in messages:
            if not isinstance(row, dict) or row.get("role") not in {"system", "user", "assistant", "tool"}:
                raise ValueError("unsupported Chat message shape/role")
        return messages

    @staticmethod
    def _tools(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
        if not tools:
            return None
        out: list[dict[str, Any]] = []
        for tool in tools:
            if tool.get("type") != "function":
                out.append(json.loads(json.dumps(tool)))
                continue
            if isinstance(tool.get("function"), dict):
                out.append(json.loads(json.dumps(tool)))
                continue
            function = {
                key: tool[key]
                for key in ("name", "description", "parameters", "strict")
                if key in tool
            }
            out.append({"type": "function", "function": function})
        return out

    @staticmethod
    def _text(message: dict[str, Any]) -> str:
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") in {"text", "output_text"}:
                    chunks.append(str(part.get("text") or ""))
            return "".join(chunks)
        return ""

    @staticmethod
    def _function_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        for row in message.get("tool_calls") or []:
            if not isinstance(row, dict) or row.get("type") != "function":
                continue
            function = row.get("function") or {}
            calls.append(
                {
                    "type": "function_call",
                    "call_id": row.get("id"),
                    "name": function.get("name"),
                    "arguments": function.get("arguments"),
                }
            )
        return calls

    @classmethod
    def normalize(cls, payload: dict[str, Any], requested_model: str) -> dict[str, Any]:
        choices = payload.get("choices") or []
        if len(choices) != 1:
            raise QwenProviderError(
                "Qwen Chat response did not contain exactly one choice",
                detail={"choice_count": len(choices)},
            )
        choice = choices[0]
        message = choice.get("message") or {}
        raw_text = cls._text(message)
        usage_raw = payload.get("usage") or {}
        usage = {
            "input_tokens": usage_raw.get("prompt_tokens", usage_raw.get("input_tokens")),
            "output_tokens": usage_raw.get("completion_tokens", usage_raw.get("output_tokens")),
            "total_tokens": usage_raw.get("total_tokens"),
            "raw": usage_raw,
        }
        return {
            "response_id": str(payload.get("id") or ""),
            "status": str(choice.get("finish_reason") or "unknown"),
            "requested_model": requested_model,
            "resolved_model": str(payload.get("model") or requested_model),
            "text": raw_text.strip(),
            "raw_text": raw_text,
            "function_calls": cls._function_calls(message),
            "usage": usage,
            "incomplete_details": {
                "finish_reason": choice.get("finish_reason"),
            },
            "choice_count": len(choices),
            "raw_payload_sha256": hashlib.sha256(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "response_metadata": {
                "object": payload.get("object"),
                "created": payload.get("created"),
                "model": payload.get("model"),
                "finish_reason": choice.get("finish_reason"),
                "choice_count": len(choices),
                "system_fingerprint": payload.get("system_fingerprint"),
            },
        }

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
        stop: list[str] | str | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        text: dict[str, Any] | None = None,
        previous_response_id: str | None = None,
        store: bool | None = None,
        thinking: str | None = None,
    ) -> dict[str, Any]:
        del text, store, thinking
        if previous_response_id is not None:
            raise QwenProviderError(
                "Chat Completions has no previous_response_id continuation; explicit messages are required",
                status_code=400,
                detail={"unsupported_parameter": "previous_response_id"},
            )
        requested_model = model or self.settings.model
        body: dict[str, Any] = {
            "model": requested_model,
            "messages": self._messages(input_items, instructions),
            "n": 1,
            "stream": False,
        }
        if max_output_tokens is not None:
            body["max_completion_tokens"] = int(max_output_tokens)
        optional = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "seed": seed,
            "stop": stop,
            "tools": self._tools(tools),
            "tool_choice": tool_choice,
        }
        body.update({key: value for key, value in optional.items() if value is not None})
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
                    raise QwenProviderError(
                        f"Qwen provider transport failure after {attempts + 1} attempt(s): {type(error).__name__}",
                        detail={"transport_error": type(error).__name__},
                    ) from error
                attempts += 1
                time.sleep(min(2 ** (attempts - 1), 4))
                continue
            if response.status_code >= 500 and attempts < self.settings.max_retries:
                attempts += 1
                time.sleep(min(2 ** (attempts - 1), 4))
                continue
            if response.status_code >= 400:
                raise QwenProviderError(
                    f"Qwen provider HTTP {response.status_code}",
                    status_code=response.status_code,
                    detail=self._safe_error_detail(response),
                )
            try:
                payload = response.json()
            except Exception as error:
                raise QwenProviderError(
                    "Qwen provider returned non-JSON success response",
                    status_code=response.status_code,
                ) from error
            normalized = self.normalize(payload, requested_model)
            headers = getattr(response, "headers", {}) or {}
            normalized["response_headers"] = {
                str(key).lower(): str(value)
                for key, value in headers.items()
                if str(key).lower().startswith(("x-ratelimit-", "x-usage-", "x-quota-"))
                or str(key).lower() in {"retry-after", "x-request-id", "request-id"}
            }
            normalized["transport_attempts"] = attempts + 1
            normalized["actual_request"] = json.loads(json.dumps(body, ensure_ascii=False))
            normalized["actual_request_sha256"] = hashlib.sha256(
                json.dumps(
                    body,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            return normalized
