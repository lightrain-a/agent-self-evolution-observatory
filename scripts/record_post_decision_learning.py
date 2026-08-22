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
    advance_frozen_paper_to_learn,
    record_frozen_contract_post_decision_learning,
    validate_paper_ledger,
)
from research_pipeline.post_decision_learning import build_learning_packet, validate_learning_receipt, validate_venue_decision_receipt


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def latest_decision(row: dict) -> dict:
    for event in reversed(row.get("events") or []):
        if isinstance(event, dict) and event.get("event_type") == "venue-decision":
            receipt = event.get("receipt") or {}
            return receipt if isinstance(receipt, dict) else {}
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Record scoped post-decision learning and advance REBUTTAL → LEARN. Venue acceptance/rejection never changes scientific claim truth or authorizes experiments.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--lessons", type=Path, required=True, help="JSON array or {lessons:[...]} of scoped learning lessons.")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    paper_path = args.root / "paper-acceptance" / f"{args.paper_id}.json"
    if not paper_path.exists():
        parser.error("canonical paper ledger not found")
    paper = load(paper_path)
    decision = latest_decision(paper)
    if not decision or not validate_venue_decision_receipt(decision):
        parser.error("current valid venue final-decision receipt is required")
    payload = json.loads(args.lessons.read_text(encoding="utf-8"))
    lessons = payload.get("lessons") if isinstance(payload, dict) else payload
    if not isinstance(lessons, list):
        parser.error("lessons input must be a JSON array or an object with a lessons array")

    receipt = build_learning_packet(paper_ledger=paper, venue_decision=decision, lessons=lessons)
    if not validate_learning_receipt(receipt):
        raise RuntimeError("learning receipt failed content-addressed validation")
    summary = {
        "status": "PASS" if receipt.get("pass") is True else "BLOCKED",
        "paper_id": args.paper_id,
        "decision": receipt.get("decision"),
        "venue_decision_sha256": receipt.get("venue_decision_sha256"),
        "learning_receipt_sha256": receipt.get("learning_receipt_sha256"),
        "lessons": (receipt.get("summary") or {}).get("lessons", 0),
        "scientific_diagnostic_only": (receipt.get("summary") or {}).get("scientific_diagnostic_only", 0),
        "blockers": receipt.get("blockers") or [],
        "scientific_claim_status_unchanged": True,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "automatic_reopen_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    if args.validate_only or receipt.get("pass") is not True:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if receipt.get("pass") is not True:
            raise SystemExit(2)
        return

    row = record_frozen_contract_post_decision_learning(args.root, args.paper_id, receipt)
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError(f"paper ledger invalid after learning receipt: {errors}")
    result = advance_frozen_paper_to_learn(args.root, args.paper_id)
    if result["receipt"].get("allowed") is not True:
        raise RuntimeError(f"LEARN transition blocked: {result['receipt'].get('blockers')}")
    summary.update({
        "status": "LEARN",
        "current_state": result["ledger"]["current_state"],
        "ledger_validation_errors": validate_paper_ledger(result["ledger"]),
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
