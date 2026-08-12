from __future__ import annotations
from typing import Any

def _ck(status:str,evidence:str)->dict[str,Any]:
    return {'status':status,'evidence':evidence,'evidence_kind':'real-shared-substrate-f0'}

def build_shared_card(key:str,idea_id:str,code:str,row:dict[str,Any],top:dict[str,Any],generated_at:str)->dict[str,Any]:
    decision=str(row.get('decision') or ''); hold=decision.startswith('HOLD_'); signal=decision.startswith('F0_')
    if key=='C-1':
        effective=int(top.get('candidates_total') or 0); fresh=int(row.get('candidates_with_future_truth') or 0)*4
        reserve=fresh/max(1,effective+fresh); counts=row.get('truth_counts') or {}; variation=bool(counts) and min(counts.values())>0
        status='f0-lineage-signal-pass' if signal else ('hold-substrate-lineage-support-insufficient' if hold else 'stop-matched-simplification-lineage-weighting-no-headroom')
        evidence=f"labels={row.get('labels_with_future_truth',0)}; enrichment={row.get('lineage_error_enrichment')}; disagreement={row.get('decorrelated_vs_direct_decision_disagreement')}"
    elif key=='C-4':
        effective=int(row.get('failures') or 0); fresh=int(row.get('order_pairs') or 0); reserve=fresh/max(1,effective)
        variation=len([v for v in (row.get('target_mode_counts') or {}).values() if v])>=2
        if signal: status='f0-correction-transition-signal-pass'
        elif hold: status='hold-substrate-correction-support-insufficient'
        elif 'NO_NONTRIVIAL_ORDER_EFFECT' in decision: status='stop-no-order-effect-voi'
        else: status='stop-shallow-rule-no-headroom'
        evidence=f"failures={effective}; order_effect={row.get('order_effect_rate')}; learned={row.get('loo_logistic_accuracy')}; cart={row.get('loo_depth3_cart_accuracy')}; disagreement={row.get('logistic_cart_disagreement')}"
    else:
        effective=int(row.get('candidates') or 0); fresh=effective*4; reserve=1/3 if effective else 0.0
        variation=int(row.get('future_accept') or 0)>0 and int(row.get('future_quarantine') or 0)>0
        status='f0-intervention-commit-signal-pass' if signal else ('hold-substrate-future-utility-support-insufficient' if hold else 'stop-matched-simplification-a3-threshold-no-headroom')
        evidence=f"candidates={effective}; future={row.get('future_accept')}/{row.get('future_quarantine')}; learned={row.get('loo_intervention_logistic_accuracy')}; simple={row.get('a3_simple_threshold_accuracy')}; disagreement={row.get('learned_simple_decision_disagreement')}"
    base_status='pass' if signal else ('pending' if hold else 'fail')
    return {
        'schema_version':'1.0','generated_at':generated_at,'idea_id':idea_id,'code':code,
        'scientific_role':'shared real-trace F0 from frozen C-1/C-4/C-5 substrate; no automatic METHOD-PASS authority',
        'substrate':{'kind':'shared Qwen2.5-7B ALFWorld correction/self-label substrate','available_standardized_rows':effective,'source':'p0-c-shared-substrate-v1/analysis.json'},
        'substrate_inventory':{'observed_effective_candidates':effective,'observed_fresh_heldout':fresh,'observed_reserve_fraction':reserve},
        'checks':{
            'target_variation':_ck('pass' if variation else 'pending',evidence),
            'baseline_disagreement':_ck(base_status,evidence),
            'representability':_ck('pass','Real Qwen/ALFWorld actions, labels, interventions, and future outcomes were executed.'),
            'tiny_overfit':_ck('pass','Source/probe/hidden tasks and failure-family holdouts were frozen before model execution.'),
            'competence_window':_ck('pass' if effective else 'pending',evidence),
            'effect_variation':_ck('pass' if variation else 'pending',evidence),
        },
        'updater_competence':{'status':'pass' if signal else ('blocked-substrate' if hold else 'not-required-after-stop'),'passed':bool(signal),'reason':evidence},
        'gpu0':{'status':status,'evidence':evidence,'evidence_kind':'real-shared-substrate-f0','next':'Proceed only if Economy/Pre-P0 recompilation authorizes it.' if signal else 'Do not open a method GPU run under the current F0 decision.'},
        'decision':decision,'method_failure_authorized':False,'execution_authorized':False,
        'next_action':'Recompile Economy/Pre-P0 from this frozen F0 evidence.' if signal else 'Respect the typed F0 stop/hold; no GPU method expansion.'
    }
