from __future__ import annotations

import argparse,hashlib,json,os,re
from datetime import datetime,timezone
from pathlib import Path

from .ark_provider import extract_json_object
from .config import PROJECT_ROOT
from .paper_first_problem_discovery_contract import SEARCH_PORTFOLIO_PRIMITIVES, audit_problem_candidate, audit_shadow_problem_candidate
from .paper_first_problem_generator import _ark,_apply_reviews,_normalize
from .paper_first_problem_generator_prompts import reviewer_prompt
from .paper_first_primary_evidence import parse_arxiv_page,extract_empirical_fact_candidates,extract_typed_evidence_candidates
from .paper_first_problem_search_portfolio import (
    _archives,_assign_structural_clusters,_evolution_prompt,_expansion_prompt,_formulation_prompt,
    _maxmin_select,_normalize_seed,_score,_semantic_dedup,_valid_seed,
)


DEFAULT_SHADOW_DEAD_END_MEMORY_PATH=PROJECT_ROOT/"generated"/"paper-first-search-portfolio-design-adjudication.json"


def _archive_raw_before_parse(run_root:Path,stem:str,raw:str,resolved_model:str)->tuple[str,Path]:
    sha=hashlib.sha256(raw.encode()).hexdigest();raw_root=run_root/"raw";raw_root.mkdir(parents=True,exist_ok=True);path=raw_root/f"{stem}-{sha[:12]}.txt";path.write_text(raw,encoding="utf-8");return sha,path


