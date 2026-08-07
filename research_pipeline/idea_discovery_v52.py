from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_PROPOSALS_JSON=PROJECT_ROOT/"generated"/"idea-discovery-v52-proposals.json"
DEFAULT_JSON=PROJECT_ROOT/"generated"/"idea-discovery-v52.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"idea-discovery-v52.js"
DEFAULT_EXTERNAL_JSON=PROJECT_ROOT/"generated"/"idea-discovery-v52-external-reviews.json"


def _load(path:Path)->dict[str,Any]:
    if not path.exists(): return {}
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return {}


def build_idea_discovery_v52()->dict[str,Any]:
    props=_load(DEFAULT_PROPOSALS_JSON).get("children",[]); reviews=_load(DEFAULT_EXTERNAL_JSON).get("reviews",{}); rows=[]
    for raw in props:
        x=dict(raw);rs=reviews.get(x.get("id"),[]);r=rs[-1] if rs else {};x["external_reviews"]=rs;x["external_review_status"]="reviewed" if rs else "pending";x["external_verdict"]=r.get("verdict","pending");x["external_finding"]=r.get("finding","");x["external_finding_zh"]=r.get("finding_zh","");x["external_required_action"]=r.get("required_action","");x["external_required_action_zh"]=r.get("required_action_zh","");rows.append(x)
    order={"pass":0,"revise":1,"pending":2,"block":3};rows.sort(key=lambda x:(order.get(x["external_verdict"],2),x.get("parent_rank",999),x.get("id","")))
    for i,x in enumerate(rows,1):x["rank"]=i
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"target_venue":"ICLR","policy":{"only_from_v51_revise":True,"target_core_pass":20,"no_block_rename":True},"summary":{"children":len(rows),"reviewed":sum(x["external_review_status"]=="reviewed" for x in rows),"pending":sum(x["external_review_status"]!="reviewed" for x in rows),"pass":sum(x["external_verdict"]=="pass" for x in rows),"revise":sum(x["external_verdict"]=="revise" for x in rows),"block":sum(x["external_verdict"]=="block" for x in rows)},"children":rows}


def validate(p:dict[str,Any])->list[str]:
    errors=[];seen=set()
    for x in p.get("children",[]):
        if not x.get("id") or not x.get("parent_id"):errors.append("missing id/parent");continue
        if x["id"] in seen:errors.append(f"duplicate {x['id']}");seen.add(x["id"])
        for f in ("title","changed_assumption","exact_mechanism","independent_ground_truth","simplest_baseline","decisive_pilot","stop_condition","material_change"):
            v=x.get(f); 
            if not isinstance(v,dict) or not v.get("zh") or not v.get("en"):errors.append(f"{x['id']} missing {f}")
    return errors


def write_idea_discovery_v52(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    p=build_idea_discovery_v52();e=validate(p)
    if e:raise ValueError("Invalid v5.2:\n- "+"\n- ".join(e))
    json_path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");js_path.write_text("window.IDEA_DISCOVERY_V52 = "+json.dumps(p,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return p

if __name__=="__main__":print(json.dumps(write_idea_discovery_v52()["summary"],ensure_ascii=False))
