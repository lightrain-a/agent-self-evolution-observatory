from __future__ import annotations
import inspect,json
from pathlib import Path
import pytest
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_runtime88_20260903 as r
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_content_addressed_fresh3_inputs_and_88_geometry():
    assert sha256_file(r.IMAGE_ROOT/'manifest-freeze.json')==r.MANIFEST_SHA
    assert sha256_file(r.IMAGE_ROOT/'blob-plan.json')==r.BLOB_PLAN_SHA
    plan=json.loads((r.IMAGE_ROOT/'blob-plan.json').read_text())
    assert plan['unique_blob_count']==88 and len(plan['rows'])==88


def test_new_runtime_root_does_not_overwrite_failed_v1():
    assert str(r.DEFAULT_ROOT).endswith('fresh3-runtime-20260903-v2')
    assert not str(r.DEFAULT_ROOT).endswith('v1')


def test_preflight_is_fresh3_specific_and_does_not_delegate_old_86_gate():
    s=inspect.getsource(r.preflight)
    assert 'base.preflight(root)' not in s
    assert 'unique_blob_count' in s and '!= 88' in s
    assert 'len(rows) != 88' in s
    assert 'base.CACHE' in s and 'sha256_file(path)' in s
    assert 'FRESH3_RUNTIME88_PREFLIGHT_PASS' in s


def test_blob_receipt_sha_is_runtime_parameter():
    r.bind('0'*64); assert r.base.BLOB_RECEIPT_SHA=='0'*64
    with pytest.raises(RuntimeError): r.bind('bad')


def test_import_and_targeted_clean_semantics_unchanged():
    assert 'base.import_all(root)' in inspect.getsource(r.import_all)
    s=inspect.getsource(r.qualify_one)
    assert 'git diff --quiet && git diff --cached --quiet' in s
    assert 'git ls-files --others --exclude-standard' in s
    assert 'path == "build" or path.startswith("build/")' in s
    assert 'git clean -fd -- build' in s and '-fdx' not in s


def test_qualification_hard_gate_20_of_20_and_zero_scientific_surface():
    s=inspect.getsource(r.qualify)
    assert 'qualified == 20' in s
    assert 'FRESH3_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN' in s
    source=inspect.getsource(r)
    for token in ('execute_trajectory(', 'writer_twins_valid(', 'shadow_phase(', 'final_measurement('): assert token not in source


def test_failed_v1_root_contains_no_artifacts():
    p=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-runtime-20260903-v1')
    assert p.is_dir()
    assert not any(x.is_file() for x in p.rglob('*'))
