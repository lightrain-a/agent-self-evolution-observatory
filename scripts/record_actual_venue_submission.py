#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_acceptance_ledger import (
    advance_frozen_paper_to_submitted,
    record_frozen_contract_actual_submission,
    validate_paper_ledger,
)
from research_pipeline.venue_submission_receipt import (
    build_submission_receipt,
    external_transition_authority_ref,
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def parse_uploaded(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"uploaded hash must use label=sha256: {value}")
        label, sha = value.split("=", 1)
        label = label.strip()
        sha = sha.strip().lower()
        if not label or len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
            raise ValueError(f"invalid uploaded artifact binding: {value}")
        if label in result:
            raise ValueError(f"duplicate uploaded artifact label: {label}")
        result[label] = sha
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record a real venue submission only after current Human Signoff. This command is not a submission client; it records an already completed human upload."
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--venue-submission-id", required=True)
    parser.add_argument("--venue-forum-ref", required=True)
    parser.add_argument("--uploaded", action="append", default=[], help="Actual uploaded artifact hash as label=sha256; repeat for every frozen artifact.")
    parser.add_argument("--submitted-at", required=True)
    parser.add_argument("--external-human-submission-authority-ref", required=True)
    args = parser.parse_args()

    root = args.root
    paper = load(root / "paper-acceptance" / f"{args.paper_id}.json")
    freeze = load(root / "paper-submission-freezes" / f"{args.paper_id}.json")
    handoff = load(root / "paper-submission-handoffs" / f"{args.paper_id}.json")
    signoff_path = root / "paper-human-signoffs" / f"{args.paper_id}.json"
    if not signoff_path.exists():
        parser.error("current Human Signoff ledger is required before actual venue submission can be recorded")
    signoff = load(signoff_path)
    uploaded = parse_uploaded(args.uploaded)
    if not uploaded:
        parser.error("at least one --uploaded label=sha256 binding is required; hashes must describe the files actually uploaded")

    receipt = build_submission_receipt(
        paper_ledger=paper,
        freeze_ledger=freeze,
        handoff_ledger=handoff,
        signoff_ledger=signoff,
        venue_submission_id=args.venue_submission_id,
        venue_forum_ref=args.venue_forum_ref,
        uploaded_artifact_sha256=uploaded,
        submitted_at=args.submitted_at,
        external_human_submission_authority_ref=args.external_human_submission_authority_ref,
    )
    row = record_frozen_contract_actual_submission(root, args.paper_id, receipt)
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError(f"paper ledger invalid after actual-submission receipt: {errors}")
    transition_ref = external_transition_authority_ref(receipt)
    result = advance_frozen_paper_to_submitted(
        root,
        args.paper_id,
        external_submission_authority_ref=transition_ref,
        actor="actual-venue-submission",
    )
    if result["receipt"].get("allowed") is not True:
        raise RuntimeError(f"SUBMITTED transition blocked: {result['receipt'].get('blockers')}")
    print(json.dumps({
        "status": "SUBMITTED",
        "paper_id": args.paper_id,
        "venue_submission_id": receipt["venue_submission_id"],
        "venue_forum_ref": receipt["venue_forum_ref"],
        "submission_receipt_sha256": receipt["submission_receipt_sha256"],
        "transition_authority_ref": transition_ref,
        "current_state": result["ledger"]["current_state"],
        "submission_authority": False,
        "ledger_validation_errors": validate_paper_ledger(result["ledger"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
