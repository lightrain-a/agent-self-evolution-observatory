from __future__ import annotations

import copy
from typing import Any

from .evidence_receipt_current_state import canonical_sha256


SCHEMA_VERSION = "1.0"


def build_claim_evidence_traceability(
    *,
    program_id: str,
    candidate_id: str,
    claim_table: dict[str, Any],
    memory_bundle: dict[str, Any],
    receipt_ref: str,
    control_design: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile explicit zero-authority claim/evidence/boundary traceability."""

    control_design = control_design or {}
    claim_ledger = [
        row for row in memory_bundle.get("claim_ledger") or [] if isinstance(row, dict)
    ]
    if len(claim_ledger) < 2:
        raise ValueError("claim/evidence traceability requires supported and causal-hold claims")
    claim_by_status = {
        str(row.get("adjudication_status") or ""): row for row in claim_ledger
    }
    supported = claim_by_status.get("SUPPORTED_NARROWLY")
    causal_hold = claim_by_status.get("HOLD_METHOD_IDENTIFICATION")
    if not supported or not causal_hold:
        raise ValueError("claim/evidence traceability claim adjudication drift")
    rows = [row for row in claim_table.get("rows") or [] if isinstance(row, dict)]
    if len(rows) != 4:
        raise ValueError("claim/evidence traceability requires the four-row paper boundary")

    supported_id = f"claim:{supported['claim_id']}"
    causal_id = f"claim:{causal_hold['claim_id']}"
    receipt_node_id = f"evidence-receipt:{canonical_sha256(receipt_ref)[:16]}"
    nodes: list[dict[str, Any]] = [
        {
            "id": receipt_node_id,
            "kind": "evidence_reference",
            "label": receipt_ref,
            "evidence_class": "adjudicated_receipt",
            "receipt_ref": receipt_ref,
            "source": "claim_evidence_traceability",
            "scientific_authority": False,
        }
    ]
    edges: list[dict[str, Any]] = [
        {
            "source": receipt_node_id,
            "target": supported_id,
            "relation": "supports_claim",
            "scope": "bounded frozen R9 operationalization",
            "scientific_authority": False,
        },
        {
            "source": receipt_node_id,
            "target": causal_id,
            "relation": "informs_claim_without_identifying",
            "scientific_authority": False,
        },
    ]

    boundary_claim_ids: list[str] = []
    limitation_ids: list[str] = []
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("row_id") or f"ROW-{index}")
        limitation = str(row.get("limitation") or "").strip()
        not_supported = str(row.get("not_supported_claim") or "").strip()
        if not limitation or not not_supported:
            raise ValueError(f"claim table row {row_id} is missing boundary text")
        boundary_id = f"claim-boundary:{program_id}:{index:02d}"
        limitation_id = f"limitation:{program_id}:{index:02d}"
        boundary_claim_ids.append(boundary_id)
        limitation_ids.append(limitation_id)
        nodes.extend(
            [
                {
                    "id": boundary_id,
                    "kind": "claim",
                    "label": not_supported,
                    "claim_id": f"{program_id}-NOT-SUPPORTED-{index:02d}",
                    "claim_type": "paper_claim_boundary",
                    "scientific_object": str(supported.get("scientific_object") or candidate_id),
                    "mechanism": str(supported.get("mechanism") or ""),
                    "adjudication_status": "NOT_SUPPORTED_BY_CURRENT_EVIDENCE",
                    "trace_complete": True,
                    "source": "paper_claim_table",
                    "scientific_authority": False,
                },
                {
                    "id": limitation_id,
                    "kind": "limitation",
                    "label": limitation,
                    "limitation_class": (
                        "method_identification" if index == 1 else
                        "external_validity" if index == 2 else
                        "statistical_scope" if index == 3 else
                        "measurement"
                    ),
                    "row_id": row_id,
                    "source": "paper_claim_table",
                    "scientific_authority": False,
                },
            ]
        )
        target = causal_id if index == 1 else supported_id
        edges.extend(
            [
                {
                    "source": limitation_id,
                    "target": target,
                    "relation": "limits_claim",
                    "scientific_authority": False,
                },
                {
                    "source": limitation_id,
                    "target": boundary_id,
                    "relation": "explains_claim_boundary",
                    "scientific_authority": False,
                },
                {
                    "source": receipt_node_id,
                    "target": boundary_id,
                    "relation": "bounds_out_claim",
                    "scientific_authority": False,
                },
            ]
        )

    counterevidence_nodes = [
        {
            "id": f"counterevidence:{program_id}:update-schedule-confound",
            "kind": "counterevidence",
            "label": (
                "Persistent update and held-out task schedule co-vary in the frozen design, "
                "so the update-alone effect is not identified."
            ),
            "counterevidence_class": "design_confound",
            "affected_layer": "method",
            "source": "evidence_receipt_failure_classification",
            "scientific_authority": False,
        },
        {
            "id": f"counterevidence:{program_id}:evaluator-uncertainty",
            "kind": "counterevidence",
            "label": "HarmBench is a frozen benchmark evaluator, not a noiseless safety oracle.",
            "counterevidence_class": "measurement_boundary",
            "affected_layer": "operationalization",
            "source": "evidence_receipt_failure_classification",
            "scientific_authority": False,
        },
    ]
    nodes.extend(counterevidence_nodes)
    edges.extend(
        [
            {
                "source": counterevidence_nodes[0]["id"],
                "target": causal_id,
                "relation": "challenges_claim",
                "scientific_authority": False,
            },
            {
                "source": counterevidence_nodes[1]["id"],
                "target": supported_id,
                "relation": "limits_measurement_interpretation",
                "scientific_authority": False,
            },
        ]
    )

    reopen = memory_bundle.get("reopen_condition") or {}
    reopen_id = f"reopen-condition:{reopen.get('condition_id')}"
    nodes.append(
        {
            "id": reopen_id,
            "kind": "reopen_condition",
            "label": str(reopen.get("condition") or ""),
            "condition_id": reopen.get("condition_id"),
            "automatic_reopen": False,
            "new_behavior_execution_authorized": False,
            "source": "agent_safety_memory_graph_bundle",
            "scientific_authority": False,
        }
    )
    edges.append(
        {
            "source": causal_id,
            "target": reopen_id,
            "relation": "reopens_if",
            "scientific_authority": False,
        }
    )

    if control_design:
        design_id = f"control-design:{control_design.get('design_id')}"
        gate_id = f"authorization-gate:{control_design.get('design_id')}"
        gate = control_design.get("authorization_gate") or {}
        nodes.extend(
            [
                {
                    "id": design_id,
                    "kind": "control_design",
                    "label": str(control_design.get("scientific_question") or ""),
                    "design_sha256": control_design.get("design_sha256"),
                    "status": control_design.get("status"),
                    "execution_authorized": False,
                    "source": "agent_safety_reopen_control_design",
                    "scientific_authority": False,
                },
                {
                    "id": gate_id,
                    "kind": "authorization_gate",
                    "label": "R9 same-schedule no-update control authorization gate",
                    "passed": int(gate.get("passed") or 0),
                    "holds": int(gate.get("holds") or 0),
                    "automatic_authorization": False,
                    "execution_authorized": False,
                    "gpu_authorized": False,
                    "source": "agent_safety_reopen_control_design",
                    "scientific_authority": False,
                },
            ]
        )
        edges.extend(
            [
                {
                    "source": design_id,
                    "target": causal_id,
                    "relation": "tests_identification_for",
                    "scientific_authority": False,
                },
                {
                    "source": gate_id,
                    "target": design_id,
                    "relation": "gates_control_design",
                    "scientific_authority": False,
                },
                {
                    "source": design_id,
                    "target": reopen_id,
                    "relation": "addresses_reopen_condition",
                    "scientific_authority": False,
                },
            ]
        )

    bundle = {
        "schema_version": SCHEMA_VERSION,
        "status": "CLAIM_EVIDENCE_TRACEABILITY_COMPILED",
        "program_id": program_id,
        "candidate_id": candidate_id,
        "receipt_ref": receipt_ref,
        "claim_table_sha256": claim_table.get("table_sha256"),
        "memory_bundle_sha256": memory_bundle.get("bundle_sha256"),
        "control_design_sha256": control_design.get("design_sha256"),
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "supported_claims_bound": 1,
            "causal_holds_bound": 1,
            "not_supported_claim_boundaries": len(boundary_claim_ids),
            "limitations_bound": len(limitation_ids),
            "counterevidence_bound": len(counterevidence_nodes),
            "reopen_conditions_bound": 1,
            "control_designs_bound": 1 if control_design else 0,
            "authorization_gates_bound": 1 if control_design else 0,
            "nodes": len(nodes),
            "edges": len(edges),
        },
        "scientific_authority": False,
    }
    bundle["bundle_sha256"] = canonical_sha256(
        {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    )
    errors = validate_claim_evidence_traceability(bundle)
    if errors:
        raise ValueError("invalid claim/evidence traceability: " + "; ".join(errors))
    return bundle


def validate_claim_evidence_traceability(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if bundle.get("status") != "CLAIM_EVIDENCE_TRACEABILITY_COMPILED":
        errors.append("claim/evidence traceability status drift")
    nodes = [row for row in bundle.get("nodes") or [] if isinstance(row, dict)]
    edges = [row for row in bundle.get("edges") or [] if isinstance(row, dict)]
    ids = [str(row.get("id") or "") for row in nodes]
    if not ids or len(ids) != len(set(ids)):
        errors.append("claim/evidence traceability node identity drift")
    allowed_external_targets = {
        edge["target"]
        for edge in edges
        if str(edge.get("target") or "").startswith("claim:")
    }
    known = set(ids) | allowed_external_targets
    for node in nodes:
        if node.get("scientific_authority") is not False:
            errors.append(f"claim/evidence node authority leak: {node.get('id')}")
        if node.get("kind") in {"control_design", "authorization_gate"}:
            if node.get("execution_authorized") is not False:
                errors.append(f"control traceability node execution leak: {node.get('id')}")
    for edge in edges:
        if edge.get("source") not in known or edge.get("target") not in known:
            errors.append("claim/evidence traceability edge endpoint missing")
        if edge.get("scientific_authority") is not False:
            errors.append("claim/evidence traceability edge authority leak")
    summary = bundle.get("summary") or {}
    if (
        summary.get("supported_claims_bound") != 1
        or summary.get("causal_holds_bound") != 1
        or summary.get("not_supported_claim_boundaries") != 4
        or summary.get("limitations_bound") != 4
        or summary.get("counterevidence_bound") != 2
        or summary.get("reopen_conditions_bound") != 1
    ):
        errors.append("claim/evidence traceability summary drift")
    expected_hash = canonical_sha256(
        {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    )
    if bundle.get("bundle_sha256") != expected_hash:
        errors.append("claim/evidence traceability hash drift")
    return errors


def copy_traceability_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(bundle)
