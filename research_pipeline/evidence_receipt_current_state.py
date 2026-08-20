from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


SCHEMA_VERSION = "1.0"
CANONICAL_FAILURE_LAYERS = (
    "runtime",
    "protocol",
    "support",
    "operationalization",
    "method",
    "principle",
)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _path(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"receipt path is missing: {dotted_path}")
        current = current[part]
    return current


def _coerce(value: Any, kind: str, dotted_path: str) -> Any:
    if kind == "int":
        if isinstance(value, bool):
            raise ValueError(f"boolean is not an integer evidence value: {dotted_path}")
        return int(value)
    if kind == "float":
        if isinstance(value, bool):
            raise ValueError(f"boolean is not a float evidence value: {dotted_path}")
        return float(value)
    if kind == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"evidence value must be boolean: {dotted_path}")
        return value
    if kind == "str":
        result = str(value or "").strip()
        if not result:
            raise ValueError(f"evidence value must be non-empty text: {dotted_path}")
        return result
    if kind == "list":
        if not isinstance(value, list):
            raise ValueError(f"evidence value must be a list: {dotted_path}")
        return copy.deepcopy(value)
    if kind == "dict":
        if not isinstance(value, dict):
            raise ValueError(f"evidence value must be an object: {dotted_path}")
        return copy.deepcopy(value)
    raise ValueError(f"unsupported evidence coercion {kind!r}: {dotted_path}")


def _validate_spec(spec: dict[str, Any]) -> None:
    required_text = (
        "projection_id",
        "program_id",
        "candidate_id",
        "receipt_status",
        "current_stage",
        "candidate_stage",
        "receipt_candidate_path",
    )
    for key in required_text:
        if not str(spec.get(key) or "").strip():
            raise ValueError(f"receipt projection spec is missing {key}")
    if not isinstance(spec.get("required_flags"), dict):
        raise ValueError("receipt projection spec required_flags must be an object")
    if not isinstance(spec.get("evidence_blocks"), dict) or not spec["evidence_blocks"]:
        raise ValueError("receipt projection spec requires evidence_blocks")
    claims = spec.get("claim_scope") or {}
    for key in ("supported_path", "not_supported_path", "limitation"):
        if not str(claims.get(key) or "").strip():
            raise ValueError(f"receipt projection claim_scope is missing {key}")
    denials = spec.get("authority_denials")
    if not isinstance(denials, list) or not denials:
        raise ValueError("receipt projection spec requires explicit authority_denials")


