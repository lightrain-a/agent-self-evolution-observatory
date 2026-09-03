#!/usr/bin/env python3
"""Fresh2 rootful exact-image/runtime qualification for C1 PACTA-MSR AtomGit Qwen3.8.

This is intentionally a thin binding layer over the already-qualified PACTA-MSR
20-image rootful importer/normalizer.  Only content-addressed fresh2 inputs and
run/layout roots are changed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_runtime_20260902 as base

IMAGE_ROOT = Path(
    "/data/wyt/agent-self-evolution-observatory/runs/"
    "c1-pacta-msr-atomgit-qwen38-fresh2-images-20260903-v1"
)
DEFAULT_ROOT = Path(
    "/data/wyt/agent-self-evolution-observatory/runs/"
    "c1-pacta-msr-atomgit-qwen38-fresh2-runtime-20260903-v1"
)
LAYOUT_ROOT = Path(
    "/data/wyt/e1-stri-reasoningbank-runtime/"
    "c1-pacta-msr-atomgit-qwen38-fresh2-oci-layouts"
)
MANIFEST_SHA256 = "45be64121d04d8b5146364463154a2c87e43f410e4449b274f77bd99cbd553c4"
BLOB_PLAN_SHA256 = "d770b3da1527709114aa866d54f944f833069ae2c72c3f46cefb6421d467d8a3"
BLOB_RECEIPT_SHA256 = "ba50bb14f170d6c180bb7fa500b5110bfde73e967e04228cde03be3707e4569a"
FRESH2_POOL_SHA256 = "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"


def bind() -> None:
    base.IMAGE_ROOT = IMAGE_ROOT
    base.DEFAULT = DEFAULT_ROOT
    base.LAYOUT_ROOT = LAYOUT_ROOT
    base.MANIFEST_SHA = MANIFEST_SHA256
    base.BLOB_RECEIPT_SHA = BLOB_RECEIPT_SHA256


def audit_inputs() -> dict:
    from research_pipeline.c1_pacta_rb_qwen397 import sha256_file

    required = {
        "manifest-freeze.json": MANIFEST_SHA256,
        "blob-plan.json": BLOB_PLAN_SHA256,
        "blob-receipt.json": BLOB_RECEIPT_SHA256,
    }
    observed = {}
    for name, expected in required.items():
        path = IMAGE_ROOT / name
        if not path.is_file():
            raise RuntimeError(f"STOP_FRESH2_RUNTIME_INPUT_MISSING:{name}")
        digest = sha256_file(path)
        observed[name] = digest
        if digest != expected:
            raise RuntimeError(f"STOP_FRESH2_RUNTIME_INPUT_HASH_DRIFT:{name}:{digest}")
    freeze = json.loads((IMAGE_ROOT / "manifest-freeze.json").read_text())
    receipt = json.loads((IMAGE_ROOT / "blob-receipt.json").read_text())
    if freeze.get("fresh_pool_sha256") != FRESH2_POOL_SHA256:
        raise RuntimeError("STOP_FRESH2_RUNTIME_POOL_BINDING_DRIFT")
    if freeze.get("image_count") != 20 or freeze.get("stable_twice") is not True:
        raise RuntimeError("STOP_FRESH2_RUNTIME_IMAGE_GEOMETRY")
    if receipt.get("all_blobs_verified") is not True or receipt.get("unique_blob_count") != 86:
        raise RuntimeError("STOP_FRESH2_RUNTIME_BLOB_VERIFICATION")
    return {
        "fresh_pool_sha256": FRESH2_POOL_SHA256,
        "image_count": 20,
        "unique_blob_count": 86,
        "input_sha256": observed,
        "provider_calls": 0,
        "scientific_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("audit", "preflight", "import", "qualify"), required=True)
    args = parser.parse_args()
    bind()
    if args.phase == "audit":
        result = audit_inputs()
    else:
        audit_inputs()
        result = {
            "preflight": base.preflight,
            "import": base.import_all,
            "qualify": base.qualify,
        }[args.phase](args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
