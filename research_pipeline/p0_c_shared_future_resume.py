from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any
from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_c_shared_core import append_jsonl, check_gpu_free, hidden_assignment, write_json

def _rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def _local_task(task: str) -> str:
    marker='/json_2.1.1/'; root=str(os.environ.get('ALFWORLD_DATA') or '').rstrip('/')
    return root+marker+task.split(marker,1)[1] if root and marker in task else task

def run_part(plan_path:Path, source_shard:int, part_index:int, num_parts:int, model_path:Path, alfworld_config:Path, shard_dir:Path)->dict[str,Any]:
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    shard=next(row for row in plan['shards'] if int(row['shard'])==int(source_shard))
    candidates=_rows(shard_dir/'correction-candidates.jsonl')[:int(shard['c5_candidate_target'])]
    if len(candidates)!=int(shard['c5_candidate_target']):
        raise RuntimeError(f"source shard {source_shard} requires {shard['c5_candidate_target']} frozen C-5 candidates; got {len(candidates)}")
    future=_rows(shard_dir/'future-runs.jsonl')
    probe_base={r['task']:int((r.get('trace') or {}).get('success',0)) for r in future if r.get('role')=='probe-baseline'}
    hidden_base={r['task']:int((r.get('trace') or {}).get('success',0)) for r in future if r.get('role')=='hidden-baseline'}
    if len(probe_base)!=len(plan['probe_tasks']) or len(hidden_base)!=len(plan['hidden_tasks']):
        raise RuntimeError(f"baseline table incomplete for shard {source_shard}: probes={len(probe_base)}/{len(plan['probe_tasks'])}, hidden={len(hidden_base)}/{len(plan['hidden_tasks'])}")
    selected=[c for idx,c in enumerate(candidates) if idx%int(num_parts)==int(part_index)]
    out=shard_dir/f'future-extra-part-{part_index}-of-{num_parts}.jsonl'
    existing=_rows(out)
    main_done={(r.get('candidate_id'),r.get('role'),r.get('task')) for r in future if r.get('role') in {'candidate-probe','candidate-hidden'}}
    all_extra=[]
    for prior in sorted(shard_dir.glob('future-extra-part-*.jsonl')):
        all_extra+=_rows(prior)
    extra_done={(r.get('candidate_id'),r.get('role'),r.get('task')) for r in all_extra if r.get('role') in {'candidate-probe','candidate-hidden'}}
    done=main_done|extra_done
    gpu=check_gpu_free(); cfg=load_config(alfworld_config); cfg.setdefault('general',{})['save_path']=str(shard_dir/f'future-extra-runtime-{part_index}-of-{num_parts}')
    policy=HFAdmissiblePolicy(model_path,policy_mode='react-family'); runner=ALFWorldGameRunner(cfg); started=time.time()
    selected_ids={c['candidate_id'] for c in selected}
    inherited=sum(1 for cid,role,task in done if cid in selected_ids)
    completed=inherited; total=len(selected)*(len(plan['probe_tasks'])+int(plan['contracts']['C-5']['hidden_per_candidate']))
    for c in selected:
        cid=c['candidate_id']; patch=c['patch']
        for task in plan['probe_tasks']:
            key=(cid,'candidate-probe',task)
            if key in done: continue
            tr=runner.run_game_file('eval_in_distribution',_local_task(task),policy,patch,max_steps=int(plan['max_steps']))
            append_jsonl(out,{'role':'candidate-probe','resume_part':f'{part_index}/{num_parts}','candidate_id':cid,'task':task,'baseline_success':probe_base[task],'trace':tr})
            done.add(key); completed+=1
            write_json(shard_dir/f'future-extra-progress-{part_index}-of-{num_parts}.json',{'source_shard':source_shard,'part_index':part_index,'num_parts':num_parts,'completed_pairs':completed,'total_pairs':total,'usage':policy.usage_snapshot()})
        for task in hidden_assignment(cid,list(plan['hidden_tasks']),int(plan['contracts']['C-5']['hidden_per_candidate']),int(plan['seed'])):
            key=(cid,'candidate-hidden',task)
            if key in done: continue
            tr=runner.run_game_file('eval_out_of_distribution',_local_task(task),policy,patch,max_steps=int(plan['max_steps']))
            append_jsonl(out,{'role':'candidate-hidden','resume_part':f'{part_index}/{num_parts}','candidate_id':cid,'task':task,'baseline_success':hidden_base[task],'trace':tr})
            done.add(key); completed+=1
            write_json(shard_dir/f'future-extra-progress-{part_index}-of-{num_parts}.json',{'source_shard':source_shard,'part_index':part_index,'num_parts':num_parts,'completed_pairs':completed,'total_pairs':total,'usage':policy.usage_snapshot()})
    result={'schema_version':'1.0','status':'complete','source_shard':source_shard,'part_index':part_index,'num_parts':num_parts,'candidate_ids':[c['candidate_id'] for c in selected],'inherited_main_pairs':inherited,'completed_pairs':completed,'total_pairs':total,'usage':policy.usage_snapshot(),'elapsed_hours':(time.time()-started)/3600.0,'gpu_preflight':gpu,'scientific_role':'resume-only C-5 future evaluation over frozen candidates/baselines; no source or label changes'}
    write_json(shard_dir/f'future-extra-complete-{part_index}-of-{num_parts}.json',result); return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--plan',type=Path,required=True); p.add_argument('--source-shard',type=int,required=True); p.add_argument('--part-index',type=int,required=True); p.add_argument('--num-parts',type=int,required=True); p.add_argument('--model-path',type=Path,required=True); p.add_argument('--alfworld-config',type=Path,required=True); p.add_argument('--shard-dir',type=Path,required=True)
    a=p.parse_args(); print(json.dumps(run_part(a.plan,a.source_shard,a.part_index,a.num_parts,a.model_path,a.alfworld_config,a.shard_dir),ensure_ascii=False,indent=2))
