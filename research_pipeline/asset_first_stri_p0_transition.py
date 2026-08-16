from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "STRI"
CANDIDATE_ID = "skill-taxonomy-representation-invariance"
P0A_EXPERIMENT_ID = "ASSET-FIRST-STRI-QWEN3-MERGE-SPLIT-P0A-20260816"
P0B_EXPERIMENT_ID = "ASSET-FIRST-STRI-QUOTIENT-REJECTION-P0B-20260816"
P0C_EXPERIMENT_ID = "ASSET-FIRST-STRI-QWEN3-SOLVER-CONSEQUENCE-P0C-20260816"
P0A_GO = "DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED"
P0A_STOP = "STOP_DYNAMIC_PARTIAL_OVERLAP_PROPAGATION_GATE_NOT_MET"
P0A_INCONCLUSIVE = {
    "INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY",
    "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED",
    "INCONCLUSIVE_BUDGET_EXCEEDED",
}
P0B_PASS = "QUOTIENT_REJECTION_LOCAL_FEASIBILITY_PASS"
P0B_STOP = "STOP_QUOTIENT_REJECTION_LOCAL_FEASIBILITY"
P0B_INVALID = "INVALID_P0B_INPUT_BINDING"
P0C_VALID = {
    "STRONG_ONE_STEP_SOLVER_CONSEQUENCE",
    "PARTIAL_ONE_STEP_SOLVER_CONSEQUENCE",
    "STOP_ONE_STEP_UTILITY_CONSEQUENCE",
}
P0C_INVALID = {
    "INVALID_P0C_INPUT_BINDING",
    "INVALID_P0C_REPARSE_QUALIFICATION_FAILED",
    "INVALID_P0C_BUDGET_EXCEEDED",
}
AUTHORITY = {
    "paper_claim_C3": False,
    "paper_claim_C4_end_of_evolution": False,
    "method": False,
    "p0": False,
    "full_experiment": False,
    "gpu": False,
    "second_backbone": False,
}


def load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt_identity_errors(receipt: dict[str, Any], *, experiment_id: str) -> list[str]:
    errors: list[str] = []
    if str(receipt.get("candidate_id") or "") != CANDIDATE_ID:
        errors.append("candidate-id-mismatch")
    if str(receipt.get("experiment_id") or "") != experiment_id:
        errors.append("experiment-id-mismatch")
    if receipt.get("scientific_authority") is not False:
        errors.append("receipt-scientific-authority-not-false")
    return errors


def _p0a_state(p0a: dict[str, Any] | None) -> dict[str, Any]:
    if p0a is None:
        return {"present": False, "valid_identity": False, "decision": "", "protocol_valid": False, "raw_sha256": "", "errors": []}
    errors = _receipt_identity_errors(p0a, experiment_id=P0A_EXPERIMENT_ID)
    decision = str(p0a.get("decision") or "")
    raw_sha = str(p0a.get("raw_sha256") or "")
    if decision == P0A_GO or decision == P0A_STOP or decision == "INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY":
        if p0a.get("protocol_valid_for_scientific_update") is not True:
            errors.append("qualified-p0a-missing-protocol-validity")
    if decision in {"INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED", "INCONCLUSIVE_BUDGET_EXCEEDED"}:
        if p0a.get("protocol_valid_for_scientific_update") is True:
            errors.append("invalid-p0a-cannot-be-protocol-valid")
    if decision == P0A_GO and len(raw_sha) != 64:
        errors.append("p0a-go-missing-raw-sha")
    return {
        "present": True,
        "valid_identity": not _receipt_identity_errors(p0a, experiment_id=P0A_EXPERIMENT_ID),
        "decision": decision,
        "protocol_valid": p0a.get("protocol_valid_for_scientific_update") is True,
        "raw_sha256": raw_sha,
        "scientific_result_available": p0a.get("scientific_result_available") is True,
        "errors": sorted(set(errors)),
    }


def _p0b_state(p0b: dict[str, Any] | None, p0a_state: dict[str, Any]) -> dict[str, Any]:
    if p0b is None:
        return {"present": False, "decision": "", "input_bound_to_p0a": False, "errors": []}
    errors = _receipt_identity_errors(p0b, experiment_id=P0B_EXPERIMENT_ID)
    decision = str(p0b.get("decision") or "")
    input_validation = p0b.get("input_validation") or {}
    p0b_raw_sha = str(input_validation.get("actual_raw_sha256") or "") if isinstance(input_validation, dict) else ""
    p0a_raw_sha = str(p0a_state.get("raw_sha256") or "")
    bound = bool(p0a_raw_sha and p0b_raw_sha == p0a_raw_sha)
    if decision in {P0B_PASS, P0B_STOP}:
        if not bound:
            errors.append("p0b-raw-sha-not-bound-to-p0a")
        if p0b.get("scientific_result_available") is not True:
            errors.append("p0b-scientific-result-not-available")
        if p0b.get("new_model_calls") != 0 or p0b.get("new_gpu_hours") not in {0, 0.0}:
            errors.append("p0b-must-use-zero-new-model-compute")
    if decision == P0B_INVALID and p0b.get("scientific_result_available") is True:
        errors.append("invalid-p0b-cannot-be-scientific-result")
    return {
        "present": True,
        "decision": decision,
        "input_bound_to_p0a": bound,
        "p0a_raw_sha256": p0a_raw_sha,
        "p0b_raw_sha256": p0b_raw_sha,
        "errors": sorted(set(errors)),
    }


