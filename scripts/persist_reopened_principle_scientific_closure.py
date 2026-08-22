#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_p0_principle_memory_authorization import validate_principle_memory_handoff
from research_pipeline.reopened_principle_memory_closure import (
    build_principle_scientific_closure,
    public_principle_closure_summary,
    publish_principle_scientific_closure,
    validate_principle_closure_ledger,
)


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_memory_handoff(root: Path, contract_id: str) -> dict:
    row = load(root / "scientific-contract-p0-principle-memory" / f"{contract_id}.json")
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validate_principle_memory_handoff(receipt):
            return receipt
    raise RuntimeError("valid human-authorized principle-memory handoff not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist a human-authorized scoped principle dead end into the canonical principle-closure registry. This does not globally blacklist adjacent research objects or update parent paper claims.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--persisted-at", required=True)
    args = parser.parse_args()
    receipt = build_principle_scientific_closure(
        memory_handoff=latest_memory_handoff(args.root, args.contract_id),
        persisted_at=args.persisted_at,
    )
    ledger = publish_principle_scientific_closure(args.root, receipt)
    errors = validate_principle_closure_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_principle_closure_summary(args.root)
    print(json.dumps({
        "status": "PASS_SCOPED_PRINCIPLE_SCIENTIFIC_CLOSURE_PERSISTED",
        "contract_id": args.contract_id,
        "principle_id": receipt["principle_id"],
        "closure_id": receipt["closure_id"],
        "memory_id": receipt["memory_id"],
        "principle_closure_sha256": receipt["principle_closure_sha256"],
        "scope": receipt["scope"],
        "reopen_condition": receipt["counter_explanation"]["reopen_condition"],
        "automatic_global_blacklist_forbidden": True,
        "adjacent_scientific_objects_remain_open": True,
        "parent_paper_claim_update_authorized": False,
        "public_summary": public,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
