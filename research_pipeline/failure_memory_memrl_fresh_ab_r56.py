#!/usr/bin/env python3
"""R56: fresh 32-cluster A/B provenance-only confirmatory runner for R53 full350."""
from __future__ import annotations

import argparse, hashlib, json, pathlib
from typing import Any

try:
    from . import failure_memory_memrl_ab_identification_r48 as r48
    from . import failure_memory_memrl_fresh_utilization_r55 as r55
except ImportError:
    import failure_memory_memrl_ab_identification_r48 as r48  # type: ignore
    import failure_memory_memrl_fresh_utilization_r55 as r55  # type: ignore

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CONTRACT_STATUS="R56_FRESH_AB_CONFIRMATORY_CONTRACT_FROZEN_PRE_VALIDATION_OUTCOME"
AUTH_STATUS="R56_FRESH_AB_CONDITIONAL_AUTHORITY_FROZEN_PRE_VALIDATION_OUTCOME"
UTIL_PASS="UTILIZATION_QUALIFICATION_PASS"
ARMS=list(r48.ARMS)


def load(p:pathlib.Path)->dict[str,Any]:
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise RuntimeError(f"not-object:{p}")
    return v


def valid(v:dict[str,Any])->bool:
    x=v.get("receipt_sha256"); return isinstance(x,str) and x==r48.digest({k:z for k,z in v.items() if k!="receipt_sha256"})


def ids_hash(ids:list[str])->str:
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def preflight(manifest_path:pathlib.Path,r55_auth_path:pathlib.Path,contract_path:pathlib.Path,authority_path:pathlib.Path,
              r54_path:pathlib.Path,selection_path:pathlib.Path,frozen_path:pathlib.Path,source_receipt_path:pathlib.Path,util_path:pathlib.Path):
    m,r55auth,contract,auth,q,sel,frozen,src,util=map(load,[manifest_path,r55_auth_path,contract_path,authority_path,r54_path,selection_path,frozen_path,source_receipt_path,util_path])
    if any(x.get("paper_id")!=PAPER_ID for x in [m,r55auth,contract,auth,q,sel,frozen,src,util]): raise RuntimeError("R56-paper-id-drift")
    if contract.get("status")!=CONTRACT_STATUS or auth.get("status")!=AUTH_STATUS: raise RuntimeError("R56-contract-authority-status-drift")
    if not all(valid(x) for x in [contract,auth,util]): raise RuntimeError("R56-receipt-hash-drift")
    # Re-run the fresh R55 preflight so host/runtime/selection/frozen support are revalidated.
    _,_,_,_,_,_,_=r55.preflight(manifest_path,r55_auth_path,r54_path,selection_path,frozen_path,source_receipt_path)
    if util.get("status")!=UTIL_PASS or util.get("pass") is not True or util.get("primary_32_clusters_authorized_next") is not True: raise RuntimeError("R56-utilization-not-pass")
    if int(util.get("primary_confirmatory_outcomes_observed") or 0)!=0: raise RuntimeError("R56-primary-already-opened")
    b=auth.get("bindings") or {}
    checks={"manifest_file_sha256":r48.sha(manifest_path),"contract_file_sha256":r48.sha(contract_path),"r55_authority_file_sha256":r48.sha(r55_auth_path),
            "r54v2_receipt_file_sha256":r48.sha(r54_path),"selection_file_sha256":r48.sha(selection_path),"frozen_retrieval_file_sha256":r48.sha(frozen_path),
            "source_receipt_file_sha256":r48.sha(source_receipt_path),"runner_sha256":r48.sha(pathlib.Path(__file__).resolve())}
    for k,v in checks.items():
        if b.get(k)!=v: raise RuntimeError(f"R56-binding-drift:{k}")
    if (auth.get("authority") or {}).get("A_B_execution_conditionally_after_R55_PASS") is not True or (auth.get("authority") or {}).get("C_D_execution") is not False: raise RuntimeError("R56-authority-scope-drift")
    e=m["execution_manifest"]; ids=[str(x) for x in e["confirmatory_units"]["representative_ids"]]
    if len(ids)!=32 or ids_hash(ids)!=e["confirmatory_units"]["representative_ids_sha256"] or ids!=[str(x) for x in sel.get("primary_representative_ids") or []]: raise RuntimeError("R56-primary-id-drift")
    records=list(sel.get("primary_records") or []); by={str(x.get("validation_task_id")):x for x in records}
    if set(by)!=set(ids) or len(by)!=32: raise RuntimeError("R56-primary-record-drift")
    make_prompt=r48.prompt_builder(m); surfaces={}; prompt_hashes={}
    for tid in ids:
        selected=list(by[tid].get("selected") or [])
        if not selected or any(x.get("eligible") is not True for x in selected): raise RuntimeError(f"R56-primary-selected-ineligible:{tid}")
        pair=r48.render_pair(selected,tid); surfaces[tid]=pair
        if "source_outcome_success" in pair["A_content_only"]: raise RuntimeError(f"R56-A-provenance-leak:{tid}")
        if pair["audit"].get("actionable_content_identical") is not True or pair["audit"].get("only_executor_visible_difference")!="source_outcome_success": raise RuntimeError(f"R56-adapter-audit-drift:{tid}")
        for arm in ARMS: prompt_hashes[f"{tid}|{arm}"]=hashlib.sha256(make_prompt(pair[arm]).encode()).hexdigest()
    return m,contract,auth,sel,util,surfaces,prompt_hashes


