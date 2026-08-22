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
from research_pipeline.reopened_child_claim_expansion_authorization import validate_child_claim_expansion_authorization, validate_claim_expansion_authority_ledger
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


def latest_expansion_authority(root: Path, attempt_sha: str) -> dict:
    path = root / "paper-scientific-claim-expansion-authority" / f"{attempt_sha}.json"
    if not path.exists():
        raise RuntimeError("current child claim-expansion authority not found")
    row = load(path); errors = validate_claim_expansion_authority_ledger(row)
    if errors:
        raise RuntimeError(errors)
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_child_claim_expansion_authorization(receipt):
            return receipt
    raise RuntimeError("valid child claim-expansion authority not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze an immutable child paper contract revision after reopened scientific evidence and independent child Claim Audit. Parent Paper Acceptance contract/submitted bytes remain immutable.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-sha256", required=True)
    parser.add_argument("--revision-spec", type=Path, required=True)
    parser.add_argument("--use-current-claim-expansion-authority", action="store_true", help="Explicitly include the current human-approved held NEW_CHILD_CLAIM ids. Without this flag, all new claims remain excluded.")
    args = parser.parse_args()
    handoff = latest(args.root, "paper-scientific-revision-handoffs", args.attempt_sha256, validate_scientific_evidence_paper_handoff, validate_paper_revision_handoff_ledger)
    audit = latest(args.root, "paper-scientific-claim-audits", args.attempt_sha256, validate_child_claim_audit, validate_child_claim_audit_ledger)
    expansion = latest_expansion_authority(args.root, args.attempt_sha256) if args.use_current_claim_expansion_authority else None
    contract = build_child_paper_contract(handoff=handoff, claim_audit=audit, revision_spec=load(args.revision_spec), claim_expansion_authorization=expansion)
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
        "approved_new_claims": len(contract.get("approved_new_claim_ids") or []),
        "new_claim_expansion_authorized": contract.get("new_claim_expansion_authorized") is True,
        "paper_preparation_review_eligible": True,
        "paper_preparation_authorized": False,
        "parent_claim_update_authorized": False,
        "submission_eligible": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
