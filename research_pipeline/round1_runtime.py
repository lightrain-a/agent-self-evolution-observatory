from __future__ import annotations
import hashlib, json, os, time, fcntl, subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any
import numpy as np
from .round1_tasks import Task

SEED=20260810; LABELS=("1","2","3","4")
@contextmanager
def run_lock(out:Path):
    out.mkdir(parents=True,exist_ok=True); f=(out/"run.lock").open("a+")
    try:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError as e:
        f.close(); raise RuntimeError(f"round1 output directory is already locked: {out}") from e
    try: yield
    finally:
        try: fcntl.flock(f.fileno(),fcntl.LOCK_UN)
        finally: f.close()
def now():
    import datetime as d
    return d.datetime.now(d.timezone.utc).replace(microsecond=0).isoformat()
def sha(s:str): return hashlib.sha256(s.encode()).hexdigest()
def git_head() -> str:
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=Path(__file__).resolve().parents[1],text=True).strip()
    except Exception: return "unknown"
def source_hash(*paths:Path) -> str:
    h=hashlib.sha256()
    for p in paths:
        h.update(str(p.name).encode()); h.update(p.read_bytes())
    return h.hexdigest()
def write_protocol(out:Path, group:str, payload:dict[str,Any], source_files:list[Path]) -> dict[str,Any]:
    row={"schema_version":"1.0","group":group,"code_commit":git_head(),"source_hash":source_hash(*source_files),"created_at":now(),**payload}; atomic(out/"protocol.json",row); return row
def atomic(path:Path,payload:Any):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def append(path:Path,row:dict[str,Any]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n"); f.flush(); os.fsync(f.fileno())

def prompt(task:Task,si:int,ctx:str=""):
    s=task.steps[si]; opts="\n".join(f"{i+1}. {x}" for i,x in enumerate(s.options)); c=f"\nPersistent guidance:\n{ctx}\n" if ctx else ""
    return f"Goal: {task.goal}\nFamily: {task.family}\nCurrent state: {s.state}{c}\nAvailable actions:\n{opts}\nSelect the single best next action."

class Scorer:
    def __init__(self,model_path:Path,cache:Path,batch_size=8,device="cuda:0"):
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        self.torch=torch; self.device=device; self.batch_size=batch_size; self.cache_path=cache; self.cache={}; self.new_scores=0; self.forward_batches=0
        if cache.exists():
            for line in cache.read_text(encoding="utf-8").splitlines():
                try:
                    r=json.loads(line); self.cache[r["key"]]=r["probs"]
                except Exception: pass
        t=time.time(); self.tok=AutoTokenizer.from_pretrained(str(model_path),trust_remote_code=True)
        if self.tok.pad_token_id is None: self.tok.pad_token=self.tok.eos_token
        self.tok.padding_side="left"
        self.model=AutoModelForCausalLM.from_pretrained(str(model_path),torch_dtype=torch.float16,low_cpu_mem_usage=True,trust_remote_code=True)
        self.model.to(device); self.model.eval(); self.load_seconds=time.time()-t
        self.label_ids=[]
        for x in LABELS:
            ids=self.tok.encode(x,add_special_tokens=False)
            if len(ids)!=1: raise RuntimeError(f"choice label {x} not single token: {ids}")
            self.label_ids.append(ids[0])
    def fmt(self,text:str):
        msgs=[{"role":"system","content":"You are a careful tool-using agent. Choose the best next action. Reply with exactly one number: 1, 2, 3, or 4."},{"role":"user","content":text}]
        return self.tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)+"\nChoice:"
    def score(self,prompts:list[str]):
        fm=[self.fmt(x) for x in prompts]; keys=[sha(x) for x in fm]; miss=[i for i,k in enumerate(keys) if k not in self.cache]
        for st in range(0,len(miss),self.batch_size):
            idx=miss[st:st+self.batch_size]; texts=[fm[i] for i in idx]
            enc=self.tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=768); enc={k:v.to(self.device) for k,v in enc.items()}
            with self.torch.inference_mode():
                logits=self.model(**enc).logits[:,-1,self.label_ids].float(); probs=self.torch.softmax(logits,-1).cpu().numpy()
            self.forward_batches+=1
            for i,p in zip(idx,probs):
                row=[float(v) for v in p]; self.cache[keys[i]]=row; append(self.cache_path,{"key":keys[i],"probs":row,"at":now()}); self.new_scores+=1
        return [self.cache[k] for k in keys]

