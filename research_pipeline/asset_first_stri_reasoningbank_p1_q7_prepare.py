"""Freeze Q6 smoke hold and preregister Q7 bounded acknowledgement grace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, run_host, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import CONTRACT_SHA256
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_prepare import (
    CONTRACT as Q6_CONTRACT,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_runtime import (
    Q6_CONTRACT_SHA256,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q6_smoke import (
    SMOKE as Q6_SMOKE,
)

FAILED_SMOKE_SHA256 = "e09a6b47f649c9a22837ecac1f06ed497486e6f8617c1036c550c3f695742ae3"
FAILED_CONTAINER_ID = "479185720bd9"
DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q6-smoke-failure-differential-20260831.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q7-create-ack-grace-contract-20260831.json"


def prepare() -> dict[str, Any]:
    for path in (DIFFERENTIAL, CONTRACT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q7 preregistration: {path}")
    if sha256_file(Q6_SMOKE) != FAILED_SMOKE_SHA256:
        raise RuntimeError("Q6 smoke artifact drift")
    smoke = load_payload(Q6_SMOKE)
    if not (
        smoke["decision"] == "Q6_RUNTIME_AND_EVALUATOR_SMOKE_HOLD"
        and smoke["failure"]["message"]
        == "Q6 docker-create timeout had no inspectable side effect"
        and smoke["model_calls"] == smoke["provider_calls"] == 0
    ):
        raise RuntimeError("Q6 failure semantics drift")
    inspect = run_host(["docker", "inspect", FAILED_CONTAINER_ID], timeout=60, docker=True)
    if inspect["returncode"] != 0:
        raise RuntimeError("Q6 side effect unavailable for Q7 preregistration")
    record = json.loads(inspect["output"])[0]
    exact = (
        record["State"]["Status"] == "created"
        and record["State"]["Running"] is False
        and record["Config"]["Entrypoint"] == ["sleep"]
        and record["Config"]["Cmd"] == ["infinity"]
        and record["HostConfig"]["PidMode"] == "host"
    )
    if not exact:
        raise RuntimeError("Q6 delayed side effect is not exact")
    differential_sha = write_json(DIFFERENTIAL, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q6-SMOKE-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "q5_contract_sha256": CONTRACT_SHA256,
        "q6_contract_sha256": Q6_CONTRACT_SHA256,
        "q6_smoke_sha256": FAILED_SMOKE_SHA256,
        "failure_stage": "post-create exact-side-effect inspection acknowledgement",
        "docker_create_reissued": False,
        "evaluator_started": False,
        "source_patch_applied": False,
        "test_patch_applied": False,
        "model_calls": 0,
        "provider_calls": 0,
        "delayed_exact_side_effect": {
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
            "environment": False,
            "artifact_integrity": False,
            "primary_failure_class": "DOCKER_INSPECT_ACK_WINDOW_TOO_SHORT",
        },
        "scientific_belief_update": "none",
        "q5_replay_executed": False,
        "credential_material_present": False,
    })
    contract_sha = write_json(CONTRACT, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q7-CREATE-ACK-GRACE-20260831",
        "created_at_utc": utcnow(),
        "purpose": "Qualify a bounded read-only acknowledgement grace without reissuing docker create.",
        "bindings": {
            "q5_contract_sha256": CONTRACT_SHA256,
            "q6_contract_sha256": sha256_file(Q6_CONTRACT),
            "q6_failed_smoke_sha256": FAILED_SMOKE_SHA256,
            "q6_failure_differential_sha256": differential_sha,
        },
        "single_variable_repair": {
            "variable": "post-create exact-side-effect inspect timeout",
            "before_seconds": 30,
            "after_seconds": 180,
            "docker_create_reissued": False,
            "docker_create_command_unchanged": True,
            "exact_side_effect_predicate_unchanged": True,
            "evaluator_command_unchanged": True,
            "task_population_patches_parser_unchanged": True,
            "model_calls": 0,
            "provider_calls": 0,
        },
        "qualification": {
            "repeat_non_scientific_smoke": True,
            "all_Q5_S1_through_S6_checks_required": True,
            "Q6_S7_required": True,
            "task_success_not_required": True,
        },
        "authorization": {
            "q7_repair_implementation_authorized": True,
            "q7_smoke_execution_authorized": True,
            "q5_replay_execution_authorized": False,
            "full_p1_execution_authorized": False,
        },
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "scientific_belief_update": "none",
        "credential_material_present": False,
    })
    return {
        "decision": "P1_Q7_CREATE_ACK_GRACE_PREREGISTERED",
        "failure_differential_sha256": differential_sha,
        "contract_sha256": contract_sha,
        "q7_smoke_execution_authorized": True,
        "q5_replay_execution_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(prepare(), sort_keys=True))
