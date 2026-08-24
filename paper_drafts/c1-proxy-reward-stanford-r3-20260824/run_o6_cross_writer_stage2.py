#!/usr/bin/env python3
from __future__ import annotations
import argparse, fcntl, hashlib, json, os, random, re, sys
from collections import Counter
from pathlib import Path
from typing import Any

DESIGN_SHA="e33996f4e4f00da7b162bf7e9c26ca004aaf7e5d04f2547aacbc04f47ad05c1e"
HANDOFF_SHA="1ec986064b4c497dd04cd11366b78c31548d1c1ce9b271c8cf5c1382b650d04b"
SOURCES=["21","22","23","25"]; FUTURES=["164","385","387","388"]
CONDS=["success_label_memory","failure_label_memory"]; N=8; CALLS=256
MODEL="doubao-seed-2.0-mini"; RESOLVED="doubao-seed-2-0-mini-260215"
BASE_URL="https://ark.cn-beijing.volces.com/api/plan/v3"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(d,dict):raise RuntimeError(f"JSON root not object:{p}")
 return d
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");os.replace(t,p)
def req(ok:bool,msg:str):
 if not ok:raise RuntimeError(msg)

def clean(a:str|None)->str:
 a=str(a or "").strip()
 if len(a)>=2 and a[0]==a[-1] and a[0] in "'\"":a=a[1:-1]
 return re.sub(r"(\w+)[\u2010-\u2015\u2212-](\w+)",r"\1-\2",a).lower()
def score(pred:str,refs:list[str])->tuple[float,list[dict[str,Any]]]:
 p=clean(pred);out=[];s=1.0
 for ref in refs:
  v=float(clean(ref) in p);s*=v;out.append({"ref":ref,"score":v})
 return s,out

def evidence(traj_json:str)->tuple[str,list[str]]:
 tr=json.loads(traj_json);states=[];hashes=[];seen=set()
 for step in (tr.get("steps") or {}).values():
  c=((step.get("input_messages") or {}).get("contents") or [])
  if not c:continue
  text=str(c[-1].get("content") or "")
  if "[Current state starts here]" not in text:continue
  text=text.split("[Current state starts here]",1)[1].strip();h=tsha(text)
  if h in seen:continue
  seen.add(h);states.append(text);hashes.append(h)
 return "\n\n--- RELEASED BROWSER STATE ---\n\n".join(states),hashes

