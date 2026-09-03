from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh3_20260903 as f3


def test_exclusion_set_is_exactly_69_unique_ids() -> None:
    ids, provenance = f3.exclusion_ids()
    assert len(ids) == 69
    assert provenance["historical_prior_count"] == 29
    assert provenance["fresh1_count"] == 20
    assert provenance["fresh2_count"] == 20
    assert provenance["total_unique_excluded"] == 69


def test_q03_pass_is_required_before_fresh3_selection() -> None:
    assert f3.sha_file(f3.Q03_CLOSEOUT) == f3.EXPECTED_Q03_CLOSEOUT_SHA
    doc = json.loads(f3.Q03_CLOSEOUT.read_text())
    assert doc["status"] == "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS"
    assert doc["fresh3_authorized"] is True


def test_selection_has_ten_repositories_twenty_disjoint_ids() -> None:
    excluded, _ = f3.exclusion_ids()
    pool = f3.select_pool()
    assert pool["candidate_count"] == 10
    assert pool["repository_count"] == 10
    ids = [task for u in pool["units"] for task in (u["source_task_id"], u["future_task_id"])]
    assert len(ids) == 20 and len(set(ids)) == 20
    assert not (set(ids) & excluded)
    assert len({u["task_family"] for u in pool["units"]}) == 10
    assert pool["provider_calls"] == 0 and pool["scientific_source_calls"] == 0


def test_selection_is_deterministic_and_uses_no_outcome_column() -> None:
    a = f3.select_pool(); b = f3.select_pool()
    keys = ["unit_id", "source_task_id", "future_task_id", "source_rank", "future_rank", "pilot_rank", "random_gate_rank"]
    assert [{k:u[k] for k in keys} for u in a["units"]] == [{k:u[k] for k in keys} for u in b["units"]]
    columns = set(pq.read_schema(f3.DATASET).names)
    assert "problem_statement" in columns
    assert a["selection"]["outcome_fields_read"] is False


def test_split_is_8_2_and_random_ranking_only_over_pilot() -> None:
    pool = f3.select_pool(); split = f3.make_split(pool)
    assert len(split["pilot"]) == 8
    assert len(split["sealed"]) == 2
    assert len(set(split["pilot"]) | set(split["sealed"])) == 10
    assert len(split["random_ranking_pre_shadow"]) == 8
    assert set(split["random_ranking_pre_shadow"]) == set(split["pilot"])
    assert split["provider_calls"] == 0


def test_new_salts_are_fresh3_specific() -> None:
    for value in (f3.SOURCE_SALT, f3.FUTURE_SALT, f3.PILOT_SALT, f3.RANDOM_SALT):
        assert "FRESH3" in value
        assert "FRESH2" not in value


def test_contract_forbids_reuse_and_provider_before_commit() -> None:
    contract = json.loads(f3.CONTRACT.read_text())
    assert contract["total_unique_excluded_expected"] == 69
    assert contract["provider_calls"] == 0
    assert contract["scientific_source_calls"] == 0
    text = " ".join(contract["forbidden"])
    assert "69 excluded" in text
    assert "before fresh3 pool and split are committed" in text
