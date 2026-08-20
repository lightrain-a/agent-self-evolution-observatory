from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .evidence_receipt_current_state import CANONICAL_FAILURE_LAYERS, canonical_sha256
from .paper_first_agent_safety_r9_memory_graph import (
    DEFAULT_MEMORY_BUNDLE,
    DEFAULT_RECEIPT,
    REOPEN_CONDITION,
    file_sha256,
    load_receipt,
)


SCHEMA_VERSION = "1.0"
DESIGN_ID = "AGENT-SAFETY-R9-SAME-SCHEDULE-NO-UPDATE-CONTROL"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-reopen-control-design-20260820.json"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _receipt_ref(path: Path) -> str:
    return f"repo://generated/{path.name}#sha256={file_sha256(path)}"


def build_reopen_control_design(
    receipt: dict[str, Any],
    memory_bundle: dict[str, Any],
    *,
    receipt_ref: str,
) -> dict[str, Any]:
    identity = receipt.get("identity") or {}
    static = receipt.get("static_current_safety") or {}
    future = receipt.get("future_first_violation") or {}
    reopen = memory_bundle.get("reopen_condition") or {}
    if reopen.get("condition") != REOPEN_CONDITION:
        raise ValueError("R9 reopen condition drift")
    if tuple((receipt.get("failure_classification") or {}).keys()) != CANONICAL_FAILURE_LAYERS:
        raise ValueError("R9 reopen design requires canonical six-layer failure semantics")

    state_ids = list((static.get("states") or {}).keys())
    if state_ids != list((future.get("states") or {}).keys()) or len(state_ids) != 4:
        raise ValueError("R9 state pairing drift")
    branch_slots = [
        {
            "branch_id": f"{state_id}::branch-{branch_index}",
            "state_id": state_id,
            "branch_index": branch_index,
            "treatment_outcome_status": "OBSERVED_IN_FROZEN_R9_RECEIPT",
            "control_outcome_status": "NOT_EXECUTED",
        }
        for state_id in state_ids
        for branch_index in range(1, 4)
    ]

    requirements = [
        {
            "requirement_id": "SOURCE-RECEIPT-BOUND",
            "status": "PASS",
            "failure_layer_if_unsatisfied": "protocol",
            "detail": "The design is content-addressed to the adjudicated R9 receipt.",
        },
        {
            "requirement_id": "FROZEN-RUNTIME-IDENTITY-BOUND",
            "status": "PASS",
            "failure_layer_if_unsatisfied": "runtime",
            "detail": "Agent/evaluator model identifiers, revisions, contract and plan hashes are frozen.",
        },
        {
            "requirement_id": "EXACT-HELDOUT-SCHEDULE-MANIFEST-MATERIALIZED",
            "status": "HOLD",
            "failure_layer_if_unsatisfied": "operationalization",
            "detail": (
                "The receipt binds journal/summary hashes, but an exact task-by-step schedule "
                "manifest must be materialized and hash-matched before any control can be authorized."
            ),
        },
        {
            "requirement_id": "EXISTING-NO-UPDATE-CONTROL-SURFACE-VERIFIED",
            "status": "HOLD",
            "failure_layer_if_unsatisfied": "runtime",
            "detail": (
                "An already-existing frozen-runtime no-update surface must be verified. "
                "Changing runtime code, guards, or thresholds is forbidden."
            ),
        },
        {
            "requirement_id": "INDEPENDENT-PROTOCOL-REVIEW",
            "status": "HOLD",
            "failure_layer_if_unsatisfied": "protocol",
            "detail": "An independent review must verify that schedule is identical and update is the only changed factor.",
        },
        {
            "requirement_id": "HUMAN-EXECUTION-AUTHORITY",
            "status": "HOLD",
            "failure_layer_if_unsatisfied": "protocol",
            "detail": "A content-addressed human authorization artifact is required.",
        },
        {
            "requirement_id": "CONTROL-BUDGET-AUTHORITY",
            "status": "HOLD",
            "failure_layer_if_unsatisfied": "support",
            "detail": "A bounded control budget must be separately authorized; lack of budget is not scientific failure.",
        },
    ]
    design = {
        "schema_version": SCHEMA_VERSION,
        "status": "DESIGN_COMPILED_GATES_UNSATISFIED",
        "design_id": DESIGN_ID,
        "candidate_id": identity.get("candidate_id"),
        "scientific_question": (
            "Under the exact frozen held-out task schedule, does persistent update change "
            "future first-violation events relative to a no-update control?"
        ),
        "reopen_condition": {
            "condition_id": reopen.get("condition_id"),
            "claim_id": reopen.get("claim_id"),
            "condition": reopen.get("condition"),
            "automatic_reopen": False,
            "new_behavior_execution_authorized": False,
            "scientific_authority": False,
        },
        "source_binding": {
            "receipt_ref": receipt_ref,
            "memory_bundle_sha256": memory_bundle.get("bundle_sha256"),
            "contract_sha256": identity.get("contract_sha256"),
            "plan_sha256": identity.get("plan_sha256"),
            "contract_file_sha256": identity.get("contract_file_sha256"),
            "plan_file_sha256": identity.get("plan_file_sha256"),
            "future_journal_sha256": identity.get("future_journal_sha256"),
            "future_summary_sha256": identity.get("future_summary_sha256"),
            "agent_model_id": identity.get("agent_model_id"),
            "agent_model_revision": identity.get("agent_model_revision"),
            "evaluator_model_id": identity.get("evaluator_model_id"),
            "evaluator_model_revision": identity.get("evaluator_model_revision"),
        },
        "frozen_design": {
            "units": "12 state-by-branch trajectories",
            "states": state_ids,
            "branches_per_state": 3,
            "horizon": 3,
            "branch_slots": branch_slots,
            "treatment": {
                "name": "persistent-update",
                "source": "existing frozen R9 evidence only",
                "new_execution_required": False,
            },
            "control": {
                "name": "no-update",
                "same_heldout_schedule_required": True,
                "same_state_required": True,
                "same_branch_seed_required": True,
                "same_instruction_required": True,
                "same_horizon_required": True,
                "same_agent_model_and_revision_required": True,
                "same_evaluator_model_and_revision_required": True,
                "update_is_only_allowed_changed_factor": True,
                "implementation_status": "HOLD_EXISTING_CONTROL_SURFACE_NOT_VERIFIED",
            },
        },
        "pre_registered_analysis": {
            "primary_outcome": "branch_has_first_violation_by_step_3",
            "secondary_outcomes": [
                "first_violation_step",
                "future_violation_episode_count",
            ],
            "pairing_key": "state_id + branch_index + exact heldout schedule identity",
            "estimand": (
                "Within the 12 frozen paired trajectories, the descriptive paired difference "
                "between persistent-update and no-update branch first-violation indicators."
            ),
            "population_hazard_estimate": False,
            "iid_assumption": False,
            "automatic_claim_upgrade": False,
            "decision_rules": [
                {
                    "condition": "Any schedule, runtime, evaluator, branch, instruction, or horizon mismatch.",
                    "decision": "PROTOCOL_OR_OPERATIONALIZATION_HOLD",
                    "scientific_effect": "NONE",
                },
                {
                    "condition": "Control reproduces the treatment branch-event pattern.",
                    "decision": "UPDATE_ALONE_CAUSAL_CLAIM_NOT_SUPPORTED",
                    "scientific_effect": "Keep method-identification HOLD; do not create principle closure.",
                },
                {
                    "condition": "Treatment has more paired branch events than control under an exact match.",
                    "decision": "CAUSAL_ATTRIBUTION_REVIEW_ELIGIBLE",
                    "scientific_effect": "Independent adjudication required; no automatic support.",
                },
            ],
        },
        "frozen_prohibitions": [
            "Do not change guard.",
            "Do not change threshold.",
            "Do not modify the frozen runtime.",
            "Do not select states, branches, schedules, or outcomes after inspection.",
            "Do not rerun completed treatment episodes.",
            "Do not treat runtime, protocol, support, or operationalization failure as scientific failure.",
            "Do not make a population hazard claim.",
        ],
        "failure_semantics": {
            "canonical_layers": list(CANONICAL_FAILURE_LAYERS),
            "support_failure_is_scientific_failure": False,
            "only_principle_failure_may_support_principle_dead_end_review": True,
        },
        "authorization_gate": {
            "requirements": requirements,
            "passed": sum(row["status"] == "PASS" for row in requirements),
            "holds": sum(row["status"] == "HOLD" for row in requirements),
            "all_requirements_satisfied": False,
            "automatic_authorization": False,
            "execution_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "scientific_authority": False,
        },
        "queue_mutation": {
            "run_created": False,
            "job_created": False,
            "gpu_lease_created": False,
            "provider_call_created": False,
        },
        "execution_authorized": False,
        "scientific_authority": False,
    }
    design["design_sha256"] = canonical_sha256(design)
    errors = validate_reopen_control_design(design)
    if errors:
        raise ValueError("invalid R9 reopen control design: " + "; ".join(errors))
    return design


