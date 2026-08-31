from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.parse
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
DATASET_REPO = "behavior-1k/2026-challenge-demos"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
MATERIALIZATION_MANIFEST_SHA256 = "9ee70726fb70750b23053e2358d3d42d4089238cd0bd52e5b74329279e961df4"
AUTHORITY_SHA256 = "9379a5b0d0ccd8d5fa288327a8a1f764e511828ba5a389395712f0086b0474c9"
HF_MIRROR = "https://hf-mirror.com"


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
    destination = (root / rel).resolve()
    root_resolved = root.resolve()
    if root_resolved not in destination.parents and destination != root_resolved:
        raise ValueError(f"path escapes destination root: {relative}")
    return destination


def verify_file(path: Path, expected_size: int, expected_sha256: str) -> bool:
    return path.is_file() and path.stat().st_size == expected_size and sha256_file(path) == expected_sha256


def git_inline_bytes(repo: Path, path: str, expected_blob_sha1: str) -> bytes:
    row = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "HEAD", "--", path], text=True).strip()
    if not row:
        raise ValueError(f"metadata path missing from pinned Git tree: {path}")
    left, observed_path = row.split("\t", 1)
    _mode, kind, blob_sha = left.split()
    if kind != "blob" or observed_path != path or blob_sha != expected_blob_sha1:
        raise ValueError(f"metadata Git blob drift: {path}")
    return subprocess.check_output(
        ["git", "-C", str(repo), "cat-file", "blob", blob_sha],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    )


