from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .p0_offline_evidence import e1

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-e1-edit-table-stop.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-e1-edit-table-stop.js"


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def build_state()->dict[str,Any]:
    root=resolve_experiment_data_root(StorageSettings.from_env())
    ev=e1(root)
    identifiable=bool(ev.get("identifiable")); workflows=int(ev.get("workflows") or 0); effective=int(ev.get("effective_workflows") or 0); unique=int(ev.get("uniquely_ranked_workflows") or 0)
    stop=(not identifiable) and workflows>0
    return {
      "schema_version":"1.0","generated_at":_now(),"idea_id":"workflow-generalization-certificate","code":"E-1",
      "scientific_scope":"current frozen 16-workflow paired edit-effect source table only",
      "source_table":{"workflows":workflows,"edits_per_workflow":int(ev.get("edits") or 0),"effective_workflows":effective,"uniquely_ranked_workflows":unique,"effective_fraction":float(ev.get("effective_fraction") or 0.0),"identifiable":identifiable},
      "decision":"STOP_CURRENT_EDIT_TABLE_RANKING_DEGENERATE" if stop else "HOLD_E1_TABLE_REVIEW",
      "current_substrate_stop_authorized":stop,"method_failure_authorized":False,"hidden_workflows_opened":False,"exact_method_stop_fired":False,
      "interpretation":"The current paired edit-effect table has insufficient within-workflow target/effect variation to identify a best-edit ranking policy. Hidden workflows must remain sealed. This stops the current source-table instantiation, not the Paired Edit-Effect Workflow Update Policy itself.",
      "next_action":"Do not open hidden workflows or train the E-1 ranker on this table. Reopen only after a newly frozen paired intervention table has genuine non-tied edit effects at the preregistered source gate; otherwise send E-1 to human pivot/drop review."}

def write_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    s=build_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_E1_EDIT_TABLE_STOP = "+json.dumps(s,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return s

if __name__=='__main__': print(json.dumps(write_state(),ensure_ascii=False,indent=2))
