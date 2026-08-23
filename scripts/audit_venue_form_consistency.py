#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.venue_form_consistency import (
    append_venue_form_audit,
    build_form_contract_template,
    build_venue_form_audit_receipt,
    validate_venue_form_audit_ledger,
)

DEFAULT_POLICY = PROJECT_ROOT / "generated" / "venue-policy-iclr2027-current.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit the final OpenReview form snapshot against the current frozen paper/source/handoff. "
            "This is a read-only validation unless --record is supplied, and it never grants submission authority."
        )
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--venue-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--show-contract-template", action="store_true")
    parser.add_argument("--form-contract", type=Path)
    parser.add_argument("--form-snapshot", type=Path)
    parser.add_argument("--record", action="store_true", help="Append the resulting PASS/FAIL receipt to paper-venue-form-audits.")
    args = parser.parse_args()

    paper = load(args.root / "paper-acceptance" / f"{args.paper_id}.json")
    freeze = load(args.root / "paper-submission-freezes" / f"{args.paper_id}.json")
    handoff = load(args.root / "paper-submission-handoffs" / f"{args.paper_id}.json")
    policy = load(args.venue_policy)
    template = build_form_contract_template(
        paper_ledger=paper,
        freeze_ledger=freeze,
        handoff_ledger=handoff,
        venue_policy=policy,
    )
    if args.show_contract_template:
        print(json.dumps(template, ensure_ascii=False, indent=2))
        return
    if args.form_contract is None or args.form_snapshot is None:
        parser.error("auditing requires --form-contract and --form-snapshot, or use --show-contract-template")
    contract = load(args.form_contract)
    snapshot = load(args.form_snapshot)

    machine_fields = template["expected_fields"]
    supplied_fields = contract.get("expected_fields") if isinstance(contract.get("expected_fields"), dict) else {}
    immutable_keys = ("title", "abstract", "author_visibility", "supplement_declared", "supplement_artifacts")
    for key in immutable_keys:
        if supplied_fields.get(key) != machine_fields.get(key):
            parser.error(f"form contract changes machine-derived frozen field {key}; regenerate from the current template")
    if contract.get("binding") != template.get("binding") or contract.get("paper_id") != template.get("paper_id") or contract.get("venue") != template.get("venue"):
        parser.error("form contract binding is stale relative to the current freeze/handoff/venue policy")
    if contract.get("source_evidence") != template.get("source_evidence"):
        parser.error("form contract source evidence is stale relative to the current frozen source")

    receipt = build_venue_form_audit_receipt(form_contract=contract, form_snapshot=snapshot)
    result = {
        "status": receipt["status"],
        "paper_id": receipt["paper_id"],
        "pass": receipt["pass"],
        "blockers": receipt["blockers"],
        "field_results": receipt["field_results"],
        "venue_form_audit_sha256": receipt["venue_form_audit_sha256"],
        "freeze_sha256": receipt["freeze_sha256"],
        "handoff_sha256": receipt["handoff_sha256"],
        "recorded": False,
        "submission_authority": False,
    }
    if args.record:
        row = append_venue_form_audit(args.root, receipt)
        errors = validate_venue_form_audit_ledger(row)
        if errors:
            raise RuntimeError(errors)
        result["recorded"] = True
        result["ledger_events"] = len(row.get("events") or [])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
