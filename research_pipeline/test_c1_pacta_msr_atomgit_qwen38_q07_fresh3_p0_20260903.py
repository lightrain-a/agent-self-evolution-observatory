from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from research_pipeline import c1_pacta_msr_atomgit_qwen38_q07_provider as provider
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q07_fresh3_p0_20260903 as q07
from research_pipeline import run_c1_pacta_msr_qwen397_p0_stages_20260902 as legacy
from research_pipeline import run_c1_pacta_msr_qwen397_p0_final_20260902 as legacy_final


def test_q07_static_inputs_and_qualifications_are_bound():
    observed = q07.verify_static()
    assert observed["pool"] == q07.POOL_SHA
    assert observed["q05"] == q07.Q05_SHA
    assert observed["q06"] == q07.Q06_SHA
    assert observed["runtime"] == q07.RUNTIME_SHA


def test_q07_split_and_shadow_geometry_are_frozen_without_source_outcome():
    split = json.loads(q07.SPLIT.read_text())
    assert len(split["pilot"]) == 8
    assert len(split["sealed"]) == 2
    assert set(split["random_ranking_pre_shadow"]) == set(split["pilot"])
    schedule = q07.schedule_shadow(split["pilot"])
    assert len(schedule) == 384
    assert len({row["case_id"] for row in schedule}) == 384
    assert all(row["unit_id"] in split["pilot"] for row in schedule)


def test_q07_probe_runtime_binding_is_ten_and_content_addressed():
    rows = q07.bound_probe_specs()
    assert len(rows) == 10
    assert all(row["future_digest_ref"].startswith("docker.1ms.run/") for row in rows.values())
    assert all(len(row["command_sha256"]) == 64 for row in rows.values())


def test_q07_provider_ceilings_and_resource_envelope_match_q05_q06_contract():
    assert provider.WRITER_MAX_TOKENS == 4096
    assert provider.BINDER_MAX_TOKENS == 2048
    assert provider.ACTION_MAX_TOKENS == 4096
    assert provider.MAX_SCIENTIFIC_REQUESTS == 816
    assert provider.MAX_COMPLETION_TOKENS_TOTAL == 3_276_800
    assert provider.STAGE_MAX == {"writer": 4096, "binder": 2048, "shadow": 4096, "final": 4096}


def test_q07_provider_records_but_does_not_use_legacy_temperature_or_ceiling():
    source = inspect.getsource(provider.Provider.call)
    assert '"legacy_callsite_max_tokens": max_tokens' in source
    assert '"legacy_callsite_temperature": temperature' in source
    assert "actual_max = STAGE_MAX[self.stage]" in source
    assert "temperature_control" in source
    assert "for attempt" not in source
    assert "retry" not in source.split("def call",1)[1].split("return",1)[0].lower() or '"provider_retries": 0' in source


def test_q07_prepare_does_not_read_source_support():
    source = inspect.getsource(q07.prepare)
    assert "source_support(" not in source
    assert "support-audit" not in source
    assert "schedule_shadow" in source
    assert "write_configs" in source


def test_q07_every_nonprepare_phase_revalidates_source_gate():
    source = inspect.getsource(q07.run_phase)
    gate_index = source.index("source_support()")
    bind_index = source.index("bind_legacy()")
    assert gate_index < bind_index
    for phase in ("probe", "writer", "binder", "shadow", "final"):
        assert f'phase == "{phase}"' in source


def test_q07_source_gate_is_fail_closed_when_audit_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(q07, "SOURCE_ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="SOURCE_GATE_PENDING"):
        q07.source_support()


def test_q07_bind_legacy_swaps_only_provider_data_and_runtime_surfaces():
    q07.bind_legacy()
    assert legacy.Provider is provider.Provider
    assert legacy.pilot_units is q07.pilot_units
    assert legacy.probe_specs is q07.bound_probe_specs
    assert legacy.Container is q07.Fresh3Container
    assert legacy.SHADOW_SALT == q07.SHADOW_SALT
    assert legacy_final.Provider is provider.Provider
    assert legacy_final.pilot_units is q07.pilot_units
    assert legacy_final.SALT == q07.FINAL_SALT


def test_q07_contract_explicitly_disclaims_temperature_equivalence_and_sealed_execution():
    contract = json.loads(q07.CONTRACT.read_text())
    assert contract["scientific_phase_execution_before_source_gate"] is False
    assert contract["sealed_execution"].startswith("forbidden")
    assert contract["writer"]["max_tokens"] == 4096
    assert contract["binder"]["max_tokens"] == 2048
    assert contract["shadow"]["max_tokens"] == 4096
    assert contract["final"]["max_tokens"] == 4096
    assert contract["temperature"]["supported_override"] is False
    assert contract["resource_envelope"]["maximum_scientific_requests_if_final_runs"] == 816
    assert contract["resource_envelope"]["maximum_completion_tokens_total"] == 3_276_800


def test_q07_no_new_method_gate_or_threshold_drift():
    contract = json.loads(q07.CONTRACT.read_text())
    assert contract["mechanism_gate"]["Gplus_open_count"] == "2..6/8"
    assert contract["mechanism_gate"]["mean_margin_Gplus_minus_G0_ge"] == 0.05
    assert contract["mechanism_gate"]["positive_margin_improvement_count_ge"] == 5
    assert contract["final"]["calls"] == 384
    assert contract["shadow"]["calls"] == 384
