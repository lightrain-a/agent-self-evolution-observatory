#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
RECOVERY_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
LEASE_STATUS = "COMPLETED_STAGE_A_V3_R3_RECOVERY_PENDING_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
EXPECTED_GATE = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
CONTROL_PLANE_REVISION = "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
EXPECTED_ADJUDICATION_OUTPUT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def task_claim_paths(claim_root: Path, task_id: str) -> tuple[Path, Path]:
    stem = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
    return claim_root / f"{stem}.attempt.json", claim_root / f"{stem}.sealed.json"


def validate_control_review(review_path: Path, *, minter_sha: str, gate_sha: str, support_adjudicator_sha: str) -> dict[str, Any]:
    review = load(review_path)
    req(review.get("status") == "COMPLETED", "post-terminal control review is not completed")
    req(review.get("surface") == "ChatGPT web", "post-terminal control review surface drift")
    req(review.get("model") == "GPT-5.6 Sol", "post-terminal control review model drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "post-terminal control review did not PASS")
    req(review.get("minter_sha256_acknowledged") == minter_sha, "post-terminal control review minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == gate_sha, "post-terminal control review gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == support_adjudicator_sha, "post-terminal control review support-adjudicator SHA drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "post-terminal control review revision drift")
    req(review.get("stage_b_authority") is False, "post-terminal control review grants Stage-B authority")
    req(review.get("scientific_authority") is False, "post-terminal control review grants scientific authority")
    return review


def validate_terminal_structure(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    contract = load(contract_path)
    recovery_auth = load(recovery_authorization_path)
    summary = load(summary_path)
    csha = sha(contract_path)
    asha = sha(recovery_authorization_path)
    ssha = sha(summary_path)

    req(contract.get("status") == CONTRACT_STATUS, "R3 recovery contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C support-control revision absent")
    trusted = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(trusted.get("algorithm") == "Ed25519", "R3C trusted signer algorithm drift")
    expected_signer_sha = str(trusted.get("public_key_sha256") or "")
    trusted_key = bound(str(trusted.get("public_key_path") or ""))
    req(bool(expected_signer_sha) and trusted_key.is_file(), "R3C trusted signer public-key path/SHA absent")
    req(sha(trusted_key) == expected_signer_sha, "R3C trusted signer public-key content drift")
    req(trusted.get("private_key_in_repository") is False, "R3C trusted signer private key must remain external")
    req(recovery_auth.get("status") == RECOVERY_AUTH_STATUS, "R3 recovery authorization status drift")
    req(recovery_auth.get("contract_sha256") == csha, "R3 recovery authorization contract SHA drift")
    req(recovery_auth.get("single_use") is True and recovery_auth.get("exactly_once") is True, "R3 recovery authorization single-use drift")
    authority = recovery_auth.get("authority") or {}
    req(authority.get("stage_a_provider_execution") is True, "R3 recovery authorization provider authority absent")
    for key in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"R3 recovery authorization overbroad: {key}")

    req(summary.get("status") == SUMMARY_STATUS, "R3 terminal summary status drift")
    req(summary.get("contract_sha256") == csha, "R3 terminal summary contract SHA drift")
    req(summary.get("authorization_sha256") == asha, "R3 terminal summary authorization SHA drift")
    req(summary.get("planned_tasks") == 160, "R3 terminal summary planned-task drift")
    req(summary.get("provider_executable_tasks") == 158, "R3 terminal summary provider-task drift")
    req(summary.get("sealed_k8_pools") == 158, "R3 terminal summary sealed-pool drift")
    req(summary.get("terminal_technical_missing") == 1, "R3 terminal summary technical-missing drift")
    req(summary.get("matched_no_provider_censor") == 1, "R3 terminal summary matched-censor drift")
    req(summary.get("actor_rollouts") == 1264, "R3 terminal summary actor-rollout drift")
    req(summary.get("support_inspected") is False, "R3 terminal summary already inspected support")
    req(summary.get("updater_calls") == 0, "R3 terminal summary updater boundary crossed")
    req(summary.get("heldout_evaluations") == 0, "R3 terminal summary heldout boundary crossed")
    req(summary.get("partial_effect_read") is False, "R3 terminal summary partial-effect boundary crossed")
    req(summary.get("scientific_scores_read") is False, "R3 terminal summary scientific-score boundary crossed")
    req(summary.get("stage_b_authority") is False, "R3 terminal summary grants Stage-B authority")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["global_lease_path"])
    req(run_root.is_dir(), "R3 terminal run root absent")
    req(lease_path.is_file(), "R3 terminal lease absent")
    lease = load(lease_path)
    req(lease.get("status") == LEASE_STATUS, "R3 terminal lease status drift")
    req(lease.get("contract_sha256") == csha, "R3 terminal lease contract SHA drift")
    req(lease.get("authorization_sha256") == asha, "R3 terminal lease authorization SHA drift")
    req(Path(str(lease.get("summary_path") or "")).resolve() == summary_path.resolve(), "R3 terminal lease summary path drift")
    req(lease.get("summary_sha256") == ssha, "R3 terminal lease summary SHA drift")

    completed_manifest = Path(str(summary.get("completed_stream_manifest_path") or ""))
    req(completed_manifest.is_file(), "R3 completed-stream manifest absent")
    req(summary.get("completed_stream_manifest_sha256") == sha(completed_manifest), "R3 completed-stream manifest SHA drift")

    exact = contract["exact_once_acquisition"]
    manifest_path = bound(exact["unit_manifest_path"])
    req(manifest_path.is_file() and sha(manifest_path) == exact["unit_manifest_sha256"], "R3 execution-unit manifest drift")
    manifest = load(manifest_path)
    tasks = [str(value) for value in manifest.get("ordered_task_ids") or []]
    req(len(tasks) == len(set(tasks)) == 158, "R3 execution-unit universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks, "R3 excluded task leaked into provider universe")

    opp_row = contract["recovery_opportunity_manifest"]
    opportunity_path = bound(opp_row["path"])
    req(opportunity_path.is_file() and sha(opportunity_path) == opp_row["sha256"], "R3 opportunity manifest drift")
    opportunity = load(opportunity_path)
    by_stream = {str(k): [str(x) for x in v] for k, v in (opportunity.get("provider_task_ids_by_stream") or {}).items()}
    req(len(by_stream) == 20, "R3 opportunity stream-count drift")
    req(len(by_stream.get("stv3-cgwb-00") or []) == 7, "R3 burned-stream opportunity geometry drift")
    req(len(by_stream.get("stv3-cgwp-00") or []) == 7, "R3 censor-stream opportunity geometry drift")
    req(all(len(v) == (7 if k in {"stv3-cgwb-00", "stv3-cgwp-00"} else 8) for k, v in by_stream.items()), "R3 7/7/8 opportunity geometry drift")
    flattened = [task for stream in by_stream.values() for task in stream]
    req(len(flattened) == len(set(flattened)) == 158 and set(flattened) == set(tasks), "R3 opportunity/provider universe mismatch")

    claim_root = Path(exact["claim_root"])
    req(claim_root.resolve() == (run_root / "checkpoints/stage_a_task_claims").resolve(), "R3 claim-root drift")
    req(claim_root.is_dir(), "R3 claim root absent")
    req(len(list(claim_root.glob("*.attempt.json"))) == 158, "R3 exact-once attempt count drift")
    req(len(list(claim_root.glob("*.sealed.json"))) == 158, "R3 exact-once seal count drift")
    for task in tasks:
        attempt_path, sealed_path = task_claim_paths(claim_root, task)
        req(attempt_path.is_file() and sealed_path.is_file(), f"R3 exact-once receipt missing: {task}")
        attempt = load(attempt_path)
        sealed = load(sealed_path)
        req(attempt.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-attempt", f"R3 attempt type drift: {task}")
        req(attempt.get("status") == "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY", f"R3 attempt status drift: {task}")
        req(sealed.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-seal", f"R3 seal type drift: {task}")
        req(sealed.get("status") == "SEALED_EXACT_ONCE", f"R3 seal status drift: {task}")
        req(attempt.get("task_id") == sealed.get("task_id") == task, f"R3 receipt task drift: {task}")
        req(attempt.get("contract_sha256") == sealed.get("contract_sha256") == csha, f"R3 receipt contract drift: {task}")
        req(attempt.get("authorization_sha256") == sealed.get("authorization_sha256") == asha, f"R3 receipt authorization drift: {task}")
        req(sealed.get("attempt_sha256") == sha(attempt_path), f"R3 attempt binding drift: {task}")
        pool_path = run_root / "cases" / task / "pool_k8.json"
        req(pool_path.is_file(), f"R3 sealed pool absent: {task}")
        req(sealed.get("pool_k8_sha256") == sha(pool_path), f"R3 sealed pool SHA drift: {task}")
    req(not (run_root / "cases" / BURNED).exists(), "burned task case unexpectedly exists in R3 run")
    req(not (run_root / "cases" / CENSOR).exists(), "matched-censor task case unexpectedly exists in R3 run")

    return {
        "contract": contract,
        "recovery_authorization": recovery_auth,
        "summary": summary,
        "contract_sha256": csha,
        "recovery_authorization_sha256": asha,
        "summary_sha256": ssha,
        "run_root": run_root,
        "lease_path": lease_path,
        "tasks": tasks,
        "manifest_path": manifest_path,
        "manifest_sha256": sha(manifest_path),
        "opportunity_path": opportunity_path,
        "opportunity_sha256": sha(opportunity_path),
    }


def build_support_authorization(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    control_review_path: Path,
    output_path: Path,
    adjudication_output_path: Path = EXPECTED_ADJUDICATION_OUTPUT,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    req(not output_path.exists(), "post-terminal support-read authorization already exists")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file(), "R3B guarded support adjudicator absent")
    req(EXPECTED_GATE.is_file(), "post-terminal support gate absent")
    minter_sha = sha(Path(__file__))
    gate_sha = sha(EXPECTED_GATE)
    support_adjudicator_sha = sha(EXPECTED_SUPPORT_ADJUDICATOR)
    state = validate_terminal_structure(
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
    )
    contract = state["contract"]
    bound_code = contract.get("bound_code") or {}
    trusted_signer = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    for key, path, expected_sha in (
        ("post_terminal_support_minter", Path(__file__), minter_sha),
        ("post_terminal_support_gate", EXPECTED_GATE, gate_sha),
        ("equal_dose_adjudicator", EXPECTED_SUPPORT_ADJUDICATOR, support_adjudicator_sha),
    ):
        row = bound_code.get(key) or {}
        req(bound(str(row.get("path") or "")).resolve() == path.resolve(), f"R3B contract {key} path drift")
        req(row.get("sha256") == expected_sha, f"R3B contract {key} SHA drift")
    review = validate_control_review(
        control_review_path,
        minter_sha=minter_sha,
        gate_sha=gate_sha,
        support_adjudicator_sha=support_adjudicator_sha,
    )
    req(not adjudication_output_path.exists(), "R3 support adjudication output already exists")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-authorization",
        "created_at_utc": timestamp,
        "status": SUPPORT_AUTH_STATUS,
        "single_use": True,
        "provider_calls": 0,
        "scientific_execution": False,
        "contract_path": str(contract_path),
        "contract_sha256": state["contract_sha256"],
        "recovery_authorization_path": str(recovery_authorization_path),
        "recovery_authorization_sha256": state["recovery_authorization_sha256"],
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": state["summary_sha256"],
        "terminal_lease_path": str(state["lease_path"]),
        "terminal_lease_sha256": sha(state["lease_path"]),
        "control_review": {
            "path": str(control_review_path.resolve()),
            "sha256": sha(control_review_path),
            "verdict": review["verdict"],
            "model": review["model"],
            "surface": review["surface"],
        },
        "bound_control_plane": {
            "minter_path": str(Path(__file__).resolve()),
            "minter_sha256": minter_sha,
            "gate_path": str(EXPECTED_GATE),
            "gate_sha256": gate_sha,
            "support_adjudicator_path": str(EXPECTED_SUPPORT_ADJUDICATOR),
            "support_adjudicator_sha256": support_adjudicator_sha,
        },
        "trusted_external_signer": {
            "algorithm": trusted_signer["algorithm"],
            "public_key_path": str(bound(str(trusted_signer["public_key_path"])).resolve()),
            "public_key_sha256": trusted_signer["public_key_sha256"],
            "private_key_in_repository": False,
            "signed_capability_required_at_point_of_use": True,
        },
        "execution_scope": {
            "required_adjudication_output": str(adjudication_output_path),
            "required_run_root": str(state["run_root"]),
            "provider_execution_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": BURNED,
            "matched_no_provider_censor": CENSOR,
            "support_required_mixed_pools_per_stream": 4,
            "opportunity_geometry": "7/7/8",
            "support_read_may_open_k8_pool_semantics": True,
            "support_read_before_terminal_recovery": False,
        },
        "authority": {
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "interpretation_boundary": "Structural post-terminal support-read request only. It is not sufficient authority by itself: point-of-use execution additionally requires an externally Ed25519-signed single-use capability from the separately trusted controller key. It grants no provider execution, updater, heldout, Stage-B execution, public benchmark, analyzer, or paper-claim authority.",
        "authority_requires_external_signed_capability": True,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--control-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adjudication-output", type=Path, default=EXPECTED_ADJUDICATION_OUTPUT)
    args = parser.parse_args()
    payload = build_support_authorization(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        control_review_path=args.control_review,
        output_path=args.output,
        adjudication_output_path=args.adjudication_output,
    )
    atomic(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "terminal_summary_sha256": payload["terminal_summary_sha256"],
        "authority": payload["authority"],
        "provider_calls": 0,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
