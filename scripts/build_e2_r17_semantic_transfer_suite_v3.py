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
    sha256_file,
    write_json,
)
from research_pipeline.e2_r17_semantic_transfer_v3_builders import (
    BINDING,
    BUILDERS,
    CELL_SPECS,
    PROCEDURAL,
    SEMANTIC_CODES,
    SEMANTIC_TYPES,
    SKELETON_CODES,
    SKELETONS,
    observable_route,
    paired_rng,
    paired_seed_key,
    require_generation_runtime,
    visible_router_features,
)

SUITE_ID = "E2-R17-SEMANTIC-TRANSFER-SUITE-V3"
UPDATE_BLOCKS = (21, 22)
HELDOUT_BLOCK = 23


def task_id(*, block: int, skeleton: str, semantic: str, profile_index: int) -> str:
    return f"r17-b{block}-{SKELETON_CODES[skeleton]}{SEMANTIC_CODES[semantic]}-p{profile_index}"


def build_task(
    root: Path,
    *,
    block: int,
    skeleton: str,
    semantic: str,
    profile_index: int,
    role: str,
) -> dict[str, Any]:
    depth, distractor_level, ambiguity = L9_PROFILES[profile_index]
    tid = task_id(block=block, skeleton=skeleton, semantic=semantic, profile_index=profile_index)
    pair_key = paired_seed_key(block=block, skeleton=skeleton, profile_index=profile_index)
    rng = paired_rng(block=block, skeleton=skeleton, profile_index=profile_index)
    # Pair cells receive the same task sentinel and RNG stream. Their init XLSX
    # therefore differs only if the common skeleton generator leaks semantic
    # identity before answer materialization; the static audit rejects that.
    wb = new_book(pair_key)
    distractors = add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
    instruction, answer_position, expected = BUILDERS[skeleton](wb, rng, depth, ambiguity, semantic)
    route_features = visible_router_features(instruction)
    route = observable_route(instruction)
    task_dir = root / "spreadsheetbench_verified_400" / "spreadsheet" / tid
    task_dir.mkdir(parents=True, exist_ok=True)
    init_path = task_dir / f"{tid}_init.xlsx"
    golden_path = task_dir / f"{tid}_golden.xlsx"
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
    cell = CELL_SPECS[(skeleton, semantic)]
    return {
        "record": {
            "id": tid,
            "instruction": instruction,
            "spreadsheet_path": f"spreadsheet/{tid}",
            "answer_position": answer_position,
            "answer_sheet": None,
            # Keep the actor-facing schema compatible while avoiding family ID
            # as a scientific router input. This identifier is never shown in
            # prompt text and is forbidden to the automatic route.
            "instruction_type": f"{skeleton}_{semantic.lower()}",
        },
        "metadata": {
            "id": tid,
            "pair_key": pair_key,
            "suite_id": SUITE_ID,
            "block": block,
            "role": role,
            "matched_skeleton": skeleton,
            "semantic_type": semantic,
            "semantic_cell_code": SEMANTIC_CODES[semantic],
            "experimental_reusable_transform_steps": cell["experimental_reusable_transform_steps"],
            "experimental_binding_candidate_count": cell["experimental_binding_candidate_count"],
            "profile_index": profile_index,
            "procedure_depth_level": depth,
            "distractor_level": distractor_level,
            "distractor_count": DISTRACTOR_COUNTS[distractor_level],
            "schema_ambiguity_level": ambiguity,
            "distractor_sheets": distractors,
            "answer_position": answer_position,
            "expected": expected,
            "golden_answer_cells": expected_values,
            "observable_router_features": route_features,
            "observable_router_route": route,
        },
        "init": init_path,
        "golden": golden_path,
    }


