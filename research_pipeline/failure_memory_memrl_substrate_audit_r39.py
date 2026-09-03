#!/usr/bin/env python3
"""Adjudicate pinned MemRL as a fresh B1 substrate through G1-G4 only.

R39 is zero-outcome. It records public source/data structure and the local
post-retrieval exact-information adapter. It does not build memories, invoke
models, run LifelongAgentBench, measure treatment outcomes, or grant G5/G6.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R38 = Path("generated/d2-failure-memory-provenance-r38-romerl-exact-information-gate.json")
ADAPTER = Path("research_pipeline/failure_memory_memrl_exact_information_adapter_r39.py")
OUT = Path("generated/d2-failure-memory-provenance-r39-memrl-substrate-audit.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    r38 = _load(R38)
    if r38["candidate_disposition"]["RoMeRL_bundled_checkpoint"] != "STOP_AS_FRESH_CONFIRMATORY_SUBSTRATE_AT_G4":
        raise RuntimeError("RoMeRL R38 G4 stop drift")
    if r38["gate_adjudication"]["gate_pass_now"] or r38["authority"]["experiment"]:
        raise RuntimeError("R38 unexpectedly grants experiment authority")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R39-MEMRL-SUBSTRATE-AUDIT",
        "recorded_date": "2026-08-25",
        "status": "MEMRL_G1_G2_G3_G4_PASS_ADVANCE_TO_G5_ONLY_NO_CONFIRMATORY_EXECUTION_AUTHORITY",
        "role": "ZERO_OUTCOME_FRESH_SUBSTRATE_QUALIFICATION_THROUGH_G4",
        "scientific_relationship": "POST_R38_REPLACEMENT_SUBSTRATE_DISCOVERY_NOT_R19_RESUME_NOT_CONFIRMATORY_EVIDENCE",
        "parent_bindings": {
            "romerl_g4_stop_r38": {"path": str(R38), "sha256": _sha(R38)},
            "memrl_exact_information_adapter": {"path": str(ADAPTER), "sha256": _sha(ADAPTER)},
        },
        "candidate": {
            "name": "MemRL",
            "title": "MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory",
            "primary_paper": "https://arxiv.org/abs/2601.03192",
            "first_party_repository": "https://github.com/MemTensor/MemRL",
            "repository_commit_sha": "c1b322ca43de36ddf64c6712f89d0095bfc35ce0",
            "repository_commit_date": "2026-07-18T00:21:34+08:00",
            "repository_commit_subject": "fix: align retrieval similarity thresholds",
            "pinned_checkout_clean": True,
            "pinned_source_sha256": {
                "memrl/service/memory_service.py": "252ad7b09d1a53f9e6d6dc925b9b85b9bff1d9cc1bb4ea184dad8de890e363c3",
                "memrl/run/llb_rl_runner.py": "3d93d5992b7496194529e02d48e148c8c5217c3bf07f2f3783c62035fa48bc18",
                "configs/rl_llb_config.yaml": "792e14fdcdf36ad6133d48a5b9a4c91959d8998e33132395d56bcf8a2131040f",
                "run/run_llb.py": "aca29c9db00571bdded58f8f8c64ebc90fe6da10615334c5e8f04f63a83d4cbe",
            },
            "pinned_data_sha256": {
                "OSInteraction": {
                    "full": "06790c2137ef7765df198bb7e14617ce79f6c5fa1c092f6df39f6f6b7abd21c7",
                    "train": "d33513493856e6cdce2377a951a48a42686463eee1c92acb9d6b0a0320601e62",
                    "validation": "1804781d7e768e74cc9f9038fcdfcf373ff34d4edc668382d6d18cbf74f856d6",
                },
                "DBBench": {
                    "full": "5553dd87f528eaa814557d2e245eb2cfd69cfb7994233fb273049445d14b088a",
                    "train": "649446019101a10d8af65b7fcdeb06f56dd4d334b3a8d99839f9d1296b4891f9",
                    "validation": "0aa01f7405403106780ed1cc0ed270417254bb9889aa5126d0f2d4ce3bcfe0a9",
                },
            },
        },
        "G1_release": {
            "passed_now": True,
            "state": "PASS_FIRST_PARTY_PINNED_SOURCE_AND_DATA",
            "evidence": [
                "first-party public MemRL repository",
                "immutable clean source revision pinned",
                "source writer, LLB runner, config, launcher, and OS/DB train-validation data are present in the same pinned revision",
                "all audited source and split files are content-addressed in this receipt",
            ],
        },
        "G2_provenance_schema": {
            "passed_now": True,
            "state": "PASS_NATIVE_SOURCE_EPISODE_OUTCOME_WRITTEN_AS_SEPARATE_MEMORY_FIELD",
            "source_chain": [
                "LLB task execution derives trajectory success from the environment evaluation outcome",
                "training runner carries that same trajectory success into metadata.success with phase=train and task/sample identifiers",
                "add_memories uses metadata.setdefault(success, bool(source_success)) rather than replacing an upstream source label",
                "memory construction stores success and full_content as separate metadata fields",
                "retrieval returns full content, metadata, similarity, and later Q estimate as separable fields",
            ],
            "post_use_utility_separation": [
                "q_value is a separate metadata/cache field",
                "update_values maps later target episode success to a reward and updates retrieved memories' Q values",
                "the stored source metadata.success is therefore not identified with later retrieval utility or post-use reward",
            ],
            "important_boundary": "Source success can initialize Q and therefore affect native retrieval. B1's provenance-only contrast is consequently defined conditionally after retrieval is frozen; R39 does not relabel Q-mediated retrieval as a provenance-only treatment.",
        },
        "G3_exact_information": {
            "passed_now": True,
            "state": "PASS_POST_RETRIEVAL_HIDDEN_VS_RAW_PROVENANCE_ADAPTER_OFFLINE",
            "pinned_retriever_selected_schema": ["memory_id", "content", "metadata", "similarity", "q_estimate", "task_id", "score"],
            "minimum_identification_arms": [
                "content-only provenance-hidden",
                "identical frozen content plus truthful metadata.success as source_outcome_success",
            ],
            "held_fixed_before_arm_projection": [
                "selected memory IDs",
                "retrieval membership and cardinality",
                "retrieval order",
                "actionable full_content bytes",
                "similarity/Q/score values as audit-only upstream state",
            ],
            "never_executor_visible_as_treatment": ["memory_id", "task_id", "similarity", "q_estimate", "score", "memory role", "other metadata"],
            "adapter_unit_tests": {"passed": 5, "total": 5},
            "adapter_sha256": _sha(ADAPTER),
            "fail_closed": [
                "missing or non-boolean metadata.success rejects a selected row",
                "missing content or stable memory_id rejects a selected row",
                "adapter never flips, synthesizes, or infers provenance from wording",
                "adapter never reruns or alters retrieval",
            ],
            "model_calls": 0,
            "environment_actions": 0,
            "treatment_outcomes_observed": 0,
        },
        "G4_fresh_capacity": {
            "passed_now": True,
            "state": "PASS_PINNED_SOURCE_FUTURE_SPLITS_WITH_CLUSTER_CAPACITY_ABOVE_REFERENCE",
            "frozen_reference_independent_units": 32,
            "validation_is_read_only": True,
            "validation_write_operations_found": 0,
            "source_memory_and_q_updates_are_training_loop_only": True,
            "OSInteraction": {
                "full_tasks": 500,
                "source_train_tasks": 350,
                "future_validation_tasks": 150,
                "train_validation_key_overlap": 0,
                "train_validation_raw_entry_hash_overlap": 0,
                "train_validation_exact_instruction_overlap": 0,
                "train_validation_exact_ground_truth_script_overlap": 0,
                "train_validation_normalized_instruction_overlap": 0,
                "validation_skill_signature_clusters": 148,
                "validation_singleton_skill_signature_clusters": 147,
                "largest_validation_skill_signature_cluster_size": 3,
                "cluster_capacity_exceeds_reference": True,
            },
            "DBBench": {
                "full_tasks": 500,
                "source_train_tasks": 361,
                "future_validation_tasks": 139,
                "train_validation_key_overlap": 0,
                "train_validation_exact_instruction_overlap": 0,
                "train_validation_normalized_instruction_overlap": 0,
                "train_validation_exact_answer_sql_overlap": 0,
                "train_validation_answer_md5_overlap": 0,
                "train_validation_table_schema_overlap": 1,
                "validation_skill_signature_clusters": 76,
                "validation_singleton_skill_signature_clusters": 44,
                "largest_validation_skill_signature_cluster_size": 8,
                "cluster_capacity_exceeds_reference": True,
            },
            "unit_policy": {
                "raw_task_count_is_not_automatically_independence": True,
                "conservative_dependency_cluster": "exact sorted skill_list signature within benchmark",
                "primary_capacity_witness": "OSInteraction has 148 validation skill-signature clusters; DBBench has 76; each independently exceeds the frozen 32-unit planning reference",
                "semantic_transfer_overlap_is_not_called_provenance_leakage": "Training and validation may share skills by design; freshness requires source episode/task disjointness, while shared skill-family dependence is handled by prospective clustering rather than by pretending related tasks are independent.",
            },
            "preoutcome_freeze": "The public split, file hashes, collision rules, and cluster rule are fixed before any B1 MemRL treatment outcome is generated.",
        },
        "gate_adjudication": {
            "G1_RELEASE": True,
            "G2_PROVENANCE_SCHEMA": True,
            "G3_EXACT_INFORMATION": True,
            "G4_FRESH_CAPACITY": True,
            "G5_SUPPORT_AND_PREREGISTRATION": False,
            "G6_AUTHORITY": False,
            "gate_pass_now": False,
            "passed_stages_now": ["G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION", "G4_FRESH_CAPACITY"],
            "next_blocking_stage": "G5_SUPPORT_AND_PREREGISTRATION",
            "qualified_for_G5_now": "MemRL",
            "qualified_for_confirmatory_execution_now": None,
        },
        "candidate_disposition": {
            "MemRL": "ADVANCE_TO_G5_SUPPORT_AND_PREREGISTRATION_AUDIT_ONLY",
            "preferred_primary_capacity_surface": "OSInteraction",
            "secondary_replication_capacity_surface": "DBBench",
            "RoMeRL_bundled_checkpoint": "KEEP_STOPPED_AT_G4",
            "RoMeRL_schema_construct_witness": "KEEP",
            "SMA": "KEEP_WATCHING_FIRST_PARTY_CODE_RELEASE",
            "R19": "REMAINS_STOPPED",
            "same_asset_27": "REMAINS_NON_CONFIRMATORY_INVENTORY",
        },
        "G5_requirements_not_yet_satisfied": [
            "freeze exact MemRL algorithm/build/retrieval/update configuration and all model/provider identities before source execution",
            "verify benchmark runtime reset/isolation, evaluator determinism/support, and retry/stop semantics without using confirmatory treatment outcomes",
            "freeze primary endpoint/estimand, task or cluster-level inference, arm order/randomization, exclusions, missingness, multiplicity, and interval/test rules",
            "freeze the hidden/raw identification arms and, if PSMG efficacy is tested, PSMG plus strongest same-information non-provenance controller",
            "define a source-build qualification gate that fails closed if both provenance polarities or sufficient retrievable source support are not produced",
        ],
        "claim_policy": {
            "new_scientific_behavioral_result": False,
            "provenance_only_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
            "MemRL_may_be_called_fresh_confirmatory_evidence": False,
            "MemRL_may_be_called_execution_ready": False,
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
        "next_action": "BUILD_ZERO_OUTCOME_G5_SUPPORT_AND_PREREGISTRATION_CONTRACT_FOR_PINNED_MEMRL",
        "scientific_verdict": "NO_VERDICT_MEMRL_IS_FIRST_CURRENT_G1_TO_G4_QUALIFIED_SUBSTRATE_CANDIDATE",
    }


def main() -> None:
    payload = build()
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "passed": payload["gate_adjudication"]["passed_stages_now"],
        "next": payload["gate_adjudication"]["next_blocking_stage"],
        "experiment_authority": payload["authority"]["experiment"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
