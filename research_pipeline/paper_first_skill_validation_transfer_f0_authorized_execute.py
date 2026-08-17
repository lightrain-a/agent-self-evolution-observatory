from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .experiment_authority import acquire_authority, release_authority
from .paper_first_skill_validation_transfer_execution_capability import (
    DEFAULT_CONTROL_ROOT,
    validate_execution_capability_receipt,
    write_execution_capability,
)
from .paper_first_skill_validation_transfer_f0 import (
    ARMS,
    CANDIDATE_ID,
    CONTRACT_VERSION,
    MODEL_PRESET,
    ORDER_SEED,
    SCHEDULE_TASKS_PER_ARM,
    SOURCE_COMMIT,
    analyze_rows,
    build_plan,
)
from .paper_first_skill_validation_transfer_f0_authority import (
    EXPECTED_RUNTIME_CONTRACT_SHA256,
    EXPECTED_SOURCE_TREE_SHA256,
    SERVER_ID,
    load_human_authority,
    require_bounded_f0_execution_authority,
)
from .paper_first_skill_validation_transfer_runtime_audit import (
    build_runtime_audit,
    validate_runtime_audit,
)

DEFAULT_RUNTIME_ROOT = Path("/home/wyt/runtime/pa05-skill-validation-transfer-f0")
DEFAULT_SOURCE_ROOT = DEFAULT_RUNTIME_ROOT / "SkillEvolBench"
DEFAULT_PYTHON = DEFAULT_RUNTIME_ROOT / "venv" / "bin" / "python"
DEFAULT_OUTPUT_ROOT = DEFAULT_RUNTIME_ROOT / "runs"
MODEL_YAML = Path("configs/models/gemini-3-flash.yaml")
RESULT_SCHEMA = "1.0-private"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def tracked_source_tree_sha256(source_root: Path) -> tuple[str, int]:
    """Hash the working-tree bytes of all Git-tracked files in deterministic order.

    Ignored install/runtime artifacts are intentionally excluded. Symlinks are hashed by
    link target rather than dereferenced content so the digest is host-independent.
    """

    root = Path(source_root).resolve()
    try:
        raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("PA-05 source root is not a readable Git checkout") from error
    rels = sorted(value.decode("utf-8") for value in raw.split(b"\0") if value)
    h = hashlib.sha256()
    for rel in rels:
        path = root / rel
        if path.is_symlink():
            data = b"SYMLINK\0" + os.readlink(path).encode("utf-8")
        elif path.is_file():
            data = path.read_bytes()
        else:
            raise RuntimeError(f"PA-05 tracked source path missing or unsupported: {rel}")
        digest = hashlib.sha256(data).hexdigest()
        h.update(rel.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\n")
    return h.hexdigest(), len(rels)


def verify_exact_source(source_root: Path) -> dict[str, Any]:
    root = Path(source_root).resolve()
    try:
        head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        tracked_status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=normal"],
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("PA-05 exact source verification failed") from error
    tree_sha, tracked_files = tracked_source_tree_sha256(root)
    errors: list[str] = []
    if head != SOURCE_COMMIT:
        errors.append(f"source-commit-mismatch:{head}")
    if tracked_status:
        errors.append("source-working-tree-not-clean")
    if tree_sha != EXPECTED_SOURCE_TREE_SHA256:
        errors.append(f"source-tracked-tree-sha256-mismatch:{tree_sha}")
    if errors:
        raise RuntimeError(";".join(errors))
    return {
        "source_root": str(root),
        "source_commit": head,
        "tracked_tree_sha256": tree_sha,
        "tracked_files": tracked_files,
        "working_tree_clean": True,
    }


def claim_permit_once(control_root: Path, human_authority: dict[str, Any], run_id: str) -> Path:
    artifact_sha = str(human_authority.get("artifact_sha256") or "")
    if len(artifact_sha) != 64:
        raise RuntimeError("cannot claim PA-05 permit without content-addressed human authority artifact")
    directory = Path(control_root) / "pa05-f0-permit-consumption"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact_sha}.json"
    row = {
        "schema_version": "1.0-private",
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "authority_artifact_sha256": artifact_sha,
        "source_message_sha256": human_authority.get("source_message_sha256"),
        "run_id": str(run_id),
        "plan_hash": build_plan()["plan_sha256"],
        "status": "claimed-single-attempt",
        "claimed_at": _now(),
        "scientific_authority": False,
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(row, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError as error:
        previous = json.loads(path.read_text(encoding="utf-8"))
        raise RuntimeError(
            "PA-05 human permit is single-use and has already been claimed: "
            + str(previous.get("run_id") or "unknown-run")
        ) from error
    return path


def update_claim(path: Path, *, status: str, outcome: str) -> None:
    row = json.loads(path.read_text(encoding="utf-8"))
    row.update({"status": status, "outcome": outcome, "updated_at": _now()})
    _atomic_json(path, row)


def build_arm_command(*, python: Path, source_root: Path, workspace_root: Path, arm: str, run_id: str, dry_run: bool = False) -> list[str]:
    if arm not in ARMS:
        raise ValueError(f"unsupported PA-05 arm: {arm}")
    command = [
        str(Path(python)),
        "-m",
        "scripts.run",
        "--baseline-name",
        arm,
        "--model-yaml",
        str(MODEL_YAML),
        "--order-seed",
        ORDER_SEED,
        "--api-key-env-var",
        "GEMINI_API_KEY",
        "--run-id",
        str(run_id),
        "--workspace-root",
        str(Path(workspace_root).resolve()),
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def _load_arm_rows(run_dir: Path) -> list[dict[str, Any]]:
    record_dir = Path(run_dir) / "stores" / "replay" / "records"
    rows: list[dict[str, Any]] = []
    for path in sorted(record_dir.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"unreadable PA-05 replay record: {path}") from error
        if not isinstance(value, dict):
            raise RuntimeError(f"invalid PA-05 replay record root: {path}")
        rows.append(value)
    if len(rows) != SCHEDULE_TASKS_PER_ARM:
        raise RuntimeError(
            f"PA-05 arm must produce exactly {SCHEDULE_TASKS_PER_ARM} replay records; got {len(rows)} at {run_dir}"
        )
    return rows


def _run_arm(*, python: Path, source_root: Path, workspace_root: Path, arm: str, arm_run_id: str, log_path: Path) -> dict[str, Any]:
    command = build_arm_command(
        python=python,
        source_root=source_root,
        workspace_root=workspace_root,
        arm=arm,
        run_id=arm_run_id,
        dry_run=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(
            command,
            cwd=source_root,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    run_dir = workspace_root / arm_run_id
    report_path = run_dir / "reports" / "full_report.json"
    if proc.returncode != 0:
        raise RuntimeError(f"PA-05 arm failed:{arm}:rc={proc.returncode}:log={log_path}")
    rows = _load_arm_rows(run_dir)
    if not report_path.is_file():
        raise RuntimeError(f"PA-05 arm missing full_report.json:{arm}")
    return {
        "arm": arm,
        "run_id": arm_run_id,
        "returncode": proc.returncode,
        "run_dir": str(run_dir),
        "records": len(rows),
        "report_path": str(report_path),
        "report_sha256": _sha(report_path),
        "log_path": str(log_path),
        "log_sha256": _sha(log_path),
    }


def _build_runtime_receipt(*, source_root: Path) -> dict[str, Any]:
    state = build_runtime_audit(host=SERVER_ID, exact_source_root=source_root)
    errors = validate_runtime_audit(state)
    if errors:
        raise RuntimeError("PA-05 runtime audit invalid:" + ";".join(errors))
    if state.get("runtime_contract_sha256") != EXPECTED_RUNTIME_CONTRACT_SHA256:
        raise RuntimeError("PA-05 runtime contract drift")
    if state.get("runtime_infrastructure_ready") is not True:
        raise RuntimeError("PA-05 runtime infrastructure is not ready")
    if state.get("provider_credential_ready") is not True or state.get("execution_ready") is not True:
        raise RuntimeError("PA-05 GEMINI_API_KEY is not loaded in the execution environment")
    return state


def execute(args: argparse.Namespace) -> dict[str, Any]:
    human_authority = require_bounded_f0_execution_authority(
        authority=load_human_authority(args.authority)
    )
    source_root = Path(args.source_root).resolve()
    python = Path(args.python).resolve()
    control_root = Path(args.control_root).resolve()
    output_root = Path(args.output_root).resolve()
    run_id = str(args.run_id).strip()
    if not run_id:
        raise RuntimeError("PA-05 run_id is required")
    if python != Path(sys.executable).resolve():
        raise RuntimeError(
            "PA-05 controller must itself run under the frozen runtime Python: "
            f"expected={python} actual={Path(sys.executable).resolve()}"
        )
    source_receipt = verify_exact_source(source_root)

    bundle = output_root / f"controller__{run_id}"
    if bundle.exists():
        raise RuntimeError(f"PA-05 controller output bundle must be new: {bundle}")
    workspace_root = bundle / "workspace"
    runtime_audit_path = bundle / "runtime-audit.json"
    capability_path = control_root / "pa05-skill-validation-transfer-execution-capability.json"
    result_path = bundle / "authorized-f0-result.json"
    plan_hash = build_plan()["plan_sha256"]

    # Runtime and credential validation happens before consuming the single-use permit.
    runtime_audit = _build_runtime_receipt(source_root=source_root)
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("PA-05 GEMINI_API_KEY is not loaded in the execution environment")

    claim_path = claim_permit_once(control_root, human_authority, run_id)
    experiment_authority: dict[str, Any] | None = None
    outcome = "controller-error-before-run"
    try:
        experiment_authority = acquire_authority(
            control_root,
            CANDIDATE_ID,
            plan_hash,
            "paper-first-pa05-f0-controller",
            "fresh-phenomenon-f0",
            run_id,
        )
        bundle.mkdir(parents=True, exist_ok=False)
        _atomic_json(runtime_audit_path, runtime_audit)
        capability = write_execution_capability(
            human_authority_path=args.authority,
            run_id=run_id,
            authority_root=control_root,
            experiment_authority_id=str(experiment_authority["authority_id"]),
            runtime_audit_path=runtime_audit_path,
            output_path=capability_path,
        )
        capability_errors = validate_execution_capability_receipt(capability)
        if capability_errors or capability.get("valid") is not True:
            raise RuntimeError("PA-05 controller capability invalid:" + ";".join(capability_errors or capability.get("errors") or []))

        workspace_root.mkdir(parents=True, exist_ok=False)
        source_path = bundle / "source-verification.json"
        _atomic_json(source_path, source_receipt)
        capability_snapshot = bundle / "controller-execution-capability.json"
        _atomic_json(capability_snapshot, capability)

        arm_receipts: dict[str, dict[str, Any]] = {}
        for arm in ARMS:
            arm_run_id = f"{run_id}__{arm}"
            arm_receipts[arm] = _run_arm(
                python=python,
                source_root=source_root,
                workspace_root=workspace_root,
                arm=arm,
                arm_run_id=arm_run_id,
                log_path=bundle / "logs" / f"{arm}.log",
            )

        raw_rows = _load_arm_rows(workspace_root / arm_receipts[ARMS[0]]["run_id"])
        selfgen_rows = _load_arm_rows(workspace_root / arm_receipts[ARMS[1]]["run_id"])
        analysis = analyze_rows(raw_rows, selfgen_rows)
        outcome = str(analysis.get("status") or "completed")
        result: dict[str, Any] = {
            "schema_version": RESULT_SCHEMA,
            "execution_status": "AUTHORIZED_BOUNDED_F0_EXECUTION_COMPLETED",
            "completed_at": _now(),
            "candidate_id": CANDIDATE_ID,
            "contract_version": CONTRACT_VERSION,
            "plan_sha256": plan_hash,
            "run_id": run_id,
            "server_id": SERVER_ID,
            "source": source_receipt,
            "runtime_contract_sha256": runtime_audit.get("runtime_contract_sha256"),
            "human_authority_artifact_sha256": human_authority.get("artifact_sha256"),
            "experiment_authority_id": experiment_authority.get("authority_id"),
            "experiment_authority_epoch": experiment_authority.get("authority_epoch"),
            "execution_kind": "api_docker",
            "gpu_used": False,
            "model_preset": MODEL_PRESET,
            "order_seed": ORDER_SEED,
            "arms": arm_receipts,
            "records_per_arm": {arm: receipt["records"] for arm, receipt in arm_receipts.items()},
            "analysis": analysis,
            "unauthorized_prior_rows_reused": False,
            "secret_values_recorded_in_result_receipt": False,
            "paper_problem_authorized": False,
            "paper_design_authorized": False,
            "method_authorized": False,
            "p0_authorized": False,
            "full_experiment_authorized": False,
            "scientific_authority": False,
        }
        result["result_sha256"] = _canonical_sha({k: v for k, v in result.items() if k != "result_sha256"})
        _atomic_json(result_path, result)
        update_claim(claim_path, status="consumed-completed", outcome=outcome)
        return result
    except Exception as error:
        outcome = f"error:{type(error).__name__}"
        update_claim(claim_path, status="consumed-error", outcome=outcome)
        raise
    finally:
        if experiment_authority is not None:
            release_authority(
                control_root,
                CANDIDATE_ID,
                str(experiment_authority["authority_id"]),
                outcome,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorized PA-05 Skill Validation Transfer F0 controller")
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--control-root", type=Path, default=DEFAULT_CONTROL_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    print(json.dumps(execute(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
