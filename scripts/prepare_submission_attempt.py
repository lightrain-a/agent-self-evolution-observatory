#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.presubmission_freeze import artifact
from research_pipeline.submission_attempt_lineage import validate_attempt_ledger
from research_pipeline.submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    build_attempt_freeze,
    build_attempt_handoff,
    build_attempt_preparation,
    current_attempt_workflow_summary,
    validate_attempt_workflow_ledger,
)


def load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def find_attempt(root: Path, paper_id: str, attempt_sha: str) -> dict:
    path = root / "paper-submission-attempts" / f"{paper_id}.json"
    row = load(path)
    errors = validate_attempt_ledger(row)
    if errors:
        raise RuntimeError(f"attempt ledger invalid: {errors}")
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and receipt.get("attempt_sha256") == attempt_sha:
            return receipt
    raise RuntimeError("attempt SHA not found")


def parse_artifact(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("artifact must be LABEL=/absolute/or/relative/path")
    label, raw = value.split("=", 1)
    if not label.strip() or not raw.strip():
        raise argparse.ArgumentTypeError("artifact label/path must be non-empty")
    return label.strip(), Path(raw).expanduser()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run attempt-scoped Preparation → Freeze → Machine Handoff for a paper-side child attempt. This command does not perform human signoff or venue submission.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--attempt-sha256", required=True)
    parser.add_argument("--preparation-packet", type=Path, required=True)
    parser.add_argument("--venue-policy", type=Path, required=True)
    parser.add_argument("--artifact", action="append", type=parse_artifact, required=True, help="Repeat as LABEL=PATH; e.g. paper_pdf=/tmp/main.pdf")
    args = parser.parse_args()

    plan = find_attempt(args.root, args.paper_id, args.attempt_sha256)
    packet = load(args.preparation_packet)
    venue_policy = load(args.venue_policy)
    specs = [artifact(label, path.resolve()) for label, path in args.artifact]

    preparation = build_attempt_preparation(attempt_plan=plan, preparation_packet=packet)
    freeze = build_attempt_freeze(attempt_plan=plan, preparation_receipt=preparation, artifacts=specs, venue_policy=venue_policy)
    handoff = build_attempt_handoff(attempt_plan=plan, preparation_receipt=preparation, freeze_receipt=freeze, venue_policy=venue_policy)
    row = append_attempt_workflow_receipt(args.root, preparation)
    row = append_attempt_workflow_receipt(args.root, freeze)
    row = append_attempt_workflow_receipt(args.root, handoff)
    errors = validate_attempt_workflow_ledger(row)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    summary = current_attempt_workflow_summary(row)
    print(json.dumps({
        "status": "PASS_ATTEMPT_MACHINE_HANDOFF_READY",
        "paper_id": args.paper_id,
        "attempt_id": plan["attempt_id"],
        "attempt_sha256": plan["attempt_sha256"],
        "attempt_preparation_sha256": preparation["attempt_preparation_sha256"],
        "attempt_freeze_sha256": freeze["attempt_freeze_sha256"],
        "attempt_handoff_sha256": handoff["attempt_handoff_sha256"],
        "workflow_status": summary["status"],
        "frozen_artifacts": summary["frozen_artifacts"],
        "human_confirmation_status": summary["human_confirmation_status"],
        "parent_submission_bytes_immutable": True,
        "actual_submission_performed": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
