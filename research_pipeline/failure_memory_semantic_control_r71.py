#!/usr/bin/env python3
"""R71 fail-closed executor/analyzer for the frozen R70 semantic-control R2.

R71 implements the reviewer-required exposure boundary. Pre-exposure technical
failures may receive at most three logged start attempts. Once the first
inference dispatch is durably recorded, the trajectory is never rerun; genuine
post-exposure technical failures become TECHNICAL_MISSING and enter a worst/best
paired sensitivity bound.

The checked-in R70 HOLD has zero execution authority. --validate-only is safe.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, socket, subprocess, sys, urllib.request
from typing import Any

try:
 from . import failure_memory_memrl_ab_identification_r48 as r48
 from . import failure_memory_memrl_utilization_r47 as r47
 from . import failure_memory_semantic_control_r70 as r70
 from .failure_memory_provenance_r66_sparse_discordance_stats import clopper_pearson
except ImportError:
 import failure_memory_memrl_ab_identification_r48 as r48  # type: ignore
 import failure_memory_memrl_utilization_r47 as r47  # type: ignore
 import failure_memory_semantic_control_r70 as r70  # type: ignore
 from failure_memory_provenance_r66_sparse_discordance_stats import clopper_pearson  # type: ignore

PAPER_ID=r70.PAPER_ID
MODEL_KEYS={"qwen":r70.QWEN,"llama":r70.LLAMA}
MAX_PREEXPOSURE_ATTEMPTS=3


def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def append(p:pathlib.Path,row:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
def rows(p:pathlib.Path)->list[dict[str,Any]]:
 return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []

def patched_manifest(parent:dict[str,Any],panel:dict[str,Any])->dict[str,Any]:
 m=json.loads(json.dumps(parent));e=m["execution_manifest"];e["confirmatory_units"]={"split":"data/llb/os_interaction_val.json","split_sha256":"1804781d7e768e74cc9f9038fcdfcf373ff34d4edc668382d6d18cbf74f856d6","cluster_rule":"exact sorted skill_list signature","selected_cluster_count":66,"representative_ids":list(panel["representative_ids"]),"representative_ids_sha256":panel["representative_ids_sha256"],"statistical_n":66};return m

def static_preflight(protocol:dict[str,Any],panel:dict[str,Any],hold:dict[str,Any],token_audit:dict[str,Any],review:dict[str,Any],qwen_manifest:dict[str,Any],llama_manifest:dict[str,Any],r54:dict[str,Any],r54_path:pathlib.Path)->dict[str,dict[str,Any]]:
 objs=[protocol,panel,hold,token_audit,review,qwen_manifest,llama_manifest,r54]
 if not all(valid(x) for x in objs):raise RuntimeError("receipt-hash-invalid")
 if protocol.get("status")!=r70.STATUS:raise RuntimeError("R70-status-drift")
 if sha(r54_path)!=r70.R54_FROZEN_SHA:raise RuntimeError("R54-file-drift")
 b=protocol.get("bindings") or {}
 if b.get("r71_execute_runner_sha256")!=sha(pathlib.Path(__file__).resolve()):raise RuntimeError("R71-runner-binding-drift")
 if b.get("r68_panel_receipt_sha256")!=panel.get("receipt_sha256") or b.get("r70_tokenizer_audit_receipt_sha256")!=token_audit.get("receipt_sha256") or b.get("r70_independent_review_receipt_sha256")!=review.get("receipt_sha256"):raise RuntimeError("R70-binding-drift")
 if review.get("verdict")!="REDUCE_OR_REDIRECT":raise RuntimeError("review-verdict-drift")
 if token_audit.get("status")!="R70_P_T_S_TOKEN_FOOTPRINT_MATCH_PASS_ZERO_MODEL":raise RuntimeError("tokenizer-gate-drift")
 if int((protocol.get("run_matrix") or {}).get("total_new_trajectories") or 0)!=321:raise RuntimeError("run-matrix-drift")
 if len((protocol["staging"]["Qwen"]["schedule"]))!=189 or len((protocol["staging"]["Llama"]["schedule"]))!=132:raise RuntimeError("stage-schedule-drift")
 if (hold.get("authority") or {}).get("qwen_execution") is not False or (hold.get("authority") or {}).get("llama_execution") is not False:raise RuntimeError("checked-in-hold-must-remain-closed")
 if protocol["failure_policy"]["scientific_boundary"]!="treatment exposure, not durable STARTED":raise RuntimeError("failure-boundary-drift")
 return {"qwen":patched_manifest(qwen_manifest,panel),"llama":patched_manifest(llama_manifest,panel)}

def runtime_records(panel:dict[str,Any],r54:dict[str,Any])->dict[str,dict[str,Any]]:
 rr=r70.r54_suffix(r54,panel);out={}
 audit={str(x["validation_task_id"]):x for x in panel.get("records") or []}
 for row in rr:
  tid=str(row["validation_task_id"]);sel=r70.selected(row);ref=audit[tid]
  content_sha=r70.digest([hashlib.sha256(str(s["content"]).encode()).hexdigest() for s in sel]);outcome_sha=r70.digest([bool(s["source_outcome_success"]) for s in sel])
  if content_sha!=ref["selected_content_sequence_sha256"] or outcome_sha!=ref["selected_source_outcome_sequence_sha256"]:raise RuntimeError(f"runtime-R54-row-drift:{tid}")
  out[tid]=row
 return out

def runtime_preflight(manifest:dict[str,Any])->None:
 e=manifest["execution_manifest"];h=e["host"];s=e["source"]
 if socket.gethostname()!=h["logical_name"]:raise RuntimeError("host-drift")
 if pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve():raise RuntimeError("python-drift")
 root=pathlib.Path(s["checkout"]);head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip();dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
 if head!=s["revision"] or dirty:raise RuntimeError("memrl-source-drift")
 split=root/e["confirmatory_units"]["split"]
 if sha(split)!=e["confirmatory_units"]["split_sha256"]:raise RuntimeError("validation-split-drift")
 image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
 if image!=e["runtime_image"]["id"]:raise RuntimeError("runtime-image-drift")
 base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
 with urllib.request.urlopen(base+"/models",timeout=5) as resp:available={str(x.get("id")) for x in json.loads(resp.read().decode()).get("data") or []}
 if e["external_runtime_adapter"]["llm_model_id"] not in available:raise RuntimeError("loopback-route-drift")

def prompt_for(manifest:dict[str,Any],ctx:str)->str:
 root=pathlib.Path(manifest["execution_manifest"]["source"]["checkout"])
 if str(root) not in sys.path:sys.path.insert(0,str(root))
 from memrl.lifelongbench_eval.prompts import DEFAULT_SYSTEM_PROMPT,build_llb_prompt_with_memory
 return build_llb_prompt_with_memory(task="os",base_prompt=DEFAULT_SYSTEM_PROMPT,memory_context=ctx)

def authority_check(authority:dict[str,Any],protocol:dict[str,Any],model_key:str,analysis:bool=False)->None:
 if not valid(authority) or authority.get("protocol_receipt_sha256")!=protocol["receipt_sha256"]:raise RuntimeError("authority-invalid")
 a=authority.get("authority") or {}
 if analysis:
  if a.get("analysis") is not True:raise RuntimeError("analysis-not-authorized")
 else:
  if a.get(f"{model_key}_execution") is not True:raise RuntimeError(f"{model_key}-execution-not-authorized")
 if any(a.get(k) for k in ["PSMG","L3","paper_claim_change"]):raise RuntimeError("authority-too-broad")

def _task_imports(manifest:dict[str,Any]):
 e=manifest["execution_manifest"];root=pathlib.Path(e["source"]["checkout"]);llb=root/"3rdparty"/"LifelongAgentBench"
 for p in [root,llb]:
  if str(p) not in sys.path:sys.path.insert(0,str(p))
 from memrl.lifelongbench_eval.task_wrappers import build_task
 from src.agents.instance.language_model_agent import LanguageModelAgent
 from src.tasks.instance.os_interaction.task import OSInteraction
 from src.tasks.task import AgentAction
 from src.typings import Session,SampleStatus,SessionEvaluationOutcome
 return build_task,LanguageModelAgent,OSInteraction,AgentAction,Session,SampleStatus,SessionEvaluationOutcome

def run_attempt(manifest:dict[str,Any],adapter:Any,tid:str,arm:str,prompt:str,event_path:pathlib.Path,attempt:int)->dict[str,Any]:
 build_task,LanguageModelAgent,OSInteraction,AgentAction,Session,SampleStatus,SessionEvaluationOutcome=_task_imports(manifest);e=manifest["execution_manifest"]
 agent=LanguageModelAgent(language_model=adapter,system_prompt=prompt);task,tname=build_task(task="os",data_file_path=str(pathlib.Path(e["source"]["checkout"])/e["confirmatory_units"]["split"]),max_round=int(e["source_build"]["max_steps"]),os_timeout=int(e["source_build"]["os_timeout_seconds"]));session=Session(task_name=tname,sample_index=tid);actions=[];first=None;steps=0;exposed=False
 try:
  task.reset(session)
  if session.sample_status!=SampleStatus.RUNNING:raise RuntimeError(f"reset-not-running:{session.sample_status}:{session.finish_reason}")
  append(event_path,{"task_id":tid,"arm":arm,"attempt":attempt,"event":"PREEXPOSURE_RESET_PASS","at":r48.now()})
  while session.sample_status==SampleStatus.RUNNING:
   if not exposed:
    append(event_path,{"task_id":tid,"arm":arm,"attempt":attempt,"event":"TREATMENT_EXPOSURE_DISPATCHED","at":r48.now(),"system_prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest()});exposed=True
   agent.inference(session);resp=str(session.chat_history.get_item_deep_copy(-1).content or "");parsed=OSInteraction._parse_agent_response(resp);content=parsed.content if parsed.action==AgentAction.EXECUTE else None;norm=r47.norm_action(content);actions.append({"response":resp,"parsed":str(parsed.action),"content":parsed.content,"normalized":norm});first=first if first is not None else norm;task.interact(session);steps+=1
   if steps>int(e["source_build"]["max_steps"])*2:raise RuntimeError("step-ceiling")
  task.complete(session);out=getattr(getattr(session,"evaluation_record",None),"outcome",None)
  if out==SessionEvaluationOutcome.CORRECT:success=True
  elif out==SessionEvaluationOutcome.INCORRECT:success=False
  else:raise RuntimeError(f"technical-evaluator-outcome:{out}")
  return {"status":"COMPLETE","task_id":tid,"arm":arm,"attempt":attempt,"terminal_success":success,"evaluation_outcome":str(out),"steps":steps,"first_executable_action":first,"actions":actions,"chat_messages":r47.chat(session),"treatment_exposed":True}
 except Exception as ex:
  return {"status":"TECHNICAL_FAILURE_POST_EXPOSURE" if exposed else "TECHNICAL_FAILURE_PREEXPOSURE","task_id":tid,"arm":arm,"attempt":attempt,"error_type":type(ex).__name__,"error":str(ex),"steps":steps,"first_executable_action":first,"actions":actions,"treatment_exposed":exposed}
 finally:
  try:task.release()
  except Exception:pass

def stage_schedule(protocol:dict[str,Any],model_key:str)->list[dict[str,Any]]:return list(protocol["staging"]["Qwen" if model_key=="qwen" else "Llama"]["schedule"])

def execute_stage(model_key:str,protocol:dict[str,Any],panel:dict[str,Any],manifest:dict[str,Any],records:dict[str,dict[str,Any]],outdir:pathlib.Path,resume:bool=False)->None:
 runtime_preflight(manifest);adapter=r47.build_adapter(manifest);sched=stage_schedule(protocol,model_key);root=outdir/model_key;root.mkdir(parents=True,exist_ok=True);terminal_path=root/"terminal-arms.jsonl";event_path=root/"attempt-events.jsonl";terminal=rows(terminal_path)
 expected=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in sched]
 got=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in terminal]
 if got!=expected[:len(got)]:raise RuntimeError("terminal-ledger-not-schedule-prefix")
 if terminal and len(terminal)<len(sched) and not resume:raise RuntimeError("partial-stage-requires-resume")
 # Recover an interrupted current item: any recorded exposure makes it non-rerunnable.
 events=rows(event_path)
 if len(terminal)<len(sched):
  item=sched[len(terminal)];key=(str(item["task_id"]),str(item["arm"]));ev=[x for x in events if (str(x.get("task_id")),str(x.get("arm")))==key]
  if any(x.get("event")=="TREATMENT_EXPOSURE_DISPATCHED" for x in ev):
   append(terminal_path,{"stage_ordinal":int(item["stage_ordinal"]),"task_id":key[0],"arm":key[1],"status":"TECHNICAL_MISSING_POST_EXPOSURE_RECOVERED","terminal_success":None,"treatment_exposed":True,"at":r48.now()});terminal=rows(terminal_path)
 for item in sched[len(terminal):]:
  ordinal=int(item["stage_ordinal"]);tid=str(item["task_id"]);arm=str(item["arm"]);ctx=r70.render_contexts(records[tid])[arm];prompt=prompt_for(manifest,ctx);pre_fail=[]
  for attempt in range(1,MAX_PREEXPOSURE_ATTEMPTS+1):
   append(event_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"attempt":attempt,"event":"ATTEMPT_BEGIN","at":r48.now(),"memory_context_sha256":hashlib.sha256(ctx.encode()).hexdigest(),"system_prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest()})
   result=run_attempt(manifest,adapter,tid,arm,prompt,event_path,attempt)
   if result["status"]=="TECHNICAL_FAILURE_PREEXPOSURE":
    pre_fail.append(result);append(event_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"attempt":attempt,"event":"PREEXPOSURE_FAILURE","at":r48.now(),"error_type":result["error_type"],"error":result["error"]});continue
   if result["status"]=="COMPLETE":
    ad=root/"arms"/f"{ordinal:04d}-{tid}-{arm}";ad.mkdir(parents=True,exist_ok=False);tp=ad/"trace.json";tp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");row={"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","terminal_success":result["terminal_success"],"steps":result["steps"],"first_executable_action":result["first_executable_action"],"first_executable_action_sha256":hashlib.sha256(str(result["first_executable_action"] or "<NONE>").encode()).hexdigest(),"attempt":attempt,"preexposure_failures":len(pre_fail),"treatment_exposed":True,"trace_file":str(tp),"trace_file_sha256":sha(tp),"completed_at":r48.now()};append(terminal_path,row);break
   # post exposure technical missing: terminal, never retry
   ad=root/"arms"/f"{ordinal:04d}-{tid}-{arm}";ad.mkdir(parents=True,exist_ok=False);fp=ad/"technical-missing.json";fp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");append(terminal_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"TECHNICAL_MISSING_POST_EXPOSURE","terminal_success":None,"attempt":attempt,"preexposure_failures":len(pre_fail),"treatment_exposed":True,"failure_file":str(fp),"failure_file_sha256":sha(fp),"completed_at":r48.now()});break
  else:
   append(terminal_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"TECHNICAL_MISSING_PREEXPOSURE_EXHAUSTED","terminal_success":None,"attempt":MAX_PREEXPOSURE_ATTEMPTS,"preexposure_failures":len(pre_fail),"treatment_exposed":False,"completed_at":r48.now()})

def exact_stats(effect_rows:list[tuple[str,bool,bool]],planned_n:int)->dict[str,Any]:
 effects=[];left_only=right_only=0
 for _,left,right in effect_rows:
  d=int(left)-int(right);effects.append(d);left_only+=int(left and not right);right_only+=int(right and not left)
 n=len(effects);obs_sum=sum(effects);missing=planned_n-n
 if n:
  lo,hi=r48.percentile_ci(effects,r70.BOOTSTRAP_SEED,100000);p=r48.exact_two_sided_signflip(left_only,right_only);rd=obs_sum/n
  blo,bhi=clopper_pearson(left_only,n,0.975);rlo,rhi=clopper_pearson(right_only,n,0.975);conservative=[blo-rhi,bhi-rlo]
 else:lo=hi=p=rd=None;conservative=[-1,1]
 sens=[(obs_sum-missing)/planned_n,(obs_sum+missing)/planned_n]
 direction=0 if not effects or obs_sum==0 else (1 if obs_sum>0 else -1)
 detected=bool(n and p<0.05 and ((direction>0 and sens[0]>0) or (direction<0 and sens[1]<0)))
 return {"planned_pairs":planned_n,"complete_pairs":n,"technical_missing_pairs":missing,"paired_risk_difference_complete_pairs":rd,"left_only_success":left_only,"right_only_success":right_only,"discordant_pairs":left_only+right_only,"exact_two_sided_signflip_p":p,"paired_bootstrap_ci95_complete_pairs":[lo,hi],"conservative_sparse_rd_ci95_complete_pairs":conservative,"technical_missing_worst_best_rd_bounds":sens,"direction":direction,"effect_detected":detected}

def contrast(stage_rows:list[dict[str,Any]],ids:list[str],left:str,right:str)->dict[str,Any]:
 by={}
 for r in stage_rows:by.setdefault(str(r["task_id"]),{})[str(r["arm"])]=r
 complete=[];action_diff=0;steps=[]
 for tid in ids:
  a=by.get(tid,{}).get(left);b=by.get(tid,{}).get(right)
  if not a or not b or type(a.get("terminal_success")) is not bool or type(b.get("terminal_success")) is not bool:continue
  complete.append((tid,bool(a["terminal_success"]),bool(b["terminal_success"])));action_diff+=int(a.get("first_executable_action")!=b.get("first_executable_action"));steps.append(int(a.get("steps") or 0)-int(b.get("steps") or 0))
 st=exact_stats(complete,len(ids));st.update({"left":left,"right":right,"first_action_diff_complete_pairs":action_diff,"mean_step_difference_complete_pairs":sum(steps)/len(steps) if steps else None,"diagnostics_inferential_authority":False});return st

def analyze(protocol:dict[str,Any],panel:dict[str,Any],outdir:pathlib.Path)->dict[str,Any]:
 ids=[str(x) for x in panel["representative_ids"]];mixed=[str(x) for x in protocol["units"]["mixed_provenance_ids"]];q=rows(outdir/"qwen"/"terminal-arms.jsonl");l=rows(outdir/"llama"/"terminal-arms.jsonl")
 if len(q)!=189 or len(l)!=132:raise RuntimeError(f"stage-seals-not-complete:{len(q)}:{len(l)}")
 qp=contrast(q,ids,"T_truthful","P_neutral");qs=contrast(q,mixed,"T_truthful","S_shuffled");lp=contrast(l,ids,"T_truthful","P_neutral")
 primary_state="EFFECT_DETECTED" if qp["effect_detected"] else "NO_EFFECT_DETECTED"
 correctness_open=qp["effect_detected"];correctness_sensitive=bool(correctness_open and qs["effect_detected"] and qs["direction"]==qp["direction"])
 replication=bool(qp["effect_detected"] and lp["effect_detected"] and lp["direction"]==qp["direction"])
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R71-COMPLETE-ONLY-ANALYSIS","status":"R71_SEMANTIC_CONTROL_R2_COMPLETE_ONLY_ANALYSIS","protocol_receipt_sha256":protocol["receipt_sha256"],"Qwen_primary_T_minus_P":qp,"Qwen_gatekept_T_minus_S":qs,"Qwen_primary_state":primary_state,"correctness_confirmatory_gate_open":correctness_open,"correctness_sensitive_detected":correctness_sensitive,"Llama_executor_replication_T_minus_P":lp,"same_direction_executor_replication_detected":replication,"interpretation_rules":{"NO_EFFECT_DETECTED":"no resolved truthful-information increment; not equivalence, not proof of prompt-format-only effect","EFFECT_DETECTED_without_correctness":"truthful-vs-neutral field treatment effect; association-correctness mechanism unresolved","EFFECT_DETECTED_with_correctness":"truthful-vs-neutral effect with same-direction correctness-sensitivity evidence on Qwen"},"cross_model_pooling":False,"semantic_reasoning_claim_from_first_action":False,"PSMG_efficacy_identified":False,"L3_transport_complete":False,"scientific_authority":False,"experiment_authority":False};out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser();
 for x in ["protocol","panel","hold","token-audit","review","qwen-manifest","llama-manifest","r54","output-dir"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 p.add_argument("--authority",type=pathlib.Path);p.add_argument("--model",choices=["qwen","llama"]);p.add_argument("--resume",action="store_true");p.add_argument("--validate-only",action="store_true");p.add_argument("--analyze",action="store_true");a=p.parse_args();protocol,panel,hold,ta,rv,qm,lm,r54=map(load,[a.protocol,a.panel,a.hold,a.token_audit,a.review,a.qwen_manifest,a.llama_manifest,a.r54]);manifests=static_preflight(protocol,panel,hold,ta,rv,qm,lm,r54,a.r54.resolve())
 if a.validate_only:print(json.dumps({"status":"R71_STATIC_PREFLIGHT_PASS_EXECUTION_STILL_CLOSED","planned_new_trajectories":321,"Qwen":189,"Llama":132,"authority_required":True,"protocol_receipt_sha256":protocol["receipt_sha256"]},sort_keys=True));return
 if a.authority is None:raise RuntimeError("execution-or-analysis-requires-separate-authority")
 auth=load(a.authority)
 if a.analyze:
  authority_check(auth,protocol,"qwen",analysis=True);out=analyze(protocol,panel,a.output_dir.resolve());op=a.output_dir/"semantic-control-r2-analysis.json";op.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(out,ensure_ascii=False,sort_keys=True));return
 if not a.model:raise RuntimeError("--model-required")
 authority_check(auth,protocol,a.model);execute_stage(a.model,protocol,panel,manifests[a.model],runtime_records(panel,r54),a.output_dir.resolve(),a.resume);print(json.dumps({"status":"R71_STAGE_TERMINAL","model":a.model},sort_keys=True))
if __name__=="__main__":main()
