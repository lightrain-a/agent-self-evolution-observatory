from __future__ import annotations
import hashlib,json,time,os
from pathlib import Path
from typing import Any
from .p0_alfworld_adapter import ALFWorldGameRunner,HFAdmissiblePolicy,load_config
from .p0_c_shared_core import append_jsonl,check_gpu_free,hidden_assignment,write_json

def _rows(path:Path):
    if not path.exists(): return []
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def _local_task(task:str)->str:
    marker='/json_2.1.1/'
    root=str(os.environ.get('ALFWORLD_DATA') or '').rstrip('/')
    return (root+marker+task.split(marker,1)[1]) if root and marker in task else task

def complete_c1_truth(plan_path:Path,root:Path,model_path:Path,alfworld_config:Path)->dict[str,Any]:
    plan=json.loads(plan_path.read_text(encoding='utf-8')); complete=root/'c1-truth-complete.json'; out=root/'c1-future-runs.jsonl'
    if complete.exists(): return json.loads(complete.read_text(encoding='utf-8'))
    if out.exists() and out.stat().st_size: raise RuntimeError('refusing to overwrite partial C1 truth completion')
    candidates=[]; labels=[]; existing=[]; baseline={}
    for shard in sorted(root.glob('shard-*')):
        candidates+=_rows(shard/'correction-candidates.jsonl'); labels+=_rows(shard/'self-labels.jsonl'); existing+=_rows(shard/'future-runs.jsonl')
    if len(candidates)!=40 or len(labels)!=400:
        raise RuntimeError(f'C-1 truth requires frozen 40 candidates + 400 labels before hidden truth opens; got {len(candidates)} candidates / {len(labels)} labels')
    for r in existing:
        if r.get('role')=='hidden-baseline': baseline.setdefault(r['task'],int((r.get('trace') or {}).get('success',0)))
    have={(r.get('candidate_id'),r.get('task')) for r in existing if r.get('role')=='candidate-hidden'}
    todo=[]; seed=int(plan['seed'])
    for c in candidates:
        for task in hidden_assignment(c['candidate_id'],list(plan['hidden_tasks']),2,seed):
            if (c['candidate_id'],task) not in have: todo.append((c,task))
    gpu=check_gpu_free(); cfg=load_config(alfworld_config); cfg.setdefault('general',{})['save_path']=str(root/'c1-truth-alfworld-runtime')
    policy=HFAdmissiblePolicy(model_path,policy_mode='react-family'); runner=ALFWorldGameRunner(cfg); started=time.time()
    out.write_text('',encoding='utf-8')
    for task in plan['hidden_tasks']:
        if task in baseline: continue
        tr=runner.run_game_file('eval_out_of_distribution',_local_task(task),policy,max_steps=int(plan['max_steps']))
        baseline[task]=int(tr.get('success',0)); append_jsonl(out,{'role':'hidden-baseline','truth_completion':'C-1','task':task,'trace':tr})
    for idx,(c,task) in enumerate(todo,1):
        tr=runner.run_game_file('eval_out_of_distribution',_local_task(task),policy,c['patch'],max_steps=int(plan['max_steps']))
        append_jsonl(out,{'role':'candidate-hidden','truth_completion':'C-1','candidate_id':c['candidate_id'],'task':task,'baseline_success':baseline[task],'trace':tr})
        write_json(root/'c1-truth-progress.json',{'completed':idx,'total':len(todo),'usage':policy.usage_snapshot()})
    result={'schema_version':'1.0','status':'complete','candidates_total':len(candidates),'frozen_self_label_decisions':len(labels),'hidden_baselines':len(baseline),'required_hidden_per_candidate':2,'existing_candidate_task_pairs':len(have),'new_candidate_task_pairs':len(todo),'planned_total_candidate_task_pairs':len(candidates)*2,'usage':policy.usage_snapshot(),'elapsed_hours':(time.time()-started)/3600.0,'gpu_preflight':gpu,'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest()}
    write_json(complete,result); return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--plan',type=Path,required=True); p.add_argument('--root',type=Path,required=True); p.add_argument('--model-path',type=Path,required=True); p.add_argument('--alfworld-config',type=Path,required=True)
    a=p.parse_args(); print(json.dumps(complete_c1_truth(a.plan,a.root,a.model_path,a.alfworld_config),ensure_ascii=False,indent=2))
