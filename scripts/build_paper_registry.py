#!/usr/bin/env python3
"""Project canonical Paper Acceptance ledgers into a frontend PaperRegistry snapshot.

The projection has zero scientific/submission authority. Canonical truth remains under
/data/.../paper-acceptance. Preparation receipts are displayed independently from the
legacy SUBMISSION_READY state so older ledgers are not silently rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_ROOT = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance")
DEFAULT_ARTIFACT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts")
DEFAULT_JSON = ROOT / "generated/paper-registry-state.json"
DEFAULT_JS = ROOT / "generated/paper-registry-state.js"


def digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def latest_event(row: dict[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(row.get("events") or []):
        if event.get("event_type") == event_type:
            return event
    return {}


def event_payload(row: dict[str, Any], event_type: str) -> dict[str, Any]:
    event = latest_event(row, event_type)
    payload = event.get("receipt") or event.get("result") or {}
    return payload if isinstance(payload, dict) else {}


def paper_preparation(row: dict[str, Any], artifact_root: Path) -> dict[str, Any]:
    receipt = event_payload(row, "paper-preparation")
    if not receipt:
        p = artifact_root / str(row.get("paper_id") or "") / "paper-preparation-receipt.json"
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    receipt = loaded
            except Exception:
                pass
    state = str(row.get("current_state") or "")
    if receipt.get("pass") is True:
        status = "PASS"
    elif state == "SUBMISSION_READY":
        status = "LEGACY_READY_NEEDS_PREPARATION_MIGRATION"
    else:
        status = "NOT_YET_ELIGIBLE"
    return {
        "status": status,
        "pass": receipt.get("pass") is True,
        "protocol_version": str(receipt.get("protocol_version") or ""),
        "receipt_sha256": str(receipt.get("receipt_sha256") or ""),
        "gate_pass": dict(receipt.get("gate_pass") or {}),
        "blockers": list(receipt.get("blockers") or []),
        "human_submission_signoff_pending": state == "SUBMISSION_READY",
    }


def project_paper(path: Path, artifact_root: Path) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding="utf-8"))
    contract = row.get("contract") or {}
    summary = row.get("summary") or {}
    claim_audit = event_payload(row, "claim-audit")
    manuscript_ci = event_payload(row, "manuscript-ci")
    prebuttal = event_payload(row, "prebuttal")
    readiness = event_payload(row, "submission-readiness")
    preparation = paper_preparation(row, artifact_root)
    supported = contract.get("supported_claims") or {}
    unsupported = contract.get("unsupported_claims") or {}
    active = contract.get("active_unrefuted_claims") or {}
    if not isinstance(supported, dict):
        supported = {}
    if not isinstance(unsupported, dict):
        unsupported = {}
    if not isinstance(active, dict):
        active = {}
    paper_id = str(row.get("paper_id") or contract.get("paper_id") or path.stem)
    state = str(row.get("current_state") or "")
    scientific_layer = "SUPPORTED_AND_AUDITED" if claim_audit.get("pass") is True else ("ACTIVE_REPAIR" if state == "TARGETED_REPAIR" else "PRE_AUDIT")
    paper_quality_layer = "PASS" if manuscript_ci.get("pass") is True and prebuttal.get("pass") is True else ("IN_PROGRESS" if state not in {"PAPER_EVIDENCE", "PAPER_DESIGN"} else "NOT_STARTED")
    return {
        "paper_id": paper_id,
        "title": str(contract.get("title") or paper_id),
        "central_question": str(contract.get("central_question") or ""),
        "current_state": state,
        "contract_sha256": str(row.get("contract_sha256") or ""),
        "ledger_events": len(row.get("events") or []),
        "supported_claims": len(supported),
        "active_unrefuted_claims": len(active),
        "unsupported_claims": len(unsupported),
        "limitations": len(contract.get("limitations") or []),
        "layers": {
            "scientific": scientific_layer,
            "paper_quality": paper_quality_layer,
            "paper_preparation": preparation["status"],
            "submission": "HUMAN_HANDOFF_PENDING" if state == "SUBMISSION_READY" else "NOT_READY_FOR_HUMAN_SUBMISSION",
        },
        "gates": {
            "claim_audit": claim_audit.get("pass") is True,
            "manuscript_ci": manuscript_ci.get("pass") is True,
            "prebuttal": prebuttal.get("pass") is True,
            "submission_readiness": readiness.get("submission_ready") is True,
        },
        "paper_preparation": preparation,
        "ledger_summary": {
            "mock_reviews": int(summary.get("mock_reviews") or 0),
            "claim_audit_receipts": int(summary.get("claim_audit_receipts") or 0),
            "manuscript_ci_receipts": int(summary.get("manuscript_ci_receipts") or 0),
            "prebuttal_receipts": int(summary.get("prebuttal_receipts") or 0),
            "paper_preparation_receipts": int(summary.get("paper_preparation_receipts") or 0),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def build(ledger_root: Path, artifact_root: Path) -> dict[str, Any]:
    papers = [project_paper(path, artifact_root) for path in sorted(ledger_root.glob("*.json"))]
    order = {"SUBMISSION_READY": 0, "PREBUTTAL": 1, "PDF_QA": 2, "CLAIM_AUDIT": 3, "TARGETED_REPAIR": 4, "MOCK_PC": 5, "MANUSCRIPT": 6, "PAPER_DESIGN": 7, "PAPER_EVIDENCE": 8}
    papers.sort(key=lambda p: (order.get(p["current_state"], 99), p["paper_id"]))
    summary = {
        "papers": len(papers),
        "submission_ready": sum(p["current_state"] == "SUBMISSION_READY" for p in papers),
        "targeted_repair": sum(p["current_state"] == "TARGETED_REPAIR" for p in papers),
        "preparation_pass": sum(p["paper_preparation"]["pass"] for p in papers),
        "legacy_ready_needs_preparation_migration": sum(p["paper_preparation"]["status"] == "LEGACY_READY_NEEDS_PREPARATION_MIGRATION" for p in papers),
        "human_submission_signoff_pending": sum(p["current_state"] == "SUBMISSION_READY" for p in papers),
    }
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "canonical_ledger_root": str(ledger_root),
        "summary": summary,
        "papers": papers,
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    payload["projection_sha256"] = digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-root", type=Path, default=DEFAULT_LEDGER_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--js-output", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    state = build(args.ledger_root, args.artifact_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.js_output.write_text("window.PAPER_REGISTRY_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": state["summary"], "projection_sha256": state["projection_sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
