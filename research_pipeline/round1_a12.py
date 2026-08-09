from __future__ import annotations
import argparse,json,random,time
from pathlib import Path
import numpy as np
from .round1_tasks import tasks,split,UPDATES,BASE_GUIDANCE
from .round1_runtime import Scorer,atomic,append,matrix,stats,mean_js,fit_logistic,predict,now,prompt,run_lock,write_protocol
SEED=20260810

def qualify(scorer,all_tasks,out):
    d,c,_=split(all_tasks); qs=d[:8]+c[:4]; rows=matrix(scorer,qs,{"base":BASE_GUIDANCE},out,"qualification")
    st=stats(rows,"base"); step=float(np.mean([s["correct"] for r in rows.values() for s in r["steps"]])); ok=(.45<=step<=.99 and .10<=st["success"]<=.95) or (.60<=step<=.97)
    q={"step_accuracy":step,"task_success":st["success"],"reward":st["reward"],"pass":ok,"at":now()};atomic(out/"qualification.json",q);return q

def plan(model,out,batch):
    all_tasks=tasks(); d,c,h=split(all_tasks); est=(1+len(UPDATES))*len(d+c+h)*3+10*4*8*3
    scorer=Scorer(model,out/"benchmark-cache.jsonl",batch); sample=[prompt(t,0) for t in all_tasks[:32]]; t=time.time();scorer.score(sample);elapsed=time.time()-t;rate=len(sample)/max(elapsed,1e-6)
    p={"group":"a12","estimated_unique_prompts":est,"benchmark":{"model_load_seconds":scorer.load_seconds,"sample_prompts":len(sample),"sample_scoring_seconds":elapsed,"prompts_per_second":rate},"estimated_total_seconds_with_35pct_margin":scorer.load_seconds+est/rate*1.35,"hard_round1_wall_seconds":max(1200,int((scorer.load_seconds+est/rate*1.35)*1.8)),"at":now()};atomic(out/"plan.json",p);return p

