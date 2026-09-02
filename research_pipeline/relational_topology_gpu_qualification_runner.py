from __future__ import annotations

import hashlib, json, os, pickle, random, re, resource, sys, time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

OBJECT_ID = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
RUN_ID = OBJECT_ID + "-gpu-training-qualification-repair-v11"
DATASET_REVISION = "c8cf0bd282699d56a7940ac588ea5e961b1260cb"
CLIP_REVISION = "3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
CORPUS_SHA = {
    "SGP-12": "9884b2afd58e05ed0eb80864154765e55551e5f77632d4fbd6308d0af50dd58b",
    "SGP-14": "51e9e6011250970c660d91c75843919f55192b800423d8ad59a2cfb5c08c4b05",
}
ELIGIBLE_SHA = "40da5528402087f97bcd5d704d914a3d4eca65a083b66fffca6be92fd452ea89"
COMPONENTS = ("BEDROOM-SG2SC-SHARED", "SGP-12", "SGP-14")
SEED, BATCH, STEPS, INTERRUPT = 20260901, 4, 100, 50
AUTHORITY = "GPU_TRAINING_QUALIFICATION_AUTHORITY_GRANTED"

class QualificationError(RuntimeError): pass

def cbytes(x: Any) -> bytes:
    return (json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

def jsha(x: Any) -> str: return hashlib.sha256(cbytes(x)).hexdigest()

def fsha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8<<20), b""): h.update(b)
    return h.hexdigest()

def norm(x: Any) -> Any:
    if isinstance(x, torch.Tensor):
        y=x.detach().cpu().contiguous(); raw=y.reshape(1).view(torch.uint8).numpy().tobytes() if y.dim()==0 else y.view(torch.uint8).numpy().tobytes()
        return {"tensor":[str(y.dtype),list(y.shape),hashlib.sha256(raw).hexdigest()]}
    if isinstance(x,np.ndarray):
        y=np.ascontiguousarray(x); return {"ndarray":[str(y.dtype),list(y.shape),hashlib.sha256(y.tobytes()).hexdigest()]}
    if isinstance(x,dict): return {str(k):norm(v) for k,v in sorted(x.items(),key=lambda kv:str(kv[0]))}
    if isinstance(x,(list,tuple)): return [norm(v) for v in x]
    if isinstance(x,(str,int,float,bool)) or x is None: return x
    return repr(x)

def ssha(x: Any) -> str: return jsha(norm(x))
def model_sha(m: torch.nn.Module) -> str: return ssha(m.state_dict())

def max_model_diff(a,b)->float:
    if set(a)!=set(b): return float("inf")
    out=0.0
    for k in a:
        x,y=a[k].detach().cpu(),b[k].detach().cpu()
        if x.shape!=y.shape or x.dtype!=y.dtype: return float("inf")
        if x.numel()==0: continue
        if x.is_floating_point() or x.is_complex(): out=max(out,float((x-y).abs().max()))
        elif not torch.equal(x,y): return float("inf")
    return out

def slot(example_id:str)->int:
    m=re.search(r"-S(\d{2})-IS-SUPPORT-(?:12|14)$",example_id)
    if not m: raise QualificationError("bad example id: "+example_id)
    return int(m.group(1))

def row_key(r): return f"{r['source_scene_id']}|S{slot(r['example_id']):02d}"

def load_jsonl(p:Path):
    with p.open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def rows_sha(rows): return hashlib.sha256(b"".join(cbytes(r) for r in rows)).hexdigest()

def frozen_order(keys):
    x=sorted(keys); random.Random(SEED).shuffle(x); return x

def set_det():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
    torch.use_deterministic_algorithms(False); torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True; torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    if hasattr(torch,"set_float32_matmul_precision"): torch.set_float32_matmul_precision("highest")

def rng_get():
    return {"python":random.getstate(),"numpy":np.random.get_state(),"torch":torch.get_rng_state(),"cuda":torch.cuda.get_rng_state_all()}

def rng_set(s):
    random.setstate(s["python"]); np.random.set_state(s["numpy"]); torch.set_rng_state(s["torch"]); torch.cuda.set_rng_state_all(s["cuda"])

def rss(): return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024

def move(batch,dev): return {k:(v if isinstance(v,list) else v.to(dev)) for k,v in batch.items()}

def grads_finite(model): return all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())

