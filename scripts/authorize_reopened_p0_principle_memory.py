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
    build_principle_memory_authorization,
    public_principle_memory_state,
    publish_principle_memory_receipt,
    validate_principle_memory_ledger,
)


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_handoff(root: Path, contract_id: str) -> dict:
    row = load(root / "scientific-contract-p0-principle-handoffs" / f"{contract_id}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_p0_principle_handoff(receipt):
            return receipt
    raise RuntimeError("valid P0 principle handoff not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record explicit human authority to create a scoped principle-dead-end Research Memory handoff. This does not write Research Memory automatically.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--external-authority-ref", required=True)
    parser.add_argument("--authorized-at", required=True)
    args = parser.parse_args()
    receipt = build_principle_memory_authorization(
        principle_handoff=latest_handoff(args.root, args.contract_id),
        external_authority_ref=args.external_authority_ref,
        authorized_at=args.authorized_at,
    )
    ledger = publish_principle_memory_receipt(args.root, receipt, recorded_at=args.authorized_at)
    errors = validate_principle_memory_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_principle_memory_state(args.root, args.contract_id)
    print(json.dumps({
        "status": "PASS_P0_PRINCIPLE_MEMORY_AUTHORIZATION_RECORDED",
        "contract_id": args.contract_id,
        "authorization_sha256": receipt["principle_memory_authorization_sha256"],
        "principle_id": receipt["principle_id"],
        "principle_memory_update_authorized": True,
        "automatic_memory_write_authorized": False,
        "persistent_memory_write_completed": False,
        "claim_update_authorized": False,
        "public_status": public["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
