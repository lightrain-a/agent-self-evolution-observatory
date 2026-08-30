"""Run the separately preregistered, non-replacement P1 Q3 qualification."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_STATE_RULE,
    MODEL,
    PID_NAMESPACE,
    ROOT,
    DockerRun,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    verify_frozen_inputs,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import run_case

FIXTURES = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-task-fixtures-20260830.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-qualification-contract-20260830.json"
ACQUISITION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runtime-acquisition-result-20260830.json"
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
SOURCE_MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json"
PRIOR_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-adjudication-20260830.json"
PARSER_QUALIFICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-parser-qualification-20260830.json"
RUNTIME_OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runtime-qualification-result-20260830.json"
RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runs-20260830"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-index-20260830.json"
ARMS = ("A", "B", "C", "D", "E")
EXPECTED_HASHES = {
    FIXTURES: "b35c9b7a798b371818b25774c129d77c74f7dc90217b3f54f7e4e1d474d15519",
    CONTRACT: "a203da329f05e50c64aefd495e39d971b1865eb8816839be1c0dffd0f939cf79",
    ACQUISITION: "b500b1a4a7d9561cbf0c0f2901c71469171ff70a92615bf98ab1144ed3d595ff",
    TREATMENTS: "35b5f8dab0606ca930a237a6248c9b0aac8a5b6f5564e3ba57217a34dfd92ad7",
    SOURCE_MEMORY: "0451d0346ab5df749df6c1f1d1ea3abbcde3f913958149be9671fce1bfbf2239",
    PRIOR_ADJUDICATION: "019cba107a4251a8791ab4b2edae8a916b48f55776fec98180b0ea914c8413bc",
    PARSER_QUALIFICATION: "b4bec669fb87160b251c123947d9dd8c3819f0c03c2e729aaa4c83c5670d6eca",
}


def load_payload(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = value.pop("payload_sha256")
    if expected != sha256_text(canonical_json(value)):
        raise RuntimeError(f"payload digest drift: {path}")
    return value


def load_q3_fixtures() -> list[dict[str, Any]]:
    return load_payload(FIXTURES)["fixtures"]


def verify_q3_inputs(*, require_acquisition: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {"p1_frozen_inputs": verify_frozen_inputs()}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256_file(path)
        checks[str(path.relative_to(ROOT))] = {
            "expected": expected, "actual": actual, "pass": actual == expected,
        }
    contract = load_payload(CONTRACT)
    fixtures = load_q3_fixtures()
    treatment = json.loads(TREATMENTS.read_text(encoding="utf-8"))
    identities = [(row["selection_rank"], row["instance_id"]) for row in fixtures]
    contract_hashes = contract["treatments"]["treatment_sha256"]
    checks["q3_identity_order"] = {
        "expected": [[5, "sphinx-doc__sphinx-9230"], [6, "django__django-11880"]],
        "actual": [list(row) for row in identities],
        "pass": identities == [
            (5, "sphinx-doc__sphinx-9230"), (6, "django__django-11880")
        ],
    }
    checks["treatment_hashes"] = {
        "pass": all(
            treatment["arms"][arm]["treatment_sha256"] == contract_hashes[arm]
            for arm in ARMS
        )
    }
    checks["preoutcome_contract"] = {
        "pass": (
            contract["scientific_boundary"]["q3_task_outcome_observed"] is False
            and contract["qualification"]["full_p1_execution_authorized"] is False
            and contract["selection"]["automatic_retry"] == "forbidden"
            and contract["selection"]["replacement_sampling"] == "forbidden"
            and contract["outcome_discipline"]["q2_runs_immutable"] is True
        )
    }
    parser_receipt = load_payload(PARSER_QUALIFICATION)
    checks["official_parser_qualification"] = {
        "pass": (
            parser_receipt["decision"] == "P1_Q3_PARSERS_QUALIFIED"
            and parser_receipt["all_cases_exact"] is True
            and parser_receipt["case_count"] == 14
            and parser_receipt["scientific_boundary"]["q3_task_outcome_observed"] is False
        ),
        "file_sha256": sha256_file(PARSER_QUALIFICATION),
    }
    if require_acquisition:
        acquisition = load_payload(ACQUISITION)
        checks["fixed_image_acquisition"] = {
            "pass": (
                acquisition["decision"] == "P1_Q3_FIXED_IMAGES_READY"
                and acquisition["unique_blob_count"] == 15
                and acquisition["unique_blob_bytes"] == 1_592_240_723
                and acquisition["all_blobs_sha256_verified"] is True
                and acquisition["all_images_imported_by_exact_digest"] is True
                and acquisition["scientific_boundary"]["q3_task_outcome_observed"] is False
            ),
            "file_sha256": sha256_file(ACQUISITION),
        }
    if not all(bool(row["pass"]) for key, row in checks.items() if key != "p1_frozen_inputs"):
        raise RuntimeError("Q3 frozen input verification failed")
    return checks


def planned_cases() -> list[dict[str, Any]]:
    result = []
    for fixture in load_q3_fixtures():
        for arm in ARMS:
            result.append({
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "arm": arm,
                "run_id": f"q3-{fixture['instance_id']}-{arm}",
            })
    return result


def qualify_runtime(output: Path = RUNTIME_OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q3 runtime evidence: {output}")
    verification = verify_q3_inputs(require_acquisition=True)
    rows = []
    for fixture in load_q3_fixtures():
        container = DockerRun(
            fixture["image_pull_reference"],
            fixture["model_visible"]["base_commit"],
            f"q3-runtime-{fixture['instance_id']}",
        )
        try:
            start = container.start()
            probe = container.exec(
                "test -d /testbed && test -d /opt/miniconda3 && "
                "test -z \"$(git status --porcelain=v1)\"",
                timeout=30,
            )
            expected_digest = fixture["image_amd64_manifest_digest"]
            digest_visible = expected_digest in start["image_inspect"]["output"]
            rows.append({
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "image": fixture["image_pull_reference"],
                "expected_manifest_digest": expected_digest,
                "start": start,
                "non_outcome_probe": probe,
                "pass": (
                    digest_visible
                    and probe["returncode"] == 0
                    and probe["output"].strip() == ""
                ),
            })
        except Exception as error:
            rows.append({
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "image": fixture["image_pull_reference"],
                "pass": False,
                "error_type": type(error).__name__,
                "message": str(error),
            })
        finally:
            container.close()
    passed = len(rows) == 2 and all(row["pass"] for row in rows)
    decision = "P1_Q3_RUNTIME_QUALIFIED" if passed else "P1_Q3_RUNTIME_HOLD"
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-RUNTIME-QUALIFICATION-20260830",
        "created_at_utc": utcnow(),
        "frozen_input_verification": verification,
        "acquisition_file": str(ACQUISITION.relative_to(ROOT)),
        "acquisition_file_sha256": sha256_file(ACQUISITION),
        "rows": rows,
        "checks": {
            "all_images_present_by_fixed_digest": passed,
            "all_base_states_exact_or_tree_equivalent": passed,
            "base_state_rule": BASE_STATE_RULE,
            "fresh_container_per_probe": True,
            "no_task_test_or_evaluator_executed": True,
            "separate_docker_daemon": True,
            "pid_namespace": PID_NAMESPACE,
        },
        "decision": decision,
        "credential_material_present": False,
        "scientific_boundary": {
            "q3_task_outcome_observed": False,
            "full_p1_execution_authorized": False,
        },
    }
    return {
        "decision": decision,
        "file_sha256": write_json(output, payload),
        "rows": len(rows),
    }


def _index_payload(
    *,
    runtime_sha256: str,
    journal: list[dict[str, Any]],
    completed: list[dict[str, Any]],
    execution_complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-QUALIFICATION-20260830",
        "created_at_utc": utcnow(),
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "fixtures": str(FIXTURES.relative_to(ROOT)),
        "fixtures_sha256": sha256_file(FIXTURES),
        "treatment_manifest": str(TREATMENTS.relative_to(ROOT)),
        "treatment_manifest_sha256": sha256_file(TREATMENTS),
        "runtime_qualification": str(RUNTIME_OUTPUT.relative_to(ROOT)),
        "runtime_qualification_sha256": runtime_sha256,
        "parser_qualification": str(PARSER_QUALIFICATION.relative_to(ROOT)),
        "parser_qualification_sha256": sha256_file(PARSER_QUALIFICATION),
        "fixed_image_acquisition": str(ACQUISITION.relative_to(ROOT)),
        "fixed_image_acquisition_sha256": sha256_file(ACQUISITION),
        "prior_adjudication": str(PRIOR_ADJUDICATION.relative_to(ROOT)),
        "prior_adjudication_sha256": sha256_file(PRIOR_ADJUDICATION),
        "model": MODEL,
        "ordered_execution": "rank 5 A/B/C/D/E then rank 6 A/B/C/D/E",
        "planned_cases": planned_cases(),
        "planned_run_count": 10,
        "run_journal": copy.deepcopy(journal),
        "completed_runs": copy.deepcopy(completed),
        "started_run_count": len(journal),
        "completed_run_count": len(completed),
        "execution_complete": execution_complete,
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "credential_material_present": False,
        "scientific_boundary": {
            "old_ten_runs_immutable": True,
            "q2_runs_immutable": True,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
    }


def run_q3(
    *,
    treatment_manifest: Path = TREATMENTS,
    output_dir: Path = RUN_DIR,
    index_path: Path = INDEX,
) -> dict[str, Any]:
    if treatment_manifest != TREATMENTS:
        raise RuntimeError("Q3 treatment path drift")
    if index_path.exists() or output_dir.exists():
        raise RuntimeError("refusing a second Q3 invocation or replacement run")
    verify_q3_inputs(require_acquisition=True)
    runtime = load_payload(RUNTIME_OUTPUT)
    if runtime["decision"] != "P1_Q3_RUNTIME_QUALIFIED":
        raise RuntimeError("Q3 runtime qualification gate is closed")
    runtime_sha = sha256_file(RUNTIME_OUTPUT)
    treatments = json.loads(treatment_manifest.read_text(encoding="utf-8"))
    fixtures = load_q3_fixtures()
    journal: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    write_json(index_path, _index_payload(
        runtime_sha256=runtime_sha, journal=journal, completed=completed,
        execution_complete=False,
    ))
    for fixture in fixtures:
        for arm in ARMS:
            arm_row = treatments["arms"][arm]
            run_id = f"q3-{fixture['instance_id']}-{arm}"
            started = {
                "ordinal": len(journal) + 1,
                "selection_rank": fixture["selection_rank"],
                "instance_id": fixture["instance_id"],
                "arm": arm,
                "run_id": run_id,
                "treatment_sha256": arm_row["treatment_sha256"],
                "attempt_count": 1,
                "started_at_utc": utcnow(),
                "status": "started_once",
            }
            journal.append(started)
            write_json(index_path, _index_payload(
                runtime_sha256=runtime_sha, journal=journal, completed=completed,
                execution_complete=False,
            ))
            receipt = run_case(
                fixture,
                selected_memory=arm_row["selected_memory"],
                run_id=run_id,
                output_dir=output_dir,
                r0=arm_row["R0"],
            )
            receipt.update({
                "ordinal": started["ordinal"],
                "selection_rank": fixture["selection_rank"],
                "arm": arm,
                "treatment_sha256": arm_row["treatment_sha256"],
                "attempt_count": 1,
            })
            completed.append(receipt)
            journal[-1]["status"] = "persisted"
            journal[-1]["completed_at_utc"] = utcnow()
            journal[-1]["run_file_sha256"] = receipt["file_sha256"]
            write_json(index_path, _index_payload(
                runtime_sha256=runtime_sha, journal=journal, completed=completed,
                execution_complete=False,
            ))
    write_json(index_path, _index_payload(
        runtime_sha256=runtime_sha, journal=journal, completed=completed,
        execution_complete=True,
    ))
    return {
        "decision": "P1_Q3_EXECUTION_COMPLETE",
        "run_count": len(completed),
        "index_path": str(index_path.relative_to(ROOT)),
        "index_sha256": sha256_file(index_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    runtime = sub.add_parser("qualify-runtime")
    runtime.add_argument("--output", type=Path, default=RUNTIME_OUTPUT)
    execute = sub.add_parser("run")
    execute.add_argument("--treatments", type=Path, default=TREATMENTS)
    execute.add_argument("--output-dir", type=Path, default=RUN_DIR)
    execute.add_argument("--index", type=Path, default=INDEX)
    args = parser.parse_args()
    if args.command == "qualify-runtime":
        result = qualify_runtime(args.output)
    else:
        result = run_q3(
            treatment_manifest=args.treatments,
            output_dir=args.output_dir,
            index_path=args.index,
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
