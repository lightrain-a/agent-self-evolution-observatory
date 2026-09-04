#!/usr/bin/env python3
"""R70 zero-model tokenizer-footprint audit for B1 semantic-control metadata.

This script verifies that the revised explicit-field arms P/T/S use the same
serialized schema, string value type, and identical token count under both
frozen executor tokenizers for every eligible R70 unit. It performs no model
inference and observes no task outcome.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, random
from typing import Any

PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
FIELD="source_outcome_status"
CODES={"success":"S","failure":"F","unknown":"U"}
PREFIX="[Retrieved Memory Context]\n[Source outcome codes: S=success, F=failure, U=unknown]\n"
PANEL_IDS_SHA="7c2b84aee347faba6d369abb403eb3a25afb164b8f5c6800ba867c25d1017187"
SHUFFLE_SEED="B1-R70-SHUFFLE-20260904"


def load(p:pathlib.Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding="utf-8"));
 if not isinstance(v,dict): raise RuntimeError(f"not-object:{p}")
 return v

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def ids_hash(xs:list[str])->str:return hashlib.sha256("\n".join(xs).encode()).hexdigest()

def eligible_rows(r54:dict[str,Any],panel:dict[str,Any])->list[dict[str,Any]]:
 rows=[r for r in r54.get("rows") or [] if r.get("has_eligible_frozen_retrieval") is True][40:]
 ids=[str(r["validation_task_id"]) for r in rows]
 if len(ids)!=66 or ids_hash(ids)!=PANEL_IDS_SHA or ids!=[str(x) for x in panel.get("representative_ids") or []]: raise RuntimeError("panel-order-drift")
 return rows

def selected(row:dict[str,Any])->list[dict[str,Any]]:
 out=[s for s in row.get("selected") or [] if s.get("eligible") is True]
 if not out or any(type(s.get("source_outcome_success")) is not bool or not str(s.get("content") or "") for s in out): raise RuntimeError(f"bad-selected:{row.get('validation_task_id')}")
 return out

def truthful_codes(sel:list[dict[str,Any]])->list[str]:return [CODES["success"] if s["source_outcome_success"] else CODES["failure"] for s in sel]
def shuffled_codes(tid:str,truth:list[str])->list[str]|None:
 if len(set(truth))<2:return None
 rng=random.Random(int(hashlib.sha256(f"{SHUFFLE_SEED}|{tid}".encode()).hexdigest()[:16],16));cand=truth[:]
 for _ in range(1024):
  rng.shuffle(cand)
  if cand!=truth: break
 if cand==truth or sorted(cand)!=sorted(truth): raise RuntimeError(f"shuffle-failed:{tid}")
 return cand

def render(sel:list[dict[str,Any]],codes:list[str])->str:
 rows=[{"position":i,"content":str(s["content"]),FIELD:code} for i,(s,code) in enumerate(zip(sel,codes))]
 return PREFIX+json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def build(r54_path:pathlib.Path,panel_path:pathlib.Path,qwen_tokenizer:pathlib.Path,llama_tokenizer:pathlib.Path)->dict[str,Any]:
 from transformers import AutoTokenizer
 r54,panel=load(r54_path),load(panel_path);rows=eligible_rows(r54,panel)
 toks={"Qwen2.5-7B-Instruct":AutoTokenizer.from_pretrained(str(qwen_tokenizer),local_files_only=True),"Meta-Llama-3.1-8B-Instruct":AutoTokenizer.from_pretrained(str(llama_tokenizer),local_files_only=True)}
 per=[];mixed=0
 for row in rows:
  tid=str(row["validation_task_id"]);sel=selected(row);truth=truthful_codes(sel);shuf=shuffled_codes(tid,truth);mixed+=int(shuf is not None)
  ctx={"P_neutral":render(sel,[CODES["unknown"]]*len(sel)),"T_truthful":render(sel,truth)}
  if shuf is not None:ctx["S_shuffled"]=render(sel,shuf)
  counts={};hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in ctx.items()}
  for model,tok in toks.items():
   c={k:len(tok(v,add_special_tokens=False)["input_ids"]) for k,v in ctx.items()};counts[model]=c
   if len(set(c.values()))!=1: raise RuntimeError(f"token-footprint-mismatch:{model}:{tid}:{c}")
  per.append({"task_id":tid,"retrieved_memory_count":len(sel),"mixed_provenance":shuf is not None,"truthful_code_sequence_sha256":digest(truth),"shuffled_code_sequence_sha256":digest(shuf) if shuf is not None else None,"context_sha256":hashes,"token_counts":counts})
 if mixed!=57: raise RuntimeError(f"mixed-count:{mixed}")
 out={"schema_version":"1.0","paper_id":PAPER_ID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R70-TOKENIZER-FOOTPRINT-AUDIT","status":"R70_P_T_S_TOKEN_FOOTPRINT_MATCH_PASS_ZERO_MODEL","role":"ZERO_MODEL_STATIC_RENDERER_TOKENIZER_AUDIT","bindings":{"r54_frozen_retrieval_file_sha256":sha(r54_path),"r68_panel_file_sha256":sha(panel_path),"qwen_tokenizer_root":str(qwen_tokenizer),"llama_tokenizer_root":str(llama_tokenizer)},"field_schema":{"field":FIELD,"value_type":"string","codes":CODES,"shared_prefix":PREFIX,"P_T_S_same_key_and_row_schema":True},"units":66,"mixed_units_with_S":57,"checks":{"Qwen_P_T_equal_token_count_all_66":True,"Qwen_P_T_S_equal_token_count_all_57_mixed":True,"Llama_P_T_equal_token_count_all_66":True,"Llama_P_T_S_equal_token_count_all_57_mixed":True,"no_model_inference":True,"task_outcomes_observed":0},"rows":per,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False}
 out["receipt_sha256"]=digest(out);return out

def main():
 p=argparse.ArgumentParser();p.add_argument("--r54",type=pathlib.Path,required=True);p.add_argument("--panel",type=pathlib.Path,required=True);p.add_argument("--qwen-tokenizer",type=pathlib.Path,required=True);p.add_argument("--llama-tokenizer",type=pathlib.Path,required=True);p.add_argument("--output",type=pathlib.Path,required=True);a=p.parse_args();out=build(a.r54.resolve(),a.panel.resolve(),a.qwen_tokenizer.resolve(),a.llama_tokenizer.resolve());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":out["status"],"units":out["units"],"mixed_units":out["mixed_units_with_S"],"receipt_sha256":out["receipt_sha256"]},sort_keys=True))
if __name__=="__main__":main()
