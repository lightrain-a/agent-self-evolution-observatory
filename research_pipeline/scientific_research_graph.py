from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Any


SCHEMA_VERSION = "2.1"
OVERLAY_NODE_KINDS = {
    "phenomenon", "problem_contract", "candidate_problem", "idea", "claim",
    "method", "experiment", "evidence_reference", "core_principle",
    "failure_asset", "success", "scientific_closure", "search_closure",
    "hold", "reopen_condition", "limitation", "counterevidence",
    "control_design", "authorization_gate",
}
POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "graph_is_a_derived_traceability_view_not_scientific_authority": True,
    "existing_evidence_graph_is_referenced_not_duplicated": True,
    "canonical_artifacts_remain_the_only_scientific_sources_of_truth": True,
    "paper_phenomenon_problem_contract_idea_claim_method_experiment_failure_success_closure_and_reopen_are_distinct_node_kinds": True,
    "experiment_failure_edge_cannot_close_core_principle": True,
    "execution_runtime_protocol_support_operationalization_and_method_failure_are_not_scientific_negatives": True,
    "only_certified_principle_dead_end_may_emit_principle_closure_edge": True,
    "search_closure_and_scientific_dead_end_are_distinct": True,
    "every_closure_and_hold_has_an_explicit_reopen_condition_node": True,
    "closure_propagation_requires_same_scientific_object_mechanism_and_claim_type": True,
    "missing_scope_key_blocks_closure_propagation": True,
    "claim_conflict_is_reported_not_automatically_resolved": True,
    "failure_assets_preserve_affected_layer_and_does_not_imply_scope": True,
    "success_memory_is_scope_bound_and_does_not_generalize_automatically": True,
    "candidate_portfolio_stage_does_not_promote_scientific_status": True,
    "aris_governance_is_a_separate_constraint_layer_not_a_scientific_truth_store": True,
    "governance_bindings_may_block_but_cannot_self_authorize": True,
    "belief_authority_never_implies_automatic_claim_mutation": True,
    "candidate_provenance_hold_cannot_be_promoted_by_memory": True,
    "claim_evidence_counterevidence_limitation_and_reopen_are_explicitly_bound": True,
    "control_design_and_authorization_gate_are_distinct_zero_authority_nodes": True,
    "not_supported_claim_boundary_is_not_a_scientific_negative": True,
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _idea_node_id(idea_id: str) -> str:
    return f"idea:{idea_id}"


