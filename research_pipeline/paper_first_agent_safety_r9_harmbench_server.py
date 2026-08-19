from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

MODEL_ID = "cais/HarmBench-Llama-2-13b-cls"
MODEL_REVISION = "0cd31cdc8b53209dd5b153b20026ff085901bb14"
PROMPT_SOURCE_REL = "src/behavior_classifier/behavior_classifier/harmbench_classifier.py"
PROMPT_SOURCE_SHA256 = "a62fda90ff8a983af378e6805afc0cac6cb45fd2cd6ce8db433bdacf1deaa214"


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_prompt_templates(browserart_root: Path) -> dict[str, str]:
    source = browserart_root / PROMPT_SOURCE_REL
    if _sha_file(source) != PROMPT_SOURCE_SHA256:
        raise RuntimeError("frozen BrowserART HarmBench source digest drift")
    spec = importlib.util.spec_from_file_location("r9_frozen_harmbench_classifier", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen BrowserART HarmBench source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(module.HarmbenchClassifier.LLAMA2_CLS_PROMPT)


def _format_prompt(templates: dict[str, str], payload: dict[str, Any]) -> str:
    behavior = str(payload.get("behavior") or "")
    context = str(payload.get("context") or "")
    generation = str(payload.get("text_output") or "")
    if not behavior:
        raise ValueError("behavior is required")
    if context:
        return templates["prompt_contextual"].format(behavior=behavior, context=context, generation=generation)
    return templates["prompt"].format(behavior=behavior, generation=generation)


def _tokenization_kwargs(max_model_len: int, max_output_tokens: int) -> dict[str, Any]:
    max_prompt_tokens = int(max_model_len) - int(max_output_tokens)
    if max_prompt_tokens <= 0:
        raise ValueError("invalid HarmBench prompt budget")
    return {"max_length": max_prompt_tokens, "truncation": True}


def _llm_kwargs(model_dir: Path, gpu_memory_utilization: float) -> dict[str, Any]:
    return {
        "model": str(model_dir),
        "tokenizer": str(model_dir),
        "tokenizer_mode": "slow",
        "dtype": "bfloat16",
        "tensor_parallel_size": 2,
        "gpu_memory_utilization": gpu_memory_utilization,
    }


def serve(args: argparse.Namespace) -> None:
    from vllm import LLM, SamplingParams

    model_dir = Path(args.model_dir)
    marker = json.loads((model_dir / ".r9-model-revision.json").read_text(encoding="utf-8"))
    if marker.get("model_id") != MODEL_ID or marker.get("revision") != MODEL_REVISION:
        raise RuntimeError("HarmBench local model provenance marker mismatch")
    templates = _load_prompt_templates(Path(args.browserart_root))

    llm = LLM(**_llm_kwargs(model_dir, args.gpu_memory_utilization))
    tokenizer = llm.get_tokenizer()
    if getattr(tokenizer, "truncation_side", None) != "left":
        raise RuntimeError("HarmBench tokenizer truncation_side must remain left")
    sampling = SamplingParams(temperature=0.0, max_tokens=1)
    tokenization_kwargs = _tokenization_kwargs(llm.model_config.max_model_len, sampling.max_tokens)
    lock = threading.Lock()
    counter = {"classifications": int(args.initial_classifications)}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *values: Any) -> None:
            return

        def _send(self, code: int, value: dict[str, Any]) -> None:
            raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path != "/health":
                self._send(404, {"status": "not_found"})
                return
            self._send(200, {
                "status": "READY_HARMBENCH_TP2_SERVICE",
                "model_id": MODEL_ID,
                "revision": MODEL_REVISION,
                "tensor_parallel_size": 2,
                "temperature": 0.0,
                "max_tokens": 1,
                "prompt_truncation": "left-to-model-context-minus-output",
                "max_prompt_tokens": tokenization_kwargs["max_length"],
                "classifications": counter["classifications"],
            })

        def do_POST(self) -> None:
            if self.path != "/classify":
                self._send(404, {"status": "not_found"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 2_000_000:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(size))
                prompt = _format_prompt(templates, payload)
                with lock:
                    output = llm.generate(
                        [prompt], sampling, use_tqdm=False, tokenization_kwargs=tokenization_kwargs
                    )[0].outputs[0].text
                    counter["classifications"] += 1
                if output in ("YES", "Yes", "yes"):
                    prediction: int | str = 1
                elif output in ("NO", "No", "no"):
                    prediction = 0
                else:
                    prediction = output
                self._send(200, {
                    "status": "HARMBENCH_CLASSIFICATION_COMPLETE",
                    "request_id": str(payload.get("request_id") or ""),
                    "prediction": prediction,
                    "raw_label": output,
                    "model_id": MODEL_ID,
                    "revision": MODEL_REVISION,
                    "tensor_parallel_size": 2,
                })
            except Exception as error:
                self._send(400, {"status": "classification_error", "error_type": type(error).__name__, "error": str(error)[:500]})

    ready = Path(args.ready_file)
    ready.parent.mkdir(parents=True, exist_ok=True)
    ready.write_text(json.dumps({
        "status": "READY_HARMBENCH_TP2_SERVICE",
        "bind": f"{args.host}:{args.port}",
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "tensor_parallel_size": 2,
        "prompt_source_sha256": PROMPT_SOURCE_SHA256,
        "temperature": 0.0,
        "max_tokens": 1,
        "prompt_truncation": "left-to-model-context-minus-output",
        "max_prompt_tokens": tokenization_kwargs["max_length"],
        "fallback_allowed": False,
        "scientific_authority": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    HTTPServer((args.host, args.port), Handler).serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--browserart-root", required=True)
    parser.add_argument("--ready-file", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18001)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    parser.add_argument("--initial-classifications", type=int, default=0)
    serve(parser.parse_args())


if __name__ == "__main__":
    main()
