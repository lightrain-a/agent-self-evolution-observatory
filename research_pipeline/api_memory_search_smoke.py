from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

from .api_memory_ablation import build_api_memory_ablation_plan
from .api_research_memory import (
    compile_api_memory_query_pack,
    invalidate_query_only_memory_run,
    record_api_memory_consumption,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object

ARMS = ("relevant", "random", "none")
GENERATOR_MODEL = "kimi-k3"
REVIEWER_MODEL = "deepseek-v4-pro"
IDEAS_PER_ARM = 6


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage") or {}
    return {
        "input_tokens": int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def _one_post_client() -> ArkResponsesClient:
    base = ArkSettings.from_env()
    return ArkResponsesClient(replace(base, max_retries=0, timeout_seconds=max(240.0, base.timeout_seconds)))


def _validate_ideas(payload: dict[str, Any]) -> list[dict[str, str]]:
    rows = payload.get("ideas")
    if not isinstance(rows, list) or len(rows) != IDEAS_PER_ARM:
        raise ValueError(f"generator must return exactly {IDEAS_PER_ARM} ideas")
    out: list[dict[str, str]] = []
    required = (
        "id", "title", "scientific_object", "exact_prediction",
        "strongest_same_information_baseline", "cheapest_falsifier",
    )
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError("idea rows must be objects")
        normalized = {key: " ".join(str(row.get(key) or "").split()) for key in required}
        if normalized["id"] != f"I{index}":
            raise ValueError("idea ids must be I1..I6 in order")
        if any(not normalized[key] for key in required[1:]):
            raise ValueError(f"idea {normalized['id']} has empty scientific fields")
        out.append(normalized)
    return out


def generation_prompt(context: dict[str, Any], pack: dict[str, Any]) -> str:
    memory = str(pack.get("text") or "").strip() or "(NO HISTORICAL API RESEARCH MEMORY PROVIDED)"
    return f'''You are generating candidate paper problems for a controlled search-policy experiment.

The research domain is self-evolving/autonomous agents: persistent memory, skills, experience accumulation, retrieval, longitudinal adaptation, and agent self-improvement. Generate exactly {IDEAS_PER_ARM} distinct falsifiable PAPER PROBLEMS, not proposed methods.

Hard contract for each idea:
1. The scientific object must be agent-specific: it should depend on persistent experience/state/retrieval/self-evolution, not merely generic LLM accuracy.
2. State one exact empirical prediction that could be false.
3. State the strongest SAME-INFORMATION baseline/reduction that could explain the prediction without a new paper mechanism.
4. State the cheapest bounded scientific falsifier that can distinguish the problem from that baseline.
5. Prefer a genuinely new scientific object over renaming a familiar memory/retrieval problem.
6. Do not treat historical failures as automatic vetoes or historical successes as truth. Historical memory is search context only.
7. Do not authorize Problem Gate, paper design, method, P0, GPU, or scientific claims.

COMMON_RESEARCH_CONTEXT={_canonical(context)}

HISTORICAL_API_RESEARCH_MEMORY_START
{memory}
HISTORICAL_API_RESEARCH_MEMORY_END

Return JSON only:
{{"ideas":[
  {{"id":"I1","title":"...","scientific_object":"...","exact_prediction":"...","strongest_same_information_baseline":"...","cheapest_falsifier":"..."}},
  ... exactly I1 through I6 ...
]}}'''


def review_prompt(history_pack: dict[str, Any], blinded: list[dict[str, str]]) -> str:
    history = str(history_pack.get("text") or "").strip()
    return f'''You are an independent SEARCH-POLICY reviewer. You are not judging novelty for publication and cannot grant scientific authority.

You receive 18 blinded candidate paper problems generated under different search contexts. The arm labels are hidden. Evaluate every candidate against the SAME supplied historical-memory pack.

For each blind_id output exactly four booleans:
- history_near_duplicate: within the supplied HISTORY PACK, there is a prior object with substantially the same scientific object + prediction/reduction basin. This is pack-scoped, NOT an exhaustive literature novelty claim.
- same_information_reduction_risk: the stated strongest same-information baseline plausibly explains the exact prediction so well that the problem should be treated as reduction-risk before expensive evidence acquisition.
- agent_specific: the scientific object genuinely depends on persistent agent experience/state/memory/retrieval/self-evolution rather than a generic model phenomenon.
- cheapest_falsifier_complete: the stated falsifier names a bounded comparison, an independent observable/outcome, and a stopping interpretation that could discriminate candidate residual vs baseline reduction.

Also give matched_history_object_id using the `id=` field from the supplied history digest when history_near_duplicate=true, otherwise empty. Keep reason <=45 words and do not infer the hidden arm.

HISTORY_PACK_START
{history}
HISTORY_PACK_END

BLINDED_IDEAS={_canonical(blinded)}

Return JSON only:
{{"reviews":[{{"blind_id":"B...","history_near_duplicate":false,"same_information_reduction_risk":false,"agent_specific":true,"cheapest_falsifier_complete":true,"matched_history_object_id":"","reason":"..."}}, ... exactly all 18 blind_id values ...]}}'''


def _token_set(text: str) -> set[str]:
    return {x for x in re.findall(r"[\w]+", text.lower(), flags=re.UNICODE) if len(x) > 1}


def _jaccard(a: str, b: str) -> float:
    x, y = _token_set(a), _token_set(b)
    return len(x & y) / len(x | y) if x or y else 0.0


def _diversity(rows: list[dict[str, str]]) -> float:
    vals = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a = rows[i]["title"] + " " + rows[i]["scientific_object"]
            b = rows[j]["title"] + " " + rows[j]["scientific_object"]
            vals.append(1.0 - _jaccard(a, b))
    return sum(vals) / len(vals) if vals else 0.0


def _max_cross_similarity(rows: list[dict[str, str]], others: list[dict[str, str]]) -> float:
    vals=[]
    for row in rows:
        a=row["title"]+" "+row["scientific_object"]
        vals.append(max((_jaccard(a,o["title"]+" "+o["scientific_object"]) for o in others),default=0.0))
    return sum(vals)/len(vals) if vals else 0.0


def run_smoke(*, root: Path, output_root: Path, run_prefix: str) -> dict[str, Any]:
    context = {
        "research_goal": "Find falsifiable paper-worthy scientific problems in self-evolving agents, with emphasis on persistent memory/skill/experience dynamics and retrieval decisions.",
        "search_constraints": [
            "agent-specific scientific object",
            "exact prediction",
            "strongest same-information reduction",
            "cheapest bounded falsifier",
            "avoid method-first proposals",
        ],
        "scientific_authority": False,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    frozen = build_api_memory_ablation_plan(
        purpose="IDEA_DISCOVERY", context=context, run_id_prefix=run_prefix,
        stage="memory-search-smoke", max_items=3, max_chars=6000, root=root,
    )
    if frozen["status"] != "API_MEMORY_ABLATION_READY":
        raise RuntimeError(f"ablation plan blocked: {frozen['invariants']}")
    (output_root / "ablation-plan.json").write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    packs: dict[str, dict[str, Any]] = {}
    for arm in ARMS:
        max_items = int(frozen["budget"]["matched_nonzero_items"]) if arm != "none" else 0
        max_chars = int(frozen["budget"]["max_chars"]) if arm != "none" else 0
        pack = compile_api_memory_query_pack(
            purpose="IDEA_DISCOVERY", context=context, run_id=f"{run_prefix}-{arm}",
            stage="memory-search-smoke", variant=arm, max_items=max_items,
            max_chars=max_chars, required=True, record_query=True, root=root,
        )
        expected = frozen["arms"][arm]["selected_memory_ids"]
        if list(pack.get("selected_memory_ids") or []) != list(expected):
            raise RuntimeError(f"frozen query pack drift for arm={arm}")
        packs[arm] = pack

    client = _one_post_client()
    generations: dict[str, dict[str, Any]] = {}
    all_for_review: list[dict[str, str]] = []
    for arm in ARMS:
        run_root = root / "runs" / f"{run_prefix}-{arm}"
        run_root.mkdir(parents=True, exist_ok=True)
        prompt = generation_prompt(context, packs[arm])
        try:
            response = client.respond(prompt, model=GENERATOR_MODEL, max_output_tokens=6000, temperature=0.0, thinking="disabled", store=True)
        except Exception as error:
            prompt_sha = _sha_text(prompt)
            fingerprint = _sha_text(_canonical({"stage":"memory-search-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":prompt_sha,"error_type":type(error).__name__,"error":str(error)[:500]}))
            record_provider_failure(run_root=run_root,stage="memory-search-smoke",payload={"status":"PROVIDER_TIMEOUT_ZERO_AUTHORITY" if "timed out" in str(error).lower() else "PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":GENERATOR_MODEL,"error_fingerprint":fingerprint,"prompt_sha256":prompt_sha},root=root)
            for pending_arm in ARMS:
                if pending_arm == arm or pending_arm in generations:
                    continue
                try:
                    invalidate_query_only_memory_run(run_id=f"{run_prefix}-{pending_arm}",reason=f"A/B/C smoke aborted before {pending_arm} provider execution because {arm} arm provider call failed: {type(error).__name__}",root=root)
                except ValueError:
                    pass
            aborted={"schema_version":"1.0","status":"API_MEMORY_SEARCH_SMOKE_ABORTED_PROVIDER_FAILURE","failed_arm":arm,"error_type":type(error).__name__,"error":str(error)[:1200],"error_fingerprint":fingerprint,"completed_arms":sorted(generations),"scientific_authority":False,"belief_authority":False}
            (output_root/"aborted.json").write_text(json.dumps(aborted,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            raise
        raw = str(response.get("text") or "")
        raw_path = run_root / "raw-generation.txt"
        raw_path.write_text(raw, encoding="utf-8")
        prompt_sha = _sha_text(prompt)
        request_fp = _sha_text(_canonical({"stage":"memory-search-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":prompt_sha,"pack_sha256":packs[arm]["query_pack_sha256"]}))
        archived = record_raw_api_output(
            run_root=run_root, stage="memory-search-smoke", raw_path=raw_path,
            requested_model=GENERATOR_MODEL, resolved_model=str(response.get("resolved_model") or GENERATOR_MODEL),
            request_fingerprint=request_fp, prompt_sha256=prompt_sha, root=root,
        )
        payload = extract_json_object(raw)
        ideas = _validate_ideas(payload)
        generations[arm] = {
            "arm":arm, "run_root":str(run_root), "prompt_sha256":prompt_sha,
            "raw_sha256":archived["raw_sha256"], "resolved_model":str(response.get("resolved_model") or ""),
            "usage":_usage(response), "pack":packs[arm], "payload":payload, "ideas":ideas,
        }
        for row in ideas:
            blind_seed=_sha_text(f"memory-search-smoke-v22:{arm}:{row['id']}:{row['scientific_object']}")
            all_for_review.append({"blind_id":"B"+blind_seed[:12],**{k:row[k] for k in row if k!="id"},"_arm":arm,"_idea_id":row["id"]})

    # Freeze reviewer history BEFORE any generated idea becomes a research object.
    blinded_sorted=sorted(all_for_review,key=lambda r:_sha_text("blind-order-v1:"+r["blind_id"]))
    public_blinded=[{k:v for k,v in row.items() if not k.startswith("_")} for row in blinded_sorted]
    reviewer_context={"generated_ideas":public_blinded,"purpose":"blind search-policy review"}
    review_run_id=f"{run_prefix}-blind-review"
    history_pack=compile_api_memory_query_pack(
        purpose="SEMANTIC_REVIEW", context=reviewer_context, run_id=review_run_id,
        stage="memory-search-smoke-review", variant="relevant", max_items=24,
        max_chars=18000, required=True, record_query=True, root=root,
    )
    review_run=root/"runs"/review_run_id; review_run.mkdir(parents=True,exist_ok=True)
    rprompt=review_prompt(history_pack,public_blinded)
    rresponse=client.respond(rprompt,model=REVIEWER_MODEL,max_output_tokens=7500,temperature=0.0,thinking="disabled",store=True)
    rraw=str(rresponse.get("text") or "")
    rraw_path=review_run/"raw-review.txt"; rraw_path.write_text(rraw,encoding="utf-8")
    rprompt_sha=_sha_text(rprompt)
    rfp=_sha_text(_canonical({"stage":"memory-search-smoke-review","model":REVIEWER_MODEL,"prompt_sha256":rprompt_sha,"pack_sha256":history_pack["query_pack_sha256"]}))
    rarch=record_raw_api_output(run_root=review_run,stage="memory-search-smoke-review",raw_path=rraw_path,requested_model=REVIEWER_MODEL,resolved_model=str(rresponse.get("resolved_model") or REVIEWER_MODEL),request_fingerprint=rfp,prompt_sha256=rprompt_sha,root=root)
    rpayload=extract_json_object(rraw)
    reviews=rpayload.get("reviews")
    if not isinstance(reviews,list) or len(reviews)!=len(public_blinded): raise ValueError("reviewer must return exactly 18 reviews")
    by_blind={str(r.get("blind_id") or ""):r for r in reviews if isinstance(r,dict)}
    if set(by_blind)!=set(r["blind_id"] for r in public_blinded): raise ValueError("review blind ids mismatch")

    # Persist parsed artifacts only after all treatment/review query packs are frozen.
    per_arm_reviews: dict[str,list[dict[str,Any]]]={arm:[] for arm in ARMS}
    for row in all_for_review:
        review=dict(by_blind[row["blind_id"]]); review["idea_id"]=row["_idea_id"]
        per_arm_reviews[row["_arm"]].append(review)
    for arm in ARMS:
        gen=generations[arm]
        structured={"schema_version":"1.0","study":"API_MEMORY_SEARCH_SMOKE_V22","arm":arm,"query_pack_sha256":gen["pack"]["query_pack_sha256"],"selected_memory_ids":gen["pack"]["selected_memory_ids"],"generator_model":GENERATOR_MODEL,"resolved_model":gen["resolved_model"],"usage":gen["usage"],"ideas":gen["ideas"],"blind_reviews":sorted(per_arm_reviews[arm],key=lambda r:str(r.get("idea_id"))),"scientific_authority":False,"belief_authority":False}
        record_parsed_api_output(run_root=Path(gen["run_root"]),stage="memory-search-smoke",raw_sha256=gen["raw_sha256"],structured_payload=structured,requested_model=GENERATOR_MODEL,resolved_model=gen["resolved_model"],research_objects=[],root=root)
        record_api_memory_consumption(run_id=f"{run_prefix}-{arm}",stage="memory-search-smoke",pack=gen["pack"],raw_sha256=gen["raw_sha256"],output_object_ids=[f"{arm}:{x['id']}" for x in gen["ideas"]],outcome_status="SEARCH_SMOKE_GENERATED_ZERO_AUTHORITY",root=root)
        (output_root/f"arm-{arm}.json").write_text(json.dumps(structured,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    review_struct={"schema_version":"1.0","study":"API_MEMORY_SEARCH_SMOKE_V22","history_query_pack_sha256":history_pack["query_pack_sha256"],"selected_history_memory_ids":history_pack["selected_memory_ids"],"reviewer_model":REVIEWER_MODEL,"resolved_model":str(rresponse.get("resolved_model") or ""),"usage":_usage(rresponse),"blinded_order":[r["blind_id"] for r in public_blinded],"reviews":reviews,"scientific_authority":False,"belief_authority":False}
    record_parsed_api_output(run_root=review_run,stage="memory-search-smoke-review",raw_sha256=rarch["raw_sha256"],structured_payload=review_struct,requested_model=REVIEWER_MODEL,resolved_model=str(rresponse.get("resolved_model") or REVIEWER_MODEL),research_objects=[],root=root)
    record_api_memory_consumption(run_id=review_run_id,stage="memory-search-smoke-review",pack=history_pack,raw_sha256=rarch["raw_sha256"],output_object_ids=[r["blind_id"] for r in public_blinded],outcome_status="SEARCH_SMOKE_BLIND_REVIEW_ZERO_AUTHORITY",root=root)
    (output_root/"blind-review.json").write_text(json.dumps(review_struct,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    metrics={}
    for arm in ARMS:
        rs=per_arm_reviews[arm]; ideas=generations[arm]["ideas"]
        def rate(key: str) -> float: return sum(bool(r.get(key)) for r in rs)/len(rs)
        survivors=sum((not bool(r.get("history_near_duplicate"))) and (not bool(r.get("same_information_reduction_risk"))) and bool(r.get("agent_specific")) and bool(r.get("cheapest_falsifier_complete")) for r in rs)
        others=[idea for other in ARMS if other!=arm for idea in generations[other]["ideas"]]
        metrics[arm]={
            "n":len(rs),
            "history_pack_duplicate_rate":rate("history_near_duplicate"),
            "same_information_reduction_risk_rate":rate("same_information_reduction_risk"),
            "agent_specific_rate":rate("agent_specific"),
            "cheapest_falsifier_complete_rate":rate("cheapest_falsifier_complete"),
            "search_survivor_count":survivors,
            "search_survivor_rate":survivors/len(rs),
            "within_arm_lexical_diversity":_diversity(ideas),
            "mean_max_cross_arm_lexical_similarity":_max_cross_similarity(ideas,others),
            "generation_input_tokens":generations[arm]["usage"]["input_tokens"],
            "generation_output_tokens":generations[arm]["usage"]["output_tokens"],
            "selected_memory_items":int((packs[arm].get("summary") or {}).get("selected") or 0),
            "selected_memory_characters":int((packs[arm].get("summary") or {}).get("characters") or 0),
        }
    primary={
        "comparison":"relevant_vs_random",
        "matched_nonzero_item_count":metrics["relevant"]["selected_memory_items"]==metrics["random"]["selected_memory_items"],
        "survivor_rate_delta":metrics["relevant"]["search_survivor_rate"]-metrics["random"]["search_survivor_rate"],
        "duplicate_rate_delta":metrics["relevant"]["history_pack_duplicate_rate"]-metrics["random"]["history_pack_duplicate_rate"],
        "reduction_risk_rate_delta":metrics["relevant"]["same_information_reduction_risk_rate"]-metrics["random"]["same_information_reduction_risk_rate"],
        "interpretation":"matched-overhead search-policy smoke only; not a scientific-performance or publication-success claim",
    }
    report={"schema_version":"1.0","status":"API_MEMORY_SEARCH_SMOKE_COMPLETE","study":"API_MEMORY_SEARCH_SMOKE_V22","memory_instance_id":packs["relevant"]["memory_instance_id"],"frozen_ablation_plan_sha256":frozen["plan_sha256"],"history_pool_available_objects":int((packs["relevant"].get("summary") or {}).get("available") or 0),"generator_model":GENERATOR_MODEL,"reviewer_model":REVIEWER_MODEL,"metrics":metrics,"primary_comparison":primary,"review_scope":"history_near_duplicate is scoped to the single frozen reviewer history pack; not exhaustive literature novelty","generated_outputs_promoted_to_research_objects":False,"scientific_authority":False,"belief_authority":False}
    report["report_sha256"]=_sha_text(_canonical(report))
    (output_root/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main() -> None:
    raise SystemExit(
        "monolithic API-memory smoke execution is disabled because connector retries can duplicate provider POSTs; use api_memory_search_smoke_staged instead"
    )


if __name__ == "__main__":
    main()
