from __future__ import annotations

import inspect

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh2_probe_specs_20260903 as mod
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_pool_binding_is_exact():
    assert sha256_file(mod.POOL) == mod.POOL_SHA


def test_probe_geometry_is_ten_and_provider_free():
    out = mod.prepare()
    assert len(out["rows"]) == 10
    assert out["provider_calls"] == 0
    assert out["scientific_source_tasks_used"] == 0
    assert out["future_task_executions"] == 0
    assert len({row["future_task_id"] for row in out["rows"]}) == 10


def test_commands_are_read_only_and_exactly_three_tokens():
    out = mod.prepare()
    for row in out["rows"]:
        assert len(row["tokens"]) == 3
        assert row["command"].startswith("git status --short; git grep -n -I ")
        assert row["command"].endswith("; git ls-files | head -n 40")
        assert row["read_only"] is True
        assert row["branch_blind"] is True
        assert row["memory_blind"] is True


def test_runtime_is_deferred_not_guessed():
    out = mod.prepare()
    assert all(row["runtime_binding"] == "DEFERRED_UNTIL_FRESH2_20_RUNTIME_READY" for row in out["rows"])
    source = inspect.getsource(mod)
    assert "digest_ref" not in source
    assert "docker" not in source.lower()


def test_no_model_or_outcome_surface():
    source = inspect.getsource(mod.prepare)
    for forbidden in ("AtomGit", "atomcode", "execute_trajectory", "source_trajectory.json", "shadow_phase(", "writer_twins("):
        assert forbidden not in source
