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
    advance_frozen_paper_to_rebuttal,
    record_frozen_contract_rebuttal_skipped_by_venue,
    record_frozen_contract_venue_decision,
    validate_paper_ledger,
)
from research_pipeline.post_decision_learning import (
    FINAL_DECISIONS,
    build_rebuttal_skipped_by_venue_receipt,
    build_venue_decision_receipt,
    validate_rebuttal_skipped_by_venue_receipt,
    validate_venue_decision_receipt,
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a real final venue decision. Use --pre-rebuttal-terminal when the venue provides no rebuttal window. The decision does not change scientific claim truth.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--decision", required=True, choices=sorted(FINAL_DECISIONS))
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--received-at", required=True)
    parser.add_argument("--decision-text", type=Path, required=True)
    parser.add_argument("--pre-rebuttal-terminal", action="store_true", help="Terminal decision received in SUBMITTED with no rebuttal window; records an explicit REBUTTAL_SKIPPED_BY_VENUE receipt and never fabricates reviews.")
    args = parser.parse_args()

    paper_path = args.root / "paper-acceptance" / f"{args.paper_id}.json"
    if not paper_path.exists():
        parser.error("canonical paper ledger not found")
    paper = load(paper_path)
    text = args.decision_text.read_text(encoding="utf-8")
    receipt = build_venue_decision_receipt(
        paper_ledger=paper,
        decision_id=args.decision_id,
        source_ref=args.source_ref,
        received_at=args.received_at,
        decision=args.decision,
        decision_text=text,
        decision_phase="PRE_REBUTTAL_TERMINAL" if args.pre_rebuttal_terminal else "POST_REBUTTAL",
        rebuttal_available=not args.pre_rebuttal_terminal,
    )
    if not validate_venue_decision_receipt(receipt):
        raise RuntimeError("venue decision receipt failed validation")
    row = record_frozen_contract_venue_decision(args.root, args.paper_id, receipt)
    skip_receipt = None
    if args.pre_rebuttal_terminal:
        skip_receipt = build_rebuttal_skipped_by_venue_receipt(paper_ledger=row, venue_decision=receipt)
        if not validate_rebuttal_skipped_by_venue_receipt(skip_receipt):
            raise RuntimeError("rebuttal-skipped-by-venue receipt failed validation")
        row = record_frozen_contract_rebuttal_skipped_by_venue(args.root, args.paper_id, skip_receipt)
        transition = advance_frozen_paper_to_rebuttal(args.root, args.paper_id, actor="venue-terminal-rebuttal-skip")
        if transition["receipt"].get("allowed") is not True:
            raise RuntimeError(f"venue-skip transition blocked: {transition['receipt'].get('blockers')}")
        row = transition["ledger"]
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError(f"paper ledger invalid after venue decision: {errors}")
    print(json.dumps({
        "status": "VENUE_DECISION_RECORDED",
        "paper_id": args.paper_id,
        "decision": receipt["decision"],
        "venue_decision_sha256": receipt["venue_decision_sha256"],
        "decision_phase": receipt["decision_phase"],
        "rebuttal_available": receipt["rebuttal_available"],
        "rebuttal_skip_sha256": str((skip_receipt or {}).get("rebuttal_skip_sha256") or ""),
        "paper_state_after_record": str(row.get("current_state") or ""),
        "scientific_claim_status_unchanged": True,
        "acceptance_does_not_prove_scientific_truth": True,
        "rejection_does_not_refute_scientific_claims": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
        "ledger_validation_errors": [],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
