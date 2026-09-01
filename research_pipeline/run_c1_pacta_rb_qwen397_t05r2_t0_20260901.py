#!/usr/bin/env python3
"""Prospective T0.5-R2 smoke, bridge, and fixed source acquisition.

The previous eight-step synthetic smoke remains immutable and failed only its
termination criterion. This new human-authorized epoch removes the contradictory
"do not modify files" synthetic task while preserving the sealed Q0 model binding,
512-token response budget, rootful exact-base runtime, and all scientific locks.
This entry point cannot reach writer, binder, shadow, gate, final measurement, or
future-task execution.
"""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes,atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import (
 Container,RawProvider,ROOTFUL_DOCKER_HOST,execute_trajectory,initial_messages,parse_action,render
)
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import SPECS,image_repo

OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
CONFIG=OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml"
POOL=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2")
T05R_RUNTIME=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05r-images-rootful-20260901-v1")
PRIOR_SMOKE=T05R_RUNTIME/"rootful-synthetic-smoke.json"
SMOKE_EPOCH=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05r2-smoke-20260901-v1")
DEFAULT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-rootful-source-20260901-v2")
SMOKE_STEP_CEILING=8
COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
T05R_QUALIFICATION_SHA256="f45a31f5365f896b8647e5ece843362aeb7a763c75f5bb775f844b442aa36bfa"
FUTURES={
"pydata__xarray-4966":"pydata__xarray-4356",
"scikit-learn__scikit-learn-14496":"scikit-learn__scikit-learn-10908",
"psf__requests-1766":"psf__requests-1724",
"matplotlib__matplotlib-24627":"matplotlib__matplotlib-25960",
"sphinx-doc__sphinx-8593":"sphinx-doc__sphinx-7748",
"mwaskom__seaborn-3187":"mwaskom__seaborn-3069",
"sympy__sympy-15599":"sympy__sympy-18189",
"astropy__astropy-7166":"astropy__astropy-14096",
"django__django-13449":"django__django-11400",
"pylint-dev__pylint-7080":"pylint-dev__pylint-8898",
"pytest-dev__pytest-5840":"pytest-dev__pytest-5809"}

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def require_key()->str:
 key=os.environ.get("AA_API_KEY","")
 if not key:raise RuntimeError("STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED")
 return key

def frozen()->tuple[dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any]]:
 q=json.loads((Q0/"qualification-result.json").read_text())
 b=json.loads((Q0/"provider-binding.json").read_text())
 qualification_path=T05R_RUNTIME/"normalization-qualification.json"
 if sha256_file(qualification_path)!=T05R_QUALIFICATION_SHA256:raise RuntimeError("T0.5-R qualification hash drift")
 runtime=json.loads(qualification_path.read_text())
 if q["decision"]!="Q0_PROVIDER_ACTION_INTERFACE_QUALIFIED" or q["frozen_output_token_budget"]!=512:
  raise RuntimeError("Q0 drift")
 if not b["identity_pass"] or b["requested_model"]!="qwen3.5-397b-a17b" or b["resolved_model"]!="qwen3.5-397b-a17b":
  raise RuntimeError("identity drift")
 if runtime["decision"]!="T0_5R_ROOTFUL_RUNTIME_READY" or runtime["qualified"]!=11:
  raise RuntimeError("T0.5-R 11/11 gate not passed")
 if runtime["docker"]["docker_host"]!=ROOTFUL_DOCKER_HOST:
  raise RuntimeError("rootful Docker host drift")
 head=subprocess.run(["git","-C",str(OFFICIAL),"rev-parse","HEAD"],text=True,capture_output=True,check=True).stdout.strip()
 if head!=COMMIT:raise RuntimeError("carrier commit drift")
 return q,b,yaml.safe_load(CONFIG.read_text()),runtime

def pool_units()->dict[str,dict[str,Any]]:
 pool=json.loads(POOL.read_text())
 return {u["source_task_id"]:u for u in pool["units"]}

def spec_map()->dict[str,str]:
 return {instance:amd64 for instance,_idx,amd64 in SPECS}