def _p0c_state(p0c: dict[str, Any] | None, p0a_state: dict[str, Any]) -> dict[str, Any]:
    if p0c is None:
        return {"present": False, "decision": "", "secondary_only": True, "input_bound_to_p0a": False, "errors": []}
    errors = _receipt_identity_errors(p0c, experiment_id=P0C_EXPERIMENT_ID)
    decision = str(p0c.get("decision") or "")
    p0c_raw_sha = str(p0c.get("p0a_raw_sha256") or "")
    p0a_raw_sha = str(p0a_state.get("raw_sha256") or "")
    bound = bool(p0a_raw_sha and p0c_raw_sha == p0a_raw_sha)
    if decision in P0C_VALID:
        if not bound:
            errors.append("p0c-raw-sha-not-bound-to-p0a")
        if p0c.get("scientific_result_available") is not True:
            errors.append("valid-p0c-scientific-result-not-available")
        if p0c.get("protocol_valid_for_scientific_update") is not True:
            errors.append("valid-p0c-protocol-not-valid")
    if decision in P0C_INVALID and p0c.get("scientific_result_available") is True:
        errors.append("invalid-p0c-cannot-be-scientific-result")
    return {
        "present": True,
        "decision": decision,
        "secondary_only": True,
        "input_bound_to_p0a": bound,
        "p0a_raw_sha256": p0a_raw_sha,
        "p0c_raw_sha256": p0c_raw_sha,
        "errors": sorted(set(errors)),
    }