def unwrap(ds):
    seen=set(); cur=ds
    while id(cur) not in seen:
        seen.add(id(cur))
        if hasattr(cur,"_tags"): return cur
        if not hasattr(cur,"_dataset"): break
        cur=cur._dataset
    raise QualificationError("official cached dataset not found")

def tag_index(ds): return {str(tag):i for i,tag in enumerate(unwrap(ds)._tags)}

def official_config(root:Path, component:str, bedroom:Path):
    fn="bedroom_sg2sc_diffusion_objfeat.yaml" if component=="BEDROOM-SG2SC-SHARED" else "bedroom_sg_diffusion_vq_objfeat.yaml"
    cfg=yaml.safe_load((root/"configs"/fn).read_text()); d=cfg["data"]
    d["dataset_directory"]=str(bedroom); d["annotation_file"]=str(root/"configs/bedroom_threed_front_splits.csv")
    d["path_to_invalid_scene_ids"]=str(root/"configs/invalid_threed_front_rooms.txt")
    d["path_to_invalid_bbox_jids"]=str(root/"configs/black_list.txt")
    d["path_to_floor_plan_textures"]=str(root/"configs/floor_plan_texture_images")
    d["path_to_pickled_3d_futute_models"]=str(bedroom.parent/"threed_future_model_bedroom.pkl")
    cfg["training"].update({"batch_size":BATCH,"splits":["train"],"epochs":1,"steps_per_epoch":STEPS})
    cfg["validation"]["frequency"]=10**9
    return cfg

def make_dataset(root:Path,cfg):
    if str(root) not in sys.path: sys.path.insert(0,str(root))
    from src.data import get_encoded_dataset,filter_function
    return get_encoded_dataset(cfg["data"],filter_function(cfg["data"],split=["train"]),None,cfg["data"].get("augmentations"),split=["train"])

def make_model(root:Path,component:str,cfg,ds,dev,clip:Path,fvq:Path,bounds:Path):
    if str(root) not in sys.path: sys.path.insert(0,str(root))
    from diffusers.training_utils import EMAModel
    from src.models import ObjectFeatureVQVAE,model_from_config,optimizer_from_config
    text=vq=None
    if component.startswith("SGP-"):
        from transformers import CLIPTokenizerFast,CLIPTextModelWithProjection
        tok=CLIPTokenizerFast.from_pretrained(str(clip),local_files_only=True)
        if tok.model_max_length!=77: raise QualificationError("CLIP max length drift")
        enc=CLIPTextModelWithProjection.from_pretrained(str(clip),local_files_only=True).to(dev).eval()
        for p in enc.parameters(): p.requires_grad_(False)
        text=(tok,enc); model=model_from_config(cfg["model"],ds.n_object_types,ds.n_predicate_types,text_emb_dim=enc.config.hidden_size).to(dev)
    else:
        with bounds.open("rb") as f: kw=pickle.load(f)
        vq=ObjectFeatureVQVAE("openshape_vitg14","gumbel",**kw)
        vq.load_state_dict(torch.load(fvq,map_location="cpu")["model"]); vq=vq.to(dev).eval()
        for p in vq.parameters(): p.requires_grad_(False)
        model=model_from_config(cfg["model"],ds.n_object_types,ds.n_predicate_types,**kw).to(dev)
    opt=optimizer_from_config(cfg["training"]["optimizer"],filter(lambda p:p.requires_grad,model.parameters()))
    e=cfg["training"]["ema"]; ema=EMAModel(model.parameters(),decay=e["max_decay"],min_decay=e["min_decay"],update_after_step=e["update_after_step"],use_ema_warmup=e["use_warmup"],inv_gamma=e["inv_gamma"],power=e["power"]); ema.to(dev)
    return model,opt,ema,text,vq

def encode(text,prompts,dev):
    tok,enc=text; z=tok(prompts,padding="max_length",max_length=77,truncation=False,return_tensors="pt")
    if z.input_ids.shape[1]>77: raise QualificationError("prompt exceeds CLIP 77")
    with torch.no_grad():
        o=enc(z.input_ids.to(dev)); h=o.last_hidden_state.float(); e=o.text_embeds.float(); e=e/e.norm(dim=-1,keepdim=True)
    return h,e

def prepare_data(component,ds,eligible,rows):
    idx=tag_index(ds)
    if component=="BEDROOM-SG2SC-SHARED":
        missing=set(eligible)-set(idx)
        if missing: raise QualificationError("eligible scene absent: "+next(iter(missing)))
        return {"ds":ds,"idx":idx,"order":frozen_order(eligible),"rows":None}
    by={row_key(r):r for r in rows}
    if len(by)!=len(rows): raise QualificationError("duplicate corpus row key")
    missing={r["source_scene_id"] for r in rows}-set(idx)
    if missing: raise QualificationError("corpus scene absent: "+next(iter(missing)))
    return {"ds":ds,"idx":idx,"order":frozen_order(by),"rows":by}

