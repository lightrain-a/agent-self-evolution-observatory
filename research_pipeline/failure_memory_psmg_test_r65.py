#!/usr/bin/env python3
"""R65 prospective hidden-governance PSMG test.

Requires a complete R64 calibration PASS and pre-outcome frozen controller/test
routing.  It executes only the two potential executor actions N=no-memory and
M=content-only on 32 fresh clusters; raw provenance is never executor-visible.
All governor values are evaluated complete-only from the paired N/M outcome table.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import random
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_ab_identification_r48 as r48
    from . import failure_memory_psmg_governance_common_r63 as common
except ImportError:
    import failure_memory_memrl_ab_identification_r48 as r48  # type: ignore
    import failure_memory_psmg_governance_common_r63 as common  # type: ignore

PAPER_ID=common.PAPER_ID
PROGRAM_STATUS="R63_PSMG_HIDDEN_GOVERNANCE_PROGRAM_FROZEN_PRE_CALIBRATION_OUTCOME"
AUTH_STATUS="R65_PSMG_TEST_CONDITIONAL_AUTHORITY_FROZEN_PRE_CALIBRATION_OUTCOME"
CAL_PASS="PSMG_CALIBRATION_ROUTE_SUPPORT_PASS_TEST_DECISIONS_FROZEN"
ARMS=["N_no_memory","M_content_only"]
ARM_SEED_STRING="B1-R65-PSMG-POTENTIAL-20260903"


def now()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p:pathlib.Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8"));
    if not isinstance(v,dict): raise RuntimeError(f"not-object:{p}")
    return v
def sha(p:pathlib.Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
    return h.hexdigest()
def valid(v:dict[str,Any])->bool:
    r=v.get("receipt_sha256"); return isinstance(r,str) and r==common.digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def append(path:pathlib.Path,row:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as f: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
def rows(path:pathlib.Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
def arm_order(tid:str)->list[str]:
    seed=int(hashlib.sha256(f"{ARM_SEED_STRING}|{tid}".encode()).hexdigest()[:16],16); a=list(ARMS); random.Random(seed).shuffle(a); return a


def retrieval_by_id(frozen:dict[str,Any])->dict[str,dict[str,Any]]:
    by={str(r.get("representative_id")):r for r in (frozen.get("rows") or [])}
    if any(t not in by or by[t].get("has_eligible_frozen_retrieval") is not True for t in common.TEST_IDS): raise RuntimeError("R65-test-retrieval-support-drift")
    return by


def preflight(runtime_manifest_path:pathlib.Path,program_path:pathlib.Path,authority_path:pathlib.Path,r54_path:pathlib.Path,frozen_path:pathlib.Path,
              source_receipt_path:pathlib.Path,calibration_receipt_path:pathlib.Path,model_path:pathlib.Path,decisions_path:pathlib.Path):
    runtime,program,auth,r54,source,cal,model,decisions=map(load,[runtime_manifest_path,program_path,authority_path,r54_path,source_receipt_path,calibration_receipt_path,model_path,decisions_path])
    frozen=load(frozen_path)
    if any(x.get("paper_id")!=PAPER_ID for x in [runtime,program,auth,r54,source,cal,model,decisions,frozen]): raise RuntimeError("R65-paper-id-drift")
    if program.get("status")!=PROGRAM_STATUS or auth.get("status")!=AUTH_STATUS or cal.get("status")!=CAL_PASS: raise RuntimeError("R65-status-drift")
    if not all(valid(x) for x in [runtime,program,auth,r54,source,cal]): raise RuntimeError("R65-receipt-hash-drift")
    if model.get("model_sha256")!=common.digest({k:v for k,v in model.items() if k!="model_sha256"}): raise RuntimeError("R65-model-hash-drift")
    if decisions.get("decision_plan_sha256")!=common.digest({k:v for k,v in decisions.items() if k!="decision_plan_sha256"}): raise RuntimeError("R65-decision-plan-hash-drift")
    if decisions.get("model_sha256")!=model.get("model_sha256") or decisions.get("test_outcomes_observed_when_frozen")!=0: raise RuntimeError("R65-decision-binding-drift")
    if cal.get("test_execution_conditionally_authorized_next") is not True or int(cal.get("test_outcomes_observed") or 0)!=0: raise RuntimeError("R65-calibration-not-authorizing")
    b=auth.get("bindings") or {}
    checks={"runtime_manifest_file_sha256":sha(runtime_manifest_path),"program_contract_file_sha256":sha(program_path),"r54v2_receipt_file_sha256":sha(r54_path),
            "frozen_retrieval_file_sha256":sha(frozen_path),"source_receipt_file_sha256":sha(source_receipt_path),"common_module_sha256":sha(pathlib.Path(common.__file__).resolve()),"runner_sha256":sha(pathlib.Path(__file__).resolve())}
    for k,v in checks.items():
        if b.get(k)!=v: raise RuntimeError(f"R65-binding-drift:{k}")
    if (auth.get("authority") or {}).get("test_execution_conditionally_after_R64_pass") is not True or (auth.get("authority") or {}).get("calibration_execution") is not False: raise RuntimeError("R65-authority-scope-drift")
    if list(map(str,decisions.get("test_ids") or []))!=common.TEST_IDS or decisions.get("test_ids_sha256")!=common.TEST_IDS_SHA256: raise RuntimeError("R65-test-id-drift")
    # Runtime checks.
    e=runtime["execution_manifest"]
    import socket,subprocess,urllib.request,sys
    h=e["host"]; src=e["source"]
    if socket.gethostname()!=h["logical_name"] or pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve() or os.environ.get("PYTHONDONTWRITEBYTECODE")!="1": raise RuntimeError("R65-host-python-drift")
    root=pathlib.Path(src["checkout"]); head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip(); dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=src["revision"] or dirty: raise RuntimeError("R65-source-checkout-drift")
    split=root/e["confirmatory_units"]["split"]
    if sha(split)!=e["confirmatory_units"]["split_sha256"]: raise RuntimeError("R65-split-drift")
    image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
    if image!=e["runtime_image"]["id"]: raise RuntimeError("R65-image-drift")
    base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
    with urllib.request.urlopen(base+"/models",timeout=5) as rr: models={str(x.get("id")) for x in json.loads(rr.read().decode()).get("data") or []}
    if {e["external_runtime_adapter"]["llm_model_id"],e["external_runtime_adapter"]["embedding_model_id"]}-models: raise RuntimeError("R65-loopback-route-drift")
    by=retrieval_by_id(frozen)
    # Recompute feature hashes and ensure frozen decisions were made from these exact pre-outcome rows.
    frows=[common.feature_record(by[t]) for t in common.TEST_IDS]; dby={str(x["task_id"]):x for x in decisions["rows"]}
    for fr in frows:
        d=dby.get(str(fr["task_id"]));
        if not d or d.get("Z_sha256")!=fr["Z_sha256"] or d.get("P_sha256")!=fr["P_sha256"]: raise RuntimeError(f"R65-feature-decision-drift:{fr['task_id']}")
    expected=common.freeze_test_decisions(model,frows)
    if expected["decision_plan_sha256"]!=decisions["decision_plan_sha256"]: raise RuntimeError("R65-recomputed-decision-drift")
    return runtime,program,auth,r54,source,cal,model,decisions,by


def build_surfaces(runtime:dict[str,Any],by:dict[str,dict[str,Any]])->tuple[dict[str,dict[str,str]],dict[str,dict[str,str]]]:
    make=r48.prompt_builder(runtime); surfaces={}; hashes={}; nctx=""; nprompt=make(nctx)
    for tid in common.TEST_IDS:
        sel=[x for x in (by[tid].get("selected") or []) if x.get("eligible") is True]; pair=r48.render_pair(sel,tid); mctx=pair["A_content_only"]
        if "source_outcome_success" in mctx: raise RuntimeError(f"R65-provenance-leak:{tid}")
        surfaces[tid]={"N_no_memory":nctx,"M_content_only":mctx}; hashes[tid]={"N_no_memory":hashlib.sha256(nprompt.encode()).hexdigest(),"M_content_only":hashlib.sha256(make(mctx).encode()).hexdigest()}
    return surfaces,hashes


def build_plan(decisions:dict[str,Any],surfaces:dict[str,dict[str,str]],hashes:dict[str,dict[str,str]])->dict[str,Any]:
    schedule=[]; ordinal=0
    for tid in common.TEST_IDS:
        for arm in arm_order(tid):
            schedule.append({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"memory_context_sha256":hashlib.sha256(surfaces[tid][arm].encode()).hexdigest(),"system_prompt_sha256":hashes[tid][arm]}); ordinal+=1
    out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R65_PSMG_POTENTIAL_OUTCOME_PLAN_FROZEN_PRE_TEST_OUTCOME","units":common.TEST_IDS,"arms":ARMS,"arm_seed_string":ARM_SEED_STRING,
         "decision_plan_sha256":decisions["decision_plan_sha256"],"schedule":schedule,"test_outcomes_observed_when_created":0,"raw_provenance_executor_visible":False}
    out["plan_sha256"]=common.digest(out); return out


def main()->None:
    ap=argparse.ArgumentParser()
    for x in ["runtime-manifest","program-contract","authority","r54v2-qualification","frozen-retrieval","source-receipt","calibration-receipt","model","test-decisions","output-dir"]: ap.add_argument("--"+x,type=pathlib.Path,required=True)
    ap.add_argument("--resume",action="store_true"); a=ap.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    runtime,program,auth,r54,source,cal,model,decisions,by=preflight(a.runtime_manifest.resolve(),a.program_contract.resolve(),a.authority.resolve(),a.r54v2_qualification.resolve(),a.frozen_retrieval.resolve(),a.source_receipt.resolve(),a.calibration_receipt.resolve(),a.model.resolve(),a.test_decisions.resolve())
    surfaces,hashes=build_surfaces(runtime,by); plan=build_plan(decisions,surfaces,hashes); pp=out/"frozen-test-potential-outcome-plan.json"
    if pp.exists():
        if load(pp).get("plan_sha256")!=plan["plan_sha256"]: raise RuntimeError("R65-plan-drift")
    else: pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    schedule=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in plan["schedule"]]
    started=rows(out/"started-test-arms.jsonl"); complete=rows(out/"completed-test-arms.jsonl")
    sk=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in started]; ck=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in complete]
    if sk!=schedule[:len(sk)] or ck!=schedule[:len(ck)]: raise RuntimeError("R65-ledger-not-schedule-prefix")
    if len(started)!=len(complete): raise RuntimeError("R65_EXPOSED_INCOMPLETE_ARM_NO_RETRY")
    if complete and len(complete)<len(schedule) and not a.resume: raise RuntimeError("R65-partial-requires-explicit-resume")
    if len(complete)<len(schedule):
        adapter=r48.r47base.build_adapter(runtime); make=r48.prompt_builder(runtime)
        for ordinal,tid,arm in schedule[len(complete):]:
            ctx=surfaces[tid][arm]; prompt=make(ctx); expected=plan["schedule"][ordinal]
            if hashlib.sha256(ctx.encode()).hexdigest()!=expected["memory_context_sha256"] or hashlib.sha256(prompt.encode()).hexdigest()!=expected["system_prompt_sha256"]: raise RuntimeError("R65-treatment-surface-drift")
            ad=out/"arms"/f"{ordinal:03d}-{tid}-{arm}"; ad.mkdir(parents=True,exist_ok=False)
            append(out/"started-test-arms.jsonl",{"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"STARTED","started_at":now(),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"no_retry_if_incomplete":True})
            try:
                tr=r48.run_arm_exact(runtime,adapter,tid,arm,prompt); tp=ad/"trace.json"; tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","completed_at":now(),"terminal_success":tr["terminal_success"],"steps":tr["steps"],"first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":sha(tp),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"external_provider_calls":0}
                append(out/"completed-test-arms.jsonl",row); print(json.dumps({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"completed":True},sort_keys=True),flush=True)
            except Exception as ex:
                fail={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","failed_at":now(),"error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False}; (ad/"failure.json").write_text(json.dumps(fail,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); raise
    complete=rows(out/"completed-test-arms.jsonl")
    if len(complete)!=64: raise RuntimeError("R65-test-incomplete")
    pair={t:{} for t in common.TEST_IDS}
    for row in complete: pair[str(row["task_id"])][str(row["arm"])]=row
    potential={}
    for tid in common.TEST_IDS:
        if set(pair[tid])!=set(ARMS): raise RuntimeError(f"R65-incomplete-pair:{tid}")
        n=pair[tid]["N_no_memory"]["terminal_success"]; m=pair[tid]["M_content_only"]["terminal_success"]
        if type(n) is not bool or type(m) is not bool: raise RuntimeError(f"R65-invalid-outcome:{tid}")
        potential[tid]={"N_no_memory":n,"M_content_only":m}
    result=common.analyze_test(decisions,potential)
    result.update({"plan_sha256":plan["plan_sha256"],"decision_plan_sha256":decisions["decision_plan_sha256"],"model_sha256":model["model_sha256"],"calibration_receipt_sha256":cal["receipt_sha256"],"program_contract_receipt_sha256":program["receipt_sha256"],"authority_receipt_sha256":auth["receipt_sha256"],"completed_arm_runs":64,"external_provider_calls":0,"scientific_authority":False})
    result["receipt_sha256"]=common.digest({k:v for k,v in result.items() if k!="receipt_sha256"}); (out/"psmg-test-receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["status","effect_psmg_minus_g0","ci95_paired_cluster_bootstrap","exact_two_sided_signflip_p","policy_values","receipt_sha256"]},sort_keys=True))


if __name__=="__main__": main()
