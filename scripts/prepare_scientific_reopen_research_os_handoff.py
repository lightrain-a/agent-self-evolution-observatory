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
    HANDOFF_DESTINATION,
    build_research_os_scientific_reopen_handoff,
    public_scientific_reopen_summary,
    publish_scientific_reopen_receipt,
    validate_research_os_scientific_reopen_handoff,
    validate_scientific_reopen_authorization,
    validate_scientific_reopen_ledger,
    validate_scientific_reopen_proposal,
)
from research_pipeline.submission_attempt_lineage import validate_attempt_ledger, validate_attempt_plan


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "unknown-paper"


def load_json(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def find_attempt(root: Path, paper_id: str, attempt_sha: str) -> dict:
    row = load_json(root / "paper-submission-attempts" / f"{slug(paper_id)}.json")
    errors = validate_attempt_ledger(row)
    if errors:
        raise RuntimeError(f"submission-attempt ledger invalid: {errors}")
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("attempt_sha256") == attempt_sha:
            if not validate_attempt_plan(receipt):
                raise RuntimeError("submission attempt plan invalid")
            return receipt
    raise RuntimeError("attempt SHA not found")


def find_reopen_receipts(root: Path, paper_id: str, authorization_sha: str) -> tuple[dict, dict, dict]:
    row = load_json(root / "paper-scientific-reopen" / f"{slug(paper_id)}.json")
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(f"scientific reopen ledger invalid: {errors}")
    authorization = {}
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("scientific_reopen_authorization_sha256") == authorization_sha:
            authorization = receipt
            break
    if not authorization or not validate_scientific_reopen_authorization(authorization):
        raise RuntimeError("scientific reopen authorization SHA not found or invalid")
    proposal_sha = str(authorization.get("scientific_reopen_proposal_sha256") or "")
    proposal = {}
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("scientific_reopen_proposal_sha256") == proposal_sha:
            proposal = receipt
            break
    if not proposal or not validate_scientific_reopen_proposal(proposal):
        raise RuntimeError("bound scientific reopen proposal missing or invalid")
    return row, proposal, authorization


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a zero-execution-authority handoff from an approved paper scientific reopen into the Research OS scientific-contract creation gate. This does not create the new contract or authorize method/P0/experiment/GPU work.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--attempt-sha256", required=True)
    parser.add_argument("--authorization-sha256", required=True)
    args = parser.parse_args()

    paper = load_json(args.root / "paper-acceptance" / f"{args.paper_id}.json")
    attempt = find_attempt(args.root, args.paper_id, args.attempt_sha256)
    _, proposal, authorization = find_reopen_receipts(args.root, args.paper_id, args.authorization_sha256)
    handoff = build_research_os_scientific_reopen_handoff(
        paper_ledger=paper,
        attempt_plan=attempt,
        proposal=proposal,
        authorization=authorization,
    )
    if not validate_research_os_scientific_reopen_handoff(handoff):
        raise RuntimeError("Research OS scientific reopen handoff failed validation")
    row = publish_scientific_reopen_receipt(args.root, handoff)
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(errors)
    summary = public_scientific_reopen_summary(row, args.attempt_sha256)
    print(json.dumps({
        "status": "PASS_RESEARCH_OS_NEW_CONTRACT_HANDOFF_RECORDED",
        "paper_id": args.paper_id,
        "attempt_id": attempt["attempt_id"],
        "attempt_sha256": attempt["attempt_sha256"],
        "scientific_reopen_status": summary["status"],
        "research_os_handoff_sha256": summary["research_os_handoff_sha256"],
        "new_contract_seed_id": summary["new_contract_seed_id"],
        "destination_gate": HANDOFF_DESTINATION,
        "new_contract_creation_eligible": True,
        "new_scientific_contract_required": True,
        "existing_scientific_contract_immutable": True,
        "automatic_contract_creation_authorized": False,
        "problem_gate_authorized": False,
        "method_design_authorized": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
