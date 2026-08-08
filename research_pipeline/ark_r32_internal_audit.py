from __future__ import annotations

import argparse, concurrent.futures, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT

SOURCE = PROJECT_ROOT / "generated" / "ark-r32-repair-candidates.json"
R31_AUDITS = (
    PROJECT_ROOT / "generated" / "ark-r31-internal-audit.json",
    PROJECT_ROOT / "generated" / "ark-r31-internal-audit-missing.json",
)
DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-r32-internal-audit.json"
DEFAULT_JUDGE = "deepseek-v4-flash"


def _audit_map() -> dict[str, dict[str, Any]]:
    out={}
    for path in R31_AUDITS:
        if not path.exists(): continue
        p=json.loads(path.read_text(encoding="utf-8"))
        for row in p.get("ideas") or []: out[row["idea_id"]]=row
    return out


def _tool(n:int)->list[dict[str,Any]]:
    props={"idea_id":{"type":"string"},"verdict":{"type":"string","enum":["advance","revise","block"]},"confidence":{"type":"string","enum":["high","medium","low"]},"problem_alignment":{"type":"integer","minimum":0,"maximum":5},"material_repair":{"type":"integer","minimum":0,"maximum":5},"simplification_resistance":{"type":"integer","minimum":0,"maximum":5},"persistent_learning":{"type":"integer","minimum":0,"maximum":5},"independent_truth":{"type":"integer","minimum":0,"maximum":5},"pilot_identifiability":{"type":"integer","minimum":0,"maximum":5},"finding":{"type":"string"},"required_action":{"type":"string"},"fatal_simplification":{"type":"string"}}
    return [{"type":"function","name":"submit_audit","description":"Submit independent R3.2 mechanism audits.","parameters":{"type":"object","properties":{"ideas":{"type":"array","minItems":n,"maxItems":n,"items":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}}},"required":["ideas"],"additionalProperties":False}}]


def _prompt(batch:list[dict[str,Any]],judge:str)->str:
    audits=_audit_map(); packets=[]
    for child in batch:
        old=audits.get(child["r31_id"],{})
        packets.append({"r31_id":child["r31_id"],"remaining_boundary_finding":old.get("finding"),"required_action":old.get("required_action"),"fatal_simplification":old.get("fatal_simplification"),"r32_child":child})
    return f"""Act as an independent strict ICLR repair auditor. You are reviewing second-generation children produced by a different model after a first internal reviewer identified one remaining boundary.

Judge: {judge}
ADVANCE only if that exact remaining boundary is materially closed. Do not grant credit for prose, added complexity, or a baseline weakened by different information/capacity/budget. Require: problem alignment, real mechanism repair, same-information strongest simplification, frozen persistent learned object, independent final truth, and one decisive crossed/factorial falsifier. If the claimed contribution still reduces to generic regularization/constraint/representation packaging, REVISE. If circular or problem-drifted, BLOCK.

Call submit_audit exactly once for all {len(batch)} items.

Packets:
{json.dumps(packets,ensure_ascii=False,indent=2)}
"""


def run(judge:str=DEFAULT_JUDGE,batch_size:int=1,max_workers:int=3,only_ids:list[str]|None=None)->dict[str,Any]:
    children=json.loads(SOURCE.read_text(encoding="utf-8")).get("repairs") or []
    wanted=set(only_ids or [])
    if wanted: children=[x for x in children if x.get("id") in wanted]
    batches=[children[i:i+batch_size] for i in range(0,len(children),batch_size)]
    def one(batch:list[dict[str,Any]])->dict[str,Any]:
        try:
            r=ArkResponsesClient().respond(_prompt(batch,judge),model=judge,max_output_tokens=6000,tools=_tool(len(batch)),thinking="disabled")
            calls=[x for x in r.get("function_calls",[]) if x.get("name")=="submit_audit"]
            if len(calls)!=1: raise ValueError(f"expected one submit_audit call, got {len(calls)}")
            rows=(json.loads(calls[0].get("arguments") or "{}")).get("ideas") or []
            expected={x["id"] for x in batch}; got={x.get("idea_id") for x in rows}
            if expected!=got: raise ValueError(f"ids mismatch {expected} {got}")
            return {"valid":True,"ids":sorted(expected),"ideas":rows,"usage":r.get("usage") or {}}
        except Exception as e: return {"valid":False,"ids":[x["id"] for x in batch],"error":str(e),"ideas":[]}
    jobs=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        fs=[pool.submit(one,b) for b in batches]
        for f in concurrent.futures.as_completed(fs): jobs.append(f.result())
    found={row["idea_id"]:row for job in jobs if job["valid"] for row in job["ideas"]}; ordered=[found[x["id"]] for x in children if x["id"] in found]
    counts={v:sum(x["verdict"]==v for x in ordered) for v in ("advance","revise","block")}
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"judge":judge,"summary":{"total":len(children),"reviewed":len(ordered),**counts,"failed_batches":sum(not j["valid"] for j in jobs)},"jobs":jobs,"ideas":ordered}


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--judge",default=DEFAULT_JUDGE); p.add_argument("--ids",nargs="*",default=None); p.add_argument("--batch-size",type=int,default=1); p.add_argument("--max-workers",type=int,default=3); p.add_argument("--json",type=Path,default=DEFAULT_JSON); a=p.parse_args()
    out=run(a.judge,a.batch_size,a.max_workers,a.ids); a.json.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(out["summary"],ensure_ascii=False));
    for x in out["ideas"]: print(x["idea_id"],x["verdict"],x["simplification_resistance"],x["finding"][:120])
    return 0

if __name__=="__main__": raise SystemExit(main())
