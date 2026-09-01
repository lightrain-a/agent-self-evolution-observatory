#!/usr/bin/env python3
"""Gate-locked T0 smoke, bridge, schedule, and fixed source acquisition."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import Container,RawProvider,execute_trajectory,initial_messages,parse_action
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
 _,_,config=frozen();instance,_idx,amd64=SPECS[0]
 digest_ref=f"docker.1ms.run/{image_repo(instance)}@sha256:{amd64}";container=Container(digest_ref)
 rows=[]
 try:
  for i,action in enumerate(("pwd","echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && printf T0_SMOKE_OK"),1):
   content=f"THOUGHT: synthetic smoke step {i}\n\n```bash\n{action}\n```"
   parsed=parse_action(content);obs=container.execute(parsed)
   rows.append({"step":i,"action":parsed,"returncode":obs["returncode"],"output":obs["output"]})
 finally:container.cleanup()
 passed=rows[0]["output"].strip()=="/testbed" and rows[1]["output"].splitlines()[:2]==["COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT","T0_SMOKE_OK"]
 result={"schema_version":1,"created_at_utc":now(),"non_scientific":True,"multi_step":True,"provider_calls":0,"rows":rows,"pass":passed}
 atomic_json(T05/"synthetic-smoke.json",result)
 if not passed:raise RuntimeError("STOP_SYNTHETIC_SMOKE")
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
