from __future__ import annotations

import csv, hashlib, json, os, random, subprocess, sys, time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

from research_pipeline.relational_topology_gpu_qualification_runner import (
    cbytes, encode, fsha, grads_finite, jsha, make_dataset, make_model,
    move, rng_get, rng_set, rows_sha, ssha, total_loss, unwrap,
)

OBJECT_ID = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
AUTHORITY_STATE = "OFFICIAL_TRAINING_DEVELOPMENTAL_AUTHORITY_GRANTED_BOUNDED"
AUTHORITY_NORMALIZED = "OFFICIAL_TRAINING_DEVELOPMENTAL_AUTHORITY_GRANTED"
COMPONENTS = ("BEDROOM-SG2SC-SHARED", "SGP-12", "SGP-14")
SEED, BATCH, STEPS, CKPT_EVERY = 20260901, 128, 1_000_000, 50_000
EXPECTED_INIT = "efd8ee84bf36e5ebfc9a191155495d5c540f289e20a117356c4b490a4c2fb3f3"
EXPECTED_PARAMS = 51_156_834
INSTRUCT_SHA = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
SPLIT_SHA = "f8f144f2380668b7db999d1b21b0331ade27b72f7e4892b43da068559ffb6d79"
TRAIN_POOL_SHA, TRAIN_POOL_N = "e1c8be1dad5d02db5aafadaadbbd4f8c69a18aeff100b46938492ffb9f388ce2", 3722
ELIGIBLE_SHA = "40da5528402087f97bcd5d704d914a3d4eca65a083b66fffca6be92fd452ea89"
CORPUS_SHA = {
    "SGP-12": "9884b2afd58e05ed0eb80864154765e55551e5f77632d4fbd6308d0af50dd58b",
    "SGP-14": "51e9e6011250970c660d91c75843919f55192b800423d8ad59a2cfb5c08c4b05",
}
FVQ_SHA = "e1c577fd55681138c7191394db5113cedcb4da5ffab2eac7272d399c33bb9cb4"
BOUNDS_SHA = "e2f290af3fe934443fce03f8d2f34adbffaf7974dcab349d517723205d4d0d30"
EXPECTED_CONFIG_SHA = {
    "BEDROOM-SG2SC-SHARED": "429301d308ee6d99c479cc6d7e4a55dca7661f3bec2c29a128e3586e4ea17b7a",
    "SGP-12": "64ce016dbeb1d3c5cee7174ae05370a5874ae716ed9fe93280b997415b1864d7",
    "SGP-14": "64ce016dbeb1d3c5cee7174ae05370a5874ae716ed9fe93280b997415b1864d7",
}
CLIP_FILES = {
    "config.json": "b575ef3c36f2a057fa19e221650105052d61cc9c1a972ec15019c6261ec98770",
    "merges.txt": "f526393189112391ce6f9795d4695f704121ce452c3aad1f5335cc41337eba85",
    "pytorch_model.bin": "a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f",
    "special_tokens_map.json": "f8c0d6c39aee3f8431078ef6646567b0aba7f2246e9c54b8b99d55c22b707cbf",
    "tokenizer_config.json": "34b7336e4bee12e0a9730eaf5189f582ef3c3eea5027f65730e5717256755aad",
    "tokenizer.json": "b556ac8c99757ffb677208af34bc8c6721572114111a6e0aaf5fa69ff0b8d842",
    "vocab.json": "5047b556ce86ccaf6aa22b3ffccfc52d391ea4accdab9c2f2407da5b742d4363",
}

class TrainingGateError(RuntimeError): pass

def load(path: Path): return json.loads(path.read_text())
def atom(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True); tmp=path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n"); os.replace(tmp,path)
def append(path: Path, obj: Any):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a") as f: f.write(cbytes(obj).decode()); f.flush(); os.fsync(f.fileno())
def file_sha(path: Path): return fsha(path)
def order_sha(values): return jsha(values)
def set_rng():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
    torch.use_deterministic_algorithms(False); torch.backends.cudnn.benchmark=False; torch.backends.cudnn.deterministic=True
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False

