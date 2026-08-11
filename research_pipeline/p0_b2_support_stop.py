from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .p0_offline_evidence import memory_full

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b2-support-stop.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b2-support-stop.js"


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def build_state()->dict[str,Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env())
    mem=memory_full(root)
    controlled=int(mem.get("controlled_nonzero") or 0); required=30
    stop=mem.get("status")=="complete" and controlled<required
    return {
      "schema_version":"1.0","generated_at":_now(),"idea_id":"contradiction-preserving-consolidation","code":"B-2",
      "scientific_scope":"current Qwen/ALFWorld shared-memory evidence substrate only",
      "frozen_support_gate":{"required_reproducible_conclusion_change_cases":required,"current_controlled_nonzero_memory_effects":controlled,"current_full_units":int(mem.get("full_completed_units") or 0),"dedicated_conclusion_change_deletion_cases_available":0,"gate_pass":False},
      "decision":"STOP_CURRENT_SUBSTRATE_CONCLUSION_CHANGE_SUPPORT_INSUFFICIENT" if stop else "HOLD_B2_SUPPORT_REVIEW",
      "current_substrate_stop_authorized":stop,"method_failure_authorized":False,"exact_method_stop_fired":False,
      "interpretation":"The completed shared-memory table cannot satisfy B-2's frozen >=30 reproducible conclusion-change deletion-case prerequisite. Its controlled-nonzero memory effects are only supporting reality evidence and are not automatically conclusion-change cores. Stop this substrate/data instantiation without calling the B-2 method a failure.",
      "next_action":"Do not open hidden E_orig or train a B-2 selector on this table. Reopen only with a fresh dedicated deletion-sensitivity collection that independently supplies >=30 reproducible conclusion-change cases; otherwise send B-2 to human pivot/drop review."}

def write_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    s=build_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_B2_SUPPORT_STOP = "+json.dumps(s,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return s

if __name__=='__main__': print(json.dumps(write_state(),ensure_ascii=False,indent=2))
