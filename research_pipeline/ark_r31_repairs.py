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

DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-r31-repair-candidates.json"
DEFAULT_MODELS = ("deepseek-v4-pro", "glm-5.2")
SOURCE_BANKS = (
    (PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", "passed_ideas"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v4.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v5.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v51.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v52.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v53.json", "children"),
)


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("en") or value.get("zh") or "")
    return str(value or "")


def _records() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path, key in SOURCE_BANKS:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get(key) or []
        if key == "all_candidates" and not rows:
            rows = payload.get("finalists") or payload.get("review_ranked_finalists") or []
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                out.setdefault(row["id"], row)
    return out


def _compact(record: dict[str, Any]) -> dict[str, Any]:
    review = (record.get("external_reviews") or [{}])[-1]
    return {
        "title": record.get("title"),
        "problem": record.get("purpose") or record.get("problem") or record.get("real_problem"),
        "importance": record.get("importance"),
        "core_idea": record.get("core_idea") or record.get("exact_mechanism"),
        "method_logic": record.get("method_logic") or record.get("exact_mechanism") or record.get("composition_logic"),
        "persistent_update_object": _text(record.get("persistent_update_object") or record.get("update_surface")),
        "learning_signal": record.get("learning_signal"),
        "independent_ground_truth": record.get("independent_ground_truth"),
        "strongest_baseline": record.get("strongest_baseline") or record.get("simplest_baseline") or review.get("strongest_baseline"),
        "decisive_pilot": record.get("decisive_pilot") or record.get("pilot") or review.get("decisive_pilot"),
        "stop_condition": record.get("stop_condition") or review.get("stop_rule"),
        "nearest_work": (record.get("nearest_work") or (review.get("direct_collision") or {}).get("closest_work") or [])[:6],
    }


def _tool(batch_size: int) -> list[dict[str, Any]]:
    props = {
        "parent_id": {"type":"string"}, "id": {"type":"string"},
        "title": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "problem": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "importance": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "core_idea": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "material_change": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "method_logic": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "persistent_update_object": {"type":"string"},
        "learning_signal": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "independent_ground_truth": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "strongest_matched_baseline": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "shared_information_budget": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "decisive_pilot": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "stop_condition": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "surviving_claim": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "why_r3_boundary_is_closed": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
        "remaining_risk": {"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False},
    }
    return [{"type":"function","name":"submit_repairs","description":"Submit one material repair child per supplied R3-REVISE parent.","parameters":{"type":"object","properties":{"repairs":{"type":"array","minItems":batch_size,"maxItems":batch_size,"items":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}}},"required":["repairs"],"additionalProperties":False}}]


def _prompt(batch: list[dict[str, Any]], model: str) -> str:
    return f"""Act as an ICLR mechanism designer repairing ideas that already failed a FINAL PRE-ADVISOR R3 audit.

You are not reviewing and must not grant PASS. For every supplied parent, create exactly one materially repaired child that closes the SINGLE stated R3 boundary while preserving the original real problem. Do not rename the parent and call it fixed.

Hard requirements:
1. The mechanism itself must change where R3 requested it; adding only an experiment is insufficient.
2. The strongest simplification receives the same observations, features, labels, intervention outcomes, traces, verifier access, model capacity, calls, tokens, optimization steps, and wall-clock wherever applicable. Never win by starving the baseline.
3. The learned object must be frozen and persistently alter future behavior after evolution context is removed.
4. Final truth is independent from the learner, its scorer, and its training labels.
5. The decisive pilot must contain the exact crossed/factorial comparison needed to identify the claimed mechanism.
6. If a parent's R3 request is fundamentally impossible without changing the research problem, make the smallest problem-preserving change and say the residual risk explicitly.
7. Do not invent citations or claim a collision is absent. Use nearest-work names only as context; final novelty will be re-searched independently.
8. The id must be a new lowercase slug ending in -r31 and must preserve parent_id exactly.
9. Output bilingual English/Chinese fields.
10. Call submit_repairs exactly once and provide all {len(batch)} children.

Generator model label: {model}

Parents:
{json.dumps(batch, ensure_ascii=False, indent=2)}
"""


def _validate(rows: list[dict[str, Any]], expected: list[str]) -> list[str]:
    errors: list[str] = []
    if len(rows) != len(expected): errors.append(f"expected {len(expected)} repairs, got {len(rows)}")
    seen = {row.get("parent_id") for row in rows if isinstance(row, dict)}
    if seen != set(expected): errors.append("parent ids mismatch")
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(set(ids)): errors.append("duplicate child ids")
    for row in rows:
        if not str(row.get("id") or "").endswith("-r31"): errors.append(f"bad child id {row.get('id')}")
        for key in ("persistent_update_object",):
            if len(str(row.get(key) or "")) < 20: errors.append(f"{row.get('parent_id')} weak {key}")
        for key in ("material_change","method_logic","strongest_matched_baseline","shared_information_budget","decisive_pilot","why_r3_boundary_is_closed"):
            value=row.get(key) or {}; text=_text(value)
            if len(text) < 80: errors.append(f"{row.get('parent_id')} weak {key}")
    return errors


