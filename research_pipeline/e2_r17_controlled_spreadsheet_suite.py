from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path
from typing import Any, Callable

from openpyxl import Workbook, load_workbook

from .e2_r17_controlled_suite_builders_a import (
    build_input_output_contract,
    build_schema_key_alignment,
    build_target_sheet_range,
)
from .e2_r17_controlled_suite_builders_b import (
    build_aggregation_join,
    build_formula_materialization,
    build_multi_step_pipeline,
)
from .e2_r17_controlled_suite_schema import (
    BLOCK_ROLES,
    DISTRACTOR_COUNTS,
    FAMILIES,
    FAMILY_CODES,
    L9_PROFILES,
    SCHEMA_VERSION,
    SUITE_ID,
    BuiltTask,
    add_distractors,
    answer_cells,
    canonical_sha,
    new_book,
    normalize_xlsx,
    seeded_rng,
    select_by_hash,
    sha256_file,
    write_json,
)

Builder = Callable[[Workbook, Any, int, int, str], tuple[str, str, dict[str, Any]]]
BUILDERS: dict[str, Builder] = {
    "input_output_contract": build_input_output_contract,
    "target_sheet_range": build_target_sheet_range,
    "schema_key_alignment": build_schema_key_alignment,
    "aggregation_join": build_aggregation_join,
    "formula_materialization": build_formula_materialization,
    "multi_step_pipeline": build_multi_step_pipeline,
}


def build_task(verified_root: Path, *, block: int, family: str, profile_index: int) -> BuiltTask:
    if block not in BLOCK_ROLES:
        raise ValueError(f"unknown block: {block}")
    if family not in FAMILIES:
        raise ValueError(f"unknown family: {family}")
    if not 0 <= profile_index < len(L9_PROFILES):
        raise ValueError(f"unknown profile: {profile_index}")
    depth, distractor_level, ambiguity = L9_PROFILES[profile_index]
    task_id = f"r17-b{block}-{FAMILY_CODES[family]}-p{profile_index}"
    rng = seeded_rng(task_id)
    wb = new_book(task_id)
    distractor_names = add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
    instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
    task_dir = verified_root / "spreadsheet" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    init_path = task_dir / f"{task_id}_init.xlsx"
    golden_path = task_dir / f"{task_id}_golden.xlsx"
    expected_values = {
        f"{sheet}!{cell}": wb[sheet][cell].value
        for sheet, cell in answer_cells(answer_position)
    }
    for sheet, cell in answer_cells(answer_position):
        wb[sheet][cell] = None
    wb.save(init_path)
    normalize_xlsx(init_path)
    for qualified_cell, value in expected_values.items():
        sheet, cell = qualified_cell.split("!", 1)
        wb[sheet][cell] = value
    wb.save(golden_path)
    normalize_xlsx(golden_path)
    wb.close()
    record = {
        "id": task_id,
        "instruction": instruction,
        "spreadsheet_path": f"spreadsheet/{task_id}",
        "answer_position": answer_position,
        "answer_sheet": None,
        "instruction_type": family,
    }
    metadata = {
        "id": task_id,
        "suite_id": SUITE_ID,
        "block": block,
        "role": BLOCK_ROLES[block],
        "primary_failure_family": family,
        "profile_index": profile_index,
        "procedure_depth_level": depth,
        "distractor_level": distractor_level,
        "distractor_count": DISTRACTOR_COUNTS[distractor_level],
        "schema_ambiguity_level": ambiguity,
        "distractor_sheets": distractor_names,
        "answer_position": answer_position,
        "expected": expected,
        "golden_answer_cells": expected_values,
    }
    return BuiltTask(task_id, record, metadata, init_path, golden_path)


def _balanced_selection(metadata: list[dict[str, Any]], *, per_family: int, salt: str) -> list[str]:
    selected: list[str] = []
    for family in FAMILIES:
        ids = [row["id"] for row in metadata if row["primary_failure_family"] == family]
        selected.extend(select_by_hash(ids, count=per_family, salt=f"{salt}|{family}"))
    return sorted(selected)


