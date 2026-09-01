#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_FAMILIES = {
    "agj": "aggregation_join",
    "fmv": "formula_materialization",
    "ioc": "input_output_contract",
    "msp": "multi_step_pipeline",
    "ska": "schema_key_alignment",
    "tsr": "target_sheet_range",
}
BUILD_STATUS = "PASS_ZERO_PROVIDER"
P0_STATUS = "P0_STRUCTURAL_SUBSTRATE_PASS_D0_POWER_PENDING"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def flatten_split(split: dict[str, Any]) -> set[str]:
    used: set[str] = set()

    def add(value: Any) -> None:
        if isinstance(value, list):
            used.update(map(str, value))
        elif isinstance(value, dict):
            for child in value.values():
                add(child)

    metadata_keys = {
        "rules",
        "selection_algorithm",
        "selection_is_outcome_blind",
        "suite_id",
        "schema_version",
    }
    for key, value in split.items():
        if key not in metadata_keys:
            add(value)
    return used


def verify_task_files(
    *,
    suite_root: Path,
    suite_manifest: dict[str, Any],
    task_ids: list[str],
) -> tuple[int, dict[str, list[dict[str, Any]]]]:
    records = {str(item["path"]): item for item in suite_manifest["files"]}
    bindings: dict[str, list[dict[str, Any]]] = {}
    checked = 0
    for task_id in task_ids:
        matching = sorted(path for path in records if f"/{task_id}/" in path)
        require(len(matching) == 2, f"expected init+golden files for {task_id}, got {matching}")
        task_bindings: list[dict[str, Any]] = []
        for rel in matching:
            record = records[rel]
            path = suite_root / rel
            require(path.is_file(), f"missing task file: {path}")
            require(path.stat().st_size == int(record["size"]), f"task file size drift: {path}")
            actual_sha = sha_file(path)
            require(actual_sha == str(record["sha256"]), f"task file SHA drift: {path}")
            task_bindings.append(
                {
                    "path": rel,
                    "sha256": actual_sha,
                    "size": int(record["size"]),
                }
            )
            checked += 1
        bindings[task_id] = task_bindings
    return checked, bindings


