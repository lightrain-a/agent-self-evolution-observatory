#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_p0_plan import validate_p0_plan
from research_pipeline.reopened_p0_result_adjudication import (
    build_p0_adjudication,
    public_p0_result,
    publish_p0_result_receipt,
    validate_p0_result_ledger,
    validate_p0_result_packet,
)


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest(root: Path, directory: str, contract_id: str, validator) -> dict:
    row = load(root / directory / f"{contract_id}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validator(receipt):
            return receipt
    raise RuntimeError(f"valid receipt not found: {directory}/{contract_id}.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Independently adjudicate a frozen confirmatory P0 result packet. METHOD-FAIL is scoped to the current method realization and never directly falsifies the principle.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--adjudication-packet", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    args = parser.parse_args()
    plan = latest(args.root, "scientific-contract-p0-plans", args.contract_id, validate_p0_plan)
    result = latest(args.root, "scientific-contract-p0-results", args.contract_id, validate_p0_result_packet)
    receipt = build_p0_adjudication(p0_plan=plan, result_packet=result, packet=load(args.adjudication_packet))
    ledger = publish_p0_result_receipt(args.root, receipt, recorded_at=args.recorded_at)
    errors = validate_p0_result_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_p0_result(args.root, args.contract_id)
    print(json.dumps({
        "status": "PASS_CONFIRMATORY_P0_RESULT_ADJUDICATED",
        "contract_id": args.contract_id,
        "p0_adjudication_sha256": receipt["p0_adjudication_sha256"],
        "p0_status": receipt["status"],
        "method_verdict": receipt["method_verdict"],
        "method_verdict_authorized": receipt["method_verdict_authorized"],
        "failure_layer": receipt["failure_layer"],
        "principle_update_allowed": False,
        "claim_update_authorized": False,
        "parent_paper_claim_status_unchanged": True,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