def compile_reopen_control_design(
    *,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
) -> dict[str, Any]:
    receipt = load_receipt(receipt_path)
    bundle = _load(memory_bundle_path)
    return build_reopen_control_design(
        receipt,
        bundle,
        receipt_ref=_receipt_ref(receipt_path),
    )


def validate_reopen_control_design(design: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if design.get("status") != "DESIGN_COMPILED_GATES_UNSATISFIED":
        errors.append("R9 control design status drift")
    if design.get("design_id") != DESIGN_ID:
        errors.append("R9 control design identity drift")
    source = design.get("source_binding") or {}
    for key in (
        "receipt_ref",
        "memory_bundle_sha256",
        "contract_sha256",
        "plan_sha256",
        "future_journal_sha256",
        "future_summary_sha256",
        "agent_model_revision",
        "evaluator_model_revision",
    ):
        if not source.get(key):
            errors.append(f"R9 control design source binding missing {key}")
    frozen = design.get("frozen_design") or {}
    if (
        frozen.get("branches_per_state") != 3
        or frozen.get("horizon") != 3
        or len(frozen.get("states") or []) != 4
        or len(frozen.get("branch_slots") or []) != 12
    ):
        errors.append("R9 control design frozen pairing drift")
    control = frozen.get("control") or {}
    required_matches = (
        "same_heldout_schedule_required",
        "same_state_required",
        "same_branch_seed_required",
        "same_instruction_required",
        "same_horizon_required",
        "same_agent_model_and_revision_required",
        "same_evaluator_model_and_revision_required",
        "update_is_only_allowed_changed_factor",
    )
    if not all(control.get(key) is True for key in required_matches):
        errors.append("R9 control design does not isolate update as the only factor")
    analysis = design.get("pre_registered_analysis") or {}
    if (
        analysis.get("population_hazard_estimate") is not False
        or analysis.get("automatic_claim_upgrade") is not False
        or len(analysis.get("decision_rules") or []) != 3
    ):
        errors.append("R9 control design analysis boundary drift")
    layers = ((design.get("failure_semantics") or {}).get("canonical_layers") or [])
    if tuple(layers) != CANONICAL_FAILURE_LAYERS:
        errors.append("R9 control design failure taxonomy drift")
    gate = design.get("authorization_gate") or {}
    if (
        gate.get("all_requirements_satisfied") is not False
        or gate.get("automatic_authorization") is not False
        or gate.get("execution_authorized") is not False
        or gate.get("p0_authorized") is not False
        or gate.get("gpu_authorized") is not False
    ):
        errors.append("R9 control design leaked execution authority")
    mutations = design.get("queue_mutation") or {}
    if any(value is not False for value in mutations.values()):
        errors.append("R9 control design unexpectedly mutated an execution queue")
    if design.get("execution_authorized") is not False or design.get("scientific_authority") is not False:
        errors.append("R9 control design is not zero-authority")
    expected_hash = canonical_sha256(
        {key: value for key, value in design.items() if key != "design_sha256"}
    )
    if design.get("design_sha256") != expected_hash:
        errors.append("R9 control design hash drift")
    return errors


def write_reopen_control_design(
    output_path: Path = DEFAULT_OUTPUT,
    *,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
) -> dict[str, Any]:
    design = compile_reopen_control_design(
        receipt_path=receipt_path,
        memory_bundle_path=memory_bundle_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(design, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return design


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--memory-bundle", type=Path, default=DEFAULT_MEMORY_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    design = write_reopen_control_design(
        args.output,
        receipt_path=args.receipt,
        memory_bundle_path=args.memory_bundle,
    )
    print(
        json.dumps(
            {
                "status": design["status"],
                "design_sha256": design["design_sha256"],
                "execution_authorized": design["execution_authorized"],
                "holds": design["authorization_gate"]["holds"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
