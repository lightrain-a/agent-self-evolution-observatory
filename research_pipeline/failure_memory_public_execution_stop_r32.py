#!/usr/bin/env python3
"""Build a public-safe stop projection for exhausted R19 pre-exposure retry."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
STATUS = "R19_CONFIRMATORY_EXECUTION_STOPPED_RETRY_EXHAUSTED_NO_VERDICT"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority-receipt", type=Path, required=True)
    ap.add_argument("--r30-checkpoint", type=Path, required=True)
    ap.add_argument("--r31-stop", type=Path, required=True)
    ap.add_argument("--psmg", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-public-stop-r32.json"))
    a = ap.parse_args()
    auth = load(a.authority_receipt)
    r30 = load(a.r30_checkpoint)
    r31 = load(a.r31_stop)
    psmg = load(a.psmg)
    if auth.get("status") != "R19_EXTERNAL_HUMAN_BOUNDED_SCIENTIFIC_EXECUTION_AUTHORITY_VALID":
        raise RuntimeError("R21 authority drift")
    if r30.get("receipt_id") != "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PARTIAL-CHECKPOINT-R30":
        raise RuntimeError("R30 checkpoint identity drift")
    if r30["execution"]["episodes_complete"] != 28 or r30["execution"]["complete_independent_tasks"] != 7:
        raise RuntimeError("R30 boundary drift")
    if r31.get("status") != "SEQ029_PREEXPOSURE_SUPPORT_FAILURE_EXACT_RETRY_EXHAUSTED_R19_STOPPED":
        raise RuntimeError("R31 stop status drift")
    if r31.get("scientific_verdict") != "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE_RETRY_EXHAUSTED":
        raise RuntimeError("R31 verdict drift")
    if r31["adjudication"]["current_R19_confirmatory_execution_stopped"] is not True:
        raise RuntimeError("R31 did not stop R19")
    if psmg.get("status") != "PREOUTCOME_METHOD_DESIGN_FROZEN_NO_NEW_EXECUTION_AUTHORITY":
        raise RuntimeError("PSMG design status drift")
    if psmg["authority"]["experiment"] is not False or psmg["future_decisive_experiment_if_separately_authorized"]["execution_authorized_now"] is not False:
        raise RuntimeError("PSMG unexpectedly authorized")

    out = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PUBLIC-STOP-R32",
        "status": STATUS,
        "authority": {
            "bounded_r19_scientific_execution_authority_was_valid": True,
            "scientific_claim_authority": False,
            "current_R19_execution_authority_consumed_for_stopped_attempt": True,
            "r18_retry_authorized": False,
            "l3_authorized": False,
            "authority_receipt_sha256": sha(a.authority_receipt),
        },
        "last_complete_task_boundary": {
            "episodes_complete": 28,
            "complete_independent_tasks": 7,
            "next_sequence_index_at_boundary": 28,
            "checkpoint_sha256": sha(a.r30_checkpoint),
        },
        "stopped_partial_prefix": {
            "episodes_complete": 29,
            "episodes_expected": 140,
            "complete_independent_tasks": 7,
            "current_incomplete_task_completed_episodes": 1,
            "last_complete_sequence_index": 28,
            "agent_completions": 513,
            "agent_completion_budget": 4200,
            "fuzzy_evaluator_completions": 0,
            "fuzzy_evaluator_completion_budget": 600,
            "post_started_failure": False,
            "in_flight_episode": False,
        },
        "support_retry_exhaustion": {
            "failed_sequence_index": 29,
            "first_attempt_scientific_exposure": False,
            "exact_retry_scientific_exposure": False,
            "first_attempt_receipt_sha256": r31["support_failure_chain"]["first_attempt"]["receipt_sha256"],
            "exact_retry_attempt_receipt_sha256": r31["support_failure_chain"]["exact_retry_attempt"]["receipt_sha256"],
            "exact_retry_consumed": True,
            "additional_retry_permitted": False,
            "r31_adjudication_sha256": sha(a.r31_stop),
        },
        "interim_policy": {
            "terminal_scores_exposed_in_projection": False,
            "task_deltas_computed": False,
            "effect_mean_computed": False,
            "p_value_computed": False,
            "confidence_interval_computed": False,
            "partial_prefix_confirmatory_analysis_permitted": False,
            "claim_update_allowed": False,
            "no_effect_claim_authorized": False,
        },
        "current_R19": {
            "execution_stopped": True,
            "resume_permitted": False,
            "sequence29_retry_permitted": False,
            "sequence30_or_later_execution_permitted": False,
            "current_attempt_retriable": False,
            "scientific_verdict": "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE_RETRY_EXHAUSTED",
            "scientific_negative": False,
        },
        "future_reopen": {
            "new_experiment_contract_required": True,
            "new_explicit_scientific_and_execution_authority_required": True,
            "support_restoration_required": True,
            "partial_R19_outcomes_must_not_select_new_design": True,
            "partial_R19_outcomes_must_not_be_pooled_into_new_confirmatory_sample": True,
        },
        "method_closure": {
            "method": "PSMG",
            "story": psmg["problem_to_method_loop"]["paper_story"],
            "method_design_frozen": True,
            "new_mitigation_experiment_authorized": False,
            "effect_claim_authorized": False,
            "design_receipt_sha256": sha(a.psmg),
        },
        "stanford_o5": {
            "disposition": "REQUIRES_SCIENTIFIC_REOPEN",
            "scientific_reopen_status": "R19_STOPPED_SUPPORT_FAILURE_RETRY_EXHAUSTED",
            "current_verdict": "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE_RETRY_EXHAUSTED",
        },
        "redaction": {
            "terminal_scores": False,
            "browser_actions": False,
            "raw_memory_text": False,
            "internal_run_paths": False,
            "authority_source_message": False,
        },
    }
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "episodes_complete": 29, "resume_permitted": False, "interim_inference": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
