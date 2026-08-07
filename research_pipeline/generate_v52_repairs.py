from __future__ import annotations

import argparse,json,math,socket,subprocess,sys,time
from pathlib import Path
from typing import Any,Sequence
from .config import PROJECT_ROOT,StorageSettings
from .iclr_external_review import EXPECTED_HOST,_atomic_json,extract_json
from .idea_discovery_v51 import DEFAULT_EXTERNAL_JSON as PARENT_REVIEWS,DEFAULT_JSON as PARENT_JSON
from .idea_discovery_v52 import DEFAULT_PROPOSALS_JSON,write_idea_discovery_v52


def _load(path:Path)->dict[str,Any]:return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
def parents()->list[dict[str,Any]]:
    bank=_load(PARENT_JSON);reviews=_load(PARENT_REVIEWS).get("reviews",{});by={x["id"]:x for x in bank.get("children",[])};out=[]
    for i,rs in reviews.items():
        if rs and rs[-1].get("verdict")=="revise" and i in by:
            x=dict(by[i]);x["review"]=rs[-1];out.append(x)
    return out

def packet(x:dict[str,Any])->dict[str,Any]:
    r=x["review"];return {"parent_id":x["id"],"title":x.get("title"),"mechanism":x.get("exact_mechanism"),"changed_assumption":x.get("changed_assumption"),"required_action":r.get("required_action"),"required_action_zh":r.get("required_action_zh"),"simplification_challenge":r.get("simplification_challenge",{}),"surviving_difference":(r.get("direct_collision") or {}).get("surviving_difference","")}
def prompt(rows:Sequence[dict[str,Any]],i:int,n:int)->str:
    schema={"children":[{"id":"new-id","parent_id":"exact parent","repair_source":"v51-review-vector","title":{"zh":"","en":""},"changed_assumption":{"zh":"","en":""},"exact_mechanism":{"zh":"","en":""},"update_surface":"","learning_signal":{"zh":"","en":""},"independent_ground_truth":{"zh":"","en":""},"simplest_baseline":{"zh":"","en":""},"decisive_pilot":{"zh":"","en":""},"stop_condition":{"zh":"","en":""},"material_change":{"zh":"","en":""}}]}
    return f"""# v5.2 second-order targeted repair — batch {i}/{n}
Generate exactly one materially distinct child for every supplied v5.1 REVISE. Follow the second reviewer vector, not the original parent wording. The child must specifically defeat the stated simplest equivalent method. Do not add generic complexity. Change the learned object, supervision, algebra, interaction structure, or crossed experiment exactly where required. BLOCK parents are absent and must not be recreated. Require frozen future behavior and independent truth. Return bilingual fields and only JSON.
Schema:\n```json\n{json.dumps(schema,ensure_ascii=False,indent=2)}\n```\nParents:\n```json\n{json.dumps([packet(x) for x in rows],ensure_ascii=False,indent=2)}\n```\n"""
def store()->dict[str,Any]:
    p=_load(DEFAULT_PROPOSALS_JSON);return p if isinstance(p,dict) else {"children":[]}
def save(new:list[dict[str,Any]])->None:
    s=store();by={x["id"]:x for x in s.get("children",[]) if isinstance(x,dict)}
    for x in new:by[x["id"]]=x
    s={"schema_version":"1.0","children":list(by.values())};_atomic_json(DEFAULT_PROPOSALS_JSON,s);write_idea_discovery_v52()
def normalize(p:dict[str,Any],ids:set[str])->list[dict[str,Any]]:
    rows=[x for x in p.get("children",[]) if isinstance(x,dict) and x.get("parent_id") in ids and x.get("id") and x.get("id")!=x.get("parent_id")];missing=ids-{x["parent_id"] for x in rows}
    if missing:raise ValueError("missing parents: "+",".join(sorted(missing)))
    return rows
def run(batch_size:int,timeout:int)->dict[str,Any]:
    if socket.gethostname()!=EXPECTED_HOST:raise RuntimeError(f"requires {EXPECTED_HOST}")
    ps=parents();existing={x.get("parent_id") for x in store().get("children",[]) if isinstance(x,dict)};ps=[x for x in ps if x["id"] not in existing];st=StorageSettings.from_env();st.ensure();out=st.run_dir/"reviews"/"idea-discovery-v52-generation";out.mkdir(parents=True,exist_ok=True);runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py";n=math.ceil(len(ps)/batch_size) if ps else 0
    for j in range(n):
        chunk=ps[j*batch_size:(j+1)*batch_size];pp=out/f"batch-{j+1:02d}-of-{n:02d}.md";rp=out/f"batch-{j+1:02d}-of-{n:02d}.response.md";pp.write_text(prompt(chunk,j+1,n),encoding="utf-8");err=""
        for a in range(1,4):
            rp.unlink(missing_ok=True);cmd=[sys.executable,str(runner),"Generate the attached v5.2 targeted children. Return only JSON.","--file",str(pp),"--slug",f"idea-v52-gen-{j+1:02d}-attempt-{a}","--timeout",str(timeout),"--output",str(rp)];done=subprocess.run(cmd,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if done.returncode:raise RuntimeError(done.stderr[-2000:] or done.stdout[-2000:]);
                children=normalize(extract_json(rp.read_text(encoding="utf-8")),{x["id"] for x in chunk});save(children);break
            except Exception as e:
                err=str(e)
                if a<3:time.sleep(45*a)
        else:raise RuntimeError(err)
    return write_idea_discovery_v52()
def main(argv:Sequence[str]|None=None)->int:
    ap=argparse.ArgumentParser();ap.add_argument("--run",action="store_true");ap.add_argument("--batch-size",type=int,default=6);ap.add_argument("--timeout",type=int,default=900);args=ap.parse_args(argv);ps=parents();existing={x.get("parent_id") for x in store().get("children",[]) if isinstance(x,dict)}
    if args.run:print(json.dumps(run(args.batch_size,args.timeout)["summary"],ensure_ascii=False))
    else:print(json.dumps({"revise_parents":len(ps),"pending":sum(x["id"] not in existing for x in ps)},ensure_ascii=False))
    return 0
if __name__=="__main__":raise SystemExit(main())
