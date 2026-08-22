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
    build_p0_result_packet,
    public_p0_result,
    publish_p0_result_receipt,
    validate_p0_result_ledger,
)


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_plan(root: Path, contract_id: str) -> dict:
    row = load(root / "scientific-contract-p0-plans" / f"{contract_id}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_p0_plan(receipt):
            return receipt
    raise RuntimeError("valid frozen P0 plan not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a content-addressed confirmatory P0 result packet without assigning a method or principle verdict.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--result-packet", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    args = parser.parse_args()
    plan = latest_plan(args.root, args.contract_id)
    receipt = build_p0_result_packet(p0_plan=plan, packet=load(args.result_packet))
    ledger = publish_p0_result_receipt(args.root, receipt, recorded_at=args.recorded_at)
    errors = validate_p0_result_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_p0_result(args.root, args.contract_id)
    print(json.dumps({
        "status": "PASS_P0_RESULT_PACKET_RECORDED_AWAIT_INDEPENDENT_ADJUDICATION",
        "contract_id": args.contract_id,
        "p0_result_packet_sha256": receipt["p0_result_packet_sha256"],
        "typed_execution_outcome": receipt["typed_execution_outcome"],
        "method_verdict_authorized": False,
        "principle_update_allowed": False,
        "claim_update_authorized": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
