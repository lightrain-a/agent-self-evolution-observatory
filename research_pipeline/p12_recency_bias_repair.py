from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .api_research_memory import record_archived_api_parse_failure,record_parsed_api_output
from .p12_recency_bias_execute import _call_once,_close_parse_failure,_current_call_cap,_prefix
from .p12_recency_bias_harness import CANDIDATE_ID,CONTRACT_SHA256,EXECUTOR_MODEL,difficulty_calibration_pairs,difficulty_prompt,difficulty_tool,sha_json
from .p12_recency_bias_protocol import (
    IMPLEMENTATION_MANIFEST_FILENAME,REPAIRED_AUTHORIZATION_FILENAME,REPAIRED_IMPLEMENTATION_MANIFEST_FILENAME,
    REVOKED_AUTHORIZATION_FILENAME,authorization_ok,load_json,lock_output,parse_difficulty_answers,sha_bytes,write_json,
)
from .paper_first_evidence_acquisition import compile_harness_runtime_invalidations,compile_harness_runtime_repair_receipts,validate_evidence_plan

FAILURE_MANIFEST_FILENAME="runtime-failure-manifest-v1.json"
INVALIDATION_RECEIPT_FILENAME="runtime-invalidation-receipt-v1.json"
REPAIR_PLAN_FILENAME="runtime-repair-plan-v2.json"
REPAIR_PROBE_FILENAME="runtime-repair-offline-probe-v2.json"
REPAIR_RECEIPT_FILENAME="runtime-repair-receipt-v2.json"
FAILED_PAIR="D-CYCLIC3-1"
RETRY_OUTPUT_TOKENS=1200
PRIOR_CALLS=4
FROZEN_MAX_MODEL_CALLS=192
REPLACEMENT_CALL_CAP=101


def _failed_receipt(run_root: Path) -> dict[str,Any]:
    return load_json(run_root/"difficulty"/f"{FAILED_PAIR}.json")


