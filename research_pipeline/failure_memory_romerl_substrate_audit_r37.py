#!/usr/bin/env python3
"""Record a zero-outcome RoMeRL substrate audit for B1's fresh-confirmatory gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R35 = Path("generated/d2-failure-memory-provenance-r35-fresh-confirmatory-reopen-gate.json")
R36 = Path("generated/d2-failure-memory-provenance-r36-psmg-manuscript-projection.json")
OUT = Path("generated/d2-failure-memory-provenance-r37-romerl-substrate-audit.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    r35 = _load(R35)
    r36 = _load(R36)
    if r35["status"] != "WAIT_FOR_NEW_PROVENANCE_BEARING_SUBSTRATE_NO_CONFIRMATORY_EXECUTION_AUTHORITY":
        raise RuntimeError("R35 fresh-confirmatory gate status drift")
    if r35["fresh_substrate_reopen_gate"]["gate_pass_now"]:
        raise RuntimeError("R35 unexpectedly authorizes confirmatory execution")
    if any(r35["hard_non_reopen_rules"].values()):
        raise RuntimeError("R35 hard non-reopen boundary drift")
    if r36["status"] != "MANUSCRIPT_DESIGN_LOOP_PROJECTED_NO_SCIENTIFIC_CLAIM_EXPANSION":
        raise RuntimeError("R36 PSMG manuscript projection status drift")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R37-ROMERL-SUBSTRATE-AUDIT",
        "recorded_date": "2026-08-25",
        "status": "ROMERL_PUBLIC_SUBSTRATE_FOUND_SOURCE_LEVEL_AUDIT_ONLY_NO_CONFIRMATORY_EXECUTION_AUTHORITY",
        "role": "ZERO_OUTCOME_SOURCE_LEVEL_SUBSTRATE_AUDIT_NO_EXECUTION_AUTHORITY",
        "scientific_relationship": "POST_R35_BOUNDED_RELEASE_SCAN_NOT_R19_RESUME_NOT_CONFIRMATORY_EVIDENCE",
        "parent_bindings": {
            "fresh_confirmatory_gate": {"path": str(R35), "sha256": _sha(R35)},
            "psmg_manuscript_projection": {"path": str(R36), "sha256": _sha(R36)},
        },
        "candidate": {
            "name": "RoMeRL",
            "title": "RoMeRL: Balancing Feedback Coverage and the Memory-Reward Trap in Self-Evolving Agent Memory via Reduced-Order Utility States",
            "primary_paper": "https://arxiv.org/abs/2608.02508",
            "first_party_repository": "https://github.com/YOUNG-fnxm/RoMeRL",
            "release_snapshot_date": "2026-08-25",
            "construct_signal": {
                "paper_describes_outcome_polarity": True,
                "paper_describes_new_experiences_entering_fixed_semantic_coordinates": True,
                "public_runtime_roles": ["best_success", "latest_failure", "best_failure", "recovery"],
                "public_memory_metadata_includes_success": True,
                "public_runtime_categorizes_by_metadata_success": True,
                "retrieval_returns_content_and_metadata_as_separate_fields": True,
            },
            "release_boundary": {
                "evaluation_only": True,
                "read_only_task_slot_runtime": True,
                "memory_construction_released": False,
                "memory_insertion_released": False,
                "role_replacement_or_promotion_released": False,
                "q_learning_or_reward_propagation_released": False,
                "checkpoint_creation_or_training_resume_released": False,
                "full_inactive_history_released": False,
            },
            "public_checkpoint_inventory": {
                "OSInteraction": {
                    "task_count": 500,
                    "query_count": 498,
                    "active_memory_count": 679,
                    "metadata_fields_include": ["full_content", "memory_role", "memory_roles", "q_value", "sample_index", "slot_task_id", "source_benchmark", "steps", "success", "task_id", "type"],
                    "public_file_sha256": {
                        "dict_memory.json.gz": "a27fe250e76b8dc79c69635df3d9b61fab78fc7bb65a1683170cff0fbc3c04ce",
                        "mem_cache.json.gz": "b21cd94cbd3394a133e4c3382cec6d29fd7b0bf7ebf540fd6907761fdcc60f5a",
                        "q_cache.json.gz": "d577f3ebe23a0d4bdbb891f033e91345f28b3956436192f51a4cf4104aa6a2f6",
                        "query_embeddings.json.gz": "c054b360788c4c631e7527a5d96ca09d60658d8827a632d6694ef40fac465d8f",
                        "task_slot_index.json.gz": "be79f99c2a63535edcd82e5332510707f800a80ed514407beacefc68611bfb79",
                    },
                },
                "DBBench": {
                    "task_count": 500,
                    "query_count": 500,
                    "active_memory_count": 1051,
                    "metadata_fields_include": ["full_content", "memory_role", "memory_roles", "q_value", "sample_index", "slot_task_id", "source_benchmark", "steps", "success", "task_id", "type"],
                    "public_file_sha256": {
                        "dict_memory.json.gz": "f83a37e2808eadd96bfe59636061b3025061fa1778f4fc3377d6e0b7251ffc01",
                        "mem_cache.json.gz": "1e26d4fb2685f56ca7e313ed4665d9a8c3557f6d7afb8f1607d54e839b08a732",
                        "q_cache.json.gz": "cd3155115f652b3d57893fcf24fd8e099665cbe15e1559fdfffe601f29ddd8ea",
                        "query_embeddings.json.gz": "48cd067e02ad905aa2b5bb6e8c177f9dcddcd14a6862b6e092136d24ef4bdc2d",
                        "task_slot_index.json.gz": "bdfd7bc0ce080fb4c54b5c4fadb641904825dc70bcc162d75de1e4edc95384fe",
                    },
                },
                "raw_task_count_total": 1000,
                "raw_active_memory_count_total": 1730,
                "raw_inventory_is_not_confirmatory_unit_count": True,
            },
            "content_addressing": {
                "checkpoint_payload_hashes_published_by_first_party": True,
                "repository_commit_sha_pinned_in_this_audit": True,
                "repository_commit_sha": "d3311e28abf9328ec5377c640763f79b9df5b9c9",
                "repository_commit_date": "2026-08-14T10:41:26+08:00",
                "repository_commit_subject": "Update README.md",
                "pinned_checkout_clean": True,
                "all_ten_checkpoint_payload_hashes_verified_against_first_party_manifests": True,
                "interpretation": "The first-party source revision and all ten public checkpoint payloads are now immutably pinned and locally verified without model or environment execution.",
            },
            "provenance_schema_audit": {
                "paper_specification": "Each observed trajectory m_i carries source outcome y_i in {0,1}; positive coordinates select successful trajectories and negative coordinates select failed trajectories.",
                "checkpoint_field": "metadata.success",
                "checkpoint_role_semantics": {
                    "best_success": True,
                    "recovery": True,
                    "best_failure": False,
                    "latest_failure": False,
                },
                "OSInteraction": {
                    "active_memories": 679,
                    "metadata_success_true": 421,
                    "metadata_success_false": 258,
                    "role_pointer_occurrences": {"best_success": 419, "best_failure": 191, "latest_failure": 67, "recovery": 7},
                    "missing_pointer_targets": 0,
                    "role_vs_success_mismatches": 0,
                },
                "DBBench": {
                    "active_memories": 1051,
                    "metadata_success_true": 482,
                    "metadata_success_false": 569,
                    "role_pointer_occurrences": {"best_success": 480, "best_failure": 440, "latest_failure": 129, "recovery": 24},
                    "missing_pointer_targets": 0,
                    "role_vs_success_mismatches": 0,
                },
                "audit_interpretation": "The paper-level generation semantics, separable checkpoint field, read-only runtime use of metadata.success, and zero role/outcome mismatches jointly identify metadata.success as an auditable source-trajectory outcome provenance field rather than a value inferred from memory wording or the later Q utility.",
            },
        },
        "gate_adjudication": {
            "G1_RELEASE": {
                "passed_now": True,
                "state": "PASS_FIRST_PARTY_PINNED_SOURCE_AND_CONTENT_ADDRESSED_CHECKPOINTS",
                "positive_evidence": [
                    "first-party public repository exists",
                    "repository revision d3311e28abf9328ec5377c640763f79b9df5b9c9 is immutably pinned",
                    "two frozen evaluation checkpoints are public",
                    "first-party manifests publish SHA-256 hashes for checkpoint payloads",
                    "all ten checkpoint payload hashes were verified on the pinned clean checkout",
                ],
                "blocker": None,
            },
            "G2_PROVENANCE_SCHEMA": {
                "passed_now": True,
                "state": "PASS_NATIVE_SOURCE_OUTCOME_PROVENANCE_AUDITED_FROM_PAPER_AND_PINNED_CHECKPOINT",
                "positive_evidence": [
                    "paper Section 5.1 defines every observed trajectory m_i with binary source outcome y_i and uses y_i to select positive versus negative memory coordinates",
                    "pinned public checkpoint metadata stores success as a separate field",
                    "pinned public runtime categorizes memories directly from metadata.success rather than inferring outcome from wording",
                    "all active slot pointers resolve and best_success/recovery versus best_failure/latest_failure have zero metadata.success polarity mismatches across both public checkpoints",
                    "Q utility remains a distinct field and retrieval signal, so provenance is not identified with later Q utility",
                ],
                "blocker": None,
                "write_side_code_released": False,
                "why_pass_remains_valid": "The first-party paper specifies the generation-time outcome variable and coordinate semantics, while the pinned source-faithful checkpoint/runtime independently exposes and preserves that outcome as metadata.success. Full writer implementation is not required to infer provenance from wording and is not being substituted with post-use reward.",
            },
            "G3_EXACT_INFORMATION": {
                "passed_now": False,
                "state": "DESIGNABLE_AFTER_RETRIEVAL_NOT_YET_VERIFIED",
                "positive_evidence": [
                    "retrieval returns actionable content and metadata separately",
                    "a prospective executor-visible provenance-hidden versus raw-provenance arm is structurally conceivable without rewriting the actionable content",
                ],
                "required_design": [
                    "freeze retrieved memory IDs, candidate set, order, content bytes, similarity, Q, and all non-provenance evidence before treatment",
                    "content-only arm hides source-outcome provenance from the executor",
                    "raw-provenance arm exposes only the audited immutable source-outcome field",
                    "do not change role, Q, retrieval score, TRS, verification, or memory wording across the two identification arms",
                    "if PSMG is evaluated, add executor-blind PSMG and strongest same-information non-provenance controller as prospectively frozen arms",
                ],
                "blocker": "exact-information switch has not been implemented or source-audited on a pinned revision",
            },
            "G4_FRESH_CAPACITY": {
                "passed_now": False,
                "state": "RAW_CAPACITY_PROMISING_INDEPENDENT_UNIT_CENSUS_NOT_FROZEN",
                "positive_evidence": [
                    "public checkpoint manifests report 500 OS tasks and 500 DB tasks",
                    "public checkpoint manifests report 1730 active memories in total",
                ],
                "blocker": "raw tasks/memories cannot be counted as independent confirmatory units until provenance eligibility, exact-information pairing, source/future-task separation, clustering, and overlap rules are prospectively audited",
                "minimum_reference_independent_units": 32,
            },
            "G5_SUPPORT_AND_PREREGISTRATION": {
                "passed_now": False,
                "state": "NOT_STARTED",
                "blocker": "no pinned-runtime support qualification or frozen confirmatory analysis contract exists",
            },
            "G6_AUTHORITY": {
                "passed_now": False,
                "state": "NOT_GRANTED",
                "blocker": "no new RoMeRL scientific experiment or execution authority has been granted",
            },
            "all_stages_required": True,
            "gate_pass_now": False,
            "passed_stages_now": ["G1_RELEASE", "G2_PROVENANCE_SCHEMA"],
            "next_blocking_stage": "G3_EXACT_INFORMATION",
            "qualified_substrate_now": None,
        },
        "candidate_watch_update": {
            "best_available_immediate_source_level_audit_target": "RoMeRL",
            "cleanest_native_construct_candidate_waiting_release": "Spatial Memory Agent (SMA)",
            "SMA_reopen_trigger_observed": False,
            "R19_reopen": False,
            "same_asset_27_promoted_to_confirmatory": False,
            "reason": "RoMeRL provides the first newly found public content-addressed checkpoint/schema surface worth deeper zero-outcome audit, but its write-side provenance origin remains unreleased; SMA remains the cleaner native process-provenance watch candidate.",
        },
        "next_zero_outcome_actions": [
            "compile and test an exact-information intervention adapter that acts only after retrieval has been frozen, without invoking models or environments",
            "enumerate prospectively eligible independent units and establish the public 7:3 LifelongAgentBench split semantics against the pinned checkpoint before treating any raw task as fresh confirmatory capacity",
            "freeze a support qualification and confirmatory analysis contract only if G3 and G4 pass",
            "only after G1-G5 pass, request a new explicitly named G6 scientific execution authority independent of R19",
        ],
        "claim_policy": {
            "new_scientific_result_from_R37": False,
            "provenance_only_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
            "may_describe_RoMeRL_as_confirmatory_evidence": False,
            "may_describe_RoMeRL_as_execution_ready": False,
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
        "scientific_verdict": "NO_VERDICT_ROMERL_ADVANCES_SUBSTRATE_DISCOVERY_NOT_CONFIRMATORY_AUTHORITY",
    }


def main() -> None:
    payload = build()
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "gate_pass": payload["gate_adjudication"]["gate_pass_now"],
        "best_audit_target": payload["candidate_watch_update"]["best_available_immediate_source_level_audit_target"],
        "experiment_authority": payload["authority"]["experiment"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
