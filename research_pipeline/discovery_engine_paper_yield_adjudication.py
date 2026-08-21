from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
from .discovery_engine_paper_yield_benchmark import ENGINE_SPECS,_now


def _basin(r):
    s=' '.join(str(r.get(k) or '') for k in ('title','scientific_question','observed_trigger','structural_variable')).lower()
    rules=(
      ('failure-derived-memory',('failure-derived','memory')),
      ('pruning-threshold',('prun','threshold')),
      ('task-order-path',('task','order')),
      ('temporal-grounding',('temporal','ground')),
      ('skill-context-transfer',('skill','transfer')),
      ('memory-update-cadence',('memory','update','frequency')),
      ('memory-update-order',('memory','update','order')),
    )
    for name,terms in rules:
        if all(t in s for t in terms):return name
    if 'memory' in s and 'update' in s and any(t in s for t in ('interval','schedul','cadence')):return 'memory-update-cadence'
    if 'skill' in s and any(t in s for t in ('context mismatch','wrong context','distribution shift')):return 'skill-context-transfer'
    return str(r.get('candidate_id') or '')

# This is a run-specific hard-gate adjudication over the frozen 2026-08-21 benchmark.
# It is intentionally explicit and zero-authority: the goal is to calibrate an
# over-permissive model review, not to grant canonical Problem/Paper/Experiment status.
DECISIONS={
"D1-C01":("HOLD",65,"Failure-derived vs success-derived memories change content as well as provenance; the proposed swap does not isolate source type from memory semantics/task hardness.","Construct matched-content or counterfactual relabel/swap units so source provenance changes without changing usable content, then test future persistent failure."),
"D1-C02":("REDUCE",31,"The claim is adaptive pruning-threshold selection by task difficulty, which is ordinary hyperparameter/regime tuning rather than an irreducible agent-evolution mechanism.","Reopen only with matched final memory state showing a history-dependent effect that no state-aware pruning baseline can express."),
"D1-C03":("REDUCE",28,"Timestamp-aware retrieval versus semantic retrieval is a generic temporal-grounding/retrieval design comparison; persistent self-evolution is not essential to the claimed residual.","Require a persistent-history variable that changes a future prediction after the same temporal information is available to both methods."),
"D2-C01":("HOLD",67,"The measured association is grounded, but the causal intervention swaps failure-derived and success-derived content, leaving content quality/task hardness as competing explanations.","Create matched retrieval interventions controlling content semantics, task hardness and retrieval position; preregister the causal contrast before outcomes."),
"D2-C02":("HOLD",59,"Fully specifying memories adds task constraints unavailable to the underspecified condition, so the baseline is not same-information and cannot isolate underspecification as the causal object.","Define a fixed-information specification perturbation or matched memory pair where only ambiguity/constraint encoding differs, then rerun order/variance tests."),
"D2-C03":("REDUCE",30,"Temporal grounding capability gaps and explicit grounding tools are generic reasoning/retrieval questions; the proposed paper does not require persistent self-evolution.","Only revisit if longitudinal memory/history creates a matched-current-state residual that static temporal grounding cannot explain."),
"D3-C01":("REDUCE",34,"Changing the pruning threshold deterministically changes which skills survive; this is the expected action of a threshold, not a new structural scientific residual.","Require a path-dependent or irreversible effect after matching the final retained-skill set and all observable state."),
"D3-C02":("HOLD",69,"Task order is a plausible structural variable, but the current falsifier allows different final memory libraries, so ordinary current-state differences can explain future behavior.","Match or quotient the final observable memory/state across different histories and test whether future behavior still diverges; otherwise model the causal write path explicitly."),
"D3-C03":("REDUCE",35,"Context-aware versus context-agnostic skill retrieval is standard conditional retrieval/domain adaptation; the baseline intentionally ignores relevant context.","Require an Agent-specific persistent-state constraint that changes a prediction even when the strongest baseline receives the same context."),
"D4-C01":("HOLD",63,"Controlling for static utility in logs may establish predictive residual, but it cannot support the current causal claim; retrieval source may proxy content/history/task difficulty.","Either narrow the paper to a prospective predictor or add a matched intervention isolating source provenance while holding content and task factors fixed."),
"D4-C02":("REDUCE",46,"A baseline that ignores a trust annotation available to the proposal is not the strongest same-information baseline; a state-aware baseline can simply condition on that annotation.","Show a structural consequence of trust-history that persists after the baseline receives the full trust annotation/history and makes a different ex-ante prediction."),
"D4-C03":("REDUCE",29,"Benchmark-specific optimal pruning thresholds varying with task distribution is hyperparameter selection, not a distinct scientific mechanism.","Reopen only with an irreversible/history-dependent effect under matched final memory state, not another adaptive-threshold rule."),
"D5-C01":("HOLD",73,"This targets genuine order/path dependence, but the described rerun does not yet guarantee identical final observable memory/state; order effects may reduce to different constructed memories.","Freeze two histories that yield the same final visible memory content/retrieval state, then measure future behavior under identical probes; alternatively preregister a causal write-path state variable."),
"D5-C02":("HOLD",76,"Hysteresis after accumulation is potentially paper-level because it predicts history dependence beyond a fixed threshold, but the current falsifier does not enforce an exact final-memory-state match.","After accumulated-then-pruned and always-pruned histories, content-address and match the final memory bank plus retrieval metadata before future probes; stop if matched states behave identically."),
"D5-C03":("HOLD",61,"Resolved versus unresolved failure text changes present memory content, so the experiment does not isolate historical exposure from current representation.","Produce distinct histories with the same final visible memory representation/annotation and test whether future infrastructure use still differs."),
"D6-C01":("HOLD",68,"Update scheduling under fixed budget can reveal path dependence, but varying order may change final memory content; then ordinary state differences explain the result.","Constrain or match the final memory state across schedules, or identify a causal internal state variable whose value predicts the residual prospectively."),
"D6-C02":("REDUCE",30,"Changing a termination threshold and measuring semantic-failure trade-offs is ordinary threshold tuning/search calibration.","Require an unexplained structural phase transition or invariant failure that cannot be represented by budget/threshold-aware search models."),
"D6-C03":("REDUCE",37,"Method advantage varying with failure base rate is a regime-specific benchmark comparison; the residual is a selection threshold rather than an agent-evolution mechanism.","Require a persistent-state mechanism or decision object whose prediction differs from the strongest frequency-aware baseline."),
"D7-C01":("REDUCE",32,"The proposed mapping from task similarity to optimal pruning threshold is a standard stability-plasticity/hyperparameter adaptation problem already expressible by continual-learning baselines.","Find an Agent-specific structural constraint that changes the continual-learning prediction under identical information."),
"D7-C02":("REDUCE",33,"Memory-update frequency versus forgetting is a standard continual-learning control variable, and identical memory content across different update frequencies is not guaranteed by the proposed test.","Require matched final state plus a residual that standard nonstationary/continual-learning models cannot express."),
"D7-C03":("REDUCE",41,"Tool-use distribution shift predicting skill transfer is a domain-adaptation predictor; the stated residual is a shift threshold, not an irreducible agent-specific mechanism.","Require an Agent-specific persistent skill/state constraint that defeats a strongest distribution-shift-aware baseline with the same histories."),
}