def smoke()->dict[str,Any]:
 key=require_key();_,b,config,_=frozen();units=pool_units()
 instance="pydata__xarray-4966";amd64=spec_map()[instance]
 if not PRIOR_SMOKE.is_file():raise RuntimeError("prior smoke artifact missing; historical STOP cannot be audited")
 prior=json.loads(PRIOR_SMOKE.read_text())
 if prior.get("pass") is not False or int(prior.get("provider_calls") or 0)!=8:
  raise RuntimeError("prior smoke history drift")
 smoke_root=SMOKE_EPOCH/"rootful-multistep-smoke"
 if SMOKE_EPOCH.exists():raise RuntimeError("new smoke epoch exists; no overwrite/retry")
 smoke_root.mkdir(parents=True)
 digest_ref=f"docker.1ms.run/{image_repo(instance)}@sha256:{amd64}"
 task=("Synthetic non-scientific runtime qualification. This task is intentionally self-contained: "
       "create one new non-test source file named runtime_smoke_marker.py whose only executable behavior "
       "is to print exactly QWEN397_T0_RUNTIME_SMOKE_OK followed by a newline. Verify it by running "
       "python runtime_smoke_marker.py, inspect the resulting git diff, and then finish using the required "
       "MiniSWEAgent completion command. Do not search for or repair any unrelated issue.")
 messages=initial_messages(task,config)
 container=Container(digest_ref,docker_host=ROOTFUL_DOCKER_HOST,
  base_commit=units[instance]["source_base_commit"],provenance_root=smoke_root)
 provider=RawProvider(key,smoke_root,b["requested_model"],b["resolved_model"])
 rows=[];submitted=False
 try:
  for step in range(1,SMOKE_STEP_CEILING+1):
   response=provider.call(messages,f"rootful-multistep-smoke-{step}")
   content=response["content"];messages.append({"role":"assistant","content":content})
   action=parse_action(content);obs=container.execute(action)
   obs_path=smoke_root/"raw"/f"observation-{step:04d}.json"
   obs_sha=atomic_bytes(obs_path,(json.dumps(obs,ensure_ascii=False,sort_keys=True)+"\n").encode())
   lines=obs["output"].lstrip().splitlines(keepends=True)
   if not obs["timeout"] and lines and lines[0].strip() in ("MINI_SWE_AGENT_FINAL_OUTPUT","COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"):
    submitted=True;messages.append({"role":"user","content":"".join(lines[1:])})
   else:
    messages.append({"role":"user","content":render(config["agent"]["action_observation_template"],
     {"task":task,"selected_memory":""},output=obs)})
   rows.append({"step":step,"action":action,"returncode":obs["returncode"],
    "response_sha256":response["provider"]["response_sha256"],"observation_path":str(obs_path),
    "observation_sha256":obs_sha})
   if submitted:break
 finally:container.cleanup()
 passed=submitted and len(rows)>=2 and provider.calls==len(list((smoke_root/"raw").glob("response-*.json")))
 result={"schema_version":1,"created_at_utc":now(),"epoch":"C1-PACTA-RB-QWEN397-T05R2-SMOKE",
  "non_scientific":True,"multi_step":True,"prior_smoke_stop_preserved":True,
  "prior_smoke_path":str(PRIOR_SMOKE),"prior_smoke_sha256":sha256_file(PRIOR_SMOKE),
  "repair_basis":"single-variable qualification repair: replace the contradictory no-modification synthetic task; keep the prior eight-step ceiling, Q0 binding, response budget, parser, provider packet, and runtime unchanged; no source task or PACTA outcome was observed",
  "scientific_outcome_access_before_repair":False,"source_tasks_consumed_before_repair":0,
  "task_contract":task,"step_ceiling":SMOKE_STEP_CEILING,
  "docker_host":ROOTFUL_DOCKER_HOST,"exact_base_normalized_before_provider":True,
  "requested_model":b["requested_model"],"resolved_model":b["resolved_model"],"enable_thinking":False,
  "max_completion_tokens":512,"provider_calls":provider.calls,"input_tokens":provider.prompt_tokens,
  "output_tokens":provider.output_tokens,"rows":rows,"submitted":submitted,"pass":passed,
  "source_tasks_consumed":0,"writer_calls":0,"binder_calls":0,"shadow_calls":0,
  "final_measurement_calls":0,"future_task_executions":0}
 atomic_json(SMOKE_EPOCH/"rootful-synthetic-smoke.json",result)
 if not passed:raise RuntimeError("STOP_T0_MULTI_STEP_RUNTIME_UNQUALIFIED")
 return result

