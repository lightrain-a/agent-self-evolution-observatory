from __future__ import annotations

import csv
import hashlib
import json
import pickle
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from research_pipeline.relational_topology_real_protocol import (
    CLIP_MAX_TOKENS, CLIP_MODEL, CLIP_REVISION, DATASET_REVISION,
    REAL_REGIME_SLOT_COUNTS, SHARED_SLOTS, ScenePayload, derive_seed,
    filter_symmetric_duplicates, render_fixed_count, topology_statistics,
)
from research_pipeline.relational_topology_training_qualification import (
    CORPUS_FIELDS, LICENSE_RECEIPT, canonical_bytes, require_license,
)

FAMILY_MAX_ABS_PROPORTION_DELTA = 0.025
DIRECTION_MAX_ABS_PROPORTION_DELTA = 0.025


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl_bytes(rows: Sequence[dict[str, Any]]) -> bytes:
    return b"".join(canonical_bytes(row) for row in rows)


def load_split(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open(newline="") as handle:
        for row in csv.reader(handle):
            if len(row) != 2 or row[1] not in {"train", "val", "test"}:
                raise ValueError(f"bad split row: {row}")
            if row[0] in result:
                raise ValueError(f"duplicate split id: {row[0]}")
            result[row[0]] = row[1]
    return result


def load_object_types(dataset_stats: Path) -> tuple[str, ...]:
    value = json.loads(dataset_stats.read_text())
    types = value.get("object_types")
    if not isinstance(types, list) or not types:
        raise ValueError("dataset_stats object_types missing")
    return tuple(str(item) for item in types)


def load_scene(scene_dir: Path, object_types: Sequence[str]) -> ScenePayload:
    with (scene_dir / "descriptions.pkl").open("rb") as handle:
        desc = pickle.load(handle)
    with (scene_dir / "models_info.pkl").open("rb") as handle:
        models = pickle.load(handle)
    with np.load(scene_dir / "boxes.npz", allow_pickle=True) as boxes:
        scene_uid = str(boxes["scene_uid"].item())
        scene_id = str(boxes["scene_id"].item())
        uids = tuple(str(value) for value in boxes["uids"].tolist())
    class_ids = tuple(int(value) for value in desc["obj_class_ids"])
    if scene_uid != scene_dir.name:
        raise ValueError(f"scene/path mismatch: {scene_uid} != {scene_dir.name}")
    if not (len(uids) == len(class_ids) == len(models)):
        raise ValueError(f"object cardinality mismatch: {scene_uid}")
    if any(value < 0 or value >= len(object_types) for value in class_ids):
        raise ValueError(f"class id out of range: {scene_uid}")
    captions: list[str] = []
    for model in models:
        caption = model.get("chatgpt_caption")
        if not isinstance(caption, str) or not caption.strip():
            raise ValueError(f"missing chatgpt_caption: {scene_uid}")
        captions.append(caption.strip())
    object_ids = tuple(f"{uid}#{index}" for index, uid in enumerate(uids))
    return ScenePayload(
        scene_uid=scene_uid,
        scene_id=scene_id,
        object_ids=object_ids,
        object_types=tuple(object_types),
        object_class_ids=class_ids,
        object_descriptions=tuple(captions),
        filtered_relations=filter_symmetric_duplicates(desc["obj_relations"]),
    )


def clip_token_count(tokenizer: Any, text: str) -> int:
    return len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])


def build_example(
    payload: ScenePayload,
    regime: str,
    sample_slot: int,
    relation_count: int,
    tokenizer: Any,
    generator_code_sha: str,
) -> dict[str, Any]:
    seed = derive_seed(payload.scene_uid, sample_slot)
    instruction, relation_set = render_fixed_count(payload, relation_count, seed)
    token_count = clip_token_count(tokenizer, instruction)
    family = Counter(item["family"] for item in relation_set)
    direction = Counter(item["predicate"] for item in relation_set)
    edges = [(item["source_object_id"], item["target_object_id"]) for item in relation_set]
    body: dict[str, Any] = {
        "example_id": f"REAL-{payload.scene_uid}-S{sample_slot:02d}-{regime}",
        "source_scene_id": payload.scene_uid,
        "room_type": "BEDROOM",
        "object_ids": list(payload.object_ids),
        "object_count": len(payload.object_ids),
        "relation_set": relation_set,
        "relation_count": relation_count,
        "relation_family_multiset": dict(sorted(family.items())),
        "direction_multiset": dict(sorted(direction.items())),
        "exact_instruction": instruction,
        "clip_tokenizer": CLIP_MODEL,
        "clip_tokenizer_revision": CLIP_REVISION,
        "exact_clip_token_count": token_count,
        "tokenizer_truncated": token_count > CLIP_MAX_TOKENS,
        "topology_statistics": topology_statistics(edges, payload.object_ids),
        "corpus_regime": regime,
        "rng_seed": seed,
        "generator_code_sha": generator_code_sha,
        "dataset_revision": DATASET_REVISION,
    }
    if tuple(body) != CORPUS_FIELDS[:-1]:
        raise AssertionError("real corpus schema/order drift")
    body["example_sha256"] = hashlib.sha256(canonical_bytes(body)).hexdigest()
    if tuple(body) != CORPUS_FIELDS:
        raise AssertionError("real corpus final schema/order drift")
    return body


