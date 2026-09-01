from pathlib import Path
from research_pipeline import run_c1_pacta_rb_qwen397_source_budget_q0_v2_20260901 as q

def test_budget_separation():
    assert q.SOURCE_OUTPUT_BUDGET==16384
    assert q.FIRST_DECISION_BUDGET==512

def test_fixture_grid_and_length():
    rows=q.fixtures();assert len(rows)==6
    assert {(r['history_pairs'],r['line_count']) for r in rows}=={(h,n) for h in (0,12,24) for n in (160,320)}
    assert max(len(r['expected_action']) for r in rows)>20000

def test_neutral_transport_surface():
    rows=q.fixtures()
    for r in rows:
        assert len(r['messages'])==2+2*r['history_pairs']
        assert 'Transport qualification only' in r['messages'][0]['content']
        assert 'Return this command exactly' in r['messages'][-1]['content']

def test_no_scientific_task_ids():
    s=Path(q.__file__).read_text()
    for x in ('pydata__xarray-4966','scikit-learn__scikit-learn-14496','matplotlib__matplotlib-24627'):
        assert x not in s

def test_exactly_once_root_guard(tmp_path):
    root=tmp_path/'x';root.mkdir()
    try:q.run(root)
    except RuntimeError as e: assert 'no overwrite/retry' in str(e)
    else: raise AssertionError('guard absent')
