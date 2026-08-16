from __future__ import annotations

import argparse, hashlib, json, math
from collections import Counter
from pathlib import Path
from typing import Any, Callable

CONDITIONS=("none","prompt","workflow","tool"); FAULTS=("prompt","workflow","tool"); CATS=("open","take","move","examine","look","use_or_transform","other")
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def cat(a:str)->str:
 t=str(a or "").strip().lower()
 if t.startswith("open "):return "open"
 if t.startswith("take "):return "take"
 if t.startswith(("move ","put ")):return "move"
 if t.startswith("examine "):return "examine"
 if t=="look" or t.startswith("look "):return "look"
 if t.startswith(("use ","clean ","cool ","heat ")):return "use_or_transform"
 return "other"
def repeats(a:list[str])->int:return sum(x.strip().lower()==y.strip().lower() for x,y in zip(a,a[1:]))
def generic(r:dict[str,Any])->list[float]:
 a=list(r.get("executed_actions") or []);n=max(1,len(a));c=Counter(cat(x) for x in a)
 return [len(a)/50,int(r.get("invalid_actions") or 0)/n,repeats(a)/max(1,len(a)-1),c["open"]/n,c["take"]/n,c["move"]/n,c["examine"]/n,c["look"]/n,c["use_or_transform"]/n]
def complete(r:dict[str,Any])->list[float]:return generic(r)[:3]
def sequence(r:dict[str,Any])->list[float]:
 a=[cat(x) for x in r.get("executed_actions") or []];pairs=Counter(zip(a,a[1:]));d=max(1,len(a)-1);return generic(r)+[pairs[(x,y)]/d for x in CATS for y in CATS]
def dist(a:list[float],b:list[float])->float:return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def centers(rows:list[dict[str,Any]],fn:Callable)->dict[str,list[float]]:
 out={}
 for f in FAULTS:
  z=[fn(r) for r in rows if r["fault"]==f]
  if z:out[f]=[sum(v)/len(v) for v in zip(*z)]
 return out
def loso(rows:list[dict[str,Any]],fn:Callable,tasks:list[str],eligible:set[tuple[str,str]])->list[dict[str,Any]]:
 out=[]
 for held in tasks:
  cen=centers([r for r in rows if r["task_id"]!=held and (r["task_id"],r["fault"]) in eligible],fn)
  if set(cen)!=set(FAULTS):raise ValueError("LOSO fold lacks fault center")
  for r in rows:
   if r["task_id"]==held and (r["task_id"],r["fault"]) in eligible:
    v=fn(r);p=min(FAULTS,key=lambda f:(dist(v,cen[f]),f));out.append({"task_id":held,"fault":r["fault"],"prediction":p,"correct":p==r["fault"]})
 return out
def accuracy(p:list[dict[str,Any]])->float:return sum(bool(x["correct"]) for x in p)/max(1,len(p))
def load_phase(root:Path,phase:str)->list[dict[str,Any]]:
 rows=[]
 for c in CONDITIONS:
  p=root/f"{phase}-{c}.jsonl"
  if not p.is_file():raise FileNotFoundError(p)
  rows.extend(json.loads(x) for x in p.read_text().splitlines() if x.strip())
 return rows

def qualification(rows:list[dict[str,Any]])->dict[str,Any]:
 tasks=sorted({r["task_id"] for r in rows});by={(r["condition"],r["task_id"]):r for r in rows}
 if len(rows)!=len(CONDITIONS)*len(tasks):raise ValueError("incomplete qualification")
 st={}
 for c in CONDITIONS:
  z=[by[c,t] for t in tasks];trans=sum(max(0,r["steps"]-1) for r in z);rep=sum(r["immediate_repeat_count"] for r in z)
  st[c]={"success_rate":sum(r["success"] for r in z)/len(z),"success_vector":[r["success"] for r in z],"repeat_count":rep,"repeat_violation_rate":rep/max(1,trans),"update_intervention_count":sum(r.get("update_intervention_count",0) for r in z),"mean_steps":sum(r["steps"] for r in z)/len(z)}
 ups=("prompt","workflow","tool");rates=[st[c]["success_rate"] for c in ups];ident=sum(len({st[c]["success_vector"][i] for c in ups})==1 for i in range(len(tasks)))
 checks={"repair_contract_compliance":all(st[c]["repeat_violation_rate"]<=.05 for c in ups),"behavioral_activity":st["none"]["repeat_count"]>=1 and st["workflow"]["update_intervention_count"]>=1 and st["tool"]["update_intervention_count"]>=1 and st["prompt"]["repeat_count"]<=st["none"]["repeat_count"]-1,"utility_equivalence":max(rates)-min(rates)<=1/6+1e-12 and ident>=5,"baseline_noninferiority":all(st[c]["success_rate"]>=st["none"]["success_rate"]-1/6-1e-12 for c in ups),"identical_success_tasks":ident}
 ok=all(v is True or k=="identical_success_tasks" for k,v in checks.items());return {"status":"PASS" if ok else "INCONCLUSIVE_FUNCTIONAL_EQUIVALENCE_QUALIFICATION_FAILED","passed":ok,"tasks":tasks,"stats":st,"checks":checks,"scientific_authority":False}

