#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh3_probe_specs_20260903 as base
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-pool-20260903.json"
POOL_SHA = "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-probe-specs-20260903.json"
TOKEN_SALT = "C1-PACTA-MSR-FRESH4-PROBE-TOKEN-v1"


def bind() -> None:
    base.POOL = POOL
    base.POOL_SHA = POOL_SHA
    base.OUT = OUT
    base.TOKEN_SALT = TOKEN_SALT


def prepare() -> dict[str, Any]:
    bind()
    result = base.prepare()
    result["experiment"] = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-PROBE-SPECS-20260903"
    result["status"] = "FRESH4_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME"
    result["fresh_pool_sha256"] = POOL_SHA
    result["token_salt"] = TOKEN_SALT
    for row in result["rows"]:
        row["runtime_binding"] = "DEFERRED_UNTIL_FRESH4_20_RUNTIME_READY"
    return result


def main() -> None:
    if OUT.exists():
        raise RuntimeError("fresh4 probe specs already exist; no overwrite")
    result = prepare()
    atomic_json(OUT, result)
    print(json.dumps({"status": result["status"], "specs": len(result["rows"]), "sha256": sha256_file(OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
