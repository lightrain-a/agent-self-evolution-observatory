from __future__ import annotations

import argparse, json, math, socket, subprocess, sys, tempfile, time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json
from .idea_discovery_v5 import DEFAULT_EXTERNAL_JSON as V5_REVIEWS, DEFAULT_JSON as V5_JSON
from .idea_discovery_v51 import DEFAULT_PROPOSALS_JSON, write_idea_discovery_v51

GENERATOR = "agent-project-web-gpt-v51-repair-generator"


def load_inputs() -> tuple[dict[str,Any],dict[str,Any]]:
    bank=json.loads(V5_JSON.read_text(encoding="utf-8")); reviews=json.loads(V5_REVIEWS.read_text(encoding="utf-8")) if V5_REVIEWS.exists() else {"reviews":{}}
    return bank,reviews


def parents_ready(bank: dict[str,Any], reviews: dict[str,Any]) -> list[dict[str,Any]]:
    by={x["id"]:x for x in bank.get("finalists",[])}; out=[]
    for idea_id, items in (reviews.get("reviews") or {}).items():
        if not items or items[-1].get("verdict")!="revise" or idea_id not in by: continue
        x=dict(by[idea_id]); x["review"]=items[-1]; out.append(x)
    return out


def packet(x:dict[str,Any])->dict[str,Any]:
    r=x["review"]
    return {"parent_id":x["id"],"title":x["title"],"problem":x["problem"],"mechanism":x["exact_mechanism"],"update_surface":x["update_surface"],"components":x.get("components",[]),"required_action":r.get("required_action"),"required_action_zh":r.get("required_action_zh"),"simplification_challenge":r.get("simplification_challenge",{}),"direct_collision":r.get("direct_collision",{}),"surviving_difference":(r.get("direct_collision") or {}).get("surviving_difference","")}


def prompt(rows:Sequence[dict[str,Any]],idx:int,total:int)->str:
    schema={"generator":GENERATOR,"children":[{"id":"new-kebab-id","parent_id":"exact parent id","repair_source":"required-action|simplification-challenge|surviving-boundary","title":{"zh":"","en":""},"problem":{"zh":"","en":""},"changed_assumption":{"zh":"","en":""},"exact_mechanism":{"zh":"","en":""},"update_surface":"exact persistent object","learning_signal":{"zh":"","en":""},"independent_ground_truth":{"zh":"","en":""},"simplest_baseline":{"zh":"","en":""},"decisive_pilot":{"zh":"","en":""},"stop_condition":{"zh":"","en":""},"what_is_inherited":{"zh":"","en":""},"material_change":{"zh":"","en":""}}]}
    return f"""# Idea Discovery v5.1 targeted repair generation — batch {idx}/{total}

Act as a method inventor, not a reviewer. For each supplied v5 REVISE parent, generate ONE materially repaired child by following the actual reviewer vector. A second child is allowed only when it changes a different scientific assumption, not wording.

Rules:
- Preserve the real problem unless the reviewer explicitly says it is invalid.
- Change the weakest mechanism/object/supervision identified in `required_action` or simplification challenge.
- Do not resubmit the parent under a new name.
- Do not add complexity unless each new component closes a distinct failure path.
- The child must create or modify a persistent object that changes frozen future behavior.
- Name the strongest capacity-matched simpler method and make the decisive pilot distinguish the child from it.
- Use the surviving difference from the review when one exists.
- Keep the method executable with public/open assets and a low-resource P0/P1 where possible.
- Return bilingual fields.

Return only JSON matching:
```json
{json.dumps(schema,ensure_ascii=False,indent=2)}
```
Parents:
```json
{json.dumps([packet(x) for x in rows],ensure_ascii=False,indent=2)}
```
"""


def read_store()->dict[str,Any]:
    if DEFAULT_PROPOSALS_JSON.exists():
        p=json.loads(DEFAULT_PROPOSALS_JSON.read_text(encoding="utf-8")); return p if isinstance(p,dict) else {"children":[]}
    return {"schema_version":"1.0","generator":GENERATOR,"children":[]}


def normalize(payload:dict[str,Any],parents:set[str])->list[dict[str,Any]]:
    rows=payload.get("children",[]); out=[]
    for x in rows:
        if not isinstance(x,dict) or x.get("parent_id") not in parents: continue
        if not x.get("id") or x.get("id")==x.get("parent_id"): continue
        out.append(x)
    covered={x["parent_id"] for x in out}; missing=parents-covered
    if missing: raise ValueError("missing repaired parents: "+", ".join(sorted(missing)))
    return out


def save_children(new:list[dict[str,Any]])->None:
    store=read_store(); by={x["id"]:x for x in store.get("children",[]) if isinstance(x,dict)}
    for x in new: by[x["id"]]=x
    store.update({"schema_version":"1.0","generator":GENERATOR,"children":list(by.values())}); _atomic_json(DEFAULT_PROPOSALS_JSON,store); write_idea_discovery_v51()


def run(batch_size:int,timeout:int)->dict[str,Any]:
    if socket.gethostname()!=EXPECTED_HOST: raise RuntimeError(f"requires {EXPECTED_HOST}")
    bank,reviews=load_inputs(); parents=parents_ready(bank,reviews); existing={x.get("parent_id") for x in read_store().get("children",[]) if isinstance(x,dict)}; parents=[x for x in parents if x["id"] not in existing]
    st=StorageSettings.from_env(); st.ensure(); out=st.run_dir/"reviews"/"idea-discovery-v51-generation"; out.mkdir(parents=True,exist_ok=True)
    runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py"; total=math.ceil(len(parents)/batch_size) if parents else 0
    for i in range(total):
        chunk=parents[i*batch_size:(i+1)*batch_size]; pp=out/f"batch-{i+1:02d}-of-{total:02d}.md"; rp=out/f"batch-{i+1:02d}-of-{total:02d}.response.md"; pp.write_text(prompt(chunk,i+1,total),encoding="utf-8")
        err=""
        for attempt in range(1,4):
            rp.unlink(missing_ok=True); cmd=[sys.executable,str(runner),"Generate the attached targeted v5.1 repair children. Return only JSON.","--file",str(pp),"--slug",f"idea-discovery-v51-gen-{i+1:02d}-attempt-{attempt}","--timeout",str(timeout),"--output",str(rp)]
            done=subprocess.run(cmd,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if done.returncode: raise RuntimeError(done.stderr[-3000:] or done.stdout[-3000:])
                payload=extract_json(rp.read_text(encoding="utf-8")); children=normalize(payload,{x["id"] for x in chunk}); save_children(children); break
            except Exception as e:
                err=str(e)
                if attempt<3: time.sleep(45*attempt)
        else: raise RuntimeError(err)
    return write_idea_discovery_v51()


def main(argv:Sequence[str]|None=None)->int:
    ap=argparse.ArgumentParser();ap.add_argument("--run",action="store_true");ap.add_argument("--batch-size",type=int,default=4);ap.add_argument("--timeout",type=int,default=900);args=ap.parse_args(argv)
    bank,reviews=load_inputs(); parents=parents_ready(bank,reviews); existing={x.get("parent_id") for x in read_store().get("children",[]) if isinstance(x,dict)}; pending=[x for x in parents if x["id"] not in existing]
    if args.run: print(json.dumps(run(args.batch_size,args.timeout)["summary"],ensure_ascii=False))
    else: print(json.dumps({"revise_parents":len(parents),"already_repaired":len(parents)-len(pending),"pending":len(pending)},ensure_ascii=False))
    return 0

if __name__=="__main__": raise SystemExit(main())
