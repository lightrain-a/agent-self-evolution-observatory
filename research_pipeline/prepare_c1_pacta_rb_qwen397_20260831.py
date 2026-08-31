from __future__ import annotations
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import (AA_BASE_URL,BUDGET_LADDER,FIRST_ACTION_RE,
 PILOT_SALT,RANDOM_SALT,atomic_json,canonical,pilot_split,sha256_file,sha256_text,validate_fresh_pool)

PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v1")
P0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-p0-20260831-v1")
DEEP=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1")
OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
EXP="C1-PACTA-RB-QWEN35-397B-P0-20260831"
OFFICIAL_COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
now=lambda:datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def git(*a):return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()
def glob_count(root:Path,patterns:list[str])->int:
 return sum(len(list(root.rglob(p))) for p in patterns)

def main():
 if Q0.exists() or P0.exists():raise RuntimeError("Qwen397 run roots already exist; no overwrite/resume")
 live=git("rev-parse","origin/main");head=git("rev-parse","HEAD")
 off=subprocess.check_output(["git","-C",str(OFFICIAL),"rev-parse","HEAD"],text=True).strip()
 if off!=OFFICIAL_COMMIT:raise RuntimeError("STOP_CARRIER_DRIFT")
 pool=json.loads((DEEP/"fresh-pool.json").read_text())
 units=pool["units"]
 historical_roots=list(Path("/data/wyt/agent-self-evolution-observatory/runs").glob("c1-pacta-rb-*"))
 prior_science=glob_count(Path("/data/wyt/agent-self-evolution-observatory/runs"),[
  "c1-pacta-rb-*/writer/*.json","c1-pacta-rb-*/binder/*.json","c1-pacta-rb-*/shadow/*.json","c1-pacta-rb-*/per_case/*.json"])
 freshness=validate_fresh_pool(units);split=pilot_split(units)
 current={
  "config":OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml",
  "agent":OFFICIAL/"third_party/src/minisweagent/agents/default.py",
  "writer":OFFICIAL/"third_party/src/minisweagent/memory/instruction.py",
  "retrieval":OFFICIAL/"third_party/src/minisweagent/memory/memory_management.py",
  "runner":OFFICIAL/"third_party/src/minisweagent/run/extra/swebench.py"}
 expected={"config":"d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41",
  "agent":"428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c",
  "writer":"08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae",
  "retrieval":"fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955",
  "runner":"8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951"}
 files={k:{"path":str(p),"sha256":sha256_file(p),"expected_sha256":expected[k],"pass":sha256_file(p)==expected[k]} for k,p in current.items()}
 if not all(x["pass"] for x in files.values()):raise RuntimeError("STOP_CARRIER_DRIFT")
 carrier={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"CARRIER_INTEGRITY_PASS",
  "carrier":"ReasoningBank + SWE-bench Verified + official MiniSWEAgent","official_commit":off,
  "implementation_files":files,"action_interface":{"surface":"one exactly fenced bash command",
   "parser_pattern":FIRST_ACTION_RE.pattern,"canonicalization":"strip exact captured UTF-8 command","llm_judge":False},
  "previous_c1_scientific_response_artifacts":prior_science,"substantive_drift":False}
 fresh={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":freshness["status"],
  "candidate_count":len(units),"candidate_repository_count":len({u["task_family"] for u in units}),
  "trajectory_backed_unit_count":freshness["valid_unit_count"],"trajectory_backed_repository_count":freshness["valid_repository_count"],
  "machine_checks":freshness["rows"],"units":units,"prior_scientific_response_artifacts":prior_science,
  "adjudication":("The 11 records are fresh source/future task-pair candidates, but none has a persisted "
   "source trajectory path/hash. They therefore are not legal inputs to the official success/failure writer."),
  "forbidden_repairs":["treat task text as trajectory","read gold patch as trajectory","add unapproved source-policy calls","replace units"]}
 ranked=sorted(({"unit_id":u["unit_id"],"rank":sha256_text(PILOT_SALT+"|"+u["unit_id"])} for u in units),key=lambda x:(x["rank"],x["unit_id"]))
 split_art={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":split["status"],
  "selection_salt":PILOT_SALT,"candidate_hash_order":ranked,"pilot":[],"sealed":[u["unit_id"] for u in units],
  "reason":"zero trajectory-backed eligible units; selection is not realized"}
 contract={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"FROZEN_PRE_SCIENCE",
  "target_model_family":"Qwen3.5-397B-A17B","provider":"典名词元 AA/OpenAI-compatible",
  "documented_endpoints":{"base":AA_BASE_URL,"models":"GET /models","chat":"POST /chat/completions",
   "docs":"https://api-doc.aa.com.cn/zh/docs/api"},
  "model_binding":{"discovery":True,"probes":3,"prefer_fixed_snapshot":True,"stable_alias_allowed_if_only_option":True,
   "fallback":False,"other_models_locked":True},"thinking":"prefer enable_thinking=false; record actual behavior",
  "action_qualification":{"fixtures":20,"budget_ladder":list(BUDGET_LADDER),"pass":"20/20 at smallest budget"},
  "token_hard_caps":{"scientific_input":5000000,"scientific_output":500000},
  "writer":{"calls":12,"temperature":0,"official_success_failure_branches_only":True},
  "scb":{"calls":12,"temperature":0,"browser_wording_removed":True},
  "shadow":{"calls":144,"temperature":.2,"gate":"min(B1,B2) > max(WS,WF)","nondegenerate":"2..5/6"},
  "random_gate":{"salt":RANDOM_SALT,"rate_matched":True},"final":{"calls":288,"temperature":.2},
  "primary":"U_A3_PACTA - U_A2_RATE_MATCHED_RANDOM","thresholds":{"mean":.05,"positive_gt_negative":True,"A3_A0_gt_0":True,"A3_A1_ge_0":True},
  "retries":0,"top_up":False,"replacement":False,"imputation":False,
  "locked":["terminal","Qwen3.5-122B","Qwen3.5-27B","Qwen3-235B","DeepSeek","second carrier","R10"]}
 provider={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"NOT_RUN_DUE_HOLD_FRESH_SUPPORT_INSUFFICIENT",
  "provider":"典名词元 AA/OpenAI-compatible","documented_base_url":AA_BASE_URL,
  "models_endpoint":"/models","chat_endpoint":"/chat/completions","credential_environment_key":"AA_API_KEY",
  "credential_configured":bool(os.environ.get("AA_API_KEY")),"models_discovery_calls":0,"identity_probe_calls":0,
  "requested_model":None,"resolved_model":None,"scientific_provider_calls":0}
 action={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"NOT_RUN_DUE_HOLD_FRESH_SUPPORT_INSUFFICIENT",
  "fixtures_planned":20,"budget_ladder":list(BUDGET_LADDER),"frozen_scientific_max_output_tokens":None,"calls":0}
 shadow={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"NOT_RUN","calls":"0/144","per_unit":[],"gate":None}
 analysis={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"NOT_EXECUTED",
  "writer":"0/12","binder":"0/12","shadow":"0/144","final":"0/288","U":None,"D_select":None,
  "effect_concentration":None,"terminal_executed":False,"second_model_executed":False}
 claim={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"NO_NEW_SCIENTIFIC_EVIDENCE",
  "failure_layer":"fresh source-trajectory provenance / carrier input realization","PACTA_mechanism_update":"NONE",
  "provider_realization":"NOT_TESTED","carrier_implementation":"PASS","writer_realization":"NOT_RUN","gate_realization":"NOT_RUN",
  "measurement":"NOT_RUN","selection_effect":"NOT_RUN","active_manuscript":"R9","R10":False,
  "reopen_condition":"Provide at least six fresh, independently sourced, content-addressed native ReasoningBank trajectories, or separately authorize prospective source-trajectory acquisition before a new run."}
 closure={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"status":"HOLD_FRESH_SUPPORT_INSUFFICIENT",
  "live_origin_main":live,"execution_sha":head,"provider_endpoint":AA_BASE_URL,"models_discovered":None,
  "model_binding":None,"thinking_mode":None,"scientific_output_budget":None,"action_qualification":"NOT_RUN",
  "scientific_tokens":{"input":0,"output":0,"estimated_cost":0},"carrier_provenance":carrier,
  "fresh_pool":{"candidates":11,"repositories":11,"trajectory_backed":0},"pilot_units":[],"sealed_count":11,
  "writer":"0/12","binder":"0/12","shadow":"0/144","gate":None,"random_gate":None,"final":"0/288",
  "U_A0":None,"U_A1":None,"U_A2":None,"U_A3":None,"mean_A3_A2":None,"signs":None,
  "A3_A1":None,"A3_A0":None,"M_open":None,"M_closed":None,"effect_concentration":None,
  "strongest_competing_explanation":"The prior 11-unit inventory counted planned task pairs as if native source trajectories already existed.",
  "pilot_verdict":"NOT_EXECUTED","claim_authority":"PACTA UNCHANGED; provenance failure before provider/science",
  "Qwen122_replication_warranted":False,"active_manuscript":"R9"}
 os_asset={"schema_version":1,"asset_id":"c1-pacta-rb-qwen397-fresh-trajectory-hold-20260831","created_at_utc":now(),
  "decision":"HOLD_FRESH_SUPPORT_INSUFFICIENT","belief_update":"No PACTA update; stopped before provider or scientific outcome access.",
  "lessons":["A fresh task pair is not a trajectory-backed ReasoningBank unit.","Writer validity requires persisted native trajectory bytes and hash before outcome-conditioned writer calls.",
   "Moving from DeepSeek to Qwen397 was prospectively frozen before any Qwen outcome; no model shopping occurred.",
   "Action-before-budget remains mandatory but was not reached.","Qwen397 remains the first planned backbone; Qwen122/27 remain locked.",
   "Rate-matched random gating remains the strongest final control."],
  "reopen_conditions":["six fresh content-addressed native trajectories","new prospective run","human authorization for trajectory acquisition if needed"],
  "active_manuscript":"R9"}
 artifacts={
  PAPER/"c1-pacta-rb-qwen397-provider-binding-20260831.json":provider,
  PAPER/"c1-pacta-rb-qwen397-action-availability-20260831.json":action,
  PAPER/"c1-pacta-rb-qwen397-carrier-audit-20260831.json":carrier,
  PAPER/"c1-pacta-rb-qwen397-fresh-pool-20260831.json":fresh,
  PAPER/"c1-pacta-rb-qwen397-pilot-split-20260831.json":split_art,
  PAPER/"c1-pacta-rb-qwen397-contract-20260831.json":contract,
  PAPER/"c1-pacta-rb-qwen397-shadow-gate-20260831.json":shadow,
  PAPER/"c1-pacta-rb-qwen397-pilot-analysis-20260831.json":analysis,
  PAPER/"c1-pacta-rb-qwen397-pilot-closure-20260831.json":closure,
  PAPER/"c1-pacta-rb-qwen397-claim-audit-20260831.json":claim,
  ROOT/"research_pipeline/c1_pacta_rb_qwen397_fresh_trajectory_hold_20260831.json":os_asset,
  Q0/"manifest.json":{"status":"HOLD_FRESH_SUPPORT_INSUFFICIENT","experiment_id":EXP,"created_at_utc":now(),"provider_calls":0,"scientific_calls":0},
  Q0/"provider-binding.json":provider,Q0/"action-availability.json":action,
  P0/"manifest.json":{"status":"HOLD_FRESH_SUPPORT_INSUFFICIENT","experiment_id":EXP,"created_at_utc":now(),"scientific_calls":0},
  P0/"contract.json":contract,P0/"fresh-pool.json":fresh,P0/"pilot-split.json":split_art,P0/"pilot-closure.json":closure}
 for p,v in artifacts.items():atomic_json(p,v)
 print(json.dumps({"status":closure["status"],"live_origin_main":live,"candidate_units":11,"trajectory_backed":0,"provider_calls":0}))

if __name__=="__main__":main()
