#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_m3r4_execution_guard import (
    FINAL_CONTRACT_STATUS,
    PREFLIGHT_AUTH_STATUS,
    validate_execution_authorization,
    validate_final_contract,
    validate_fresh_identity,
    validate_zero_provider_draft,
)
from research_pipeline.e2_r17_m3r4_execution_plan import (
    MAX_OUTPUT_TOKENS,
    MAX_TURNS,
    REQUIRED_RESOLVED_MODEL,
    TASK_IDS,
    sha256_file,
    structural_provider_budget,
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def repo_ref(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def build_final_contract(*, draft_path: Path, identity_path: Path) -> dict[str, Any]:
    draft = validate_zero_provider_draft(draft_path)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    validate_fresh_identity(identity, draft)

    final = copy.deepcopy(draft)
    final["artifact_type"] = "e2-r17-m3r4-execution-final-contract"
    final["status"] = FINAL_CONTRACT_STATUS
    final["finalized_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    final["git_commit_at_final_freeze"] = git_head()
    final["parent_draft"] = {
        "path": repo_ref(draft_path),
        "sha256": sha256_file(draft_path),
    }
    final["fresh_model_identity"] = {
        "path": repo_ref(identity_path),
        "sha256": sha256_file(identity_path),
    }
    gate = final["fresh_model_identity_gate"]
    gate["fresh_identity_artifact"] = repo_ref(identity_path)
    gate["fresh_identity_sha256"] = sha256_file(identity_path)
    final["authority"] = {key: False for key in final["authority"]}
    final["next_gate"] = "ACTUAL_PATH_ZERO_PROVIDER_PREFLIGHT_ONLY"
    final["interpretation_boundary"] = (
        "Final content-addressed M3R4 execution contract only. The contract itself grants zero provider, "
        "scientific, actor-measurement, updater, analysis, M4, E3, paper-promotion, or submission authority. "
        "Only a separately validated preflight-only authorization may traverse the real actor path before "
        "provider I/O; scientific measurement still requires a separate explicit measurement authorization."
    )
    final.setdefault("bound_code", {})["final_contract_freezer"] = {
        "path": "scripts/freeze_e2_r17_m3r4_final_contract.py",
        "sha256": sha256_file(ROOT / "scripts/freeze_e2_r17_m3r4_final_contract.py"),
    }
    return final


def build_preflight_authorization(*, contract_path: Path, contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-actual-path-preflight-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_AUTH_STATUS,
        "contract_sha256": sha256_file(contract_path),
        "authority": {
            "scientific_experiment": False,
            "provider_io": False,
            "actor_measurement": False,
            "updater": False,
            "analysis": False,
        },
        "execution_scope": {
            "scientific_object": contract["scientific_object"],
            "allowed_task_ids": list(TASK_IDS),
            "state_ids": ["ff_r1", "ff_r2"],
            "actor_replicates": [1, 2],
            "logical_units": 72,
            "completed_unit_replay": False,
            "automatic_retry": False,
            "partial_effect_read": False,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "max_turns": MAX_TURNS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "provider_budget": structural_provider_budget(),
        },
        "next_gate": "RUN_REAL_ACTOR_PATH_WITH_STOP_BEFORE_PROVIDER_IO_ONLY",
        "measurement_authorization_created": False,
        "scientific_outcomes_read": False,
    }


def freeze(*, draft_path: Path, identity_path: Path, contract_output: Path, preflight_authorization_output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if contract_output.exists() or preflight_authorization_output.exists():
        raise RuntimeError("M3R4 final freeze refuses to overwrite an existing contract/authorization")
    if not identity_path.is_file():
        raise RuntimeError("M3R4 fresh identity artifact missing")

    contract = build_final_contract(draft_path=draft_path, identity_path=identity_path)
    atomic_json(contract_output, contract)
    try:
        validated = validate_final_contract(contract_output)
        preflight = build_preflight_authorization(contract_path=contract_output, contract=validated)
        atomic_json(preflight_authorization_output, preflight)
        validate_execution_authorization(
            contract_path=contract_output,
            authorization_path=preflight_authorization_output,
            stop_before_provider_io=True,
        )
    except BaseException:
        contract_output.unlink(missing_ok=True)
        preflight_authorization_output.unlink(missing_ok=True)
        raise
    return contract, preflight


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--contract-output", type=Path, required=True)
    parser.add_argument("--preflight-authorization-output", type=Path, required=True)
    args = parser.parse_args()

    contract, preflight = freeze(
        draft_path=args.draft,
        identity_path=args.identity,
        contract_output=args.contract_output,
        preflight_authorization_output=args.preflight_authorization_output,
    )
    print(
        json.dumps(
            {
                "status": "FROZEN_M3R4_FINAL_CONTRACT_AND_PREFLIGHT_AUTHORIZATION",
                "contract_path": str(args.contract_output),
                "contract_sha256": sha256_file(args.contract_output),
                "preflight_authorization_path": str(args.preflight_authorization_output),
                "preflight_authorization_sha256": sha256_file(args.preflight_authorization_output),
                "fresh_identity_sha256": contract["fresh_model_identity"]["sha256"],
                "preflight_status": preflight["status"],
                "provider_io_authorized": False,
                "measurement_authorization_created": False,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
