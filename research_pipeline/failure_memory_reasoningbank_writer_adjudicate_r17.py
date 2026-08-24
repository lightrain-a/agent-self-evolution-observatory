#!/usr/bin/env python3
"""Adjudicate the completed B1/L2B R17 writer batch without reading outcomes.

Produces a public hash-only receipt and a private ordered memories.jsonl in the
run root. No downstream BrowserGym episode is executed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

EXPECTED_R13_SHA = "ffbe9baad45ae9e79b9c3eddb8eb54bf57734d6095810e97a45d3cc4b452aa8f"
EXPECTED_R14_SHA = "b0743822c6fe8e06895997bacce8951b26ee00281dcaf68f9bd426920dac3507"
EXPECTED_R15_SHA = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_R16_SHA = "f12b18c129c4e65c076b2f811b65a0a505bf618665f63c87fb883c6d4cf72b4b"
EXPECTED_AUTHORITY_SHA = "83c6801eacb5787606e73eab0c130ce9c4e7130596254ed32eb32b760f76ff64"
EXPECTED_MODEL_MANIFEST = "sha256:9f13ba1299afea09d9a956fc6a85becc99115a6d596fae201a5487a03bdc4368"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def validate_hash(path: Path, expected: str, name: str) -> dict[str, Any]:
    actual = sha_file(path)
    if actual != expected:
        raise RuntimeError(f"{name} SHA drift: {actual} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def adjudicate(run_root: Path, r13: dict[str, Any], r14: dict[str, Any], r15: dict[str, Any], r16: dict[str, Any]) -> dict[str, Any]:
    summary = json.loads((run_root / "summary.json").read_text(encoding="utf-8"))
    progress = read_jsonl(run_root / "progress.jsonl")
    attempts = read_jsonl(run_root / "attempts.jsonl")
    if (run_root / "failure.json").exists():
        raise RuntimeError("R17 failure receipt exists")
    if summary.get("status") != "WRITER_BATCH_COMPLETE" or summary.get("source_tasks_complete") != 36 or summary.get("model_calls_executed") != 36:
        raise RuntimeError("R17 summary is not 36/36 complete")
    if summary.get("downstream_l2_outcomes_opened") is not False:
        raise RuntimeError("R17 opened downstream outcomes")
    if len(progress) != 36 or len(attempts) != 36:
        raise RuntimeError("R17 ledgers must contain exactly 36 rows each")
    if any(x.get("status") != "COMPLETE" or x.get("model_call_count") != 1 for x in progress):
        raise RuntimeError("R17 progress contains non-complete or non-single-call row")
    if any(x.get("status") != "STARTED" or x.get("model_call_count") != 1 for x in attempts):
        raise RuntimeError("R17 attempt ledger invalid")
    pids = [str(x["source_task_id"]) for x in progress]
    aids = [str(x["source_task_id"]) for x in attempts]
    expected_ids = [str(x["source_task_id"]) for x in r13["writer_input_manifest"]]
    if pids != expected_ids or aids != expected_ids:
        raise RuntimeError("R17 source order drift")
    if any(int(x.get("memory_heading_count") or 0) < 1 or int(x.get("memory_heading_count") or 0) > 3 for x in progress):
        raise RuntimeError("R17 memory heading count invalid")
    if r14["prospective_writer_realization"]["manifest_digest"] != EXPECTED_MODEL_MANIFEST:
        raise RuntimeError("R14 model manifest drift")
    if r16["authority_artifact_sha256"] != EXPECTED_AUTHORITY_SHA or r16["status"] != "EXTERNAL_HUMAN_BOUNDED_EXECUTION_AUTHORITY_VALID":
        raise RuntimeError("R16 authority drift")
    if r15["cohort_and_rollouts"]["independent_tasks"] != 36 or r15["cohort_and_rollouts"]["total_terminal_episodes"] != 144:
        raise RuntimeError("R15 execution geometry drift")

    private_records = []
    public_rows = []
    for p in progress:
        tid = str(p["source_task_id"])
        raw_path = run_root / "raw" / f"{tid}.txt"
        mem_path = run_root / "memories" / f"{tid}.json"
        api_path = run_root / "api-responses" / f"{tid}.json"
        for x in (raw_path, mem_path, api_path):
            if not x.is_file():
                raise RuntimeError(f"missing R17 artifact: {x}")
        raw = raw_path.read_bytes()
        mem_bytes = mem_path.read_bytes()
        api_bytes = api_path.read_bytes().rstrip(b"\n")
        if sha_bytes(raw) != p["raw_response_sha256"] or sha_bytes(raw) != p["joined_memory_bytes_sha256"]:
            raise RuntimeError(f"raw/joined memory SHA drift task {tid}")
        if sha_bytes(mem_bytes) != p["memory_record_sha256"]:
            raise RuntimeError(f"memory record SHA drift task {tid}")
        if sha_bytes(api_bytes) != p["api_response_sha256"]:
            raise RuntimeError(f"API response SHA drift task {tid}")
        mem = json.loads(mem_bytes)
        if str(mem["source_task_id"]) != tid or "\n\n".join(mem["memory_items"]).encode("utf-8") != raw:
            raise RuntimeError(f"memory split/join drift task {tid}")
        private_records.append(mem)
        public_rows.append({
            "source_task_id": tid,
            "downstream_task_id": str(p["downstream_task_id"]),
            "native_source_status": str(p["native_source_status"]),
            "request_sha256": p["request_sha256"],
            "writer_request_fingerprint": p["writer_request_fingerprint"],
            "raw_response_sha256": p["raw_response_sha256"],
            "joined_memory_bytes_sha256": p["joined_memory_bytes_sha256"],
            "memory_record_sha256": p["memory_record_sha256"],
            "response_chars": p["response_chars"],
            "memory_heading_count": p["memory_heading_count"],
            "memory_items_count": p["memory_items_count"],
            "prompt_eval_count": p.get("prompt_eval_count"),
            "eval_count": p.get("eval_count"),
            "done_reason": p.get("done_reason"),
        })

    private_data = b"".join((canonical_json(x) + "\n").encode("utf-8") for x in private_records)
    atomic_write(run_root / "memories.jsonl", private_data)
    progress_sha = sha_file(run_root / "progress.jsonl")
    attempts_sha = sha_file(run_root / "attempts.jsonl")
    memories_sha = sha_file(run_root / "memories.jsonl")
    raw_manifest = [{"source_task_id": x["source_task_id"], "raw_response_sha256": x["raw_response_sha256"]} for x in public_rows]

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-WRITER-REALIZATION-R17",
        "recorded_date": "2026-08-24",
        "status": "UNIFORM_36_MEMORY_REALIZATION_COMPLETE_EXACT_BYTES_BOUND",
        "role": "AUTHORIZED_PRE_OUTCOME_WRITER_REALIZATION",
        "bindings": {
            "r13_writer_input_sha256": EXPECTED_R13_SHA,
            "r14_writer_model_sha256": EXPECTED_R14_SHA,
            "r15_executor_contract_sha256": EXPECTED_R15_SHA,
            "r16_execution_authority_sha256": EXPECTED_R16_SHA,
            "external_human_authority_artifact_sha256": EXPECTED_AUTHORITY_SHA,
            "writer_model_manifest": EXPECTED_MODEL_MANIFEST,
        },
        "execution": {
            "source_tasks_expected": 36,
            "source_tasks_complete": 36,
            "model_calls_executed": 36,
            "model_calls_budget": 36,
            "one_call_per_source": True,
            "transport_retries": 0,
            "semantic_retries": 0,
            "failure_receipt_present": False,
            "all_first_complete_responses_frozen": True,
            "downstream_l2_outcomes_opened": False,
        },
        "artifacts": {
            "private_run_root": str(run_root),
            "attempts_jsonl_sha256": attempts_sha,
            "progress_jsonl_sha256": progress_sha,
            "ordered_private_memories_jsonl_sha256": memories_sha,
            "raw_response_manifest_sha256": sha_bytes(canonical_json(raw_manifest).encode("utf-8")),
            "raw_memory_text_embedded_in_public_receipt": False,
        },
        "structure": {
            "heading_count_distribution": {str(k): sum(1 for x in public_rows if x["memory_heading_count"] == k) for k in sorted({x["memory_heading_count"] for x in public_rows})},
            "all_raw_equals_joined_memory_bytes": True,
            "all_memory_records_content_addressed": True,
            "exact_memory_bytes_bound_for_all_36_sources": True,
        },
        "source_memory_manifest": public_rows,
        "downstream_gate": {
            "exact_memory_bytes_bound": True,
            "R15_executor_rollout_analysis_contract_frozen": True,
            "R16_bounded_execution_authority_valid": True,
            "144_terminal_episode_execution_may_begin": True,
            "scientific_claim_support_prejudged": False,
            "l3_unblocked": False,
        },
        "scientific_verdict": "NO_VERDICT_WRITER_REALIZATION_ONLY",
        "scientific_authority": False,
        "authority": {
            "experiment_execution": True,
            "scientific": False,
            "claim_expansion": False,
            "l3": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--r13", type=Path, required=True)
    p.add_argument("--r14", type=Path, required=True)
    p.add_argument("--r15", type=Path, required=True)
    p.add_argument("--r16", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-writer-realization-r17.json"))
    a = p.parse_args()
    r13 = validate_hash(a.r13, EXPECTED_R13_SHA, "R13")
    r14 = validate_hash(a.r14, EXPECTED_R14_SHA, "R14")
    r15 = validate_hash(a.r15, EXPECTED_R15_SHA, "R15")
    r16 = validate_hash(a.r16, EXPECTED_R16_SHA, "R16")
    out = adjudicate(a.run_root, r13, r14, r15, r16)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(a.output, (json.dumps(out, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": out["status"],
        "complete": out["execution"]["source_tasks_complete"],
        "calls": out["execution"]["model_calls_executed"],
        "memories_sha256": out["artifacts"]["ordered_private_memories_jsonl_sha256"],
        "downstream_may_begin": out["downstream_gate"]["144_terminal_episode_execution_may_begin"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
