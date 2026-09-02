from __future__ import annotations

import json

from research_pipeline import asset_first_stri_reasoningbank_p1_core as p1_core
from research_pipeline import asset_first_stri_swebench_oci_import as oci
from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_d0_qualify as d0
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_rootful_runtime import (
    CONTRACT,
    CONTRACT_SHA256,
    ROOTFUL_DOCKER_HOST,
    activate,
    verify_contract,
)


def test_rootful_repair_contract_is_exact_and_single_variable() -> None:
    assert p1_core.sha256_file(CONTRACT) == CONTRACT_SHA256
    doc = verify_contract()
    assert doc["decision"] == "D0_ROOTFUL_DOCKER_RUNTIME_REPAIR_PREREGISTERED"
    assert doc["trigger"]["ordinal"] == 117
    assert doc["trigger"]["instance_id"] == "matplotlib__matplotlib-24026"
    assert doc["trigger"]["qualification_attempt_consumed"] is False
    assert doc["single_variable_repair"]["before"].endswith("e1-reasoningbank-docker.sock")
    assert doc["single_variable_repair"]["after"] == ROOTFUL_DOCKER_HOST
    assert doc["single_variable_repair"]["model_calls"] == 0
    assert doc["single_variable_repair"]["provider_calls"] == 0


def test_activate_scopes_d0_helpers_to_rootful_daemon(monkeypatch) -> None:
    old_core = p1_core.DOCKER_HOST
    old_oci = oci.DOCKER_HOST
    try:
        receipt = activate()
        assert receipt["docker_host"] == ROOTFUL_DOCKER_HOST
        assert p1_core.DOCKER_HOST == ROOTFUL_DOCKER_HOST
        assert oci.DOCKER_HOST == ROOTFUL_DOCKER_HOST
    finally:
        p1_core.DOCKER_HOST = old_core
        oci.DOCKER_HOST = old_oci


def test_live_parent_index_records_terminal_four_repo_qualification() -> None:
    doc = json.loads(d0.INDEX.read_text(encoding="utf-8"))
    assert doc["completed_qualification_count"] == 91
    assert doc["execution_complete"] is True
    assert doc["decision"] == "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS"
    assert doc["operational_blocker"] is None
    assert doc["selected_repositories"] == [
        "pydata/xarray",
        "sympy/sympy",
        "matplotlib/matplotlib",
        "django/django",
    ]
    state = {row["repo"]: row for row in doc["repository_state"]}
    for repo in doc["selected_repositories"]:
        assert state[repo]["qualified_count"] == d0.MIN_QUALIFIED_PER_REPO
        assert state[repo]["eligibility"] == "ELIGIBLE"
    schedule = d0.candidate_schedule()
    completed = d0.existing_receipts(schedule)
    assert len(completed) == 91
    assert d0.next_unit(schedule, completed) is None


def test_index_payload_binds_runtime_repair_without_changing_attempts() -> None:
    schedule = d0.candidate_schedule()
    completed = d0.existing_receipts(schedule)
    payload = d0.index_payload(schedule, completed)
    assert payload["runtime_repair"]["contract_sha256"] == CONTRACT_SHA256
    assert payload["runtime_repair"]["docker_host_for_new_units"] == ROOTFUL_DOCKER_HOST
    assert payload["checks"]["every_attempt_count_one"] is True
    assert payload["checks"]["no_model_calls"] is True
    assert payload["checks"]["no_provider_calls"] is True
