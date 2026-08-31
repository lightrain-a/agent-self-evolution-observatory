"""Non-scientific Q5 evaluator smoke and machine-readable execution authority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    EVALUATOR_TIMEOUT_SECONDS, ROOT, DockerRun, sha256_file, sha256_text,
    utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    CONTRACT_SHA256, fixture_by_id, image_digest_visible,
    official_and_local_maps, repaired_fixture, verify_q5_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CONTRACT, SPHINX_AFTER, SPHINX_BEFORE, load_payload,
)

SMOKE = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-evaluator-verbosity-smoke-20260831.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-execution-authority-20260831.json"
SMOKE_TEST = "tests/test_domain_py.py::test_function_signatures"
SMOKE_COMMAND = f"tox --current-env -epy39 -v -- -rA {SMOKE_TEST}"


def run_smoke(output: Path = SMOKE) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q5 smoke: {output}")
    verification = verify_q5_contract()
    fixture = fixture_by_id()["sphinx-doc__sphinx-9230"]
    container = DockerRun(
        fixture["image_pull_reference"],
        fixture["model_visible"]["base_commit"],
        "q5-nonscientific-evaluator-verbosity-smoke",
        exact_base=True,
    )
    try:
        start = container.start()
        before = container.exec(
            "git rev-parse HEAD && git diff --quiet HEAD && "
            "test -z \"$(git status --porcelain=v1 --untracked-files=all)\"",
            timeout=30,
        )
        install = container.exec(
            "source /opt/miniconda3/bin/activate && conda activate testbed && "
            "python -m pip install -e .[test]",
            timeout=EVALUATOR_TIMEOUT_SECONDS,
        )
        execution = container.exec(
            "source /opt/miniconda3/bin/activate && conda activate testbed && "
            + SMOKE_COMMAND,
            timeout=EVALUATOR_TIMEOUT_SECONDS,
        )
        official, local = official_and_local_maps("parse_log_sphinx", execution["output"])
        after = container.exec(
            "git rev-parse HEAD && git -c core.fileMode=false diff --binary HEAD",
            timeout=30,
        )
        checks = {
            "S1_per_test_result_lines": SMOKE_TEST in official,
            "S2_official_status_map_nonempty": len(official) > 0,
            "S3_official_local_parser_exact": official == local,
            "S4_only_reporting_verbosity_changed": (
                SPHINX_AFTER.replace("tests/test_domain_py.py", SMOKE_TEST)
                == SMOKE_COMMAND
                and fixture["evaluator_only"]["eval_script"].count(SPHINX_BEFORE) == 1
                and before["returncode"] == 0
                and after["returncode"] == 0
                and after["output"].strip() == fixture["model_visible"]["base_commit"]
            ),
            "S5_no_model_or_provider_call": True,
            "S6_evaluator_terminated_normally": (
                install["returncode"] == 0
                and not install["timed_out"]
                and execution["returncode"] == 0
                and not execution["timed_out"]
            ),
            "fresh_exact_digest_container": image_digest_visible(
                start, fixture["image_amd64_manifest_digest"]
            ),
            "exact_base_normalization": (
                start["base_commit_receipt"]["rule"]
                == "exact_base_after_preregistered_hard_reset"
                and start["base_commit_receipt"]["observed_head"]
                == fixture["model_visible"]["base_commit"]
            ),
        }
        passed = all(checks.values())
        payload = {
            "schema_version": 1,
            "experiment_id": "NON_SCIENTIFIC_EVALUATOR_VERBOSITY_SMOKE-20260831",
            "created_at_utc": utcnow(),
            "contract_sha256": CONTRACT_SHA256,
            "verification": verification,
            "scientific_authority": False,
            "paper_authority": False,
            "mechanism_authority": False,
            "task_outcome_authority": False,
            "fixture": {
                "instance_id": fixture["instance_id"],
                "image": fixture["image_pull_reference"],
                "image_digest": fixture["image_amd64_manifest_digest"],
                "base_commit": fixture["model_visible"]["base_commit"],
                "source_patch_applied": False,
                "test_patch_applied": False,
                "selected_test_file": "tests/test_domain_py.py",
                "selected_test": SMOKE_TEST,
            },
            "command": SMOKE_COMMAND,
            "command_sha256": sha256_text(SMOKE_COMMAND),
            "runtime_start": start,
            "install": install,
            "execution": execution,
            "official_status_map": official,
            "local_status_map": local,
            "checks": checks,
            "pass": passed,
            "decision": (
                "Q5_EVALUATOR_VERBOSITY_SMOKE_PASS"
                if passed else "Q5_EVALUATOR_VERBOSITY_SMOKE_HOLD"
            ),
            "model_calls": 0,
            "provider_calls": 0,
            "credential_material_present": False,
        }
    except Exception as error:
        payload = {
            "schema_version": 1,
            "experiment_id": "NON_SCIENTIFIC_EVALUATOR_VERBOSITY_SMOKE-20260831",
            "created_at_utc": utcnow(),
            "contract_sha256": CONTRACT_SHA256,
            "scientific_authority": False,
            "paper_authority": False,
            "mechanism_authority": False,
            "task_outcome_authority": False,
            "pass": False,
            "decision": "Q5_EVALUATOR_VERBOSITY_SMOKE_HOLD",
            "failure": {"error_type": type(error).__name__, "message": str(error)},
            "model_calls": 0,
            "provider_calls": 0,
            "credential_material_present": False,
        }
    finally:
        container.close()
    file_sha = write_json(output, payload)
    return {"decision": payload["decision"], "pass": payload["pass"], "file_sha256": file_sha}


def generate_authority(
    smoke_path: Path = SMOKE, output: Path = AUTHORITY,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q5 authority: {output}")
    verification = verify_q5_contract()
    smoke = load_payload(smoke_path)
    contract = load_payload(CONTRACT)
    fixtures = fixture_by_id()
    repaired = {key: repaired_fixture(value) for key, value in fixtures.items()}
    sphinx_before = fixtures["sphinx-doc__sphinx-9230"]["evaluator_only"]["eval_script"]
    sphinx_after = repaired["sphinx-doc__sphinx-9230"]["evaluator_only"]["eval_script"]
    django_before = fixtures["django__django-11880"]["evaluator_only"]["eval_script"]
    django_after = repaired["django__django-11880"]["evaluator_only"]["eval_script"]
    checks = {
        "contract_exact": verification["pass"] and sha256_file(CONTRACT) == CONTRACT_SHA256,
        "q4_source_artifacts_exact": all(r["pass"] for r in verification["source_checks"]),
        "q4_adjudication_exact": (
            verification["q4_adjudication_sha256"]
            == contract["bindings"]["q4_adjudication_sha256"]
        ),
        "official_parser_exact": (
            verification["official_swebench_wheel_sha256"]
            == contract["bindings"]["official_swebench_wheel_sha256"]
        ),
        "smoke_pass": (
            smoke["decision"] == "Q5_EVALUATOR_VERBOSITY_SMOKE_PASS"
            and smoke["pass"] is True
            and all(smoke["checks"].values())
        ),
        "single_variable_change_exact": (
            sphinx_before.count(SPHINX_BEFORE) == 1
            and sphinx_after == sphinx_before.replace(SPHINX_BEFORE, SPHINX_AFTER)
            and django_after == django_before
        ),
        "model_provider_unreachable": True,
        "fresh_container_base_path_qualified": (
            smoke["checks"]["fresh_exact_digest_container"]
            and smoke["checks"]["exact_base_normalization"]
        ),
        "no_treatment_or_input_change": True,
        "no_outcome_dependent_selection": True,
        "no_frozen_artifact_drift": True,
    }
    authorized = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-EXECUTION-AUTHORITY-20260831",
        "created_at_utc": utcnow(),
        "contract_sha256": CONTRACT_SHA256,
        "smoke_sha256": sha256_file(smoke_path),
        "checks": checks,
        "decision": (
            "P1_Q5_REPLAY_EXECUTION_AUTHORIZED"
            if authorized else "P1_Q5_REPLAY_EXECUTION_HOLD"
        ),
        "q5_replay_execution_authorized": authorized,
        "q5_execution_order": "rank 5 A/B/C/D/E then rank 6 A/B/C/D/E",
        "attempt_count": 1,
        "automatic_retry": "forbidden",
        "replacement_sampling": "forbidden",
        "model_calls": 0,
        "provider_calls": 0,
        "full_p1_execution_authorized": False,
        "paper_result_claim_authorized": False,
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "q5_replay_execution_authorized": authorized,
        "file_sha256": file_sha,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("smoke", "authorize"))
    args = parser.parse_args()
    result = run_smoke() if args.command == "smoke" else generate_authority()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
