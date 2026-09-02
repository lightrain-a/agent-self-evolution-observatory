from __future__ import annotations

import asyncio
import hashlib
import json
import time
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LocalOllamaReactReceipt:
    call_index: int
    created_at_utc: str
    requested_model: str
    resolved_model: str
    request_sha256: str
    response_message_sha256: str
    response_id_sha256: str
    provider_status: str
    done_reason: str
    finish_reason: str
    prompt_eval_count: int
    eval_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    temperature_requested: float
    top_p_requested: float
    seed_requested: int
    max_output_tokens: int
    parallel_tool_calls: bool
    tool_call_id_policy: str
    provider_retry_limit: int
    hidden_provider_retry_used: bool
    wall_time_seconds: float


class LocalOllamaReactLLM:
    """Narrow MindMemOS LLMCallable over Ollama's native /api/chat route.

    This is a separate realization from the OpenAI-compatible local adapter. It
    exists only to test whether binding sampler options natively removes the
    score-level reproducibility failure observed through the compatibility
    transport. It is not authorized for historical DeepSeek science.
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
            raise RuntimeError("local Ollama adapter accepts loopback endpoints only")
        self.base_url = base_url.rstrip("/")
        self.requested_model = str(requested_model)
        self.required_resolved_model = str(required_resolved_model)
        self.max_output_tokens = int(max_output_tokens)
        self.seed = int(seed)
        self.timeout_seconds = float(timeout_seconds)
        self.provider_budget_ledger = None
        self.provider_budget_unit_id = None
        self.receipts: list[LocalOllamaReactReceipt] = []

    async def __call__(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return await asyncio.to_thread(self._complete, messages, tools or [])

    @staticmethod
    def _normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out=[]
        for row in messages:
            item={k:v for k,v in row.items() if k in {"role","content","tool_name","images"} and v is not None}
            if row.get("tool_calls"):
                calls=[]
                for call in row["tool_calls"]:
                    fn=call.get("function") or {}
                    raw=fn.get("arguments")
                    try: args=json.loads(raw) if isinstance(raw,str) else raw
                    except Exception: args=raw
                    calls.append({"function":{"name":fn.get("name"),"arguments":args}})
                item["tool_calls"]=calls
            out.append(item)
        return out

    def _complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        payload={
            "model":self.requested_model,
            "messages":self._normalize_messages(messages),
            "tools":tools or None,
            "stream":False,
            "options":{"seed":self.seed,"temperature":0.0,"top_p":1.0,"num_predict":self.max_output_tokens},
        }
        if payload["tools"] is None:
            payload.pop("tools")
        request_sha=_canonical_sha(payload)
        req=urllib.request.Request(self.base_url+"/api/chat",data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"})
        started=time.monotonic()
        with urllib.request.urlopen(req,timeout=self.timeout_seconds) as response:
            raw=json.loads(response.read().decode("utf-8"))
        elapsed=time.monotonic()-started
        resolved=str(raw.get("model") or "")
        if resolved != self.required_resolved_model:
            raise RuntimeError(f"resolved-model-drift: required={self.required_resolved_model};observed={resolved}")
        native=raw.get("message") or {}
        message={"role":"assistant","content":str(native.get("content") or "")}
        calls=[]
        for index,call in enumerate(native.get("tool_calls") or []):
            fn=call.get("function") or {}; args=fn.get("arguments")
            if not isinstance(args,str): args=json.dumps(args or {},ensure_ascii=False,sort_keys=True,separators=(",", ":"))
            stable=f"{request_sha}:{index}".encode("utf-8")
            calls.append({"id":f"call_{hashlib.sha256(stable).hexdigest()[:24]}","type":"function","function":{"name":str(fn.get("name") or ""),"arguments":args},"index":index})
        if calls: message["tool_calls"]=calls
        prompt_tokens=int(raw.get("prompt_eval_count") or 0)
        completion_tokens=int(raw.get("eval_count") or 0)
        done_reason=str(raw.get("done_reason") or "")
        receipt=LocalOllamaReactReceipt(
            call_index=len(self.receipts),created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            requested_model=self.requested_model,resolved_model=resolved,request_sha256=request_sha,
            response_message_sha256=_canonical_sha(message),response_id_sha256=_canonical_sha(raw),
            provider_status="completed",done_reason=done_reason,finish_reason=done_reason,
            prompt_eval_count=prompt_tokens,eval_count=completion_tokens,prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,total_tokens=prompt_tokens+completion_tokens,
            temperature_requested=0.0,top_p_requested=1.0,seed_requested=self.seed,max_output_tokens=self.max_output_tokens,
            parallel_tool_calls=False,tool_call_id_policy="sha256(request_payload):tool_index",provider_retry_limit=0,
            hidden_provider_retry_used=False,wall_time_seconds=elapsed,
        )
        self.receipts.append(receipt)
        return message

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(x) for x in self.receipts]

    def public_budget_claims(self) -> list[dict[str, Any]]:
        return []

    @property
    def receipt_bundle_sha256(self) -> str:
        return _canonical_sha(self.public_receipts())


__all__=["LocalOllamaReactLLM","LocalOllamaReactReceipt"]
