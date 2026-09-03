#!/usr/bin/env python3
"""Freeze the R59--R61 Meta-Llama-3.1-8B-Instruct executor replication.

This is a robustness experiment, not a rescue of R56. It reuses the exact R54
fresh units and frozen retrieval/content/order surfaces, changes only the
executor backbone, and requires a Llama-specific source-side native-parser gate
and utilization first stage before the 32-pair A/B replication can open.
"""
from __future__ import annotations

import copy, hashlib, json, pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
LLAMA_ROOT = "/data/lry/models/Meta-Llama-3.1-8B-Instruct"
LLAMA_MANIFEST_SHA = "8071d53a4509c0404328b791800ba79657556490b276b8383e1e8b2f0f63e104"
LLAMA_FILES = [
 {"path":"config.json","bytes":855,"sha256":"29e4c210b0d6ac178b16b2a255a568bdb23b581e50ca1ef6a6d071dd85704e6e"},
 {"path":"generation_config.json","bytes":184,"sha256":"189fb0c0d7fd8a527db217c0a60a0e013f0394cd8800f9697a666a9e75e5f7fd"},
 {"path":"model-00001-of-00004.safetensors","bytes":4976698672,"sha256":"2b1879f356aed350030bb40eb45ad362c89d9891096f79a3ab323d3ba5607668"},
 {"path":"model-00002-of-00004.safetensors","bytes":4999802720,"sha256":"09d433f650646834a83c580877bd60c6d1f88f7755305c12576b5c7058f9af15"},
 {"path":"model-00003-of-00004.safetensors","bytes":4915916176,"sha256":"fc1cdddd6bfa91128d6e94ee73d0ce62bfcdb7af29e978ddcab30c66ae9ea7fa"},
 {"path":"model-00004-of-00004.safetensors","bytes":1168138808,"sha256":"92ecfe1a2414458b4821ac8c13cf8cb70aed66b5eea8dc5ad9eeb4ff309d6d7b"},
 {"path":"model.safetensors.index.json","bytes":23950,"sha256":"146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"},
 {"path":"special_tokens_map.json","bytes":296,"sha256":"6f38c73729248f6c127296386e3cdde96e254636cc58b4169d3fd32328d9a8ec"},
 {"path":"tokenizer.json","bytes":9085657,"sha256":"79e3e522635f3171300913bb421464a87de6222182a0570b9b2ccba2a964b2b4"},
 {"path":"tokenizer_config.json","bytes":55351,"sha256":"177c7b61e616fecb84c17ce0591acb92c6c4d60e9ac5ababfb940ff23bbcd424"},
]
PROBE_IDS = ["103", "256", "54"]


def digest(v: Any) -> str:
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
    return h.hexdigest()


def seal(v: dict[str, Any]) -> dict[str, Any]:
    v=dict(v); v.pop("receipt_sha256",None); v["receipt_sha256"]=digest(v); return v


def write(name: str, v: dict[str, Any]) -> tuple[str,str]:
    p=ROOT/"generated"/name; p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return sha(p),str(v["receipt_sha256"])