def _homogeneous_streams(
    metadata: list[dict[str, Any]],
    *,
    role: str,
    streams_per_family: int,
    salt: str,
    prefix: str,
) -> tuple[dict[str, list[str]], list[str]]:
    streams: dict[str, list[str]] = {}
    reserve: list[str] = []
    for family in FAMILIES:
        ids = sorted(
            row["id"]
            for row in metadata
            if row["role"] == role and row["primary_failure_family"] == family
        )
        required = streams_per_family * 8
        selected = select_by_hash(ids, count=required, salt=f"{salt}|{family}")
        reserve.extend(sorted(set(ids) - set(selected)))
        for index in range(streams_per_family):
            stream_id = f"{prefix}-{FAMILY_CODES[family]}-{index:02d}"
            streams[stream_id] = selected[index * 8 : (index + 1) * 8]
    return streams, sorted(reserve)


def _file_rows(output_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(output_root.rglob("*")):
        if not path.is_file() or path.name == "suite_manifest.json" or path.suffix == ".tar":
            continue
        rows.append(
            {
                "path": str(path.relative_to(output_root)),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def build_suite(output_root: Path, *, overwrite: bool = False) -> dict[str, Any]:
    if output_root.exists():
        if not overwrite:
            raise FileExistsError(output_root)
        shutil.rmtree(output_root)
    verified_root = output_root / "spreadsheetbench_verified_400"
    split_root = output_root / "spreadsheetbench_id_split"
    verified_root.mkdir(parents=True)
    records: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    for block in sorted(BLOCK_ROLES):
        for family in FAMILIES:
            for profile_index in range(len(L9_PROFILES)):
                task = build_task(verified_root, block=block, family=family, profile_index=profile_index)
                records.append(task.record)
                metadata.append(task.metadata)
    records.sort(key=lambda row: row["id"])
    metadata.sort(key=lambda row: row["id"])
    write_json(verified_root / "dataset.json", records)
    write_json(output_root / "r17_controlled_metadata.json", metadata)

    by_role: dict[str, list[str]] = {}
    for row in metadata:
        by_role.setdefault(row["role"], []).append(row["id"])
    development = _balanced_selection(
        [row for row in metadata if row["role"] == "development"],
        per_family=2,
        salt="r17-development-v1",
    )
    calibration = sorted(by_role["e0_calibration"])
    streams, update_reserve = _homogeneous_streams(
        metadata,
        role="e1_update_candidate",
        streams_per_family=2,
        salt="r17-e1-update-v2",
        prefix="e1",
    )
    update = [task_id for stream_ids in streams.values() for task_id in stream_ids]
    probe = _balanced_selection(
        [row for row in metadata if row["role"] == "e1_heldout_probe_candidate"],
        per_family=3,
        salt="r17-e1-probe-v2",
    )
    future_streams, future_reserve = _homogeneous_streams(
        metadata,
        role="e3_future_candidate",
        streams_per_family=2,
        salt="r17-e3-future-v2",
        prefix="e3",
    )
    future = [task_id for stream_ids in future_streams.values() for task_id in stream_ids]
    split_manifest = {
        "schema_version": SCHEMA_VERSION,
        "suite_id": SUITE_ID,
        "selection_is_outcome_blind": True,
        "selection_algorithm": "SHA256(salt|task_id); family-balanced where stated",
        "development": development,
        "e0_calibration": calibration,
        "e1_update_streams": streams,
        "e1_update_reserve_integrity_only": update_reserve,
        "e1_common_heldout_probe": probe,
        "e3_future_streams": future_streams,
        "e3_future_reserve_integrity_only": future_reserve,
        "rules": {
            "development_never_promoted": True,
            "reserve_only_for_preexecution_file_integrity_failure": True,
            "reserve_never_replaces_model_failure_or_bad_outcome": True,
            "e1_probe_never_fed_to_updater": True,
            "e3_future_unseen_until_prediction_freeze": True,
            "e1_streams_are_single_family": True,
            "e3_streams_are_single_family": True,
        },
    }
    write_json(output_root / "r17_split_manifest.json", split_manifest)
    train_ids = sorted(set(development + calibration + update + update_reserve))
    test_ids = sorted(set(future + future_reserve))
    for split_name, ids in (("train", train_ids), ("val", probe), ("test", test_ids)):
        write_json(split_root / split_name / "items.json", [{"id": task_id} for task_id in ids])

    file_rows = _file_rows(output_root)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "suite_id": SUITE_ID,
        "task_count": len(records),
        "family_count": len(FAMILIES),
        "families": list(FAMILIES),
        "blocks": {str(key): value for key, value in BLOCK_ROLES.items()},
        "l9_profiles": [list(row) for row in L9_PROFILES],
        "factor_names": ["procedure_depth_level", "distractor_level", "schema_ambiguity_level"],
        "dataset_sha256": canonical_sha(file_rows),
        "files": file_rows,
        "split_manifest_sha256": sha256_file(output_root / "r17_split_manifest.json"),
        "metadata_sha256": sha256_file(output_root / "r17_controlled_metadata.json"),
        "dataset_json_sha256": sha256_file(verified_root / "dataset.json"),
    }
    write_json(output_root / "suite_manifest.json", manifest)
    return manifest


def make_deterministic_tar(output_root: Path, archive_path: Path) -> str:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(output_root.rglob("*")):
            if not path.is_file() or path == archive_path:
                continue
            info = archive.gettarinfo(str(path), arcname=str(path.relative_to(output_root.parent)))
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            with path.open("rb") as handle:
                archive.addfile(info, handle)
    return sha256_file(archive_path)


def self_check_suite(output_root: Path) -> dict[str, Any]:
    manifest = json.loads((output_root / "suite_manifest.json").read_text(encoding="utf-8"))
    records = json.loads((output_root / "spreadsheetbench_verified_400/dataset.json").read_text(encoding="utf-8"))
    metadata = json.loads((output_root / "r17_controlled_metadata.json").read_text(encoding="utf-8"))
    split = json.loads((output_root / "r17_split_manifest.json").read_text(encoding="utf-8"))
    ids = [row["id"] for row in records]
    if len(ids) != 378 or len(ids) != len(set(ids)) or len(metadata) != len(records):
        raise AssertionError("task or metadata cardinality mismatch")
    update_ids = [task_id for values in split["e1_update_streams"].values() for task_id in values]
    future_ids = [task_id for values in split["e3_future_streams"].values() for task_id in values]
    role_sets = {
        "development": set(split["development"]),
        "calibration": set(split["e0_calibration"]),
        "update": set(update_ids),
        "reserve": set(split["e1_update_reserve_integrity_only"]),
        "probe": set(split["e1_common_heldout_probe"]),
        "future": set(future_ids),
        "future_reserve": set(split["e3_future_reserve_integrity_only"]),
    }
    role_names = list(role_sets)
    for index, left in enumerate(role_names):
        for right in role_names[index + 1 :]:
            if role_sets[left] & role_sets[right]:
                raise AssertionError(f"split overlap: {left}/{right}")
    if len(update_ids) != 96 or len(split["e1_update_streams"]) != 12:
        raise AssertionError("E1 stream shape mismatch")
    if len(future_ids) != 96 or len(split["e3_future_streams"]) != 12:
        raise AssertionError("E3 stream shape mismatch")
    if len(split["e1_common_heldout_probe"]) != 18:
        raise AssertionError("E1 probe shape mismatch")
    for record in records:
        task_dir = output_root / "spreadsheetbench_verified_400" / record["spreadsheet_path"]
        golden = next(task_dir.glob("*golden*.xlsx"))
        wb = load_workbook(golden, data_only=True)
        try:
            for sheet, cell in answer_cells(record["answer_position"]):
                if wb[sheet][cell].value is None:
                    raise AssertionError(f"empty golden answer: {record['id']} {sheet}!{cell}")
        finally:
            wb.close()
    observed_sha = canonical_sha(_file_rows(output_root))
    if observed_sha != manifest["dataset_sha256"]:
        raise AssertionError("dataset SHA mismatch")
    meta_by_id = {row["id"]: row for row in metadata}
    probe_counts = {family: 0 for family in FAMILIES}
    for task_id in split["e1_common_heldout_probe"]:
        probe_counts[meta_by_id[task_id]["primary_failure_family"]] += 1
    if set(probe_counts.values()) != {3}:
        raise AssertionError("probe family balance mismatch")
    for stream_name in ("e1_update_streams", "e3_future_streams"):
        for stream_id, task_ids in split[stream_name].items():
            families = {meta_by_id[task_id]["primary_failure_family"] for task_id in task_ids}
            if len(task_ids) != 8 or len(families) != 1:
                raise AssertionError(f"non-homogeneous stream: {stream_name}/{stream_id}")
    return {
        "status": "PASS",
        "task_count": len(records),
        "dataset_sha256": observed_sha,
        "e0_calibration_tasks": len(split["e0_calibration"]),
        "e1_streams": len(split["e1_update_streams"]),
        "e1_tasks_per_stream": 8,
        "e1_probe_tasks": len(split["e1_common_heldout_probe"]),
        "e3_streams": len(split["e3_future_streams"]),
        "e3_tasks_per_stream": 8,
        "e3_future_tasks": len(future_ids),
        "probe_family_counts": probe_counts,
    }
