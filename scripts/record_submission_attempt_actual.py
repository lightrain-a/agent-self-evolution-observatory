#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    build_attempt_actual_submission,
    current_attempt_workflow_summary,
    validate_attempt_human_signoff,
    validate_attempt_workflow_ledger,
)


def load_workflow(root: Path, attempt_id: str) -> dict:
    path = root / "paper-submission-attempt-workflows" / f"{attempt_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("attempt workflow ledger is not an object")
    errors = validate_attempt_workflow_ledger(payload)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    return payload


def latest_signoff(row: dict) -> dict:
    for event in reversed(row.get("events") or []):
        if isinstance(event, dict) and event.get("event_type") == "attempt-human-signoff":
            receipt = event.get("receipt") or {}
            if isinstance(receipt, dict) and validate_attempt_human_signoff(receipt):
                return receipt
    raise RuntimeError("valid child-attempt human signoff not found")


def parse_hash(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("uploaded hash must be LABEL=SHA256")
    label, sha = value.split("=", 1)
    label = label.strip(); sha = sha.strip().lower()
    if not label or len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
        raise argparse.ArgumentTypeError("uploaded hash must be LABEL=64-hex-SHA256")
    return label, sha


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a child attempt that a human has already uploaded to the venue. This command records the receipt only; it does not upload anything.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--venue-submission-id", required=True)
    parser.add_argument("--venue-forum-ref", required=True)
    parser.add_argument("--submitted-at", required=True)
    parser.add_argument("--external-human-submission-authority-ref", required=True)
    parser.add_argument("--uploaded-hash", action="append", type=parse_hash, required=True)
    args = parser.parse_args()

    row = load_workflow(args.root, args.attempt_id)
    signoff = latest_signoff(row)
    uploaded = {label: sha for label, sha in args.uploaded_hash}
    if len(uploaded) != len(args.uploaded_hash):
        raise RuntimeError("duplicate uploaded artifact labels are not allowed")
    receipt = build_attempt_actual_submission(
        workflow_ledger=row,
        signoff_receipt=signoff,
        venue_submission_id=args.venue_submission_id,
        venue_forum_ref=args.venue_forum_ref,
        uploaded_artifact_sha256=uploaded,
        submitted_at=args.submitted_at,
        external_human_submission_authority_ref=args.external_human_submission_authority_ref,
    )
    row = append_attempt_workflow_receipt(args.root, receipt)
    errors = validate_attempt_workflow_ledger(row)
    if errors:
        raise RuntimeError(errors)
    summary = current_attempt_workflow_summary(row)
    print(json.dumps({
        "status": "PASS_ATTEMPT_ACTUAL_SUBMISSION_RECORDED",
        "paper_id": row["paper_id"],
        "attempt_id": row["attempt_id"],
        "attempt_sha256": row["attempt_sha256"],
        "venue_submission_id": receipt["venue_submission_id"],
        "attempt_submission_receipt_sha256": receipt["attempt_submission_receipt_sha256"],
        "workflow_status": summary["status"],
        "parent_submission_receipt_reuse_forbidden": True,
        "parent_submission_bytes_immutable": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
