from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_DATASET_REVISION = "301e409f34db633c4a4ed13fc4149440dffbcbb4"
EXPECTED_FULL_DATA_SHA256 = "c4cab948b923b522b9ba4991e167e1c5c7d503786f2b2e5c11a64dab89113c21"
EXPECTED_SCENE_COUNT = 130


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_scene(index: int, scene: dict[str, Any], instruction: str) -> None:
    if scene.get("index") != index:
        raise ValueError(f"scene {index}: index mismatch {scene.get('index')!r}")
    if scene.get("query") != instruction:
        raise ValueError(f"scene {index}: query does not match pinned full_data instruction")
    for key in ("rooms", "objects", "walls", "doors", "windows"):
        if not isinstance(scene.get(key), list):
            raise ValueError(f"scene {index}: {key} must be a list")


def build_manifest(full_data_path: Path, scene_root: Path) -> dict[str, Any]:
    full_raw = full_data_path.read_bytes()
    full_sha = sha256_bytes(full_raw)
    if full_sha != EXPECTED_FULL_DATA_SHA256:
        raise ValueError(f"full_data SHA-256 drift: {full_sha}")
    full_data = json.loads(full_raw)
    if not isinstance(full_data, list) or len(full_data) != EXPECTED_SCENE_COUNT:
        raise ValueError(f"expected {EXPECTED_SCENE_COUNT} full_data rows")

    rows: list[dict[str, Any]] = []
    total_bytes = 0
    for index, item in enumerate(full_data):
        scene_path = scene_root / f"data_{index}.json"
        raw = scene_path.read_bytes()
        total_bytes += len(raw)
        scene = json.loads(raw)
        validate_scene(index, scene, str(item.get("instruction") or ""))
        rows.append(
            {
                "index": index,
                "path": f"scenes/data_{index}.json",
                "sha256": sha256_bytes(raw),
                "bytes": len(raw),
                "rooms": len(scene["rooms"]),
                "objects": len(scene["objects"]),
                "walls": len(scene["walls"]),
                "doors": len(scene["doors"]),
                "windows": len(scene["windows"]),
            }
        )

    scene_hash_root = sha256_bytes(
        "\n".join(f"{row['index']}:{row['sha256']}" for row in rows).encode("utf-8")
    )
    return {
        "schema_version": "lego-bench-aligned-scenes-manifest-v1",
        "dataset_revision": EXPECTED_DATASET_REVISION,
        "full_data_sha256": full_sha,
        "scene_count": len(rows),
        "scene_json_bytes": total_bytes,
        "scene_hash_root": scene_hash_root,
        "all_index_query_pairs_match_full_data": True,
        "outcome_fields_inspected": False,
        "scientific_authority": False,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-data", type=Path, required=True)
    parser.add_argument("--scene-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.full_data, args.scene_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "dataset_revision": manifest["dataset_revision"],
        "scene_count": manifest["scene_count"],
        "scene_json_bytes": manifest["scene_json_bytes"],
        "scene_hash_root": manifest["scene_hash_root"],
        "outcome_fields_inspected": manifest["outcome_fields_inspected"],
        "scientific_authority": manifest["scientific_authority"],
    }, indent=2))


if __name__ == "__main__":
    main()
