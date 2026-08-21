from __future__ import annotations

import argparse, fcntl, json
from pathlib import Path

from .ark_provider import extract_json_object
from .paper_first_problem_generator import _ark
from .discovery_engine_paper_yield_benchmark import (
    ENGINE_SPECS, _audit, _combine, _engine_context, _gen_prompt, _memory_pack, _normalize,
    _now, _primary_pack, _review_prompt, _sha, _sha_json, _summaries,
)


def _client_call(prompt, model, max_output_tokens, temperature, stage):
    return _ark(prompt=prompt,model=model,max_output_tokens=max_output_tokens,temperature=temperature,stage=stage,allow_transport_fallback=False)


def _lock(path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    handle=path.open("a+")
    try:
        fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status":"ALREADY_RUNNING","lock":str(path)})); raise SystemExit(0)
    return handle


def generate(args):
    target=Path(args.run_dir)/f"{args.engine}-generation.json"
    if target.exists(): print(json.dumps({"status":"ALREADY_COMPLETE","path":str(target)})); return
    spec=next((s for s in ENGINE_SPECS if s[0]==args.engine),None)
    if not spec: raise SystemExit(f"unknown engine {args.engine}")
    lock=_lock(Path(args.run_dir)/f".{args.engine}.lock")
    try:
        if target.exists(): print(json.dumps({"status":"ALREADY_COMPLETE","path":str(target)})); return
        pool=json.loads(Path(args.primary_pool).read_text()); memory=json.loads(Path(args.research_memory).read_text())
        primary=_primary_pack(pool); mem=_memory_pack(memory); engine_primary,engine_memory=_engine_context(spec,primary,mem); prompt=_gen_prompt(spec,engine_primary,engine_memory,args.candidates_per_engine)
        res=_client_call(prompt,args.generator_model,7600,.15,"problem_generation"); raw=str(res.get("text") or "")
        raw_path=Path(args.run_dir)/f"{args.engine}-generation.txt"; raw_path.parent.mkdir(parents=True,exist_ok=True); raw_path.write_text(raw,encoding="utf-8")
        payload=extract_json_object(raw); rows=[r for r in (payload.get("candidates") or []) if isinstance(r,dict)][:args.candidates_per_engine]; candidates=[_normalize(r,spec,i) for i,r in enumerate(rows,1)]
        record={"status":"COMPLETE","generated_at":_now(),"engine_id":args.engine,"candidates":candidates,"receipt":{"requested_model":args.generator_model,"resolved_model":res.get("resolved_model") or args.generator_model,"prompt_sha256":_sha(prompt.encode()),"raw_sha256":_sha(raw.encode()),"generated":len(candidates),"context_primary_refs":[r.get("ref") for r in engine_primary],"context_memory_ids":[r.get("memory_id") for r in engine_memory],"usage":res.get("usage") or {},"scientific_authority":False},"scientific_authority":False}
        target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"COMPLETE","engine":args.engine,"generated":len(candidates),"resolved_model":record["receipt"]["resolved_model"]},ensure_ascii=False))
    finally: lock.close()


def _all_candidates(run_dir):
    rows=[]; receipts=[]
    for eid,_,_ in ENGINE_SPECS:
        path=Path(run_dir)/f"{eid}-generation.json"
        if not path.exists(): raise SystemExit(f"missing generation stage: {eid}")
        d=json.loads(path.read_text()); rows.extend(d.get("candidates") or []); receipts.append({"engine_id":eid,**(d.get("receipt") or {})})
    return rows,receipts


def review(args):
    target=Path(args.run_dir)/f"review-{args.batch:02d}.json"
    if target.exists(): print(json.dumps({"status":"ALREADY_COMPLETE","path":str(target)})); return
    lock=_lock(Path(args.run_dir)/f".review-{args.batch:02d}.lock")
    try:
        if target.exists(): print(json.dumps({"status":"ALREADY_COMPLETE","path":str(target)})); return
        pool=json.loads(Path(args.primary_pool).read_text()); memory=json.loads(Path(args.research_memory).read_text()); primary=_primary_pack(pool); mem=_memory_pack(memory); prefs={r["ref"] for r in primary if r.get("ref")}; mids={r["memory_id"] for r in mem if r.get("memory_id")}; candidates,_=_all_candidates(args.run_dir)
        start=(args.batch-1)*args.review_batch_size; batch=candidates[start:start+args.review_batch_size]
        if not batch: raise SystemExit(f"empty review batch {args.batch}")
        prompt=_review_prompt(batch,prefs,mids); res=_client_call(prompt,args.reviewer_model,7600,0.0,"semantic_review"); raw=str(res.get("text") or "")
        raw_path=Path(args.run_dir)/f"review-{args.batch:02d}.txt"; raw_path.write_text(raw,encoding="utf-8"); payload=extract_json_object(raw); reviews=[r for r in (payload.get("reviews") or []) if isinstance(r,dict)]
        record={"status":"COMPLETE","generated_at":_now(),"batch":args.batch,"candidate_ids":[r["candidate_id"] for r in batch],"reviews":reviews,"receipt":{"requested_model":args.reviewer_model,"resolved_model":res.get("resolved_model") or args.reviewer_model,"prompt_sha256":_sha(prompt.encode()),"raw_sha256":_sha(raw.encode()),"reviewed":len(reviews),"usage":res.get("usage") or {},"scientific_authority":False},"scientific_authority":False}; target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"COMPLETE","batch":args.batch,"reviewed":len(reviews),"resolved_model":record["receipt"]["resolved_model"]},ensure_ascii=False))
    finally: lock.close()