def historical_name_hits(runs_root: Path, protected_ids: set[str]) -> list[str]:
    if not runs_root.is_dir():
        return []
    hits: list[str] = []
    # Operational/provenance-only check: inspect path names, never file payloads.
    for dirpath, dirnames, filenames in os.walk(runs_root):
        for name in dirnames:
            if name in protected_ids:
                hits.append(str(Path(dirpath) / name))
        for name in filenames:
            if any(task_id in name for task_id in protected_ids):
                hits.append(str(Path(dirpath) / name))
        if hits:
            # Any historical consumption is a fail-closed blocker; no need to enumerate further.
            break
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "P0 substrate audit already exists")
    build = load_json(args.build_receipt)
    proposal = load_json(args.proposal)
    require(build.get("status") == BUILD_STATUS, "controlled-suite build receipt not passing")
    require(build.get("provider_calls") == 0, "controlled-suite build used provider calls unexpectedly")
    require(build.get("benchmark_outcomes_accessed") is False, "controlled-suite build crossed outcome boundary")
    require(proposal.get("status") == "PRE_F0_PROPOSAL_ONLY_ZERO_AUTHORITY", "E3 proposal status drift")
    require(not any((proposal.get("authority") or {}).values()), "E3 proposal unexpectedly grants execution authority")

    suite_root = Path(build["output_root"])
    suite_manifest_path = Path(build["suite_manifest"])
    require(suite_root.is_dir() and suite_manifest_path.is_file(), "controlled suite missing")
    require(sha_file(suite_manifest_path) == build["suite_manifest_sha256"], "suite manifest SHA drift")
    suite_manifest = load_json(suite_manifest_path)
    require(suite_manifest.get("dataset_sha256") == build["dataset_sha256"], "dataset SHA drift")

    split_path = suite_root / "r17_split_manifest.json"
    metadata_path = suite_root / "r17_controlled_metadata.json"
    require(sha_file(split_path) == suite_manifest["split_manifest_sha256"], "split manifest SHA drift")
    require(sha_file(metadata_path) == suite_manifest["metadata_sha256"], "metadata SHA drift")
    split = load_json(split_path)
    metadata_rows = load_json(metadata_path)
    metadata = {str(row["id"]): row for row in metadata_rows}
    require(len(metadata) == int(suite_manifest["task_count"]) == 378, "metadata task cardinality drift")
    require(split.get("selection_is_outcome_blind") is True, "split selection is not frozen outcome-blind")
    rules = split.get("rules") or {}
    require(rules.get("e3_future_unseen_until_prediction_freeze") is True, "E3 future-unseen rule missing")
    require(rules.get("e3_streams_are_single_family") is True, "E3 single-family rule missing")
    require(rules.get("reserve_never_replaces_model_failure_or_bad_outcome") is True, "reserve outcome-safety rule missing")

    e3_streams = split.get("e3_future_streams") or {}
    require(len(e3_streams) == 12, "expected exactly 12 pre-reserved E3 streams")
    e3_tasks: list[str] = []
    family_stream_counts: Counter[str] = Counter()
    stream_manifest: dict[str, Any] = {}
    for stream_id in sorted(e3_streams):
        tasks = list(map(str, e3_streams[stream_id]))
        require(len(tasks) == 8 and len(set(tasks)) == 8, f"E3 stream task cardinality drift: {stream_id}")
        parts = stream_id.split("-")
        require(len(parts) >= 3 and parts[0] == "e3", f"unexpected E3 stream id: {stream_id}")
        abbrev = parts[1]
        require(abbrev in EXPECTED_FAMILIES, f"unknown E3 family abbreviation: {stream_id}")
        expected_family = EXPECTED_FAMILIES[abbrev]
        observed_families = {str(metadata[t]["primary_failure_family"]) for t in tasks}
        observed_roles = {str(metadata[t]["role"]) for t in tasks}
        observed_blocks = {int(metadata[t]["block"]) for t in tasks}
        require(observed_families == {expected_family}, f"E3 family purity drift: {stream_id}")
        require(observed_roles == {"e3_future_candidate"}, f"E3 role drift: {stream_id}")
        require(observed_blocks <= {5, 6}, f"E3 block drift: {stream_id}")
        family_stream_counts[abbrev] += 1
        e3_tasks.extend(tasks)
        stream_manifest[stream_id] = {
            "family_abbrev": abbrev,
            "family": expected_family,
            "task_ids": tasks,
        }
    require(len(e3_tasks) == 96 and len(set(e3_tasks)) == 96, "E3 future task uniqueness drift")
    require(family_stream_counts == Counter({family: 2 for family in EXPECTED_FAMILIES}), "E3 family balance drift")

    used_by_split = flatten_split(split)
    all_b4 = sorted(task_id for task_id, row in metadata.items() if int(row["block"]) == 4)
    e1_probe = set(map(str, split["e1_common_heldout_probe"]))
    e3_probe = sorted(task_id for task_id in all_b4 if task_id not in used_by_split)
    require(len(all_b4) == 54 and len(e1_probe) == 18, "B4/e1 probe cardinality drift")
    require(len(e3_probe) == 36 and len(set(e3_probe)) == 36, "expected all 36 previously-unsplit B4 probes")
    probe_family_counts = Counter(task_id.split("-")[2] for task_id in e3_probe)
    require(probe_family_counts == Counter({family: 6 for family in EXPECTED_FAMILIES}), "E3 probe family balance drift")
    require({metadata[t]["role"] for t in e3_probe} == {"e1_heldout_probe_candidate"}, "unused B4 probe role drift")

    e1_update = {task for tasks in split["e1_update_streams"].values() for task in tasks}
    require(not (set(e3_tasks) & e1_update), "E3 future task overlaps E1 update")
    require(not (set(e3_tasks) & e1_probe), "E3 future task overlaps V2 heldout probe")
    require(not (set(e3_probe) & e1_probe), "E3 heldout probe overlaps V2 heldout probe")
    require(not (set(e3_tasks) & set(e3_probe)), "E3 update and heldout sets overlap")

    protected_ids = set(e3_tasks) | set(e3_probe)
    name_hits = historical_name_hits(args.runs_root, protected_ids)
    require(not name_hits, f"historical run-name consumption detected: {name_hits[:3]}")

    checked_files, file_bindings = verify_task_files(
        suite_root=suite_root,
        suite_manifest=suite_manifest,
        task_ids=e3_tasks + e3_probe,
    )
    require(checked_files == 264, "E3 task file cardinality drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e3-p0-zero-outcome-substrate-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": P0_STATUS,
        "scientific_object": proposal["scientific_object"],
        "proposal_path": str(args.proposal),
        "proposal_sha256": sha_file(args.proposal),
        "build_receipt_path": str(args.build_receipt),
        "build_receipt_sha256": sha_file(args.build_receipt),
        "suite_root": str(suite_root),
        "suite_manifest_path": str(suite_manifest_path),
        "suite_manifest_sha256": sha_file(suite_manifest_path),
        "dataset_sha256": suite_manifest["dataset_sha256"],
        "split_manifest_path": str(split_path),
        "split_manifest_sha256": sha_file(split_path),
        "metadata_sha256": sha_file(metadata_path),
        "selection_is_outcome_blind": True,
        "provider_calls": 0,
        "scientific_outcomes_read": False,
        "v2_effects_read_by_p0": False,
        "e3_update_stream_count": 12,
        "e3_update_task_count": 96,
        "e3_update_streams": stream_manifest,
        "e3_family_stream_counts": dict(sorted(family_stream_counts.items())),
        "e3_heldout_derivation_rule": "ALL_PREVIOUSLY_UNSPLIT_BLOCK4_TASKS_NO_SUBSAMPLING",
        "e3_heldout_task_count": 36,
        "e3_heldout_family_counts": dict(sorted(probe_family_counts.items())),
        "e3_heldout_task_ids": e3_probe,
        "historical_run_name_match_count": 0,
        "task_files_verified": checked_files,
        "task_file_bindings": file_bindings,
        "overlap_checks": {
            "e3_update_vs_e1_update": 0,
            "e3_update_vs_v2_heldout": 0,
            "e3_heldout_vs_v2_heldout": 0,
            "e3_update_vs_e3_heldout": 0,
        },
        "structural_substrate_pass": True,
        "power_sufficiency": "PENDING_SEPARATE_D0_DEVELOPMENT_ONLY_AUTHORIZATION",
        "interpretation": (
            "A prospectively reserved, outcome-blind E3 update substrate exists: 12 single-family streams "
            "covering six families, plus 36 previously-unsplit balanced B4 tasks that can be frozen in full "
            "as a new E3 heldout set. No historical run-name consumption was found and all 264 task files "
            "match the original content-addressed suite manifest. Statistical power for the new prediction-loss "
            "primary cannot be adjudicated without a separately authorized D0 development analysis."
        ),
        "authority": {
            "provider_io": False,
            "new_search_pool_acquisition": False,
            "v2_family_analysis": False,
            "d0_calibration": False,
            "confirmatory_execution": False,
            "heldout_evaluation": False,
            "gpu": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_allowed_action": "PREPARE_D0_DEVELOPMENT_ONLY_CONTRACT_AND_INDEPENDENT_REVIEW_NO_EXECUTION",
    }
    atomic_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "e3_update_stream_count": payload["e3_update_stream_count"],
        "e3_update_task_count": payload["e3_update_task_count"],
        "e3_heldout_task_count": payload["e3_heldout_task_count"],
        "task_files_verified": payload["task_files_verified"],
        "historical_run_name_match_count": payload["historical_run_name_match_count"],
        "scientific_outcomes_read": payload["scientific_outcomes_read"],
        "power_sufficiency": payload["power_sufficiency"],
        "next_allowed_action": payload["next_allowed_action"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
