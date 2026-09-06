#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_runtime import run_stage_a


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--stop-before-provider-io", action="store_true")
    parser.add_argument("--preflight-output", type=Path)
    args = parser.parse_args()
    return asyncio.run(
        run_stage_a(
            root=ROOT,
            contract_path=args.contract,
            auth_path=args.authorization,
            env_file=args.env_file,
            stop_before_provider_io=args.stop_before_provider_io,
            preflight_output=args.preflight_output,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
