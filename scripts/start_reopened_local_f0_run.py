#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_experiment_lease import validate_reopened_experiment_lease, validate_reopened_experiment_lease_ledger
from research_pipeline.reopened_experiment_lease_request import validate_experiment_lease_request
from research_pipeline.reopened_local_f0_run import (
    ACTIVE_STATUS,
    public_reopened_local_f0_run,
    start_and_publish_reopened_local_f0_run,
    validate_run_start_ledger,
)
from research_pipeline.reopened_local_validation_authorization import validate_local_validation_authorization
from research_pipeline.reopened_pre_experiment_adapter import validate_reopened_pre_experiment


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest(path: Path, validator, *, ledger_validator=None) -> dict:
    row = load(path)
    if ledger_validator is not None:
        errors = ledger_validator(row)
        if errors:
            raise RuntimeError(errors)
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validator(receipt):
            return receipt
    raise RuntimeError(f"valid receipt not found: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Acquire the bounded GPU resource lease and record an explicit reopened local-F0 run start. "
            "This creates the run root/marker but does not launch a model process or claim any scientific/P0 result."
        )
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--ttl-minutes", type=int, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-revision", required=True)
    args = parser.parse_args()

    cid = args.contract_id
    experiment_lease = latest(
        args.root / "scientific-contract-experiment-leases" / f"{cid}.json",
        validate_reopened_experiment_lease,
        ledger_validator=validate_reopened_experiment_lease_ledger,
    )
    lease_request = latest(
        args.root / "scientific-contract-experiment-lease-requests" / f"{cid}.json",
        validate_experiment_lease_request,
    )
    pre_experiment = latest(
        args.root / "scientific-contract-pre-experiment" / f"{cid}.json",
        validate_reopened_pre_experiment,
    )
    local_auth = latest(
        args.root / "scientific-contract-local-validation-authority" / f"{cid}.json",
        validate_local_validation_authorization,
    )

    receipt, ledger = start_and_publish_reopened_local_f0_run(
        root=args.root,
        experiment_lease=experiment_lease,
        lease_request=lease_request,
        pre_experiment_receipt=pre_experiment,
        local_authorization=local_auth,
        server_id=args.server_id,
        gpu_uuid=args.gpu_uuid,
        owner=args.owner,
        ttl_minutes=args.ttl_minutes,
        run_root=args.run_root,
        model_name=args.model_name,
        model_revision=args.model_revision,
    )
    errors = validate_run_start_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_reopened_local_f0_run(args.root, cid)
    if public.get("status") != ACTIVE_STATUS:
        raise RuntimeError("run-start receipt was recorded but experiment/resource authority is not current")

    print(json.dumps({
        "status": "PASS_REOPEN_LOCAL_F0_RUN_STARTED_MODEL_NOT_LOADED",
        "contract_id": cid,
        "run_start_sha256": receipt["run_start_sha256"],
        "run_id": receipt["run_id"],
        "server_gpu_binding_sha256": receipt["server_gpu_binding_sha256"],
        "gpu_lease_id": receipt["gpu_lease_id"],
        "gpu_lease_epoch": receipt["gpu_lease_epoch"],
        "model_name": receipt["model_name"],
        "model_revision": receipt["model_revision"],
        "execution_started": True,
        "gpu_allocated": True,
        "model_loaded": False,
        "scientific_authority": False,
        "p0_authority": False,
        "full_experiment_authority": False,
        "events": len(ledger.get("events") or []),
        "public_status": public.get("status"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
