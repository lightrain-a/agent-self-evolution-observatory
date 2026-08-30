from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1_PROMPTS = HERE / "c1-pacta-projector-prompts-20260830.json"
V11_SCHEMA = HERE / "c1-pacta-v11-action-schema-20260830.json"
V11_FIXTURES = HERE / "c1-pacta-v11-schema-fixtures-20260830.json"
V11_SPLIT = HERE / "c1-pacta-v11-split-20260830.json"
V11_CONTRACT = HERE / "c1-pacta-v11-contract-20260830.json"


def load_module(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_single_variable_prompt_hashes_unchanged():
    prompts = json.loads(V1_PROMPTS.read_text())
    contract = json.loads(V11_CONTRACT.read_text())
    assert prompts["P0"]["template_sha256"] == contract["unchanged"]["P0_sha256"] == "d4f1f4aeafac058b83930499ea10a2db0b70db9f5a76131fcd4ff8e0486de295"
    assert prompts["P1"]["template_sha256"] == contract["unchanged"]["P1_sha256"] == "cfe5f1957da06a674d7c90e4c7e7753505482c7f17de9ecd28191e4fd3c44caf"
    assert contract["single_variable_repair"]["after"].startswith("ACTION_SCHEMA = deterministically extracted")
    assert contract["lineage"]["PACTA_v1"] == "INVALID_UNQUALIFIED_INTERFACE_EXECUTION"


def test_schema_contains_only_affordances():
    artifact = json.loads(V11_SCHEMA.read_text())
    schema = artifact["projector_schema_canonical_json"]
    assert hashlib.sha256(schema.encode()).hexdigest() == artifact["action_schema_sha256"]
    assert set(json.loads(schema)) == {"tools"}
    forbidden = (
        "current_state",
        "next_goal",
        "REUSABLE MEMORY",
        "ULTIMATE TASK",
        "evaluation_previous_goal",
        "You are an AI agent",
        "Your responses must",
    )
    assert not any(text in schema for text in forbidden)
    assert artifact["source_system_instruction_sha256"] != artifact["action_schema_sha256"]


def test_fresh_hash_selected_template_pilot():
    split = json.loads(V11_SPLIT.read_text())
    assert len(split["candidate_pool"]) == 23
    assert len({row["intent_template_id"] for row in split["candidate_pool"]}) == 7
    assert split["pilot_ids"] == [353, 238, 272, 653, 440, 792, 264]
    assert len(split["unused_without_outcome_access"]) == 16
    for template in sorted({row["intent_template_id"] for row in split["candidate_pool"]}):
        rows = [row for row in split["candidate_pool"] if row["intent_template_id"] == template]
        chosen = min(rows, key=lambda row: row["split_hash"])
        assert chosen["future_task"] in split["pilot_ids"]
        for row in rows:
            expected = hashlib.sha256(f"C1-PACTA-V11-PILOT-v1|{template}|{row['future_task']}".encode()).hexdigest()
            assert row["split_hash"] == expected
            assert row["prior_pacta_projection_or_policy_outputs"] == []
            assert row["prior_scmb_scientific_outputs"] == []


def test_non_scientific_fixture_geometry():
    fixtures = json.loads(V11_FIXTURES.read_text())
    assert fixtures["scientific_state_used"] is False
    assert fixtures["expected_calls"] == 40
    assert len(fixtures["fixtures"]) == 20
    assert len({row["fixture_id"] for row in fixtures["fixtures"]}) == 20


def test_exact_projection_contract_rejects_native_envelope_and_prose():
    runner = load_module("run_c1_pacta_v11_20260830.py", "pacta_v11_runner")
    schema_module = load_module("c1_pacta_v11_action_schema.py", "pacta_v11_schema")
    schema = schema_module.canonical_schema()
    good = '{"action":[{"click_element":{"index":7}}],"next_goal":"Open reviews"}'
    parsed, canonical = runner.exact_projection(good, schema)
    assert canonical == '{"click_element":{"index":7}}'
    assert parsed["next_goal"] == "Open reviews"
    for bad in (
        '{"current_state":{"next_goal":"Open reviews"},"action":[{"click_element":{"index":7}}]}',
        'prose {"action":[{"click_element":{"index":7}}],"next_goal":"Open reviews"}',
        '{"action":[{"unknown_tool":{}}],"next_goal":"Continue"}',
    ):
        try:
            runner.exact_projection(bad, schema)
        except Exception:
            pass
        else:
            raise AssertionError(f"invalid projection accepted: {bad}")


def test_arm_identity_and_stop_boundary():
    runner = load_module("run_c1_pacta_v11_20260830.py", "pacta_v11_runner_arms")
    projection = '{"action":[{"click_element":{"index":1}}],"next_goal":"Open"}'
    args = ("system", "task", "state", "memory")
    native = runner.v1.policy_prompt(*args, None, False)
    sap = runner.v1.policy_prompt(*args, projection, True)
    assert native == runner.v1.policy_prompt(*args, None, False)
    assert sap == runner.v1.policy_prompt(*args, projection, True)
    contract = json.loads(V11_CONTRACT.read_text())
    assert contract["pilot"]["gate_open_min"] == 2
    assert contract["pilot"]["gate_open_max"] == 6
    assert contract["pilot"]["gate_open_mean_D_gate_min"] == 0.05
    assert contract["pilot"]["gate_open_positive_fraction_min"] == 0.5
    assert contract["stop_after_pilot"] is True
    assert contract["terminal_authorized"] is False
    assert contract["same_substrate_confirmatory_authorized"] is False