def _first_text(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _text(row.get(key))
        if value:
            return value
    return ""


def _scope_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip().startswith("{"):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def closure_scope_signature(row: dict[str, Any]) -> tuple[str, str, str]:
    scope = _scope_dict(row.get("scope"))
    scientific_object = _first_text(
        row, "scientific_object", "object", "object_id", "candidate_id", "idea_id"
    ) or _first_text(scope, "scientific_object", "object", "object_id", "candidate_id", "idea_id")
    mechanism = _first_text(
        row, "mechanism", "mechanism_id", "mechanism_axis", "core_mechanism"
    ) or _first_text(scope, "mechanism", "mechanism_id", "mechanism_axis", "core_mechanism")
    claim_type = _first_text(
        row, "claim_type", "claim_kind", "claim_surface"
    ) or _first_text(scope, "claim_type", "claim_kind", "claim_surface")
    return scientific_object, mechanism, claim_type


def can_propagate_closure(closure: dict[str, Any], target: dict[str, Any]) -> bool:
    closure_scope = closure_scope_signature(closure)
    target_scope = closure_scope_signature(target)
    return all(closure_scope) and closure_scope == target_scope


def _failure_class(affected_layer: str) -> str:
    layer = affected_layer.lower().replace("_", "-")
    if any(token in layer for token in ("execution", "ssh", "transport", "infrastructure")):
        return "execution"
    if "runtime" in layer:
        return "runtime"
    if "protocol" in layer or "authority" in layer:
        return "protocol"
    if "support" in layer:
        return "support"
    if "operational" in layer or "identifiability" in layer:
        return "operationalization"
    if "principle" in layer or "core-principle" in layer:
        return "principle"
    return "method"


def _canonical_base_kind(kind: str) -> str:
    value = kind.lower().replace("-", "_")
    aliases = {
        "paper_record": "paper", "primary_paper": "paper", "literature": "paper",
        "problem": "problem_contract", "candidate_problem": "problem_contract",
        "failure": "failure_asset", "closure": "scientific_closure",
        "evidence": "evidence_reference",
    }
    return aliases.get(value, value or "evidence_reference")


def lint_scientific_research_graph(graph: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    base_ids = set(graph.get("base_graph", {}).get("node_ids") or [])
    nodes = [row for row in graph.get("overlay_nodes") or [] if isinstance(row, dict)]
    edges = [row for row in graph.get("overlay_edges") or [] if isinstance(row, dict)]
    ids = [_text(row.get("id")) for row in nodes]
    by_id = {_text(row.get("id")): row for row in nodes}
    if len(ids) != len(set(ids)):
        errors.append({"code": "duplicate-overlay-node-id"})
    for node in nodes:
        node_id, kind = _text(node.get("id")), _text(node.get("kind"))
        if kind not in OVERLAY_NODE_KINDS:
            errors.append({"code": "invalid-overlay-node-kind", "node_id": node_id, "kind": kind})
        if node.get("scientific_authority") is not False:
            errors.append({"code": "derived-node-authority-leak", "node_id": node_id})
        if kind == "failure_asset":
            failure_class = _text(node.get("failure_class"))
            if failure_class != "principle" and node.get("scientific_negative") is True:
                errors.append({"code": "non-principle-failure-became-scientific-negative", "node_id": node_id})
            failure_code = _text(node.get("failure_code"))
            if failure_code in {"IMPLEMENTATION_ERROR", "RUNTIME_ERROR", "PROVENANCE_INCONCLUSIVE", "BUDGET_STOP"} and node.get("belief_authority") is not False:
                errors.append({"code": "execution-or-provenance-failure-gained-belief-authority", "node_id": node_id})
        if kind == "experiment" and node.get("effective_execution_authorized") is True and node.get("authorization_blockers"):
            errors.append({"code": "experiment-authorized-with-governance-blocker", "node_id": node_id})
        if kind == "candidate_problem" and node.get("provenance_status") == "PROVENANCE_INCONCLUSIVE" and node.get("downstream_authorization_blocked") is not True:
            errors.append({"code": "candidate-provenance-hold-not-enforced", "node_id": node_id})
        if kind in {"scientific_closure", "search_closure", "hold"}:
            reopen_id = _text(node.get("reopen_condition_id"))
            if not reopen_id or by_id.get(reopen_id, {}).get("kind") != "reopen_condition":
                errors.append({"code": "closure-or-hold-missing-reopen-node", "node_id": node_id})
            if kind == "scientific_closure" and node.get("principle_dead_end_certified") is not True:
                errors.append({"code": "scientific-closure-without-principle-certificate", "node_id": node_id})
        if kind in {"control_design", "authorization_gate"}:
            if node.get("execution_authorized") is not False:
                errors.append({"code": "control-or-gate-execution-authority-leak", "node_id": node_id})
        if kind == "authorization_gate" and node.get("automatic_authorization") is not False:
            errors.append({"code": "authorization-gate-became-automatic", "node_id": node_id})
    known_ids = base_ids | set(ids)
    for edge in edges:
        source, target = _text(edge.get("source")), _text(edge.get("target"))
        relation = _text(edge.get("relation"))
        if source not in known_ids or target not in known_ids:
            errors.append({"code": "edge-endpoint-missing", "source": source, "target": target, "relation": relation})
        if edge.get("scientific_authority") is not False:
            errors.append({"code": "derived-edge-authority-leak", "source": source, "target": target})
        if relation == "propagates_closure":
            closure, claim = by_id.get(source) or {}, by_id.get(target) or {}
            if not can_propagate_closure(closure, claim):
                errors.append({"code": "closure-propagation-scope-mismatch", "source": source, "target": target})
        if relation in {"closes_claim", "closes_principle"}:
            source_node = by_id.get(source) or {}
            if source_node.get("kind") == "failure_asset" and source_node.get("failure_class") != "principle":
                errors.append({"code": "non-principle-failure-emitted-closure-edge", "source": source, "target": target})
        if relation in {
            "supports_claim",
            "informs_claim_without_identifying",
            "limits_claim",
            "challenges_claim",
            "limits_measurement_interpretation",
            "bounds_out_claim",
            "tests_identification_for",
        }:
            target_node = by_id.get(target) or {}
            if target not in base_ids and target_node.get("kind") != "claim":
                errors.append({"code": "claim-traceability-edge-target-is-not-claim", "source": source, "target": target, "relation": relation})
    bindings = graph.get("governance_bindings") or {}
    if bindings and bindings.get("scientific_authority") is not False:
        errors.append({"code": "governance-bindings-authority-leak"})
    claim_bindings = graph.get("claim_evidence_bindings") or {}
    if claim_bindings and claim_bindings.get("scientific_authority") is not False:
        errors.append({"code": "claim-evidence-bindings-authority-leak"})
    for missing in (graph.get("typed_coverage") or {}).get("missing_pipeline_kinds") or []:
        warnings.append({"code": "typed-pipeline-kind-not-yet-materialized", "kind": missing})
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "scientific_authority": False,
    }


def build_scientific_research_graph(
    *,
    evidence_graph: dict[str, Any],
    candidate_portfolio: dict[str, Any],
    scientific_meta_trace: dict[str, Any],
    failure_asset_library: dict[str, Any],
    pilot_registry: dict[str, Any],
    research_memory_wiki: dict[str, Any] | None = None,
    claim_ledger: list[dict[str, Any]] | None = None,
    experiment_iteration: dict[str, Any] | None = None,
    governance_layer: dict[str, Any] | None = None,
    claim_evidence_traceability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile a typed, read-only overlay over canonical scientific artifacts."""
    research_memory_wiki = research_memory_wiki or {}
    claim_ledger = claim_ledger or []
    experiment_iteration = experiment_iteration or {}
    governance_layer = governance_layer or {}
    claim_evidence_traceability = claim_evidence_traceability or {}
    failure_governance = {
        (_text(row.get("idea_id")), _text(row.get("signature"))): row
        for row in governance_layer.get("failure_authority_records") or []
        if isinstance(row, dict)
    }
    experiment_governance = {
        (_text(row.get("idea_id")), _text(row.get("phase"))): row
        for row in governance_layer.get("experiment_authorizations") or []
        if isinstance(row, dict)
    }
    candidate_governance = {
        _text(row.get("candidate_id")): row
        for row in governance_layer.get("candidate_lineage") or []
        if isinstance(row, dict) and _text(row.get("candidate_id"))
    }
    base_nodes = [
        row for row in evidence_graph.get("nodes") or []
        if isinstance(row, dict) and _text(row.get("id"))
    ]
    base_edges = [row for row in evidence_graph.get("edges") or [] if isinstance(row, dict)]
    base_ids = {_text(row.get("id")) for row in base_nodes}
    base_node_kinds = Counter(_canonical_base_kind(_text(row.get("kind"))) for row in base_nodes)
    base_relations = Counter(_text(row.get("relation")) or "related" for row in base_edges)
    overlay_nodes: dict[str, dict[str, Any]] = {}
    overlay_edges: list[dict[str, Any]] = []

    def add_node(node: dict[str, Any]) -> str:
        node_id = _text(node.get("id"))
        if not node_id:
            raise ValueError("typed research graph node requires id")
        if node_id not in base_ids:
            node = dict(node)
            node["scientific_authority"] = False
            overlay_nodes.setdefault(node_id, node)
        return node_id

    def add_edge(source: str, target: str, relation: str, **data: Any) -> None:
        overlay_edges.append({
            "source": source, "target": target, "relation": relation, **data,
            "scientific_authority": False,
        })

    def ensure_idea(idea_id: str, source: str) -> str:
        return add_node({
            "id": _idea_node_id(idea_id), "kind": "idea",
            "label": idea_id, "source": source,
        })

    for row in candidate_portfolio.get("rows") or []:
        if not isinstance(row, dict):
            continue
        cid = _text(row.get("candidate_id"))
        if not cid:
            continue
        lineage_record = candidate_governance.get(cid) or {}
        candidate_id = add_node({
            "id": f"candidate:{cid}", "kind": "candidate_problem",
            "label": _text(row.get("title")) or cid, "candidate_id": cid,
            "stage": _text(row.get("stage")),
            "portfolio_state": _text(row.get("portfolio_state")),
            "lineage_id": _text(lineage_record.get("lineage_id")),
            "parent_candidate": _text(lineage_record.get("parent_candidate")),
            "provenance_status": _text(lineage_record.get("provenance_status")),
            "downstream_authorization_blocked": lineage_record.get("downstream_authorization_blocked") is True,
            "source": "research_candidate_portfolio",
        })
        idea_id = ensure_idea(cid, "research_candidate_portfolio")
        add_edge(idea_id, candidate_id, "formulated_as")
        phenomenon = _first_text(row, "phenomenon", "phenomenon_text", "target_phenomenon")
        if phenomenon:
            phenomenon_id = add_node({
                "id": f"phenomenon:{_short_hash(cid + '|' + phenomenon)}",
                "kind": "phenomenon", "label": phenomenon,
                "scientific_object": _first_text(row, "scientific_object", "object") or cid,
                "source": "research_candidate_portfolio",
            })
            add_edge(phenomenon_id, candidate_id, "motivates_problem_contract")
        problem_text = _first_text(row, "problem_contract", "problem_text", "research_question")
        if problem_text:
            contract_id = add_node({
                "id": f"problem-contract:{_short_hash(cid + '|' + problem_text)}",
                "kind": "problem_contract", "label": problem_text,
                "scientific_object": _first_text(row, "scientific_object", "object") or cid,
                "mechanism": _first_text(row, "mechanism", "mechanism_axis"),
                "claim_type": _first_text(row, "claim_type", "claim_kind"),
                "source": "research_candidate_portfolio",
            })
            add_edge(candidate_id, contract_id, "defines_problem_contract")
        method = _first_text(row, "method", "method_name", "proposed_method")
        if method:
            method_id = add_node({
                "id": f"method:{_short_hash(cid + '|' + method)}",
                "kind": "method", "label": method,
                "source": "research_candidate_portfolio",
            })
            add_edge(candidate_id, method_id, "proposes_method")

    claim_nodes: list[dict[str, Any]] = []
    claim_groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for idx, row in enumerate(claim_ledger):
        if not isinstance(row, dict):
            continue
        claim_id = _text(row.get("claim_id")) or f"ledger-{idx}"
        statement = _first_text(row, "claim_text", "statement", "claim")
        object_id, mechanism, claim_type = closure_scope_signature(row)
        node_id = add_node({
            "id": f"claim:{claim_id}", "kind": "claim",
            "label": statement or claim_id, "claim_id": claim_id,
            "claim_type": claim_type, "scientific_object": object_id,
            "mechanism": mechanism, "scope": row.get("scope") or "",
            "adjudication_status": _text(row.get("adjudication_status")),
            "trace_complete": row.get("trace_complete") is True,
            "evidence_ids": [str(value) for value in row.get("evidence_ids") or [] if str(value)],
            "source": "claim_ledger",
        })
        claim_node = overlay_nodes.get(node_id)
        if claim_node:
            claim_nodes.append(claim_node)
        group_key = (object_id, mechanism, claim_type, " ".join(statement.lower().split()))
        claim_groups[group_key].append(row)
        for evidence_id in row.get("evidence_ids") or []:
            evidence_ref = _text(evidence_id)
            if not evidence_ref:
                continue
            evidence_node = add_node({
                "id": f"evidence-ref:{_short_hash(evidence_ref)}",
                "kind": "evidence_reference", "label": evidence_ref,
                "source": "claim_ledger",
            })
            add_edge(evidence_node, node_id, "supports_claim")

    if claim_evidence_traceability:
        if claim_evidence_traceability.get("status") != "CLAIM_EVIDENCE_TRACEABILITY_COMPILED":
            raise ValueError("claim/evidence traceability bundle is not compiled")
        for node in claim_evidence_traceability.get("nodes") or []:
            if not isinstance(node, dict):
                raise ValueError("claim/evidence traceability node must be an object")
            add_node(dict(node))
        for edge in claim_evidence_traceability.get("edges") or []:
            if not isinstance(edge, dict):
                raise ValueError("claim/evidence traceability edge must be an object")
            data = {
                key: value
                for key, value in edge.items()
                if key not in {"source", "target", "relation", "scientific_authority"}
            }
            add_edge(
                _text(edge.get("source")),
                _text(edge.get("target")),
                _text(edge.get("relation")),
                **data,
            )

    for row in scientific_meta_trace.get("principles") or []:
        if not isinstance(row, dict):
            continue
        principle_id, idea_id = _text(row.get("principle_id")), _text(row.get("idea_id"))
        if not principle_id:
            continue
        node_id = add_node({
            "id": f"principle:{principle_id}", "kind": "core_principle",
            "label": _text(row.get("mechanism")) or principle_id,
            "mechanism": _text(row.get("mechanism")),
            "belief_state": _text(row.get("belief_state")),
            "source": "scientific_meta_trace",
        })
        if idea_id:
            add_edge(node_id, ensure_idea(idea_id, "scientific_meta_trace"), "principle_for")

    experiment_nodes: dict[tuple[str, str], str] = {}
    for row in pilot_registry.get("phases") or []:
        if not isinstance(row, dict):
            continue
        idea_id, phase = _text(row.get("idea_id")), _text(row.get("phase"))
        if not idea_id or not phase:
            continue
        authorization = experiment_governance.get((idea_id, phase)) or {}
        node_id = add_node({
            "id": f"experiment:{idea_id}:{phase}", "kind": "experiment",
            "label": _text(row.get("title")) or f"{idea_id} {phase}",
            "idea_id": idea_id, "phase": phase,
            "status": _text(row.get("status")),
            "authorization_id": _text(authorization.get("authorization_id")),
            "scientific_stage": _text(authorization.get("scientific_stage")),
            "effective_execution_authorized": authorization.get("effective_execution_authorized") is True,
            "authorization_blockers": list(authorization.get("blockers") or []),
            "source": "pilot_registry",
        })
        experiment_nodes[(idea_id, phase)] = node_id
        add_edge(ensure_idea(idea_id, "pilot_registry"), node_id, "tested_by")

    for idx, row in enumerate(failure_asset_library.get("assets") or []):
        if not isinstance(row, dict):
            continue
        idea_id, phase = _text(row.get("idea_id")), _text(row.get("phase"))
        signature = _text(row.get("signature")) or f"failure-{idx}"
        affected_layer = _text(row.get("affected_layer"))
        failure_class = _failure_class(affected_layer)
        authority_record = failure_governance.get((idea_id, signature)) or {}
        node_id = add_node({
            "id": f"failure:{_short_hash(f'{idea_id}|{phase}|{signature}|{idx}')}",
            "kind": "failure_asset", "label": signature,
            "failure_class": failure_class, "affected_layer": affected_layer,
            "failure_record_id": _text(authority_record.get("failure_record_id")),
            "failure_code": _text(authority_record.get("failure_code")),
            "belief_authority": authority_record.get("belief_authority") is True,
            "allowed_effects": list(authority_record.get("allowed_effects") or []),
            "forbidden_effects": list(authority_record.get("forbidden_effects") or []),
            "next_action": _text(authority_record.get("next_action")),
            "does_not_imply": _text(row.get("does_not_imply")),
            "scientific_negative": False, "source": "failure_asset_library",
        })
        if idea_id:
            target = experiment_nodes.get((idea_id, phase)) if phase else ""
            target = target or ensure_idea(idea_id, "failure_asset_library")
            add_edge(node_id, target, f"diagnoses_{failure_class}_failure")

    for row in research_memory_wiki.get("entries") or []:
        if not isinstance(row, dict):
            continue
        memory_id, kind = _text(row.get("memory_id")), _text(row.get("kind"))
        if not memory_id:
            continue
        if kind == "SUCCESS_ASSET":
            node_id = add_node({
                "id": f"success:{memory_id}", "kind": "success",
                "label": _text(row.get("title")) or memory_id,
                "scope": row.get("scope") or "",
                "affected_layer": _text(row.get("affected_layer")),
                "source_refs": list(row.get("source_refs") or []),
                "automatic_generalization": False,
                "source": "research_memory_wiki",
            })
            candidate_id = _text(row.get("candidate_id"))
            if candidate_id:
                claim_target = f"claim:{candidate_id}"
                target = claim_target if claim_target in base_ids or claim_target in overlay_nodes else ensure_idea(candidate_id, "research_memory_wiki")
                add_edge(node_id, target, "records_success_for")
            continue
        if kind not in {"SCIENTIFIC_CLOSURE", "SEARCH_CLOSURE", "HOLD"}:
            continue
        closure_kind = {
            "SCIENTIFIC_CLOSURE": "scientific_closure",
            "SEARCH_CLOSURE": "search_closure",
            "HOLD": "hold",
        }[kind]
        reopen_text = _text(row.get("reopen_condition"))
        reopen_id = add_node({
            "id": f"reopen:{memory_id}", "kind": "reopen_condition",
            "label": reopen_text, "source": "research_memory_wiki",
        })
        object_id, mechanism, claim_type = closure_scope_signature(row)
        closure_id = add_node({
            "id": f"closure:{memory_id}", "kind": closure_kind,
            "label": _text(row.get("title")) or memory_id,
            "scientific_object": object_id, "mechanism": mechanism,
            "claim_type": claim_type, "scope": row.get("scope") or "",
            "affected_layer": _text(row.get("affected_layer")),
            "principle_dead_end_certified": row.get("scientific_dead_end_certified") is True,
            "reopen_condition_id": reopen_id, "source": "research_memory_wiki",
        })
        add_edge(closure_id, reopen_id, "reopens_if")
        candidate_id = _text(row.get("candidate_id"))
        if candidate_id:
            target = f"claim:{candidate_id}"
            if target not in base_ids and target not in overlay_nodes:
                target = ensure_idea(candidate_id, "research_memory_wiki")
            relation = "scientific_closure_for" if closure_kind == "scientific_closure" else "search_control_for"
            add_edge(closure_id, target, relation)


    dead_end_registry = failure_asset_library.get("dead_end_registry") or {}
    for idx, row in enumerate(dead_end_registry.get("certified_principle_dead_ends") or []):
        if not isinstance(row, dict) or row.get("principle_dead_end_certified") is not True:
            continue
        principle_id = _text(row.get("principle_id") or row.get("id"))
        closure_key = _text(row.get("closure_id") or row.get("counter_explanation") or principle_id or str(idx))
        reopen_text = _first_text(row, "reopen_condition", "reopen_only_if") or (
            "New evidence must invalidate the certified counter-explanation within "
            "the same scientific object, mechanism, and claim type."
        )
        reopen_id = add_node({
            "id": f"reopen:principle:{_short_hash(closure_key)}",
            "kind": "reopen_condition", "label": reopen_text,
            "source": "failure_asset_library",
        })
        object_id, mechanism, claim_type = closure_scope_signature(row)
        closure_id = add_node({
            "id": f"closure:principle:{_short_hash(closure_key)}",
            "kind": "scientific_closure",
            "label": _text(row.get("counter_explanation") or row.get("reason")) or closure_key,
            "scientific_object": object_id, "mechanism": mechanism,
            "claim_type": claim_type, "closure_layer": "core_principle",
            "source": "failure_asset_library",
            "principle_dead_end_certified": True,
            "reopen_condition_id": reopen_id,
        })
        add_edge(closure_id, reopen_id, "reopens_if")
        if principle_id:
            target = add_node({
                "id": f"principle:{principle_id}", "kind": "core_principle",
                "label": principle_id, "source": "failure_asset_library",
            })
            add_edge(closure_id, target, "closes_principle")
        closure_node = overlay_nodes.get(closure_id) or {}
        for claim_node in claim_nodes:
            if can_propagate_closure(closure_node, claim_node):
                add_edge(
                    closure_id, _text(claim_node.get("id")), "propagates_closure",
                    propagation_key={
                        "scientific_object": object_id,
                        "mechanism": mechanism,
                        "claim_type": claim_type,
                    },
                )

    conflicts: list[dict[str, Any]] = []
    positive = {"SUPPORTED", "SUPPORTED_NARROWLY"}
    negative = {"REJECTED", "CONTRADICTED", "UNSUPPORTED"}
    for key, rows in claim_groups.items():
        statuses = {_text(row.get("adjudication_status")) for row in rows}
        if statuses & positive and statuses & negative:
            conflicts.append({
                "scientific_object": key[0], "mechanism": key[1],
                "claim_type": key[2], "claim_fingerprint": _short_hash(key[3]),
                "statuses": sorted(statuses),
                "claim_ids": sorted({_text(row.get("claim_id")) for row in rows}),
                "automatic_resolution": False, "scientific_authority": False,
            })

    overlay_kinds = Counter(_text(row.get("kind")) or "unknown" for row in overlay_nodes.values())
    overlay_relations = Counter(_text(row.get("relation")) or "unknown" for row in overlay_edges)
    unified_kinds = base_node_kinds + overlay_kinds
    unified_relations = base_relations + overlay_relations
    pipeline_kinds = (
        "paper", "phenomenon", "problem_contract", "idea", "claim", "method",
        "experiment", "failure_asset", "success", "scientific_closure",
        "reopen_condition",
    )
    typed_coverage = {
        "required_pipeline_kinds": list(pipeline_kinds),
        "materialized_pipeline_kinds": [
            kind for kind in pipeline_kinds if unified_kinds.get(kind, 0) > 0
        ],
        "missing_pipeline_kinds": [
            kind for kind in pipeline_kinds if unified_kinds.get(kind, 0) == 0
        ],
    }
    closure_edges = sum(row.get("relation") == "closes_principle" for row in overlay_edges)
    propagation_edges = sum(row.get("relation") == "propagates_closure" for row in overlay_edges)
    governance_bindings = {
        "schema_version": "1.0",
        "source_state_key": "aris_governance_layer",
        "failure_records_bound": sum(bool(row.get("failure_record_id")) for row in overlay_nodes.values()),
        "experiment_authorizations_bound": sum(bool(row.get("authorization_id")) for row in overlay_nodes.values()),
        "candidate_lineage_bound": sum(bool(row.get("lineage_id")) for row in overlay_nodes.values()),
        "bindings_are_derived_zero_authority": True,
        "scientific_authority": False,
    }
    claim_evidence_bindings = {
        "schema_version": "1.0",
        "source_bundle_sha256": claim_evidence_traceability.get("bundle_sha256"),
        "supported_claims_bound": int((claim_evidence_traceability.get("summary") or {}).get("supported_claims_bound") or 0),
        "causal_holds_bound": int((claim_evidence_traceability.get("summary") or {}).get("causal_holds_bound") or 0),
        "not_supported_claim_boundaries": int((claim_evidence_traceability.get("summary") or {}).get("not_supported_claim_boundaries") or 0),
        "limitations_bound": int((claim_evidence_traceability.get("summary") or {}).get("limitations_bound") or 0),
        "counterevidence_bound": int((claim_evidence_traceability.get("summary") or {}).get("counterevidence_bound") or 0),
        "reopen_conditions_bound": int((claim_evidence_traceability.get("summary") or {}).get("reopen_conditions_bound") or 0),
        "control_designs_bound": int((claim_evidence_traceability.get("summary") or {}).get("control_designs_bound") or 0),
        "authorization_gates_bound": int((claim_evidence_traceability.get("summary") or {}).get("authorization_gates_bound") or 0),
        "bindings_are_derived_zero_authority": True,
        "scientific_authority": False,
    }
    graph = {
        "schema_version": SCHEMA_VERSION,
        "status": "RESEARCH_GRAPH_COMPILED",
        "policy": dict(POLICY),
        "base_graph": {
            "state_key": "evidence_graph", "nodes": len(base_nodes),
            "edges": len(base_edges), "node_ids": sorted(base_ids),
            "referenced_not_duplicated": True,
        },
        "typed_coverage": typed_coverage,
        "claim_conflicts": conflicts,
        "governance_bindings": governance_bindings,
        "claim_evidence_bindings": claim_evidence_bindings,
        "summary": {
            "nodes": len(base_ids | set(overlay_nodes)),
            "edges": len(base_edges) + len(overlay_edges),
            "node_kinds": dict(sorted(unified_kinds.items())),
            "relations": dict(sorted(unified_relations.items())),
            "base_nodes": len(base_nodes), "base_edges": len(base_edges),
            "overlay_nodes": len(overlay_nodes),
            "new_overlay_nodes": len({node_id for node_id in overlay_nodes if node_id not in base_ids}),
            "overlay_edges": len(overlay_edges),
            "candidate_nodes": overlay_kinds.get("candidate_problem", 0),
            "phenomenon_nodes": overlay_kinds.get("phenomenon", 0),
            "problem_contract_nodes": overlay_kinds.get("problem_contract", 0),
            "claim_nodes": unified_kinds.get("claim", 0),
            "method_nodes": overlay_kinds.get("method", 0),
            "experiment_nodes": overlay_kinds.get("experiment", 0),
            "principle_nodes": overlay_kinds.get("core_principle", 0),
            "failure_asset_nodes": overlay_kinds.get("failure_asset", 0),
            "success_nodes": overlay_kinds.get("success", 0),
            "scientific_closure_nodes": overlay_kinds.get("scientific_closure", 0),
            "search_closure_nodes": overlay_kinds.get("search_closure", 0),
            "reopen_condition_nodes": overlay_kinds.get("reopen_condition", 0),
            "limitation_nodes": overlay_kinds.get("limitation", 0),
            "counterevidence_nodes": overlay_kinds.get("counterevidence", 0),
            "control_design_nodes": overlay_kinds.get("control_design", 0),
            "authorization_gate_nodes": overlay_kinds.get("authorization_gate", 0),
            "claim_evidence_traceability_nodes": int((claim_evidence_traceability.get("summary") or {}).get("nodes") or 0),
            "claim_evidence_traceability_edges": int((claim_evidence_traceability.get("summary") or {}).get("edges") or 0),
            "principle_closure_edges": closure_edges,
            "exact_scope_propagation_edges": propagation_edges,
            "claim_conflicts": len(conflicts),
            "failure_governance_bindings": governance_bindings["failure_records_bound"],
            "experiment_authorization_bindings": governance_bindings["experiment_authorizations_bound"],
            "candidate_lineage_bindings": governance_bindings["candidate_lineage_bound"],
            "typed_pipeline_kinds_materialized": len(typed_coverage["materialized_pipeline_kinds"]),
            "typed_pipeline_kinds_required": len(pipeline_kinds),
        },
        "overlay_nodes": sorted(overlay_nodes.values(), key=lambda row: _text(row.get("id"))),
        "overlay_edges": overlay_edges,
        "scientific_authority": False,
    }
    graph["lint"] = lint_scientific_research_graph(graph)
    graph["status"] = (
        "RESEARCH_GRAPH_COMPILED"
        if graph["lint"]["status"] == "PASS"
        else "RESEARCH_GRAPH_INVALID"
    )
    return graph