def compile_evidence_receipt_projection(
    receipt: dict[str, Any],
    *,
    spec: dict[str, Any],
    receipt_ref: str,
    dependency_refs: dict[str, str],
    reopen_condition: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    """Compile one zero-authority current-state projection from an evidence receipt.

    The compiler is intentionally domain-neutral. Domain adapters provide a declarative
    projection spec and retain responsibility for domain-specific scientific checks.
    """

    _validate_spec(spec)
    if not isinstance(receipt, dict):
        raise ValueError("evidence receipt must be an object")
    if receipt.get("status") != spec["receipt_status"]:
        raise ValueError("evidence receipt status does not match projection spec")
    candidate_id = str(_path(receipt, spec["receipt_candidate_path"]) or "")
    if candidate_id != spec["candidate_id"]:
        raise ValueError("evidence receipt candidate identity does not match projection spec")
    for dotted_path, expected in spec["required_flags"].items():
        if _path(receipt, dotted_path) != expected:
            raise ValueError(f"evidence receipt requirement failed: {dotted_path}")

    failure_layers_path = str(spec.get("failure_layers_path") or "failure_classification")
    failure_layers = _path(receipt, failure_layers_path)
    if not isinstance(failure_layers, dict):
        raise ValueError("evidence receipt failure classification must be an object")
    if tuple(failure_layers) != CANONICAL_FAILURE_LAYERS:
        raise ValueError("evidence receipt must expose the canonical six failure layers in order")
    if not all(isinstance(failure_layers[key], list) for key in CANONICAL_FAILURE_LAYERS):
        raise ValueError("every canonical failure-layer payload must be a list")

    evidence_blocks: dict[str, dict[str, Any]] = {}
    for block_name, fields in spec["evidence_blocks"].items():
        if not isinstance(fields, dict) or not fields:
            raise ValueError(f"evidence block {block_name} must contain field mappings")
        block: dict[str, Any] = {}
        for output_name, mapping in fields.items():
            if isinstance(mapping, str):
                dotted_path, kind = mapping, "str"
            elif isinstance(mapping, dict):
                dotted_path = str(mapping.get("path") or "")
                kind = str(mapping.get("type") or "str")
            else:
                raise ValueError(f"invalid field mapping in evidence block {block_name}")
            block[output_name] = _coerce(_path(receipt, dotted_path), kind, dotted_path)
        evidence_blocks[str(block_name)] = block

    claim_spec = spec["claim_scope"]
    supported_claim = str(_path(receipt, claim_spec["supported_path"]) or "").strip()
    not_supported_claims = _path(receipt, claim_spec["not_supported_path"])
    if not supported_claim or not isinstance(not_supported_claims, list):
        raise ValueError("evidence receipt claim boundary is incomplete")
    not_supported_claims = [str(value).strip() for value in not_supported_claims]
    if not all(not_supported_claims):
        raise ValueError("not-supported claim boundary contains empty text")
    expected_count = int(claim_spec.get("expected_not_supported_count") or 0)
    if expected_count and len(not_supported_claims) != expected_count:
        raise ValueError("not-supported claim boundary cardinality drift")

    if (
        reopen_condition.get("automatic_reopen") is not False
        or reopen_condition.get("new_behavior_execution_authorized") is not False
        or reopen_condition.get("scientific_authority") is not False
    ):
        raise ValueError("reopen condition must be fail-closed and zero-authority")
    if not str(reopen_condition.get("condition") or "").strip():
        raise ValueError("reopen condition text is missing")

    authority = {str(key): False for key in spec["authority_denials"]}
    projection = {
        "schema_version": SCHEMA_VERSION,
        "projection_id": spec["projection_id"],
        "program_id": spec["program_id"],
        "candidate_id": candidate_id,
        "current_stage": spec["current_stage"],
        "candidate_stage": spec["candidate_stage"],
        "status": receipt["status"],
        "receipt_ref": receipt_ref,
        "generated_at": generated_at,
        "paper_evidence_ready": bool(
            _path(receipt, str(spec.get("paper_evidence_ready_path") or "paper_evidence_ready"))
        ),
        "claim_boundary": {
            "supported_claim": supported_claim,
            "not_supported_claims": not_supported_claims,
            "limitation": str(claim_spec["limitation"]),
        },
        "evidence_blocks": evidence_blocks,
        "failure_classification": copy.deepcopy(failure_layers),
        "reopen_condition": copy.deepcopy(reopen_condition),
        "authority": authority,
        "execution_authorized": False,
        "scientific_authority": False,
    }
    compiler_receipt = {
        "schema_version": SCHEMA_VERSION,
        "compiler": "generic-evidence-receipt-current-state",
        "projection_spec_sha256": canonical_sha256(spec),
        "source_receipt_sha256": canonical_sha256(receipt),
        "source_receipt_ref": receipt_ref,
        "dependency_refs": dict(sorted(dependency_refs.items())),
        "domain_adapter_required_for_scientific_validation": True,
        "automatic_stage_transition": False,
        "automatic_reopen": False,
        "execution_authorized": False,
        "scientific_authority": False,
    }
    projection["compiler_receipt"] = compiler_receipt
    projection["projection_payload_sha256"] = canonical_sha256(projection)
    errors = validate_evidence_receipt_projection(projection, spec=spec)
    if errors:
        raise ValueError("invalid evidence receipt projection: " + "; ".join(errors))
    return projection


def validate_evidence_receipt_projection(
    projection: dict[str, Any], *, spec: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if projection.get("schema_version") != SCHEMA_VERSION:
        errors.append("generic receipt projection schema drift")
    for key in ("projection_id", "program_id", "candidate_id", "current_stage", "candidate_stage"):
        if projection.get(key) != spec.get(key):
            errors.append(f"generic receipt projection {key} drift")
    if projection.get("status") != spec.get("receipt_status"):
        errors.append("generic receipt projection source status drift")
    if projection.get("paper_evidence_ready") is not True:
        errors.append("generic receipt projection paper evidence is not ready")
    if tuple((projection.get("failure_classification") or {}).keys()) != CANONICAL_FAILURE_LAYERS:
        errors.append("generic receipt projection lost canonical failure layers")
    authority = projection.get("authority") or {}
    if set(authority) != {str(key) for key in spec.get("authority_denials") or []}:
        errors.append("generic receipt projection authority surface drift")
    if projection.get("execution_authorized") is not False or any(
        value is not False for value in authority.values()
    ):
        errors.append("generic receipt projection leaked execution authority")
    reopen = projection.get("reopen_condition") or {}
    if (
        reopen.get("automatic_reopen") is not False
        or reopen.get("new_behavior_execution_authorized") is not False
        or reopen.get("scientific_authority") is not False
    ):
        errors.append("generic receipt projection reopen condition is not fail-closed")
    compiler = projection.get("compiler_receipt") or {}
    if (
        compiler.get("compiler") != "generic-evidence-receipt-current-state"
        or compiler.get("automatic_stage_transition") is not False
        or compiler.get("execution_authorized") is not False
        or compiler.get("scientific_authority") is not False
    ):
        errors.append("generic receipt compiler receipt is incomplete")
    expected_hash = canonical_sha256(
        {key: value for key, value in projection.items() if key != "projection_payload_sha256"}
    )
    if projection.get("projection_payload_sha256") != expected_hash:
        errors.append("generic receipt projection payload hash drift")
    return errors
