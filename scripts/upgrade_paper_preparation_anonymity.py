#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_acceptance_ledger import record_frozen_contract_paper_preparation, validate_paper_ledger
from research_pipeline.paper_anonymity_audit import SCHEMA_VERSION as ANON_VERSION, validate_anonymity_audit_receipt
from research_pipeline.paper_anonymized_submission_projection import validate_projection_receipt
from research_pipeline.paper_preparation_protocol import build_paper_preparation_receipt, evaluate_paper_preparation


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def latest_preparation_receipt(ledger: dict) -> dict:
    for event in reversed(ledger.get("events") or []):
        if event.get("event_type") == "paper-preparation" and isinstance(event.get("receipt"), dict):
            return event["receipt"]
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade a current Paper Preparation packet by binding a content-addressed Double-Blind Leakage Audit. Legacy packets remain replayable; this appends a new post-ready preparation event without changing paper state or authority.")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--base-packet", type=Path, required=True)
    parser.add_argument("--anonymity-audit", type=Path, required=True)
    parser.add_argument("--projection-receipt", action="append", type=Path, default=[])
    parser.add_argument("--output-packet", type=Path, required=True)
    parser.add_argument("--actor", default="double-blind-preparation-upgrade")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    ledger_root = args.data_root / "paper-acceptance"
    ledger_path = ledger_root / f"{args.paper_id}.json"
    ledger = load(ledger_path)
    errors = validate_paper_ledger(ledger)
    if errors: raise RuntimeError(f"canonical paper ledger invalid before anonymity upgrade: {errors}")
    if str(ledger.get("paper_id") or "") != args.paper_id: raise RuntimeError("paper id mismatch")
    audit = load(args.anonymity_audit)
    if not validate_anonymity_audit_receipt(audit): raise RuntimeError("invalid Double-Blind Leakage Audit receipt")
    if audit.get("pass") is not True: raise RuntimeError("Double-Blind Leakage Audit is blocked")
    projections = [load(path) for path in args.projection_receipt]
    if any(not validate_projection_receipt(row) for row in projections): raise RuntimeError("invalid anonymized submission projection receipt")

    base = load(args.base_packet)
    upgraded = json.loads(json.dumps(base))
    gates = upgraded.get("gates") or {}
    submission = gates.get("submission-package") or {}
    if not isinstance(gates, dict) or not isinstance(submission, dict): raise RuntimeError("submission-package gate missing from base packet")
    submission["anonymity_audit_version"] = ANON_VERSION
    submission["double_blind_audit_receipt"] = audit
    submission["anonymity_audit_sha256"] = str(audit.get("anonymity_audit_sha256") or "")
    submission["anonymized_submission_projection_sha256"] = [str(row.get("projection_sha256") or "") for row in projections]
    submission["anonymized_submission_projection_requires_refreeze"] = bool(projections)
    gates["submission-package"] = submission; upgraded["gates"] = gates
    result = evaluate_paper_preparation(upgraded)
    if result.get("pass") is not True: raise RuntimeError(f"upgraded Paper Preparation packet blocked: {result.get('blockers')}")

    frozen_sha = str(ledger.get("contract_sha256") or "")
    expected = build_paper_preparation_receipt(paper_id=args.paper_id, contract_sha256=frozen_sha, packet=upgraded)
    latest = latest_preparation_receipt(ledger)
    base_sha = digest(base); upgraded_sha = digest(upgraded)
    current_packet_sha = str(latest.get("packet_sha256") or "")
    if current_packet_sha == upgraded_sha:
        status = "ALREADY_UPGRADED"
        receipt = latest
    else:
        if current_packet_sha != base_sha:
            raise RuntimeError(f"base preparation packet is stale: canonical={current_packet_sha} supplied={base_sha}")
        receipt = expected
        status = "PASS_VALIDATE_ONLY" if args.validate_only else "PASS_ANONYMITY_PREPARATION_UPGRADED"
        if not args.validate_only:
            updated = record_frozen_contract_paper_preparation(ledger_root, args.paper_id, upgraded, actor=args.actor)
            receipt = latest_preparation_receipt(updated)
            after_errors = validate_paper_ledger(updated)
            if after_errors: raise RuntimeError(f"paper ledger invalid after anonymity upgrade: {after_errors}")
            if str(updated.get("current_state") or "") != str(ledger.get("current_state") or ""):
                raise RuntimeError("anonymity preparation upgrade must not change paper state")
    args.output_packet.parent.mkdir(parents=True, exist_ok=True)
    args.output_packet.write_text(json.dumps(upgraded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status, "paper_id": args.paper_id, "paper_state": ledger.get("current_state"),
        "base_packet_sha256": base_sha, "upgraded_packet_sha256": upgraded_sha,
        "preparation_receipt_sha256": receipt.get("receipt_sha256"),
        "anonymity_audit_sha256": audit.get("anonymity_audit_sha256"),
        "anonymity_status": audit.get("status"), "warning_count": audit.get("warning_count", 0),
        "projection_count": len(projections), "requires_new_submission_freeze": bool(projections),
        "scientific_authority": False, "experiment_authority": False, "gpu_authority": False, "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
