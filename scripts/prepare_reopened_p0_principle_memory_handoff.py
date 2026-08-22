#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_p0_principle_handoff import validate_p0_principle_handoff
from research_pipeline.reopened_p0_principle_memory_authorization import (
    build_principle_memory_handoff,
    public_principle_memory_state,
    publish_principle_memory_receipt,
    validate_principle_memory_authorization,
    validate_principle_memory_ledger,
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
    parser = argparse.ArgumentParser(description="Prepare a scoped Research Memory principle-dead-end handoff after explicit human authorization. This does not persist the memory entry automatically.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--memory-spec", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    args = parser.parse_args()
    handoff = latest(args.root, "scientific-contract-p0-principle-handoffs", args.contract_id, validate_p0_principle_handoff)
    authorization = latest(args.root, "scientific-contract-p0-principle-memory", args.contract_id, validate_principle_memory_authorization)
    receipt = build_principle_memory_handoff(
        principle_handoff=handoff,
        authorization=authorization,
        memory_spec=load(args.memory_spec),
    )
    ledger = publish_principle_memory_receipt(args.root, receipt, recorded_at=args.recorded_at)
    errors = validate_principle_memory_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_principle_memory_state(args.root, args.contract_id)
    print(json.dumps({
        "status": "PASS_RESEARCH_MEMORY_PRINCIPLE_DEAD_END_HANDOFF_RECORDED",
        "contract_id": args.contract_id,
        "memory_handoff_sha256": receipt["principle_memory_handoff_sha256"],
        "principle_id": receipt["principle_id"],
        "destination_gate": receipt["destination_gate"],
        "principle_update_allowed": True,
        "automatic_memory_write_authorized": False,
        "persistent_memory_write_completed": False,
        "claim_update_authorized": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