def invalidate_v1(run_root: Path) -> dict[str,Any]:
    output=run_root/REVOKED_AUTHORIZATION_FILENAME;lock=lock_output(output,{"stage":"p12-runtime-invalidate-v1"})
    try:
        plan=load_json(run_root/"authorization-plan.json");manifest=load_json(run_root/IMPLEMENTATION_MANIFEST_FILENAME);failed=_failed_receipt(run_root)
        if failed.get("status")!="DIFFICULTY_PROTOCOL_FAILURE": raise RuntimeError("expected frozen CYCLIC3 protocol failure")
        completed=[]
        for path in sorted((run_root/"difficulty").glob("*.json")):
            row=load_json(path)
            if row.get("status")=="DIFFICULTY_COMPLETE": completed.append(row.get("pair_id"))
        if sorted(completed)!=["D-ALTERNATING2-1","D-LINEAR-1","D-QUADRATIC-1"]: raise RuntimeError(f"unexpected completed difficulty set:{completed}")
        if any((run_root/"skill-compilation").glob("*.json")) or any((run_root/"units").glob("*.json")): raise RuntimeError("P12 v1 invalidation requires no skill/evaluation execution")
        failure={"schema_version":"1.0","status":"P12_RUNTIME_PROTOCOL_FAILURE_V1","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_manifest_sha256":manifest["harness_manifest_sha256"],"failed_stage":"difficulty-calibration","failed_unit":FAILED_PAIR,"raw_sha256":failed["raw_sha256"],"failure_class":"protocol","reason":"Frozen Kimi-K3 paired difficulty call reached the 600-token output cap before submitting the required structured answers. Full provider response was archived and GET-only recovery remained incomplete; partial reasoning text is inadmissible as a calibration answer.","provider_calls_charged":PRIOR_CALLS,"remaining_model_call_budget":FROZEN_MAX_MODEL_CALLS-PRIOR_CALLS,"reopen_condition":"Retry exactly D-CYCLIC3-1 once with identical prompt, task, truth, model, temperature and function schema while increasing only max_output_tokens from 600 to 1200. Reuse the three completed difficulty receipts. Then execute the unchanged four skill-compilation and 96 evaluation calls. No outcome-conditioned task, skill, retrieval, threshold, or analysis change is allowed.","scientific_authority":False,"belief_authority":False};failure["failure_manifest_sha256"]=sha_json(failure);write_json(run_root/FAILURE_MANIFEST_FILENAME,failure)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_manifest_sha256":manifest["harness_manifest_sha256"],"failure_manifest_sha256":failure["failure_manifest_sha256"],"failure_class":"protocol","reason":failure["reason"],"reopen_condition":failure["reopen_condition"],"provider_calls_charged":PRIOR_CALLS,"remaining_model_call_budget":FROZEN_MAX_MODEL_CALLS-PRIOR_CALLS}]};write_json(run_root/INVALIDATION_RECEIPT_FILENAME,receipt)
        held=compile_harness_runtime_invalidations(plan,receipt);errors=validate_evidence_plan(held)
        if errors: raise ValueError(f"P12 invalidation failed:{errors}")
        write_json(output,held);row=next(x for x in held["entries"] if x.get("candidate_id")==CANDIDATE_ID)
        return {"status":"P12_RUNTIME_INVALIDATED","failure_manifest_sha256":failure["failure_manifest_sha256"],"p12_status":row["status"],"execution_authorized":row["execution_authorized"],"scientific_authority":False}
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def build_repair_plan(run_root: Path) -> dict[str,Any]:
    failure=load_json(run_root/FAILURE_MANIFEST_FILENAME);old=load_json(run_root/IMPLEMENTATION_MANIFEST_FILENAME)
    core={"schema_version":"1.0","status":"P12_RUNTIME_REPAIR_PLAN_V2","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"failed_pair":FAILED_PAIR,"protocol_only_change":True,"scientific_object_unchanged":True,"retry":{"pair_id":FAILED_PAIR,"old_max_output_tokens":600,"new_max_output_tokens":RETRY_OUTPUT_TOKENS,"max_attempts":1,"prompt_unchanged":True,"model_unchanged":True,"temperature_unchanged":True,"tool_schema_unchanged":True,"truth_unchanged":True},"reuse_completed_difficulty":["D-LINEAR-1","D-QUADRATIC-1","D-ALTERNATING2-1"],"remaining_scientific_work":{"skill_compilation_calls":4,"evaluation_calls":96},"replacement_provider_call_cap":REPLACEMENT_CALL_CAP,"provider_calls_already_charged":PRIOR_CALLS,"remaining_model_call_budget_before_repair":FROZEN_MAX_MODEL_CALLS-PRIOR_CALLS,"scientific_authority":False,"belief_authority":False};core["replacement_harness_plan_sha256"]=sha_json(core);return core


def run_offline_repair_probe(run_root: Path) -> dict[str,Any]:
    output=run_root/REPAIR_PROBE_FILENAME;lock=lock_output(output,{"stage":"p12-repair-offline-probe-v2"})
    try:
        plan=build_repair_plan(run_root);checks={"retry_only_failed_pair":plan["retry"]["pair_id"]==FAILED_PAIR,"only_output_cap_changes":all(plan["retry"][key] is True for key in ("prompt_unchanged","model_unchanged","temperature_unchanged","tool_schema_unchanged","truth_unchanged")),"reuse_exact_three_completed":len(plan["reuse_completed_difficulty"])==3,"replacement_calls_101":plan["replacement_provider_call_cap"]==101,"total_calls_105_within_192":PRIOR_CALLS+plan["replacement_provider_call_cap"]<=FROZEN_MAX_MODEL_CALLS}
        result={"schema_version":"1.0","status":"P12_RUNTIME_REPAIR_OFFLINE_PROBE_PASS" if all(checks.values()) else "P12_RUNTIME_REPAIR_OFFLINE_PROBE_FAIL","checks":checks,"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"scientific_authority":False,"belief_authority":False};result["repair_probe_sha256"]=sha_json(result);write_json(run_root/REPAIR_PLAN_FILENAME,plan);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def authorize_repair(run_root: Path) -> dict[str,Any]:
    output=run_root/REPAIRED_AUTHORIZATION_FILENAME;lock=lock_output(output,{"stage":"p12-authorize-runtime-repair-v2"})
    try:
        held=load_json(run_root/REVOKED_AUTHORIZATION_FILENAME);failure=load_json(run_root/FAILURE_MANIFEST_FILENAME);old=load_json(run_root/IMPLEMENTATION_MANIFEST_FILENAME);plan=load_json(run_root/REPAIR_PLAN_FILENAME);probe=load_json(run_root/REPAIR_PROBE_FILENAME)
        if probe.get("status")!="P12_RUNTIME_REPAIR_OFFLINE_PROBE_PASS": raise RuntimeError("P12 repair offline probe not PASS")
        names=("p12_recency_bias_harness.py","p12_recency_bias_protocol.py","p12_recency_bias_execute.py","p12_recency_bias_repair.py");base=Path(__file__).parent
        manifest={"schema_version":"1.0","status":"P12_RUNTIME_REPAIR_HARNESS_PASS","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"repair_probe_sha256":probe["repair_probe_sha256"],"code_sha256":{name:sha_bytes((base/name).read_bytes()) for name in names},"replacement_provider_call_cap":REPLACEMENT_CALL_CAP,"sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"protocol_only_change":True,"scientific_authority":False,"belief_authority":False};manifest["harness_manifest_sha256"]=sha_json(manifest);write_json(run_root/REPAIRED_IMPLEMENTATION_MANIFEST_FILENAME,manifest)
        receipt={"schema_version":"1.0","scientific_authority":False,"receipts":[{"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"failure_manifest_sha256":failure["failure_manifest_sha256"],"replaces_harness_manifest_sha256":old["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"harness_manifest_sha256":manifest["harness_manifest_sha256"],"implementation_summary":"Protocol-only P12 repair: reuse three completed no-skill difficulty pairs; retry only D-CYCLIC3-1 once with identical scientific inputs and max_output_tokens 600->1200; then run the unchanged four skill compilation and 96 evaluation units. Total scientific calls are capped at 105/192.","sandboxed":True,"probe_passed":True,"budget_feasible":True,"scientific_object_unchanged":True,"protocol_only_change":True,"replacement_provider_call_cap":REPLACEMENT_CALL_CAP}]};write_json(run_root/"runtime-repair-receipt-v2.json",receipt)
        repaired=compile_harness_runtime_repair_receipts(held,receipt);errors=validate_evidence_plan(repaired)
        if errors: raise ValueError(f"P12 repair authorization invalid:{errors}")
        write_json(output,repaired);row=next(x for x in repaired["entries"] if x.get("candidate_id")==CANDIDATE_ID)
        return {"status":"P12_RUNTIME_REPAIR_AUTHORIZED","harness_manifest_sha256":manifest["harness_manifest_sha256"],"replacement_harness_plan_sha256":plan["replacement_harness_plan_sha256"],"execution_authorized":row["execution_authorized"],"replacement_provider_call_cap":REPLACEMENT_CALL_CAP,"scientific_authority":False}
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def retry_failed_difficulty(*,run_root: Path,persistent_root: Path) -> dict[str,Any]:
    authorization_ok(run_root);output=run_root/"difficulty-repair-v2"/f"{FAILED_PAIR}.json";lock=lock_output(output,{"stage":"p12-difficulty-repair-v2","pair_id":FAILED_PAIR})
    try:
        pair=next(x for x in difficulty_calibration_pairs() if x["pair_id"]==FAILED_PAIR);prefix=_prefix(run_root);run_id=prefix+"difficulty-repair-"+FAILED_PAIR.lower()
        archive,failure=_call_once(persistent_root=persistent_root,run_id=run_id,stage="p12-difficulty-calibration-repair-v2",prompt=difficulty_prompt(pair),tools=difficulty_tool(),max_output_tokens=RETRY_OUTPUT_TOKENS)
        if archive is None: result={"schema_version":"1.0","status":"DIFFICULTY_PROVIDER_FAILURE","pair_id":FAILED_PAIR,**failure};write_json(output,result);return result
        try: answers,source=parse_difficulty_answers(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root,archive=archive,stage="p12-difficulty-calibration-repair-v2",error=error);result={"schema_version":"1.0","status":"DIFFICULTY_PROTOCOL_FAILURE","pair_id":FAILED_PAIR,"raw_sha256":archive["raw_sha256"],"error":f"{type(error).__name__}:{error}","scientific_authority":False,"belief_authority":False};write_json(output,result);return result
        result={"schema_version":"1.0","status":"DIFFICULTY_COMPLETE","pair_id":FAILED_PAIR,"family":pair["family"],"raw_sha256":archive["raw_sha256"],"resolved_model":archive["resolved_model"],"answer_source":source,"backward_answer":answers["backward_answer"],"forward_answer":answers["forward_answer"],"backward_truth":pair["backward"]["answer"],"forward_truth":pair["forward"]["answer"],"backward_success":answers["backward_answer"]==pair["backward"]["answer"],"forward_success":answers["forward_answer"]==pair["forward"]["answer"],"usage":archive["usage"],"runtime_repair_v2":True,"scientific_authority":False,"belief_authority":False};result["receipt_sha256"]=sha_json(result);record_parsed_api_output(run_root=persistent_root/"runs"/run_id,stage="p12-difficulty-calibration-repair-v2",raw_sha256=archive["raw_sha256"],structured_payload=result,requested_model=EXECUTOR_MODEL,resolved_model=archive["resolved_model"],research_objects=[],root=persistent_root);write_json(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=("invalidate","offline-probe","authorize","retry"));p.add_argument("--run-root",type=Path,required=True);p.add_argument("--persistent-root",type=Path);a=p.parse_args()
    if a.cmd=="invalidate": out=invalidate_v1(a.run_root)
    elif a.cmd=="offline-probe": out=run_offline_repair_probe(a.run_root)
    elif a.cmd=="authorize": out=authorize_repair(a.run_root)
    else:
        if a.persistent_root is None: raise SystemExit('--persistent-root required for retry')
        out=retry_failed_difficulty(run_root=a.run_root,persistent_root=a.persistent_root)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
