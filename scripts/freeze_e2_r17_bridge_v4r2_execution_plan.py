#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import canonical_sha256, validate_plan


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("bridge V4-R2 execution plan output already exists")
    plan = validate_plan()
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-bridge-v4r2-zero-provider-execution-plan",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "FROZEN_ZERO_PROVIDER_BRIDGE_V4R2_EXECUTION_PLAN_ONLY",
        "plan_sha256": canonical_sha256(plan),
        "plan": plan,
        "authority": {
            "provider_io": False,
            "search_pool_acquisition": False,
            "updater_execution": False,
            "actor_evaluation": False,
            "screen_opening": False,
            "validation_opening": False,
            "analysis": False,
            "e3": False,
            "public_benchmark": False,
            "second_backbone": False,
            "paper_promotion": False,
            "submission": False,
        },
        "scientific_outcomes_read": False,
        "interpretation_boundary": "Execution geometry/order/budget preparation only. This artifact grants zero Bridge provider or scientific authority. VALIDATION remains sealed until a future separately authorized RAW_GENERATOR_SCREEN_PASS.",
    }
    atomic_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "plan_sha256": payload["plan_sha256"],
        "screen_hard_max_provider_calls_pre_alias": plan["stages"]["SCREEN"]["budget"]["stage_hard_max_provider_calls_pre_alias"],
        "validation_hard_max_provider_calls_pre_alias": plan["stages"]["VALIDATION"]["budget"]["stage_hard_max_provider_calls_pre_alias"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