def prompt(task:str,ev:str,memory:str)->str:
 return f"""You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence.
- REUSABLE MEMORY is procedural guidance. It may influence how you interpret or organize the evidence, but it is not task-specific ground truth.
- Do not invent reviewer names, ratings, product facts, or quotes that are absent from the released evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

REUSABLE MEMORY:
{memory.strip() if memory.strip() else 'No reusable memory is supplied.'}

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""

def validate(c:dict[str,Any]):
 req(c.get("status")=="FROZEN_BEFORE_PROVIDER_CALLS","contract not frozen")
 req(c.get("paper_id")=="D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE" and c.get("objection_id")=="PROXY-O6","identity drift")
 req(c["design"]["sha256"]==DESIGN_SHA and c["stage1_handoff"]["sha256"]==HANDOFF_SHA,"design/handoff drift")
 req(c["source_memory_tasks"]==SOURCES and c["future_tasks"]==FUTURES and c["conditions"]==CONDS,"support drift")
 req(c["rollouts_per_cell_per_condition"]==N and c["expected_provider_calls"]==CALLS,"call geometry drift")
 m=c["model"];req(m["requested"]==MODEL and m["expected_resolved"]==RESOLVED and m["temperature"]==0.2 and m["max_output_tokens"]==900 and m["thinking"]=="disabled","model drift")
 req(m["provider_retries"]==0 and m["allow_thinking_compatibility_fallback"] is False and m["substitution_allowed"] is False,"provider semantics drift")
 g=c["terminal_gate"];req(g["permutation_repetitions"]==100000 and g["permutation_seed"]==20260824 and g["alpha"]==0.05 and g["min_mean_absolute_success_rate_difference"]==0.15,"gate drift")
 req(c["o5_no_memory"]["primary_gate_uses"] is False and c["original_f2r1"]["primary_gate_uses"] is False,"secondary evidence leaked into gate")
 miss=c["missingness_policy"];req(miss["provider_retries"]==0 and miss["stop_after_first_no_text_provider_failure"] is True and miss["top_up_failed_units"] is False and miss["text_bearing_provider_status_incomplete_is_scorable"] is True,"missingness drift")
 a=c["authority"];req(a["experiment_authority"] is True and a["provider_call_authority"] is True and a["claim_expansion_authority"] is False and a["submission_authority"] is False,"authority drift")
 for r in c["source_artifacts"].values():
  p=Path(r["path"]);req(p.is_file() and sha(p)==r["sha256"],f"source drift:{p}")
 hp=Path(c["human_authority"]["path"]);req(hp.is_file() and sha(hp)==c["human_authority"]["sha256"],"human authority drift")
 h=Path(c["stage1_handoff"]["path"]);req(h.is_file() and sha(h)==HANDOFF_SHA,"handoff file drift")
 for s in SOURCES:
  for cond in CONDS:
   r=c["memory_objects"][s][cond];p=Path(r["path"]);req(p.is_file() and sha(p)==r["sha256"],f"memory drift:{s}/{cond}")
 r=c["code"]["runner"];req(Path(r["path"]).resolve()==Path(__file__).resolve() and sha(Path(__file__))==r["sha256"],"runner SHA drift")

def runtime(c:dict[str,Any]):
 root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root));sys.path.insert(0,str(Path(c["vendor_path"])))
 import pyarrow.parquet as pq
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
 load_env_file(Path(c["provider_env_file"]));base=ArkSettings.from_env();req(bool(base.api_key),"credential absent");req(base.base_url==BASE_URL,"base URL drift")
 cfg=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0)
 return pq,ArkResponseStateError,ArkResponsesClient(cfg),cfg.safe_summary()

def tasks(c:dict[str,Any],pq)->dict[str,dict[str,Any]]:
 sup=load(Path(c["source_artifacts"]["support"]["path"]));req(sup.get("status")=="SUPPORT_QUALIFIED","support not qualified")
 sr={str(x["task_id"]):x for x in sup["tasks"]};par=Path(c["source_artifacts"]["parquet"]["path"])
 rel={str(x["task_id"]):x for x in pq.read_table(par,columns=["task_id","trajectory_json"]).to_pylist()};out={}
 for f in FUTURES:
  r=sr[f];req(r["qualified"] is True,f"future not qualified:{f}");ev,hs=evidence(str(rel[f]["trajectory_json"]));req(tsha(ev)==r["evidence_sha256"] and hs==r["released_state_sha256"],f"evidence drift:{f}")
  out[f]={"task_prompt":str(r["task_prompt"]),"reference_answers":list(r["reference_answers"]),"evidence":ev}
 return out

def stage(s:str,f:str,c:str,i:int)->str:return f"terminal-{f}-source-{s}-{c}-r{i}"

def one(client,error_type,s:str,f:str,cond:str,i:int,t:dict[str,Any],memory:str,root:Path)->dict[str,Any]:
 st=stage(s,f,cond,i);sp=root/"stages"/f"{st}.json"
 if sp.is_file():
  d=load(sp);req(d.get("stage")==st,f"cache identity drift:{st}");return d
 pr=prompt(t["task_prompt"],t["evidence"],memory);base={"stage":st,"source_memory_task":s,"future_task":f,"condition":cond,"rollout":i,"prompt_sha256":tsha(pr),"requested_model":MODEL}
 try:
  r=client.respond(pr,model=MODEL,max_output_tokens=900,temperature=0.2,thinking="disabled",store=True,allow_thinking_compatibility_fallback=False);ans=str(r.get("text") or "").strip()
  writej(root/"provider-responses"/f"{st}.json",{**base,"response_id":r.get("response_id"),"provider_status":r.get("status"),"requested_model_returned":r.get("requested_model"),"resolved_model":r.get("resolved_model"),"usage":r.get("usage") or {},"answer":ans,"answer_sha256":tsha(ans) if ans else "","thinking_compatibility_fallback":r.get("thinking_compatibility_fallback")})
  req(str(r.get("requested_model"))==MODEL and str(r.get("resolved_model"))==RESOLVED,f"model resolution drift:{r.get('resolved_model')}");req(r.get("thinking_compatibility_fallback") is False,"thinking fallback");req(bool(ans),"no assistant text")
  sc,checks=score(ans,list(t["reference_answers"]));d={**base,"status":"complete","provider_status":r.get("status"),"response_id":r.get("response_id"),"resolved_model":r.get("resolved_model"),"usage":r.get("usage") or {},"answer_sha256":tsha(ans),"benchmark_score":sc,"evaluator_checks":checks}
 except error_type as e:d={**base,"status":"provider_state_failure_no_text","error_type":type(e).__name__,"provider_receipt":e.receipt()}
 except Exception as e:d={**base,"status":"provider_or_runtime_failure","error_type":type(e).__name__,"error":str(e)[:1000]}
 writej(sp,d);return d

def stats(rows:list[dict[str,Any]])->tuple[float,list[dict[str,Any]]]:
 vals=[];cells=[]
 for s in SOURCES:
  for f in FUTURES:
   a=[float(r["benchmark_score"]) for r in rows if r["source_memory_task"]==s and r["future_task"]==f and r["condition"]==CONDS[0]];b=[float(r["benchmark_score"]) for r in rows if r["source_memory_task"]==s and r["future_task"]==f and r["condition"]==CONDS[1]]
   req(len(a)==N and len(b)==N,f"incomplete cell:{s}/{f}");pa=sum(a)/N;pb=sum(b)/N;v=abs(pa-pb);vals.append(v);cells.append({"source_memory_task":s,"future_task":f,"success_memory_rate":round(pa,6),"failure_memory_rate":round(pb,6),"absolute_rate_difference":round(v,6),"signed_failure_minus_success":round(pb-pa,6)})
 return sum(vals)/len(vals),cells

def perm(rows:list[dict[str,Any]],observed:float)->float:
 rng=random.Random(20260824);pools=[]
 for s in SOURCES:
  for f in FUTURES:
   a=[float(r["benchmark_score"]) for r in rows if r["source_memory_task"]==s and r["future_task"]==f and r["condition"]==CONDS[0]];b=[float(r["benchmark_score"]) for r in rows if r["source_memory_task"]==s and r["future_task"]==f and r["condition"]==CONDS[1]];pools.append(a+b)
 ge=0
 for _ in range(100000):
  vs=[]
  for pool in pools:
   z=list(pool);rng.shuffle(z);vs.append(abs(sum(z[:N])/N-sum(z[N:])/N))
  if sum(vs)/16>=observed-1e-12:ge+=1
 return (ge+1)/100001

def report(cp:Path,c:dict[str,Any],rows:list[dict[str,Any]],provider:dict[str,Any])->dict[str,Any]:
 good=[r for r in rows if r.get("status")=="complete"];bad=[r for r in rows if r.get("status")!="complete"];full=len(good)==CALLS and not bad;obs=pv=None;cells=[];gate=False
 if full:obs,cells=stats(good);pv=perm(good,obs);gate=obs>=0.15 and pv<0.05
 signed=sum(float(x["signed_failure_minus_success"]) for x in cells)/16 if cells else None;decision="SUPPORT_CROSS_WRITER_TERMINAL_REPLICATION" if gate else ("CROSS_WRITER_TERMINAL_GENERALIZATION_NOT_ESTABLISHED" if full else "STAGE2_SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY")
 return {"schema_version":"1.0","experiment_id":c["experiment_id"],"paper_id":c["paper_id"],"objection_id":c["objection_id"],"status":"O6_STAGE2_COMPLETE" if full else "O6_STAGE2_INCOMPLETE","contract_sha256":sha(cp),"provider":provider,"summary":{"requested_primary_calls":CALLS,"complete_primary_calls":len(good),"provider_failures":len(bad),"provider_status_counts":dict(sorted(Counter(str(r.get("provider_status") or "unknown") for r in good).items())),"observed_mean_absolute_success_rate_difference":None if obs is None else round(obs,6),"mean_signed_failure_minus_success":None if signed is None else round(signed,6),"permutation_p_ge_observed":None if pv is None else round(pv,6),"gate_pass":gate},"cell_results":cells,"rollouts":[{k:r.get(k) for k in ("source_memory_task","future_task","condition","rollout","answer_sha256","benchmark_score","evaluator_checks","provider_status","resolved_model","usage")} for r in good],"failures":[{k:r.get(k) for k in ("source_memory_task","future_task","condition","rollout","stage","status","error_type","provider_receipt","error")} for r in bad],"decision":decision,"scientific_authority":False,"experiment_authority":True,"claim_expansion_authority":False}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--contract",required=True,type=Path);ap.add_argument("--output",required=True,type=Path);ap.add_argument("--private-root",required=True,type=Path);a=ap.parse_args();c=load(a.contract);validate(c);a.private_root.mkdir(parents=True,exist_ok=True);fh=(a.private_root/"transaction.lock").open("a+")
 try:fcntl.flock(fh.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({"status":"TRANSACTION_ALREADY_RUNNING","provider_calls_executed_by_this_process":0}));return 3
 try:
  pq,etype,client,ps=runtime(c);td=tasks(c,pq);mem={(s,cond):Path(c["memory_objects"][s][cond]["path"]).read_text(encoding="utf-8") for s in SOURCES for cond in CONDS};rows=[];stop=False
  for s in SOURCES:
   if stop:break
   for f in FUTURES:
    if stop:break
    for cond in CONDS:
     if stop:break
     for i in range(1,N+1):
      r=one(client,etype,s,f,cond,i,td[f],mem[(s,cond)],a.private_root);rows.append(r);writej(a.output,report(a.contract,c,rows,ps))
      if len(rows)%8==0 or r.get("status")!="complete":print(json.dumps({"stage":r["stage"],"status":r["status"],"complete_so_far":sum(x.get("status")=="complete" for x in rows),"seen_so_far":len(rows)}),flush=True)
      if r.get("status")!="complete":stop=True;break
  out=report(a.contract,c,rows,ps);writej(a.output,out);print(json.dumps({"status":out["status"],"summary":out["summary"],"decision":out["decision"]},indent=2),flush=True);return 0 if out["status"]=="O6_STAGE2_COMPLETE" else 2
 finally:fcntl.flock(fh.fileno(),fcntl.LOCK_UN);fh.close()
if __name__=="__main__":raise SystemExit(main())