def finalize(args):
    pool=json.loads(Path(args.primary_pool).read_text()); memory=json.loads(Path(args.research_memory).read_text()); primary=_primary_pack(pool); mem=_memory_pack(memory); prefs={r["ref"] for r in primary if r.get("ref")}; mids={r["memory_id"] for r in mem if r.get("memory_id")}; candidates,greceipts=_all_candidates(args.run_dir)
    reviews={}; rreceipts=[]
    batches=(len(candidates)+args.review_batch_size-1)//args.review_batch_size
    for b in range(1,batches+1):
        path=Path(args.run_dir)/f"review-{b:02d}.json"
        if not path.exists(): raise SystemExit(f"missing review stage {b}")
        d=json.loads(path.read_text()); rreceipts.append({"batch":b,**(d.get("receipt") or {})})
        for r in d.get("reviews") or []:
            if isinstance(r,dict) and r.get("candidate_id"): reviews[str(r["candidate_id"])]=r
    rows=[_combine(r,reviews.get(r["candidate_id"],{}),_audit(r,prefs,mids)) for r in candidates]; ranking=_summaries(rows,args.candidates_per_engine); top=sorted(rows,key=lambda r:(r["benchmark_outcome"]["paper_design_ready"],r["benchmark_outcome"]["pre_f0_ready"],r["benchmark_outcome"]["paper_conversion_score"],-r["benchmark_outcome"]["distance_to_paper"]),reverse=True)[:10]
    report={"schema_version":"1.0","benchmark_id":"discovery-engine-paper-yield-v1","generated_at":_now(),"status":"COMPLETE","policy":{"same_frozen_evidence_snapshot_for_all_engines":True,"same_candidate_budget_per_engine":True,"same_generator_model_for_all_engines":True,"same_independent_review_rubric_for_all_engines":True,"review_is_advisory_not_novelty_authority":True,"paper_design_ready_is_benchmark_readiness_not_canonical_authority":True,"benchmark_authorizes_nothing":True},"source_snapshot":{"primary_pool_sha256":_sha_json(pool),"research_memory_wiki_sha256":memory.get("wiki_sha256") or _sha_json(memory),"primary_records_supplied":len(primary),"memory_entries_supplied":len(mem)},"models":{"generator_requested":args.generator_model,"reviewer_requested":args.reviewer_model},"summary":{"engines":7,"requested_candidates":7*args.candidates_per_engine,"generated_candidates":len(rows),"pre_f0_ready":sum(r["benchmark_outcome"]["pre_f0_ready"] for r in rows),"paper_design_ready":sum(r["benchmark_outcome"]["paper_design_ready"] for r in rows),"generator_calls":len(greceipts),"reviewer_calls":len(rreceipts)},"engine_ranking":ranking,"top_candidates":[{"candidate_id":r["candidate_id"],"engine_id":r["engine_id"],"title":r.get("title"),**r["benchmark_outcome"],"hard_blocker":r["review"]["hard_blocker"],"minimum_next_evidence":r["review"]["minimum_next_evidence"]} for r in top],"candidates":rows,"provider_receipts":{"generation":greceipts,"review":rreceipts},"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"COMPLETE","summary":report["summary"],"ranking":ranking},ensure_ascii=False,indent=2))


def main():
    p=argparse.ArgumentParser(); p.add_argument("phase",choices=("generate","review","finalize")); p.add_argument("--primary-pool",required=True); p.add_argument("--research-memory",required=True); p.add_argument("--run-dir",required=True); p.add_argument("--output",default="generated/discovery-engine-paper-yield-benchmark.json"); p.add_argument("--engine"); p.add_argument("--batch",type=int,default=1); p.add_argument("--review-batch-size",type=int,default=7); p.add_argument("--candidates-per-engine",type=int,default=4); p.add_argument("--generator-model",default="kimi-k3"); p.add_argument("--reviewer-model",default="deepseek-v4-pro"); a=p.parse_args(); {"generate":generate,"review":review,"finalize":finalize}[a.phase](a)
if __name__=="__main__": main()
