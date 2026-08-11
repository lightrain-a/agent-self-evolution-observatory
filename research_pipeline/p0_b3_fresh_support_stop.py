from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b3-fresh-support-stop.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b3-fresh-support-stop.js"
FAMILIES=("pick_and_place_simple","pick_clean_then_place_in_recep","pick_cool_then_place_in_recep","pick_heat_then_place_in_recep")

def _scenario(x:str)->str:
 x=x.split('/valid_unseen/',1)[-1];return x.split('/trial_',1)[0]

def build_state()->dict[str,Any]:
 root=resolve_experiment_data_root(StorageSettings.from_env()); run=root/"runs"/"p0-mem-xfer-support-enriched-qwen-v1"
 mem=[json.loads(x) for x in (run/"source-memories.jsonl").read_text(encoding='utf-8').splitlines() if x.strip()];old=json.loads((run/"plan.json").read_text(encoding='utf-8'))
 src={_scenario(str(x['source_task_id'])) for x in mem}; prior={_scenario(str(x['target_task_id'])) for x in old.get('units',[])}
 q=root/"qualification"/"qwen25-react-family-ood134-instruct"/"qualification-traces-full-134.jsonl"
 exposed=[json.loads(line) for line in q.read_text(encoding='utf-8').splitlines() if line.strip()];counts={};fresh_all=[]
 for fam in FAMILIES:
  allsc=sorted({_scenario(str(row['trace']['task_id'])) for row in exposed if str(row.get('family'))==fam})
  fresh=[x for x in allsc if x not in src and x not in prior]; counts[fam]={'all':len(allsc),'fresh':len(fresh),'fresh_scenarios':fresh};fresh_all+=fresh
 required=6; actual=len(set(fresh_all)); stop=actual<required
 return {'schema_version':'1.0','idea_id':'retrieval-interference-auditor','code':'B-3','freshness_contract':'exclude all source-memory scenarios, all previously observed full-support target scenarios, and duplicate target scenarios','required_unique_fresh_pair_targets':required,'available_unique_fresh_pair_targets':actual,'family_support':counts,'invalid_development_run':'p0-b3-real-cinteraction-qwen-v1','decision':'STOP_CURRENT_SUBSTRATE_FRESH_CINTERACTION_SUPPORT_INSUFFICIENT' if stop else 'FRESH_REALITY_SUPPORT_AVAILABLE','current_substrate_stop_authorized':stop,'method_failure_authorized':False,'interpretation':'The synthetic pathway screening signal cannot be promoted because ALFWorld has fewer outcome-unseen source-disjoint target scenarios than the frozen six-pair prevalence gate requires. Reusing prior targets or duplicate scenarios would invalidate the fresh-prevalence claim.','next_action':'Stop the current ALFWorld B-3 instance and send it to human pivot/drop review; reopen only on a fresh co-retrieval substrate with at least six independent unseen pair-target units.'}

def write_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
 s=build_state();json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');js_path.write_text('window.P0_B3_FRESH_SUPPORT_STOP = '+json.dumps(s,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');return s
if __name__=='__main__': print(json.dumps(write_state(),ensure_ascii=False,indent=2))