def matrix(scorer:Scorer,tasks:list[Task],contexts:dict[str,str],out:Path,stage:str):
    pairs=[]
    for cid,ctx in contexts.items():
        for t in tasks:
            for si in range(len(t.steps)): pairs.append((cid,t,si,prompt(t,si,ctx)))
    probs=scorer.score([x[3] for x in pairs]); grouped={}
    for (cid,t,si,_),p in zip(pairs,probs):
        pred=int(np.argmax(p)); grouped.setdefault((cid,t.task_id),[]).append({"step":si,"probs":p,"pred":pred,"correct":pred in t.steps[si].correct})
    rows={}
    for (cid,tid),steps in grouped.items():
        t=next(x for x in tasks if x.task_id==tid); r=sum(s["correct"] for s in steps)/len(steps)
        row={"stage":stage,"context_id":cid,"task_id":tid,"family":t.family,"process_family":t.process_family,"reward":r,"success":all(s["correct"] for s in steps),"steps":steps,"at":now()}
        rows[f"{cid}|{tid}"]=row; append(out/"evaluations.jsonl",row)
    atomic(out/"progress.json",{"stage":stage,"rows":len(rows),"new_prompt_scores":scorer.new_scores,"forward_batches":scorer.forward_batches,"at":now()}); return rows

def stats(rows,cid,ids=None):
    ids=set(ids) if ids is not None else None; xs=[r for r in rows.values() if r["context_id"]==cid and (ids is None or r["task_id"] in ids)]
    if not xs:return {"reward":0.0,"success":0.0}
    return {"reward":float(np.mean([x["reward"] for x in xs])),"success":float(np.mean([x["success"] for x in xs]))}
def mean_js(rows,base,cid,ids):
    vals=[]; eps=1e-9
    for tid in ids:
        for a,b in zip(rows[f"{base}|{tid}"]["steps"],rows[f"{cid}|{tid}"]["steps"]):
            p=np.asarray(a["probs"])+eps; q=np.asarray(b["probs"])+eps; p/=p.sum();q/=q.sum();m=(p+q)/2
            vals.append(.5*np.sum(p*np.log(p/m))+.5*np.sum(q*np.log(q/m)))
    return float(np.mean(vals)) if vals else 0.0

def auc(y,p):
    y=np.asarray(y); p=np.asarray(p); pos=p[y==1]; neg=p[y==0]
    if not len(pos) or not len(neg): return .5
    return float(np.mean((pos[:,None]>neg[None,:]) + .5*(pos[:,None]==neg[None,:])))
def fit_logistic(Xt,yt,Xv,yv,out:Path,min_epochs=40,max_epochs=500,patience=50,lr=.05,l2=1e-3):
    rng=np.random.default_rng(SEED); mu=Xt.mean(0); sd=Xt.std(0); sd[sd<1e-6]=1.; A=(Xt-mu)/sd; V=(Xv-mu)/sd
    w=rng.normal(0,.02,A.shape[1]); b=0.; best=None; noimp=0; hist=[]
    for ep in range(1,max_epochs+1):
        p=1/(1+np.exp(-np.clip(A@w+b,-30,30))); gw=A.T@(p-yt)/len(yt)+l2*w; gb=float(np.mean(p-yt)); w-=lr*gw;b-=lr*gb
        pv=1/(1+np.exp(-np.clip(V@w+b,-30,30))); loss=float(-np.mean(yv*np.log(pv+1e-9)+(1-yv)*np.log(1-pv+1e-9))); va=auc(yv,pv); g=float(np.linalg.norm(gw))
        rec={"epoch":ep,"val_loss":loss,"val_auc":va,"grad_norm":g}; hist.append(rec); append(out/"fit_history.jsonl",rec)
        if ep%10==0: atomic(out/"checkpoints"/f"epoch-{ep:04d}.json",{"epoch":ep,"w":w.tolist(),"b":b,"mu":mu.tolist(),"sd":sd.tolist(),"val_loss":loss,"val_auc":va})
        score=(va,-loss)
        if best is None or score>best[0]: best=(score,ep,w.copy(),b,loss,va);noimp=0
        else:noimp+=1
        if ep>=min_epochs and noimp>=patience and g<.03:break
    _,bep,bw,bb,bl,bauc=best; conv=len(hist)>=min_epochs and (len(hist)<max_epochs or hist[-1]["grad_norm"]<.08)
    res={"epochs_ran":len(hist),"best_epoch":bep,"val_loss":bl,"val_auc":bauc,"converged":conv,"w":bw.tolist(),"b":bb,"mu":mu.tolist(),"sd":sd.tolist()}; atomic(out/"fit.json",res);return res
def predict(fit,X):
    w=np.asarray(fit["w"]);mu=np.asarray(fit["mu"]);sd=np.asarray(fit["sd"]);return 1/(1+np.exp(-np.clip(((X-mu)/sd)@w+fit["b"],-30,30)))
