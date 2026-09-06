#!/usr/bin/env python3
"""R88 fail-closed executor for the frozen B1 R87 12-run strong-scale check.

This runner reuses the frozen R72 P/T renderer and the exact R73 OSInteraction
run_attempt implementation.  It adds only a strong-model-specific manifest,
runtime preflight, and the 12-row R87 schedule.  No analysis is performed here.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,socket,subprocess,sys,urllib.request
from typing import Any

try:
 import failure_memory_semantic_control_r72 as r72
 import failure_memory_semantic_control_r73 as r73
 import failure_memory_memrl_utilization_r47 as r47
 import failure_memory_memrl_ab_identification_r48 as r48
except ImportError:
 from . import failure_memory_semantic_control_r72 as r72
 from . import failure_memory_semantic_control_r73 as r73
 from . import failure_memory_memrl_utilization_r47 as r47
 from . import failure_memory_memrl_ab_identification_r48 as r48

MAX_PREEXPOSURE_ATTEMPTS=3
PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict):raise RuntimeError(f"not-object:{p}")
 return v
def valid(v:dict[str,Any])->bool:return isinstance(v.get("receipt_sha256"),str) and v["receipt_sha256"]==digest({k:x for k,x in v.items() if k!="receipt_sha256"})
def sha(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def append(p:pathlib.Path,row:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
def rows(p:pathlib.Path)->list[dict[str,Any]]:
 return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []

def runtime_preflight(manifest:dict[str,Any],r87:dict[str,Any])->None:
 if not valid(manifest) or not valid(r87):raise RuntimeError("R88-receipt-invalid")
 if manifest.get("status")!="R90_STRONG_RUNTIME_MANIFEST_MATERIALIZED_EXECUTION_STILL_CLOSED":raise RuntimeError("R88-manifest-status-drift")
 b=manifest.get("bindings") or {}
 if b.get("r87_protocol_receipt_sha256")!=r87["receipt_sha256"]:raise RuntimeError("R88-R87-binding-drift")
 if b.get("r88_runner_sha256")!=sha(pathlib.Path(__file__).resolve()):raise RuntimeError("R88-runner-binding-drift")
 e=manifest["execution_manifest"];h=e["host"];s=e["source"]
 if socket.gethostname()!=h["logical_name"]:raise RuntimeError("host-drift")
 if pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve():raise RuntimeError("python-drift")
 root=pathlib.Path(s["checkout"]);head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip();dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
 if head!=s["revision"] or dirty:raise RuntimeError("source-drift")
 split=root/e["confirmatory_units"]["split"]
 if sha(split)!=e["confirmatory_units"]["split_sha256"]:raise RuntimeError("validation-split-drift")
 image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
 if image!=e["runtime_image"]["id"]:raise RuntimeError("runtime-image-drift")
 sm=manifest["strong_model_materialization"];model_root=pathlib.Path(sm["root"])
 if not model_root.is_dir():raise RuntimeError("strong-model-root-missing")
 if sm.get("artifact_manifest_receipt_sha256")!=b.get("r89_materialization_receipt_sha256"):raise RuntimeError("strong-model-receipt-binding-drift")
 base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/")
 with urllib.request.urlopen(base+"/models",timeout=5) as resp:models={str(x.get("id")) for x in json.loads(resp.read().decode()).get("data") or []}
 if e["external_runtime_adapter"]["llm_model_id"] not in models:raise RuntimeError("loopback-route-drift")
 if len(r87["panel"]["schedule"])!=12 or r87["panel"]["trajectory_count"]!=12:raise RuntimeError("R87-schedule-drift")

def authority_check(authority:dict[str,Any],manifest:dict[str,Any],r87:dict[str,Any])->None:
 if not valid(authority):raise RuntimeError("R88-authority-invalid")
 if authority.get("r87_protocol_receipt_sha256")!=r87["receipt_sha256"] or authority.get("runtime_manifest_receipt_sha256")!=manifest["receipt_sha256"]:raise RuntimeError("R88-authority-binding-drift")
 a=authority.get("authority") or {}
 if a.get("strong_model_execution") is not True or a.get("gpu") is not True:raise RuntimeError("R88-execution-not-authorized")
 if any(a.get(k) for k in ["analysis","paper_claim_change","PSMG","L3","qwen_execution","llama_execution"]):raise RuntimeError("R88-authority-too-broad")

def execute(r87:dict[str,Any],r72protocol:dict[str,Any],panel:dict[str,Any],r54:dict[str,Any],manifest:dict[str,Any],outdir:pathlib.Path,resume:bool=False)->None:
 runtime_preflight(manifest,r87);adapter=r47.build_adapter(manifest);records=r73.runtime_records(r72protocol,panel,r54);sched=list(r87["panel"]["schedule"]);root=outdir;root.mkdir(parents=True,exist_ok=True);terminal_path=root/"terminal-arms.jsonl";event_path=root/"attempt-events.jsonl";terminal=rows(terminal_path)
 expected=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in sched];got=[(int(x["stage_ordinal"]),str(x["task_id"]),str(x["arm"])) for x in terminal]
 if got!=expected[:len(got)]:raise RuntimeError("R88-terminal-ledger-not-schedule-prefix")
 if terminal and len(terminal)<len(sched) and not resume:raise RuntimeError("R88-partial-stage-requires-resume")
 events=rows(event_path)
 if len(terminal)<len(sched):
  item=sched[len(terminal)];key=(str(item["task_id"]),str(item["arm"]));ev=[x for x in events if (str(x.get("task_id")),str(x.get("arm")))==key]
  if any(x.get("event")=="TREATMENT_EXPOSURE_DISPATCHED" for x in ev):append(terminal_path,{"stage_ordinal":int(item["stage_ordinal"]),"task_id":key[0],"arm":key[1],"status":"TECHNICAL_MISSING_POST_EXPOSURE_RECOVERED","terminal_success":None,"treatment_exposed":True,"at":r48.now()});terminal=rows(terminal_path)
 for item in sched[len(terminal):]:
  ordinal=int(item["stage_ordinal"]);tid=str(item["task_id"]);arm=str(item["arm"]);ctx=r72.render_contexts(records[tid])[arm];prompt=r73.prompt_for(manifest,ctx);pre_fail=[]
  for attempt in range(1,MAX_PREEXPOSURE_ATTEMPTS+1):
   append(event_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"attempt":attempt,"event":"ATTEMPT_BEGIN","at":r48.now(),"memory_context_sha256":hashlib.sha256(ctx.encode()).hexdigest(),"system_prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest()})
   result=r73.run_attempt(manifest,adapter,tid,arm,prompt,event_path,attempt)
   if result["status"]=="TECHNICAL_FAILURE_PREEXPOSURE":pre_fail.append(result);append(event_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"attempt":attempt,"event":"PREEXPOSURE_FAILURE","at":r48.now(),"error_type":result["error_type"],"error":result["error"]});continue
   ad=root/"arms"/f"{ordinal:04d}-{tid}-{arm}";ad.mkdir(parents=True,exist_ok=False)
   if result["status"]=="COMPLETE":
    tp=ad/"trace.json";tp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");append(terminal_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"COMPLETE","terminal_success":result["terminal_success"],"steps":result["steps"],"first_executable_action":result["first_executable_action"],"first_executable_action_sha256":hashlib.sha256(str(result["first_executable_action"] or "<NONE>").encode()).hexdigest(),"attempt":attempt,"preexposure_failures":len(pre_fail),"treatment_exposed":True,"trace_file":str(tp),"trace_file_sha256":sha(tp),"completed_at":r48.now()});break
   fp=ad/"technical-missing.json";fp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");append(terminal_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"TECHNICAL_MISSING_POST_EXPOSURE","terminal_success":None,"attempt":attempt,"preexposure_failures":len(pre_fail),"treatment_exposed":True,"failure_file":str(fp),"failure_file_sha256":sha(fp),"completed_at":r48.now()});break
  else:append(terminal_path,{"stage_ordinal":ordinal,"task_id":tid,"arm":arm,"status":"TECHNICAL_MISSING_PREEXPOSURE_EXHAUSTED","terminal_success":None,"attempt":MAX_PREEXPOSURE_ATTEMPTS,"preexposure_failures":len(pre_fail),"treatment_exposed":False,"completed_at":r48.now()})

def main():
 ap=argparse.ArgumentParser()
 for x in ["r87","r72-protocol","panel","r54","manifest","authority","output-dir"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
 ap.add_argument("--resume",action="store_true");ap.add_argument("--validate-only",action="store_true");a=ap.parse_args();r87,r72p,panel,r54,manifest,auth=map(load,[a.r87,a.r72_protocol,a.panel,a.r54,a.manifest,a.authority])
 if a.validate_only:runtime_preflight(manifest,r87);authority_check(auth,manifest,r87);print(json.dumps({"status":"R88_STRONG_SCALE_RUNTIME_AUTHORITY_PREFLIGHT_PASS","schedule":12,"analysis_authorized":False},sort_keys=True));return
 authority_check(auth,manifest,r87);execute(r87,r72p,panel,r54,manifest,a.output_dir.resolve(),a.resume);print(json.dumps({"status":"R88_STRONG_SCALE_STAGE_TERMINAL"},sort_keys=True))
if __name__=="__main__":main()
