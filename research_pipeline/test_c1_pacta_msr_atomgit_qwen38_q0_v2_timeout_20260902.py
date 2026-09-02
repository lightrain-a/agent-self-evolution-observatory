from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q0_v2_timeout_20260902 as v2
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q0_20260902 as v1
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file, sha256_text


def test_single_variable_timeout_repair_is_frozen():
    assert v2.TIMEOUT_SECONDS == 900
    assert v2.SOURCE_BUDGET == 16384
    assert v2.FIRST_BUDGET == 2048
    source = inspect.getsource(v2.call)
    assert "timeout=TIMEOUT_SECONDS" in source
    assert "provider_retries\": 0" in source
    assert "--no-tools" in source and "--ephemeral" in source and "--no-telemetry" in source


def test_parent_receipts_are_exact_content_addresses():
    observed = v2.verify_parent()
    assert observed == v2.EXPECTED_PARENT


def test_six_long_fixtures_are_exactly_inherited_from_v1():
    a = v1.long_fixtures()
    b = v2.long_fixtures()
    assert len(a) == len(b) == 6
    assert [x["fixture_id"] for x in a] == [x["fixture_id"] for x in b]
    assert [x["expected_sha256"] for x in a] == [x["expected_sha256"] for x in b]
    assert [sha256_text(v1.serialize_messages(x["messages"])) for x in a] == [sha256_text(v1.serialize_messages(x["messages"])) for x in b]


def test_reproduced_configs_are_byte_identical_to_parent():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for budget in (v2.FIRST_BUDGET, v2.SOURCE_BUDGET):
            out = root / f"max-{budget}.toml"
            v2.write_config(out, budget)
            parent = v2.PARENT_ROOT / "configs" / f"max-{budget}.toml"
            assert out.read_bytes() == parent.read_bytes()
            assert sha256_file(out) == v2.EXPECTED_PARENT[f"configs/max-{budget}.toml"]


def test_contract_declares_no_scientific_authority():
    contract = json.loads(v2.CONTRACT.read_text())
    assert contract["single_changed_variable"] == {
        "name": "atomcode_subprocess_timeout_seconds",
        "from": 300,
        "to": 900,
    }
    assert contract["source_budget"]["fixed_max_tokens"] == 16384
    assert contract["authority"]["scientific_source_acquisition"] is False
    assert contract["authority"]["pacta_effect_measurement"] is False


def test_q0v2_has_no_scientific_execution_surface():
    source = inspect.getsource(v2)
    for forbidden in (
        "execute_trajectory(",
        "future_task_executions +=",
        "writer_twins",
        "shadow_phase",
        "final_measurement(",
    ):
        assert forbidden not in source


def test_sampling_is_diagnostic_only_and_same_first_budget():
    source = inspect.getsource(v2.sampling)
    assert "FIRST_BUDGET" in source
    assert '"pass_requirement": False' in source
    assert "first_action_fixtures()[:2]" in source
