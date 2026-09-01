from __future__ import annotations

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_structural import (
    structural_receipt, treatment_cases,
)

SAMPLING = {"temperature": 1.0, "top_p": .95, "top_k": 40,
            "max_output_tokens": 32768}


def test_complete_r1_invariants_and_evidence():
    case = {"task_id": "source", "query": "source issue",
            "memory_items": ["first lesson", "second lesson", "third lesson"]}
    receipt = structural_receipt(
        instance_id="eval", task_sha256="a" * 64,
        problem_statement="fix the bug", retrieved_case=case, sampling=SAMPLING)
    hashes = receipt["complete_R1_sha256"]
    assert hashes["A"] == hashes["B"] == hashes["E"]
    assert hashes["D"] != hashes["A"]
    assert receipt["complete_R1"]["A"] == receipt["complete_R1"]["B"]
    assert receipt["complete_R1"]["A"] == receipt["complete_R1"]["E"]
    assert receipt["complete_R1"]["D"] != receipt["complete_R1"]["A"]
    assert receipt["structurally_qualified"] is True
    assert receipt["behavioral_calls_made"] == 0


def test_d_uses_only_first_case_under_top1_without_adding_evidence():
    cases = treatment_cases("source", "query", ["one", "two", "three"])
    assert cases["D"][0]["memory_items"] == ["one"]
    assert cases["D"][1]["memory_items"] == ["two", "three"]
    assert cases["A"][0]["memory_items"] == ["one\n\ntwo\n\nthree"]


def test_requires_two_nonempty_items():
    try:
        treatment_cases("source", "query", ["one", " "])
    except ValueError as error:
        assert "at least two" in str(error)
    else:
        raise AssertionError("expected structural ineligibility")