def run(model,out,batch):
    all_tasks=tasks(); d,c,h=split(all_tasks); scorer=Scorer(model,out/"score-cache.jsonl",batch); q=qualify(scorer,all_tasks,out)
    if not q["pass"]: dec={"status":"qualification-fail","scientific_result":False,"qualification":q};atomic(out/"decision.json",dec);return dec
    contexts={"base":BASE_GUIDANCE}|{u[0]:BASE_GUIDANCE+"\nLATEST PERSISTENT UPDATE OVERRIDES ANY CONFLICTING LEGACY RULE:\n"+u[3] for u in UPDATES}; rows=matrix(scorer,d+c+h,contexts,out,"a1-matrix"); probe=[t.task_id for t in c[:4]]
    X=[];y=[];meta=[]
    for uid,surface,target,text in UPDATES:
        targ=[t.task_id for t in d if t.family==target]; prot=[t.task_id for t in d if t.family!=target]
        gain=stats(rows,uid,targ)["reward"]-stats(rows,"base",targ)["reward"]; reg=stats(rows,"base",prot)["reward"]-stats(rows,uid,prot)["reward"]; drift=mean_js(rows,"base",uid,probe); harm=1 if reg>.02 else 0
        X.append([gain,drift,len(text.split())/30]);y.append(harm);meta.append({"id":uid,"surface":surface,"target":target,"gain":gain,"reg":reg,"drift":drift,"harmful":harm})
    X=np.asarray(X,float);y=np.asarray(y,int);pos=[i for i,v in enumerate(y) if v==1];neg=[i for i,v in enumerate(y) if v==0]
    if len(pos)<2 or len(neg)<2:
        dec={"status":"substrate-no-update-variation","scientific_result":False,"updates":meta};atomic(out/"decision.json",dec);return dec
    va=np.unique(np.asarray([pos[-1],neg[-1],pos[-2],neg[-2]]));tr=np.asarray([i for i in range(len(y)) if i not in set(va.tolist())]);fit=fit_logistic(X[tr],y[tr],X[va],y[va],out/"a1-fit");fitpass=fit["converged"] and fit["val_auc"]>=.60; probs=predict(fit,X)
    hm=[]
    for i,(uid,surface,target,text) in enumerate(UPDATES):
        th=[t.task_id for t in h if t.family==target];ph=[t.task_id for t in h if t.family!=target];hg=stats(rows,uid,th)["reward"]-stats(rows,"base",th)["reward"];hr=stats(rows,"base",ph)["reward"]-stats(rows,uid,ph)["reward"]
        hm.append(meta[i]|{"hidden_gain":hg,"hidden_regression":hr,"harm_probability":float(probs[i])})
    k=4
    def summ(name,idx):
        xs=[hm[i] for i in idx];return {"policy":name,"accepted":len(xs),"harmful":sum(x["hidden_regression"]>.02 for x in xs),"mean_gain":float(np.mean([x["hidden_gain"] for x in xs])),"mean_regression":float(np.mean([max(0,x["hidden_regression"]) for x in xs]))}
    gain=sorted(range(len(meta)),key=lambda i:meta[i]["gain"],reverse=True)[:k];raw=sorted(range(len(meta)),key=lambda i:(-meta[i]["gain"],meta[i]["drift"]))[:k];mdl=sorted(range(len(meta)),key=lambda i:(probs[i],-meta[i]["gain"]))[:k]
    a1=[summ("gain-only",gain),summ("gain+raw-drift",raw),summ("fitted-cross-surface-drift",mdl)]
    strongest=min(a1[:2],key=lambda x:(x["harmful"],-x["mean_gain"],x["mean_regression"])); learned=a1[2]
    a1_go=bool(fitpass and learned["harmful"] < strongest["harmful"] and learned["mean_gain"] >= strongest["mean_gain"]-.02)
    atomic(out/"a1-main-table.json",a1)
    # A2: full sequences are precomputed once and reused by all controllers.
    rng=random.Random(SEED);um={u[0]:u for u in UPDATES};ids=list(um);seqs=[]
    for _ in range(10): z=ids.copy();rng.shuffle(z);seqs.append(z[:4])
    a2tasks=d[:4]+c[:2]+h[:2];ctx={"base":BASE_GUIDANCE};seqctx=[]
    for si,s in enumerate(seqs):
        cur=[];row=[]
        for r,uid in enumerate(s,1):cur.append(um[uid][3]);cid=f"s{si:02d}-r{r}";ctx[cid]=BASE_GUIDANCE+"\nLATEST PERSISTENT UPDATES OVERRIDE CONFLICTING LEGACY RULES; APPLY THEM IN ORDER:\n"+"\n".join(cur);row.append(cid)
        seqctx.append(row)
    rr=matrix(scorer,a2tasks,ctx,out,"a2-sequences"); F=[];Y=[];fm=[]
    for si,cs in enumerate(seqctx):
        prev=stats(rr,"base",[t.task_id for t in a2tasks]); ss=[]
        for j,cid in enumerate(cs,1):
            st=stats(rr,cid,[t.task_id for t in a2tasks]); ss.append((st,st["reward"]-prev["reward"],max(0,prev["reward"]-st["reward"]))); prev=st
        util=[s[0]["reward"]-.02*(j+1) for j,s in enumerate(ss)];best=int(np.argmax(util))+1
        for j,(st,g,preg) in enumerate(ss[:-1],1):F.append([g,preg,st["reward"],j/4]);Y.append(1 if best>j else 0);fm.append((si,j))
    F=np.asarray(F,float);Y=np.asarray(Y,int);tri=np.asarray([i for i,(s,_) in enumerate(fm) if s<6]);vai=np.asarray([i for i,(s,_) in enumerate(fm) if s in (6,7)])
    if len(set(Y[tri].tolist()))<2 or len(set(Y[vai].tolist()))<2: af={"converged":False,"val_auc":.5,"reason":"no-label-variation"};ap=False
    else: af=fit_logistic(F[tri],Y[tri],F[vai],Y[vai],out/"a2-fit",min_epochs=50);ap=af["converged"] and af["val_auc"]>=.60
    hidden=[]
    if ap:
        for si in (8,9):
            prev=stats(rr,"base",[t.task_id for t in a2tasks]);chosen=4
            for j,cid in enumerate(seqctx[si][:-1],1):st=stats(rr,cid,[t.task_id for t in a2tasks]);p=float(predict(af,np.asarray([[st["reward"]-prev["reward"],max(0,prev["reward"]-st["reward"]),st["reward"],j/4]]))[0]);prev=st
            # deliberately evaluate all observed rounds; controller may stop at first p<.5
                
            # re-evaluate decision loop without model calls using cached stats
            prev=stats(rr,"base",[t.task_id for t in a2tasks]);chosen=4
            for j,cid in enumerate(seqctx[si][:-1],1):
                st=stats(rr,cid,[t.task_id for t in a2tasks]);p=float(predict(af,np.asarray([[st["reward"]-prev["reward"],max(0,prev["reward"]-st["reward"]),st["reward"],j/4]]))[0]);prev=st
                if p<.5:chosen=j;break
            st=stats(rr,seqctx[si][chosen-1],[t.task_id for t in a2tasks]);hidden.append({"sequence":si,"selected_round":chosen,"reward":st["reward"]})
    a2_go=bool(ap and hidden and np.mean([x["selected_round"] for x in hidden]) < 3.0)
    a2={"fit_gate":ap,"method_go":a2_go,"fit":af,"hidden":hidden};atomic(out/"a2-main-table.json",a2)
    any_interpretable=bool(fitpass or ap)
    dec={"status":"complete" if any_interpretable else "fit-gate-inconclusive","scientific_result_available":any_interpretable,"qualification":q,"a1":{"fit_gate":fitpass,"method_go":a1_go,"fit":fit,"table":a1,"updates":hm},"a2":a2,"cost":{"new_prompt_scores":scorer.new_scores,"forward_batches":scorer.forward_batches},"at":now()};atomic(out/"decision.json",dec);return dec

def main():
    ap=argparse.ArgumentParser();ap.add_argument("cmd",choices=("plan","execute"));ap.add_argument("--model-path",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);ap.add_argument("--batch-size",type=int,default=8);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    if a.cmd=="plan": r=plan(a.model_path,a.output_dir,a.batch_size)
    else:
        with run_lock(a.output_dir):
            src=Path(__file__); write_protocol(a.output_dir,"a12",{"estimated_unique_prompts":(1+len(UPDATES))*32*3+10*4*8*3,"harm_threshold":.02,"a1_fit_gate":{"min_epochs":40,"val_auc":.60},"a1_method_go":"strictly fewer harmful accepted updates than strongest simple baseline with <=2pp mean-gain loss","a2_fit_gate":{"min_epochs":50,"requires_continue_stop_label_variation":True},"incremental_artifacts":["events.jsonl","score-cache.jsonl","evaluations.jsonl","fit_history.jsonl","checkpoints/"]},[src,src.with_name("round1_runtime.py"),src.with_name("round1_tasks.py")]); append(a.output_dir/"events.jsonl",{"event":"execute-start","at":now()});r=run(a.model_path,a.output_dir,a.batch_size);append(a.output_dir/"events.jsonl",{"event":"execute-finish","at":now(),"status":r.get("status")})
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
