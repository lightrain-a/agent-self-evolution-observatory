#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEMANTICS = ("INSTANCE_BINDING_LOCALIZATION", "PROCEDURAL_TRANSFORMATION")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def mean_abs_diff(a: float, b: float) -> float:
    return abs(float(a) - float(b))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--suite-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    req(not args.output.exists(), "balance audit output already exists")

    root = args.suite_root
    split_path = root / "r17_split_manifest.json"
    meta_path = root / "r17_controlled_metadata.json"
    data_path = root / "spreadsheetbench_verified_400" / "dataset.json"
    manifest_path = root / "suite_manifest.json"
    for path in (split_path, meta_path, data_path, manifest_path):
        req(path.is_file(), f"missing suite artifact: {path}")

    split = json.loads(split_path.read_text(encoding="utf-8"))
    meta = {str(row["id"]): row for row in json.loads(meta_path.read_text(encoding="utf-8"))}
    data = {str(row["id"]): row for row in json.loads(data_path.read_text(encoding="utf-8"))}
    update_ids = [str(task) for tasks in split["e1_update_streams"].values() for task in tasks]
    req(len(update_ids) == 144 and len(set(update_ids)) == 144, "update task shape drift")

    by_semantic: dict[str, dict[str, Any]] = {}
    for semantic in SEMANTICS:
        ids = [task_id for task_id in update_ids if meta[task_id]["semantic_type"] == semantic]
        req(len(ids) == 72, f"semantic task count drift: {semantic}")
        row: dict[str, Any] = {"tasks": len(ids)}
        for key in ("procedure_depth_level", "distractor_level", "schema_ambiguity_level"):
            vals = [int(meta[task_id][key]) for task_id in ids]
            row[key] = {
                "mean": statistics.fmean(vals),
                "counts": {str(level): vals.count(level) for level in (0, 1, 2)},
            }
        instruction_chars = [len(str(data[task_id]["instruction"])) for task_id in ids]
        xlsx_bytes = []
        for task_id in ids:
            spreadsheet_path = str(data[task_id]["spreadsheet_path"])
            init_path = root / "spreadsheetbench_verified_400" / spreadsheet_path / f"{task_id}_init.xlsx"
            req(init_path.is_file(), f"missing init workbook: {task_id}")
            xlsx_bytes.append(init_path.stat().st_size)
        row["instruction_chars"] = {
            "mean": statistics.fmean(instruction_chars),
            "min": min(instruction_chars),
            "max": max(instruction_chars),
        }
        row["xlsx_bytes"] = {
            "mean": statistics.fmean(xlsx_bytes),
            "min": min(xlsx_bytes),
            "max": max(xlsx_bytes),
        }
        by_semantic[semantic] = row

    b = by_semantic["INSTANCE_BINDING_LOCALIZATION"]
    q = by_semantic["PROCEDURAL_TRANSFORMATION"]
    checks = {
        "depth_mean_abs_diff_le_0_10": mean_abs_diff(b["procedure_depth_level"]["mean"], q["procedure_depth_level"]["mean"]) <= 0.10,
        "distractor_mean_abs_diff_le_0_10": mean_abs_diff(b["distractor_level"]["mean"], q["distractor_level"]["mean"]) <= 0.10,
        "ambiguity_mean_abs_diff_le_0_10": mean_abs_diff(b["schema_ambiguity_level"]["mean"], q["schema_ambiguity_level"]["mean"]) <= 0.10,
        "instruction_mean_abs_diff_le_40_chars": mean_abs_diff(b["instruction_chars"]["mean"], q["instruction_chars"]["mean"]) <= 40.0,
        "xlsx_mean_abs_diff_le_250_bytes": mean_abs_diff(b["xlsx_bytes"]["mean"], q["xlsx_bytes"]["mean"]) <= 250.0,
    }
    for key in ("procedure_depth_level", "distractor_level", "schema_ambiguity_level"):
        counts_b = b[key]["counts"]
        counts_q = q[key]["counts"]
        checks[f"{key}_per_level_count_abs_diff_le_8"] = max(abs(int(counts_b[str(level)]) - int(counts_q[str(level)])) for level in (0, 1, 2)) <= 8
    req(all(checks.values()), f"static nuisance balance failed: {checks}")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v2-static-nuisance-balance-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_SEMANTIC_TRANSFER_V2_STATIC_NUISANCE_BALANCE",
        "suite_root": str(root),
        "suite_manifest_sha256": sha(manifest_path),
        "split_manifest_sha256": sha(split_path),
        "metadata_sha256": sha(meta_path),
        "dataset_sha256": sha(data_path),
        "update_tasks": len(update_ids),
        "by_semantic": by_semantic,
        "checks": checks,
        "interpretation": (
            "The two semantic groups are statically balanced on the controlled L9 depth/distractor/ambiguity factors, "
            "instruction length, and input-workbook size before any model outcome. These checks do not prove equal behavioral difficulty; "
            "Stage-A acting success is therefore retained as a pre-learning difficulty reduction baseline rather than assumed away."
        ),
        "authority": {
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps({"status": payload["status"], "checks": checks, "by_semantic": by_semantic}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
