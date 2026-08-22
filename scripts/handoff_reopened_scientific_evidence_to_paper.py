#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_p0_result_adjudication import validate_p0_adjudication, validate_p0_result_packet
from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_evidence_paper_handoff import (
    build_scientific_evidence_paper_handoff,
    public_scientific_evidence_paper_handoff,
    publish_scientific_evidence_paper_handoff,
    validate_paper_revision_handoff_ledger,
)
from research_pipeline.submission_attempt_lineage import validate_attempt_plan


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest(root: Path, directory: str, name: str, validator) -> dict:
    row = load(root / directory / f"{name}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validator(receipt):
            return receipt
    raise RuntimeError(f"valid receipt not found: {directory}/{name}.json")


def find_attempt(root: Path, attempt_sha: str) -> dict:
    for path in (root / "paper-submission-attempts").glob("*.json"):
        row = load(path)
        for event in reversed(row.get("events") or []):
            receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
            if isinstance(receipt, dict) and receipt.get("attempt_sha256") == attempt_sha and validate_attempt_plan(receipt):
                return receipt
    raise RuntimeError("valid submission attempt plan not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bind independently adjudicated reopened P0 METHOD-PASS evidence back to a child paper revision. This only enables manuscript revision and Claim Audit; no claim upgrade or paper preparation is authorized.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--revision-spec", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    args = parser.parse_args()
    contract = load(args.root / "scientific-contracts" / f"{args.contract_id}.json")
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("valid reopened scientific contract not found")
    attempt = find_attempt(args.root, str(contract.get("source_attempt_sha256") or ""))
    result = latest(args.root, "scientific-contract-p0-results", args.contract_id, validate_p0_result_packet)
    adjudication = latest(args.root, "scientific-contract-p0-results", args.contract_id, validate_p0_adjudication)
    receipt = build_scientific_evidence_paper_handoff(
        attempt_plan=attempt,
        reopened_contract=contract,
        p0_result_packet=result,
        p0_adjudication=adjudication,
        revision_spec=load(args.revision_spec),
    )
    ledger = publish_scientific_evidence_paper_handoff(args.root, receipt, recorded_at=args.recorded_at)
    errors = validate_paper_revision_handoff_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_scientific_evidence_paper_handoff(args.root, attempt["attempt_sha256"])
    print(json.dumps({
        "status": "PASS_SCIENTIFIC_EVIDENCE_CHILD_PAPER_HANDOFF_RECORDED",
        "paper_id": attempt["paper_id"],
        "attempt_sha256": attempt["attempt_sha256"],
        "reopened_contract_id": args.contract_id,
        "paper_revision_handoff_sha256": receipt["paper_revision_handoff_sha256"],
        "candidate_claims": len(receipt["candidate_claims"]),
        "child_manuscript_revision_eligible": True,
        "child_claim_audit_required": True,
        "claim_upgrade_authorized": False,
        "paper_preparation_eligible": False,
        "submission_eligible": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
