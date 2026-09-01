#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_workbook(task_dir: Path, kind: str) -> Path:
    hits = sorted(task_dir.glob(f"*{kind}*.xlsx"))
    if len(hits) != 1:
        raise RuntimeError(f"expected one {kind} workbook under {task_dir}, observed {hits}")
    return hits[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_roots = [
        args.mindmemos_root / "src/mindmemos_eval",
        args.mindmemos_root / "src/mindmemos_sdk",
        args.mindmemos_root / "src/mindmemos",
    ]
    for source_root in reversed(source_roots):
        if str(source_root) not in sys.path:
            sys.path.insert(0, str(source_root))
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv
    from mindmemos_eval.skills.envs.spreadsheetbench.evaluator import compare_workbooks

    manifest = json.loads((args.suite_root / "suite_manifest.json").read_text(encoding="utf-8"))
    dataset = json.loads(
        (args.suite_root / "spreadsheetbench_verified_400/dataset.json").read_text(encoding="utf-8")
    )
    split = json.loads((args.suite_root / "r17_split_manifest.json").read_text(encoding="utf-8"))
    env = SpreadsheetBenchEnv(args.suite_root, args.suite_root / ".qualification-run")
    cases = env.load_cases("all")
    by_id = {case.id: case for case in cases}
    golden_pass = 0
    init_negative = 0
    failures: list[dict[str, Any]] = []
    for record in dataset:
        task_id = str(record["id"])
        case = by_id[task_id]
        task_dir = args.suite_root / "spreadsheetbench_verified_400" / record["spreadsheet_path"]
        init = find_workbook(task_dir, "init")
        golden = find_workbook(task_dir, "golden")
        answer_position = env.answer_position(case)
        ok_gold, message_gold = compare_workbooks(golden, golden, answer_position)
        ok_init, message_init = compare_workbooks(golden, init, answer_position)
        golden_pass += int(ok_gold)
        init_negative += int(not ok_init)
        if not ok_gold or ok_init:
            failures.append(
                {
                    "task_id": task_id,
                    "golden_ok": ok_gold,
                    "golden_message": message_gold,
                    "init_unexpectedly_ok": ok_init,
                    "init_message": message_init,
                }
            )
    substrate_head = subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    clean = not subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "status", "--porcelain"], text=True
    ).strip()
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-controlled-suite-mindmemos-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER" if not failures else "FAIL",
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": sha256(args.suite_root / "suite_manifest.json"),
        "dataset_sha256": manifest["dataset_sha256"],
        "split_manifest_sha256": sha256(args.suite_root / "r17_split_manifest.json"),
        "mindmemos_root": str(args.mindmemos_root),
        "mindmemos_commit": substrate_head,
        "mindmemos_clean": clean,
        "cases_loaded": len(cases),
        "golden_self_check_pass": golden_pass,
        "init_negative_control_pass": init_negative,
        "failures": failures,
        "split_shape": {
            "development": len(split["development"]),
            "e0_calibration": len(split["e0_calibration"]),
            "e1_streams": len(split["e1_update_streams"]),
            "e1_tasks_per_stream": sorted({len(ids) for ids in split["e1_update_streams"].values()}),
            "e1_probe": len(split["e1_common_heldout_probe"]),
            "e3_streams": len(split["e3_future_streams"]),
            "e3_tasks_per_stream": sorted({len(ids) for ids in split["e3_future_streams"].values()}),
            "e3_future": sum(len(ids) for ids in split["e3_future_streams"].values()),
        },
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
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
