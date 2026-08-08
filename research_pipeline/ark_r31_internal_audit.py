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

SOURCE = PROJECT_ROOT / "generated" / "ark-r31-repair-candidates-merged.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-r31-internal-audit.json"
DEFAULT_JUDGE = "glm-5.2"


def _tool(n: int) -> list[dict[str, Any]]:
    props = {
        "idea_id":{"type":"string"},
        "verdict":{"type":"string","enum":["advance","revise","block"]},
        "confidence":{"type":"string","enum":["high","medium","low"]},
        "problem_alignment":{"type":"integer","minimum":0,"maximum":5},
        "material_repair":{"type":"integer","minimum":0,"maximum":5},
        "simplification_resistance":{"type":"integer","minimum":0,"maximum":5},
        "persistent_learning":{"type":"integer","minimum":0,"maximum":5},
        "independent_truth":{"type":"integer","minimum":0,"maximum":5},
        "pilot_identifiability":{"type":"integer","minimum":0,"maximum":5},
        "finding":{"type":"string"},
        "required_action":{"type":"string"},
        "fatal_simplification":{"type":"string"},
    }
    return [{"type":"function","name":"submit_audit","description":"Submit strict internal R3.1 repair audits.","parameters":{"type":"object","properties":{"ideas":{"type":"array","minItems":n,"maxItems":n,"items":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}}},"required":["ideas"],"additionalProperties":False}}]


def _prompt(rows: list[dict[str, Any]], judge: str) -> str:
    r3={x["idea_id"]:x for x in build_r3_final_audit()["ideas"]}
    packets=[]
    for child in rows:
        parent=child["parent_id"]
        packets.append({"parent_id":parent,"original_r3_finding":r3[parent]["finding"],"original_r3_required_action":r3[parent]["required_action"],"child":child})
    return f"""Act as a strict ICLR R3.1 REPAIR AUDITOR. These children were generated after their parents received R3 REVISE. This is an internal mechanism audit before expensive fresh literature search.

Judge model: {judge}

ADVANCE only if the child actually closes the exact original R3 objection with no obvious remaining mechanism/simplification boundary. Do not reward complexity or wording changes.

Hard checks:
1. Problem alignment: the child still solves the parent's real problem.
2. Material repair: mechanism changed where R3 requested, not only the experiment.
3. Simplification resistance: strongest baseline gets THE SAME observations/features/labels/interventions/traces/verifier access/capacity/calls/tokens/optimization/wall-clock. If the proposal wins by denying baseline information, score 0 and REVISE/BLOCK.
4. Persistent learning: a frozen learned object persists and changes future behavior after evolution context is removed. A test-time scorer/search/evaluator alone is not enough.
5. Independent truth: final endpoint is external to learner/training judge.
6. Pilot identifiability: one decisive crossed/factorial comparison directly separates the claimed mechanism from strongest matched simplification.
7. Claim discipline: do not infer semantic novelty from a geometric/statistical certificate that proves less.

`advance` means ready for fresh official-source collision search, NOT final PASS. `revise` means one repairable boundary remains. `block` means the child is still reducible/circular/problem-drifted.

Call submit_audit exactly once and audit all {len(rows)} children.

Packets:
{json.dumps(packets,ensure_ascii=False,indent=2)}
"""


def run(judge: str = DEFAULT_JUDGE, batch_size: int = 4, max_workers: int = 2, only_ids: list[str] | None = None) -> dict[str, Any]:
    source=json.loads(SOURCE.read_text(encoding="utf-8")); children=source.get("repairs") or []
    wanted=set(only_ids or [])
    if wanted: children=[x for x in children if x.get("id") in wanted]
    batches=[children[i:i+batch_size] for i in range(0,len(children),batch_size)]
    def one(batch: list[dict[str,Any]]) -> dict[str,Any]:
        client=ArkResponsesClient()
        try:
            response=client.respond(_prompt(batch,judge),model=judge,max_output_tokens=9000,tools=_tool(len(batch)),thinking="disabled")
            calls=[x for x in response.get("function_calls",[]) if x.get("name")=="submit_audit"]
            if len(calls)!=1: raise ValueError(f"expected one submit_audit call, got {len(calls)}")
            obj=json.loads(calls[0].get("arguments") or "{}"); rows=obj.get("ideas") or []
            expected={x["id"] for x in batch}; got={x.get("idea_id") for x in rows}
            if expected != got: raise ValueError(f"ids mismatch expected={sorted(expected)} got={sorted(got)}")
            return {"valid":True,"ids":sorted(expected),"usage":response.get("usage") or {},"ideas":rows}
        except Exception as e:
            return {"valid":False,"ids":[x["id"] for x in batch],"error":str(e),"ideas":[]}
    jobs=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(one,b) for b in batches]
        for f in concurrent.futures.as_completed(futures): jobs.append(f.result())
    ideas=[]
    for job in jobs:
        if job["valid"]: ideas.extend(job["ideas"])
    by_id={x["idea_id"]:x for x in ideas}; ordered=[by_id[x["id"]] for x in children if x["id"] in by_id]
    counts={v:sum(x.get("verdict")==v for x in ordered) for v in ("advance","revise","block")}
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"judge":judge,"summary":{"total":len(children),"reviewed":len(ordered),**counts,"failed_batches":sum(not j["valid"] for j in jobs)},"jobs":jobs,"ideas":ordered}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--judge",default=DEFAULT_JUDGE); parser.add_argument("--ids",nargs="*",default=None); parser.add_argument("--batch-size",type=int,default=4); parser.add_argument("--max-workers",type=int,default=2); parser.add_argument("--json",type=Path,default=DEFAULT_JSON); args=parser.parse_args()
    payload=run(args.judge,args.batch_size,args.max_workers,args.ids); args.json.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(payload["summary"],ensure_ascii=False));
    for row in payload["ideas"]: print(row["idea_id"],row["verdict"],row["simplification_resistance"],row["finding"][:120])
    return 0


if __name__=="__main__": raise SystemExit(main())
