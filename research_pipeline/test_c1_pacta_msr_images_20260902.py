from __future__ import annotations
from research_pipeline import prepare_c1_pacta_msr_images_20260902 as m


def test_image_units_cover_source_and_future_exactly_once():
    rows=m.image_units()
    assert len(rows)==20
    assert len({x['instance_id'] for x in rows})==20
    assert sum(x['role']=='source' for x in rows)==10
    assert sum(x['role']=='future' for x in rows)==10
    assert all(len(x['base_commit'])==40 for x in rows)


def test_image_prepare_is_zero_provider_by_construction():
    source=open(m.__file__,encoding='utf-8').read()
    assert 'AA_API_KEY' not in source
    assert 'chat/completions' not in source
    assert 'provider_calls' in source
    assert 'scientific_calls' in source
