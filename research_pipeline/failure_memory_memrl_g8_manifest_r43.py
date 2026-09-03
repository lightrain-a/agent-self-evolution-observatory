"""Freeze B1 MemRL's current G8 execution manifest before any confirmatory outcome.

R43 is a zero-outcome compiler. It binds the pinned MemRL source, local model
artifacts, local provider adapter, runtime image, deterministic source/validation
unit selection, arm realization, estimands, exclusions, analysis and stopping
rules. It grants no scientific or execution authority by itself.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PINNED_MEMRL = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"
DESIGN = PROJECT_ROOT / "research_pipeline" / "b1_process_provenance_governance_design_20260827.json"
R40 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r40-memrl-g5-preflight.json"
R42 = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r42-memrl-current-g1-g8-preflight.json"
MODEL_ID = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-model-identity-evidence.json"
UNIT_SELECTION = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-unit-selection-evidence.json"
IMAGE = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r42-memrl-image-compatibility-evidence.json"
IMAGE_ALIAS = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-image-alias-evidence.json"
ADAPTER = PROJECT_ROOT / "research_pipeline" / "failure_memory_memrl_local_runtime_r43.py"
LOCAL_SERVER = PROJECT_ROOT / "research_pipeline" / "failure_memory_memrl_local_openai_server_r43.py"
PY_RUNTIME = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-python-runtime-evidence.json"
SYNTHETIC_STACK = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-synthetic-stack-smoke.json"
SYNTHETIC_RUNNER = PROJECT_ROOT / "research_pipeline" / "failure_memory_memrl_synthetic_stack_smoke_r43.py"
OUT = PROJECT_ROOT / "generated" / "d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"

EXPECTED_LLM_MANIFEST = "c7e4242ce0f2ebd0700ce3c0ff8e24044a2dddc29f68ef8358993f66e60c153c"
EXPECTED_EMBED_MANIFEST = "ddd2853514c3aadf62ae9efd1751aac4ea3a7b8414b0da654b45f6915894a9e0"
EXPECTED_IMAGE_ID = "sha256:a42dc29f8d95292f261a309a21ba21ceff3a9edef516c54d40e5e9b51f253f1a"
EXPECTED_RUNTIME_TREE = "353284315ca6481db3010ff83a5791424f0fcbb4d3d1830b46b3bfba9626dd28"
EXPECTED_RUNTIME_MANIFEST = "ed146d1f040aaabbf8053ec821ba40e71085d98988b88ff5470ff465d6112cb6"
EXPECTED_RUNTIME_MANIFEST_FILE = "532c0da4ab3bcfaa9f02b18caa00cb77c62766c6b61ece5dc205dab18b4e1cc3"
EXPECTED_SYNTHETIC_RECEIPT = "abd02364984657e25430b26fe111225566adc1ae9bfc658f14392f93b092133e"


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
    design = _load(DESIGN)
    r40 = _load(R40)
    r42 = _load(R42)
    model_id = _load(MODEL_ID)
    units = _load(UNIT_SELECTION)
    image = _load(IMAGE)
    image_alias = _load(IMAGE_ALIAS)
    py_runtime = _load(PY_RUNTIME)
    synthetic = _load(SYNTHETIC_STACK)

    if design.get("paper_id") != PAPER_ID or r42.get("paper_id") != PAPER_ID:
        raise ValueError("paper-id-drift")
    r42_summary = r42.get("summary") or {}
    r42_gates = r42.get("current_gate_adjudication") or {}
    if int(r42_summary.get("passed") or 0) != 7 or r42_summary.get("blocking_gates") != ["G8"]:
        raise ValueError("r42-not-exactly-g8-hold")
    if any((r42_gates.get(key) or {}).get("pass") is not True for key in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")):
        raise ValueError("r42-g1-g7-drift")
    if int(r42_summary.get("confirmatory_validation_outcomes_observed") or 0) != 0:
        raise ValueError("pre-manifest-confirmatory-outcome-leak")

    llm = model_id.get("llm") or {}
    embed = model_id.get("embedding") or {}
    if llm.get("manifest_sha256") != EXPECTED_LLM_MANIFEST or embed.get("manifest_sha256") != EXPECTED_EMBED_MANIFEST:
        raise ValueError("model-identity-manifest-drift")
    if int(llm.get("file_count") or 0) < 10 or int(llm.get("bytes") or 0) < 10_000_000_000:
        raise ValueError("llm-artifact-incomplete")
    if int(embed.get("file_count") or 0) < 5 or int(embed.get("bytes") or 0) < 100_000_000:
        raise ValueError("embedding-artifact-incomplete")

    source_sel = units.get("source_selection") or {}
    val_sel = units.get("validation_selection") or {}
    util_sel = units.get("utilization_pilot_selection") or {}
    unit_access = units.get("outcome_blindness") or {}
    if int(source_sel.get("selected_count") or 0) != 128:
        raise ValueError("source-unit-count-drift")
    if int(val_sel.get("selected_cluster_count") or 0) != 32 or len(val_sel.get("selected_representative_ids") or []) != 32:
        raise ValueError("validation-unit-count-drift")
    if int(util_sel.get("selected_cluster_count") or 0) != 8 or util_sel.get("disjoint_from_primary") is not True:
        raise ValueError("utilization-pilot-unit-drift")
    support_proxy = units.get("support_proxy") or {}
    if support_proxy.get("primary_validation_skills_missing_from_source_union") != [] or support_proxy.get("utilization_pilot_skills_missing_from_source_union") != []:
        raise ValueError("source-skill-surface-does-not-cover-frozen-validation")
    if any(int(unit_access.get(k) or 0) != 0 for k in unit_access):
        raise ValueError("unit-selection-outcome-or-provider-leak")

    image_row = image.get("candidate_runtime_image") or {}
    image_access = image.get("access_accounting") or {}
    if image_row.get("id") != EXPECTED_IMAGE_ID or image.get("all_declared_skills_available") is not True:
        raise ValueError("runtime-image-incompatible")
    if any(int(image_access.get(k) or 0) != 0 for k in image_access):
        raise ValueError("image-qualification-outcome-or-provider-leak")
    alias_access = image_alias.get("access_accounting") or {}
    if image_alias.get("same_content_identity") is not True or image_alias.get("source_image_id") != EXPECTED_IMAGE_ID or image_alias.get("alias_image_id") != EXPECTED_IMAGE_ID or image_alias.get("required_pinned_llb_tag") != "local-os/default:latest":
        raise ValueError("runtime-image-alias-drift")
    if any(int(alias_access.get(k) or 0) != 0 for k in alias_access):
        raise ValueError("image-alias-outcome-or-provider-leak")
    packages = py_runtime.get("packages") or {}
    if (
        py_runtime.get("tree_sha256") != EXPECTED_RUNTIME_TREE
        or py_runtime.get("private_full_manifest_sha256") != EXPECTED_RUNTIME_MANIFEST
        or py_runtime.get("private_full_manifest_file_sha256") != EXPECTED_RUNTIME_MANIFEST_FILE
        or packages.get("MemoryOS") != "1.0.0"
        or packages.get("qdrant-client") != "1.15.1"
        or packages.get("chonkie") != "1.2.1"
    ):
        raise ValueError("python-runtime-tree-drift")
    synthetic_access = synthetic.get("access_accounting") or {}
    synthetic_freezes = synthetic.get("runtime_freezes") or {}
    if synthetic.get("receipt_sha256") != EXPECTED_SYNTHETIC_RECEIPT or synthetic.get("support_only") is not True or (synthetic.get("memory_service") or {}).get("built_memory_retrieved") is not True or int((synthetic.get("memory_service") or {}).get("checkpoint_visible_memories") or 0) != 1:
        raise ValueError("synthetic-stack-support-drift")
    if any(int(synthetic_access.get(k) or 0) != 0 for k in synthetic_access):
        raise ValueError("synthetic-stack-benchmark-or-provider-leak")
    if synthetic_freezes.get("chunker_tokenizer_or_token_counter") != "character" or int(synthetic_freezes.get("embedding_runtime_dimension") or 0) != 3072 or synthetic_freezes.get("loopback_only") is not True:
        raise ValueError("synthetic-stack-runtime-freeze-drift")
    if (synthetic.get("script") or {}).get("sha256") != _sha(SYNTHETIC_RUNNER):
        raise ValueError("synthetic-runner-drift")

    contract = r40.get("frozen_confirmatory_contract") or {}
    source_build = contract.get("source_build") or {}
    arms = contract.get("arms") or {}
    required_arms = {"A_content_only", "B_raw_provenance", "C_PSMG", "D_nonprovenance_controller"}
    if set(arms) != required_arms:
        raise ValueError("four-arm-contract-drift")

    execution_manifest = {
        "host": {
            "logical_name": "workstation3090",
            "ssh_identity": "yutong@222.20.126.60",
            "gpu_assignment": {"llm": "cuda:0", "embedding": "cuda:1", "environment": "cpu/docker"},
            "python": "/home/hdd/yutong/envs/vlm_fp_231_exact/bin/python3.11",
            "pythonpath": "/home/hdd/yutong/b1-memrl-r43-runtime/site",
            "runtime_tree_sha256": py_runtime.get("tree_sha256"),
            "runtime_manifest_sha256": py_runtime.get("private_full_manifest_sha256"),
            "runtime_manifest_file_sha256": py_runtime.get("private_full_manifest_file_sha256"),
            "runtime_packages": {key: py_runtime.get("packages", {}).get(key) for key in ("MemoryOS", "qdrant-client", "transformers", "openai", "docker", "tenacity")},
            "environment": {
                "PYTHONDONTWRITEBYTECODE": "1",
                "runtime_target_is_read_only_after_freeze": True,
            },
        },
        "source": {
            "repository": "https://github.com/MemTensor/MemRL",
            "checkout": "/home/hdd/yutong/b1-memrl-r41",
            "revision": PINNED_MEMRL,
            "clean_checkout_required": True,
            "pinned_source_file_sha256": {
                "memrl/service/memory_service.py": "252ad7b09d1a53f9e6d6dc925b9b85b9bff1d9cc1bb4ea184dad8de890e363c3",
                "memrl/run/llb_rl_runner.py": "3d93d5992b7496194529e02d48e148c8c5217c3bf07f2f3783c62035fa48bc18",
                "configs/rl_llb_config.yaml": "792e14fdcdf36ad6133d48a5b9a4c91959d8998e33132395d56bcf8a2131040f",
                "run/run_llb.py": "aca29c9db00571bdded58f8f8c64ebc90fe6da10615334c5e8f04f63a83d4cbe",
            },
        },
        "external_runtime_adapter": {
            "provider_path": str(ADAPTER.relative_to(PROJECT_ROOT)),
            "provider_sha256": _sha(ADAPTER),
            "loopback_server_path": str(LOCAL_SERVER.relative_to(PROJECT_ROOT)),
            "loopback_server_sha256": _sha(LOCAL_SERVER),
            "loopback_base_url": "http://127.0.0.1:18143/v1",
            "llm_model_id": "B1-Qwen2.5-7B-Instruct-r43",
            "embedding_model_id": "B1-all-mpnet-base-v2-isometric3072-r43",
            "network_scope": "loopback-only",
            "external_provider_calls": 0,
            "modifies_pinned_memrl_checkout": False,
        },
        "models": {
            "llm": {
                "family": "Qwen2.5-7B-Instruct",
                "root": llm.get("root"),
                "artifact_manifest_sha256": llm.get("manifest_sha256"),
                "file_count": llm.get("file_count"),
                "bytes": llm.get("bytes"),
                "device": "cuda:0",
                "temperature": 0.0,
                "max_new_tokens": 512,
                "external_api": False,
            },
            "embedding": {
                "family": "sentence-transformers/all-mpnet-base-v2",
                "root": embed.get("root"),
                "artifact_manifest_sha256": embed.get("manifest_sha256"),
                "file_count": embed.get("file_count"),
                "bytes": embed.get("bytes"),
                "native_dimension": 768,
                "runtime_dimension": 3072,
                "pooling": "attention-mask mean pooling then L2 normalization",
                "dimension_bridge": "repeat normalized 768-vector four times and divide every coordinate by sqrt(4)",
                "dimension_bridge_preserves_l2_norm_and_pairwise_cosine_exactly": True,
                "max_token_length": 384,
                "device": "cuda:1",
                "external_api": False,
            },
        },
        "runtime_image": {
            "qualified_tag": image_row.get("tag"),
            "execution_tag": image_alias.get("required_pinned_llb_tag"),
            "id": image_row.get("id"),
            "execution_tag_same_content_identity": image_alias.get("same_content_identity"),
            "declared_validation_skills": image.get("declared_skill_count"),
            "available_validation_skills": image.get("available_skill_count"),
            "source_default_image_equivalence_claimed": False,
            "role": "frozen confirmatory runtime realization",
        },
        "memoryos_internal": {
            "chat_backend": "openai-compatible loopback",
            "chat_model": "B1-Qwen2.5-7B-Instruct-r43",
            "embedding_backend": "universal_api/openai-compatible loopback",
            "embedding_model": "B1-all-mpnet-base-v2-isometric3072-r43",
            "vector_db_backend": "qdrant local mode",
            "vector_dimension": 3072,
            "distance_metric": "cosine",
            "chunker_backend": "sentence",
            "chunker_tokenizer_or_token_counter": "character",
            "chunk_size": 500,
            "chunk_overlap": 128,
            "min_sentences_per_chunk": 1,
            "network_dependent_gpt2_default_forbidden": True,
            "synthetic_stack_receipt_sha256": synthetic.get("receipt_sha256"),
        },
        "source_build": {
            "split": source_sel.get("split"),
            "split_sha256": source_sel.get("split_sha256"),
            "selection_rule": source_sel.get("rule"),
            "selection_seed_string": source_sel.get("seed_string"),
            "selected_count": source_sel.get("selected_count"),
            "selected_ids_sha256": source_sel.get("selected_ids_sha256"),
            "selected_ids": source_sel.get("selected_ids"),
            "num_sections": 1,
            "batch_size": 1,
            "max_steps": 15,
            "os_timeout_seconds": 20,
            "retrieve_k": 10,
            "bon": 0,
            "dataset_ratio": 1.0,
            "algorithm": "rl",
            "mode": "train",
            "random_seed": 20260825,
            "val_before_train": False,
            "valid_file": None,
            "valid_interval": 0,
            "test_interval": 0,
            "build_strategy": "proceduralization",
            "retrieve_strategy": "query",
            "update_strategy": "adjustment",
            "k_retrieve": 10,
            "max_keywords": 8,
            "confidence_threshold": 0.0,
            "memory_confidence": 100.0,
            "add_similarity_threshold": 0.99,
            "user_id": "b1_r43_memrl_source",
            "sim_norm_mean": 0.39,
            "sim_norm_std": 0.14,
            "enable_value_driven": True,
            "llb_use_z_score_normalization": True,
            "llb_q_floor": 0.0,
            "dedup_by_task_id": False,
            "memory_service_runtime": {
                "num_workers": 1,
                "db_max_concurrency": 1,
                "mem_cache_max_size": 10000,
                "q_cache_max_size": 1000000,
            },
            "execution_order": "exact selected_ids array order",
            "trace_jsonl_required": True,
            "checkpoint_after_each_source_unit": True,
            "source_unit_failure_rule": "stop at the first source execution/memory-write failure; do not skip, replace, or outcome-select a source unit",
            "resume_rule": "load the latest per-unit checkpoint and continue only source IDs absent from the durable completed-id ledger",
            "system_prompt": "pinned MemRL LLB_DEFAULT_SYSTEM_PROMPT transformed only by build_llb_system_prompt(task=os)",
            "rl": {
                "epsilon": 0.01, "tau": 0.35, "alpha": 0.3, "gamma": 0.0,
                "q_init_pos": 0.5, "q_init_neg": 0.5, "success_reward": 1.0,
                "failure_reward": 0.0, "sim_threshold_os": 0.50, "topk": 5,
                "novelty_threshold": 0.85, "weight_sim": 0.5, "weight_q": 0.5,
            },
            "qualification_before_validation": [
                "source build completes once with no scientific-exposure retry",
                "retrievable source memories include both metadata.success polarities",
                "all 32 selected validation dependency clusters retain at least one eligible frozen retrieval",
                "selected memory IDs/order/content bytes are frozen before arm projection",
                "failure of any qualification item yields SUPPORT_STOP_NO_VERDICT with zero validation treatment outcomes",
            ],
        },
        "utilization_qualification": {
            "split": val_sel.get("split"),
            "split_sha256": val_sel.get("split_sha256"),
            "rank_range": util_sel.get("rank_range"),
            "selected_cluster_count": util_sel.get("selected_cluster_count"),
            "representative_ids_sha256": util_sel.get("representative_ids_sha256"),
            "representative_ids": util_sel.get("selected_representative_ids"),
            "cluster_records": util_sel.get("selected_clusters"),
            "disjoint_from_primary": util_sel.get("disjoint_from_primary"),
            "arms": {
                "U0_no_memory": "no memory payload",
                "U1_true_memory": "frozen top retrieval content for the matching unit",
                "U2_null_memory": "same memory surface with an empty/no-op memory body",
                "U3_reversed_memory": "same retrieved procedural steps in deterministic reversed step order",
                "U4_shuffled_memory": "same memory surface with another utilization unit's frozen retrieved content assigned by seed 20260825",
            },
            "promotion_endpoint": "first executable action only; terminal success is recorded diagnostically but cannot decide promotion",
            "pass_rule": "at least 3/8 units have U1 first action different from both U0 and U2, and this U1-specific count exceeds the U2-vs-U0 divergence count by at least 1",
            "fail_route": "OPERATIONALIZATION_STOP_MEMORY_NOT_BEHAVIORALLY_USED; do not open primary 32 clusters",
            "primary_units_excluded_from_utilization_pilot": True,
        },
        "confirmatory_units": {
            "split": val_sel.get("split"),
            "split_sha256": val_sel.get("split_sha256"),
            "cluster_rule": val_sel.get("cluster_rule"),
            "selection_rule": val_sel.get("rule"),
            "selection_seed_string": val_sel.get("seed_string"),
            "selected_cluster_count": val_sel.get("selected_cluster_count"),
            "representative_ids_sha256": val_sel.get("representative_ids_sha256"),
            "representative_ids": val_sel.get("selected_representative_ids"),
            "cluster_records": val_sel.get("selected_clusters"),
            "statistical_n": "exact skill_list-signature dependency cluster",
            "seeds_and_requests_are_nested_repetitions": True,
            "opens_only_if_source_and_utilization_qualification_pass": True,
        },
        "arms": arms,
        "arm_realization": {
            "A_content_only": "freeze retrieval then expose actionable content only; raw source provenance hidden",
            "B_raw_provenance": "same frozen IDs/order/content bytes as A plus truthful metadata.success rendered only as source_outcome_success",
            "C_PSMG": "same frozen retrieval; provenance available to frozen PSMG controller only; executor gets approved actionable content with no raw provenance label",
            "D_nonprovenance_controller": "same frozen retrieval and same pre-outcome controller information as C except the provenance variable under test",
            "backend_only_relabel_negative_control": "change only a backend metadata copy not observable by executor/controller; predicted exact behavioral equivalence",
            "retrieval_rerun_between_arms": False,
            "actionable_content_byte_match_required": True,
        },
        "randomization": {
            "seed": 20260825,
            "unit": "selected validation dependency cluster representative",
            "arm_order": "per-unit deterministic permutation generated only after source qualification and retrieval freeze, before any treatment outcome",
            "no_outcome_adaptive_randomization": True,
        },
        "endpoints": {
            "primary": contract.get("primary_endpoint"),
            "secondary": contract.get("secondary_endpoints"),
            "evaluator": "pinned LifelongAgentBench native OSInteraction terminal evaluator",
            "no_endpoint_substitution_after_outcomes": True,
        },
        "estimands": {
            "identification": contract.get("identification_estimand"),
            "governance": contract.get("governance_estimand"),
            "scientific_object_estimands": design.get("estimands"),
        },
        "e0_e5_mapping": {
            "E0": "source provenance integrity, byte-match/retrieval-match audits, utilization witness, backend-only relabel equivalence",
            "E1": "A/B paired terminal success identifies content-controlled visible-provenance effect after frozen retrieval",
            "E2": "A/B plus C/D separate executor-visible and governor-mediated provenance channels; wider A0-A7 remains appendix/future decomposition unless preregistered before outcomes",
            "E3": "predeclared moderator analysis only; no subgroup may redefine the primary estimand",
            "E4": "C/D evaluates incremental governance value of provenance over same-information non-provenance control",
            "E5": "the 32 fresh MemRL validation dependency clusters are the fresh replication; historical R19/R4/R6/legacy27 are excluded from confirmatory estimation",
        },
        "moderators": design.get("experiment_program", {}).get("E3_regime_law", {}).get("moderators"),
        "exclusions": contract.get("exclusions"),
        "missingness": contract.get("missingness"),
        "multiplicity": contract.get("multiplicity"),
        "analysis": {
            "unit": contract.get("inference_unit"),
            "paired_cluster_effects": True,
            "confidence_interval": "95% cluster-level paired interval",
            "test": contract.get("interval_and_test_rule"),
            "effect_relevance_floor": contract.get("effect_relevance_floor"),
            "p_value_cannot_upgrade_rung_by_itself": True,
            "A_vs_B_and_C_vs_D_not_pooled": True,
            "historical_evidence_not_pooled": True,
        },
        "stopping": {
            "no_interim_inference": contract.get("no_interim_inference"),
            "no_optional_stopping_on_effect": contract.get("no_optional_stopping_on_effect"),
            "source_support_stop": "fail before any validation treatment outcome if qualification fails",
            "post_exposure_infrastructure_failure": "stop affected confirmatory transaction and do not ad-hoc retry; preserve partial artifacts as execution diagnostics only",
            "full_primary_completion": "attempt every preregistered primary unit/arm unless a frozen infrastructure/safety stop fires",
        },
        "persistence": {
            "incremental_jsonl_required": True,
            "per_unit_arm_artifact_required": True,
            "raw_prompt_action_evaluator_trace_hash_required": True,
            "frozen_retrieval_artifact_required": True,
            "source_memory_snapshot_required_before_validation": True,
            "resume_may_continue_only_unexposed_units": True,
        },
    }

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R43-MEMRL-G8-EXECUTION-MANIFEST",
        "recorded_date": "2026-08-29",
        "status": "MEMRL_CURRENT_G1_G8_PASS_EXECUTION_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES",
        "role": "CURRENT_B1_G8_CONTENT_ADDRESSED_EXECUTION_FREEZE",
        "parent_bindings": {
            "design": {"path": str(DESIGN.relative_to(PROJECT_ROOT)), "sha256": _sha(DESIGN)},
            "r40_contract": {"path": str(R40.relative_to(PROJECT_ROOT)), "sha256": _sha(R40)},
            "r42_gate": {"path": str(R42.relative_to(PROJECT_ROOT)), "sha256": _sha(R42)},
            "model_identity": {"path": str(MODEL_ID.relative_to(PROJECT_ROOT)), "sha256": _sha(MODEL_ID)},
            "unit_selection": {"path": str(UNIT_SELECTION.relative_to(PROJECT_ROOT)), "sha256": _sha(UNIT_SELECTION)},
            "image_compatibility": {"path": str(IMAGE.relative_to(PROJECT_ROOT)), "sha256": _sha(IMAGE)},
            "image_alias": {"path": str(IMAGE_ALIAS.relative_to(PROJECT_ROOT)), "sha256": _sha(IMAGE_ALIAS)},
            "runtime_adapter": {"path": str(ADAPTER.relative_to(PROJECT_ROOT)), "sha256": _sha(ADAPTER)},
            "loopback_server": {"path": str(LOCAL_SERVER.relative_to(PROJECT_ROOT)), "sha256": _sha(LOCAL_SERVER)},
            "python_runtime": {"path": str(PY_RUNTIME.relative_to(PROJECT_ROOT)), "sha256": _sha(PY_RUNTIME)},
            "synthetic_stack": {"path": str(SYNTHETIC_STACK.relative_to(PROJECT_ROOT)), "sha256": _sha(SYNTHETIC_STACK)},
            "synthetic_stack_runner": {"path": str(SYNTHETIC_RUNNER.relative_to(PROJECT_ROOT)), "sha256": _sha(SYNTHETIC_RUNNER)},
        },
        "inherited_gate_state": {key: True for key in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")},
        "G8": {
            "pass": True,
            "manifest_complete": True,
            "models_content_addressed": True,
            "runtime_image_content_addressed": True,
            "units_deterministically_frozen": True,
            "arms_estimands_exclusions_analysis_stopping_frozen": True,
            "confirmatory_outcomes_observed_before_freeze": 0,
        },
        "execution_manifest": execution_manifest,
        "claim_policy": {
            "new_behavioral_result": False,
            "provenance_causal_sign_updated": False,
            "PSMG_efficacy_updated": False,
            "paper_claim_expansion_allowed": False,
            "G8_pass_is_execution_readiness_not_scientific_result": True,
        },
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
        "next_action": "RUN_SUPPORT_ONLY_LOCAL_PROVIDER_SMOKE_THEN_RECORD_EXPLICIT_BOUNDED_EXECUTION_AUTHORITY_AND_START_THE_FROZEN_128_TASK_SOURCE_BUILD; VALIDATION_REMAINS_SEALED_UNTIL_SOURCE_QUALIFICATION_PASSES",
        "scientific_verdict": "NO_BEHAVIORAL_VERDICT_CURRENT_MEMRL_SUBSTRATE_NOW_PASSES_G1_G8_PREOUTCOME_FREEZE",
    }
    payload["receipt_sha256"] = _digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("status") != "MEMRL_CURRENT_G1_G8_PASS_EXECUTION_MANIFEST_FROZEN_ZERO_CONFIRMATORY_OUTCOMES":
        errors.append("status")
    if payload.get("paper_id") != PAPER_ID:
        errors.append("paper-id")
    inherited = payload.get("inherited_gate_state") or {}
    if any(inherited.get(k) is not True for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")):
        errors.append("inherited-g1-g7")
    g8 = payload.get("G8") or {}
    if g8.get("pass") is not True or int(g8.get("confirmatory_outcomes_observed_before_freeze") or 0) != 0:
        errors.append("g8")
    manifest = payload.get("execution_manifest") or {}
    if int(((manifest.get("source_build") or {}).get("selected_count") or 0)) != 128:
        errors.append("source-count")
    if int(((manifest.get("confirmatory_units") or {}).get("selected_cluster_count") or 0)) != 32:
        errors.append("validation-count")
    util = manifest.get("utilization_qualification") or {}
    if int(util.get("selected_cluster_count") or 0) != 8 or util.get("disjoint_from_primary") is not True:
        errors.append("utilization-pilot")
    if set(manifest.get("arms") or {}) != {"A_content_only", "B_raw_provenance", "C_PSMG", "D_nonprovenance_controller"}:
        errors.append("arms")
    if (manifest.get("models") or {}).get("llm", {}).get("artifact_manifest_sha256") != EXPECTED_LLM_MANIFEST:
        errors.append("llm-manifest")
    embedding = (manifest.get("models") or {}).get("embedding", {})
    if embedding.get("artifact_manifest_sha256") != EXPECTED_EMBED_MANIFEST:
        errors.append("embedding-manifest")
    if embedding.get("runtime_dimension") != 3072 or embedding.get("dimension_bridge_preserves_l2_norm_and_pairwise_cosine_exactly") is not True:
        errors.append("embedding-dimension-bridge")
    host = manifest.get("host") or {}
    if host.get("runtime_tree_sha256") != EXPECTED_RUNTIME_TREE or host.get("runtime_manifest_sha256") != EXPECTED_RUNTIME_MANIFEST or host.get("runtime_manifest_file_sha256") != EXPECTED_RUNTIME_MANIFEST_FILE:
        errors.append("python-runtime")
    if (host.get("environment") or {}).get("PYTHONDONTWRITEBYTECODE") != "1" or (host.get("environment") or {}).get("runtime_target_is_read_only_after_freeze") is not True:
        errors.append("python-runtime-write-policy")
    adapter = manifest.get("external_runtime_adapter") or {}
    if adapter.get("network_scope") != "loopback-only" or int(adapter.get("external_provider_calls") or 0) != 0:
        errors.append("provider-route")
    if (manifest.get("runtime_image") or {}).get("id") != EXPECTED_IMAGE_ID:
        errors.append("image-id")
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
        raise ValueError("invalid B1 MemRL G8 manifest:" + ";".join(errors))
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    row = write()
    print(json.dumps({"status": row["status"], "receipt_sha256": row["receipt_sha256"], "G8": row["G8"], "next_action": row["next_action"]}, ensure_ascii=False, sort_keys=True))
