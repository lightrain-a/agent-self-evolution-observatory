from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

from .api_memory_ablation import build_api_memory_ablation_plan
from .api_memory_search_smoke import (
    ARMS, GENERATOR_MODEL, REVIEWER_MODEL, _canonical, _diversity,
    _max_cross_similarity, _sha_text, _usage, _validate_ideas,
    generation_prompt, review_prompt,
)
from .api_research_memory import (
    compile_api_memory_query_pack, record_api_memory_consumption,
    record_parsed_api_output, record_provider_failure, record_raw_api_output,
)
from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object


def _client() -> ArkResponsesClient:
    base=ArkSettings.from_env()
    return ArkResponsesClient(replace(base,max_retries=0,timeout_seconds=max(240.0,base.timeout_seconds)))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def _load(path: Path) -> dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected object: {path}")
    return value


def _lock(path: Path, payload: dict[str,Any]) -> Path:
    lock=Path(str(path)+".lock")
    if path.exists(): raise RuntimeError(f"OUTPUT_ALREADY_EXISTS:{path}")
    lock.parent.mkdir(parents=True,exist_ok=True)
    try: fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as error: raise RuntimeError(f"STAGE_ALREADY_RUNNING_OR_STALE_LOCK:{lock}") from error
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        f.write(json.dumps(payload,ensure_ascii=False,indent=2)+"\n");f.flush();os.fsync(f.fileno())
    return lock


def context() -> dict[str,Any]:
    return {
        "research_goal":"Find falsifiable paper-worthy scientific problems in self-evolving agents, with emphasis on persistent memory/skill/experience dynamics and retrieval decisions.",
        "search_constraints":["agent-specific scientific object","exact prediction","strongest same-information reduction","cheapest bounded falsifier","avoid method-first proposals"],
        "scientific_authority":False,
    }


