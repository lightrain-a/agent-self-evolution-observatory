from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
PREREG_SHA256 = "483235155b6fec941969a4a766cbe15e50f2807b06828e625942f3d731d0e231"
SUBSET_SHA256 = "da1e5abab701e3a5ab150e3abc530043ddf5f01a4b91efd7f094293a27354bf4"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_paths(metadata_root: Path, prereg: dict) -> tuple[list[str], dict]:
    import pyarrow.parquet as pq

    selected: set[str] = set()
    per_task = {}
    video_features = None
    for task_index in map(int, prereg["panel"]["task_indices"]):
        path = metadata_root / f"chunk-{task_index:03d}" / "file-000.parquet"
        table = pq.read_table(path)
        data = table.to_pydict()
        if len(data["episode_index"]) != 200 or set(map(int, data["task_index"])) != {task_index}:
            raise ValueError(f"task {task_index}: metadata drift")
        if video_features is None:
            video_features = sorted(
                name[len("videos/") : -len("/chunk_index")]
                for name in table.column_names
                if name.startswith("videos/") and name.endswith("/chunk_index")
            )
            if len(video_features) != 6:
                raise ValueError(f"expected six video features, got {video_features}")
        data_paths = {
            f"data/chunk-{int(chunk):03d}/file-{int(file_idx):03d}.parquet"
            for chunk, file_idx in zip(data["data/chunk_index"], data["data/file_index"], strict=True)
        }
        video_paths = set()
        for feature in video_features:
            video_paths.update(
                f"videos/{feature}/chunk-{int(chunk):03d}/file-{int(file_idx):03d}.mp4"
                for chunk, file_idx in zip(
                    data[f"videos/{feature}/chunk_index"],
                    data[f"videos/{feature}/file_index"],
                    strict=True,
                )
            )
        selected.update(data_paths)
        selected.update(video_paths)
        per_task[str(task_index)] = {
            "data_file_count": len(data_paths),
            "video_file_count": len(video_paths),
            "selected_file_count": len(data_paths | video_paths),
        }
    return sorted(selected), {"video_features": video_features or [], "per_task": per_task}


def tree_blob_map(repo: Path, paths: list[str]) -> dict[str, str]:
    # Query only the frozen selected paths. The dataset checkout is a partial clone;
    # reading blob bodies can trigger lazy network fetches even though ls-tree does not.
    raw = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "-z", "HEAD", "--", *paths])
    mapping = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        left, path = entry.split(b"\t", 1)
        _, obj_type, blob_sha = left.split()
        if obj_type == b"blob":
            mapping[path.decode("utf-8")] = blob_sha.decode("ascii")
    missing = [path for path in paths if path not in mapping]
    if missing:
        raise ValueError(f"selected paths absent from pinned tree: {missing[:10]}")
    return mapping


def parse_lfs_pointer(content: bytes) -> tuple[str, int]:
    lines = content.decode("utf-8").splitlines()
    if not lines or lines[0] != "version https://git-lfs.github.com/spec/v1":
        raise ValueError("not a canonical Git LFS v1 pointer")
    fields = {}
    for line in lines[1:]:
        if " " in line:
            key, value = line.split(" ", 1)
            fields[key] = value
    oid_field = fields.get("oid", "")
    size_text = fields.get("size", "")
    if not oid_field.startswith("sha256:"):
        raise ValueError("LFS pointer missing sha256 oid")
    oid = oid_field.split(":", 1)[1]
    if len(oid) != 64 or any(ch not in "0123456789abcdef" for ch in oid):
        raise ValueError("invalid LFS sha256 oid")
    if not size_text.isdigit() or int(size_text) <= 0:
        raise ValueError("invalid LFS size")
    return oid, int(size_text)


