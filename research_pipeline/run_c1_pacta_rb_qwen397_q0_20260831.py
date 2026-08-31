#!/usr/bin/env python3
"""Non-scientific Q0 qualification for C1-PACTA-RB-QWEN397."""
from __future__ import annotations
import argparse, json, os, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import (
 AA_BASE_URL,atomic_bytes,atomic_json,canonical,discover_qwen397,
 parse_first_decision,sha256_file,sha256_text)

EXP="C1-PACTA-RB-QWEN397-Q0-20260831-v2"
DEFAULT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2")
OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
CONFIG=OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml"
COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
LADDER=(512,1024,2048,4096)
TASKS=(
 "A Python package reports a public function returning the wrong type. Inspect the repository to begin.",
 "A command-line option is ignored in a small Python project. Inspect relevant files before editing.",
 "A serializer drops a documented field. Locate the implementation and tests.",
 "A parser rejects a valid empty collection. Inspect the parsing code.",
 "A numerical helper mishandles a scalar input. Find its definition.",
 "A configuration loader applies the wrong default. Inspect configuration modules.",
 "A warning is emitted for a supported input. Locate the warning condition.",
 "A path utility fails on relative paths. Inspect repository structure.",
 "A formatter loses trailing whitespace unexpectedly. Find formatter code.",
 "A cache invalidation helper keeps stale entries. Inspect cache implementation.",
 "A date conversion uses the wrong timezone. Locate conversion logic.",
 "A dataframe accessor returns an inconsistent dtype. Inspect accessor code.",
 "A plotting keyword is not forwarded. Locate the wrapper implementation.",
 "A validation function accepts a malformed tuple. Inspect validation code.",
 "A decorator drops function metadata. Find the decorator implementation.",
 "A test discovery option is parsed but unused. Inspect option handling.",
 "A network helper mishandles a unicode method name. Locate request construction.",
 "A symbolic simplifier changes an equivalent expression. Inspect simplification rules.",
 "A documentation builder omits one registered directive. Inspect registry code.",
 "An array reduction fails over multiple axes. Locate reduction implementation.",
)
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def model_ids(p):
 if not isinstance(p,dict) or not isinstance(p.get("data"),list):raise ValueError("models response has no data list")
 return [str(r.get("id") or "") for r in p["data"] if isinstance(r,dict) and r.get("id")]
def content(p):return str(p["choices"][0]["message"]["content"])
def usage(p):return p.get("usage") if isinstance(p.get("usage"),dict) else {}
def body(model,messages,budget):
 return {"model":model,"messages":messages,"stream":False,"n":1,"max_completion_tokens":budget,
         "temperature":0.0,"enable_thinking":False,"enable_search":False}

