import json
import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_fidelity import (
    parse_review,
)


def valid():
    return {
        "faithful_to_source_trajectory": True,
        "unsupported_facts_absent": True,
        "gold_or_unavailable_test_leak_absent": True,
        "plausible_reusable_lesson": True,
        "SEVERE_FIDELITY_FAILURE": False,
        "rationale": "The lesson is supported by the visible trajectory.",
    }


def test_parse_exact_review_schema():
    assert parse_review(json.dumps(valid())) == valid()


def test_parse_rejects_missing_boolean_or_empty_rationale():
    row = valid()
    del row["faithful_to_source_trajectory"]
    with pytest.raises(ValueError, match="schema drift"):
        parse_review(json.dumps(row))
    row = valid()
    row["rationale"] = ""
    with pytest.raises(ValueError, match="rationale"):
        parse_review(json.dumps(row))
