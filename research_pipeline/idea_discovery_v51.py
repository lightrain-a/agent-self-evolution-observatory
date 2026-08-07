from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_PROPOSALS_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v51-proposals.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v51.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "idea-discovery-v51.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v51-external-reviews.json"


def load_proposals(path: Path = DEFAULT_PROPOSALS_JSON) -> list[dict[str, Any]]:
    if not path.exists(): return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("children", []) if isinstance(payload, dict) else []
    return rows if isinstance(rows, list) else []


def _reviews(path: Path = DEFAULT_EXTERNAL_JSON) -> dict[str, list[dict[str, Any]]]:
    if not path.exists(): return {}
    try: payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}
    rows = payload.get("reviews", {})
    return rows if isinstance(rows, dict) else {}


def validate_child(x: dict[str, Any]) -> list[str]:
    errors=[]
    if not x.get("id") or not x.get("parent_id"): errors.append("missing id/parent")
    for field in ("title","problem","changed_assumption","exact_mechanism","learning_signal","independent_ground_truth","simplest_baseline","decisive_pilot","stop_condition"):
        v=x.get(field)
        if not isinstance(v,dict) or not v.get("zh") or not v.get("en"): errors.append(f"missing bilingual {field}")
    if not x.get("update_surface"): errors.append("missing update surface")
    if not x.get("repair_source"): errors.append("missing repair source")
    return errors


def build_idea_discovery_v51() -> dict[str, Any]:
    ext=_reviews(); rows=[]
    for raw in load_proposals():
        x=dict(raw); reviews=ext.get(x["id"],[]); latest=reviews[-1] if reviews else {}
        x["external_reviews"]=reviews; x["external_review_status"]="reviewed" if reviews else "pending"; x["external_verdict"]=latest.get("verdict","pending")
        x["external_finding"]=latest.get("finding",""); x["external_finding_zh"]=latest.get("finding_zh",""); x["external_required_action"]=latest.get("required_action",""); x["external_required_action_zh"]=latest.get("required_action_zh","")
        rows.append(x)
    order={"pass":0,"revise":1,"pending":2,"block":3}; rows.sort(key=lambda x:(order.get(x["external_verdict"],2),x.get("parent_rank",999),x["id"]))
    for rank,x in enumerate(rows,1): x["rank"]=rank
    reviewed=[x for x in rows if x["external_review_status"]=="reviewed"]
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"target_venue":"ICLR","policy":{"generated_only_from_review_vectors":True,"block_resubmission_without_material_change":False,"max_children_per_parent":2,"target_total_core_pass":20},"summary":{"children":len(rows),"reviewed":len(reviewed),"pending":len(rows)-len(reviewed),"pass":sum(x["external_verdict"]=="pass" for x in rows),"revise":sum(x["external_verdict"]=="revise" for x in rows),"block":sum(x["external_verdict"]=="block" for x in rows)},"children":rows}


def validate(payload: dict[str, Any]) -> list[str]:
    errors=[]; ids=set()
    for x in payload.get("children",[]):
        if x.get("id") in ids: errors.append(f"duplicate {x.get('id')}")
        ids.add(x.get("id")); errors.extend(f"{x.get('id')}: {e}" for e in validate_child(x))
    return errors


def write_idea_discovery_v51(json_path: Path=DEFAULT_JSON, js_path: Path=DEFAULT_JS) -> dict[str, Any]:
    payload=build_idea_discovery_v51(); errors=validate(payload)
    if errors: raise ValueError("Invalid v5.1 proposals:\n- "+"\n- ".join(errors))
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.IDEA_DISCOVERY_V51 = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return payload

if __name__=="__main__": print(json.dumps(write_idea_discovery_v51()["summary"],ensure_ascii=False))
