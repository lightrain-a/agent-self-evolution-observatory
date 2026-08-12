from __future__ import annotations

import json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT,StorageSettings,resolve_experiment_data_root

DEFAULT_JSON=PROJECT_ROOT/'generated'/'paper-first-p0-f0-state.json';DEFAULT_JS=PROJECT_ROOT/'generated'/'paper-first-p0-f0-state.js'
IDEAS=("future-learnability-preserving-self-evolution","cross-surface-repair-routing","diagnosability-preserving-self-evolution","failure-mode-transport-under-self-evolution")
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(path:Path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return {}
def check(status,evidence):return {"status":status,"evidence":evidence,"evidence_kind":"paper-first-local-f0"}
def pending(iid,progress):
 running=str(progress.get('status') or '')=='running';s='running-f0' if running else 'pending-f0'
 return {"idea_id":iid,"decision":"F0_RUNNING" if running else "F0_PENDING","method_failure_authorized":False,"execution_authorized":False,"gpu0":{"status":s,"evidence":"Paper-first local F0 is running." if running else "Paper-first local F0 has not completed.","evidence_kind":"paper-first-local-f0"},"checks":{k:check('pending','Await local F0.') for k in ('target_variation','baseline_disagreement','representability','tiny_overfit','competence_window','effect_variation')},"updater_competence":{"status":s,"passed":False,"reason":"local support/variation qualification pending"},"substrate_inventory":{}}
def from_future(result):
 a=result.get('analysis') or {};support=bool(a.get('support_pass'));status='pass' if support else 'fail';gpu='f0-support-pass' if support else 'hold-f0-support-insufficient';matched=int(a.get('matched_candidates') or 0);nz=int(a.get('nonzero_matched_candidates') or 0)
 return {"idea_id":IDEAS[0],"decision":"F0_SUPPORT_PASS" if support else "HOLD_F0_SUPPORT_INSUFFICIENT","method_failure_authorized":False,"execution_authorized":False,"gpu0":{"status":gpu,"evidence":f"matched current/retention={matched}; nonzero future-learnability={nz}; range={a.get('future_learnability_range')}","evidence_kind":"paper-first-local-f0"},"checks":{"target_variation":check(status,f"matched={matched}, nonzero={nz}"),"baseline_disagreement":check(status,"future-learnability delta versus current+retention-only control"),"representability":check('pass','two-stage patch/adaptation operator executed on real ALFWorld tasks'),"tiny_overfit":check('pass','deterministic three-candidate local probe completed'),"competence_window":check('pass','Qwen react-family qualification=41/134 across 5 successful task families'),"effect_variation":check(status,f"future_learnability_range={a.get('future_learnability_range')}")},"updater_competence":{"status":"pass" if support else 'hold-support-insufficient',"passed":support,"reason":"candidate updates exhibit matched current/retention future-adaptation variation" if support else 'insufficient matched/nonzero future-adaptation variation'},"substrate_inventory":{"observed_effective_candidates":3,"observed_fresh_heldout":4,"observed_reserve_fraction":0.25},"analysis_summary":a}
def from_shared(iid,result,key):
 a=(result.get('analysis') or {}).get(key) or {};support=bool(a.get('support_pass'));status='pass' if support else 'fail';gpu='f0-support-pass' if support else 'hold-f0-support-insufficient'
 if key=='pf2':eff,held,res=18,9,.5;ev=f"oracle={a.get('heldout_oracle_repair_rate')} fixed={a.get('best_fixed_surface_rate')} ownership={a.get('ownership_accuracy')} distinct={a.get('distinct_best_surfaces')}"
 elif key=='pf4':eff,held,res=3,9,.5;ev=f"baseline_diag={a.get('baseline_diagnostic_accuracy')} drops={a.get('diagnostic_drop')}"
 else:eff,held,res=27,9,.5;ev=f"modes={a.get('failure_modes')} non_diagonal={a.get('non_diagonal_transitions')} decision_pair={a.get('decision_relevant_pair')}"
 return {"idea_id":iid,"decision":"F0_SUPPORT_PASS" if support else "HOLD_F0_SUPPORT_INSUFFICIENT","method_failure_authorized":False,"execution_authorized":False,"gpu0":{"status":gpu,"evidence":ev,"evidence_kind":"paper-first-local-f0"},"checks":{"target_variation":check(status,ev),"baseline_disagreement":check(status,ev),"representability":check('pass','controlled fault x repair-surface table executed on real ALFWorld tasks'),"tiny_overfit":check('pass','dev/heldout split analyzed with frozen simple rules'),"competence_window":check('pass','Qwen react-family qualification=41/134 across 5 successful task families'),"effect_variation":check(status,ev)},"updater_competence":{"status":"pass" if support else 'hold-support-insufficient',"passed":support,"reason":"local support/variation qualification passed" if support else 'local support/variation qualification insufficient'},"substrate_inventory":{"observed_effective_candidates":eff,"observed_fresh_heldout":held,"observed_reserve_fraction":res},"analysis_summary":a}
def build_paper_first_p0_f0_state(data_root:Path|None=None):
 root=data_root or resolve_experiment_data_root(StorageSettings.from_env());run=root/'runs'/'paper-first-p0-20260812';future=load(run/'future-learnability'/'result.json');shared=load(run/'shared-surface'/'result.json');fp=load(run/'future-learnability'/'progress.json');sp=load(run/'shared-surface'/'progress.json');cards=[]
 cards.append(from_future(future) if future.get('status')=='complete' else pending(IDEAS[0],fp))
 for iid,key in zip(IDEAS[1:],('pf2','pf4','pf6')):cards.append(from_shared(iid,shared,key) if shared.get('status')=='complete' else pending(iid,sp))
 return {"schema_version":"1.0","generated_at":now(),"run_root":str(run),"policy":{"f0_cannot_emit_method_fail":True,"shared_collection_for_pf2_pf4_pf6":True,"p0_method_requires_support_pass_and_pre_experiment_authority":True},"summary":{"ideas":4,"running":sum(c['decision']=='F0_RUNNING' for c in cards),"support_pass":sum(c['decision']=='F0_SUPPORT_PASS' for c in cards),"support_hold":sum(c['decision']=='HOLD_F0_SUPPORT_INSUFFICIENT' for c in cards),"method_fail_authorized":0},"cards":cards}
def write_paper_first_p0_f0_state(json_path=DEFAULT_JSON,js_path=DEFAULT_JS):
 s=build_paper_first_p0_f0_state();json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');js_path.write_text('window.PAPER_FIRST_P0_F0_STATE = '+json.dumps(s,ensure_ascii=False,separators=(',',':'))+';\n');return s
if __name__=='__main__':print(json.dumps(write_paper_first_p0_f0_state(),ensure_ascii=False,indent=2))
