#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_child_claim_audit import validate_child_claim_audit, validate_child_claim_audit_ledger
from research_pipeline.reopened_child_paper_contract import build_child_paper_contract, public_child_paper_contract, publish_child_paper_contract
from research_pipeline.reopened_scientific_evidence_paper_handoff import validate_scientific_evidence_paper_handoff, validate_paper_revision_handoff_ledger


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest(root: Path, directory: str, attempt_sha: str, validator, ledger_validator) -> dict:
    row = load(root / directory / f"{attempt_sha}.json")
    errors = ledger_validator(row)
    if errors:
        raise RuntimeError(errors)
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validator(receipt):
            return receipt
    raise RuntimeError(f"valid receipt not found: {directory}/{attempt_sha}.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze an immutable child paper contract revision after reopened scientific evidence and independent child Claim Audit. Parent Paper Acceptance contract/submitted bytes remain immutable.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-sha256", required=True)
    parser.add_argument("--revision-spec", type=Path, required=True)
    args = parser.parse_args()
    handoff = latest(args.root, "paper-scientific-revision-handoffs", args.attempt_sha256, validate_scientific_evidence_paper_handoff, validate_paper_revision_handoff_ledger)
    audit = latest(args.root, "paper-scientific-claim-audits", args.attempt_sha256, validate_child_claim_audit, validate_child_claim_audit_ledger)
    contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=load(args.revision_spec))
    publish_child_paper_contract(args.root, contract)
    public = public_child_paper_contract(args.root, args.attempt_sha256)
    print(json.dumps({
        "status": "PASS_CHILD_PAPER_CONTRACT_REVISION_FROZEN",
        "paper_id": contract["paper_id"],
        "attempt_sha256": contract["attempt_sha256"],
        "child_paper_contract_id": contract["child_paper_contract_id"],
        "child_paper_contract_sha256": contract["child_paper_contract_sha256"],
        "supported_claims": len(contract["supported_claims"]),
        "held_new_claims": len(contract["held_new_claim_ids"]),
        "paper_preparation_review_eligible": True,
        "paper_preparation_authorized": False,
        "parent_claim_update_authorized": False,
        "submission_eligible": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
