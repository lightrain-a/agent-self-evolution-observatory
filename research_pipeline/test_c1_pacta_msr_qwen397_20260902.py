from __future__ import annotations
import json
from pathlib import Path
from research_pipeline import prepare_c1_pacta_msr_qwen397_20260902 as p


def test_zero_provider_fresh_pool_has_ten_disjoint_pairs():
    pool=p.select_pool()
    assert pool['candidate_count']==10
    assert pool['repository_count']==10
    assert pool['provider_calls']==0
    ids=[]
    for u in pool['units']:
        ids.extend([u['source_task_id'],u['future_task_id']])
        assert u['source_task_id']!=u['future_task_id']
        assert u['prior_id_overlap'] is False
    assert len(ids)==20 and len(set(ids))==20
    prior,_=p.prior_ids()
    assert not (set(ids)&prior)


def test_salts_are_new_and_method_specific():
    assert 'MSR' in p.SOURCE_SALT and 'MSR' in p.FUTURE_SALT
    assert 'MSR' in p.PILOT_SALT and 'MSR' in p.RANDOM_SALT
    assert p.SOURCE_SALT!='C1-PACTA-RB-DEEPSEEK-SOURCE-v1'


def test_design_forbids_old_rescue_paths():
    d=json.loads(p.DESIGN.read_text())
    locked=' '.join(d['locked'])
    assert 'old 3-unit sealed reserve' in locked
    assert 'old gate threshold tuning' in locked
    assert d['freshness']['new_source_future_pairs']==10
    assert d['freshness']['pilot']==8
    assert d['freshness']['sealed_reserve']==2


def test_method_has_same_state_ablation_and_strong_control():
    d=json.loads(p.DESIGN.read_text())
    m=d['method']
    assert set(m['two_selector_shadow_ablation']) >= {'G0','Gplus','gate','margin'}
    assert m['final_arms']['A2_RATE_MATCHED_RANDOM'].startswith('SCB enabled on exactly K')
    assert m['mechanism_gate']['required_Gplus_geometry']=='2..6/8'
    assert m['mechanism_gate']['positive_margin_improvement_count_ge']==5