class RawAA:
 def __init__(self,key,root):
  if not key:raise RuntimeError("AA_API_KEY is not configured")
  self.key=key;self.root=root;self.calls=0
 def call(self,label,method,path,packet):
  self.calls+=1
  safe={"method":method,"endpoint":AA_BASE_URL+path,"body":packet,
        "authorization_material_persisted":False,"transport_attempt":1,"provider_retries":0}
  request_path=self.root/"raw"/f"{self.calls:04d}-{label}.request.json"
  response_path=self.root/"raw"/f"{self.calls:04d}-{label}.response.json"
  request_sha=atomic_bytes(request_path,(canonical(safe)+"\n").encode())
  data=None if packet is None else canonical(packet).encode()
  req=urllib.request.Request(AA_BASE_URL+path,data=data,method=method,
       headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json"})
  status=None
  try:
   with urllib.request.urlopen(req,timeout=240) as response:
    status=int(response.status);raw=response.read()
  except urllib.error.HTTPError as error:
   status=int(error.code);raw=error.read()
  returned=now()
  # This is the hard boundary: durable raw body before JSON decoding.
  response_sha=atomic_bytes(response_path,raw)
  meta={"label":label,"timestamp_utc":returned,"status_code":status,
        "request_path":str(request_path),"request_sha256":request_sha,
        "response_path":str(response_path),"response_sha256":response_sha,
        "response_bytes":len(raw),"persisted_before_parse":True,
        "transport_attempt_count":1}
  if status is None or not 200<=status<300:
   atomic_json(self.root/"calls"/f"{self.calls:04d}-{label}.json",{**meta,"parse_status":"NOT_PARSED_HTTP_ERROR"})
   raise RuntimeError(f"AA HTTP {status}; response_sha256={response_sha}")
  try:p=json.loads(raw.decode())
  except Exception:
   atomic_json(self.root/"calls"/f"{self.calls:04d}-{label}.json",{**meta,"parse_status":"JSON_PARSE_FAILED"})
   raise
  atomic_json(self.root/"calls"/f"{self.calls:04d}-{label}.json",{**meta,"parse_status":"JSON_PARSED"})
  return p,meta

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run-root",type=Path,default=DEFAULT);args=ap.parse_args()
 root=args.run_root
 if root.exists():raise RuntimeError(f"Q0 root exists; no overwrite/resume: {root}")
 root.mkdir(parents=True);(root/".lock").write_text(EXP+"\n")
 cfg=yaml.safe_load(CONFIG.read_text());system=str(cfg["agent"]["system_template"]);instance=str(cfg["agent"]["instance_template"])
 fixtures=[]
 for i,task in enumerate(TASKS,1):
  messages=[{"role":"system","content":system},
   {"role":"user","content":instance.replace("{{task}}",task).replace("{{selected_memory}}","")}]
  fixtures.append({"fixture_id":i,"task":task,"task_sha256":sha256_text(task),"messages":messages})
 atomic_json(root/"fixtures.json",{"schema_version":1,"experiment_id":EXP,"non_scientific":True,
  "frozen_before_provider_calls":True,"count":20,"official_config_path":str(CONFIG),
  "official_config_sha256":sha256_file(CONFIG),"system_template_sha256":sha256_text(system),
  "instance_template_sha256":sha256_text(instance),"fixtures":fixtures})
 atomic_json(root/"manifest.json",{"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),
  "status":"Q0_RUNNING","official_commit":COMMIT,"scientific_calls":0,
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0})
 provider=RawAA(os.environ.get("AA_API_KEY",""),root)
 models,mm=provider.call("models","GET","/models",None)
 ids=model_ids(models);requested=discover_qwen397(ids)
 atomic_json(root/"models-discovery.json",{**mm,"discovered_model_count":len(ids),
  "qwen397_matches":[x for x in ids if "qwen" in x.lower() and "397b" in x.lower()],
  "requested_model":requested})
 probes=[]
 for i in range(1,4):
  nonce=f"QWEN397_IDENTITY_PROBE_{i}_OK"
  packet=body(requested,[{"role":"system","content":"Follow the exact output instruction and add nothing."},
                         {"role":"user","content":f"Reply exactly {nonce}"}],128)
  p,m=provider.call(f"identity-{i}","POST","/chat/completions",packet)
  probes.append({**m,"probe":i,"requested_model":requested,"resolved_model":str(p.get("model") or ""),
   "response_model":str(p.get("model") or ""),"response_id":str(p.get("id") or ""),
   "exact_text_pass":content(p).strip()==nonce,"enable_thinking_requested":False,
   "thinking_parameter_accepted":True,"usage":usage(p)})
 resolved={x["resolved_model"] for x in probes}
 if len(resolved)!=1 or not next(iter(resolved)) or not all(x["exact_text_pass"] for x in probes):
  raise RuntimeError("HOLD_PROVIDER_IDENTITY_UNRESOLVED")
 resolved_model=next(iter(resolved))
 binding={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),
  "provider":"典名词元 AA/OpenAI-compatible","endpoint":AA_BASE_URL+"/chat/completions",
  "models_endpoint":AA_BASE_URL+"/models","models_raw_response_path":mm["response_path"],
  "models_raw_response_sha256":mm["response_sha256"],"requested_model":requested,
  "resolved_model":resolved_model,"response_model":resolved_model,"identity_probes":probes,
  "identity_pass":True,"enable_thinking_request":False,
  "enable_thinking_status":"accepted_and_frozen","internal_reasoning_absence_claimed":False,
  "provider_retries":0,"substitution":False}
 atomic_json(root/"provider-binding.json",binding)
 rows=[];rungs=[];frozen=None
 for budget in LADDER:
  current=[]
  for f in fixtures:
   label=f"budget-{budget}-fixture-{f['fixture_id']:02d}"
   p,m=provider.call(label,"POST","/chat/completions",body(requested,f["messages"],budget))
   text=content(p);ok=False;action=None;error=None
   try:
    action=parse_first_decision(text)
    if not action.strip() or chr(0) in action or (chr(96)*3) in action:raise ValueError("non-executable capture")
    action=action.strip();ok=True
   except Exception as exc:error=f"{type(exc).__name__}: {exc}"
   row={**m,"fixture_id":f["fixture_id"],"budget":budget,"requested_model":requested,
    "resolved_model":str(p.get("model") or ""),"model_drift":str(p.get("model") or "")!=resolved_model,
    "provider_packet_drift":False,"hidden_fallback":False,"response_id":str(p.get("id") or ""),
    "raw_content_sha256":sha256_text(text),"response_nonempty":bool(text),"parse_success":ok,
    "parse_error":error,"exactly_one_executable_action":ok,"canonical_action":action,
    "usage":usage(p),"enable_thinking_requested":False,"thinking_fallback":False,"non_scientific":True}
   atomic_json(root/"qualification"/f"{label}.json",row);rows.append(row);current.append(row)
  passed=len(current)==20 and all(x["response_nonempty"] and x["parse_success"] and
   not x["model_drift"] and not x["provider_packet_drift"] and not x["hidden_fallback"] and
   not x["thinking_fallback"] and x["persisted_before_parse"] for x in current)
  rungs.append({"budget":budget,"passed":sum(x["parse_success"] and not x["model_drift"] for x in current),
                "total":20,"qualification_pass":passed})
  if passed:frozen=budget;break
 decision="Q0_PROVIDER_ACTION_INTERFACE_QUALIFIED" if frozen else "HOLD_ACTION_INTERFACE_UNQUALIFIED"
 all_receipts=probes+rows
 totals={"input_tokens":sum(int(x["usage"].get("prompt_tokens") or x["usage"].get("input_tokens") or 0) for x in all_receipts),
  "output_tokens":sum(int(x["usage"].get("completion_tokens") or x["usage"].get("output_tokens") or 0) for x in all_receipts),
  "provider_calls":provider.calls,"estimated_cost":None}
 result={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"decision":decision,
  "identity_pass":True,"identity_probes":"3/3","requested_model":requested,"resolved_model":resolved_model,
  "enable_thinking_status":"request parameter accepted and frozen","rung_results":rungs,
  "frozen_output_token_budget":frozen,"usage":totals,"scientific_calls":0,
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0}
 atomic_json(root/"qualification-result.json",result)
 if frozen:
  atomic_json(root/"source-acquisition-contract.json",{"schema_version":1,
   "experiment_id":"C1-PACTA-RB-QWEN397-T0-20260831-v1","created_at_utc":now(),
   "provider_binding_path":str(root/"provider-binding.json"),
   "provider_binding_sha256":sha256_file(root/"provider-binding.json"),
   "qualification_result_path":str(root/"qualification-result.json"),
   "qualification_result_sha256":sha256_file(root/"qualification-result.json"),
   "requested_model":requested,"resolved_model":resolved_model,"enable_thinking":False,
   "max_completion_tokens":frozen,"temperature":0.0,"provider_retries":0,
   "logical_attempts_per_source":1,"memory":"","writer_calls":0,
   "forbidden_stages":["writer","binder","shadow","gate","random_gate","final","future_policy"]})
 print(canonical({"decision":decision,"requested_model":requested,"resolved_model":resolved_model,
                  "rungs":rungs,"frozen_budget":frozen,"provider_calls":provider.calls}))
 if not frozen:raise SystemExit(2)
if __name__=="__main__":main()