def run(models: list[str] | None = None, batch_size: int = 4, max_workers: int = 4, only_parents: list[str] | None = None) -> dict[str, Any]:
    chosen = models or list(DEFAULT_MODELS)
    records = _records()
    r3 = build_r3_final_audit()
    wanted = set(only_parents or [])
    parents=[]
    for audit in r3["ideas"]:
        if audit["verdict"] != "revise": continue
        if wanted and audit["idea_id"] not in wanted: continue
        parents.append({"idea_id":audit["idea_id"],"r3_finding":audit["finding"],"r3_required_action":audit["required_action"],"dossier":_compact(records.get(audit["idea_id"],{}))})
    jobs=[]
    for model in chosen:
        for offset in range(0,len(parents),batch_size): jobs.append((model,parents[offset:offset+batch_size]))

    def one(job: tuple[str,list[dict[str,Any]]]) -> dict[str,Any]:
        model,batch=job; client=ArkResponsesClient(); expected=[x["idea_id"] for x in batch]
        try:
            response=client.respond(_prompt(batch,model),model=model,max_output_tokens=max(5500, 5500*len(batch)),tools=_tool(len(batch)),thinking="disabled")
            calls=[x for x in response.get("function_calls",[]) if x.get("name")=="submit_repairs"]
            if len(calls)!=1: raise ValueError(f"expected one submit_repairs function call, got {len(calls)}")
            obj=json.loads(calls[0].get("arguments") or "{}")
            rows=obj.get("repairs") or []; errors=_validate(rows,expected)
            return {"model":model,"parent_ids":expected,"valid":not errors,"errors":errors,"usage":response.get("usage") or {},"repairs":rows}
        except Exception as e:
            return {"model":model,"parent_ids":expected,"valid":False,"errors":[str(e)],"repairs":[]}

    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(one,job) for job in jobs]
        for f in concurrent.futures.as_completed(futures): results.append(f.result())
    order={m:i for i,m in enumerate(chosen)}; results.sort(key=lambda r:(order.get(r["model"],99),r["parent_ids"][0]))
    repairs=[]
    for result in results:
        if not result["valid"]: continue
        for row in result["repairs"]:
            repairs.append({"generator_model":result["model"],**row})
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"models":chosen,"summary":{"parents":len(parents),"jobs":len(results),"valid_jobs":sum(r["valid"] for r in results),"candidate_repairs":len(repairs)},"jobs":results,"repairs":repairs}


def _merge(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    jobs = {(j.get("model"), tuple(j.get("parent_ids") or [])): j for j in existing.get("jobs") or []}
    for job in incoming.get("jobs") or []: jobs[(job.get("model"), tuple(job.get("parent_ids") or []))] = job
    repairs = {(r.get("generator_model"), r.get("parent_id")): r for r in existing.get("repairs") or []}
    for row in incoming.get("repairs") or []: repairs[(row.get("generator_model"), row.get("parent_id"))] = row
    models = list(dict.fromkeys([*(existing.get("models") or []), *(incoming.get("models") or [])]))
    return {**incoming, "models":models, "summary":{"parents":len({r.get('parent_id') for r in repairs.values()}),"jobs":len(jobs),"valid_jobs":sum(j.get('valid') for j in jobs.values()),"candidate_repairs":len(repairs)},"jobs":list(jobs.values()),"repairs":list(repairs.values())}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--models",nargs="*",default=None); parser.add_argument("--parents",nargs="*",default=None); parser.add_argument("--batch-size",type=int,default=4); parser.add_argument("--max-workers",type=int,default=4); parser.add_argument("--json",type=Path,default=DEFAULT_JSON); args=parser.parse_args()
    payload=run(args.models,args.batch_size,args.max_workers,args.parents)
    if args.json.exists():
        try: payload=_merge(json.loads(args.json.read_text(encoding='utf-8')),payload)
        except Exception: pass
    args.json.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(payload["summary"],ensure_ascii=False));
    for job in payload["jobs"][-max(1,len(args.models or DEFAULT_MODELS)):]:
        print(job["model"],job["parent_ids"][0],"valid="+str(job["valid"]),"errors="+str(job["errors"][:1]))
    return 0


if __name__=="__main__": raise SystemExit(main())
