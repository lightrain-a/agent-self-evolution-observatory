from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
SOURCE_ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0")
RUNTIME_ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2")
SOURCE_INFO_SHA256 = "24c77f7a984bcee775e666203881a946b11a899f524fbc2405922b2109757874"
WHOLE_SEAL_SHA256 = "1890045423141532213f9398451a7f51e7c481b3ea90a5cc0fa86c3516db1a9f"
REMOVED_DEPTH_FEATURES = (
    "observation.depth_linear.left_realsense_link_camera_0",
    "observation.depth_linear.right_realsense_link_camera_0",
    "observation.depth_linear.zed_link_camera_0",
)
REQUIRED_RGB_FEATURES = (
    "observation.rgb.zed_link_camera_0",
    "observation.rgb.left_realsense_link_camera_0",
    "observation.rgb.right_realsense_link_camera_0",
)
SOURCE_META_ENTRIES = ("episodes", "stats.json", "tasks.jsonl", "tasks.parquet")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def projected_info(source_info: dict) -> dict:
    features = source_info.get("features")
    if not isinstance(features, dict):
        raise ValueError("source info.json missing features mapping")
    for key in REMOVED_DEPTH_FEATURES:
        if key not in features or features[key].get("dtype") != "video":
            raise ValueError(f"expected depth video feature missing or changed: {key}")
    for key in REQUIRED_RGB_FEATURES:
        if key not in features or features[key].get("dtype") != "video":
            raise ValueError(f"required RGB video feature missing or changed: {key}")
    result = json.loads(json.dumps(source_info))
    for key in REMOVED_DEPTH_FEATURES:
        del result["features"][key]
    return result


def verify_projection_delta(source_info: dict, runtime_info: dict) -> None:
    expected = projected_info(source_info)
    if runtime_info != expected:
        raise ValueError("runtime info differs from source by more than the three frozen depth-feature removals")


def build_projection(source_root: Path, runtime_root: Path) -> dict:
    if source_root.resolve() != SOURCE_ROOT.resolve():
        raise ValueError("source root drift")
    if runtime_root != RUNTIME_ROOT:
        raise ValueError("runtime root drift")
    if runtime_root.exists() or runtime_root.is_symlink():
        raise FileExistsError(f"runtime projection root already exists: {runtime_root}")

    source_info_path = source_root / "meta/info.json"
    if sha256_file(source_info_path) != SOURCE_INFO_SHA256:
        raise ValueError("source info.json SHA drift")
    source_info = json.loads(source_info_path.read_text(encoding="utf-8"))
    runtime_info = projected_info(source_info)

    tmp_root = runtime_root.with_name(runtime_root.name + ".tmp")
    if tmp_root.exists() or tmp_root.is_symlink():
        raise FileExistsError(f"temporary runtime projection root already exists: {tmp_root}")
    try:
        tmp_root.mkdir(parents=True)
        os.symlink(source_root / "data", tmp_root / "data", target_is_directory=True)
        os.symlink(source_root / "videos", tmp_root / "videos", target_is_directory=True)
        meta = tmp_root / "meta"
        meta.mkdir()
        for entry in SOURCE_META_ENTRIES:
            source = source_root / "meta" / entry
            if not source.exists():
                raise FileNotFoundError(source)
            os.symlink(source, meta / entry, target_is_directory=source.is_dir())
        info_path = meta / "info.json"
        info_path.write_text(json.dumps(runtime_info, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        verify_projection_delta(source_info, json.loads(info_path.read_text(encoding="utf-8")))
        os.replace(tmp_root, runtime_root)
    except Exception:
        if tmp_root.exists() and not tmp_root.is_symlink():
            shutil.rmtree(tmp_root)
        raise

    symlinks = {}
    for relative in ("data", "videos", *(f"meta/{x}" for x in SOURCE_META_ENTRIES)):
        path = runtime_root / relative
        if not path.is_symlink():
            raise RuntimeError(f"expected projection symlink missing: {relative}")
        symlinks[relative] = os.readlink(path)

    projected_path = runtime_root / "meta/info.json"
    return {
        "source_info_sha256": sha256_file(source_info_path),
        "projected_info_sha256": sha256_file(projected_path),
        "source_feature_count": len(source_info["features"]),
        "projected_feature_count": len(runtime_info["features"]),
        "removed_features": list(REMOVED_DEPTH_FEATURES),
        "required_rgb_features": list(REQUIRED_RGB_FEATURES),
        "symlinks": symlinks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the preregistered metadata-only RGB runtime view for shared26")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--whole-seal", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {args.receipt}")
    if sha256_file(args.whole_seal) != WHOLE_SEAL_SHA256:
        raise ValueError("whole-manifest final seal SHA drift")
    seal = json.loads(args.whole_seal.read_text(encoding="utf-8"))
    if seal.get("status") != "WHOLE_MANIFEST_FINAL_SEAL_PASS":
        raise ValueError("whole-manifest final seal is not PASS")

    lock_path = args.runtime_root.parent / f".{args.runtime_root.name}.projection.lock"
    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another runtime projection actor holds {lock_path}") from exc
        source_meta_hashes_before = {
            entry: sha256_file(args.source_root / "meta" / entry)
            for entry in ("info.json", "stats.json", "tasks.jsonl", "tasks.parquet")
        }
        result = build_projection(args.source_root, args.runtime_root)
        source_meta_hashes_after = {
            entry: sha256_file(args.source_root / "meta" / entry)
            for entry in ("info.json", "stats.json", "tasks.jsonl", "tasks.parquet")
        }
        if source_meta_hashes_before != source_meta_hashes_after:
            raise RuntimeError("source metadata changed while building runtime projection")
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-rgb-runtime-projection-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "RGB_RUNTIME_PROJECTION_PASS",
        "source_root": str(args.source_root),
        "runtime_root": str(args.runtime_root),
        "whole_manifest_final_seal_path": str(args.whole_seal),
        "whole_manifest_final_seal_sha256": sha256_file(args.whole_seal),
        "source_metadata_hashes_before": source_meta_hashes_before,
        "source_metadata_hashes_after": source_meta_hashes_after,
        **result,
        "scientific_payload_bytes_copied_or_reencoded": 0,
        "network_access_used": False,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate": "REPAIR2_CPU_ONLY_HUB_OFFLINE_SAMPLE_SCHEMA_QUALIFICATION",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "source_feature_count": receipt["source_feature_count"],
        "projected_feature_count": receipt["projected_feature_count"],
        "projected_info_sha256": receipt["projected_info_sha256"],
        "scientific_payload_bytes_copied_or_reencoded": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
