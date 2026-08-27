#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_controlled_spreadsheet_suite import (
    build_suite,
    make_deterministic_tar,
    self_check_suite,
)
from research_pipeline.e2_r17_controlled_suite_schema import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = build_suite(args.output_root, overwrite=args.overwrite)
    check = self_check_suite(args.output_root)
    archive_sha = make_deterministic_tar(args.output_root, args.archive)
    receipt = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-controlled-spreadsheet-suite-build-receipt",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER",
        "output_root": str(args.output_root),
        "archive": str(args.archive),
        "archive_sha256": archive_sha,
        "suite_manifest": str(args.output_root / "suite_manifest.json"),
        "suite_manifest_sha256": sha256_file(args.output_root / "suite_manifest.json"),
        "dataset_sha256": manifest["dataset_sha256"],
        "self_check": check,
        "provider_calls": 0,
        "benchmark_outcomes_accessed": False,
        "scientific_outcome": False,
        "authority": {
            "f0_r4_freeze": False,
            "scientific_experiment": False,
            "gpu": False,
            "submission": False,
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
