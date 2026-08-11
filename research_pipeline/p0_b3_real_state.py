from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b3-real-cinteraction.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b3-real-cinteraction.js"
RUN_ID="p0-b3-real-cinteraction-qwen-v1"

def _load(p:Path)->dict[str,Any]:
    try:return json.loads(p.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):return {}

def build_state()->dict[str,Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env()); run=root/"runs"/RUN_ID
    progress=_load(run/"progress.json"); decision=_load(run/"decision.json"); plan=_load(run/"plan.json"); invalid=_load(run/"INVALID_TARGET_OVERLAP_DEVELOPMENT_ONLY.json")
    complete=(not invalid) and progress.get('status')=='complete' and int(progress.get('completed_executions') or 0)==24 and bool(decision)
    status='invalid-development' if invalid else ('complete' if complete else ('running' if progress else 'missing'))
    return {'schema_version':'1.0','idea_id':'retrieval-interference-auditor','code':'B-3','run_id':RUN_ID,'status':status,'plan_hash':plan.get('plan_hash'),'progress':progress,'decision':decision if complete else None,'invalid_development':invalid or None,'method_failure_authorized':False,'scientific_role':'real co-retrieval phenomenon gate only; no pathway-method PASS authority'}

def write_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    s=build_state();json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');js_path.write_text('window.P0_B3_REAL_CINTERACTION = '+json.dumps(s,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');return s
if __name__=='__main__': print(json.dumps(write_state(),ensure_ascii=False,indent=2))
