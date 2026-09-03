#!/usr/bin/env python3
"""Freeze the prospective B1 MemRL full-350 source program (R53).

R53 is a new scientific lineage after the R51 support stop.  It does not append
or resume the 128-source R45-M1 bank.  The source universe is the complete
350-task frozen MemRL OSInteraction training split, ordered by the original R43
hash rule.  Fresh validation clusters are selected only after source build by a
pre-frozen, validation-outcome-blind native-support rule.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PARENT = ROOT / "generated/d2-failure-memory-provenance-r45m1-host-migration-execution-manifest-v2.json"
R51 = ROOT / "generated/d2-failure-memory-provenance-r51-r45m1-support-stop-adjudication.json"
R52 = ROOT / "generated/d2-failure-memory-provenance-r52-support-root-cause-diagnostic-20260902.json"
MODEL = ROOT / "generated/d2-failure-memory-provenance-r45m1-model-identity-evidence.json"
RUNNER = ROOT / "research_pipeline/failure_memory_memrl_source_execute_r53.py"

CONTRACT = ROOT / "generated/d2-failure-memory-provenance-r53-full350-ab-program-contract.json"
MANIFEST = ROOT / "generated/d2-failure-memory-provenance-r53-full350-source-execution-manifest.json"
AUTH = ROOT / "generated/d2-failure-memory-provenance-r53-full350-source-execution-authority.json"

SOURCE_SEED = "B1-R43-SOURCE-20260829"
SOURCE_COUNT = 350
SOURCE_ORDER_SHA256 = "a8b8f519e41522d4222e5cadde214b5c7318b7c307a620fbd0c8c9827c0443f4"
SOURCE_SPLIT_SHA256 = "d33513493856e6cdce2377a951a48a42686463eee1c92acb9d6b0a0320601e62"
VALIDATION_SEED = "B1-R53-VALIDATION-20260902"
MANIFEST_STATUS = "MEMRL_R53_FULL350_SOURCE_EXECUTION_MANIFEST_FROZEN_ZERO_VALIDATION_OUTCOMES"
AUTH_STATUS = "HUMAN_BOUNDED_R53_FULL350_SOURCE_EXECUTION_AUTHORITY_RECORDED"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"not-object:{path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def seal(value: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(value)
    out.pop("receipt_sha256", None)
    out["receipt_sha256"] = digest(out)
    return out


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_contract() -> dict[str, Any]:
    return seal({
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R53-FULL350-AB-PROGRAM-CONTRACT",
        "recorded_date": "2026-09-02",
        "status": "PROSPECTIVE_FULL350_AB_PROGRAM_FROZEN_PRE_SOURCE_OUTCOME",
        "role": "NEW_SCIENTIFIC_LINEAGE_AFTER_R51_SUPPORT_STOP",
        "scientific_question": "After actionable memory content and frozen retrieval are fixed, does truthful source-outcome provenance add terminal task value beyond content alone?",
        "pilot_boundary": {
            "R45_M1_128_source": "PILOT_SUPPORT_EVIDENCE_ONLY",
            "R51": "SUPPORT_STOP_NO_BEHAVIORAL_VERDICT",
            "R52": "POST_STOP_ROOT_CAUSE_DIAGNOSTIC_ONLY",
            "reuse_old_source_memories_or_checkpoints": False,
            "pool_old_validation_or_confirmatory_outcomes": False,
            "old_40_validation_clusters_eligible_for_R53": False,
        },
        "source_program": {
            "split": "data/llb/os_interaction_train.json",
            "split_sha256": SOURCE_SPLIT_SHA256,
            "universe": "ALL_TASKS_IN_FROZEN_SPLIT",
            "count": SOURCE_COUNT,
            "order_rule": f"ascending SHA256({SOURCE_SEED}|task_id)",
            "seed_string": SOURCE_SEED,
            "ordered_ids_sha256": SOURCE_ORDER_SHA256,
            "batch_size": 1,
            "max_steps": 15,
            "retrieve_k": 10,
            "similarity_threshold": 0.5,
            "attempts": 1,
            "checkpoint_after_each_unit": True,
            "no_skip_or_replacement": True,
        },
        "fresh_validation_program": {
            "split": "data/llb/os_interaction_val.json",
            "split_sha256": "1804781d7e768e74cc9f9038fcdfcf373ff34d4edc668382d6d18cbf74f856d6",
            "cluster_unit": "exact sorted skill_list signature",
            "exclude": "all 40 R43 primary/utilization cluster signatures",
            "candidate_rank_rule": f"ascending SHA256({VALIDATION_SEED}|cluster|joined_signature)",
            "representative_rule": f"minimum SHA256({VALIDATION_SEED}|member|task_id) within cluster",
            "support_is_measured_before_any_validation_environment_reset": True,
            "native_retrieval": {"k": 10, "similarity_threshold": 0.5},
            "eligible_cluster": "native frozen retrieval has >=1 memory with nonempty content, source_task_id in the full350 source universe, and boolean source_outcome_success",
            "primary_selection": "first 32 eligible clusters in frozen candidate rank order",
            "utilization_selection": "next 8 eligible clusters in frozen candidate rank order",
            "minimum_eligible_clusters": 40,
            "require_both_source_provenance_polarities_retrievable": True,
            "selection_uses_validation_outcomes": False,
            "selected_ids_and_retrieval_are_frozen_before_first_treatment": True,
        },
        "utilization_gate": {
            "arms": ["U0_no_memory", "U1_true_memory", "U2_null_memory", "U3_reversed_memory", "U4_shuffled_memory"],
            "primary_endpoint": "first executable action",
            "pass_rule": ">=3/8 U1 differs from both U0 and U2 AND U1-specific divergence >= U2-vs-U0 divergence + 1",
            "terminal_success": "diagnostic_only",
            "primary_A_B_opens_only_if_pass": True,
        },
        "AB_confirmatory": {
            "arms": ["A_content_only", "B_raw_provenance"],
            "retrieval_rerun_between_arms": False,
            "actionable_content_byte_match_required": True,
            "only_executor_visible_difference": "truthful source_outcome_success",
            "primary_endpoint": "native LLB OSInteraction terminal success",
            "inference_unit": "fresh exact skill_list-signature dependency cluster",
            "estimand": "B_raw_provenance - A_content_only",
            "confidence_interval": "95% paired cluster interval",
            "test": "exact two-sided paired sign-flip/randomization test",
            "effect_relevance_floor": 0.15,
            "no_historical_pooling": True,
            "no_interim_effect_inspection": True,
            "no_optional_stopping": True,
        },
        "PSMG_CD": {
            "execution": False,
            "reason": "pre-outcome executable controller remains underdetermined; R53 is the clean L2 A/B identification experiment only",
        },
        "hard_limits": {
            "source_unit_replacement": False,
            "threshold_change_after_source_outcome": False,
            "model_or_runtime_change": False,
            "validation_outcome_driven_selection": False,
            "reuse_R51_results": False,
            "partial_effect_inspection": False,
            "second_source_attempt": False,
        },
        "authority": {"source_execution": False, "validation_execution": False, "claim_expansion": False},
    })


def build_manifest(contract: dict[str, Any]) -> dict[str, Any]:
    parent = load(PARENT)
    old = parent["execution_manifest"]
    execution = {key: copy.deepcopy(old[key]) for key in (
        "host", "source", "external_runtime_adapter", "models", "runtime_image", "memoryos_internal", "source_build", "stopping", "persistence"
    )}
    sb = execution["source_build"]
    sb["selection_rule"] = "all task IDs in frozen train split ordered by ascending SHA256(B1-R43-SOURCE-20260829|task_id)"
    sb["selection_seed_string"] = SOURCE_SEED
    sb["selected_count"] = SOURCE_COUNT
    sb["selected_ids_sha256"] = SOURCE_ORDER_SHA256
    sb.pop("selected_ids", None)
    sb["execution_order"] = "materialize all frozen split IDs by selection_rule; ordered-ID SHA must equal selected_ids_sha256 before first task"
    sb["qualification_before_validation"] = "R53 fresh support selector must freeze 32 primary + 8 utilization clusters before any validation treatment"
    return seal({
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R53-FULL350-SOURCE-EXECUTION-MANIFEST",
        "recorded_date": "2026-09-02",
        "role": "PROSPECTIVE_FULL_TRAIN_UNIVERSE_SOURCE_BUILD_ONLY",
        "status": MANIFEST_STATUS,
        "lineage": {"id": "R53-FULL350", "fresh_source_build": True, "resume_of_R45_M1": False, "source_attempt_count": 1},
        "bindings": {
            "program_contract": {"path": str(CONTRACT.relative_to(ROOT)), "file_sha256": sha(CONTRACT), "receipt_sha256": contract["receipt_sha256"]},
            "R51_stop": {"path": str(R51.relative_to(ROOT)), "file_sha256": sha(R51), "receipt_sha256": load(R51)["receipt_sha256"]},
            "R52_root_cause": {"path": str(R52.relative_to(ROOT)), "file_sha256": sha(R52), "receipt_sha256": load(R52)["receipt_sha256"]},
            "infrastructure_parent": {"path": str(PARENT.relative_to(ROOT)), "file_sha256": sha(PARENT), "receipt_sha256": parent["receipt_sha256"]},
        },
        "execution_manifest": execution,
        "validation_treatment_outcomes_observed": 0,
        "confirmatory_outcomes_observed": 0,
        "authority": {"execution": False, "scientific_claim_change": False},
    })


def build_authority(manifest: dict[str, Any]) -> dict[str, Any]:
    return seal({
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R53-FULL350-SOURCE-EXECUTION-AUTHORITY",
        "recorded_date": "2026-09-02",
        "status": AUTH_STATUS,
        "authorized_by": "explicit current-conversation user directive: run Scheme A full 350 because local execution consumes no external API quota",
        "lineage": {"replacement": "R53-FULL350", "resume_of_old_r45": False, "source_attempt_count": 1},
        "bindings": {
            "source_manifest": {"path": str(MANIFEST.relative_to(ROOT)), "sha256": sha(MANIFEST), "receipt_sha256": manifest["receipt_sha256"]},
            "program_contract": {"path": str(CONTRACT.relative_to(ROOT)), "sha256": sha(CONTRACT), "receipt_sha256": load(CONTRACT)["receipt_sha256"]},
            "model_identity": {"path": str(MODEL.relative_to(ROOT)), "sha256": sha(MODEL), "receipt_sha256": load(MODEL).get("receipt_sha256")},
            "source_runner": {"path": str(RUNNER.relative_to(ROOT)), "sha256": sha(RUNNER)},
        },
        "authorized_scope": {
            "source_build": {"authorized": True, "count": 1, "exact_selected_source_tasks": SOURCE_COUNT, "source_selection_sha256": SOURCE_ORDER_SHA256, "external_provider_spend": False},
            "fresh_validation_selection": {"authorized_after_source_complete": False},
            "utilization": {"authorized": False},
            "AB_confirmatory": {"authorized": False},
        },
        "replacement_limits": {"old_r45_remote_access": False, "old_r45_artifact_reuse": False, "partial_effect_inspection": False},
        "hard_limits": {"second_source_attempt": False, "skip_or_replace_source_unit": False, "model_or_embedding_change": False, "runtime_image_change": False, "threshold_change": False, "historical_pooling": False},
        "authority": {"execution": True, "local_gpu": True, "external_provider_spend": False, "validation_execution": False, "claim_expansion": False},
        "failure_routing": {"source_failure": "FAIL_CLOSED_R53_SOURCE_BUILD", "source_complete": "FREEZE_SOURCE_RECEIPT_THEN_RUN_ZERO_OUTCOME_FRESH_SUPPORT_SELECTION_ONLY"},
        "pre_authority_accounting": {"scientific_source_units_executed": 0, "validation_units_opened": 0, "confirmatory_outcomes_observed": 0},
    })


def main() -> None:
    contract = build_contract(); write_json(CONTRACT, contract)
    manifest = build_manifest(contract); write_json(MANIFEST, manifest)
    authority = build_authority(manifest); write_json(AUTH, authority)
    print(json.dumps({
        "contract_file_sha256": sha(CONTRACT), "contract_receipt_sha256": contract["receipt_sha256"],
        "manifest_file_sha256": sha(MANIFEST), "manifest_receipt_sha256": manifest["receipt_sha256"],
        "authority_file_sha256": sha(AUTH), "authority_receipt_sha256": authority["receipt_sha256"],
        "source_count": SOURCE_COUNT, "source_order_sha256": SOURCE_ORDER_SHA256,
        "validation_outcomes_observed": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
