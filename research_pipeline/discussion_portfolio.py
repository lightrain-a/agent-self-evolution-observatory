from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "discussion-ready-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "discussion-ready-ideas.js"
TARGET = 20

SOURCES = (
    ("main-r2", PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", "passed_ideas", "external_verdict", "pass"),
    ("v4-r2", PROJECT_ROOT / "generated" / "idea-discovery-v4.json", "review_ranked_finalists", "external_verdict", "pass"),
    ("v5-r2", PROJECT_ROOT / "generated" / "idea-discovery-v5.json", "finalists", "external_verdict", "pass"),
    ("v51-r2", PROJECT_ROOT / "generated" / "idea-discovery-v51.json", "children", "external_verdict", "pass"),
    ("v52-r2", PROJECT_ROOT / "generated" / "idea-discovery-v52.json", "children", "external_verdict", "pass"),
    ("v53-r2", PROJECT_ROOT / "generated" / "idea-discovery-v53.json", "children", "external_verdict", "pass"),
)


def _load(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}


def build_discussion_portfolio() -> dict[str, Any]:
    rows=[]
    for source,path,key,verdict_key,wanted in SOURCES:
        payload=_load(path); candidates=payload.get(key) or ([] if key!="review_ranked_finalists" else payload.get("tournament_finalists",[]))
        for x in candidates:
            if x.get(verdict_key)!=wanted: continue
            rows.append({"source":source,"id":x.get("id"),"title":x.get("title",{}),"verdict":"pass","rank":x.get("external_rank") or x.get("rank"),"parent_ids":x.get("parent_ids") or ([x.get("parent_id")] if x.get("parent_id") else []),"reviewed":True})
    seen=set(); unique=[]
    for x in rows:
        key=(x["source"],x["id"])
        if key in seen: continue
        seen.add(key); unique.append(x)
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"target":TARGET,"count":len(unique),"remaining":max(0,TARGET-len(unique)),"ready":len(unique)>=TARGET,"policy":{"strict_external_pass_only":True,"supplementary_machine_school_not_counted":True,"revise_not_counted":True,"internal_shortlist_not_counted":True},"ideas":unique}


def write_discussion_portfolio(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    payload=build_discussion_portfolio();json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.DISCUSSION_READY_IDEAS = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return payload

if __name__=="__main__": print(json.dumps(write_discussion_portfolio(),ensure_ascii=False))
