"""Recompile pinned MemRL against B1's current 2026-08-27 G1-G8 substrate gate.

This is a zero-confirmatory-outcome gate compiler.  It deliberately translates
older R39/R40 gate names into the current scientific contract instead of
pretending that the historical G1-G6 ladder is still authoritative.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
DESIGN = PROJECT_ROOT / "research_pipeline" / "b1_process_provenance_governance_design_20260827.json"
R19 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-l2b-r19-contract.json"
R39 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r39-memrl-substrate-audit.json"
R40 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r40-memrl-g5-preflight.json"
R41 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r41-memrl-g5-runtime-adjudication.json"
IMAGE = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r42-memrl-image-compatibility-evidence.json"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r42-memrl-current-g1-g8-preflight.json"
PINNED = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"
EXPECTED_GATE_PREFIXES = ["G1 ", "G2 ", "G3 ", "G4 ", "G5 ", "G6 ", "G7 ", "G8 "]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object:{path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    design, r19, r39, r40, r41, image = map(_load, (DESIGN, R19, R39, R40, R41, IMAGE))
    gates = design.get("fresh_substrate_gate") or []
    if len(gates) != 8 or any(not str(row).startswith(prefix) for row, prefix in zip(gates, EXPECTED_GATE_PREFIXES)):
        raise ValueError("current-G1-G8-contract-drift")
    if r39.get("paper_id") != PAPER_ID or r41.get("paper_id") != PAPER_ID:
        raise ValueError("paper-id-drift")
    if (r39.get("candidate") or {}).get("repository_commit_sha") != PINNED:
        raise ValueError("memrl-pin-drift")
    if (r41.get("source_identity") or {}).get("revision") != PINNED:
        raise ValueError("r41-pin-drift")
    r39_g2 = r39.get("G2_provenance_schema") or {}
    r39_g3 = r39.get("G3_exact_information") or {}
    r39_g4 = r39.get("G4_fresh_capacity") or {}
    old_g5 = (r41.get("historical_r39_r40_gate_adjudication") or {}).get("G5_SUPPORT_AND_PREREGISTRATION") is True
    access = r41.get("access_accounting") or {}
    no_confirmatory_access = (
        int(access.get("confirmatory_validation_tasks_executed") or 0) == 0
        and int(access.get("confirmatory_treatment_outcomes_observed") or 0) == 0
    )
    historical_substrate = str((((r19.get("executor") or {}).get("historical_relationship") or {}).get("claim_scope") or ""))
    historical_task_family = str(((r19.get("browsergym_runtime") or {}).get("task_family") or ""))
    memrl_capacity = r39_g4.get("OSInteraction") or {}
    r40_contract = r40.get("frozen_confirmatory_contract") or {}
    image_access = image.get("access_accounting") or {}
    image_zero_outcome = all(int(image_access.get(key) or 0) == 0 for key in (
        "validation_task_initializations", "validation_evaluator_calls", "validation_ground_truth_calls", "validation_treatment_outcomes_observed", "model_calls", "provider_calls"
    ))

    current = {
        "G1": {
            "pass": r39_g2.get("passed_now") is True,
            "evidence": "Released LLB terminal success is produced by the environment evaluator and propagated into source memory metadata.success; post-use q_value remains a separate field.",
            "source": "R39.G2_provenance_schema",
        },
        "G2": {
            "pass": r39_g3.get("passed_now") is True,
            "evidence": "R39 freezes selected IDs/order/content bytes before arm projection and exposes provenance as a separate field without consulting future target outcomes.",
            "source": "R39.G3_exact_information",
        },
        "G3": {
            "pass": r39_g3.get("passed_now") is True,
            "evidence": "Content-only versus truthful source_outcome_success arms are projected after identical retrieval; backend-only relabel remains an equivalence control and no retrieval rerun is allowed.",
            "source": "R39.G3_exact_information",
        },
        "G4": {
            "pass": bool(
                r39_g4.get("passed_now") is True
                and int(memrl_capacity.get("future_validation_tasks") or 0) == 150
                and int(memrl_capacity.get("train_validation_key_overlap") or 0) == 0
                and "ReasoningBank/WebArena" in historical_substrate
                and "browsergym/webarena" in historical_task_family
            ),
            "evidence": "MemRL OSInteraction uses a separate 150-task validation split; the historical R19/legacy cohort is ReasoningBank/BrowserGym WebArena Shopping, so target task identity is disjoint by substrate and task namespace.",
            "source": "R39.G4_fresh_capacity + frozen R19 contract",
        },
        "G5": {
            "pass": bool(old_g5 and (r41.get("runtime_support") or {}).get("training_support_evaluator_replay_pass") is True and no_confirmatory_access),
            "evidence": "Native OSInteractionContainer reset/isolation/timeout/cleanup and repeated released evaluator replay pass on a fixed train support unit while validation treatment outcomes remain sealed.",
            "source": "R41 runtime support adjudication",
        },
        "G6": {
            "pass": bool(
                int(memrl_capacity.get("validation_skill_signature_clusters") or 0) >= int(r40_contract.get("minimum_reference_independent_units") or 10**9)
                and r40_contract.get("inference_unit")
            ),
            "evidence": "The inference unit is prospectively frozen as exact skill_list-signature dependency cluster; OSInteraction has 148 validation clusters versus the frozen 32-unit reference, while seeds/requests remain nested repetitions.",
            "source": "R39.G4_fresh_capacity + R40 frozen_confirmatory_contract",
        },
        "G7": {
            "pass": bool(
                r39_g4.get("validation_is_read_only") is True
                and int(r39_g4.get("validation_write_operations_found") or 0) == 0
                and "retrieval for every analyzed unit must be frozen before arm projection" in ((r40_contract.get("source_build") or {}).get("qualification_gate") or [])
                and no_confirmatory_access
            ),
            "evidence": "Validation is read-only; matching/collision rules, retrieval membership, exclusions, and support requirements are frozen before arm projection and before any confirmatory outcome.",
            "source": "R39.G4_fresh_capacity + R40 frozen_confirmatory_contract + R41 access accounting",
        },
        "G8": {
            "pass": False,
            "evidence": "Scientific estimands/moderators plus the R40 randomization/exclusion/missingness/multiplicity/test/stopping rules are frozen, and a fixed image candidate has 29/29 declared validation skills. The current E0-E5 execution manifest, exact model/embedding identities, and final confirmatory runtime image binding have not yet been sealed together in one content-addressed manifest.",
            "source": "2026-08-27 design + R40 + R42 image compatibility",
            "image_surface_compatible": image.get("all_declared_skills_available") is True and image_zero_outcome,
        },
    }
    passed = [key for key, value in current.items() if value["pass"]]
    blockers = [key for key, value in current.items() if not value["pass"]]
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R42-MEMRL-CURRENT-G1-G8-PREFLIGHT",
        "recorded_date": "2026-08-29",
        "status": "MEMRL_CURRENT_G1_G7_PASS_G8_MANIFEST_FREEZE_HOLD_ZERO_CONFIRMATORY_OUTCOMES",
        "role": "CURRENT_B1_FRESH_SUBSTRATE_GATE_RECOMPILE",
        "parent_bindings": {
            "current_design": {"path": str(DESIGN.relative_to(PROJECT_ROOT)), "sha256": _sha(DESIGN)},
            "historical_r19_contract": {"path": str(R19.relative_to(PROJECT_ROOT)), "sha256": _sha(R19)},
            "memrl_r39": {"path": str(R39.relative_to(PROJECT_ROOT)), "sha256": _sha(R39)},
            "memrl_r40": {"path": str(R40.relative_to(PROJECT_ROOT)), "sha256": _sha(R40)},
            "memrl_r41": {"path": str(R41.relative_to(PROJECT_ROOT)), "sha256": _sha(R41)},
            "image_compatibility": {"path": str(IMAGE.relative_to(PROJECT_ROOT)), "sha256": _sha(IMAGE)},
        },
        "current_gate_contract": gates,
        "current_gate_adjudication": current,
        "summary": {
            "passed": len(passed),
            "total": 8,
            "passed_gates": passed,
            "blocking_gates": blockers,
            "confirmatory_validation_outcomes_observed": 0,
        },
        "runtime_candidate": {
            "image": image.get("candidate_runtime_image") or {},
            "declared_validation_skills": image.get("declared_skill_count"),
            "available_validation_skills": image.get("available_skill_count"),
            "all_declared_skills_available": image.get("all_declared_skills_available"),
            "final_confirmatory_image_frozen": False,
        },
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
        "next_action": "FREEZE_ONE_CONTENT_ADDRESSED_CURRENT_E0_E5_EXECUTION_MANIFEST_WITH_EXACT_MODELS_EMBEDDINGS_RUNTIME_IMAGE_ARM_REALIZATION_AND_STOPPING_RULES_BEFORE_ANY_VALIDATION_TREATMENT_OUTCOME",
        "scientific_verdict": "NO_BEHAVIORAL_VERDICT_MEMRL_PASSES_CURRENT_G1_G7_AND_IS_BLOCKED_ONLY_ON_G8_EXECUTION_MANIFEST_FREEZE",
    }
    payload["receipt_sha256"] = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    s = payload.get("summary") or {}
    g = payload.get("current_gate_adjudication") or {}
    if s.get("passed") != 7 or s.get("total") != 8 or s.get("blocking_gates") != ["G8"]:
        errors.append("expected-G1-G7-pass-G8-hold")
    if any((g.get(k) or {}).get("pass") is not True for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")):
        errors.append("G1-G7-not-all-pass")
    if (g.get("G8") or {}).get("pass") is not False:
        errors.append("G8-must-hold")
    if int(s.get("confirmatory_validation_outcomes_observed") or 0) != 0:
        errors.append("confirmatory-outcome-leak")
    if any((payload.get("authority") or {}).values()):
        errors.append("authority-leak")
    expected = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    if payload.get("receipt_sha256") != expected:
        errors.append("receipt-hash")
    return errors


def write(path: Path = OUT) -> dict[str, Any]:
    payload = build()
    errors = validate(payload)
    if errors:
        raise ValueError("invalid current B1 MemRL gate:" + ";".join(errors))
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    row = write()
    print(json.dumps({"status": row["status"], "summary": row["summary"], "receipt_sha256": row["receipt_sha256"]}, ensure_ascii=False, sort_keys=True))
