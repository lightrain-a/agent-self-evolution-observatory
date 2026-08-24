#!/usr/bin/env python3
"""Execute the authorized 36-source B1/L2B ReasoningBank writer realization.

The run is append-only and resumable. A source task is called at most once.
No semantic output selection or regeneration is allowed. If any response fails
the frozen structural contract, the batch stops and downstream L2B execution
remains locked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.failure_memory_reasoningbank_execution_authority_r16 import require_authority
from research_pipeline.failure_memory_reasoningbank_writer_input_r13 import (
    EXPECTED_PARQUET_SHA256,
    extract_constants,
    load_parquet,
    parse_trajectory,
    serialize_trace,
    sha_file,
)

EXPECTED_R13_SHA = "ffbe9baad45ae9e79b9c3eddb8eb54bf57734d6095810e97a45d3cc4b452aa8f"
EXPECTED_R14_SHA = "b0743822c6fe8e06895997bacce8951b26ee00281dcaf68f9bd426920dac3507"
EXPECTED_R15_SHA = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_R16_SHA = "f12b18c129c4e65c076b2f811b65a0a505bf618665f63c87fb883c6d4cf72b4b"
EXPECTED_MODEL_MANIFEST = "sha256:9f13ba1299afea09d9a956fc6a85becc99115a6d596fae201a5487a03bdc4368"
MODEL_TAG = "qwen2.5:32b"
MODEL_TEMPERATURE = 0.0
MODEL_SEED = 0
MODEL_NUM_CTX = 32768
MODEL_NUM_PREDICT = 2048
MAX_REQUESTS = 36


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def validate_receipt_hash(path: Path, expected: str, label: str) -> dict[str, Any]:
    actual = sha_file(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA drift: {actual} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def structural_parse(response: str) -> dict[str, Any]:
    if not response or not response.strip():
        raise RuntimeError("empty writer response")
    headings = list(re.finditer(r"(?m)^# Memory Item\s+(\d+)\s*$", response))
    if not (1 <= len(headings) <= 3):
        raise RuntimeError(f"writer response must contain 1-3 memory headings, found {len(headings)}")
    nums = [int(m.group(1)) for m in headings]
    if nums != list(range(1, len(nums) + 1)):
        raise RuntimeError(f"memory headings must be sequential from 1: {nums}")
    blocks = []
    for i, m in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(response)
        block = response[m.start():end]
        for marker in ["## Title", "## Description", "## Content"]:
            if marker not in block:
                raise RuntimeError(f"memory item {i+1} missing {marker}")
        blocks.append(block)
    memory_items = response.split("\n\n")
    if "\n\n".join(memory_items) != response:
        raise RuntimeError("memory_items split/join roundtrip failed")
    return {
        "heading_count": len(headings),
        "heading_numbers": nums,
        "memory_items_count": len(memory_items),
        "memory_items": memory_items,
    }


def post_json(url: str, payload: dict[str, Any], timeout: int = 600) -> dict[str, Any]:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=raw, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    obj = json.loads(body)
    if not isinstance(obj, dict):
        raise RuntimeError("Ollama response root is not an object")
    return obj


def get_json(url: str, timeout: int = 10) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def reconstruct_inputs(r13: dict[str, Any], parquet: Path, prompt_file: Path) -> list[dict[str, Any]]:
    if sha_file(parquet) != EXPECTED_PARQUET_SHA256:
        raise RuntimeError("frozen parquet SHA drift")
    rows = load_parquet(parquet)
    by_id = {str(x.get("task_id")): x for x in rows}
    prompts = extract_constants(prompt_file)
    out = []
    manifest = r13["writer_input_manifest"]
    if len(manifest) != 36:
        raise RuntimeError("R13 manifest must contain 36 sources")
    for item in manifest:
        tid = str(item["source_task_id"])
        row = by_id.get(tid)
        if row is None:
            raise RuntimeError(f"source task missing from parquet: {tid}")
        task_prompt = str(row.get("task_prompt") or "")
        trajectory, raw = parse_trajectory(row.get("trajectory_json"))
        compact = serialize_trace(task_prompt, trajectory)
        system_name = str(item["system_prompt"])
        system_prompt = prompts[system_name]
        checks = {
            "task_prompt_sha256": sha_bytes(task_prompt.encode()),
            "raw_trajectory_json_sha256": sha_bytes(raw),
            "compact_trace_sha256": sha_bytes(compact.encode()),
            "system_prompt_sha256": sha_bytes(system_prompt.encode()),
            "writer_request_fingerprint": sha_bytes((system_prompt + "\n\0\n" + compact).encode()),
        }
        for k, actual in checks.items():
            if actual != item[k]:
                raise RuntimeError(f"R13 input drift task={tid} field={k}: {actual} != {item[k]}")
        out.append({
            "source_task_id": tid,
            "downstream_task_id": str(item["downstream_task_id"]),
            "template_id": str(item["template_id"]),
            "native_source_status": str(item["native_source_status"]),
            "system_prompt_name": system_name,
            "system_prompt": system_prompt,
            "compact_trace": compact,
            "writer_request_fingerprint": item["writer_request_fingerprint"],
        })
    return out


def read_progress(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def execute(args: argparse.Namespace) -> dict[str, Any]:
    authority = require_authority(args.authority)
    r13 = validate_receipt_hash(args.r13, EXPECTED_R13_SHA, "R13")
    r14 = validate_receipt_hash(args.r14, EXPECTED_R14_SHA, "R14")
    validate_receipt_hash(args.r15, EXPECTED_R15_SHA, "R15")
    validate_receipt_hash(args.r16, EXPECTED_R16_SHA, "R16")
    if r14["prospective_writer_realization"]["manifest_digest"] != EXPECTED_MODEL_MANIFEST:
        raise RuntimeError("R14 model manifest drift")
    if authority["budgets"]["writer_request_budget"] != MAX_REQUESTS:
        raise RuntimeError("authority writer budget drift")

    tags = get_json(args.ollama.rstrip("/") + "/api/tags")
    found = {x.get("name"): x for x in tags.get("models", [])}
    if MODEL_TAG not in found:
        raise RuntimeError(f"pinned writer model not present: {MODEL_TAG}")
    if str(found[MODEL_TAG].get("digest")) != EXPECTED_MODEL_MANIFEST.removeprefix("sha256:"):
        raise RuntimeError("live Ollama model digest drift")

    inputs = reconstruct_inputs(r13, args.source_parquet, args.prompt_file)
    run_root = args.run_root
    run_root.mkdir(parents=True, exist_ok=True)
    progress_path = run_root / "progress.jsonl"
    attempts_path = run_root / "attempts.jsonl"
    existing = read_progress(progress_path)
    attempts = read_progress(attempts_path)
    completed_ids = [str(x["source_task_id"]) for x in existing if x.get("status") == "COMPLETE"]
    attempted_ids = [str(x["source_task_id"]) for x in attempts if x.get("status") == "STARTED"]
    if len(completed_ids) != len(set(completed_ids)):
        raise RuntimeError("duplicate completed source in progress ledger")
    if len(attempted_ids) != len(set(attempted_ids)):
        raise RuntimeError("duplicate source in attempt ledger")
    known = {x["source_task_id"] for x in inputs}
    if not set(completed_ids).issubset(known) or not set(attempted_ids).issubset(known):
        raise RuntimeError("progress/attempt ledger contains unknown source task")
    if any(x.get("status") != "COMPLETE" for x in existing):
        raise RuntimeError("progress contains prior failed/partial row; batch is fail-closed")
    uncertain = sorted(set(attempted_ids) - set(completed_ids), key=int)
    if uncertain:
        raise RuntimeError(f"source tasks have a prior STARTED call without durable COMPLETE; automatic retry forbidden: {uncertain}")
    if set(completed_ids) != set(attempted_ids):
        raise RuntimeError("complete/attempt ledger mismatch")

    preflight = {
        "schema_version": "1.0",
        "run_id": run_root.name,
        "created_at": now(),
        "status": "WRITER_BATCH_IN_PROGRESS" if len(completed_ids) < 36 else "WRITER_BATCH_COMPLETE",
        "authority_artifact_sha256": authority["artifact_sha256"],
        "bindings": {"r13": EXPECTED_R13_SHA, "r14": EXPECTED_R14_SHA, "r15": EXPECTED_R15_SHA, "r16": EXPECTED_R16_SHA},
        "model": {"tag": MODEL_TAG, "manifest": EXPECTED_MODEL_MANIFEST, "temperature": MODEL_TEMPERATURE, "seed": MODEL_SEED, "num_ctx": MODEL_NUM_CTX, "num_predict": MODEL_NUM_PREDICT},
        "policy": {"one_call_per_source_max": True, "semantic_retry": False, "transport_retry": False, "total_writer_call_budget": 36, "downstream_outcomes_allowed_in_this_runner": False},
        "source_tasks": [x["source_task_id"] for x in inputs],
        "already_complete": completed_ids,
    }
    atomic_json(run_root / "run-contract.json", preflight)

    remaining = [x for x in inputs if x["source_task_id"] not in set(completed_ids)]
    limit = len(remaining) if args.max_new is None else min(args.max_new, len(remaining))
    new_calls = 0
    for item in remaining[:limit]:
        tid = item["source_task_id"]
        if len(attempted_ids) + new_calls >= MAX_REQUESTS:
            raise RuntimeError("writer request budget exhausted")
        input_record = {
            "source_task_id": tid,
            "downstream_task_id": item["downstream_task_id"],
            "template_id": item["template_id"],
            "native_source_status": item["native_source_status"],
            "system_prompt_name": item["system_prompt_name"],
            "system_prompt_sha256": sha_bytes(item["system_prompt"].encode()),
            "compact_trace_sha256": sha_bytes(item["compact_trace"].encode()),
            "writer_request_fingerprint": item["writer_request_fingerprint"],
            "system_prompt": item["system_prompt"],
            "compact_trace": item["compact_trace"],
        }
        atomic_json(run_root / "inputs" / f"{tid}.json", input_record)
        request_obj = {
            "model": MODEL_TAG,
            "messages": [
                {"role": "system", "content": item["system_prompt"]},
                {"role": "user", "content": item["compact_trace"]},
            ],
            "stream": False,
            "options": {"temperature": MODEL_TEMPERATURE, "seed": MODEL_SEED, "num_ctx": MODEL_NUM_CTX, "num_predict": MODEL_NUM_PREDICT},
            "keep_alive": "30m",
        }
        request_sha = sha_bytes(canonical_json(request_obj).encode())
        started = now()
        append_jsonl(attempts_path, {
            "source_task_id": tid,
            "status": "STARTED",
            "started_at": started,
            "request_sha256": request_sha,
            "writer_request_fingerprint": item["writer_request_fingerprint"],
            "model": MODEL_TAG,
            "model_call_count": 1,
        })
        try:
            response_obj = post_json(args.ollama.rstrip("/") + "/api/chat", request_obj, timeout=args.timeout)
        except Exception as exc:
            failure = {"source_task_id": tid, "status": "FAILED_TRANSPORT", "started_at": started, "failed_at": now(), "request_sha256": request_sha, "error_class": type(exc).__name__, "error": str(exc)[:1000], "model_call_count": 1}
            atomic_json(run_root / "failure.json", failure)
            raise RuntimeError(f"writer transport failure at task {tid}; no retry permitted") from exc
        new_calls += 1
        raw_api = canonical_json(response_obj).encode("utf-8")
        (run_root / "api-responses").mkdir(parents=True, exist_ok=True)
        (run_root / "api-responses" / f"{tid}.json").write_bytes(raw_api + b"\n")
        message = response_obj.get("message") or {}
        response = message.get("content")
        if not isinstance(response, str):
            failure = {"source_task_id": tid, "status": "FAILED_STRUCTURE", "failed_at": now(), "request_sha256": request_sha, "api_response_sha256": sha_bytes(raw_api), "error": "missing string message.content", "model_call_count": 1}
            atomic_json(run_root / "failure.json", failure)
            raise RuntimeError(f"writer structure failure at task {tid}; no retry permitted")
        raw_bytes = response.encode("utf-8")
        (run_root / "raw").mkdir(parents=True, exist_ok=True)
        (run_root / "raw" / f"{tid}.txt").write_bytes(raw_bytes)
        try:
            parsed = structural_parse(response)
        except Exception as exc:
            failure = {"source_task_id": tid, "status": "FAILED_STRUCTURE", "failed_at": now(), "request_sha256": request_sha, "raw_response_sha256": sha_bytes(raw_bytes), "error_class": type(exc).__name__, "error": str(exc)[:1000], "model_call_count": 1}
            atomic_json(run_root / "failure.json", failure)
            raise RuntimeError(f"writer structure failure at task {tid}; no retry permitted") from exc
        joined = "\n\n".join(parsed["memory_items"])
        joined_bytes = joined.encode("utf-8")
        if joined_bytes != raw_bytes:
            raise RuntimeError("joined memory bytes differ from raw writer response")
        memory_obj = {
            "source_task_id": tid,
            "downstream_task_id": item["downstream_task_id"],
            "template_id": item["template_id"],
            "status": item["native_source_status"],
            "memory_items": parsed["memory_items"],
        }
        memory_bytes = (canonical_json(memory_obj) + "\n").encode("utf-8")
        (run_root / "memories").mkdir(parents=True, exist_ok=True)
        (run_root / "memories" / f"{tid}.json").write_bytes(memory_bytes)
        row = {
            "source_task_id": tid,
            "downstream_task_id": item["downstream_task_id"],
            "status": "COMPLETE",
            "native_source_status": item["native_source_status"],
            "completed_at": now(),
            "model_call_count": 1,
            "request_sha256": request_sha,
            "writer_request_fingerprint": item["writer_request_fingerprint"],
            "api_response_sha256": sha_bytes(raw_api),
            "raw_response_sha256": sha_bytes(raw_bytes),
            "joined_memory_bytes_sha256": sha_bytes(joined_bytes),
            "memory_record_sha256": sha_bytes(memory_bytes),
            "response_chars": len(response),
            "memory_heading_count": parsed["heading_count"],
            "memory_items_count": parsed["memory_items_count"],
            "prompt_eval_count": response_obj.get("prompt_eval_count"),
            "eval_count": response_obj.get("eval_count"),
            "done_reason": response_obj.get("done_reason"),
        }
        append_jsonl(progress_path, row)

    all_progress = read_progress(progress_path)
    complete = [x for x in all_progress if x.get("status") == "COMPLETE"]
    summary = {
        "schema_version": "1.0",
        "run_id": run_root.name,
        "updated_at": now(),
        "status": "WRITER_BATCH_COMPLETE" if len(complete) == 36 else "WRITER_BATCH_PARTIAL_PRECHECK",
        "source_tasks_expected": 36,
        "source_tasks_complete": len(complete),
        "model_calls_executed": sum(int(x.get("model_call_count") or 0) for x in complete),
        "all_source_ids": [x["source_task_id"] for x in inputs],
        "complete_source_ids": [x["source_task_id"] for x in complete],
        "downstream_l2_outcomes_opened": False,
        "execution_permitted": len(complete) == 36 and not (run_root / "failure.json").exists(),
    }
    atomic_json(run_root / "summary.json", summary)
    return summary


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--r13", type=Path, required=True)
    p.add_argument("--r14", type=Path, required=True)
    p.add_argument("--r15", type=Path, required=True)
    p.add_argument("--r16", type=Path, required=True)
    p.add_argument("--source-parquet", type=Path, required=True)
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--ollama", default="http://127.0.0.1:11444")
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--max-new", type=int, default=None)
    a = p.parse_args()
    s = execute(a)
    print(json.dumps(s, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
