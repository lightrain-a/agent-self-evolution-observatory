from __future__ import annotations

import json, os, time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from research_pipeline.relational_topology_official_training_dev_v14a import (
    OBJECT_ID, COMPONENTS, SEED, BATCH, STEPS, CKPT_EVERY, EXPECTED_INIT,
    TrainingGateError, append, atom, build_config, claim_key, env, file_sha,
    get_batch, init_component, jsha, load, loss_for, make_dataset, move,
    prepare, rng_get, rng_set, set_rng, ssha, verify_assets, verify_authority,
    grads_finite,
)


def save_checkpoint(*,root:Path,component:str,model,opt,ema,step:int,cursor:int,order:list[str],content_sha:str,cfg_sha:str,code_sha:str,segment_id:str):
    payload={"object_id":OBJECT_ID,"component_id":component,"global_step":step,"model":model.state_dict(),"optimizer":opt.state_dict(),"ema":ema.state_dict(),"scheduler":{"kind":"OFFICIAL_NO_SCHEDULER_NOOP_STATE"},"rng":rng_get(),"sampler":{"order":order,"order_sha256":jsha(order),"cursor":cursor,"seed":SEED},"content_sha256":content_sha,"config_sha256":cfg_sha,"code_sha":code_sha,"segment_id":segment_id}
    tmp=root/f".step-{step:07d}.{os.getpid()}.tmp.pt"; start=time.perf_counter(); torch.save(payload,tmp); seconds=time.perf_counter()-start; digest=file_sha(tmp)
    final=root/f"step-{step:07d}-{digest[:16]}.pt"
    if final.exists(): raise TrainingGateError("completed checkpoint already exists")
    os.replace(tmp,final); check=torch.load(final,map_location="cpu")
    if check.get("global_step")!=step or check.get("component_id")!=component: raise TrainingGateError("checkpoint readback failed")
    return {"component_id":component,"global_step":step,"segment_id":segment_id,"checkpoint_path":str(final),"checkpoint_sha256":digest,"checkpoint_bytes":final.stat().st_size,"checkpoint_write_seconds":seconds,"model_state_sha256":ssha(payload["model"]),"optimizer_state_sha256":ssha(payload["optimizer"]),"ema_state_sha256":ssha(payload["ema"]),"rng_state_sha256":ssha(payload["rng"]),"sampler_state_sha256":ssha(payload["sampler"]),"sampler_cursor":cursor,"content_sha256":content_sha,"config_sha256":cfg_sha,"code_sha":code_sha}


def restore_checkpoint(path:Path,*,component:str,model,opt,ema,content_sha:str,cfg_sha:str,code_sha:str):
    p=torch.load(path,map_location="cpu")
    if p.get("object_id")!=OBJECT_ID or p.get("component_id")!=component: raise TrainingGateError("resume identity drift")
    if p.get("content_sha256")!=content_sha or p.get("config_sha256")!=cfg_sha or p.get("code_sha")!=code_sha: raise TrainingGateError("resume content/config/code drift")
    if p.get("scheduler")!={"kind":"OFFICIAL_NO_SCHEDULER_NOOP_STATE"}: raise TrainingGateError("resume scheduler drift")
    model.load_state_dict(p["model"]); opt.load_state_dict(p["optimizer"]); ema.load_state_dict(p["ema"]); ema.to(next(model.parameters()).device); rng_set(p["rng"])
    sampler=p["sampler"]
    if sampler.get("order_sha256")!=jsha(sampler.get("order")): raise TrainingGateError("resume sampler order drift")
    return int(p["global_step"]),int(sampler["cursor"]),list(sampler["order"])


