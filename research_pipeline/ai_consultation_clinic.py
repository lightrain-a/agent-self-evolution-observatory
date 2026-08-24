from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT
DEFAULT_JSON=PROJECT_ROOT/'generated'/'ai-consultation-clinic.json'
DEFAULT_JS=PROJECT_ROOT/'generated'/'ai-consultation-clinic.js'
PANEL={
 'independent_first_round':True,
 'preferred_reviewers':['web-gpt-current-source-review','domestic-reasoner-a','domestic-reasoner-b'],
 'synthesis_only_after_independent_reviews':True,
 'failed_or_empty_model_response_is_missing_not_pass':True,
 'reviewers_do_not_see_each_others_first_round':True,
}
POLICY={
 'schema_version':'1.0','ai_vote_has_scientific_authority':False,'ai_vote_can_authorize_gpu':False,
 'ai_vote_can_authorize_second_backbone':False,'ai_vote_can_emit_method_pass_fail':False,
 'consultation_is_diagnostic_not_authoritative':True,'high_risk_findings_must_be_compiled_into_machine_checks':True,
 'post_screen_ranked_hypotheses_must_freeze_before_final_failure_adjudication':True,
 'unresolved_high_risk_findings_block_the_next_expensive_transition':True,
 'human_may_accept_residual_risk_only_with_explicit_reason':True,
}
CHECKPOINTS=(
 {
  'key':'idea_premortem','stage':'after-evidence-before-hypothesis-freeze','priority':1,
  'trigger':'every candidate that could enter the discussion-ready/P0 funnel',
  'purpose':'attack the scientific formulation before implementation begins',
  'questions':['Is the problem real but the proposed learnable assumption stronger than the underlying principle?','What is the natural causal unit, prediction unit, stability scope, and aggregation risk?','What closest work or generic formulation would subsume the contribution?','What is the simplest mechanism that could explain the claimed effect?'],
  'required_outputs':['broken_bridge','causal_unit_risk','closest_collision','simplest_explanation','one_cheapest_falsifier'],
  'compile_to':['collision_engine','p0_economy.causal_unit_observable','p0_economy.decision_voi'],
  'cost_saving_role':'prevents implementing a method whose principle is plausible but prediction unit/formulation is wrong',
 },
 {
  'key':'economy_red_team','stage':'before-p0-economy-freeze','priority':2,
  'trigger':'every candidate proposed for P0 Economy evaluation','purpose':'find cheap ways to kill or simplify the method before GPU work',
  'questions':['Which complexity-matched non-learning/shallow baseline could reproduce the decisions?','Does the current substrate contain enough effective candidates, label variation, fresh held-out units, and reserve?','Which CPU/offline falsifier has the highest probability of changing KEEP/PIVOT/STOP?','Which result would make another GPU run scientifically pointless?'],
  'required_outputs':['matched_simplifications','substrate_risks','cheapest_falsifier','decision_changing_outcomes','abandonment_condition'],
  'compile_to':['matched_simplification_compiler','p0_economy.substrate_inventory','p0_economy.decision_voi'],
  'cost_saving_role':'targets the dominant simplification-equivalence and substrate-insufficiency stop classes',
 },
 {
  'key':'pre_launch_stress_review','stage':'after-economy-pass-before-first-expensive-launch','priority':3,
  'trigger':'Economy 5/5 candidate before hidden-test opening or first GPU/multi-hour launch',
  'purpose':'red-team the exact frozen experiment contract, not the idea wording',
  'questions':['Can the frozen GO/STOP gate actually be attained with the available prevalence and sample resolution?','Can leakage, provenance drift, hardware/runtime mismatch, or duplicated launch invalidate the result?','Is there an earlier stopping boundary that preserves the decision while saving compute?','Does every expensive branch correspond to a result that can change the next action?'],
  'required_outputs':['gate_attainability_attack','leakage_provenance_attack','early_stop_opportunities','wasted_branch_candidates'],
  'compile_to':['pre_experiment_compiler','experiment_authority','budget_watchdog','outcome_semantics'],
  'cost_saving_role':'prevents full-table collection when the contract is underpowered, unreproducible, or decision-irrelevant',
 },
 {
  'key':'post_screen_differential_diagnosis','stage':'after-screening-or-nonpositive-pilot-before-repair','priority':4,
  'trigger':'SCREENING-NO-SIGNAL, INCONCLUSIVE, floor/ceiling, or surprising weak result',
  'purpose':'separate formulation, substrate, representation, optimization, baseline, and execution failures before another run',
  'questions':['Did the experiment fail to expose the mechanism, or did the mechanism lose under a qualified test?','Is the prediction unit/observable wrong despite a valid scientific principle?','Did a simpler baseline absorb the apparent gain?','Before final adjudication, what are the top 1–3 competing failure layers and what evidence would distinguish them?','What single-variable repair is falsifiable without reopening the full experiment?'],
  'required_outputs':['ranked_failure_hypotheses','principle_vs_formulation','baseline_reducibility','one_atomic_repair','repair_falsifier'],
  'compile_to':['failure_differential_registry','experiment_iteration','repair_queue','pre_p0_recompile'],
  'cost_saving_role':'prevents blind reruns, larger models, or extra seeds when the real failure is structural',
 },
 {
  'key':'pre_scale_collision_recheck','stage':'before-full-p0-second-backbone-p1-or-paper-claim-expansion','priority':5,
  'trigger':'positive signal proposed for scale-up, second backbone, P1, or stronger novelty claim',
  'purpose':'recheck novelty and marginal value before multiplying compute',
  'questions':['Has new or previously missed work reduced the surviving novelty boundary?','Does the positive signal beat the strongest current matched simplification, not only the original baseline?','What uncertainty is the second backbone/extra seed actually resolving?','Would scale-up change the paper claim or only increase confidence in an already non-novel mechanism?'],
  'required_outputs':['fresh_collision_recheck','updated_strongest_baseline','scale_up_question','second_backbone_value','claim_delta'],
  'compile_to':['collision_engine','matched_simplification_compiler','human_scale_up_approval'],
  'cost_saving_role':'prevents expensive confirmation of a result that has lost novelty or no longer changes the claim',
 },
)

