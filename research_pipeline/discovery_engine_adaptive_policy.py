from __future__ import annotations
import argparse,json
from pathlib import Path
from .discovery_engine_paper_yield_benchmark import _now

POLICY={
  "schema_version":"1.0",
  "policy_id":"adaptive-discovery-paper-yield-v1",
  "status":"SHADOW_POLICY_RECOMMENDED",
  "evidence_basis":{
    "benchmark":"generated/discovery-engine-paper-yield-benchmark.json",
    "hard_gate_adjudication":"generated/discovery-engine-paper-yield-adjudication.json",
    "minimum_replication_before_canonical_auto_reweight":2,
    "current_replications":1,
  },
  "birth_engines":[
    {"engine_id":"D5","role":"PRIMARY_BIRTH","budget_share":0.45,"reason":"Highest near-paper yield; 3/3 candidates survive simple reduction as HOLDs centered on longitudinal/path-dependent residuals."},
    {"engine_id":"D2","role":"PRIMARY_BIRTH","budget_share":0.35,"reason":"Evidence-grounded anomaly/failure mining yields 2/3 near-paper HOLDs and naturally starts from measurable phenomena."},
    {"engine_id":"D1","role":"EVENT_TRIGGERED_BIRTH","budget_share":0.10,"reason":"Useful when fresh primary evidence or an explicit closure reopen condition appears; otherwise prone to generic retrieval/threshold formulations."},
    {"engine_id":"D7","role":"DIVERSITY_EXPLORATION","budget_share":0.05,"reason":"Keep a small exploration reserve, but current 3/3 candidates reduced to mature continual-learning/domain-adaptation accounts."},
    {"engine_id":"D4","role":"RESERVE_BIRTH","budget_share":0.05,"reason":"Independent birth often creates easy-to-run but information-asymmetric/correlation-to-causality claims; retain only as reserve generation."}
  ],
  "mandatory_transformers":[
    {"order":1,"engine_id":"D4","role":"STRONGEST_BASELINE_ATTACK","instruction":"For every D5/D2 birth, construct the strongest same-information baseline and attempt to absorb the claimed residual. If it absorbs the residual, REDUCE before further work."},
    {"order":2,"engine_id":"D3","role":"STRUCTURAL_VARIABLE_REPAIR","instruction":"For survivors, name the minimal Agent-specific structural variable that changes an ex-ante prediction. Do not accept a tunable threshold, ordinary context feature, or state variable already available to the baseline."},
    {"order":3,"engine_id":"D6","role":"EXECUTABLE_FALSIFIER_COMPILER","instruction":"Compile the surviving question into a bounded executable counterexample/falsifier space. Do not turn parameter search itself into the paper contribution."}
  ],
  "gating":{
    "support_feasibility_required_before_counting_paper_convertible_yield":True,
    "first_party_code_data_or_equivalent_existing_substrate_required_for_immediate_falsifier":True,
    "missing_release_is_support_hold_not_scientific_failure":True,
    "path_dependence_requires_matched_final_observable_state_or_explicit_causal_write_state":True,
    "same_information_baseline_required":True,
    "correlation_to_causality_forbidden_without_intervention":True,
    "hyperparameter_or_regime_tuning_reduced_before_paper_design":True,
    "generic_temporal_grounding_continual_learning_domain_adaptation_reduced_unless_agent_specific_residual":True,
    "zero_candidate_round_is_valid":True,
    "automatic_problem_gate_authority":False,
    "automatic_paper_design_authority":False,
    "automatic_method_experiment_p0_gpu_authority":False
  },
  "next_replication":{
    "recommended":True,
    "compare_only_top_birth_engines":["D5","D2"],
    "candidate_budget_each":6,
    "use_different_generator_family":True,
    "reuse_same_hard_gates":True,
    "promote_policy_only_if_rank_order_or_combined_yield_is_replicated":True
  },
  "scientific_authority":False,
  "authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}
}

def compile_policy(adjudication):
    out=json.loads(json.dumps(POLICY));out['generated_at']=_now();out['observed_ranking']=adjudication.get('engine_ranking') or [];out['observed_summary']=adjudication.get('summary') or {};return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--adjudication',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();adj=json.loads(a.adjudication.read_text());out=compile_policy(adj);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({"status":out['status'],"birth_engines":out['birth_engines'],"next_replication":out['next_replication']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
