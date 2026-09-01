"""Content-address and qualify the frozen local Qwen retrieval embedding snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)

MODEL_ID = "Qwen/Qwen3-Embedding-8B"
REVISION = "1d8ad4ca9b3dd8059ad90a75d4983776a23d44af"
SNAPSHOT = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-qwen3-embedding-8b-1d8ad4ca9b3dd8059ad90a75d4983776a23d44af"
)
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-embedding-snapshot-receipt-20260901.json"
EXPECTED_FILES = (
    ".gitattributes", "1_Pooling/config.json", "LICENSE", "README.md", "config.json",
    "config_sentence_transformers.json", "generation_config.json", "merges.txt",
    "model-00001-of-00004.safetensors", "model-00002-of-00004.safetensors",
    "model-00003-of-00004.safetensors", "model-00004-of-00004.safetensors",
    "model.safetensors.index.json", "modules.json", "tokenizer.json",
    "tokenizer_config.json", "vocab.json",
)


def revision_metadata(snapshot: Path) -> set[str]:
    values = set()
    cache = snapshot / ".cache/huggingface/download"
    for path in cache.rglob("*.metadata"):
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines:
            values.add(lines[0].strip())
    return values


def verify_snapshot(snapshot: Path = SNAPSHOT) -> dict[str, Any]:
    actual = tuple(sorted(
        str(path.relative_to(snapshot))
        for path in snapshot.rglob("*")
        if path.is_file() and ".cache" not in path.parts
    ))
    expected = tuple(sorted(EXPECTED_FILES))
    if actual != expected:
        raise RuntimeError("embedding snapshot file inventory drift")
    revisions = revision_metadata(snapshot)
    if revisions != {REVISION}:
        raise RuntimeError("embedding snapshot revision metadata drift")
    rows = []
    for relative in expected:
        path = snapshot / relative
        rows.append({
            "path": relative, "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    index = json.loads((snapshot / "model.safetensors.index.json").read_text())
    shards = sorted(set(index["weight_map"].values()))
    expected_shards = [f"model-{index:05d}-of-00004.safetensors" for index in range(1, 5)]
    checks = {
        "revision_exact": True, "file_inventory_exact": True,
        "four_weight_shards_exact": shards == expected_shards,
        "all_file_sha256_recorded": all(len(row["sha256"]) == 64 for row in rows),
        "model_not_loaded_during_byte_qualification": True,
        "retrieval_vectors_not_computed": True,
    }
    if not all(checks.values()):
        raise RuntimeError("embedding snapshot byte qualification failed")
    return {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901",
        "stage": "RETRIEVAL_EMBEDDING_SNAPSHOT_BYTE_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN3_EMBEDDING_8B_FIXED_SNAPSHOT_BYTE_QUALIFIED",
        "model_id": MODEL_ID, "revision": REVISION,
        "download_route": "hf-mirror", "snapshot_path": str(snapshot),
        "files": rows, "file_count": len(rows),
        "total_size_bytes": sum(row["size_bytes"] for row in rows),
        "weight_shards": shards, "checks": checks,
        "scientific_boundary": {
            "embedding_model_loaded": False, "retrieval_executed": False,
            "policy_model_calls": 0, "behavioral_outcomes_observed": False,
        },
        "credential_material_present": False,
    }


def write_receipt(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite embedding snapshot receipt")
    payload = verify_snapshot()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "file_count": payload["file_count"],
            "total_size_bytes": payload["total_size_bytes"]}


if __name__ == "__main__":
    print(json.dumps(write_receipt(), sort_keys=True))
