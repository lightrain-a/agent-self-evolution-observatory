#!/usr/bin/env python3
"""R91 load-only runtime preflight receipt for B1 R87 strong-scale.

Runs after the exact 32B model is materialized and R90 static runtime objects
are frozen.  It may inspect GET /models and /health only.  It sends no benchmark
prompt and creates no task container.  A PASS receipt is required before R92 can
mint the 12-run execution authority.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,socket,subprocess,sys,urllib.request
from typing import Any

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
def get_json(url:str)->dict[str,Any]:
 with urllib.request.urlopen(url,timeout=8) as r:return json.loads(r.read().decode())

def build(manifest:dict[str,Any],load_auth:dict[str,Any],r87:dict[str,Any],r89:dict[str,Any],server:pathlib.Path,runner:pathlib.Path)->dict[str,Any]:
 if not all(valid(x) for x in [manifest,load_auth,r87,r89]):raise RuntimeError("R91-input-receipt-invalid")
 if manifest.get("status")!="R90_STRONG_RUNTIME_MANIFEST_MATERIALIZED_EXECUTION_STILL_CLOSED":raise RuntimeError("R91-manifest-status")
 if load_auth.get("status")!="R90_STRONG_MODEL_GPU_LOAD_AND_ROUTE_PREFLIGHT_ONLY_EXECUTION_CLOSED":raise RuntimeError("R91-load-authority-status")
 a=load_auth.get("authority") or {}
 if a.get("strong_model_load") is not True or a.get("route_preflight") is not True or a.get("strong_model_execution") is not False:raise RuntimeError("R91-load-authority-scope")
 if load_auth.get("runtime_manifest_receipt_sha256")!=manifest["receipt_sha256"] or manifest.get("bindings",{}).get("r89_materialization_receipt_sha256")!=r89["receipt_sha256"]:raise RuntimeError("R91-binding-drift")
 if manifest.get("bindings",{}).get("r87_protocol_receipt_sha256")!=r87["receipt_sha256"]:raise RuntimeError("R91-R87-binding-drift")
 if manifest.get("bindings",{}).get("r88_server_sha256")!=sha(server) or manifest.get("bindings",{}).get("r88_runner_sha256")!=sha(runner):raise RuntimeError("R91-code-binding-drift")
 e=manifest["execution_manifest"];h=e["host"];s=e["source"]
 if socket.gethostname()!=h["logical_name"]:raise RuntimeError("R91-host-drift")
 if pathlib.Path(sys.executable).resolve()!=pathlib.Path(h["python"]).resolve():raise RuntimeError("R91-python-drift")
 root=pathlib.Path(s["checkout"]);head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip();dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
 if head!=s["revision"] or dirty:raise RuntimeError("R91-source-drift")
 split=root/e["confirmatory_units"]["split"]
 if sha(split)!=e["confirmatory_units"]["split_sha256"]:raise RuntimeError("R91-split-drift")
 image=subprocess.check_output(["docker","image","inspect",e["runtime_image"]["execution_tag"],"--format","{{.Id}}"],text=True).strip()
 if image!=e["runtime_image"]["id"]:raise RuntimeError("R91-image-drift")
 base=e["external_runtime_adapter"]["loopback_base_url"].rstrip("/");models=get_json(base+"/models");health=get_json(base.replace('/v1','')+"/health")
 ids={str(x.get("id")) for x in models.get("data") or []};mid=e["external_runtime_adapter"]["llm_model_id"]
 if mid not in ids or health.get("status")!="ok" or health.get("llm")!=mid:raise RuntimeError("R91-loopback-route-drift")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R91-STRONG-RUNTIME-PREFLIGHT","recorded_date":"2026-09-06","status":"R91_STRONG_RUNTIME_PREFLIGHT_PASS_ZERO_BENCHMARK_CALLS","role":"POST_MODEL_LOAD_PRE_TREATMENT_RUNTIME_EQUIVALENCE_RECEIPT","bindings":{"r87_protocol_receipt_sha256":r87["receipt_sha256"],"r89_materialization_receipt_sha256":r89["receipt_sha256"],"r90_runtime_manifest_receipt_sha256":manifest["receipt_sha256"],"r90_load_authority_receipt_sha256":load_auth["receipt_sha256"],"r88_server_sha256":sha(server),"r88_runner_sha256":sha(runner)},"checks":{"hostname":socket.gethostname(),"python":str(pathlib.Path(sys.executable).resolve()),"source_revision":head,"source_clean":True,"validation_split_sha256":sha(split),"docker_image_id":image,"model_route":mid,"health":"ok","schedule_rows":len(r87["panel"]["schedule"]),"materialization_payload_sha256":r89["payload"]["rows_sha256"]},"benchmark_model_calls":0,"treatment_exposures":0,"task_containers_created":0,"strong_model_loaded":True,"authority":{"strong_model_execution":False,"analysis":False,"paper_claim_change":False},"scientific_authority":False,"experiment_authority":False,"gpu_authority":False};out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser()
 for x in ["manifest","load-authority","r87","r89","server","runner","output"]:p.add_argument("--"+x,type=pathlib.Path,required=True)
 a=p.parse_args();out=build(load(a.manifest),load(a.load_authority),load(a.r87),load(a.r89),a.server,a.runner);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"benchmark_calls":0},sort_keys=True))
if __name__=="__main__":main()
