from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .matched_simplification_compiler import compile_matched_simplifications
GATES=(
 {"key":"matched_simplification","title":"Matched-Simplification Headroom"},
 {"key":"substrate_inventory","title":"Substrate / Support Inventory"},
 {"key":"causal_unit_observable","title":"Causal Unit & Observable"},
 {"key":"decision_voi","title":"Decision-Changing Value of Information"},
 {"key":"single_writer_authority","title":"Single-Writer Experiment Authority"},
)
POLICY={"schema_version":"1.1","stage_semantics":"resource-economy gate before P0 execution compilation; not a ninth Pre-Experiment gate","all_five_required_before_execution_compilation":True,"matched_simplification_must_precede_gpu":True,"complexity_ladder_required_before_gpu":True,"complexity_ladder_order":["constant-or-mean","threshold-or-lookup","shallow-or-sparse","proposed-mechanism"],"lower_complexity_headroom_required":True,"substrate_inventory_must_precede_hidden_or_gpu":True,"causal_unit_and_observable_must_be_explicit":True,"gpu_requires_decision_changing_voi":True,"single_writer_authority_required":True,"economy_failure_cannot_emit_method_fail":True,"micro_p0_fraction_max":0.20,"second_backbone_cannot_rescue_failed_economy_gate":True}
SIMPLIFICATION_TOKENS=("equivalent","dominates","ceiling","group-testing","generic-state-diff","recency-frequency","simple-anchor","intersection-filter","boolean-rule","shallow-rule","nary","complexity-matched","direct-order-aware-risk")
SUBSTRATE_TOKENS=("substrate","support-insufficient","support_cardinality","support-cardinality","fresh-cinteraction-support-insufficient","ranking-degenerate","updater-incompetent")
def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _gate(key,status,reason,evidence=None): return {"key":key,"status":status,"pass":status=="pass","reason":reason,"evidence":evidence or {}}
def _check(card,key): return str(((card.get("checks") or {}).get(key) or {}).get("status") or "pending")
def _econ(contract):
 raw=(contract or {}).get("economy") or {}
 return raw if isinstance(raw,dict) else {}
