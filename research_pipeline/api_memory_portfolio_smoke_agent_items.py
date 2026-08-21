from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_portfolio_smoke_reviewers import AGENT_REVIEWER_MODEL, agent_prompt
from .api_memory_search_smoke import _canonical, _sha_text, _usage
from .api_memory_search_smoke_staged import _client, _load, _lock, _write
from .api_research_memory import record_parsed_api_output, record_provider_failure, record_raw_api_output
from .ark_provider import extract_json_object

DEFAULT_ATTEMPT = 1


def _agent_tool() -> tuple[str, list[dict[str, Any]]]:
    name = "submit_agent_specificity_reviews"
    props = {
        "blind_id": {"type": "string"},
        "agent_specificity": {"type": "string", "enum": ["AGENT_SPECIFIC", "GENERIC_OR_MODEL_LEVEL", "UNCERTAIN"]},
        "reason": {"type": "string"},
    }
    return name, [{"type":"function","name":name,"description":"Submit exactly one agent-specificity review.","parameters":{"type":"object","properties":{"reviews":{"type":"array","minItems":1,"maxItems":1,"items":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}}},"required":["reviews"],"additionalProperties":False}}]


def _sum_usage(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {key: sum(int((row.get("usage") or {}).get(key) or 0) for row in rows)
            for key in ("input_tokens", "output_tokens", "total_tokens")}


def _one(*, root: Path, study: Path, item: dict[str, Any], prefix: str, attempt: int) -> dict[str, Any]:
    blind_id = str(item["blind_id"])
    output = study / f"review-agent-item-{blind_id}-a{attempt}.json"
    if output.is_file():
        existing = _load(output)
        if existing.get("status") == "AGENT_ITEM_COMPLETE": return existing
        raise RuntimeError(f"existing failed agent item requires new attempt: {output.name}")
    run_id = f"{prefix}-agent-item-{blind_id}-a{attempt}"
    lock = _lock(output,{"stage":"agent-item","blind_id":blind_id,"attempt":attempt,"run_id":run_id})
    prep = _load(study / "review-prepared.json"); subset=dict(prep); subset["blinded"]=[item]
    prompt = agent_prompt(subset); function_name, tools = _agent_tool()
    run_root=root/"runs"/run_id; run_root.mkdir(parents=True,exist_ok=True)
    try:
        try:
            response=_client().respond(prompt,model=AGENT_REVIEWER_MODEL,max_output_tokens=1100,
                                       temperature=0.0,tools=tools,thinking="disabled",store=True)
        except Exception as error:
            psha=_sha_text(prompt); fp=_sha_text(_canonical({"stage":"memory-portfolio-agent-item","blind_id":blind_id,
                 "model":AGENT_REVIEWER_MODEL,"prompt_sha256":psha,"error_type":type(error).__name__,"error":str(error)[:500]}))
            rec=record_provider_failure(run_root=run_root,stage="memory-portfolio-agent-item",payload={
                "status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":AGENT_REVIEWER_MODEL,
                "error_fingerprint":fp,"prompt_sha256":psha,"failure_class":"execution"},root=root)
            failed={"schema_version":"1.0","status":"PROVIDER_FAILURE","blind_id":blind_id,"run_id":run_id,
                    "error_type":type(error).__name__,"error":str(error)[:1200],"provider_failure":rec,
                    "scientific_authority":False,"belief_authority":False};_write(output,failed);return failed

        calls=[c for c in response.get("function_calls") or [] if c.get("name")==function_name]
        transport="FUNCTION_TOOL"; raw=""; reviews=None
        if len(calls)==1:
            payload=json.loads(str(calls[0].get("arguments") or "{}"));reviews=payload.get("reviews")
            raw=json.dumps({"function_name":function_name,"arguments":payload},ensure_ascii=False,sort_keys=True,separators=(",",":"))
        elif len(calls)==0 and str(response.get("text") or "").strip():
            transport="JSON_TEXT_FALLBACK";raw=str(response.get("text") or "");reviews=extract_json_object(raw).get("reviews")
        if not isinstance(reviews,list) or len(reviews)!=1 or str(reviews[0].get("blind_id") or "")!=blind_id:
            psha=_sha_text(prompt); fp=_sha_text(_canonical({"stage":"memory-portfolio-agent-item","blind_id":blind_id,
                 "model":AGENT_REVIEWER_MODEL,"prompt_sha256":psha,"error":"structured response missing or wrong blind id"}))
            rec=record_provider_failure(run_root=run_root,stage="memory-portfolio-agent-item",payload={
                "status":"PROTOCOL_ERROR_ZERO_AUTHORITY","requested_model":AGENT_REVIEWER_MODEL,
                "error_fingerprint":fp,"prompt_sha256":psha,"failure_class":"protocol"},root=root)
            failed={"schema_version":"1.0","status":"PROTOCOL_FAILURE","blind_id":blind_id,"run_id":run_id,
                    "provider_failure":rec,"scientific_authority":False,"belief_authority":False};_write(output,failed);return failed

        raw_file=run_root/f"raw-agent-item-{blind_id}.txt";raw_file.write_text(raw,encoding="utf-8")
        psha=_sha_text(prompt); fp=_sha_text(_canonical({"stage":"memory-portfolio-agent-item","blind_id":blind_id,
             "model":AGENT_REVIEWER_MODEL,"prompt_sha256":psha,"transport":transport}))
        arch=record_raw_api_output(run_root=run_root,stage="memory-portfolio-agent-item",raw_path=raw_file,
            requested_model=AGENT_REVIEWER_MODEL,resolved_model=str(response.get("resolved_model") or AGENT_REVIEWER_MODEL),
            request_fingerprint=fp,prompt_sha256=psha,root=root)
        structured={"schema_version":"2.3","study":"API_MEMORY_PORTFOLIO_SMOKE","review_stage":"agent",
                    "transport":transport,"blind_id":blind_id,"usage":_usage(response),"review":reviews[0],
                    "scientific_authority":False,"belief_authority":False}
        record_parsed_api_output(run_root=run_root,stage="memory-portfolio-agent-item",raw_sha256=arch["raw_sha256"],
            structured_payload=structured,requested_model=AGENT_REVIEWER_MODEL,
            resolved_model=str(response.get("resolved_model") or AGENT_REVIEWER_MODEL),research_objects=[],root=root)
        result={"schema_version":"2.3","status":"AGENT_ITEM_COMPLETE","blind_id":blind_id,"run_id":run_id,
                "raw_sha256":arch["raw_sha256"],"resolved_model":str(response.get("resolved_model") or ""),
                "transport":transport,"usage":_usage(response),"review":reviews[0],
                "scientific_authority":False,"belief_authority":False}; result["stage_sha256"]=_sha_text(_canonical(result));_write(output,result);return result
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def run(*, root: Path, study: Path, attempt: int = DEFAULT_ATTEMPT) -> dict[str, Any]:
    aggregate=study/f"review-agent-result-r{attempt}.json"
    if aggregate.exists(): raise RuntimeError(f"aggregate already exists: {aggregate.name}")
    prep=_load(study/"review-prepared.json"); prefix=str(_load(study/"state-prepared.json")["prefix"]); results=[]
    for item in prep["blinded"]:
        row=_one(root=root,study=study,item=item,prefix=prefix,attempt=attempt)
        if row.get("status")!="AGENT_ITEM_COMPLETE":
            return {"schema_version":"2.3","status":"AGENT_ITEMIZED_REVIEW_INCOMPLETE","failed_blind_id":item["blind_id"],
                    "failure":row,"completed":len(results),"scientific_authority":False,"belief_authority":False}
        results.append(row)
    resolved={r["resolved_model"] for r in results}
    if len(resolved)!=1: raise RuntimeError(f"agent reviewer resolved-model drift: {resolved}")
    reviews=[r["review"] for r in results]
    out={"schema_version":"2.3","status":"AGENT_REVIEW_COMPLETE","stage":"agent","attempt":attempt,
         "transport":"ITEMIZED_FUNCTION_OR_JSON_18X1","requested_model":AGENT_REVIEWER_MODEL,
         "resolved_model":next(iter(resolved)),"usage":_sum_usage(results),
         "item_results":[{"blind_id":r["blind_id"],"run_id":r["run_id"],"raw_sha256":r["raw_sha256"],"transport":r["transport"],"usage":r["usage"]} for r in results],
         "reviews":reviews,"scientific_authority":False,"belief_authority":False}
    out["stage_sha256"]=_sha_text(_canonical(out));_write(aggregate,out);return out


def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--persistent-root",type=Path,required=True);p.add_argument("--study",type=Path,required=True);p.add_argument("--attempt",type=int,default=DEFAULT_ATTEMPT)
    a=p.parse_args();print(json.dumps(run(root=a.persistent_root,study=a.study,attempt=a.attempt),ensure_ascii=False,indent=2))


if __name__=="__main__":main()
