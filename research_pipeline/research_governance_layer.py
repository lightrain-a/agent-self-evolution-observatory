from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .governance_protocol import FAILURES, PREDECESSOR_EVIDENCE, STAGES


SCHEMA_VERSION = "1.0"
POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "layer_name": "ARIS Governance Layer",
    "memory_graph_version": "2.1",
    "governance_layer_records_why_a_transition_is_legal_not_what_is_scientifically_true": True,
    "governance_layer_has_zero_scientific_authority": True,
    "governance_may_block_or_require_review_but_cannot_self_authorize": True,
    "execution_failure_has_no_belief_authority": True,
    "belief_authority_does_not_equal_automatic_claim_mutation": True,
    "experiment_authorization_is_fail_closed": True,
    "candidate_lineage_is_receipted_and_missing_provenance_is_a_hold": True,
    "pre_f0_route_receipt_is_a_zero_authority_disposition_not_semantic_review": True,
    "pre_f0_lineage_completion_cannot_clear_reduction_or_support_holds": True,
    "aggregate_funnel_accounting_cannot_claim_record_level_elimination_lineage": True,
    "repair_proposals_do_not_consume_budget_until_recorded": True,
    "one_load_bearing_repair_per_child": True,
    "max_representation_or_objective_repairs_per_substrate": 2,
    "memory_graph_remains_a_derived_traceability_view": True,
}

FAILURE_EFFECTS: dict[str, dict[str, Any]] = {
    "FAIL_PROBLEM": {
        "allowed_effects": ["block_experiment", "request_problem_reframe"],
        "forbidden_effects": ["automatic_claim_invalidation", "automatic_scientific_closure"],
    },
    "FAIL_SUBSTRATE": {
        "allowed_effects": ["block_experiment", "change_substrate"],
        "forbidden_effects": ["invalidate_claim", "scientific_closure"],
    },
    "FAIL_TARGET_DEGENERACY": {
        "allowed_effects": ["block_experiment", "repair_target_construction"],
        "forbidden_effects": ["invalidate_claim", "scientific_closure"],
    },
    "FAIL_REPRESENTATION": {
        "allowed_effects": ["block_experiment", "atomic_representation_repair"],
        "forbidden_effects": ["invalidate_claim", "scientific_closure"],
    },
    "FAIL_BASELINE_CEILING": {
        "allowed_effects": ["block_experiment", "request_simplify_or_merge_review"],
        "forbidden_effects": ["automatic_claim_invalidation", "automatic_scientific_closure"],
    },
    "SUPPORT_INSUFFICIENT": {
        "allowed_effects": ["block_experiment", "acquire_support"],
        "forbidden_effects": ["invalidate_claim", "method_failure", "scientific_closure"],
    },
    "METHOD_FAIL": {
        "allowed_effects": ["block_experiment", "request_method_merge_stop_or_pivot_review"],
        "forbidden_effects": ["automatic_claim_invalidation", "automatic_scientific_closure"],
    },
    "IMPLEMENTATION_ERROR": {
        "allowed_effects": ["require_execution_repair", "no_scientific_effect"],
        "forbidden_effects": ["invalidate_claim", "method_failure", "scientific_closure"],
    },
    "RUNTIME_ERROR": {
        "allowed_effects": ["require_runtime_repair", "no_scientific_effect"],
        "forbidden_effects": ["invalidate_claim", "method_failure", "scientific_closure"],
    },
    "PROVENANCE_INCONCLUSIVE": {
        "allowed_effects": ["block_experiment", "repair_provenance_or_rerun"],
        "forbidden_effects": ["invalidate_claim", "method_failure", "scientific_closure"],
    },
    "BUDGET_STOP": {
        "allowed_effects": ["block_experiment", "replan_cost"],
        "forbidden_effects": ["invalidate_claim", "method_failure", "scientific_closure"],
    },
    "PRINCIPLE_DEAD_END": {
        "allowed_effects": [
            "block_experiment",
            "request_scoped_claim_adjudication",
            "request_scoped_scientific_closure_review",
        ],
        "forbidden_effects": ["automatic_claim_invalidation", "automatic_scientific_closure"],
    },
}

