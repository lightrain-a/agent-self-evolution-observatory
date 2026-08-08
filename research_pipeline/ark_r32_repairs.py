from __future__ import annotations

import argparse
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT
from .r3_final_audit import build_r3_final_audit

R31_SOURCE = PROJECT_ROOT / "generated" / "ark-r31-repair-candidates-merged.json"
AUDIT_SOURCES = (
    PROJECT_ROOT / "generated" / "ark-r31-internal-audit.json",
    PROJECT_ROOT / "generated" / "ark-r31-internal-audit-missing.json",
)
DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-r32-repair-candidates.json"
DEFAULT_MODEL = "glm-5.2"


def _audit_map() -> dict[str, dict[str, Any]]:
    out={}
    for path in AUDIT_SOURCES:
        if not path.exists(): continue
        p=json.loads(path.read_text(encoding="utf-8"))
        for row in p.get("ideas") or []: out[row["idea_id"]]=row
    return out


def _tool() -> list[dict[str, Any]]:
    bi={"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False}
    props={"parent_id":{"type":"string"},"r31_id":{"type":"string"},"id":{"type":"string"},"title":bi,"problem":bi,"importance":bi,"core_idea":bi,"material_change":bi,"method_logic":bi,"persistent_update_object":{"type":"string"},"learning_signal":bi,"independent_ground_truth":bi,"strongest_matched_baseline":bi,"shared_information_budget":bi,"decisive_pilot":bi,"stop_condition":bi,"surviving_claim":bi,"why_remaining_boundary_is_closed":bi,"remaining_risk":bi}
    return [{"type":"function","name":"submit_repair","description":"Submit one second-generation repair.","parameters":{"type":"object","properties":{"repair":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}},"required":["repair"],"additionalProperties":False}}]


def _prompt(packet: dict[str, Any]) -> str:
    return f"""Act as an ICLR mechanism designer performing a SECOND-GENERATION targeted repair.

The R3.1 child below was independently audited and has exactly one remaining repairable boundary. Fix that boundary without drifting from the original problem and without weakening the strongest baseline.

Rules:
1. Make the smallest material mechanism/identification change required by the audit.
2. If the audit requests an added baseline/factor/independent truth source, include it exactly.
3. The strongest baseline gets identical information, labels, traces, capacity, calls, tokens, optimization, and wall-clock wherever applicable.
4. Preserve a frozen persistent learned object; no hidden target-time relearning/search may masquerade as persistence.
5. Separate training labels from final evaluation truth whenever the audit identified circularity.
6. Do not invent citations or novelty claims; fresh collision search happens later.
7. New id must end in -r32. Preserve parent_id and r31_id exactly.
8. Call submit_repair exactly once. Bilingual English/Chinese output.

Packet:
{json.dumps(packet,ensure_ascii=False,indent=2)}
"""


def run(model: str=DEFAULT_MODEL, max_workers: int=3) -> dict[str, Any]:
    r31=json.loads(R31_SOURCE.read_text(encoding="utf-8")); audits=_audit_map(); r3={x["idea_id"]:x for x in build_r3_final_audit()["ideas"]}
    jobs=[]
    for child in r31.get("repairs") or []:
        audit=audits.get(child["id"])
        if not audit or audit.get("verdict")!="revise": continue
        jobs.append({"parent_id":child["parent_id"],"r31_id":child["id"],"original_r3_finding":r3[child["parent_id"]]["finding"],"original_r3_required_action":r3[child["parent_id"]]["required_action"],"r31_child":child,"r31_internal_finding":audit.get("finding"),"r31_required_action":audit.get("required_action"),"fatal_simplification":audit.get("fatal_simplification")})
    def one(packet: dict[str,Any]) -> dict[str,Any]:
        client=ArkResponsesClient()
        try:
            response=client.respond(_prompt(packet),model=model,max_output_tokens=7000,tools=_tool(),thinking="disabled")
            calls=[x for x in response.get("function_calls",[]) if x.get("name")=="submit_repair"]
            if len(calls)!=1: raise ValueError(f"expected one submit_repair call, got {len(calls)}")
            row=(json.loads(calls[0].get("arguments") or "{}")).get("repair") or {}
            if row.get("parent_id")!=packet["parent_id"] or row.get("r31_id")!=packet["r31_id"] or not str(row.get("id") or "").endswith("-r32"): raise ValueError("repair identity mismatch")
            return {"valid":True,"parent_id":packet["parent_id"],"usage":response.get("usage") or {},"repair":{"generator_model":model,**row}}
        except Exception as e: return {"valid":False,"parent_id":packet["parent_id"],"error":str(e)}
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(one,p) for p in jobs]
        for f in concurrent.futures.as_completed(futures): results.append(f.result())
    repairs=[r["repair"] for r in results if r["valid"]]
    by_parent={r["parent_id"]:r for r in repairs}; repairs=[by_parent[p["parent_id"]] for p in jobs if p["parent_id"] in by_parent]
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"generator_model":model,"summary":{"requested":len(jobs),"generated":len(repairs),"failed":sum(not r["valid"] for r in results)},"jobs":results,"repairs":repairs}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--model",default=DEFAULT_MODEL); parser.add_argument("--max-workers",type=int,default=3); parser.add_argument("--json",type=Path,default=DEFAULT_JSON); args=parser.parse_args()
    p=run(args.model,args.max_workers); args.json.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(p["summary"],ensure_ascii=False));
    for j in p["jobs"]:
        if not j["valid"]: print('FAIL',j["parent_id"],j.get('error'))
    return 0


if __name__=="__main__": raise SystemExit(main())
