#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.scientific_reopen_protocol import (
    build_scientific_reopen_authorization,
    public_scientific_reopen_summary,
    publish_scientific_reopen_receipt,
    validate_scientific_reopen_ledger,
    validate_scientific_reopen_proposal,
)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "unknown-paper"


def load_ledger(root: Path, paper_id: str) -> dict:
    path = root / "paper-scientific-reopen" / f"{slug(paper_id)}.json"
    row = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(f"scientific reopen ledger invalid: {errors}")
    return row


def proposal_by_sha(row: dict, proposal_sha: str) -> dict:
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("scientific_reopen_proposal_sha256") == proposal_sha:
            if not validate_scientific_reopen_proposal(receipt):
                raise RuntimeError("scientific reopen proposal invalid")
            return receipt
    raise RuntimeError("scientific reopen proposal SHA not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record an external PI/human authorization to create a new scientific contract. This command does not create the contract and grants no experiment/GPU/claim-expansion authority.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--proposal-sha256", required=True)
    parser.add_argument("--external-scientific-authority-ref", required=True)
    parser.add_argument("--authorized-at", required=True)
    args = parser.parse_args()

    row = load_ledger(args.root, args.paper_id)
    proposal = proposal_by_sha(row, args.proposal_sha256)
    authorization = build_scientific_reopen_authorization(
        proposal=proposal,
        external_scientific_authority_ref=args.external_scientific_authority_ref,
        authorized_at=args.authorized_at,
    )
    row = publish_scientific_reopen_receipt(args.root, authorization)
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(errors)
    summary = public_scientific_reopen_summary(row, proposal["attempt_sha256"])
    print(json.dumps({
        "status": "PASS_EXTERNAL_SCIENTIFIC_REOPEN_AUTHORIZATION_RECORDED",
        "paper_id": args.paper_id,
        "attempt_id": proposal["attempt_id"],
        "attempt_sha256": proposal["attempt_sha256"],
        "scientific_reopen_status": summary["status"],
        "proposal_sha256": summary["proposal_sha256"],
        "authorization_sha256": summary["authorization_sha256"],
        "authorization_scope": summary["authorization_scope"],
        "external_scientific_authority_confirmed": True,
        "new_scientific_contract_required": True,
        "existing_scientific_contract_immutable": True,
        "automatic_contract_creation_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "gpu_execution_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
