#!/usr/bin/env python3
"""R89 content-addressed materialization receipt for B1 Qwen2.5-32B.

Runs only after the exact R86B-authorized Hugging Face snapshot is complete.
It performs no model loading or inference.  The receipt binds both the complete
local tree and the model payload files used by Transformers, with explicit
hashes for config/tokenizer/template/index and all safetensor shards.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
REPO="Qwen/Qwen2.5-32B-Instruct"
REVISION="c53f764956643a675cfff8ad85b3c9e9b3029e06"
EXPECTED_SHARDS=17

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
  for b in iter(lambda:f.read(16*1024*1024),b""):h.update(b)
 return h.hexdigest()
def row(root:pathlib.Path,p:pathlib.Path)->dict[str,Any]:return {"path":str(p.relative_to(root)),"bytes":p.stat().st_size,"sha256":sha(p)}

def build(root:pathlib.Path,authority:dict[str,Any])->dict[str,Any]:
 if not valid(authority):raise RuntimeError("R89-authority-receipt-invalid")
 if authority.get("status")!="R86B_STRONG_MODEL_MATERIALIZATION_HOST_SUBSTITUTED_TO_231_EXECUTION_CLOSED":raise RuntimeError("R89-R86B-status-drift")
 inv=authority.get("scientific_invariants") or {};op=authority.get("operational_change") or {}
 if inv.get("repository")!=REPO or inv.get("revision")!=REVISION or op.get("new_target_root")!=str(root):raise RuntimeError("R89-model-identity-drift")
 if not root.is_dir():raise RuntimeError("R89-root-missing")
 all_files=sorted([p for p in root.rglob("*") if p.is_file()],key=lambda p:str(p.relative_to(root)))
 payload=[p for p in all_files if not str(p.relative_to(root)).startswith(".cache/")]
 shards=sorted(root.glob("model-*-of-*.safetensors"))
 if len(shards)!=EXPECTED_SHARDS:raise RuntimeError(f"R89-shard-count:{len(shards)}")
 required=["config.json","generation_config.json","tokenizer.json","tokenizer_config.json","merges.txt","vocab.json","model.safetensors.index.json"]
 missing=[x for x in required if not (root/x).is_file()]
 if missing:raise RuntimeError(f"R89-required-files-missing:{missing}")
 optional=[x for x in ["chat_template.jinja","LICENSE","README.md"] if (root/x).is_file()]
 full_rows=[row(root,p) for p in all_files];payload_rows=[row(root,p) for p in payload];shard_rows=[row(root,p) for p in shards]
 index=json.loads((root/"model.safetensors.index.json").read_text(encoding="utf-8"));weight_map=index.get("weight_map") or {}
 referenced=sorted(set(str(x) for x in weight_map.values()))
 if referenced!=sorted(p.name for p in shards):raise RuntimeError("R89-index-shard-set-drift")
 out={
  "schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R89-STRONG-MODEL-MATERIALIZATION","recorded_date":"2026-09-06","status":"R89_QWEN25_32B_EXACT_REVISION_MATERIALIZED_HASHED_EXECUTION_STILL_CLOSED","role":"ZERO_INFERENCE_CONTENT_ADDRESSED_STRONG_MODEL_RECEIPT",
  "bindings":{"r86b_materialization_authority_receipt_sha256":authority["receipt_sha256"]},
  "model":{"repository":REPO,"revision":REVISION,"root":str(root),"parameter_scale":"32.5B","quantization":"none","expected_runtime_dtype":"float16"},
  "tree":{"file_count":len(full_rows),"bytes":sum(x["bytes"] for x in full_rows),"rows":full_rows,"rows_sha256":digest(full_rows)},
  "payload":{"file_count":len(payload_rows),"bytes":sum(x["bytes"] for x in payload_rows),"rows":payload_rows,"rows_sha256":digest(payload_rows)},
  "safetensors":{"shard_count":len(shard_rows),"bytes":sum(x["bytes"] for x in shard_rows),"rows":shard_rows,"rows_sha256":digest(shard_rows),"index_sha256":sha(root/"model.safetensors.index.json"),"index_referenced_shards":referenced},
  "critical_files":{x:sha(root/x) for x in required+optional},
  "model_loaded":False,"model_inference_calls":0,
  "authority":{"strong_model_execution":False,"analysis":False,"gpu":False,"paper_claim_change":False},
  "scientific_authority":False,"experiment_authority":False,"gpu_authority":False,
 }
 out["receipt_sha256"]=digest(out);return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=pathlib.Path,required=True);ap.add_argument("--authority",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);a=ap.parse_args();out=build(a.root.resolve(),load(a.authority));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"receipt_sha256":out["receipt_sha256"],"payload_bytes":out["payload"]["bytes"],"shards":out["safetensors"]["shard_count"],"inference_calls":0},sort_keys=True))
if __name__=="__main__":main()
