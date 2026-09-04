#!/usr/bin/env python3
"""R69 execution/analyzer for the frozen R68 five-arm semantic-control panel.

The checked-in R68 authority object is intentionally HOLD.  This runner refuses
scientific execution until a later content-addressed authority explicitly opens
it after independent pre-execution review.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, random, socket, subprocess, sys, urllib.request
from typing import Any

try:
 from . import failure_memory_memrl_ab_identification_r48 as r48
 from . import failure_memory_memrl_utilization_r47 as r47
 from . import failure_memory_semantic_control_r68 as r68
 from .failure_memory_provenance_r66_sparse_discordance_stats import clopper_pearson
except ImportError:
 import failure_memory_memrl_ab_identification_r48 as r48  # type: ignore
 import failure_memory_memrl_utilization_r47 as r47  # type: ignore
 import failure_memory_semantic_control_r68 as r68  # type: ignore
 from failure_memory_provenance_r66_sparse_discordance_stats import clopper_pearson  # type: ignore

PAPER_ID=r68.PAPER_ID; ARMS=list(r68.ARMS); MODELS=list(r68.MODELS)
MODEL_KEYS={"qwen":"Qwen2.5-7B-Instruct","llama":"Meta-Llama-3.1-8B-Instruct"}


def load(p):
 v=json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
 if not isinstance(v,dict): raise RuntimeError(f"not-object:{p}")
 return v
def digest(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def valid(v): return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def append(p,row):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
def read_rows(p):
 p=pathlib.Path(p);return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def patched_manifest(parent:dict[str,Any],panel:dict[str,Any]):
 m=json.loads(json.dumps(parent));e=m["execution_manifest"]
 e["confirmatory_units"]={"split":"data/llb/os_interaction_val.json","split_sha256":"1804781d7e768e74cc9f9038fcdfcf373ff34d4edc668382d6d18cbf74f856d6","cluster_rule":"exact sorted skill_list signature","selected_cluster_count":len(panel["representative_ids"]),"representative_ids":list(panel["representative_ids"]),"representative_ids_sha256":panel["representative_ids_sha256"],"statistical_n":len(panel["representative_ids"]),"seeds_and_requests_are_nested_repetitions":True}
 return m


def static_preflight(protocol,panel,hold,qwen_manifest,llama_manifest,r54_frozen,r54_path):
 if not all(valid(x) for x in [protocol,panel,hold,qwen_manifest,llama_manifest,r54_frozen]): raise RuntimeError("receipt-hash-invalid")
 if sha(pathlib.Path(r54_path))!=r68.R54_FROZEN_SHA: raise RuntimeError("r54-frozen-file-hash-drift")
 if protocol.get("status")!=r68.STATUS_PROTOCOL or panel.get("role")!="R68_FRESH_UNEXPOSED_SEMANTIC_CONTROL_PANEL": raise RuntimeError("R68-status-drift")
 if protocol["bindings"].get("panel_receipt_sha256")!=panel["receipt_sha256"]: raise RuntimeError("panel-binding-drift")
 if protocol["bindings"].get("r69_execute_runner_sha256")!=sha(pathlib.Path(__file__).resolve()): raise RuntimeError("runner-binding-drift")
 if len(panel.get("representative_ids") or [])!=66 or panel.get("representative_ids_sha256")!=r68.PANEL_ID_SHA: raise RuntimeError("panel-unit-drift")
 if len(protocol["randomization"]["schedule"])!=660: raise RuntimeError("schedule-size-drift")
 if protocol["execution"].get("analysis_sealed_until_all_660_terminal") is not True: raise RuntimeError("analysis-seal-drift")
 if (hold.get("authority") or {}).get("semantic_control_execution") is not False: raise RuntimeError("checked-in-R68-hold-must-remain-closed")
 return {"qwen":patched_manifest(qwen_manifest,panel),"llama":patched_manifest(llama_manifest,panel)}


def runtime_preflight(manifest):
 e=manifest["execution_manifest"];h=e["host"];s=e["source"]
 if socket.gethostname()!=h["logical_name"]: raise RuntimeError("host-drift")
 if pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve(): raise RuntimeError("python-drift")
 root=pathlib.Path(s["checkout"]);head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip();dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
 if head!=s["revision"] or dirty: raise RuntimeError("memrl-source-drift")
 split=root/e["confirmatory_units"]["split"]
 if sha(split)!=e["confirmatory_units"]["split_sha256"]: raise RuntimeError("validation-split-drift")
 image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
 if image!=e["runtime_image"]["id"]: raise RuntimeError("runtime-image-drift")
 base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
 with urllib.request.urlopen(base+"/models",timeout=5) as resp: models={str(x.get("id")) for x in json.loads(resp.read().decode()).get("data") or []}
 if e["external_runtime_adapter"]["llm_model_id"] not in models: raise RuntimeError("llm-loopback-route-drift")


def prompt_for(manifest,ctx):
 root=pathlib.Path(manifest["execution_manifest"]["source"]["checkout"])
 if str(root) not in sys.path: sys.path.insert(0,str(root))
 from memrl.lifelongbench_eval.prompts import DEFAULT_SYSTEM_PROMPT,build_llb_prompt_with_memory
 return build_llb_prompt_with_memory(task="os",base_prompt=DEFAULT_SYSTEM_PROMPT,memory_context=ctx)


def authorized(authority,protocol):
 if not valid(authority): raise RuntimeError("authority-receipt-invalid")
 if authority.get("protocol_receipt_sha256")!=protocol["receipt_sha256"]: raise RuntimeError("authority-protocol-binding-drift")
 a=authority.get("authority") or {}
 if a.get("semantic_control_execution") is not True or a.get("qwen") is not True or a.get("llama") is not True: raise RuntimeError("semantic-control-execution-not-authorized")
 if any(a.get(k) for k in ["PSMG","L3","gpu_claim","paper_claim_change"]): raise RuntimeError("authority-scope-too-broad")

def conservative_rd(b_only,a_only,n):
 blo,bhi=clopper_pearson(b_only,n,0.975);alo,ahi=clopper_pearson(a_only,n,0.975)
 return [blo-ahi,bhi-alo]


def contrast_stats(by,ids,left,right):
 effects=[];b_only=a_only=0;action_diff=0;step_diffs=[];unit_rows=[]
 for tid in ids:
  l=by[tid][left];r=by[tid][right];yl=l["terminal_success"];yr=r["terminal_success"]
  if type(yl) is not bool or type(yr) is not bool: raise RuntimeError(f"invalid-terminal:{tid}:{left}:{right}")
  d=int(yl)-int(yr);effects.append(d);b_only+=int(yl and not yr);a_only+=int(yr and not yl)
  ad=l.get("first_executable_action")!=r.get("first_executable_action");action_diff+=int(ad);sd=int(l.get("steps") or 0)-int(r.get("steps") or 0);step_diffs.append(sd)
  unit_rows.append({"task_id":tid,"left_success":yl,"right_success":yr,"paired_effect":d,"first_action_diff":ad,"step_count_diff":sd})
 n=len(ids);lo,hi=r48.percentile_ci(effects,r68.BOOTSTRAP_SEED,r68.BOOTSTRAP_REPETITIONS)
 return {"left":left,"right":right,"n_pairs":n,"effect":sum(effects)/n,"left_only_success":b_only,"right_only_success":a_only,"discordant_pairs":b_only+a_only,"exact_two_sided_signflip_p":r48.exact_two_sided_signflip(b_only,a_only),"paired_bootstrap_ci95":[lo,hi],"conservative_paired_rd_ci95":conservative_rd(b_only,a_only,n),"first_action_diff_units":action_diff,"first_action_diff_fraction":action_diff/n,"mean_step_count_difference":sum(step_diffs)/n,"unit_rows":unit_rows}


def analyze_all(protocol,panel,outdir):
 ids=[str(x) for x in panel["representative_ids"]];models={}
 contrast_map={"primary_truthful_vs_unknown":("T3_truthful","P2_unknown"),"correctness_truthful_vs_reversed":("T3_truthful","R4_reversed"),"field_presence_unknown_vs_masked":("P2_unknown","M1_masked"),"content_masked_vs_no_memory":("M1_masked","N0_no_memory"),"legacy_truthful_vs_masked":("T3_truthful","M1_masked")}
 for key,name in MODEL_KEYS.items():
  rr=read_rows(pathlib.Path(outdir)/key/"completed-arms.jsonl")
  if len(rr)!=len(ids)*len(ARMS) or any(r.get("status")!="COMPLETE" for r in rr): raise RuntimeError(f"analysis-sealed-until-complete:{key}:{len(rr)}")
  by={}
  for row in rr: by.setdefault(str(row["task_id"]),{})[str(row["arm"])]=row
  if set(by)!=set(ids) or any(set(by[t])!=set(ARMS) for t in ids): raise RuntimeError(f"model-arm-matrix-incomplete:{key}")
  models[name]={"arm_runs":len(rr),"contrasts":{label:contrast_stats(by,ids,*pair) for label,pair in contrast_map.items()}}
 out={"schema_version":"1.0","paper_id":PAPER_ID,"role":"R69_SEMANTIC_CONTROL_COMPLETE_ONLY_ANALYSIS","status":"SEMANTIC_CONTROL_COMPLETE_ONLY_ANALYSIS","protocol_receipt_sha256":protocol["receipt_sha256"],"panel_receipt_sha256":panel["receipt_sha256"],"complete_arm_runs":660,"models":models,"primary_inference":"Qwen T3_truthful - P2_unknown terminal success; Llama repeats the identical estimand as executor-only replication; no pooling","semantic_reasoning_claim_from_first_action_alone":False,"PSMG_efficacy_identified":False,"L3_transport_complete":False,"scientific_authority":False,"experiment_authority":False}
 out["receipt_sha256"]=digest(out);return out


def materialize_records(panel,r54_frozen):
 elig=[r for r in r54_frozen["rows"] if r.get("has_eligible_frozen_retrieval") is True][40:];ids=[str(r["validation_task_id"]) for r in elig]
 if ids!=[str(x) for x in panel["representative_ids"]]: raise RuntimeError("r54-runtime-panel-order-drift")
 audit={str(r["validation_task_id"]):r for r in panel["records"]};out={}
 for row in elig:
  tid=str(row["validation_task_id"]);sel=r68.compact_selected(row,True);ref=audit[tid]
  if len(sel)!=int(ref["selected_count"]) or r68.digest([s["content_utf8_sha256"] for s in sel])!=ref["selected_content_sequence_sha256"] or r68.digest([s["source_outcome_success"] for s in sel])!=ref["selected_source_outcome_sequence_sha256"]: raise RuntimeError(f"r54-runtime-row-drift:{tid}")
  out[tid]={"validation_task_id":tid,"selected":sel}
 return out


def execute_model(model_key,protocol,panel,manifest,runtime_records,outdir,resume=False):
 model_name=MODEL_KEYS[model_key];runtime_preflight(manifest);adapter=r47.build_adapter(manifest)
 schedule=[x for x in protocol["randomization"]["schedule"] if x["model"]==model_name]
 if len(schedule)!=len(panel["representative_ids"])*len(ARMS): raise RuntimeError("model-schedule-size-drift")
 root=pathlib.Path(outdir)/model_key;root.mkdir(parents=True,exist_ok=True);started=read_rows(root/"started-arms.jsonl");done=read_rows(root/"completed-arms.jsonl")
 key=lambda r:(int(r["ordinal"]),str(r["task_id"]),str(r["arm"]))
 expected=[(int(r["ordinal"]),str(r["task_id"]),str(r["arm"])) for r in schedule]
 if [key(r) for r in started]!=expected[:len(started)] or [key(r) for r in done]!=expected[:len(done)]: raise RuntimeError("ledger-not-schedule-prefix")
 if len(started)!=len(done): raise RuntimeError("exposed-incomplete-arm-no-retry")
 if done and len(done)<len(schedule) and not resume: raise RuntimeError("partial-requires-explicit-resume")
 for item in schedule[len(done):]:
  ordinal=int(item["ordinal"]);tid=str(item["task_id"]);arm=str(item["arm"]);contexts=r68.render_arms(runtime_records[tid]);ctx=contexts[arm];prompt=prompt_for(manifest,ctx)
  ad=root/"arms"/f"{ordinal:04d}-{tid}-{arm}";ad.mkdir(parents=True,exist_ok=False)
  start={"ordinal":ordinal,"model":model_name,"task_id":tid,"arm":arm,"status":"STARTED","started_at":r48.now(),"memory_context_sha256":hashlib.sha256(ctx.encode()).hexdigest(),"system_prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),"no_retry_if_incomplete":True};append(root/"started-arms.jsonl",start)
  try:
   tr=r48.run_arm_exact(manifest,adapter,tid,arm,prompt);tp=ad/"trace.json";tp.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
   row={**start,"status":"COMPLETE","completed_at":r48.now(),"terminal_success":tr["terminal_success"],"steps":tr["steps"],"first_executable_action":tr["first_executable_action"],"first_executable_action_sha256":hashlib.sha256(str(tr["first_executable_action"] or "<NONE>").encode()).hexdigest(),"trace_file":str(tp),"trace_file_sha256":sha(tp),"external_provider_calls":0};append(root/"completed-arms.jsonl",row)
  except Exception as ex:
   fail={**start,"status":"EXECUTION_FAILURE_EXPOSED_NO_RETRY","error_type":type(ex).__name__,"error":str(ex),"scientific_update_allowed":False};(ad/"failure.json").write_text(json.dumps(fail,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise


def main():
 ap=argparse.ArgumentParser()
 for x in ["protocol","panel","hold","qwen-manifest","llama-manifest","r54-frozen-retrieval","output-dir"]: ap.add_argument("--"+x,type=pathlib.Path,required=True)
 ap.add_argument("--authority",type=pathlib.Path);ap.add_argument("--model",choices=["qwen","llama"]);ap.add_argument("--resume",action="store_true");ap.add_argument("--validate-only",action="store_true");ap.add_argument("--analyze",action="store_true")
 a=ap.parse_args();protocol,panel,hold,qm,lm=map(load,[a.protocol,a.panel,a.hold,a.qwen_manifest,a.llama_manifest]);r54f=load(a.r54_frozen_retrieval);manifests=static_preflight(protocol,panel,hold,qm,lm,r54f,a.r54_frozen_retrieval.resolve())
 if a.validate_only:
  print(json.dumps({"status":"R69_STATIC_PREFLIGHT_PASS_EXECUTION_STILL_CLOSED","planned_arm_runs":660,"authority_required":True,"protocol_receipt_sha256":protocol["receipt_sha256"]},sort_keys=True));return
 if a.authority is None: raise RuntimeError("execution-or-analysis-requires-separate-authority")
 auth=load(a.authority);authorized(auth,protocol)
 if a.analyze:
  out=analyze_all(protocol,panel,a.output_dir);p=a.output_dir/"semantic-control-analysis.json";p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(out,ensure_ascii=False,sort_keys=True));return
 if not a.model: raise RuntimeError("--model-required-for-execution")
 execute_model(a.model,protocol,panel,manifests[a.model],materialize_records(panel,r54f),a.output_dir,a.resume)
 print(json.dumps({"status":"MODEL_BLOCK_EXECUTION_COMPLETE","model":a.model},sort_keys=True))

if __name__=="__main__": main()

