from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import paper_first_evidence_echo_f0 as f0
from research_pipeline.experiment_authority import acquire_authority, release_authority
from research_pipeline.paper_first_fresh_f0_authority import (
    CANDIDATE_ID,
    CONTRACT_VERSION,
    EXPECTED_REPAIR_SHA256,
    EXPECTED_RUNTIME_SHA256,
    load_human_authority,
    require_bounded_f0_execution_authority,
)
from research_pipeline.resource_lease import acquire_gpu_lease, release_gpu_lease


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLLER_PATH = Path(__file__).resolve()
AUTHORITY_CODE_PATH = PROJECT_ROOT / "research_pipeline" / "paper_first_fresh_f0_authority.py"
RUNNER_PATH = PROJECT_ROOT / "research_pipeline" / "paper_first_evidence_echo_f0.py"
REPAIR_PATH = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-f0-operationalization-repair-20260817.json"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def resolve_gpu_uuid(cuda_index: int) -> str:
    raw = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader,nounits"],
        text=True,
    )
    rows: dict[int, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        left, right = line.split(",", 1)
        rows[int(left.strip())] = right.strip()
    if cuda_index not in rows:
        raise RuntimeError(f"CUDA index not found in nvidia-smi inventory: {cuda_index}")
    return rows[cuda_index]


def claim_permit_once(control_root: Path, authority: dict[str, Any], run_id: str, plan_hash: str) -> Path:
    artifact_sha = str(authority.get("artifact_sha256") or "")
    if len(artifact_sha) != 64:
        raise RuntimeError("cannot claim fresh F0 permit without content-addressed authority artifact")
    directory = control_root / "fresh-f0-permit-consumption"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact_sha}.json"
    row = {
        "schema_version": "1.0-private",
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "authority_artifact_sha256": artifact_sha,
        "source_message_sha256": authority.get("source_message_sha256"),
        "run_id": run_id,
        "plan_hash": plan_hash,
        "status": "claimed-single-attempt",
        "claimed_at": _iso_now(),
        "scientific_authority": False,
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(row, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError as error:
        previous = json.loads(path.read_text(encoding="utf-8"))
        raise RuntimeError(
            "fresh F0 human permit is single-use and has already been claimed: "
            + str(previous.get("run_id") or "unknown-run")
        ) from error
    return path


def update_claim(path: Path, *, status: str, outcome: str) -> None:
    row = json.loads(path.read_text(encoding="utf-8"))
    row.update({"status": status, "outcome": outcome, "updated_at": _iso_now()})
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def build_execution_binding(
    *,
    authority: dict[str, Any],
    parent_plan: Path,
    samples: Path,
    pdf_dir: Path,
    cache_dir: Path,
    model: Path,
    out_dir: Path,
    server_id: str,
    cuda_index: int,
    gpu_uuid: str,
    run_id: str,
) -> dict[str, Any]:
    plan = f0.build_plan(parent_plan, samples)
    return {
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "run_id": run_id,
        "controller_sha256": _sha(CONTROLLER_PATH),
        "authority_code_sha256": _sha(AUTHORITY_CODE_PATH),
        "runtime_sha256": _sha(RUNNER_PATH),
        "operationalization_repair_sha256": _sha(REPAIR_PATH),
        "authority_artifact_sha256": authority.get("artifact_sha256"),
        "source_message_sha256": authority.get("source_message_sha256"),
        "parent_plan_path": str(parent_plan.resolve()),
        "parent_plan_sha256": _sha(parent_plan),
        "samples_path": str(samples.resolve()),
        "samples_sha256": _sha(samples),
        "pdf_dir": str(pdf_dir.resolve()),
        "cache_dir": str(cache_dir.resolve()),
        "model_path": str(model.resolve()),
        "out_dir": str(out_dir.resolve()),
        "server_id": server_id,
        "cuda_index": int(cuda_index),
        "gpu_uuid": gpu_uuid,
        "f0_plan_sha256": _canonical_sha(plan),
        "single_attempt": True,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "full_experiment_authorized": False,
        "scientific_authority": False,
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    authority = require_bounded_f0_execution_authority(authority=load_human_authority(args.authority))
    actual_runtime_sha = _sha(RUNNER_PATH)
    actual_repair_sha = _sha(REPAIR_PATH)
    if actual_runtime_sha != EXPECTED_RUNTIME_SHA256:
        raise RuntimeError(f"frozen Evidence Echo runtime drift: {actual_runtime_sha}")
    if actual_repair_sha != EXPECTED_REPAIR_SHA256:
        raise RuntimeError(f"frozen Evidence Echo operationalization repair drift: {actual_repair_sha}")
    if args.out_dir.exists():
        raise RuntimeError(f"authorized F0 output directory must be new: {args.out_dir}")

    gpu_uuid = resolve_gpu_uuid(args.cuda_index)
    binding = build_execution_binding(
        authority=authority,
        parent_plan=args.parent_plan,
        samples=args.samples,
        pdf_dir=args.pdf_dir,
        cache_dir=args.cache_dir,
        model=args.model,
        out_dir=args.out_dir,
        server_id=args.server_id,
        cuda_index=args.cuda_index,
        gpu_uuid=gpu_uuid,
        run_id=args.run_id,
    )
    plan_hash = _canonical_sha(binding)
    claim_path = claim_permit_once(args.control_root, authority, args.run_id, plan_hash)

    experiment_authority: dict[str, Any] | None = None
    gpu_lease: dict[str, Any] | None = None
    outcome = "controller-error-before-run"
    try:
        experiment_authority = acquire_authority(
            args.control_root,
            CANDIDATE_ID,
            plan_hash,
            "paper-first-fresh-f0-controller",
            "fresh-phenomenon-f0",
            args.run_id,
        )
        gpu_lease = acquire_gpu_lease(
            args.control_root,
            args.server_id,
            gpu_uuid,
            args.run_id,
            CANDIDATE_ID,
            idea_id=CANDIDATE_ID,
            authority_id=str(experiment_authority["authority_id"]),
            plan_hash=plan_hash,
            ttl_minutes=args.ttl_minutes,
        )

        args.out_dir.mkdir(parents=True, exist_ok=False)
        receipt = {
            "schema_version": "1.0-private",
            "status": "AUTHORIZED_BOUNDED_F0_EXECUTION_STARTED",
            "started_at": _iso_now(),
            "binding": binding,
            "plan_hash": plan_hash,
            "authority": {
                "human_artifact_path": authority.get("artifact_path"),
                "human_artifact_sha256": authority.get("artifact_sha256"),
                "source_message_ref": authority.get("source_message_ref"),
                "source_message_sha256": authority.get("source_message_sha256"),
                "experiment_authority_id": experiment_authority.get("authority_id"),
                "experiment_authority_epoch": experiment_authority.get("authority_epoch"),
                "gpu_lease_id": gpu_lease.get("lease_id"),
                "gpu_lease_epoch": gpu_lease.get("lease_epoch"),
            },
            "unauthorized_prior_rows_reused": False,
            "scientific_authority": False,
        }
        receipt_path = args.out_dir / "authorized-execution-receipt.json"
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.cuda_index)
        os.environ["P06_DEVICE_MAP"] = "single"
        analysis = f0.run(
            parent_plan_path=args.parent_plan,
            samples_path=args.samples,
            pdf_dir=args.pdf_dir,
            cache_dir=args.cache_dir,
            model_path=args.model,
            out_dir=args.out_dir,
        )
        outcome = str(analysis.get("status") or "completed")
        receipt.update(
            {
                "status": "AUTHORIZED_BOUNDED_F0_EXECUTION_COMPLETED",
                "completed_at": _iso_now(),
                "analysis_status": outcome,
                "analysis_sha256": _sha(args.out_dir / "analysis.json"),
                "rows_sha256": _sha(args.out_dir / "rows.jsonl"),
                "scientific_authority": False,
            }
        )
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        update_claim(claim_path, status="consumed-completed", outcome=outcome)
        return {"receipt": receipt, "analysis": analysis}
    except Exception as error:
        outcome = f"error:{type(error).__name__}"
        update_claim(claim_path, status="consumed-error", outcome=outcome)
        raise
    finally:
        if gpu_lease is not None and experiment_authority is not None:
            try:
                release_gpu_lease(
                    args.control_root,
                    args.server_id,
                    gpu_uuid,
                    str(gpu_lease["lease_id"]),
                    idea_id=CANDIDATE_ID,
                    authority_id=str(experiment_authority["authority_id"]),
                    plan_hash=plan_hash,
                    outcome=outcome,
                )
            finally:
                release_authority(
                    args.control_root,
                    CANDIDATE_ID,
                    str(experiment_authority["authority_id"]),
                    outcome,
                )
        elif experiment_authority is not None:
            release_authority(
                args.control_root,
                CANDIDATE_ID,
                str(experiment_authority["authority_id"]),
                outcome,
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--control-root", type=Path, required=True)
    parser.add_argument("--parent-plan", type=Path, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--server-id", default="52")
    parser.add_argument("--cuda-index", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ttl-minutes", type=int, default=120)
    args = parser.parse_args()
    print(json.dumps(execute(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
