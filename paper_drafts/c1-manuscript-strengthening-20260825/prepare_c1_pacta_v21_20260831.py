from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
B3=Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json")
B4=Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json")
B10=Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
V2_CONTRACT=HERE/"c1-pacta-v2-contract-20260830.json"
V2_CLOSURE=HERE/"c1-pacta-v2-pilot-closure-20260830.json"
V2_RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1")
QUAL_RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-q0-measurement-20260831-v1")
RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-p0-measurement-repair-20260831-v1")
SPLIT_SALT="C1-PACTA-V21-PILOT-v1"
RANDOM_SALT="C1-PACTA-V21-RANDOM-GATE-v1"
CANDIDATE_BY_TEMPLATE={137:[354,355],138:[241,242],139:[269,270],156:[436,438],172:[508],211:[262]}
V2_STATES={352,239,271,437,506,261}
PRIOR_RUNS=[
 Path("/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1"),
 Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1"),
 Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-c1-20260830-confirmatory-v1"),
 Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-p0-fresh-7template-20260830-v1"),
 Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1"),
]

def now(): return datetime.now(timezone.utc).isoformat()
def sha_text(value): return hashlib.sha256(value.encode("utf-8")).hexdigest()
def sha_file(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def dump(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def write_jsonl(path,rows):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text("".join(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n" for row in rows),encoding="utf-8"); tmp.replace(path)
def require(value,message):
 if not value: raise RuntimeError(message)
def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
def prior_outputs(run,task):
 if not run.exists(): return []
 needle=f"task-{task}__"; found=[]
 for folder in ("projection","binder","scb","shadow","per_case"):
  base=run/folder
  if base.exists(): found.extend(str(path) for path in base.glob(f"*{needle}*"))
 return sorted(found)

def main():
 candidates={task for tasks in CANDIDATE_BY_TEMPLATE.values() for task in tasks}
 require(len(candidates)==10 and len(CANDIDATE_BY_TEMPLATE)==6,"candidate geometry drift")
 require(not candidates & V2_STATES,"v2 sample overlap")
 require(not RUN.exists(),"v2.1 run already exists")
 v2=load(V2_CONTRACT); closure=load(V2_CLOSURE); v2_novelty=load(V2_RUN/"novelty-audit.json")
 require(closure["status"]=="STOP_FINAL_POLICY_MEASUREMENT_PARSER_FAILURE","v2 closure drift")
 require(v2_novelty["verdict"]=="PASS_NOVEL_RESIDUAL","v2 novelty authority drift")
 require(closure["claim_authority"]["method_status"]=="PACTA_V2_NOT_QUALIFIED_FINAL_EFFECT_UNMEASURED","v2 claim drift")
 b3,b4,b10=load(B3),load(B4),load(B10)
 retrieval={int(row["task_id"]):row for row in b3["all_rows"]}
 wrappers={(int(row["source_task"]),str(row["condition"])):row for row in b4["objects"]}
 sys.path.insert(0,str(b10["vendor_path"]))
 import pyarrow.parquet as pq
 parquet=Path(b10["source_bindings"]["parquet"]["path"]); require(sha_file(parquet)==b10["source_bindings"]["parquet"]["sha256"],"parquet drift")
 table={int(row["task_id"]):row for row in pq.read_table(parquet,columns=["task_id","task_prompt","trajectory_json"]).to_pylist()}
 pool=[]
 for template,tasks in sorted(CANDIDATE_BY_TEMPLATE.items()):
  for task in tasks:
   source=retrieval[task]
   require(int(source["intent_template_id"])==template,f"template drift {task}")
   require(bool(source["trajectory_available"]) and bool(source["threshold_hit"]),f"trajectory/retrieval failure {task}")
   raw=table[task]; trajectory=json.loads(str(raw["trajectory_json"])); step=(trajectory.get("steps") or {}).get("1")
   contents=((step.get("input_messages") or {}).get("contents") or []); system=str(contents[0].get("content") or ""); last=str(contents[-1].get("content") or "")
   marker="[Current state starts here]"; require(marker in last,f"state marker missing {task}"); state=last.split(marker,1)[1].strip()
   source_task=int(source["top1_source_task"]); prior=[]
   for run in PRIOR_RUNS: prior.extend(prior_outputs(run,task))
   require(not prior,f"prior scientific output {task}: {prior[:2]}")
   unit={"future_task":task,"intent_template_id":template,"selected_source_task":source_task,
         "trajectory_available":True,"retrieval_threshold_hit":True,"retrieval_similarity":source["top1_similarity"],
         "retrieval_margin":source["top1_margin"],"evaluator_class":source["evaluator_class"],
         "split_hash":sha_text(f"{SPLIT_SALT}|{template}|{task}"),"random_gate_hash":sha_text(f"{RANDOM_SALT}|{template}|{task}"),
         "task_prompt_sha256":sha_text(str(raw["task_prompt"])),"current_state_sha256":sha_text(state),
         "system_instruction_sha256":sha_text(system),"prior_scmb_or_pacta_outputs":[]}
   for branch in ("success","failure"):
    wrapper=wrappers[(source_task,branch)]; path=Path(wrapper["native_wrapper_path"])
    require(path.is_file() and sha_file(path)==wrapper["native_wrapper_sha256"],f"wrapper drift {source_task}/{branch}")
    unit[f"{branch}_memory_wrapper_path"]=str(path); unit[f"{branch}_memory_wrapper_sha256"]=wrapper["native_wrapper_sha256"]
   pool.append(unit)
 pilot=[min((unit for unit in pool if unit["intent_template_id"]==template),key=lambda unit:unit["split_hash"]) for template in sorted(CANDIDATE_BY_TEMPLATE)]
 expected=[354,242,270,438,508,262]; require([unit["future_task"] for unit in pilot]==expected,"selection drift")
 unused=[unit for unit in pool if unit not in pilot]; ranking=sorted(pilot,key=lambda unit:unit["random_gate_hash"])
 contract={
  "schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FROZEN_CONTRACT","status":"FROZEN_MEASUREMENT_ONLY_REPAIR",
  "experiment_id":"C1-PACTA-V21-MEASUREMENT-ONLY-REPAIR-PILOT-20260831",
  "lineage":{"PACTA_v2":"method/gate realized; final measurement lost because response was not persisted before strict envelope parsing",
             "v2_run_modified":False,"v2_states_excluded":sorted(V2_STATES),"v2_partial_responses_excluded":61},
  "method_frozen":{
   "scientific_object":v2["scientific_object"],"models":v2["models"],"scb":v2["scb"],"arms":v2["arms"],
   "observable":v2["observable"],"shadow_realization":v2["shadow_realization"],"gate_geometry":v2["gate_geometry"],
   "final_policy":v2["final_policy"],"pilot_gate":v2["pilot_gate"]
  },
  "measurement_only_repair":{
   "write_before_parse":["response_id","provider status","requested/resolved model","thinking fallback","usage","raw response","raw response SHA","prompt SHA","timestamp"],
   "parser":"strict full-envelope JSON first; on failure recover only the first complete action object with deterministic string-aware extraction",
   "validation":["exactly one tool key","args are a JSON object","tool belongs to frozen action schema"],
   "forbidden":["LLM repair","semantic guessing","next_goal inference","current_state inference","retry","top-up","replacement","imputation"]
  },
  "sample":{"pilot_states":6,"templates":6,"selection_salt":SPLIT_SALT},
  "random_gate":{"mechanism":"rate matched to realized PACTA gate-open K","salt":RANDOM_SALT,"ranking_frozen_before_shadow":True},
  "execution":{"binder_calls":12,"shadow_calls":144,"conditional_final_calls":288,"provider_retries":0},
  "adjudication":{"measurement_failure":"STOP_PACTA_ON_SHOPPING","gate_degenerate":"STOP_PACTA_ON_SHOPPING",
                  "qualified_A3_approx_A2":"PACTA_SELECTION_CRITERION_UNSUPPORTED",
                  "qualified_A3_lt_A2":"PACTA_MECHANISM_NEGATIVE_UNDER_QUALIFIED_TEST",
                  "pass":"PACTA_PRELIMINARY_MECHANISM_SIGNAL_THEN_STOP"},
  "same_substrate_confirmatory_authorized":False,"terminal_authorized":False,"R10_authorized":False
 }
 split={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FRESH_SPLIT","status":"FROZEN_OUTCOME_BLIND",
        "salt":SPLIT_SALT,"candidate_pool":pool,"pilot":pilot,"pilot_ids":expected,"unused_without_outcome_access":unused,"outcome_accessed_for_selection":False}
 random_artifact={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_RANDOM_GATE_RANKING","status":"FROZEN_BEFORE_SHADOW_OUTPUT",
                  "salt":RANDOM_SALT,"ranking":[{"rank":i,"future_task":u["future_task"],"intent_template_id":u["intent_template_id"],"sha256":u["random_gate_hash"]} for i,u in enumerate(ranking,1)],"K":"realized after complete shadow calibration"}
 freeze={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FREEZE","status":"FROZEN_BEFORE_QUALIFICATION_OR_PROVIDER_CALLS",
         "origin_main_sha":git("rev-parse","origin/main"),"design_parent_sha":git("rev-parse","HEAD"),"pilot_ids":expected,
         "method_identical_to_v2":True,"single_changed_layer":"measurement robustness","qualification_required":str(QUAL_RUN/"qualification.json"),
         "no_retry_topup_replacement_imputation":True}
 preflight={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_ZERO_PROVIDER_PREFLIGHT","status":"PASS",
            "checks":{"candidate_states":10,"templates":6,"pilot_states":6,"v2_sample_overlap":0,"prior_scmb_or_pacta_outputs":0,
                      "trajectory_available":"10/10","retrieval_threshold_hit":"10/10","wrapper_hashes_verified":"20/20","selection_recomputed":expected}}
 novelty={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_INHERITED_NOVELTY_AUTHORITY","verdict":"PASS_NOVEL_RESIDUAL",
          "basis":"PACTA-v2 mechanism is frozen; v2.1 changes measurement robustness only",
          "source_artifact":str(V2_RUN/"novelty-audit.json"),"source_sha256":sha_file(V2_RUN/"novelty-audit.json"),
          "new_mechanism_claim":False}
 RUN.mkdir(parents=True)
 for name,value in (("contract",contract),("split",split),("random-gate-ranking",random_artifact),("freeze",freeze),("preflight",preflight),("fresh-pool",{"pool":pool})):
  dump(HERE/f"c1-pacta-v21-{name}-20260831.json",value); dump(RUN/f"{name}.json",value)
 dump(RUN/"novelty-audit.json",novelty)
 input_rows=[]
 for unit in pilot:
  for branch in ("success","failure"):
   input_rows.append({"future_task":unit["future_task"],"intent_template_id":unit["intent_template_id"],"branch":branch,
    "system_sha256":unit["system_instruction_sha256"],"task_sha256":unit["task_prompt_sha256"],"state_sha256":unit["current_state_sha256"],
    "memory_sha256":unit[f"{branch}_memory_wrapper_sha256"]})
 write_jsonl(RUN/"input-index.jsonl",input_rows)
 dump(RUN/"manifest.json",{"schema_version":"1.0","run_id":RUN.name,"status":"FROZEN_AWAITING_MEASUREMENT_QUALIFICATION",
       "origin_main_sha":git("rev-parse","origin/main"),"design_git_sha":git("rev-parse","HEAD"),"pilot_ids":expected,
       "expected_binder_calls":12,"expected_shadow_calls":144,"conditional_final_calls":288,"created_at":now()})
 print(json.dumps({"status":"PREPARED","pilot_ids":expected,"random_ranking":[u["future_task"] for u in ranking],"run":str(RUN)}))
 return 0
if __name__=="__main__": raise SystemExit(main())
