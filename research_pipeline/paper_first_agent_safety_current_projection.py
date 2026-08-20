from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_agent_safety_program_state import (
    PUBLIC_GLOBAL,
    validate_agent_safety_program_state,
)
from .paper_first_agent_safety_r9_memory_graph import (
    compile_memory_graph_inputs,
    file_sha256,
)


SCHEMA_VERSION = "1.0"
CURRENT_STAGE = "PAPER_EVIDENCE_READY_CAUSAL_ATTRIBUTION_HOLD"
CURRENT_CANDIDATE_STAGE = "SUPPORTED_NARROWLY_WITH_METHOD_IDENTIFICATION_HOLD"
DEFAULT_PROGRAM_JSON = PROJECT_ROOT / "generated" / "agent-safety-program-state.json"
DEFAULT_PROGRAM_JS = PROJECT_ROOT / "generated" / "agent-safety-program-state.js"
DEFAULT_RECEIPT = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-future-evidence-adjudication-20260820.json"
)
DEFAULT_MEMORY_BUNDLE = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-memory-graph21-inputs-20260820.json"
)
FAILURE_LAYERS = (
    "runtime",
    "protocol",
    "support",
    "operationalization",
    "method",
    "principle",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _historical_base(state: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(state)
    snapshot = base.pop("historical_projection", None)
    base.pop("future_evidence", None)
    base.pop("paper_claim_boundary", None)
    base.pop("projection_consistency", None)
    if isinstance(snapshot, dict):
        for key in (
            "schema_version",
            "current_stage",
            "candidate_stage",
            "next_gate",
            "authority",
            "execution_authorized",
        ):
            if key in snapshot:
                base[key] = copy.deepcopy(snapshot[key])
        for key in ("qualification", "support_root_diagnosis", "support_realization_adjudication"):
            value = base.get(key)
            if isinstance(value, dict):
                value.pop("historical_only", None)
    return base


def _receipt_ref(path: Path) -> str:
    return f"repo://generated/{path.name}#sha256={file_sha256(path)}"


def project_agent_safety_current_state(
    base_state: dict[str, Any],
    *,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
    generated_at: str | None = None,
) -> dict[str, Any]:
    historical = _historical_base(base_state)
    historical_errors = validate_agent_safety_program_state(historical)
    if historical_errors:
        raise ValueError(
            "historical agent-safety projection is invalid: " + "; ".join(historical_errors)
        )

    claim_table, compiled_bundle = compile_memory_graph_inputs(Path(receipt_path))
    stored_bundle = _load(Path(memory_bundle_path))
    if stored_bundle.get("bundle_sha256") != compiled_bundle.get("bundle_sha256"):
        raise ValueError("stored R9 memory bundle does not match the frozen evidence receipt")
    receipt = _load(Path(receipt_path))
    receipt_ref = _receipt_ref(Path(receipt_path))
    if stored_bundle.get("receipt_ref") != receipt_ref:
        raise ValueError("R9 memory bundle receipt reference drift")
    if (receipt.get("identity") or {}).get("candidate_id") != historical.get("candidate_id"):
        raise ValueError("R9 future evidence candidate identity drift")

    static = receipt.get("static_current_safety") or {}
    future = receipt.get("future_first_violation") or {}
    prediction = receipt.get("prediction_adjudication") or {}
    integrity = receipt.get("execution_integrity") or {}
    failure_classification = receipt.get("failure_classification") or {}
    if tuple(failure_classification) != FAILURE_LAYERS:
        raise ValueError("R9 future evidence must expose the canonical six failure layers")
    if not all(isinstance(failure_classification[key], list) for key in FAILURE_LAYERS):
        raise ValueError("R9 future evidence failure-layer payloads must be lists")

    supported_claim = str((receipt.get("claim_scope") or {}).get("supported") or "")
    not_supported = list((receipt.get("claim_scope") or {}).get("not_supported") or [])
    reopen = stored_bundle.get("reopen_condition") or {}
    if not supported_claim or len(not_supported) != 4:
        raise ValueError("R9 future evidence claim boundary drift")
    if reopen.get("automatic_reopen") is not False or reopen.get("new_behavior_execution_authorized") is not False:
        raise ValueError("R9 causal-identification HOLD cannot auto-reopen or authorize execution")

    projected = copy.deepcopy(historical)
    projected["schema_version"] = "1.1"
    projected["generated_at"] = generated_at or _now()
    projected["historical_projection"] = {
        "schema_version": historical.get("schema_version"),
        "current_stage": historical.get("current_stage"),
        "candidate_stage": historical.get("candidate_stage"),
        "next_gate": copy.deepcopy(historical.get("next_gate") or {}),
        "authority": copy.deepcopy(historical.get("authority") or {}),
        "execution_authorized": historical.get("execution_authorized") is True,
        "historical_only": True,
        "superseded_as_current_status_by": receipt_ref,
        "scientific_authority": False,
    }
    for key in ("qualification", "support_root_diagnosis", "support_realization_adjudication"):
        value = projected.get(key)
        if isinstance(value, dict) and value:
            value["historical_only"] = True

    projected["current_stage"] = CURRENT_STAGE
    projected["candidate_stage"] = CURRENT_CANDIDATE_STAGE
    projected["future_evidence"] = {
        "schema_version": SCHEMA_VERSION,
        "status": receipt.get("status"),
        "receipt_ref": receipt_ref,
        "memory_bundle_sha256": stored_bundle.get("bundle_sha256"),
        "paper_claim_table_sha256": claim_table.get("table_sha256"),
        "paper_evidence_ready": receipt.get("paper_evidence_ready") is True,
        "supported_claim": supported_claim,
        "not_supported_claims": not_supported,
        "claim_adjudication": {
            "supported_claim_id": (stored_bundle.get("claim_ledger") or [{}])[0].get("claim_id"),
            "supported_status": (stored_bundle.get("claim_ledger") or [{}])[0].get("adjudication_status"),
            "causal_hold_claim_id": (stored_bundle.get("claim_ledger") or [{}, {}])[1].get("claim_id"),
            "causal_hold_status": (stored_bundle.get("claim_ledger") or [{}, {}])[1].get("adjudication_status"),
            "scientific_closures": int((stored_bundle.get("summary") or {}).get("scientific_closures") or 0),
            "principle_updates": int((stored_bundle.get("summary") or {}).get("principle_updates") or 0),
        },
        "static_current_safety": {
            "selected_states": int(static.get("selected_states") or 0),
            "qualification_episodes": int(static.get("qualification_episodes") or 0),
            "qualification_violations": int(static.get("qualification_violations") or 0),
        },
        "future_first_violation": {
            "future_episodes": int(future.get("future_episodes") or 0),
            "future_violation_episodes": int(future.get("future_violation_episodes") or 0),
            "branches": int(future.get("branches") or 0),
            "branches_with_first_violation": int(future.get("branches_with_first_violation") or 0),
            "states_with_first_violation": int(future.get("states_with_first_violation") or 0),
            "first_violation_step_counts": copy.deepcopy(future.get("first_violation_step_counts") or {}),
        },
        "prediction_adjudication": copy.deepcopy(prediction),
        "execution_integrity": copy.deepcopy(integrity),
        "failure_classification": copy.deepcopy(failure_classification),
        "limitation": (
            "Persistent update and held-out task schedule change together in the frozen "
            "design; causal attribution to the update alone remains on HOLD."
        ),
        "reopen_condition": copy.deepcopy(reopen),
        "additional_behavior_execution_authorized": False,
        "scientific_authority": False,
    }
    projected["paper_claim_boundary"] = {
        "supported_claim": supported_claim,
        "not_supported_claims": not_supported,
        "limitation": projected["future_evidence"]["limitation"],
        "claim_table_sha256": claim_table.get("table_sha256"),
        "scientific_authority": False,
    }
    projected["next_gate"] = {
        "name": "SEPARATE_PERSISTENT_UPDATE_FROM_HELDOUT_SCHEDULE",
        "required": True,
        "reason": str(reopen.get("condition") or ""),
        "automatic_reopen": False,
        "new_behavior_execution_authorized": False,
        "scientific_authority": False,
    }
    authority = projected.setdefault("authority", {})
    for key in (
        "scientific_claim",
        "live_problem_gate",
        "paper_design",
        "method",
        "experiment",
        "p0",
        "gpu",
        "bounded_evidence_acquisition",
        "qualification_probe_execution",
        "heldout_future_probe_execution",
    ):
        authority[key] = False
    projected["execution_authorized"] = False
    projected.setdefault("source_artifacts", {}).update(
        {
            "future_evidence_receipt": _sha(Path(receipt_path)),
            "future_memory_graph_bundle": _sha(Path(memory_bundle_path)),
        }
    )
    projected["projection_consistency"] = {
        "receipt_is_current_scientific_state": True,
        "historical_support_and_realization_stops_retained_as_history": True,
        "heldout_execution_completed": int(integrity.get("completed_future_episodes") or 0) == 36,
        "public_state_does_not_authorize_new_behavior_execution": True,
        "scientific_authority": False,
    }

    errors = validate_current_agent_safety_projection(
        projected,
        receipt_path=Path(receipt_path),
        memory_bundle_path=Path(memory_bundle_path),
    )
    if errors:
        raise ValueError("invalid current agent-safety projection: " + "; ".join(errors))
    return projected


def validate_current_agent_safety_projection(
    state: dict[str, Any],
    *,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
) -> list[str]:
    errors: list[str] = []
    future = state.get("future_evidence") or {}
    bundle = _load(Path(memory_bundle_path))
    receipt = _load(Path(receipt_path))
    expected_ref = _receipt_ref(Path(receipt_path))
    static = future.get("static_current_safety") or {}
    hazard = future.get("future_first_violation") or {}
    adjudication = future.get("claim_adjudication") or {}
    reopen = future.get("reopen_condition") or {}
    authority = state.get("authority") or {}

    if state.get("current_stage") != CURRENT_STAGE or state.get("candidate_stage") != CURRENT_CANDIDATE_STAGE:
        errors.append("current Agent Safety stage is not derived from final paper evidence")
    if future.get("status") != receipt.get("status") or future.get("receipt_ref") != expected_ref:
        errors.append("current Agent Safety receipt binding drift")
    if future.get("memory_bundle_sha256") != bundle.get("bundle_sha256"):
        errors.append("current Agent Safety memory bundle binding drift")
    if future.get("paper_evidence_ready") is not True:
        errors.append("current Agent Safety paper evidence is not ready")
    if (static.get("qualification_episodes"), static.get("qualification_violations")) != (12, 0):
        errors.append("current Agent Safety static evidence projection drift")
    if (
        hazard.get("future_episodes"),
        hazard.get("future_violation_episodes"),
        hazard.get("branches"),
        hazard.get("branches_with_first_violation"),
        hazard.get("states_with_first_violation"),
    ) != (36, 11, 12, 8, 3):
        errors.append("current Agent Safety future first-violation projection drift")
    if adjudication.get("supported_status") != "SUPPORTED_NARROWLY":
        errors.append("current Agent Safety narrow supported claim missing")
    if adjudication.get("causal_hold_status") != "HOLD_METHOD_IDENTIFICATION":
        errors.append("current Agent Safety causal attribution must remain on method HOLD")
    if int(adjudication.get("scientific_closures") or 0) != 0 or int(adjudication.get("principle_updates") or 0) != 0:
        errors.append("current Agent Safety projection cannot create scientific closure or principle update")
    if set((future.get("failure_classification") or {}).keys()) != set(FAILURE_LAYERS):
        errors.append("current Agent Safety projection lost canonical six-layer failure taxonomy")
    if not str(reopen.get("condition") or "").startswith(
        "Separate persistent update effect from held-out schedule effect"
    ):
        errors.append("current Agent Safety causal HOLD lost its reopen condition")
    if reopen.get("automatic_reopen") is not False or reopen.get("new_behavior_execution_authorized") is not False:
        errors.append("current Agent Safety causal HOLD leaked automatic reopen/execution authority")
    if future.get("additional_behavior_execution_authorized") is not False:
        errors.append("current Agent Safety evidence unexpectedly authorizes more behavior execution")
    if state.get("execution_authorized") is not False or any(
        authority.get(key) is True
        for key in (
            "scientific_claim",
            "live_problem_gate",
            "paper_design",
            "method",
            "experiment",
            "p0",
            "gpu",
            "bounded_evidence_acquisition",
            "qualification_probe_execution",
            "heldout_future_probe_execution",
        )
    ):
        errors.append("current Agent Safety public projection leaked downstream execution authority")
    historical = state.get("historical_projection") or {}
    if historical.get("historical_only") is not True or historical.get("current_stage") != "CURRENT_SAFETY_SUPPORT_STOP":
        errors.append("current Agent Safety projection did not preserve the old support stop as history")
    consistency = state.get("projection_consistency") or {}
    if (
        consistency.get("receipt_is_current_scientific_state") is not True
        or consistency.get("historical_support_and_realization_stops_retained_as_history") is not True
        or consistency.get("heldout_execution_completed") is not True
        or consistency.get("public_state_does_not_authorize_new_behavior_execution") is not True
    ):
        errors.append("current Agent Safety cross-projection consistency receipt is incomplete")
    return errors


def load_current_agent_safety_program_state(
    path: Path = DEFAULT_PROGRAM_JSON,
    *,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
) -> dict[str, Any]:
    state = _load(Path(path))
    errors = validate_current_agent_safety_projection(
        state,
        receipt_path=Path(receipt_path),
        memory_bundle_path=Path(memory_bundle_path),
    )
    if errors:
        raise ValueError("invalid published current Agent Safety state: " + "; ".join(errors))
    return state


def write_current_agent_safety_projection(
    *,
    base_state_path: Path = DEFAULT_PROGRAM_JSON,
    receipt_path: Path = DEFAULT_RECEIPT,
    memory_bundle_path: Path = DEFAULT_MEMORY_BUNDLE,
    json_path: Path = DEFAULT_PROGRAM_JSON,
    js_path: Path = DEFAULT_PROGRAM_JS,
    generated_at: str | None = None,
) -> dict[str, Any]:
    state = project_agent_safety_current_state(
        _load(Path(base_state_path)),
        receipt_path=Path(receipt_path),
        memory_bundle_path=Path(memory_bundle_path),
        generated_at=generated_at,
    )
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    Path(js_path).write_text(
        f"window.{PUBLIC_GLOBAL} = "
        + json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-state", type=Path, default=DEFAULT_PROGRAM_JSON)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--memory-bundle", type=Path, default=DEFAULT_MEMORY_BUNDLE)
    parser.add_argument("--json", type=Path, default=DEFAULT_PROGRAM_JSON)
    parser.add_argument("--js", type=Path, default=DEFAULT_PROGRAM_JS)
    args = parser.parse_args()
    state = write_current_agent_safety_projection(
        base_state_path=args.base_state,
        receipt_path=args.receipt,
        memory_bundle_path=args.memory_bundle,
        json_path=args.json,
        js_path=args.js,
    )
    print(
        json.dumps(
            {
                "status": state["current_stage"],
                "supported_status": state["future_evidence"]["claim_adjudication"]["supported_status"],
                "causal_status": state["future_evidence"]["claim_adjudication"]["causal_hold_status"],
                "new_behavior_execution_authorized": False,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
