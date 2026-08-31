from __future__ import annotations

import csv
import fcntl
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import run_c1_pacta_20260830 as legacy
from c1_pacta_v21_measurement import journal_provider_response, parse_journaled_response

RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-p0-measurement-repair-20260831-v1")
QUAL_RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-q0-measurement-20260831-v1")
B10=Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
MODEL="doubao-seed-2.0-mini"
RESOLVED="doubao-seed-2-0-mini-260215"
BRANCHES=("success","failure")
BLOCKS=(1,2)
ARMS=("A0_NATIVE","A1_SCB_ALWAYS","A2_RANDOM_RATE_MATCHED","A3_PACTA_V2")
REPS=6

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
def tv(left,right):
 require(bool(left) and bool(right),"TV requires non-empty samples")
 a,b=Counter(left),Counter(right); keys=set(a)|set(b)
 return 0.5*sum(abs(a[k]/len(left)-b[k]/len(right)) for k in keys)
def distribution(values): return dict(sorted(Counter(values).items()))

def materialize_states():
 b10=load(B10); split=load(RUN/"split.json"); units=split["pilot"]
 sys.path.insert(0,str(b10["vendor_path"]))
 import pyarrow.parquet as pq
 parquet=Path(b10["source_bindings"]["parquet"]["path"]); require(sha_file(parquet)==b10["source_bindings"]["parquet"]["sha256"],"parquet drift")
 table={int(r["task_id"]):r for r in pq.read_table(parquet,columns=["task_id","task_prompt","trajectory_json"]).to_pylist()}
 states={}
 for unit in units:
  tid=int(unit["future_task"]); row=table[tid]; task=str(row["task_prompt"]); require(sha_text(task)==unit["task_prompt_sha256"],f"task drift {tid}")
  tr=json.loads(str(row["trajectory_json"])); step=(tr.get("steps") or {}).get("1"); contents=((step.get("input_messages") or {}).get("contents") or [])
  system=str(contents[0].get("content") or ""); last=str(contents[-1].get("content") or ""); marker="[Current state starts here]"
  require(marker in last,f"state marker absent {tid}"); state=last.split(marker,1)[1].strip()
  require(sha_text(system)==unit["system_instruction_sha256"] and sha_text(state)==unit["current_state_sha256"],f"packet drift {tid}")
  memories={}
  for branch in BRANCHES:
   path=Path(unit[f"{branch}_memory_wrapper_path"]); require(path.is_file() and sha_file(path)==unit[f"{branch}_memory_wrapper_sha256"],f"memory drift {tid}/{branch}")
   memories[branch]=path.read_text(encoding="utf-8")
  states[tid]={"unit":unit,"system":system,"task":task,"state":state,"memory":memories}
 return states

def call_record(response,text):
 return {"requested_model":response.get("requested_model"),"resolved_model":response.get("resolved_model"),
         "thinking_compatibility_fallback":response.get("thinking_compatibility_fallback"),"response_id":response.get("response_id"),
         "provider_status":response.get("status"),"usage":response.get("usage") or {},"raw_response":text,
         "raw_response_sha256":sha_text(text),"completed_at":now()}

def execute_binder(client,states,contract):
 notes={}
 instruction=contract["method_frozen"]["scb"]["instruction"]
 for tid,state in states.items():
  notes[tid]={}
  for branch in BRANCHES:
   path=RUN/"binder"/f"task-{tid}__branch-{branch}.json"
   prompt=legacy.scb_prompt(instruction,state["memory"][branch],state["task"],state["state"])
   if path.exists():
    row=load(path); require(row["status"]=="complete" and row["prompt_sha256"]==sha_text(prompt),f"binder resume drift {tid}/{branch}")
   else:
    try:
     response,text=legacy.provider_call(client,prompt,180,0.0)
     row={"schema_version":"1.0","artifact_kind":"C1_PACTA_V2_FROZEN_R9_SCB","status":"complete","future_task":tid,"branch":branch,
          "prompt_sha256":sha_text(prompt),"memory_sha256":sha_text(state["memory"][branch]),"task_sha256":sha_text(state["task"]),
          "state_sha256":sha_text(state["state"]),"text":text.strip(),"text_sha256":sha_text(text.strip()),"word_count":len(text.split()),**call_record(response,text)}
    except Exception as exc:
     row={"status":"failed","future_task":tid,"branch":branch,"prompt_sha256":sha_text(prompt),"failure_type":type(exc).__name__,"failure":str(exc)[:2000],"completed_at":now()}
    dump(path,row)
   require(row["status"]=="complete",f"binder failure {tid}/{branch}")
   notes[tid][branch]=row["text"]
 rows=[load(p) for p in sorted((RUN/"binder").glob("*.json"))]
 require(len(rows)==12 and all(r["requested_model"]==MODEL and r["resolved_model"]==RESOLVED and r["thinking_compatibility_fallback"] is False for r in rows),"binder realization failure")
 dump(RUN/"binder-manifest.json",{"status":"FROZEN_COMPLETE_BEFORE_SHADOW","calls":12,"expected":12,
      "artifacts_sha256":sha_text("|".join(sha_file(p) for p in sorted((RUN/"binder").glob("*.json")))),"completed_at":now()})
 return notes

