#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_experiment_lease import (
    acquire_reopened_experiment_lease,
    public_reopened_experiment_lease,
    publish_reopened_experiment_lease,
    validate_reopened_experiment_lease_ledger,
)
from research_pipeline.reopened_experiment_lease_request import validate_experiment_lease_request
from research_pipeline.reopened_local_validation_authorization import validate_local_validation_authorization
from research_pipeline.reopened_pre_experiment_adapter import validate_reopened_pre_experiment
from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_experiment_blueprint import (
    validate_reopen_blueprint_review,
    validate_reopen_experiment_blueprint,
)


def load(path: Path) -> dict:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return row


def latest_receipt(path: Path, validator) -> dict:
    row = load(path)
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, dict) else {}
        if isinstance(receipt, dict) and validator(receipt):
            return receipt
    raise RuntimeError(f"valid receipt not found: {path}")


def contract_at(root: Path, contract_id: str) -> dict:
    contract = load(root / "scientific-contracts" / f"{contract_id}.json")
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("invalid reopened scientific contract")
    return contract


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Explicitly acquire the single-writer experiment lease for a reopened local-F0 plan. "
            "This rechecks governance and config identity, records the lease, but never starts the run, loads a model, or allocates a GPU."
        )
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--runtime-supplement", type=Path, required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--external-execution-authority-ref", required=True)
    args = parser.parse_args()

    contract = contract_at(args.root, args.contract_id)
    blueprint_path = args.root / "scientific-contract-experiment-blueprints" / f"{args.contract_id}.json"
    blueprint = latest_receipt(blueprint_path, validate_reopen_experiment_blueprint)
    blueprint_review = latest_receipt(blueprint_path, validate_reopen_blueprint_review)
    local_auth = latest_receipt(
        args.root / "scientific-contract-local-validation-authority" / f"{args.contract_id}.json",
        validate_local_validation_authorization,
    )
    pre = latest_receipt(
        args.root / "scientific-contract-pre-experiment" / f"{args.contract_id}.json",
        validate_reopened_pre_experiment,
    )
    request = latest_receipt(
        args.root / "scientific-contract-experiment-lease-requests" / f"{args.contract_id}.json",
        validate_experiment_lease_request,
    )
    runtime = load(args.runtime_supplement)

    receipt = acquire_reopened_experiment_lease(
        root=args.root,
        contract=contract,
        blueprint=blueprint,
        blueprint_review=blueprint_review,
        local_authorization=local_auth,
        pre_experiment_receipt=pre,
        lease_request=request,
        runtime_supplement=runtime,
        actor=args.actor,
        run_id=args.run_id,
        external_execution_authority_ref=args.external_execution_authority_ref,
    )
    ledger = publish_reopened_experiment_lease(args.root, receipt)
    errors = validate_reopened_experiment_lease_ledger(ledger)
    if errors:
        raise RuntimeError(errors)
    public = public_reopened_experiment_lease(args.root, args.contract_id)
    if public.get("status") != "EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED":
        raise RuntimeError("experiment lease was recorded but is not current/active")

    print(
        json.dumps(
            {
                "status": "PASS_EXPERIMENT_LEASE_ACQUIRED_RUN_NOT_STARTED",
                "contract_id": args.contract_id,
                "lease_acquisition_sha256": receipt["lease_acquisition_sha256"],
                "experiment_authority_id": receipt["experiment_authority_id"],
                "authority_epoch": receipt["authority_epoch"],
                "run_id": receipt["run_id"],
                "governance_stage": receipt["governance_stage"],
                "experiment_authority_acquired": True,
                "execution_authorized": True,
                "execution_started": False,
                "model_loaded": False,
                "gpu_allocated": False,
                "resource_lease_required_if_gpu": True,
                "explicit_run_start_required": True,
                "events": len(ledger.get("events") or []),
                "public_status": public.get("status"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
