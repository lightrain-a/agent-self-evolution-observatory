from __future__ import annotations

import argparse, json, math, socket, subprocess, sys, time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v51 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v51, write_idea_discovery_v51

REVIEWER="agent-project-web-gpt-idea-discovery-v51-area-chair"


def load_bank()->dict[str,Any]:
    return json.loads(DEFAULT_JSON.read_text(encoding="utf-8")) if DEFAULT_JSON.exists() else build_idea_discovery_v51()


def packet(x:dict[str,Any])->dict[str,Any]:
    return {k:x.get(k) for k in ("id","parent_id","repair_source","title","problem","changed_assumption","exact_mechanism","update_surface","learning_signal","independent_ground_truth","simplest_baseline","decisive_pilot","stop_condition","what_is_inherited","material_change")}


def prompt(rows:Sequence[dict[str,Any]],idx:int,total:int)->str:
    schema={"reviewer":REVIEWER,"review_date":"YYYY-MM-DD","ideas":[{"idea_id":"exact id","verdict":"pass|revise|block","confidence":"high|medium|low","finding":"English","finding_zh":"中文","required_action":"English","required_action_zh":"中文","simplification_challenge":{"simplest_equivalent_method":"","reducible":"yes|partial|no","what_must_survive":""},"direct_collision":{"status":"none|partial|direct|unknown","closest_work":[],"surviving_difference":""},"strongest_baseline":"","decisive_pilot":"","stop_rule":"","unknowns":[]}]}
    return f"""# Independent v5.1 targeted-repair audit — batch {idx}/{total}

Act as a strict ICLR area chair. Every child was generated from a concrete v5 REVISE vector. Verify that the child MATERIALly fixes the reviewer objection rather than renaming the parent.
Use only official paper/PDF/proceedings/project/author-repo sources through 2026-08-01.

PASS only if:
- the changed assumption/object/supervision directly addresses the parent's required action;
- the persistent operator changes frozen future behavior;
- the simplest capacity-matched method using identical data/budget cannot reproduce it;
- independent truth and a decisive held-out pilot are valid.
REVISE when one material piece remains. BLOCK when the repair is cosmetic, directly collided, or reducible. BLOCK remains a future component/revival source.

Return only JSON:
```json
{json.dumps(schema,ensure_ascii=False,indent=2)}
```
Children:
```json
{json.dumps([packet(x) for x in rows],ensure_ascii=False,indent=2)}
```
"""


def read_store()->dict[str,Any]:
    if DEFAULT_EXTERNAL_JSON.exists():
        p=json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"));
        if isinstance(p,dict) and isinstance(p.get("reviews"),dict): return p
    return {"schema_version":"1.0","pipeline":"code-oracle -> signed-in ChatGPT web UI -> Agent project","required_host":EXPECTED_HOST,"reviews":{},"status":{}}


def prepare(bank:dict[str,Any],out:Path,batch_size:int)->dict[str,Any]:
    done=read_store().get("reviews",{}); rows=[x for x in bank.get("children",[]) if not done.get(x["id"])]
    out.mkdir(parents=True,exist_ok=True); n=math.ceil(len(rows)/batch_size) if rows else 0; batches=[]
    for i in range(n):
        chunk=rows[i*batch_size:(i+1)*batch_size]; pp=out/f"batch-{i+1:02d}-of-{n:02d}.md";rp=out/f"batch-{i+1:02d}-of-{n:02d}.response.md";pp.write_text(prompt(chunk,i+1,n),encoding="utf-8");batches.append({"index":i+1,"ids":[x["id"] for x in chunk],"prompt":str(pp),"response":str(rp)})
    m={"queued":len(rows),"batches":batches};_atomic_json(out/"manifest.json",m);return m


def run(batch_size:int,timeout:int)->dict[str,Any]:
    if socket.gethostname()!=EXPECTED_HOST:raise RuntimeError(f"requires {EXPECTED_HOST}")
    bank=load_bank();ids=[x["id"] for x in bank.get("children",[])];st=StorageSettings.from_env();st.ensure();out=st.run_dir/"reviews"/"idea-discovery-v51-web-gpt";m=prepare(bank,out,batch_size);store=read_store();runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py"
    for b in m["batches"]:
        pp=Path(b["prompt"]);rp=Path(b["response"]);err=""
        for attempt in range(1,4):
            rp.unlink(missing_ok=True);cmd=[sys.executable,str(runner),"Review the attached v5.1 repaired idea batch. Return only JSON.","--file",str(pp),"--slug",f"idea-discovery-v51-r2-{b['index']:02d}-attempt-{attempt}","--timeout",str(timeout),"--output",str(rp)];done=subprocess.run(cmd,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if done.returncode:raise RuntimeError(done.stderr[-3000:] or done.stdout[-3000:])
                payload=extract_json(rp.read_text(encoding="utf-8")); reviews=normalize_response(payload,b["ids"],source_artifact=str(rp));store=update_store(store,reviews,all_ids=ids,attempt_result=f"batch_{b['index']}_completed",attempt_host=socket.gethostname());_atomic_json(DEFAULT_EXTERNAL_JSON,store);write_idea_discovery_v51();break
            except Exception as e:
                err=str(e)
                if attempt<3:time.sleep(45*attempt)
        else:raise RuntimeError(err)
    return write_idea_discovery_v51()


def main(argv:Sequence[str]|None=None)->int:
    ap=argparse.ArgumentParser();ap.add_argument("--run",action="store_true");ap.add_argument("--batch-size",type=int,default=5);ap.add_argument("--timeout",type=int,default=900);args=ap.parse_args(argv);bank=load_bank();st=StorageSettings.from_env();st.ensure();m=prepare(bank,st.run_dir/"reviews"/"idea-discovery-v51-web-gpt",args.batch_size)
    if args.run:print(json.dumps(run(args.batch_size,args.timeout)["summary"],ensure_ascii=False))
    else:print(json.dumps({"children":len(bank.get("children",[])),"queued":m["queued"],"batches":len(m["batches"])},ensure_ascii=False))
    return 0

if __name__=="__main__":raise SystemExit(main())
