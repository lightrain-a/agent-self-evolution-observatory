"""Freeze Q7 smoke hold and preregister Q8 Docker-start acknowledgement grace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import ROOT, sha256_file, utcnow, write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import CONTRACT_SHA256
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload
from research_pipeline.asset_first_stri_reasoningbank_p1_q7_prepare import CONTRACT as Q7_CONTRACT
from research_pipeline.asset_first_stri_reasoningbank_p1_q7_runtime import Q7_CONTRACT_SHA256
from research_pipeline.asset_first_stri_reasoningbank_p1_q7_smoke import SMOKE as Q7_SMOKE

FAILED_SMOKE_SHA256 = "6b3eb6f8cdad4d8f511ca74e11eff3d26dfdf28247a6b7cc282ca81f3e63f2f7"
DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q7-smoke-failure-differential-20260831.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q8-start-ack-grace-contract-20260831.json"


def prepare() -> dict[str, Any]:
    for path in (DIFFERENTIAL, CONTRACT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q8 preregistration: {path}")
    if sha256_file(Q7_SMOKE) != FAILED_SMOKE_SHA256:
        raise RuntimeError("Q7 smoke drift")
    smoke = load_payload(Q7_SMOKE)
    if smoke["failure"]["message"] != "docker start failed: ":
        raise RuntimeError("Q7 failure semantics drift")
    differential_sha = write_json(DIFFERENTIAL, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q7-SMOKE-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "q5_contract_sha256": CONTRACT_SHA256,
        "q7_contract_sha256": Q7_CONTRACT_SHA256,
        "q7_smoke_sha256": FAILED_SMOKE_SHA256,
        "failure_stage": "docker start acknowledgement",
        "observed_daemon_event_order": ["create", "start", "kill", "die", "destroy"],
        "start_side_effect_observed": True,
        "evaluator_started": False,
        "source_patch_applied": False,
        "test_patch_applied": False,
        "model_calls": 0,
        "provider_calls": 0,
        "classification": {
            "implementation_runtime": True,
            "primary_failure_class": "DOCKER_START_ACK_WINDOW_TOO_SHORT",
        },
        "scientific_belief_update": "none",
        "credential_material_present": False,
    })
    contract_sha = write_json(CONTRACT, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q8-START-ACK-GRACE-20260831",
        "created_at_utc": utcnow(),
        "bindings": {
            "q5_contract_sha256": CONTRACT_SHA256,
            "q7_contract_sha256": sha256_file(Q7_CONTRACT),
            "q7_failed_smoke_sha256": FAILED_SMOKE_SHA256,
            "q7_failure_differential_sha256": differential_sha,
        },
        "single_variable_repair": {
            "variable": "docker start acknowledgement timeout",
            "before_seconds": 60,
            "after_seconds": 180,
            "docker_create_and_inspect_unchanged": True,
            "evaluator_command_unchanged": True,
            "task_population_patches_parser_unchanged": True,
            "model_calls": 0,
            "provider_calls": 0,
        },
        "qualification": {
            "repeat_non_scientific_smoke": True,
            "all_Q5_S1_through_S6_and_runtime_checks_required": True,
            "task_success_not_required": True,
        },
        "authorization": {
            "q8_repair_implementation_authorized": True,
            "q8_smoke_execution_authorized": True,
            "q5_replay_execution_authorized": False,
            "full_p1_execution_authorized": False,
        },
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "scientific_belief_update": "none",
        "credential_material_present": False,
    })
    return {
        "decision": "P1_Q8_START_ACK_GRACE_PREREGISTERED",
        "failure_differential_sha256": differential_sha,
        "contract_sha256": contract_sha,
        "q8_smoke_execution_authorized": True,
        "q5_replay_execution_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(prepare(), sort_keys=True))
