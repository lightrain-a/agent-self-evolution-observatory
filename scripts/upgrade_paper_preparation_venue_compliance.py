#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.paper_acceptance_ledger import record_frozen_contract_paper_preparation, validate_paper_ledger
from research_pipeline.paper_anonymity_audit import SCHEMA_VERSION as ANONYMITY_VERSION, validate_anonymity_audit_receipt
from research_pipeline.paper_preparation_protocol import build_paper_preparation_receipt, evaluate_paper_preparation
from research_pipeline.paper_venue_compliance_projection import validate_projection_receipt


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def latest_preparation_receipt(ledger: dict) -> dict:
    for event in reversed(ledger.get("events") or []):
        if isinstance(event, dict) and event.get("event_type") == "paper-preparation" and isinstance(event.get("receipt"), dict):
            return event["receipt"]
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebind a current Paper Preparation packet to a venue-compliance source projection and a fresh PASS Double-Blind Leakage Audit. This appends preparation only; paper state and all scientific/experiment/GPU/submission authority remain unchanged.")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--base-packet", type=Path, required=True)
    parser.add_argument("--anonymity-audit", type=Path, required=True)
    parser.add_argument("--venue-compliance-projection", type=Path, required=True)
    parser.add_argument("--output-packet", type=Path, required=True)
    parser.add_argument("--actor", default="venue-compliance-preparation-upgrade")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    ledger_path = args.data_root / "paper-acceptance" / f"{args.paper_id}.json"
    ledger = load(ledger_path)
    before_state = str(ledger.get("current_state") or "")
    before_contract = str(ledger.get("contract_sha256") or "")
    errors = validate_paper_ledger(ledger)
    if errors:
        raise RuntimeError(f"canonical paper ledger invalid before venue-compliance upgrade: {errors}")
    if str(ledger.get("paper_id") or "") != args.paper_id:
        raise RuntimeError("paper id mismatch")

    audit = load(args.anonymity_audit)
    if not validate_anonymity_audit_receipt(audit) or audit.get("pass") is not True:
        raise RuntimeError("fresh Double-Blind Leakage Audit must be a valid PASS receipt")
    projection = load(args.venue_compliance_projection)
    if not validate_projection_receipt(projection):
        raise RuntimeError("invalid venue-compliance source projection receipt")
    if str(projection.get("paper_id") or "") != args.paper_id:
        raise RuntimeError("venue-compliance projection paper id mismatch")

    base = load(args.base_packet)
    base_sha = digest(base)
    latest = latest_preparation_receipt(ledger)
    current_packet_sha = str(latest.get("packet_sha256") or "")
    if current_packet_sha != base_sha:
        raise RuntimeError(f"base preparation packet is stale: canonical={current_packet_sha} supplied={base_sha}")

    upgraded = copy.deepcopy(base)
    gates = upgraded.get("gates")
    if not isinstance(gates, dict):
        raise RuntimeError("Paper Preparation gates missing")
    submission = gates.get("submission-package")
    if not isinstance(submission, dict):
        raise RuntimeError("submission-package gate missing")
    submission["anonymity_audit_version"] = ANONYMITY_VERSION
    submission["double_blind_audit_receipt"] = audit
    submission["anonymity_audit_sha256"] = str(audit.get("anonymity_audit_sha256") or "")
    prior = [str(item) for item in submission.get("venue_compliance_projection_sha256") or [] if str(item)]
    submission["venue_compliance_projection_sha256"] = list(dict.fromkeys([*prior, str(projection.get("projection_sha256") or "")]))
    submission["venue_compliance_projection_requires_refreeze"] = True
    submission["ai_use_statement_in_paper_verified"] = True
    submission["ai_use_statement_sha256"] = str(projection.get("statement_sha256") or "")
    submission["canonical_scientific_artifacts_unchanged"] = True
    gates["submission-package"] = submission
    upgraded["gates"] = gates

    evaluation = evaluate_paper_preparation(upgraded)
    if evaluation.get("pass") is not True:
        raise RuntimeError(f"venue-compliance Paper Preparation packet blocked: {evaluation.get('blockers')}")
    expected = build_paper_preparation_receipt(paper_id=args.paper_id, contract_sha256=before_contract, packet=upgraded)
    upgraded_sha = digest(upgraded)

    if args.validate_only:
        receipt = expected
        status = "PASS_VALIDATE_ONLY"
    else:
        args.output_packet.parent.mkdir(parents=True, exist_ok=True)
        args.output_packet.write_text(json.dumps(upgraded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated = record_frozen_contract_paper_preparation(args.data_root, args.paper_id, upgraded, actor=args.actor)
        after_errors = validate_paper_ledger(updated)
        if after_errors:
            raise RuntimeError(f"paper ledger invalid after venue-compliance upgrade: {after_errors}")
        if str(updated.get("current_state") or "") != before_state:
            raise RuntimeError("venue-compliance preparation upgrade must not change paper state")
        if str(updated.get("contract_sha256") or "") != before_contract:
            raise RuntimeError("venue-compliance preparation upgrade must not change frozen contract")
        receipt = latest_preparation_receipt(updated)
        if str(receipt.get("packet_sha256") or "") != upgraded_sha:
            raise RuntimeError("recorded Paper Preparation packet SHA mismatch")
        status = "PASS_VENUE_COMPLIANCE_PREPARATION_UPGRADED"

    print(json.dumps({
        "status": status,
        "paper_id": args.paper_id,
        "paper_state": before_state,
        "contract_sha256": before_contract,
        "base_packet_sha256": base_sha,
        "upgraded_packet_sha256": upgraded_sha,
        "preparation_receipt_sha256": receipt.get("receipt_sha256"),
        "anonymity_audit_sha256": audit.get("anonymity_audit_sha256"),
        "venue_compliance_projection_sha256": projection.get("projection_sha256"),
        "ai_use_statement_sha256": projection.get("statement_sha256"),
        "canonical_scientific_artifacts_unchanged": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
