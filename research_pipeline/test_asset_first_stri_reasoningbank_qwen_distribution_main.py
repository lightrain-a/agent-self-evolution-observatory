from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_main import (
    chunk_headroom, consumed_resources, next_chunk,
)


def authority(request_budget=None, token_budget=None):
    return {
        "quota_evidence": {
            "effective_request_budget": request_budget,
            "effective_token_budget": token_budget,
            "request_budget_proven": request_budget is not None,
            "token_budget_proven": token_budget is not None,
        },
        "resource_summary": {
            "model_calls": {"p95": 3},
            "total_tokens": {"p95": 1000},
        },
    }


def test_next_chunk_supports_boundary_and_prefix_resume():
    chunks = [
        {"chunk_id": 1, "start_ordinal": 1, "end_ordinal": 24},
        {"chunk_id": 2, "start_ordinal": 25, "end_ordinal": 48},
    ]
    assert next_chunk(chunks, 0)["chunk_id"] == 1
    assert next_chunk(chunks, 17)["chunk_id"] == 1
    assert next_chunk(chunks, 24)["chunk_id"] == 2
    assert next_chunk(chunks, 48) is None


def test_consumed_resources_reads_only_persisted_usage():
    receipts = [{
        "trajectory": {
            "model_call_count": 2,
            "responses": [
                {"usage": {"input_tokens": 10, "output_tokens": 2}},
                {"usage": {"input_tokens": 20, "output_tokens": 3}},
            ],
        },
    }]
    assert consumed_resources(receipts) == {"model_calls": 2, "total_tokens": 35}


def test_chunk_headroom_accepts_either_proven_budget_dimension():
    chunk = {"chunk_id": 1, "start_ordinal": 1, "end_ordinal": 24}
    request_pass = chunk_headroom(
        authority(request_budget=100), chunk, 0,
        {"model_calls": 0, "total_tokens": 0})
    assert request_pass["decision"] == "CHUNK_RESOURCE_HEADROOM_PASS"
    token_pass = chunk_headroom(
        authority(token_budget=50_000), chunk, 0,
        {"model_calls": 0, "total_tokens": 0})
    assert token_pass["decision"] == "CHUNK_RESOURCE_HEADROOM_PASS"
    held = chunk_headroom(
        authority(request_budget=10), chunk, 0,
        {"model_calls": 0, "total_tokens": 0})
    assert held["decision"] == "CHUNK_RESOURCE_HEADROOM_HOLD"
