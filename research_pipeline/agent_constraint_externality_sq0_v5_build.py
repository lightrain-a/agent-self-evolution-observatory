from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import load_cases as load_v1_cases
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases as load_v2r1_cases
from research_pipeline.agent_constraint_externality_sq0_v3_build import load_cases as load_v3_cases
from research_pipeline.agent_constraint_externality_sq0_v4_build import load_cases as load_v4_cases
from research_pipeline.agent_constraint_externality_sq0_v4_oracle import public_oracle
from research_pipeline.agent_constraint_externality_sq0_v5_cases import build_cases
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/"generated"
OLD_F0_BUNDLE=GENERATED/"agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V4_CLOSEOUT=GENERATED/"agent-constraint-externality-sq0-v4-closeout-20260903.json"
V4_ROOT_CAUSE=GENERATED/"agent-constraint-externality-sq0-v4-root-cause-20260903.json"
OUTPUT_BUNDLE=GENERATED/"agent-constraint-externality-sq0-v5-target-challenge-protected-20260903.bundle"
CONTRACT_OUTPUT=GENERATED/"agent-constraint-externality-sq0-v5-target-challenge-contract-20260903.json"
QUAL_OUTPUT=GENERATED/"agent-constraint-externality-sq0-v5-static-qualification-20260903.json"
SQ0_ID="ACE-SQ0-V5-FINAL-CALIBRATION-20260903"
TOOL_CALL_CAP=80
CASE_COUNT=12


def _verified(path:Path,status:str)->dict[str,Any]:
    x=json.loads(path.read_text());
    if x.get("object_id")!=OBJECT_ID or x.get("status")!=status: raise RuntimeError(f"Invalid prerequisite {path}")
    c=x.get("content_sha256");u=dict(x);u.pop("content_sha256",None)
    if c!=sha256_value(u):raise RuntimeError(f"Hash mismatch {path}")
    return x


def _pack(cases:list[dict[str,Any]])->None:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix="ace-sq0-v5-") as d:
        root=Path(d);p=root/"sq0v5"/"case_spec.json";p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"object_id":OBJECT_ID,"sq0_id":SQ0_ID,"cases":cases},ensure_ascii=False,indent=2,sort_keys=True)+"\n")
        pack_bundle(str(OUTPUT_BUNDLE),str(root),["sq0v5"],PASSWORD,SALT,include_license=False)


def load_cases(path:Path=OUTPUT_BUNDLE)->list[dict[str,Any]]:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import bundle_file_path_to_content
    content=bundle_file_path_to_content(str(path),PASSWORD,SALT,include_file_paths=["sq0v5/case_spec.json"])
    x=json.loads(content["sq0v5/case_spec.json"])
    if x.get("object_id")!=OBJECT_ID or x.get("sq0_id")!=SQ0_ID:raise RuntimeError("SQ0-V5 bundle identity mismatch")
    return list(x["cases"])


def _freshness(cases:list[dict[str,Any]])->dict[str,Any]:
    priors={"v1":load_v1_cases(),"v2r1":load_v2r1_cases(),"v3":load_v3_cases(),"v4":load_v4_cases()}
    old=load_protected_spec(OLD_F0_BUNDLE)
    ids={c["case_id"] for rows in priors.values() for c in rows}|{f["family_id"] for f in old["families"]}
    ih={sha256_value(c["task_instruction"]) for rows in priors.values() for c in rows}|{sha256_value(t) for f in old["families"] for t in [f["target_instruction"],*[a["task_instruction"] for a in f["arms"]]]}
    fh={sha256_value(c["fixture"]) for rows in priors.values() for c in rows}
    rh={sha256_value(x) for rows in priors.values() for c in rows for x in c.get("target_local_resources",[])}
    cur_ids=[c["case_id"] for c in cases];cur_i=[sha256_value(c["task_instruction"]) for c in cases];cur_f=[sha256_value(c["fixture"]) for c in cases];cur_r=[sha256_value(x) for c in cases for x in c.get("target_local_resources",[])]
    return {"case_ids_unique":len(cur_ids)==len(set(cur_ids))==CASE_COUNT,"case_id_overlap_count":len(set(cur_ids)&ids),"instruction_hash_overlap_count":len(set(cur_i)&ih),"fixture_hash_overlap_count":len(set(cur_f)&fh),"target_local_resource_hash_overlap_count":len(set(cur_r)&rh),"prior_development_sets_checked":["SQ0_V1","SQ0_V2R1","SQ0_V3","SQ0_V4","OLD_F0"]}