def freeze_shadow_schedule(states,notes):
 rows=[]
 for tid,state in states.items():
  unit=state["unit"]
  for branch in BRANCHES:
   prompt=legacy.policy_prompt(state["system"],state["task"],state["state"],state["memory"][branch],notes[tid][branch],False)
   for block in BLOCKS:
    for rollout in range(1,REPS+1):
     cid=f"task-{tid}__branch-{branch}__block-{block}__r{rollout}"
     rows.append({"case_id":cid,"future_task":tid,"intent_template_id":unit["intent_template_id"],"selected_source_task":unit["selected_source_task"],
                  "branch":branch,"block":block,"rollout":rollout,"prompt":prompt,"prompt_sha256":sha_text(prompt),
                  "system_sha256":sha_text(state["system"]),"task_sha256":sha_text(state["task"]),"state_sha256":sha_text(state["state"]),
                  "memory_sha256":sha_text(state["memory"][branch]),"scb_sha256":sha_text(notes[tid][branch])})
 rows.sort(key=lambda r:sha_text("C1-PACTA-V21-SHADOW-SCHEDULE-v1|"+r["case_id"]))
 for i,row in enumerate(rows,1): row["order"]=i
 require(len(rows)==144,"shadow geometry drift")
 schedule=RUN/"shadow-schedule.jsonl"
 if schedule.exists():
  old=[json.loads(x) for x in schedule.read_text(encoding="utf-8").splitlines() if x.strip()]
  require([x["prompt_sha256"] for x in old]==[x["prompt_sha256"] for x in rows],"shadow schedule drift")
 else: write_jsonl(schedule,rows)
 dump(RUN/"shadow-input-manifest.json",{"status":"FROZEN_BEFORE_ANY_SHADOW_OUTPUT","cases":144,"schedule_sha256":sha_file(schedule),"created_at":now()})
 return rows

def execute_cases(client,rows,folder,kind,expected):
 for row in rows:
  path=RUN/folder/f"{row['case_id']}.json"
  if path.exists():
   artifact=load(path)
   require(artifact["status"]=="complete" and artifact["prompt_sha256"]==row["prompt_sha256"],
           f"{kind} existing artifact is not resumable {row['case_id']}")
   continue
  response,text=legacy.provider_call(client,row["prompt"],900,0.2)
  request_fields={**row,"artifact_kind":kind}
  journal_provider_response(path,request_fields,response,text)
  artifact=parse_journaled_response(path)
  completed=len(list((RUN/folder).glob("*.json")))
  dump(RUN/f"{folder}-progress.json",{"status":"RUNNING" if artifact["status"]=="complete" else "STOP_ON_FIRST_FAILURE",
       "completed":completed,"expected":expected,"updated_at":now()})
  require(artifact["status"]=="complete",f"{kind} first action unparseable {row['case_id']}")
 cases=[load(p) for p in sorted((RUN/folder).glob("*.json"))]
 require(len(cases)==expected and all(c["status"]=="complete" for c in cases),f"{kind} incomplete")
 require(all(c["requested_model"]==MODEL and c["resolved_model"]==RESOLVED and c["thinking_compatibility_fallback"] is False for c in cases),f"{kind} model drift")
 dump(RUN/f"{folder}-progress.json",{"status":"COMPLETE","completed":expected,"expected":expected,"failed":0,"updated_at":now()})
 return cases