def pointer_rows(repo: Path, paths: list[str], mapping: dict[str, str]) -> list[dict]:
    process = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**__import__("os").environ, "GIT_NO_LAZY_FETCH": "1"},
    )
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    rows = []
    for path in paths:
        process.stdin.write((mapping[path] + "\n").encode("ascii"))
        process.stdin.flush()
        header = process.stdout.readline().decode("ascii").strip().split()
        if len(header) != 3:
            raise RuntimeError(f"bad cat-file header for {path}: {header}")
        blob_sha, obj_type, size_text = header
        if obj_type != "blob":
            raise RuntimeError(f"bad git object type for {path}: {obj_type}")
        content = process.stdout.read(int(size_text))
        if process.stdout.read(1) != b"\n":
            raise RuntimeError(f"cat-file framing error for {path}")
        oid, lfs_size = parse_lfs_pointer(content)
        rows.append({
            "path": path,
            "git_blob_sha1": blob_sha,
            "lfs_oid_sha256": oid,
            "lfs_size_bytes": lfs_size,
            "metadata_transport": "full Git pointer clone only; GIT_LFS_SKIP_SMUDGE=1; payload body not downloaded",
            "observed_repo_commit": DATASET_REVISION,
        })
    process.stdin.close()
    error = process.stderr.read().decode("utf-8", errors="replace")
    rc = process.wait()
    if rc != 0:
        raise RuntimeError(f"git cat-file failed ({rc}): {error[:1000]}")
    return rows


def compile_manifest(prereg_path: Path, subset_path: Path, metadata_root: Path, git_repo: Path) -> dict:
    if sha256_file(prereg_path) != PREREG_SHA256:
        raise ValueError("shared-child preregistration drift")
    if sha256_file(subset_path) != SUBSET_SHA256:
        raise ValueError("shared-child subset qualification drift")
    prereg = load_json(prereg_path)
    subset = load_json(subset_path)
    if prereg.get("object_id") != OBJECT_ID or subset.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    revision = subprocess.check_output(["git", "-C", str(git_repo), "rev-parse", "HEAD"], text=True).strip()
    if revision != DATASET_REVISION:
        raise ValueError(f"dataset git revision drift: {revision}")

    paths, meta = derive_paths(metadata_root, prereg)
    rows = pointer_rows(git_repo, paths, tree_blob_map(git_repo, paths))
    data_rows = [row for row in rows if row["path"].startswith("data/")]
    video_rows = [row for row in rows if row["path"].startswith("videos/")]
    manifest_text = "".join(
        f'{row["path"]}\t{row["lfs_oid_sha256"]}\t{row["lfs_size_bytes"]}\n' for row in rows
    )
    total = sum(row["lfs_size_bytes"] for row in rows)
    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-payload-manifest-v1",
        "object_id": OBJECT_ID,
        "status": "SELECTED_PAYLOAD_MANIFEST_FROZEN_ZERO_DOWNLOAD",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "payload_materialization_authorized": False,
        "policy_outcomes_read": False,
        "payload_bytes_downloaded": 0,
        "dataset": {"repo_id": "behavior-1k/2026-challenge-demos", "revision": DATASET_REVISION},
        "bindings": {"preregistration_sha256": PREREG_SHA256, "subset_qualification_sha256": SUBSET_SHA256},
        "selection": {
            "task_count": 26,
            "episode_count": 5200,
            "metadata_fields_used_for_path_derivation": [
                "task_index", "episode_index", "data/chunk_index", "data/file_index",
                "videos/*/chunk_index", "videos/*/file_index",
            ],
            **meta,
        },
        "summary": {
            "total_file_count": len(rows),
            "total_bytes": total,
            "total_gib": total / (1024**3),
            "total_tib": total / (1024**4),
            "data_file_count": len(data_rows),
            "data_bytes": sum(row["lfs_size_bytes"] for row in data_rows),
            "video_file_count": len(video_rows),
            "video_bytes": sum(row["lfs_size_bytes"] for row in video_rows),
            "path_oid_size_manifest_sha256": hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
        },
        "files": rows,
        "next_gate": "content-address the frozen public GR00T terminal checkpoint; payload download remains forbidden",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--git-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = compile_manifest(args.prereg, args.subset, args.metadata_root, args.git_repo)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "artifact_sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
