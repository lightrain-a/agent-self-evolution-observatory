from __future__ import annotations

import argparse,json,os,time
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Iterable

from .p0_alfworld_adapter import ALFWorldGameRunner,HFAdmissiblePolicy,load_config,run_episode


def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def atomic(p:Path,x:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n");t.replace(p)
def append(p:Path,x:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f:f.write(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
def hist(root:Path)->Iterable[dict[str,Any]]:
 for p in sorted((root/"runs").glob("*/raw-traces.jsonl")):
  try:
   for line in p.read_text(encoding="utf-8").splitlines():
    if not line.strip():continue
    r=json.loads(line);r=r.get("trace") if isinstance(r.get("trace"),dict) else r;task=str(r.get("task_id") or r.get("target_task_id") or r.get("gamefile") or "")
    if task:yield {**r,"task_id":task,"source_artifact":str(p)}
  except Exception:continue
def pick(root:Path,token:str,success:bool|None,n:int):
 out=[];seen=set()
 for r in hist(root):
  t=r["task_id"]
  if token not in t or t in seen or (success is not None and bool(r.get("success")) is not success):continue
  seen.add(t);out.append(r)
 return sorted(out,key=lambda r:r["task_id"])[:n]
def usage_delta(a,b):return {k:int(b.get(k,0))-int(a.get(k,0)) for k in set(a)|set(b)}
def eval_set(runner,policy,tasks,split,patch,label,traces):
 rows=[]
 for task in tasks:
  env=runner.build_env(split,[task])
  try:
   before=policy.usage_snapshot();r=run_episode(env,policy,patch,max_steps=50);after=policy.usage_snapshot();r.update({"task_id":task,"condition":label,"patch":patch,"usage":usage_delta(before,after),"recorded_at":now()});append(traces,r);rows.append(r)
  finally:
   c=getattr(env,"close",None);c() if callable(c) else None
 return rows
def rate(rows,label):
 x=[r for r in rows if r["condition"]==label];return sum(int(r.get("success") or 0) for r in x)/max(1,len(x))
def analyze(rows,patch_ids):
 bc,br,bf=rate(rows,"base-current"),rate(rows,"base-retention"),rate(rows,"base-future-before");ca=rate(rows,"control-future-after");cg=ca-bf;cs=[]
 for pid in patch_ids:
  cur,ret,bef,aft=rate(rows,pid+"-current"),rate(rows,pid+"-retention"),rate(rows,pid+"-future-before"),rate(rows,pid+"-future-after");matched=abs(cur-bc)<=.25 and abs(ret-br)<=.25;gain=aft-bef;cs.append({"patch_id":pid,"current":cur,"retention":ret,"future_before":bef,"future_after":aft,"adaptation_gain":gain,"control_adaptation_gain":cg,"future_learnability_delta":gain-cg,"matched_current_retention":matched})
 m=[c for c in cs if c["matched_current_retention"]];nz=[c for c in m if abs(c["future_learnability_delta"])>=.25];rng=(max((c["future_learnability_delta"] for c in m),default=0)-min((c["future_learnability_delta"] for c in m),default=0)) if m else 0;support=len(m)>=2 and (len(nz)>=1 or rng>=.25)
 return {"schema_version":"1.0","experiment":"PF-1-FUTURE-LEARNABILITY-F0","support_pass":support,"baseline":{"current":bc,"retention":br,"future_before":bf,"control_future_after":ca,"control_adaptation_gain":cg},"matched_candidates":len(m),"nonzero_matched_candidates":len(nz),"future_learnability_range":rng,"candidates":cs,"scientific_semantics":"F0/P0-Support only; no METHOD-PASS/FAIL authority."}
def main():
 p=argparse.ArgumentParser();p.add_argument("--data-root",required=True);p.add_argument("--model-path",required=True);p.add_argument("--alfworld-config",required=True);p.add_argument("--output-dir",required=True);p.add_argument("--device",default="cuda");a=p.parse_args();root=Path(a.data_root);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);traces=out/"raw-traces.jsonl";progress=out/"progress.json"
 if traces.exists():raise RuntimeError("PF-1 F0 output must be fresh; refusing to mix adaptation rows")
 train_fail=pick(root,"/train/",False,3);seen_ok=pick(root,"/valid_seen/",True,8);unseen=pick(root,"/valid_unseen/",None,4);seen_fail=pick(root,"/valid_seen/",False,1)
 if len(train_fail)<3 or len(seen_ok)<8 or len(unseen)<4 or not seen_fail:raise RuntimeError(f"insufficient frozen substrate train_fail={len(train_fail)} seen_ok={len(seen_ok)} unseen={len(unseen)} seen_fail={len(seen_fail)}")
 current=[r["task_id"] for r in seen_ok[:4]];retention=[r["task_id"] for r in seen_ok[4:8]];future=[r["task_id"] for r in unseen[:4]];future_source=seen_fail[0]
 runner=ALFWorldGameRunner(load_config(Path(a.alfworld_config)));policy=HFAdmissiblePolicy(Path(a.model_path),device=a.device,policy_mode="react-family");patches=[]
 for i,src in enumerate(train_fail,1):patches.append({"patch_id":f"p{i}","patch":policy.propose_patch(src,seed=4200+i,variant=i-1),"source_task":src["task_id"]})
 control2=policy.propose_patch(future_source,seed=7777,previous_patch="",variant=0);start=time.time();rows=[]
 rows+=eval_set(runner,policy,current,"eval_in_distribution","","base-current",traces);rows+=eval_set(runner,policy,retention,"eval_in_distribution","","base-retention",traces);rows+=eval_set(runner,policy,future,"eval_out_of_distribution","","base-future-before",traces);rows+=eval_set(runner,policy,future,"eval_out_of_distribution",control2,"control-future-after",traces)
 for i,x in enumerate(patches,1):
  q=x["patch"];rows+=eval_set(runner,policy,current,"eval_in_distribution",q,x["patch_id"]+"-current",traces);rows+=eval_set(runner,policy,retention,"eval_in_distribution",q,x["patch_id"]+"-retention",traces);rows+=eval_set(runner,policy,future,"eval_out_of_distribution",q,x["patch_id"]+"-future-before",traces);second=policy.propose_patch(future_source,seed=7777,previous_patch=q,variant=0);x["second_patch"]=second;rows+=eval_set(runner,policy,future,"eval_out_of_distribution",q+"\n"+second,x["patch_id"]+"-future-after",traces);atomic(progress,{"schema_version":"1.0","status":"running","candidate":i,"candidates":len(patches),"elapsed_hours":(time.time()-start)/3600,"updated_at":now()})
 ana=analyze(rows,[x["patch_id"] for x in patches]);ana.update({"patches":patches,"control_second_patch":control2,"future_adaptation_source_task":future_source["task_id"],"task_sets":{"current":current,"retention":retention,"future":future}});atomic(out/"analysis.json",ana);atomic(progress,{"schema_version":"1.0","status":"complete","candidate":len(patches),"candidates":len(patches),"elapsed_hours":(time.time()-start)/3600,"updated_at":now()});res={"schema_version":"1.0","status":"complete","analysis":ana,"usage":policy.usage_snapshot(),"completed_at":now()};atomic(out/"result.json",res);print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
