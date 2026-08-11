from __future__ import annotations

import argparse, hashlib, importlib.util, json, os, site
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TRACE_CONTRACT={
 "schema_version":"2.0",
 "wrapper_required":["role","trace"],
 "trace_required":["task_id","task_goal","task_family","initial_observation","observations","actions","raw_choices","success","steps","model_calls"],
 "recommended":["admissible_actions","failure_location","update_activation","invalid_actions","score","seed","model_hash","code_hash","environment_hash"],
 "persistence":"append-only-jsonl",
}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def _atomic(p:Path,row:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_suffix(p.suffix+".tmp")
 t.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 os.replace(t,p)

def validate_trace_record(row:dict[str,Any])->list[str]:
 errors=[]
 for key in TRACE_CONTRACT["wrapper_required"]:
  if key not in row: errors.append(f"wrapper-missing:{key}")
 trace=row.get("trace") or {}
 if not isinstance(trace,dict): return errors+["trace-not-object"]
 for key in TRACE_CONTRACT["trace_required"]:
  if key not in trace: errors.append(f"trace-missing:{key}")
 for key in ("observations","actions","raw_choices"):
  if key in trace and not isinstance(trace.get(key),list): errors.append(f"trace-not-list:{key}")
 return errors

def validate_raw_trace_file(path:Path)->dict[str,Any]:
 if not path.exists():
  return {"schema_version":"2.0","status":"fail","pass":False,"path":str(path),"rows":0,"invalid_rows":0,"errors":["raw-traces-missing"],"contract":TRACE_CONTRACT}
 rows=invalid=0; examples=[]
 with path.open("r",encoding="utf-8") as handle:
  for line_no,line in enumerate(handle,1):
   if not line.strip(): continue
   rows+=1
   try: obj=json.loads(line); errs=validate_trace_record(obj if isinstance(obj,dict) else {})
   except json.JSONDecodeError: errs=["invalid-json"]
   if errs:
    invalid+=1
    if len(examples)<10: examples.append({"line":line_no,"errors":errs})
 ok=rows>0 and invalid==0
 return {"schema_version":"2.0","status":"pass" if ok else "fail","pass":ok,"path":str(path),"rows":rows,"invalid_rows":invalid,"examples":examples,"sha256":_sha(path),"contract":TRACE_CONTRACT}

def pre_model_load_audit(idea_id:str,stage:str,config_path:Path,model_path:Path,alfworld_data:Path,extra_pythonpath:Path,output_dir:Path,source_files:Iterable[Path]=())->dict[str,Any]:
 blockers=[]
 existing=list(output_dir.iterdir()) if output_dir.exists() else []
 allowed_existing={"pre-model-load-audit.json","frozen-config.json","pre-experiment-card.json","governance-stage-contract.json"}
 unexpected=[p.name for p in existing if p.name not in allowed_existing]
 if unexpected: blockers.append("output-dir-not-empty:"+",".join(sorted(unexpected)[:8]))
 model_files=("config.json","tokenizer.json","model.safetensors.index.json")
 if not model_path.is_dir() or any(not (model_path/name).exists() for name in model_files): blockers.append("model-identity-files-missing")
 if not config_path.exists(): blockers.append("frozen-config-missing")
 if not extra_pythonpath.exists(): blockers.append("extra-pythonpath-missing")
 else: site.addsitedir(str(extra_pythonpath))
 required_data=("json_2.1.1/train","json_2.1.1/valid_seen","json_2.1.1/valid_unseen","logic/alfred.pddl","logic/alfred.twl2")
 if any(not (alfworld_data/rel).exists() for rel in required_data): blockers.append("alfworld-data-missing")
 modules={name:importlib.util.find_spec(name) is not None for name in ("torch","transformers","alfworld","textworld")}
 blockers.extend(f"python-module-missing:{name}" for name,ok in modules.items() if not ok)
 source_hashes={}
 for path in source_files:
  if not path.exists(): blockers.append(f"source-missing:{path}")
  else: source_hashes[str(path)]=_sha(path)
 ids=[config_path,model_path/"config.json",model_path/"tokenizer.json",model_path/"model.safetensors.index.json",alfworld_data/"logic/alfred.pddl",alfworld_data/"logic/alfred.twl2"]
 runtime_blocked=any(x.startswith("python-module-missing:") or x=="alfworld-data-missing" for x in blockers)
 failure_kind=None if not blockers else ("RUNTIME_ERROR" if runtime_blocked else "IMPLEMENTATION_ERROR")
 payload={
  "schema_version":"2.0","idea_id":idea_id,"stage":stage,
  "status":"PASS_PRE_MODEL_LOAD" if not blockers else "BLOCK_PRE_MODEL_LOAD","pass":not blockers,"failure_kind":failure_kind,
  "created_at":_now(),"blockers":blockers,"modules":modules,"source_sha256":source_hashes,
  "identity_sha256":{str(path):_sha(path) for path in ids if path.exists()},"output_dir":str(output_dir),
  "trace_contract":TRACE_CONTRACT,"scientific_result_available":False,
 }
 output_dir.mkdir(parents=True,exist_ok=True)
 _atomic(output_dir/"pre-model-load-audit.json",payload)
 return payload

def main()->int:
 parser=argparse.ArgumentParser(description="Pre-model-load audit")
 sub=parser.add_subparsers(dest="command",required=True)
 pre=sub.add_parser("prelaunch")
 for name in ("idea-id","stage","config","model-path","alfworld-data","extra-pythonpath","output-dir"):
  pre.add_argument("--"+name,required=True)
 pre.add_argument("--source",action="append",default=[])
 args=parser.parse_args()
 row=pre_model_load_audit(args.idea_id,args.stage,Path(args.config),Path(args.model_path),Path(args.alfworld_data),Path(args.extra_pythonpath),Path(args.output_dir),[Path(x) for x in args.source])
 print(json.dumps(row,ensure_ascii=False))
 return 0 if row["pass"] else 2

if __name__=="__main__": raise SystemExit(main())