def diagnostic(rows:list[dict[str,Any]],q:dict[str,Any])->dict[str,Any]:
 if not q["passed"]:return {"status":q["status"],"scientific_authority":False}
 tasks=list(q["tasks"]);by={c:[r for r in rows if r["condition"]==c] for c in CONDITIONS};eligible={(r["task_id"],r["fault"]) for r in by["none"] if r.get("fault_intervention_count",0)>=1};fc=Counter(f for _,f in eligible)
 if len(eligible)<12 or any(fc[f]<3 for f in FAULTS):return {"status":"INCONCLUSIVE_FAULT_SUPPORT","eligible_probes":len(eligible),"eligible_by_fault":dict(fc),"scientific_authority":False}
 metrics={};fns={"completeness":complete,"generic_composition":generic,"sequence":sequence}
 for c in ("prompt","workflow","tool"):
  metrics[c]={}
  for name,fn in fns.items():
   p=loso(by[c],fn,tasks,eligible);metrics[c][name]={"accuracy":accuracy(p),"correct":sum(x["correct"] for x in p),"predictions":p}
  metrics[c]["sequence_minus_generic"]=metrics[c]["sequence"]["accuracy"]-metrics[c]["generic_composition"]["accuracy"]
 seq={c:metrics[c]["sequence"]["accuracy"] for c in metrics};adv={c:metrics[c]["sequence_minus_generic"] for c in metrics};best=max(seq,key=lambda c:(seq[c],c));worst=min(seq,key=lambda c:(seq[c],c));sr=max(seq.values())-min(seq.values());rr=max(adv.values())-min(adv.values());cg=metrics[best]["sequence"]["correct"]-metrics[worst]["sequence"]["correct"]
 jack=[]
 for deleted in tasks:
  kt=[t for t in tasks if t!=deleted];ke={(t,f) for t,f in eligible if t!=deleted};vals={}
  for c in (best,worst):vals[c]=accuracy(loso(by[c],sequence,kt,ke))
  jack.append({"deleted_task":deleted,"best_accuracy":vals[best],"worst_accuracy":vals[worst],"gap":vals[best]-vals[worst]})
 jp=all(x["gap"]>0 for x in jack) and sum(x["gap"]>=.10 for x in jack)>=5;survive=sr>=.20 and rr>=.15 and cg>=3 and jp
 return {"status":"RESIDUAL_SURVIVES" if survive else "REDUCTION_SUPPORTED","eligible_probes":len(eligible),"eligible_by_fault":dict(fc),"metrics":metrics,"sequence_accuracy_range":sr,"sequence_minus_generic_range":rr,"best_realization":best,"worst_realization":worst,"correct_probe_gap":cg,"jackknife":jack,"jackknife_pass":jp,"scientific_authority":False}

def analyze(contract:Path,root:Path,out:Path)->dict[str,Any]:
 c=json.loads(contract.read_text());q=qualification(load_phase(root,"qualification"))
 if not q["passed"]:r={"schema_version":"1.0","experiment_id":c["experiment_id"],"outcome":q["status"],"qualification":q,"scientific_result_available":False,"protocol_valid":True,"scientific_authority":False}
 else:
  d=diagnostic(load_phase(root,"faults"),q);r={"schema_version":"1.0","experiment_id":c["experiment_id"],"outcome":d["status"],"qualification":q,"diagnostic":d,"scientific_result_available":d["status"] in {"RESIDUAL_SURVIVES","REDUCTION_SUPPORTED"},"protocol_valid":True,"scientific_authority":False}
 r["contract_sha256"]=sha(contract);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n");return r

def main():
 p=argparse.ArgumentParser();p.add_argument("--contract",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();print(json.dumps(analyze(a.contract,a.output_dir,a.output),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
