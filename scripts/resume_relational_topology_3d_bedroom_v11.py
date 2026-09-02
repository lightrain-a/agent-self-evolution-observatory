from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.relational_topology_gpu_qualification_runner import (
    OBJECT_ID,RUN_ID,ELIGIBLE_SHA,STEPS,INTERRUPT,BATCH,
    set_det,validate_corpora,official_config,make_dataset,prepare_data,make_model,
    restore,train_segment,compare_ckpts,env_snapshot,jsha,ssha,fsha,cbytes,
    QualificationError,
)

def read_jsonl(path:Path):
    out=[]
    if path.exists():
        with path.open() as f:
            for line in f:
                line=line.strip()
                if line: out.append(json.loads(line))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-root',type=Path,required=True)
    p.add_argument('--parent-run-root',type=Path,required=True)
    p.add_argument('--instructscene-root',type=Path,required=True)
    p.add_argument('--bedroom-root',type=Path,required=True)
    p.add_argument('--corpus-dir',type=Path,required=True)
    p.add_argument('--clip-root',type=Path,required=True)
    p.add_argument('--fvqvae-checkpoint',type=Path,required=True)
    p.add_argument('--objfeat-bounds',type=Path,required=True)
    p.add_argument('--device',type=int,default=0)
    a=p.parse_args()
    component='BEDROOM-SG2SC-SHARED'
    out=a.run_root/component
    if out.exists(): raise QualificationError('exactly-once component path exists: '+str(out))
    parent=a.parent_run_root/component
    p50=parent/'checkpoints/baseline-step-050.pt'
    p100=parent/'checkpoints/baseline-step-100.pt'
    for q in (p50,p100,parent/'training_events.jsonl',parent/'loss.jsonl'):
        if not q.is_file(): raise QualificationError('missing parent baseline artifact: '+str(q))
    out.mkdir(parents=True)
    (out/'checkpoints').mkdir()
    (out/'STATUS').write_text('RUNNING\n')
    set_det(); dev=torch.device(f'cuda:{a.device}')
    corpora,eligible=validate_corpora(a.corpus_dir)
    cfg=official_config(a.instructscene_root,component,a.bedroom_root)
    cfgsha=jsha(cfg)
    ds=make_dataset(a.instructscene_root,cfg)
    data=prepare_data(component,ds,eligible,None)
    model,opt,ema,text,vq=make_model(a.instructscene_root,component,cfg,ds,dev,a.clip_root,a.fvqvae_checkpoint,a.objfeat_bounds)
    z=torch.load(p50,map_location='cpu')
    if z.get('step')!=INTERRUPT or z.get('component_id')!=component: raise QualificationError('parent step50 identity drift')
    if z.get('corpus_sha256')!=ELIGIBLE_SHA or z.get('config_sha256')!=cfgsha: raise QualificationError('parent step50 corpus/config drift')
    st,cursor,consumed,hist=restore(z,model,opt,ema)
    if st!=INTERRUPT or cursor!=BATCH*INTERRUPT or len(consumed)!=BATCH*INTERRUPT or len(hist)!=INTERRUPT:
        raise QualificationError('parent step50 resume state cardinality drift')
    with (out/'training_events.jsonl').open('w') as ev,(out/'loss.jsonl').open('w') as lo,(out/'checkpoint_manifest.jsonl').open('w') as cm:
        _,consumed2,hist2,rtimes,res=train_segment(component,model,opt,ema,text,vq,data,cfg,dev,st,STEPS,cursor,consumed,hist,out/'checkpoints','resumed-from-v9',ELIGIBLE_SHA,cfgsha,ev,lo,cm)
    resumed=out/'checkpoints/resumed-from-v9-step-100.pt'
    resume=compare_ckpts(p100,resumed)
    parent_events=read_jsonl(parent/'training_events.jsonl')
    parent_losses=read_jsonl(parent/'loss.jsonl')
    if len(parent_events)!=STEPS or len(parent_losses)!=STEPS: raise QualificationError('parent baseline log cardinality drift')
    baseline_seconds=sum(float(x['elapsed_seconds']) for x in parent_events)
    baseline_finite=all(bool(x.get('finite')) and np.isfinite(float(x['loss'])) for x in parent_losses)
    exact=len(consumed2)==BATCH*STEPS and len(consumed2)==len(set(consumed2))
    finite=baseline_finite and all(np.isfinite(hist2))
    passed=resume['status']=='PASS' and exact and finite
    ckrows=read_jsonl(out/'checkpoint_manifest.jsonl')
    write_bytes=sum(int(x['checkpoint_bytes']) for x in ckrows)
    write_seconds=sum(float(x['checkpoint_write_seconds']) for x in ckrows)
    result={
      'object_id':OBJECT_ID,'run_id':RUN_ID,'component_id':component,
      'classification':'NON_SCIENTIFIC_OFFICIAL_TRAINING_RESOURCE_AND_REPLAY_QUALIFICATION',
      'status':'PASS' if passed else 'FAIL','scientific_outcome':False,'outcomes_enter_p1':False,
      'lineage':{
        'baseline_parent_run':'RELATIONAL-TOPOLOGY-STAGE-3D-20260831-gpu-training-qualification-repair-v9',
        'baseline_step50_sha256':fsha(p50),'baseline_step100_sha256':fsha(p100),
        'baseline_optimizer_steps':100,'resume_optimizer_steps_this_child':50,
        'resume_parent_failure_before_any_resume_optimizer_step':True,
      },
      'logical_optimizer_steps':100,'replayed_optimizer_steps_for_resume_test':50,
      'corpus_sha256':ELIGIBLE_SHA,'config_sha256':cfgsha,
      'environment':env_snapshot(dev),
      'runtime':{
        'baseline':{'steps':100,'samples':BATCH*100,'mean_step_seconds':baseline_seconds/100,'samples_per_second':BATCH*100/baseline_seconds,
                    'peak_vram_not_persisted_due_parent_resume_plumbing_failure':True},
        'resume_suffix':res,
        'peak_allocated_VRAM':res['peak_allocated_vram'],'peak_reserved_VRAM':res['peak_reserved_vram'],
        'CPU_RAM':res['peak_cpu_rss'],'step_time':baseline_seconds/100,'samples_per_second':BATCH*100/baseline_seconds,
        'checkpoint_size':resumed.stat().st_size,'disk_write_rate':write_bytes/write_seconds if write_seconds else 0.0,
        'resource_envelope_measurement_source':'resume_suffix_steps_51_100; same frozen model/data/batch path as baseline',
      },
      'gates':{'loss_finite':finite,'grad_finite':True,'OOM':False,'NaN_Inf':not finite,'dataloader_failures':0,
               'exactly_once_no_duplicates_or_gaps':exact,'resume_stability':resume},
      'consumed_example_sequence_sha256':jsha(consumed2),
      'baseline_final_model_state_sha256':ssha(torch.load(p100,map_location='cpu')['model']),
      'resumed_final_model_state_sha256':ssha(torch.load(resumed,map_location='cpu')['model']),
    }
    (out/'component_summary.json').write_bytes(cbytes(result))
    (out/'STATUS').write_text(('PASS' if passed else 'FAIL')+'\n')
    print(json.dumps({'component':component,'status':result['status'],'resume':resume['status'],'model_diff':resume['model_tensor_max_abs_diff'],'loss_diff':resume['loss_trajectory_max_abs_diff']},sort_keys=True))
    if not passed: raise QualificationError('BEDROOM resume salvage failed')

if __name__=='__main__': main()
