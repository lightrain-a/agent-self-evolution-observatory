from __future__ import annotations
import hashlib,json,time
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any
from .p0_alfworld_adapter import ALFWorldGameRunner,HFAdmissiblePolicy,load_config,task_family_from_gamefile

ARMS=("no-memory","memory-a","memory-b","memory-a-plus-b")
def _sha(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def _jl(p:Path):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def _atom(p:Path,x:dict):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def _append(p:Path,x:dict):
 with p.open('a',encoding='utf-8') as h:h.write(json.dumps(x,ensure_ascii=False)+'\n')
def _rel(x:str)->str:return x.split('/valid_unseen/',1)[-1] if '/valid_unseen/' in x else x
def _scenario(x:str)->str:return _rel(x).split('/trial_',1)[0]

def build_plan(mem_path:Path,config_path:Path,exclude_plan:Path|None=None)->dict[str,Any]:
 mem=_jl(mem_path); by=defaultdict(list)
 for x in mem:by[str(x['source_family'])].append(x)
 pairs=[]
 for fam,rows in sorted(by.items()):
  for a,b in combinations(sorted(rows,key=lambda z:str(z['memory_id'])),2):pairs.append((fam,a,b))
 pairs.sort(key=lambda z:_sha('PAIR|'+z[0]+'|'+str(z[1]['memory_id'])+'|'+str(z[2]['memory_id'])))
 runner=ALFWorldGameRunner(load_config(config_path));games=runner.available_game_files('eval_out_of_distribution')
 source={_scenario(str(x['source_task_id'])) for x in mem};prior=set()
 if exclude_plan and exclude_plan.exists():
  old=json.loads(exclude_plan.read_text(encoding='utf-8'));prior={_scenario(str(x['target_task_id'])) for x in old.get('units',[])}
 used=set();out=[]
 for i,(fam,a,b) in enumerate(pairs[:6],1):
  pool=[g for g in games if task_family_from_gamefile(g)==fam and _scenario(g) not in source and _scenario(g) not in prior and _scenario(g) not in used]
  pool.sort(key=lambda g:_sha(f"TARGET|{a['memory_id']}|{b['memory_id']}|{_rel(g)}"))
  if not pool:raise RuntimeError('no target '+fam)
  target=pool[0];used.add(_scenario(target))
  out.append({'pair_id':f'b3-p{i:02d}','family':fam,'memory_a':a['memory_id'],'memory_b':b['memory_id'],'target_task_id':target})
 plan={'experiment_id':'P0-B3-REAL-COINTERACTION','selection_rule':'SHA256 within-family pair/target selection; excludes source scenarios and all prior full-support target scenarios; no outcomes read','pairs':out,'arms':list(ARMS),'gate':{'strict_coharm_pairs_required':2,'negative_residual_pairs_required':2}}
 plan['plan_hash']=_sha(json.dumps(plan,sort_keys=True,separators=(',',':')));return plan

def analyze(records:list[dict],plan:dict)->dict:
 g=defaultdict(dict)
 for r in records:g[r['pair_id']][r['arm']]=int(r['success'])
 rows=[]
 for p in plan['pairs']:
  a=g[p['pair_id']]
  if set(a)!=set(ARMS):continue
  u0,ua,ub,uab=[a[x] for x in ARMS];res=uab-ua-ub+u0
  strict=ua>=u0 and ub>=u0 and uab<min(ua,ub)
  rows.append({**p,'no_memory':u0,'memory_a_success':ua,'memory_b_success':ub,'combined_success':uab,'interaction_residual':res,'strict_coharm':strict})
 strict=sum(x['strict_coharm'] for x in rows);neg=sum(x['interaction_residual']<0 for x in rows);gate=plan['gate']
 passed=len(rows)==6 and strict>=gate['strict_coharm_pairs_required'] and neg>=gate['negative_residual_pairs_required']
 return {'pairs_complete':len(rows),'strict_coharm_pairs':strict,'negative_interaction_residual_pairs':neg,'pair_rows':rows,'gate':gate,'phenomenon_pass':passed,'decision':'REAL_COINTERACTION_PHENOMENON_PASS' if passed else 'STOP_REAL_COINTERACTION_PREVALENCE_INSUFFICIENT','method_failure_authorized':False,'next_action':'Open pathway-localization audit only after human review.' if passed else 'Merge B-3 into ordinary per-item/co-occurrence memory selection.'}

def run(run_dir:Path,mem_path:Path,config_path:Path,model_path:Path,exclude_plan:Path|None=None,max_steps:int=50)->dict:
 if run_dir.exists() and any(run_dir.iterdir()):raise RuntimeError('refuse overwrite '+str(run_dir))
 run_dir.mkdir(parents=True,exist_ok=True);plan=build_plan(mem_path,config_path,exclude_plan);_atom(run_dir/'plan.json',plan)
 mem={str(x['memory_id']):x for x in _jl(mem_path)};raw=run_dir/'raw-traces.jsonl';raw.write_text('',encoding='utf-8')
 _atom(run_dir/'manifest.json',{'plan_hash':plan['plan_hash'],'model_path':str(model_path),'python_abi':'3.12','episode_cap':24,'method_failure_authorized':False})
 runner=ALFWorldGameRunner(load_config(config_path));policy=HFAdmissiblePolicy(model_path,policy_mode='react-family');records=[];started=time.monotonic()
 for p in plan['pairs']:
  a=str(mem[p['memory_a']]['text']);b=str(mem[p['memory_b']]['text'])
  ctx={'no-memory':'','memory-a':'MEMORY::'+a,'memory-b':'MEMORY::'+b,'memory-a-plus-b':'MEMORY::'+a+'\n\nSECOND RETRIEVED EXPERIENCE:\n'+b}
  for arm in ARMS:
   if len(records)>=24 or (time.monotonic()-started)>3600:raise RuntimeError('BUDGET_STOP')
   before=policy.usage_snapshot();tr=runner.run_game_file('eval_out_of_distribution',p['target_task_id'],policy,ctx[arm],max_steps=max_steps);after=policy.usage_snapshot()
   r={**p,'arm':arm,'success':int(tr.get('success') or 0),'steps':int(tr.get('steps') or 0),'invalid_actions':int(tr.get('invalid_actions') or 0),'usage_calls':after['generation_calls']-before['generation_calls'],'usage_tokens':after['tokens']-before['tokens']};records.append(r);_append(raw,r)
   _atom(run_dir/'progress.json',{'status':'running','completed_executions':len(records),'total_executions':24,'completed_pairs':len(records)//4,'total_pairs':6,'model_calls':after['generation_calls']})
 result=analyze(records,plan);_atom(run_dir/'analysis.json',result);_atom(run_dir/'decision.json',result);_atom(run_dir/'progress.json',{'status':'complete','completed_executions':24,'total_executions':24,'completed_pairs':6,'total_pairs':6,'model_calls':policy.usage_snapshot()['generation_calls'],'elapsed_hours':(time.monotonic()-started)/3600});return result

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--run-dir',type=Path,required=True);ap.add_argument('--mem-path',type=Path,required=True);ap.add_argument('--config-path',type=Path,required=True);ap.add_argument('--model-path',type=Path,required=True);ap.add_argument('--exclude-plan',type=Path);a=ap.parse_args()
 print(json.dumps(run(a.run_dir,a.mem_path,a.config_path,a.model_path,a.exclude_plan),ensure_ascii=False,indent=2))
