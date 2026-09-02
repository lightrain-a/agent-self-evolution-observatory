from __future__ import annotations

import json
from pathlib import Path

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh2_20260903 as f


def test_exclusions_are_49_unique_and_include_entire_retired_pool():
    ids, provenance = f.exclusion_ids()
    assert len(ids) == 49
    assert provenance["base_prior_count"] == 29
    assert provenance["retired_pool_count"] == 20
    retired = json.loads(f.RETIRED_POOL.read_text())
    retired_ids = {x for u in retired["units"] for x in (u["source_task_id"], u["future_task_id"])}
    assert retired_ids <= ids
    assert "matplotlib__matplotlib-25479" in ids


def test_pool_is_twenty_new_ids_across_ten_repositories():
    excluded, _ = f.exclusion_ids()
    pool = f.select_pool()
    assert pool["candidate_count"] == 10
    assert pool["repository_count"] == 10
    ids = [x for u in pool["units"] for x in (u["source_task_id"], u["future_task_id"])]
    assert len(ids) == len(set(ids)) == 20
    assert not (set(ids) & excluded)
    assert all(u["prior_id_overlap"] is False for u in pool["units"])
    assert pool["selection"]["outcome_fields_read"] is False


def test_selection_is_deterministic():
    a = f.select_pool()
    b = f.select_pool()
    assert [(u["unit_id"], u["source_rank"], u["future_rank"]) for u in a["units"]] == [
        (u["unit_id"], u["source_rank"], u["future_rank"]) for u in b["units"]
    ]


def test_split_is_eight_two_and_random_ranking_frozen():
    pool = f.select_pool()
    s = f.split(pool)
    assert len(s["pilot"]) == 8
    assert len(s["sealed"]) == 2
    assert not (set(s["pilot"]) & set(s["sealed"]))
    assert len(s["random_ranking_pre_shadow"]) == 8
    assert set(s["random_ranking_pre_shadow"]) == set(s["pilot"])
    assert s["provider_calls"] == 0 and s["scientific_source_calls"] == 0


def test_contract_binds_q02_budget_and_forbids_reuse():
    c = json.loads(f.CONTRACT.read_text())
    assert c["exclusions"]["expected_total_unique_excluded_ids"] == 49
    assert c["exclusions"]["reuse_allowed"] is False
    assert c["frozen_model_transport_for_later"]["source_max_completion_tokens"] == 32768
    assert c["frozen_model_transport_for_later"]["source_invocation_timeout_seconds"] == 900
    assert c["pilot_geometry"] == {"pilot_units": 8, "sealed_units": 2, "freeze_before_any_model_call": True}


def test_compiler_has_no_provider_or_scientific_execution_surface():
    src = Path(f.__file__).read_text(encoding="utf-8")
    for marker in ("atomcode", "AA_API_KEY", "execute_trajectory(", "docker run", "writer_phase(", "shadow_phase("):
        assert marker not in src.lower() if marker.islower() else marker not in src
    assert "problem_statement" in src  # selection metadata only
    assert "gold_patch" not in src
    assert "FAIL_TO_PASS" not in src
