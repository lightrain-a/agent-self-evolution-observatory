from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_identity import validate_candidate_identity
from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-falsifier-adjudication.json"
AUTHORITY = {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False}
POLICY = {
    "support_qualified_is_required_but_does_not_itself_authorize_execution": True,
    "executed_falsifier_must_bind_exact_candidate_snapshot": True,
    "adjudication_binds_sealed_discovery_transaction": True,
    "run_local_candidate_id_requires_snapshot_bound_execution_lineage": True,
    "human_reformulation_must_transitively_bind_parent_snapshot": True,
    "pre_f0_reduction_stop_closes_current_formulation_only": True,
    "pre_f0_stop_cannot_enter_persistent_dead_end_memory": True,
    "reduction_supported_requires_explicit_reopen_condition": True,
    "residual_survives_returns_to_semantic_and_current_source_review": True,
    "inconclusive_requires_stop_or_human_reformulation": True,
    "adjudication_cannot_mutate_generator_queue_or_preflight": True,
    "adjudication_cannot_authorize_problem_gate_or_downstream_execution": True,
    "public_evidence_refs_are_logical_uris_plus_sha256_only": True,
}
OUTCOMES = {"REDUCTION_SUPPORTED", "RESIDUAL_SURVIVES", "INCONCLUSIVE"}
STOP_STATUS = "STOP_CURRENT_FORMULATION_EXACT_REDUCTION_SUPPORTED"
RETURN_STATUS = "RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW"
HOLD_STATUS = "HOLD_PREF0_FALSIFIER_INCONCLUSIVE"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _text(value: Any, limit: int = 6000) -> str:
    return " ".join(str(value or "").split())[:limit]