def realize_gate(states,cases):
 geometry={}
 for tid in states:
  sample={}
  for branch in BRANCHES:
   for block in BLOCKS:
    values=[c["action_signature"] for c in cases if c["future_task"]==tid and c["branch"]==branch and c["block"]==block]
    require(len(values)==6,f"shadow replicate drift {tid}/{branch}/{block}"); sample[(branch,block)]=values
  b1=tv(sample[("success",1)],sample[("failure",1)])
  b2=tv(sample[("success",2)],sample[("failure",2)])
  ws=tv(sample[("success",1)],sample[("success",2)])
  wf=tv(sample[("failure",1)],sample[("failure",2)])
  gate=min(b1,b2)>max(ws,wf)
  geometry[tid]={"future_task":tid,"intent_template_id":states[tid]["unit"]["intent_template_id"],"B1":b1,"B2":b2,"WS":ws,"WF":wf,
                 "cross_feedback_floor":min(b1,b2),"within_noise_ceiling":max(ws,wf),"G":gate,
                 "distributions":{"S1":distribution(sample[("success",1)]),"S2":distribution(sample[("success",2)]),
                                  "F1":distribution(sample[("failure",1)]),"F2":distribution(sample[("failure",2)])}}
 open_ids=[tid for tid,g in geometry.items() if g["G"]]
 dump(RUN/"gate-geometry.json",{"status":"REALIZED_FROM_COMPLETE_FROZEN_SHADOW","definition":"min(B1,B2) > max(WS,WF)",
      "open_count":len(open_ids),"closed_count":len(states)-len(open_ids),"open_ids":open_ids,"closed_ids":[tid for tid in states if tid not in open_ids],
      "states":list(geometry.values()),"shadow_calls":len(cases),"completed_at":now()})
 return geometry

def freeze_final_schedule(states,notes,geometry):
 ranking=load(RUN/"random-gate-ranking.json")["ranking"]; k=sum(g["G"] for g in geometry.values())
 random_open={r["future_task"] for r in ranking[:k]}; pacta_open={tid for tid,g in geometry.items() if g["G"]}
 dump(RUN/"random-gate-realization.json",{"status":"RATE_MATCHED_FROM_PREOUTPUT_FROZEN_RANKING","K":k,"open_ids":[r["future_task"] for r in ranking[:k]],
      "closed_ids":[r["future_task"] for r in ranking[k:]],"ranking_sha256":sha_file(RUN/"random-gate-ranking.json"),"realized_at":now()})
 rows=[]
 for tid,state in states.items():
  for arm in ARMS:
   use_scb=(arm=="A1_SCB_ALWAYS" or (arm=="A2_RANDOM_RATE_MATCHED" and tid in random_open) or (arm=="A3_PACTA_V2" and tid in pacta_open))
   for branch in BRANCHES:
    note=notes[tid][branch] if use_scb else None
    prompt=legacy.policy_prompt(state["system"],state["task"],state["state"],state["memory"][branch],note,False)
    for rollout in range(1,REPS+1):
     cid=f"task-{tid}__{arm}__branch-{branch}__r{rollout}"
     rows.append({"case_id":cid,"future_task":tid,"intent_template_id":state["unit"]["intent_template_id"],"arm":arm,"branch":branch,
                  "rollout":rollout,"uses_scb":use_scb,"PACTA_gate_open":tid in pacta_open,"random_gate_open":tid in random_open,
                  "prompt":prompt,"prompt_sha256":sha_text(prompt),"memory_sha256":sha_text(state["memory"][branch]),
                  "support_sha256":sha_text(note) if note else ""})
 rows.sort(key=lambda r:sha_text("C1-PACTA-V21-FINAL-POLICY-SCHEDULE-v1|"+r["case_id"]))
 for i,row in enumerate(rows,1): row["order"]=i
 require(len(rows)==288,"final schedule geometry drift")
 schedule=RUN/"final-policy-schedule.jsonl"; require(not schedule.exists(),"final schedule already exists before first realization")
 write_jsonl(schedule,rows); dump(RUN/"final-policy-input-manifest.json",{"status":"FROZEN_BEFORE_ANY_FINAL_POLICY_OUTPUT","cases":288,"schedule_sha256":sha_file(schedule),"K":k,"created_at":now()})
 return rows

