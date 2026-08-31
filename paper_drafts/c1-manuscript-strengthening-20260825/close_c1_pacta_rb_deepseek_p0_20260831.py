from __future__ import annotations
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-q0-20260831-v1")
P0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1")
RESPONSE=Q0/"responses/budget-900__fixture-01.json"
REQ="deepseek-v4-pro";EXPECTED="deepseek-v4-pro-260425"
now=lambda:datetime.now(timezone.utc).replace(microsecond=0).isoformat()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
shaf=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);y=dict(x);y["payload_sha256"]=sha(canon(x));t=p.with_suffix(p.suffix+".tmp")
 with t.open("w",encoding="utf-8") as f:f.write(json.dumps(y,ensure_ascii=False,indent=2,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
 t.replace(p)
def load(p):return json.loads(Path(p).read_text())
def git(*a):return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()

def main():
 r=load(RESPONSE)
 assert r["requested_model"]==REQ and r["resolved_model"]!=EXPECTED
 assert r["persisted_before_parse"] is True and r["status"]=="completed" and r["raw_response"]
 head=git("rev-parse","HEAD");live=git("rev-parse","origin/main")
 binding={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "status":"STOP_MODEL_BINDING","expected_requested_model":REQ,"expected_resolved_model":EXPECTED,
  "requested_model":r["requested_model"],"resolved_model":r["resolved_model"],"case_id":r["case_id"],
  "response_artifact":str(RESPONSE),"response_artifact_sha256":shaf(RESPONSE),
  "provider_status":r["status"],"raw_response_persisted_before_parse":True,
  "thinking_requested":"disabled","thinking_compatibility_fallback":False,
  "scientific_provider_calls":0,"substitution_attempted":False,"fallback_attempted":False}
 availability={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "status":"NOT_RUN_DUE_STOP_MODEL_BINDING","qualification_fixture_calls_returned":1,
  "budget_ladder":[900,1200,1600,2048],"selected_scientific_max_output_tokens":None,
  "action_availability_adjudicated":False,"stop_precedence":"exact model binding precedes action availability",
  "scientific_provider_calls":0,"no_rescue":True}
 claim={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "verdict":"STOP_MODEL_BINDING","PACTA_method_claim_authority":"NO_NEW_SCIENTIFIC_EVIDENCE",
  "carrier_qualification":"pre-provider infrastructure PASS","novelty":"NOVELTY_RESIDUAL_INHERITED_CARRIER_CLEAR",
  "model_realization":"FAIL exact resolved identity","writer_twin_realization":"NOT_RUN",
  "gate_realization":"NOT_RUN","selection_effect":"NOT_RUN","measurement":"NOT_RUN",
  "active_manuscript":"R9","R10_created":False,
  "larger_deepseek_only_confirmation_warranted":False,
  "reopen_condition":"human author supplies a provider route that resolves exactly to deepseek-v4-pro-260425 and separately authorizes a new prospective run"}
 closure={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "status":"STOP_MODEL_BINDING","live_origin_main":live,"scientific_execution_sha":head,
  "selected_carrier":"SWE-bench Verified / official MiniSWEAgent",
  "reused_provenance":{"official_commit":"ed80611788292ea739f1effd31f16c53823b8a0d",
   "carrier_branch":"origin/research/e1-stri-reasoningbank-p1-20260829"},
  "model":{"requested":REQ,"expected_resolved":EXPECTED,"actual_resolved":r["resolved_model"]},
  "scientific_budget":None,"action_availability":"NOT_RUN_DUE_STOP_MODEL_BINDING",
  "writer_twin_support_count":0,"fresh_candidate_pool_count":11,"selected_pilot_units":[],
  "binder_completion":"0/12","shadow_completion":"0/144","gate_geometry":None,
  "random_gate_geometry":None,"final_completion":"0/288","U":None,"primary_mean_A3_minus_A2":None,
  "sign_counts":None,"secondary":None,"M_open":None,"M_closed":None,
  "strongest_competing_explanation":"The configured alias pointed to a different dated DeepSeek deployment; no scientific result exists to explain.",
  "failure_differential":{"carrier":False,"collision":False,"provider_credentials":False,
   "exact_model_binding":True,"action_availability":"not_adjudicated","writer":"not_run",
   "binder":"not_run","shadow":"not_run","gate":"not_run","final_measurement":"not_run","terminal":"locked"},
  "pilot_verdict":"NOT_EXECUTED","method_claim_status":"PACTA_UNCHANGED_NO_UPDATE",
  "larger_confirmation_warranted":False,"active_manuscript":"R9",
  "scientific_provider_calls":0,"non_scientific_provider_calls":1,
  "terminal_executed":False,"same_carrier_confirmatory_executed":False}
 os_asset={"schema_version":1,"asset_id":"c1-pacta-rb-deepseek-model-binding-stop-20260831","created_at_utc":now(),
  "scientific_object":"PACTA-v2 on independent ReasoningBank carrier with exact DeepSeek V4 Pro binding",
  "decision":"STOP_MODEL_BINDING","belief_update":"No update to PACTA mechanism; failure occurred before action-availability or scientific execution.",
  "lessons":[
   "A requested model alias is not sufficient scientific identity; the resolved dated deployment must match the frozen contract.",
   "Carrier qualification, model realization, writer-twin realization, gate realization, and selection effect are separate claim layers.",
   "Shopping remains closed; ReasoningBank was an independent carrier attempt, not a Shopping rescue.",
   "Same-model writer/binder/shadow/final reduces cross-model confounding only when the exact model binding is realized.",
   "An existing method adapted from problem A must not be relabeled as novelty for problem B; novelty resides in the additional mechanism required by the adaptation failure."],
  "claim_authority":"No DeepSeek/ReasoningBank PACTA effect claim.","active_manuscript":"R9",
  "reopen_conditions":["exact requested/resolved identity available","new human authorization","new prospective run root; never resume this stopped run"]}
 dump(PAPER/"c1-pacta-rb-deepseek-model-binding-20260831.json",binding)
 dump(PAPER/"c1-pacta-rb-deepseek-action-availability-qualification-20260831.json",availability)
 dump(PAPER/"c1-pacta-rb-deepseek-claim-update-20260831.json",claim)
 dump(PAPER/"c1-pacta-rb-deepseek-pilot-closure-20260831.json",closure)
 dump(ROOT/"research_pipeline/c1_pacta_rb_deepseek_model_binding_stop_20260831.json",os_asset)
 dump(Q0/"action-availability-qualification.json",availability)
 qman=load(Q0/"manifest.json");qman.update({"status":"STOP_MODEL_BINDING","actual_resolved_model":r["resolved_model"],"scientific_provider_calls":0,"completed_at_utc":now()});dump(Q0/"manifest.json",qman)
 pman=load(P0/"manifest.json");pman.update({"status":"STOP_MODEL_BINDING","scientific_provider_calls":0,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_calls":0,"completed_at_utc":now()});dump(P0/"manifest.json",pman)
 dump(P0/"pilot-closure.json",closure);dump(P0/"claim-update.json",claim)
 print(json.dumps({"status":"STOP_MODEL_BINDING","actual_resolved":r["resolved_model"],"scientific_calls":0,"active_manuscript":"R9"}))
if __name__=="__main__":main()
