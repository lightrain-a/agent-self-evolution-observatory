import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_resource import (
    chunk_plan, numeric_remaining, quantile, summarize_resources,
)


def test_quantile_and_resource_summary_are_deterministic():
    rows = [
        {"model_calls": i, "input_tokens": i * 10, "output_tokens": i * 2,
         "total_tokens": i * 12, "provider_latency_seconds": i / 2}
        for i in (1, 2, 3, 4)
    ]
    assert quantile([1, 2, 3, 4], .5) == 2.5
    result = summarize_resources(rows)
    assert result["model_calls"]["p50"] == 2.5
    assert result["total_tokens"]["p95"] == pytest.approx(46.2)


def test_chunk_plan_is_exact_contiguous_432_schedule():
    chunks = chunk_plan(432, 24)
    assert len(chunks) == 18
    assert chunks[0] == {"chunk_id": 1, "start_ordinal": 1,
                         "end_ordinal": 24, "unit_count": 24}
    assert chunks[-1]["end_ordinal"] == 432
    assert sum(row["unit_count"] for row in chunks) == 432
    assert all(left["end_ordinal"] + 1 == right["start_ordinal"]
               for left, right in zip(chunks, chunks[1:]))


def test_numeric_remaining_reads_only_matching_safe_quota_dimensions():
    headers = [
        {"x-ratelimit-remaining-requests": "700",
         "x-ratelimit-remaining-tokens": "9000"},
        {"x-quota-limit-requests": "1000", "retry-after": "2"},
    ]
    assert numeric_remaining(headers, "request") == [700]
    assert numeric_remaining(headers, "token") == [9000]