def _now()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def build_ai_consultation_clinic_state()->dict[str,Any]:
 return {'schema_version':'1.0','generated_at':_now(),'policy':POLICY,'panel':PANEL,
  'summary':{'checkpoints':len(CHECKPOINTS),'pre_gpu_checkpoints':3,'post_screen_checkpoints':1,'pre_scale_checkpoints':1,'ai_authoritative_checkpoints':0,'all_findings_require_structured_disposition':True},
  'checkpoints':list(CHECKPOINTS),
  'finding_dispositions':['machine_gate_added','matched_baseline_added','cheap_falsifier_run','evidence_resolves_risk','human_accepts_residual_risk_with_reason','stop_or_merge_before_expensive_transition']}

def validate_ai_consultation_clinic_state(state:dict[str,Any])->list[str]:
 errors=[]
 if state.get('summary',{}).get('checkpoints')!=5: errors.append('AI consultation clinic must expose five checkpoints')
 if state.get('policy',{}).get('ai_vote_can_authorize_gpu') is not False: errors.append('AI consultation must not authorize GPU execution')
 if state.get('policy',{}).get('high_risk_findings_must_be_compiled_into_machine_checks') is not True: errors.append('AI findings must compile into machine-checkable controls')
 if state.get('panel',{}).get('independent_first_round') is not True: errors.append('AI reviewers must be independent in the first round')
 keys=[str(row.get('key') or '') for row in state.get('checkpoints') or []]
 if len(keys)!=len(set(keys)) or not all(keys): errors.append('AI consultation checkpoint keys must be unique and non-empty')
 if any(not row.get('compile_to') or not row.get('required_outputs') for row in state.get('checkpoints') or []): errors.append('Every AI consultation checkpoint needs structured outputs and a machine compilation target')
 post=next((row for row in state.get('checkpoints') or [] if row.get('key')=='post_screen_differential_diagnosis'),{})
 if state.get('policy',{}).get('post_screen_ranked_hypotheses_must_freeze_before_final_failure_adjudication') is not True: errors.append('Post-screen differential hypotheses must freeze before final adjudication')
 if 'ranked_failure_hypotheses' not in (post.get('required_outputs') or []) or 'failure_differential_registry' not in (post.get('compile_to') or []): errors.append('Post-screen diagnosis must compile ranked hypotheses into the failure differential registry')
 return errors

def write_ai_consultation_clinic_state(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
 state=build_ai_consultation_clinic_state(); errors=validate_ai_consultation_clinic_state(state)
 if errors: raise ValueError('Invalid AI consultation clinic state:\n- '+'\n- '.join(errors))
 json_path.parent.mkdir(parents=True,exist_ok=True)
 json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 js_path.write_text('window.AI_CONSULTATION_CLINIC = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 return state
if __name__=='__main__': print(json.dumps(write_ai_consultation_clinic_state(),ensure_ascii=False))
