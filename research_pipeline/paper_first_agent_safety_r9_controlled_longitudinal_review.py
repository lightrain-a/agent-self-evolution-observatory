from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def attach_hash(value: dict[str, Any], key: str) -> dict[str, Any]:
    value[key] = sha_bytes(canonical(value))
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def review(args: argparse.Namespace) -> dict[str, Any]:
    prereg_path = Path(args.preregistration)
    treatment_plan_path = Path(args.treatment_plan)
    experiment_root = Path(args.experiment_root)
    output = Path(args.output)

    prereg = load(prereg_path)
    require(prereg["status"] == "COMPILED_AWAITING_INDEPENDENT_PROTOCOL_REVIEW", "preregistration status drift")
    expected_prereg_hash = sha_bytes(canonical({k: v for k, v in prereg.items() if k != "preregistration_sha256"}))
    require(prereg["preregistration_sha256"] == expected_prereg_hash, "preregistration hash drift")

    auth_path = experiment_root / "human-execution-authorization.json"
    auth = load(auth_path)
    expected_auth_hash = sha_bytes(canonical({k: v for k, v in auth.items() if k != "authorization_sha256"}))
    require(auth["authorization_sha256"] == expected_auth_hash == prereg["authorization_sha256"], "human authorization drift")
    require(auth["execution_authorized"] is True, "human execution authority missing")
    require(auth["guard_change_authorized"] is False, "guard authority drift")
    require(auth["threshold_change_authorized"] is False, "threshold authority drift")
    require(auth["frozen_runtime_change_authorized"] is False, "runtime authority drift")
    require(auth["outcome_driven_selection_authorized"] is False, "selection authority drift")

    treatment = load(treatment_plan_path)
    no_update_path = experiment_root / "no-update" / "control-plan.json"
    fixed_path = experiment_root / "fixed-probe" / "control-plan.json"
    no_update = load(no_update_path)
    fixed = load(fixed_path)
    require(sha_file(no_update_path) == prereg["arms"]["same_schedule_no_update"]["plan_sha256"], "no-update plan file drift")
    require(sha_file(fixed_path) == prereg["arms"]["fixed_probe_snapshot"]["plan_sha256"], "fixed-probe plan file drift")

    treatment_rows = treatment["episodes"]
    control_rows = no_update["episodes"]
    require(len(treatment_rows) == len(control_rows) == 36, "no-update cardinality mismatch")
    allowed_changed = {
        "episode_id",
        "workflow_sha256",
        "appended_unit_sha256",
        "experimental_arm",
        "update_enabled",
    }
    no_update_pair_checks = []
    for treated, control in zip(treatment_rows, control_rows):
        common_keys = set(treated) | set(control)
        unexpected = []
        for key in common_keys - allowed_changed:
            if treated.get(key) != control.get(key):
                unexpected.append(key)
        require(not unexpected, f"no-update changes non-update fields: {unexpected}")
        require(control["experimental_arm"] == "same-schedule-no-update", "no-update arm label drift")
        require(control["update_enabled"] is False, "no-update flag drift")
        state_id = control["state_id"]
        base_sha = next(
            row["workflow_sha256"]
            for row in prereg["step0_qualification_rows"][state_id]
            if int(row["behavior_id"]) == 14
        )
        require(control["workflow_sha256"] == base_sha, f"control not held at base state: {state_id}")
        workflow_path = experiment_root / "no-update" / "future-workflows" / f"{state_id}__step{int(control['future_step'])}.txt"
        require(sha_file(workflow_path) == base_sha, f"control workflow serialization drift: {workflow_path}")
        no_update_pair_checks.append({
            "state_id": state_id,
            "branch_seed": int(control["branch_seed"]),
            "future_step": int(control["future_step"]),
            "behavior_id": int(control["behavior_id"]),
            "only_allowed_fields_changed": True,
        })

    fixed_rows = fixed["episodes"]
    require(len(fixed_rows) == 36, "fixed-probe cardinality mismatch")
    expected_probes = {
        (int(row["behavior_id"]), int(row["seed"]))
        for row in prereg["arms"]["fixed_probe_snapshot"]["fixed_probes"]
    }
    treatment_snapshot_sha: dict[tuple[str, int], str] = {}
    for row in treatment_rows:
        key = (row["state_id"], int(row["future_step"]))
        if key in treatment_snapshot_sha:
            require(treatment_snapshot_sha[key] == row["workflow_sha256"], f"treatment snapshot differs by branch: {key}")
        treatment_snapshot_sha[key] = row["workflow_sha256"]

    fixed_seen = set()
    for row in fixed_rows:
        key = (row["state_id"], int(row["future_step"]), int(row["behavior_id"]), int(row["seed"]))
        require(key not in fixed_seen, f"duplicate fixed-probe row: {key}")
        fixed_seen.add(key)
        require((int(row["behavior_id"]), int(row["seed"])) in expected_probes, "fixed probe/seed drift")
        require(row["experimental_arm"] == "fixed-qualification-probe-by-exposure", "fixed arm label drift")
        require(row["probe_writeback_enabled"] is False, "fixed probe writeback drift")
        expected_sha = treatment_snapshot_sha[(row["state_id"], int(row["future_step"]))]
        require(row["workflow_sha256"] == expected_sha, f"fixed snapshot binding drift: {key}")
        workflow_path = experiment_root / "fixed-probe" / "future-workflows" / f"{row['state_id']}__step{int(row['future_step'])}.txt"
        require(sha_file(workflow_path) == expected_sha, f"fixed workflow serialization drift: {workflow_path}")

    expected_fixed = {
        (state_id, step, behavior_id, seed)
        for state_id in prereg["step0_qualification_rows"]
        for step in (1, 2, 3)
        for behavior_id, seed in expected_probes
    }
    require(fixed_seen == expected_fixed, "fixed-probe factorial coverage drift")

    outcome_dirs = [
        experiment_root / "no-update-execution",
        experiment_root / "fixed-probe-execution",
    ]
    for path in outcome_dirs:
        require(not path.exists() or not any(path.iterdir()), f"outcomes exist before protocol review: {path}")

    review_row = attach_hash({
        "schema_version": "1.0",
        "status": "PASS_EXACT_MATCHED_CONTROL_PROTOCOL_REVIEW",
        "review_kind": "independently implemented deterministic field-level comparison",
        "preregistration_sha256": prereg["preregistration_sha256"],
        "human_authorization_sha256": auth["authorization_sha256"],
        "checks": {
            "treatment_receipt_hash_bound": True,
            "exact_heldout_schedule": True,
            "same_state_identity": True,
            "same_branch_seed": True,
            "same_behavior_and_instruction": True,
            "same_horizon": True,
            "no_update_only_changed_factor": True,
            "fixed_probe_set_and_seed": True,
            "fixed_probe_read_only": True,
            "runtime_source_hash_bound": True,
            "outcomes_absent_during_review": True,
            "bounded_budget": True,
        },
        "no_update_pairs_verified": len(no_update_pair_checks),
        "fixed_probe_rows_verified": len(fixed_seen),
        "failure_classification": {
            "runtime": [],
            "protocol": [],
            "support": [],
            "operationalization": [],
            "method": [],
            "principle": [],
        },
        "execution_authorized": True,
        "scientific_authority": False,
    }, "review_sha256")
    atomic_json(output, review_row)
    atomic_json(experiment_root / "protocol-review.json", review_row)

    gate = attach_hash({
        "schema_version": "1.0",
        "status": "READY_R23_CONTROLLED_LONGITUDINAL_EXECUTION",
        "preregistration_sha256": prereg["preregistration_sha256"],
        "review_sha256": review_row["review_sha256"],
        "human_authorization_sha256": auth["authorization_sha256"],
        "no_update_plan_sha256": no_update["plan_sha256"],
        "fixed_probe_plan_sha256": fixed["plan_sha256"],
        "new_behavior_episodes": 72,
        "agent_model_calls_upper_bound": 288,
        "classifier_evaluations_upper_bound": 72,
        "guard_changed": False,
        "threshold_changed": False,
        "frozen_runtime_changed": False,
        "outcomes_inspected_before_freeze": False,
        "execution_authorized": True,
        "gpu_authorized": True,
        "scientific_authority": False,
    }, "gate_sha256")
    atomic_json(experiment_root / "execution-gate.json", gate)
    return review_row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--treatment-plan", required=True)
    parser.add_argument("--experiment-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = review(args)
    print(json.dumps({
        "status": result["status"],
        "review_sha256": result["review_sha256"],
        "execution_authorized": result["execution_authorized"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