def verify_authority(authority: Path, proposal: Path):
    if not authority.is_file(): raise TrainingGateError("official developmental training authority receipt absent")
    a=load(authority); g=a.get("grant") or {}; scope=g.get("scope") or {}
    if a.get("object_id")!=OBJECT_ID or a.get("state")!=AUTHORITY_STATE: raise TrainingGateError("authority identity/state invalid")
    if g.get("normalized_authority")!=AUTHORITY_NORMALIZED: raise TrainingGateError("normalized authority absent")
    if a.get("proposal_sha256")!=file_sha(proposal): raise TrainingGateError("proposal hash mismatch")
    expected={"components":list(COMPONENTS),"training_seed":SEED,"training_seed_count":1,"batch_size":BATCH,
              "gradient_accumulation":1,"logical_optimizer_steps_per_component":STEPS,"checkpoint_every_steps":CKPT_EVERY,
              "validation_during_training":False,"scientific_metrics_during_training":False,"scientific_outcomes":0,"outcomes_enter_p1":False}
    for k,v in expected.items():
        if scope.get(k)!=v: raise TrainingGateError(f"authority scope drift: {k}")
    return a

def verify_assets(source: Path, clip: Path, fvq: Path, bounds: Path):
    head=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
    if head!=INSTRUCT_SHA: raise TrainingGateError("InstructScene source drift")
    if file_sha(fvq)!=FVQ_SHA or file_sha(bounds)!=BOUNDS_SHA: raise TrainingGateError("fVQ asset drift")
    for name,digest in CLIP_FILES.items():
        if not (clip/name).is_file() or file_sha(clip/name)!=digest: raise TrainingGateError(f"CLIP drift: {name}")

def build_config(source: Path, component: str, bedroom: Path):
    name="bedroom_sg2sc_diffusion_objfeat.yaml" if component=="BEDROOM-SG2SC-SHARED" else "bedroom_sg_diffusion_vq_objfeat.yaml"
    cfg=yaml.safe_load((source/"configs"/name).read_text()); d=cfg["data"]
    d.update(dataset_directory=str(bedroom),annotation_file=str(source/"configs/bedroom_threed_front_splits.csv"),
             path_to_invalid_scene_ids=str(source/"configs/invalid_threed_front_rooms.txt"),path_to_invalid_bbox_jids=str(source/"configs/black_list.txt"),
             path_to_floor_plan_textures=str(source/"configs/floor_plan_texture_images"),path_to_pickled_3d_futute_models=str(bedroom.parent/"threed_future_model_bedroom.pkl"))
    cfg["training"].update(splits=["train"],epochs=2000,steps_per_epoch=500,batch_size=BATCH); cfg["validation"]["frequency"]=10**12
    actual=jsha(cfg)
    if actual!=EXPECTED_CONFIG_SHA[component]: raise TrainingGateError(f"developmental config hash/runtime-layout drift: {actual}")
    return cfg

def split_map(path: Path):
    if file_sha(path)!=SPLIT_SHA: raise TrainingGateError("BEDROOM split drift")
    rows=list(csv.reader(path.open())); m={a:b for a,b in rows}
    if {s:sum(v==s for v in m.values()) for s in ("train","val","test")}!={"train":6037,"val":249,"test":248}: raise TrainingGateError("split counts drift")
    return m

def tag_index(ds): return {str(tag):i for i,tag in enumerate(unwrap(ds)._tags)}
def train_pool(ds, split: Path):
    m=split_map(split); tags=[str(x) for x in unwrap(ds)._tags]
    ids=sorted(x for x in tags if m.get(x.split("_",1)[1] if "_" in x else x)=="train")
    digest=hashlib.sha256(("\n".join(ids)+"\n").encode()).hexdigest()
    if len(ids)!=TRAIN_POOL_N or digest!=TRAIN_POOL_SHA: raise TrainingGateError("materialized train pool drift")
    return ids

