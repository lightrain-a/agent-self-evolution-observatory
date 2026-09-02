#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_controlled_suite_schema import (
    DISTRACTOR_COUNTS,
    L9_PROFILES,
    add_distractors,
    answer_cells,
    canonical_sha,
    new_book,
    normalize_xlsx,
    seeded_rng,
    sha256_file,
    write_json,
)
from research_pipeline.e2_r17_semantic_transfer_builders import (
    BUILDERS,
    FAMILIES,
    FAMILY_CODES,
    FAMILY_SPECS,
)

SUITE_ID = "E2-R17-SEMANTIC-TRANSFER-SUITE-V2"
UPDATE_BLOCKS = (17, 18, 19)
HELDOUT_BLOCK = 20


def build_task(root: Path, *, block: int, family: str, profile_index: int, role: str) -> dict[str, Any]:
    depth, distractor_level, ambiguity = L9_PROFILES[profile_index]
    task_id = f"r17-b{block}-{FAMILY_CODES[family]}-p{profile_index}"
    rng = seeded_rng(task_id)
    wb = new_book(task_id)
    distractors = add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
    instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
    task_dir = root / "spreadsheetbench_verified_400" / "spreadsheet" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    init_path = task_dir / f"{task_id}_init.xlsx"
    golden_path = task_dir / f"{task_id}_golden.xlsx"
    expected_values = {f"{s}!{c}": wb[s][c].value for s, c in answer_cells(answer_position)}
    for s, c in answer_cells(answer_position):
        wb[s][c] = None
    wb.save(init_path)
    normalize_xlsx(init_path)
    for key, value in expected_values.items():
        sheet, cell = key.split("!", 1)
        wb[sheet][cell] = value
    wb.save(golden_path)
    normalize_xlsx(golden_path)
    wb.close()
    spec = FAMILY_SPECS[family]
    return {
        "record": {
            "id": task_id,
            "instruction": instruction,
            "spreadsheet_path": f"spreadsheet/{task_id}",
            "answer_position": answer_position,
            "answer_sheet": None,
            "instruction_type": family,
        },
        "metadata": {
            "id": task_id,
            "suite_id": SUITE_ID,
            "block": block,
            "role": role,
            "primary_failure_family": family,
            "semantic_type": spec["semantic_type"],
            "matched_skeleton": spec["matched_skeleton"],
            "reusable_transform_steps": spec["reusable_transform_steps"],
            "binding_candidate_count": spec["binding_candidate_count"],
            "profile_index": profile_index,
            "procedure_depth_level": depth,
            "distractor_level": distractor_level,
            "distractor_count": DISTRACTOR_COUNTS[distractor_level],
            "schema_ambiguity_level": ambiguity,
            "distractor_sheets": distractors,
            "answer_position": answer_position,
            "expected": expected,
            "golden_answer_cells": expected_values,
        },
        "init": init_path,
        "golden": golden_path,
    }


