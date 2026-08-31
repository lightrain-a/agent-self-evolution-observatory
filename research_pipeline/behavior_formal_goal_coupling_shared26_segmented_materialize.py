from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from behavior_formal_goal_coupling_shared26_materialize import (
    AUTHORITY_SHA256,
    DATASET_REVISION,
    MATERIALIZATION_MANIFEST_SHA256,
    download_lfs,
    exclusive_materialization_lock,
    load_and_validate,
    safe_destination,
    sha256_file,
    verify_file,
)

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
SEGMENT_PLAN_SHA256 = "1ad14491dbbcbff289bdaada9bcd02c64ff271a7374e4e9bcdff28c8d11d493a"
BASE_RUNNER_SHA256 = "a8c4ab53f3b7ba3b762dad110bf80ecc5010de35501432538b1a48885ae46f72"
MAX_WORKERS = 4
SAFETY_FREE_BYTES = 64 * 1024 ** 3


def segment_digest(rows: list[dict]) -> str:
    text = "".join(f'{row["path"]}\t{row["lfs_oid_sha256"]}\t{row["lfs_size_bytes"]}\n' for row in rows)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_segment(
    manifest_path: Path,
    authority_path: Path,
    plan_path: Path,
    git_repo: Path,
    base_runner_path: Path,
    segment_id: str,
) -> tuple[dict, dict, list[dict]]:
    manifest, authority = load_and_validate(manifest_path, authority_path, git_repo)
    if sha256_file(base_runner_path) != BASE_RUNNER_SHA256:
        raise ValueError("base materializer helper SHA drift")
    if sha256_file(plan_path) != SEGMENT_PLAN_SHA256:
        raise ValueError("segment plan SHA drift")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("object_id") != OBJECT_ID or manifest.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    matches = [row for row in plan["segments"] if row["segment_id"] == segment_id]
    if len(matches) != 1:
        raise ValueError(f"unknown/non-unique segment id: {segment_id}")
    segment = matches[0]
    start = int(segment["start_index"])
    stop = int(segment["stop_index_exclusive"])
    rows = manifest["required_payload"][start:stop]
    if len(rows) != int(segment["file_count"]):
        raise ValueError("segment file count drift")
    if sum(int(row["lfs_size_bytes"]) for row in rows) != int(segment["bytes"]):
        raise ValueError("segment byte accounting drift")
    if segment_digest(rows) != segment["segment_path_oid_size_sha256"]:
        raise ValueError("segment path/OID/size digest drift")
    return authority, segment, rows


def _one(destination_root: Path, row: dict) -> dict:
    expected_size = int(row["lfs_size_bytes"])
    expected_sha = row["lfs_oid_sha256"]
    destination = safe_destination(destination_root, row["path"])
    before_part = destination.with_name(destination.name + ".part")
    before_size = before_part.stat().st_size if before_part.exists() else 0
    if destination.exists():
        if not verify_file(destination, expected_size, expected_sha):
            raise ValueError(f"existing finalized file mismatch: {row['path']}")
        return {"path": row["path"], "size": expected_size, "sha256": expected_sha, "state": "verified-existing", "transported_bytes": 0}
    result = download_lfs(destination, row["path"], expected_size, expected_sha)
    transported = int(result["transported_bytes"])
    if result["state"] == "resumed-complete-and-verified":
        transported = 0
    elif transported == 0 and before_size < expected_size:
        transported = expected_size - before_size
    return {"path": row["path"], "size": expected_size, "sha256": expected_sha, "state": result["state"], "transported_bytes": transported}


