from __future__ import annotations
import argparse,json,math,socket,subprocess,sys,time
from pathlib import Path
from typing import Any,Sequence
from .config import PROJECT_ROOT,StorageSettings
from .iclr_external_review import EXPECTED_HOST,_atomic_json,extract_json,normalize_response,update_store
from .idea_discovery_v52 import DEFAULT_EXTERNAL_JSON,DEFAULT_JSON,build_idea_discovery_v52,write_idea_discovery_v52
REVIEWER="agent-project-web-gpt-idea-discovery-v52-area-chair"
def bank()->dict[str,Any]:return json.loads(DEFAULT_JSON.read_text(encoding="utf-8")) if DEFAULT_JSON.exists() else build_idea_discovery_v52()
def prompt(rows:Sequence[dict[str,Any]],i:int,n:int)->str:
 s={"reviewer":REVIEWER,"review_date":"YYYY-MM-DD","ideas":[{"idea_id":"exact id","verdict":"pass|revise|block","confidence":"high|medium|low","finding":"English","finding_zh":"中文","required_action":"English","required_action_zh":"中文","direct_collision":{"status":"none|partial|direct|unknown","closest_work":[],"surviving_difference":""},"strongest_baseline":"","decisive_pilot":"","stop_rule":"","unknowns":[]}]}
 return f"""# Independent v5.2 second-order repair audit — {i}/{n}
Act as a strict ICLR area chair. These children repair a v5.1 REVISE after two prior reviewer vectors. PASS only when the second-order material change defeats the previously stated simplest equivalent method, creates a persistent frozen operator, has independent truth, and survives official-source collision search through 2026-08-01. REVISE if one material boundary remains; BLOCK if reducible/collided/cosmetic. Do not reward accumulated complexity. Return only JSON.\nSchema:\n```json\n{json.dumps(s,ensure_ascii=False,indent=2)}\n```\nChildren:\n```json\n{json.dumps(rows,ensure_ascii=False,indent=2)}\n```\n"""
def store()->dict[str,Any]:
 if DEFAULT_EXTERNAL_JSON.exists():
  p=json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"));
  if isinstance(p,dict) and isinstance(p.get("reviews"),dict):return p
 return {"schema_version":"1.0","reviews":{},"status":{}}
def run(bs:int,timeout:int)->dict[str,Any]:
 if socket.gethostname()!=EXPECTED_HOST:raise RuntimeError(f"requires {EXPECTED_HOST}")
 b=bank();ids=[x["id"] for x in b.get("children",[])];done=store().get("reviews",{});rows=[x for x in b.get("children",[]) if not done.get(x["id"])];st=StorageSettings.from_env();st.ensure();out=st.run_dir/"reviews"/"idea-discovery-v52-web-gpt";out.mkdir(parents=True,exist_ok=True);runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py";n=math.ceil(len(rows)/bs) if rows else 0;st0=store()
 for j in range(n):
  ch=rows[j*bs:(j+1)*bs];pp=out/f"batch-{j+1:02d}-of-{n:02d}.md";rp=out/f"batch-{j+1:02d}-of-{n:02d}.response.md";pp.write_text(prompt(ch,j+1,n),encoding="utf-8");err=""
  for a in range(1,4):
   rp.unlink(missing_ok=True);cmd=[sys.executable,str(runner),"Review the attached v5.2 repaired idea batch. Return only JSON.","--file",str(pp),"--slug",f"idea-v52-r2-{j+1:02d}-attempt-{a}","--timeout",str(timeout),"--output",str(rp)];p=subprocess.run(cmd,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
   try:
    if p.returncode:raise RuntimeError(p.stderr[-2000:] or p.stdout[-2000:])
    rev=normalize_response(extract_json(rp.read_text(encoding="utf-8")),[x["id"] for x in ch],source_artifact=str(rp));st0=update_store(st0,rev,all_ids=ids,attempt_result=f"batch_{j+1}_completed",attempt_host=socket.gethostname());_atomic_json(DEFAULT_EXTERNAL_JSON,st0);write_idea_discovery_v52();break
   except Exception as e:
    err=str(e)
    if a<3:time.sleep(45*a)
  else:raise RuntimeError(err)
 return write_idea_discovery_v52()
def main(argv:Sequence[str]|None=None)->int:
 ap=argparse.ArgumentParser();ap.add_argument("--run",action="store_true");ap.add_argument("--batch-size",type=int,default=6);ap.add_argument("--timeout",type=int,default=900);a=ap.parse_args(argv);b=bank();pending=sum(not store().get("reviews",{}).get(x["id"]) for x in b.get("children",[]))
 if a.run:print(json.dumps(run(a.batch_size,a.timeout)["summary"],ensure_ascii=False))
 else:print(json.dumps({"children":len(b.get("children",[])),"pending":pending},ensure_ascii=False))
 return 0
if __name__=="__main__":raise SystemExit(main())
