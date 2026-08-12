from __future__ import annotations
import fcntl, json, time
from pathlib import Path
from typing import Any
from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_c_shared_core import append_jsonl, check_gpu_free, hidden_assignment, ordered_pair, replan_patch, self_label_lineages, write_json

STREAMS=('source-traces.jsonl','correction-candidates.jsonl','mode-runs.jsonl','self-labels.jsonl','future-runs.jsonl')

def _prepare(output_dir:Path)->None:
    output_dir.mkdir(parents=True,exist_ok=True)
    for name in STREAMS:
        p=output_dir/name
        if p.exists() and p.stat().st_size:
            raise RuntimeError(f'refusing to overwrite non-empty shard artifact: {p}')
        p.write_text('',encoding='utf-8')

def _collect_sources(plan:dict[str,Any],shard:dict[str,Any],runner:ALFWorldGameRunner,policy:HFAdmissiblePolicy,output_dir:Path):
    si=int(shard['shard']); seed=int(plan['seed'])+10000*si; max_steps=int(plan['max_steps']); target=int(shard['failure_target'])
    failures=[]; candidates=[]; memory_bank={}
    modes={k:0 for k in ('rewrite','replan','retrieve','rollback','stop','rewrite-replan','replan-rewrite')}
    for source_idx,game_file in enumerate(shard['source_pool']):
        baseline=runner.run_game_file('eval_in_distribution',game_file,policy,max_steps=max_steps)
        append_jsonl(output_dir/'source-traces.jsonl',{'role':'source-baseline','source_index':source_idx,'trace':baseline})
        if baseline.get('success'): continue
        failures.append(baseline); cid=f'c{si}-{len(failures)-1:03d}'
        rewrite=policy.propose_patch(baseline,seed=seed+100+len(failures),variant=len(failures)); replan=replan_patch(baseline)
        family=str(baseline.get('task_family') or task_family_from_gamefile(game_file))
        cand={'candidate_id':cid,'shard':si,'source_task':game_file,'task_family':family,'patch':rewrite,'replan_patch':replan,'source_steps':int(baseline.get('steps',0)),'source_invalid_rate':float(baseline.get('invalid_choice_rate',0.0)),'patch_words':len(rewrite.split())}
        wr=runner.run_game_file('eval_in_distribution',game_file,policy,rewrite,max_steps=max_steps)
        rp=runner.run_game_file('eval_in_distribution',game_file,policy,replan,max_steps=max_steps)
        cand.update({'source_before_success':0,'rewrite_success':int(wr.get('success',0)),'replan_success':int(rp.get('success',0))})
        append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'rewrite','trace':wr}); modes['rewrite']+=1
        append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'replan','trace':rp}); modes['replan']+=1
        retrieved=(memory_bank.get(family) or [])[-1] if memory_bank.get(family) else None
        if retrieved:
            rr=runner.run_game_file('eval_in_distribution',game_file,policy,'MEMORY::'+retrieved,max_steps=max_steps)
            cand['retrieve_success']=int(rr.get('success',0)); append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'retrieve','trace':rr}); modes['retrieve']+=1
        else:
            cand['retrieve_success']=None
        append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'rollback','reused_baseline':True,'success':0}); modes['rollback']+=1
        append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'stop','no_execution':True,'success':0}); modes['stop']+=1
        if len(failures)<=6:
            a=runner.run_game_file('eval_in_distribution',game_file,policy,ordered_pair(rewrite,replan),max_steps=max_steps)
            b=runner.run_game_file('eval_in_distribution',game_file,policy,ordered_pair(replan,rewrite),max_steps=max_steps)
            cand['rewrite_replan_success']=int(a.get('success',0)); cand['replan_rewrite_success']=int(b.get('success',0))
            append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'rewrite-replan','trace':a}); modes['rewrite-replan']+=1
            append_jsonl(output_dir/'mode-runs.jsonl',{'candidate_id':cid,'mode':'replan-rewrite','trace':b}); modes['replan-rewrite']+=1
        else:
            cand['rewrite_replan_success']=None; cand['replan_rewrite_success']=None
        if wr.get('success'):
            memory_bank.setdefault(family,[]).append(rewrite)
        elif rp.get('success'):
            memory_bank.setdefault(family,[]).append(replan)
        labels=self_label_lineages(policy,cand,baseline,wr,seed+5000+len(failures)*20)
        for row in labels:
            append_jsonl(output_dir/'self-labels.jsonl',row)
        cand['self_labels_frozen']=len(labels); candidates.append(cand)
        append_jsonl(output_dir/'correction-candidates.jsonl',cand)
        write_json(output_dir/'progress.json',{'stage':'source','shard':si,'failures':len(failures),'target':target,'usage':policy.usage_snapshot()})
        if len(failures)>=target:
            break
    if len(failures)<target:
        raise RuntimeError(f'shard {si} found only {len(failures)} failures < target {target}')
    return candidates,modes

