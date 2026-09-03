from __future__ import annotations

import inspect
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh2_runtime_clean_20260903 as r


def test_parent_receipts_are_content_addressed():
    a = r.parent_audit()
    assert a['import_sha256'] == r.PARENT_IMPORT_SHA
    assert a['qualification_sha256'] == r.PARENT_QUAL_SHA


def test_repair_is_targeted_not_generic_clean_x():
    src = inspect.getsource(r.qualify_one)
    assert "git clean -fd -- build" in src
    assert "git clean -fdx" not in src
    assert "git clean -fd '" not in src


def test_repair_rejects_tracked_dirt_and_non_build_untracked():
    src = inspect.getsource(r.qualify_one)
    assert 'git diff --quiet && git diff --cached --quiet' in src
    assert "x == 'build' or x.startswith('build/')" in src
    assert "initial_tracked_tree_clean" in src
    assert "initial_untracked_only_build" in src


def test_repair_requires_exact_postconditions():
    src = inspect.getsource(r.qualify_one)
    assert "post_reset_head_exact" in src
    assert "post_reset_working_tree_clean" in src
    assert "git status --porcelain=v1 --untracked-files=all" in src


def test_requalification_is_all_20_not_only_failed_future():
    src = inspect.getsource(r.qualify)
    assert 'for row in frozen_rows()' in src
    assert "n == 20" in src
    assert "source_qualified" in src and "future_qualified" in src


def test_no_provider_or_scientific_stage_surface():
    src = inspect.getsource(r)
    assert 'atomcode' not in src.lower()
    for token in ('AA_API_KEY', 'writer_phase(', 'binder_phase(', 'shadow_phase(', 'final_measurement('):
        assert token not in src
    assert "'provider_calls': 0" in src
    assert "'scientific_source_tasks_used': 0" in src


def test_contract_exists():
    assert r.CONTRACT.is_file()
