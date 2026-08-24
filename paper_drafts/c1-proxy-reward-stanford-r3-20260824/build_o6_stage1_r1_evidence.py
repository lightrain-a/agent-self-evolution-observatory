#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_CONTRACT_SHA = "16be37f6419a8ec36a214fb09dac1c96117e6607b8a97cd8d649c6cf4a690e72"
EXPECTED_AUTH_SHA = "52895af2094b1277fae551a45f9bf4df2283b482b27926fe32a3cccd9ffa100a"
EXPECTED_RESULT_SHA = "85662afcc1a49b9d51e8ea5b22c6a30e85749c37828513a9e45d08070d8a0bf2"
EXPECTED_REPAIR_DESIGN_SHA = "19b3ea55704f4774405713f285b29d53f0ece7d78f9299fbb81ae86939f879b8"
EXPECTED_PARENT_FAILURE_SHA = "f7c204ea3f68a87082c729d5f6206077e04d995c93242af8baf8caa803bf7112"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True, type=Path)
    ap.add_argument("--repair-design", required=True, type=Path)
    ap.add_argument("--parent-failure", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    paths = {
        "contract": args.run_root / "o6-stage1-r1-contract.json",
        "authorization": args.run_root / "o6-stage1-r1-authorization-receipt.json",
        "result": args.run_root / "o6-stage1-r1-result.json",
    }
    expected = {"contract": EXPECTED_CONTRACT_SHA, "authorization": EXPECTED_AUTH_SHA, "result": EXPECTED_RESULT_SHA}
    for key, path in paths.items():
        if not path.is_file() or sha(path) != expected[key]:
            raise RuntimeError(f"Stage-1 R1 {key} binding mismatch")
    if sha(args.repair_design) != EXPECTED_REPAIR_DESIGN_SHA:
        raise RuntimeError("R1 repair design SHA drift")
    if sha(args.parent_failure) != EXPECTED_PARENT_FAILURE_SHA:
        raise RuntimeError("parent Stage-1 failure asset SHA drift")

    result = load(paths["result"])
    contract = load(paths["contract"])
    parent_failure = load(args.parent_failure)
    summary = result["summary"]
    if result["status"] != "O6_STAGE1_COMPLETE" or result["decision"] != "ADVANCE_TO_CROSS_WRITER_TERMINAL_STAGE2":
        raise RuntimeError("Stage-1 R1 did not reach the frozen advance decision")
    required = {
        "requested_provider_calls": 8,
        "complete_provider_calls": 8,
        "complete_pairs": 4,
        "exact_content_changed_pairs": 4,
        "title_set_changed_pairs": 4,
        "stage1_gate_pass": True,
    }
    for key, value in required.items():
        if summary.get(key) != value:
            raise RuntimeError(f"Stage-1 R1 summary drift: {key}")

    private = args.run_root / "private"
    stage_files = sorted((private / "stages").glob("*.json"))
    response_files = sorted((private / "provider-responses").glob("*.json"))
    raw_files = sorted((private / "raw").rglob("*.txt"))
    if not (len(stage_files) == len(response_files) == len(raw_files) == 8):
        raise RuntimeError("Stage-1 R1 receipt/raw cardinality mismatch")

    memory_rows = []
    seen_sha: set[str] = set()
    for pair in result["pairs"]:
        if not pair.get("complete_pair") or not pair.get("exact_content_changed") or not pair.get("title_set_changed"):
            raise RuntimeError(f"Stage-1 R1 pair gate drift: {pair.get('task_id')}")
        for label, key in (("success_label_memory", "success_memory_sha256"), ("failure_label_memory", "failure_memory_sha256")):
            digest = str(pair[key])
            raw = private / "raw" / digest[:2] / f"{digest}.txt"
            if not raw.is_file() or sha(raw) != digest:
                raise RuntimeError(f"Stage-1 R1 raw memory binding mismatch: {pair['task_id']} {label}")
            seen_sha.add(digest)
            memory_rows.append({"source_memory_task": str(pair["task_id"]), "condition": label, "raw_sha256": digest, "raw_path": str(raw.resolve())})
    if len(seen_sha) != 8:
        raise RuntimeError("Stage-1 R1 memories are not eight unique content-addressed objects")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "o6-cross-writer-stage1-r1-handoff",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "objection_id": "PROXY-O6",
        "status": "STAGE1_R1_PASS_READY_FOR_SEPARATE_STAGE2_CONTRACT",
        "bindings": {
            "repair_design_sha256": EXPECTED_REPAIR_DESIGN_SHA,
            "parent_failure_asset_sha256": EXPECTED_PARENT_FAILURE_SHA,
            "contract_sha256": EXPECTED_CONTRACT_SHA,
            "authorization_sha256": EXPECTED_AUTH_SHA,
            "result_sha256": EXPECTED_RESULT_SHA,
        },
        "summary": dict(summary),
        "memory_objects": memory_rows,
        "pair_results": result["pairs"],
        "execution_accounting": {
            "parent_2200_provider_posts_exact": None,
            "parent_2200_provider_posts_observable_lower_bound": parent_failure["execution_concurrency_failure"]["provider_post_count_observable_lower_bound"],
            "parent_2200_scientific_stage_pass": False,
            "r1_4096_provider_calls": 8,
            "r1_4096_scientifically_usable_calls": 8,
            "r1_resume_reused_cached_calls": 6,
            "r1_resume_new_calls": 2,
        },
        "stage2_gate_inherited_unchanged": contract["stage2_preregistered_gate"],
        "stage2_provider_calls_authorized_by_handoff": 0,
        "stage2_requires_separate_execution_contract": True,
        "claim_boundary": {
            "write_channel_cross_writer_supported_on_four_sources": True,
            "terminal_cross_writer_supported": False,
            "writer_population_generalization_supported": False,
            "domain_generalization_supported": False,
        },
        "scientific_authority": False,
        "claim_expansion_authority": False,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "memories": len(payload["memory_objects"]), "stage2_gate": payload["stage2_gate_inherited_unchanged"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