def compile_transition(*, p0a: dict[str, Any] | None, p0b: dict[str, Any] | None = None, p0c: dict[str, Any] | None = None) -> dict[str, Any]:
    a = _p0a_state(p0a)
    b = _p0b_state(p0b, a)
    c = _p0c_state(p0c, a)
    all_errors = [f"p0a:{e}" for e in a["errors"]] + [f"p0b:{e}" for e in b["errors"]] + [f"p0c:{e}" for e in c["errors"]]

    status = "WAIT_P0A_RESULT"
    allowed: list[str] = []
    c4_realized_task_state = "LOCKED_PENDING_P0A"
    p0b_state = "LOCKED_PENDING_P0A"
    full_state = "LOCKED"
    primary_stop_reason = ""

    if a["present"]:
        if a["errors"]:
            status = "HOLD_P0A_RECEIPT_INVALID_NO_BELIEF_UPDATE"
            primary_stop_reason = "P0-A receipt identity/protocol binding is invalid."
        elif a["decision"] in {"INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED", "INCONCLUSIVE_BUDGET_EXCEEDED"}:
            status = "HOLD_P0A_INVALID_OR_BUDGET_NO_BELIEF_UPDATE"
            primary_stop_reason = "P0-A did not produce a qualified scientific result; no automatic retry or repair is authorized."
        elif a["decision"] == "INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY":
            status = "HOLD_P0A_INCONCLUSIVE_NO_ADAPTIVE_EXTRA_GENERATION"
            c4_realized_task_state = "INCONCLUSIVE_ONE_WITNESS_ONLY"
            primary_stop_reason = "Exactly one mandatory-overlap witness passed; do not add generations, retune thresholds, or switch backbone."
        elif a["decision"] == P0A_STOP:
            status = "STOP_DYNAMIC_PROPAGATION_ON_PREREGISTERED_BACKBONE"
            c4_realized_task_state = "STOPPED_BY_QUALIFIED_P0A"
            p0b_state = "DISABLED_P0A_STOP"
            full_state = "DISABLED_P0A_STOP"
            primary_stop_reason = "Qualified P0-A found neither mandatory-overlap dynamic propagation witness."
        elif a["decision"] == P0A_GO:
            c4_realized_task_state = "SUPPORTED_REALIZED_TASK_DISTRIBUTION_ONLY_NOT_END_OF_EVOLUTION"
            if not b["present"]:
                status = "P0A_GO_P0B_READY_FOR_SEPARATE_GOVERNED_EXECUTION"
                p0b_state = "ELIGIBLE_INPUTS_REQUIRE_MANUAL_EXECUTION_GATE"
                allowed = ["RUN_FROZEN_P0B_ZERO_NEW_MODEL_CALLS", "OPTIONAL_RUN_FROZEN_P0C_SECONDARY"]
            elif b["errors"] or b["decision"] == P0B_INVALID:
                status = "HOLD_P0B_INVALID_NO_BELIEF_UPDATE"
                p0b_state = "INVALID"
                primary_stop_reason = "P0-B input/provenance binding is invalid; P0-C cannot rescue it."
                if not c["present"]:
                    allowed = ["OPTIONAL_RUN_FROZEN_P0C_SECONDARY"]
            elif b["decision"] == P0B_STOP:
                status = "STOP_CURRENT_SQC_REALIZATION_P0B_FEASIBILITY_FAILED"
                p0b_state = "STOPPED"
                full_state = "DISABLED_P0B_STOP"
                primary_stop_reason = "Frozen quotient/rejection realization could not realize all five atoms within the matched source-call budget."
            elif b["decision"] == P0B_PASS:
                status = "P0A_P0B_PASS_FULL_REMAINS_GOVERNANCE_LOCKED"
                p0b_state = "LOCAL_FEASIBILITY_SUPPORTED"
                full_state = "BLUEPRINT_ELIGIBLE_BUT_NOT_AUTHORIZED"
                allowed = ["REQUEST_GOVERNED_FULL_EXPERIMENT_AUTHORITY"]
                if not c["present"]:
                    allowed.append("OPTIONAL_RUN_FROZEN_P0C_SECONDARY")
            else:
                status = "HOLD_UNKNOWN_P0B_DECISION"
                p0b_state = "UNKNOWN"
                primary_stop_reason = f"Unrecognized P0-B decision: {b['decision']}"
        else:
            status = "HOLD_UNKNOWN_P0A_DECISION"
            primary_stop_reason = f"Unrecognized P0-A decision: {a['decision']}"

    # P0-C is always secondary. It may annotate one-step utility evidence but can never
    # promote, rescue, or override the primary P0-A/P0-B progression state.
    p0c_annotation = "NOT_RUN"
    if c["present"]:
        if c["errors"] or c["decision"] in P0C_INVALID:
            p0c_annotation = "INVALID_SECONDARY_NO_BELIEF_UPDATE"
        elif c["decision"] in P0C_VALID:
            p0c_annotation = c["decision"]
        else:
            p0c_annotation = "UNKNOWN_SECONDARY_DECISION"

    if all_errors:
        # Primary valid STOPs remain STOPs; secondary errors are annotations only. But an
        # error in a receipt that is required for current progression prevents promotion.
        if status == "P0A_P0B_PASS_FULL_REMAINS_GOVERNANCE_LOCKED" and b["errors"]:
            status = "HOLD_P0B_INVALID_NO_BELIEF_UPDATE"
            full_state = "LOCKED"
            allowed = []

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "candidate_id": CANDIDATE_ID,
        "stage": "ZERO_AUTHORITY_P0_TRANSITION_COMPILER",
        "status": status,
        "receipts": {"p0a": a, "p0b": b, "p0c": c},
        "claim_state": {
            "C1_control_plane_representation_sensitivity": "SUPPORTED_PRE_P0",
            "C2_structural_package_only_residual": "SUPPORTED_PRE_P0",
            "C3_sqc_method_claim": "LOCKED_UNTIL_FULL_PRIMARY_GATES",
            "C4_realized_task_propagation": c4_realized_task_state,
            "C4_end_of_evolution_or_utility": "LOCKED_UNTIL_P0C_OR_FULL_WITH_CLAIM_SCOPE_REVIEW",
        },
        "p0b_state": p0b_state,
        "p0c_annotation": p0c_annotation,
        "full_experiment_state": full_state,
        "allowed_next_actions": allowed,
        "primary_stop_reason": primary_stop_reason,
        "policy": {
            "p0c_is_secondary_and_cannot_rescue_p0a_or_p0b": True,
            "p0a_stop_disables_p0b_p0c_as_primary_rescue_and_full": True,
            "p0a_inconclusive_forbids_adaptive_extra_generation_threshold_change_or_second_backbone": True,
            "p0b_requires_p0a_go_protocol_valid_and_exact_raw_sha": True,
            "p0b_stop_disables_current_sqc_full_experiment": True,
            "p0a_p0b_pass_does_not_auto_authorize_full_experiment": True,
            "no_execution_is_triggered_by_this_compiler": True,
        },
        "errors": all_errors,
        "scientific_authority": False,
        "execution_authorized": False,
        "authority": dict(AUTHORITY),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p0a-result", type=Path)
    ap.add_argument("--p0b-result", type=Path)
    ap.add_argument("--p0c-result", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    state = compile_transition(p0a=load_json(args.p0a_result), p0b=load_json(args.p0b_result), p0c=load_json(args.p0c_result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": state["status"], "allowed_next_actions": state["allowed_next_actions"], "scientific_authority": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
