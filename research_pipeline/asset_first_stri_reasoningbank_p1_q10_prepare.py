"""Freeze Q10 Docker-start daemon-state reconciliation before replay."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CONTRACT as Q5_CONTRACT, load_payload,
)

Q4_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-index-20260830.json"
Q5_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-index-20260831.json"
Q5_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-adjudication-20260831.json"
Q5_MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-artifact-manifest-20260831.json"
Q5_DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-failure-differential-20260831.json"
Q9_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q9-start-ack-grace-contract-20260831.json"
Q9_SMOKE = ROOT / "generated/asset-first-stri-reasoningbank-p1-q9-evaluator-verbosity-smoke-20260831.json"
Q9_AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q9-q5-replay-execution-authority-20260831.json"
SCIENTIFIC_MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-q3-q4-q5-scientific-memory-20260831.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-docker-start-reconciliation-contract-20260831.json"

EXPECTED_HASHES = {
    Q4_INDEX: "f6ce4e4a345fa8e105ddca934faa1c85af14b039497768ebef1bd0222409a0bf",
    Q5_CONTRACT: "972aab1ce256a759fc20e5762ab4ef05254e8abdbdb65f9c417c8eef7f30700f",
    Q5_INDEX: "16e188146e651c13cd41c9b97ceffff5f29b5937928894bfbfb4e136204c777e",
    Q5_ADJUDICATION: "39721690bdcfea975681494d791e0e99146a2e926321ae2ca96a3b6a7fa0b8d0",
    Q5_MANIFEST: "27ab58ee8966c99f659db914a592dbf1e7075c2d05970249fadb302b9c1e777c",
    Q5_DIFFERENTIAL: "0590bfebfda68889684a4d270b686a72eefb23b39d80db6ecf288e34e69ff503",
    Q9_CONTRACT: "5779bd037811c6446610eb31b6b7f73f8110993f5ad0f112902523477ee0158b",
    Q9_SMOKE: "50685527c8fbef42e242a285d2f12f484ed17cedde9a6916c5ca6bd04a74087a",
    Q9_AUTHORITY: "56023442130efd367279d09d87eb208500ce20703a8e73f7c4dba049f77f767e",
    SCIENTIFIC_MEMORY: "6a33edff017b283f464d5340514cad91cd4a0e1fcb17c92c3d2849507a02a687",
}
EXPECTED_ORDER = [
    *[(5, "sphinx-doc__sphinx-9230", arm) for arm in "ABCDE"],
    *[(6, "django__django-11880", arm) for arm in "ABCDE"],
]


def verify_history() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256_file(path)
        checks[str(path.relative_to(ROOT))] = {
            "expected": expected, "actual": actual, "pass": actual == expected,
        }
    q4 = load_payload(Q4_INDEX)
    q5 = load_payload(Q5_INDEX)
    adjudication = load_payload(Q5_ADJUDICATION)
    q9 = load_payload(Q9_AUTHORITY)
    order = [
        (row["selection_rank"], row["instance_id"], row["arm"])
        for row in q5["completed_runs"]
    ]
    journal_order = [
        (row["selection_rank"], row["instance_id"], row["arm"])
        for row in q5["run_journal"]
    ]
    checks["q4_q5_immutable_terminal_history"] = {"pass": bool(
        q4["execution_complete"] is True
        and q5["execution_complete"] is True
        and len(q5["completed_runs"]) == len(q5["run_journal"]) == 10
        and order == journal_order == EXPECTED_ORDER
        and all(row["attempt_count"] == 1 for row in q5["completed_runs"])
        and all(row["attempt_count"] == 1 and row["status"] == "persisted"
                for row in q5["run_journal"])
        and q5["automatic_retry"] == q5["replacement_sampling"] == "forbidden"
    )}
    checks["q5_hold_preserved"] = {"pass": bool(
        adjudication["decision"] == "P1_Q5_EVALUATOR_REPAIR_UNQUALIFIED_FULL_P1_HOLD"
        and adjudication["implementation_qualified"] is False
        and adjudication["authorization"]["full_p1_execution_authorized"] is False
        and adjudication["scientific_boundary"]["scientific_belief_update"] == "none"
    )}
    checks["q9_history_preserved"] = {"pass": bool(
        q9["decision"] == "P1_Q9_RUNTIME_AND_EVALUATOR_QUALIFIED_Q5_REPLAY_AUTHORIZED"
        and q9["q5_replay_execution_authorized"] is True
        and q9["full_p1_execution_authorized"] is False
        and q9["model_calls"] == q9["provider_calls"] == 0
    )}
    if not all(row["pass"] for row in checks.values()):
        raise RuntimeError("Q10 preregistration history verification failed")
    return checks


def prepare(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q10 contract: {output}")
    verification = verify_history()
    q5_contract = load_payload(Q5_CONTRACT)
    sources = copy.deepcopy(q5_contract["frozen_replay_sources"])
    order = [
        (row["selection_rank"], row["instance_id"], row["arm"]) for row in sources
    ]
    if order != EXPECTED_ORDER or len(sources) != 10:
        raise RuntimeError("Q10 frozen source order drift")
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q10-RUNTIME-RECONCILIATION-20260831",
        "created_at_utc": utcnow(),
        "decision": "P1_Q10_DOCKER_START_DAEMON_RECONCILIATION_PREREGISTERED",
        "qualification_scope": "prospective implementation/runtime qualification only",
        "single_changed_variable": {
            "variable": "Docker start acknowledgement acceptance rule",
            "before": "client acknowledgement required",
            "after": (
                "client acknowledgement OR exact daemon-side running-state proof "
                "after an ambiguous client timeout"
            ),
            "timeout_duration_changed": False,
            "scientific_treatment_changed": False,
        },
        "reconciliation_trigger": {
            "allowed": [
                "timed_out == true",
                "returncode is None after timeout",
                "equivalent empty acknowledgement produced by the exact wrapper",
            ],
            "explicit_non_timeout_errors_remain_hard_failures": True,
            "substantive_nonzero_output_remains_hard_failure": True,
        },
        "exact_running_state_proof": {
            "container_name_exact": True,
            "container_id_matches_create_receipt": True,
            "image_exact": True,
            "image_digest_exact": True,
            "config_image_exact": True,
            "entrypoint_exact": ["sleep"],
            "cmd_exact": ["infinity"],
            "pid_namespace_exact": "host",
            "state_status_exact": "running",
            "state_running": True,
            "state_pid_positive": True,
            "state_dead": False,
            "state_restarting": False,
            "restart_count": 0,
            "no_substitute_container": True,
            "fail_closed": True,
        },
        "exactly_once_invariants": {
            "client_start_invocations": 1,
            "second_start_forbidden": True,
            "automatic_retry": "forbidden",
            "replacement_sampling": "forbidden",
            "attempt_count": 1,
        },
        "cleanup_order": [
            "create",
            "start exactly once",
            "reconcile ambiguous acknowledgement before cleanup",
            "persist finalized receipt",
            "continue or HOLD",
            "cleanup and persist cleanup receipt",
        ],
        "fault_test_gate": [
            "T1 normal success",
            "T2 timeout exact running accepted",
            "T3 timeout created HOLD",
            "T4 timeout exited HOLD",
            "T5 timeout restarting HOLD",
            "T6 wrong identity HOLD",
            "T7 wrong image/pid/command HOLD",
            "T8 explicit error hard failure without reconciliation",
            "T9 inspect timeout HOLD",
            "T10 cleanup after finalized receipt",
        ],
        "frozen_replay_sources": sources,
        "planned_order": [list(row) for row in EXPECTED_ORDER],
        "planned_run_count": 10,
        "frozen_inputs": {
            "same_q4_q5_patches": True,
            "same_task_ids": True,
            "same_arms": ["A", "B", "C", "D", "E"],
            "same_images_and_digests": True,
            "same_base_commits": True,
            "same_evaluator_scripts": True,
            "same_sphinx_rA_repair": True,
            "same_official_swebench_5_0_2_parser": True,
            "same_django_evaluator": True,
            "model_calls": 0,
            "provider_calls": 0,
        },
        "bindings": {
            str(path.relative_to(ROOT)): sha256_file(path)
            for path in EXPECTED_HASHES
        },
        "history_verification": verification,
        "pass_criteria": {
            "all_ten_implementation_valid": True,
            "exactly_once_order_and_persistence": True,
            "all_start_invocation_counts_one": True,
            "all_second_start_invoked_false": True,
            "all_parser_maps_valid_and_exact": True,
            "task_success_used_for_qualification": False,
        },
        "failure_stop_rule": (
            "If exact daemon-state reconciliation cannot qualify Q10, freeze Q10 and "
            "reclassify the competing layer as execution substrate / Docker daemon "
            "transport instability; do not extend timeout or retry."
        ),
        "authorization": {
            "q10_implementation_authorized": True,
            "q10_live_smoke_authorized": True,
            "q10_replay_execution_authorized": False,
            "full_p1_preregistration_authorized": False,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "scientific_boundary": {
            "scientific_belief_update": "none",
            "mechanism_claim_authorized": False,
            "task_outcomes_descriptive_only": True,
            "q4_q5_reclassified": False,
        },
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {"decision": payload["decision"], "file_sha256": file_sha}


def main() -> None:
    print(json.dumps(prepare(), sort_keys=True))


if __name__ == "__main__":
    main()
