from __future__ import annotations

import argparse, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object

Caller = Callable[..., dict[str, Any]]
ENGINE_SPECS = (
    ("D1", "literature_closure_contradiction", "Start from primary findings plus closure/hold memory. Find a real contradiction, violated assumption, or recorded reopen condition materially satisfied by new evidence. Generic literature gaps are invalid."),
    ("D2", "empirical_anomaly_failure_mining", "Start from measured failures, quantitative boundaries, first-party scientific failure/success assets, or unresolved observations. Runtime/protocol/support-only failures have no scientific authority. Birth a question only from an unexplained residual."),
    ("D3", "structural_variable_hypothesis", "Find an Agent-specific structural variable of persistent self-evolution (state, order, locality, decomposition, write/retrieval surface, evaluator coupling, update timing, etc.) that changes an ex-ante prediction after the baseline gets exactly the same information."),
    ("D4", "strongest_baseline_counterexample", "Begin from the strongest simple same-information explanation. Search for a grounded regime where it predicts one outcome and evidence suggests a systematic residual/counterexample. Return fewer candidates instead of inventing residuals."),
    ("D5", "longitudinal_path_dependence", "Search for history/order/horizon dependence: hysteresis, delayed effects, irreversibility, recovery, interference, accumulation, or state-dependent future response. Static snapshot effects are insufficient; require a matched-history/current-state falsifier."),
    ("D6", "executable_symbolic_search", "Define a bounded executable search over update order, memory schedule, task order, workflow/tool state, feedback timing or horizon, with an objective evaluator and outlier/counterexample criterion. The scientific question must be born from what this search can reveal, not generic prose ideation."),
    ("D7", "cross_domain_mechanism_transfer", "Map a mature mechanism from continual learning, online algorithms, control, causal discovery, distributed systems, program synthesis, active learning or information theory. Require an Agent-specific constraint that changes a falsifiable prediction; metaphor-only transfer is invalid."),
)
GATES = {
    "G0": "Grounded provenance; no invented evidence/source.",
    "G1": "Escapes existing closure or materially satisfies its reopen condition.",
    "G2": "Explicit scientific object, alternatives, and measurable uncertainty; not just a feature/method.",
    "G3": "Agent-specific structural variable changes an ex-ante prediction.",
    "G4": "Strongest same-information baseline gets identical state/history/evidence/budget/evaluator access.",
    "G5": "Concrete nontrivial residual where baseline predicts differently; no information withholding.",
    "G6": "Cheap executable falsifier with setup, comparison/intervention, metric, and stop condition.",
    "G7": "Not already absorbed by supplied mature reduction/closure; triage only, not novelty authority.",
    "G8": "Narrow falsifiable paper-level claim with realistic evidence program.",
}
REQUIRED = ("title", "scientific_question", "observed_trigger", "structural_variable", "strongest_same_information_baseline", "baseline_counterexample", "cheapest_falsifier", "closest_known_explanation", "residual_after_reduction", "paper_level_claim")


