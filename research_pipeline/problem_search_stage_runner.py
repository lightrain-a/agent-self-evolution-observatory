from __future__ import annotations

import argparse,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path

from .ark_provider import extract_json_object
from .paper_first_problem_discovery_contract import DISCOVERY_LANES
from .paper_first_problem_generator import _ark,_apply_reviews
from .paper_first_problem_generator_prompts import reviewer_prompt
from .paper_first_primary_evidence import parse_arxiv_page,extract_empirical_fact_candidates,extract_typed_evidence_candidates
from .paper_first_problem_search_portfolio import (
    _archives,_assign_structural_clusters,_evolution_prompt,_expansion_prompt,_formulation_prompt,
    _maxmin_select,_normalize_seed,_score,_semantic_dedup,_valid_seed,
)


def expand(*,pool:Path,run_root:Path,lane:str,count:int=6,model:str="ark-code-latest",part:int=1) -> dict:
    payload=json.loads(pool.read_text(encoding="utf-8"));records=payload.get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    lane=lane.strip().upper()
    if lane not in DISCOVERY_LANES:raise ValueError(f"unknown lane {lane}")
    prompt=_expansion_prompt(lane,records,count);res=_ark(prompt=prompt,model=model,max_output_tokens=5200,temperature=.85);raw=str(res.get("text") or "");parsed=extract_json_object(raw)
    seeds=[]
    for i,item in enumerate(parsed.get("seeds") or [],1):
        if not isinstance(item,dict):continue
        row=_normalize_seed(item,lane,i);row["seed_id"]=f"{lane}-P{part}-{i:03d}"
        if _valid_seed(row,registry):seeds.append(row)
    out={"schema_version":"1.0","lane":lane,"part":part,"requested":count,"resolved_model":str(res.get("resolved_model") or model),"raw_sha256":hashlib.sha256(raw.encode()).hexdigest(),"valid_seeds":len(seeds),"seeds":seeds,"scientific_authority":False}
    run_root.mkdir(parents=True,exist_ok=True);(run_root/f"expand-{lane}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    raw_root=run_root/"raw";raw_root.mkdir(exist_ok=True);(raw_root/f"expand-{lane}-p{part}-{out['raw_sha256'][:12]}.txt").write_text(raw,encoding="utf-8")
    return {k:out[k] for k in ("lane","part","requested","resolved_model","raw_sha256","valid_seeds")}


def assemble(*,run_root:Path,archive_capacity:int=48,evolution_parents:int=24)->dict:
    raw=[];shards=[]
    for path in sorted(run_root.glob("expand-*.json")):
        payload=json.loads(path.read_text(encoding="utf-8"));rows=[row for row in (payload.get("seeds") or []) if isinstance(row,dict)];raw.extend(rows);shards.append({"path":path.name,"lane":payload.get("lane"),"part":payload.get("part","legacy"),"requested":payload.get("requested"),"valid_seeds":len(rows),"raw_sha256":payload.get("raw_sha256"),"resolved_model":payload.get("resolved_model")})
    unique,dups=_semantic_dedup(raw);unique,clusters=_assign_structural_clusters(unique);archives=_archives(unique,archive_capacity);by_id={row["seed_id"]:row for row in unique};breadth=[by_id[sid] for sid in archives["breadth"] if sid in by_id];parents=_maxmin_select(breadth,min(evolution_parents,len(breadth)))
    lane_counts={lane:sum(row.get("discovery_lane")==lane for row in raw) for lane in DISCOVERY_LANES};archive_lanes={lane:sum(by_id[sid].get("discovery_lane")==lane for sid in archives["breadth"] if sid in by_id) for lane in DISCOVERY_LANES}
    out={"schema_version":"1.0","shards":shards,"summary":{"raw_seeds":len(raw),"semantic_unique":len(unique),"semantic_duplicates":len(dups),"structural_clusters":clusters,"breadth_archive":len(archives["breadth"]),"evolution_parents":len(parents),"lane_coverage":sum(value>0 for value in lane_counts.values()),"archive_lane_coverage":sum(value>0 for value in archive_lanes.values())},"lane_counts":lane_counts,"archive_lane_counts":archive_lanes,"archives":archives,"duplicates":dups,"unique_seeds":unique,"parents":parents,"scientific_authority":False}
    (run_root/"base.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return out["summary"]


def evolve(*,pool:Path,run_root:Path,generation:int,part:int,batch_size:int=6,model:str="ark-code-latest")->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")};base=json.loads((run_root/"base.json").read_text(encoding="utf-8"))
    if generation==1:parents=base.get("parents") or []
    elif generation==2:
        g1=[]
        for path in sorted(run_root.glob("evolve-g1-p*.json")):g1.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
        parents=sorted(g1,key=_score,reverse=True)[:12]
    else:raise ValueError("generation must be 1 or 2")
    start=(part-1)*batch_size;batch=parents[start:start+batch_size]
    if not batch:raise ValueError(f"empty evolution batch generation={generation} part={part}")
    temperature=.60 if generation==1 else .35;prompt=_evolution_prompt(batch,generation);res=_ark(prompt=prompt,model=model,max_output_tokens=5200,temperature=temperature);raw=str(res.get("text") or "");payload=extract_json_object(raw);pmap={p["seed_id"]:p for p in batch};children=[]
    for i,item in enumerate(payload.get("children") or [],1):
        if not isinstance(item,dict):continue
        parent=pmap.get(str(item.get("parent_id") or ""))
        if not parent:continue
        merged={**parent,**item,"discovery_lane":parent["discovery_lane"],"empirical_evidence":parent["empirical_evidence"],"lane_evidence":parent["lane_evidence"],"cross_domain_origin":parent.get("cross_domain_origin","")};row=_normalize_seed(merged,parent["discovery_lane"],i);row["seed_id"]=f"{parent['seed_id']}-G{generation}";row["parent_id"]=parent["seed_id"];row["branch_depth"]=generation
        if _valid_seed(row,registry):children.append(row)
    out={"schema_version":"1.0","generation":generation,"part":part,"parent_ids":[p["seed_id"] for p in batch],"requested_children":len(batch),"valid_children":len(children),"resolved_model":str(res.get("resolved_model") or model),"raw_sha256":hashlib.sha256(raw.encode()).hexdigest(),"temperature":temperature,"children":children,"scientific_authority":False}
    (run_root/f"evolve-g{generation}-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raw_root=run_root/"raw";raw_root.mkdir(exist_ok=True);(raw_root/f"evolve-g{generation}-p{part}-{out['raw_sha256'][:12]}.txt").write_text(raw,encoding="utf-8")
    return {k:out[k] for k in ("generation","part","requested_children","valid_children","resolved_model","raw_sha256")}


def formulation_pool(run_root:Path,budget:int=24)->list[dict]:
    base=json.loads((run_root/"base.json").read_text(encoding="utf-8"));rows=list(base.get("parents") or [])
    for path in sorted(run_root.glob("evolve-g1-p*.json")):rows.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
    for path in sorted(run_root.glob("evolve-g2-p*.json")):rows.extend(json.loads(path.read_text(encoding="utf-8")).get("children") or [])
    rows,_=_assign_structural_clusters(rows)
    return _maxmin_select(rows,min(budget,len(rows)))


def formulate(*,pool:Path,run_root:Path,part:int,batch_size:int=2,budget:int=24,model:str="ark-code-latest")->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")};branches=formulation_pool(run_root,budget);start=(part-1)*batch_size;batch=branches[start:start+batch_size]
    if not batch:raise ValueError(f"empty formulation batch part={part}")
    prompt=_formulation_prompt(batch,registry);res=_ark(prompt=prompt,model=model,max_output_tokens=5600,temperature=.15);raw=str(res.get("text") or "");payload=extract_json_object(raw);live=[x for x in (payload.get("candidates") or []) if isinstance(x,dict)];dead=[x for x in (payload.get("rejected") or []) if isinstance(x,dict)]
    # Preserve branch provenance and typed evidence deterministically. The model
    # may sharpen claims but cannot silently change the source refs or lane.
    by={b["seed_id"]:b for b in batch};normalized=[]
    for i,item in enumerate(live,1):
        parent=by.get(str(item.get("source_branch_id") or ""))
        if not parent:continue
        row=dict(item);row["candidate_id"]=str(row.get("candidate_id") or f"PORT-{part}-{i}");row["source_branch_id"]=parent["seed_id"];row["branch_depth"]=parent.get("branch_depth",0);row["discovery_lane"]=parent["discovery_lane"];row["empirical_evidence"]=parent["empirical_evidence"];row["lane_evidence"]=parent["lane_evidence"];normalized.append(row)
    out={"schema_version":"1.0","part":part,"branch_ids":[b["seed_id"] for b in batch],"resolved_model":str(res.get("resolved_model") or model),"raw_sha256":hashlib.sha256(raw.encode()).hexdigest(),"candidates":normalized,"rejected":dead,"scientific_authority":False}
    (run_root/f"formulate-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raw_root=run_root/"raw";raw_root.mkdir(exist_ok=True);(raw_root/f"formulate-p{part}-{out['raw_sha256'][:12]}.txt").write_text(raw,encoding="utf-8")
    return {"part":part,"branches":len(batch),"candidates":len(normalized),"rejected":len(dead),"resolved_model":out["resolved_model"],"raw_sha256":out["raw_sha256"]}


def review(*,pool:Path,run_root:Path,part:int,batch_size:int=2,model:str="glm-5.2")->dict:
    records=json.loads(pool.read_text(encoding="utf-8")).get("records") or [];registry={str(r.get("ref")):r for r in records if isinstance(r,dict) and r.get("ref")}
    audit=json.loads((run_root/"machine-audit.json").read_text(encoding="utf-8"));rows=audit.get("reviewable") or [];start=(part-1)*batch_size;selected=rows[start:start+batch_size]
    if not selected:raise ValueError(f"empty review batch part={part}")
    candidates=[dict(row["candidate"]) for row in selected];prompt=reviewer_prompt(candidates,registry);res=_ark(prompt=prompt,model=model,max_output_tokens=5200,temperature=0.0);raw=str(res.get("text") or "");sha=hashlib.sha256(raw.encode()).hexdigest();resolved=str(res.get("resolved_model") or model)
    _apply_reviews(candidates,extract_json_object(raw),model,resolved,"doubao-seed-evolving",sha,registry)
    out={"schema_version":"1.0","part":part,"candidate_ids":[c["candidate_id"] for c in candidates],"requested_model":model,"resolved_model":resolved,"raw_sha256":sha,"candidates":candidates,"scientific_authority":False}
    (run_root/f"review-p{part}.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");raw_root=run_root/"raw";raw_root.mkdir(exist_ok=True);(raw_root/f"review-p{part}-{sha[:12]}.txt").write_text(raw,encoding="utf-8")
    return {"part":part,"candidate_ids":out["candidate_ids"],"resolved_model":resolved,"raw_sha256":sha,"semantic_clear":sum((c.get("semantic_reduction_review") or {}).get("verdict")=="CLEAR" for c in candidates)}


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("command",choices=("expand","assemble","evolve","formulate","review"));ap.add_argument("--pool",type=Path);ap.add_argument("--run-root",type=Path,required=True);ap.add_argument("--lane");ap.add_argument("--count",type=int,default=6);ap.add_argument("--part",type=int,default=1);ap.add_argument("--generation",type=int,default=1);ap.add_argument("--model",default="ark-code-latest");a=ap.parse_args()
    if a.command=="expand":result=expand(pool=a.pool,run_root=a.run_root,lane=a.lane,count=a.count,model=a.model,part=a.part)
    elif a.command=="assemble":result=assemble(run_root=a.run_root)
    elif a.command=="evolve":result=evolve(pool=a.pool,run_root=a.run_root,generation=a.generation,part=a.part,model=a.model)
    elif a.command=="formulate":result=formulate(pool=a.pool,run_root=a.run_root,part=a.part,model=a.model)
    else:result=review(pool=a.pool,run_root=a.run_root,part=a.part,model="glm-5.2" if a.model=="ark-code-latest" else a.model)
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
