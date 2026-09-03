from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases as load_v2r1_cases
from research_pipeline.agent_constraint_externality_sq0_v3_cases import build_cases
from research_pipeline.agent_constraint_externality_sq0_v3_oracle import TOOL_CALL_CAP, public_oracle
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/"generated"
V4_BUNDLE=GENERATED/"agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V2R1_CLOSEOUT=GENERATED/"agent-constraint-externality-sq0-v2r1-closeout-20260903.json"
V2R1_ROOT_CAUSE=GENERATED/"agent-constraint-externality-sq0-v2r1-root-cause-20260903.json"
OUTPUT_BUNDLE=GENERATED/"agent-constraint-externality-sq0-v3-target-challenge-protected-20260903.bundle"
CONTRACT_OUTPUT=GENERATED/"agent-constraint-externality-sq0-v3-target-challenge-contract-20260903.json"
QUAL_OUTPUT=GENERATED/"agent-constraint-externality-sq0-v3-static-qualification-20260903.json"
SQ0_ID="ACE-SQ0-V3-SEMANTIC-TARGET-CHALLENGE-20260903"
CASE_COUNT=12


def _pack(cases:list[dict[str,Any]])->None:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix="ace-sq0-v3-") as d:
        root=Path(d);p=root/"sq0v3"/"case_spec.json";p.parent.mkdir(parents=True);p.write_text(json.dumps({"object_id":OBJECT_ID,"sq0_id":SQ0_ID,"cases":cases},ensure_ascii=False,indent=2,sort_keys=True)+"\n")
        pack_bundle(str(OUTPUT_BUNDLE),str(root),["sq0v3"],PASSWORD,SALT,include_license=False)


def load_cases(path:Path=OUTPUT_BUNDLE)->list[dict[str,Any]]:
    from appworld.common.constants import PASSWORD,SALT
    from appworld.common.crypto import bundle_file_path_to_content
    content=bundle_file_path_to_content(str(path),PASSWORD,SALT,include_file_paths=["sq0v3/case_spec.json"]);spec=json.loads(content["sq0v3/case_spec.json"])
    if spec.get("object_id")!=OBJECT_ID or spec.get("sq0_id")!=SQ0_ID:raise RuntimeError("SQ0-V3 bundle identity mismatch.")
    return list(spec["cases"])


def _verified(path:Path,status:str)->dict[str,Any]:
    x=json.loads(path.read_text());
    if x.get("object_id")!=OBJECT_ID or x.get("status")!=status:raise RuntimeError(f"Invalid prerequisite {path}")
    c=x.get("content_sha256");u=dict(x);u.pop("content_sha256",None)
    if c!=sha256_value(u):raise RuntimeError(f"Hash mismatch {path}")
    return x


