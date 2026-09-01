#!/usr/bin/env python3
"""Execute the separately frozen B1 MemRL A/B L2 identification contrast.

This runner cannot execute C/D. It requires strict R46M2 support and an R47M2
utilization PASS, then runs exactly 32 frozen OSInteraction cluster
representatives under A_content_only and B_raw_provenance. Retrieval is never
rerun between arms; R39's exact-information adapter is applied to the frozen R46
rows and serialized with the R48 canonical renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import random
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_utilization_r47 as r47base
    from . import failure_memory_memrl_utilization_r47m2 as r47m2
    from .failure_memory_memrl_exact_information_adapter_r39 import build_memrl_exact_information_pair
except ImportError:
    import failure_memory_memrl_utilization_r47 as r47base  # type: ignore
    import failure_memory_memrl_utilization_r47m2 as r47m2  # type: ignore
    from failure_memory_memrl_exact_information_adapter_r39 import build_memrl_exact_information_pair  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CONTRACT_STATUS = "PREVALIDATION_AB_IDENTIFICATION_FROZEN_C_D_REMAINS_NOT_EXECUTABLE"
AUTH_STATUS = "CONDITIONAL_AB_SUBESTIMAND_EXECUTION_AUTHORITY_FROZEN_PREVALIDATION"
UTIL_PASS = "UTILIZATION_QUALIFICATION_PASS"
ARMS = ["A_content_only", "B_raw_provenance"]
PREFIX = "[Retrieved Memory Context]\n"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(p: pathlib.Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict): raise RuntimeError(f"not-object:{p}")
    return v


def digest(v: Any) -> str:
    return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def sha(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
    return h.hexdigest()


def valid(v: dict[str,Any]) -> bool:
    x=v.get("receipt_sha256"); return isinstance(x,str) and x==digest({k:z for k,z in v.items() if k!="receipt_sha256"})


def append(path: pathlib.Path, row: dict[str,Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())


def rows(path: pathlib.Path) -> list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def canonical_json(v: Any) -> str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def arm_order(seed: int, task_id: str) -> list[str]:
    r=random.Random(int(hashlib.sha256(f"B1-R48-AB-ARM|{seed}|{task_id}".encode()).hexdigest()[:16],16))
    a=list(ARMS);r.shuffle(a);return a


def adapter_input(selected: list[dict[str,Any]], task_id: str) -> list[dict[str,Any]]:
    if not selected: raise RuntimeError(f"primary-retrieval-empty:{task_id}")
    out=[]
    for i,s in enumerate(selected):
        if s.get("eligible") is not True:
            raise RuntimeError(f"primary-selected-row-not-eligible:{task_id}:{i}")
        if type(s.get("source_outcome_success")) is not bool:
            raise RuntimeError(f"primary-selected-row-provenance-invalid:{task_id}:{i}")
        if not s.get("memory_id") or not s.get("content"):
            raise RuntimeError(f"primary-selected-row-content-invalid:{task_id}:{i}")
        out.append({
            "memory_id":str(s["memory_id"]),
            "content":str(s["content"]),
            "metadata":{"success":bool(s["source_outcome_success"])},
            "similarity":s.get("similarity"),
            "q_estimate":s.get("q_estimate"),
            "score":s.get("score"),
            "task_id":str(s.get("source_task_id") or ""),
        })
    return out


def render_pair(selected: list[dict[str,Any]], task_id: str) -> dict[str,Any]:
    pair=build_memrl_exact_information_pair(adapter_input(selected,task_id))
    a=pair["content_only_provenance_hidden"]
    b=pair["raw_provenance_exact_information"]
    if len(a)!=len(b) or not a: raise RuntimeError(f"adapter-pair-shape:{task_id}")
    for x,y in zip(a,b):
        if x.get("position")!=y.get("position") or x.get("content")!=y.get("content"):
            raise RuntimeError(f"adapter-content-drift:{task_id}")
        if set(y)-set(x)!={"source_outcome_success"}:
            raise RuntimeError(f"adapter-visible-diff-drift:{task_id}")
    ctxA=PREFIX+canonical_json(a);ctxB=PREFIX+canonical_json(b)
    return {"A_content_only":ctxA,"B_raw_provenance":ctxB,"audit":pair["audit"]}


def prompt_builder(manifest: dict[str,Any]):
    e=manifest["execution_manifest"];root=pathlib.Path(e["source"]["checkout"])
    if str(root) not in sys.path: sys.path.insert(0,str(root))
    from memrl.lifelongbench_eval.prompts import DEFAULT_SYSTEM_PROMPT, build_llb_prompt_with_memory
    def make(ctx: str) -> str:
        return build_llb_prompt_with_memory(task="os",base_prompt=DEFAULT_SYSTEM_PROMPT,memory_context=ctx)
    return make


def preflight(manifest: dict[str,Any], parent_auth: dict[str,Any], contract: dict[str,Any], authority: dict[str,Any], qual: dict[str,Any], frozen: dict[str,Any], source_receipt: dict[str,Any], util: dict[str,Any]) -> tuple[dict[str,dict[str,Any]],dict[str,str]]:
    if contract.get("status")!=CONTRACT_STATUS or authority.get("status")!=AUTH_STATUS: raise RuntimeError("R48-contract-authority-status-drift")
    if not all(valid(x) for x in [manifest,parent_auth,contract,authority,qual,frozen,source_receipt,util]): raise RuntimeError("R48-receipt-hash-drift")
    if ((authority.get("bindings") or {}).get("contract_receipt_sha256"))!=contract.get("receipt_sha256"): raise RuntimeError("R48-authority-contract-binding-drift")
    if ((authority.get("bindings") or {}).get("parent_authority_receipt_sha256"))!=parent_auth.get("receipt_sha256"): raise RuntimeError("R48-parent-authority-binding-drift")
    if ((authority.get("authority") or {}).get("A_B_execution_conditionally")) is not True or ((authority.get("authority") or {}).get("C_D_execution")) is not False: raise RuntimeError("R48-authority-scope-drift")
    r47m2.preflight(manifest,parent_auth,qual,frozen,source_receipt)
    if util.get("status")!=UTIL_PASS or util.get("pass") is not True or util.get("primary_32_clusters_authorized_next") is not True: raise RuntimeError("R47-utilization-not-pass")
    if int(util.get("primary_confirmatory_outcomes_observed") or 0)!=0: raise RuntimeError("primary-outcome-already-opened")
    e=manifest["execution_manifest"];ids=[str(x) for x in e["confirmatory_units"]["representative_ids"]]
    if ids != [str(x) for x in ((contract.get("units") or {}).get("representative_ids") or [])]: raise RuntimeError("R48-primary-id-contract-drift")
    primary=[x for x in frozen.get("rows") or [] if x.get("cohort")=="primary"];by={str(x.get("validation_task_id")):x for x in primary}
    if set(by)!=set(ids) or len(by)!=32: raise RuntimeError("R48-frozen-primary-row-drift")
    make_prompt=prompt_builder(manifest);surfaces={};prompts={}
    for tid in ids:
        rp=render_pair(list(by[tid].get("selected") or []),tid);surfaces[tid]=rp;prompts[tid]={}
        for arm in ARMS:
            prompt=make_prompt(rp[arm]);prompts[tid][arm]=prompt
            if "source_outcome_success" in rp["A_content_only"]: raise RuntimeError(f"A-provenance-leak:{tid}")
        # A content strings must be byte-identical to the B content strings after removing only provenance.
        if rp["audit"].get("actionable_content_identical") is not True or rp["audit"].get("only_executor_visible_difference")!="source_outcome_success": raise RuntimeError(f"R39-adapter-audit-drift:{tid}")
    return surfaces,{f"{tid}|{arm}":hashlib.sha256(prompts[tid][arm].encode()).hexdigest() for tid in ids for arm in ARMS}


def build_plan(manifest: dict[str,Any],contract: dict[str,Any],surfaces: dict[str,dict[str,Any]],prompt_hashes: dict[str,str]) -> dict[str,Any]:
    e=manifest["execution_manifest"];ids=[str(x) for x in e["confirmatory_units"]["representative_ids"]];seed=int(e["randomization"]["seed"])
    schedule=[];ordinal=0
    for tid in ids:
        for arm in arm_order(seed,tid):
            schedule.append({"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"memory_context_sha256":hashlib.sha256(surfaces[tid][arm].encode()).hexdigest(),"system_prompt_sha256":prompt_hashes[f"{tid}|{arm}"]});ordinal+=1
    p={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R48_AB_IDENTIFICATION_SCHEDULE_FROZEN_PRE_TREATMENT","contract_receipt_sha256":contract.get("receipt_sha256"),"randomization_seed":seed,"units":ids,"arms":ARMS,"schedule":schedule,"A_B_treatment_outcomes_observed_when_plan_created":0,"C_D_execution":False}
    p["plan_sha256"]=digest(p);return p


def run_arm_exact(manifest: dict[str,Any],adapter: Any,task_id: str,arm: str,prompt: str) -> dict[str,Any]:
    e=manifest["execution_manifest"];root=pathlib.Path(e["source"]["checkout"]);llb=root/"3rdparty"/"LifelongAgentBench"
    if str(root) not in sys.path: sys.path.insert(0,str(root))
    if str(llb) not in sys.path: sys.path.insert(0,str(llb))
    from memrl.lifelongbench_eval.task_wrappers import build_task
    from src.agents.instance.language_model_agent import LanguageModelAgent
    from src.tasks.instance.os_interaction.task import OSInteraction
    from src.tasks.task import AgentAction
    from src.typings import Session,SampleStatus,SessionEvaluationOutcome
    agent=LanguageModelAgent(language_model=adapter,system_prompt=prompt)
    task,tname=build_task(task="os",data_file_path=str(root/e["confirmatory_units"]["split"]),max_round=int(e["source_build"]["max_steps"]),os_timeout=int(e["source_build"]["os_timeout_seconds"]));session=Session(task_name=tname,sample_index=task_id)
    actions=[];first=None;steps=0;success=None;evaluation_outcome=None
    try:
        task.reset(session)
        while session.sample_status==SampleStatus.RUNNING:
            agent.inference(session);resp=str(session.chat_history.get_item_deep_copy(-1).content or "");parsed=OSInteraction._parse_agent_response(resp)
            content=parsed.content if parsed.action==AgentAction.EXECUTE else None
            norm=r47base.norm_action(content);actions.append({"response":resp,"parsed":str(parsed.action),"content":parsed.content,"normalized":norm});first=first if first is not None else norm
            task.interact(session);steps+=1
            if steps>int(e["source_build"]["max_steps"])*2: raise RuntimeError("step-ceiling")
        task.complete(session);out=getattr(getattr(session,"evaluation_record",None),"outcome",None);evaluation_outcome=str(out);success=(out==SessionEvaluationOutcome.CORRECT)
    finally:
        try: task.release()
        except Exception: pass
    return {"task_id":task_id,"arm":arm,"full_system_prompt":prompt,"chat_messages":r47base.chat(session),"actions":actions,"first_executable_action":first,"terminal_success":success,"evaluation_outcome":evaluation_outcome,"steps":steps}


def exact_two_sided_signflip(b_only: int,a_only: int) -> float:
    m=b_only+a_only
    if m==0:return 1.0
    lo=min(b_only,a_only)
    tail=sum(math.comb(m,k) for k in range(lo+1))/(2**m)
    return min(1.0,2.0*tail)


def percentile_ci(effects: list[int],seed: int,reps: int=100000) -> tuple[float,float]:
    r=random.Random(seed);n=len(effects);vals=[]
    for _ in range(reps): vals.append(sum(effects[r.randrange(n)] for _ in range(n))/n)
    vals.sort();lo=vals[math.floor(0.025*(reps-1))];hi=vals[math.ceil(0.975*(reps-1))];return float(lo),float(hi)


def analyze(plan: dict[str,Any],complete: list[dict[str,Any]],contract: dict[str,Any]) -> dict[str,Any]:
    by={}
    for r in complete:
        by.setdefault(str(r["task_id"]),{})[str(r["arm"])]=r
    units=[];effects=[];b_only=a_only=0
    for tid in plan["units"]:
        a=by.get(tid,{}).get("A_content_only");b=by.get(tid,{}).get("B_raw_provenance")
        if not a or not b: raise RuntimeError(f"incomplete-A-B-pair:{tid}")
        ya=a.get("terminal_success");yb=b.get("terminal_success")
        if type(ya) is not bool or type(yb) is not bool: raise RuntimeError(f"invalid-terminal-outcome:{tid}")
        d=int(yb)-int(ya);effects.append(d);b_only+=int(yb and not ya);a_only+=int(ya and not yb);units.append({"task_id":tid,"A_terminal_success":ya,"B_terminal_success":yb,"paired_effect":d})
    if len(effects)!=32: raise RuntimeError("A-B-unit-count-drift")
    effect=sum(effects)/len(effects);seed=int((contract.get("analysis") or {}).get("bootstrap_seed") or 0);reps=int((contract.get("analysis") or {}).get("bootstrap_repetitions") or 0);lo,hi=percentile_ci(effects,seed,reps);p=exact_two_sided_signflip(b_only,a_only);floor=float((contract.get("analysis") or {}).get("effect_relevance_floor_abs") or 0.0)
    out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R48_AB_IDENTIFICATION_COMPLETE_ONLY_ANALYSIS","status":"AB_IDENTIFICATION_ESTIMATE_COMPLETE","units":32,"arm_runs":64,"estimand":"B_raw_provenance - A_content_only","effect":effect,"ci95_paired_cluster_bootstrap":[lo,hi],"bootstrap_repetitions":reps,"bootstrap_seed":seed,"B_only_success":b_only,"A_only_success":a_only,"discordant_pairs":b_only+a_only,"exact_two_sided_signflip_p":p,"effect_relevance_floor_abs":floor,"effect_relevance_floor_met":abs(effect)>=floor,"p_value_cannot_upgrade_rung_by_itself":True,"unit_rows":units,"C_D_status":"NOT_EXECUTED_PSMG_OPERATIONALIZATION_NOT_QUALIFIED","PSMG_efficacy_status":"NOT_IDENTIFIED","historical_pooling":False}
    out["receipt_sha256"]=digest(out);return out


def main() -> None:
    p=argparse.ArgumentParser()
    for x in ["manifest","parent-authorization","contract","authority","source-qualification","frozen-retrieval","source-receipt","utilization-receipt","output-dir"]: p.add_argument("--"+x,type=pathlib.Path,required=True)
    p.add_argument("--resume",action="store_true");a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest,parent_auth,contract,authority,qual,frozen,source_receipt,util=map(load,[a.manifest,a.parent_authorization,a.contract,a.authority,a.source_qualification,a.frozen_retrieval,a.source_receipt,a.utilization_receipt])
    surfaces,prompt_hashes=preflight(manifest,parent_auth,contract,authority,qual,frozen,source_receipt,util)
    pp=out/"frozen-ab-plan.json";plan=load(pp) if pp.exists() else build_plan(manifest,contract,surfaces,prompt_hashes)
    if not pp.exists(): pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if plan.get("plan_sha256")!=digest({k:v for k,v in plan.items() if k!="plan_sha256"}): raise RuntimeError("A-B-plan-hash-drift")
    schedule=[(int(r["schedule_ordinal"]),str(r["task_id"]),str(r["arm"])) for r in plan["schedule"]]
    started=rows(out/"started-ab-arms.jsonl");complete=rows(out/"completed-ab-arms.jsonl")
    s_keys=[(int(r["schedule_ordinal"]),str(r["task_id"]),str(r["arm"])) for r in started];c_keys=[(int(r["schedule_ordinal"]),str(r["task_id"]),str(r["arm"])) for r in complete]
    if s_keys!=schedule[:len(s_keys)] or c_keys!=schedule[:len(c_keys)]: raise RuntimeError("A-B-ledger-not-schedule-prefix")
    if len(started)!=len(complete): raise RuntimeError("EXPOSED_INCOMPLETE_ARM_NO_RETRY")
    if complete and not a.resume: raise RuntimeError("existing-A-B-exposure-requires-explicit-resume")
    if len(complete)<len(schedule):
        adapter=r47base.build_adapter(manifest);make_prompt=prompt_builder(manifest)
        for ordinal,tid,arm in schedule[len(complete):]:
            ctx=surfaces[tid][arm];prompt=make_prompt(ctx);expected=plan["schedule"][ordinal]
            if hashlib.sha256(ctx.encode()).hexdigest()!=expected["memory_context_sha256"] or hashlib.sha256(prompt.encode()).hexdigest()!=expected["system_prompt_sha256"]: raise RuntimeError("A-B-treatment-surface-drift")
            arm_dir=out/"arms"/f"{ordinal:03d}-{tid}-{arm}";arm_dir.mkdir(parents=True,exist_ok=False)
            started_row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"STARTED","started_at":now(),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"no_retry_if_incomplete":True};append(out/"started-ab-arms.jsonl",started_row)
            try:
                tr=run_arm_exact(manifest,adapter,tid,arm,prompt);tp=arm_dir/"trace.json";tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                row={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","completed_at":now(),"terminal_success":tr["terminal_success"],"steps":tr["steps"],"first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":sha(tp),"memory_context_sha256":expected["memory_context_sha256"],"system_prompt_sha256":expected["system_prompt_sha256"],"external_provider_calls":0};append(out/"completed-ab-arms.jsonl",row);print(json.dumps({k:row[k] for k in ["schedule_ordinal","task_id","arm","terminal_success"]},sort_keys=True),flush=True)
            except Exception as ex:
                failure={"schedule_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","failed_at":now(),"error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False};(arm_dir/"failure.json").write_text(json.dumps(failure,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise
    complete=rows(out/"completed-ab-arms.jsonl")
    if len(complete)!=64: raise RuntimeError("A-B-run-incomplete")
    result=analyze(plan,complete,contract);result.update({"plan_sha256":plan["plan_sha256"],"contract_receipt_sha256":contract["receipt_sha256"],"authority_receipt_sha256":authority["receipt_sha256"],"external_provider_calls":0});result["receipt_sha256"]=digest({k:v for k,v in result.items() if k!="receipt_sha256"});(out/"ab-identification-receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__=="__main__": main()
