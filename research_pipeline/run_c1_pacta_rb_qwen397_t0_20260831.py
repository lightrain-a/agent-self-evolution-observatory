#!/usr/bin/env python3
"""T0 runtime preflight and support closure for the fixed Qwen397 source pool.

No model, writer, binder, shadow, gate, final, evaluator, or future-task policy
call is reachable from this program. A later acquisition runner is only legal
when this preflight reports at least six valid source runtimes.
"""
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,canonical,sha256_file,sha256_text

EXP="C1-PACTA-RB-QWEN397-T0-20260831-v1"
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2")
T0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-source-trajectory-20260831-v1")
OLD_Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v1")
OLD_P0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-p0-20260831-v1")
POOL=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")
PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
OS_PATH=ROOT/"research_pipeline/c1_pacta_rb_qwen397_t0_source_trajectory_acquisition_20260831.json"
OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
PAIRS=(
 ("pydata__xarray-4966","pydata__xarray-4356"),
 ("scikit-learn__scikit-learn-14496","scikit-learn__scikit-learn-10908"),
 ("psf__requests-1766","psf__requests-1724"),
 ("matplotlib__matplotlib-24627","matplotlib__matplotlib-25960"),
 ("sphinx-doc__sphinx-8593","sphinx-doc__sphinx-7748"),
 ("mwaskom__seaborn-3187","mwaskom__seaborn-3069"),
 ("sympy__sympy-15599","sympy__sympy-18189"),
 ("astropy__astropy-7166","astropy__astropy-14096"),
 ("django__django-13449","django__django-11400"),
 ("pylint-dev__pylint-7080","pylint-dev__pylint-8898"),
 ("pytest-dev__pytest-5840","pytest-dev__pytest-5809"),
)
FILES={
 "config":OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml",
 "agent":OFFICIAL/"third_party/src/minisweagent/agents/default.py",
 "writer":OFFICIAL/"third_party/src/minisweagent/memory/instruction.py",
 "retrieval":OFFICIAL/"third_party/src/minisweagent/memory/memory_management.py",
 "runner":OFFICIAL/"third_party/src/minisweagent/run/extra/swebench.py",
}
EXPECTED={
 "config":"d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41",
 "agent":"428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c",
 "writer":"08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae",
 "retrieval":"fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955",
 "runner":"8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951",
}
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def run(*args):return subprocess.run(args,text=True,capture_output=True)
def image_name(iid):return "swebench/sweb.eval.x86_64."+iid.replace("__","_1776_").lower()+":latest"
def prior_response_paths(iid):
 roots=Path("/data/wyt/agent-self-evolution-observatory/runs")
 hits=[]
 for base in roots.glob("c1-pacta*"):
  if base in {Q0,T0}:continue
  for folder in ("per_case","writer","binder","shadow","final","source","projection"):
   d=base/folder
   if d.is_dir():
    hits += [str(p) for p in d.rglob("*") if p.is_file() and iid in p.name]
 return sorted(hits)
