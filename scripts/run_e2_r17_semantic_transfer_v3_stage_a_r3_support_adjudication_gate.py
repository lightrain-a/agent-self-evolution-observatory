#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"
COMPLETION_NAME = "post_terminal_support_read_adjudication.completed.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def validate_support_authorization(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    support_auth = load(support_authorization_path)
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "post-terminal support-read authorization status drift")
    req(support_auth.get("single_use") is True, "post-terminal support-read authorization is not single-use")
    req(support_auth.get("provider_calls") == 0, "post-terminal support-read authorization provider-call drift")
    req(support_auth.get("scientific_execution") is False, "post-terminal support-read authorization incorrectly records scientific execution")

    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "Stage-A support-read authority absent")
    for key in (
        "stage_a_provider_execution",
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"post-terminal support-read authorization overbroad: {key}")

    req(support_auth.get("contract_sha256") == sha(contract_path), "post-terminal support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "post-terminal support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "post-terminal support-read summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve() == contract_path.resolve(), "post-terminal support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve() == recovery_authorization_path.resolve(), "post-terminal support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve() == summary_path.resolve(), "post-terminal support-read summary path drift")

    summary = load(summary_path)
    req(summary.get("status") == SUMMARY_STATUS, "terminal summary no longer at pending-support boundary")
    req(summary.get("support_inspected") is False, "terminal summary indicates support already inspected")
    req(summary.get("stage_b_authority") is False, "terminal summary grants Stage-B authority")

    control = support_auth.get("bound_control_plane") or {}
    minter_path = Path(str(control.get("minter_path") or ""))
    gate_path = Path(str(control.get("gate_path") or ""))
    adjudicator_path = Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256") == sha(minter_path), "support-read minter provenance drift")
    req(gate_path.resolve() == Path(__file__).resolve() and control.get("gate_sha256") == sha(Path(__file__)), "support-read gate SHA drift")
    req(adjudicator_path.resolve() == EXPECTED_SUPPORT_ADJUDICATOR.resolve(), "support adjudicator path drift")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file() and control.get("support_adjudicator_sha256") == sha(EXPECTED_SUPPORT_ADJUDICATOR), "guarded support adjudicator SHA drift")

    review_row = support_auth.get("control_review") or {}
    review_path = Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256") == sha(review_path), "support-read control-review receipt binding drift")
    review = load(review_path)
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "support-read control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT and review_row.get("verdict") == CONTROL_REVIEW_VERDICT, "support-read control-review verdict drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "support-read control-review revision drift")
    req(review.get("minter_sha256_acknowledged") == control.get("minter_sha256"), "support-read review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == control.get("gate_sha256"), "support-read review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == control.get("support_adjudicator_sha256"), "support-read review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "support-read control review grants forbidden authority")

    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == output_path.resolve(), "support adjudication output path drift")
    req(scope.get("provider_execution_tasks") == 158 and scope.get("sealed_k8_pools") == 158, "post-terminal support-read geometry drift")
    req(scope.get("opportunity_geometry") == "7/7/8", "post-terminal support-read opportunity geometry drift")
    req(scope.get("support_required_mixed_pools_per_stream") == 4, "post-terminal support threshold drift")

    run_root = Path(str(scope.get("required_run_root") or ""))
    req(run_root.is_dir(), "post-terminal support-read run root absent")
    lease_path = Path(str(support_auth.get("terminal_lease_path") or ""))
    req(lease_path.is_file() and support_auth.get("terminal_lease_sha256") == sha(lease_path), "post-terminal support-read lease binding drift")
    return {"support_authorization": support_auth, "summary": summary, "run_root": run_root, "lease_path": lease_path}


def default_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_gate(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
    invoke: Callable[[list[str]], subprocess.CompletedProcess[str]] = default_invoke,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3 support adjudication output already exists")
    state = validate_support_authorization(
        support_authorization_path=support_authorization_path,
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
        output_path=output_path,
    )
    run_root: Path = state["run_root"]
    control_root = run_root / "checkpoints/post_terminal_support_read"
    consumption = control_root / CONSUMPTION_NAME
    completion = control_root / COMPLETION_NAME
    req(not consumption.exists(), "post-terminal support-read authorization already consumed; retry forbidden")
    req(not completion.exists(), "post-terminal support adjudication completion receipt already exists")

    auth_sha = sha(support_authorization_path)
    summary_sha = sha(summary_path)
    support_auth = state["support_authorization"]
    review_row = support_auth["control_review"]
    consumption_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
        "support_authorization_path": str(support_authorization_path),
        "support_authorization_sha256": auth_sha,
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": summary_sha,
        "required_output": str(output_path),
        "gate_sha256": sha(Path(__file__)),
        "control_review_sha256": review_row["sha256"],
        "automatic_retry": False,
        "stage_b_authority": False,
    }
    _exclusive_json(consumption, consumption_payload)

    command = [
        python_executable,
        str(EXPECTED_SUPPORT_ADJUDICATOR),
        "--contract",
        str(contract_path),
        "--authorization",
        str(recovery_authorization_path),
        "--summary",
        str(summary_path),
        "--support-authorization",
        str(support_authorization_path),
        "--consumption-marker",
        str(consumption),
        "--output",
        str(output_path),
    ]
    result = invoke(command)
    if result.returncode not in {0, 3}:
        raise RuntimeError(
            "R3 support adjudicator failed outside terminal PASS/HOLD states; support-read permit remains consumed and manual review is required. "
            f"returncode={result.returncode}; stdout_tail={result.stdout[-1200:]}; stderr_tail={result.stderr[-1200:]}"
        )
    req(output_path.is_file(), "R3 support adjudicator returned terminal code without output artifact")
    adjudication = load(output_path)
    expected_statuses = {
        0: "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
        3: "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    }
    req(adjudication.get("status") == expected_statuses[result.returncode], "R3 support adjudicator terminal status/returncode mismatch")
    authority = adjudication.get("authority") or {}
    req(authority.get("execute_stage_b") is False, "R3 support adjudication improperly grants Stage-B execution")
    req(authority.get("heldout_evaluation") is False, "R3 support adjudication improperly grants heldout evaluation")
    req(authority.get("analyzer") is False, "R3 support adjudication improperly grants analyzer authority")
    req(authority.get("paper_promotion") is False, "R3 support adjudication improperly grants paper-promotion authority")

    completion_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-completion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED_POST_TERMINAL_SUPPORT_READ",
        "support_authorization_sha256": auth_sha,
        "consumption_path": str(consumption),
        "consumption_sha256": sha(consumption),
        "terminal_summary_sha256": summary_sha,
        "adjudication_output": str(output_path),
        "adjudication_output_sha256": sha(output_path),
        "adjudication_status": adjudication["status"],
        "adjudicator_returncode": result.returncode,
        "stage_b_authority": False,
        "automatic_retry": False,
    }
    _exclusive_json(completion, completion_payload)
    return {
        "status": completion_payload["status"],
        "adjudication_status": adjudication["status"],
        "returncode": result.returncode,
        "consumption_path": str(consumption),
        "completion_path": str(completion),
        "stage_b_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--support-authorization", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_gate(
        support_authorization_path=args.support_authorization,
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        output_path=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
