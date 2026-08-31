"""Issue the separate Full-P1 behavioral execution authority after all gates pass."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    MODEL,
    ROOT,
    sha256_file,
    utcnow,
    write_json,
)

PREREGISTRATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"
POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
ACQUISITION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-result-20260831.json"
QUALIFICATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-provider-evaluator-qualification-20260831.json"
TEST_GATE = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-targeted-test-gate-20260831.json"
RUNNER = ROOT / "research_pipeline/asset_first_stri_reasoningbank_full_p1_runner.py"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-execution-authority-20260831.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-index-20260831.json"
RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runs-20260831"
EXPECTED_PREREGISTRATION_SHA256 = "af8e9efb53ad5df5e846329b289ce791bc8ffe7c581f810c0ade1067d09fe7dd"
EXPECTED_POPULATION_SHA256 = "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8"
EXPECTED_TEST_GATE_SHA256 = "5149077ee086cde2a20a9563f33e8f4785d93dd582b6b44ab1c7d864142b3e4d"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def authorize(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Full-P1 execution authority")
    if INDEX.exists() or RUN_DIR.exists():
        raise RuntimeError("Full-P1 execution artifacts predate authority")
    prereg = load(PREREGISTRATION)
    acquisition = load(ACQUISITION)
    qualification = load(QUALIFICATION)
    test_gate = load(TEST_GATE)
    checks = {
        "preregistration_exact_and_execution_unauthorized": (
            sha256_file(PREREGISTRATION) == EXPECTED_PREREGISTRATION_SHA256
            and prereg["decision"]
            == "FULL_P1_BEHAVIORAL_PROPAGATION_PREREGISTERED_EXECUTION_UNAUTHORIZED"
            and prereg["claim_boundary"]["behavioral_execution_authorized"] is False
        ),
        "population_exact": sha256_file(POPULATION) == EXPECTED_POPULATION_SHA256,
        "images_exact_and_ready": (
            acquisition["decision"] == "FULL_P1_EXACT_IMAGES_READY"
            and acquisition["all_blobs_sha256_verified"] is True
            and acquisition["all_images_imported_by_exact_digest"] is True
            and acquisition["scientific_boundary"]["task_outcomes_observed"] is False
        ),
        "runtime_provider_evaluator_qualified": (
            qualification["decision"]
            == "FULL_P1_RUNTIME_PROVIDER_EVALUATOR_QUALIFIED"
            and qualification["runtime_preflight"]["pass"] is True
            and qualification["provider_qualification"]["pass"] is True
            and qualification["parser_evaluator_qualification"]["pass"] is True
            and qualification["execution_authorized"] is False
            and qualification["scientific_boundary"]["task_outcomes_observed"] is False
        ),
        "targeted_tests_exact_and_passed": (
            sha256_file(TEST_GATE) == EXPECTED_TEST_GATE_SHA256
            and test_gate["decision"] == "FULL_P1_TARGETED_TEST_GATE_PASS"
            and test_gate["pass"] is True
        ),
        "runner_frozen": RUNNER.exists(),
        "provider_model_exact": (
            prereg["provider_and_sampling"]["model"] == MODEL
            and qualification["provider_qualification"]["frozen_model"] == MODEL
        ),
        "frozen_unit_count_exact": (
            prereg["execution_contract"]["unit_count"] == 40
            and len(prereg["execution_contract"]["journal_units"]) == 40
        ),
        "all_attempt_counts_one": all(
            row["attempt_count"] == 1
            for row in prereg["execution_contract"]["journal_units"]
        ),
        "no_retry_no_replacement": (
            prereg["execution_contract"]["automatic_retry"] is False
            and prereg["execution_contract"]["manual_retry"] is False
            and prereg["execution_contract"]["replacement_sampling"] is False
        ),
        "execution_has_not_started": not INDEX.exists() and not RUN_DIR.exists(),
    }
    passed = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-EXECUTION-AUTHORITY-20260831",
        "created_at_utc": utcnow(),
        "decision": (
            "FULL_P1_BEHAVIORAL_EXECUTION_AUTHORIZED"
            if passed
            else "FULL_P1_BEHAVIORAL_EXECUTION_AUTHORITY_HOLD"
        ),
        "execution_authorized": passed,
        "bindings": {
            "preregistration": str(PREREGISTRATION.relative_to(ROOT)),
            "preregistration_sha256": sha256_file(PREREGISTRATION),
            "population": str(POPULATION.relative_to(ROOT)),
            "population_sha256": sha256_file(POPULATION),
            "acquisition": str(ACQUISITION.relative_to(ROOT)),
            "acquisition_sha256": sha256_file(ACQUISITION),
            "qualification": str(QUALIFICATION.relative_to(ROOT)),
            "qualification_sha256": sha256_file(QUALIFICATION),
            "targeted_test_gate": str(TEST_GATE.relative_to(ROOT)),
            "targeted_test_gate_sha256": sha256_file(TEST_GATE),
            "runner": str(RUNNER.relative_to(ROOT)),
            "runner_sha256": sha256_file(RUNNER),
            "model": MODEL,
        },
        "checks": checks,
        "authorized_action": {
            "command": "python -m research_pipeline.asset_first_stri_reasoningbank_full_p1_runner",
            "invocation_count": 1,
            "planned_run_count": 40,
            "order": "selection_rank ascending; within rank A/B/C/D/E",
            "attempt_count_each": 1,
            "automatic_retry": False,
            "manual_retry": False,
            "replacement_sampling": False,
            "authority_consumed_by_first_index_creation": True,
        },
        "failure_rule": (
            "A failed or interrupted behavioral unit remains the sole terminal record "
            "for that frozen unit. Do not rerun, replace, or issue another authority "
            "without a new prospective protocol outside this Full-P1 execution."
        ),
        "claim_boundary": {
            "authority_permits_execution_only": True,
            "authority_is_not_a_scientific_result": True,
            "paper_claim_authorized": False,
            "R2_R3_result_requires_R4_difference": False,
        },
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "execution_authorized": passed,
        "file_sha256": write_json(output, payload),
    }


def main() -> None:
    print(json.dumps(authorize(), sort_keys=True))


if __name__ == "__main__":
    main()
