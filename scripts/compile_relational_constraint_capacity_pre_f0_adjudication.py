from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONSTRUCT = ROOT / "generated" / "relational-constraint-capacity-construct-v2-20260830.json"
SMOKE_RUNNER = ROOT / "scripts" / "run_instructscene_non_scientific_execution_smoke.py"
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
EXPECTED_CONSTRUCT_SHA256 = "48a86fa4bb83cdb9308a1cd6a005cf8ea34033f8649cd579c15fbe3e8347317f"
EXPECTED_SMOKE_RUNNER_SHA256 = "fe9978ada3504f81793cfb4fab23215846dbe0037fc89055deb3478277f82511"
EXPECTED_SMOKE_SUMMARY_SHA256 = "ff885cc06783c99ed3ea4369e70964db38fa06e01a41d1cc4154cd54c4db0c17"
EXPECTED_CASE_HASHES = {
    "smoke-000.json": "c14e8d60d87d70ff436dddb0cb39ce5907b5c5b71e55b58facccd010d5a7f5dc",
    "smoke-001.json": "c4031c057dff8f1b9fd314c3423578eef99368cd381934868c4ea9e99edfca5b",
    "smoke-002.json": "7f561434b3485d1ce36fc84a5912730f8809db419a1cf2ed2d2c0d60ac7fec39",
    "smoke-003.json": "08e1ab8cc8d526495656fb40ad45d5cd772c347ade2846ef3bd1d3a277ebe2c5",
    "smoke-004.json": "a1ffd34f8a4faa9926f6c107eb5988a2b4a42e701453d1f6aded27b702ddf3f5",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_construct() -> dict[str, Any]:
    actual_hash = sha256_file(CONSTRUCT)
    if actual_hash != EXPECTED_CONSTRUCT_SHA256:
        raise SystemExit(f"construct artifact drift: {actual_hash}")
    if sha256_file(SMOKE_RUNNER) != EXPECTED_SMOKE_RUNNER_SHA256:
        raise SystemExit("smoke runner drift")
    construct = load_json(CONSTRUCT)
    if construct.get("object_id") != "RELATIONAL-CONSTRAINT-CAPACITY-20260830":
        raise SystemExit("construct object identity drift")
    qualification = construct.get("construct_qualification_v2") or {}
    if qualification.get("verdict") != "PASS":
        raise SystemExit("construct qualification is not PASS")
    if qualification.get("scientific_outcomes_observed") != 0:
        raise SystemExit("construct artifact contains scientific outcomes")
    if any((construct.get("authority") or {}).values()):
        raise SystemExit("construct authority drifted open")
    return construct


def verify_smoke(smoke_run_dir: Path) -> dict[str, Any]:
    summary_path = smoke_run_dir / "run-summary.json"
    actual_summary_hash = sha256_file(summary_path)
    if actual_summary_hash != EXPECTED_SMOKE_SUMMARY_SHA256:
        raise SystemExit(f"smoke summary drift: {actual_summary_hash}")
    summary = load_json(summary_path)
    if summary.get("object_id") != "RELATIONAL-CONSTRAINT-CAPACITY-20260830":
        raise SystemExit("smoke object identity drift")
    if summary.get("pipeline_label") != "NON_SCIENTIFIC_EXECUTION_SMOKE":
        raise SystemExit("smoke label drift")
    if summary.get("verdict") != "PASS" or summary.get("case_count") != 5:
        raise SystemExit("smoke did not pass exact 5-case contract")
    components = summary.get("components") or {}
    if set(components.values()) != {"PASS"}:
        raise SystemExit("not all smoke components passed")
    invocations = [
        (row.get("processed_cases"), row.get("resume_skipped_cases"))
        for row in summary.get("invocations") or []
    ]
    if invocations != [(5, 0), (0, 5)]:
        raise SystemExit(f"resume history drift: {invocations}")
    if summary.get("scientific_evidence_eligible") is not False:
        raise SystemExit("smoke scientific eligibility drift")
    if summary.get("p1_projection_forbidden") is not True:
        raise SystemExit("smoke P1 projection drift")
    if summary.get("official_reproduction_evidence") is not False:
        raise SystemExit("smoke official-evidence classification drift")
    if summary.get("scientific_metrics_exported") != []:
        raise SystemExit("smoke exported scientific metrics")
    if summary.get("data_archives_downloaded_or_used") != []:
        raise SystemExit("smoke touched data archives")
    if any((summary.get("authority") or {}).values()):
        raise SystemExit("smoke authority drifted open")

    case_dir = smoke_run_dir / "cases"
    case_hashes = {}
    for filename, expected_hash in EXPECTED_CASE_HASHES.items():
        path = case_dir / filename
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise SystemExit(f"smoke case drift: {filename}")
        row = load_json(path)
        if row.get("pipeline_label") != "NON_SCIENTIFIC_EXECUTION_SMOKE":
            raise SystemExit(f"case label drift: {filename}")
        if row.get("scientific_evidence_eligible") is not False:
            raise SystemExit(f"case scientific eligibility drift: {filename}")
        if row.get("p1_projection_forbidden") is not True:
            raise SystemExit(f"case P1 projection drift: {filename}")
        if row.get("official_reproduction_evidence") is not False:
            raise SystemExit(f"case official evidence drift: {filename}")
        metric_projection = row.get("metric_projection") or {}
        if metric_projection != {
            "exact_all_success": "FORBIDDEN",
            "relation_level_iRecall": "FORBIDDEN",
        }:
            raise SystemExit(f"case metric projection drift: {filename}")
        if set((row.get("component_checks") or {}).values()) != {True}:
            raise SystemExit(f"case component failure: {filename}")
        case_hashes[filename] = actual_hash
    extras = sorted(path.name for path in case_dir.glob("*.json"))
    if extras != sorted(EXPECTED_CASE_HASHES):
        raise SystemExit(f"unexpected smoke case files: {extras}")
    return {
        "summary": summary,
        "summary_sha256": actual_summary_hash,
        "case_hashes": case_hashes,
    }


def port010_snapshot() -> dict[str, Any]:
    plan = load_json(PORT_PLAN)
    rows = [
        row
        for row in plan.get("entries") or []
        if row.get("candidate_id") == "PORT-010"
        and row.get("title")
        == "Complex-description boundary in end-to-end 3D world construction"
    ]
    if len(rows) != 1:
        raise SystemExit("exact PORT-010 row not found")
    row = rows[0]
    adjudication = row["release_change_adjudication"]
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED":
        raise SystemExit("PORT-010 status drift")
    if row["evidence_review"].get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 evidence review drift")
    if adjudication.get("required_reopen_components") != [
        "query_units",
        "per_case_outcomes",
    ]:
        raise SystemExit("PORT-010 required reopen components drift")
    if adjudication.get("materialized_reopen_components") != ["query_units"]:
        raise SystemExit("PORT-010 materialized components drift")
    if adjudication.get("remaining_reopen_components") != ["per_case_outcomes"]:
        raise SystemExit("PORT-010 remaining components drift")
    keys = [
        "offline_replay_tier_authorized",
        "provider_authority",
        "gpu_authority",
        "scientific_execution_authority",
    ]
    if any(adjudication.get(key) is not False for key in keys):
        raise SystemExit("PORT-010 authority drift")
    return {
        "candidate_id": "PORT-010",
        "status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
        "evidence_review": "BLOCK_BAKE_IN",
        "required_reopen_components": ["query_units", "per_case_outcomes"],
        "materialized_reopen_components": ["query_units"],
        "remaining_reopen_components": ["per_case_outcomes"],
        **{key: False for key in keys},
        "changed_by_this_object": False,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    construct = verify_construct()
    smoke = verify_smoke(args.smoke_run_dir)
    summary = smoke["summary"]
    both_pass = (
        construct["construct_qualification_v2"]["verdict"] == "PASS"
        and summary["verdict"] == "PASS"
    )
    if not both_pass:
        raise SystemExit("dual-key gate is not satisfied")

    authority = {
        "provider": False,
        "gpu": False,
        "scientific_execution": False,
        "p1": False,
        "official_training": False,
        "data_license_acceptance_confirmed": False,
    }
    return {
        "schema_version": "relational-constraint-capacity-pre-f0-adjudication-v1",
        "generated_at": "2026-08-30T15:30:00+00:00",
        "object_id": "RELATIONAL-CONSTRAINT-CAPACITY-20260830",
        "canonical_candidate_id": None,
        "lifecycle_phase": "PRE_F0",
        "status": "PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY",
        "dual_key_adjudication": {
            "construct_qualification_v2": {
                "verdict": "PASS",
                "artifact": str(CONSTRUCT.relative_to(ROOT)),
                "sha256": EXPECTED_CONSTRUCT_SHA256,
                "scientific_outcomes_observed": 0,
            },
            "non_scientific_execution_smoke": {
                "verdict": "PASS",
                "run_id": summary["run_id"],
                "case_count": 5,
                "summary_sha256": smoke["summary_sha256"],
                "case_hashes": smoke["case_hashes"],
                "components": summary["components"],
                "invocation_history": [
                    {"processed_cases": 5, "resume_skipped_cases": 0},
                    {"processed_cases": 0, "resume_skipped_cases": 5},
                ],
                "scientific_evidence_eligible": False,
                "p1_projection_forbidden": True,
                "official_reproduction_evidence": False,
                "scientific_metrics_exported": [],
                "data_archives_downloaded_or_used": [],
            },
            "both_pass": True,
            "gate_effect": "OPEN_FOR_PRE_F0_PROPOSAL_ONLY",
            "does_not_grant_authority": True,
        },
        "scientific_evidence_firewall": {
            "p1_evidence_inputs": [],
            "smoke_case_outcomes_projected_to_p1": 0,
            "smoke_metrics_projected_to_p1": [],
            "unofficial_checkpoint_role": (
                "execution plumbing only; cannot qualify official reproduction, estimate a "
                "scientific effect, or support/falsify the construct"
            ),
            "scientific_belief_update_from_smoke": "NONE",
        },
        "pre_f0_next_authority_proposal": {
            "status": "PROPOSED_AWAITS_EXPLICIT_HUMAN_CONFIRMATION_AND_GRANT",
            "proposal_is_authority": False,
            "data_license_confirmation": {
                "requested_confirmation": (
                    "An authorized operator or institution has accepted the official "
                    "3D-FRONT/3D-FUTURE research-use terms for this project."
                ),
                "current_state": "NOT_CONFIRMED",
                "mirror_or_derivative_is_not_acceptance_evidence": True,
                "data_materialization_before_confirmation": "FORBIDDEN",
                "required_record": [
                    "authorized confirming identity or institutional role",
                    "terms/version or official access route",
                    "confirmation timestamp",
                    "project/use scope",
                ],
            },
            "official_two_stage_training_gpu_authority": {
                "requested_scope": (
                    "After license confirmation, train the official pinned InstructScene "
                    "bedroom semantic-graph prior and graph-to-layout decoder only."
                ),
                "source_revision": "a9097a62c484c56ac7be5ec2928ef497cbbaaf24",
                "stages": [
                    "stage 1: official instruction-to-semantic-graph prior",
                    "stage 2: official semantic-graph-to-scene-layout decoder",
                ],
                "object_feature_vqvae": (
                    "use the repository-declared official fVQ-VAE path; do not use unofficial "
                    "two-stage weights as scientific initialization evidence"
                ),
                "proposed_budget": (
                    "one A40-equivalent GPU per stage, repository-declared 1-3 days per stage; "
                    "cap proposal at 2-6 GPU-days total before any expansion review"
                ),
                "current_state": "NOT_GRANTED",
                "can_start_now": False,
                "dependencies": [
                    "explicit data-license confirmation recorded",
                    "separate explicit GPU authority grant",
                    "dataset and official training input hashes pinned",
                    "no P1 execution until official checkpoint qualification",
                ],
            },
        },
        "gates": {
            "construct_qualification_v2": "PASS",
            "non_scientific_execution_smoke": "PASS",
            "data_license_confirmation": "AWAITING_EXPLICIT_CONFIRMATION",
            "official_two_stage_training_gpu_authority": "PROPOSED_NOT_GRANTED",
            "official_checkpoint_qualification": "NOT_RUN",
            "P1": "NOT_AUTHORIZED",
            "P2": "NOT_AUTHORIZED",
            "P3": "NOT_AUTHORIZED",
        },
        "relation_to_port010": port010_snapshot(),
        "authority": authority,
        "scientific_authority": False,
        "execution_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--smoke-run-dir",
        type=Path,
        default=Path(
            "/data/wyt/constraint-capacity-smoke-20260830/"
            "non-scientific-bedroom-5case-v1"
        ),
    )
    args = parser.parse_args()
    artifact = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
