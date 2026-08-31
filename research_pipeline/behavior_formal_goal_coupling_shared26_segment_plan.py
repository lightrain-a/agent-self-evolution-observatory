from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
MATERIALIZATION_MANIFEST_SHA256 = "9ee70726fb70750b23053e2358d3d42d4089238cd0bd52e5b74329279e961df4"
MAX_FILES_PER_SEGMENT = 50
MAX_BYTES_PER_SEGMENT = 8 * 1024 ** 3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def segment_digest(rows: list[dict]) -> str:
    text = "".join(f'{row["path"]}\t{row["lfs_oid_sha256"]}\t{row["lfs_size_bytes"]}\n' for row in rows)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compile_plan(manifest_path: Path) -> dict:
    if sha256_file(manifest_path) != MATERIALIZATION_MANIFEST_SHA256:
        raise ValueError("materialization manifest SHA drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    rows = manifest["required_payload"]
    segments = []
    index = 0
    while index < len(rows):
        start = index
        total_bytes = 0
        count = 0
        while index < len(rows) and count < MAX_FILES_PER_SEGMENT:
            size = int(rows[index]["lfs_size_bytes"])
            if count > 0 and total_bytes + size > MAX_BYTES_PER_SEGMENT:
                break
            total_bytes += size
            count += 1
            index += 1
        selected = rows[start:index]
        segments.append(
            {
                "segment_id": f"S{len(segments) + 1:02d}",
                "start_index": start,
                "stop_index_exclusive": index,
                "file_count": count,
                "bytes": total_bytes,
                "gib": total_bytes / (1024 ** 3),
                "segment_path_oid_size_sha256": segment_digest(selected),
                "first_path": selected[0]["path"],
                "last_path": selected[-1]["path"],
            }
        )
    if sum(row["file_count"] for row in segments) != len(rows):
        raise ValueError("segment file accounting mismatch")
    if sum(row["bytes"] for row in segments) != manifest["summary"]["required_payload_bytes"]:
        raise ValueError("segment byte accounting mismatch")
    if segments[0]["start_index"] != 0 or segments[-1]["stop_index_exclusive"] != len(rows):
        raise ValueError("segment coverage mismatch")
    for left, right in zip(segments, segments[1:]):
        if left["stop_index_exclusive"] != right["start_index"]:
            raise ValueError("segment coverage is not contiguous")
    return {
        "schema_version": "behavior-formal-goal-coupling-shared26-payload-segment-plan-v1",
        "object_id": OBJECT_ID,
        "status": "PAYLOAD_SEGMENT_PLAN_FROZEN_ZERO_TRANSPORT",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "payload_bytes_transported": 0,
        "materialization_manifest_sha256": MATERIALIZATION_MANIFEST_SHA256,
        "partition_rule": {
            "ordered_source": "required_payload rows in the frozen materialization manifest",
            "max_files_per_segment": MAX_FILES_PER_SEGMENT,
            "max_bytes_per_segment": MAX_BYTES_PER_SEGMENT,
            "no_reordering": True,
            "no_task_or_episode_selection_change": True,
        },
        "summary": {
            "segment_count": len(segments),
            "file_count": len(rows),
            "bytes": sum(row["bytes"] for row in segments),
            "gib": sum(row["bytes"] for row in segments) / (1024 ** 3),
        },
        "segments": segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = compile_plan(args.manifest)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "artifact_sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
