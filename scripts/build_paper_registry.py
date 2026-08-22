#!/usr/bin/env python3
"""Project canonical Paper Acceptance ledgers into a frontend PaperRegistry snapshot.

The projection has zero scientific/submission authority. Canonical truth remains in
the append-only Paper Acceptance ledger. Preparation receipts are displayed independently
from the legacy SUBMISSION_READY state so older ledgers are not silently rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research_pipeline.presubmission_freeze import verify_frozen_artifacts
DEFAULT_LEDGER_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ROOT") else None
DEFAULT_ARTIFACT_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ARTIFACT_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ARTIFACT_ROOT") else None
DEFAULT_FREEZE_ROOT = Path(os.environ["PAPER_SUBMISSION_FREEZE_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_FREEZE_ROOT") else None
DEFAULT_JSON = ROOT / "generated/paper-registry-state.json"
DEFAULT_JS = ROOT / "generated/paper-registry-state.js"
C01_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
C01_ADJUDICATION = ROOT / "generated/d2-failure-memory-provenance-targeted-repair-adjudication-20260822.json"
D2_SCHEDULER = ROOT / "generated/d2-active-paper-reopen-scheduler.json"


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


def targeted_repair_boundary(paper_id: str) -> dict[str, Any]:
    """Return public-safe decision boundaries for a paper still in targeted repair.

    This projection intentionally carries only scientific decision summaries. It omits
    execution hosts, filesystem locations, provider response identifiers, and raw prompts.
    """
    if paper_id != C01_ID or not C01_ADJUDICATION.exists():
        return {}
    try:
        adjudication = _load_json(C01_ADJUDICATION)
    except (OSError, json.JSONDecodeError):
        return {}
    scheduler_state = "HOLD_SUPPORT_AND_IDENTIFICATION"
    if D2_SCHEDULER.exists():
        try:
            scheduler = _load_json(D2_SCHEDULER)
            match = next((entry for entry in scheduler.get("entries") or [] if entry.get("paper_id") == paper_id), {})
            scheduler_state = str(match.get("scheduler_state") or scheduler_state)
        except (OSError, json.JSONDecodeError):
            pass
    r4 = adjudication.get("r4_primary_result") or {}
    power = adjudication.get("power_audit") or {}
    ident = adjudication.get("identification_audit") or {}
    confirm = adjudication.get("independent_confirmation_support") or {}
    decision = adjudication.get("scientific_decision") or {}
    return {
        "scheduler_state": scheduler_state,
        "scientific_decision": str(decision.get("C4") or ""),
        "primary_result": {
            "success_minus_failure": r4.get("mean_success_minus_failure_terminal_rate"),
            "effect_floor": r4.get("support_effect_floor"),
            "permutation_p_success_greater": r4.get("permutation_p_success_greater"),
            "p_threshold": r4.get("p_threshold"),
            "support_gate_pass": r4.get("support_gate_pass") is True,
            "counterevidence_gate_pass": r4.get("counterevidence_gate_pass") is True,
            "verdict": str(r4.get("verdict") or ""),
        },
        "power": {
            "four_pair_power_range": list(power.get("approx_power_at_four_pairs_range") or []),
            "independent_pairs_for_80pct_power_range": list(power.get("approx_independent_pairs_for_80pct_power_range") or []),
        },
        "identification": {
            "primary_pairs": int(ident.get("primary_pairs") or 0),
            "original_verifier_strict_pass": int(ident.get("original_verifier_strict_pass") or 0),
            "deepseek_strict_pass": int(ident.get("deepseek_strict_pass") or 0),
            "kimi_strict_pass": int(ident.get("kimi_strict_pass") or 0),
            "three_reviewer_unanimous_strict_pass": int(ident.get("three_reviewer_unanimous_strict_pass") or 0),
            "minimum_embedding_cosine": ident.get("minimum_primary_embedding_cosine"),
        },
        "independent_confirmation": {
            "fresh_same_release_qualified_tasks": int(confirm.get("fresh_qualified_task_count") or 0),
            "same_release_confirmation_available": confirm.get("same_release_confirmation_available") is True,
        },
        "reopen_conditions": list(adjudication.get("reopen_conditions") or []),
        "forbidden_repairs": list(adjudication.get("forbidden_repairs") or []),
    }


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def paper_preparation(row: dict[str, Any], artifact_root: Path | None) -> dict[str, Any]:
    receipt = event_payload(row, "paper-preparation")
    if not receipt and artifact_root is not None:
        p = artifact_root / str(row.get("paper_id") or "") / "paper-preparation-receipt.json"
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    receipt = loaded
            except Exception:
                pass
    state = str(row.get("current_state") or "")
    if receipt:
        status = "PASS" if receipt.get("pass") is True else "BLOCKED"
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
        "human_submission_signoff_pending": state == "SUBMISSION_READY" and receipt.get("pass") is True,
    }


def submission_freeze(paper_id: str, preparation: dict[str, Any], freeze_root: Path | None) -> dict[str, Any]:
    receipt: dict[str, Any] = {}
    drift_errors: list[str] = []
    if freeze_root is not None:
        path = freeze_root / f"{paper_id}.json"
        if path.exists():
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                event = latest_event(row, "pre-submission-freeze")
                candidate = event.get("receipt") or {}
                identity = {key: candidate.get(key) for key in (
                    "paper_id", "contract_sha256", "paper_preparation_receipt_sha256",
                    "venue_policy_snapshot_sha256", "frozen_artifacts", "status", "human_signoff_status"
                )}
                if candidate.get("freeze_sha256") == digest(identity):
                    receipt = candidate
                else:
                    drift_errors.append("freeze-receipt-hash-invalid")
            except Exception:
                drift_errors.append("freeze-ledger-unreadable")
    if receipt:
        drift_errors.extend(verify_frozen_artifacts(receipt))
        if preparation.get("receipt_sha256") and receipt.get("paper_preparation_receipt_sha256") != preparation.get("receipt_sha256"):
            drift_errors.append("freeze-preparation-receipt-stale")
        if freeze_root is not None:
            index = freeze_root / "current-freeze-index.json"
            if index.exists():
                try:
                    current_policy = str(json.loads(index.read_text(encoding="utf-8")).get("venue_policy_snapshot_sha256") or "")
                    if current_policy and receipt.get("venue_policy_snapshot_sha256") != current_policy:
                        drift_errors.append("freeze-venue-policy-stale")
                except Exception:
                    drift_errors.append("freeze-policy-index-unreadable")
        drift_errors = list(dict.fromkeys(drift_errors))
        status = "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" if not drift_errors else "MACHINE_FREEZE_STALE"
    elif preparation.get("status") == "PASS":
        status = "MACHINE_FREEZE_PENDING"
    elif preparation.get("status") == "BLOCKED":
        status = "PREPARATION_BLOCKED"
    else:
        status = "NOT_READY_FOR_HUMAN_SUBMISSION"
    return {
        "status": status,
        "freeze_sha256": str(receipt.get("freeze_sha256") or ""),
        "venue_policy_snapshot_sha256": str(receipt.get("venue_policy_snapshot_sha256") or ""),
        "human_signoff_status": str(receipt.get("human_signoff_status") or ""),
        "frozen_artifacts": len(receipt.get("frozen_artifacts") or []),
        "integrity_pass": bool(receipt) and not drift_errors,
        "drift_errors": drift_errors,
        "external_human_submission_authority_required": True,
    }


def project_paper(path: Path, artifact_root: Path | None, freeze_root: Path | None = None) -> dict[str, Any]:
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
    freeze = submission_freeze(paper_id, preparation, freeze_root)
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
            "submission": freeze["status"],
        },
        "gates": {
            "claim_audit": claim_audit.get("pass") is True,
            "manuscript_ci": manuscript_ci.get("pass") is True,
            "prebuttal": prebuttal.get("pass") is True,
            "submission_readiness": readiness.get("submission_ready") is True,
        },
        "paper_preparation": preparation,
        "submission_freeze": freeze,
        "targeted_repair_boundary": targeted_repair_boundary(paper_id) if state == "TARGETED_REPAIR" else {},
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


def build(ledger_root: Path, artifact_root: Path | None = None, freeze_root: Path | None = None) -> dict[str, Any]:
    papers = [project_paper(path, artifact_root, freeze_root) for path in sorted(ledger_root.glob("*.json"))]
    order = {"SUBMISSION_READY": 0, "PREBUTTAL": 1, "PDF_QA": 2, "CLAIM_AUDIT": 3, "TARGETED_REPAIR": 4, "MOCK_PC": 5, "MANUSCRIPT": 6, "PAPER_DESIGN": 7, "PAPER_EVIDENCE": 8}
    papers.sort(key=lambda p: (order.get(p["current_state"], 99), p["paper_id"]))
    summary = {
        "papers": len(papers),
        "submission_ready": sum(p["current_state"] == "SUBMISSION_READY" for p in papers),
        "targeted_repair": sum(p["current_state"] == "TARGETED_REPAIR" for p in papers),
        "preparation_pass": sum(p["paper_preparation"]["pass"] for p in papers),
        "preparation_blocked": sum(p["paper_preparation"]["status"] == "BLOCKED" for p in papers),
        "legacy_ready_needs_preparation_migration": sum(p["paper_preparation"]["status"] == "LEGACY_READY_NEEDS_PREPARATION_MIGRATION" for p in papers),
        "machine_frozen_candidates": sum(p["submission_freeze"]["status"] == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" for p in papers),
        "machine_freeze_stale": sum(p["submission_freeze"]["status"] == "MACHINE_FREEZE_STALE" for p in papers),
        "human_submission_signoff_pending": sum(p["submission_freeze"]["status"] == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" for p in papers),
    }
    payload = {
        "schema_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "canonical_paper_acceptance_ledger",
        "summary": summary,
        "papers": papers,
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    payload["projection_sha256"] = digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-root", type=Path, default=DEFAULT_LEDGER_ROOT, help="Canonical Paper Acceptance ledger root; may also be supplied via PAPER_ACCEPTANCE_ROOT.")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT, help="Optional paper-preparation artifact root; may also be supplied via PAPER_ACCEPTANCE_ARTIFACT_ROOT.")
    parser.add_argument("--freeze-root", type=Path, default=DEFAULT_FREEZE_ROOT, help="Optional pre-submission freeze ledger root; may also be supplied via PAPER_SUBMISSION_FREEZE_ROOT.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--js-output", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    if args.ledger_root is None:
        parser.error("canonical ledger root is required via --ledger-root or PAPER_ACCEPTANCE_ROOT")
    state = build(args.ledger_root, args.artifact_root, args.freeze_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.js_output.write_text("window.PAPER_REGISTRY_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": state["summary"], "projection_sha256": state["projection_sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
