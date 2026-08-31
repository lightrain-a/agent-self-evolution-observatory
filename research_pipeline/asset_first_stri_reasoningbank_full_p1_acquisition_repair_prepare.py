"""Preregister the single-variable Full-P1 mirror acquisition repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    sha256_file,
    utcnow,
    write_json,
)

HOLD = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-result-20260831.json"
POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-acquisition-repair-contract-20260831.json"
EXPECTED_HOLD_SHA256 = "7edaa23c18ac3463b2d0498ee42752186b3a4dc922cc3f49bf951a4dba6a1857"
EXPECTED_POPULATION_SHA256 = "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8"
MISSING_DIGEST = "sha256:90046bcf0aab9c523973ff07859cb84058dbaac249b5d3b77122aaacd56e73bc"
MISSING_SIZE = 103_220_401


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Full-P1 acquisition repair contract")
    if sha256_file(HOLD) != EXPECTED_HOLD_SHA256:
        raise RuntimeError("Full-P1 acquisition HOLD SHA drift")
    if sha256_file(POPULATION) != EXPECTED_POPULATION_SHA256:
        raise RuntimeError("Full-P1 population SHA drift")
    hold = load(HOLD)
    population = load(POPULATION)
    failures = hold["failures"]
    if not (
        hold["decision"] == "FULL_P1_IMAGE_ACQUISITION_HOLD"
        and len(hold["download_rows"]) == 39
        and len(failures) == 1
        and failures[0]["digest"] == MISSING_DIGEST
        and failures[0]["stage"] == "blob_acquisition"
        and "404 Client Error" in failures[0]["message"]
        and len(hold["import_rows"]) == 0
        and hold["scientific_boundary"]["task_outcomes_observed"] is False
    ):
        raise RuntimeError("Full-P1 acquisition failure differential drift")
    rank19 = next(row for row in population["population"] if row["selection_rank"] == 19)
    if rank19["image_amd64_manifest_digest"] != (
        "sha256:a067cc9cec81ba8be9799c03da7a3355fdcd1f10477142052f3477ce8b33057d"
    ):
        raise RuntimeError("rank-19 manifest drift")
    manifest = load(ROOT / rank19["manifest_path"])
    matches = [row for row in manifest["layers"] if row["digest"] == MISSING_DIGEST]
    if len(matches) != 1 or int(matches[0]["size"]) != MISSING_SIZE:
        raise RuntimeError("missing descriptor drift")
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-ACQUISITION-REPAIR-20260831",
        "created_at_utc": utcnow(),
        "decision": "FULL_P1_ACQUISITION_SINGLE_VARIABLE_REPAIR_AUTHORIZED",
        "failure_differential": {
            "classification": "external mirror repository blob availability",
            "failed_channel": "docker.1ms.run",
            "http_status": 404,
            "failed_digest": MISSING_DIGEST,
            "failed_size": MISSING_SIZE,
            "affected_selection_rank": 19,
            "affected_instance_id": "django__django-15695",
            "task_outcomes_observed": False,
            "model_calls": 0,
            "evaluator_calls": 0,
        },
        "single_changed_variable": {
            "variable": "OCI blob acquisition channel for the sole unavailable blob",
            "from": "https://docker.1ms.run",
            "to": "https://docker.1panel.live",
            "manifest_digest_changed": False,
            "blob_digest_changed": False,
            "blob_size_changed": False,
            "task_changed": False,
            "treatment_changed": False,
            "provider_model_changed": False,
            "sampling_changed": False,
            "runtime_semantics_changed": False,
        },
        "capability_probe": {
            "alternative_manifest_amd64_digest": rank19["image_amd64_manifest_digest"],
            "expected_manifest_amd64_digest": rank19["image_amd64_manifest_digest"],
            "blob_response_status": 200,
            "blob_response_docker_content_digest": MISSING_DIGEST,
            "blob_response_content_length": MISSING_SIZE,
            "probe_persisted_blob": False,
        },
        "repair_action": {
            "missing_blob_digest": MISSING_DIGEST,
            "missing_blob_size": MISSING_SIZE,
            "source_url": (
                "https://docker.1panel.live/v2/"
                "swebench/sweb.eval.x86_64.django_1776_django-15695/blobs/"
                + MISSING_DIGEST
            ),
            "acquisition_invocation_count": 1,
            "downloader_internal_max_tries": 10,
            "sha256_verification_required": True,
            "verify_all_40_frozen_descriptors_after_repair": True,
            "import_all_8_images_by_exact_frozen_manifest_digest": True,
            "run_model": False,
            "run_evaluator": False,
        },
        "bindings": {
            "failed_acquisition": str(HOLD.relative_to(ROOT)),
            "failed_acquisition_sha256": sha256_file(HOLD),
            "population": str(POPULATION.relative_to(ROOT)),
            "population_sha256": sha256_file(POPULATION),
            "rank19_manifest": rank19["manifest_path"],
            "rank19_manifest_sha256": rank19["manifest_file_sha256"],
        },
        "failure_policy": {
            "automatic_repair_rerun": False,
            "task_replacement": False,
            "image_replacement": False,
            "digest_substitution": False,
            "behavioral_execution_remains_unauthorized": True,
            "repair_failure_decision": "FULL_P1_ACQUISITION_REPAIR_HOLD",
        },
        "scientific_boundary": {
            "qualification_or_repair_is_not_scientific_evidence": True,
            "task_outcomes_observed": False,
            "behavioral_execution_authorized": False,
            "paper_claim_authorized": False,
        },
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
    }


def main() -> None:
    print(json.dumps(prepare(), sort_keys=True))


if __name__ == "__main__":
    main()
