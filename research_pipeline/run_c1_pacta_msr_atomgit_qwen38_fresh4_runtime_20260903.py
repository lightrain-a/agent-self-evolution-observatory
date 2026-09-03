#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import run_c1_pacta_msr_runtime_20260902 as base
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_runtime_20260903 as fresh3_runtime
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file

IMAGE_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-images-20260903-v1")
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-runtime-20260903-v1")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/c1-pacta-msr-atomgit-qwen38-fresh4-oci-layouts")
POOL_SHA = "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"
MANIFEST_SHA = "8b84467e67bc4c514a921f53515b50741a7427051941671084e2263e5f95d91f"
BLOB_PLAN_SHA = "5e7bddd3772f43c2e9bd3dd8895c3bb7039fe90952934aaa42db7286eda76478"
UNIQUE_BLOB_COUNT = 86
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def bind(blob_receipt_sha: str) -> None:
    if not SHA_RE.fullmatch(blob_receipt_sha):
        raise RuntimeError("STOP_FRESH4_BLOB_RECEIPT_SHA_FORMAT")
    base.IMAGE_ROOT = IMAGE_ROOT
    base.DEFAULT = DEFAULT_ROOT
    base.LAYOUT_ROOT = LAYOUT_ROOT
    base.MANIFEST_SHA = MANIFEST_SHA
    base.BLOB_RECEIPT_SHA = blob_receipt_sha


def audit_inputs(blob_receipt_sha: str) -> dict[str, Any]:
    bind(blob_receipt_sha)
    expected = {
        "manifest-freeze.json": MANIFEST_SHA,
        "blob-plan.json": BLOB_PLAN_SHA,
        "blob-receipt.json": blob_receipt_sha,
    }
    observed: dict[str, str] = {}
    for name, expected_sha in expected.items():
        path = IMAGE_ROOT / name
        if not path.is_file():
            raise RuntimeError(f"STOP_FRESH4_RUNTIME_INPUT_MISSING:{name}")
        actual = sha256_file(path)
        observed[name] = actual
        if actual != expected_sha:
            raise RuntimeError(f"STOP_FRESH4_RUNTIME_INPUT_HASH_DRIFT:{name}:{actual}")
    freeze = load(IMAGE_ROOT / "manifest-freeze.json")
    plan = load(IMAGE_ROOT / "blob-plan.json")
    receipt = load(IMAGE_ROOT / "blob-receipt.json")
    if (
        freeze.get("fresh_pool_sha256") != POOL_SHA
        or freeze.get("image_count") != 20
        or freeze.get("stable_twice") is not True
    ):
        raise RuntimeError("STOP_FRESH4_RUNTIME_MANIFEST_GEOMETRY")
    if plan.get("unique_blob_count") != UNIQUE_BLOB_COUNT:
        raise RuntimeError("STOP_FRESH4_RUNTIME_BLOB_PLAN_GEOMETRY")
    if receipt.get("all_blobs_verified") is not True or receipt.get("unique_blob_count") != UNIQUE_BLOB_COUNT:
        raise RuntimeError("STOP_FRESH4_RUNTIME_BLOB_VERIFICATION")
    return {
        "fresh4_pool_sha256": POOL_SHA,
        "image_count": 20,
        "unique_blob_count": UNIQUE_BLOB_COUNT,
        "input_sha256": observed,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }


def preflight(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit_inputs(blob_receipt_sha)
    result = base.preflight(root)
    result.update({
        "fresh4_pool_sha256": POOL_SHA,
        "manifest_freeze_sha256": MANIFEST_SHA,
        "blob_plan_sha256": BLOB_PLAN_SHA,
        "blob_receipt_sha256": blob_receipt_sha,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    })
    atomic_json(root / "preflight.json", result)
    return result


def import_all(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit_inputs(blob_receipt_sha)
    pre = load(root / "preflight.json")
    if pre.get("blob_receipt_sha256") != blob_receipt_sha:
        raise RuntimeError("STOP_FRESH4_RUNTIME_PREFLIGHT_RECEIPT_DRIFT")
    return base.import_all(root)


def qualify(root: Path, blob_receipt_sha: str) -> dict[str, Any]:
    audit_inputs(blob_receipt_sha)
    if (root / "normalization-qualification.json").exists():
        raise RuntimeError("qualification exists; no overwrite")
    imports = {row["instance_id"]: row for row in load(root / "import-receipt.json")["rows"]}
    rows: list[dict[str, Any]] = []
    journal = root / "normalization-journal.jsonl"
    for frozen in base.frozen_rows():
        result = fresh3_runtime.qualify_one(frozen, imports[frozen["instance_id"]])
        with journal.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        rows.append(result)
        print(json.dumps({
            "instance_id": result["instance_id"],
            "role": result["role"],
            "pass": result["exact_base_normalization_pass"],
            "untracked": result.get("initial_untracked_count"),
        }), flush=True)
    qualified = sum(bool(row["exact_base_normalization_pass"]) for row in rows)
    result = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH4_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN" if qualified == 20 else "HOLD_FRESH4_RUNTIME_SUPPORT_INCOMPLETE",
        "qualified": qualified,
        "total": 20,
        "source_qualified": sum(row["role"] == "source" and row["exact_base_normalization_pass"] for row in rows),
        "future_qualified": sum(row["role"] == "future" and row["exact_base_normalization_pass"] for row in rows),
        "blob_receipt_sha256": blob_receipt_sha,
        "manifest_freeze_sha256": MANIFEST_SHA,
        "fresh4_pool_sha256": POOL_SHA,
        "rows": rows,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
    }
    atomic_json(root / "normalization-qualification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("audit", "preflight", "import", "qualify"), required=True)
    parser.add_argument("--blob-receipt-sha", required=True)
    args = parser.parse_args()
    bind(args.blob_receipt_sha)
    if args.phase == "audit":
        result = audit_inputs(args.blob_receipt_sha)
    elif args.phase == "preflight":
        result = preflight(args.root, args.blob_receipt_sha)
    elif args.phase == "import":
        result = import_all(args.root, args.blob_receipt_sha)
    else:
        result = qualify(args.root, args.blob_receipt_sha)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