def analyze(states,geometry,cases):
 per=[]
 for tid,state in states.items():
  row={"future_task":tid,"intent_template_id":state["unit"]["intent_template_id"],**{k:geometry[tid][k] for k in ("B1","B2","WS","WF","G")}}
  for arm in ARMS:
   success=[c["action_signature"] for c in cases if c["future_task"]==tid and c["arm"]==arm and c["branch"]=="success"]
   failure=[c["action_signature"] for c in cases if c["future_task"]==tid and c["arm"]==arm and c["branch"]=="failure"]
   require(len(success)==6 and len(failure)==6,f"final replicate drift {tid}/{arm}"); row[f"U_{arm}"]=tv(success,failure)
  row["D_select"]=row["U_A3_PACTA_V2"]-row["U_A2_RANDOM_RATE_MATCHED"]
  row["A3_minus_A1"]=row["U_A3_PACTA_V2"]-row["U_A1_SCB_ALWAYS"]
  row["A3_minus_A0"]=row["U_A3_PACTA_V2"]-row["U_A0_NATIVE"]
  row["A1_minus_A0"]=row["U_A1_SCB_ALWAYS"]-row["U_A0_NATIVE"]
  per.append(row)
 means={f"mean_U_{arm}":sum(r[f"U_{arm}"] for r in per)/len(per) for arm in ARMS}
 for key in ("D_select","A3_minus_A1","A3_minus_A0","A1_minus_A0"): means[f"mean_{key}"]=sum(r[key] for r in per)/len(per)
 pos=sum(r["D_select"]>0 for r in per); neg=sum(r["D_select"]<0 for r in per); zero=len(per)-pos-neg
 open_rows=[r for r in per if r["G"]]; closed_rows=[r for r in per if not r["G"]]
 m_open=sum(r["A1_minus_A0"] for r in open_rows)/len(open_rows); m_closed=sum(r["A1_minus_A0"] for r in closed_rows)/len(closed_rows)
 checks={"gate_non_degenerate_2_to_5":2<=len(open_rows)<=5,"final_policy_288_complete":len(cases)==288,
         "model_drift_zero":all(c["requested_model"]==MODEL and c["resolved_model"]==RESOLVED for c in cases),
         "mean_D_select_ge_0_05":means["mean_D_select"]>=0.05,"positive_state_count_gt_negative":pos>neg,
         "mean_A3_minus_A0_gt_zero":means["mean_A3_minus_A0"]>0,"mean_A3_minus_A1_ge_zero":means["mean_A3_minus_A1"]>=0}
 passed=all(checks.values())
 if passed:
  status="PACTA_PRELIMINARY_MECHANISM_SIGNAL"
 elif means["mean_D_select"] < 0:
  status="PACTA_MECHANISM_NEGATIVE_UNDER_QUALIFIED_TEST"
 else:
  status="PACTA_SELECTION_CRITERION_UNSUPPORTED"
 with (RUN/"pilot-per-state.csv").open("w",newline="",encoding="utf-8") as handle:
  writer=csv.DictWriter(handle,fieldnames=list(per[0])); writer.writeheader(); writer.writerows(per)
 result={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_PILOT_ANALYSIS","status":status,
         "execution":{"states":6,"templates":6,"binder_calls":12,"shadow_calls":144,"final_policy_calls":288,"model_drift":0,"parser_failure":0,
                      "confirmatory_executed":False,"terminal_executed":False},
         "gate_geometry":{"open_count":len(open_rows),"closed_count":len(closed_rows),"open_ids":[r["future_task"] for r in open_rows],"closed_ids":[r["future_task"] for r in closed_rows]},
         "effect_summary":means,"primary":{"contrast":"A3_PACTA_V2 - A2_RANDOM_RATE_MATCHED","mean_D_select":means["mean_D_select"],
                      "positive_states":pos,"negative_states":neg,"zero_states":zero},
         "secondary":{"mean_A3_minus_A1":means["mean_A3_minus_A1"],"mean_A3_minus_A0":means["mean_A3_minus_A0"]},
         "mechanism_diagnostic":{"M_open":m_open,"M_closed":m_closed,"M_open_minus_M_closed":m_open-m_closed,
             "definition":"statewise A1_SCB_ALWAYS minus A0_NATIVE grouped by frozen PACTA-v2 G"},
         "gate":{"checks":checks,"pass":passed,"thresholds_unchanged":True},"heterogeneity":per,
         "claim_boundary":"A passing six-template Pilot is preliminary one-substrate mechanism signal only; R9 remains active pending independent-carrier confirmation."}
 dump(RUN/"pilot-analysis.json",result)
 mechanism=("preliminary_one_substrate_signal" if passed else
            "negative_A3_below_rate_matched_random" if means["mean_D_select"] < 0 else
            "selection_criterion_unsupported")
 differential={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FAILURE_DIFFERENTIAL","pilot_status":status,
  "layers":{"execution":False,"provider":False,"shadow_realization":False,"gate_degeneracy":False,"measurement":False,
            "SCB_transport_surface":("positive" if means["mean_A1_minus_A0"]>0 else "nonpositive"),
            "paired_noise_calibrated_gate_mechanism":mechanism,"terminal_utility":"not_tested"},
  "strongest_competing_explanation":"Any A3 advantage could reflect which states receive SCB rather than paired counterfactual calibration; the pre-output rate-matched random gate is the primary control, but this remains a six-state one-substrate Pilot.",
  "comparisons":{"A3_minus_A2":means["mean_D_select"],"A3_minus_A1":means["mean_A3_minus_A1"],"A3_minus_A0":means["mean_A3_minus_A0"],"M_open_minus_M_closed":m_open-m_closed}}
 dump(RUN/"pilot-failure-differential.json",differential)
 return result

