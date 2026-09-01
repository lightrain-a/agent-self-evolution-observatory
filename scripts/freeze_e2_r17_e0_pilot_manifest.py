#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SALT = "E2-R17-E0-PILOT-FAMILY-BALANCED-v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(task_id: str) -> str:
    return hashlib.sha256(f"{SALT}|{task_id}".encode("utf-8")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--per-family", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    split_path = args.suite_root / "r17_split_manifest.json"
    metadata_path = args.suite_root / "r17_controlled_metadata.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in json.loads(metadata_path.read_text(encoding="utf-8"))}
    calibration = [str(value) for value in split["e0_calibration"]]
    by_family: dict[str, list[str]] = defaultdict(list)
    for task_id in calibration:
        by_family[str(metadata[task_id]["primary_failure_family"])].append(task_id)
    selected: list[str] = []
    selection_rows: dict[str, list[dict[str, str]]] = {}
    for family in sorted(by_family):
        ordered = sorted(by_family[family], key=lambda task_id: (rank(task_id), task_id))
        chosen = ordered[: args.per_family]
        selected.extend(chosen)
        selection_rows[family] = [
            {"task_id": task_id, "selection_rank_sha256": rank(task_id)} for task_id in chosen
        ]
    selected_set = set(selected)
    extension = [task_id for task_id in calibration if task_id not in selected_set]
    checks = {
        "calibration_count": len(calibration) == 54,
        "six_families": len(by_family) == 6,
        "equal_family_size": len({len(values) for values in by_family.values()}) == 1,
        "pilot_is_family_balanced": all(len(rows) == args.per_family for rows in selection_rows.values()),
        "pilot_and_extension_disjoint": not (set(selected) & set(extension)),
        "pilot_union_extension_is_calibration": set(selected) | set(extension) == set(calibration),
        "development_disjoint": not (set(selected) & set(split.get("development") or [])),
        "heldout_probe_disjoint": not (set(selected) & set(split.get("e1_common_heldout_probe") or [])),
    }
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e0-pilot-manifest",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "FROZEN_PRE_OUTCOME" if all(checks.values()) else "FAIL",
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": sha256(args.suite_root / "suite_manifest.json"),
        "split_manifest_sha256": sha256(split_path),
        "metadata_sha256": sha256(metadata_path),
        "selection_algorithm": f"sort by SHA256({SALT}|task_id), then take {args.per_family} per family",
        "selection_is_outcome_blind": True,
        "model_outcomes_accessed": False,
        "provider_calls": 0,
        "pilot_task_ids": selected,
        "pilot_by_family": selection_rows,
        "extension_task_ids": extension,
        "checks": checks,
        "pilot_execution_rule": (
            "Run all selected tasks at K=8 and derive K=1/2/4/8 only from nested prefixes. "
            "The pilot may qualify runtime, rescue support, and pool-law measurement, but no task may be replaced because of model outcome."
        ),
        "authority": {
            "scientific_experiment": False,
            "gpu": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "FROZEN_PRE_OUTCOME" else 2


if __name__ == "__main__":
    raise SystemExit(main())