def get_batch(data,cursor):
    keys=[data["order"][(cursor+j)%len(data["order"])] for j in range(BATCH)]; samples=[]; prompts=None
    if data["rows"] is None:
        for k in keys: samples.append(data["ds"][data["idx"][k]])
    else:
        prompts=[]
        for k in keys:
            r=data["rows"][k]; samples.append(data["ds"][data["idx"][r["source_scene_id"]]]); prompts.append(r["exact_instruction"])
    return data["ds"].collate_fn(samples),keys,prompts

def total_loss(losses,weights,dev):
    out=torch.zeros(1,device=dev)
    for k,v in losses.items(): out=out+float(weights.get(k,1.0))*v
    return out

def ckpt_payload(component,model,opt,ema,step,cursor,order,consumed,losses,corpus_sha,config_sha):
    return {"run_id":RUN_ID,"component_id":component,"step":step,"model":model.state_dict(),"optimizer":opt.state_dict(),"ema":ema.state_dict(),"scheduler":{"kind":"OFFICIAL_NO_SCHEDULER_NOOP_STATE"},"rng":rng_get(),"sampler":{"order":order,"cursor":cursor,"seed":SEED},"consumed":consumed,"losses":losses,"corpus_sha256":corpus_sha,"config_sha256":config_sha}

def save_ckpt(path:Path,payload):
    t=time.perf_counter(); torch.save(payload,path); sec=time.perf_counter()-t
    man={"run_id":RUN_ID,"component_id":payload["component_id"],"step":payload["step"],"model_state_sha256":ssha(payload["model"]),"optimizer_state_sha256":ssha(payload["optimizer"]),"scheduler_state_sha256":ssha(payload["scheduler"]),"rng_state_sha256":ssha(payload["rng"]),"sampler_state_sha256":ssha(payload["sampler"]),"sampler_position":payload["sampler"]["cursor"],"corpus_cursor":payload["sampler"]["cursor"],"corpus_sha256":payload["corpus_sha256"],"config_sha256":payload["config_sha256"],"code_sha":"BOUND_BY_RUN_MANIFEST","checkpoint_sha256":fsha(path),"checkpoint_bytes":path.stat().st_size,"checkpoint_write_seconds":sec}
    return man

def restore(p,model,opt,ema):
    model.load_state_dict(p["model"]); opt.load_state_dict(p["optimizer"]); ema.load_state_dict(p["ema"]); ema.to(next(model.parameters()).device)
    if p["scheduler"]!={"kind":"OFFICIAL_NO_SCHEDULER_NOOP_STATE"}: raise QualificationError("scheduler state drift")
    rng_set(p["rng"]); return int(p["step"]),int(p["sampler"]["cursor"]),list(p["consumed"]),[float(x) for x in p["losses"]]

