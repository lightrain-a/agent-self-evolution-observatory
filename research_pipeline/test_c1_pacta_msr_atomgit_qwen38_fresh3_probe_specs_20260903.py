from __future__ import annotations

import inspect

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh3_probe_specs_20260903 as p
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_pool_binding_and_geometry() -> None:
    assert sha256_file(p.POOL) == p.POOL_SHA
    row = p.prepare()
    assert row["status"] == "FRESH3_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME"
    assert len(row["rows"]) == 10
    assert len({x["future_task_id"] for x in row["rows"]}) == 10


def test_probe_is_branch_memory_provider_blind_and_read_only() -> None:
    row = p.prepare()
    for item in row["rows"]:
        assert item["provider_calls"] == 0
        assert item["future_task_executions"] == 0
        assert item["branch_blind"] is True
        assert item["memory_blind"] is True
        assert item["read_only"] is True
        assert item["command"].startswith("git status --short; git grep")
        assert "git ls-files | head -n 40" in item["command"]


def test_token_salt_is_fresh3_specific() -> None:
    assert "FRESH3" in p.TOKEN_SALT and "FRESH2" not in p.TOKEN_SALT


def test_no_runtime_or_model_call_surface() -> None:
    source = inspect.getsource(p)
    for forbidden in ("atomcode", "execute_trajectory(", "docker run", "subprocess.run"):
        assert forbidden not in source.lower()
