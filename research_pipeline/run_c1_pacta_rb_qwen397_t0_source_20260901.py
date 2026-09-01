#!/usr/bin/env python3
"""Gate-locked T0 smoke, bridge, schedule, and fixed source acquisition."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes,atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import Container,RawProvider,execute_trajectory,initial_messages,parse_action,render
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import SPECS,image_repo

OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
CONFIG=OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml"
POOL=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2")
T05=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")
DEFAULT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-source-trajectory-20260901-v2")
COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
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

def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def frozen()->tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
 q=json.loads((Q0/"qualification-result.json").read_text());b=json.loads((Q0/"provider-binding.json").read_text())
 runtime=json.loads((T05/"runtime-qualification.json").read_text())
 if q["decision"]!="Q0_PROVIDER_ACTION_INTERFACE_QUALIFIED" or q["frozen_output_token_budget"]!=512:raise RuntimeError("Q0 drift")
 if not b["identity_pass"] or b["requested_model"]!="qwen3.5-397b-a17b" or b["resolved_model"]!="qwen3.5-397b-a17b":raise RuntimeError("identity drift")
 if runtime["decision"]!="T0_5_FIXED_IMAGES_READY" or runtime["qualified_images"]!=11:raise RuntimeError("T0.5 11/11 gate not passed")
 if subprocess.run(["git","-C",str(OFFICIAL),"rev-parse","HEAD"],text=True,capture_output=True).stdout.strip()!=COMMIT:raise RuntimeError("carrier commit drift")
 return q,b,yaml.safe_load(CONFIG.read_text())

def smoke()->dict[str,Any]:
 _,b,config=frozen();instance,_idx,amd64=SPECS[0]
 smoke_root=T05/"multistep-smoke"
 if smoke_root.exists():raise RuntimeError("smoke root exists; no overwrite/retry")
 smoke_root.mkdir(parents=True)
 digest_ref=f"docker.1ms.run/{image_repo(instance)}@sha256:{amd64}"
 task=("Synthetic non-scientific runtime qualification. First inspect the current working directory, "
       "then inspect one harmless file such as README, then issue another harmless shell command, "
       "then finish using the required completion command. Do not modify files.")
 messages=initial_messages(task,config)
 provider=RawProvider(os.environ.get("AA_API_KEY",""),smoke_root,b["requested_model"],b["resolved_model"])
 container=Container(digest_ref);rows=[];submitted=False
 try:
  for step in range(1,9):
   response=provider.call(messages,f"multistep-smoke-{step}");content=response["content"]
   messages.append({"role":"assistant","content":content});action=parse_action(content);obs=container.execute(action)
   obs_path=smoke_root/"raw"/f"observation-{step:04d}.json"
   obs_sha=atomic_bytes(obs_path,(json.dumps(obs,ensure_ascii=False,sort_keys=True)+"\n").encode())
   lines=obs["output"].lstrip().splitlines(keepends=True)
   if not obs["timeout"] and lines and lines[0].strip() in ("MINI_SWE_AGENT_FINAL_OUTPUT","COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"):
    submitted=True;messages.append({"role":"user","content":"".join(lines[1:])})
   else:
    messages.append({"role":"user","content":render(config["agent"]["action_observation_template"],{"task":task,"selected_memory":""},output=obs)})
   rows.append({"step":step,"action":action,"returncode":obs["returncode"],"response_sha256":response["provider"]["response_sha256"],"observation_path":str(obs_path),"observation_sha256":obs_sha})
   if submitted:break
 finally:container.cleanup()
 passed=submitted and len(rows)>=2 and provider.calls==len(list((smoke_root/"raw").glob("response-*.json")))
 result={"schema_version":1,"created_at_utc":now(),"non_scientific":True,"multi_step":True,
  "requested_model":b["requested_model"],"resolved_model":b["resolved_model"],"enable_thinking":False,
  "max_completion_tokens":512,"provider_calls":provider.calls,"input_tokens":provider.prompt_tokens,
  "output_tokens":provider.output_tokens,"rows":rows,"submitted":submitted,"pass":passed}
 atomic_json(T05/"synthetic-smoke.json",result)
 if not passed:raise RuntimeError("STOP_T0_MULTI_STEP_RUNTIME_UNQUALIFIED")
 return result

def prepare(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError(f"T0 root exists; no overwrite/resume: {root}")
 q,b,_=frozen();pool=json.loads(POOL.read_text());units={u["source_task_id"]:u for u in pool["units"]}
 digest_by={instance:amd64 for instance,_idx,amd64 in SPECS};schedule=[]
 for seq,instance in enumerate(FUTURES,1):
  u=units[instance];schedule.append({"sequence":seq,"source_task_id":instance,"future_task_id":FUTURES[instance],
   "repository":u["task_family"],"task_sha256":u["source_task_sha256"],"base_commit":u["source_base_commit"],
   "digest_ref":f"docker.1ms.run/{image_repo(instance)}@sha256:{digest_by[instance]}",
   "logical_attempts":1,"selected_memory":"","future_task_executed":False})
 root.mkdir(parents=True)
 contract={"schema_version":1,"created_at_utc":now(),"status":"FROZEN_BEFORE_SOURCE_POLICY","official_commit":COMMIT,
  "official_config_path":str(CONFIG),"official_config_sha256":sha256_file(CONFIG),
  "provider_binding_path":str(Q0/"provider-binding.json"),"provider_binding_sha256":sha256_file(Q0/"provider-binding.json"),
  "runtime_qualification_path":str(T05/"runtime-qualification.json"),"runtime_qualification_sha256":sha256_file(T05/"runtime-qualification.json"),
  "requested_model":b["requested_model"],"resolved_model":b["resolved_model"],"enable_thinking":False,
  "max_completion_tokens":q["frozen_output_token_budget"],"temperature":0.0,"step_call_ceiling":250,
  "provider_retries":0,"logical_attempts_per_source":1,"replacement":False,"top_up":False,"selected_memory":"",
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0,
  "forbidden":["writer","binder","shadow","gate","random_gate","final","future_policy","future_evaluator","other_model","R10"]}
 atomic_json(root/"contract.json",contract)
 atomic_json(root/"acquisition-schedule.json",{"schema_version":1,"created_at_utc":now(),"status":"FROZEN","schedule":schedule,
  "scheduled_count":11,"selection":"all fixed preflight-valid units","outcome_blind":True,"replacement":False,"top_up":False})
 return {"schedule":schedule}

def bridge(root:Path)->dict[str,Any]:
 _,b,_=frozen();provider=RawProvider(os.environ.get("AA_API_KEY",""),root/"bridge",b["requested_model"],b["resolved_model"])
 response=provider.call([{"role":"system","content":"Return exactly one bash action and nothing else."},
  {"role":"user","content":"Return exactly: ```bash\nprintf T0_BRIDGE_OK\n```"}],"bridge-identity")
 action=parse_action(response["content"])
 result={"schema_version":1,"created_at_utc":now(),"non_scientific":True,"requested_model":b["requested_model"],
  "resolved_model":response["provider"]["resolved_model"],"enable_thinking":False,"max_completion_tokens":512,
  "action":action,"pass":action=="printf T0_BRIDGE_OK","provider_calls":1,"usage":response["provider"]["usage"]}
 atomic_json(root/"bridge-qualification.json",result)
 if not result["pass"]:raise RuntimeError("STOP_BRIDGE_QUALIFICATION")
 return result

def acquire(root:Path)->dict[str,Any]:
 if not (root/"bridge-qualification.json").is_file():raise RuntimeError("bridge not qualified")
 _,b,config=frozen();pool=json.loads(POOL.read_text());units={u["source_task_id"]:u for u in pool["units"]}
 schedule=json.loads((root/"acquisition-schedule.json").read_text())["schedule"];rows=[]
 for item in schedule:
  instance=item["source_task_id"]
  row=execute_trajectory(instance,units[instance]["source_task"],item["digest_ref"],root/f"source-{instance}",
   config,os.environ.get("AA_API_KEY",""),b["requested_model"],b["resolved_model"])
  rows.append(row);print(json.dumps({"instance_id":instance,"calls":row["model_call_count"],"terminal":row["terminal_status"],"validity":row["validity_status"]}),flush=True)
 valid=[r for r in rows if r["validity_status"]=="TRAJECTORY_BACKED_VALID"]
 repos={units[r["source_task_id"]]["task_family"] for r in valid}
 decision="SOURCE_TRAJECTORY_POOL_QUALIFIED" if len(valid)==11 else ("SOURCE_TRAJECTORY_POOL_PARTIAL" if len(valid)>=6 else "HOLD_FRESH_SUPPORT_INSUFFICIENT_AFTER_ACQUISITION")
 result={"schema_version":1,"created_at_utc":now(),"rows":rows,"N_valid_trajectory":len(valid),"N_valid_repository":len(repos),
  "full_6_plus_5_design_recovered":len(valid)==11,"decision":decision,"source_logical_attempts":len(rows),
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0,
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9"}
 atomic_json(root/"support-audit.json",result);return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=DEFAULT)
 ap.add_argument("--phase",choices=("smoke","prepare","bridge","acquire"),required=True);args=ap.parse_args()
 if args.phase=="smoke":result=smoke()
 elif args.phase=="prepare":result=prepare(args.root)
 elif args.phase=="bridge":result=bridge(args.root)
 else:result=acquire(args.root)
 print(json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
