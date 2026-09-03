from __future__ import annotations

import inspect
import json

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh4_20260903 as f4


def test_fresh4_excludes_exactly_89_unique_prior_ids():
    ids, provenance = f4.exclusion_ids()
    assert len(ids) == 89
    assert provenance["historical_prior_count"] == 29
    assert provenance["fresh1_count"] == 20
    assert provenance["fresh2_count"] == 20
    assert provenance["fresh3_count"] == 20
    assert provenance["total_unique_excluded"] == 89


def test_fresh4_pool_geometry_is_nine_repos_ten_pairs_twenty_new_ids():
    excluded, _ = f4.exclusion_ids()
    pool = f4.select_pool()
    assert pool["candidate_count"] == 10
    assert pool["repository_count"] == 9
    counts = sorted(pool["repository_pair_counts"].values())
    assert counts == [1] * 8 + [2]
    duplicate = pool["selection"]["duplicate_repository"]
    assert pool["repository_pair_counts"][duplicate] == 2
    ids = [x for u in pool["units"] for x in (u["source_task_id"], u["future_task_id"])]
    assert len(ids) == 20 and len(set(ids)) == 20
    assert not (set(ids) & excluded)
    assert all(u["provider_interface"] == "controlled-output-mcp-q03" for u in pool["units"])


def test_fresh4_split_is_frozen_eight_plus_two():
    pool = f4.select_pool()
    split = f4.split(pool)
    assert len(split["pilot"]) == 8
    assert len(split["sealed"]) == 2
    assert len(split["random_ranking_pre_shadow"]) == 8
    assert set(split["pilot"]).isdisjoint(split["sealed"])
    assert set(split["random_ranking_pre_shadow"]) == set(split["pilot"])


def test_fresh4_selection_never_reads_outcome_fields():
    src = inspect.getsource(f4.select_pool)
    assert "problem_statement" in src
    assert "base_commit" in src
    for forbidden in ("PASS_TO_PASS", "FAIL_TO_PASS", "patch", "test_patch", "resolved"):
        assert forbidden not in src


def test_fresh4_contract_requires_controlled_output_and_no_reuse():
    contract = json.loads(f4.CONTRACT.read_text())
    assert contract["expected_unique_exclusion_count"] == 89
    assert contract["provider_calls"] == 0
    assert contract["scientific_source_calls"] == 0
    assert contract["replacement"] is False
    assert contract["top_up"] is False
    assert contract["repository_count"] == 9
    assert "hash-selected repository contributes two pairs" in contract["repository_pair_weighting"]
    assert contract["controlled_output_policy"]["allowed_tool"] == "mcp__c1output__submit_output"
    assert contract["controlled_output_policy"]["host_tools_allowed"] is False
    assert "reuse any fresh1/fresh2/fresh3 task" in contract["forbidden"]


def test_fresh4_main_is_zero_provider_only():
    src = inspect.getsource(f4.main)
    assert "atomcode" not in src.lower()
    assert "provider_calls" in src
    assert "scientific_source_calls" in src
