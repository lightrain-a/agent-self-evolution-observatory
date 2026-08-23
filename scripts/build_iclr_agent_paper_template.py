#!/usr/bin/env python3
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.iclr_agent_paper_template import template_payload

GEN=ROOT/"generated"

def main()->None:
    payload=template_payload(); GEN.mkdir(parents=True,exist_ok=True)
    (GEN/"iclr-agent-paper-template.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (GEN/"iclr-agent-paper-template.js").write_text("window.ICLR_AGENT_PAPER_TEMPLATE = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    print(f"PASS {payload['template_id']} refs={len(payload['derived_from'])} lanes={len(payload['experiment_lanes'])} checklist={len(payload['final_checklist'])}")

if __name__=="__main__":main()
