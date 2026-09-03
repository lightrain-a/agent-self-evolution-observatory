from __future__ import annotations
import inspect,json
from pathlib import Path
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_source_runtime_v2_20260903 as v2
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_source_20260903 as base


def test_rebind_changes_only_runtime_and_source_root():
    assert str(v2.RUNTIME).endswith('fresh3-runtime-20260903-v2/normalization-qualification.json')
    assert str(v2.DEFAULT).endswith('fresh3-source-20260903-v2')
    old_runtime=base.RUNTIME; old_default=base.DEFAULT
    try:
        v2.bind()
        assert base.RUNTIME==v2.RUNTIME and base.DEFAULT==v2.DEFAULT
    finally:
        base.RUNTIME=old_runtime; base.DEFAULT=old_default


def test_scientific_provider_and_frozen_objects_are_inherited_unchanged():
    assert base.POOL_SHA=='3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257'
    assert base.Q03_CLOSURE_SHA=='077383ca894abc1c3986e01ef90b16628d2580a3058d66c2838a63796208fdac'
    assert base.FROZEN_SCHEDULE_SHA=='2e78838a46b3a37c09e07e2f0abdf0d9eb82d271e53d91245a41306d0e5b273f'
    assert base.PROBE_SPECS_SHA=='19f119fdb80e58427809a565d515900a14455394e79c31126645521702940c97'
    assert base.SOURCE_MAX_COMPLETION_TOKENS==32768
    assert base.PACTA_FIRST_DECISION_BUDGET==2048
    assert base.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS==900


def test_runtime_sha_remains_explicit_execution_input():
    source=inspect.getsource(v2.main)
    assert '--runtime-qualification-sha' in source
    assert 'required=True' in source
    assert 'args.runtime_qualification_sha' in source


def test_phase_order_and_hard_gates_are_inherited():
    smoke=inspect.getsource(base.smoke)
    acquire=inspect.getsource(base.acquire)
    assert 'prelaunch not passed' in smoke
    assert 'smoke not passed' in acquire
    assert 'len(results) == 10 and len(valid) == 10' in acquire
    assert 'replacement' in acquire and 'top_up' in acquire


def test_no_new_scientific_logic_in_rebind_wrapper():
    source=inspect.getsource(v2)
    for token in ('execute_trajectory(', 'writer', 'binder', 'shadow', 'final_measurement'):
        assert token not in source


def test_contract_records_zero_provider_and_source_calls():
    p=Path('paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-source-runtime-v2-rebind-contract-20260903.json')
    o=json.loads(p.read_text())
    assert o['status']=='FROZEN_BEFORE_FRESH3_RUNTIME_V2_QUALIFICATION_OUTCOME'
    assert o['provider_calls']==0 and o['scientific_source_tasks_used']==0
    assert o['unchanged']['source_gate'].startswith('all 10 provenance-valid')