def manifest_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "suite_manifest.json":
            rows.append(
                {
                    "path": str(path.relative_to(root)),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return rows


def _all_xlsx_hashes(root: Path) -> set[str]:
    base = root / "spreadsheetbench_verified_400" / "spreadsheet"
    if not base.is_dir():
        return set()
    return {sha256_file(path) for path in base.rglob("*.xlsx")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--old-suite-root", type=Path, action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = args.output_root
    if root.exists():
        if not args.overwrite:
            raise FileExistsError(root)
        shutil.rmtree(root)
    (root / "spreadsheetbench_verified_400").mkdir(parents=True)

    records: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    built: list[dict[str, Any]] = []
    for block in UPDATE_BLOCKS:
        for family in FAMILIES:
            for profile in range(len(L9_PROFILES)):
                item = build_task(root, block=block, family=family, profile_index=profile, role="semantic_transfer_update")
                records.append(item["record"])
                metadata.append(item["metadata"])
                built.append(item)
    for family in FAMILIES:
        for profile in range(len(L9_PROFILES)):
            item = build_task(root, block=HELDOUT_BLOCK, family=family, profile_index=profile, role="semantic_transfer_heldout")
            records.append(item["record"])
            metadata.append(item["metadata"])
            built.append(item)

    records.sort(key=lambda row: row["id"])
    metadata.sort(key=lambda row: row["id"])
    write_json(root / "spreadsheetbench_verified_400" / "dataset.json", records)
    write_json(root / "r17_semantic_transfer_metadata.json", metadata)
    by_id = {row["id"]: row for row in metadata}

    streams: dict[str, list[str]] = {}
    reserve: dict[str, list[str]] = {}
    for family in FAMILIES:
        code = FAMILY_CODES[family]
        family_reserve: list[str] = []
        for stream_index, block in enumerate(UPDATE_BLOCKS):
            ids = sorted(
                row["id"]
                for row in metadata
                if row["block"] == block and row["primary_failure_family"] == family
            )
            if len(ids) != 9:
                raise RuntimeError(f"unexpected update block shape: {family} b{block} {len(ids)}")
            order = sorted(ids, key=lambda task_id: hashlib.sha256(f"semantic-transfer-v2|{task_id}".encode()).hexdigest())
            streams[f"st-{code}-{stream_index:02d}"] = order[:8]
            family_reserve.extend(order[8:])
        reserve[family] = sorted(family_reserve)

    heldout: list[str] = []
    heldout_reserve: list[str] = []
    for family in FAMILIES:
        ids = sorted(
            row["id"]
            for row in metadata
            if row["block"] == HELDOUT_BLOCK and row["primary_failure_family"] == family
        )
        valid: list[tuple[str, ...]] = []
        for combo in itertools.combinations(ids, 3):
            rows = [by_id[task_id] for task_id in combo]
            if (
                len({row["procedure_depth_level"] for row in rows}) == 3
                and len({row["distractor_level"] for row in rows}) == 3
                and len({row["schema_ambiguity_level"] for row in rows}) == 3
            ):
                valid.append(combo)
        if not valid:
            raise RuntimeError(f"no orthogonal heldout triple for {family}")
        chosen = min(
            valid,
            key=lambda combo: hashlib.sha256((f"semantic-transfer-heldout-v2|{family}|" + "|".join(combo)).encode()).hexdigest(),
        )
        heldout.extend(chosen)
        heldout_reserve.extend(sorted(set(ids) - set(chosen)))
    heldout = sorted(heldout)

    semantic_streams: dict[str, list[str]] = {"PROCEDURAL_TRANSFORMATION": [], "INSTANCE_BINDING_LOCALIZATION": []}
    skeleton_streams: dict[str, list[str]] = {}
    for stream_id, task_ids in streams.items():
        rows = [by_id[task_id] for task_id in task_ids]
        families = {row["primary_failure_family"] for row in rows}
        semantic = {row["semantic_type"] for row in rows}
        skeleton = {row["matched_skeleton"] for row in rows}
        if len(families) != 1 or len(semantic) != 1 or len(skeleton) != 1:
            raise RuntimeError(f"non-homogeneous stream: {stream_id}")
        semantic_value = next(iter(semantic))
        skeleton_value = next(iter(skeleton))
        semantic_streams[semantic_value].append(stream_id)
        skeleton_streams.setdefault(skeleton_value, []).append(stream_id)

    split = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "selection_is_outcome_blind": True,
        "selection_algorithm": "fixed SHA256 ordering over generated task IDs; no model outcomes",
        "semantic_routing_rule": {
            "PROCEDURAL_TRANSFORMATION": "MRW4",
            "INSTANCE_BINDING_LOCALIZATION": "WIN-C",
            "mechanical_definition": (
                "PROCEDURAL_TRANSFORMATION iff reusable_transform_steps>=2 and binding_candidate_count==1; "
                "INSTANCE_BINDING_LOCALIZATION iff binding_candidate_count>=2 and reusable_transform_steps<=1"
            ),
        },
        "family_specs": FAMILY_SPECS,
        "update_streams": streams,
        "streams_by_semantic_type": {key: sorted(value) for key, value in semantic_streams.items()},
        "streams_by_matched_skeleton": {key: sorted(value) for key, value in skeleton_streams.items()},
        "update_reserve_integrity_only": reserve,
        "common_heldout_probe": heldout,
        "heldout_reserve_integrity_only": sorted(heldout_reserve),
        "rules": {
            "old_family_identity_lookup_cannot_route_new_families": True,
            "all_update_families_new_relative_to_closed_experiment": True,
            "all_scientific_task_ids_new": True,
            "heldout_never_fed_to_updater": True,
            "semantic_type_frozen_before_provider_execution": True,
            "reserve_never_replaces_bad_outcome_or_model_failure": True,
        },
    }
    write_json(root / "r17_semantic_transfer_split_manifest.json", split)
    # Compatibility aliases for the frozen generic actor. These files only
    # rename schema fields; they point to the exact same 144 update tasks and
    # 18 heldout tasks and do not alter any task or treatment semantics.
    compat_split = dict(split)
    compat_split["development"] = []
    compat_split["e1_update_streams"] = streams
    compat_split["e1_common_heldout_probe"] = heldout
    write_json(root / "r17_split_manifest.json", compat_split)
    write_json(root / "r17_controlled_metadata.json", metadata)

    new_ids = {row["id"] for row in metadata}
    new_hashes = {sha256_file(item[key]) for item in built for key in ("init", "golden")}
    old_id_overlap: dict[str, int] = {}
    old_content_overlap: dict[str, int] = {}
    for old_root in args.old_suite_root:
        meta_candidates = list(old_root.glob("*metadata*.json"))
        old_ids: set[str] = set()
        for path in meta_candidates:
            try:
                payload = json.loads(path.read_text())
            except Exception:
                continue
            if isinstance(payload, list):
                old_ids.update(str(row.get("id")) for row in payload if isinstance(row, dict) and row.get("id"))
        old_hashes = _all_xlsx_hashes(old_root)
        label = str(old_root)
        old_id_overlap[label] = len(new_ids & old_ids)
        old_content_overlap[label] = len(new_hashes & old_hashes)
        if old_id_overlap[label] or old_content_overlap[label]:
            raise RuntimeError(
                f"old-suite overlap with {old_root}: ids={old_id_overlap[label]} xlsx={old_content_overlap[label]}"
            )

    update_ids = {task_id for task_ids in streams.values() for task_id in task_ids}
    heldout_ids = set(heldout)
    if update_ids & heldout_ids:
        raise RuntimeError("update/heldout overlap")
    if len(streams) != 18 or any(len(task_ids) != 8 for task_ids in streams.values()):
        raise RuntimeError("stream shape mismatch")
    if len(update_ids) != 144 or len(heldout_ids) != 18:
        raise RuntimeError("scientific task cardinality mismatch")
    if any(len(value) != 9 for value in semantic_streams.values()):
        raise RuntimeError(f"semantic stream balance mismatch: {semantic_streams}")
    if any(len(value) != 6 for value in skeleton_streams.values()):
        raise RuntimeError(f"matched skeleton balance mismatch: {skeleton_streams}")

    files = manifest_rows(root)
    manifest = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_SUITE_MATERIALIZATION",
        "provider_calls": 0,
        "scientific_outcomes_accessed": False,
        "task_count": len(records),
        "families": list(FAMILIES),
        "family_specs": FAMILY_SPECS,
        "update_blocks": list(UPDATE_BLOCKS),
        "heldout_block": HELDOUT_BLOCK,
        "update_streams": 18,
        "update_tasks": 144,
        "heldout_tasks": 18,
        "semantic_stream_counts": {key: len(value) for key, value in semantic_streams.items()},
        "matched_skeleton_stream_counts": {key: len(value) for key, value in skeleton_streams.items()},
        "split_manifest_sha256": sha256_file(root / "r17_semantic_transfer_split_manifest.json"),
        "metadata_sha256": sha256_file(root / "r17_semantic_transfer_metadata.json"),
        "actor_compat_split_manifest_sha256": sha256_file(root / "r17_split_manifest.json"),
        "actor_compat_metadata_sha256": sha256_file(root / "r17_controlled_metadata.json"),
        "dataset_sha256": canonical_sha(files),
        "old_suite_disjointness": {
            "task_id_overlap": old_id_overlap,
            "xlsx_sha256_overlap": old_content_overlap,
        },
        "files": files,
    }
    write_json(root / "suite_manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "task_count": manifest["task_count"],
                "update_streams": manifest["update_streams"],
                "update_tasks": manifest["update_tasks"],
                "heldout_tasks": manifest["heldout_tasks"],
                "semantic_stream_counts": manifest["semantic_stream_counts"],
                "matched_skeleton_stream_counts": manifest["matched_skeleton_stream_counts"],
                "old_suite_disjointness": manifest["old_suite_disjointness"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
