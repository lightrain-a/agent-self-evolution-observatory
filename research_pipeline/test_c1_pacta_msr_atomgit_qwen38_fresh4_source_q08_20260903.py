from __future__ import annotations

import inspect

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh4_source_q08_20260903 as run
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_q08_authority_artifacts_are_exactly_bound() -> None:
    assert sha256_file(run.STRESS_RESULT) == run.STRESS_RESULT_SHA
    assert sha256_file(run.STRESS_CLOSURE) == run.STRESS_CLOSURE_SHA
    assert sha256_file(run.Q08_CONTRACT) == run.Q08_CONTRACT_SHA


def test_q08_authority_is_currently_passed() -> None:
    authority = run.assert_q08_source_authority()
    assert authority == {
        "stress_result_sha256": run.STRESS_RESULT_SHA,
        "stress_closure_sha256": run.STRESS_CLOSURE_SHA,
        "q08_contract_sha256": run.Q08_CONTRACT_SHA,
    }


def test_every_source_entry_point_revalidates_q08_authority() -> None:
    for fn in (run.prepare, run.prelaunch, run.smoke, run.acquire):
        source = inspect.getsource(fn)
        assert "assert_q08_source_authority()" in source


def test_prepare_records_successor_metric_repair() -> None:
    source = inspect.getsource(run.prepare)
    assert "unbiased exact-match-kernel MMD2 / collision U-statistic" in source
    assert 'contract["successor_mean_D_select_threshold"] = 0.20' in source
    assert 'contract["q08_transport_precondition_pass"] = True' in source


def test_wrapper_does_not_change_fresh4_source_geometry_or_provider() -> None:
    source = inspect.getsource(run)
    assert "base.DEFAULT" in source
    assert "base.prepare" in source
    assert "base.prelaunch" in source
    assert "base.smoke" in source
    assert "base.acquire" in source
    assert "mcp__c1output__submit_output" not in source
    assert "replacement" not in source
    assert "top_up" not in source