def _collect_future(plan:dict[str,Any],shard:dict[str,Any],candidates:list[dict[str,Any]],runner:ALFWorldGameRunner,policy:HFAdmissiblePolicy,output_dir:Path)->int:
    max_steps=int(plan['max_steps']); selected=candidates[:int(shard['c5_candidate_target'])]
    probes=list(plan['probe_tasks']); hidden=list(plan['hidden_tasks']); probe_base={}; hidden_base={}
    for task in probes:
        tr=runner.run_game_file('eval_in_distribution',task,policy,max_steps=max_steps); probe_base[task]=tr
        append_jsonl(output_dir/'future-runs.jsonl',{'role':'probe-baseline','task':task,'trace':tr})
    for task in hidden:
        tr=runner.run_game_file('eval_out_of_distribution',task,policy,max_steps=max_steps); hidden_base[task]=tr
        append_jsonl(output_dir/'future-runs.jsonl',{'role':'hidden-baseline','task':task,'trace':tr})
    hidden_each=int(plan['contracts']['C-5']['hidden_per_candidate']); seed=int(plan['seed'])
    for idx,cand in enumerate(selected,1):
        cid=cand['candidate_id']; patch=cand['patch']
        for task in probes:
            tr=runner.run_game_file('eval_in_distribution',task,policy,patch,max_steps=max_steps)
            append_jsonl(output_dir/'future-runs.jsonl',{'role':'candidate-probe','candidate_id':cid,'task':task,'baseline_success':int(probe_base[task].get('success',0)),'trace':tr})
        for task in hidden_assignment(cid,hidden,hidden_each,seed):
            tr=runner.run_game_file('eval_out_of_distribution',task,policy,patch,max_steps=max_steps)
            append_jsonl(output_dir/'future-runs.jsonl',{'role':'candidate-hidden','candidate_id':cid,'task':task,'baseline_success':int(hidden_base[task].get('success',0)),'trace':tr})
        write_json(output_dir/'progress.json',{'stage':'future','shard':int(shard['shard']),'candidates_completed':idx,'candidates_total':len(selected),'usage':policy.usage_snapshot()})
    return len(selected)

def collect_shard(plan_path:Path,shard_index:int,model_path:Path,alfworld_config:Path,output_dir:Path)->dict[str,Any]:
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    shard=next(r for r in plan['shards'] if int(r['shard'])==int(shard_index))
    output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'.collect.lock').open('a+') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        complete=output_dir/'complete.json'
        if complete.exists():
            return json.loads(complete.read_text(encoding='utf-8'))
        _prepare(output_dir); gpu=check_gpu_free(); cfg=load_config(alfworld_config)
        cfg.setdefault('general',{})['save_path']=str(output_dir/'alfworld-runtime')
        started=time.time(); policy=HFAdmissiblePolicy(model_path,policy_mode='react-family'); runner=ALFWorldGameRunner(cfg)
        candidates,modes=_collect_sources(plan,shard,runner,policy,output_dir)
        c5_count=_collect_future(plan,shard,candidates,runner,policy,output_dir)
        result={'schema_version':'1.0','status':'complete','shard':int(shard_index),'failures':len(candidates),'candidates':len(candidates),'c5_candidates':c5_count,'self_label_decisions':len(candidates)*10,'mode_counts':modes,'probe_tasks':len(plan['probe_tasks']),'hidden_tasks':len(plan['hidden_tasks']),'usage':policy.usage_snapshot(),'elapsed_hours':(time.time()-started)/3600.0,'gpu_preflight':gpu,'scientific_role':plan['scientific_role']}
        write_json(complete,result); return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--plan',type=Path,required=True); p.add_argument('--shard',type=int,required=True); p.add_argument('--model-path',type=Path,required=True); p.add_argument('--alfworld-config',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args(); print(json.dumps(collect_shard(a.plan,a.shard,a.model_path,a.alfworld_config,a.output_dir),ensure_ascii=False,indent=2))
