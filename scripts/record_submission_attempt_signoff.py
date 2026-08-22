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
    build_attempt_human_signoff,
    build_attempt_signoff_template,
    current_attempt_workflow_summary,
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Record explicit human signoff for one child submission attempt. This command never performs the actual venue upload.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--show-template", action="store_true")
    parser.add_argument("--confirm", action="append", default=[], dest="confirmed_check_ids")
    parser.add_argument("--external-human-confirmation-ref", default="")
    parser.add_argument("--confirmed-at", default="")
    parser.add_argument("--acknowledge-current-artifact-hashes", action="store_true")
    parser.add_argument("--acknowledge-actual-submission-not-performed", action="store_true")
    args = parser.parse_args()

    row = load_workflow(args.root, args.attempt_id)
    if args.show_template:
        print(json.dumps(build_attempt_signoff_template(row), ensure_ascii=False, indent=2))
        return

    receipt = build_attempt_human_signoff(
        workflow_ledger=row,
        confirmed_check_ids=args.confirmed_check_ids,
        external_human_confirmation_ref=args.external_human_confirmation_ref,
        confirmed_at=args.confirmed_at,
        acknowledge_current_artifact_hashes=args.acknowledge_current_artifact_hashes,
        acknowledge_actual_submission_not_performed=args.acknowledge_actual_submission_not_performed,
    )
    row = append_attempt_workflow_receipt(args.root, receipt)
    errors = validate_attempt_workflow_ledger(row)
    if errors:
        raise RuntimeError(errors)
    summary = current_attempt_workflow_summary(row)
    print(json.dumps({
        "status": "PASS_ATTEMPT_HUMAN_SIGNOFF_RECORDED",
        "paper_id": row["paper_id"],
        "attempt_id": row["attempt_id"],
        "attempt_sha256": row["attempt_sha256"],
        "attempt_signoff_sha256": receipt["attempt_signoff_sha256"],
        "workflow_status": summary["status"],
        "actual_submission_performed": False,
        "parent_signoff_reuse_forbidden": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
