"""Freeze the failed Q5 smoke and preregister one Q6 runtime-receipt repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    DOCKER_HOST, ROOT, run_host, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import CONTRACT_SHA256
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_smoke import SMOKE
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload

FAILED_SMOKE_SHA256 = "0cbccd9edaeecb970727e6eeed6eef80c9c2ab046658831ec303a03bd3866345"
FAILED_CONTAINER_ID = "f5d084b4cd91"
DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-smoke-failure-differential-20260831.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q6-container-create-receipt-repair-contract-20260831.json"


def prepare() -> dict[str, Any]:
    for path in (DIFFERENTIAL, CONTRACT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q6 preregistration: {path}")
    if sha256_file(SMOKE) != FAILED_SMOKE_SHA256:
        raise RuntimeError("failed Q5 smoke artifact drift")
    smoke = load_payload(SMOKE)
    if not (
        smoke["decision"] == "Q5_EVALUATOR_VERBOSITY_SMOKE_HOLD"
        and smoke["failure"]["message"] == "docker create failed: "
        and smoke["model_calls"] == smoke["provider_calls"] == 0
    ):
        raise RuntimeError("Q5 smoke failure semantics drift")
    inspect = run_host(
        ["docker", "inspect", FAILED_CONTAINER_ID], timeout=30, docker=True
    )
    if inspect["returncode"] != 0:
        raise RuntimeError("failed Q5 smoke container receipt unavailable")
    record = json.loads(inspect["output"])[0]
    expected_image = (
        "docker.1ms.run/swebench/sweb.eval.x86_64.sphinx-doc_1776_sphinx-9230"
        "@sha256:036fb5014ef0054831e7218af5addb8957f527fe4a01bf6d4b6e1eebfdd4fca1"
    )
    side_effect_exact = (
        record["State"]["Status"] == "created"
        and record["State"]["Running"] is False
        and record["Config"]["Image"] == expected_image
        and record["Config"]["Entrypoint"] == ["sleep"]
        and record["Config"]["Cmd"] == ["infinity"]
        and record["HostConfig"]["PidMode"] == "host"
    )
    if not side_effect_exact:
        raise RuntimeError("failed docker-create side effect is not exact")

    differential_sha = write_json(DIFFERENTIAL, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-SMOKE-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "q5_contract_sha256": CONTRACT_SHA256,
        "q5_smoke_sha256": FAILED_SMOKE_SHA256,
        "failure_stage": "fresh container creation acknowledgement",
        "evaluator_started": False,
        "source_patch_applied": False,
        "test_patch_applied": False,
        "model_calls": 0,
        "provider_calls": 0,
        "failed_container_receipt": {
            "container_id": record["Id"],
            "name": record["Name"],
            "created": record["Created"],
            "state": record["State"],
            "image": record["Config"]["Image"],
            "entrypoint": record["Config"]["Entrypoint"],
            "cmd": record["Config"]["Cmd"],
            "pid_mode": record["HostConfig"]["PidMode"],
        },
        "classification": {
            "implementation_runtime": True,
            "provider": False,
            "parser": False,
            "evaluator": False,
            "base_state_normalization": False,
            "environment": False,
            "artifact_integrity": False,
            "treatment_invariant_failure": False,
            "genuine_non_implementation_issue": False,
            "primary_failure_class": "DOCKER_CREATE_ACK_TIMEOUT_WITH_EXACT_SIDE_EFFECT",
        },
        "scientific_belief_update": "none",
        "q5_replay_executed": False,
        "q5_execution_authorized": False,
        "credential_material_present": False,
    })
    contract_sha = write_json(CONTRACT, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q6-CONTAINER-CREATE-RECEIPT-REPAIR-20260831",
        "created_at_utc": utcnow(),
        "purpose": (
            "Prospectively repair only Docker create acknowledgement reconciliation "
            "before repeating a non-scientific evaluator-interface smoke."
        ),
        "bindings": {
            "q5_contract_sha256": CONTRACT_SHA256,
            "q5_failed_smoke_sha256": FAILED_SMOKE_SHA256,
            "q5_smoke_failure_differential_sha256": differential_sha,
        },
        "single_variable_repair": {
            "variable": "Docker create acknowledgement reconciliation",
            "before": (
                "any nonzero/timeout docker-create receipt raises even when the exact "
                "unique container side effect exists"
            ),
            "after": (
                "on docker-create timeout only, inspect the unique generated name and "
                "accept only an exact Created container with frozen image, sleep "
                "entrypoint, infinity command, and host PID mode"
            ),
            "docker_create_command_unchanged": True,
            "evaluator_command_unchanged_from_q5": True,
            "sphinx_reporting_repair_unchanged": True,
            "task_population_unchanged": True,
            "patches_unchanged": True,
            "parser_unchanged": True,
            "model_calls": 0,
            "provider_calls": 0,
        },
        "qualification": {
            "repeat_non_scientific_smoke": True,
            "same_smoke_test": "tests/test_domain_py.py::test_function_signatures",
            "same_repaired_command": (
                "tox --current-env -epy39 -v -- -rA "
                "tests/test_domain_py.py::test_function_signatures"
            ),
            "all_Q5_S1_through_S6_checks_required": True,
            "reconciled_create_receipt_required": True,
            "task_success_not_required": True,
        },
        "authorization": {
            "q6_repair_implementation_authorized": True,
            "q6_smoke_execution_authorized": True,
            "q5_replay_execution_authorized": False,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "scientific_belief_update": "none",
        "credential_material_present": False,
    })
    return {
        "decision": "P1_Q6_CONTAINER_CREATE_RECEIPT_REPAIR_PREREGISTERED",
        "failure_differential_sha256": differential_sha,
        "contract_sha256": contract_sha,
        "q6_smoke_execution_authorized": True,
        "q5_replay_execution_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(prepare(), sort_keys=True))
