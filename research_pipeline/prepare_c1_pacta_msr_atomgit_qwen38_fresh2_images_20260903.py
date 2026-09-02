#!/usr/bin/env python3
"""Bind the verified PACTA-MSR 20-image resolver to the AtomGit fresh2 pool."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_pipeline import prepare_c1_pacta_msr_images_20260902 as base
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-pool-20260903.json"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-images-20260903-v1")
EXPECTED_POOL_SHA = "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"


def bind() -> None:
    if not POOL.is_file() or sha256_file(POOL) != EXPECTED_POOL_SHA:
        raise RuntimeError("STOP_FRESH2_POOL_HASH_DRIFT")
    base.POOL = POOL


def image_units():
    bind()
    rows = base.image_units()
    if len(rows) != 20 or len({x["instance_id"] for x in rows}) != 20:
        raise RuntimeError("fresh2 image geometry")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--phase", choices=("resolve", "finalize-existing"), default="resolve")
    args = ap.parse_args()
    bind()
    result = base.resolve(args.root) if args.phase == "resolve" else base.finalize_existing(args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