def build_plan(m:dict[str,Any],contract:dict[str,Any],surfaces:dict[str,dict[str,Any]],prompt_hashes:dict[str,str])->dict[str,Any]:
    e=m["execution_manifest"]; ids=[str(x) for x in e["confirmatory_units"]["representative_ids"]]; seed=int((contract.get("randomization") or {}).get("seed") or 0)
    schedule=[]; ordinal=0
    for tid in ids:
        for arm in r48.arm_order(seed,tid):
            schedule.append({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"memory_context_sha256":hashlib.sha256(surfaces[tid][arm].encode()).hexdigest(),"system_prompt_sha256":prompt_hashes[f"{tid}|{arm}"]}); ordinal+=1
    p={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R56_FRESH_AB_SCHEDULE_FROZEN_PRE_TREATMENT","contract_receipt_sha256":contract["receipt_sha256"],
       "randomization_seed":seed,"units":ids,"arms":ARMS,"schedule":schedule,"A_B_treatment_outcomes_observed_when_plan_created":0,"C_D_execution":False}
    p["plan_sha256"]=r48.digest(p); return p


def main()->None:
    p=argparse.ArgumentParser()
    for x in ["manifest","r55-authorization","contract","authority","r54v2-qualification","selection","frozen-retrieval","source-receipt","utilization-receipt","output-dir"]: p.add_argument("--"+x,type=pathlib.Path,required=True)
    p.add_argument("--resume",action="store_true"); a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    m,contract,auth,sel,util,surfaces,prompt_hashes=preflight(a.manifest.resolve(),a.r55_authorization.resolve(),a.contract.resolve(),a.authority.resolve(),
        a.r54v2_qualification.resolve(),a.selection.resolve(),a.frozen_retrieval.resolve(),a.source_receipt.resolve(),a.utilization_receipt.resolve())
    pp=out/"frozen-ab-plan.json"; plan=load(pp) if pp.exists() else build_plan(m,contract,surfaces,prompt_hashes)
    if not pp.exists(): pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if plan.get("plan_sha256")!=r48.digest({k:v for k,v in plan.items() if k!="plan_sha256"}): raise RuntimeError("R56-plan-hash-drift")
    schedule=[(int(z["schedule_ordinal"]),str(z["task_id"]),str(z["arm"])) for z in plan["schedule"]]
    started=r48.rows(out/"started-ab-arms.jsonl"); complete=r48.rows(out/"completed-ab-arms.jsonl")
    sk=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in started]; ck=[(int(x["schedule_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in complete]
    if sk!=schedule[:len(sk)] or ck!=schedule[:len(ck)]: raise RuntimeError("R56-ledger-not-schedule-prefix")
    if len(started)!=len(complete): raise RuntimeError("R56_EXPOSED_INCOMPLETE_ARM_NO_RETRY")
    if complete and len(complete)<len(schedule) and not a.resume: raise RuntimeError("R56-partial-requires-explicit-resume")
    if len(complete)<len(schedule):
        adapter=r48.r47base.build_adapter(m); make_prompt=r48.prompt_builder(m)
        for ordinal,tid,arm in schedule[len(complete):]:
            ctx=surfaces[tid][arm]; prompt=make_prompt(ctx); expected=plan["schedule"][ordinal]
            if hashlib.sha256(ctx.encode()).hexdigest()!=expected["memory_context_sha256"] or hashlib.sha256(prompt.encode()).hexdigest()!=expected["system_prompt_sha256"]: raise RuntimeError("R56-treatment-surface-drift")
            ad=out/"arms"/f"{ordinal:03d}-{tid}-{arm}"; ad.mkdir(parents=True,exist_ok=False)
            r48.append(out/"started-ab-arms.jsonl",{"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"STARTED","started_at":r48.now(),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"no_retry_if_incomplete":True})
            try:
                tr=r48.run_arm_exact(m,adapter,tid,arm,prompt); tp=ad/"trace.json"; tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","completed_at":r48.now(),"terminal_success":tr["terminal_success"],"steps":tr["steps"],
                     "first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":r48.sha(tp),
                     "memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"external_provider_calls":0}
                r48.append(out/"completed-ab-arms.jsonl",row); print(json.dumps({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"completed":True},sort_keys=True),flush=True)
            except Exception as ex:
                fail={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","failed_at":r48.now(),"error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False}
                (ad/"failure.json").write_text(json.dumps(fail,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); raise
    complete=r48.rows(out/"completed-ab-arms.jsonl")
    if len(complete)!=64: raise RuntimeError("R56-A-B-run-incomplete")
    result=r48.analyze(plan,complete,contract); result.update({"role":"R56_FRESH_AB_COMPLETE_ONLY_ANALYSIS","status":"FRESH_AB_IDENTIFICATION_ESTIMATE_COMPLETE",
        "plan_sha256":plan["plan_sha256"],"contract_receipt_sha256":contract["receipt_sha256"],"authority_receipt_sha256":auth["receipt_sha256"],
        "fresh_selection_receipt_sha256":sel["receipt_sha256"],"utilization_receipt_sha256":util["receipt_sha256"],"external_provider_calls":0,"C_D_status":"NOT_EXECUTED","PSMG_efficacy_status":"NOT_IDENTIFIED"})
    result["receipt_sha256"]=r48.digest({k:v for k,v in result.items() if k!="receipt_sha256"})
    (out/"ab-identification-receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__=="__main__": main()