def build()->tuple[dict[str,Any],dict[str,Any]]:
    close=_verified(V2R1_CLOSEOUT,"SQ0_V2R1_TOO_EASY_CLOSEOUT");root=_verified(V2R1_ROOT_CAUSE,"SQ0_V2R1_RAW_FAILURES_ARE_FORMATTING_PSEUDO_FAILURES")
    cases=build_cases();prior=load_v2r1_cases();old=load_protected_spec(V4_BUNDLE)
    if len(cases)!=CASE_COUNT or len({c["case_id"] for c in cases})!=CASE_COUNT:raise RuntimeError("SQ0-V3 cardinality drifted.")
    prior_ids={c["case_id"] for c in prior}|{f["family_id"] for f in old["families"]};prior_hashes={sha256_value(c["task_instruction"]) for c in prior}|{sha256_value(t) for f in old["families"] for t in [f["target_instruction"],*[a["task_instruction"] for a in f["arms"]]]}
    if any(c["case_id"] in prior_ids or sha256_value(c["task_instruction"]) in prior_hashes for c in cases):raise RuntimeError("SQ0-V3 reuses observed identity/instruction.")
    _pack(cases);replay=load_cases()
    if sha256_value(cases)!=sha256_value(replay):raise RuntimeError("SQ0-V3 encrypted replay drifted.")
    oracles=[public_oracle(c) for c in replay]
    if not all(r["target_success"] and not r["private_fixture_ids_used"] for r in oracles):raise RuntimeError("SQ0-V3 public oracle failed.")
    min_headroom=min(r["headroom"] for r in oracles);max_calls=max(r["public_tool_calls"] for r in oracles)
    if min_headroom<18:raise RuntimeError("SQ0-V3 public oracle headroom below frozen minimum 18.")
    public=[{"case_id":c["case_id"],"kind":c["kind"],"instruction_sha256":sha256_value(c["task_instruction"]),"fixture_sha256":sha256_value(c["fixture"]),"target_local_resource_hashes":[sha256_value(x) for x in c["target_local_resources"]]} for c in cases]
    contract={"schema_version":"ace-sq0-v3-contract-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_V3_STATIC_DESIGN_READY","development_iteration":3,"purpose":"DEVELOPMENT_ONLY_SEMANTIC_SOURCE_FAILURE_QUALIFICATION_NOT_CONFIRMATORY_F0_EVIDENCE","v2r1_closeout_content_sha256":close["content_sha256"],"v2r1_root_cause_content_sha256":root["content_sha256"],"design_change":"FRESH_DYNAMIC_MULTI_SOURCE_RULE_COMPOSITION; TERMINAL_NEWLINE_ONLY_EVALUATOR_NORMALIZATION; ORIGINAL_TARGET_APP_FAMILIES_PRESERVED","case_count":12,"case_kinds":{"FG_SEMANTIC_V3":6,"TNF_SEMANTIC_V3":6},"cases":public,"protected_bundle":{"path":str(OUTPUT_BUNDLE.relative_to(ROOT)),"sha256":sha256_file(OUTPUT_BUNDLE)},"tool_call_cap":TOOL_CALL_CAP,"usable_failure_window":{"min":0.75,"max":0.90},"semantic_failure_definition":["NORMAL_SCIENTIFIC_TERMINAL","TARGET_EVALUATOR_FALSE_AFTER_TERMINAL_NEWLINE_NORMALIZATION_ONLY","NO_PROVIDER_INTERFACE_OR_HARNESS_FAILURE","COMPLETE_TARGET_RELEVANT_TRAJECTORY_AVAILABLE"],"target_app_families":{"FG":["file_system","gmail"],"TNF":["file_system","simple_note","todoist"]},"v2r1_case_reuse":False,"old_f0_case_reuse":False,"confirmatory_reuse":False,"coupling_visible_to_sq0_model":False,"non_target_outcomes_visible_to_sq0_model":False,"provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_v3_execution":False,"f0_r1":False,"probe":False,"p1":False,"toolsandbox":False,"appworld_ul":False,"paper_claim":False}}
    contract["content_sha256"]=sha256_value(contract)
    qual={"schema_version":"ace-sq0-v3-static-qualification-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_V3_PUBLIC_REACHABILITY_PASS","contract_content_sha256":contract["content_sha256"],"protected_bundle_sha256":sha256_file(OUTPUT_BUNDLE),"case_count":12,"public_oracles":oracles,"max_public_tool_calls":max_calls,"minimum_headroom":min_headroom,"private_fixture_ids_used":False,"provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_v3_execution":False,"f0_r1":False,"probe":False,"p1":False,"toolsandbox":False,"appworld_ul":False,"paper_claim":False}}
    qual["content_sha256"]=sha256_value(qual);CONTRACT_OUTPUT.write_text(json.dumps(contract,ensure_ascii=False,indent=2,sort_keys=True)+"\n");QUAL_OUTPUT.write_text(json.dumps(qual,ensure_ascii=False,indent=2,sort_keys=True)+"\n");return contract,qual


def main()->None:
    _,q=build();print(json.dumps({"status":q["status"],"case_count":q["case_count"],"max_public_tool_calls":q["max_public_tool_calls"],"minimum_headroom":q["minimum_headroom"],"provider_requests":0,"sq0_v3_execution_authorized":False},sort_keys=True))

if __name__=="__main__":main()
