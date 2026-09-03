#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline import prepare_c1_pacta_msr_images_20260902 as base
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
POOL_SHA = "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"
DEFAULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-images-20260903-v1")


def bind() -> None:
    if not POOL.is_file() or sha256_file(POOL) != POOL_SHA:
        raise RuntimeError("STOP_FRESH3_IMAGE_POOL_HASH_DRIFT")
    base.POOL = POOL
    base.DEFAULT = DEFAULT


def audit() -> dict[str, Any]:
    bind()
    rows = base.image_units()
    if len(rows) != 20 or len({row["instance_id"] for row in rows}) != 20:
        raise RuntimeError("STOP_FRESH3_IMAGE_GEOMETRY")
    return {
        "status": "FRESH3_IMAGE_RESOLVER_BINDING_PASS",
        "fresh3_pool_sha256": POOL_SHA,
        "image_count": 20,
        "source_count": sum(row["role"] == "source" for row in rows),
        "future_count": sum(row["role"] == "future" for row in rows),
        "provider_calls": 0,
        "scientific_source_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--phase", choices=("audit", "resolve", "finalize-existing"), default="audit")
    args = parser.parse_args()
    bind()
    if args.phase == "audit": result = audit()
    elif args.phase == "resolve": result = base.resolve(args.root)
    else: result = base.finalize_existing(args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
