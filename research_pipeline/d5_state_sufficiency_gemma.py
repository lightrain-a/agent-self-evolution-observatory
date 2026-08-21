from __future__ import annotations

import argparse, hashlib, json, os, time
from collections import defaultdict
from pathlib import Path
from typing import Any
import requests

from .d5_state_sufficiency_f0 import ARMS, MEMORY_IDS, SOURCE_FAMILY, _read_jsonl, _sha_file, _stable_hash, _task_rel_id, historical_task_exposure
from .p0_alfworld_adapter import ALFWorldGameRunner, load_config
from .p0_mem_xfer_support_enriched import _token_matched_placebo
from .vllm_alfworld_policy import VLLMAdmissiblePolicy

EXPERIMENT_ID="D5-STATE-SUFFICIENCY-GEMMA-v1"
MODEL_ID="google/gemma-4-26B-A4B-it"
DEFAULT_BASE_URL="http://127.0.0.1:18002"
DEV_PER_FAMILY=1
FUTURE_PER_FAMILY=1
MAX_STEPS=50
SUPPORT_SCHEMA_FAMILIES=("pick_and_place_simple","pick_clean_then_place_in_recep","pick_cool_then_place_in_recep","pick_heat_then_place_in_recep")

def _now():
    from datetime import datetime,timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def _service_identity(base_url:str,receipt_path:Path)->dict[str,Any]:
    r=requests.get(base_url.rstrip("/")+"/v1/models",timeout=10);r.raise_for_status()
    rows=[x for x in r.json().get("data") or [] if isinstance(x,dict)]
    live=next((x for x in rows if str(x.get("id") or "")==MODEL_ID),None)
    if live is None:raise RuntimeError(f"{MODEL_ID} not served")
    receipt=json.loads(receipt_path.read_text())
    if receipt.get("formal_asset_verified") is not True or receipt.get("status")!="FORMAL_LOCAL_ASSET_VERIFIED":raise RuntimeError("invalid Gemma asset receipt")
    if receipt.get("model_id")!=MODEL_ID or str(live.get("root") or "")!=str(receipt.get("destination") or ""):raise RuntimeError("served Gemma identity does not match receipt")
    return {"model_id":MODEL_ID,"served_root":str(live.get("root") or ""),"max_model_len":int(live.get("max_model_len") or 0),"exact_revision":str(receipt.get("exact_revision") or ""),"formal_asset_receipt_path":str(receipt_path),"formal_asset_receipt_sha256":_sha_file(receipt_path),"official_source_manifest_sha256":str(receipt.get("official_source_manifest_sha256") or ""),"verified_weight_digests":{str(x.get("path")):str(x.get("observed_digest")) for x in receipt.get("verified_files") or [] if isinstance(x,dict) and str(x.get("path") or "").endswith(".safetensors")}}

