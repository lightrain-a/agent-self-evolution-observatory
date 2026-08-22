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
    record_frozen_contract_rebuttal_preparation,
    validate_paper_ledger,
)
from research_pipeline.rebuttal_protocol import build_rebuttal_preparation, validate_rebuttal_receipt


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return value


def latest_review_set(row: dict) -> dict:
    for event in reversed(row.get("events") or []):
        if isinstance(event, dict) and event.get("event_type") == "review-set":
            value = event.get("review_set") or {}
            return value if isinstance(value, dict) else {}
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and record a rebuttal response against the current frozen claim/evidence contract. This command never authorizes a new experiment or claim expansion.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--plan", type=Path, required=True, help="JSON object with objections, resolutions, response_text, and response_limit_words.")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    paper_path = args.root / "paper-acceptance" / f"{args.paper_id}.json"
    review_path = args.root / "paper-review-intake" / f"{args.paper_id}.json"
    if not paper_path.exists() or not review_path.exists():
        parser.error("canonical paper ledger and review-intake ledger are both required")
    paper = load(paper_path)
    review_ledger = load(review_path)
    review_set = latest_review_set(review_ledger)
    plan = load(args.plan)
    if not isinstance(plan, dict):
        parser.error("rebuttal plan must be a JSON object")

    receipt = build_rebuttal_preparation(
        paper_ledger=paper,
        review_set=review_set,
        objections=plan.get("objections") or [],
        resolutions=plan.get("resolutions") or [],
        response_text=str(plan.get("response_text") or ""),
        response_limit_words=int(plan.get("response_limit_words") or 0),
    )
    if not validate_rebuttal_receipt(receipt):
        raise RuntimeError("rebuttal receipt failed content-addressed validation")
    summary = {
        "status": "PASS" if receipt.get("pass") is True else "BLOCKED",
        "paper_id": args.paper_id,
        "review_set_sha256": receipt.get("review_set_sha256"),
        "rebuttal_receipt_sha256": receipt.get("rebuttal_receipt_sha256"),
        "response_words": receipt.get("response_words"),
        "response_limit_words": receipt.get("response_limit_words"),
        "blockers": receipt.get("blockers") or [],
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
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

    row = record_frozen_contract_rebuttal_preparation(args.root, args.paper_id, receipt)
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError(f"paper ledger invalid after rebuttal preparation: {errors}")
    result = advance_frozen_paper_to_rebuttal(args.root, args.paper_id)
    if result["receipt"].get("allowed") is not True:
        raise RuntimeError(f"REBUTTAL transition blocked: {result['receipt'].get('blockers')}")
    summary.update({
        "status": "REBUTTAL",
        "current_state": result["ledger"]["current_state"],
        "ledger_validation_errors": validate_paper_ledger(result["ledger"]),
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