_STAGE_PREREQUISITES: dict[str, list[str]] = {
    "problem": ["problem_contract"],
    "substrate": ["problem_evidence"],
    "f0-identifiability": ["substrate_evidence"],
    "p0-support": ["f0_evidence"],
    "p0-method": ["support_evidence", "support_freeze"],
    "p1-replication": ["method_evidence", "method_freeze"],
    "paper-experiment": ["p1_evidence", "method_freeze", "experiment_blueprint_freeze"],
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _record_id(prefix: str, *parts: Any) -> str:
    payload = "|".join(_text(part) for part in parts)
    return f"{prefix}:{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:20]}"


def scientific_transitions() -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    for index, to_stage in enumerate(STAGES):
        from_stage = STAGES[index - 1] if index else ""
        evidence_field = PREDECESSOR_EVIDENCE.get(to_stage, "")
        transitions.append({
            "transition_id": f"transition:{from_stage or 'entry'}->{to_stage}",
            "from_stage": from_stage,
            "to_stage": to_stage,
            "stage_index": index,
            "evidence_required": list(_STAGE_PREREQUISITES[to_stage]),
            "canonical_predecessor_evidence_field": evidence_field,
            "authorization": "independent-stage-pass",
            "automatic_transition": False,
            "scientific_authority": False,
        })
    return transitions


def classify_failure_code(row: dict[str, Any]) -> str:
    explicit = _text(row.get("failure_code") or row.get("failure_kind")).upper()
    if explicit in FAILURES:
        return explicit
    if row.get("principle_dead_end_certified") is True:
        return "PRINCIPLE_DEAD_END"
    text = " ".join(_text(row.get(key)).lower() for key in ("affected_layer", "diagnosis", "signature"))
    if "provenance" in text:
        return "PROVENANCE_INCONCLUSIVE"
    if "budget" in text or "economy" in text:
        return "BUDGET_STOP"
    if "runtime" in text:
        return "RUNTIME_ERROR"
    if any(token in text for token in ("implementation", "execution", "transport", "ssh", "infrastructure")):
        return "IMPLEMENTATION_ERROR"
    if any(token in text for token in ("target-degener", "no-label-variation", "constant-target")):
        return "FAIL_TARGET_DEGENERACY"
    if "representation" in text or "operationalization" in text or "identifiability" in text:
        return "FAIL_REPRESENTATION"
    if "support" in text or "insufficient" in text:
        return "SUPPORT_INSUFFICIENT"
    if "substrate" in text:
        return "FAIL_SUBSTRATE"
    if any(token in text for token in ("baseline-ceiling", "matched-simplification", "same-information")):
        return "FAIL_BASELINE_CEILING"
    if "problem" in text:
        return "FAIL_PROBLEM"
    return "METHOD_FAIL"


def failure_authority_record(row: dict[str, Any], index: int = 0) -> dict[str, Any]:
    code = classify_failure_code(row)
    belief_authority, next_action, persistent_dead_end_authority = FAILURES[code]
    effects = FAILURE_EFFECTS[code]
    return {
        "failure_record_id": _record_id(
            "failure-authority", row.get("idea_id"), row.get("phase"), row.get("signature"), index
        ),
        "failure_code": code,
        "idea_id": _text(row.get("idea_id")),
        "phase": _text(row.get("phase")),
        "signature": _text(row.get("signature")) or f"failure-{index}",
        "affected_layer": _text(row.get("affected_layer")),
        "belief_authority": bool(belief_authority),
        "persistent_dead_end_authority": bool(persistent_dead_end_authority),
        "allowed_effects": list(effects["allowed_effects"]),
        "forbidden_effects": list(effects["forbidden_effects"]),
        "next_action": next_action,
        "claim_mutation_requires_independent_adjudication": True,
        "scientific_authority": False,
    }


def _stage_for_phase(phase: str) -> str:
    token = phase.strip().lower()
    if "support" in token or "screen" in token or "qualif" in token:
        return "p0-support"
    if token.startswith("f0"):
        return "f0-identifiability"
    if token.startswith("p0"):
        return "p0-method"
    if token.startswith("p1"):
        return "p1-replication"
    if token.startswith("p2") or "paper" in token or "full" in token:
        return "paper-experiment"
    return "f0-identifiability"


def _blockers(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    return [text] if text else []


def experiment_authorization_records(pilot_registry: dict[str, Any]) -> list[dict[str, Any]]:
    transitions = {row["to_stage"]: row for row in scientific_transitions()}
    records: list[dict[str, Any]] = []
    for index, row in enumerate(pilot_registry.get("phases") or []):
        if not isinstance(row, dict):
            continue
        idea_id, phase = _text(row.get("idea_id")), _text(row.get("phase"))
        if not idea_id or not phase:
            continue
        stage = _stage_for_phase(phase)
        transition = transitions[stage]
        blockers = _blockers(row.get("blocked_by"))
        source_authorized = row.get("execution_authorized") is True
        freeze_receipts = {
            "method_freeze": _text(row.get("method_freeze_sha256") or row.get("method_hash")),
            "experiment_blueprint_freeze": _text(
                row.get("experiment_blueprint_sha256") or row.get("experiment_blueprint_hash")
            ),
        }
        if stage == "paper-experiment":
            for key, value in freeze_receipts.items():
                if not value:
                    blockers.append(f"{key}-missing")
        if not source_authorized and not blockers:
            blockers.append("canonical-execution-authorization-absent")
        blockers = list(dict.fromkeys(blockers))
        effective_authorized = bool(source_authorized and not blockers)
        records.append({
            "authorization_id": _record_id("experiment-authorization", idea_id, phase, index),
            "experiment_key": f"{idea_id}:{phase}",
            "idea_id": idea_id,
            "phase": phase,
            "scientific_stage": stage,
            "transition_id": transition["transition_id"],
            "prerequisites": list(transition["evidence_required"]),
            "canonical_execution_authorized": source_authorized,
            "effective_execution_authorized": effective_authorized,
            "blockers": blockers,
            "freeze_receipts": freeze_receipts,
            "source": "pilot_registry",
            "automatic_authorization": False,
            "scientific_authority": False,
        })
    return records


def _load_recorded_repairs(repair_budget_root: Path | None) -> list[dict[str, Any]]:
    if repair_budget_root is None or not repair_budget_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(repair_budget_root.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        idea_id = _text(payload.get("idea_id") or path.stem)
        for index, repair in enumerate(payload.get("repairs") or []):
            if not isinstance(repair, dict):
                continue
            row = dict(repair)
            row.update({
                "repair_record_id": _text(repair.get("repair_id")) or _record_id(
                    "repair", idea_id, repair.get("substrate_id"), index
                ),
                "idea_id": idea_id,
                "recorded": True,
                "consumes_budget": _text(repair.get("repair_kind")) in {"representation", "objective"},
                "scientific_authority": False,
            })
            rows.append(row)
    return rows


def repair_history_records(
    experiment_iteration: dict[str, Any],
    repair_budget_root: Path | None,
) -> list[dict[str, Any]]:
    rows = _load_recorded_repairs(repair_budget_root)
    for node in experiment_iteration.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        idea_id = _text(node.get("idea_id"))
        substrate_id = _text(node.get("artifact_dir")) or idea_id
        for index, child in enumerate(node.get("repair_children") or []):
            if not isinstance(child, dict):
                continue
            operator = _text(child.get("operator"))
            kind = (
                "representation" if "representation" in operator
                else "objective" if "objective" in operator
                else "substrate" if "substrate" in operator
                else "proposal"
            )
            rows.append({
                "repair_record_id": _record_id("repair-proposal", idea_id, child.get("child"), index),
                "idea_id": idea_id,
                "substrate_id": substrate_id,
                "child_id": _text(child.get("child")),
                "repair_kind": kind,
                "changed_assumption": _text(child.get("changed_variable")),
                "precondition": _text(child.get("precondition")),
                "original_claim": _text(node.get("code")),
                "scientific_distance": (
                    "load-bearing"
                    if kind in {"representation", "objective", "substrate"}
                    else "diagnostic"
                ),
                "recorded": False,
                "consumes_budget": False,
                "proposal_only": True,
                "scientific_authority": False,
            })
    return rows


def repair_budget_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    recorded = [row for row in records if row.get("recorded") is True]
    counted = [
        row for row in recorded
        if _text(row.get("repair_kind")) in {"representation", "objective"}
    ]
    by_substrate: dict[tuple[str, str], int] = {}
    by_child: dict[tuple[str, str], int] = {}
    for row in counted:
        substrate_key = (_text(row.get("idea_id")), _text(row.get("substrate_id")))
        by_substrate[substrate_key] = by_substrate.get(substrate_key, 0) + 1
        child_id = _text(row.get("child_id"))
        if child_id:
            child_key = (_text(row.get("idea_id")), child_id)
            by_child[child_key] = by_child.get(child_key, 0) + 1
    substrate_violations = [
        {"idea_id": key[0], "substrate_id": key[1], "count": count}
        for key, count in sorted(by_substrate.items())
        if count > int(POLICY["max_representation_or_objective_repairs_per_substrate"])
    ]
    child_violations = [
        {"idea_id": key[0], "child_id": key[1], "count": count}
        for key, count in sorted(by_child.items())
        if count > 1
    ]
    return {
        "recorded_repairs": len(recorded),
        "proposal_only_repairs": sum(row.get("proposal_only") is True for row in records),
        "budget_consuming_repairs": len(counted),
        "substrate_budget_violations": substrate_violations,
        "one_load_bearing_repair_per_child_violations": child_violations,
        "review_required": bool(substrate_violations or child_violations),
    }


def _candidate_rows(*states: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for state in states:
        for key in ("candidates", "pre_f0_candidates", "rows", "passed", "blocked", "audited"):
            for row in state.get(key) or []:
                if not isinstance(row, dict):
                    continue
                candidate_id = _text(row.get("candidate_id"))
                if candidate_id:
                    grouped.setdefault(candidate_id, []).append(row)
    return grouped


def _recovered_formulation_origin_receipts(
    generator_state: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Map recovered PORT ordinals to archived formulation bytes.

    Archived ingestion assigns PORT ids in formulation-role order. Reconstructing that
    deterministic ordinal map proves where a candidate formulation came from without
    pretending that the formulation call performed semantic review.
    """
    recovery = generator_state.get("portfolio_ingestion_recovery") or {}
    receipts = [
        row for row in recovery.get("formulation_receipts") or []
        if isinstance(row, dict)
    ]
    def role_index(row: dict[str, Any]) -> int:
        match = re.fullmatch(r"formulate-(\d+)", _text(row.get("role")))
        return int(match.group(1)) if match else 10**9
    receipts.sort(key=role_index)
    out: dict[str, dict[str, str]] = {}
    ordinal = 0
    for row in receipts:
        count = int(row.get("complete_candidates") or 0)
        raw_sha = _text(row.get("source_raw_sha256") or row.get("raw_sha256")).lower()
        fingerprint = _text(row.get("request_fingerprint")).lower()
        role = _text(row.get("role"))
        if count <= 0:
            continue
        if (
            not re.fullmatch(r"[0-9a-f]{64}", raw_sha)
            or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
            or not re.fullmatch(r"formulate-\d+", role)
        ):
            # Fail closed for the whole ordinal map: one malformed positive receipt
            # makes every later PORT position ambiguous.
            return {}
        for _ in range(count):
            ordinal += 1
            out[f"PORT-{ordinal:03d}"] = {
                "role": role,
                "raw_sha256": raw_sha,
                "request_fingerprint": fingerprint,
            }
    expected = int(recovery.get("recovered_candidates") or 0)
    if expected and ordinal != expected:
        return {}
    return out


def _pre_f0_route_receipt_sha256(
    *,
    candidate_id: str,
    snapshot_sha256: str,
    route_reason: str,
    blockers: list[str],
    formulation_raw_sha256: str,
    recovery_sha256: str,
) -> str:
    if not all((candidate_id, snapshot_sha256, route_reason, formulation_raw_sha256, recovery_sha256)):
        return ""
    payload = {
        "receipt_class": "PRE_F0_MACHINE_ROUTE_ZERO_AUTHORITY",
        "candidate_id": candidate_id,
        "candidate_snapshot_sha256": snapshot_sha256,
        "route_reason": route_reason,
        "reduction_blockers": sorted(set(blockers)),
        "formulation_raw_sha256": formulation_raw_sha256,
        "ingestion_recovery_sha256": recovery_sha256,
        "scientific_authority": False,
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def candidate_lineage_records(
    *,
    generator_state: dict[str, Any],
    pre_f0_state: dict[str, Any],
    problem_gate_state: dict[str, Any],
    candidate_portfolio: dict[str, Any],
) -> list[dict[str, Any]]:
    grouped = _candidate_rows(
        generator_state, pre_f0_state, problem_gate_state, candidate_portfolio
    )
    generator_receipt = _text(
        ((generator_state.get("raw_artifacts") or {}).get("generator") or {}).get("sha256")
    )
    recovery = generator_state.get("portfolio_ingestion_recovery") or {}
    transaction_id = _text(
        generator_state.get("discovery_transaction_id")
        or recovery.get("source_transaction_id")
    )
    recovery_sha = _text(recovery.get("recovery_sha256")).lower()
    formulation_origins = _recovered_formulation_origin_receipts(generator_state)
    pre_f0_ids = {
        _text(row.get("candidate_id"))
        for state in (generator_state, pre_f0_state)
        for row in (
            (state.get("pre_f0_candidates") or [])
            if state is generator_state
            else (state.get("rows") or [])
        )
        if isinstance(row, dict)
    }
    run_id = _text(generator_state.get("run_id"))
    records: list[dict[str, Any]] = []
    for candidate_id, versions in sorted(grouped.items()):
        merged: dict[str, Any] = {}
        for row in versions:
            merged.update(row)
        review_receipts: list[str] = []
        for row in versions:
            review = row.get("semantic_reduction_review")
            if isinstance(review, dict):
                for key in ("raw_sha256", "sha256", "review_receipt_sha256"):
                    value = _text(review.get(key))
                    if value:
                        review_receipts.append(value)
        blockers: list[str] = []
        for row in versions:
            blockers.extend(_blockers(row.get("reduction_blockers")))
            blockers.extend(_blockers(row.get("blockers")))
        route_reason = _text(merged.get("route_reason"))
        portfolio_state = _text(merged.get("portfolio_state"))
        if route_reason and ("BLOCK" in route_reason.upper() or "HOLD" in portfolio_state.upper()):
            blockers.append(route_reason)
        snapshot_sha = _text(merged.get("candidate_snapshot_sha256"))
        parent_candidate = _text(merged.get("parent_candidate") or merged.get("source_branch_id"))
        generation_receipt_complete = bool(generator_receipt and run_id)
        review_receipt_complete = bool(review_receipts)
        formulation_origin = formulation_origins.get(candidate_id) or {}
        formulation_raw_sha = _text(formulation_origin.get("raw_sha256"))
        pre_f0_route_receipt = ""
        if candidate_id in pre_f0_ids:
            pre_f0_route_receipt = _pre_f0_route_receipt_sha256(
                candidate_id=candidate_id,
                snapshot_sha256=snapshot_sha,
                route_reason=route_reason,
                blockers=list(dict.fromkeys(blockers)),
                formulation_raw_sha256=formulation_raw_sha,
                recovery_sha256=recovery_sha,
            )
        disposition_receipts = sorted(set(review_receipts + ([pre_f0_route_receipt] if pre_f0_route_receipt else [])))
        disposition_receipt_complete = bool(disposition_receipts)
        origin_receipt_complete = bool(formulation_raw_sha or generator_receipt)
        lineage_complete = bool(
            candidate_id
            and snapshot_sha
            and parent_candidate
            and generation_receipt_complete
            and origin_receipt_complete
            and disposition_receipt_complete
        )
        records.append({
            "lineage_id": _record_id("candidate-lineage", candidate_id, snapshot_sha, run_id),
            "candidate_id": candidate_id,
            "parent_candidate": parent_candidate,
            "candidate_snapshot_sha256": snapshot_sha,
            "source_run_id": run_id,
            "discovery_transaction_id": transaction_id,
            "generation_receipt_sha256": generator_receipt,
            "formulation_origin_role": _text(formulation_origin.get("role")),
            "formulation_raw_sha256": formulation_raw_sha,
            "formulation_request_fingerprint": _text(formulation_origin.get("request_fingerprint")),
            "ingestion_recovery_sha256": recovery_sha,
            "review_receipt_sha256": sorted(set(review_receipts)),
            "pre_f0_route_receipt_sha256": pre_f0_route_receipt,
            "disposition_receipt_sha256": disposition_receipts,
            "disposition_receipt_kind": (
                "SEMANTIC_REVIEW"
                if review_receipts
                else ("PRE_F0_MACHINE_ROUTE_ZERO_AUTHORITY" if pre_f0_route_receipt else "")
            ),
            "elimination_reason": list(dict.fromkeys(blockers)),
            "portfolio_state": portfolio_state,
            "route_reason": route_reason,
            "generation_receipt_complete": generation_receipt_complete,
            "origin_receipt_complete": origin_receipt_complete,
            "review_receipt_complete": review_receipt_complete,
            "disposition_receipt_complete": disposition_receipt_complete,
            "lineage_complete": lineage_complete,
            "provenance_status": "COMPLETE" if lineage_complete else "PROVENANCE_INCONCLUSIVE",
            "downstream_authorization_blocked": not lineage_complete,
            "pre_f0_route_has_scientific_authority": False,
            "belief_authority": False,
            "scientific_authority": False,
        })
    return records


def candidate_stage_receipts(
    generator_state: dict[str, Any],
    candidate_portfolio: dict[str, Any],
    problem_gate_state: dict[str, Any],
) -> list[dict[str, Any]]:
    search = generator_state.get("search_portfolio") or {}
    config = search.get("config") or {}
    summary = search.get("summary") or generator_state.get("summary") or {}
    requested = int(config.get("requested_raw_seeds") or 0)
    raw = int(summary.get("raw_seeds") or 0)
    unique = int(summary.get("semantic_unique") or summary.get("semantic_unique_seeds") or 0)
    pre_f0 = int(
        summary.get("recovered_pre_f0_eligible")
        or summary.get("pre_f0_eligible")
        or len(generator_state.get("pre_f0_candidates") or [])
    )
    visible = int((candidate_portfolio.get("summary") or {}).get("visible_candidates") or 0)
    passed = int((problem_gate_state.get("summary") or {}).get("passed_problem_gate") or 0)
    held_at_problem_gate = max(0, visible - passed)
    run_id = _text(generator_state.get("run_id"))
    rows = [
        ("generation-target", requested, raw, 0, "requested target versus observed raw seeds"),
        ("semantic-uniqueness", raw, unique, 0, "raw seeds to semantic-unique candidates"),
        ("pre-f0-route", unique, pre_f0, 0, "semantic-unique candidates to pre-F0"),
        ("portfolio-visibility", pre_f0, visible, 0, "pre-F0 candidates visible in portfolio"),
        ("problem-gate", visible, passed, held_at_problem_gate, "visible candidates to Problem Gate PASS or HOLD"),
    ]
    receipts: list[dict[str, Any]] = []
    for stage, input_count, output_count, held_count, note in rows:
        eliminated_count = (
            max(0, input_count - output_count - held_count)
            if stage != "generation-target"
            else 0
        )
        receipts.append({
            "stage_receipt_id": _record_id(
                "candidate-stage", run_id, stage, input_count, output_count
            ),
            "stage": stage,
            "input_count": input_count,
            "output_count": output_count,
            "held_count": held_count,
            "eliminated_count": eliminated_count,
            "unrealized_target": (
                max(0, input_count - output_count) if stage == "generation-target" else 0
            ),
            "record_level_elimination_reasons_complete": eliminated_count == 0,
            "record_level_disposition_reasons_complete": stage in {
                "portfolio-visibility", "problem-gate"
            },
            "note": note,
            "source_run_id": run_id,
            "scientific_authority": False,
        })
    return receipts


def lint_governance_layer(layer: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if layer.get("scientific_authority") is not False:
        errors.append({"code": "governance-layer-authority-leak"})
    transitions = layer.get("scientific_transitions") or []
    if [row.get("to_stage") for row in transitions] != list(STAGES):
        errors.append({"code": "scientific-transition-order-mismatch"})
    for row in layer.get("failure_authority_records") or []:
        code = _text(row.get("failure_code"))
        if code in {
            "IMPLEMENTATION_ERROR",
            "RUNTIME_ERROR",
            "PROVENANCE_INCONCLUSIVE",
            "BUDGET_STOP",
        }:
            if row.get("belief_authority") is not False:
                errors.append({
                    "code": "non-scientific-failure-gained-belief-authority",
                    "failure_code": code,
                })
            forbidden = set(row.get("forbidden_effects") or [])
            if "invalidate_claim" not in forbidden:
                errors.append({
                    "code": "non-scientific-failure-may-invalidate-claim",
                    "failure_code": code,
                })
    for row in layer.get("experiment_authorizations") or []:
        if row.get("effective_execution_authorized") is True and (
            row.get("blockers") or row.get("canonical_execution_authorized") is not True
        ):
            errors.append({
                "code": "experiment-authorized-without-canonical-clearance",
                "authorization_id": row.get("authorization_id"),
            })
    for row in layer.get("candidate_lineage") or []:
        if row.get("provenance_status") == "PROVENANCE_INCONCLUSIVE":
            warnings.append({
                "code": "candidate-lineage-provenance-inconclusive",
                "candidate_id": row.get("candidate_id"),
            })
    for row in layer.get("candidate_stage_receipts") or []:
        input_count = int(row.get("input_count") or 0)
        accounted = sum(int(row.get(key) or 0) for key in (
            "output_count", "held_count", "eliminated_count", "unrealized_target"
        ))
        if accounted != input_count:
            errors.append({
                "code": "candidate-stage-receipt-accounting-mismatch",
                "stage": row.get("stage"),
                "input_count": input_count,
                "accounted": accounted,
            })
        if int(row.get("eliminated_count") or 0) > 0 and row.get("record_level_elimination_reasons_complete") is not True:
            warnings.append({
                "code": "candidate-stage-record-level-elimination-lineage-incomplete",
                "stage": row.get("stage"),
                "eliminated_count": int(row.get("eliminated_count") or 0),
            })
    repair_summary = layer.get("repair_budget") or {}
    for row in repair_summary.get("substrate_budget_violations") or []:
        errors.append({"code": "repair-budget-violation", **row})
    for row in repair_summary.get("one_load_bearing_repair_per_child_violations") or []:
        errors.append({"code": "multiple-load-bearing-repairs-for-child", **row})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "scientific_authority": False,
    }


def build_aris_governance_layer(
    *,
    governance_state: dict[str, Any],
    pilot_registry: dict[str, Any],
    failure_asset_library: dict[str, Any],
    experiment_iteration: dict[str, Any],
    generator_state: dict[str, Any],
    pre_f0_state: dict[str, Any],
    problem_gate_state: dict[str, Any],
    candidate_portfolio: dict[str, Any],
    repair_budget_root: Path | None = None,
) -> dict[str, Any]:
    transitions = scientific_transitions()
    failures = [
        failure_authority_record(row, index)
        for index, row in enumerate(failure_asset_library.get("assets") or [])
        if isinstance(row, dict)
    ]
    authorizations = experiment_authorization_records(pilot_registry)
    repairs = repair_history_records(experiment_iteration, repair_budget_root)
    repair_budget = repair_budget_summary(repairs)
    lineage = candidate_lineage_records(
        generator_state=generator_state,
        pre_f0_state=pre_f0_state,
        problem_gate_state=problem_gate_state,
        candidate_portfolio=candidate_portfolio,
    )
    stage_receipts = candidate_stage_receipts(
        generator_state, candidate_portfolio, problem_gate_state
    )
    layer = {
        "schema_version": SCHEMA_VERSION,
        "status": "GOVERNANCE_COMPILED",
        "policy": {
            **POLICY,
            "source_governance_schema": governance_state.get("schema_version"),
        },
        "scientific_state_machine": {
            "stages": list(STAGES),
            "transitions_are_fail_closed": True,
            "automatic_transition_authority": False,
        },
        "scientific_transitions": transitions,
        "failure_authority_records": failures,
        "experiment_authorizations": authorizations,
        "repair_history": repairs,
        "repair_budget": repair_budget,
        "candidate_lineage": lineage,
        "candidate_stage_receipts": stage_receipts,
        "memory_graph_integration": {
            "memory_graph_schema": "2.1",
            "failure_binding_key": "failure_record_id",
            "experiment_binding_key": "authorization_id",
            "candidate_binding_key": "lineage_id",
            "bindings_are_derived_zero_authority": True,
        },
        "summary": {
            "stages": len(STAGES),
            "transitions": len(transitions),
            "failure_authority_records": len(failures),
            "belief_authority_true": sum(
                row.get("belief_authority") is True for row in failures
            ),
            "belief_authority_false": sum(
                row.get("belief_authority") is False for row in failures
            ),
            "experiment_authorizations": len(authorizations),
            "experiments_effectively_authorized": sum(
                row.get("effective_execution_authorized") is True
                for row in authorizations
            ),
            "experiment_authorization_holds": sum(
                row.get("effective_execution_authorized") is not True
                for row in authorizations
            ),
            "repair_records": len(repairs),
            "candidate_lineage_records": len(lineage),
            "candidate_lineage_complete": sum(
                row.get("lineage_complete") is True for row in lineage
            ),
            "candidate_provenance_holds": sum(
                row.get("provenance_status") == "PROVENANCE_INCONCLUSIVE"
                for row in lineage
            ),
            "candidate_stage_receipts": len(stage_receipts),
            "candidate_stage_lineage_gaps": sum(
                int(row.get("eliminated_count") or 0) > 0
                and row.get("record_level_elimination_reasons_complete") is not True
                for row in stage_receipts
            ),
            "candidate_stage_unreceipted_elimination_events": sum(
                int(row.get("eliminated_count") or 0)
                for row in stage_receipts
                if row.get("record_level_elimination_reasons_complete") is not True
            ),
        },
        "scientific_authority": False,
        "authority": {
            "claim_mutation": False,
            "scientific_closure": False,
            "problem_gate": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }
    layer["lint"] = lint_governance_layer(layer)
    if layer["lint"]["status"] != "PASS":
        layer["status"] = "GOVERNANCE_INVALID"
    return layer