def _shared_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    fields = (
        "source_scene_id", "object_ids", "object_count", "relation_set",
        "relation_count", "relation_family_multiset", "direction_multiset",
        "exact_instruction", "clip_tokenizer", "clip_tokenizer_revision",
        "exact_clip_token_count", "tokenizer_truncated", "topology_statistics",
        "rng_seed", "generator_code_sha", "dataset_revision",
    )
    return all(left[field] == right[field] for field in fields)


def build_scene_candidate(
    scene_dir: Path,
    split: dict[str, str],
    object_types: Sequence[str],
    tokenizer: Any,
    generator_code_sha: str,
) -> dict[str, Any]:
    try:
        payload = load_scene(scene_dir, object_types)
    except Exception as exc:
        return {"scene_uid": scene_dir.name, "eligible": False,
                "reason": "SCENE_LOAD_FAILURE", "detail": f"{type(exc).__name__}: {exc}"}
    if split.get(payload.scene_id) != "train":
        return {"scene_uid": payload.scene_uid, "scene_id": payload.scene_id,
                "eligible": False, "reason": "NOT_TRAIN_SPLIT"}
    if len(payload.filtered_relations) < 4:
        return {"scene_uid": payload.scene_uid, "scene_id": payload.scene_id,
                "eligible": False, "reason": "FEWER_THAN_FOUR_UNIQUE_RELATION_PAIRS",
                "unique_relation_pairs": len(payload.filtered_relations)}
    rows: dict[str, list[dict[str, Any]]] = {}
    for regime, slot_counts in REAL_REGIME_SLOT_COUNTS.items():
        rows[regime] = [build_example(
            payload, regime, slot, count, tokenizer, generator_code_sha
        ) for slot, count in enumerate(slot_counts)]
    all_rows = rows["IS-SUPPORT-12"] + rows["IS-SUPPORT-14"]
    if any(row["tokenizer_truncated"] for row in all_rows):
        return {"scene_uid": payload.scene_uid, "scene_id": payload.scene_id,
                "eligible": False, "reason": "CLIP_TOKEN_LIMIT_EXCEEDED_SCENE_LEVEL_EXCLUSION",
                "max_clip_tokens": max(row["exact_clip_token_count"] for row in all_rows)}
    if any(not _shared_equal(rows["IS-SUPPORT-12"][slot], rows["IS-SUPPORT-14"][slot])
           for slot in SHARED_SLOTS):
        return {"scene_uid": payload.scene_uid, "scene_id": payload.scene_id,
                "eligible": False, "reason": "SHARED_SUBSET_DRIFT"}
    return {"scene_uid": payload.scene_uid, "scene_id": payload.scene_id,
            "eligible": True, "object_count": len(payload.object_ids), "rows": rows}


def compile_pair(
    bedroom_root: Path,
    split_csv: Path,
    object_types: Sequence[str],
    tokenizer: Any,
    generator_code_sha: str,
    license_receipt: str | None,
    traversal: str = "forward",
    workers: int = 1,
) -> dict[str, Any]:
    require_license(license_receipt)
    split = load_split(split_csv)
    scene_dirs = sorted(path for path in bedroom_root.iterdir() if path.is_dir())
    if traversal == "reverse":
        scene_dirs.reverse()
    elif traversal == "shuffled":
        rng = np.random.default_rng(20260901)
        order = rng.permutation(len(scene_dirs)).tolist()
        scene_dirs = [scene_dirs[int(index)] for index in order]
    elif traversal != "forward":
        raise ValueError(traversal)
    def build(path: Path) -> dict[str, Any]:
        return build_scene_candidate(path, split, object_types, tokenizer, generator_code_sha)
    if workers == 1:
        candidates = [build(path) for path in scene_dirs]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            candidates = list(executor.map(build, scene_dirs))
    eligible = [item for item in candidates if item["eligible"]]
    excluded = [item for item in candidates if not item["eligible"]]
    rows = {regime: [] for regime in REAL_REGIME_SLOT_COUNTS}
    for item in eligible:
        for regime in REAL_REGIME_SLOT_COUNTS:
            rows[regime].extend(item["rows"][regime])
    for regime in rows:
        rows[regime].sort(key=lambda row: row["example_id"])
    hashes = {regime: hashlib.sha256(jsonl_bytes(value)).hexdigest() for regime, value in rows.items()}
    return {
        "rows": rows,
        "jsonl_sha256": hashes,
        "eligible_scenes": sorted(item["scene_uid"] for item in eligible),
        "excluded": sorted(excluded, key=lambda item: item["scene_uid"]),
    }


