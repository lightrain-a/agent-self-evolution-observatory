#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import (
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)
from scripts.run_e2_r17_deepseek_v2_repair2_continuation import (
    ARMS,
    REPLICATES,
    load_stream_pools,
    validate_contract_auth,
)
from scripts.run_e2_r17_v31_provider_runtime_pilot import validate_updater_runtime
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import load_json, sha_file


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--review-summary", type=Path)
    parser.add_argument("--stage", choices=("draft", "frozen"), required=True)
    args = parser.parse_args()

    contract_path = resolve(args.contract)
    contract = load_json(contract_path)
    if args.stage == "draft":
        require(contract.get("status") == "DRAFT_PENDING_DUAL_REPAIR2_REVIEW", "Repair2 draft status drift")
        require(args.authorization is None, "draft preflight must not accept scientific authorization")
        authority = contract.get("authority") or {}
        require(authority and all(value is False for value in authority.values()), "draft authority must remain all false")
        if args.review_summary:
            review_path = resolve(args.review_summary)
            review = load_json(review_path)
            require(review.get("all_pass_to_separately_authorized_repair2") is True, "dual review did not authorize freezing")
            require(review.get("draft_contract_sha256") == sha_file(contract_path), "dual review draft binding drift")
    else:
        require(args.authorization is not None, "frozen preflight requires authorization")
        auth_path = resolve(args.authorization)
        contract, _ = validate_contract_auth(contract_path, auth_path)

    env_file = contract.get("env_file")
    require(isinstance(env_file, str) and env_file.strip(), "contract env_file missing/empty")
    env_path = Path(env_file)
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    require(env_path.is_file(), f"contract env_file not found: {env_path}")

    updater_python, _ = validate_updater_runtime({"runtime": contract["updater_runtime"], "mindmemos": contract["mindmemos"]})
    actor_python, _ = validate_actor_runtime({"runtime": contract["actor_runtime"]})
    require(Path(sys.executable) == updater_python, f"preflight must run under updater runtime: observed={sys.executable} expected={updater_python}")

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")

    repair1 = contract["repair1_parent"]
    repair1_contract = ROOT / repair1["contract_path"]
    repair1_auth = ROOT / repair1["authorization_path"]
    require(repair1_contract.is_file() and sha_file(repair1_contract) == repair1["contract_sha256"], "Repair1 contract drift")
    require(repair1_auth.is_file() and sha_file(repair1_auth) == repair1["authorization_sha256"], "Repair1 authorization drift")

    compatibility_item = contract["compatibility_manifest"]
    inherited = validate_compatibility_manifest(
        path=ROOT / compatibility_item["path"],
        expected_sha=compatibility_item["sha256"],
        repair1_contract_sha=repair1["contract_sha256"],
        repair1_authorization_sha=repair1["authorization_sha256"],
        heldout_task_ids=contract["heldout"]["task_ids"],
    )
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows(inherited, streams=contract["streams"], quarantine=quarantine, require_complete=False)
    require(len(inherited) == 14, "preflight requires exactly 14 frozen inherited pairs")
    require(f"{quarantine['stream_id']}/rep{int(quarantine['replicate_id'])}" not in {row["unit_id"] for row in inherited}, "quarantine leaked into inherited set")

    failure_item = contract["superseding_failure_analysis"]
    failure_path = ROOT / failure_item["path"]
    require(failure_path.is_file() and sha_file(failure_path) == failure_item["sha256"], "superseding failure analysis drift")
    failure = load_json(failure_path)
    require(failure.get("primary_classification") == "IMPLEMENTATION / UPDATER_PATCH_APPLY_FAILURE", "failure classification drift")
    require(failure.get("provider_response_ambiguity") is False and failure.get("scientific_belief_update") == "NONE", "failure semantics drift")

    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    support = load_json(ROOT / contract["e1_a_support"]["path"])
    for stream in contract["streams"]:
        require(len(load_stream_pools(contract, stream, split, support)) == 8, f"pool count drift: {stream}")

    require(len(contract["streams"]) == 12 and len(REPLICATES) == 4 and len(ARMS) == 2, "design cardinality drift")
    require(int(contract["replication"]["paired_replicate_units"]) == 48 and int(contract["replication"]["learned_states"]) == 96, "replication summary drift")
    require(len(contract["heldout"]["task_ids"]) == 18, "heldout task count drift")
    require(int(contract["updater"]["max_parse_attempts"]) == 2, "max_parse_attempts must be 2")
    require(int(contract["budget"]["max_provider_calls_per_unit"]) == 11, "provider unit budget must be 11")
    require(int(contract["budget"]["max_provider_calls_per_state"]) == 191, "state budget must be 191")
    require(int(contract["budget"]["hard_max_provider_calls_structural"]) == 96 * 191, "budget structure drift")
    require(int(contract["actor"]["max_turns"]) == 10 and int(contract["actor"]["max_output_tokens"]) == 8192, "actor protocol drift")
    require(contract["updater"]["provider_retry_limit"] == 0 and contract["actor"]["provider_retry_limit"] == 0, "provider retry drift")
    require(contract["updater"]["requested_model"] == "deepseek-v4-pro" and contract["actor"]["requested_model"] == "deepseek-v4-pro", "scientific model drift")

    identity_item = contract["model_identity"]
    identity_path = ROOT / identity_item["path"]
    require(identity_path.is_file() and sha_file(identity_path) == identity_item["sha256"], "fresh model identity drift")
    identity = load_json(identity_path)
    require(identity.get("status") == identity_item["required_status"], "fresh model identity not qualified")
    model_row = identity["requested_and_resolved"]["deepseek-v4-pro"]
    require(model_row["requested"] == "deepseek-v4-pro", "requested model identity drift")
    require(model_row["resolved"] == contract["updater"]["resolved_model"] == contract["actor"]["resolved_model"], "resolved family drift")
    qualification_path = ROOT / identity_item["qualification_path"]
    require(qualification_path.is_file() and sha_file(qualification_path) == identity_item["qualification_sha256"], "fresh DeepSeek qualification drift")
    qualification = load_json(qualification_path)
    deep_rows = [row for row in qualification.get("models") or [] if row.get("requested_model") == "deepseek-v4-pro"]
    require(len(deep_rows) == 1 and deep_rows[0].get("status") == "PASS", "fresh DeepSeek identity call not PASS")
    deep = deep_rows[0]
    require(deep.get("resolved_model") == model_row["resolved"], "fresh DeepSeek resolved suffix drift")
    require(int(deep.get("max_output_tokens")) == 8192 and deep.get("thinking_requested") == "disabled", "fresh DeepSeek output/thinking qualification drift")
    require(int(deep.get("provider_retry_limit")) == 0 and deep.get("hidden_provider_retry_used") is False, "identity provider retry drift")
    require(deep.get("benchmark_data_accessed") is False and deep.get("scientific_outcome") is False, "identity qualification crossed scientific boundary")

    process_text = subprocess.run(
        ["ps", "-eo", "pid,ppid,etime,stat,cmd"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    active = [
        line for line in process_text.splitlines()
        if ("run_e2_r17_deepseek_v2_repair2_continuation.py" in line or "run_e2_r17_actor_pool.py" in line)
        and str(Path(__file__).name) not in line
    ]
    require(not active, f"active duplicate Repair2/actor process: {active}")

    run_root = Path(contract["run_root"])
    require(not run_root.exists() or not any(run_root.rglob("*")), f"Repair2 run root not fresh: {run_root}")
    valid_path = Path(contract["valid_replicate_manifest"]["path"])
    require(not valid_path.exists(), f"valid manifest already exists before Repair2 execution: {valid_path}")

    print("PREFLIGHT_PASS")
    print("stage", args.stage)
    print("updater_python", updater_python)
    print("actor_python", actor_python)
    print("streams", 12, "replicates", 4, "valid_pairs", 48, "states", 96, "heldout_rollouts", 1728)
    print("inherited_pairs", len(inherited), "fresh_pairs", 34)
    print("quarantine", quarantine["status"])
    print("max_parse_attempts", 2, "updater_budget", 11, "state_budget", 191, "actor_max_turns", 10)
    print("run_root", run_root)
    print("contract_sha", sha_file(contract_path))
    if args.stage == "frozen":
        print("authorization_sha", sha_file(resolve(args.authorization)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