def train_segment(component,model,opt,ema,text,vq,data,cfg,dev,start,end,cursor,consumed,history,ckdir,prefix,corpus_sha,config_sha,events,losslog,cklog):
    times=[]; maxrss=rss(); ckstats=[]; weights=cfg["training"]["loss_weights"]; model.train(); torch.cuda.reset_peak_memory_stats(dev)
    for step in range(start+1,end+1):
        tic=time.perf_counter()
        try: batch,keys,prompts=get_batch(data,cursor)
        except Exception as e: raise QualificationError(f"dataloader failure step {step}: {e}") from e
        batch=move(batch,dev); opt.zero_grad(set_to_none=True)
        if component.startswith("SGP-"):
            h,e=encode(text,prompts,dev); losses=model.compute_losses(batch,h,e)
        else: losses=model.compute_losses(batch,vqvae_model=vq)
        loss=total_loss(losses,weights,dev)
        if not torch.isfinite(loss).all(): raise QualificationError(f"nonfinite loss step {step}")
        loss.backward()
        if not grads_finite(model): raise QualificationError(f"nonfinite grad step {step}")
        opt.step(); ema.step(model.parameters()); torch.cuda.synchronize(dev)
        dt=time.perf_counter()-tic; val=float(loss.detach().cpu()); times.append(dt); history.append(val); consumed.extend(keys); cursor+=BATCH; maxrss=max(maxrss,rss())
        events.write(cbytes({"event":"optimizer_step_committed","component_id":component,"step":step,"cursor":cursor,"batch_keys_sha256":jsha(keys),"elapsed_seconds":dt}).decode()); events.flush()
        losslog.write(cbytes({"component_id":component,"step":step,"loss":val,"finite":True,"sub_losses":{k:float(v.detach().cpu()) for k,v in losses.items()}}).decode()); losslog.flush()
        if step in {INTERRUPT,STEPS}:
            p=ckdir/f"{prefix}-step-{step:03d}.pt"; man=save_ckpt(p,ckpt_payload(component,model,opt,ema,step,cursor,data["order"],consumed,history,corpus_sha,config_sha)); ckstats.append(man)
            z=torch.load(p,map_location="cpu");
            if z["step"]!=step or z["component_id"]!=component: raise QualificationError("checkpoint readability failure")
            cklog.write(cbytes(man).decode()); cklog.flush()
    sec=sum(times); return cursor,consumed,history,times,{"steps":end-start,"samples":BATCH*(end-start),"mean_step_seconds":sec/len(times),"samples_per_second":BATCH*(end-start)/sec,"peak_allocated_vram":int(torch.cuda.max_memory_allocated(dev)),"peak_reserved_vram":int(torch.cuda.max_memory_reserved(dev)),"peak_cpu_rss":maxrss,"checkpoint_stats":ckstats}

def compare_ckpts(a:Path,b:Path):
    x=torch.load(a,map_location="cpu"); y=torch.load(b,map_location="cpu")
    md=max_model_diff(x["model"],y["model"]); lx=x["losses"]; ly=y["losses"]
    ld=max((abs(float(p)-float(q)) for p,q in zip(lx,ly)),default=0.0) if len(lx)==len(ly) else float("inf")
    out={"consumed_example_key_sequence_identical":x["consumed"]==y["consumed"],"sampler_state_identical":x["sampler"]==y["sampler"],"optimizer_state_identical":ssha(x["optimizer"])==ssha(y["optimizer"]),"model_state_hash_identical":ssha(x["model"])==ssha(y["model"]),"model_tensor_max_abs_diff":md,"loss_trajectory_max_abs_diff":ld,"tolerance":1e-7}
    out["status"]="PASS" if out["consumed_example_key_sequence_identical"] and out["sampler_state_identical"] and out["optimizer_state_identical"] and md<=1e-7 and ld<=1e-7 else "FAIL"
    return out

def validate_corpora(cdir:Path):
    a=load_jsonl(cdir/"IS-SUPPORT-12.jsonl"); b=load_jsonl(cdir/"IS-SUPPORT-14.jsonl"); sa,sb=rows_sha(a),rows_sha(b)
    if sa!=CORPUS_SHA["SGP-12"] or sb!=CORPUS_SHA["SGP-14"]: raise QualificationError(f"corpus hash drift {sa} {sb}")
    if {row_key(r) for r in a}!={row_key(r) for r in b}: raise QualificationError("common structural key mismatch")
    scenes=[x.strip() for x in (cdir/"eligible_scenes.txt").read_text().splitlines() if x.strip()]
    if jsha(scenes)!=ELIGIBLE_SHA: raise QualificationError("eligible scene hash drift")
    return {"SGP-12":a,"SGP-14":b},scenes

def env_snapshot(dev):
    p=torch.cuda.get_device_properties(dev)
    try: driver=Path("/proc/driver/nvidia/version").read_text().split("Kernel Module")[1].split()[0]
    except Exception: driver=None
    return {"GPU_model":p.name,"GPU_total_memory":int(p.total_memory),"CUDA":torch.version.cuda,"driver":driver,"PyTorch":torch.__version__,"precision":"FP32_FIXED_SEED_TF32_DISABLED_FRAMEWORK_DETERMINISM_OFF_WITH_EXACT_RESUME_GATE","batch_size":BATCH,"gradient_accumulation":1,"CUBLAS_WORKSPACE_CONFIG":os.environ.get("CUBLAS_WORKSPACE_CONFIG")}

def write_rate(runtime):
    s=runtime["checkpoint_stats"]; n=sum(x["checkpoint_bytes"] for x in s); t=sum(x["checkpoint_write_seconds"] for x in s); return n/t if t else 0.0

