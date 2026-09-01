from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
MATERIALIZATION_MANIFEST_SHA256 = "9ee70726fb70750b23053e2358d3d42d4089238cd0bd52e5b74329279e961df4"
EXPECTED_FILE_COUNT = 1380
EXPECTED_BYTES = 236_480_375_583
EXPECTED_DESTINATION_ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_destination(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe manifest path: {relative}")
    root_resolved = root.resolve()
    destination = (root / rel).resolve()
    if destination != root_resolved and root_resolved not in destination.parents:
        raise ValueError(f"path escapes destination root: {relative}")
    return destination


def verify_manifest_shape(manifest: dict) -> list[dict]:
    if manifest.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    if manifest.get("bindings", {}).get("dataset_revision") != DATASET_REVISION:
        raise ValueError("dataset revision drift")
    rows = manifest.get("required_payload")
    if not isinstance(rows, list):
        raise ValueError("required_payload missing")
    summary = manifest.get("summary", {})
    if len(rows) != EXPECTED_FILE_COUNT or summary.get("required_payload_file_count") != EXPECTED_FILE_COUNT:
        raise ValueError("frozen payload file count drift")
    total = sum(int(row["lfs_size_bytes"]) for row in rows)
    if total != EXPECTED_BYTES or summary.get("required_payload_bytes") != EXPECTED_BYTES:
        raise ValueError("frozen payload byte count drift")
    return rows


def inspect_root(manifest: dict, destination_root: Path) -> dict:
    rows = verify_manifest_shape(manifest)
    verified_count = 0
    verified_bytes = 0
    missing: list[str] = []
    size_mismatch: list[dict] = []
    sha_mismatch: list[dict] = []

    for row in rows:
        relative = row["path"]
        expected_size = int(row["lfs_size_bytes"])
        expected_sha = row["lfs_oid_sha256"]
        path = safe_destination(destination_root, relative)
        if not path.is_file():
            missing.append(relative)
            continue
        observed_size = path.stat().st_size
        if observed_size != expected_size:
            size_mismatch.append({"path": relative, "expected": expected_size, "observed": observed_size})
            continue
        observed_sha = sha256_file(path)
        if observed_sha != expected_sha:
            sha_mismatch.append({"path": relative, "expected": expected_sha, "observed": observed_sha})
            continue
        verified_count += 1
        verified_bytes += expected_size

    partials = sorted(str(p.relative_to(destination_root)) for p in destination_root.rglob("*.part") if p.is_file())
    passed = (
        verified_count == EXPECTED_FILE_COUNT
        and verified_bytes == EXPECTED_BYTES
        and not missing
        and not size_mismatch
        and not sha_mismatch
        and not partials
    )
    return {
        "verified_file_count": verified_count,
        "verified_bytes": verified_bytes,
        "missing_file_count": len(missing),
        "size_mismatch_count": len(size_mismatch),
        "sha_mismatch_count": len(sha_mismatch),
        "partial_file_count": len(partials),
        "missing_files": missing,
        "size_mismatches": size_mismatch,
        "sha_mismatches": sha_mismatch,
        "partial_files": partials,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only whole-manifest rehash seal for the frozen BEHAVIOR shared26 payload")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.destination_root.resolve() != EXPECTED_DESTINATION_ROOT.resolve():
        raise ValueError("destination root differs from frozen shared26 root")
    if sha256_file(args.manifest) != MATERIALIZATION_MANIFEST_SHA256:
        raise ValueError("materialization manifest SHA drift")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    lock_path = args.destination_root.parent / f".{args.destination_root.name}.materialization.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"materialization writer still holds lock: {lock_path}") from exc
        result = inspect_root(manifest, args.destination_root)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-whole-manifest-final-seal-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "WHOLE_MANIFEST_FINAL_SEAL_PASS" if result["passed"] else "WHOLE_MANIFEST_FINAL_SEAL_HOLD",
        "materialization_manifest_sha256": MATERIALIZATION_MANIFEST_SHA256,
        "dataset_revision": DATASET_REVISION,
        "destination_root": str(args.destination_root),
        "single_writer_lock_path": str(lock_path),
        "expected_file_count": EXPECTED_FILE_COUNT,
        "expected_bytes": EXPECTED_BYTES,
        **{k: v for k, v in result.items() if k != "passed"},
        "network_access_used": False,
        "repair_or_download_attempted": False,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate_if_pass": "SHARED26_NORMALIZATION_AND_ZERO_UPDATE_DATA_RUNTIME_QUALIFICATION",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "verified_file_count": receipt["verified_file_count"],
        "verified_bytes": receipt["verified_bytes"],
        "missing_file_count": receipt["missing_file_count"],
        "size_mismatch_count": receipt["size_mismatch_count"],
        "sha_mismatch_count": receipt["sha_mismatch_count"],
        "partial_file_count": receipt["partial_file_count"],
    }, sort_keys=True))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
