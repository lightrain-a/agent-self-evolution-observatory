from __future__ import annotations

import argparse, hashlib, json, os, time
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import extract_task_goal, task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config

CONDITIONS=("none","prompt","workflow","tool")
FAULTS=("prompt","workflow","tool")
PROMPT_REPAIR=("Persistent repair: Never execute the exact same admissible command in two consecutive steps when any different admissible command exists. If your first choice would repeat the previous command, choose a different admissible command that still advances the task.")
PROMPT_FAULT="Fault injection: Never use an `open` action. Prefer looking or examining instead, even if a receptacle may be closed."

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def repeats(actions:list[str])->int:return sum(a.strip().lower()==b.strip().lower() for a,b in zip(actions,actions[1:]))
def different(commands:list[str],previous:str)->str|None:
 p=previous.strip().lower();return next((c for c in commands if c.strip().lower()!=p),None)
def nonprogress(commands:list[str])->str|None:
 if not commands:return None
 return next((c for c in commands if c.lower() in {"look","inventory"} or c.lower().startswith("examine ")),commands[0])

def validate_model(contract:dict[str,Any],model:Path)->None:
 s=contract.get("substrate") or {}
 for name,key in (("config.json","model_config_sha256"),("model.safetensors.index.json","model_index_sha256"),("tokenizer_config.json","tokenizer_config_sha256")):
  p=model/name
  if not p.is_file() or sha(p)!=str(s.get(key) or ""):raise ValueError(f"model contract mismatch:{name}")

def resolve_tasks(contract:dict[str,Any],data:Path)->list[str]:
 base=data/"json_2.1.1"/"valid_seen";tasks=[str(base/r) for r in (contract.get("substrate") or {}).get("task_relative_paths") or []]
 missing=[p for p in tasks if not Path(p).is_file()]
 if missing:raise FileNotFoundError(f"missing frozen task:{missing[:2]}")
 return tasks

def episode(env,policy:HFAdmissiblePolicy,*,condition:str,fault:str,max_steps:int)->dict[str,Any]:
 obs,info=env.reset();hist=[];executed=[];selected=[];observations=[str(obs[0])];raws=[];env_cmds=[];visible_cmds=[];uflags=[];fflags=[];invalid=0
 gamefile=str((info.get("extra.gamefile") or [""])[0]);goal=extract_task_goal(str(obs[0]));family=task_family_from_gamefile(gamefile);done=False;won=False;score=0.0
 while not done and len(executed)<max_steps:
  commands=list((info.get("admissible_commands") or [[]])[0])
  if not commands:break
  env_cmds.append(list(commands));visible=list(commands);prev=executed[-1] if executed else "";uf=False;ff=False
  if condition=="tool" and prev and len(visible)>1:
   f=[c for c in visible if c.strip().lower()!=prev.strip().lower()]
   if f and len(f)<len(visible):visible=f;uf=True
  if fault=="tool":
   f=[c for c in visible if not c.lower().startswith("open ")]
   if f and len(f)<len(visible):visible=f;ff=True
  patches=[]
  if condition=="prompt":patches.append(PROMPT_REPAIR)
  if fault=="prompt":patches.append(PROMPT_FAULT);ff=True
  action,bad,raw=policy.choose(str(obs[0]),visible,hist,"\n".join(patches),goal_context=goal,task_family=family);invalid+=int(bad);selected.append(action)
  if condition=="workflow" and prev and action.strip().lower()==prev.strip().lower():
   alt=different(visible,prev)
   if alt is not None:action=alt;uf=True
  if fault=="workflow" and len(executed)>=2 and action.lower().startswith(("take ","move ","put ","use ","clean ","cool ","heat ")):
   alt=nonprogress(visible)
   if alt is not None:action=alt;ff=True
  if action not in commands:raise RuntimeError(f"non-admissible executed action:{action}")
  visible_cmds.append(list(visible));executed.append(action);raws.append(raw);uflags.append(bool(uf or condition=="prompt"));fflags.append(bool(ff))
  obs,scores,dones,info=env.step([action]);score=float(scores[0]);done=bool(dones[0]);won=bool((info.get("won") or [False])[0]);observations.append(str(obs[0]));hist.append((action,str(obs[0])))
 return {"task_id":gamefile,"condition":condition,"fault":fault,"success":int(won),"score":score,"steps":len(executed),"invalid_actions":invalid,"immediate_repeat_count":repeats(executed),"environment_admissible_commands":env_cmds,"visible_admissible_commands":visible_cmds,"raw_model_choices":raws,"selected_actions_before_workflow_update":selected,"executed_actions":executed,"observations":observations,"update_intervention_flags":uflags,"update_intervention_count":sum(uflags) if condition!="prompt" else 0,"prompt_update_active":condition=="prompt","fault_intervention_flags":fflags,"fault_intervention_count":sum(fflags),"terminated":done,"step_cap":max_steps}

def run_condition(contract_path:Path,*,condition:str,phase:str,config_path:Path,model_path:Path,alfworld_data:Path,output_dir:Path,device:str="cuda")->dict[str,Any]:
 if condition not in CONDITIONS or phase not in {"qualification","faults"}:raise ValueError("invalid condition/phase")
 contract=json.loads(contract_path.read_text());validate_model(contract,model_path);tasks=resolve_tasks(contract,alfworld_data);max_steps=int((contract.get("substrate") or {}).get("max_steps") or 50)
 os.environ["ALFWORLD_DATA"]=str(alfworld_data);config=load_config(config_path);policy=HFAdmissiblePolicy(model_path,device=device,policy_mode=str((contract.get("substrate") or {}).get("policy_mode") or "react-family"));runner=ALFWorldGameRunner(config);faults=("none",) if phase=="qualification" else FAULTS;rows=[];started=time.time()
 for task in tasks:
  for fault in faults:
   env=runner.build_env("eval_in_distribution",[task])
   try:r=episode(env,policy,condition=condition,fault=fault,max_steps=max_steps)
   finally:
    close=getattr(env,"close",None)
    if callable(close):close()
   r["task_id"]=task;rows.append(r)
 output_dir.mkdir(parents=True,exist_ok=True);path=output_dir/f"{phase}-{condition}.jsonl";path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
 state={"schema_version":"1.0","experiment_id":contract.get("experiment_id"),"condition":condition,"phase":phase,"rows":len(rows),"raw_sha256":sha(path),"contract_sha256":sha(contract_path),"model_snapshot":(contract.get("substrate") or {}).get("model_snapshot"),"usage":policy.usage_snapshot(),"elapsed_seconds":time.time()-started,"scientific_authority":False}
 (output_dir/f"{phase}-{condition}-manifest.json").write_text(json.dumps(state,indent=2)+"\n");return state

def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--contract",type=Path,required=True);p.add_argument("--condition",choices=CONDITIONS,required=True);p.add_argument("--phase",choices=("qualification","faults"),required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--model",type=Path,required=True);p.add_argument("--alfworld-data",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--device",default="cuda");a=p.parse_args();print(json.dumps(run_condition(a.contract,condition=a.condition,phase=a.phase,config_path=a.config,model_path=a.model,alfworld_data=a.alfworld_data,output_dir=a.output_dir,device=a.device),indent=2))
if __name__=="__main__":main()
