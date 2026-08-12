from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT
SOURCE=Path(__file__).with_name('persistent_updater_program_final_20260812.json')
PUBLIC_JSON=PROJECT_ROOT/'generated'/'persistent-updater-program-final.json'
PUBLIC_JS=PROJECT_ROOT/'generated'/'persistent-updater-program-final.js'
def build_persistent_updater_program_final()->dict[str,Any]:
 row=json.loads(SOURCE.read_text(encoding='utf-8'))
 if row.get('verdict')!='STOP_CURRENT_PERSISTENT_UPDATER_PROGRAM':raise ValueError('persistent updater program final verdict must remain STOP')
 if row.get('batch_experiment_authorized') is not False or row.get('second_backbone_authorized') is not False:raise ValueError('terminal updater program cannot authorize batch or second backbone')
 if (row.get('final_ai_adjudication') or {}).get('web_gpt')!=row['verdict'] or (row.get('final_ai_adjudication') or {}).get('deepseek_v4_flash')!=row['verdict']:raise ValueError('final clinic must independently agree with terminal verdict')
 if (row.get('states') or {}).get('A2')!='KEEP_PROBLEM_HOLD_NO_QUALIFIED_UPDATER':raise ValueError('A2 must remain scientific HOLD, not method failure')
 return row
def write_persistent_updater_program_final(json_path:Path=PUBLIC_JSON,js_path:Path=PUBLIC_JS)->dict[str,Any]:
 row=build_persistent_updater_program_final();json_path.parent.mkdir(parents=True,exist_ok=True);json_path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');js_path.write_text('window.PERSISTENT_UPDATER_PROGRAM_FINAL = '+json.dumps(row,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');return row