def prepare(*,root:Path,study:Path,prefix:str)->dict[str,Any]:
    output=study/"state-prepared.json"; lock=_lock(output,{"stage":"prepare","prefix":prefix})
    try:
        ctx=context()
        plan=build_api_memory_ablation_plan(purpose="IDEA_DISCOVERY",context=ctx,run_id_prefix=prefix,stage="memory-search-smoke",max_items=3,max_chars=6000,root=root)
        if plan["status"]!="API_MEMORY_ABLATION_READY": raise RuntimeError(str(plan["invariants"]))
        packs={}
        for arm in ARMS:
            items=int(plan["budget"]["matched_nonzero_items"]) if arm!="none" else 0
            chars=int(plan["budget"]["max_chars"]) if arm!="none" else 0
            pack=compile_api_memory_query_pack(purpose="IDEA_DISCOVERY",context=ctx,run_id=f"{prefix}-{arm}",stage="memory-search-smoke",variant=arm,max_items=items,max_chars=chars,required=True,record_query=True,root=root)
            if list(pack.get("selected_memory_ids") or [])!=list(plan["arms"][arm]["selected_memory_ids"]): raise RuntimeError(f"pack drift:{arm}")
            packs[arm]=pack
        state={"schema_version":"1.0","status":"PREPARED","prefix":prefix,"context":ctx,"plan":plan,"packs":packs,"scientific_authority":False,"belief_authority":False}
        state["state_sha256"]=_sha_text(_canonical(state));_write(output,state);return state
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def generate_arm(*,root:Path,study:Path,arm:str)->dict[str,Any]:
    if arm not in ARMS: raise ValueError(arm)
    prep=_load(study/"state-prepared.json");prefix=prep["prefix"];output=study/f"generation-{arm}.json";lock=_lock(output,{"stage":"generate","arm":arm,"prefix":prefix})
    try:
        pack=prep["packs"][arm];prompt=generation_prompt(prep["context"],pack);run_root=root/"runs"/f"{prefix}-{arm}";run_root.mkdir(parents=True,exist_ok=True)
        try:
            response=_client().respond(prompt,model=GENERATOR_MODEL,max_output_tokens=6000,temperature=0.0,thinking="disabled",store=True)
        except Exception as error:
            psha=_sha_text(prompt);fp=_sha_text(_canonical({"stage":"memory-search-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":psha,"error_type":type(error).__name__,"error":str(error)[:500]}))
            rec=record_provider_failure(run_root=run_root,stage="memory-search-smoke",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":GENERATOR_MODEL,"error_fingerprint":fp,"prompt_sha256":psha},root=root)
            fail={"schema_version":"1.0","status":"PROVIDER_FAILURE","arm":arm,"error_type":type(error).__name__,"error":str(error)[:1200],"error_fingerprint":fp,"provider_failure":rec,"scientific_authority":False,"belief_authority":False};_write(output,fail);return fail
        raw=str(response.get("text") or "");raw_file=run_root/"raw-generation.txt";raw_file.write_text(raw,encoding="utf-8");psha=_sha_text(prompt);rfp=_sha_text(_canonical({"stage":"memory-search-smoke","arm":arm,"model":GENERATOR_MODEL,"prompt_sha256":psha,"pack_sha256":pack["query_pack_sha256"]}))
        arch=record_raw_api_output(run_root=run_root,stage="memory-search-smoke",raw_path=raw_file,requested_model=GENERATOR_MODEL,resolved_model=str(response.get("resolved_model") or GENERATOR_MODEL),request_fingerprint=rfp,prompt_sha256=psha,root=root)
        payload=extract_json_object(raw);ideas=_validate_ideas(payload)
        out={"schema_version":"1.0","status":"GENERATION_COMPLETE_UNCOMMITTED","arm":arm,"run_id":f"{prefix}-{arm}","raw_sha256":arch["raw_sha256"],"prompt_sha256":psha,"resolved_model":str(response.get("resolved_model") or ""),"usage":_usage(response),"query_pack_sha256":pack["query_pack_sha256"],"selected_memory_ids":pack["selected_memory_ids"],"ideas":ideas,"scientific_authority":False,"belief_authority":False};out["stage_sha256"]=_sha_text(_canonical(out));_write(output,out);return out
    finally:
        if output.exists(): lock.unlink(missing_ok=True)


def prepare_review(*,root:Path,study:Path)->dict[str,Any]:
    prep=_load(study/"state-prepared.json");prefix=prep["prefix"];output=study/"review-prepared.json";lock=_lock(output,{"stage":"prepare-review","prefix":prefix})
    try:
        all_rows=[]
        for arm in ARMS:
            gen=_load(study/f"generation-{arm}.json")
            if gen.get("status")!="GENERATION_COMPLETE_UNCOMMITTED": raise RuntimeError(f"arm not complete:{arm}:{gen.get('status')}")
            for idea in gen["ideas"]:
                seed=_sha_text(f"memory-search-smoke-v22:{arm}:{idea['id']}:{idea['scientific_object']}")
                all_rows.append({"blind_id":"B"+seed[:12],**{k:v for k,v in idea.items() if k!="id"},"_arm":arm,"_idea_id":idea["id"]})
        ordered=sorted(all_rows,key=lambda r:_sha_text("blind-order-v1:"+r["blind_id"]));public=[{k:v for k,v in r.items() if not k.startswith("_")} for r in ordered]
        review_context={"generated_ideas":public,"purpose":"blind search-policy review"}
        rid=f"{prefix}-blind-review"
        pack=compile_api_memory_query_pack(purpose="SEMANTIC_REVIEW",context=review_context,run_id=rid,stage="memory-search-smoke-review",variant="relevant",max_items=24,max_chars=18000,required=True,record_query=True,root=root)
        out={"schema_version":"1.0","status":"REVIEW_PREPARED","review_run_id":rid,"history_pack":pack,"blinded":public,"mapping":[{"blind_id":r["blind_id"],"arm":r["_arm"],"idea_id":r["_idea_id"]} for r in ordered],"scientific_authority":False,"belief_authority":False};out["stage_sha256"]=_sha_text(_canonical(out));_write(output,out);return out
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def run_review(*,root:Path,study:Path)->dict[str,Any]:
    prep=_load(study/"review-prepared.json");output=study/"review-result.json";lock=_lock(output,{"stage":"review","run_id":prep["review_run_id"]})
    try:
        prompt=review_prompt(prep["history_pack"],prep["blinded"]);run_root=root/"runs"/prep["review_run_id"];run_root.mkdir(parents=True,exist_ok=True)
        try: response=_client().respond(prompt,model=REVIEWER_MODEL,max_output_tokens=7500,temperature=0.0,thinking="disabled",store=True)
        except Exception as error:
            psha=_sha_text(prompt);fp=_sha_text(_canonical({"stage":"memory-search-smoke-review","model":REVIEWER_MODEL,"prompt_sha256":psha,"error":str(error)[:500]}));rec=record_provider_failure(run_root=run_root,stage="memory-search-smoke-review",payload={"status":"PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":REVIEWER_MODEL,"error_fingerprint":fp,"prompt_sha256":psha},root=root);fail={"status":"PROVIDER_FAILURE","error_type":type(error).__name__,"error":str(error)[:1200],"provider_failure":rec,"scientific_authority":False,"belief_authority":False};_write(output,fail);return fail
        raw=str(response.get("text") or "");raw_file=run_root/"raw-review.txt";raw_file.write_text(raw,encoding="utf-8");psha=_sha_text(prompt);rfp=_sha_text(_canonical({"stage":"memory-search-smoke-review","model":REVIEWER_MODEL,"prompt_sha256":psha,"pack_sha256":prep["history_pack"]["query_pack_sha256"]}));arch=record_raw_api_output(run_root=run_root,stage="memory-search-smoke-review",raw_path=raw_file,requested_model=REVIEWER_MODEL,resolved_model=str(response.get("resolved_model") or REVIEWER_MODEL),request_fingerprint=rfp,prompt_sha256=psha,root=root);payload=extract_json_object(raw);reviews=payload.get("reviews")
        if not isinstance(reviews,list) or len(reviews)!=18: raise ValueError("reviewer must return 18 reviews")
        ids={str(x.get("blind_id") or "") for x in reviews if isinstance(x,dict)};expected={x["blind_id"] for x in prep["blinded"]}
        if ids!=expected: raise ValueError("review blind ids mismatch")
        out={"schema_version":"1.0","status":"REVIEW_COMPLETE_UNCOMMITTED","run_id":prep["review_run_id"],"raw_sha256":arch["raw_sha256"],"prompt_sha256":psha,"resolved_model":str(response.get("resolved_model") or ""),"usage":_usage(response),"reviews":reviews,"scientific_authority":False,"belief_authority":False};out["stage_sha256"]=_sha_text(_canonical(out));_write(output,out);return out
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def finalize(*,root:Path,study:Path)->dict[str,Any]:
    output=study/"report.json";lock=_lock(output,{"stage":"finalize"})
    try:
        prep=_load(study/"state-prepared.json");rprep=_load(study/"review-prepared.json");rr=_load(study/"review-result.json")
        if rr.get("status")!="REVIEW_COMPLETE_UNCOMMITTED":raise RuntimeError("review not complete")
        by_blind={str(r["blind_id"]):r for r in rr["reviews"]};mapping={x["blind_id"]:(x["arm"],x["idea_id"]) for x in rprep["mapping"]};per={arm:[] for arm in ARMS}
        for bid,review in by_blind.items():
            arm,iid=mapping[bid];row=dict(review);row["idea_id"]=iid;per[arm].append(row)
        gens={arm:_load(study/f"generation-{arm}.json") for arm in ARMS}
        for arm in ARMS:
            gen=gens[arm];pack=prep["packs"][arm];structured={"schema_version":"1.0","study":"API_MEMORY_SEARCH_SMOKE_V22_STAGED","arm":arm,"query_pack_sha256":pack["query_pack_sha256"],"selected_memory_ids":pack["selected_memory_ids"],"usage":gen["usage"],"ideas":gen["ideas"],"blind_reviews":sorted(per[arm],key=lambda r:r["idea_id"]),"scientific_authority":False,"belief_authority":False}
            record_parsed_api_output(run_root=root/"runs"/gen["run_id"],stage="memory-search-smoke",raw_sha256=gen["raw_sha256"],structured_payload=structured,requested_model=GENERATOR_MODEL,resolved_model=gen["resolved_model"],research_objects=[],root=root)
            record_api_memory_consumption(run_id=gen["run_id"],stage="memory-search-smoke",pack=pack,raw_sha256=gen["raw_sha256"],output_object_ids=[f"{arm}:{x['id']}" for x in gen["ideas"]],outcome_status="SEARCH_SMOKE_GENERATED_ZERO_AUTHORITY",root=root)
        review_struct={"schema_version":"1.0","study":"API_MEMORY_SEARCH_SMOKE_V22_STAGED","history_query_pack_sha256":rprep["history_pack"]["query_pack_sha256"],"selected_history_memory_ids":rprep["history_pack"]["selected_memory_ids"],"usage":rr["usage"],"reviews":rr["reviews"],"scientific_authority":False,"belief_authority":False}
        record_parsed_api_output(run_root=root/"runs"/rr["run_id"],stage="memory-search-smoke-review",raw_sha256=rr["raw_sha256"],structured_payload=review_struct,requested_model=REVIEWER_MODEL,resolved_model=rr["resolved_model"],research_objects=[],root=root);record_api_memory_consumption(run_id=rr["run_id"],stage="memory-search-smoke-review",pack=rprep["history_pack"],raw_sha256=rr["raw_sha256"],output_object_ids=list(by_blind),outcome_status="SEARCH_SMOKE_BLIND_REVIEW_ZERO_AUTHORITY",root=root)
        metrics={}
        for arm in ARMS:
            rs=per[arm];ideas=gens[arm]["ideas"]
            rate=lambda key:sum(bool(r.get(key)) for r in rs)/len(rs)
            survivors=sum((not bool(r.get("history_near_duplicate"))) and (not bool(r.get("same_information_reduction_risk"))) and bool(r.get("agent_specific")) and bool(r.get("cheapest_falsifier_complete")) for r in rs)
            others=[x for a in ARMS if a!=arm for x in gens[a]["ideas"]]
            metrics[arm]={"n":len(rs),"history_pack_duplicate_rate":rate("history_near_duplicate"),"same_information_reduction_risk_rate":rate("same_information_reduction_risk"),"agent_specific_rate":rate("agent_specific"),"cheapest_falsifier_complete_rate":rate("cheapest_falsifier_complete"),"search_survivor_count":survivors,"search_survivor_rate":survivors/len(rs),"within_arm_lexical_diversity":_diversity(ideas),"mean_max_cross_arm_lexical_similarity":_max_cross_similarity(ideas,others),"generation_input_tokens":gens[arm]["usage"]["input_tokens"],"generation_output_tokens":gens[arm]["usage"]["output_tokens"],"selected_memory_items":int((prep["packs"][arm].get("summary") or {}).get("selected") or 0),"selected_memory_characters":int((prep["packs"][arm].get("summary") or {}).get("characters") or 0)}
        primary={"comparison":"relevant_vs_random","matched_nonzero_item_count":metrics["relevant"]["selected_memory_items"]==metrics["random"]["selected_memory_items"],"survivor_rate_delta":metrics["relevant"]["search_survivor_rate"]-metrics["random"]["search_survivor_rate"],"duplicate_rate_delta":metrics["relevant"]["history_pack_duplicate_rate"]-metrics["random"]["history_pack_duplicate_rate"],"reduction_risk_rate_delta":metrics["relevant"]["same_information_reduction_risk_rate"]-metrics["random"]["same_information_reduction_risk_rate"],"interpretation":"matched-overhead search-policy smoke only; not scientific-performance/publication-success evidence"}
        report={"schema_version":"1.0","status":"API_MEMORY_SEARCH_SMOKE_COMPLETE","study":"API_MEMORY_SEARCH_SMOKE_V22_STAGED","memory_instance_id":prep["packs"]["relevant"]["memory_instance_id"],"frozen_ablation_plan_sha256":prep["plan"]["plan_sha256"],"history_pool_available_objects":int((prep["packs"]["relevant"].get("summary") or {}).get("available") or 0),"generator_model":GENERATOR_MODEL,"reviewer_model":REVIEWER_MODEL,"metrics":metrics,"primary_comparison":primary,"review_scope":"history_near_duplicate is scoped to the single frozen reviewer history pack","generated_outputs_promoted_to_research_objects":False,"scientific_authority":False,"belief_authority":False};report["report_sha256"]=_sha_text(_canonical(report));_write(output,report);return report
    finally:
        if output.exists():lock.unlink(missing_ok=True)


def main()->None:
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
    for cmd in ("prepare","prepare-review","review","finalize"):
        p=sub.add_parser(cmd);p.add_argument("--persistent-root",type=Path,required=True);p.add_argument("--study",type=Path,required=True);p.add_argument("--prefix",default="api-memory-search-smoke-v22-r4")
    p=sub.add_parser("generate");p.add_argument("--persistent-root",type=Path,required=True);p.add_argument("--study",type=Path,required=True);p.add_argument("--arm",choices=ARMS,required=True)
    a=ap.parse_args()
    if a.cmd=="prepare":out=prepare(root=a.persistent_root,study=a.study,prefix=a.prefix)
    elif a.cmd=="generate":out=generate_arm(root=a.persistent_root,study=a.study,arm=a.arm)
    elif a.cmd=="prepare-review":out=prepare_review(root=a.persistent_root,study=a.study)
    elif a.cmd=="review":out=run_review(root=a.persistent_root,study=a.study)
    else:out=finalize(root=a.persistent_root,study=a.study)
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