def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def _sha(raw: bytes): return hashlib.sha256(raw).hexdigest()
def _sha_json(x): return _sha(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
def _trim(x, n=500):
    s=" ".join(str(x or "").split()); return s if len(s)<=n else s[:n-1]+"…"

def _primary_pack(pool, limit=16):
    rows=[r for r in pool.get("records",[]) if isinstance(r,dict)]
    def w(r):
        t=r.get("typed_evidence") or {}; return (4*len(t.get("measured_failures") or [])+4*len(t.get("boundary_observations") or [])+3*len(t.get("operational_assumptions") or [])+len(r.get("empirical_facts") or []), str(r.get("publication_date") or ""))
    out=[]
    for r in sorted(rows,key=w,reverse=True)[:limit]:
        t=r.get("typed_evidence") or {}
        def sn(key): return [_trim((x.get("text") if isinstance(x,dict) else x),360) for x in (t.get(key) or [])[:2] if (x.get("text") if isinstance(x,dict) else x)]
        facts=[_trim((x.get("text") if isinstance(x,dict) else x),360) for x in (r.get("empirical_facts") or [])[:3] if (x.get("text") if isinstance(x,dict) else x)]
        out.append({"ref":r.get("ref"),"title":_trim(r.get("title"),180),"date":r.get("publication_date"),"facts":facts,"assumptions":sn("operational_assumptions"),"failures":sn("measured_failures"),"boundaries":sn("boundary_observations")})
    return out

def _memory_pack(wiki):
    caps={"SCIENTIFIC_CLOSURE":3,"SEARCH_CLOSURE":6,"HOLD":6,"OPEN_QUESTION":3,"FAILURE_ASSET":3,"SUCCESS_ASSET":3,"REPEATED_REVIEW_BLOCK":1}; seen={k:0 for k in caps}; out=[]
    for r in wiki.get("entries",[]):
        if not isinstance(r,dict) or r.get("prompt_eligible") is not True: continue
        k=str(r.get("kind") or "")
        if k not in caps or seen[k]>=caps[k]: continue
        seen[k]+=1; out.append({"memory_id":r.get("memory_id"),"kind":k,"title":_trim(r.get("title"),220),"summary":_trim(r.get("summary"),650),"layer":r.get("affected_layer"),"reopen_condition":_trim(r.get("reopen_condition"),500),"opposite_search_seed":_trim(r.get("opposite_search_seed"),350),"source_refs":(r.get("source_refs") or [])[:6],"scientific_dead_end":bool(r.get("scientific_dead_end_certified"))})
    return out

def _engine_context(spec, primary, memory):
    eid=spec[0]
    keywords={
        "D1":("assumption","fail","boundary","fragility","skill","memory"),
        "D2":("fail","fragility","variance","drift","reward","skill"),
        "D3":("memory","skill","harness","update","evolv","order"),
        "D4":("fail","variance","drift","reward","retrieval","skill"),
        "D5":("time","order","continual","evolving","variance","memory"),
        "D6":("search","harness","repository","architecture","iteration","verification"),
        "D7":("continual","harness","memory","skill","evolving","variance"),
    }[eid]
    def pscore(r):
        text=(str(r.get("title") or "")+" "+" ".join(r.get("failures") or [])+" "+" ".join(r.get("boundaries") or [])).lower()
        return sum(k in text for k in keywords)
    primary_sel=sorted(primary,key=lambda r:(pscore(r),str(r.get("date") or "")),reverse=True)[:8]
    wanted={
        "D1":{"SCIENTIFIC_CLOSURE","SEARCH_CLOSURE","OPEN_QUESTION","HOLD"},
        "D2":{"FAILURE_ASSET","SUCCESS_ASSET","OPEN_QUESTION","HOLD","REPEATED_REVIEW_BLOCK"},
        "D3":{"SCIENTIFIC_CLOSURE","SEARCH_CLOSURE","OPEN_QUESTION","HOLD"},
        "D4":{"SCIENTIFIC_CLOSURE","SEARCH_CLOSURE","HOLD","REPEATED_REVIEW_BLOCK"},
        "D5":{"OPEN_QUESTION","HOLD","SEARCH_CLOSURE","SUCCESS_ASSET"},
        "D6":{"OPEN_QUESTION","HOLD","SCIENTIFIC_CLOSURE","SEARCH_CLOSURE"},
        "D7":{"SCIENTIFIC_CLOSURE","SEARCH_CLOSURE","OPEN_QUESTION","HOLD"},
    }[eid]
    memory_sel=[r for r in memory if r.get("kind") in wanted][:10]
    return primary_sel,memory_sel

def _gen_prompt(spec, primary, memory, n):
    eid,name,rule=spec
    schema={"candidates":[{"title":"","birth_evidence_refs":["arXiv:..."],"memory_refs":["MEM-..."],"scientific_question":"","observed_trigger":"","structural_variable":"","strongest_same_information_baseline":"","baseline_counterexample":"","cheapest_falsifier":{"setup":"","intervention_or_comparison":"","metric":"","stop_if":"","estimated_effort":""},"closest_known_explanation":"","residual_after_reduction":"","paper_level_claim":"","paperability_axis":"P|M|E|B|T|S","executable_now":True}],"no_candidate_reason":""}
    return f'''You are scientific discovery engine {eid} / {name}. Candidate generation has ZERO scientific authority.
BIRTH RULE: {rule}
GLOBAL RULES: use only supplied evidence; persistent/self-evolving agents only; strongest baseline receives the SAME observable information/history/budget/evaluator access; specify a different ex-ante prediction; respect closures and reopen conditions; support/runtime/protocol failure alone is not scientific evidence; prefer the cheapest outcome-independent falsifier before method design; failed ideas are not repaired by changing their core claim; pure-topic brainstorm, missing-cell, and generic shared limitations are forbidden. A phenomenon/theory/evaluation paper is allowed; method novelty is optional. Return at most {n} genuinely grounded candidates; fewer is better than fabrication. Be concise: every free-text candidate field <=45 words, every cheapest_falsifier subfield <=25 words, no prose outside JSON.
PRIMARY EVIDENCE:\n{json.dumps(primary,ensure_ascii=False)}
RESEARCH MEMORY:\n{json.dumps(memory,ensure_ascii=False)}
Return STRICT JSON only in this shape:\n{json.dumps(schema,ensure_ascii=False)}'''

def _review_prompt(rows, primary_refs, memory_ids):
    slim=[{k:r.get(k) for k in ("candidate_id","engine_id",*REQUIRED,"birth_evidence_refs","memory_refs","paperability_axis","executable_now")} for r in rows]
    schema={"reviews":[{"candidate_id":"D1-C01","gate_verdicts":{g:"PASS|HOLD|FAIL" for g in GATES},"hard_blocker":"","strongest_reduction":"","minimum_next_evidence":"","evidence_readiness":0,"falsifier_executability":0,"claim_specificity":0,"estimated_experiments_to_paper":1,"estimated_effort_level":1,"advisory_summary":""}]}
    return f'''You are an INDEPENDENT BLOCK-ONLY scientific triage reviewer. You authorize nothing. Judge structural distance to a paper-ready research program under one identical rubric. Do not reward eloquence.
GATES:\n{json.dumps(GATES,ensure_ascii=False)}
VALID PRIMARY REFS: {sorted(primary_refs)}
VALID MEMORY IDS: {sorted(memory_ids)}
Scores evidence_readiness/falsifier_executability/claim_specificity are integers 0-5. estimated_experiments_to_paper and estimated_effort_level are integers 1-5 (1=near/cheap, 5=far/expensive). Keep every reviewer free-text field <=35 words. G7 is collision/reduction triage only, NOT novelty certification. Invalid cited IDs => G0 FAIL. Existing closure without materially new reopen evidence => G1/G7 FAIL. Same decision under same information => G5 FAIL. New unsupported substrate needed before testing => G6 HOLD/FAIL.
CANDIDATES:\n{json.dumps(slim,ensure_ascii=False)}
Return STRICT JSON only:\n{json.dumps(schema,ensure_ascii=False)}'''

def _normalize(raw,spec,i):
    eid,name,_=spec; r=dict(raw or {}); r.update(candidate_id=f"{eid}-C{i:02d}",engine_id=eid,engine_name=name,scientific_authority=False); r["birth_evidence_refs"]=[str(x).strip() for x in (r.get("birth_evidence_refs") or []) if str(x).strip()]; r["memory_refs"]=[str(x).strip() for x in (r.get("memory_refs") or []) if str(x).strip()]; r["cheapest_falsifier"]=r.get("cheapest_falsifier") if isinstance(r.get("cheapest_falsifier"),dict) else {}; return r

def _audit(r,prefs,mids):
    miss=[]
    for k in REQUIRED:
        v=r.get(k); empty=not any(str(x or "").strip() for x in v.values()) if isinstance(v,dict) else not str(v or "").strip()
        if empty: miss.append(k)
    refs=set(r.get("birth_evidence_refs") or []); mem=set(r.get("memory_refs") or []); f=r.get("cheapest_falsifier") or {}; fc=all(str(f.get(k) or "").strip() for k in ("setup","intervention_or_comparison","metric","stop_if"))
    return {"missing_required_fields":miss,"invalid_primary_refs":sorted(refs-prefs),"invalid_memory_refs":sorted(mem-mids),"has_grounded_primary_ref":bool(refs&prefs),"falsifier_complete":fc,"schema_complete":not miss and fc,"provenance_valid":not(refs-prefs) and not(mem-mids) and bool(refs&prefs)}
def _intval(v,lo,hi,d):
    try: v=int(v)
    except: v=d
    return max(lo,min(hi,v))

def _combine(r,review,audit):
    gv={g:(str((review.get("gate_verdicts") or {}).get(g) or "HOLD").upper()) for g in GATES}; gv={g:(v if v in {"PASS","HOLD","FAIL"} else "HOLD") for g,v in gv.items()}
    if not audit["provenance_valid"]: gv["G0"]="FAIL"
    if not audit["falsifier_complete"]: gv["G6"]="FAIL"
    pre=all(gv[g]=="PASS" for g in ("G0","G1","G2","G3","G4","G5","G6")); paper=pre and gv["G7"]==gv["G8"]=="PASS"
    er=_intval(review.get("evidence_readiness"),0,5,0); fe=_intval(review.get("falsifier_executability"),0,5,0); cs=_intval(review.get("claim_specificity"),0,5,0); ex=_intval(review.get("estimated_experiments_to_paper"),1,5,5); ef=_intval(review.get("estimated_effort_level"),1,5,5)
    pc=sum(v=="PASS" for v in gv.values()); score=50*(pc/9)+3*er+3*fe+2*cs+5*((6-ex)/5)+5*((6-ef)/5)
    groups=(("provenance",("G0",)),("closure_escape",("G1",)),("scientific_object",("G2","G3")),("same_information_residual",("G4","G5")),("cheap_falsifier",("G6",)),("reduction_boundary",("G7",)),("paper_claim",("G8",))); missing=[n for n,gs in groups if not all(gv[g]=="PASS" for g in gs)]
    return {**r,"deterministic_audit":audit,"review":{"gate_verdicts":gv,"hard_blocker":_trim(review.get("hard_blocker"),700),"strongest_reduction":_trim(review.get("strongest_reduction"),700),"minimum_next_evidence":_trim(review.get("minimum_next_evidence"),700),"evidence_readiness":er,"falsifier_executability":fe,"claim_specificity":cs,"estimated_experiments_to_paper":ex,"estimated_effort_level":ef,"advisory_summary":_trim(review.get("advisory_summary"),700)},"benchmark_outcome":{"pre_f0_ready":pre,"paper_design_ready":paper,"paper_conversion_score":round(max(0,min(100,score)),2),"distance_to_paper":len(missing),"missing_milestones":missing},"scientific_authority":False}

def _summaries(rows,n):
    out=[]
    for eid,name,_ in ENGINE_SPECS:
        rr=[r for r in rows if r["engine_id"]==eid]; scores=[r["benchmark_outcome"]["paper_conversion_score"] for r in rr]; dist=[r["benchmark_outcome"]["distance_to_paper"] for r in rr]; ex=[r["review"]["estimated_experiments_to_paper"] for r in rr]; ef=[r["review"]["estimated_effort_level"] for r in rr]; blockers={}
        for r in rr:
            for b in r["benchmark_outcome"]["missing_milestones"]: blockers[b]=blockers.get(b,0)+1
        med=lambda x: round(float(statistics.median(x)),3) if x else None
        out.append({"engine_id":eid,"engine_name":name,"requested":n,"generated":len(rr),"schema_complete":sum(r["deterministic_audit"]["schema_complete"] for r in rr),"provenance_valid":sum(r["deterministic_audit"]["provenance_valid"] for r in rr),"pre_f0_ready":sum(r["benchmark_outcome"]["pre_f0_ready"] for r in rr),"paper_design_ready":sum(r["benchmark_outcome"]["paper_design_ready"] for r in rr),"median_paper_conversion_score":med(scores),"best_paper_conversion_score":max(scores) if scores else None,"median_distance_to_paper":med(dist),"median_estimated_experiments_to_paper":med(ex),"median_effort_level":med(ef),"main_blockers":dict(sorted(blockers.items(),key=lambda x:(-x[1],x[0]))),"scientific_authority":False})
    out.sort(key=lambda s:(s["paper_design_ready"],s["pre_f0_ready"],s["median_paper_conversion_score"] or 0,-(s["median_distance_to_paper"] or 99),-(s["median_effort_level"] or 99)),reverse=True)
    for i,s in enumerate(out,1): s["rank"]=i
    return out

def run_benchmark(primary_pool,research_memory,n,gcall:Caller,rcall:Caller,gmodel,rmodel,raw_dir=None):
    primary=_primary_pack(primary_pool); memory=_memory_pack(research_memory); prefs={r["ref"] for r in primary if r.get("ref")}; mids={r["memory_id"] for r in memory if r.get("memory_id")}; candidates=[]; greceipts=[]; rreceipts=[]; raw_dir=Path(raw_dir) if raw_dir else None
    if raw_dir: raw_dir.mkdir(parents=True,exist_ok=True)
    for spec in ENGINE_SPECS:
        engine_primary,engine_memory=_engine_context(spec,primary,memory)
        prompt=_gen_prompt(spec,engine_primary,engine_memory,n); res=gcall(prompt=prompt,model=gmodel,max_output_tokens=7600,temperature=.15); raw=str(res.get("text") or "")
        if raw_dir: (raw_dir/f"{spec[0]}-generation.txt").write_text(raw,encoding="utf-8")
        payload=extract_json_object(raw); rr=[x for x in (payload.get("candidates") or []) if isinstance(x,dict)][:n]; candidates += [_normalize(x,spec,i) for i,x in enumerate(rr,1)]; greceipts.append({"engine_id":spec[0],"requested_model":gmodel,"resolved_model":res.get("resolved_model") or gmodel,"prompt_sha256":_sha(prompt.encode()),"raw_sha256":_sha(raw.encode()),"generated":len(rr),"usage":res.get("usage") or {},"scientific_authority":False})
    reviews={}
    for start in range(0,len(candidates),7):
        batch=candidates[start:start+7]; prompt=_review_prompt(batch,prefs,mids); res=rcall(prompt=prompt,model=rmodel,max_output_tokens=7600,temperature=0.0); raw=str(res.get("text") or "")
        if raw_dir: (raw_dir/f"review-{start//7+1:02d}.txt").write_text(raw,encoding="utf-8")
        payload=extract_json_object(raw); got={str(x.get("candidate_id")):x for x in (payload.get("reviews") or []) if isinstance(x,dict) and x.get("candidate_id")}; reviews.update(got); rreceipts.append({"batch":start//7+1,"candidate_ids":[r["candidate_id"] for r in batch],"requested_model":rmodel,"resolved_model":res.get("resolved_model") or rmodel,"prompt_sha256":_sha(prompt.encode()),"raw_sha256":_sha(raw.encode()),"reviewed":len(got),"usage":res.get("usage") or {},"scientific_authority":False})
    rows=[_combine(r,reviews.get(r["candidate_id"],{}),_audit(r,prefs,mids)) for r in candidates]; ranking=_summaries(rows,n); top=sorted(rows,key=lambda r:(r["benchmark_outcome"]["paper_design_ready"],r["benchmark_outcome"]["pre_f0_ready"],r["benchmark_outcome"]["paper_conversion_score"],-r["benchmark_outcome"]["distance_to_paper"]),reverse=True)[:10]
    return {"schema_version":"1.0","benchmark_id":"discovery-engine-paper-yield-v1","generated_at":_now(),"status":"COMPLETE","policy":{"same_frozen_evidence_snapshot_for_all_engines":True,"same_candidate_budget_per_engine":True,"same_generator_model_for_all_engines":True,"same_independent_review_rubric_for_all_engines":True,"review_is_advisory_not_novelty_authority":True,"paper_design_ready_is_benchmark_readiness_not_canonical_authority":True,"benchmark_authorizes_nothing":True},"source_snapshot":{"primary_pool_sha256":_sha_json(primary_pool),"research_memory_wiki_sha256":research_memory.get("wiki_sha256") or _sha_json(research_memory),"primary_records_supplied":len(primary),"memory_entries_supplied":len(memory)},"models":{"generator_requested":gmodel,"reviewer_requested":rmodel},"summary":{"engines":7,"requested_candidates":7*n,"generated_candidates":len(rows),"pre_f0_ready":sum(r["benchmark_outcome"]["pre_f0_ready"] for r in rows),"paper_design_ready":sum(r["benchmark_outcome"]["paper_design_ready"] for r in rows),"generator_calls":len(greceipts),"reviewer_calls":len(rreceipts)},"engine_ranking":ranking,"top_candidates":[{"candidate_id":r["candidate_id"],"engine_id":r["engine_id"],"title":r.get("title"),**r["benchmark_outcome"],"hard_blocker":r["review"]["hard_blocker"],"minimum_next_evidence":r["review"]["minimum_next_evidence"]} for r in top],"candidates":rows,"provider_receipts":{"generation":greceipts,"review":rreceipts},"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--primary-pool",type=Path,required=True); p.add_argument("--research-memory",type=Path,required=True); p.add_argument("--output",type=Path,default=Path("generated/discovery-engine-paper-yield-benchmark.json")); p.add_argument("--raw-dir",type=Path,default=Path("generated/research-data/discovery-engine-paper-yield-benchmark")); p.add_argument("--candidates-per-engine",type=int,default=4); p.add_argument("--generator-model",default="kimi-k3"); p.add_argument("--reviewer-model",default="deepseek-v4-pro"); a=p.parse_args()
    if not 1<=a.candidates_per_engine<=8: raise SystemExit("candidates-per-engine must be 1..8")
    pool=json.loads(a.primary_pool.read_text()); memory=json.loads(a.research_memory.read_text()); client=ArkResponsesClient(ArkSettings.from_env())
    def call(**kw): return client.respond(kw["prompt"],model=kw["model"],max_output_tokens=kw["max_output_tokens"],temperature=kw["temperature"],thinking=None,store=True)
    report=run_benchmark(pool,memory,a.candidates_per_engine,call,call,a.generator_model,a.reviewer_model,a.raw_dir); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"summary":report["summary"],"ranking":report["engine_ranking"]},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
