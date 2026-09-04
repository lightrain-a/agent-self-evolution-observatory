from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from research_pipeline.e2_r17_m3r4_execution_plan import (
    MAX_OUTPUT_TOKENS,
    MAX_TURNS,
    PROVIDER_RETRY_LIMIT,
    REQUESTED_MODEL,
    REQUIRED_RESOLVED_MODEL,
    TASK_IDS,
    sha256_file,
    structural_provider_budget,
    validate_state_bindings,
)


DRAFT_STATUS = "HOLD_FRESH_MODEL_IDENTITY_REQUALIFICATION_REQUIRED_ZERO_PROVIDER_PREP_ONLY"
FINAL_CONTRACT_STATUS = "FROZEN_E2_R17_M3R4_EXECUTION"
PREFLIGHT_AUTH_STATUS = "PREFLIGHT_ONLY_E2_R17_M3R4_EXECUTION"
MEASUREMENT_AUTH_STATUS = "AUTHORIZED_E2_R17_M3R4_ACTOR_MEASUREMENT_ONLY"
FRESH_IDENTITY_STATUS = "PASS_M3R4_SCIENTIFIC_TRANCHE_MODEL_IDENTITY"
PLAN_ROUTE = "https://ark.cn-beijing.volces.com/api/plan/v3"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_zero_provider_draft(contract_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    require(contract.get("status") == DRAFT_STATUS, "M3R4 draft status drift")
    authority = contract.get("authority") or {}
    require(bool(authority) and all(value is False for value in authority.values()), "M3R4 draft must have zero authority")
    identity_gate = contract.get("fresh_model_identity_gate") or {}
    require(identity_gate.get("required_before_final_contract") is True, "M3R4 fresh identity gate missing")
    require(identity_gate.get("historical_identity_reusable_for_m3r4") is False, "historical identity must be non-reusable")
    require(identity_gate.get("fresh_identity_artifact") is None, "draft must not already contain a fresh identity")
    require(identity_gate.get("fresh_identity_sha256") is None, "draft must not already contain a fresh identity SHA")
    require(identity_gate.get("requested_model_must_remain") == REQUESTED_MODEL, "draft requested-model target drift")
    require(identity_gate.get("resolved_model_must_remain") == REQUIRED_RESOLVED_MODEL, "draft resolved-model target drift")
    require(identity_gate.get("route_must_remain") == PLAN_ROUTE, "draft Ark route target drift")
    require(int(identity_gate.get("provider_retry_limit_must_remain", -1)) == PROVIDER_RETRY_LIMIT, "draft retry target drift")
    require(int(identity_gate.get("max_output_tokens_smoke", -1)) == MAX_OUTPUT_TOKENS, "draft identity smoke output limit drift")
    order = contract.get("logical_unit_order") or {}
    order_path = Path(__file__).resolve().parents[1] / str(order.get("path") or "")
    require(order_path.is_file() and sha256_file(order_path) == order.get("sha256"), "draft logical-unit order binding drift")
    order_payload = load_json(order_path)
    require(int(order_payload.get("unit_count", -1)) == 72, "draft logical unit count drift")
    require(set(row["task_id"] for row in order_payload.get("logical_units") or []) == set(TASK_IDS), "draft task set drift")
    budget = contract.get("provider_budget") or {}
    expected_budget = structural_provider_budget()
    require(budget == expected_budget, "draft structural provider budget drift")
    validate_state_bindings()
    require(not Path(str(contract.get("run_root") or "")).exists(), "draft zero-provider preflight requires absent run root")
    require(not Path(str(contract.get("lineage_lease_path") or "")).exists(), "draft zero-provider preflight requires absent lineage lease")
    return contract


def validate_fresh_identity(identity: Mapping[str, Any], draft: Mapping[str, Any]) -> None:
    """Validate a future M3R4-specific identity qualification artifact.

    No current artifact is expected to pass this function before quota/resource
    gates open.  The dedicated status prevents an older review-tranche identity
    from being reused merely because requested/resolved strings happen to match.
    """

    require(identity.get("status") == FRESH_IDENTITY_STATUS, "fresh M3R4 identity status missing")
    require(identity.get("route") == PLAN_ROUTE, "fresh M3R4 identity route drift")
    row = (identity.get("requested_and_resolved") or {}).get(REQUESTED_MODEL) or {}
    require(row.get("requested") == REQUESTED_MODEL, "fresh M3R4 requested model drift")
    require(row.get("resolved") == REQUIRED_RESOLVED_MODEL, "fresh M3R4 resolved model drift")
    require(row.get("thinking_requested") == "disabled", "fresh M3R4 thinking drift")
    require(int(identity.get("provider_retry_limit", -1)) == PROVIDER_RETRY_LIMIT, "fresh M3R4 retry drift")
    require(int(identity.get("max_output_tokens_smoke", -1)) == MAX_OUTPUT_TOKENS, "fresh M3R4 output-token smoke drift")
    require(identity.get("scientific_tranche") == "E2-R17-M3R4", "fresh identity tranche binding drift")
    require(identity.get("scientific_experiment") is False, "model identity qualification must remain non-scientific")
    draft_gate = draft.get("fresh_model_identity_gate") or {}
    require(draft_gate.get("requested_model_must_remain") == row.get("requested"), "fresh identity requested-model mismatch to draft")
    require(draft_gate.get("resolved_model_must_remain") == row.get("resolved"), "fresh identity resolved-model mismatch to draft")


def validate_final_contract(contract_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    require(contract.get("status") == FINAL_CONTRACT_STATUS, "M3R4 scientific runner requires final frozen contract")
    identity = contract.get("fresh_model_identity") or {}
    identity_path = Path(str(identity.get("path") or ""))
    if not identity_path.is_absolute():
        identity_path = Path(__file__).resolve().parents[1] / identity_path
    require(identity_path.is_file(), "M3R4 final contract missing fresh identity artifact")
    require(sha256_file(identity_path) == identity.get("sha256"), "M3R4 final identity content-address drift")
    validate_fresh_identity(load_json(identity_path), contract)
    require((contract.get("authority") or {}).get("provider_io") is False, "final contract itself must not grant provider authority")
    require(int((contract.get("scientific_scope") or {}).get("logical_units", -1)) == 72, "M3R4 final contract unit count drift")
    require((contract.get("provider_budget") or {}) == structural_provider_budget(), "M3R4 final contract budget drift")
    return contract


def validate_execution_authorization(
    *,
    contract_path: Path,
    authorization_path: Path,
    stop_before_provider_io: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail-closed authorization gate for both future actual-path preflight and execution."""

    contract = validate_final_contract(contract_path)
    authorization = load_json(authorization_path)
    require(authorization.get("contract_sha256") == sha256_file(contract_path), "M3R4 authorization/contract SHA drift")
    status = authorization.get("status")
    require(status in {PREFLIGHT_AUTH_STATUS, MEASUREMENT_AUTH_STATUS}, "invalid M3R4 authorization status")
    authority = authorization.get("authority") or {}
    if status == PREFLIGHT_AUTH_STATUS:
        require(stop_before_provider_io, "M3R4 preflight authorization can never reach provider I/O")
        require(authority.get("scientific_experiment") is False, "M3R4 preflight must be non-scientific")
        require(authority.get("provider_io") is False, "M3R4 preflight provider authority must be false")
    else:
        require(not stop_before_provider_io, "scientific authorization should not be passed to a preflight-only invocation")
        require(authority.get("scientific_experiment") is True, "M3R4 measurement scientific authority missing")
        require(authority.get("provider_io") is True, "M3R4 measurement provider authority missing")
    require(authority.get("actor_measurement") is (status == MEASUREMENT_AUTH_STATUS), "M3R4 actor authority bit drift")
    require(authority.get("updater") is False, "M3R4 updater authority must be false")
    require(authority.get("analysis") is False, "M3R4 analysis authority must be false during measurement")
    scope = authorization.get("execution_scope") or {}
    require(scope.get("scientific_object") == contract.get("scientific_object"), "M3R4 scientific object drift")
    require(scope.get("allowed_task_ids") == list(TASK_IDS), "M3R4 authorization task order/set drift")
    require(scope.get("state_ids") == ["ff_r1", "ff_r2"], "M3R4 authorization state set drift")
    require(scope.get("actor_replicates") == [1, 2], "M3R4 actor replicate scope drift")
    require(int(scope.get("logical_units", -1)) == 72, "M3R4 authorization unit count drift")
    require(scope.get("completed_unit_replay") is False, "M3R4 authorization must forbid completed-unit replay")
    require(scope.get("automatic_retry") is False, "M3R4 authorization must forbid automatic retry")
    require(scope.get("partial_effect_read") is False, "M3R4 authorization must forbid partial effect reads")
    require(scope.get("required_resolved_model") == REQUIRED_RESOLVED_MODEL, "M3R4 authorization resolved model drift")
    require(int(scope.get("max_turns", -1)) == MAX_TURNS, "M3R4 authorization max turns drift")
    require(int(scope.get("max_output_tokens", -1)) == MAX_OUTPUT_TOKENS, "M3R4 authorization output tokens drift")
    require((scope.get("provider_budget") or {}) == structural_provider_budget(), "M3R4 authorization provider budget drift")
    return contract, authorization


__all__ = [
    "DRAFT_STATUS",
    "FINAL_CONTRACT_STATUS",
    "PREFLIGHT_AUTH_STATUS",
    "MEASUREMENT_AUTH_STATUS",
    "FRESH_IDENTITY_STATUS",
    "PLAN_ROUTE",
    "load_json",
    "validate_zero_provider_draft",
    "validate_fresh_identity",
    "validate_final_contract",
    "validate_execution_authorization",
]