def main() -> None:
    base=json.loads((ROOT/"generated/d2-failure-memory-provenance-r55-fresh-utilization-manifest.json").read_text())
    r56=json.loads((ROOT/"generated/d2-failure-memory-provenance-r56-fresh-ab-confirmatory-contract.json").read_text())
    r57=json.loads((ROOT/"generated/d2-failure-memory-provenance-r57-full350-l2-final-adjudication.json").read_text())
    server=ROOT/"research_pipeline/failure_memory_memrl_local_openai_server_r59_llama.py"
    parser=ROOT/"research_pipeline/failure_memory_memrl_llama_parser_qualification_r59.py"
    util=ROOT/"research_pipeline/failure_memory_memrl_llama_utilization_r60.py"
    ab=ROOT/"research_pipeline/failure_memory_memrl_llama_ab_r61.py"
    adapter=ROOT/"research_pipeline/failure_memory_memrl_exact_information_adapter_r39.py"

    identity=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R59-LLAMA-MODEL-IDENTITY",
      "recorded_date":"2026-09-02","status":"CONTENT_ADDRESSED_LOCAL_MODEL_IDENTITY_FROZEN",
      "root":LLAMA_ROOT,"family":"Meta-Llama-3.1-8B-Instruct","architecture":"LlamaForCausalLM",
      "files":LLAMA_FILES,"file_count":len(LLAMA_FILES),"bytes":sum(x["bytes"] for x in LLAMA_FILES),
      "manifest_sha256":LLAMA_MANIFEST_SHA,"local_files_only":True,"external_provider":False,
      "scientific_authority":False,
    })
    ident_file,ident_receipt=write("d2-failure-memory-provenance-r59-llama-model-identity.json",identity)

    m=copy.deepcopy(base)
    m["receipt_id"]="D2-FAILURE-MEMORY-PROVENANCE-R59-LLAMA-EXECUTOR-REPLICATION-MANIFEST"
    m["status"]="R59_LLAMA_EXECUTOR_REPLICATION_MANIFEST_FROZEN_PRE_PROBE"
    m["role"]="SECOND_BACKBONE_EXECUTOR_ONLY_REPLICATION_MANIFEST"
    m["recorded_date"]="2026-09-02"
    e=m["execution_manifest"]
    e["models"]["llm"]={
      "family":"Meta-Llama-3.1-8B-Instruct","root":LLAMA_ROOT,"artifact_manifest_sha256":LLAMA_MANIFEST_SHA,
      "file_count":len(LLAMA_FILES),"bytes":sum(x["bytes"] for x in LLAMA_FILES),"device":"cuda:0",
      "temperature":0.0,"max_new_tokens":512,"runtime_dtype":"float16 via frozen LocalQwenProvider generic AutoModelForCausalLM path","external_api":False,
    }
    a=e["external_runtime_adapter"]
    a.update({
      "loopback_server_path":"research_pipeline/failure_memory_memrl_local_openai_server_r59_llama.py",
      "loopback_server_sha256":sha(server),"loopback_base_url":"http://127.0.0.1:18144/v1",
      "llm_model_id":"B1-Meta-Llama-3.1-8B-Instruct-r59","embedding_model_id":"B1-all-mpnet-base-v2-isometric3072-r43",
      "network_scope":"loopback-only","external_provider_calls":0,"modifies_pinned_memrl_checkout":False,
    })
    m["replication_boundary"]={
      "parent_qwen_R57_status":r57["status"],"parent_qwen_R57_receipt_sha256":r57["receipt_sha256"],
      "Qwen_result_is_fixed_not_rescued":True,"same_R54_primary_and_utilization_ids":True,
      "same_frozen_retrieval_content_and_order":True,"same_A_B_renderer":True,"same_endpoints_and_analysis":True,
      "only_scientific_factor_changed":"executor backbone",
    }
    m=seal(m); manifest_file,manifest_receipt=write("d2-failure-memory-provenance-r59-llama-executor-replication-manifest.json",m)

    program=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R59-R61-LLAMA-EXECUTOR-REPLICATION-CONTRACT",
      "recorded_date":"2026-09-02","status":"SECOND_BACKBONE_REPLICATION_FROZEN_BEFORE_LLAMA_PROBE",
      "role":"ROBUSTNESS_REPLICATION_NOT_R56_RESCUE",
      "scientific_question":"Does the Qwen R56 pattern of behaviorally legible but low terminal provenance value reproduce when only the executor backbone changes to Meta-Llama-3.1-8B-Instruct?",
      "bindings":{
        "R57_receipt_sha256":r57["receipt_sha256"],"R57_file_sha256":sha(ROOT/"generated/d2-failure-memory-provenance-r57-full350-l2-final-adjudication.json"),
        "R54_selection_file_sha256":r56["bindings"]["r54_selection_file_sha256"],
        "R39_adapter_sha256":sha(adapter),"llama_model_identity_file_sha256":ident_file,"llama_model_manifest_sha256":LLAMA_MANIFEST_SHA,
        "replication_manifest_file_sha256":manifest_file,"loopback_server_sha256":sha(server),
        "parser_runner_sha256":sha(parser),"utilization_runner_sha256":sha(util),"ab_runner_sha256":sha(ab),
      },
      "parser_gate":{
        "probe_split":"same frozen OSInteraction train split; never R54 validation","probe_ids":PROBE_IDS,
        "observation":"first model response after reset only","pass_rule":"3/3 native parser responses are nonempty executable actions",
        "terminal_evaluator_calls":0,"attempts":1,"prompt_patch_after_probe":False,
      },
      "utilization_gate":{
        "representative_ids":e["utilization_qualification"]["representative_ids"],"arms":e["utilization_qualification"]["arms"],
        "pass_rule":e["utilization_qualification"]["pass_rule"],"primary_endpoint":e["utilization_qualification"]["promotion_endpoint"],
        "terminal_success":"diagnostic_only","exact_arm_runs":40,
      },
      "AB_replication":{
        "representative_ids":e["confirmatory_units"]["representative_ids"],"arms":["A_content_only","B_raw_provenance"],
        "same_R54_retrieval_rows":True,"same_R39_renderer":True,"same_arm_order_seed":20260825,
        "endpoint":"native LifelongAgentBench OSInteraction terminal success","exact_arm_runs":64,
        "analysis":r56["analysis"],"model_specific_analysis":True,"pool_with_Qwen":False,
      },
      "hard_limits":{
        "Qwen_R56_result_changed":False,"unit_replacement":False,"retrieval_rerun":False,"memory_content_change":False,
        "prompt_text_change":False,"parser_prompt_repair_after_probe":False,"second_attempt_after_exposed_incomplete_arm":False,
        "interim_AB_effect_inspection":False,"outcome_driven_model_switch":False,"C_D_execution":False,
      },
      "scientific_authority":False,
    })
    program_file,program_receipt=write("d2-failure-memory-provenance-r59-r61-llama-executor-replication-contract.json",program)

    parser_auth=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R59-LLAMA-PARSER-AUTHORITY",
      "recorded_date":"2026-09-02","status":"R59_LLAMA_PARSER_QUALIFICATION_AUTHORITY_FROZEN_PRE_PROBE",
      "bindings":{"manifest_file_sha256":manifest_file,"manifest_receipt_sha256":manifest_receipt,"model_identity_file_sha256":ident_file,
                  "model_identity_receipt_sha256":ident_receipt,"parser_runner_sha256":sha(parser),"program_contract_file_sha256":program_file,"program_contract_receipt_sha256":program_receipt},
      "probe_ids":PROBE_IDS,"attempts":1,"validation_units_opened":False,"primary_units_opened":False,
      "authority":{"parser_qualification":True,"utilization":False,"A_B":False,"C_D":False,"external_provider_spend":False},
      "scientific_authority":False,
    })
    parser_auth_file,parser_auth_receipt=write("d2-failure-memory-provenance-r59-llama-parser-authority.json",parser_auth)

    r60auth=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R60-LLAMA-UTILIZATION-AUTHORITY",
      "recorded_date":"2026-09-02","status":"R60_LLAMA_FRESH_UTILIZATION_AUTHORITY_FROZEN_PRE_PROBE",
      "bindings":{"manifest_file_sha256":manifest_file,"manifest_receipt_sha256":manifest_receipt,
        "r54v2_receipt_file_sha256":"650e145a491f09555e40aa8c81c8598d8e1e2dc9febd906857fb8a3202f3aca3",
        "selection_file_sha256":"39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c",
        "frozen_retrieval_file_sha256":"fc906765f2f94b053996bef2d7a085b6a2534b0922f2929da253390d3b855b72",
        "source_receipt_file_sha256":"64b64cb2ca170482fafe4bb89db96071e896d1a952dc6c9a8002093849a000b0",
        "runner_sha256":sha(util),"parser_runner_sha256":sha(parser),"program_contract_receipt_sha256":program_receipt},
      "conditional_on":"R59 parser receipt PASS from exact frozen runner/probe IDs",
      "scope":{"exact_clusters":8,"arms":e["utilization_qualification"]["arms"],"exact_arm_runs":40,"attempts":1},
      "authority":{"utilization_conditionally":True,"A_B":False,"C_D":False,"external_provider_spend":False},
      "scientific_authority":False,
    })
    r60_file,r60_receipt=write("d2-failure-memory-provenance-r60-llama-utilization-authority.json",r60auth)

    r61contract=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R61-LLAMA-AB-REPLICATION-CONTRACT",
      "recorded_date":"2026-09-02","status":"R61_LLAMA_FRESH_AB_REPLICATION_CONTRACT_FROZEN_PRE_PROBE",
      "role":"SECOND_EXECUTOR_BACKBONE_EXACT_SURFACE_REPLICATION",
      "bindings":{"program_contract_receipt_sha256":program_receipt,"replication_manifest_file_sha256":manifest_file,
        "r54_selection_file_sha256":"39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c",
        "r39_exact_information_adapter_sha256":sha(adapter),"r61_runner_sha256":sha(ab),"llama_model_manifest_sha256":LLAMA_MANIFEST_SHA},
      "units":{"count":32,"representative_ids":e["confirmatory_units"]["representative_ids"],"representative_ids_sha256":e["confirmatory_units"]["representative_ids_sha256"],
               "statistical_unit":r56["units"]["statistical_unit"]},
      "arms":{"A_content_only":"same frozen actionable content with provenance hidden","B_raw_provenance":"same frozen actionable content plus truthful source_outcome_success"},
      "renderer":r56["renderer"],"randomization":r56["randomization"],"execution":r56["execution"],"analysis":r56["analysis"],
      "replication_analysis":{"report_model_specific_effect":True,"compare_descriptively_to_R56_Qwen_effect":0.03125,"pool_with_Qwen":False,
        "robust_low_terminal_value_pattern":"Llama absolute effect below 0.15 relevance floor; statistical significance is reported but is not required to call the model-specific effect small"},
      "hard_limits":{"unit_replacement":False,"retrieval_rerun_between_arms":False,"prompt_or_renderer_change":False,"interim_effect_inspection":False,"second_A_B_run":False,"C_D_execution":False},
      "scientific_authority":False,
    })
    r61c_file,r61c_receipt=write("d2-failure-memory-provenance-r61-llama-ab-replication-contract.json",r61contract)

    r61auth=seal({
      "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R61-LLAMA-AB-CONDITIONAL-AUTHORITY",
      "recorded_date":"2026-09-02","status":"R61_LLAMA_FRESH_AB_CONDITIONAL_AUTHORITY_FROZEN_PRE_PROBE",
      "bindings":{"manifest_file_sha256":manifest_file,"contract_file_sha256":r61c_file,"contract_receipt_sha256":r61c_receipt,
        "r60_authority_file_sha256":r60_file,"r54v2_receipt_file_sha256":"650e145a491f09555e40aa8c81c8598d8e1e2dc9febd906857fb8a3202f3aca3",
        "selection_file_sha256":"39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c",
        "frozen_retrieval_file_sha256":"fc906765f2f94b053996bef2d7a085b6a253390d3b855b72",
        "source_receipt_file_sha256":"64b64cb2ca170482fafe4bb89db96071e896d1a952dc6c9a8002093849a000b0","runner_sha256":sha(ab)},
      "conditional_on":"R60 Llama utilization PASS from exact frozen 40-arm schedule",
      "authority":{"A_B_execution_conditionally_after_R60_PASS":True,"C_D_execution":False,"external_provider_spend":False},
      "hard_limits":{"second_A_B_run":False,"unit_replacement":False,"partial_effect_inspection":False,"model_switch_after_R60":False},
      "scientific_authority":False,
    })
    r61a_file,r61a_receipt=write("d2-failure-memory-provenance-r61-llama-ab-conditional-authority.json",r61auth)

    print(json.dumps({"model_identity_file_sha256":ident_file,"manifest_file_sha256":manifest_file,"program_contract_file_sha256":program_file,
      "parser_authority_file_sha256":parser_auth_file,"r60_authority_file_sha256":r60_file,"r61_contract_file_sha256":r61c_file,"r61_authority_file_sha256":r61a_file,
      "parser_runner_sha256":sha(parser),"r60_runner_sha256":sha(util),"r61_runner_sha256":sha(ab),"server_sha256":sha(server)},sort_keys=True))

if __name__ == "__main__": main()