def _parse_archived_json(run_root:Path,stem:str,raw:str,resolved_model:str)->tuple[dict,str]:
    sha,_=_archive_raw_before_parse(run_root,stem,raw,resolved_model)
    try:return extract_json_object(raw),sha
    except Exception as error:
        err={"schema_version":"1.0","stage":stem,"status":"PARSE_ERROR_ZERO_AUTHORITY","resolved_model":resolved_model,"raw_sha256":sha,"error":f"{type(error).__name__}:{str(error)[:1200]}","scientific_authority":False}
        (run_root/f"error-{stem}-{sha[:12]}.json").write_text(json.dumps(err,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raise


def _ark_with_provider_receipt(*,run_root:Path,stem:str,requested_model:str,context:dict|None=None,**kwargs)->dict:
    try:
        return _ark(model=requested_model,**kwargs)
    except Exception as error:
        message=f"{type(error).__name__}:{str(error)[:1600]}";fingerprint=hashlib.sha256(json.dumps({"stage":stem,"requested_model":requested_model,"error":message},sort_keys=True,separators=(",",":")).encode()).hexdigest()
        timeout=any(token in message.lower() for token in ("timeout","timed out","read timed out"))
        payload={"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"stage":stem,"status":"PROVIDER_TIMEOUT_ZERO_AUTHORITY" if timeout else "PROVIDER_ERROR_ZERO_AUTHORITY","requested_model":requested_model,"complete_response_received":False,"raw_sha256":"","error_fingerprint":fingerprint,"error":message,"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
        if isinstance(context,dict):payload.update({k:v for k,v in context.items() if k in {"lane","part","generation","branch_ids","candidate_ids","requested","requested_children"}})
        run_root.mkdir(parents=True,exist_ok=True);(run_root/f"error-{stem}-provider-{fingerprint[:12]}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        raise

def _shadow_dead_end_memory(path:Path|None)->dict:
    resolved=path or DEFAULT_SHADOW_DEAD_END_MEMORY_PATH
    if not resolved.exists():return {}
    payload=json.loads(resolved.read_text(encoding="utf-8"))
    memory=payload.get("shadow_dead_end_memory") if isinstance(payload,dict) else None
    if not isinstance(memory,dict):memory=payload if isinstance(payload,dict) else {}
    if memory.get("scientific_authority") is not False or memory.get("live_source_coverage_effect") is not False or memory.get("cannot_mutate_canonical_generator_or_queue") is not True:
        raise ValueError("shadow dead-end memory must be zero-authority and unable to mutate canonical discovery")
    return memory


def _text_tokens(value:str)->set[str]:
    return {token for token in re.findall(r"[a-z0-9]+",str(value or "").lower()) if len(token)>=3}


def _text_jaccard(left:str,right:str)->float:
    a,b=_text_tokens(left),_text_tokens(right)
    return len(a&b)/len(a|b) if a and b else 0.0


def _semantic_dead_end_seed_blocker(seed:dict,memory:dict,pool_sha:str)->dict|None:
    lane=str(seed.get("discovery_lane") or "").strip().upper()
    evidence=seed.get("empirical_evidence") or {}
    refs=sorted({str((evidence.get(key) or {}).get("ref") or "").strip() for key in ("source_a","source_b") if str((evidence.get(key) or {}).get("ref") or "").strip()})
    claims=" ".join(str((evidence.get(key) or {}).get("claim") or "") for key in ("source_a","source_b"))
    problem=" ".join(str(seed.get(key) or "") for key in ("title","problem_seed","scientific_tension","structural_signature","irreducible_object","exact_prediction"))
    for row in memory.get("blocked_objects") or []:
        if not isinstance(row,dict):continue
        basin=str(row.get("basin") or "")
        if not basin.startswith(("semantic-exact-reduction-","semantic-lane-contract-")):continue
        if str(row.get("frozen_pool_sha256") or "")!=str(pool_sha or ""):continue
        if str(row.get("search_primitive") or "").strip().upper()!=lane:continue
        memory_refs=sorted({str(ref) for ref in row.get("current_source_refs") or [] if str(ref)})
        if refs!=memory_refs:continue
        claim_sim=_text_jaccard(claims," ".join(str(value) for value in row.get("evidence_claims") or []))
        problem_sim=_text_jaccard(problem,str(row.get("problem_text") or ""))
        if claim_sim<0.55 and problem_sim<0.35:continue
        return {"basin":basin,"source_candidate_id":str(row.get("source_candidate_id") or ""),"search_primitive":lane,"source_refs":refs,"claim_similarity":round(claim_sim,4),"problem_similarity":round(problem_sim,4),"reason":"same frozen evidence pool re-entered a persisted semantic dead-end without new evidence","scientific_authority":False}
    return None


def expand(*,pool:Path,run_root:Path,lane:str,count:int=6,model:str="ark-code-latest",part:int=1,memory_path:Path|None=None) -> dict:
    payload=json.loads(pool.read_text(encoding="utf-8"));records=payload.get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    lane=lane.strip().upper()
    if lane not in SEARCH_PORTFOLIO_PRIMITIVES:raise ValueError(f"unknown search primitive {lane}")
    memory=_shadow_dead_end_memory(memory_path);prompt=_expansion_prompt(lane,records,count,memory);res=_ark_with_provider_receipt(run_root=run_root,stem=f"expand-{lane}-p{part}",requested_model=model,context={"lane":lane,"part":part,"requested":count},prompt=prompt,max_output_tokens=5200,temperature=.85);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);parsed,raw_sha=_parse_archived_json(run_root,f"expand-{lane}-p{part}",raw,resolved)
    pool_sha=str(payload.get("frozen_pool_sha256") or "").strip();seeds=[];dead_end_blocks=[]
    for i,item in enumerate(parsed.get("seeds") or [],1):
        if not isinstance(item,dict):continue
        row=_normalize_seed(item,lane,i);row["seed_id"]=f"{lane}-P{part}-{i:03d}"
        if not _valid_seed(row,registry):continue
        blocker=_semantic_dead_end_seed_blocker(row,memory,pool_sha)
        if blocker:
            dead_end_blocks.append({"seed_id":row["seed_id"],**blocker});continue
        seeds.append(row)
    out={"schema_version":"1.3","lane":lane,"part":part,"requested":count,"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"shadow_dead_end_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"valid_seeds":len(seeds),"semantic_dead_end_blocks":dead_end_blocks,"semantic_dead_end_block_count":len(dead_end_blocks),"seeds":seeds,"scientific_authority":False}
    run_root.mkdir(parents=True,exist_ok=True);(run_root/f"expand-{lane}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {k:out[k] for k in ("lane","part","requested","resolved_model","raw_sha256","valid_seeds")}


def assemble(*,run_root:Path,archive_capacity:int=48,evolution_parents:int=24)->dict:
    raw=[];shards=[]
    for path in sorted(run_root.glob("expand-*.json")):
        payload=json.loads(path.read_text(encoding="utf-8"));rows=[row for row in (payload.get("seeds") or []) if isinstance(row,dict)];raw.extend(rows);shards.append({"path":path.name,"lane":payload.get("lane"),"part":payload.get("part","legacy"),"requested":payload.get("requested"),"valid_seeds":len(rows),"semantic_dead_end_blocks":int(payload.get("semantic_dead_end_block_count") or 0),"raw_sha256":payload.get("raw_sha256"),"resolved_model":payload.get("resolved_model")})
    unique,dups=_semantic_dedup(raw);unique,clusters=_assign_structural_clusters(unique);archives=_archives(unique,archive_capacity);by_id={row["seed_id"]:row for row in unique};breadth=[by_id[sid] for sid in archives["breadth"] if sid in by_id];parents=_maxmin_select(breadth,min(evolution_parents,len(breadth)))
    lane_counts={lane:sum(row.get("discovery_lane")==lane for row in raw) for lane in SEARCH_PORTFOLIO_PRIMITIVES};archive_lanes={lane:sum(by_id[sid].get("discovery_lane")==lane for sid in archives["breadth"] if sid in by_id) for lane in SEARCH_PORTFOLIO_PRIMITIVES}
    out={"schema_version":"1.1","shards":shards,"summary":{"raw_seeds":len(raw),"semantic_dead_end_blocks":sum(int(shard.get("semantic_dead_end_blocks") or 0) for shard in shards),"semantic_unique":len(unique),"semantic_duplicates":len(dups),"structural_clusters":clusters,"breadth_archive":len(archives["breadth"]),"evolution_parents":len(parents),"lane_coverage":sum(value>0 for value in lane_counts.values()),"archive_lane_coverage":sum(value>0 for value in archive_lanes.values())},"lane_counts":lane_counts,"archive_lane_counts":archive_lanes,"archives":archives,"duplicates":dups,"unique_seeds":unique,"parents":parents,"scientific_authority":False}
    (run_root/"base.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def evolve(*,pool:Path,run_root:Path,generation:int,part:int,batch_size:int=6,model:str="ark-code-latest",memory_path:Path|None=None)->dict:
    pool_payload=json.loads(pool.read_text(encoding="utf-8"));records=pool_payload.get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")};pool_sha=str(pool_payload.get("frozen_pool_sha256") or "").strip();base=json.loads((run_root/"base.json").read_text(encoding="utf-8"))
    if generation==1:parents=base.get("parents") or []
    elif generation==2:
        g1=[]
        for path in sorted(run_root.glob("evolve-g1-p*.json")):g1.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
        parents=_maxmin_select(g1,min(12,len(g1)))
    else:raise ValueError("generation must be 1 or 2")
    start=(part-1)*batch_size;batch=parents[start:start+batch_size]
    if not batch:raise ValueError(f"empty evolution batch generation={generation} part={part}")
    memory=_shadow_dead_end_memory(memory_path);temperature=.60 if generation==1 else .35;prompt=_evolution_prompt(batch,generation)+" SHADOW DEAD-END MEMORY (search control only; never scientific authority)="+json.dumps(memory,ensure_ascii=False,separators=(",",":"));res=_ark_with_provider_receipt(run_root=run_root,stem=f"evolve-g{generation}-p{part}",requested_model=model,context={"generation":generation,"part":part,"requested_children":len(batch)},prompt=prompt,max_output_tokens=5200,temperature=temperature);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,raw_sha=_parse_archived_json(run_root,f"evolve-g{generation}-p{part}",raw,resolved);pmap={p["seed_id"]:p for p in batch};children=[];dead_end_blocks=[]
    for i,item in enumerate(payload.get("children") or [],1):
        if not isinstance(item,dict):continue
        parent=pmap.get(str(item.get("parent_id") or ""))
        if not parent:continue
        merged={**parent,**item,"discovery_lane":parent["discovery_lane"],"empirical_evidence":parent["empirical_evidence"],"lane_evidence":parent["lane_evidence"],"cross_domain_origin":parent.get("cross_domain_origin","")};row=_normalize_seed(merged,parent["discovery_lane"],i);row["seed_id"]=f"{parent['seed_id']}-G{generation}";row["parent_id"]=parent["seed_id"];row["branch_depth"]=generation
        if not _valid_seed(row,registry):continue
        blocker=_semantic_dead_end_seed_blocker(row,memory,pool_sha)
        if blocker:
            dead_end_blocks.append({"seed_id":row["seed_id"],**blocker});continue
        children.append(row)
    out={"schema_version":"1.3","generation":generation,"part":part,"parent_ids":[p["seed_id"] for p in batch],"requested_children":len(batch),"valid_children":len(children),"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"shadow_dead_end_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"semantic_dead_end_blocks":dead_end_blocks,"semantic_dead_end_block_count":len(dead_end_blocks),"temperature":temperature,"children":children,"scientific_authority":False}
    (run_root/f"evolve-g{generation}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {k:out[k] for k in ("generation","part","requested_children","valid_children","resolved_model","raw_sha256")}


def formulation_pool(run_root:Path,budget:int=24)->list[dict]:
    base=json.loads((run_root/"base.json").read_text(encoding="utf-8"));rows=list(base.get("parents") or [])
    for path in sorted(run_root.glob("evolve-g1-p*.json")):rows.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
    for path in sorted(run_root.glob("evolve-g2-p*.json")):rows.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
    rows,_=_assign_structural_clusters(rows)
    return _maxmin_select(rows,min(budget,len(rows)))


def formulate(*,pool:Path,run_root:Path,part:int,batch_size:int=2,budget:int=24,model:str="ark-code-latest",memory_path:Path|None=None)->dict:
    pool_payload=json.loads(pool.read_text(encoding="utf-8"));records=pool_payload.get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")};pool_sha=str(pool_payload.get("frozen_pool_sha256") or "").strip();branches=formulation_pool(run_root,budget);start=(part-1)*batch_size;batch=branches[start:start+batch_size]
    if not batch:raise ValueError(f"empty formulation batch part={part}")
    memory=_shadow_dead_end_memory(memory_path);prompt=_formulation_prompt(batch,registry,memory);res=_ark_with_provider_receipt(run_root=run_root,stem=f"formulate-p{part}",requested_model=model,context={"part":part,"branch_ids":[b["seed_id"] for b in batch]},prompt=prompt,max_output_tokens=5600,temperature=.15);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,raw_sha=_parse_archived_json(run_root,f"formulate-p{part}",raw,resolved);live=[x for x in (payload.get("candidates") or []) if isinstance(x,dict)];dead=[x for x in (payload.get("rejected") or []) if isinstance(x,dict)]
    # Preserve branch provenance and typed evidence deterministically. The model
    # may sharpen claims but cannot silently change the source refs or lane.
    by={b["seed_id"]:b for b in batch};normalized=[];dead_end_blocks=[]
    for i,item in enumerate(live,1):
        parent=by.get(str(item.get("source_branch_id") or ""))
        if not parent:continue
        row=dict(item);row["model_candidate_id"]=str(row.get("candidate_id") or "").strip();row["candidate_id"]=f"SHADOW-P{part:02d}-C{i:02d}";row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"]
        blocker=_semantic_dead_end_seed_blocker(row,memory,pool_sha)
        if blocker:
            dead_end_blocks.append({"candidate_id":row["candidate_id"],"source_branch_id":parent["seed_id"],**blocker});continue
        normalized.append(row)
    out={"schema_version":"1.3","part":part,"branch_ids":[b["seed_id"] for b in batch],"resolved_model":resolved,"raw_sha256":raw_sha,"raw_archived_before_parse":True,"shadow_dead_end_memory_sha256":hashlib.sha256(json.dumps(memory,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest() if memory else "","frozen_pool_sha256":pool_sha,"semantic_dead_end_blocks":dead_end_blocks,"semantic_dead_end_block_count":len(dead_end_blocks),"candidates":normalized,"rejected":dead,"scientific_authority":False}
    (run_root/f"formulate-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"branches":len(batch),"candidates":len(normalized),"rejected":len(dead),"resolved_model":out["resolved_model"],"raw_sha256":out["raw_sha256"]}


_PROBLEM_FALSIFIER_ONLY_BLOCKERS=("reduction-falsifiability-contract-incomplete","saturation-exact-reduction-pending:","unresolved-exact-reduction-test:")


def _problem_falsifier_eligible(candidate:dict,audit:dict)->bool:
    blockers=[str(value) for value in audit.get("blockers") or []]
    if not blockers or audit.get("passed") is True:return False
    if not all(any(blocker.startswith(prefix) for prefix in _PROBLEM_FALSIFIER_ONLY_BLOCKERS) for blocker in blockers):return False
    if not any(blocker.startswith(("saturation-exact-reduction-pending:","unresolved-exact-reduction-test:")) for blocker in blockers):return False
    return all(str(candidate.get(key) or "").strip() for key in ("exact_prediction","strongest_same_information_baseline","cheapest_problem_falsifier"))


def machine_audit(*,pool:Path,run_root:Path)->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    reviewable=[];blocked=[];problem_falsifier_queue=[];formulated=0
    for path in sorted(run_root.glob("formulate-p*.json"),key=lambda value:int(value.stem.split("p")[-1])):
        payload=json.loads(path.read_text(encoding="utf-8"));part=int(payload.get("part") or path.stem.split("p")[-1])
        for idx,item in enumerate(payload.get("candidates") or [],1):
            if not isinstance(item,dict):continue
            formulated+=1;raw_candidate=dict(item);model_id=str(raw_candidate.get("model_candidate_id") or raw_candidate.get("candidate_id") or "").strip();raw_candidate["model_candidate_id"]=model_id;raw_candidate["candidate_id"]=f"SHADOW-P{part:02d}-C{idx:02d}"
            candidate=_normalize(raw_candidate,registry);audit=audit_shadow_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=False)
            falsifier_eligible=_problem_falsifier_eligible(candidate,audit)
            row={"candidate_id":candidate["candidate_id"],"model_candidate_id":model_id,"source_artifact":path.name,"candidate":candidate,"audit":audit,"problem_falsifier_eligible":falsifier_eligible}
            (reviewable if audit.get("passed") else blocked).append(row)
            if falsifier_eligible:
                problem_falsifier_queue.append({"candidate_id":candidate["candidate_id"],"title":candidate.get("title"),"discovery_lane":candidate.get("discovery_lane"),"blockers":list(audit.get("blockers") or []),"exact_prediction":candidate.get("exact_prediction"),"strongest_same_information_baseline":candidate.get("strongest_same_information_baseline"),"cheapest_problem_falsifier":candidate.get("cheapest_problem_falsifier"),"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}})
    ids=[row["candidate_id"] for row in reviewable+blocked]
    if len(ids)!=len(set(ids)):raise ValueError("shadow machine audit candidate ids must be unique")
    out={"schema_version":"1.1-shadow","summary":{"formulated":formulated,"reviewable":len(reviewable),"blocked":len(blocked),"problem_falsifier_eligible":len(problem_falsifier_queue),"live_problem_gate_eligible":0},"policy":{"problem_falsifier_route_is_zero_authority":True,"only_exact_reduction_uncertainty_can_enter_problem_falsifier_route":True,"closest_work_lane_provenance_or_schema_failures_cannot_enter_problem_falsifier_route":True,"problem_falsifier_route_cannot_authorize_paper_design_method_experiment_p0_or_gpu":True},"reviewable":reviewable,"blocked":blocked,"problem_falsifier_queue":problem_falsifier_queue,"scientific_authority":False,"authority":{"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"machine-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def review(*,pool:Path,run_root:Path,part:int,batch_size:int=2,model:str="glm-5.2")->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    audit=json.loads((run_root/"machine-audit.json").read_text(encoding="utf-8"));rows=audit.get("reviewable") or [];start=(part-1)*batch_size;selected=rows[start:start+batch_size]
    if not selected:raise ValueError(f"empty review batch part={part}")
    candidates=[dict(row["candidate"]) for row in selected];prompt=reviewer_prompt(candidates,registry,shadow_mode=True);res=_ark_with_provider_receipt(run_root=run_root,stem=f"review-p{part}",requested_model=model,context={"part":part,"candidate_ids":[c["candidate_id"] for c in candidates]},prompt=prompt,max_output_tokens=5200,temperature=0.0);raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,sha=_parse_archived_json(run_root,f"review-p{part}",raw,resolved)
    _apply_reviews(candidates,payload,model,resolved,"doubao-seed-evolving",sha,registry)
    out={"schema_version":"1.1","part":part,"candidate_ids":[c["candidate_id"] for c in candidates],"requested_model":model,"resolved_model":resolved,"raw_sha256":sha,"raw_archived_before_parse":True,"candidates":candidates,"scientific_authority":False}
    (run_root/f"review-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"part":part,"candidate_ids":out["candidate_ids"],"resolved_model":resolved,"raw_sha256":sha,"semantic_clear":sum((c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR" for c in candidates)}


def finalize(*,pool:Path,run_root:Path)->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    machine=json.loads((run_root/"machine-audit.json").read_text(encoding="utf-8"));reviewed=[]
    for path in sorted(run_root.glob("review-p*.json"),key=lambda value:int(value.stem.split("p")[-1])):
        reviewed.extend([row for row in (json.loads(path.read_text(encoding="utf-8")).get("candidates") or []) if isinstance(row,dict)])
    by_id={str(row.get("candidate_id") or ""):row for row in reviewed if row.get("candidate_id")};final_rows=[]
    for row in machine.get("reviewable") or []:
        candidate=by_id.get(str(row.get("candidate_id") or "")) or dict(row.get("candidate") or {})
        shadow=audit_shadow_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=True)
        live=audit_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=True)
        final_rows.append({"candidate_id":candidate.get("candidate_id"),"title":candidate.get("title"),"search_primitive":candidate.get("discovery_lane"),"shadow_clear":bool(shadow.get("passed")),"shadow_audit":shadow,"live_problem_gate_compatible":bool(live.get("passed")),"live_problem_gate_blockers":live.get("blockers") or [],"candidate":candidate})
    clear=sum(row["shadow_clear"] for row in final_rows);live_ready=sum(row["shadow_clear"] and row["live_problem_gate_compatible"] for row in final_rows)
    out={"schema_version":"1.0-shadow","summary":{"machine_reviewable":len(machine.get("reviewable") or []),"reviewed":len(final_rows),"semantic_clear":clear,"semantic_blocked":len(final_rows)-clear,"shadow_survivors":clear,"live_problem_gate_compatible_survivors":live_ready,"live_paper_design_eligible":0},"rows":final_rows,"scientific_authority":False,"policy":{"shadow_survival_is_not_live_problem_gate_pass":True,"shadow_survivor_must_be_reformulated_under_a_live_empirical_lane":True,"canonical_generator_and_queue_untouched":True},"authority":{"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    (run_root/"shadow-final-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("command",choices=("expand","assemble","evolve","formulate","audit","review","finalize"));ap.add_argument("--pool",type=Path);ap.add_argument("--run-root",type=Path,required=True);ap.add_argument("--lane");ap.add_argument("--count",type=int,default=6);ap.add_argument("--part",type=int,default=1);ap.add_argument("--generation",type=int,default=1);ap.add_argument("--model",default="ark-code-latest");ap.add_argument("--memory",type=Path);a=ap.parse_args()
    stop_marker=a.run_root/"shadow-run-qualification-stop.json"
    if stop_marker.exists():
        state=json.loads(stop_marker.read_text(encoding="utf-8"));raise SystemExit(f"shadow run stopped by qualification gate: {state.get('status','STOPPED')}")
    if a.command=="expand":result=expand(pool=a.pool,run_root=a.run_root,lane=a.lane,count=a.count,model=a.model,part=a.part,memory_path=a.memory)
    elif a.command=="assemble":result=assemble(run_root=a.run_root)
    elif a.command=="evolve":result=evolve(pool=a.pool,run_root=a.run_root,generation=a.generation,part=a.part,model=a.model,memory_path=a.memory)
    elif a.command=="formulate":result=formulate(pool=a.pool,run_root=a.run_root,part=a.part,model=a.model,memory_path=a.memory)
    elif a.command=="audit":result=machine_audit(pool=a.pool,run_root=a.run_root)
    elif a.command=="finalize":result=finalize(pool=a.pool,run_root=a.run_root)
    else:result=review(pool=a.pool,run_root=a.run_root,part=a.part,model="glm-5.2" if a.model=="ark-code-latest" else a.model)
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
