import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    memory_for_arm,
)


BANK = {"source": {"source_task_id": "source",
                   "parsed_memory_items": ["one", "two", "three"]}}
RETRIEVAL = {"top1_source_task_id": "source"}


def test_behavioral_memories_A_D_N():
    assert memory_for_arm(BANK, RETRIEVAL, "A") == "one\n\ntwo\n\nthree"
    assert memory_for_arm(BANK, RETRIEVAL, "D") == "one"
    assert memory_for_arm(BANK, RETRIEVAL, "N") == ""


def test_d_requires_structural_split():
    bank = {"source": {"source_task_id": "source", "parsed_memory_items": ["one"]}}
    with pytest.raises(RuntimeError, match="not structurally splittable"):
        memory_for_arm(bank, RETRIEVAL, "D")


def test_B_is_not_a_behavioral_arm():
    with pytest.raises(ValueError, match="unsupported"):
        memory_for_arm(BANK, RETRIEVAL, "B")
