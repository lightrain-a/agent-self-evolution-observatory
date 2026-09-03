from __future__ import annotations

import inspect
import json

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_text_bridge_20260903 as q03
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q06_downstream_estimand_20260903 as q06
from research_pipeline.c1_pacta_rb_qwen397 import sha256_text


def messages_sha(fx):
    return sha256_text(json.dumps(fx["messages"], ensure_ascii=False, sort_keys=True))


def test_q06_action_budget_ladder_starts_from_old_first_decision_and_stops_at_q03_ceiling():
    assert q06.ACTION_BUDGETS == (2048, 4096, 8192, 16384, 32768)
    assert q06.SAMPLING_FIXTURE_IDS == ("q03-first-01", "q03-first-02")
    assert q06.SAMPLING_REPS == 6


def test_q06_parent_verification_passes_and_binds_q03_q05_p0_fresh3():
    parent = q06.verify_parent()
    assert parent["q03_prepare_sha256"] == q06.Q03_PREPARE_SHA
    assert parent["q03_result_sha256"] == q06.Q03_RESULT_SHA
    assert parent["q05_closure_sha256"] == q06.Q05_CLOSURE_SHA
    assert parent["original_p0_sha256"] == q06.ORIGINAL_P0_SHA
    assert parent["fresh3_split_sha256"] == q06.FRESH3_SPLIT_SHA
    assert parent["fresh3_probe_specs_sha256"] == q06.FRESH3_PROBES_SHA
    assert parent["fresh3_source_schedule_sha256"] == q06.FRESH3_SCHEDULE_SHA


def test_q06_reuses_exact_q03_messages():
    prep = json.loads(q06.Q03_PREPARE.read_text())
    expected = {row["fixture_id"]: row["messages_sha256"] for row in prep["fixtures"]}
    fixtures = q03.fixtures()
    assert len(fixtures) == 12
    for fx in fixtures:
        assert messages_sha(fx) == expected[fx["fixture_id"]]


def test_q06_budget_runner_changes_only_q03_max_token_config_and_calls_same_bridge():
    source = inspect.getsource(q06._run_budget)
    assert "q03.fixtures()" in source
    assert "q03.call_fixture" in source
    bind_source = inspect.getsource(q06._bind_budget)
    assert "q03.MAX_TOKENS = budget" in bind_source
    assert "q03.write_config" in bind_source


def test_q06_sampling_is_exact_repeat_of_two_q03_fixtures():
    source = inspect.getsource(q06._run_sampling)
    assert "SAMPLING_FIXTURE_IDS" in source
    assert "SAMPLING_REPS" in source
    assert "q03.call_fixture" in source
    assert "diversity_is_descriptive_not_gate" in source


def test_q06_selects_first_passing_budget_only():
    source = inspect.getsource(q06.run)
    assert "if res[\"pass\"]:" in source
    assert "selected = budget" in source
    assert "break" in source


def test_q06_has_no_fresh3_source_artifact_input():
    source = inspect.getsource(q06)
    for forbidden in (
        "fresh3-source-20260903-v2",
        "source_trajectory.json",
        "acquisition-journal.jsonl",
        "support-audit.json",
        "psf__requests-6028",
        "sympy__sympy-15875",
    ):
        assert forbidden not in source


def test_q06_has_no_scientific_downstream_execution_surface():
    source = inspect.getsource(q06)
    for forbidden in ("writer_phase(", "binder_phase(", "shadow_phase(", "final_measurement(", "execute_trajectory("):
        assert forbidden not in source
    for guard in ("scientific_writer_calls", "scientific_binder_calls", "scientific_shadow_calls", "scientific_final_calls"):
        assert guard in source


def test_q06_contract_explicitly_disclaims_temperature_equivalence_and_conditions_on_realized_states():
    contract = json.loads(q06.CONTRACT.read_text())
    assert contract["fresh3_source_terminal_outcomes_used_to_choose_q06_parameters"] is False
    assert contract["fresh3_source_artifacts_used_as_q06_fixtures"] is False
    assert contract["action_budget_qualification"]["candidate_max_tokens"] == [2048, 4096, 8192, 16384, 32768]
    assert "does not expose" in contract["motivation"]
    assert "conditions on those realized" in contract["downstream_state_generation"]["interpretation"]
    assert "No temperature equivalence claim" in contract["downstream_action_estimand"]["sampling"]
    assert contract["mechanism_gate"]["unchanged_from_original_p0"] is True