def inspect_runtime(unit):
 iid=unit["source_task_id"];image=image_name(iid)
 p=run("docker","image","inspect",image)
 if p.returncode:
  return {"image_reference":image,"image_available":False,"image_digest":None,
          "container_start_pass":False,"base_commit_pass":False,"working_tree_equivalent":False,
          "runtime_executable_pass":False,"reason":"local SWE-bench image unavailable; no pull/substitution authorized"}
 try:meta=json.loads(p.stdout)[0]
 except Exception:
  return {"image_reference":image,"image_available":True,"image_digest":None,
          "container_start_pass":False,"base_commit_pass":False,"working_tree_equivalent":False,
          "runtime_executable_pass":False,"reason":"docker image metadata parse failure"}
 digest=(meta.get("RepoDigests") or [meta.get("Id")])[0]
 check=run("docker","run","--rm",image,"sh","-lc",
  "cd /testbed && printf 'HEAD=' && git rev-parse HEAD && printf 'DIRTY=' && git status --porcelain | wc -l && command -v bash && command -v git && command -v python")
 values={}
 for line in check.stdout.splitlines():
  if "=" in line:
   k,v=line.split("=",1);values[k]=v
 head=values.get("HEAD","");dirty=values.get("DIRTY","")
 return {"image_reference":image,"image_available":True,"image_digest":digest,
  "container_start_pass":check.returncode==0,"observed_base_commit":head,
  "base_commit_pass":head==unit["source_base_commit"],"working_tree_equivalent":dirty=="0",
  "runtime_executable_pass":check.returncode==0 and "/bash" in check.stdout and "/git" in check.stdout and "/python" in check.stdout,
  "reason":"pass" if check.returncode==0 and head==unit["source_base_commit"] and dirty=="0" else "runtime provenance mismatch"}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--t0-root",type=Path,default=T0);args=ap.parse_args()
 t0=args.t0_root
 if t0.exists():raise RuntimeError(f"T0 root exists; no overwrite/resume: {t0}")
 if not OLD_Q0.is_dir() or not OLD_P0.is_dir():raise RuntimeError("sealed historical Q0/P0 roots missing")
 q=json.loads((Q0/"qualification-result.json").read_text())
 if q.get("decision")!="Q0_PROVIDER_ACTION_INTERFACE_QUALIFIED":raise RuntimeError("Q0 not qualified")
 binding=json.loads((Q0/"provider-binding.json").read_text())
 source_contract=json.loads((Q0/"source-acquisition-contract.json").read_text())
 if run("git","-C",str(OFFICIAL),"rev-parse","HEAD").stdout.strip()!=OFFICIAL_COMMIT:raise RuntimeError("STOP_CARRIER_DRIFT")
 carrier={k:{"path":str(p),"sha256":sha256_file(p),"expected_sha256":EXPECTED[k],
             "pass":sha256_file(p)==EXPECTED[k]} for k,p in FILES.items()}
 if not all(x["pass"] for x in carrier.values()):raise RuntimeError("STOP_CARRIER_DRIFT")
 t0.mkdir(parents=True);(t0/".lock").write_text(EXP+"\n")
 pool=json.loads(POOL.read_text());units=pool["units"];by={u["source_task_id"]:u for u in units}
 if tuple((u["source_task_id"],u["future_task_id"]) for u in units)!=PAIRS:raise RuntimeError("fixed pair order/content drift")
 rows=[]
 for source,future in PAIRS:
  u=by[source]
  task_hash=sha256_text(u["source_task"]);future_hash=sha256_text(u["future_task"])
  runtime=inspect_runtime(u);prior=prior_response_paths(source)
  static={
   "source_task_hash_pass":task_hash==u["source_task_sha256"],
   "future_task_hash_pass":future_hash==u["future_task_sha256"],
   "source_future_disjoint":source!=future and u["source_task_sha256"]!=u["future_task_sha256"],
   "repository_identity":u["task_family"],"base_commit":u["source_base_commit"],
   "prior_pacta_response_artifacts":prior,"prior_scientific_output_absent":not prior,
  }
  valid=all(static[k] for k in ("source_task_hash_pass","future_task_hash_pass","source_future_disjoint","prior_scientific_output_absent")) and all(runtime[k] for k in ("image_available","container_start_pass","base_commit_pass","working_tree_equivalent","runtime_executable_pass"))
  rows.append({"unit_id":u["unit_id"],"source_task_id":source,"future_task_id":future,
   "repository":u["task_family"],"source_task_sha256":task_hash,"future_task_sha256":future_hash,
   "official_config_sha256":carrier["config"]["sha256"],"static":static,"runtime":runtime,
   "preflight_valid":valid,"invalid_reason":None if valid else runtime["reason"]})
 valid=[r for r in rows if r["preflight_valid"]]
 schedule=[{"sequence":i,"source_task_id":r["source_task_id"],"future_task_id":r["future_task_id"],
            "repository":r["repository"],"logical_attempts":1,"selected_memory":"","future_task_executed":False,
            "writer_calls":0} for i,r in enumerate(valid,1)]
 preflight_status="T0_RUNTIME_PREFLIGHT_PASS" if len(valid)>=6 else "HOLD_FRESH_RUNTIME_SUPPORT_INSUFFICIENT"
 contract={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"FROZEN_BEFORE_SOURCE_POLICY",
  "provider_binding_sha256":sha256_file(Q0/"provider-binding.json"),
  "qualification_result_sha256":sha256_file(Q0/"qualification-result.json"),
  "source_acquisition_contract_sha256":sha256_file(Q0/"source-acquisition-contract.json"),
  "requested_model":binding["requested_model"],"resolved_model":binding["resolved_model"],
  "enable_thinking":False,"output_token_budget":q["frozen_output_token_budget"],"temperature":0.0,
  "provider_retries":0,"logical_attempts_per_source":1,"replacement":False,"top_up":False,
  "selected_memory":"","official_commit":OFFICIAL_COMMIT,"carrier_files":carrier,
  "fixed_pairs":[{"source":a,"future":b} for a,b in PAIRS],
  "forbidden":["writer","binder","shadow","gate","random_gate","final","future_policy","future_evaluator","other_model","R10"]}
 preflight={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":preflight_status,
  "valid_source_units":len(valid),"total_source_units":11,"carrier":carrier,"rows":rows,
  "source_model_calls":0,"future_task_executions":0,"writer_calls":0}
 acquisition={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),
  "status":"FROZEN" if len(valid)>=6 else "NOT_REALIZED_RUNTIME_SUPPORT_INSUFFICIENT",
  "schedule":schedule,"scheduled_count":len(schedule),"selection":"all preflight-valid units; no six-unit selection",
  "outcome_blind":True,"replacement":False,"top_up":False,"source_model_calls":0,
  "future_task_executions":0,"writer_calls":0}
 atomic_json(t0/"contract.json",contract);atomic_json(t0/"runtime-preflight.json",preflight);atomic_json(t0/"acquisition-schedule.json",acquisition)
 # This audited run has zero supported source containers; fail closed before model calls.
 if len(valid)>=6:raise RuntimeError("SOURCE_ACQUISITION_PATH_NOT_REACHED_IN_THIS_RUNTIME")
 gate="HOLD_FRESH_RUNTIME_SUPPORT_INSUFFICIENT"
 audit={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":gate,
  "N_preflight_valid":len(valid),"N_valid_trajectory":0,"N_valid_repository":0,
  "full_6_plus_5_design_recoverable":False,"source_logical_attempts":0,
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9"}
 closure={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":gate,
  "failure_layer":"fresh runtime/container substrate support before source-policy calls",
  "provider_qualification":"PASS","source_runtime_preflight":f"{len(valid)}/11",
  "source_logical_attempts":"0/11","trajectory_backed_valid":0,"valid_repositories":0,
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,
  "future_task_executions":0,"PACTA_mechanism_update":"NONE",
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9",
  "strongest_failure_differential":"Qwen397 provider/action interface qualified, but none of the fixed SWE-bench source images is locally available; no source trajectory or PACTA mechanism call was made."}
 atomic_json(t0/"support-audit.json",audit);atomic_json(t0/"closure.json",closure)
 copies={
  "c1-pacta-rb-qwen397-q0-provider-binding-v2-20260831.json":binding,
  "c1-pacta-rb-qwen397-q0-action-qualification-v2-20260831.json":q,
  "c1-pacta-rb-qwen397-t0-contract-20260831.json":contract,
  "c1-pacta-rb-qwen397-t0-runtime-preflight-20260831.json":preflight,
  "c1-pacta-rb-qwen397-t0-acquisition-schedule-20260831.json":acquisition,
  "c1-pacta-rb-qwen397-t0-support-audit-20260831.json":audit,
  "c1-pacta-rb-qwen397-t0-closure-20260831.json":closure,
 }
 for name,payload in copies.items():atomic_json(PAPER/name,payload)
 os_asset={"schema_version":1,"asset_id":"c1-pacta-rb-qwen397-t0-source-trajectory-acquisition-20260831",
  "created_at_utc":now(),"decision":gate,"belief_update":"No PACTA mechanism update; stopped before source-policy calls.",
  "lessons":[
   "A planned native source ID is not a native source trajectory. A writer-ready experience requires persisted trajectory bytes, an exact rendering contract, and content-addressed provenance.",
   "ReasoningBank exposes native SUCCESSFUL_SI and FAILED_SI induction instructions over the same Query + Trajectory input. PACTA may use them as a controlled writer-branch intervention, but this must not be described as ReasoningBank's natural branch selection or as pure reward-bit causality.",
   "Runtime/container support is distinct from provider/action-interface support and from PACTA mechanism evidence."],
  "call_counts":{"source_policy":0,"writer":0,"binder":0,"shadow":0,"final":0,"future_task":0},
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9",
  "reopen_conditions":["Provide at least six of the fixed eleven exact SWE-bench source images with audited digests and base commits, then obtain new human authorization for T0 acquisition."]}
 atomic_json(OS_PATH,os_asset)
 print(canonical({"status":gate,"preflight_valid":len(valid),"source_calls":0,"writer_calls":0}))
if __name__=="__main__":main()
