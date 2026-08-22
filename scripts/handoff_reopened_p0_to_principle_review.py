#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_p0_principle_handoff import (
    build_p0_principle_handoff,
    public_p0_principle_handoff,
    publish_p0_principle_handoff,
    validate_p0_principle_handoff_ledger,
)
from research_pipeline.reopened_p0_result_adjudication import validate_p0_adjudication


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_adjudication(root: Path, contract_id: str) -> dict:
    row = load(root / "scientific-contract-p0-results" / f"{contract_id}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_p0_adjudication(receipt):
            return receipt
    raise RuntimeError("valid independent P0 adjudication not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile an independently adjudicated confirmatory P0 result into a principle-review handoff. This never updates persistent principle memory automatically.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--principle-certificate", type=Path, required=True)
    parser.add_argument("--principle-evidence", type=Path)
    parser.add_argument("--recorded-at", required=True)
    args = parser.parse_args()
    receipt = build_p0_principle_handoff(
        p0_adjudication=latest_adjudication(args.root, args.contract_id),
        principle_certificate=load(args.principle_certificate),
        principle_evidence=load(args.principle_evidence) if args.principle_evidence else {},
    )
    ledger = publish_p0_principle_handoff(args.root, receipt, recorded_at=args.recorded_at)
    errors = validate_p0_principle_handoff_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_p0_principle_handoff(args.root, args.contract_id)
    print(json.dumps({
        "status": "PASS_P0_PRINCIPLE_HANDOFF_RECORDED",
        "contract_id": args.contract_id,
        "principle_handoff_sha256": receipt["principle_handoff_sha256"],
        "principle_status": receipt["status"],
        "underlying_verdict": receipt["underlying_verdict"],
        "registered_prediction_rejected": receipt["registered_prediction_rejected"],
        "dead_end_candidate": receipt["dead_end_candidate"],
        "external_human_principle_review_required": receipt["external_human_principle_review_required"],
        "automatic_principle_update_authorized": False,
        "persistent_dead_end_memory_write_authorized": False,
        "claim_update_authorized": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
