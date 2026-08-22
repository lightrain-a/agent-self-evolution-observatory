#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.human_submission_signoff import (
    append_signoff,
    build_signoff_receipt,
    build_signoff_template,
    validate_signoff_ledger,
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Record an explicit human author confirmation bound to the current machine handoff. This does not submit the paper.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--handoff-sha256")
    parser.add_argument("--confirm", action="append", default=[], help="Required confirmation ID; repeat for every item in the template.")
    parser.add_argument("--external-human-confirmation-ref")
    parser.add_argument("--confirmed-at", help="Human-provided ISO-8601 confirmation time.")
    parser.add_argument("--acknowledge-current-artifact-hashes", action="store_true")
    parser.add_argument("--acknowledge-actual-submission-not-performed", action="store_true")
    parser.add_argument("--show-template", action="store_true")
    args = parser.parse_args()

    handoff_path = args.root / "paper-submission-handoffs" / f"{args.paper_id}.json"
    freeze_path = args.root / "paper-submission-freezes" / f"{args.paper_id}.json"
    if not handoff_path.exists() or not freeze_path.exists():
        parser.error("current machine handoff and freeze ledgers are both required")
    handoff_ledger = load(handoff_path)
    freeze_ledger = load(freeze_path)
    template = build_signoff_template(handoff_ledger)
    if args.show_template:
        print(json.dumps(template, ensure_ascii=False, indent=2))
        return
    if not args.handoff_sha256 or not args.external_human_confirmation_ref or not args.confirmed_at:
        parser.error("recording signoff requires --handoff-sha256, --external-human-confirmation-ref, and --confirmed-at")
    if str(template.get("handoff_sha256") or "") != args.handoff_sha256:
        parser.error("provided handoff SHA256 does not match the current handoff; refresh the handoff before confirming")
    receipt = build_signoff_receipt(
        handoff_ledger=handoff_ledger,
        freeze_ledger=freeze_ledger,
        confirmed_check_ids=args.confirm,
        external_human_confirmation_ref=args.external_human_confirmation_ref,
        confirmed_at=args.confirmed_at,
        acknowledge_current_artifact_hashes=args.acknowledge_current_artifact_hashes,
        acknowledge_actual_submission_not_performed=args.acknowledge_actual_submission_not_performed,
    )
    row = append_signoff(args.root, receipt)
    errors = validate_signoff_ledger(row)
    if errors:
        raise RuntimeError(errors)
    print(json.dumps({
        "status": receipt["status"],
        "paper_id": args.paper_id,
        "signoff_sha256": receipt["signoff_sha256"],
        "handoff_sha256": receipt["handoff_sha256"],
        "actual_submission_status": receipt["actual_submission_status"],
        "submission_authority": False,
        "ledger_events": len(row.get("events") or []),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
