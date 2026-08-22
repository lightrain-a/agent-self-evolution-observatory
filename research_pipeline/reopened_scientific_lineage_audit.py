from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .reopened_child_claim_audit import validate_child_claim_audit, validate_child_claim_audit_ledger
from .reopened_child_claim_expansion_authorization import validate_child_claim_expansion_authorization, validate_claim_expansion_authority_ledger
from .reopened_child_paper_contract import load_child_paper_contract, validate_child_paper_contract
from .reopened_p0_principle_handoff import validate_p0_principle_handoff, validate_p0_principle_handoff_ledger
from .reopened_p0_principle_memory_authorization import (
    validate_principle_memory_authorization,
    validate_principle_memory_handoff,
    validate_principle_memory_ledger,
)
from .reopened_p0_result_adjudication import validate_p0_adjudication, validate_p0_result_ledger, validate_p0_result_packet
from .reopened_principle_memory_closure import load_principle_closures, validate_principle_closure_ledger
from .reopened_scientific_contract import validate_reopened_scientific_contract
from .reopened_scientific_evidence_paper_handoff import (
    validate_paper_revision_handoff_ledger,
    validate_scientific_evidence_paper_handoff,
)
from .submission_attempt_lineage import validate_attempt_ledger, validate_attempt_plan

SCHEMA_VERSION = "1.0"
ZERO_AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _find_attempt(root: Path, attempt_sha256: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    for path in sorted((root / "paper-submission-attempts").glob("*.json")) if (root / "paper-submission-attempts").exists() else []:
        row = _read(path)
        ledger_errors = validate_attempt_ledger(row) if row else ["attempt-ledger-unreadable"]
        if ledger_errors:
            errors.extend(f"attempt-ledger:{code}" for code in ledger_errors)
            continue
        for event in row.get("events") or []:
            receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(receipt, Mapping) and _text(receipt.get("attempt_sha256")) == attempt_sha256 and validate_attempt_plan(receipt):
                return dict(receipt), []
    return {}, list(dict.fromkeys(errors or ["attempt-not-found"]))


def _latest_valid_ledger(path: Path, ledger_validator, receipt_validator) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    if not path.exists():
        return {}, {}, []
    row = _read(path)
    if not row:
        return {}, {}, ["ledger-unreadable"]
    errors = list(ledger_validator(row))
    if errors:
        return row, {}, errors
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if isinstance(receipt, Mapping) and receipt_validator(receipt):
            return row, dict(receipt), []
    return row, {}, ["valid-receipt-missing"]


def _find_reopened_contract(root: Path, attempt_sha256: str) -> tuple[dict[str, Any], list[str]]:
    matches: list[dict[str, Any]] = []
    for path in sorted((root / "scientific-contracts").glob("*.json")) if (root / "scientific-contracts").exists() else []:
        row = _read(path)
        if row and validate_reopened_scientific_contract(row) and _text(row.get("source_attempt_sha256")) == attempt_sha256:
            matches.append(row)
    if len(matches) > 1:
        return {}, ["multiple-reopened-scientific-contracts-for-attempt"]
    return (matches[0], []) if matches else ({}, [])


def _p0_result_receipts(root: Path, contract_id: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    path = root / "scientific-contract-p0-results" / f"{contract_id}.json"
    if not path.exists():
        return {}, {}, []
    row = _read(path)
    if not row:
        return {}, {}, ["p0-result-ledger-unreadable"]
    errors = validate_p0_result_ledger(row)
    if errors:
        return {}, {}, [f"p0-result-ledger:{code}" for code in errors]
    result: dict[str, Any] = {}; adjudication: dict[str, Any] = {}
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if validate_p0_result_packet(receipt): result = dict(receipt)
        elif validate_p0_adjudication(receipt): adjudication = dict(receipt)
    return result, adjudication, []


def audit_reopened_scientific_attempt(root: Path, attempt_sha256: str) -> dict[str, Any]:
    root = Path(root); errors: list[str] = []; warnings: list[str] = []
    attempt, attempt_errors = _find_attempt(root, attempt_sha256); errors.extend(attempt_errors)
    if not attempt:
        return _result(attempt_sha256, {}, {}, {}, errors, warnings)
    if attempt.get("requires_explicit_scientific_reopen") is not True:
        return {**_result(attempt_sha256, attempt, {}, {}, [], []), "status": "NOT_A_SCIENTIFIC_REOPEN_ATTEMPT"}

    reopened_contract, contract_errors = _find_reopened_contract(root, attempt_sha256); errors.extend(contract_errors)
    contract_id = _text(reopened_contract.get("contract_id"))
    if reopened_contract:
        if _text(reopened_contract.get("parent_paper_id")) != _text(attempt.get("paper_id")) or _text(reopened_contract.get("parent_contract_sha256")) != _text(attempt.get("contract_sha256")):
            errors.append("reopened-scientific-contract-parent-lineage-mismatch")
    paper: dict[str, Any] = {
        "status": "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_REQUIRED",
        "paper_revision_handoff_sha256": "", "child_claim_audit_sha256": "",
        "claim_expansion_authorization_sha256": "", "child_paper_contract_sha256": "",
    }
    principle: dict[str, Any] = {
        "status": "P0_PRINCIPLE_HANDOFF_NOT_YET_RECORDED", "principle_handoff_sha256": "",
        "principle_memory_authorization_sha256": "", "principle_memory_handoff_sha256": "",
        "principle_closure_sha256": "",
    }

    handoff_path = root / "paper-scientific-revision-handoffs" / f"{attempt_sha256}.json"
    _, handoff, handoff_errors = _latest_valid_ledger(handoff_path, validate_paper_revision_handoff_ledger, validate_scientific_evidence_paper_handoff)
    errors.extend(f"paper-handoff:{code}" for code in handoff_errors)
    if handoff:
        paper["status"] = "SCIENTIFIC_REOPEN_EVIDENCE_READY_CHILD_CLAIM_AUDIT_REQUIRED"
        paper["paper_revision_handoff_sha256"] = _text(handoff.get("paper_revision_handoff_sha256"))
        if _text(handoff.get("attempt_sha256")) != attempt_sha256:
            errors.append("paper-handoff-attempt-sha-mismatch")
        if _text(handoff.get("paper_id")) != _text(attempt.get("paper_id")) or _text(handoff.get("parent_paper_contract_sha256")) != _text(attempt.get("contract_sha256")):
            errors.append("paper-handoff-parent-paper-lineage-mismatch")
        if not reopened_contract or _text(handoff.get("reopened_contract_id")) != contract_id or _text(handoff.get("reopened_contract_sha256")) != _text(reopened_contract.get("contract_sha256")):
            errors.append("paper-handoff-reopened-contract-lineage-mismatch")
        result, adjudication, p0_errors = _p0_result_receipts(root, contract_id or _text(handoff.get("reopened_contract_id")))
        errors.extend(p0_errors)
        if not result or not adjudication:
            errors.append("paper-handoff-p0-result-or-adjudication-missing")
        else:
            if _text(handoff.get("p0_result_packet_sha256")) != _text(result.get("p0_result_packet_sha256")):
                errors.append("paper-handoff-p0-result-sha-mismatch")
            if _text(handoff.get("p0_adjudication_sha256")) != _text(adjudication.get("p0_adjudication_sha256")):
                errors.append("paper-handoff-p0-adjudication-sha-mismatch")

        audit_path = root / "paper-scientific-claim-audits" / f"{attempt_sha256}.json"
        _, claim_audit, audit_errors = _latest_valid_ledger(audit_path, validate_child_claim_audit_ledger, validate_child_claim_audit)
        errors.extend(f"child-claim-audit:{code}" for code in audit_errors)
        if claim_audit:
            paper["child_claim_audit_sha256"] = _text(claim_audit.get("child_claim_audit_sha256"))
            if _text(claim_audit.get("paper_revision_handoff_sha256")) != paper["paper_revision_handoff_sha256"]:
                errors.append("child-claim-audit-handoff-sha-mismatch")
            paper["status"] = _text(claim_audit.get("status"))

        auth_path = root / "paper-scientific-claim-expansion-authority" / f"{attempt_sha256}.json"
        _, expansion, expansion_errors = _latest_valid_ledger(auth_path, validate_claim_expansion_authority_ledger, validate_child_claim_expansion_authorization)
        errors.extend(f"claim-expansion-authority:{code}" for code in expansion_errors)
        if expansion:
            paper["claim_expansion_authorization_sha256"] = _text(expansion.get("child_claim_expansion_authorization_sha256"))
            if not claim_audit or _text(expansion.get("child_claim_audit_sha256")) != paper["child_claim_audit_sha256"]:
                errors.append("claim-expansion-authority-claim-audit-sha-mismatch")
            paper["status"] = _text(expansion.get("status"))

        child_contract_path = root / "paper-scientific-child-contracts" / f"{attempt_sha256}.json"
        child_contract = load_child_paper_contract(root, attempt_sha256)
        if child_contract_path.exists() and not child_contract:
            errors.append("child-paper-contract-invalid")
        if child_contract:
            if not validate_child_paper_contract(child_contract):
                errors.append("child-paper-contract-invalid")
            else:
                paper["child_paper_contract_sha256"] = _text(child_contract.get("child_paper_contract_sha256"))
                paper["status"] = _text(child_contract.get("status"))
                if not claim_audit or _text(child_contract.get("child_claim_audit_sha256")) != paper["child_claim_audit_sha256"]:
                    errors.append("child-paper-contract-claim-audit-sha-mismatch")
                if _text(child_contract.get("paper_revision_handoff_sha256")) != paper["paper_revision_handoff_sha256"]:
                    errors.append("child-paper-contract-handoff-sha-mismatch")
                child_auth_sha = _text(child_contract.get("claim_expansion_authorization_sha256"))
                if child_auth_sha and child_auth_sha != paper["claim_expansion_authorization_sha256"]:
                    errors.append("child-paper-contract-claim-expansion-authority-sha-mismatch")
                if child_contract.get("human_claim_expansion_authority_confirmed") is True and not child_auth_sha:
                    errors.append("child-paper-contract-human-expansion-without-authority-receipt")
    else:
        if (root / "paper-scientific-claim-audits" / f"{attempt_sha256}.json").exists(): errors.append("child-claim-audit-without-paper-handoff")
        if (root / "paper-scientific-claim-expansion-authority" / f"{attempt_sha256}.json").exists(): errors.append("claim-expansion-authority-without-paper-handoff")
        if (root / "paper-scientific-child-contracts" / f"{attempt_sha256}.json").exists(): errors.append("child-paper-contract-without-paper-handoff")

    # Principle-memory branch progresses independently of positive paper return.
    if not contract_id:
        warnings.append("reopened-scientific-contract-not-yet-created")
    else:
        result, adjudication, p0_errors = _p0_result_receipts(root, contract_id); errors.extend(p0_errors)
        principle_path = root / "scientific-contract-p0-principle-handoffs" / f"{contract_id}.json"
        _, ph, ph_errors = _latest_valid_ledger(principle_path, validate_p0_principle_handoff_ledger, validate_p0_principle_handoff)
        errors.extend(f"principle-handoff:{code}" for code in ph_errors)
        if ph:
            principle["principle_handoff_sha256"] = _text(ph.get("principle_handoff_sha256")); principle["status"] = _text(ph.get("status"))
            if not adjudication or _text(ph.get("p0_adjudication_sha256")) != _text(adjudication.get("p0_adjudication_sha256")):
                errors.append("principle-handoff-p0-adjudication-sha-mismatch")
            memory_path = root / "scientific-contract-p0-principle-memory" / f"{contract_id}.json"
            if memory_path.exists():
                row = _read(memory_path); memory_errors = validate_principle_memory_ledger(row) if row else ["memory-ledger-unreadable"]
                errors.extend(f"principle-memory:{code}" for code in memory_errors)
                authorization: dict[str, Any] = {}; memory_handoff: dict[str, Any] = {}
                if not memory_errors:
                    for event in row.get("events") or []:
                        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
                        if validate_principle_memory_authorization(receipt): authorization = dict(receipt)
                        elif validate_principle_memory_handoff(receipt): memory_handoff = dict(receipt)
                if authorization:
                    principle["principle_memory_authorization_sha256"] = _text(authorization.get("principle_memory_authorization_sha256")); principle["status"] = _text(authorization.get("status"))
                    if _text(authorization.get("principle_handoff_sha256")) != principle["principle_handoff_sha256"]:
                        errors.append("principle-memory-authorization-handoff-sha-mismatch")
                if memory_handoff:
                    principle["principle_memory_handoff_sha256"] = _text(memory_handoff.get("principle_memory_handoff_sha256")); principle["status"] = _text(memory_handoff.get("status"))
                    if not authorization or _text(memory_handoff.get("principle_memory_authorization_sha256")) != principle["principle_memory_authorization_sha256"]:
                        errors.append("principle-memory-handoff-authorization-sha-mismatch")
                    closure_path = root / "research-memory-principle-closures" / f"{_text(ph.get('principle_id'))}.json"
                    if closure_path.exists():
                        closure_ledger = _read(closure_path)
                        closure_errors = validate_principle_closure_ledger(closure_ledger) if closure_ledger else ["closure-ledger-unreadable"]
                        errors.extend(f"principle-closure:{code}" for code in closure_errors)
                    matches = [row for row in load_principle_closures(root) if _text(row.get("principle_memory_handoff_sha256")) == principle["principle_memory_handoff_sha256"]]
                    if matches:
                        closure = matches[-1]; principle["principle_closure_sha256"] = _text(closure.get("principle_closure_sha256")); principle["status"] = _text(closure.get("status"))
                        if _text(closure.get("principle_evidence_sha256")) != _text(memory_handoff.get("principle_evidence_sha256")):
                            errors.append("principle-closure-evidence-sha-mismatch")
        else:
            # A memory/closure without its principle handoff is never a valid partial state.
            if (root / "scientific-contract-p0-principle-memory" / f"{contract_id}.json").exists(): errors.append("principle-memory-without-principle-handoff")

    return _result(attempt_sha256, attempt, paper, principle, errors, warnings)


def _result(attempt_sha256: str, attempt: Mapping[str, Any], paper: Mapping[str, Any], principle: Mapping[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    errors = list(dict.fromkeys(errors)); warnings = list(dict.fromkeys(warnings))
    status = "REOPENED_SCIENTIFIC_LINEAGE_INVALID" if errors else "REOPENED_SCIENTIFIC_LINEAGE_RECONCILED"
    payload = {
        "schema_version": SCHEMA_VERSION, "status": status, "attempt_sha256": attempt_sha256,
        "paper_id": _text(attempt.get("paper_id")), "paper_branch": dict(paper), "principle_branch": dict(principle),
        "errors": errors, "warnings": warnings,
        "parent_submission_bytes_immutable": True, "parent_claim_update_authorized": False,
        "automatic_principle_update_authorized": False, "automatic_memory_write_authorized": False,
        "scientific_authority": False, "experiment_authority": False, "gpu_authority": False, "submission_authority": False,
    }
    payload["lineage_audit_sha256"] = _digest({key: payload[key] for key in payload if key != "lineage_audit_sha256"})
    return payload


def audit_reopened_scientific_portfolio(root: Path) -> dict[str, Any]:
    root = Path(root); attempts: list[str] = []
    directory = root / "paper-submission-attempts"
    for path in sorted(directory.glob("*.json")) if directory.exists() else []:
        row = _read(path)
        if not row or validate_attempt_ledger(row): continue
        for event in row.get("events") or []:
            receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(receipt, Mapping) and validate_attempt_plan(receipt) and receipt.get("requires_explicit_scientific_reopen") is True:
                sha = _text(receipt.get("attempt_sha256"))
                if sha and sha not in attempts: attempts.append(sha)
    rows = [audit_reopened_scientific_attempt(root, sha) for sha in attempts]
    payload = {
        "schema_version": SCHEMA_VERSION, "status": "PASS" if all(not row["errors"] for row in rows) else "FAIL",
        "attempts": rows,
        "summary": {"scientific_reopen_attempts": len(rows), "reconciled": sum(not row["errors"] for row in rows), "invalid": sum(bool(row["errors"]) for row in rows)},
        "authority": dict(ZERO_AUTHORITY),
    }
    payload["audit_sha256"] = _digest({key: payload[key] for key in payload if key != "audit_sha256"})
    return payload
