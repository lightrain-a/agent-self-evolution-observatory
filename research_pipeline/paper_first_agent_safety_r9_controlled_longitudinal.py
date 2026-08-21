from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = "1.0"
EXPECTED_TREATMENT = {
    "contract_file_sha256": "2e1a156080e32bc450aa00a024ab3bc23537614332748c064d96a2f679e9bdd5",
    "plan_file_sha256": "966ecd38d6906d352737f30b50c0a1331e3bdf89ec7f4310bf56c82f243a2a2d",
    "future_journal_sha256": "22eef2239ff1273f2e251074d12e3dabe0210a029c7d5037c99fd695cac45117",
    "future_summary_sha256": "2f07fbabe5469a75ca594045129f37a0fb3db113917cc7df3f2b076990dd6a49",
}
QWEN_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"
HARMBENCH_REVISION = "0cd31cdc8b53209dd5b153b20026ff085901bb14"
QUALIFICATION_PROBES = (14, 16, 18)
CANONICAL_LAYERS = ("runtime", "protocol", "support", "operationalization", "method", "principle")


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
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def copy_exact(source: Path, target: Path, expected_sha: str) -> None:
    require(source.is_file(), f"missing source: {source}")
    raw = source.read_bytes()
    require(sha_bytes(raw) == expected_sha, f"source hash drift: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    require(sha_file(target) == expected_sha, f"serialized hash drift: {target}")


def qualification_index(journal_paths: list[Path]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in journal_paths:
        for episode_id, row in (load(path).get("episodes") or {}).items():
            require(episode_id not in index, f"duplicate qualification episode: {episode_id}")
            index[episode_id] = row
    return index


def build(args: argparse.Namespace) -> dict[str, Any]:
    treatment_root = Path(args.treatment_root)
    treatment_execution = Path(args.treatment_execution)
    experiment_root = Path(args.experiment_root)
    receipt_path = Path(args.receipt)
    output = Path(args.output)
    runtime_source = Path(args.runtime_source)

    contract_path = treatment_root / "frozen-future-contract.json"
    plan_path = treatment_root / "future-plan.json"
    journal_path = treatment_execution / "runtime-journal.json"
    summary_path = treatment_execution / "future-outcomes-summary.json"
    for key, path in (
        ("contract_file_sha256", contract_path),
        ("plan_file_sha256", plan_path),
        ("future_journal_sha256", journal_path),
        ("future_summary_sha256", summary_path),
    ):
        require(sha_file(path) == EXPECTED_TREATMENT[key], f"treatment binding drift: {key}")

    receipt = load(receipt_path)
    require(all(receipt["identity"][key] == value for key, value in EXPECTED_TREATMENT.items()),
            "receipt no longer binds expected treatment")
    require(tuple((receipt.get("failure_classification") or {}).keys()) == CANONICAL_LAYERS,
            "failure taxonomy drift")

    contract = load(contract_path)
    treatment_plan = load(plan_path)
    states = {row["state_id"]: row for row in contract["selected_states"]}
    require(list(states) == ["map-P2-A", "map-V4-C1", "reddit-A", "reddit-B"], "state order drift")
    treatment_rows = treatment_plan["episodes"]
    require(len(treatment_rows) == 36, "treatment plan cardinality drift")

    base_texts: dict[str, bytes] = {}
    for state_id, row in states.items():
        source = Path(row["source_path"])
        raw = source.read_bytes()
        require(sha_bytes(raw) == row["workflow_sha256"], f"base-state drift: {state_id}")
        base_texts[state_id] = raw

    qindex = qualification_index([Path(x) for x in args.qualification_journal])
    support = receipt["static_current_safety"]["states"]
    probe_seed: dict[int, int] = {}
    step0_rows: dict[str, list[dict[str, Any]]] = {}
    for state_id in states:
        rows = []
        for episode_id in support[state_id]["episode_ids"]:
            require(episode_id in qindex, f"missing qualification episode: {episode_id}")
            row = qindex[episode_id]
            require(row["state_id"] == state_id and row["harmbench_prediction"] == 0,
                    f"qualification support drift: {episode_id}")
            behavior_id = int(row["behavior_id"])
            seed = int(row["seed"])
            require(behavior_id in QUALIFICATION_PROBES, f"qualification probe drift: {behavior_id}")
            if behavior_id in probe_seed:
                require(probe_seed[behavior_id] == seed, f"qualification seed mismatch: {behavior_id}")
            probe_seed[behavior_id] = seed
            rows.append({
                "episode_id": episode_id,
                "behavior_id": behavior_id,
                "seed": seed,
                "workflow_sha256": row["workflow_sha256"],
                "harmbench_prediction": 0,
            })
        step0_rows[state_id] = sorted(rows, key=lambda x: x["behavior_id"])
    require(tuple(sorted(probe_seed)) == QUALIFICATION_PROBES, "qualification probe set drift")

    treatment_by_key = {
        (row["state_id"], int(row["branch_seed"]), int(row["future_step"])): row
        for row in treatment_rows
    }
    schedule_manifest = []
    for row in treatment_rows:
        schedule_manifest.append({
            "state_id": row["state_id"],
            "branch_seed": int(row["branch_seed"]),
            "future_step": int(row["future_step"]),
            "behavior_id": int(row["behavior_id"]),
            "seed": int(row["seed"]),
            "treatment_episode_id": row["episode_id"],
            "treatment_workflow_sha256": row["workflow_sha256"],
        })

    no_update_rows = []
    no_update_root = experiment_root / "no-update"
    for row in treatment_rows:
        state_id = row["state_id"]
        spec = dict(row)
        spec.update({
            "episode_id": f"r23noupdate__{state_id}__branch{int(row['branch_seed'])}__step{int(row['future_step'])}__b{int(row['behavior_id'])}",
            "workflow_sha256": states[state_id]["workflow_sha256"],
            "appended_unit_sha256": None,
            "experimental_arm": "same-schedule-no-update",
            "update_enabled": False,
        })
        no_update_rows.append(spec)
    for state_id, state in states.items():
        for step in (1, 2, 3):
            target = no_update_root / "future-workflows" / f"{state_id}__step{step}.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(base_texts[state_id])
            require(sha_file(target) == state["workflow_sha256"], f"no-update serializer drift: {state_id}:{step}")

    fixed_rows = []
    fixed_root = experiment_root / "fixed-probe"
    for state_id in states:
        for exposure_step in (1, 2, 3):
            treatment_example = treatment_by_key[(state_id, 11, exposure_step)]
            expected_snapshot_sha = treatment_example["workflow_sha256"]
            source = treatment_root / "future-workflows" / f"{state_id}__step{exposure_step}.txt"
            target = fixed_root / "future-workflows" / f"{state_id}__step{exposure_step}.txt"
            copy_exact(source, target, expected_snapshot_sha)
            for behavior_id in QUALIFICATION_PROBES:
                seed = probe_seed[behavior_id]
                fixed_rows.append({
                    "phase": "future",
                    "episode_id": f"r23fixedprobe__{state_id}__exposure{exposure_step}__b{behavior_id}__s{seed}",
                    "state_id": state_id,
                    "site_stratum": states[state_id]["site_stratum"],
                    "behavior_id": behavior_id,
                    "seed": seed,
                    "branch_seed": seed,
                    "future_step": exposure_step,
                    "workflow_sha256": expected_snapshot_sha,
                    "appended_unit_sha256": treatment_example["appended_unit_sha256"],
                    "execution_condition": "R23_CONTROLLED_LONGITUDINAL_GATES_PASS",
                    "max_agent_model_calls": 4,
                    "classifier_model_evaluations": 1,
                    "experimental_arm": "fixed-qualification-probe-by-exposure",
                    "update_enabled": True,
                    "probe_writeback_enabled": False,
                })

    budget = {
        "new_arms": 2,
        "episodes_per_arm": 36,
        "new_behavior_episodes": 72,
        "agent_model_calls_upper_bound": 288,
        "classifier_evaluations_upper_bound": 72,
        "combined_model_evaluations_upper_bound": 360,
        "reruns_allowed": False,
    }
    common_plan = {
        "schema_version": SCHEMA,
        "status": "R23_CONTROL_PLAN_FROZEN",
        "source_treatment_plan_sha256": sha_file(plan_path),
        "budget_per_arm": {
            "episodes": 36,
            "agent_model_calls_upper_bound": 144,
            "classifier_evaluations_upper_bound": 36,
            "model_evaluations_upper_bound": 180,
        },
        "scientific_authority": False,
    }
    no_update_plan = attach_hash({**common_plan, "arm": "same-schedule-no-update", "episodes": no_update_rows}, "plan_sha256")
    fixed_plan = attach_hash({**common_plan, "arm": "fixed-qualification-probe-by-exposure", "episodes": fixed_rows}, "plan_sha256")
    atomic_json(no_update_root / "control-plan.json", no_update_plan)
    atomic_json(fixed_root / "control-plan.json", fixed_plan)

    auth = attach_hash({
        "schema_version": SCHEMA,
        "status": "HUMAN_EXECUTION_AUTHORITY_RECORDED",
        "authority_source": "user instruction in active project conversation",
        "directive": "感觉还是有很大差异的，你继续补充实验吧，可以参考他的实验设计。",
        "scope": [
            "same-schedule no-update matched control",
            "fixed-probe read-only snapshot panel",
        ],
        "bounded_budget": budget,
        "guard_change_authorized": False,
        "threshold_change_authorized": False,
        "frozen_runtime_change_authorized": False,
        "outcome_driven_selection_authorized": False,
        "execution_authorized": True,
        "scientific_authority": False,
    }, "authorization_sha256")
    atomic_json(experiment_root / "human-execution-authorization.json", auth)

    prereg = {
        "schema_version": SCHEMA,
        "status": "COMPILED_AWAITING_INDEPENDENT_PROTOCOL_REVIEW",
        "design_id": "AGENT-SAFETY-R9-R23-CONTROLLED-LONGITUDINAL",
        "source_receipt": str(receipt_path),
        "source_bindings": {
            **EXPECTED_TREATMENT,
            "receipt_sha256": sha_file(receipt_path),
            "runtime_source": str(runtime_source),
            "runtime_source_sha256": sha_file(runtime_source),
            "qwen_revision": QWEN_REVISION,
            "harmbench_revision": HARMBENCH_REVISION,
        },
        "arms": {
            "observed_persistent_update_heldout_schedule": {
                "episodes": 36,
                "source": "frozen R9 treatment receipt",
            },
            "same_schedule_no_update": {
                "episodes": 36,
                "plan": str(no_update_root / "control-plan.json"),
                "plan_sha256": sha_file(no_update_root / "control-plan.json"),
                "changed_factor": "workflow snapshot remains at step-0 base state",
            },
            "fixed_probe_snapshot": {
                "new_episodes": 36,
                "reused_step0_episodes": 12,
                "plan": str(fixed_root / "control-plan.json"),
                "plan_sha256": sha_file(fixed_root / "control-plan.json"),
                "fixed_probes": [{"behavior_id": k, "seed": probe_seed[k]} for k in sorted(probe_seed)],
                "exposure_steps": [0, 1, 2, 3],
                "probe_writeback": False,
            },
        },
        "exact_heldout_schedule_manifest": schedule_manifest,
        "step0_qualification_rows": step0_rows,
        "pre_registered_analysis": {
            "primary": {
                "comparison": "persistent-update versus same-schedule-no-update",
                "unit": "state-by-branch trajectory",
                "outcome": "branch_has_first_violation_by_step_3",
                "report": [
                    "paired treatment-only event branches",
                    "paired control-only event branches",
                    "paired equal branches",
                    "state-stratified first-event timing",
                ],
            },
            "secondary": {
                "comparison": "same qualification probe set over exposure steps 0,1,2,3",
                "unit": "state-by-fixed-probe trajectory",
                "outcome": "first exposure step with evaluator-classified violation",
                "report": [
                    "violations by exposure step",
                    "trajectories with first violation",
                    "state and probe localization",
                ],
            },
            "population_hazard_estimate": False,
            "iid_assumption": False,
            "automatic_claim_upgrade": False,
        },
        "failure_semantics": {
            "layers": list(CANONICAL_LAYERS),
            "support_failure_is_scientific_failure": False,
        },
        "prohibitions": [
            "No guard change.",
            "No threshold change.",
            "No frozen runtime change.",
            "No state, branch, probe, schedule, or horizon selection after outcomes.",
            "No rerun of completed episodes.",
            "No population hazard claim.",
        ],
        "budget": budget,
        "authorization_sha256": auth["authorization_sha256"],
        "review_required": True,
        "execution_authorized": False,
        "scientific_authority": False,
    }
    attach_hash(prereg, "preregistration_sha256")
    atomic_json(output, prereg)
    atomic_json(experiment_root / "preregistration.json", prereg)
    return prereg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treatment-root", required=True)
    parser.add_argument("--treatment-execution", required=True)
    parser.add_argument("--experiment-root", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--runtime-source", required=True)
    parser.add_argument("--qualification-journal", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = build(args)
    print(json.dumps({
        "status": result["status"],
        "preregistration_sha256": result["preregistration_sha256"],
        "new_behavior_episodes": result["budget"]["new_behavior_episodes"],
        "execution_authorized": result["execution_authorized"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
