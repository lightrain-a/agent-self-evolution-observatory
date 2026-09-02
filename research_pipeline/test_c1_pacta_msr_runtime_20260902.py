from __future__ import annotations
from pathlib import Path
from research_pipeline import run_c1_pacta_msr_runtime_20260902 as r


def test_frozen_runtime_rows_cover_all_twenty_images():
    rows=r.frozen_rows()
    assert len(rows)==20
    assert len({x['instance_id'] for x in rows})==20
    assert sum(x['role']=='source' for x in rows)==10
    assert sum(x['role']=='future' for x in rows)==10
    assert all(x['amd64_digest'].startswith('sha256:') for x in rows)
    assert all(len(x['base_commit'])==40 for x in rows)


def test_runtime_module_has_no_provider_or_scientific_surface():
    source=Path(r.__file__).read_text()
    for forbidden in ('AA_API_KEY','chat/completions','SUCCESSFUL_SI','FAILED_SI','shadow','A3_PACTA'):
        assert forbidden not in source
    assert r.ROOTFUL_HOST=='unix:///var/run/docker.sock'


def test_hard_gate_requires_all_twenty():
    source=Path(r.__file__).read_text()
    assert "'MSR_20_IMPORT_PASS' if n==20" in source
    assert "'MSR_20_RUNTIME_READY' if n==20" in source
    assert "source_qualified" in source and "future_qualified" in source