def slot(example_id):
    import re
    m=re.search(r"-S(\d{2})-IS-SUPPORT-(?:12|14)$",example_id)
    if not m: raise TrainingGateError("bad example id")
    return int(m.group(1))
def row_key(r): return f"{r['source_scene_id']}|S{slot(r['example_id']):02d}"
def corpus_rows(corpus_dir: Path, component: str):
    p=corpus_dir/("IS-SUPPORT-12.jsonl" if component=="SGP-12" else "IS-SUPPORT-14.jsonl")
    rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    if len(rows)!=12240 or rows_sha(rows)!=CORPUS_SHA[component]: raise TrainingGateError(f"{component} corpus drift")
    eligible=[x.strip() for x in (corpus_dir/"eligible_scenes.txt").read_text().splitlines() if x.strip()]
    if jsha(eligible)!=ELIGIBLE_SHA: raise TrainingGateError("eligible pool drift")
    return rows
def frozen_order(keys):
    x=sorted(keys); random.Random(SEED).shuffle(x); return x
def prepare(component, ds, split, corpus_dir):
    idx=tag_index(ds)
    if component=="BEDROOM-SG2SC-SHARED":
        order=frozen_order(train_pool(ds,split)); return {"ds":ds,"idx":idx,"order":order,"rows":None,"sha":TRAIN_POOL_SHA}
    rows=corpus_rows(corpus_dir,component); by={row_key(r):r for r in rows}
    if len(by)!=len(rows) or ({r["source_scene_id"] for r in rows}-set(idx)): raise TrainingGateError("corpus key/scene mapping failure")
    return {"ds":ds,"idx":idx,"order":frozen_order(list(by)),"rows":by,"sha":CORPUS_SHA[component]}
def get_batch(data,cursor):
    keys=[data["order"][(cursor+i)%len(data["order"])] for i in range(BATCH)]; samples=[]; prompts=None
    if data["rows"] is None:
        samples=[data["ds"][data["idx"][k]] for k in keys]
    else:
        prompts=[]
        for k in keys:
            r=data["rows"][k]; samples.append(data["ds"][data["idx"][r["source_scene_id"]]]); prompts.append(r["exact_instruction"])
    return data["ds"].collate_fn(samples),keys,prompts

def init_component(source,component,cfg,ds,device,clip,fvq,bounds):
    if component.startswith("SGP-"):
        if str(source) not in sys.path: sys.path.insert(0,str(source))
        from diffusers.training_utils import EMAModel
        from transformers import CLIPTokenizerFast,CLIPTextModelWithProjection
        from src.models import model_from_config,optimizer_from_config
        tok=CLIPTokenizerFast.from_pretrained(str(clip),local_files_only=True)
        if tok.model_max_length!=77: raise TrainingGateError("CLIP max length drift")
        enc=CLIPTextModelWithProjection.from_pretrained(str(clip),local_files_only=True).to(device).eval()
        for p in enc.parameters(): p.requires_grad_(False)
        # CLIP loading may consume Torch RNG. Restore the preregistered stream
        # immediately before SGP construction so both support arms begin from
        # the exact frozen initialization and identical subsequent RNG state.
        set_rng()
        model=model_from_config(cfg["model"],ds.n_object_types,ds.n_predicate_types,text_emb_dim=enc.config.hidden_size).to(device)
        opt=optimizer_from_config(cfg["training"]["optimizer"],filter(lambda p:p.requires_grad,model.parameters()))
        e=cfg["training"]["ema"]
        ema=EMAModel(model.parameters(),decay=e["max_decay"],min_decay=e["min_decay"],update_after_step=e["update_after_step"],use_ema_warmup=e["use_warmup"],inv_gamma=e["inv_gamma"],power=e["power"]); ema.to(device)
        text=(tok,enc); vq=None
    else:
        model,opt,ema,text,vq=make_model(source,component,cfg,ds,device,clip,fvq,bounds)
    init=ssha(model.state_dict()); params=sum(p.numel() for p in model.parameters())
    if component.startswith("SGP-") and (init!=EXPECTED_INIT or params!=EXPECTED_PARAMS): raise TrainingGateError("SGP initialization invariant failed")
    return model,opt,ema,text,vq,init,params

