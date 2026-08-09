from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from .round1_tasks import tasks,split,LESSONS,BASE_GUIDANCE
from .round1_runtime import Scorer,atomic,append,matrix,stats,now,prompt,run_lock,write_protocol

def qualify(scorer,all_tasks,out):
    d,c,_=split(all_tasks);qs=d[:8]+c[:4];rows=matrix(scorer,qs,{"base":BASE_GUIDANCE},out,"qualification");st=stats(rows,"base");step=float(np.mean([s["correct"] for r in rows.values() for s in r["steps"]]));ok=(.45<=step<=.99 and .10<=st["success"]<=.95) or (.60<=step<=.97);q={"step_accuracy":step,"task_success":st["success"],"reward":st["reward"],"pass":ok,"at":now()};atomic(out/"qualification.json",q);return q

def plan(model,out,batch):
    all_tasks=tasks();d,c,h=split(all_tasks);est=(1+len(LESSONS))*len(c+h)*3 + len(d[:8])*3;sc=Scorer(model,out/"benchmark-cache.jsonl",batch);sample=[prompt(t,0) for t in all_tasks[:32]];t=time.time();sc.score(sample);dt=time.time()-t;rate=len(sample)/max(dt,1e-6);p={"group":"b1","estimated_unique_prompts":est,"benchmark":{"model_load_seconds":sc.load_seconds,"sample_prompts":len(sample),"sample_scoring_seconds":dt,"prompts_per_second":rate},"estimated_total_seconds_with_35pct_margin":sc.load_seconds+est/rate*1.35,"hard_round1_wall_seconds":max(900,int((sc.load_seconds+est/rate*1.35)*1.8)),"at":now()};atomic(out/"plan.json",p);return p

def run(model,out,batch):
    all_tasks=tasks();_,c,h=split(all_tasks);sc=Scorer(model,out/"score-cache.jsonl",batch);q=qualify(sc,all_tasks,out)
    if not q["pass"]:dec={"status":"qualification-fail","scientific_result":False,"qualification":q};atomic(out/"decision.json",dec);return dec
    ctx={"base":BASE_GUIDANCE}|{x[0]:BASE_GUIDANCE+"\nRETRIEVED LESSON OVERRIDES ANY CONFLICTING LEGACY RULE:\n"+x[3] for x in LESSONS};rows=matrix(sc,c+h,ctx,out,"lesson-matrix");pgrp=sorted({t.process_family for t in c});effects=[];hids=[t.task_id for t in h]
    for lid,sem,src,text in LESSONS:
        per=[]
        for pg in pgrp:
            ids=[t.task_id for t in c if t.process_family==pg]
            if ids:per.append((pg,stats(rows,lid,ids)["reward"]-stats(rows,"base",ids)["reward"],len(ids)))
        mean=float(np.average([x[1] for x in per],weights=[x[2] for x in per])) if per else 0.;worst=min([x[1] for x in per],default=0.);var=float(np.var([x[1] for x in per])) if per else 0.;he=stats(rows,lid,hids)["reward"]-stats(rows,"base",hids)["reward"]
        effects.append({"id":lid,"semantic":sem,"source_process":src,"validation_mean":mean,"validation_worst":worst,"validation_var":var,"process_effects":per,"hidden_effect":he})
    coverage=all(len(x["process_effects"])>=2 for x in effects);variation=float(np.std([x["validation_mean"] for x in effects]));gate=coverage and variation>=.005;k=3
    util=sorted(range(len(effects)),key=lambda i:effects[i]["validation_mean"],reverse=True)[:k];rob=sorted(range(len(effects)),key=lambda i:(effects[i]["validation_worst"],effects[i]["validation_mean"],-effects[i]["validation_var"]),reverse=True)[:k]
    counts={s:len({x["source_process"] for x in effects if x["semantic"]==s}) for s in {x["semantic"] for x in effects}};cons=[i for i,x in enumerate(effects) if counts[x["semantic"]]>=3][:k];single=list(range(k))
    def summ(name,idx):
        vals=[effects[i]["hidden_effect"] for i in idx];return {"policy":name,"lessons":[effects[i]["id"] for i in idx],"mean_hidden_effect":float(np.mean(vals)) if vals else 0.,"negative_hidden":sum(v<0 for v in vals)}
    table=[summ("single-source",single),summ("consensus",cons),summ("utility-only",util),summ("cross-process-robust",rob)];atomic(out/"main_table.json",table)
    utility_row=table[2]; robust_row=table[3]
    method_go=bool(gate and ((robust_row["mean_hidden_effect"] >= utility_row["mean_hidden_effect"]+.02) or (robust_row["negative_hidden"] < utility_row["negative_hidden"] and robust_row["mean_hidden_effect"] >= utility_row["mean_hidden_effect"]-.02)))
    dec={"status":"complete" if gate else "estimation-inconclusive","scientific_result_available":bool(gate),"method_go":method_go,"qualification":q,"estimation_gate":{"coverage_ok":coverage,"validation_effect_std":variation,"pass":gate},"effects":effects,"table":table,"cost":{"new_prompt_scores":sc.new_scores,"forward_batches":sc.forward_batches},"at":now()};atomic(out/"decision.json",dec);return dec

def main():
    ap=argparse.ArgumentParser();ap.add_argument("cmd",choices=("plan","execute"));ap.add_argument("--model-path",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);ap.add_argument("--batch-size",type=int,default=8);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    if a.cmd=="plan": r=plan(a.model_path,a.output_dir,a.batch_size)
    else:
        with run_lock(a.output_dir):
            src=Path(__file__); write_protocol(a.output_dir,"b1",{"estimated_unique_prompts":648,"estimation_gate":{"min_process_families":2,"min_validation_effect_std":.005},"method_go":"cross-process robust must beat utility-only by >=2pp hidden effect, or reduce negative hidden lessons with <=2pp effect loss","incremental_artifacts":["events.jsonl","score-cache.jsonl","evaluations.jsonl","progress.json"]},[src,src.with_name("round1_runtime.py"),src.with_name("round1_tasks.py")]); append(a.output_dir/"events.jsonl",{"event":"execute-start","at":now()});r=run(a.model_path,a.output_dir,a.batch_size);append(a.output_dir/"events.jsonl",{"event":"execute-finish","status":r.get("status"),"at":now()})
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
