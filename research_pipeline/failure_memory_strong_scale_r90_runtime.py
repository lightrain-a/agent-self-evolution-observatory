#!/usr/bin/env python3
"""R90 static runtime manifest + load-only authority for B1 strong-scale.

Consumes the complete R89 model materialization receipt.  It derives the strong
runtime from the already-used R81 Qwen manifest, explicitly materializes the
66-task confirmatory split, swaps only the LLM identity/root and chat-loopback
server, and grants GPU model-load / route-preflight authority only.  Benchmark
execution remains closed.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
SERVER_ID="B1-Qwen2.5-32B-Instruct-r87"
LOOPBACK="http://127.0.0.1:18145/v1"
VAL_SHA="1804781d7e768e74cc9f9038fcdfcf373ff34d4edc668382d6d18cbf74f856d6"

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

def build(parent:dict[str,Any],r87:dict[str,Any],r89:dict[str,Any],panel:dict[str,Any],server:pathlib.Path,runner:pathlib.Path)->tuple[dict[str,Any],dict[str,Any]]:
 if not all(valid(x) for x in [parent,r87,r89,panel]):raise RuntimeError("R90-input-receipt-invalid")
 if r89.get("status")!="R89_QWEN25_32B_EXACT_REVISION_MATERIALIZED_HASHED_EXECUTION_STILL_CLOSED":raise RuntimeError("R90-R89-not-complete")
 if r87.get("status")!="R87_STRONG_SCALE_PROTOCOL_FROZEN_EXECUTION_CLOSED":raise RuntimeError("R90-R87-drift")
 ids=[str(x) for x in panel.get("representative_ids") or []]
 if len(ids)!=66:raise RuntimeError("R90-panel-cardinality-drift")
 m=copy.deepcopy(parent);e=m["execution_manifest"]
 e["confirmatory_units"]={"split":"data/llb/os_interaction_val.json","split_sha256":VAL_SHA,"cluster_rule":"exact sorted skill_list signature","selected_cluster_count":66,"representative_ids":ids,"representative_ids_sha256":panel["representative_ids_sha256"],"statistical_n":66}
 llm=e["models"]["llm"];llm.update({"family":"Qwen2.5-32B-Instruct","root":r89["model"]["root"],"artifact_manifest_sha256":r89["payload"]["rows_sha256"],"file_count":r89["payload"]["file_count"],"bytes":r89["payload"]["bytes"],"device":"cuda:0","temperature":0.0,"max_new_tokens":512,"external_api":False,"quantization":"none","runtime_dtype":"float16"})
 e["external_runtime_adapter"]={"provider_path":"research_pipeline/failure_memory_memrl_local_runtime_r43.py","provider_sha256":"32762bafdf0bb4274c6f3b521ceb3e8c008178361503c320691543d51007a3f2","loopback_server_path":"research_pipeline/failure_memory_strong_scale_r88_server.py","loopback_server_sha256":sha(server),"loopback_base_url":LOOPBACK,"llm_model_id":SERVER_ID,"network_scope":"loopback-only","external_provider_calls":0,"retrieval_recomputed":False,"embedding_route_required":False,"modifies_pinned_memrl_checkout":False}
 m["schema_version"]="1.0";m["status"]="R90_STRONG_RUNTIME_MANIFEST_MATERIALIZED_EXECUTION_STILL_CLOSED";m["role"]="R87_STRONG_SCALE_RUNTIME_MANIFEST";m["parent_qwen_manifest_receipt_sha256"]=parent["receipt_sha256"]
 m["strong_model_materialization"]={"root":r89["model"]["root"],"artifact_manifest_receipt_sha256":r89["receipt_sha256"],"payload_rows_sha256":r89["payload"]["rows_sha256"],"safetensor_rows_sha256":r89["safetensors"]["rows_sha256"],"payload_bytes":r89["payload"]["bytes"],"model_loaded":False,"model_inference_calls":0}
 m["bindings"]={"r87_protocol_receipt_sha256":r87["receipt_sha256"],"r89_materialization_receipt_sha256":r89["receipt_sha256"],"r88_server_sha256":sha(server),"r88_runner_sha256":sha(runner),"r68_panel_receipt_sha256":panel["receipt_sha256"]}
 m["scientific_authority"]=False;m["experiment_authority"]=False;m["gpu_authority"]=False
 m["receipt_sha256"]=digest({k:v for k,v in m.items() if k!="receipt_sha256"})
 a={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R90-STRONG-MODEL-LOAD-PREFLIGHT-AUTHORITY","recorded_date":"2026-09-06","status":"R90_STRONG_MODEL_GPU_LOAD_AND_ROUTE_PREFLIGHT_ONLY_EXECUTION_CLOSED","role":"LOAD_ONLY_NO_TASK_EXPOSURE_AUTHORITY","r87_protocol_receipt_sha256":r87["receipt_sha256"],"runtime_manifest_receipt_sha256":m["receipt_sha256"],"r89_materialization_receipt_sha256":r89["receipt_sha256"],"authority":{"strong_model_load":True,"route_preflight":True,"gpu":True,"strong_model_execution":False,"analysis":False,"qwen_execution":False,"llama_execution":False,"paper_claim_change":False,"PSMG":False,"L3":False},"allowed_action":"start R88 loopback server and verify /models/health only; do not send benchmark prompts","strong_model_outcomes_observed_when_created":0,"scientific_authority":False,"experiment_authority":False,"gpu_authority":True};a["receipt_sha256"]=digest(a)
 return m,a

def main():
 ap=argparse.ArgumentParser()
 for x in ["parent","r87","r89","panel","server","runner","manifest-output","load-authority-output"]:ap.add_argument("--"+x,type=pathlib.Path,required=True)
 a=ap.parse_args();m,au=build(load(a.parent),load(a.r87),load(a.r89),load(a.panel),a.server,a.runner);a.manifest_output.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");a.load_authority_output.write_text(json.dumps(au,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"manifest_receipt_sha256":m["receipt_sha256"],"load_authority_receipt_sha256":au["receipt_sha256"],"execution":False},sort_keys=True))
if __name__=="__main__":main()
