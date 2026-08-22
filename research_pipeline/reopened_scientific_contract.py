from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .scientific_reopen_protocol import (
    HANDOFF_DESTINATION,
    HANDOFF_STATUS,
    validate_research_os_scientific_reopen_handoff,
)

SCHEMA_VERSION = "1.0"
CONTRACT_TYPE = "scientific-reopen-child-contract"
CONTRACT_STATUS = "NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED"
ZERO_AUTHORITY = {
    "problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
    "submission": False,
}
REQUIRED_TEXT_FIELDS = (
    "scientific_question",
    "hypothesis",
    "falsifiable_prediction",
    "cheapest_falsifier",
    "scope",
    "stop_condition",
    "difference_from_parent",
    "limitations_boundary",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown-contract"


def _text(value: Any) -> str:
    return str(value or "").strip()


def required_delta_keys(handoff: Mapping[str, Any]) -> list[str]:
    deltas = handoff.get("requested_scientific_deltas") or {}
    if not isinstance(deltas, Mapping):
        return []
    keys: set[str] = set()
    if deltas.get("scientific_contract_unchanged") is not True:
        keys.add("SCIENTIFIC_CONTRACT")
    for category in deltas.get("scientific_revision_categories") or []:
        token = _text(category).upper()
        if token:
            keys.add(token)
    if deltas.get("new_claim_requested") is True:
        keys.add("NEW_CLAIM")
    if deltas.get("new_experiment_requested") is True:
        keys.add("NEW_EXPERIMENT")
    if deltas.get("new_scientific_evidence_requested") is True:
        keys.add("NEW_SCIENTIFIC_EVIDENCE")
    if deltas.get("scientific_interpretation_change_requested") is True:
        keys.add("SCIENTIFIC_INTERPRETATION_CHANGE")
    return sorted(keys)


def evaluate_new_contract_spec(handoff: Mapping[str, Any], spec: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if not validate_research_os_scientific_reopen_handoff(handoff):
        blockers.append("invalid-research-os-reopen-handoff")
    if handoff.get("status") != HANDOFF_STATUS or handoff.get("destination_gate") != HANDOFF_DESTINATION:
        blockers.append("reopen-handoff-not-at-scientific-contract-creation-gate")
    row = dict(spec) if isinstance(spec, Mapping) else {}
    for field in REQUIRED_TEXT_FIELDS:
        if not _text(row.get(field)):
            blockers.append(f"new-contract-spec-missing:{field}")
    evidence_plan = row.get("evidence_plan") or []
    if not isinstance(evidence_plan, Sequence) or isinstance(evidence_plan, (str, bytes)) or not [x for x in evidence_plan if _text(x)]:
        blockers.append("new-contract-spec-evidence-plan-empty")
    mapping = row.get("requested_delta_mapping") or {}
    if not isinstance(mapping, Mapping):
        blockers.append("new-contract-spec-delta-mapping-not-object")
        mapping = {}
    required = required_delta_keys(handoff)
    supplied = sorted(_text(key).upper() for key in mapping.keys() if _text(key))
    if supplied != required:
        blockers.append("new-contract-spec-delta-mapping-must-match-requested-deltas-exactly")
    for key in required:
        if not _text(mapping.get(key)):
            blockers.append(f"new-contract-spec-delta-mapping-empty:{key}")
    if row.get("reviewer_feedback_used_as") != "DIAGNOSTIC_CONTEXT_ONLY":
        blockers.append("reviewer-feedback-must-remain-diagnostic-context")
    if row.get("existing_evidence_used_as") != "CONTEXT_PENDING_NEW_CONTRACT_READJUDICATION":
        blockers.append("existing-evidence-must-await-new-contract-readjudication")
    if row.get("new_evidence_required_before_claim_upgrade") is not True:
        blockers.append("new-evidence-required-before-claim-upgrade")
    if row.get("outcome_driven_selection_forbidden") is not True:
        blockers.append("outcome-driven-selection-must-remain-forbidden")
    if row.get("support_failure_not_scientific_negative") is not True:
        blockers.append("support-failure-boundary-must-be-preserved")
    if row.get("inherit_parent_claim_status") is not False:
        blockers.append("parent-claim-status-must-not-be-inherited")
    return {
        "pass": not blockers,
        "blockers": list(dict.fromkeys(blockers)),
        "required_delta_keys": required,
        "required_text_fields": list(REQUIRED_TEXT_FIELDS),
    }


def contract_identity(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_type": contract.get("contract_type"),
        "parent_paper_id": contract.get("parent_paper_id"),
        "parent_contract_sha256": contract.get("parent_contract_sha256"),
        "source_attempt_sha256": contract.get("source_attempt_sha256"),
        "research_os_handoff_sha256": contract.get("research_os_handoff_sha256"),
        "new_contract_seed_id": contract.get("new_contract_seed_id"),
        "scientific_question": contract.get("scientific_question"),
        "hypothesis": contract.get("hypothesis"),
        "falsifiable_prediction": contract.get("falsifiable_prediction"),
        "cheapest_falsifier": contract.get("cheapest_falsifier"),
        "scope": contract.get("scope"),
        "stop_condition": contract.get("stop_condition"),
        "difference_from_parent": contract.get("difference_from_parent"),
        "limitations_boundary": contract.get("limitations_boundary"),
        "evidence_plan": contract.get("evidence_plan") or [],
        "requested_delta_mapping": contract.get("requested_delta_mapping") or {},
        "status": contract.get("status"),
        "scientific_stage": contract.get("scientific_stage"),
        "problem_gate_required": contract.get("problem_gate_required"),
    }


def build_reopened_scientific_contract(*, handoff: Mapping[str, Any], spec: Mapping[str, Any]) -> dict[str, Any]:
    audit = evaluate_new_contract_spec(handoff, spec)
    if audit["pass"] is not True:
        raise RuntimeError("invalid reopened scientific contract spec: " + ",".join(audit["blockers"]))
    row = dict(spec)
    evidence_plan = [_text(value) for value in row.get("evidence_plan") or [] if _text(value)]
    mapping = {_text(key).upper(): _text(value) for key, value in (row.get("requested_delta_mapping") or {}).items()}
    contract: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "contract_type": CONTRACT_TYPE,
        "parent_paper_id": str(handoff.get("paper_id") or ""),
        "parent_contract_sha256": str(handoff.get("source_contract_sha256") or ""),
        "source_attempt_id": str(handoff.get("attempt_id") or ""),
        "source_attempt_sha256": str(handoff.get("attempt_sha256") or ""),
        "research_os_handoff_sha256": str(handoff.get("research_os_handoff_sha256") or ""),
        "new_contract_seed_id": str(handoff.get("new_contract_seed_id") or ""),
        "scientific_question": _text(row.get("scientific_question")),
        "hypothesis": _text(row.get("hypothesis")),
        "falsifiable_prediction": _text(row.get("falsifiable_prediction")),
        "cheapest_falsifier": _text(row.get("cheapest_falsifier")),
        "scope": _text(row.get("scope")),
        "stop_condition": _text(row.get("stop_condition")),
        "difference_from_parent": _text(row.get("difference_from_parent")),
        "limitations_boundary": _text(row.get("limitations_boundary")),
        "evidence_plan": evidence_plan,
        "requested_delta_mapping": mapping,
        "required_delta_keys": list(audit["required_delta_keys"]),
        "reviewer_feedback_used_as": "DIAGNOSTIC_CONTEXT_ONLY",
        "existing_evidence_used_as": "CONTEXT_PENDING_NEW_CONTRACT_READJUDICATION",
        "new_evidence_required_before_claim_upgrade": True,
        "outcome_driven_selection_forbidden": True,
        "support_failure_not_scientific_negative": True,
        "inherit_parent_claim_status": False,
        "parent_claim_status_unchanged": True,
        "status": CONTRACT_STATUS,
        "scientific_stage": "problem",
        "problem_gate_required": True,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_design_authorized": False,
        "experiment_blueprint_authorized": False,
        "p0_authorized": False,
        "claim_expansion_authorized": False,
        "experiment_authorized": False,
        "gpu_execution_authorized": False,
        "automatic_provider_calls_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
        "created_at": _now(),
    }
    contract_sha = _digest(contract_identity(contract))
    contract["contract_sha256"] = contract_sha
    contract["contract_id"] = "reopen-contract-" + contract_sha[:20]
    return contract


def validate_reopened_scientific_contract(contract: Mapping[str, Any]) -> bool:
    if contract.get("contract_type") != CONTRACT_TYPE or contract.get("status") != CONTRACT_STATUS:
        return False
    if contract.get("scientific_stage") != "problem" or contract.get("problem_gate_required") is not True:
        return False
    for key in (
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_design_authorized",
        "experiment_blueprint_authorized",
        "p0_authorized",
        "claim_expansion_authorized",
        "experiment_authorized",
        "gpu_execution_authorized",
        "automatic_provider_calls_authorized",
        "scientific_authority",
        "experiment_authority",
        "gpu_authority",
        "submission_authority",
    ):
        if contract.get(key) is not False:
            return False
    if contract.get("reviewer_feedback_used_as") != "DIAGNOSTIC_CONTEXT_ONLY":
        return False
    if contract.get("existing_evidence_used_as") != "CONTEXT_PENDING_NEW_CONTRACT_READJUDICATION":
        return False
    if contract.get("inherit_parent_claim_status") is not False or contract.get("parent_claim_status_unchanged") is not True:
        return False
    if contract.get("new_evidence_required_before_claim_upgrade") is not True:
        return False
    if contract.get("outcome_driven_selection_forbidden") is not True or contract.get("support_failure_not_scientific_negative") is not True:
        return False
    if not contract.get("research_os_handoff_sha256") or not contract.get("parent_contract_sha256"):
        return False
    expected_sha = _digest(contract_identity(contract))
    if str(contract.get("contract_sha256") or "") != expected_sha:
        return False
    return str(contract.get("contract_id") or "") == "reopen-contract-" + expected_sha[:20]


def _contract_directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contracts" else root / "scientific-contracts"


def publish_reopened_scientific_contract(root: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("invalid reopened scientific contract")
    directory = _contract_directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    contract_id = str(contract.get("contract_id") or "")
    path = directory / f"{_slug(contract_id)}.json"
    lock = directory / f".{_slug(contract_id)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if path.exists():
            current = json.loads(path.read_text(encoding="utf-8"))
            if str(current.get("contract_sha256") or "") == str(contract.get("contract_sha256") or "") and validate_reopened_scientific_contract(current):
                return current
            raise RuntimeError("scientific contract id collision or attempted mutation")
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(dict(contract), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return dict(contract)


def find_contract_by_handoff(root: Path, handoff_sha256: str) -> dict[str, Any]:
    directory = _contract_directory(root)
    if not directory.exists():
        return {}
    matches: list[dict[str, Any]] = []
    for path in sorted(directory.glob("reopen-contract-*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if str(row.get("research_os_handoff_sha256") or "") == str(handoff_sha256 or "") and validate_reopened_scientific_contract(row):
            matches.append(row)
    if len(matches) > 1:
        raise RuntimeError("multiple reopened scientific contracts bind the same Research OS handoff")
    return matches[0] if matches else {}


def public_reopened_contract_summary(contract: Mapping[str, Any]) -> dict[str, Any]:
    if not contract:
        return {
            "status": "NEW_SCIENTIFIC_CONTRACT_NOT_CREATED",
            "contract_id": "",
            "contract_sha256": "",
            "scientific_question": "",
            "scientific_stage": "",
            "problem_gate_required": True,
            "authority": dict(ZERO_AUTHORITY),
        }
    if not validate_reopened_scientific_contract(contract):
        return {
            "status": "NEW_SCIENTIFIC_CONTRACT_INVALID",
            "contract_id": str(contract.get("contract_id") or ""),
            "contract_sha256": str(contract.get("contract_sha256") or ""),
            "scientific_question": "",
            "scientific_stage": "",
            "problem_gate_required": True,
            "authority": dict(ZERO_AUTHORITY),
        }
    return {
        "status": CONTRACT_STATUS,
        "contract_id": str(contract.get("contract_id") or ""),
        "contract_sha256": str(contract.get("contract_sha256") or ""),
        "parent_contract_sha256": str(contract.get("parent_contract_sha256") or ""),
        "research_os_handoff_sha256": str(contract.get("research_os_handoff_sha256") or ""),
        "scientific_question": str(contract.get("scientific_question") or ""),
        "falsifiable_prediction": str(contract.get("falsifiable_prediction") or ""),
        "scientific_stage": "problem",
        "problem_gate_required": True,
        "problem_gate_authorized": False,
        "method_design_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_execution_authorized": False,
        "authority": dict(ZERO_AUTHORITY),
    }