def prepolicy_stop(status,states,geometry,execution_sha):
 open_ids=[tid for tid,g in geometry.items() if g["G"]]
 analysis={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_PILOT_ANALYSIS","status":status,
           "execution":{"states":6,"binder_calls":12,"shadow_calls":144,"final_policy_calls":0,"confirmatory_executed":False,"terminal_executed":False},
           "gate_geometry":{"open_count":len(open_ids),"closed_count":6-len(open_ids),"open_ids":open_ids,"closed_ids":[tid for tid in states if tid not in open_ids]},
           "effect_summary":{f"mean_U_{arm}":None for arm in ARMS},"primary":{"mean_D_select":None},
           "claim_boundary":"Gate geometry failed the frozen identifiability screen; final policy evaluation was not authorized."}
 dump(RUN/"pilot-analysis.json",analysis)
 dump(RUN/"pilot-failure-differential.json",{"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FAILURE_DIFFERENTIAL","pilot_status":status,
      "layers":{"execution":False,"provider":False,"shadow_realization":False,"gate_degeneracy":True,"measurement":False,
                "paired_noise_calibrated_gate_mechanism":"not_qualified_gate_degenerate","terminal_utility":"not_tested"},
      "strongest_competing_explanation":"The cross-feedback signal relative to same-condition stochasticity did not yield a non-degenerate selective gate on this substrate."})
 dump(RUN/"final-verdict.json",{"status":"STOP_PACTA_ON_SHOPPING","reason":status,"method_claim_status":"PACTA_NOT_QUALIFIED","active_manuscript":"R9",
      "final_policy_executed":False,"confirmatory_executed":False,"terminal_executed":False,"execution_git_sha":execution_sha,"completed_at":now()})
 return analysis

def execution_stop(stage,exc,execution_sha):
 failed=[]
 for folder in ("binder","shadow","per_case"):
  for path in sorted((RUN/folder).glob("*.json")):
   row=load(path)
   if row.get("status") not in ("complete","SUPPORT_PASS"):
    failed.append({"path":str(path),"status":row.get("status"),"response_id":row.get("response_id"),
                   "raw_response_retained":isinstance(row.get("raw_response"),str),
                   "raw_response_sha256":row.get("raw_response_sha256"),"failure_type":row.get("failure_type")})
 measurement_failure=any(row["status"]=="failed_first_action_parser" for row in failed)
 reason="STOP_MEASUREMENT_FAILURE" if measurement_failure else "STOP_EXECUTION_OR_PROVIDER"
 result={"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_EXECUTION_STOP","status":"STOP_PACTA_ON_SHOPPING" if measurement_failure else reason,
         "reason":reason,"stage":stage,"failure_type":type(exc).__name__,"failure":str(exc)[:2000],
         "failed_artifacts":failed,"no_retry_topup_replacement_imputation":True,"execution_git_sha":execution_sha,
         "active_manuscript":"R9","confirmatory_executed":False,"terminal_executed":False,"completed_at":now()}
 dump(RUN/"pilot-analysis.json",result)
 dump(RUN/"pilot-failure-differential.json",{"schema_version":"1.0","artifact_kind":"C1_PACTA_V21_FAILURE_DIFFERENTIAL",
      "pilot_status":result["status"],"layers":{"execution":not measurement_failure,"provider":not measurement_failure,
      "shadow_realization":stage=="shadow","gate_degeneracy":False,"measurement":measurement_failure,
      "paired_noise_calibrated_gate_mechanism":"not_adjudicated","terminal_utility":"not_tested"},
      "failed_artifacts":failed,"strongest_competing_explanation":"The frozen mechanism cannot be adjudicated because the qualified execution did not produce a complete first-action measurement."})
 dump(RUN/"final-verdict.json",result)
 manifest=load(RUN/"manifest.json"); manifest.update({"status":result["status"],"stop_reason":reason,"completed_at":now()}); dump(RUN/"manifest.json",manifest)
 return result

