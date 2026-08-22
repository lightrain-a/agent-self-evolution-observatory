#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_child_claim_audit import (
    build_child_claim_audit,
    public_child_claim_audit,
    publish_child_claim_audit,
    validate_child_claim_audit_ledger,
)
from research_pipeline.reopened_scientific_evidence_paper_handoff import validate_scientific_evidence_paper_handoff, validate_paper_revision_handoff_ledger


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_handoff(root: Path, attempt_sha: str) -> dict:
    row = load(root / "paper-scientific-revision-handoffs" / f"{attempt_sha}.json")
    errors = validate_paper_revision_handoff_ledger(row)
    if errors:
        raise RuntimeError(errors)
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_scientific_evidence_paper_handoff(receipt):
            return receipt
    raise RuntimeError("valid scientific-evidence paper handoff not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Independently audit reopened child-paper candidate claims against the fresh scientific evidence. This still does not update claims or unlock paper preparation automatically.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-sha256", required=True)
    parser.add_argument("--audit-packet", type=Path, required=True)
    args = parser.parse_args()
    handoff = latest_handoff(args.root, args.attempt_sha256)
    receipt = build_child_claim_audit(handoff=handoff, audit_packet=load(args.audit_packet))
    ledger = publish_child_claim_audit(args.root, receipt)
    errors = validate_child_claim_audit_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_child_claim_audit(args.root, args.attempt_sha256)
    print(json.dumps({
        "status": "PASS_CHILD_CLAIM_AUDIT_RECORDED",
        "paper_id": receipt["paper_id"],
        "attempt_sha256": receipt["attempt_sha256"],
        "child_claim_audit_sha256": receipt["child_claim_audit_sha256"],
        "audit_status": receipt["status"],
        "supported_claims": len(receipt["supported_claim_ids"]),
        "held_new_claims": len(receipt["held_new_claim_ids"]),
        "failed_claims": len(receipt["failed_claim_ids"]),
        "paper_contract_revision_eligible": receipt["paper_contract_revision_eligible"],
        "claim_update_authorized": False,
        "paper_preparation_eligible": False,
        "submission_eligible": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
