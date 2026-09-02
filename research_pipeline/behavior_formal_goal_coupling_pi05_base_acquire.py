from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.parse
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import google_crc32c

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
EXPECTED_REMOTE_MANIFEST_SHA256 = "eee9dbb488b19f85cf60b9eacd5556ae75b8a567b4657f45877914c4f5f2d4ad"
EXPECTED_PREFIX = "checkpoints/pi05_base/params/"
EXPECTED_OBJECT_COUNT = 20
EXPECTED_TOTAL_BYTES = 12_441_721_931
BUCKET = "openpi-assets"


@contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        os.fsync(handle.fileno())
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def all_digests(path: Path) -> tuple[str, str, str]:
    sha = hashlib.sha256()
    md5 = hashlib.md5()  # noqa: S324 - used only to verify GCS transport metadata, not for security.
    crc = google_crc32c.Checksum()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            sha.update(chunk)
            md5.update(chunk)
            crc.update(chunk)
    return (
        sha.hexdigest(),
        base64.b64encode(md5.digest()).decode("ascii"),
        base64.b64encode(crc.digest()).decode("ascii"),
    )


def validate_local(path: Path, row: dict) -> dict:
    expected_size = int(row["size"])
    if not path.is_file() or path.stat().st_size != expected_size:
        raise RuntimeError(f"local size mismatch for {row['name']}: {path.stat().st_size if path.exists() else -1}/{expected_size}")
    sha256, md5_b64, crc32c_b64 = all_digests(path)
    if row.get("md5Hash") is not None and md5_b64 != row["md5Hash"]:
        raise RuntimeError(f"GCS MD5 mismatch for {row['name']}")
    if crc32c_b64 != row["crc32c"]:
        raise RuntimeError(f"GCS CRC32C mismatch for {row['name']}")
    return {
        "name": row["name"],
        "relative_path": row["name"][len(EXPECTED_PREFIX) :],
        "size": expected_size,
        "generation": row["generation"],
        "remote_md5_b64": row.get("md5Hash"),
        "remote_crc32c_b64": row["crc32c"],
        "local_sha256": sha256,
        "local_md5_b64": md5_b64,
        "local_crc32c_b64": crc32c_b64,
    }


def download_exact(row: dict, destination: Path) -> str:
    if destination.exists():
        validate_local(destination, row)
        return "verified-existing"

    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_name(destination.name + ".part")
    expected_size = int(row["size"])
    if part.exists() and part.stat().st_size > expected_size:
        raise RuntimeError(f"partial exceeds expected size: {part}")

    encoded = urllib.parse.quote(row["name"], safe="")
    url = (
        f"https://storage.googleapis.com/download/storage/v1/b/{BUCKET}/o/{encoded}"
        f"?alt=media&generation={row['generation']}"
    )
    if expected_size == 0:
        part.parent.mkdir(parents=True, exist_ok=True)
        part.write_bytes(b"")
    else:
        command = [
            "curl",
            "-fL",
            "--connect-timeout",
            "15",
            "--max-time",
            "0",
            "--retry",
            "6",
            "--retry-delay",
            "2",
            "--retry-all-errors",
            "--continue-at",
            "-",
            "--output",
            str(part),
            url,
        ]
        completed = subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if completed.returncode != 0:
            raise RuntimeError(f"curl failed rc={completed.returncode} for {row['name']}: {completed.stderr[-1000:]}")
    validate_local(part, row)
    os.replace(part, destination)
    return "downloaded-exact-generation"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-manifest", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.remote_manifest.resolve()
    destination_root = args.destination_root.resolve()
    receipt_path = args.receipt.resolve()
    lock_path = Path("/data/wyt/.formal-goal-pi05-base-params-v1.acquire.lock")

    if sha256_file(manifest_path) != EXPECTED_REMOTE_MANIFEST_SHA256:
        raise RuntimeError("remote manifest SHA drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest["objects"]
    if manifest.get("object_count") != EXPECTED_OBJECT_COUNT or len(rows) != EXPECTED_OBJECT_COUNT:
        raise RuntimeError("remote object count drift")
    if manifest.get("total_bytes") != EXPECTED_TOTAL_BYTES or sum(int(x["size"]) for x in rows) != EXPECTED_TOTAL_BYTES:
        raise RuntimeError("remote byte total drift")
    if any(not row["name"].startswith(EXPECTED_PREFIX) for row in rows):
        raise RuntimeError("unexpected remote object prefix")

    destination_root.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    error: str | None = None
    with exclusive_lock(lock_path):
        try:
            for row in rows:
                relative = row["name"][len(EXPECTED_PREFIX) :]
                if not relative or relative.startswith("/") or ".." in Path(relative).parts:
                    raise RuntimeError(f"unsafe relative path: {relative}")
                destination = destination_root / relative
                transport_state = download_exact(row, destination)
                record = validate_local(destination, row)
                record["transport_state"] = transport_state
                records.append(record)
        except Exception as exc:  # preserve a fail-closed acquisition receipt.
            error = f"{type(exc).__name__}: {exc}"

    verified_bytes = sum(int(r["size"]) for r in records)
    complete = error is None and len(records) == EXPECTED_OBJECT_COUNT and verified_bytes == EXPECTED_TOTAL_BYTES
    receipt = {
        "schema_version": "behavior-formal-goal-coupling-pi05-base-local-content-address-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_BASE_LOCAL_CONTENT_ADDRESS_COMPLETE" if complete else "PI05_BASE_ASSET_ACQUISITION_HOLD",
        "remote_manifest": str(manifest_path),
        "remote_manifest_sha256": EXPECTED_REMOTE_MANIFEST_SHA256,
        "source": manifest["source"],
        "destination_root": str(destination_root),
        "verified_object_count": len(records),
        "expected_object_count": EXPECTED_OBJECT_COUNT,
        "verified_bytes": verified_bytes,
        "expected_bytes": EXPECTED_TOTAL_BYTES,
        "error": error,
        "objects": records,
        "model_checkpoint_weight_downloaded": complete,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "optimizer_update": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate": "PI05_NO_UPDATE_MODEL_LOAD_QUALIFICATION" if complete else "TRANSPORT_REPAIR_ONLY",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ["status", "verified_object_count", "verified_bytes", "error", "next_gate"]}, sort_keys=True))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