def train(*,component:str,run_root:Path,authority:Path,proposal:Path,source:Path,bedroom:Path,split:Path,corpus_dir:Path,clip:Path,fvq:Path,bounds:Path,code_sha:str,device_index:int=0,resume:Path|None=None):
    verify_authority(authority,proposal); verify_assets(source,clip,fvq,bounds)
    if component not in COMPONENTS or not torch.cuda.is_available(): raise TrainingGateError("component/CUDA invalid")
    root=run_root/component; claim_path=root/"claim.json"; preflight_path=root/"resource_preflight.json"
    if not claim_path.is_file() or not preflight_path.is_file(): raise TrainingGateError("resource preflight must exist before training")
    claim,pre=load(claim_path),load(preflight_path)
    if claim.get("state")!="RESOURCE_PREFLIGHT_PASS" or pre.get("state")!="RESOURCE_PREFLIGHT_PASS": raise TrainingGateError("resource preflight not passed")
    if claim.get("resource_preflight_sha256")!=file_sha(preflight_path): raise TrainingGateError("preflight content address drift")
    set_rng(); device=torch.device(f"cuda:{device_index}"); cfg=build_config(source,component,bedroom); cfg_sha=jsha(cfg); ds=make_dataset(source,cfg); data=prepare(component,ds,split,corpus_dir)
    if claim.get("claim_key")!=claim_key(component,data["sha"],cfg_sha): raise TrainingGateError("exactly-once claim drift")
    if pre.get("content_sha256")!=data["sha"] or pre.get("config_sha256")!=cfg_sha: raise TrainingGateError("preflight config/content drift")
    model,opt,ema,text,vq,init,_=init_component(source,component,cfg,ds,device,clip,fvq,bounds)
    if component.startswith("SGP-") and init!=EXPECTED_INIT: raise TrainingGateError("SGP init drift")
    ckdir=root/"checkpoints"; segroot=root/"segments"; ckdir.mkdir(exist_ok=True); segroot.mkdir(exist_ok=True)
    existing=sorted(p for p in segroot.iterdir() if p.is_dir() and p.name.startswith("segment-")); seg=f"segment-{len(existing)+1:04d}"; segdir=segroot/seg; segdir.mkdir(exist_ok=False)
    start,cursor,order=0,0,data["order"]
    if resume is not None:
        start,cursor,restored=restore_checkpoint(resume,component=component,model=model,opt=opt,ema=ema,content_sha=data["sha"],cfg_sha=cfg_sha,code_sha=code_sha)
        if restored!=order: raise TrainingGateError("resume order differs from frozen order")
    elif existing: raise TrainingGateError("existing segment requires explicit resume; silent restart forbidden")
    if start>=STEPS: raise TrainingGateError("checkpoint already at fixed endpoint")
    events,losses,fail=segdir/"training_events.jsonl",segdir/"loss.jsonl",segdir/"failures.jsonl"; ckmanifest=root/"checkpoint_manifest.jsonl"; segmanifest=root/"segment_manifest.jsonl"; heartbeat=root/"heartbeat.json"
    claim.update(state="TRAINING_RUNNING",current_segment_id=seg,training_code_sha=code_sha,optimizer_steps_committed=start); atom(claim_path,claim)
    append(segmanifest,{"segment_id":seg,"state":"STARTED","start_step":start,"resume_checkpoint":str(resume) if resume else None,"resume_checkpoint_sha256":file_sha(resume) if resume else None,"scientific_outcomes":0})
    model.train()
    with torch.cuda.device(device):
        torch.cuda.reset_peak_memory_stats()
    wall=time.perf_counter(); last=None
    try:
        for step in range(start+1,STEPS+1):
            tic=time.perf_counter(); batch,keys,prompts=get_batch(data,cursor); batch=move(batch,device); opt.zero_grad(set_to_none=True); sub,total=loss_for(component,model,batch,prompts,text,vq,cfg,device)
            if not bool(torch.isfinite(total).all()): raise TrainingGateError(f"nonfinite loss step {step}")
            total.backward()
            if not grads_finite(model): raise TrainingGateError(f"nonfinite grad step {step}")
            opt.step(); ema.step(model.parameters()); torch.cuda.synchronize(device); cursor+=BATCH; dt=time.perf_counter()-tic
            append(events,{"segment_id":seg,"event":"optimizer_step_committed","global_step":step,"cursor":cursor,"batch_keys_sha256":jsha(keys),"elapsed_seconds":dt})
            append(losses,{"segment_id":seg,"global_step":step,"loss":float(total.detach().cpu()),"finite":True,"sub_losses":{k:float(v.detach().cpu()) for k,v in sub.items()}})
            atom(heartbeat,{"object_id":OBJECT_ID,"component_id":component,"segment_id":seg,"state":"TRAINING_RUNNING","global_step":step,"cursor":cursor,"last_update_unix":time.time(),"scientific_outcomes":0})
            if step%CKPT_EVERY==0 or step==STEPS:
                last=save_checkpoint(root=ckdir,component=component,model=model,opt=opt,ema=ema,step=step,cursor=cursor,order=order,content_sha=data["sha"],cfg_sha=cfg_sha,code_sha=code_sha,segment_id=seg); append(ckmanifest,last)
                claim.update(state="CHECKPOINT_COMMITTED",optimizer_steps_committed=step,latest_checkpoint_sha256=last["checkpoint_sha256"],latest_checkpoint_path=last["checkpoint_path"]); atom(claim_path,claim)
        if not last or last["global_step"]!=STEPS: raise TrainingGateError("final checkpoint missing")
        final={"object_id":OBJECT_ID,"component_id":component,"state":"TRAINING_COMPLETE","classification":"DEVELOPMENTAL_OFFICIAL_TRAINING_NO_SCIENTIFIC_OUTCOME_ADMISSION","training_seed":SEED,"batch_size":BATCH,"logical_optimizer_steps":STEPS,"final_checkpoint_path":last["checkpoint_path"],"final_checkpoint_sha256":last["checkpoint_sha256"],"final_checkpoint_step":STEPS,"final_ema_state_sha256":last["ema_state_sha256"],"content_sha256":data["sha"],"config_sha256":cfg_sha,"initial_model_state_sha256":init,"training_code_sha":code_sha,"environment":env(device),"peak_allocated_vram":int(torch.cuda.max_memory_allocated(device)),"peak_reserved_vram":int(torch.cuda.max_memory_reserved(device)),"wall_seconds_this_segment":time.perf_counter()-wall,"validation_outputs_generated":0,"test_outputs_generated":0,"scientific_outcomes":0,"outcomes_enter_p1":False}
        atom(root/"final_training_summary.json",final); append(segmanifest,{"segment_id":seg,"state":"COMPLETED","start_step":start,"end_step":STEPS,"final_checkpoint_sha256":last["checkpoint_sha256"],"scientific_outcomes":0}); claim.update(state="TRAINING_COMPLETE",optimizer_steps_committed=STEPS); atom(claim_path,claim); atom(heartbeat,{"object_id":OBJECT_ID,"component_id":component,"segment_id":seg,"state":"TRAINING_COMPLETE","global_step":STEPS,"last_update_unix":time.time(),"scientific_outcomes":0}); return final
    except Exception as exc:
        append(fail,{"object_id":OBJECT_ID,"component_id":component,"segment_id":seg,"state":"FAIL_CLOSED","error_type":type(exc).__name__,"error":str(exc),"scientific_outcomes":0}); claim["state"]="FAIL_CLOSED"; atom(claim_path,claim); raise
