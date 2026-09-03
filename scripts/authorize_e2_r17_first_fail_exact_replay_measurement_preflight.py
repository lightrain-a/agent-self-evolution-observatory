#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json,require,sha_file
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--group',choices=('rep1','rep2'),required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'measurement preflight auth exists')
 c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); g=next(x for x in c['state_groups'] if x['group']==a.group)
 d={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-preflight-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PREFLIGHT_ONLY_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract_path':str(a.contract),'contract_sha256':sha_file(a.contract),'group':a.group,'mindmemos_commit':c['mindmemos']['commit'],'parent_repair2_provenance':{'contract_path':g['parent_contract_path'],'contract_sha256':g['parent_contract_sha256'],'authorization_path':g['parent_authorization_path'],'authorization_sha256':g['parent_authorization_sha256']},'authority':{'measurement_only':True,'scientific_experiment':False,'updater':False,'analyzer':False,'provider_io':False,'paper_promotion':False,'submission':False},'execution_scope':{'measurement_child':'E2-R17-FIRST-FAIL-EXACT-REPLAY-MEASUREMENT','allowed_modes':['e1'],'allowed_task_ids':c['heldout_task_ids'],'exact_k':1,'allow_noninitial_skill':True,'learned_states':g['learned_states'],'provider_budget':{'required':True,'total_limit':191,'per_unit_limit':11},'required_resolved_model':c['actor']['resolved_model'],'identity_artifact_sha256':c['model_identity']['sha256'],'suite_manifest_sha256':c['suite']['suite_manifest_sha256'],'split_manifest_sha256':c['suite']['split_manifest_sha256'],'max_turns':c['actor']['max_turns'],'max_output_tokens':c['actor']['max_output_tokens']}}; atomic(a.output,d); print(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