def compile_contract(*,source_memories_path:Path,historical_runs_root:Path,alfworld_root:Path,alfworld_config:Path,qwen_contract_path:Path|None,service_base_url:str,model_receipt_path:Path)->dict[str,Any]:
    memories={str(x["memory_id"]):x for x in _read_jsonl(source_memories_path)}
    if any(mid not in memories for mid in MEMORY_IDS):raise ValueError("frozen history memory missing")
    if any(str(memories[mid].get("source_family") or "")!=SOURCE_FAMILY for mid in MEMORY_IDS):raise ValueError("frozen history family mismatch")
    exposed=historical_task_exposure(historical_runs_root);excluded=set(exposed)
    excluded.update(_task_rel_id(memories[mid].get("source_task_id") or "") for mid in MEMORY_IDS)
    qwen=[]
    if qwen_contract_path and qwen_contract_path.exists():
        q=json.loads(qwen_contract_path.read_text());qwen=[str(x["task_relpath"]) for x in q.get("task_selection",{}).get("selected_tasks",[])];excluded.update(qwen)
    task_root=alfworld_root/"json_2.1.1"/"valid_unseen";dev=[];future=[];fresh_counts={};eligible={}
    need=DEV_PER_FAMILY+FUTURE_PER_FAMILY
    for fam in SUPPORT_SCHEMA_FAMILIES:
        cand=sorted(str(p) for p in task_root.glob(f"{fam}-*/**/game.tw-pddl") if _task_rel_id(p) not in excluded)
        fresh_counts[fam]=len(cand)
        if len(cand)>=need:eligible[fam]=cand
    target_families=tuple(fam for fam in SUPPORT_SCHEMA_FAMILIES if fam in eligible)
    if len(target_families)<3:raise ValueError(f"fewer than three support-schema families have >= {need} fresh tasks: {fresh_counts}")
    for fam in target_families:
        cand=eligible[fam]
        dev.extend({"target_family":fam,"task_relpath":_task_rel_id(p)} for p in cand[:DEV_PER_FAMILY])
        future.extend({"target_family":fam,"task_relpath":_task_rel_id(p)} for p in cand[DEV_PER_FAMILY:need])
    frozen=[]
    for mid in MEMORY_IDS:
        row=memories[mid];text=str(row.get("text") or "")
        frozen.append({"memory_id":mid,"source_family":SOURCE_FAMILY,"source_task_relpath":_task_rel_id(row.get("source_task_id") or ""),"memory_text_sha256":hashlib.sha256(text.encode()).hexdigest(),"candidate_index":int(row.get("candidate_index") or 0),"candidate_role":str(row.get("candidate_role") or "")})
    material={"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"scientific_question":"If different persistent memories are indistinguishable under a frozen current evaluation signature, are they also equivalent in future controlled transfer effect?","claim_boundary":"Tests sufficiency of current evaluation for a persistent memory state; does not claim history has an effect after byte-identical complete internal-state equality.","frozen_history_object":{"source_family":SOURCE_FAMILY,"memory_ids":list(MEMORY_IDS),"selected_before_any_gemma_alfworld_outcome":True,"selection_basis":"Qwen development-score-equivalent heat-memory trio identified before Gemma execution; Gemma must independently requalify equivalence","memories":frozen},"stage_a":{"name":"CURRENT_EQUIVALENCE_QUALIFICATION","tasks":dev,"episodes":len(dev)*len(MEMORY_IDS)*len(ARMS),"arms":list(ARMS),"pass_rule":"For every common development task all three memories have exactly the same (retrieved_success,placebo_success,no_memory_success); no-memory success+actions also reproduce exactly.","failure_action":"STOP_GEMMA_SUBSTRATE_WITHOUT_OPENING_STAGE_B"},"stage_b":{"name":"SEALED_FUTURE_EQUIVALENCE_TEST","tasks":future,"episodes":len(future)*len(MEMORY_IDS)*len(ARMS),"arms":list(ARMS),"sealed_before_stage_a_outcomes":True,"unlock_requires_stage_a_pass":True,"controlled_delta":"retrieved_success-placebo_success","go_min_divergent_tasks":2,"go_min_divergent_target_families":2,"go_requires_no_memory_success_and_actions_reproducible":True},"task_selection":{"rule":"within the four target families in the frozen mem-xfer support schema, retain every family with >=2 fresh tasks after historical/Qwen-sealed exclusion; per retained family take lexicographically first fresh task for Stage A and second for Stage B","outcome_independent":True,"support_schema_families":list(SUPPORT_SCHEMA_FAMILIES),"fresh_counts_before_selection":fresh_counts,"retained_target_families":list(target_families),"historical_exposed_task_count":len(exposed),"historical_exposure_sha256":_stable_hash(sorted(exposed)),"qwen_sealed_tasks_excluded":qwen},"runtime":{"alfworld_root":str(alfworld_root),"alfworld_config_path":str(alfworld_config),"alfworld_config_sha256":_sha_file(alfworld_config),"policy_mode":"react-family","max_history":6,"max_steps":MAX_STEPS,"decoding":"vLLM chat temperature=0","placebo":"token-matched, absolute gap <=1","outcome_truth":"ALFWorld won/success; no LLM judge"},"service_model":_service_identity(service_base_url,model_receipt_path),"source_artifacts":{"source_memories_path":str(source_memories_path),"source_memories_sha256":_sha_file(source_memories_path),"model_receipt_path":str(model_receipt_path),"model_receipt_sha256":_sha_file(model_receipt_path)},"authority":{"scientific_authority":False,"canonical_problem_gate":False,"canonical_p0":False,"canonical_gpu":False,"user_requested_isolated_paper_conversion_experiment":True}}
    out=dict(material);out["contract_sha256"]=_stable_hash(material);out["created_at"]=_now();out["scientific_authority"]=False;return out

def verify_contract(c:dict[str,Any],source_memories_path:Path,service_base_url:str)->None:
    material={k:v for k,v in c.items() if k not in {"contract_sha256","created_at","scientific_authority"}}
    if _stable_hash(material)!=c.get("contract_sha256"):raise RuntimeError("contract hash mismatch")
    if _sha_file(source_memories_path)!=c["source_artifacts"]["source_memories_sha256"]:raise RuntimeError("source memories changed")
    cur=_service_identity(service_base_url,Path(c["source_artifacts"]["model_receipt_path"]))
    for k in ("model_id","served_root","exact_revision","formal_asset_receipt_sha256"):
        if cur[k]!=c["service_model"][k]:raise RuntimeError(f"served model changed: {k}")

def _no_memory_repro(rows,task):
    rr=[r for r in rows if r["task_relpath"]==task and r["arm"]=="no-memory"]
    return len(rr)==len(MEMORY_IDS) and len({(int(r["success"]),tuple(r.get("actions") or [])) for r in rr})==1

def analyze_a(rows,c):
    exp=int(c["stage_a"]["episodes"])
    by=defaultdict(dict)
    for r in rows:by[(r["memory_id"],r["task_relpath"])][r["arm"]]=r
    details=[]
    for t in c["stage_a"]["tasks"]:
        task=t["task_relpath"]
        if any(set(by.get((mid,task),{}))!=set(ARMS) for mid in MEMORY_IDS):
            continue
        trip={}
        for mid in MEMORY_IDS:
            a=by[(mid,task)];trip[mid]=(int(a["retrieved"]["success"]),int(a["placebo"]["success"]),int(a["no-memory"]["success"]))
        e=len(set(trip.values()))==1;n=_no_memory_repro(rows,task)
        details.append({"task_relpath":task,"target_family":t["target_family"],"triples":{k:list(v) for k,v in trip.items()},"exact_score_equivalent":e,"no_memory_reproducible":n})
        if not e or not n:
            return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"EARLY_STOP_QUALIFICATION_FAILED","contract_sha256":c["contract_sha256"],"rows":len(rows),"expected":exp,"completed_tasks":len(details),"exact_score_equivalence_all_completed_tasks":all(x["exact_score_equivalent"] for x in details),"no_memory_reproducible_all_completed_tasks":all(x["no_memory_reproducible"] for x in details),"tasks":details,"decision":"STOP_GEMMA_SUBSTRATE_NO_CURRENT_EQUIVALENCE","stage_b_authorized_by_this_gate":False,"remaining_stage_a_rows_not_required":exp-len(rows),"stop_logic":"Stage A is a conjunctive qualification gate. One completed task violating exact score equivalence or no-memory reproducibility cannot be repaired by later tasks.","scientific_authority":False}
    if len(rows)!=exp:
        return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"INCOMPLETE","contract_sha256":c["contract_sha256"],"rows":len(rows),"expected":exp,"completed_tasks":len(details),"tasks":details,"scientific_authority":False}
    passed=len(details)==len(c["stage_a"]["tasks"]) and all(x["exact_score_equivalent"] and x["no_memory_reproducible"] for x in details)
    return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"A","status":"COMPLETE","contract_sha256":c["contract_sha256"],"rows":len(rows),"exact_score_equivalence_all_tasks":passed,"no_memory_reproducible_all_tasks":passed,"tasks":details,"decision":"PASS_OPEN_SEALED_STAGE_B" if passed else "STOP_GEMMA_SUBSTRATE_NO_CURRENT_EQUIVALENCE","stage_b_authorized_by_this_gate":passed,"scientific_authority":False}