def loss_for(component,model,batch,prompts,text,vq,cfg,device):
    if component.startswith("SGP-"):
        h,e=encode(text,prompts,device); losses=model.compute_losses(batch,h,e)
    else: losses=model.compute_losses(batch,vqvae_model=vq)
    return losses,total_loss(losses,cfg["training"]["loss_weights"],device)

def env(device):
    p=torch.cuda.get_device_properties(device)
    try: driver=subprocess.check_output(["nvidia-smi","--query-gpu=driver_version","--format=csv,noheader"],text=True).splitlines()[0].strip()
    except Exception: driver=None
    return {"gpu_model":p.name,"gpu_total_memory":int(p.total_memory),"cuda":torch.version.cuda,"driver":driver,"pytorch":torch.__version__,"batch_size":BATCH,"gradient_accumulation":1}
def claim_key(component,sha,cfgsha): return hashlib.sha256(f"{OBJECT_ID}|{component}|{sha}|{cfgsha}|{SEED}|{STEPS}|{BATCH}".encode()).hexdigest()

def preflight(*,component,run_root,authority,proposal,source,bedroom,split,corpus_dir,clip,fvq,bounds,device_index=0):
    verify_authority(authority,proposal); verify_assets(source,clip,fvq,bounds)
    if component not in COMPONENTS or not torch.cuda.is_available(): raise TrainingGateError("component/CUDA invalid")
    root=run_root/component; root.mkdir(parents=True,exist_ok=False); set_rng(); device=torch.device(f"cuda:{device_index}")
    cfg=build_config(source,component,bedroom); cfgsha=jsha(cfg); ds=make_dataset(source,cfg); data=prepare(component,ds,split,corpus_dir)
    claim={"object_id":OBJECT_ID,"component_id":component,"claim_key":claim_key(component,data["sha"],cfgsha),"state":"CLAIMED_RESOURCE_PREFLIGHT","optimizer_steps_committed":0,"scientific_outcomes":0}
    atom(root/"claim.json",claim)
    with torch.cuda.device(device):
        torch.cuda.reset_peak_memory_stats()
    try:
        model,opt,ema,text,vq,init,params=init_component(source,component,cfg,ds,device,clip,fvq,bounds)
        batch,keys,prompts=get_batch(data,0); batch=move(batch,device); opt.zero_grad(set_to_none=True); losses,total=loss_for(component,model,batch,prompts,text,vq,cfg,device)
        if not bool(torch.isfinite(total).all()): raise TrainingGateError("nonfinite preflight loss")
        total.backward()
        if not grads_finite(model): raise TrainingGateError("nonfinite preflight gradient")
        torch.cuda.synchronize(device)
        out={"object_id":OBJECT_ID,"component_id":component,"state":"RESOURCE_PREFLIGHT_PASS","optimizer_steps":0,"scientific_outcomes":0,"batch_size":BATCH,"initial_model_state_sha256":init,"parameter_count":params,"first_batch_keys_sha256":jsha(keys),"loss_finite":True,"grad_finite":True,"peak_allocated_vram":int(torch.cuda.max_memory_allocated(device)),"peak_reserved_vram":int(torch.cuda.max_memory_reserved(device)),"environment":env(device),"content_sha256":data["sha"],"config_sha256":cfgsha}
        atom(root/"resource_preflight.json",out); claim.update(state="RESOURCE_PREFLIGHT_PASS",resource_preflight_sha256=file_sha(root/"resource_preflight.json")); atom(root/"claim.json",claim); return out
    except Exception as exc:
        atom(root/"resource_preflight_failure.json",{"component_id":component,"state":"RESOURCE_PREFLIGHT_FAIL","optimizer_steps":0,"scientific_outcomes":0,"error_type":type(exc).__name__,"error":str(exc)}); claim["state"]="FAIL_CLOSED"; atom(root/"claim.json",claim); raise