def materialize_segment(
    manifest_path: Path,
    authority_path: Path,
    plan_path: Path,
    git_repo: Path,
    base_runner_path: Path,
    destination_root: Path,
    segment_id: str,
    receipt_path: Path,
) -> dict:
    authority, segment, rows = validate_segment(
        manifest_path, authority_path, plan_path, git_repo, base_runner_path, segment_id
    )
    if str(destination_root) != authority["destination_root"]:
        raise ValueError("destination root differs from authority")
    missing_bytes = 0
    for row in rows:
        destination = safe_destination(destination_root, row["path"])
        if destination.exists() and verify_file(destination, int(row["lfs_size_bytes"]), row["lfs_oid_sha256"]):
            continue
        part = destination.with_name(destination.name + ".part")
        existing_partial = part.stat().st_size if part.exists() else 0
        missing_bytes += max(0, int(row["lfs_size_bytes"]) - existing_partial)
    free_bytes = shutil.disk_usage(destination_root.parent).free
    if free_bytes < missing_bytes + SAFETY_FREE_BYTES:
        raise RuntimeError("insufficient disk for segment remainder plus 64 GiB safety margin")

    records: list[dict] = []
    errors: list[dict] = []
    with exclusive_materialization_lock(destination_root) as lock_path:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(_one, destination_root, row): row for row in rows}
            for future in as_completed(futures):
                row = futures[future]
                try:
                    records.append(future.result())
                except Exception as exc:
                    errors.append({"path": row["path"], "error": f"{type(exc).__name__}: {exc}"})

        # Every successful _one() result is emitted only after exact size+SHA-256 verification.
        # Because the root-level exclusive lock is held across the whole segment, no second
        # materializer can mutate a finalized file between per-file verification and receipt
        # creation. Avoid a redundant second full-segment rehash here; a single final whole-
        # materialization seal is required after all segments complete.
        verified_records = records
        verified_bytes = sum(int(row["size"]) for row in verified_records)
        part_files = [
            str(safe_destination(destination_root, row["path"]).with_name(Path(row["path"]).name + ".part"))
            for row in rows
            if safe_destination(destination_root, row["path"]).with_name(Path(row["path"]).name + ".part").exists()
        ]
        status = "PAYLOAD_SEGMENT_COMPLETE" if len(verified_records) == len(rows) and not errors else "PAYLOAD_SEGMENT_TRANSPORT_HOLD"
        receipt = {
            "schema_version": "behavior-formal-goal-coupling-shared26-payload-segment-receipt-v1",
            "object_id": OBJECT_ID,
            "status": status,
            "segment_id": segment_id,
            "segment_plan_sha256": SEGMENT_PLAN_SHA256,
            "materialization_manifest_sha256": MATERIALIZATION_MANIFEST_SHA256,
            "authority_sha256": AUTHORITY_SHA256,
            "base_runner_sha256": BASE_RUNNER_SHA256,
            "dataset_revision": DATASET_REVISION,
            "single_writer_lock_path": str(lock_path),
            "internal_transport_workers": MAX_WORKERS,
            "segment": segment,
            "verified_file_count": len(verified_records),
            "verified_bytes": verified_bytes,
            "remaining_file_count": len(rows) - len(verified_records),
            "verification_semantics": "each record returned only after exact per-file size+SHA-256 verification while the exclusive root lock is held; no redundant segment-end rehash; one final whole-materialization rehash seal remains required",
            "transported_bytes_this_invocation": sum(int(row["transported_bytes"]) for row in records),
            "verified_existing_this_invocation": sum(row["state"] == "verified-existing" for row in records),
            "completed_or_resumed_this_invocation": sum(row["state"] != "verified-existing" for row in records),
            "partial_file_count": len(part_files),
            "partial_files_are_evidence": False,
            "errors": errors,
            "records": sorted(records, key=lambda row: row["path"]),
            "model_checkpoint_weight_downloaded": False,
            "model_loaded": False,
            "gpu_used": False,
            "training_started": False,
            "policy_rollouts_started": False,
            "policy_outcomes_read": False,
        }
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Single-writer, internally bounded-parallel shared26 payload segment materializer")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--git-repo", type=Path, required=True)
    parser.add_argument("--base-runner", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--segment-id", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = materialize_segment(
        args.manifest, args.authority, args.plan, args.git_repo, args.base_runner,
        args.destination_root, args.segment_id, args.receipt,
    )
    print(json.dumps({k: receipt[k] for k in [
        "status", "segment_id", "verified_file_count", "verified_bytes",
        "remaining_file_count", "transported_bytes_this_invocation", "partial_file_count"
    ]}, sort_keys=True))
    return 0 if receipt["status"] == "PAYLOAD_SEGMENT_COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