def run_component(component:str,run_root:Path,instructscene:Path,bedroom:Path,corpus_dir:Path,clip:Path,fvq:Path,bounds:Path,device_index:int=0):
    if component not in COMPONENTS: raise QualificationError("unknown component")
    if not torch.cuda.is_available(): raise QualificationError("CUDA unavailable")
    dev=torch.device(f"cuda:{device_index}"); set_det(); corpora,eligible=validate_corpora(corpus_dir); rows=corpora.get(component)
    csha=ELIGIBLE_SHA if component=="BEDROOM-SG2SC-SHARED" else CORPUS_SHA[component]
    cfg=official_config(instructscene,component,bedroom); cfgsha=jsha(cfg); ds=make_dataset(instructscene,cfg); data=prepare_data(component,ds,eligible,rows)
    out=run_root/component
    if out.exists(): raise QualificationError("exactly-once component path exists: "+str(out))
    (out/"checkpoints").mkdir(parents=True); (out/"config.yaml").write_text(yaml.safe_dump(cfg,sort_keys=True)); (out/"STATUS").write_text("RUNNING\n")
    model,opt,ema,text,vq=make_model(instructscene,component,cfg,ds,dev,clip,fvq,bounds); initsha=model_sha(model); torch.cuda.empty_cache()
    with (out/"training_events.jsonl").open("w") as ev,(out/"loss.jsonl").open("w") as lo,(out/"checkpoint_manifest.jsonl").open("w") as cm:
        cursor,consumed,hist,times,base=train_segment(component,model,opt,ema,text,vq,data,cfg,dev,0,STEPS,0,[],[],out/"checkpoints","baseline",csha,cfgsha,ev,lo,cm)
        p50=out/"checkpoints"/"baseline-step-050.pt"; p100=out/"checkpoints"/"baseline-step-100.pt"
        set_det(); rm,ro,re,rt,rv=make_model(instructscene,component,cfg,ds,dev,clip,fvq,bounds)
        if model_sha(rm)!=initsha: raise QualificationError("initial model hash drift")
        z=torch.load(p50,map_location="cpu"); st,rc,co,hi=restore(z,rm,ro,re)
        _,_,_,rtimes,res=train_segment(component,rm,ro,re,rt,rv,data,cfg,dev,st,STEPS,rc,co,hi,out/"checkpoints","resumed",csha,cfgsha,ev,lo,cm)
    pr=out/"checkpoints"/"resumed-step-100.pt"; resume=compare_ckpts(p100,pr); exact=len(consumed)==BATCH*STEPS and len(consumed)==len(set(consumed)); finite=all(np.isfinite(hist)); passed=resume["status"]=="PASS" and exact and finite
    result={"object_id":OBJECT_ID,"run_id":RUN_ID,"component_id":component,"classification":"NON_SCIENTIFIC_OFFICIAL_TRAINING_RESOURCE_AND_REPLAY_QUALIFICATION","authority_receipt_normalized":AUTHORITY,"status":"PASS" if passed else "FAIL","logical_optimizer_steps":STEPS,"replayed_optimizer_steps_for_resume_test":STEPS-INTERRUPT,"scientific_outcome":False,"outcomes_enter_p1":False,"corpus_sha256":csha,"config_sha256":cfgsha,"environment":env_snapshot(dev),"runtime":{"baseline":base,"resume_suffix":res,"peak_allocated_VRAM":max(base["peak_allocated_vram"],res["peak_allocated_vram"]),"peak_reserved_VRAM":max(base["peak_reserved_vram"],res["peak_reserved_vram"]),"CPU_RAM":max(base["peak_cpu_rss"],res["peak_cpu_rss"]),"step_time":sum(times)/len(times),"samples_per_second":base["samples_per_second"],"checkpoint_size":p100.stat().st_size,"disk_write_rate":write_rate(base)},"gates":{"loss_finite":finite,"grad_finite":True,"OOM":False,"NaN_Inf":not finite,"dataloader_failures":0,"exactly_once_no_duplicates_or_gaps":exact,"resume_stability":resume},"consumed_example_sequence_sha256":jsha(consumed),"initial_model_state_sha256":initsha,"baseline_final_model_state_sha256":ssha(torch.load(p100,map_location="cpu")["model"]),"resumed_final_model_state_sha256":ssha(torch.load(pr,map_location="cpu")["model"])}
    (out/"component_summary.json").write_bytes(cbytes(result)); (out/"STATUS").write_text(("PASS" if passed else "FAIL")+"\n")
    if not passed: raise QualificationError("component failed: "+component)
    return result
