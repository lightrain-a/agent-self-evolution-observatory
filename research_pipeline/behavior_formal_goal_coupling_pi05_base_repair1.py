from __future__ import annotations

import argparse
import base64
import concurrent.futures
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import google_crc32c

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
REMOTE_MANIFEST_SHA256 = "eee9dbb488b19f85cf60b9eacd5556ae75b8a567b4657f45877914c4f5f2d4ad"
HOLD_SHA256 = "b92fca803ba2efdde2f70c3c0238e5824b1cdfbb4e7b2b0222cc1c6c8d90dfb1"
AUTHORITY_SHA256 = None  # checked dynamically after the authority artifact is content-addressed in canonical
PREFIX = "checkpoints/pi05_base/params/"
EXPECTED_OBJECT_COUNT = 20
EXPECTED_TOTAL_BYTES = 12_441_721_931
MAX_WORKERS = 4


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


def digests(path: Path) -> dict:
    sha = hashlib.sha256()
    md5 = hashlib.md5()  # noqa: S324 - transport verification against GCS metadata only.
    crc = google_crc32c.Checksum()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            sha.update(chunk)
            md5.update(chunk)
            crc.update(chunk)
    return {
        "sha256": sha.hexdigest(),
        "md5_b64": base64.b64encode(md5.digest()).decode("ascii"),
        "crc32c_b64": base64.b64encode(crc.digest()).decode("ascii"),
    }


def validate(path: Path, row: dict) -> dict:
    expected_size = int(row["size"])
    if not path.is_file() or path.stat().st_size != expected_size:
        raise RuntimeError(f"size mismatch for {row['name']}: {path.stat().st_size if path.exists() else -1}/{expected_size}")
    observed = digests(path)
    if row.get("md5Hash") is not None and observed["md5_b64"] != row["md5Hash"]:
        raise RuntimeError(f"MD5 mismatch for {row['name']}")
    if observed["crc32c_b64"] != row["crc32c"]:
        raise RuntimeError(f"CRC32C mismatch for {row['name']}")
    return observed


def generation_uri(row: dict) -> str:
    return f"gs://openpi-assets/{row['name']}#{row['generation']}"


