#!/usr/bin/env python3
"""Generate the prospective R63--R65 PSMG hidden-governance closure.

This generator is zero-outcome and zero-execution-authority by itself.  It binds
already-frozen R53/R54 source/retrieval evidence, the exact fresh calibration/test
units, deterministic controller code, and conditional execution authorities.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

try:
    from . import failure_memory_psmg_governance_common_r63 as common
except ImportError:
    import failure_memory_psmg_governance_common_r63 as common  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
PAPER_ID = common.PAPER_ID

RUNTIME_MANIFEST = ROOT / "generated/d2-failure-memory-provenance-r55-fresh-utilization-manifest.json"
COMMON = ROOT / "research_pipeline/failure_memory_psmg_governance_common_r63.py"
R64 = ROOT / "research_pipeline/failure_memory_psmg_calibration_r64.py"
R65 = ROOT / "research_pipeline/failure_memory_psmg_test_r65.py"
R39 = ROOT / "research_pipeline/failure_memory_memrl_exact_information_adapter_r39.py"
R48 = ROOT / "research_pipeline/failure_memory_memrl_ab_identification_r48.py"

# Runtime artifacts live on host 231 and were content-addressed before this program.
R54_FILE_SHA = "650e145a491f09555e40aa8c81c8598d8e1e2dc9febd906857fb8a3202f3aca3"
R54_RECEIPT_SHA = "032c79998165700d5405d2d56bd30cf2dfe044b9f9ec97d2e51461a429514c42"
FROZEN_RETRIEVAL_FILE_SHA = "fc906765f2f94b053996bef2d7a085b6a2534b0922f2929da253390d3b855b72"
SOURCE_RECEIPT_FILE_SHA = "64b64cb2ca170482fafe4bb89db96071e896d1a952dc6c9a8002093849a000b0"
SOURCE_RECEIPT_SHA = "ce15c57e9c1274d1b40aca49850c7b0cbb5a8fe0656314d8bdfca3d7024e95c7"
R41_HISTORICAL_FILE_SHA = "93ee2fa94d2c551208c225f796ec6030b697d739977d3719662ceb5ffd47178f"
R62_CROSS_BACKBONE_FILE_SHA = "67c1848831c93839697262c0626ee0c107c4643f7f94d440ad34fa7f41b6c572"
R62_CROSS_BACKBONE_RECEIPT_SHA = "8a9ea03a0fdead265a90573aa09240237020422394bac95890985bf4f5960956"

PREVIOUSLY_EXPOSED_40 = [
    "150","327","98","335","161","366","125","260","176","136","3","236","28","235","202","40",
    "467","470","79","275","290","15","414","411","463","135","71","325","282","193","252","441",
    "110","438","456","258","427","183","388","16",
]


def sha(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
    return h.hexdigest()


def sealed(obj: dict[str, Any]) -> dict[str, Any]:
    out=dict(obj); out["receipt_sha256"]=common.digest(out); return out


def write(name: str, obj: dict[str, Any]) -> pathlib.Path:
    path=GEN/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return path


def main() -> None:
    GEN.mkdir(parents=True,exist_ok=True)
    runtime=json.loads(RUNTIME_MANIFEST.read_text())
    if sha(RUNTIME_MANIFEST)!="cc2200f898175963e3d0762c370f6d83dad4d572850f88618f24b15f891ca38b": raise RuntimeError("R63-runtime-manifest-drift")
    if runtime.get("receipt_sha256")!=common.digest({k:v for k,v in runtime.items() if k!="receipt_sha256"}): raise RuntimeError("R63-runtime-receipt-drift")
    code={"common_module_sha256":sha(COMMON),"r64_runner_sha256":sha(R64),"r65_runner_sha256":sha(R65),"r39_exact_information_adapter_sha256":sha(R39),"r48_executor_runner_sha256":sha(R48)}
    if code["r39_exact_information_adapter_sha256"]!="c94353ca46c8cfb65cfae6218d2e03ae6946b37aa25e52ee83212e2dfe03afe2": raise RuntimeError("R63-R39-drift")
    if set(PREVIOUSLY_EXPOSED_40)&(set(common.CALIBRATION_IDS)|set(common.TEST_IDS)|set(common.RESERVE_IDS)): raise RuntimeError("R63-exposure-overlap")
    if common.ids_hash(common.CALIBRATION_IDS)!=common.CALIBRATION_IDS_SHA256 or common.ids_hash(common.TEST_IDS)!=common.TEST_IDS_SHA256 or common.ids_hash(common.RESERVE_IDS)!=common.RESERVE_IDS_SHA256: raise RuntimeError("R63-id-hash-drift")

    program=sealed({
        "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R63-PSMG-HIDDEN-GOVERNANCE-PROGRAM",
        "recorded_date":"2026-09-03","status":"R63_PSMG_HIDDEN_GOVERNANCE_PROGRAM_FROZEN_PRE_CALIBRATION_OUTCOME",
        "role":"PROSPECTIVE_EXECUTOR_BLIND_PROVENANCE_GOVERNANCE_EFFICACY_CONTRACT",
        "scientific_lineage":{
            "historical_R41_mechanism_redesign_file_sha256":R41_HISTORICAL_FILE_SHA,
            "R62_two_backbone_visible_L2_file_sha256":R62_CROSS_BACKBONE_FILE_SHA,
            "R62_two_backbone_visible_L2_receipt_sha256":R62_CROSS_BACKBONE_RECEIPT_SHA,
            "question":"Does authentic source-outcome provenance improve a hidden memory-manager reuse decision beyond the strongest same-information provenance-free governor?",
            "raw_provenance_executor_visible":False,
            "visible_L2_and_hidden_governance_are_distinct_estimands":True,
        },
        "bindings":{
            "runtime_manifest_file_sha256":sha(RUNTIME_MANIFEST),"runtime_manifest_receipt_sha256":runtime["receipt_sha256"],
            "r54v2_receipt_file_sha256":R54_FILE_SHA,"r54v2_receipt_sha256":R54_RECEIPT_SHA,
            "frozen_retrieval_file_sha256":FROZEN_RETRIEVAL_FILE_SHA,
            "source_receipt_file_sha256":SOURCE_RECEIPT_FILE_SHA,"source_receipt_sha256":SOURCE_RECEIPT_SHA,
            **code,
        },
        "units":{
            "selection_rule":"from the 106 R54-native-supported fresh clusters in ascending frozen cluster_rank_sha256, exclude the already exposed first 40; take next 24 calibration, next 32 test, leave final 10 untouched reserve",
            "previously_exposed_ids":PREVIOUSLY_EXPOSED_40,"previously_exposed_count":40,
            "calibration_ids":common.CALIBRATION_IDS,"calibration_ids_sha256":common.CALIBRATION_IDS_SHA256,"calibration_count":24,
            "test_ids":common.TEST_IDS,"test_ids_sha256":common.TEST_IDS_SHA256,"test_count":32,
            "reserve_ids":common.RESERVE_IDS,"reserve_ids_sha256":common.RESERVE_IDS_SHA256,"reserve_count":10,
            "remaining66_sha256":common.REMAINING66_SHA256,
            "unit_replacement":False,"reserve_use_in_current_experiment":False,
        },
        "executor_potential_actions":{
            "N_no_memory":"native empty-memory MemRL prompt, identical to the qualified U0 no-memory surface",
            "M_content_only":"R39/R48 exact-information content-only rendering of the R54 frozen selected memories; provenance field hidden",
            "potential_actions_observed_per_unit":2,
            "raw_source_outcome_success_in_executor_prompt":False,
            "retrieval_rerun_between_actions":False,
        },
        "feature_schema":{
            "Z_definition":"all frozen non-provenance pre-target-outcome retrieval/content/task features available to both governors",
            "Z_feature_names":common.Z_FEATURE_NAMES,
            "P_definition":"authentic source_outcome_success receipt aggregated over the same frozen selected memories; available only to provenance-aware governor",
            "P_feature_names":common.P_FEATURE_NAMES,
            "residual_moderator_Z_names":common.RESIDUAL_MODERATOR_Z_NAMES,
            "residual_feature_names":common.residual_feature_names(),
            "feature_extractor_code_sha256":code["common_module_sha256"],
            "target_outcome_features_forbidden":True,
        },
        "calibration":{
            "episodes":48,"arms":["N_no_memory","M_content_only"],"memory_marginal_utility":"M_terminal_success - N_terminal_success",
            "fit_only_after_all_48_complete":True,
            "route_support_gate":{
                "minimum_beneficial_memory_units":common.CALIBRATION_MIN_BENEFICIAL,
                "minimum_harmful_memory_units":common.CALIBRATION_MIN_HARMFUL,
                "failure_status":"CALIBRATION_ROUTE_SUPPORT_STOP_NO_TEST",
                "no_test_if_gate_fails":True,
            },
        },
        "controller":{
            "g0":"ridge on standardized Z with unpenalized intercept","g0_lambda":common.G0_RIDGE_LAMBDA,
            "provenance_residual":"ridge on standardized P main effects plus P-by-frozen-Z-moderator interactions; no intercept","residual_lambda":common.RESIDUAL_RIDGE_LAMBDA,
            "residual_target":"calibration utility - g0 prediction","fixed_success_failure_sign":False,
            "decision":"M_content_only iff predicted marginal utility > 0; ties/nonpositive choose N_no_memory",
            "shrinkage_toward_zero":True,"raw_provenance_executor_visible":False,
            "fit_implementation_sha256":code["common_module_sha256"],
        },
        "test_decisions_frozen_after_calibration_before_test_outcomes":{
            "g0":"same-information provenance-free controller",
            "psmg":"g0 plus truthful provenance residual",
            "shuffled_psmg":"same fitted residual with P vector deterministically assigned from another test cluster",
            "naive_success_prior":"M iff frozen selected-memory success_fraction > 0.5, otherwise N",
            "always_memory":"M","never_memory":"N","binary_oracle":"post-outcome diagnostic upper bound max(N,M), not a deployable policy",
            "shuffle_seed_string":common.SHUFFLE_SEED_STRING,
            "test_predictions_may_not_be_refit_after_test_outcome":True,
        },
        "primary_analysis":{
            "estimand":"mean over 32 test clusters of terminal_success(policy PSMG)-terminal_success(policy g0), evaluated exactly from complete paired N/M potential-action outcomes",
            "effect_relevance_floor_abs":common.EFFECT_RELEVANCE_FLOOR_ABS,
            "test":"two-sided exact paired sign-flip over policy-outcome discordances",
            "confidence_interval":"95% paired-cluster percentile bootstrap","bootstrap_repetitions":common.BOOTSTRAP_REPETITIONS,"bootstrap_seed":common.BOOTSTRAP_SEED,
            "support":"effect >= +0.15 and exact two-sided p < 0.05",
            "harm":"effect <= -0.15 and exact two-sided p < 0.05",
            "otherwise":"PSMG_EFFICACY_NOT_ESTABLISHED",
            "no_cross_model_pooling":True,"no_visible_L2_pooling":True,
        },
        "secondary_analysis":["policy value for g0/PSMG/shuffled/naive/always/never","binary-oracle regret","harmful reuse","missed useful memory","beneficial failure-memory retention","harmful success-memory rejection","route disagreement"],
        "stopping_and_integrity":{
            "no_interim_calibration_utility_inspection":True,"no_interim_test_effect_inspection":True,"exactly_once_per_unit_action":True,
            "exposed_incomplete_arm_no_retry":True,"no_optional_stopping":True,"no_threshold_or_lambda_change":True,"no_unit_replacement":True,"reserve_locked":True,
            "calibration_gate_failure_is_support_stop_not_method_null":True,
        },
        "episode_budget":{"calibration":48,"test_if_calibration_passes":64,"maximum_total":112,"external_provider_calls":0},
        "claim_boundary":{"PSMG_efficacy_claim_allowed_only_after_R65_primary_support":True,"audit_value_of_provenance_independent_of_efficacy":True,"L3_transport_complete":False,"universal_provenance_claim":False},
        "scientific_authority":False,"experiment_authority":False,"submission_authority":False,
    })
    program_path=write("d2-failure-memory-provenance-r63-psmg-hidden-governance-program.json",program)

    r64_auth=sealed({
        "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R64-PSMG-CALIBRATION-AUTHORITY","recorded_date":"2026-09-03",
        "status":"R64_PSMG_CALIBRATION_EXECUTION_AUTHORITY_FROZEN_PRE_CALIBRATION_OUTCOME",
        "bindings":{
            "runtime_manifest_file_sha256":sha(RUNTIME_MANIFEST),"program_contract_file_sha256":sha(program_path),"program_contract_receipt_sha256":program["receipt_sha256"],
            "r54v2_receipt_file_sha256":R54_FILE_SHA,"frozen_retrieval_file_sha256":FROZEN_RETRIEVAL_FILE_SHA,"source_receipt_file_sha256":SOURCE_RECEIPT_FILE_SHA,
            "common_module_sha256":code["common_module_sha256"],"runner_sha256":code["r64_runner_sha256"],
        },
        "scope":{"exact_clusters":24,"arms":["N_no_memory","M_content_only"],"exact_arm_runs":48,"attempts":1},
        "authority":{"calibration_execution":True,"test_execution":False,"reserve_execution":False,"raw_provenance_executor_visible":False,"external_provider_spend":False},
        "scientific_authority":False,
    })
    r64_path=write("d2-failure-memory-provenance-r64-psmg-calibration-authority.json",r64_auth)

    r65_auth=sealed({
        "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R65-PSMG-TEST-CONDITIONAL-AUTHORITY","recorded_date":"2026-09-03",
        "status":"R65_PSMG_TEST_CONDITIONAL_AUTHORITY_FROZEN_PRE_CALIBRATION_OUTCOME",
        "bindings":{
            "runtime_manifest_file_sha256":sha(RUNTIME_MANIFEST),"program_contract_file_sha256":sha(program_path),"program_contract_receipt_sha256":program["receipt_sha256"],
            "r64_authority_file_sha256":sha(r64_path),"r64_authority_receipt_sha256":r64_auth["receipt_sha256"],
            "r54v2_receipt_file_sha256":R54_FILE_SHA,"frozen_retrieval_file_sha256":FROZEN_RETRIEVAL_FILE_SHA,"source_receipt_file_sha256":SOURCE_RECEIPT_FILE_SHA,
            "common_module_sha256":code["common_module_sha256"],"runner_sha256":code["r65_runner_sha256"],
        },
        "conditional_on":"R64 complete 48/48, route-support PASS, deterministic model and all 32 test decisions frozen before first R65 outcome",
        "scope":{"exact_clusters":32,"arms":["N_no_memory","M_content_only"],"exact_arm_runs":64,"attempts":1},
        "authority":{"calibration_execution":False,"test_execution_conditionally_after_R64_pass":True,"reserve_execution":False,"raw_provenance_executor_visible":False,"external_provider_spend":False},
        "hard_limits":{"no_second_test_run":True,"no_unit_replacement":True,"no_model_refit_after_test_exposure":True,"no_threshold_or_lambda_change":True,"partial_effect_inspection":False},
        "scientific_authority":False,
    })
    r65_path=write("d2-failure-memory-provenance-r65-psmg-test-conditional-authority.json",r65_auth)

    print(json.dumps({
        "program_file_sha256":sha(program_path),"program_receipt_sha256":program["receipt_sha256"],
        "r64_authority_file_sha256":sha(r64_path),"r64_authority_receipt_sha256":r64_auth["receipt_sha256"],
        "r65_authority_file_sha256":sha(r65_path),"r65_authority_receipt_sha256":r65_auth["receipt_sha256"],
        **code,
    },sort_keys=True))


if __name__=="__main__": main()
