from __future__ import annotations
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from .config import PROJECT_ROOT
from .human_terminal_state import build_human_terminal_state
from .p0_revived_c_f0 import run_c1_f0, run_c4_f0, run_c5_f0
from .p0_revived_d2_f0 import run_d2_f0
from .p0_revived_f1_f0 import run_f1_f0
from .p0_revived_f2_f0 import run_f2_f0
from .p0_revived_f3_f0 import run_f3_f0

DEFAULT_JSON=PROJECT_ROOT/'generated'/'p0-revived-batch-f0.json'
DEFAULT_JS=PROJECT_ROOT/'generated'/'p0-revived-batch-f0.js'
RUNNERS:dict[str,Callable[[],dict[str,Any]]]={
 'self-label-confidence-flow':run_c1_f0,'self-correction-collapse-detector':run_c4_f0,
 'intervention-validated-self-correction':run_c5_f0,'failure-frontier-curriculum':run_d2_f0,
 'world-model-error-gated-learning':run_f1_f0,'irreversible-action-counterfactuals':run_f2_f0,
 'recovery-conditioned-experience':run_f3_f0,
}
def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def build_revived_batch_f0():
 with ThreadPoolExecutor(max_workers=7) as pool:
  fut={iid:pool.submit(fn) for iid,fn in RUNNERS.items()}; fresh=[fut[iid].result() for iid in RUNNERS]
 by={r['idea_id']:r for r in fresh}; human=build_human_terminal_state(); parents=[]
 for iid,meta in human['parents'].items():
  if meta.get('terminal_state')!='p0': continue
  if iid in by:
   row=by[iid]; dec=row['decision']; disp='CPU-MICRO-P0: upstream substrate hold' if dec.startswith('HOLD') else ('CPU-MICRO-P0: matched-simplification stop' if dec.startswith('STOP_MATCHED') else 'CPU-MICRO-P0: signal continue')
   parents.append({'code':meta['code'],'idea_id':iid,'mode':'fresh-cpu-f0','decision':dec,'disposition':disp,'next_action':row['next_action']})
  else:
   dec=meta.get('p0_decision') or meta.get('p0_screening_decision') or 'REUSE_EXISTING_P0_EVIDENCE'
   parents.append({'code':meta['code'],'idea_id':iid,'mode':'reuse-existing-p0','decision':dec,'disposition':'REUSE: no duplicate compute','next_action':'Use frozen existing P0 evidence; do not rerun identical compute.'})
 parents.sort(key=lambda r:(r['code'].split('-')[0],int(r['code'].split('-')[1])))
 stops=sum(r['decision'].startswith('STOP_MATCHED') for r in fresh); holds=sum(r['decision'].startswith('HOLD') for r in fresh); cont=len(fresh)-stops-holds
 return {'schema_version':'1.0','generated_at':_now(),'policy':{'parent_batch_size':20,'duplicate_existing_p0_compute_forbidden':True,'fresh_revived_f0_parallel':True,'cpu_f0_cannot_emit_method_pass_fail':True,'substrate_missing_is_upstream_hold':True,'matched_simplification_stop_precedes_gpu':True},'summary':{'parent_p0':len(parents),'reused_existing_p0':sum(r['mode']=='reuse-existing-p0' for r in parents),'fresh_cpu_f0':len(fresh),'fresh_matched_simplification_stop':stops,'fresh_upstream_hold':holds,'fresh_signal_continue':cont,'gpu_queue_candidates_before_economy':cont},'revived':fresh,'parent_batch':parents}
def write_revived_batch_f0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS):
 state=build_revived_batch_f0(); json_path.parent.mkdir(parents=True,exist_ok=True); json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); js_path.write_text('window.P0_REVIVED_BATCH_F0 = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8'); return state
if __name__=='__main__': print(json.dumps(write_revived_batch_f0(),ensure_ascii=False,indent=2))
