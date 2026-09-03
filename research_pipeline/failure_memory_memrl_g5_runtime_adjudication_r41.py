"""Adjudicate the zero-confirmatory-outcome MemRL G5 runtime support smoke.

R41 consumes the frozen R40 preregistration plus a content-addressed support-only
runtime receipt.  It may close the historical G5 support/preregistration gate,
but it cannot authorize confirmatory treatment outcomes or treat the support
image as the final frozen confirmatory image.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R40 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r40-memrl-g5-preflight.json"
EVIDENCE = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r41-memrl-g5-runtime-evidence.json"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r41-memrl-g5-runtime-adjudication.json"
PINNED = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build() -> dict[str, Any]:
    r40 = _load(R40)
    ev = _load(EVIDENCE)
    if r40.get("paper_id") != PAPER_ID or ev.get("paper_id") != PAPER_ID:
        raise ValueError("paper-id-drift")
    if (r40.get("runtime_preflight") or {}).get("pinned_commit_expected") != PINNED:
        raise ValueError("r40-pinned-revision-drift")
    if ev.get("source_revision") != PINNED or ev.get("source_clean") is not True:
        raise ValueError("r41-source-revision-or-cleanliness-failed")
    access = ev.get("access_accounting") or {}
    if int(access.get("confirmatory_validation_tasks_executed") or 0) != 0:
        raise ValueError("confirmatory-validation-accessed")
    if int(access.get("confirmatory_treatment_outcomes_observed") or 0) != 0:
        raise ValueError("confirmatory-outcome-accessed")
    if int(access.get("model_calls") or 0) != 0 or int(access.get("provider_calls") or 0) != 0:
        raise ValueError("model-or-provider-call-in-support-smoke")
    runtime = ev.get("native_runtime_smoke") or {}
    evaluator = ev.get("training_support_evaluator_replay") or {}
    support_image = ev.get("support_image") or {}
    runtime_pass = bool(
        runtime.get("pass") is True
        and (runtime.get("basic_exec") or {}).get("exit_code") == 0
        and (runtime.get("basic_exec") or {}).get("timeout_flag") is False
        and (runtime.get("state_isolation") or {}).get("second_fresh_container_marker_absent") is True
        and (runtime.get("timeout_semantics") or {}).get("timeout_flag") is True
        and int((runtime.get("cleanup") or {}).get("new_labelled_containers_remaining") or 0) == 0
    )
    evaluator_pass = bool(
        evaluator.get("pass") is True
        and evaluator.get("validation_split_used") is False
        and evaluator.get("confirmatory_treatment_outcome_used") is False
        and (evaluator.get("first_container") or {}).get("evaluation_replay_deterministic") is True
        and (evaluator.get("fresh_container") or {}).get("reset_replays_initial_state") is True
    )
    source_faithful_confirmatory_image = bool(support_image.get("source_default_image_equivalent_claimed") is True)
    historical_g5_pass = bool(
        runtime_pass
        and evaluator_pass
        and (r40.get("G5_adjudication") or {}).get("preregistration_contract_frozen") is True
        and (r40.get("G5_adjudication") or {}).get("static_pinned_source_support") is True
    )
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R41-MEMRL-G5-RUNTIME-ADJUDICATION",
        "recorded_date": "2026-08-29",
        "status": "MEMRL_R40_G5_SUPPORT_AND_PREREGISTRATION_PASS_CONFIRMATORY_IMAGE_STILL_UNFROZEN",
        "role": "ZERO_CONFIRMATORY_OUTCOME_RUNTIME_SUPPORT_ADJUDICATION",
        "parent_bindings": {
            "r40_preregistration": {"path": str(R40.relative_to(PROJECT_ROOT)), "sha256": _sha(R40)},
            "r41_runtime_evidence": {"path": str(EVIDENCE.relative_to(PROJECT_ROOT)), "sha256": _sha(EVIDENCE)},
        },
        "source_identity": {
            "repo": ev.get("source_repo"),
            "revision": ev.get("source_revision"),
            "host": ev.get("host"),
            "docker_server": ev.get("docker_server"),
            "source_file_sha256": ev.get("source_file_sha256") or {},
        },
        "runtime_support": {
            "native_osinteraction_container_lifecycle_pass": runtime_pass,
            "fresh_container_isolation_pass": (runtime.get("state_isolation") or {}).get("second_fresh_container_marker_absent") is True,
            "timeout_semantics_pass": (runtime.get("timeout_semantics") or {}).get("timeout_flag") is True,
            "cleanup_pass": int((runtime.get("cleanup") or {}).get("new_labelled_containers_remaining") or 0) == 0,
            "training_support_evaluator_replay_pass": evaluator_pass,
            "training_support_unit": {
                "split": evaluator.get("split"),
                "unit_id": evaluator.get("unit_id"),
                "instruction_sha256": evaluator.get("instruction_sha256"),
            },
            "validation_split_executed": False,
            "confirmatory_outcome_observed": False,
            "support_image": support_image,
            "support_image_is_final_confirmatory_image": False,
            "source_faithful_confirmatory_image_frozen": source_faithful_confirmatory_image,
        },
        "historical_r39_r40_gate_adjudication": {
            "G1_RELEASE": True,
            "G2_PROVENANCE_SCHEMA": True,
            "G3_EXACT_INFORMATION": True,
            "G4_FRESH_CAPACITY": True,
            "G5_SUPPORT_AND_PREREGISTRATION": historical_g5_pass,
            "G6_AUTHORITY": False,
            "passed_now": historical_g5_pass,
            "next_blocking_stage": "CURRENT_20260827_G1_G8_RECOMPILE_AND_CONFIRMATORY_IMAGE_FREEZE",
        },
        "current_program_boundary": {
            "r40_gate_names_are_historical_and_do_not_replace_20260827_G1_G8": True,
            "current_fresh_substrate_gate_must_be_recompiled": True,
            "confirmatory_image_must_be_frozen_before_first_validation_treatment_outcome": True,
            "current_user_request_may_authorize_continuation_but_does_not_waive_scientific_gates": True,
        },
        "access_accounting": access,
        "claim_policy": {
            "new_scientific_behavioral_result": False,
            "provenance_only_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
        },
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "evaluator_calls_on_confirmatory_validation": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
        "next_action": "RECOMPILE_PINNED_MEMRL_AGAINST_CURRENT_G1_G8_WITHOUT_VALIDATION_TREATMENT_OUTCOME_ACCESS",
        "scientific_verdict": "NO_BEHAVIORAL_VERDICT_RUNTIME_SUPPORT_FAILURE_WAS_IMPLEMENTATION_LEVEL_AND_IS_NOW_CLOSED",
    }
    payload["receipt_sha256"] = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("paper_id") != PAPER_ID:
        errors.append("paper-id")
    if payload.get("status") != "MEMRL_R40_G5_SUPPORT_AND_PREREGISTRATION_PASS_CONFIRMATORY_IMAGE_STILL_UNFROZEN":
        errors.append("status")
    h = payload.get("historical_r39_r40_gate_adjudication") or {}
    if h.get("G5_SUPPORT_AND_PREREGISTRATION") is not True or h.get("G6_AUTHORITY") is not False:
        errors.append("historical-gate-adjudication")
    r = payload.get("runtime_support") or {}
    if r.get("native_osinteraction_container_lifecycle_pass") is not True or r.get("training_support_evaluator_replay_pass") is not True:
        errors.append("runtime-support")
    if r.get("validation_split_executed") is not False or r.get("confirmatory_outcome_observed") is not False:
        errors.append("confirmatory-access")
    if r.get("support_image_is_final_confirmatory_image") is not False:
        errors.append("support-image-authority")
    if any((payload.get("authority") or {}).get(k) is not False for k in ("scientific_execution", "experiment", "model_calls", "evaluator_calls_on_confirmatory_validation", "gpu", "claim_expansion", "submission")):
        errors.append("authority-leak")
    expected = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    if payload.get("receipt_sha256") != expected:
        errors.append("receipt-hash")
    return errors


def write(path: Path = OUT) -> dict[str, Any]:
    payload = build()
    errors = validate(payload)
    if errors:
        raise ValueError("invalid R41 MemRL G5 runtime adjudication:" + ";".join(errors))
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    row = write()
    print(json.dumps({
        "status": row["status"],
        "G5": row["historical_r39_r40_gate_adjudication"]["G5_SUPPORT_AND_PREREGISTRATION"],
        "next": row["next_action"],
        "receipt_sha256": row["receipt_sha256"],
    }, ensure_ascii=False, sort_keys=True))