def manifest_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "suite_manifest.json":
            rows.append({"path": str(path.relative_to(root)), "size": path.stat().st_size, "sha256": sha256_file(path)})
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

    generation_runtime = require_generation_runtime()
    root = args.output_root
    if root.exists():
        if not args.overwrite:
            raise FileExistsError(root)
        shutil.rmtree(root)
    (root / "spreadsheetbench_verified_400").mkdir(parents=True)

    records: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    built: list[dict[str, Any]] = []
    for block in (*UPDATE_BLOCKS, HELDOUT_BLOCK):
        role = "semantic_transfer_v3_update" if block in UPDATE_BLOCKS else "semantic_transfer_v3_heldout"
        for skeleton in SKELETONS:
            for semantic in SEMANTIC_TYPES:
                for profile in range(len(L9_PROFILES)):
                    item = build_task(
                        root,
                        block=block,
                        skeleton=skeleton,
                        semantic=semantic,
                        profile_index=profile,
                        role=role,
                    )
                    records.append(item["record"])
                    metadata.append(item["metadata"])
                    built.append(item)

    records.sort(key=lambda row: row["id"])
    metadata.sort(key=lambda row: row["id"])
    write_json(root / "spreadsheetbench_verified_400" / "dataset.json", records)
    write_json(root / "r17_semantic_transfer_v3_metadata.json", metadata)
    by_id = {row["id"]: row for row in metadata}

    # Strong crossing invariant: paired procedural/binding update inputs are
    # byte-identical for the same block/skeleton/profile. Only instructions and
    # golden answers encode the semantic treatment cell.
    pair_init_hashes: dict[str, dict[str, str]] = {}
    for item in built:
        row = item["metadata"]
        pair_init_hashes.setdefault(row["pair_key"], {})[row["semantic_type"]] = sha256_file(item["init"])
    bad_pairs = {
        key: value
        for key, value in pair_init_hashes.items()
        if set(value) != set(SEMANTIC_TYPES) or len(set(value.values())) != 1
    }
    if bad_pairs:
        raise RuntimeError(f"crossed init mismatch: {list(bad_pairs.items())[:3]}")

    streams: dict[str, list[str]] = {}
    reserve: dict[str, list[str]] = {}
    for skeleton in SKELETONS:
        for stream_index, block in enumerate(UPDATE_BLOCKS):
            # Choose the scientific profile set once per skeleton/block with a
            # semantic-blind hash. Both semantic cells therefore use exactly
            # the same eight nuisance profiles; the ninth paired profile is an
            # integrity-only reserve on both sides.
            profile_order = sorted(
                range(len(L9_PROFILES)),
                key=lambda profile: hashlib.sha256(
                    f"semantic-transfer-v3-update-profile|b{block}|{skeleton}|p{profile}".encode()
                ).hexdigest(),
            )
            selected_profiles = set(profile_order[:8])
            for semantic in SEMANTIC_TYPES:
                reserve_key = f"{skeleton}|{semantic}"
                reserve.setdefault(reserve_key, [])
                ids = sorted(
                    row["id"]
                    for row in metadata
                    if row["block"] == block
                    and row["matched_skeleton"] == skeleton
                    and row["semantic_type"] == semantic
                )
                if len(ids) != 9:
                    raise RuntimeError(f"unexpected cell block shape: {skeleton} {semantic} b{block} {len(ids)}")
                chosen = [tid for tid in ids if int(by_id[tid]["profile_index"]) in selected_profiles]
                omitted = [tid for tid in ids if int(by_id[tid]["profile_index"]) not in selected_profiles]
                if len(chosen) != 8 or len(omitted) != 1:
                    raise RuntimeError(f"semantic-blind update profile selection drift: {skeleton} {semantic} b{block}")
                sid = f"stv3-{SKELETON_CODES[skeleton]}{SEMANTIC_CODES[semantic]}-{stream_index:02d}"
                streams[sid] = sorted(chosen)
                reserve[reserve_key].extend(omitted)

    heldout: list[str] = []
    heldout_reserve: list[str] = []
    for skeleton in SKELETONS:
        # Select heldout profiles once per skeleton, then instantiate the same
        # profile pair on both semantic sides.
        valid_profiles: list[tuple[int, int]] = []
        for combo in itertools.combinations(range(len(L9_PROFILES)), 2):
            rows = [L9_PROFILES[p] for p in combo]
            if (
                len({row[0] for row in rows}) == 2
                and len({row[1] for row in rows}) == 2
                and len({row[2] for row in rows}) == 2
            ):
                valid_profiles.append(combo)
        if not valid_profiles:
            raise RuntimeError(f"no balanced heldout profile pair for {skeleton}")
        chosen_profiles = min(
            valid_profiles,
            key=lambda combo: hashlib.sha256(
                (f"semantic-transfer-heldout-v3|{skeleton}|" + "|".join(f"p{x}" for x in combo)).encode()
            ).hexdigest(),
        )
        chosen_profile_set = set(chosen_profiles)
        for semantic in SEMANTIC_TYPES:
            ids = sorted(
                row["id"]
                for row in metadata
                if row["block"] == HELDOUT_BLOCK
                and row["matched_skeleton"] == skeleton
                and row["semantic_type"] == semantic
            )
            chosen = [tid for tid in ids if int(by_id[tid]["profile_index"]) in chosen_profile_set]
            if len(chosen) != 2:
                raise RuntimeError(f"semantic-blind heldout profile selection drift: {skeleton} {semantic}")
            heldout.extend(chosen)
            heldout_reserve.extend(sorted(set(ids) - set(chosen)))
    heldout = sorted(heldout)

    streams_by_cell: dict[str, list[str]] = {}
    streams_by_skeleton: dict[str, list[str]] = {s: [] for s in SKELETONS}
    for sid, ids in streams.items():
        rows = [by_id[x] for x in ids]
        skeletons = {row["matched_skeleton"] for row in rows}
        semantics = {row["semantic_type"] for row in rows}
        if len(skeletons) != 1 or len(semantics) != 1:
            raise RuntimeError(f"non-homogeneous stream: {sid}")
        skeleton = next(iter(skeletons))
        semantic = next(iter(semantics))
        streams_by_skeleton[skeleton].append(sid)
        streams_by_cell.setdefault(f"{skeleton}|{semantic}", []).append(sid)

    route_counts: dict[str, int] = {"MRW4": 0, "WIN-C": 0, "UNCLASSIFIED": 0}
    hidden_route_mismatch: list[str] = []
    for row in metadata:
        route = row["observable_router_route"]
        route_counts[route] = route_counts.get(route, 0) + 1
        expected = "MRW4" if row["semantic_type"] == PROCEDURAL else "WIN-C"
        if route != expected:
            hidden_route_mismatch.append(row["id"])
    if hidden_route_mismatch:
        raise RuntimeError(f"observable route qualification mismatch: {hidden_route_mismatch[:5]}")

    split = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "selection_is_outcome_blind": True,
        "scientific_unit": "matched_skeleton_interaction",
        "primary_interaction": "I_h=D_h,PROCEDURAL_TRANSFORMATION-D_h,INSTANCE_BINDING_LOCALIZATION",
        "hidden_semantic_labels_are_router_inputs": False,
        "router_input": "exact actor-visible natural-language instruction only",
        "router_function": {
            "MRW4": "visible_operation_clause_count>=3 and visible_binding_alternative_count<=1",
            "WIN-C": "visible_binding_alternative_count>=2 and visible_operation_clause_count<=2",
            "otherwise": "HOLD_V3_ROUTER_UNCLASSIFIED",
        },
        "mrw4_failed_witness_selector": "lowest original rollout index among verifier-failure nonwinner trajectories",
        "treated_pool_selection": "lowest SHA256(semantic-transfer-mrw4-v3|stream_id|task_id) among mixed pools; exactly four per qualified stream",
        "update_streams": streams,
        "streams_by_crossed_cell": {key: sorted(value) for key, value in sorted(streams_by_cell.items())},
        "streams_by_matched_skeleton": {key: sorted(value) for key, value in streams_by_skeleton.items()},
        "update_reserve_integrity_only": {key: sorted(value) for key, value in reserve.items()},
        "common_heldout_probe": heldout,
        "heldout_reserve_integrity_only": sorted(heldout_reserve),
        "rules": {
            "five_independent_crossed_skeletons": True,
            "paired_semantic_init_xlsx_byte_identical": True,
            "family_template_task_block_hidden_metadata_forbidden_to_router": True,
            "router_has_no_hidden_fallback": True,
            "all_scientific_task_ids_new": True,
            "heldout_never_fed_to_updater": True,
            "reserve_never_replaces_bad_outcome_or_model_failure": True,
        },
    }
    write_json(root / "r17_semantic_transfer_v3_split_manifest.json", split)
    compat = dict(split)
    compat["development"] = []
    compat["e1_update_streams"] = streams
    compat["e1_common_heldout_probe"] = heldout
    write_json(root / "r17_split_manifest.json", compat)
    write_json(root / "r17_controlled_metadata.json", metadata)

    new_ids = {row["id"] for row in metadata}
    new_hashes = {sha256_file(item[key]) for item in built for key in ("init", "golden")}
    old_id_overlap: dict[str, int] = {}
    old_content_overlap: dict[str, int] = {}
    for old_root in args.old_suite_root:
        old_ids: set[str] = set()
        for path in old_root.glob("*metadata*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(payload, list):
                old_ids.update(str(row.get("id")) for row in payload if isinstance(row, dict) and row.get("id"))
        old_hashes = _all_xlsx_hashes(old_root)
        label = str(old_root)
        old_id_overlap[label] = len(new_ids & old_ids)
        old_content_overlap[label] = len(new_hashes & old_hashes)
        if old_id_overlap[label] or old_content_overlap[label]:
            raise RuntimeError(f"old-suite overlap with {old_root}: ids={old_id_overlap[label]} xlsx={old_content_overlap[label]}")

    update_ids = {x for ids in streams.values() for x in ids}
    heldout_ids = set(heldout)
    if update_ids & heldout_ids:
        raise RuntimeError("update/heldout overlap")
    if len(streams) != 20 or any(len(ids) != 8 for ids in streams.values()):
        raise RuntimeError("stream shape mismatch")
    if len(update_ids) != 160 or len(heldout_ids) != 20:
        raise RuntimeError("scientific task cardinality mismatch")
    if any(len(ids) != 2 for ids in streams_by_cell.values()) or len(streams_by_cell) != 10:
        raise RuntimeError(f"crossed cell balance mismatch: {streams_by_cell}")
    if any(len(ids) != 4 for ids in streams_by_skeleton.values()):
        raise RuntimeError(f"skeleton stream balance mismatch: {streams_by_skeleton}")

    files = manifest_rows(root)
    manifest = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_CROSSED_SUITE_MATERIALIZATION",
        "provider_calls": 0,
        "scientific_outcomes_accessed": False,
        "generation_runtime_pinned": True,
        "generation_runtime": generation_runtime,
        "task_count": len(records),
        "generated_tasks": len(records),
        "matched_skeletons": list(SKELETONS),
        "semantic_types": list(SEMANTIC_TYPES),
        "update_blocks": list(UPDATE_BLOCKS),
        "heldout_block": HELDOUT_BLOCK,
        "update_streams": len(streams),
        "update_tasks": len(update_ids),
        "heldout_tasks": len(heldout_ids),
        "crossed_cells": len(streams_by_cell),
        "streams_per_crossed_cell": 2,
        "streams_per_skeleton": 4,
        "pair_init_checks": len(pair_init_hashes),
        "pair_init_mismatches": len(bad_pairs),
        "observable_route_counts_all_generated_tasks": route_counts,
        "observable_route_hidden_label_mismatches": len(hidden_route_mismatch),
        "split_manifest_sha256": sha256_file(root / "r17_semantic_transfer_v3_split_manifest.json"),
        "metadata_sha256": sha256_file(root / "r17_semantic_transfer_v3_metadata.json"),
        "actor_compat_split_manifest_sha256": sha256_file(root / "r17_split_manifest.json"),
        "actor_compat_metadata_sha256": sha256_file(root / "r17_controlled_metadata.json"),
        "dataset_sha256": canonical_sha(files),
        "old_suite_disjointness": {"task_id_overlap": old_id_overlap, "xlsx_sha256_overlap": old_content_overlap},
        "files": files,
    }
    write_json(root / "suite_manifest.json", manifest)
    print(json.dumps({k: manifest[k] for k in (
        "status", "task_count", "update_streams", "update_tasks", "heldout_tasks", "crossed_cells",
        "pair_init_checks", "pair_init_mismatches", "observable_route_counts_all_generated_tasks",
        "observable_route_hidden_label_mismatches", "old_suite_disjointness",
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
