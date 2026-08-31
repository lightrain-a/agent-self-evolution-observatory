from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
PAYLOAD_MANIFEST_SHA256 = "927e9b648fb46d682450c424dde4afbc815fcda2a17351bd0b22e5f725337979"
OPENPI_REVISION = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
OPENPI_R1PRO_CONFIG_SHA256 = "d3d5af8ab4c5eca57cd33cdf81fdbc23dea78aa2cb7932736c8722687d0d1e1c"
RGB_FEATURES = {
    "observation.rgb.zed_link_camera_0",
    "observation.rgb.left_realsense_link_camera_0",
    "observation.rgb.right_realsense_link_camera_0",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_lfs_pointer(content: bytes) -> tuple[str, int] | None:
    if not content.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        return None
    fields = {}
    for line in content.decode("utf-8").splitlines()[1:]:
        if " " in line:
            key, value = line.split(" ", 1)
            fields[key] = value
    oid_field = fields.get("oid", "")
    size_text = fields.get("size", "")
    if not oid_field.startswith("sha256:") or not size_text.isdigit():
        raise ValueError("malformed Git LFS pointer")
    oid = oid_field.split(":", 1)[1]
    size = int(size_text)
    if len(oid) != 64 or size <= 0:
        raise ValueError("invalid Git LFS pointer")
    return oid, size


def git_blob(repo: Path, path: str) -> tuple[str, bytes]:
    row = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "HEAD", "--", path], text=True).strip()
    if not row:
        raise ValueError(f"missing git path: {path}")
    left, observed = row.split("\t", 1)
    _mode, kind, blob_sha = left.split()
    if kind != "blob" or observed != path:
        raise ValueError(f"bad tree entry for {path}")
    content = subprocess.check_output(
        ["git", "-C", str(repo), "cat-file", "blob", blob_sha],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    )
    return blob_sha, content


def compile_manifest(payload_path: Path, dataset_repo: Path, openpi_repo: Path) -> dict:
    if sha256_file(payload_path) != PAYLOAD_MANIFEST_SHA256:
        raise ValueError("frozen payload manifest drift")
    dataset_head = subprocess.check_output(["git", "-C", str(dataset_repo), "rev-parse", "HEAD"], text=True).strip()
    openpi_head = subprocess.check_output(["git", "-C", str(openpi_repo), "rev-parse", "HEAD"], text=True).strip()
    if dataset_head != DATASET_REVISION or openpi_head != OPENPI_REVISION:
        raise ValueError("source revision drift")
    r1pro_path = openpi_repo / "src/openpi/configs/robots/b1k.py"
    if sha256_file(r1pro_path) != OPENPI_R1PRO_CONFIG_SHA256:
        raise ValueError("OpenPI R1Pro observation map drift")
    source_text = r1pro_path.read_text(encoding="utf-8")
    for feature in RGB_FEATURES:
        if feature not in source_text:
            raise ValueError(f"required RGB feature missing from pinned R1Pro config: {feature}")
    if "depth_linear" in source_text:
        raise ValueError("pinned R1Pro config unexpectedly declares depth input")

    full = json.loads(payload_path.read_text(encoding="utf-8"))
    required_payload = []
    for row in full["files"]:
        path = row["path"]
        if path.startswith("data/"):
            required_payload.append(row)
            continue
        if path.startswith("videos/"):
            feature = path.split("/", 2)[1]
            if feature in RGB_FEATURES:
                required_payload.append(row)
    if not required_payload:
        raise ValueError("required payload projection is empty")

    meta_paths = subprocess.check_output(
        ["git", "-C", str(dataset_repo), "ls-tree", "-r", "--name-only", "HEAD", "meta"], text=True
    ).splitlines()
    metadata_rows = []
    for path in meta_paths:
        blob_sha, content = git_blob(dataset_repo, path)
        lfs = parse_lfs_pointer(content)
        if lfs is None:
            metadata_rows.append({
                "path": path,
                "storage": "inline-git-blob",
                "git_blob_sha1": blob_sha,
                "content_sha256": hashlib.sha256(content).hexdigest(),
                "content_size_bytes": len(content),
            })
        else:
            oid, size = lfs
            metadata_rows.append({
                "path": path,
                "storage": "git-lfs",
                "git_blob_sha1": blob_sha,
                "lfs_oid_sha256": oid,
                "payload_size_bytes": size,
            })

    payload_bytes = sum(int(row["lfs_size_bytes"]) for row in required_payload)
    meta_bytes = sum(int(row.get("payload_size_bytes", row.get("content_size_bytes", 0))) for row in metadata_rows)
    data_bytes = sum(int(row["lfs_size_bytes"]) for row in required_payload if row["path"].startswith("data/"))
    video_bytes = payload_bytes - data_bytes
    full_bytes = int(full["summary"]["total_bytes"])
    payload_manifest_text = "".join(
        f'{row["path"]}\t{row["lfs_oid_sha256"]}\t{row["lfs_size_bytes"]}\n' for row in required_payload
    )
    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-pi05-materialization-manifest-v1",
        "object_id": OBJECT_ID,
        "status": "PI05_REQUIRED_FEATURE_MATERIALIZATION_FROZEN_ZERO_DOWNLOAD",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "payload_materialization_authorized": False,
        "policy_outcomes_read": False,
        "bindings": {
            "full_selected_payload_manifest_sha256": PAYLOAD_MANIFEST_SHA256,
            "dataset_revision": DATASET_REVISION,
            "openpi_revision": OPENPI_REVISION,
            "openpi_r1pro_config_sha256": OPENPI_R1PRO_CONFIG_SHA256,
        },
        "source_projection": {
            "required_video_features": sorted(RGB_FEATURES),
            "forbidden_as_unused": [
                "observation.depth_linear.left_realsense_link_camera_0",
                "observation.depth_linear.right_realsense_link_camera_0",
                "observation.depth_linear.zed_link_camera_0",
            ],
            "reason": "pinned OpenPI R1Pro observation map consumes exactly three RGB cameras and does not declare depth input",
        },
        "summary": {
            "required_payload_file_count": len(required_payload),
            "required_data_file_count": sum(row["path"].startswith("data/") for row in required_payload),
            "required_rgb_video_file_count": sum(row["path"].startswith("videos/") for row in required_payload),
            "required_payload_bytes": payload_bytes,
            "required_payload_gib": payload_bytes / (1024 ** 3),
            "data_bytes": data_bytes,
            "data_gib": data_bytes / (1024 ** 3),
            "rgb_video_bytes": video_bytes,
            "rgb_video_gib": video_bytes / (1024 ** 3),
            "full_upper_bound_bytes": full_bytes,
            "avoided_unused_depth_bytes": full_bytes - payload_bytes,
            "avoided_unused_depth_gib": (full_bytes - payload_bytes) / (1024 ** 3),
            "runtime_metadata_file_count": len(metadata_rows),
            "runtime_metadata_bytes": meta_bytes,
            "runtime_metadata_mib": meta_bytes / (1024 ** 2),
            "required_payload_path_oid_size_manifest_sha256": hashlib.sha256(payload_manifest_text.encode("utf-8")).hexdigest(),
        },
        "runtime_metadata": metadata_rows,
        "required_payload": required_payload,
        "next_gate": "freeze the pi0.5 shared-subset child config and zero-update source/data-constructor smoke; no payload download or model load yet",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload-manifest", type=Path, required=True)
    parser.add_argument("--dataset-repo", type=Path, required=True)
    parser.add_argument("--openpi-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = compile_manifest(args.payload_manifest, args.dataset_repo, args.openpi_repo)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "artifact_sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
