from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from research_pipeline.agent_safety_g1_qwen397_capability_requal import MODEL

TEMPERATURE = 0.1
MODEL_SEED = 0
MAX_NEW_TOKENS = 2000
MAX_CALLS = 10


class ProviderError(RuntimeError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _atomic_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())


def serialize_messages(messages: Iterable[Any]) -> tuple[list[dict[str, str]], str]:
    roles = {"system": "system", "human": "user", "ai": "assistant"}
    rows: list[dict[str, str]] = []
    for message in messages:
        role = roles.get(str(getattr(message, "type", "")).lower())
        content = getattr(message, "content", None)
        if role is None or not isinstance(content, str):
            raise ProviderError("text LangChain messages required")
        rows.append({"role": role, "content": content})
    raw = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return rows, _sha(raw)


class RawCallLedger:
    def __init__(self, path: Path, raw_dir: Path, cap: int = MAX_CALLS):
        self.path, self.raw_dir, self.cap = Path(path), Path(raw_dir), int(cap)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            _atomic_json(self.path, {"schema_version": "g1-qwen397-provider-ledger-v1", "cap": self.cap, "calls": []})

    def _load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, value: dict[str, Any]) -> None:
        _atomic_json(self.path, value)

    def begin(self, prompt_sha: str) -> int:
        state = self._load(); calls = state["calls"]
        if any(row["status"] == "DISPATCHED" for row in calls):
            raise ProviderError("unknown-after-dispatch forbids continuation")
        if len(calls) >= self.cap:
            raise ProviderError("provider call cap exceeded")
        call_id = len(calls) + 1
        calls.append({
            "call_id": call_id, "status": "DISPATCHED", "prompt_sha256": prompt_sha,
            "requested_model": MODEL, "temperature": TEMPERATURE, "seed": MODEL_SEED,
            "max_tokens": MAX_NEW_TOKENS, "enable_thinking": False, "dispatch_time_ns": time.time_ns(),
        })
        self._save(state); return call_id

    def persist_raw(self, call_id: int, raw: bytes, *, is_error: bool = False) -> Path:
        suffix = "raw-error" if is_error else "raw.json"
        raw_path = self.raw_dir / f"call-{call_id:03d}.{suffix}"
        if raw_path.exists(): raise ProviderError("raw provider bytes overwrite forbidden")
        _atomic_bytes(raw_path, raw)
        state = self._load(); row = state["calls"][call_id - 1]
        if row["status"] != "DISPATCHED": raise ProviderError("raw persistence requires open dispatch")
        row.update({"raw_path": str(raw_path), "raw_sha256": _sha(raw), "raw_persisted_time_ns": time.time_ns()})
        self._save(state); return raw_path

    def complete(self, call_id: int, response: dict[str, Any]) -> None:
        state = self._load(); row = state["calls"][call_id - 1]
        if row["status"] != "DISPATCHED" or not row.get("raw_path"): raise ProviderError("completion requires persisted raw bytes")
        row.update({
            "status": "COMPLETED", "response_id": response.get("id"), "returned_model": response.get("model"),
            "system_fingerprint": response.get("system_fingerprint"), "usage": response.get("usage") or {},
            "complete_time_ns": time.time_ns(),
        }); self._save(state)

    def fail(self, call_id: int, failure_class: str, message: str) -> None:
        state = self._load(); row = state["calls"][call_id - 1]
        if row["status"] != "DISPATCHED": raise ProviderError("failure without open dispatch")
        row.update({"status": "FAILED", "failure_class": failure_class, "message": message[:500],
                    "retry_attempted": False, "complete_time_ns": time.time_ns()}); self._save(state)

    def summary(self) -> dict[str, Any]:
        state = self._load(); calls = state["calls"]
        return {
            "cap": self.cap, "used": len(calls),
            "completed": sum(x["status"] == "COMPLETED" for x in calls),
            "failed": sum(x["status"] == "FAILED" for x in calls),
            "unknown_after_dispatch": sum(x["status"] == "DISPATCHED" for x in calls),
            "ledger_sha256": _sha(self.path.read_bytes()),
        }


class RawProviderChat:
    def __init__(self, args: "Qwen397ChatArgs"):
        self.args = args
        self.ledger = RawCallLedger(Path(args.ledger_path), Path(args.raw_response_dir))

    def invoke(self, messages: Iterable[Any]) -> Any:
        from langchain.schema import AIMessage
        payload, prompt_sha = serialize_messages(messages); call_id = self.ledger.begin(prompt_sha)
        body = {"model": MODEL, "messages": payload, "temperature": TEMPERATURE, "max_tokens": MAX_NEW_TOKENS,
                "seed": MODEL_SEED, "enable_thinking": False}
        request = urllib.request.Request(
            self.args.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(),
            headers={"Authorization": "Bearer " + self.args.api_key, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.args.timeout_seconds) as response: raw = response.read()
        except urllib.error.HTTPError as exc:
            raw = exc.read() if hasattr(exc, "read") else b""; self.ledger.persist_raw(call_id, raw, is_error=True); self.ledger.fail(call_id, "HTTPError", str(exc)); raise ProviderError("HTTP failure; no retry") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self.ledger.fail(call_id, type(exc).__name__, str(exc)); raise ProviderError("transport failure; no retry") from exc
        self.ledger.persist_raw(call_id, raw)  # Strictly before JSON/semantic parsing.
        try: parsed = json.loads(raw.decode())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.ledger.fail(call_id, "MALFORMED_JSON", str(exc)); raise ProviderError("malformed provider response; no retry") from exc
        if not isinstance(parsed, dict) or parsed.get("model") != MODEL:
            self.ledger.fail(call_id, "MODEL_IDENTITY_DRIFT", str(parsed.get("model") if isinstance(parsed, dict) else None)); raise ProviderError("returned model drift")
        choices = parsed.get("choices"); text = None
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            message = choices[0].get("message"); text = message.get("content") if isinstance(message, dict) else None
        if not isinstance(text, str) or not text.strip():
            self.ledger.fail(call_id, "EMPTY_CONTENT", "missing choices[0].message.content"); raise ProviderError("empty provider content")
        self.ledger.complete(call_id, parsed)
        return AIMessage(content=text)


@dataclass
class Qwen397ChatArgs:
    model_name: str = MODEL
    base_url: str = "https://api.aa.com.cn/api/v1"
    api_key: str = ""
    ledger_path: str = ""
    raw_response_dir: str = ""
    max_total_tokens: int | None = None
    max_input_tokens: int | None = None
    max_new_tokens: int = MAX_NEW_TOKENS
    temperature: float = TEMPERATURE
    timeout_seconds: float = 120.0

    def make_chat_model(self):
        if not self.api_key or not self.ledger_path or not self.raw_response_dir: raise ProviderError("missing key/ledger/raw response dir")
        return RawProviderChat(self)

    def has_vision(self) -> bool:
        return False
