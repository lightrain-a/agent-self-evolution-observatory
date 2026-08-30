from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_c1_pacta_20260830.py"


def load_module():
    spec = importlib.util.spec_from_file_location("c1_pacta_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_novelty_and_name_boundary():
    audit = json.loads((HERE / "c1-cast-novelty-audit-20260830.json").read_text())
    assert audit["verdict"] == "PASS_NOVEL_RESIDUAL"
    assert audit["name_verdict"] == "RENAME_CAST_TO_PACTA"
    assert audit["candidate_method"]["frozen_name"] == "PACTA"
    assert audit["fatal_collision_test"]["matching_prior_work_found"] is False


def test_frozen_split():
    split = json.loads((HERE / "c1-pacta-split-20260830.json").read_text())
    assert [u["future_task"] for u in split["pilot"]] == [313, 376, 368, 512, 300, 191]
    assert [u["future_task"] for u in split["confirmatory"]] == [510, 117, 24, 332, 656, 240, 166, 263, 273, 793, 351, 96, 439]
    for unit in split["pilot"] + split["confirmatory"]:
        expected = hashlib.sha256(f"C1-CAST-SPLIT-v1|{unit['intent_template_id']}|{unit['future_task']}".encode()).hexdigest()
        assert unit["cast_split_hash"] == expected


def test_prompt_hashes_and_field_symmetry():
    prompts = json.loads((HERE / "c1-pacta-projector-prompts-20260830.json").read_text())
    assert prompts["input_fields"] == ["REUSABLE MEMORY", "ULTIMATE TASK", "CURRENT BROWSER STATE", "ACTION SCHEMA"]
    for name in ["P0", "P1"]:
        assert hashlib.sha256(prompts[name]["template"].encode()).hexdigest() == prompts[name]["template_sha256"]
        for field in prompts["input_fields"]:
            assert field + ":" in prompts[name]["template"]
    suffix0 = prompts["P0"]["template"].split("\n\n", 1)[1]
    suffix1 = prompts["P1"]["template"].split("\n\n", 1)[1]
    assert suffix0 == suffix1


def test_projection_canonicalization_excludes_next_goal():
    module = load_module()
    schema = "Available action: click_element with integer index"
    a = '{"action":[{"click_element":{"index":7,"note":"x"}}],"next_goal":"first"}'
    b = '{"next_goal":"second","action":[{"click_element":{"note":"x","index":7}}]}'
    _, ca = module.parse_projection(a, schema)
    _, cb = module.parse_projection(b, schema)
    assert ca == cb == '{"click_element":{"index":7,"note":"x"}}'


def test_policy_arm_identity_when_gate_open_or_closed():
    module = load_module()
    args = ("sys", "task", "state", "memory")
    projection = '{"action":[{"click_element":{"index":1}}],"next_goal":"open"}'
    native = module.policy_prompt(*args, None, False)
    sap = module.policy_prompt(*args, projection, True)
    pacta_open = module.policy_prompt(*args, projection, True)
    pacta_closed = module.policy_prompt(*args, None, False)
    assert pacta_open == sap
    assert pacta_closed == native


def test_sign_flip_is_frozen_and_deterministic():
    module = load_module()
    values = [1.0, 1.0, 0.5, 0.0]
    first = module.sign_flip_test(values, repetitions=1000, seed=20260830)
    second = module.sign_flip_test(values, repetitions=1000, seed=20260830)
    assert first == second
    assert first[0] == sum(values) / len(values)


def test_contract_primary_cannot_switch():
    contract = json.loads((HERE / "c1-pacta-contract-20260830.json").read_text())
    assert contract["contrasts"]["primary"].startswith("D_gate_i")
    assert contract["confirmatory_gate"]["repetitions"] == 100000
    assert contract["confirmatory_gate"]["seed"] == 20260830
    assert contract["terminal_unlock"].startswith("only after confirmatory first-action PASS")