def atomic_write_inline(destination: Path, content: bytes, expected_size: int, expected_sha256: str) -> None:
    if len(content) != expected_size or hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError(f"inline metadata verification failed before write: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".part", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        tmp = Path(tmp_name)
        if not verify_file(tmp, expected_size, expected_sha256):
            raise ValueError(f"inline metadata temp verification failed: {destination}")
        os.replace(tmp, destination)
    finally:
        tmp = Path(tmp_name)
        if tmp.exists():
            tmp.unlink()


def download_lfs(destination: Path, relative: str, expected_size: int, expected_sha256: str) -> dict:
    if destination.exists():
        if verify_file(destination, expected_size, expected_sha256):
            return {"state": "verified-existing", "transported_bytes": 0}
        raise ValueError(f"existing finalized file mismatches frozen manifest: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_name(destination.name + ".part")
    if part.exists() and part.stat().st_size > expected_size:
        raise ValueError(f"partial file exceeds frozen size: {part}")
    if part.exists() and verify_file(part, expected_size, expected_sha256):
        os.replace(part, destination)
        return {"state": "resumed-complete-and-verified", "transported_bytes": 0}
    before = part.stat().st_size if part.exists() else 0
    quoted = urllib.parse.quote(relative, safe="/")
    url = f"{HF_MIRROR}/datasets/{DATASET_REPO}/resolve/{DATASET_REVISION}/{quoted}"
    command = [
        "curl", "-fL", "--connect-timeout", "10", "--max-time", "0",
        "--retry", "3", "--retry-delay", "2", "--retry-all-errors",
        "--continue-at", "-", "--output", str(part), url,
    ]
    completed = subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"transport failed for {relative}: rc={completed.returncode}: {completed.stderr[-800:]}")
    if not verify_file(part, expected_size, expected_sha256):
        observed_size = part.stat().st_size if part.exists() else -1
        observed_sha = sha256_file(part) if part.exists() else ""
        raise ValueError(
            f"download verification failed for {relative}: size={observed_size}/{expected_size} sha={observed_sha}/{expected_sha256}"
        )
    os.replace(part, destination)
    return {"state": "downloaded-and-verified", "transported_bytes": max(0, expected_size - before)}


def load_and_validate(manifest_path: Path, authority_path: Path, git_repo: Path) -> tuple[dict, dict]:
    if sha256_file(manifest_path) != MATERIALIZATION_MANIFEST_SHA256:
        raise ValueError("materialization manifest SHA drift")
    if sha256_file(authority_path) != AUTHORITY_SHA256:
        raise ValueError("materialization authority SHA drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    if manifest.get("object_id") != OBJECT_ID or authority.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    if manifest.get("bindings", {}).get("dataset_revision") != DATASET_REVISION:
        raise ValueError("manifest dataset revision drift")
    if authority.get("dataset_revision") != DATASET_REVISION:
        raise ValueError("authority dataset revision drift")
    if not authority.get("dataset_materialization_authorized") or authority.get("gpu_authorized"):
        raise ValueError("authority scope invalid")
    if authority.get("authorized_payload_bytes") != manifest["summary"]["required_payload_bytes"]:
        raise ValueError("authority payload byte ceiling drift")
    if authority.get("authorized_payload_files") != manifest["summary"]["required_payload_file_count"]:
        raise ValueError("authority payload file count drift")
    head = subprocess.check_output(["git", "-C", str(git_repo), "rev-parse", "HEAD"], text=True).strip()
    if head != DATASET_REVISION:
        raise ValueError("pointer repository revision drift")
    return manifest, authority


def materialize(
    manifest_path: Path,
    authority_path: Path,
    git_repo: Path,
    destination_root: Path,
    receipt_path: Path,
    *,
    scope: str,
    max_files: int | None,
    max_bytes: int | None,
) -> dict:
    manifest, authority = load_and_validate(manifest_path, authority_path, git_repo)
    if str(destination_root) != authority["destination_root"]:
        raise ValueError("destination root differs from authority")
    free_bytes = shutil.disk_usage(destination_root.parent).free
    required_total = int(authority["total_byte_ceiling"])
    if not destination_root.exists() and free_bytes < required_total + 64 * 1024**3:
        raise RuntimeError("insufficient free disk for frozen payload plus 64 GiB safety margin")
    destination_root.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, dict]] = []
    if scope in {"metadata", "all"}:
        rows.extend(("metadata", row) for row in manifest["runtime_metadata"])
    if scope in {"payload", "all"}:
        rows.extend(("payload", row) for row in manifest["required_payload"])

    verified_before = 0
    completed_now = 0
    transported_bytes = 0
    processed = 0
    records = []
    for kind, row in rows:
        if max_files is not None and processed >= max_files:
            break
        if kind == "metadata" and row["storage"] == "inline-git-blob":
            expected_size = int(row["content_size_bytes"])
            expected_sha = row["content_sha256"]
        elif kind == "metadata":
            expected_size = int(row["payload_size_bytes"])
            expected_sha = row["lfs_oid_sha256"]
        else:
            expected_size = int(row["lfs_size_bytes"])
            expected_sha = row["lfs_oid_sha256"]
        if max_bytes is not None and processed > 0 and transported_bytes + expected_size > max_bytes:
            break
        destination = safe_destination(destination_root, row["path"])
        if destination.exists():
            if not verify_file(destination, expected_size, expected_sha):
                raise ValueError(f"existing finalized file mismatch: {row['path']}")
            state = "verified-existing"
            delta = 0
            verified_before += 1
        elif kind == "metadata" and row["storage"] == "inline-git-blob":
            content = git_inline_bytes(git_repo, row["path"], row["git_blob_sha1"])
            atomic_write_inline(destination, content, expected_size, expected_sha)
            state = "materialized-inline-and-verified"
            delta = 0
            completed_now += 1
        else:
            result = download_lfs(destination, row["path"], expected_size, expected_sha)
            state = result["state"]
            delta = int(result["transported_bytes"])
            if state == "verified-existing":
                verified_before += 1
            else:
                completed_now += 1
        transported_bytes += delta
        processed += 1
        records.append({"kind": kind, "path": row["path"], "size": expected_size, "sha256": expected_sha, "state": state})

    # Full current-state verification count over the requested scope, without accepting .part files.
    finalized_verified = 0
    finalized_bytes = 0
    for kind, row in rows:
        if kind == "metadata" and row["storage"] == "inline-git-blob":
            expected_size = int(row["content_size_bytes"]); expected_sha = row["content_sha256"]
        elif kind == "metadata":
            expected_size = int(row["payload_size_bytes"]); expected_sha = row["lfs_oid_sha256"]
        else:
            expected_size = int(row["lfs_size_bytes"]); expected_sha = row["lfs_oid_sha256"]
        destination = safe_destination(destination_root, row["path"])
        if destination.exists() and verify_file(destination, expected_size, expected_sha):
            finalized_verified += 1
            finalized_bytes += expected_size

    status = "MATERIALIZATION_SCOPE_COMPLETE" if finalized_verified == len(rows) else "MATERIALIZATION_PROGRESS_VERIFIED_PARTIAL"
    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-materialization-receipt-v1",
        "object_id": OBJECT_ID,
        "status": status,
        "scope": scope,
        "materialization_manifest_sha256": MATERIALIZATION_MANIFEST_SHA256,
        "authority_sha256": AUTHORITY_SHA256,
        "dataset_revision": DATASET_REVISION,
        "destination_root": str(destination_root),
        "requested_scope_file_count": len(rows),
        "processed_this_invocation": processed,
        "verified_existing_this_invocation": verified_before,
        "completed_this_invocation": completed_now,
        "transported_bytes_this_invocation": transported_bytes,
        "finalized_verified_file_count": finalized_verified,
        "finalized_verified_bytes": finalized_bytes,
        "remaining_file_count": len(rows) - finalized_verified,
        "partial_files_are_evidence": False,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "records_this_invocation": records,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded content-addressed materialization of the frozen BEHAVIOR shared26 dataset")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--git-repo", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--scope", choices=["metadata", "payload", "all"], required=True)
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--max-bytes", type=int)
    args = parser.parse_args()
    receipt = materialize(
        args.manifest, args.authority, args.git_repo, args.destination_root, args.receipt,
        scope=args.scope, max_files=args.max_files, max_bytes=args.max_bytes,
    )
    print(json.dumps({k: receipt[k] for k in [
        "status", "scope", "processed_this_invocation", "completed_this_invocation",
        "transported_bytes_this_invocation", "finalized_verified_file_count",
        "finalized_verified_bytes", "remaining_file_count"
    ]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