def prepare(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError(f"T0 root exists; no overwrite/resume: {root}")
 smoke_path=SMOKE_EPOCH/"rootful-synthetic-smoke.json"
 if not smoke_path.is_file() or not json.loads(smoke_path.read_text()).get("pass"):
  raise RuntimeError("new synthetic smoke not qualified")
 q,b,_,_=frozen();units=pool_units();digest_by=spec_map();schedule=[]
 for seq,instance in enumerate(FUTURES,1):
  u=units[instance]
  schedule.append({"sequence":seq,"source_task_id":instance,"future_task_id":FUTURES[instance],
   "repository":u["task_family"],"task_sha256":u["source_task_sha256"],
   "base_commit":u["source_base_commit"],
   "digest_ref":f"docker.1ms.run/{image_repo(instance)}@sha256:{digest_by[instance]}",
   "logical_attempts":1,"selected_memory":"","future_task_executed":False})
 root.mkdir(parents=True)
 contract={"schema_version":1,"created_at_utc":now(),"status":"FROZEN_BEFORE_SOURCE_POLICY",
  "official_commit":COMMIT,"official_config_path":str(CONFIG),"official_config_sha256":sha256_file(CONFIG),
  "provider_binding_path":str(Q0/"provider-binding.json"),
  "provider_binding_sha256":sha256_file(Q0/"provider-binding.json"),
  "runtime_qualification_path":str(T05R_RUNTIME/"normalization-qualification.json"),
  "runtime_qualification_sha256":sha256_file(T05R_RUNTIME/"normalization-qualification.json"),
  "synthetic_smoke_path":str(smoke_path),
  "synthetic_smoke_sha256":sha256_file(smoke_path),
  "docker_host":ROOTFUL_DOCKER_HOST,"exact_base_normalization_before_provider":True,
  "requested_model":b["requested_model"],"resolved_model":b["resolved_model"],"enable_thinking":False,
  "max_completion_tokens":q["frozen_output_token_budget"],"temperature":0.0,"step_call_ceiling":250,
  "provider_retries":0,"logical_attempts_per_source":1,"replacement":False,"top_up":False,
  "selected_memory":"","writer_calls":0,"binder_calls":0,"shadow_calls":0,
  "final_measurement_calls":0,"future_task_executions":0,
  "forbidden":["writer","binder","shadow","gate","random_gate","final","future_policy",
   "future_evaluator","other_model","R10"]}
 atomic_json(root/"contract.json",contract)
 schedule_doc={"schema_version":1,"created_at_utc":now(),"status":"FROZEN","schedule":schedule,
  "scheduled_count":11,"selection":"all fixed preflight-valid units","outcome_blind":True,
  "replacement":False,"top_up":False}
 atomic_json(root/"acquisition-schedule.json",schedule_doc)
 return {"schedule":schedule,"schedule_sha256":sha256_file(root/"acquisition-schedule.json")}

def bridge(root:Path)->dict[str,Any]:
 key=require_key()
 if not (SMOKE_EPOCH/"rootful-synthetic-smoke.json").is_file():raise RuntimeError("new synthetic smoke not qualified")
 smoke=json.loads((SMOKE_EPOCH/"rootful-synthetic-smoke.json").read_text())
 if not smoke.get("pass"):raise RuntimeError("synthetic smoke not qualified")
 _,b,_,_=frozen()
 bridge_root=root/"bridge"
 if bridge_root.exists():raise RuntimeError("bridge root exists; no overwrite/retry")
 provider=RawProvider(key,bridge_root,b["requested_model"],b["resolved_model"])
 response=provider.call([{"role":"system","content":"Return exactly one bash action and nothing else."},
  {"role":"user","content":"Return exactly: ```bash\nprintf T0_BRIDGE_OK\n```"}],"bridge-identity")
 action=parse_action(response["content"])
 result={"schema_version":1,"created_at_utc":now(),"non_scientific":True,
  "requested_model":b["requested_model"],"resolved_model":response["provider"]["resolved_model"],
  "enable_thinking":False,"max_completion_tokens":512,"action":action,
  "pass":action=="printf T0_BRIDGE_OK","provider_calls":1,"usage":response["provider"]["usage"]}
 atomic_json(root/"bridge-qualification.json",result)
 if not result["pass"]:raise RuntimeError("STOP_BRIDGE_QUALIFICATION")
 return result

def acquire(root:Path)->dict[str,Any]:
 key=require_key()
 bridge_path=root/"bridge-qualification.json"
 if not bridge_path.is_file() or not json.loads(bridge_path.read_text()).get("pass"):
  raise RuntimeError("bridge not qualified")
 _,b,config,_=frozen();units=pool_units()
 schedule=json.loads((root/"acquisition-schedule.json").read_text())["schedule"];rows=[]
 for item in schedule:
  instance=item["source_task_id"]
  row=execute_trajectory(instance,units[instance]["source_task"],item["digest_ref"],
   root/f"source-{instance}",config,key,b["requested_model"],b["resolved_model"],
   docker_host=ROOTFUL_DOCKER_HOST,base_commit=item["base_commit"])
  rows.append(row)
  print(json.dumps({"instance_id":instance,"calls":row["model_call_count"],
   "terminal":row["terminal_status"],"validity":row["validity_status"]}),flush=True)
 valid=[r for r in rows if r["validity_status"]=="TRAJECTORY_BACKED_VALID"]
 repos={units[r["source_task_id"]]["task_family"] for r in valid}
 decision=("SOURCE_TRAJECTORY_POOL_QUALIFIED" if len(valid)==11 else
  ("SOURCE_TRAJECTORY_POOL_PARTIAL" if len(valid)>=6 else
   "HOLD_FRESH_SUPPORT_INSUFFICIENT_AFTER_ACQUISITION"))
 result={"schema_version":1,"created_at_utc":now(),"rows":rows,
  "N_valid_trajectory":len(valid),"N_valid_repository":len(repos),
  "full_6_plus_5_design_recovered":len(valid)==11,"decision":decision,
  "source_logical_attempts":len(rows),"writer_calls":0,"binder_calls":0,"shadow_calls":0,
  "final_measurement_calls":0,"future_task_executions":0,
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9"}
 atomic_json(root/"support-audit.json",result)
 return result

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=DEFAULT)
 ap.add_argument("--phase",choices=("smoke","prepare","bridge","acquire"),required=True)
 args=ap.parse_args()
 if args.phase=="smoke":result=smoke()
 elif args.phase=="prepare":result=prepare(args.root)
 elif args.phase=="bridge":result=bridge(args.root)
 else:result=acquire(args.root)
 print(json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
