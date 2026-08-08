from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT
from .r31_finalizer import DEFAULT_JSON as R31_JSON
from .r31_panel_review import DEFAULT_JSON as PANEL_JSON

DEFAULT_JSON = PROJECT_ROOT / "generated" / "r32-final-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "r32-final-ideas.js"
REPAIR_MODEL = "kimi-k3"
REVIEWER = "deepseek-v4-pro"


def _bi_schema() -> dict[str, Any]:
    return {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False}


def tool() -> list[dict[str, Any]]:
    bi=_bi_schema()
    props={
        "idea_id":{"type":"string"},"revision":{"type":"string"},"title":bi,"purpose":bi,"importance":bi,"core_idea":bi,
        "core_intuition":bi,"rationale":bi,"method_logic":bi,"persistent_update_object":{"type":"string"},"learning_signal":bi,
        "independent_ground_truth":bi,"strongest_baseline":bi,"matched_resources":{"type":"array","items":{"type":"string"}},
        "decisive_pilot":bi,"stop_condition":bi,"surviving_claim":bi,"collision_boundary":bi,"r3_repair_summary":bi,"remaining_risk":bi,
    }
    return [{"type":"function","name":"submit_repair","description":"Submit one targeted R3.2 page version.","parameters":{"type":"object","properties":{"idea":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}},"required":["idea"],"additionalProperties":False}}]


def prompt(page: dict[str, Any], review: dict[str, Any]) -> str:
    return f"""Act as a surgical ICLR revision editor. The page below was independently reviewed by DeepSeek V4 Pro after GLM-5.2 had passed it. Repair ONLY the material boundary identified by DeepSeek. Do not change unrelated mechanisms, datasets, or claims unless necessary for that boundary.

Rules:
1. Preserve the same real problem. For a prior BLOCK, a material mechanism repair is allowed, but do not drift to a different problem.
2. Implement every concrete item in `required_action` inside the method/pilot/stop contract, not merely in prose.
3. If the reviewer says a baseline is unfair, make it receive the same architecture/information/calibration/human-design budget as required.
4. If the reviewer says the pilot is circular or selected, replace it with a full-distribution or crossed design and keep any special subset only as a secondary diagnostic.
5. If the reviewer says a human prior confounds learning, add the exact human-prior baseline or remove human state design so the learned component is identifiable.
6. If the reviewer says a cap is arbitrary, remove it or add a preregistered sensitivity/coverage rule that kills the claim when the cap excludes material cases.
7. Add mechanically executable thresholds/margins when requested. The stop rule must state exactly when the claim dies or narrows.
8. Keep all matched-resource commitments from R3.1 and add the new matched item. Independent truth remains external/programmatic.
9. Revision must be `R3.2`. Return bilingual equivalent fields and call `submit_repair` exactly once.

Frozen R3.1 page:
{json.dumps(page, ensure_ascii=False, indent=2)}

DeepSeek review:
{json.dumps({k:review.get(k) for k in ['verdict','finding','required_action','mechanism_identifiability','simplification_challenge','baseline_fairness','pilot_decisiveness','decisive_falsifier']}, ensure_ascii=False, indent=2)}
"""


def _load() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ideas=json.loads(R31_JSON.read_text(encoding="utf-8")).get("ideas") or []
    reviews=json.loads(PANEL_JSON.read_text(encoding="utf-8")).get("reviews") or {}
    return ideas,reviews


def _validate(row: dict[str, Any], idea_id: str) -> None:
    if row.get("idea_id")!=idea_id or row.get("revision")!="R3.2": raise ValueError("bad id/revision")
    if len(row.get("matched_resources") or [])<6: raise ValueError("too few matched resources")
    for key in ("core_idea","method_logic","strongest_baseline","decisive_pilot","stop_condition","r3_repair_summary"):
        v=row.get(key) or {}
        if len(str(v.get("en") or ""))<30 or len(str(v.get("zh") or ""))<15: raise ValueError(f"weak {key}")


def build(*, limit: int | None=None) -> dict[str, Any]:
    r31,reviews=_load(); by_id={x['idea_id']:dict(x) for x in r31}
    nonpass=[]
    for x in r31:
        r=(reviews.get(x['idea_id']) or {}).get(REVIEWER)
        if r and r.get('verdict')!='pass': nonpass.append(x['idea_id'])
    existing={}
    if DEFAULT_JSON.exists():
        try:
            p=json.loads(DEFAULT_JSON.read_text(encoding='utf-8'))
            existing={x['idea_id']:x for x in p.get('ideas') or [] if x.get('revision')=='R3.2'}
        except Exception: pass
    todo=[i for i in nonpass if i not in existing]
    if limit is not None: todo=todo[:limit]
    client=ArkResponsesClient(); errors=[]
    for idea_id in todo:
        review=reviews[idea_id][REVIEWER]
        try:
            resp=client.respond(prompt(by_id[idea_id],review),model=REPAIR_MODEL,max_output_tokens=12000,tools=tool(),thinking='disabled')
            calls=[c for c in resp.get('function_calls',[]) if c.get('name')=='submit_repair']
            if len(calls)!=1: raise ValueError(f"expected one submit_repair, got {len(calls)}")
            row=json.loads(calls[0].get('arguments') or '{}').get('idea') or {}
            _validate(row,idea_id); row['repair_source_review']=review; row['repair_model']=REPAIR_MODEL; row['repair_usage']=resp.get('usage') or {}
            existing[idea_id]=row
        except Exception as e: errors.append({'idea_id':idea_id,'error':str(e)})
        payload=_payload(r31,nonpass,existing,errors); _write(payload)
    payload=_payload(r31,nonpass,existing,errors); _write(payload); return payload


def _payload(r31:list[dict[str,Any]],nonpass:list[str],existing:dict[str,dict[str,Any]],errors:list[dict[str,Any]])->dict[str,Any]:
    rows=[]
    for x in r31: rows.append(existing.get(x['idea_id'],x))
    return {'schema_version':'1.0','generated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'repair_model':REPAIR_MODEL,'source':'R3.1 + DeepSeek internal pre-audit','targeted_ids':nonpass,'summary':{'total':len(rows),'targeted':len(nonpass),'repaired':len(existing),'pending':len(nonpass)-len(existing)},'ideas':rows,'errors':errors}


def _write(payload:dict[str,Any])->None:
    DEFAULT_JSON.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    DEFAULT_JS.write_text('window.R32_FINAL_IDEAS = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=None);args=ap.parse_args();p=build(limit=args.limit);print(json.dumps(p['summary'],ensure_ascii=False));
    if p.get('errors'): print(json.dumps(p['errors'][-5:],ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
