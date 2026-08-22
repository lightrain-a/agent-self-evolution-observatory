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
    build_scientific_reopen_proposal,
    public_scientific_reopen_summary,
    publish_scientific_reopen_receipt,
    validate_scientific_reopen_ledger,
    validate_scientific_reopen_proposal,
)
from research_pipeline.submission_attempt_lineage import validate_attempt_ledger, validate_attempt_plan


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "unknown-paper"


def load_attempt(root: Path, paper_id: str, attempt_sha: str, attempt_id: str) -> dict:
    path = root / "paper-submission-attempts" / f"{slug(paper_id)}.json"
    row = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_attempt_ledger(row)
    if errors:
        raise RuntimeError(f"submission-attempt ledger invalid: {errors}")
    receipts = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, dict) and isinstance(event.get("receipt"), dict)]
    if attempt_sha:
        receipts = [receipt for receipt in receipts if receipt.get("attempt_sha256") == attempt_sha]
    elif attempt_id:
        receipts = [receipt for receipt in receipts if receipt.get("attempt_id") == attempt_id]
    if not receipts:
        raise RuntimeError("requested submission attempt not found")
    receipt = receipts[-1]
    if not validate_attempt_plan(receipt):
        raise RuntimeError("submission attempt plan invalid")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a scientific-reopen proposal for a child attempt that requests scientific changes. This command grants no scientific, experiment, GPU, or submission authority.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--attempt-sha256", default="")
    parser.add_argument("--attempt-id", default="")
    args = parser.parse_args()

    attempt = load_attempt(args.root, args.paper_id, args.attempt_sha256, args.attempt_id)
    proposal = build_scientific_reopen_proposal(attempt)
    if not validate_scientific_reopen_proposal(proposal):
        raise RuntimeError("scientific reopen proposal failed validation")
    row = publish_scientific_reopen_receipt(args.root, proposal)
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(errors)
    summary = public_scientific_reopen_summary(row, attempt["attempt_sha256"])
    print(json.dumps({
        "status": "PASS_SCIENTIFIC_REOPEN_PROPOSAL_RECORDED",
        "paper_id": args.paper_id,
        "attempt_id": attempt["attempt_id"],
        "attempt_sha256": attempt["attempt_sha256"],
        "scientific_reopen_status": summary["status"],
        "proposal_sha256": summary["proposal_sha256"],
        "new_scientific_contract_required": True,
        "existing_scientific_contract_immutable": True,
        "automatic_contract_creation_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
