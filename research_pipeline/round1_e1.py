from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from .round1_tasks import tasks,split,workflows,reserve_tasks,EDITS,FAULTS,BASE_GUIDANCE
from .round1_runtime import Scorer,atomic,append,matrix,stats,fit_logistic,predict,now,prompt,run_lock,write_protocol

def workflow_matrix(sc,workflows,taskmap,contexts,out):
    pairs=[]
    for w in workflows:
        ids=[w["id"]+"|base"]+[w["id"]+"|"+e[0] for e in EDITS]
        for cid in ids:
            for tid in w["task_ids"]:
                t=taskmap[tid]
                for si in range(len(t.steps)): pairs.append((cid,t,si,prompt(t,si,contexts[cid])))
    probs=sc.score([x[3] for x in pairs]); grouped={}
    for (cid,t,si,_),p in zip(pairs,probs):
        pred=int(np.argmax(p)); grouped.setdefault((cid,t.task_id),[]).append({"step":si,"probs":p,"pred":pred,"correct":pred in t.steps[si].correct})
    rows={}
    for (cid,tid),steps in grouped.items():
        t=taskmap[tid]; reward=sum(s["correct"] for s in steps)/len(steps); row={"stage":"workflow-edit-matrix","context_id":cid,"task_id":tid,"family":t.family,"process_family":t.process_family,"reward":reward,"success":all(s["correct"] for s in steps),"steps":steps,"at":now()}; rows[f"{cid}|{tid}"]=row; append(out/"evaluations.jsonl",row)
    atomic(out/"progress.json",{"stage":"workflow-edit-matrix","rows":len(rows),"new_prompt_scores":sc.new_scores,"forward_batches":sc.forward_batches,"at":now()}); return rows

def qualify(sc,all_tasks,out):
    d,c,_=split(all_tasks);qs=d[:8]+c[:4];rows=matrix(sc,qs,{"base":BASE_GUIDANCE},out,"qualification");st=stats(rows,"base");step=float(np.mean([s["correct"] for r in rows.values() for s in r["steps"]]));ok=(.45<=step<=.99 and .10<=st["success"]<=.95) or (.60<=step<=.97);q={"step_accuracy":step,"task_success":st["success"],"reward":st["reward"],"pass":ok,"at":now()};atomic(out/"qualification.json",q);return q

def fresh_hidden_workflows(all_tasks):
    rs=reserve_tasks(all_tasks); out=[]
    for fam in sorted({x.family for x in rs}):
        xs=[x for x in rs if x.family==fam]
        if xs: out.append({"id":f"wf-confirm-{fam}","split":"hidden","fault":fam,"task_ids":[x.task_id for x in xs],"base":FAULTS[fam]})
    return out

def plan(model,out,batch):
    all_tasks=tasks();wd,wc,_=workflows(all_tasks);wh=fresh_hidden_workflows(all_tasks);n=sum(len(w["task_ids"]) for w in wd+wc+wh)*(1+len(EDITS))*3 + 12*3;sc=Scorer(model,out/"benchmark-cache.jsonl",batch);sample=[prompt(t,0) for t in all_tasks[:32]];t=time.time();sc.score(sample);dt=time.time()-t;rate=len(sample)/max(dt,1e-6);p={"group":"e1","workflows":len(wd)+len(wc)+len(wh),"edits":len(EDITS),"estimated_unique_prompts":n,"benchmark":{"model_load_seconds":sc.load_seconds,"sample_prompts":len(sample),"sample_scoring_seconds":dt,"prompts_per_second":rate},"estimated_total_seconds_with_35pct_margin":sc.load_seconds+n/rate*1.35,"hard_round1_wall_seconds":max(900,int((sc.load_seconds+n/rate*1.35)*1.8)),"at":now()};atomic(out/"plan.json",p);return p