def _aggregate(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(row[field])
    return dict(sorted(counts.items()))


def _proportions(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    return {key: value / total for key, value in counts.items()} if total else {}


def _max_delta(left: dict[str, float], right: dict[str, float]) -> float:
    return max((abs(left.get(k, 0.0) - right.get(k, 0.0)) for k in set(left) | set(right)), default=0.0)


def _hist(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _token_stats(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    values = np.array([row["exact_clip_token_count"] for row in rows], dtype=np.int64)
    result: dict[str, Any] = {
        "n": int(values.size), "min": int(values.min()), "max": int(values.max()),
        "mean": float(values.mean()), "median": float(np.median(values)),
        "q05": float(np.quantile(values, .05)), "q25": float(np.quantile(values, .25)),
        "q75": float(np.quantile(values, .75)), "q95": float(np.quantile(values, .95)),
        "histogram": dict(sorted(Counter(str(int(x)) for x in values).items())),
    }
    result["by_relation_count"] = {}
    for count in sorted({row["relation_count"] for row in rows}):
        subset = np.array([row["exact_clip_token_count"] for row in rows if row["relation_count"] == count])
        result["by_relation_count"][str(count)] = {
            "n": int(subset.size), "min": int(subset.min()), "max": int(subset.max()),
            "mean": float(subset.mean()), "median": float(np.median(subset)),
            "q05": float(np.quantile(subset, .05)), "q95": float(np.quantile(subset, .95)),
        }
    return result


def audit_pair(compiled: dict[str, Any]) -> dict[str, Any]:
    left = compiled["rows"]["IS-SUPPORT-12"]
    right = compiled["rows"]["IS-SUPPORT-14"]
    if not left or not right:
        raise ValueError("empty real corpus")
    family_counts = {"IS-SUPPORT-12": _aggregate(left, "relation_family_multiset"), "IS-SUPPORT-14": _aggregate(right, "relation_family_multiset")}
    direction_counts = {"IS-SUPPORT-12": _aggregate(left, "direction_multiset"), "IS-SUPPORT-14": _aggregate(right, "direction_multiset")}
    family_props = {key: _proportions(value) for key, value in family_counts.items()}
    direction_props = {key: _proportions(value) for key, value in direction_counts.items()}
    family_delta = _max_delta(family_props["IS-SUPPORT-12"], family_props["IS-SUPPORT-14"])
    direction_delta = _max_delta(direction_props["IS-SUPPORT-12"], direction_props["IS-SUPPORT-14"])
    shared_exact = True; shared_rows = 0
    def slot_of(row: dict[str, Any]) -> int:
        match = re.search(r"-S(\d{2})-IS-SUPPORT-(?:12|14)$", row["example_id"])
        if match is None:
            raise ValueError(f"malformed real example id: {row['example_id']}")
        return int(match.group(1))
    peer = {(row["source_scene_id"], slot_of(row)): row for row in right}
    for row in left:
        slot = slot_of(row)
        if slot in SHARED_SLOTS:
            shared_rows += 1
            shared_exact &= _shared_equal(row, peer[(row["source_scene_id"], slot)])
    scene_exact = {r["source_scene_id"] for r in left} == {r["source_scene_id"] for r in right}
    object_exact = _hist(left, "object_count") == _hist(right, "object_count")
    zero_trunc = not any(row["tokenizer_truncated"] for row in left + right)
    gates = {
        "equal_example_count": len(left) == len(right), "scene_pool_exact": scene_exact,
        "object_count_strata_exact": object_exact, "shared_1_2_relation_subset_exact": shared_exact,
        "zero_clip_truncation": zero_trunc,
        "relation_family_balance": family_delta <= FAMILY_MAX_ABS_PROPORTION_DELTA,
        "direction_balance": direction_delta <= DIRECTION_MAX_ABS_PROPORTION_DELTA,
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL", "gates": gates,
        "rows": {"IS-SUPPORT-12": len(left), "IS-SUPPORT-14": len(right)},
        "eligible_scene_count": len(compiled["eligible_scenes"]),
        "excluded_scene_count": len(compiled["excluded"]),
        "exclusion_reasons": dict(sorted(Counter(x["reason"] for x in compiled["excluded"]).items())),
        "relation_count_histogram": {"IS-SUPPORT-12": _hist(left, "relation_count"), "IS-SUPPORT-14": _hist(right, "relation_count")},
        "relation_family": {"counts": family_counts, "proportions": family_props, "max_abs_proportion_delta": family_delta, "frozen_tolerance": FAMILY_MAX_ABS_PROPORTION_DELTA},
        "direction": {"counts": direction_counts, "proportions": direction_props, "max_abs_proportion_delta": direction_delta, "frozen_tolerance": DIRECTION_MAX_ABS_PROPORTION_DELTA},
        "scene_object_strata": {"scene_pool_exact": scene_exact, "object_count_histogram": {"IS-SUPPORT-12": _hist(left, "object_count"), "IS-SUPPORT-14": _hist(right, "object_count")}},
        "shared_subset": {"slots": list(SHARED_SLOTS), "rows_compared": shared_rows, "exact_selection_surface_tokens_topology": shared_exact},
        "clip_tokens": {"IS-SUPPORT-12": _token_stats(left), "IS-SUPPORT-14": _token_stats(right), "max_allowed": CLIP_MAX_TOKENS, "truncated_rows": sum(int(r["tokenizer_truncated"]) for r in left + right)},
        "corpus_jsonl_sha256": compiled["jsonl_sha256"],
    }
