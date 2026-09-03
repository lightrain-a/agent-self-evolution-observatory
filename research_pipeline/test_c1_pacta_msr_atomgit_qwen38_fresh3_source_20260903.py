from __future__ import annotations

import inspect
import tempfile
from pathlib import Path

import pytest

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_source_20260903 as s
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_fixed_inputs_are_content_addressed_except_runtime_receipt() -> None:
    for path, expected in (
        (s.POOL, s.POOL_SHA), (s.Q02_CLOSURE, s.Q02_CLOSURE_SHA), (s.Q02_RESULT, s.Q02_RESULT_SHA),
        (s.Q03_CLOSURE, s.Q03_CLOSURE_SHA), (s.Q03_CONFIG, s.Q03_CONFIG_SHA),
        (s.FROZEN_SCHEDULE, s.FROZEN_SCHEDULE_SHA), (s.PROBE_SPECS, s.PROBE_SPECS_SHA),
        (s.EXECUTION_CONTRACT, s.EXECUTION_CONTRACT_SHA), (s.CONFIG, s.CONFIG_SHA),
    ):
        assert sha256_file(path) == expected
    assert not hasattr(s, "RUNTIME_SHA")


def test_runtime_sha_is_required_as_explicit_64hex_input() -> None:
    with pytest.raises(RuntimeError, match="RUNTIME_SHA_FORMAT"):
        s.verify("bad")
    source = inspect.getsource(s.main)
    assert '"--runtime-qualification-sha"' in source
    assert "required=True" in source


def test_provider_config_is_byte_equal_q03_bridge_config() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "provider.toml"
        s.write_config(path)
        assert path.read_bytes() == s.Q03_CONFIG.read_bytes()
        assert sha256_file(path) == s.Q03_CONFIG_SHA


def test_source_condition_is_q02_budget_plus_q03_bridge() -> None:
    assert s.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert s.PACTA_FIRST_DECISION_BUDGET == 2048
    assert s.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900
    assert s.BRIDGE_SCHEMA == "c1-minisweagent-ordinary-json-text-bridge-v1"
    assert "FRESH3_JSON_BRIDGE_SOURCE" in s.PROVIDER_ID


def test_prelaunch_uses_fresh3_targeted_clean_container() -> None:
    source = inspect.getsource(s.prelaunch)
    assert "Fresh3Container(" in source
    assert "provider_calls" in source
    assert "execute_trajectory(" not in source


def test_smoke_and_scientific_source_share_bridge_runtime() -> None:
    smoke = inspect.getsource(s.smoke); acquire = inspect.getsource(s.acquire)
    assert "execute_trajectory(" in smoke
    assert "execute_trajectory(" in acquire
    assert "provider_config_path=root / \"provider-config.toml\"" in smoke
    assert "provider_config_path=root / \"provider-config.toml\"" in acquire


def test_source_gate_has_no_partial_or_replacement_path() -> None:
    source = inspect.getsource(s.acquire)
    assert "SOURCE_POOL_PARTIAL_STOP" not in source
    assert "FRESH3_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED" in source
    assert "HOLD_FRESH3_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE" in source
    assert '"replacement": False' in source
    assert '"top_up": False' in source


def test_no_downstream_stage_surface() -> None:
    source = inspect.getsource(s)
    for forbidden in ("writer_twins_valid(", "binder_phase(", "shadow_phase(", "final_measurement("):
        assert forbidden not in source
