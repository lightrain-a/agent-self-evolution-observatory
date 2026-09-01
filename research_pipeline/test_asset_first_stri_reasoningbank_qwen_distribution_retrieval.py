import torch

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_retrieval import (
    detailed_query, retrieval_receipt, stable_top_scores,
)


def test_detailed_query_preserves_official_instruction():
    text = detailed_query("fix bug")
    assert text.startswith("Instruct: Given the prior software engineering queries")
    assert text.endswith("Query: fix bug")


def test_stable_top_scores_preserves_source_order_on_tie():
    sources = torch.tensor([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    query = torch.tensor([[1.0, 0.0]])
    rows = stable_top_scores(["first", "second", "third"], sources, query)
    assert [row[0] for row in rows] == ["first", "second", "third"]


def test_receipt_has_top2_margin_and_same_repo():
    receipt = retrieval_receipt(
        instance_id="repo__eval", task_sha256="a" * 64, query="query",
        source_ids=["repo__source", "other__source"],
        source_repositories=["repo", "other"],
        source_vectors=torch.tensor([[1.0, 0.0], [0.0, 1.0]]),
        query_vector=torch.tensor([[1.0, 0.0]]), source_bank_sha256="b" * 64)
    assert receipt["top1_source_task_id"] == "repo__source"
    assert receipt["top1_relevance"] == 100
    assert receipt["top2_relevance"] == 0
    assert receipt["top1_top2_margin"] == 100
    assert receipt["same_repository_indicator"] is True
    assert receipt["top_k"] == 1