def analyze_b(rows,c):
    exp=int(c["stage_b"]["episodes"])
    if len(rows)!=exp:return {"status":"INCOMPLETE","rows":len(rows),"expected":exp,"scientific_authority":False}
    by=defaultdict(dict)
    for r in rows:by[(r["memory_id"],r["task_relpath"])][r["arm"]]=r
    table=[];repro=True
    for t in c["stage_b"]["tasks"]:
        task=t["task_relpath"];d={}
        for mid in MEMORY_IDS:
            a=by[(mid,task)];d[mid]=int(a["retrieved"]["success"])-int(a["placebo"]["success"])
        n=_no_memory_repro(rows,task);repro&=n;table.append({"task_relpath":task,"target_family":t["target_family"],"controlled_deltas":d,"divergent":len(set(d.values()))>1,"no_memory_reproducible":n})
    div=[x for x in table if x["divergent"]];families=sorted({x["target_family"] for x in div});passed=repro and len(div)>=int(c["stage_b"]["go_min_divergent_tasks"]) and len(families)>=int(c["stage_b"]["go_min_divergent_target_families"])
    return {"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":"B","status":"COMPLETE","contract_sha256":c["contract_sha256"],"rows":len(rows),"no_memory_reproducible_all_tasks":repro,"effect_table":table,"divergent_task_count":len(div),"divergent_target_families":families,"decision":"GO_PAPER_DESIGN_AND_PROSPECTIVE_CONFIRMATION" if passed else "STOP_CURRENT_STATE_SUFFICIENCY_PAPER_ON_GEMMA","claim_update":"Current evaluation equivalence is insufficient for future transfer equivalence on this frozen Gemma substrate." if passed else "Frozen Gemma substrate does not meet the preregistered cross-family future-divergence gate.","paper_authorized":False,"scientific_authority":False}

