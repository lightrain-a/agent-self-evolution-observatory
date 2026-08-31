"""Exactly-once Full-P1 behavioral runner using the Q10 reconciled runtime."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline import asset_first_stri_reasoningbank_p1_core as core
from research_pipeline import asset_first_stri_reasoningbank_p1_eval as evaluation
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    MODEL,
    ROOT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)

POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
PREREGISTRATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
ACQUISITION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-result-20260831.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-execution-authority-20260831.json"
RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runs-20260831"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-index-20260831.json"
EXPECTED_POPULATION_SHA256 = "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8"
EXPECTED_PREREGISTRATION_SHA256 = "af8e9efb53ad5df5e846329b289ce791bc8ffe7c581f810c0ade1067d09fe7dd"
EXPECTED_TREATMENTS_SHA256 = "35b5f8dab0606ca930a237a6248c9b0aac8a5b6f5564e3ba57217a34dfd92ad7"
ARMS = ("A", "B", "C", "D", "E")
_ACTIVE_CONTAINERS: dict[str, "FullP1DockerRun"] = {}


class FullP1DockerRun(DaemonReconciledDockerRun):
    """Adapter preserving the frozen agent API while binding the image digest."""

    def __init__(
        self,
        image: str,
        base_commit: str,
        run_id: str,
        exact_base: bool = False,
    ) -> None:
        if "@sha256:" not in image:
            raise RuntimeError("Full-P1 image reference is not digest-bound")
        expected_digest = image.rsplit("@", 1)[1]
        super().__init__(
            image=image,
            base_commit=base_commit,
            run_id=run_id,
            expected_image_digest=expected_digest,
            exact_base=exact_base,
        )
        _ACTIVE_CONTAINERS[run_id] = self


def load_document(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_inputs() -> dict[str, Any]:
    fixed = {
        "population": (POPULATION, EXPECTED_POPULATION_SHA256),
        "preregistration": (PREREGISTRATION, EXPECTED_PREREGISTRATION_SHA256),
        "treatments": (TREATMENTS, EXPECTED_TREATMENTS_SHA256),
    }
    checks: dict[str, Any] = {}
    for label, (path, expected) in fixed.items():
        actual = sha256_file(path)
        checks[label] = {"path": str(path.relative_to(ROOT)), "expected": expected, "actual": actual, "pass": actual == expected}
    acquisition = load_document(ACQUISITION)
    authority = load_document(AUTHORITY)
    checks["acquisition"] = {
        "path": str(ACQUISITION.relative_to(ROOT)),
        "actual": sha256_file(ACQUISITION),
        "pass": (
            acquisition["decision"] == "FULL_P1_EXACT_IMAGES_READY"
            and acquisition["all_blobs_sha256_verified"] is True
            and acquisition["all_images_imported_by_exact_digest"] is True
            and acquisition["scientific_boundary"]["task_outcomes_observed"] is False
        ),
    }
    checks["authority"] = {
        "path": str(AUTHORITY.relative_to(ROOT)),
        "actual": sha256_file(AUTHORITY),
        "pass": (
            authority["decision"] == "FULL_P1_BEHAVIORAL_EXECUTION_AUTHORIZED"
            and authority["execution_authorized"] is True
            and authority["bindings"]["preregistration_sha256"] == EXPECTED_PREREGISTRATION_SHA256
            and authority["bindings"]["acquisition_sha256"] == sha256_file(ACQUISITION)
        ),
    }
    if not all(row["pass"] for row in checks.values()):
        raise RuntimeError("Full-P1 frozen-input/execution-authority gate failed")
    return checks


def population() -> list[dict[str, Any]]:
    rows = load_document(POPULATION)["population"]
    if [row["selection_rank"] for row in rows] != [7, 8, 9, 11, 12, 13, 14, 19]:
        raise RuntimeError("Full-P1 population order drift")
    return rows


def execute_with_q10(
    fixture: dict[str, Any],
    *,
    selected_memory: str,
    run_id: str,
) -> tuple[dict[str, Any], FullP1DockerRun]:
    original = core.DockerRun
    core.DockerRun = FullP1DockerRun
    try:
        trajectory, container = core.execute_agent(
            fixture,
            selected_memory=selected_memory,
            run_id=run_id,
            exact_base=True,
        )
    finally:
        core.DockerRun = original
    if not isinstance(container, FullP1DockerRun):
        raise RuntimeError("Full-P1 runtime adapter was not used")
    return trajectory, container


def run_case(
    fixture: dict[str, Any],
    *,
    arm: str,
    treatment: dict[str, Any],
    run_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    container: FullP1DockerRun | None = None
    trajectory: dict[str, Any]
    try:
        trajectory, container = execute_with_q10(
            fixture,
            selected_memory=treatment["selected_memory"],
            run_id=run_id,
        )
        trajectory["R0_representation_retrieval_state"] = copy.deepcopy(treatment["R0"])
        trajectory["R1_exact_model_visible_request_sha256"] = sha256_text(
            canonical_json(trajectory["R1_model_visible_requests"])
        )
        trajectory["R2_first_behavior_action"] = trajectory.get(
            "R2_first_behavioral_decision"
        )
        trajectory["R3_complete_trajectory_sha256"] = sha256_text(
            canonical_json({
                "actions": trajectory.get("R3_actions", []),
                "patch_and_status": trajectory.get("patch_and_status"),
                "exit_status": trajectory.get("exit_status"),
            })
        )
        trajectory["R4_terminal_outcome"] = evaluation.evaluate(container, fixture)
        trajectory["execution_status"] = "TERMINAL_PERSISTED"
        trajectory["failure_classification"] = trajectory.get("failure")
        trajectory["scientific_boundary"] = {
            "gold_patch_model_visible": False,
            "test_patch_model_visible": False,
            "evaluator_script_model_visible": False,
            "R2_R3_requires_R4_difference": False,
        }
    except Exception as error:
        container = container or _ACTIVE_CONTAINERS.get(run_id)
        start_receipt = (
            copy.deepcopy(container.start_reconciliation_receipt)
            if container is not None
            else None
        )
        trajectory = {
            "schema_version": 1,
            "run_id": run_id,
            "created_at_utc": utcnow(),
            "instance_id": fixture["instance_id"],
            "R0_representation_retrieval_state": copy.deepcopy(treatment["R0"]),
            "R1_exact_model_visible_request_sha256": None,
            "R2_first_behavior_action": None,
            "R3_complete_trajectory_sha256": None,
            "R4_terminal_outcome": None,
            "execution_status": "TERMINAL_IMPLEMENTATION_OR_SUBSTRATE_FAILURE",
            "failure": {
                "failure_layer": "runtime_or_execution",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            "failure_classification": {
                "classification_pending_adjudication": True,
                "error_type": type(error).__name__,
            },
            "q10_start_reconciliation_on_failure": start_receipt,
            "scientific_outcome_authorized": False,
            "credential_material_present": False,
        }
    finally:
        cleanup = container.close() if container is not None else {
            "cleanup_invoked": False,
            "accepted": True,
            "reason": "no container side effect obtained",
        }
        _ACTIVE_CONTAINERS.pop(run_id, None)

    trajectory.update({
        "selection_rank": fixture["selection_rank"],
        "arm": arm,
        "attempt_count": 1,
        "model_visible_task_sha256": fixture["model_visible_task_sha256"],
        "evaluator_fixture_sha256": fixture["evaluator_fixture_sha256"],
        "image_amd64_manifest_digest": fixture["image_amd64_manifest_digest"],
        "selected_memory_sha256": treatment["R0"]["selected_memory_sha256"],
        "treatment_sha256": treatment["treatment_sha256"],
        "docker_cleanup_receipt": cleanup,
        "credential_material_present": False,
    })
    out_path = output_dir / run_id / "run.json"
    file_sha = write_json(out_path, trajectory)
    return {
        "run_id": run_id,
        "instance_id": fixture["instance_id"],
        "selection_rank": fixture["selection_rank"],
        "arm": arm,
        "attempt_count": 1,
        "path": str(out_path.relative_to(ROOT)),
        "file_sha256": file_sha,
        "execution_status": trajectory["execution_status"],
        "exit_status": trajectory.get("exit_status"),
        "resolved": (trajectory.get("R4_terminal_outcome") or {}).get("resolved"),
        "evaluator_valid": (trajectory.get("R4_terminal_outcome") or {}).get("valid"),
        "failure": trajectory.get("failure"),
        "model_calls": (trajectory.get("resource_accounting") or {}).get("model_calls", 0),
    }


def planned_units() -> list[dict[str, Any]]:
    treatments = load_document(TREATMENTS)["arms"]
    return [
        {
            "ordinal": ordinal,
            "selection_rank": fixture["selection_rank"],
            "instance_id": fixture["instance_id"],
            "arm": arm,
            "run_id": f"full-p1-{fixture['instance_id']}-{arm}",
            "attempt_count": 1,
            "model_visible_task_sha256": fixture["model_visible_task_sha256"],
            "evaluator_fixture_sha256": fixture["evaluator_fixture_sha256"],
            "image_amd64_manifest_digest": fixture["image_amd64_manifest_digest"],
            "selected_memory_sha256": treatments[arm]["R0"]["selected_memory_sha256"],
            "treatment_sha256": treatments[arm]["treatment_sha256"],
        }
        for ordinal, (fixture, arm) in enumerate(
            ((fixture, arm) for fixture in population() for arm in ARMS),
            start=1,
        )
    ]


def index_payload(
    *,
    verification: dict[str, Any],
    journal: list[dict[str, Any]],
    completed: list[dict[str, Any]],
    execution_complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-BEHAVIORAL-PROPAGATION-20260831",
        "created_at_utc": utcnow(),
        "model": MODEL,
        "preregistration": str(PREREGISTRATION.relative_to(ROOT)),
        "preregistration_sha256": sha256_file(PREREGISTRATION),
        "execution_authority": str(AUTHORITY.relative_to(ROOT)),
        "execution_authority_sha256": sha256_file(AUTHORITY),
        "runtime_acquisition": str(ACQUISITION.relative_to(ROOT)),
        "runtime_acquisition_sha256": sha256_file(ACQUISITION),
        "frozen_input_verification": verification,
        "execution_order": "selection_rank ascending; within rank A/B/C/D/E",
        "planned_units": planned_units(),
        "planned_run_count": 40,
        "run_journal": copy.deepcopy(journal),
        "completed_runs": copy.deepcopy(completed),
        "started_run_count": len(journal),
        "completed_run_count": len(completed),
        "execution_complete": execution_complete,
        "attempt_counts": {row["run_id"]: 1 for row in journal},
        "automatic_retry": "forbidden",
        "manual_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "credential_material_present": False,
        "claim_boundary": {
            "R0_R4_propagation_localization_only": True,
            "R2_R3_result_requires_R4_difference": False,
            "paper_claim_authorized_before_adjudication": False,
        },
    }


def run(
    *,
    output_dir: Path = RUN_DIR,
    index_path: Path = INDEX,
) -> dict[str, Any]:
    if index_path.exists() or output_dir.exists():
        raise RuntimeError("refusing duplicate, replacement, or retry Full-P1 execution")
    verification = verify_inputs()
    fixtures = population()
    treatments = load_document(TREATMENTS)["arms"]
    journal: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    write_json(index_path, index_payload(
        verification=verification,
        journal=journal,
        completed=completed,
        execution_complete=False,
    ))
    for fixture in fixtures:
        for arm in ARMS:
            treatment = treatments[arm]
            run_id = f"full-p1-{fixture['instance_id']}-{arm}"
            started = {
                "ordinal": len(journal) + 1,
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "arm": arm,
                "run_id": run_id,
                "attempt_count": 1,
                "treatment_sha256": treatment["treatment_sha256"],
                "started_at_utc": utcnow(),
                "status": "started_once",
            }
            journal.append(started)
            write_json(index_path, index_payload(
                verification=verification,
                journal=journal,
                completed=completed,
                execution_complete=False,
            ))
            receipt = run_case(
                fixture,
                arm=arm,
                treatment=treatment,
                run_id=run_id,
                output_dir=output_dir,
            )
            completed.append(receipt)
            journal[-1].update({
                "status": "persisted",
                "completed_at_utc": utcnow(),
                "run_file_sha256": receipt["file_sha256"],
            })
            write_json(index_path, index_payload(
                verification=verification,
                journal=journal,
                completed=completed,
                execution_complete=False,
            ))
    write_json(index_path, index_payload(
        verification=verification,
        journal=journal,
        completed=completed,
        execution_complete=True,
    ))
    return {
        "decision": "FULL_P1_BEHAVIORAL_EXECUTION_COMPLETE",
        "run_count": len(completed),
        "index_path": str(index_path.relative_to(ROOT)),
        "index_sha256": sha256_file(index_path),
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