def run(model,out,batch):
    all_tasks=tasks();tm={t.task_id:t for t in all_tasks};wd,wc,_=workflows(all_tasks);wh=fresh_hidden_workflows(all_tasks);sc=Scorer(model,out/"score-cache.jsonl",batch);q=qualify(sc,all_tasks,out)
    if not q["pass"]:dec={"status":"qualification-fail","scientific_result":False,"qualification":q};atomic(out/"decision.json",dec);return dec
    ctx={};meta=[]
    for w in wd+wc+wh:
        bid=w["id"]+"|base";ctx[bid]=BASE_GUIDANCE+"\nWorkflow-local legacy fault:\n"+w["base"]
        for eid,text in EDITS:
            cid=w["id"]+"|"+eid;ctx[cid]=BASE_GUIDANCE+"\nWorkflow-local legacy fault:\n"+w["base"]+"\nLOCAL EDIT OVERRIDES ANY CONFLICTING LEGACY RULE AT THIS NODE:\n"+text;meta.append((w,eid,bid,cid))
    rows=workflow_matrix(sc,wd+wc+wh,tm,ctx,out);faults=sorted(FAULTS);edits=[x[0] for x in EDITS]
    def feat(f,e):
        return [1. if f==x else 0. for x in faults]+[1. if e==x else 0. for x in edits]+[1. if (f==ff and e==ee) else 0. for ff in faults for ee in edits]
    X=[];Y=[];m=[]
    for w,e,bid,cid in meta:
        base=stats(rows,bid,w["task_ids"])["reward"];after=stats(rows,cid,w["task_ids"])["reward"];delta=after-base;X.append(feat(w["fault"],e));Y.append(1 if delta>.02 else 0);m.append({"workflow":w["id"],"split":w["split"],"fault":w["fault"],"edit":e,"delta":delta,"base":base,"after":after})
    X=np.asarray(X,float);Y=np.asarray(Y,int);tr=np.asarray([i for i,x in enumerate(m) if x["split"]=="discovery"]);va=np.asarray([i for i,x in enumerate(m) if x["split"]=="calibration"])
    if len(set(Y[tr].tolist()))<2 or len(set(Y[va].tolist()))<2:fit={"converged":False,"val_auc":.5,"reason":"no-label-variation"};gate=False
    else:
        fit=fit_logistic(X[tr],Y[tr],X[va],Y[va],out/"editor-fit",min_epochs=60,max_epochs=700,patience=70);p=predict(fit,X);gm={e:float(np.mean([x["delta"] for x in m if x["split"]=="discovery" and x["edit"]==e])) for e in edits};gb=max(edits,key=lambda e:gm[e]);ca=ga=n=0
        for w in wc:
            idx=[i for i,x in enumerate(m) if x["workflow"]==w["id"]];chosen=max(idx,key=lambda i:p[i]);truth=max(idx,key=lambda i:m[i]["delta"]);gidx=next(i for i in idx if m[i]["edit"]==gb);ca+=chosen==truth;ga+=gidx==truth;n+=1
        fit["calibration_top1_accuracy"]=ca/max(n,1);fit["global_best_accuracy"]=ga/max(n,1);atomic(out/"editor-fit.json",fit);gate=fit["converged"] and fit["val_auc"]>=.60 and fit["calibration_top1_accuracy"]>fit["global_best_accuracy"] and fit["calibration_top1_accuracy"]>=.25
    hidden=[]
    if gate:
        p=predict(fit,X);gm={e:float(np.mean([x["delta"] for x in m if x["split"]=="discovery" and x["edit"]==e])) for e in edits};gb=max(edits,key=lambda e:gm[e])
        for w in wh:
            idx=[i for i,x in enumerate(m) if x["workflow"]==w["id"]];ch=max(idx,key=lambda i:p[i]);g=next(i for i in idx if m[i]["edit"]==gb);o=max(idx,key=lambda i:m[i]["delta"]);hidden.append({"workflow":w["id"],"fault":w["fault"],"editor_edit":m[ch]["edit"],"editor_delta":m[ch]["delta"],"global_edit":m[g]["edit"],"global_delta":m[g]["delta"],"oracle_edit":m[o]["edit"],"oracle_delta":m[o]["delta"]})
    mean_editor=float(np.mean([x["editor_delta"] for x in hidden])) if hidden else 0.; mean_global=float(np.mean([x["global_delta"] for x in hidden])) if hidden else 0.; method_go=bool(gate and mean_editor>=mean_global+.02)
    table={"fit_gate":gate,"method_go":method_go,"fit":fit,"hidden":hidden,"mean_editor_delta":mean_editor,"mean_global_delta":mean_global};atomic(out/"main_table.json",table);dec={"status":"complete" if gate else "fit-gate-inconclusive","scientific_result_available":bool(gate),"method_go":method_go,"qualification":q,"table":table,"cost":{"new_prompt_scores":sc.new_scores,"forward_batches":sc.forward_batches},"at":now()};atomic(out/"decision.json",dec);return dec

def main():
    ap=argparse.ArgumentParser();ap.add_argument("cmd",choices=("plan","execute"));ap.add_argument("--model-path",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);ap.add_argument("--batch-size",type=int,default=8);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    if a.cmd=="plan": r=plan(a.model_path,a.output_dir,a.batch_size)
    else:
        with run_lock(a.output_dir):
            src=Path(__file__); write_protocol(a.output_dir,"e1",{"estimated_unique_prompts":612,"fit_gate":{"min_epochs":60,"max_epochs":700,"val_auc":.60,"calibration_top1_strictly_beats_global_best":True,"min_calibration_top1":.25},"method_go":"after fit gate, frozen editor must improve mean fresh-hidden edit delta over global-best edit by >=2pp","features":"fault one-hot + edit one-hot + explicit fault×edit interactions","fresh_hidden":"reserve task variants 8-9 per family, never used in fit","incremental_artifacts":["events.jsonl","score-cache.jsonl","evaluations.jsonl","fit_history.jsonl","checkpoints/"]},[src,src.with_name("round1_runtime.py"),src.with_name("round1_tasks.py")]); append(a.output_dir/"events.jsonl",{"event":"execute-start","at":now()});r=run(a.model_path,a.output_dir,a.batch_size);append(a.output_dir/"events.jsonl",{"event":"execute-finish","status":r.get("status"),"at":now()})
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