def run_stage(*,stage:str,contract_path:Path,source_memories_path:Path,alfworld_root:Path,alfworld_config:Path,service_base_url:str,output_dir:Path,max_new_rows:int=0)->dict[str,Any]:
    c=json.loads(contract_path.read_text());verify_contract(c,source_memories_path,service_base_url)
    if stage=="B":
        ap=output_dir/"stage-a-analysis.json"
        if not ap.exists():raise RuntimeError("Stage B locked: missing Stage A analysis")
        a=json.loads(ap.read_text())
        if a.get("decision")!="PASS_OPEN_SEALED_STAGE_B":raise RuntimeError(f"Stage B locked: {a.get('decision')}")
    output_dir.mkdir(parents=True,exist_ok=True);rawp=output_dir/f"stage-{stage.lower()}-raw.jsonl"
    prior=_read_jsonl(rawp) if rawp.exists() else []
    tasks=c["stage_a"]["tasks"] if stage=="A" else c["stage_b"]["tasks"]
    expected={(mid,str(t["task_relpath"]),arm) for t in tasks for mid in MEMORY_IDS for arm in ARMS}
    done={(r["memory_id"],r["task_relpath"],r["arm"]):r for r in prior}
    if any(k not in expected for k in done):raise RuntimeError("existing raw row outside frozen grid")
    memories={str(x["memory_id"]):x for x in _read_jsonl(source_memories_path)}
    os.environ["ALFWORLD_DATA"]=str(alfworld_root)
    policy=VLLMAdmissiblePolicy(base_url=service_base_url,model=MODEL_ID,policy_mode="react-family")
    runner=ALFWorldGameRunner(load_config(alfworld_config));placebo={};pa={}
    for mid in MEMORY_IDS:
        text=str(memories[mid]["text"]);p,mt,pt=_token_matched_placebo(policy,text)
        if abs(mt-pt)>1:raise RuntimeError(f"placebo mismatch {mid}: {mt}/{pt}")
        placebo[mid]=p;pa[mid]={"memory_tokens":mt,"placebo_tokens":pt,"gap":abs(mt-pt)}
    rows=list(prior);started=time.monotonic();new_rows=0;stop_chunk=False
    for task in tasks:
        if stop_chunk:break
        rel=str(task["task_relpath"]);path=alfworld_root/rel
        if not path.exists():raise FileNotFoundError(path)
        for mid in MEMORY_IDS:
            if stop_chunk:break
            memory=str(memories[mid]["text"])
            for arm in ARMS:
                if max_new_rows and new_rows>=max_new_rows:
                    stop_chunk=True;break
                key=(mid,rel,arm)
                if key in done:continue
                patch="" if arm=="no-memory" else "MEMORY::"+(memory if arm=="retrieved" else placebo[mid])
                tr=runner.run_game_file("eval_out_of_distribution",str(path),policy,patch,max_steps=MAX_STEPS)
                row={"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":stage,"contract_sha256":c["contract_sha256"],"memory_id":mid,"task_relpath":rel,"target_family":str(task["target_family"]),"arm":arm,"success":int(tr.get("success") or 0),"score":float(tr.get("score") or 0),"steps":int(tr.get("steps") or 0),"invalid_actions":int(tr.get("invalid_actions") or 0),"actions":tr.get("actions") or [],"model_calls":int(tr.get("model_calls") or 0),"recorded_at":_now()}
                with rawp.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
                rows.append(row);done[key]=row;new_rows+=1
                (output_dir/f"stage-{stage.lower()}-progress.json").write_text(json.dumps({"status":"RUNNING","contract_sha256":c["contract_sha256"],"completed_rows":len(rows),"expected_rows":len(expected),"elapsed_hours":(time.monotonic()-started)/3600,"usage":policy.usage_snapshot(),"updated_at":_now()},ensure_ascii=False,indent=2)+"\n")
        if stage=="A":
            interim=analyze_a(rows,c)
            if interim.get("decision")=="STOP_GEMMA_SUBSTRATE_NO_CURRENT_EQUIVALENCE":
                stop_chunk=True
    analysis=analyze_a(rows,c) if stage=="A" else analyze_b(rows,c);analysis["new_rows_this_invocation"]=new_rows;ap=output_dir/f"stage-{stage.lower()}-analysis.json";ap.write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+"\n")
    manifest={"schema_version":"1.0","experiment_id":EXPERIMENT_ID,"stage":stage,"contract_sha256":c["contract_sha256"],"raw_sha256":_sha_file(rawp),"analysis_sha256":_sha_file(ap),"rows":len(rows),"placebo_audit":pa,"service_model":c["service_model"],"usage_this_invocation":policy.usage_snapshot(),"elapsed_hours_this_invocation":(time.monotonic()-started)/3600,"scientific_authority":False}
    (output_dir/f"stage-{stage.lower()}-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n");return analysis

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("compile","run-a","run-b","analyze-a","analyze-b"));p.add_argument("--source-memories",type=Path,required=True);p.add_argument("--historical-runs-root",type=Path);p.add_argument("--alfworld-root",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--qwen-contract",type=Path);p.add_argument("--model-receipt",type=Path,required=True);p.add_argument("--service-base-url",default=DEFAULT_BASE_URL);p.add_argument("--contract",type=Path,required=True);p.add_argument("--output-dir",type=Path);p.add_argument("--max-new-rows",type=int,default=0);a=p.parse_args()
    if a.phase=="compile":
        if a.historical_runs_root is None:p.error("--historical-runs-root required")
        c=compile_contract(source_memories_path=a.source_memories,historical_runs_root=a.historical_runs_root,alfworld_root=a.alfworld_root,alfworld_config=a.config,qwen_contract_path=a.qwen_contract,service_base_url=a.service_base_url,model_receipt_path=a.model_receipt);a.contract.parent.mkdir(parents=True,exist_ok=True);a.contract.write_text(json.dumps(c,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"status":"FROZEN","contract_sha256":c["contract_sha256"],"stage_a":c["stage_a"],"stage_b":c["stage_b"]},ensure_ascii=False,indent=2));return
    if a.output_dir is None:p.error("--output-dir required")
    if a.phase in {"run-a","run-b"}:out=run_stage(stage="A" if a.phase=="run-a" else "B",contract_path=a.contract,source_memories_path=a.source_memories,alfworld_root=a.alfworld_root,alfworld_config=a.config,service_base_url=a.service_base_url,output_dir=a.output_dir,max_new_rows=max(0,a.max_new_rows))
    else:
        c=json.loads(a.contract.read_text());stage="A" if a.phase=="analyze-a" else "B";rows=_read_jsonl(a.output_dir/f"stage-{stage.lower()}-raw.jsonl");out=analyze_a(rows,c) if stage=="A" else analyze_b(rows,c)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