def build()->tuple[dict[str,Any],dict[str,Any]]:
    close=_verified(V4_CLOSEOUT,"SQ0_V4_TOO_HARD_CLOSEOUT");root=_verified(V4_ROOT_CAUSE,"SQ0_V4_TOO_HARD_WITH_SERIALIZATION_AND_SEMANTIC_FAILURE_MIX")
    constraints=root.get("prospective_v5_constraints",{})
    if constraints.get("v5_is_final_sq0_calibration_iteration") is not True or constraints.get("tnf_semantic_decision_graph_change")!="NONE" or constraints.get("tnf_serialization_change")!="EXPLICIT_FIELD_TO_SOURCE_ATTRIBUTE_MAPPING":raise RuntimeError("V5 no longer matches frozen V4 diagnosis")
    cases=build_cases();fresh=_freshness(cases)
    if len(cases)!=12 or not fresh["case_ids_unique"] or any(fresh[k]!=0 for k in ("case_id_overlap_count","instruction_hash_overlap_count","fixture_hash_overlap_count","target_local_resource_hash_overlap_count")):raise RuntimeError(f"V5 freshness failed: {fresh}")
    _pack(cases);replay=load_cases()
    if sha256_value(cases)!=sha256_value(replay):raise RuntimeError("V5 encrypted replay drifted")
    oracles=[public_oracle(c) for c in replay]
    if not all(r["target_success"] and not r["private_fixture_ids_used"] for r in oracles):raise RuntimeError("V5 public oracle failed")
    max_calls=max(r["public_tool_calls"] for r in oracles);min_head=min(r["headroom"] for r in oracles)
    if max_calls!=48 or min_head!=32:raise RuntimeError("V5 reachability/headroom drifted")
    public=[{"case_id":c["case_id"],"kind":c["kind"],"instruction_sha256":sha256_value(c["task_instruction"]),"fixture_sha256":sha256_value(c["fixture"]),"target_local_resource_hashes":[sha256_value(x) for x in c["target_local_resources"]]} for c in cases]
    contract={"schema_version":"ace-sq0-v5-contract-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_V5_STATIC_DESIGN_READY_FINAL_CALIBRATION","development_iteration":5,"final_sq0_calibration_iteration":True,"failure_to_pass_disposition":"STOP_SQ0_DEVELOPMENT_NO_V6","purpose":"DEVELOPMENT_ONLY_SOURCE_FAILURE_QUALIFICATION_NOT_CONFIRMATORY_F0_EVIDENCE","v4_closeout_content_sha256":close["content_sha256"],"v4_root_cause_content_sha256":root["content_sha256"],"design_change":{"FG_SEMANTIC_V5":"V4_FG_MECHANISM_UNCHANGED_FRESH_PARAMETERIZATION_ONLY","TNF_SEMANTIC_V5":"V4_SEMANTIC_DECISION_GRAPH_UNCHANGED_PLUS_EXPLICIT_OUTPUT_FIELD_MAPPING","difficulty_not_from_tool_budget":True},"case_count":12,"case_kinds":{"FG_SEMANTIC_V5":6,"TNF_SEMANTIC_V5":6},"cases":public,"freshness_audit":fresh,"protected_bundle":{"path":str(OUTPUT_BUNDLE.relative_to(ROOT)),"sha256":sha256_file(OUTPUT_BUNDLE)},"tool_call_cap":80,"usable_failure_window":{"min":0.75,"max":0.90},"acceptable_final_failure_counts":[9,10],"semantic_failure_definition":["NORMAL_SCIENTIFIC_TERMINAL","TARGET_EVALUATOR_FALSE_WITH_TERMINAL_NEWLINE_NORMALIZATION_ONLY","NO_PROVIDER_INTERFACE_OR_HARNESS_FAILURE","COMPLETE_TARGET_RELEVANT_TRAJECTORY_AVAILABLE"],"confirmatory_reuse":False,"old_f0_case_reuse":False,"v1_case_reuse":False,"v2r1_case_reuse":False,"v3_case_reuse":False,"v4_case_reuse":False,"coupling_visible_to_sq0_model":False,"non_target_outcomes_visible_to_sq0_model":False,"provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_v5_execution":False,"f0_r1":False,"probe":False,"p1":False,"paper_claim":False}}
    contract["content_sha256"]=sha256_value(contract)
    qual={"schema_version":"ace-sq0-v5-static-qualification-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_V5_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_FINAL_CALIBRATION","contract_content_sha256":contract["content_sha256"],"protected_bundle_sha256":sha256_file(OUTPUT_BUNDLE),"case_count":12,"public_oracles":oracles,"max_public_tool_calls":max_calls,"minimum_headroom":min_head,"private_fixture_ids_used":False,"freshness_audit":fresh,"provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_v5_execution":False,"f0_r1":False,"probe":False,"p1":False,"paper_claim":False}}
    qual["content_sha256"]=sha256_value(qual)
    CONTRACT_OUTPUT.write_text(json.dumps(contract,ensure_ascii=False,indent=2,sort_keys=True)+"\n");QUAL_OUTPUT.write_text(json.dumps(qual,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    return contract,qual


def main()->None:
    _,q=build();print(json.dumps({"status":q["status"],"case_count":12,"max_public_tool_calls":q["max_public_tool_calls"],"minimum_headroom":q["minimum_headroom"],"provider_requests":0,"sq0_v5_execution_authorized":False,"final_calibration":True},sort_keys=True))

if __name__=="__main__":main()
