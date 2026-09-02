#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_STATUS = "FROZEN_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT"
PREFLIGHT_STATUS = "PASS_RBAGG_SEMANTIC_PILOT_ZERO_PROVIDER_PREFLIGHT"
AUTH_STATUS = "AUTHORIZED_E2_R17_POSTHOLD_RBAGG_SEMANTIC_PILOT_EXACTLY_ONCE"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--preflight", type=Path, required=True)
    ap.add_argument("--runner", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "semantic-pilot authorization already exists")
    for path in (args.contract, args.preflight, args.runner):
        require(path.is_file(), f"missing authorization input: {path}")
    contract = load_json(args.contract)
    preflight = load_json(args.preflight)
    contract_sha = sha_file(args.contract)
    preflight_sha = sha_file(args.preflight)
    runner_sha = sha_file(args.runner)
    require(contract.get("status") == CONTRACT_STATUS, "semantic-pilot contract not frozen")
    require(preflight.get("status") == PREFLIGHT_STATUS, "semantic-pilot preflight not passing")
    require(preflight.get("contract_sha256") == contract_sha, "semantic-pilot preflight contract drift")
    require(preflight.get("provider_calls") == 0 and preflight.get("provider_claims") == 0, "preflight crossed provider boundary")
    require(preflight.get("heldout_evaluations") == 0 and preflight.get("scientific_effectiveness_evaluated") is False, "preflight crossed scientific boundary")
    require(preflight.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "preflight parent status drift")
    require(contract.get("parent_primary_status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "contract parent status drift")
    require(not Path(contract["run_root"]).exists(), "semantic-pilot run root appeared after preflight")
    require(contract["bound_files"]["pilot_runner"]["sha256"] == runner_sha, "runner SHA differs from frozen contract")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-semantic-pilot-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUTH_STATUS,
        "single_use": True,
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "preflight_path": str(args.preflight),
        "preflight_sha256": preflight_sha,
        "runner_path": str(args.runner),
        "runner_sha256": runner_sha,
        "run_root": contract["run_root"],
        "fixed_stream": contract["pilot"]["fixed_stream"],
        "task_ids": contract["pilot"]["task_ids"],
        "model": contract["model"],
        "provider_budget": contract["provider_budget"],
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "authority": {
            "semantic_provider_pilot": True,
            "provider_io": True,
            "rbagg_full_diagnostic": False,
            "heldout_evaluation": False,
            "scientific_effectiveness_inference": False,
            "paper_promotion": False,
            "public_benchmark": False,
            "second_backbone": False,
        },
        "interpretation_boundary": (
            "Exactly one fixed-stream semantic provider pilot. Eight ReasoningBank-style aggregation calls plus one MindMemOS updater realization, "
            "hard ceiling eleven total provider claims. The pilot skill is permanently quarantined; no heldout evaluation or scientific effectiveness inference is authorized."
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
