"""Loopback-only OpenAI-compatible server for R45-M1 on host 231.

Only physical model roots and the embedding device differ from the forensic
R43 server. Model bytes, IDs, temperature, token limit, pooling, and the 3072
isometric bridge remain frozen. This module contains no benchmark logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from failure_memory_memrl_local_runtime_r43 import LocalMPNetEmbedder, LocalQwenProvider

LLM_MODEL_ID = "B1-Qwen2.5-7B-Instruct-r43"
EMBED_MODEL_ID = "B1-all-mpnet-base-v2-isometric3072-r43"
LLM_ROOT = Path("/data/lry/models/Qwen2.5-7B-Instruct")
EMBED_ROOT = Path("/data/wyt/models/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130")


def _flatten_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text") or ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content or "")


class Runtime:
    def __init__(self) -> None:
        self.llm = LocalQwenProvider(model_root=LLM_ROOT, device="cuda:0", max_new_tokens=512)
        self.embedder = LocalMPNetEmbedder(model_root=EMBED_ROOT, device="cuda:0", output_dimension=3072)

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        model = str(payload.get("model") or LLM_MODEL_ID)
        if model != LLM_MODEL_ID:
            raise ValueError(f"unsupported chat model:{model}")
        messages = [
            {"role": str(row.get("role") or "user"), "content": _flatten_content(row.get("content"))}
            for row in (payload.get("messages") or [])
            if isinstance(row, dict)
        ]
        if not messages:
            raise ValueError("messages required")
        before = self.llm.get_token_usage()
        text = self.llm.generate(
            messages,
            temperature=float(payload.get("temperature") or 0.0),
            max_tokens=int(payload.get("max_tokens") or payload.get("max_completion_tokens") or 512),
        )
        after = self.llm.get_token_usage()
        prompt_tokens = int(after["prompt_tokens"] - before["prompt_tokens"])
        completion_tokens = int(after["completion_tokens"] - before["completion_tokens"])
        request_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:20]
        return {
            "id": f"chatcmpl-b1-{request_hash}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": LLM_MODEL_ID,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens},
        }

    def embeddings(self, payload: dict[str, Any]) -> dict[str, Any]:
        model = str(payload.get("model") or EMBED_MODEL_ID)
        if model != EMBED_MODEL_ID:
            raise ValueError(f"unsupported embedding model:{model}")
        raw = payload.get("input")
        texts = [raw] if isinstance(raw, str) else list(raw or [])
        if not texts or any(not isinstance(x, str) for x in texts):
            raise ValueError("embedding input must be string or list of strings")
        vectors = self.embedder.embed(texts)
        return {
            "object": "list",
            "data": [{"object": "embedding", "index": i, "embedding": vector} for i, vector in enumerate(vectors)],
            "model": EMBED_MODEL_ID,
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        }


class Handler(BaseHTTPRequestHandler):
    runtime: Runtime
    server_version = "B1R45M1LocalOpenAI/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.rstrip("/") in {"/v1/models", "/models"}:
            self._json(200, {"object": "list", "data": [
                {"id": LLM_MODEL_ID, "object": "model", "owned_by": "local-b1-r43"},
                {"id": EMBED_MODEL_ID, "object": "model", "owned_by": "local-b1-r43"},
            ]})
            return
        if self.path.rstrip("/") in {"/health", "/v1/health"}:
            self._json(200, {"status": "ok", "llm": LLM_MODEL_ID, "embedding": EMBED_MODEL_ID})
            return
        self._json(404, {"error": {"message": "not found", "type": "not_found"}})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
            path = self.path.rstrip("/")
            if path in {"/v1/chat/completions", "/chat/completions"}:
                self._json(200, self.runtime.chat(payload))
                return
            if path in {"/v1/embeddings", "/embeddings"}:
                self._json(200, self.runtime.embeddings(payload))
                return
            self._json(404, {"error": {"message": "not found", "type": "not_found"}})
        except Exception as exc:
            self._json(400, {"error": {"message": str(exc), "type": type(exc).__name__}})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18143)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("B1 R45-M1 server is loopback-only")
    Handler.runtime = Runtime()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"status": "READY", "host": args.host, "port": args.port, "llm": LLM_MODEL_ID, "embedding": EMBED_MODEL_ID}, sort_keys=True), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