def compile_adjudication(base):
    rows=[];basins={}
    for r in base.get('candidates') or []:
        cid=str(r.get('candidate_id') or '')
        verdict,score,reason,next_evidence=DECISIONS.get(cid,("HOLD",50,"No calibrated hard-gate decision recorded.","Independent adjudication required."))
        basin=_basin(r);basins.setdefault(basin,[]).append(cid)
        rows.append({"candidate_id":cid,"engine_id":r.get('engine_id'),"title":r.get('title'),"basin_id":basin,"verdict":verdict,"strict_score":score,"reason":reason,"minimum_next_evidence":next_evidence,"canonical_problem_gate_authority":False,"paper_design_authority":False,"scientific_authority":False})
    # One basin contributes at most one unit of near-paper evidence; credit is split across engines that reach HOLD or SURVIVE in that basin.
    near_by_basin={}
    for row in rows:
        if row['verdict'] in {'HOLD','SURVIVE'} and row['strict_score']>=55:near_by_basin.setdefault(row['basin_id'],set()).add(str(row.get('engine_id') or ''))
    for row in rows:
        engines=near_by_basin.get(row['basin_id'],set());row['fractional_near_paper_yield']=round(1/max(1,len(engines)),4) if row['verdict'] in {'HOLD','SURVIVE'} and row['strict_score']>=55 else 0.0
    ranking=[]
    for eid,name,_ in ENGINE_SPECS:
        rr=[r for r in rows if r['engine_id']==eid];scores=[r['strict_score'] for r in rr];holds=sum(r['verdict']=='HOLD' for r in rr);surv=sum(r['verdict']=='SURVIVE' for r in rr);red=sum(r['verdict']=='REDUCE' for r in rr);frac=sum(r['fractional_near_paper_yield'] for r in rr)
        ranking.append({"engine_id":eid,"engine_name":name,"generated":len(rr),"survive":surv,"hold_near_paper":holds,"reduce":red,"fractional_near_paper_yield":round(frac,4),"median_strict_score":round(float(statistics.median(scores)),2) if scores else None,"best_strict_score":max(scores) if scores else None,"scientific_authority":False})
    ranking.sort(key=lambda x:(x['survive'],x['fractional_near_paper_yield'],x['hold_near_paper'],x['median_strict_score'] or 0,x['best_strict_score'] or 0),reverse=True)
    for i,r in enumerate(ranking,1):r['rank']=i
    return {"schema_version":"1.0","generated_at":_now(),"status":"HARD_GATE_ADJUDICATION_COMPLETE","source_benchmark_id":base.get('benchmark_id'),"source_generated_at":base.get('generated_at'),"policy":{"first_reviewer_21_of_21_pass_was_treated_as_calibration_failure":True,"same_information_baseline_required":True,"correlation_does_not_grant_causal_claim":True,"hyperparameter_or_regime_tuning_is_reduced":True,"path_dependence_requires_matched_final_observable_state_or_explicit_causal_write_state":True,"generic_temporal_grounding_continual_learning_domain_adaptation_is_not_agent_specific_by_default":True,"provider_failure_has_zero_scientific_authority":True,"hard_gate_adjudication_has_zero_canonical_authority":True},"summary":{"candidates":len(rows),"survive":sum(r['verdict']=='SURVIVE' for r in rows),"hold_near_paper":sum(r['verdict']=='HOLD' for r in rows),"reduce":sum(r['verdict']=='REDUCE' for r in rows),"semantic_basins":len(basins)},"basins":basins,"engine_ranking":ranking,"candidates":rows,"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();base=json.loads(a.input.read_text());out=compile_adjudication(base);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':out['status'],'summary':out['summary'],'ranking':out['engine_ranking']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