def _candidate(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    rows = [r for r in queue.get("rows") or [] if isinstance(r, dict) and r.get("candidate_id") == candidate_id]
    if len(rows) != 1:
        raise ValueError(f"expected one Pre-F0 queue row:{candidate_id}")
    validate_candidate_identity(rows[0])
    return rows[0]


def _support(preflight: dict[str, Any], candidate_id: str, snapshot: str) -> dict[str, Any]:
    rows = [r for r in preflight.get("rows") or [] if isinstance(r, dict) and r.get("candidate_id") == candidate_id]
    if len(rows) != 1:
        raise ValueError(f"expected one Pre-F0 support row:{candidate_id}")
    row = rows[0]
    if str(row.get("candidate_snapshot_sha256") or "").lower() != snapshot:
        raise ValueError("support row snapshot mismatch")
    if row.get("candidate_identity_version") != "candidate-content-v1" or row.get("disposition") != "SUPPORT_QUALIFIED":
        raise ValueError("falsifier adjudication requires the exact SUPPORT_QUALIFIED candidate")
    if row.get("scientific_authority") is not False:
        raise ValueError("support row authority leak")
    return row


def build_adjudication(*, queue: dict[str, Any], preflight: dict[str, Any], discovery_transaction_id: str,
                       candidate_id: str, outcome: str, evidence_receipts: list[dict[str, Any]],
                       current_formulation: str, strongest_reduction: str, scope_limit: str, reopen_only_if: str,
                       execution_lineage: dict[str, Any] | None = None,
                       conflict_resolution: dict[str, Any] | None = None,
                       generated_at: str | None = None) -> dict[str, Any]:
    outcome = str(outcome or "").upper()
    if outcome not in OUTCOMES:
        raise ValueError(f"invalid outcome:{outcome}")
    qrow = _candidate(queue, candidate_id)
    snapshot = str(qrow["candidate_snapshot_sha256"]).lower()
    support = _support(preflight, candidate_id, snapshot)
    transaction_id = str(discovery_transaction_id or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        raise ValueError("sealed discovery transaction id required")
    generator_run_id = str(queue.get("source_generator_run_id") or "").strip()
    if not generator_run_id:
        raise ValueError("source generator run id required")
    if not evidence_receipts:
        raise ValueError("evidence receipts required")
    lineage = dict(execution_lineage or {})
    lineage.update({
        "discovery_transaction_id": transaction_id,
        "source_generator_run_id": generator_run_id,
        "candidate_snapshot_sha256": snapshot,
        "candidate_id_is_run_local_alias": True,
        "scientific_authority": False,
    })
    if outcome == "REDUCTION_SUPPORTED":
        status, portfolio, opened, next_action = STOP_STATUS, "SEARCH_STOP_CURRENT_FORMULATION", False, "REOPEN_ONLY_IF_RECORDED_CONDITION_MET"
    elif outcome == "RESIDUAL_SURVIVES":
        status, portfolio, opened, next_action = RETURN_STATUS, "SEARCH_REVIEW", True, "SEMANTIC_AND_CURRENT_SOURCE_REVIEW"
    else:
        status, portfolio, opened, next_action = HOLD_STATUS, "SEARCH_HOLD", True, "STOP_OR_HUMAN_REFORMULATION"
    entry = {
        "candidate_id": candidate_id,
        "candidate_identity_version": qrow["candidate_identity_version"],
        "candidate_snapshot_sha256": snapshot,
        "title": qrow.get("title"), "discovery_lane": qrow.get("discovery_lane"),
        "primary_refs": list(qrow.get("primary_refs") or []),
        "preflight_disposition": support.get("disposition"),
        "preflight_support_scope": _text(support.get("support_scope"), 4000),
        "outcome": outcome, "status": status, "portfolio_state": portfolio,
        "current_formulation": _text(current_formulation), "current_formulation_open": opened,
        "strongest_same_information_reduction": _text(strongest_reduction),
        "scope_limit": _text(scope_limit), "reopen_only_if": _text(reopen_only_if), "next_action": next_action,
        "persistent_dead_end_memory_authorized": False, "principle_dead_end_certified": False,
        "problem_gate_passed": False, "evidence_receipts": [dict(r) for r in evidence_receipts],
        "execution_lineage": lineage, "conflict_resolution": dict(conflict_resolution or {}),
        "scientific_authority": False, "authority": dict(AUTHORITY),
    }
    state = {
        "schema_version": SCHEMA_VERSION, "generated_at": generated_at or _now(),
        "status": "PRE_F0_FALSIFIER_ADJUDICATION_COMPLETE", "policy": dict(POLICY),
        "discovery_transaction_id": transaction_id,
        "source_generator_run_id": generator_run_id,
        "source_pre_f0_queue_status": str(queue.get("status") or ""),
        "source_preflight_status": str(preflight.get("status") or ""),
        "summary": {"adjudicated": 1, "reduction_supported": int(outcome == "REDUCTION_SUPPORTED"),
                    "residual_survives": int(outcome == "RESIDUAL_SURVIVES"), "inconclusive": int(outcome == "INCONCLUSIVE"),
                    "current_formulation_stopped": int(outcome == "REDUCTION_SUPPORTED"), "persistent_dead_end_created": 0,
                    "problem_gate_authorized": 0, "paper_design_authorized": 0, "method_authorized": 0,
                    "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
        "entries": [entry], "scientific_authority": False, "authority": dict(AUTHORITY),
    }
    errors = validate_adjudication(state, queue=queue, preflight=preflight)
    if errors:
        raise ValueError("invalid Pre-F0 falsifier adjudication: " + "; ".join(errors))
    return state


def validate_adjudication(state: dict[str, Any], *, queue: dict[str, Any] | None = None,
                           preflight: dict[str, Any] | None = None,
                           transaction_queue: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if state.get("scientific_authority") is not False or any((state.get("authority") or {}).values()):
        errors.append("adjudication authority leak")
    for key, expected in POLICY.items():
        if (state.get("policy") or {}).get(key) != expected:
            errors.append(f"policy-mismatch:{key}")
    transaction_id = str(state.get("discovery_transaction_id") or "").strip().lower()
    generator_run_id = str(state.get("source_generator_run_id") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        errors.append("invalid discovery transaction binding")
    if not generator_run_id:
        errors.append("missing source generator run binding")
    if queue is not None and generator_run_id != str(queue.get("source_generator_run_id") or "").strip():
        errors.append("source generator run mismatch")
    if transaction_queue is not None:
        if transaction_queue.get("discovery_transaction_role") != "queue":
            errors.append("sealed transaction queue role mismatch")
        if transaction_id != str(transaction_queue.get("discovery_transaction_id") or "").strip().lower():
            errors.append("sealed discovery transaction mismatch")
    entries = [r for r in state.get("entries") or [] if isinstance(r, dict)]
    summary = state.get("summary") or {}
    if len(entries) != int(summary.get("adjudicated") or 0):
        errors.append("entry accounting mismatch")
    expected_counts = {"reduction_supported": "REDUCTION_SUPPORTED", "residual_survives": "RESIDUAL_SURVIVES", "inconclusive": "INCONCLUSIVE"}
    for key, outcome in expected_counts.items():
        if int(summary.get(key) or 0) != sum(r.get("outcome") == outcome for r in entries):
            errors.append(f"outcome accounting mismatch:{key}")
    if int(summary.get("persistent_dead_end_created") or 0) != 0 or any(int(summary.get(k) or 0) for k in ("problem_gate_authorized", "paper_design_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("downstream/dead-end authority leak")
    qindex = {(str(r.get("candidate_id") or ""), str(r.get("candidate_snapshot_sha256") or "").lower()) for r in (queue or {}).get("rows") or [] if isinstance(r, dict)}
    pindex = {(str(r.get("candidate_id") or ""), str(r.get("candidate_snapshot_sha256") or "").lower()): r for r in (preflight or {}).get("rows") or [] if isinstance(r, dict)}
    for row in entries:
        cid, snapshot = str(row.get("candidate_id") or ""), str(row.get("candidate_snapshot_sha256") or "").lower()
        if row.get("candidate_identity_version") != "candidate-content-v1" or not re.fullmatch(r"[0-9a-f]{64}", snapshot):
            errors.append(f"invalid identity:{cid}")
        if row.get("preflight_disposition") != "SUPPORT_QUALIFIED" or row.get("scientific_authority") is not False or any((row.get("authority") or {}).values()):
            errors.append(f"support/authority mismatch:{cid}")
        if row.get("persistent_dead_end_memory_authorized") is not False or row.get("principle_dead_end_certified") is not False or row.get("problem_gate_passed") is not False:
            errors.append(f"illegal Pre-F0 promotion:{cid}")
        if row.get("outcome") == "REDUCTION_SUPPORTED" and (row.get("status") != STOP_STATUS or row.get("portfolio_state") != "SEARCH_STOP_CURRENT_FORMULATION" or row.get("current_formulation_open") is not False or not row.get("reopen_only_if")):
            errors.append(f"reduction-stop semantics drift:{cid}")
        lineage = row.get("execution_lineage") or {}
        if lineage.get("candidate_id_is_run_local_alias") is not True:
            errors.append(f"run-local candidate alias semantics missing:{cid}")
        if str(lineage.get("candidate_snapshot_sha256") or "").strip().lower() != snapshot:
            errors.append(f"execution lineage snapshot mismatch:{cid}")
        if str(lineage.get("source_generator_run_id") or "").strip() != generator_run_id:
            errors.append(f"execution lineage generator-run mismatch:{cid}")
        if str(lineage.get("discovery_transaction_id") or "").strip().lower() != transaction_id:
            errors.append(f"execution lineage transaction mismatch:{cid}")
        if lineage.get("scientific_authority") is not False:
            errors.append(f"execution lineage authority leak:{cid}")
        if str(lineage.get("r2_branch_relation") or "").startswith("HUMAN_REFORMULATION_AFTER_PARENT_INCONCLUSIVE"):
            if lineage.get("r2_identity_binding") != "TRANSITIVE_VIA_R1_ADJUDICATED_PLAN_SHA256" or lineage.get("r2_candidate_id_is_run_local_alias") is not True:
                errors.append(f"human-reformulation identity binding missing:{cid}")
            if str(lineage.get("r1_execution_ready_candidate_snapshot_sha256") or "").lower() != snapshot or str(lineage.get("r1_adjudicated_candidate_snapshot_sha256") or "").lower() != snapshot:
                errors.append(f"human-reformulation parent snapshot mismatch:{cid}")
            for key in ("r1_execution_ready_plan_sha256", "r1_adjudicated_plan_sha256", "r1_contract_sha256", "r2_contract_sha256"):
                if not re.fullmatch(r"[0-9a-f]{64}", str(lineage.get(key) or "").lower()):
                    errors.append(f"human-reformulation lineage digest invalid:{cid}:{key}")
            if lineage.get("r1_execution_was_authorized") is not True:
                errors.append(f"R1 bounded-evidence authority provenance missing:{cid}")
            if row.get("outcome") == "REDUCTION_SUPPORTED" and (lineage.get("r2_execution_authority_artifact_present") is not True or lineage.get("r2_evidence_admitted_for_terminal_adjudication") is not True):
                errors.append(f"terminal reduction lacks R2 execution-authority provenance:{cid}")
        receipts = [x for x in row.get("evidence_receipts") or [] if isinstance(x, dict)]
        if not receipts:
            errors.append(f"missing evidence:{cid}")
        for receipt in receipts:
            uri, digest = str(receipt.get("artifact_uri") or ""), str(receipt.get("sha256") or "").lower()
            if not uri or uri.startswith("/") or "/home/" in uri or "/data/" in uri:
                errors.append(f"private evidence URI:{cid}")
            if not re.fullmatch(r"[0-9a-f]{64}", digest) or receipt.get("scientific_authority") is not False:
                errors.append(f"invalid evidence receipt:{cid}")
        if queue is not None and (cid, snapshot) not in qindex:
            errors.append(f"queue snapshot mismatch:{cid}")
        if preflight is not None and (cid, snapshot) not in pindex or (preflight is not None and pindex.get((cid, snapshot), {}).get("disposition") != "SUPPORT_QUALIFIED"):
            errors.append(f"preflight snapshot mismatch:{cid}")
    return sorted(set(errors))


def load_adjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if Path(path).exists():
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    return {"schema_version": SCHEMA_VERSION, "status": "NOT_RUN", "policy": dict(POLICY),
            "summary": {"adjudicated": 0, "reduction_supported": 0, "residual_survives": 0, "inconclusive": 0,
                        "current_formulation_stopped": 0, "persistent_dead_end_created": 0, "problem_gate_authorized": 0,
                        "paper_design_authorized": 0, "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
            "entries": [], "scientific_authority": False, "authority": dict(AUTHORITY)}