def acquire_to_quarantine(row: dict, quarantine_root: Path) -> tuple[str, dict]:
    relative = row["name"][len(PREFIX) :]
    qpath = quarantine_root / relative
    qpath.parent.mkdir(parents=True, exist_ok=True)
    if qpath.exists():
        observed = validate(qpath, row)
        return "verified-existing-quarantine", observed
    tmp = qpath.with_name(qpath.name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    completed = subprocess.run(
        ["gsutil", "cp", generation_uri(row), str(tmp)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"gsutil rc={completed.returncode} for {row['name']}: {completed.stderr[-1200:]}")
    observed = validate(tmp, row)
    os.replace(tmp, qpath)
    return "downloaded-generation-pinned-to-quarantine", observed


def install_verified(qpath: Path, destination: Path, row: dict) -> dict:
    qobs = validate(qpath, row)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + ".relay.tmp")
    if tmp.exists():
        tmp.unlink()
    shutil.copyfile(qpath, tmp)
    tobs = validate(tmp, row)
    if tobs != qobs:
        raise RuntimeError(f"quarantine-to-destination digest drift for {row['name']}")
    os.replace(tmp, destination)
    stale_part = destination.with_name(destination.name + ".part")
    if stale_part.exists():
        stale_part.unlink()
    return validate(destination, row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-manifest", type=Path, required=True)
    parser.add_argument("--hold", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--quarantine-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    remote_manifest = args.remote_manifest.resolve()
    hold_path = args.hold.resolve()
    authority_path = args.authority.resolve()
    destination_root = args.destination_root.resolve()
    quarantine_root = args.quarantine_root.resolve()
    receipt_path = args.receipt.resolve()

    if sha256_file(remote_manifest) != REMOTE_MANIFEST_SHA256:
        raise RuntimeError("remote manifest SHA drift")
    if sha256_file(hold_path) != HOLD_SHA256:
        raise RuntimeError("original HOLD SHA drift")
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    if authority.get("status") != "AUTHORIZED_TRANSPORT_ONLY_REPAIR1":
        raise RuntimeError("repair authority not active")
    if authority.get("parallel_transport_workers") != MAX_WORKERS:
        raise RuntimeError("repair worker count drift")

    manifest = json.loads(remote_manifest.read_text(encoding="utf-8"))
    rows = manifest["objects"]
    if len(rows) != EXPECTED_OBJECT_COUNT or manifest["total_bytes"] != EXPECTED_TOTAL_BYTES:
        raise RuntimeError("frozen object set drift")

    destination_root.mkdir(parents=True, exist_ok=True)
    quarantine_root.mkdir(parents=True, exist_ok=True)
    lock_path = Path("/data/wyt/.formal-goal-pi05-base-params-v1.acquire.lock")
    acquisition_states: dict[str, str] = {}
    error: str | None = None

    with exclusive_lock(lock_path):
        try:
            missing_rows = []
            for row in rows:
                relative = row["name"][len(PREFIX) :]
                dest = destination_root / relative
                if dest.exists():
                    validate(dest, row)
                    acquisition_states[row["name"]] = "verified-existing-destination"
                else:
                    missing_rows.append(row)

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                futures = {pool.submit(acquire_to_quarantine, row, quarantine_root): row for row in missing_rows}
                for future in concurrent.futures.as_completed(futures):
                    row = futures[future]
                    state, _ = future.result()
                    acquisition_states[row["name"]] = state

            # Install only after every missing remote object exists and verifies in quarantine.
            for row in missing_rows:
                relative = row["name"][len(PREFIX) :]
                qpath = quarantine_root / relative
                destination = destination_root / relative
                install_verified(qpath, destination, row)
                acquisition_states[row["name"]] += "+installed-verified"

            # Full end-to-end revalidation of all 20 scientific checkpoint objects.
            final_records = []
            for row in rows:
                relative = row["name"][len(PREFIX) :]
                destination = destination_root / relative
                observed = validate(destination, row)
                final_records.append({
                    "name": row["name"],
                    "relative_path": relative,
                    "size": int(row["size"]),
                    "generation": row["generation"],
                    "remote_md5_b64": row.get("md5Hash"),
                    "remote_crc32c_b64": row["crc32c"],
                    "local_sha256": observed["sha256"],
                    "local_md5_b64": observed["md5_b64"],
                    "local_crc32c_b64": observed["crc32c_b64"],
                    "transport_state": acquisition_states[row["name"]],
                })
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            final_records = []
            for row in rows:
                relative = row["name"][len(PREFIX) :]
                destination = destination_root / relative
                try:
                    observed = validate(destination, row)
                except Exception:
                    continue
                final_records.append({
                    "name": row["name"],
                    "relative_path": relative,
                    "size": int(row["size"]),
                    "generation": row["generation"],
                    "remote_md5_b64": row.get("md5Hash"),
                    "remote_crc32c_b64": row["crc32c"],
                    "local_sha256": observed["sha256"],
                    "local_md5_b64": observed["md5_b64"],
                    "local_crc32c_b64": observed["crc32c_b64"],
                    "transport_state": acquisition_states.get(row["name"], "verified-after-hold"),
                })

    verified_bytes = sum(x["size"] for x in final_records)
    complete = error is None and len(final_records) == EXPECTED_OBJECT_COUNT and verified_bytes == EXPECTED_TOTAL_BYTES
    receipt = {
        "schema_version": "behavior-formal-goal-coupling-pi05-base-transport-repair1-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_BASE_TRANSPORT_REPAIR1_COMPLETE" if complete else "PI05_BASE_TRANSPORT_REPAIR1_HOLD",
        "original_hold_path": str(hold_path),
        "original_hold_sha256": HOLD_SHA256,
        "authority_path": str(authority_path),
        "authority_sha256": sha256_file(authority_path),
        "remote_manifest": str(remote_manifest),
        "remote_manifest_sha256": REMOTE_MANIFEST_SHA256,
        "destination_root": str(destination_root),
        "quarantine_root": str(quarantine_root),
        "parallel_transport_workers": MAX_WORKERS,
        "verified_object_count": len(final_records),
        "expected_object_count": EXPECTED_OBJECT_COUNT,
        "verified_bytes": verified_bytes,
        "expected_bytes": EXPECTED_TOTAL_BYTES,
        "error": error,
        "objects": final_records,
        "quarantine_is_scientific_evidence": False,
        "partial_files_are_scientific_evidence": False,
        "model_checkpoint_weight_downloaded": complete,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "optimizer_update": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate": "PI05_NO_UPDATE_MODEL_LOAD_QUALIFICATION" if complete else "TRANSPORT_REPAIR_REVIEW",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ["status", "verified_object_count", "verified_bytes", "error", "next_gate"]}, sort_keys=True))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
