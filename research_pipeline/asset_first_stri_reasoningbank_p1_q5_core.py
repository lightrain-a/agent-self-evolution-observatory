"""Frozen Q5 evaluator-replay primitives; this module has no provider/model path."""

from __future__ import annotations

import base64
import copy
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, sha256_text,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import (
    evaluate, parse_django, parse_pytest_v2,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_parser_qualification import (
    WHEEL_SHA256, load_official,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CONTRACT, FIXTURES, Q4_ADJUDICATION, Q4_INDEX, SPHINX_AFTER, SPHINX_BEFORE,
    load_payload,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q9_runtime import (
    ExtendedStartGraceDockerRun,
)

CONTRACT_SHA256 = "972aab1ce256a759fc20e5762ab4ef05254e8abdbdb65f9c417c8eef7f30700f"
ARMS = ("A", "B", "C", "D", "E")
EXPECTED_ORDER = [
    *[(5, "sphinx-doc__sphinx-9230", arm) for arm in ARMS],
    *[(6, "django__django-11880", arm) for arm in ARMS],
]


def verify_q5_contract() -> dict[str, Any]:
    if sha256_file(CONTRACT) != CONTRACT_SHA256:
        raise RuntimeError("Q5 contract SHA-256 drift")
    contract = load_payload(CONTRACT)
    auth = contract["authorization"]
    repair = contract["single_variable_repair"]
    if not (
        auth["q5_replay_runner_implementation_authorized"] is True
        and auth["q5_replay_execution_authorized"] is False
        and repair["before"] == SPHINX_BEFORE
        and repair["after"] == SPHINX_AFTER
        and repair["model_calls"] == repair["provider_calls"] == 0
        and len(contract["frozen_replay_sources"]) == 10
    ):
        raise RuntimeError("Q5 contract semantic drift")
    actual_order = [
        (r["selection_rank"], r["instance_id"], r["arm"])
        for r in contract["frozen_replay_sources"]
    ]
    if actual_order != EXPECTED_ORDER:
        raise RuntimeError("Q5 replay order drift")
    q4_index = load_payload(Q4_INDEX)
    q4_by_id = {r["run_id"]: r for r in q4_index["completed_runs"]}
    source_checks = []
    for row in contract["frozen_replay_sources"]:
        receipt = q4_by_id.get(row["source_run_id"])
        source_path = ROOT / row["source_run_path"]
        actual = sha256_file(source_path)
        passed = bool(
            receipt
            and receipt["file_sha256"] == row["source_run_sha256"] == actual
            and sha256_text(load_payload(source_path)["result"])
            == row["source_patch_sha256"]
        )
        source_checks.append({
            "source_run_id": row["source_run_id"],
            "expected_sha256": row["source_run_sha256"],
            "actual_sha256": actual,
            "pass": passed,
        })
    if not all(r["pass"] for r in source_checks):
        raise RuntimeError("Q4 replay-source artifact drift")
    return {
        "contract_sha256": CONTRACT_SHA256,
        "q4_index_sha256": sha256_file(Q4_INDEX),
        "q4_adjudication_sha256": sha256_file(Q4_ADJUDICATION),
        "official_swebench_wheel_sha256": WHEEL_SHA256,
        "source_checks": source_checks,
        "pass": True,
    }


def fixture_by_id() -> dict[str, dict[str, Any]]:
    return {row["instance_id"]: row for row in load_payload(FIXTURES)["fixtures"]}


def repaired_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(fixture)
    script = result["evaluator_only"]["eval_script"]
    if fixture["instance_id"] == "sphinx-doc__sphinx-9230":
        if script.count(SPHINX_BEFORE) != 1:
            raise RuntimeError("Sphinx preregistered command not found exactly once")
        result["evaluator_only"]["eval_script"] = script.replace(
            SPHINX_BEFORE, SPHINX_AFTER
        )
    elif fixture["instance_id"] != "django__django-11880":
        raise RuntimeError("unexpected Q5 task")
    return result


def sliced_output(raw: str) -> str:
    start, end = ">>>>> Start Test Output", ">>>>> End Test Output"
    if start not in raw or end not in raw:
        return raw
    return raw.split(start, 1)[1].split(end, 1)[0]


def official_and_local_maps(
    parser_name: str, raw: str,
) -> tuple[dict[str, str], dict[str, str]]:
    official, _ = load_official()
    sliced = sliced_output(raw)
    if parser_name == "parse_log_sphinx":
        return official["parse_log_pytest_v2"](sliced, None), parse_pytest_v2(sliced)
    if parser_name == "parse_log_django":
        return official["parse_log_django"](sliced, None), parse_django(sliced)
    raise RuntimeError(f"unsupported Q5 parser {parser_name}")


def image_digest_visible(start: dict[str, Any], expected: str) -> bool:
    return expected in (start.get("image_inspect") or {}).get("output", "")


def apply_patch(container: ExtendedStartGraceDockerRun, patch: str) -> dict[str, Any]:
    encoded = base64.b64encode(patch.encode("utf-8")).decode("ascii")
    return container.exec(
        f"printf %s {encoded} | base64 -d | git apply --binary -", timeout=60
    )


def replay_one(
    source: dict[str, Any], fixture: dict[str, Any], run_id: str,
) -> dict[str, Any]:
    source_path = ROOT / source["source_run_path"]
    if sha256_file(source_path) != source["source_run_sha256"]:
        raise RuntimeError("source run SHA drift")
    q4 = load_payload(source_path)
    patch = q4["result"]
    if sha256_text(patch) != source["source_patch_sha256"]:
        raise RuntimeError("source patch SHA drift")
    if q4["task_sha256"] != source["task_sha256"]:
        raise RuntimeError("source task SHA drift")
    if fixture["image_amd64_manifest_digest"] != source["image_amd64_manifest_digest"]:
        raise RuntimeError("image digest drift")
    if fixture["model_visible"]["base_commit"] != source["base_commit"]:
        raise RuntimeError("base commit drift")
    repaired = repaired_fixture(fixture)
    original_script = fixture["evaluator_only"]["eval_script"]
    repaired_script = repaired["evaluator_only"]["eval_script"]
    container = ExtendedStartGraceDockerRun(
        fixture["image_pull_reference"], source["base_commit"], run_id, exact_base=True
    )
    try:
        start = container.start()
        application = apply_patch(container, patch)
        if application["returncode"] != 0 or application["timed_out"]:
            raise RuntimeError("frozen Q4 result patch application failed")
        applied = container.exec("git -c core.fileMode=false diff --binary HEAD", timeout=60)
        if applied["returncode"] != 0 or sha256_text(applied["output"]) != sha256_text(patch):
            raise RuntimeError("applied Q4 patch differs from frozen patch")
        outcome = evaluate(container, repaired)
        official, local = official_and_local_maps(
            fixture["evaluator_only"]["log_parser"],
            outcome["raw_execution"]["output"],
        )
        expected = fixture["evaluator_only"]["FAIL_TO_PASS"] + fixture["evaluator_only"]["PASS_TO_PASS"]
        coverage = {case: official.get(case, "MISSING") for case in expected}
        checks = {
            "source_run_sha_exact": True,
            "source_patch_sha_exact": True,
            "task_fixture_sha_exact": sha256_file(FIXTURES)
            == load_payload(CONTRACT)["bindings"]["fixtures_sha256"],
            "image_digest_exact": image_digest_visible(
                start, source["image_amd64_manifest_digest"]
            ),
            "base_commit_exact": (
                start["base_commit_receipt"]["observed_head"] == source["base_commit"]
                and start["base_commit_receipt"]["rule"]
                == "exact_base_after_preregistered_hard_reset"
            ),
            "patch_applied_exactly": True,
            "test_patch_sha_exact": outcome["test_patch_sha256"]
            == sha256_text(fixture["evaluator_only"]["test_patch"]),
            "official_status_map_nonempty": len(official) > 0,
            "official_local_parser_exact": official == local == outcome["status_map"],
            "required_case_coverage_sufficient": all(v != "MISSING" for v in coverage.values()),
            "evaluator_terminated": (
                not outcome["raw_execution"]["timed_out"]
                and outcome["raw_execution"]["returncode"] == 0
            ),
            "command_change_exact": (
                repaired_script == original_script.replace(SPHINX_BEFORE, SPHINX_AFTER)
                if fixture["instance_id"] == "sphinx-doc__sphinx-9230"
                else repaired_script == original_script
            ),
            "model_provider_calls_zero": True,
        }
        return {
            "schema_version": 1,
            "run_id": run_id,
            "instance_id": source["instance_id"],
            "arm": source["arm"],
            "selection_rank": source["selection_rank"],
            "source_q4": copy.deepcopy(source),
            "source_patch_sha256": sha256_text(patch),
            "fixture_sha256": sha256_file(FIXTURES),
            "image": fixture["image_pull_reference"],
            "image_digest": source["image_amd64_manifest_digest"],
            "base_commit": source["base_commit"],
            "runtime_start": start,
            "patch_application": application,
            "applied_patch_sha256": sha256_text(applied["output"]),
            "original_eval_script_sha256": sha256_text(original_script),
            "repaired_eval_script_sha256": sha256_text(repaired_script),
            "official_parser_status_map": official,
            "local_parser_status_map": local,
            "required_case_status": coverage,
            "R4_terminal_outcome": outcome,
            "implementation_checks": checks,
            "implementation_valid": all(checks.values()),
            "resolved": outcome["resolved"],
            "task_outcome_affects_qualification": False,
            "attempt_count": 1,
            "model_calls": 0,
            "provider_calls": 0,
            "credential_material_present": False,
        }
    finally:
        container.close()
