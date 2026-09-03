#!/usr/bin/env python3
"""Close B1 RoMeRL G3 offline and adjudicate bundled-checkpoint G4 fail-closed.

R38 records no benchmark outcome.  It binds the R37 source/provenance audit to
an exact-information post-retrieval adapter, then asks whether the bundled
RoMeRL checkpoints can supply prospectively fresh independent task units.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R37 = Path("generated/d2-failure-memory-provenance-r37-romerl-substrate-audit.json")
ADAPTER = Path("research_pipeline/failure_memory_romerl_exact_information_adapter_r38.py")
OUT = Path("generated/d2-failure-memory-provenance-r38-romerl-exact-information-gate.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    r37 = _load(R37)
    gate37 = r37["gate_adjudication"]
    if not gate37["G1_RELEASE"]["passed_now"]:
        raise RuntimeError("R37 G1 release gate is not closed")
    if not gate37["G2_PROVENANCE_SCHEMA"]["passed_now"]:
        raise RuntimeError("R37 G2 provenance schema gate is not closed")
    if gate37["gate_pass_now"] or r37["authority"]["experiment"]:
        raise RuntimeError("R37 unexpectedly grants experiment authority")
    pin = r37["candidate"]["content_addressing"]
    if pin["repository_commit_sha"] != "d3311e28abf9328ec5377c640763f79b9df5b9c9":
        raise RuntimeError("RoMeRL pinned revision drift")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R38-ROMERL-EXACT-INFORMATION-GATE",
        "recorded_date": "2026-08-25",
        "status": "ROMERL_G1_G2_G3_PASS_BUNDLED_CHECKPOINT_STOP_AT_G4_NO_CONFIRMATORY_EXECUTION_AUTHORITY",
        "role": "ZERO_OUTCOME_EXACT_INFORMATION_CLOSURE_AND_FRESH_CAPACITY_ADJUDICATION",
        "scientific_relationship": "POST_R37_OFFLINE_DESIGN_AUDIT_NOT_R19_RESUME_NOT_CONFIRMATORY_EVIDENCE",
        "parent_bindings": {
            "romerl_substrate_audit_r37": {"path": str(R37), "sha256": _sha(R37)},
            "exact_information_adapter": {"path": str(ADAPTER), "sha256": _sha(ADAPTER)},
        },
        "pinned_external_surface": {
            "repository": "https://github.com/YOUNG-fnxm/RoMeRL",
            "commit_sha": "d3311e28abf9328ec5377c640763f79b9df5b9c9",
            "release_mode": "evaluation-only active-slot checkpoint export",
            "benchmark_universes": {
                "OSInteraction": 500,
                "DBBench": 500,
            },
            "paper_transfer_partition": {
                "rule": "fixed 7:3 random split",
                "seed": 42,
                "applies_to": ["OSInteraction", "DBBench"],
                "split_is_not_embedded_in_bundled_romerl_runner": True,
            },
        },
        "G3_exact_information": {
            "passed_now": True,
            "state": "PASS_POST_RETRIEVAL_EXACT_INFORMATION_ADAPTER_OFFLINE",
            "minimum_identification_arms": [
                "content-only provenance-hidden",
                "same actionable content plus truthful raw source-outcome provenance",
            ],
            "treatment_field": "source_outcome_success",
            "held_fixed": [
                "retrieval membership",
                "retrieval cardinality",
                "retrieval order",
                "actionable content bytes",
                "query-conditioned upstream retrieval result",
            ],
            "not_executor_visible": [
                "memory_id",
                "query bookkeeping",
                "similarity",
                "Q estimate",
                "memory role",
                "other metadata",
            ],
            "fail_closed_rules": [
                "missing metadata.success rejects the row",
                "non-boolean metadata.success rejects the row",
                "the adapter never flips or synthesizes provenance",
                "the adapter runs only after retrieval is frozen",
            ],
            "unit_tests": {"passed": 6, "total": 6},
            "pinned_checkpoint_integration": {
                "OSInteraction": {
                    "rows_checked": 32,
                    "source_outcome_success_true": 21,
                    "source_outcome_success_false": 11,
                    "actionable_content_identical": True,
                    "retrieval_order_preserved": True,
                    "retrieval_cardinality_preserved": True,
                    "q_or_role_exposed_to_executor": False,
                    "frozen_retrieval_sha256": "437977d7c928aee835c018c82b8ce292b6f936ad9073ead7d9d484ba51ceaa5c",
                },
                "DBBench": {
                    "rows_checked": 32,
                    "source_outcome_success_true": 15,
                    "source_outcome_success_false": 17,
                    "actionable_content_identical": True,
                    "retrieval_order_preserved": True,
                    "retrieval_cardinality_preserved": True,
                    "q_or_role_exposed_to_executor": False,
                    "frozen_retrieval_sha256": "a72c640541a6aad7a485fd45809f503f523717952108b7c1cd12df04d57a6b53",
                },
                "selection_rule": "deterministic outcome-blind first 32 active memory IDs in sorted task/role traversal; schema integration only, not an inference sample",
                "model_calls": 0,
                "environment_actions": 0,
                "outcome_measurements": 0,
            },
            "scientific_interpretation": "RoMeRL can support the frozen hidden-versus-raw-provenance identification contrast without changing actionable memory content once retrieval has been frozen. This closes intervention design only; it is not a behavioral result.",
        },
        "G4_fresh_capacity": {
            "passed_now": False,
            "state": "STOP_CURRENT_BUNDLED_CHECKPOINT_TASK_UNIVERSE_ALREADY_SOURCE_EXPOSED",
            "frozen_reference_independent_units": 32,
            "raw_manifest_counts_are_not_inference_units": True,
            "source_memory_task_coverage": {
                "OSInteraction": {
                    "benchmark_task_universe": 500,
                    "unique_task_ids_with_active_source_memory": 498,
                    "task_ids_without_active_source_memory_upper_bound": 2,
                    "can_supply_32_task_level_unexposed_units": False,
                },
                "DBBench": {
                    "benchmark_task_universe": 500,
                    "unique_task_ids_with_active_source_memory": 500,
                    "task_ids_without_active_source_memory_upper_bound": 0,
                    "can_supply_32_task_level_unexposed_units": False,
                },
            },
            "logic": [
                "the paper's 7:3 validation split is drawn from the same 500-task OS/DB universes",
                "the bundled DB checkpoint has active provenance-bearing source memories for all 500 task IDs",
                "the bundled OS checkpoint has active provenance-bearing source memories for 498 of 500 task IDs",
                "therefore no choice of a held-out subset from those same universes can produce at least 32 task-level units that were unexposed to the bundled source-memory checkpoint",
                "the exact seed-42 membership list is not needed for this upper-bound argument",
            ],
            "forbidden_shortcuts": [
                "count 500 checkpoint tasks as 500 fresh future units",
                "use the paper's 30% validation set while retaining a checkpoint that already contains source memories from those task IDs",
                "declare within-task later episodes independent fresh tasks without a prospective cluster/episode estimand",
                "rebuild a train-only RoMeRL checkpoint because writer/update code is not released",
                "shrink the 32-unit reference because only two OS task IDs remain unexposed",
            ],
            "what_would_reopen_G4": [
                "a first-party/source-faithful RoMeRL checkpoint generated only from a prospectively frozen source split, leaving at least 32 disjoint future task units",
                "a newly released provenance-bearing RoMeRL checkpoint on a separate task universe with prospectively auditable source/future separation",
                "another substrate that already exposes source-outcome provenance and at least 32 source-disjoint future units without reconstructing unpublished writer dynamics",
            ],
            "current_bundled_checkpoint_confirmatory_eligible": False,
        },
        "gate_adjudication": {
            "G1_RELEASE": True,
            "G2_PROVENANCE_SCHEMA": True,
            "G3_EXACT_INFORMATION": True,
            "G4_FRESH_CAPACITY": False,
            "G5_SUPPORT_AND_PREREGISTRATION": False,
            "G6_AUTHORITY": False,
            "gate_pass_now": False,
            "passed_stages_now": ["G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION"],
            "blocking_stage": "G4_FRESH_CAPACITY",
            "qualified_substrate_now": None,
        },
        "candidate_disposition": {
            "RoMeRL_bundled_checkpoint": "STOP_AS_FRESH_CONFIRMATORY_SUBSTRATE_AT_G4",
            "RoMeRL_schema_construct_witness": "KEEP",
            "RoMeRL_exact_information_adapter": "KEEP_AS_ZERO_OUTCOME_METHOD_ASSET",
            "SMA_watch": "KEEP_WAITING_FOR_FIRST_PARTY_CODE_RELEASE",
            "R19": "REMAINS_STOPPED",
            "same_asset_27": "REMAINS_NON_CONFIRMATORY_INVENTORY",
        },
        "claim_policy": {
            "new_scientific_behavioral_result": False,
            "provenance_only_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
            "RoMeRL_may_be_called_confirmatory_evidence": False,
            "RoMeRL_bundled_checkpoint_may_be_executed_for_B1_confirmation": False,
        },
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
        "next_action": "CONTINUE_BOUNDED_SUBSTRATE_DISCOVERY_WITH_G1_TO_G4_PREOUTCOME_AUDIT_ONLY",
        "scientific_verdict": "NO_VERDICT_ROMERL_BUNDLED_CHECKPOINT_FAILS_FRESH_CAPACITY_WITHOUT_RELAXING_GATE",
    }


def main() -> None:
    payload = build()
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "G3": payload["gate_adjudication"]["G3_EXACT_INFORMATION"],
        "G4": payload["gate_adjudication"]["G4_FRESH_CAPACITY"],
        "gate_pass": payload["gate_adjudication"]["gate_pass_now"],
        "experiment_authority": payload["authority"]["experiment"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
