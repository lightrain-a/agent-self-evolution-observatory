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

from research_pipeline.reopened_scientific_contract import (
    build_reopened_scientific_contract,
    public_reopened_contract_summary,
    publish_reopened_scientific_contract,
    validate_reopened_scientific_contract,
)
from research_pipeline.scientific_reopen_protocol import (
    validate_research_os_scientific_reopen_handoff,
    validate_scientific_reopen_ledger,
)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown-paper"


def load_json(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def find_handoff(root: Path, paper_id: str, handoff_sha: str) -> dict:
    row = load_json(root / "paper-scientific-reopen" / f"{slug(paper_id)}.json")
    errors = validate_scientific_reopen_ledger(row)
    if errors:
        raise RuntimeError(f"scientific reopen ledger invalid: {errors}")
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("research_os_handoff_sha256") == handoff_sha:
            if not validate_research_os_scientific_reopen_handoff(receipt):
                raise RuntimeError("Research OS reopen handoff invalid")
            return receipt
    raise RuntimeError("Research OS reopen handoff SHA not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an immutable child scientific contract from an approved Research OS reopen handoff. The new contract starts at PROBLEM_GATE_REQUIRED and grants no downstream execution authority.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--handoff-sha256", required=True)
    parser.add_argument("--spec", type=Path, required=True, help="JSON object with the new scientific question, hypothesis, falsifier, scope, evidence plan, stop condition, and exact requested-delta mapping.")
    args = parser.parse_args()

    handoff = find_handoff(args.root, args.paper_id, args.handoff_sha256)
    spec = load_json(args.spec)
    contract = build_reopened_scientific_contract(handoff=handoff, spec=spec)
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("reopened scientific contract failed validation")
    contract = publish_reopened_scientific_contract(args.root, contract)
    public = public_reopened_contract_summary(contract)
    print(json.dumps({
        "status": "PASS_NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED",
        "paper_id": args.paper_id,
        "contract_id": public["contract_id"],
        "contract_sha256": public["contract_sha256"],
        "parent_contract_sha256": public["parent_contract_sha256"],
        "research_os_handoff_sha256": public["research_os_handoff_sha256"],
        "scientific_question": public["scientific_question"],
        "scientific_stage": public["scientific_stage"],
        "problem_gate_required": True,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_design_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_execution_authorized": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