def main():
 lock_path=RUN/".execution.lock"; lock_path.parent.mkdir(parents=True,exist_ok=True); lock=lock_path.open("a+"); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 require(git("status","--porcelain")=="","scientific execution worktree must be clean and committed")
 qualification=load(QUAL_RUN/"qualification.json")
 require(qualification["status"]=="PASS_MEASUREMENT_QUALIFICATION","measurement qualification did not pass")
 audit=load(RUN/"novelty-audit.json"); require(audit["verdict"]=="PASS_NOVEL_RESIDUAL","novelty audit closed")
 support=load(RUN/"model-support.json"); require(support["status"]=="SUPPORT_PASS" and support["resolved_model"]==RESOLVED,"support not qualified")
 contract=load(RUN/"contract.json"); execution_sha=git("rev-parse","HEAD"); states=materialize_states()
 manifest=load(RUN/"manifest.json"); manifest.update({"status":"SCIENTIFIC_EXECUTION_STARTED","execution_git_sha":execution_sha,"started_at":now()}); dump(RUN/"manifest.json",manifest)
 client,summary=legacy.client(); dump(RUN/"provider-summary.json",summary)
 try:
  notes=execute_binder(client,states,contract)
 except Exception as exc:
  result=execution_stop("binder",exc,execution_sha); print(json.dumps({"status":result["status"],"reason":result["reason"]})); return 0
 shadow_rows=freeze_shadow_schedule(states,notes)
 try:
  shadow=execute_cases(client,shadow_rows,"shadow","C1_PACTA_V21_SHADOW_POLICY_RESPONSE",144)
 except Exception as exc:
  result=execution_stop("shadow",exc,execution_sha); print(json.dumps({"status":result["status"],"reason":result["reason"]})); return 0
 geometry=realize_gate(states,shadow); open_count=sum(g["G"] for g in geometry.values())
 if not 2<=open_count<=5:
  result=prepolicy_stop("STOP_GATE_DEGENERATE",states,geometry,execution_sha); print(json.dumps({"status":"STOP_PACTA_ON_SHOPPING","reason":result["status"],"open_count":open_count,"final_policy_calls":0})); return 0
 final_rows=freeze_final_schedule(states,notes,geometry)
 try:
  final_cases=execute_cases(client,final_rows,"per_case","C1_PACTA_V21_FINAL_POLICY_RESPONSE",288)
 except Exception as exc:
  result=execution_stop("final_policy",exc,execution_sha); print(json.dumps({"status":result["status"],"reason":result["reason"]})); return 0
 result=analyze(states,geometry,final_cases)
 dump(RUN/"final-verdict.json",{"status":result["status"],"method_claim_status":"PRELIMINARY_ONE_SUBSTRATE_SIGNAL_ONLY" if result["gate"]["pass"] else result["status"],
      "active_manuscript":"R9","final_policy_executed":True,"confirmatory_executed":False,"terminal_executed":False,
      "execution_git_sha":execution_sha,"completed_at":now()})
 manifest=load(RUN/"manifest.json"); manifest.update({"status":result["status"],"completed_at":now(),"confirmatory_executed":False,"terminal_executed":False}); dump(RUN/"manifest.json",manifest)
 print(json.dumps({"status":result["status"],"open_count":open_count,"means":result["effect_summary"],"primary":result["primary"]}))
 return 0
if __name__=="__main__": raise SystemExit(main())
