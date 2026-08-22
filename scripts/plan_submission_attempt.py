#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.submission_attempt_lineage import (
    ATTEMPT_TYPES,
    REVISION_CATEGORIES,
    build_attempt_plan,
    publish_attempt_plan,
    validate_attempt_ledger,
    validate_attempt_plan,
)
from research_pipeline.submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_workflow_ledger


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def _parent_attempt(root: Path, paper_id: str, attempt_sha: str) -> dict | None:
    if not attempt_sha:
        return None
    path = root / "paper-submission-attempts" / f"{paper_id}.json"
    if not path.exists():
        raise RuntimeError("parent attempt ledger does not exist")
    row = _load(path)
    errors = validate_attempt_ledger(row)
    if errors:
        raise RuntimeError(f"parent attempt ledger invalid: {errors}")
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("attempt_sha256") == attempt_sha:
            return receipt
    raise RuntimeError("requested parent attempt SHA not found")


def _completed_parent_attempt_workflow(root: Path, parent: dict | None) -> dict | None:
    if not parent:
        return None
    attempt_id = str(parent.get("attempt_id") or "")
    if not attempt_id:
        return None
    path = root / "paper-submission-attempt-workflows" / f"{attempt_id}.json"
    if not path.exists():
        return None
    row = _load(path)
    errors = validate_attempt_workflow_ledger(row)
    if errors:
        raise RuntimeError(f"parent attempt workflow invalid: {errors}")
    return row if current_attempt_workflow_summary(row).get("status") == "ATTEMPT_POST_DECISION_LEARN_COMPLETE" else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan a resubmission or camera-ready child attempt without mutating the parent submission. The command never authorizes scientific changes or experiments."
    )
    parser.add_argument("--root", type=Path, required=True, help="Research OS root containing paper-acceptance and paper-submission-attempts.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--attempt-type", required=True, choices=sorted(ATTEMPT_TYPES))
    parser.add_argument("--target-venue", required=True)
    parser.add_argument("--revision-category", action="append", dest="revision_categories", choices=sorted(REVISION_CATEGORIES), required=True)
    parser.add_argument("--scientific-contract-unchanged", action="store_true", help="Explicitly affirm that the frozen scientific contract is unchanged. Omit this flag to force REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN.")
    parser.add_argument("--new-claim-requested", action="store_true")
    parser.add_argument("--new-experiment-requested", action="store_true")
    parser.add_argument("--new-scientific-evidence-requested", action="store_true")
    parser.add_argument("--scientific-interpretation-change-requested", action="store_true")
    parser.add_argument("--parent-attempt-sha256", default="")
    parser.add_argument("--validate-only", action="store_true", help="Build and validate the plan without appending it to the attempt ledger.")
    args = parser.parse_args()

    paper_path = args.root / "paper-acceptance" / f"{args.paper_id}.json"
    paper_ledger = _load(paper_path)
    parent = _parent_attempt(args.root, args.paper_id, args.parent_attempt_sha256)
    parent_workflow = _completed_parent_attempt_workflow(args.root, parent)
    receipt = build_attempt_plan(
        paper_ledger=paper_ledger,
        target_venue=args.target_venue,
        attempt_type=args.attempt_type,
        revision_categories=args.revision_categories,
        scientific_contract_unchanged=args.scientific_contract_unchanged,
        new_claim_requested=args.new_claim_requested,
        new_experiment_requested=args.new_experiment_requested,
        new_scientific_evidence_requested=args.new_scientific_evidence_requested,
        scientific_interpretation_change_requested=args.scientific_interpretation_change_requested,
        parent_attempt=parent,
        parent_attempt_workflow=parent_workflow,
    )
    if not validate_attempt_plan(receipt):
        raise RuntimeError("submission attempt plan failed validation")

    events = 0
    if not args.validate_only:
        row = publish_attempt_plan(receipt, args.root)
        errors = validate_attempt_ledger(row)
        if errors:
            raise RuntimeError(f"submission attempt ledger failed validation: {errors}")
        events = len(row.get("events") or [])

    print(json.dumps({
        "status": "PASS_VALIDATE_ONLY" if args.validate_only else "PASS_ATTEMPT_PLAN_RECORDED",
        "paper_id": args.paper_id,
        "attempt_id": receipt["attempt_id"],
        "attempt_sha256": receipt["attempt_sha256"],
        "attempt_type": receipt["attempt_type"],
        "target_venue": receipt["target_venue"],
        "plan_status": receipt["status"],
        "machine_preparation_eligible": receipt["machine_preparation_eligible"],
        "requires_explicit_scientific_reopen": receipt["requires_explicit_scientific_reopen"],
        "parent_submission_bytes_immutable": receipt["parent_submission_bytes_immutable"],
        "parent_attempt_outcome_bound": parent_workflow is not None,
        "attempt_ledger_events": events,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