def evaluate_economy_card(idea_id:str,offline_card:dict[str,Any]|None,contract:dict[str,Any]|None,setup:dict[str,Any]|None)->dict[str,Any]:
 offline=offline_card or {}; gpu0=offline.get('gpu0') or {}; status=str(gpu0.get('status') or gpu0.get('phenomenon') or 'pending').lower(); text=' '.join((status,str(gpu0.get('evidence') or '').lower())); econ=_econ(contract); setup=setup or {}
 simpl_plan=compile_matched_simplifications(idea_id,str((contract or {}).get('mechanism') or ''),str((contract or {}).get('baseline') or ''))
 baseline=_check(offline,'baseline_disagreement')
 if any(t in text for t in SIMPLIFICATION_TOKENS) or baseline=='fail': simpl=_gate('matched_simplification','fail','matched simpler baseline reproduces or dominates current mechanism',{'gpu0_status':status,'compiler':simpl_plan})
 elif baseline=='pass' and simpl_plan['baseline_count']>=simpl_plan['minimum_required_baselines']: simpl=_gate('matched_simplification','pass','method-versus-simplification disagreement is empirically present against a compiled baseline tournament',{'gpu0_status':status,'compiler':simpl_plan})
 else: simpl=_gate('matched_simplification','pending','compiled matched-simplification tournament has not established headroom',{'gpu0_status':status,'compiler':simpl_plan})
 inventory=dict(econ.get('substrate_inventory') or {})
 observed=offline.get('substrate_inventory') or {}
 for key in ('observed_effective_candidates','observed_fresh_heldout','observed_reserve_fraction'):
  if observed.get(key) is not None: inventory[key]=observed.get(key)
 inv_fields=('effective_candidates_min','fresh_heldout_min','reserve_fraction_min','target_variation_rule','observed_effective_candidates','observed_fresh_heldout','observed_reserve_fraction'); inv_missing=[k for k in inv_fields if inventory.get(k) in (None,'')]
 if any(t in text for t in SUBSTRATE_TOKENS): substrate=_gate('substrate_inventory','fail','current substrate/support inventory cannot instantiate the frozen test',{'gpu0_status':status})
 else:
  effect,competence=_check(offline,'effect_variation'),_check(offline,'competence_window'); updater=offline.get('updater_competence') or {}
  if status.startswith('stop'): substrate=_gate('substrate_inventory','pass','substrate was sufficient to reach a non-substrate scientific simplification stop')
  elif inv_missing: substrate=_gate('substrate_inventory','pending','explicit substrate inventory contract missing: '+', '.join(inv_missing),{'missing':inv_missing})
  elif int(inventory.get('observed_effective_candidates') or 0)<int(inventory.get('effective_candidates_min') or 0) or int(inventory.get('observed_fresh_heldout') or 0)<int(inventory.get('fresh_heldout_min') or 0) or float(inventory.get('observed_reserve_fraction') or 0)<float(inventory.get('reserve_fraction_min') or 0): substrate=_gate('substrate_inventory','fail','observed substrate inventory is below the frozen minimum',{'inventory':inventory})
  elif effect=='pass' and competence=='pass' and updater.get('passed') is not False: substrate=_gate('substrate_inventory','pass','inventory, competence, effect variation, and updater/action support are qualified',{'inventory':inventory})
  else: substrate=_gate('substrate_inventory','pending','inventory exists but empirical competence/effect/updater qualification is incomplete',{'inventory':inventory})
 causal_fields=('causal_unit','prediction_unit','effect_observable','effect_moderators','effect_stability_scope','aggregation_risk'); missing=[k for k in causal_fields if not econ.get(k)]
 unit_mismatch=bool(econ.get('causal_unit') and econ.get('prediction_unit') and econ.get('causal_unit')!=econ.get('prediction_unit'))
 aggregation_ack=str(econ.get('aggregation_risk') or '').strip().lower() not in {'','none','n/a','na'}
 causal_pass=not missing and (not unit_mismatch or aggregation_ack)
 causal=_gate('causal_unit_observable','pass' if causal_pass else 'pending','causal/prediction units, observable, moderators, stability scope, and aggregation risk are frozen' if causal_pass else ('causal-to-prediction aggregation mismatch is not explicitly handled' if unit_mismatch and not aggregation_ack else 'explicit causal-unit contract missing: '+', '.join(missing)),{'missing':missing,'causal_prediction_unit_mismatch':unit_mismatch,'aggregation_risk_acknowledged':aggregation_ack})
 voi_fields=('cheapest_falsifier','decision_changing_outcomes','abandonment_condition'); vmiss=[k for k in voi_fields if not econ.get(k)]
 if status.startswith('stop'): voi=_gate('decision_voi','fail','terminal evidence says another GPU run cannot change the current standalone decision',{'gpu0_status':status})
 else: voi=_gate('decision_voi','pass' if not vmiss else 'pending','cheapest falsifier and decision-changing outcomes frozen' if not vmiss else 'VOI contract missing: '+', '.join(vmiss),{'missing':vmiss})
 authority_mode=str(setup.get('authority_mode') or ''); apass=bool(setup.get('exclusive_output_lock')) and authority_mode=='single-writer-lease'
 authority=_gate('single_writer_authority','pass' if apass else 'pending','single-writer lease plus exclusive output lock required',{'authority_mode':authority_mode,'exclusive_output_lock':bool(setup.get('exclusive_output_lock'))})
 gates=[simpl,substrate,causal,voi,authority]; passed=sum(g['pass'] for g in gates); ready=passed==len(gates)
 primary='matched-simplification' if simpl['status']=='fail' else ('substrate' if substrate['status']=='fail' else ('voi' if voi['status']=='fail' else ''))
 return {'schema_version':'1.0','idea_id':idea_id,'generated_at':_now(),'status':'pass' if ready else ('stop-before-p0-execution' if primary else 'blocked'),'execution_compilation_authorized':ready,'passed_gates':passed,'gate_count':len(gates),'primary_stop_class':primary,'gates':gates,'policy':POLICY,'scientific_role':'pre-execution resource-economy decision only; cannot emit METHOD-PASS/FAIL'}
def build_economy_state(admission_cards:list[dict[str,Any]])->dict[str,Any]:
 rows=[(c.get('execution_preflight') or {}).get('economy_gate') or {} for c in admission_cards]; stops={}
 for row in rows:
  key=str(row.get('primary_stop_class') or '')
  if key: stops[key]=stops.get(key,0)+1
 return {'schema_version':'1.0','generated_at':_now(),'policy':POLICY,'gates':list(GATES),'summary':{'ideas':len(rows),'economy_ready':sum(bool(r.get('execution_compilation_authorized')) for r in rows),'blocked_or_stopped':sum(not bool(r.get('execution_compilation_authorized')) for r in rows),'stop_classes':stops,'matched_simplification_stops':stops.get('matched-simplification',0),'substrate_stops':stops.get('substrate',0),'voi_stops':stops.get('voi',0)},'rows':rows}
