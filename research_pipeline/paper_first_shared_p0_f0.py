from __future__ import annotations

import argparse,json,math,os,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Iterable

from .alfworld_react_scaffold import extract_task_goal,task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner,HFAdmissiblePolicy,load_config
from .paper_first_p0_promotions import require_local_validation_authority

FAULTS=("prompt","workflow","tool"); SURFACES=("prompt","workflow","tool")
RISK={"success":0.0,"premature-stop":1.0,"search-timeout":2.0,"missing-required-transform":3.0,"loop-timeout":3.0,"invalid-action":4.0}

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def atomic(p:Path,x:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n"); t.replace(p)
def append(p:Path,x:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f: f.write(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n"); f.flush(); os.fsync(f.fileno())
def rows_from_history(root:Path)->Iterable[dict[str,Any]]:
 for p in sorted((root/"runs").glob("*/raw-traces.jsonl")):
  try:
   for line in p.read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    r=json.loads(line); r=r.get("trace") if isinstance(r.get("trace"),dict) else r
    task=str(r.get("task_id") or r.get("target_task_id") or r.get("gamefile") or "")
    if task: yield {**r,"task_id":task,"source_artifact":str(p)}
  except Exception: continue
def select_tasks(root:Path,n:int=6)->list[str]:
 out=[]; seen=set()
 for r in rows_from_history(root):
  task=r["task_id"]; acts=[str(x).lower() for x in r.get("actions") or []]
  if "/valid_seen/" not in task or not r.get("success") or not any(a.startswith("open ") for a in acts) or task in seen: continue
  seen.add(task); out.append(task)
 return sorted(out)[:n]
def usage_delta(a,b): return {k:int(b.get(k,0))-int(a.get(k,0)) for k in set(a)|set(b)}
def nonprogress(cmds,action): return "look" if "look" in cmds else next((c for c in cmds if c.startswith("examine ")),action)

def run_one(runner,split,task,policy,fault,repair,max_steps=50):
 env=runner.build_env(split,[task])
 try:
  obs,info=env.reset(); start=str(obs[0]); hist=[]; acts=[]; obss=[start]; raws=[]; invalid=0; score=0.; won=False
  goal=extract_task_goal(start); fam=task_family_from_gamefile(task); patch=""
  if fault=="prompt": patch="Never use the open action, even for a closed receptacle. Search elsewhere instead."
  if repair=="prompt": patch+="\nRepair override: if a required object may be inside a closed receptacle, opening it has priority."
  before=policy.usage_snapshot(); done=False
  while not done and len(acts)<max_steps:
   cmds=list((info.get("admissible_commands") or [[]])[0]);
   if not cmds: break
   visible=cmds
   if fault=="tool" and repair!="tool": visible=[c for c in cmds if not c.startswith("open ")] or cmds
   action,bad,raw=policy.choose(str(obs[0]),visible,hist,patch,goal_context=goal,task_family=fam)
   if fault=="workflow" and repair!="workflow" and len(acts)>=2 and action.startswith(("take ","move ","put ","use ","clean ","cool ","heat ")): action=nonprogress(cmds,action)
   invalid+=int(bad); raws.append(raw); obs,scores,dones,info=env.step([action]); acts.append(action); obss.append(str(obs[0])); hist.append((action,str(obs[0]))); score=float(scores[0]); done=bool(dones[0]); won=bool((info.get("won") or [score>0])[0])
  return {"task_id":task,"task_family":fam,"fault":fault,"repair":repair,"success":int(won or score>0),"score":score,"steps":len(acts),"invalid_actions":invalid,"actions":acts,"observations":obss,"raw_choices":raws,"task_goal":goal,"usage":usage_delta(before,policy.usage_snapshot()),"recorded_at":now()}
 finally:
  c=getattr(env,"close",None); c() if callable(c) else None

def feats(r):
 a=[str(x).lower() for x in r.get("actions") or []]; n=max(1,len(a)); c=Counter((x.split() or [""])[0] for x in a)
 return [float(r.get("steps") or 0)/50,float(r.get("invalid_actions") or 0)/n,1-len(set(a))/n,c["open"]/n,c["take"]/n,c["move"]/n,c["examine"]/n,c["look"]/n,c["use"]/n]
def dist(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def centers(rows):
 by=defaultdict(list)
 for r in rows: by[r["fault"]].append(feats(r))
 return {k:[sum(x[i] for x in xs)/len(xs) for i in range(len(xs[0]))] for k,xs in by.items()}
def acc(rows,cen):
 if not rows:return 1.0
 return sum(min(cen,key=lambda k:dist(feats(r),cen[k]))==r["fault"] for r in rows)/len(rows)
def mode(r):
 if r["success"]: return "success"
 acts=[str(x).lower() for x in r.get("actions") or []]; joined=" ".join(acts); task=r["task_id"].lower(); req=None
 if "pick_clean_then_place" in task:req="clean "
 elif "pick_cool_then_place" in task:req="cool "
 elif "pick_heat_then_place" in task:req="heat "
 elif "look_at_obj_in_light" in task:req="use "
 if req and req not in joined:return "missing-required-transform"
 if r.get("invalid_actions",0)>0:return "invalid-action"
 rep=1-len(set(acts))/max(1,len(acts))
 if r.get("steps",0)>=50 and rep>=.45:return "loop-timeout"
 if r.get("steps",0)>=50:return "search-timeout"
 return "premature-stop"

def analyze(rows,tasks):
 held=set(tasks[len(tasks)//2:]); dev=set(tasks[:len(tasks)//2]); idx={(r["task_id"],r["fault"],r["repair"]):r for r in rows}
 own=[]
 for task in tasks:
  for fault in FAULTS:
   base=idx[task,fault,"none"]; reps={s:idx[task,fault,s] for s in SURFACES}; gains={s:reps[s]["success"]-base["success"] for s in SURFACES}; best=max(SURFACES,key=lambda s:(gains[s],-reps[s]["steps"],s==fault)); own.append({"task_id":task,"fault":fault,"split":"heldout" if task in held else "dev","baseline_success":base["success"],"repair_success":{s:reps[s]["success"] for s in SURFACES},"best_surface":best,"oracle_correct":best==fault})
 h=[r for r in own if r["split"]=="heldout"]; per={s:sum(r["repair_success"][s] for r in h)/max(1,len(h)) for s in SURFACES}; oracle=sum(r["repair_success"][r["fault"]] for r in h)/max(1,len(h)); fixed=max(per.values()); ownacc=sum(r["oracle_correct"] for r in h)/max(1,len(h)); distinct=len({r["best_surface"] for r in h}); pf2=distinct>=2 and oracle-fixed>=.15 and ownacc>=.60
 cen=centers([idx[t,f,"none"] for t in dev for f in FAULTS]); base_diag=acc([idx[t,f,"none"] for t in held for f in FAULTS],cen); post={}; succ={}
 for s in SURFACES:
  subset=[idx[t,f,s] for t in held for f in FAULTS if f!=s]; failed=[r for r in subset if not r["success"]]; post[s]=acc(failed,cen); succ[s]=sum(r["success"] for r in subset)/max(1,len(subset))
 drops={s:base_diag-post[s] for s in SURFACES}; pf4=base_diag>=.5 and max(drops.values())>=.15
 transport=Counter(); summaries={}
 for s in SURFACES:
  pairs=[]
  for t in held:
   for f in FAULTS:
    b=mode(idx[t,f,"none"]); a=mode(idx[t,f,s]); transport[s,b,a]+=1; pairs.append((b,a,idx[t,f,s]["success"]))
  sr=sum(x[2] for x in pairs)/len(pairs); residual=[RISK.get(a,2) for _,a,ok in pairs if not ok]; summaries[s]={"success_rate":sr,"residual_failure_risk":sum(residual)/len(residual) if residual else 0.0,"pairs":len(pairs)}
 pair=[]
 for i,a in enumerate(SURFACES):
  for b in SURFACES[i+1:]: pair.append({"a":a,"b":b,"success_gap":abs(summaries[a]["success_rate"]-summaries[b]["success_rate"]),"risk_gap":abs(summaries[a]["residual_failure_risk"]-summaries[b]["residual_failure_risk"])})
 modes={b for _,b,a in transport}|{a for _,b,a in transport}; non=sum(v for (s,b,a),v in transport.items() if a!=b); dp=next((x for x in pair if x["success_gap"]<=.17 and x["risk_gap"]>=.5),None); pf6=len(modes)>=3 and non>0 and dp is not None
 return {"schema_version":"1.0","experiment":"PF-SHARED-SURFACE-F0","analyzed_at":now(),"task_count":len(tasks),"rows":len(rows),"pf2":{"support_pass":pf2,"heldout_oracle_repair_rate":oracle,"best_fixed_surface_rate":fixed,"ownership_accuracy":ownacc,"distinct_best_surfaces":distinct,"per_surface":per},"pf4":{"support_pass":pf4,"baseline_diagnostic_accuracy":base_diag,"post_update_wrong_surface_accuracy":post,"diagnostic_drop":drops},"pf6":{"support_pass":pf6,"failure_modes":sorted(modes),"non_diagonal_transitions":non,"repair_summaries":summaries,"decision_relevant_pair":dp,"transport":[{"surface":s,"before":b,"after":a,"count":n} for (s,b,a),n in sorted(transport.items())]},"scientific_semantics":"F0/P0-Support only; no METHOD-PASS/FAIL authority."}

def main():
 p=argparse.ArgumentParser();p.add_argument("--data-root",required=True);p.add_argument("--model-path",required=True);p.add_argument("--alfworld-config",required=True);p.add_argument("--output-dir",required=True);p.add_argument("--device",default="cuda");p.add_argument("--resume",action="store_true");a=p.parse_args(); require_local_validation_authority({"PF-2","PF-4","PF-6"}); out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True); traces=out/"raw-traces.jsonl"; progress=out/"progress.json"
 if traces.exists() and not a.resume: raise RuntimeError("nonempty output; use --resume")
 tasks=select_tasks(Path(a.data_root),6)
 if len(tasks)<6:raise RuntimeError(f"need 6 competent open-action tasks, got {len(tasks)}")
 runner=ALFWorldGameRunner(load_config(Path(a.alfworld_config)));policy=HFAdmissiblePolicy(Path(a.model_path),device=a.device,policy_mode="react-family");done=set()
 if traces.exists():
  for line in traces.read_text().splitlines():
   if line.strip():r=json.loads(line);done.add((r["task_id"],r["fault"],r["repair"]))
 plan=[(t,f,r) for t in tasks for f in FAULTS for r in ("none",)+SURFACES]; start=time.time();c=len(done)
 for t,f,r in plan:
  if (t,f,r) in done:continue
  row=run_one(runner,"eval_in_distribution",t,policy,f,r);append(traces,row);c+=1;atomic(progress,{"schema_version":"1.0","status":"running","completed":c,"total":len(plan),"elapsed_hours":(time.time()-start)/3600,"tasks":tasks,"updated_at":now()})
 rows=[json.loads(x) for x in traces.read_text().splitlines() if x.strip()];ana=analyze(rows,tasks);atomic(out/"analysis.json",ana);atomic(progress,{"schema_version":"1.0","status":"complete","completed":len(plan),"total":len(plan),"elapsed_hours":(time.time()-start)/3600,"tasks":tasks,"updated_at":now()});res={"schema_version":"1.0","status":"complete","analysis":ana,"usage":policy.usage_snapshot(),"completed_at":now()};atomic(out/"result.json",res);print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
