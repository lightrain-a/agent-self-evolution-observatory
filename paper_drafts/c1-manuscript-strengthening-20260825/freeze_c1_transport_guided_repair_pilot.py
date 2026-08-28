from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PILOT_CONTRACT = HERE / "c1-transport-guided-repair-pilot-contract-20260828.json"
DATA_PREFLIGHT = HERE / "c1-transport-guided-repair-data-preflight-20260828.json"
B10_CONTRACT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
OUTPUT = HERE / "c1-transport-guided-repair-pilot-freeze-20260828.json"
SALT = "C1-TGRP-PILOT-v1"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def selection_hash(intent_template_id: int, future_task: int) -> str:
    return hashlib.sha256(f"{SALT}|{intent_template_id}|{future_task}".encode("utf-8")).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    contract = json.loads(PILOT_CONTRACT.read_text(encoding="utf-8"))
    preflight = json.loads(DATA_PREFLIGHT.read_text(encoding="utf-8"))
    b10 = json.loads(B10_CONTRACT.read_text(encoding="utf-8"))
    require(preflight["status"] == "OFFLINE_PACKET_REPLAY_PREFLIGHT_PASS_NO_EXECUTION_AUTHORITY", "data preflight not qualified")
    require(len(b10["task_units"]) == 36, "B10 support drift")
    require(not any(contract["authority"].values()), "design artifact unexpectedly carries authority")

    groups: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for unit in b10["task_units"]:
        groups[int(unit["intent_template_id"])].append(unit)
    require(len(groups) == 13, "intent-template support drift")

    pilot_units: list[dict[str, Any]] = []
    for intent_template_id in sorted(groups):
        candidates = groups[intent_template_id]
        selected = min(candidates, key=lambda row: selection_hash(intent_template_id, int(row["future_task"])))
        pilot_units.append(
            {
                "future_task": int(selected["future_task"]),
                "selected_source_task": int(selected["selected_source_task"]),
                "intent_template_id": intent_template_id,
                "selection_hash": selection_hash(intent_template_id, int(selected["future_task"])),
                "task_prompt_sha256": selected["task_prompt_sha256"],
                "system_instruction_sha256": selected["system_instruction_sha256"],
                "current_state_sha256": selected["current_state_sha256"],
                "success_memory_wrapper_sha256": selected["memory_wrappers"]["success"]["sha256"],
                "failure_memory_wrapper_sha256": selected["memory_wrappers"]["failure"]["sha256"],
            }
        )

    pilot_ids = {row["future_task"] for row in pilot_units}
    holdout_units = [
        {
            "future_task": int(unit["future_task"]),
            "selected_source_task": int(unit["selected_source_task"]),
            "intent_template_id": int(unit["intent_template_id"]),
            "task_prompt_sha256": unit["task_prompt_sha256"],
            "system_instruction_sha256": unit["system_instruction_sha256"],
            "current_state_sha256": unit["current_state_sha256"],
            "success_memory_wrapper_sha256": unit["memory_wrappers"]["success"]["sha256"],
            "failure_memory_wrapper_sha256": unit["memory_wrappers"]["failure"]["sha256"],
        }
        for unit in sorted(b10["task_units"], key=lambda row: int(row["future_task"]))
        if int(unit["future_task"]) not in pilot_ids
    ]
    require(len(pilot_units) == 13 and len(holdout_units) == 23, "pilot/holdout partition drift")
    require(len(pilot_ids) == 13, "pilot duplicate tasks")
    require(pilot_ids.isdisjoint({row["future_task"] for row in holdout_units}), "pilot/holdout overlap")

    model = b10["model"]
    require(model["requested"] == "doubao-seed-2.0-mini", "model request drift")
    require(model["expected_resolved"] == "doubao-seed-2-0-mini-260215", "model resolution drift")

    rollouts = 4
    arms = ["A0_NATIVE", "A1_MEMORY_BLIND_DECISION_CHECK", "A2_MEMORY_USE_CHECK"]
    branches = ["success_memory", "failure_memory"]
    pilot_calls = len(pilot_units) * len(arms) * len(branches) * rollouts
    confirmatory_calls = len(holdout_units) * len(arms) * len(branches) * rollouts
    require(pilot_calls == 312 and confirmatory_calls == 552, "call geometry drift")

    output = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TRANSPORT_GUIDED_REPAIR_PILOT_FREEZE",
        "paper_id": contract["paper_id"],
        "experiment_id": contract["experiment_id"],
        "generated_at": "2026-08-28",
        "status": "PILOT_PROTOCOL_FROZEN_EXECUTION_LOCKED",
        "selection": {
            "selection_input": "B10 contract metadata only: future_task, intent_template_id, selected_source_task and content hashes; no B10 action or terminal outcome enters selection",
            "rule": "Partition the 36 replayable states by intent_template_id and select exactly one state per template using the lexicographically smallest sha256(SALT|intent_template_id|future_task).",
            "salt": SALT,
            "intent_templates": len(groups),
            "pilot_units": len(pilot_units),
            "confirmatory_holdout_units": len(holdout_units),
            "pilot_ids_sha256": sha_json(sorted(pilot_ids)),
            "holdout_ids_sha256": sha_json(sorted(row["future_task"] for row in holdout_units)),
            "pilot": pilot_units,
            "confirmatory_holdout": holdout_units,
        },
        "execution_geometry": {
            "arms": arms,
            "branches": branches,
            "rollouts_per_branch_per_arm_per_state": rollouts,
            "pilot_provider_calls_if_authorized": pilot_calls,
            "confirmatory_provider_calls_if_later_authorized": confirmatory_calls,
            "pilot_and_confirmatory_are_disjoint": True,
            "pilot_never_pooled_into_confirmatory_inference": True
        },
        "model": {
            "requested": model["requested"],
            "expected_resolved": model["expected_resolved"],
            "temperature": model["temperature"],
            "max_output_tokens": model["max_output_tokens"],
            "thinking": model["thinking"],
            "provider_retries": 0,
            "substitution_allowed": False
        },
        "primary_observable": {
            "per_state_per_arm": "U_i,a = empirical total-variation distance between success-memory and failure-memory first-action action-signature distributions using four rollouts per branch",
            "memory_specific_contrast": "D_i = U_i,A2 - U_i,A1",
            "native_contrast": "N_i = U_i,A2 - U_i,A0",
            "why_A1_primary_control": "A1 matches the additional decision-check structure while remaining memory-blind; A2-A1 therefore tests memory-specific uptake beyond generic extra decision checking."
        },
        "pilot_gate": {
            "role": "screen identifiability/signal only; not a scientific confirmatory claim",
            "go_full_if_all": [
                "all packet and parser realization checks pass with no arm-dependent missingness",
                "mean(U_A2) >= 0.20, reusing the previously frozen B10 practical first-action TV floor",
                "mean(D_i) >= 0.10, half of the previously frozen B10 practical TV floor and positive in at least 8 of 13 pilot states",
                "mean(N_i) > 0",
                "A1 does not absorb the A2 effect: mean(D_i) must remain >= 0.10"
            ],
            "hold_or_stop_if": [
                "A1 and A2 move similarly",
                "A2 manipulation is not realized or packet invariance fails",
                "mean(D_i) < 0.10",
                "fewer than 8 of 13 pilot states have D_i > 0",
                "provider/model support changes the frozen model identity or response semantics"
            ],
            "pilot_results_forbidden_from_confirmatory_pool": True
        },
        "prospective_confirmatory_gate_if_pilot_passes": {
            "data": "23 frozen holdout states only",
            "primary_statistic": "mean(D_i) over the 23 holdout states",
            "practical_margin": 0.10,
            "absolute_A2_mean_U_floor": 0.20,
            "test": "one-sided paired sign-flip/randomization test over D_i under arm-label exchange at the state level",
            "repetitions": 100000,
            "seed": 20260828,
            "p_lt": 0.05,
            "pass_requires": [
                "mean(D_i) >= 0.10",
                "mean(U_A2) >= 0.20",
                "one-sided paired sign-flip p < 0.05",
                "all upstream packet invariance checks pass",
                "no outcome-conditioned replacement or top-up"
            ],
            "terminal_outcome": "not part of this first-action confirmatory gate; only reopen terminal utility intervention if uptake is first established"
        },
        "missingness": {
            "provider_retries": 0,
            "replacement_units": False,
            "top_up_failed_units": False,
            "arm_dependent_missingness": "HOLD and diagnose; do not impute or replace"
        },
        "source_bindings": {
            "pilot_contract": {"path": str(PILOT_CONTRACT), "sha256": sha_file(PILOT_CONTRACT)},
            "data_preflight": {"path": str(DATA_PREFLIGHT), "sha256": sha_file(DATA_PREFLIGHT)},
            "b10_contract": {"path": str(B10_CONTRACT), "sha256": sha_file(B10_CONTRACT)}
        },
        "scientific_boundary": "The pilot tests whether the stage diagnosis predicts an actionable post-retrieval uptake manipulation. Even a pass does not establish downstream utility, a universal mediator, or a novel utilization algorithm.",
        "authority": {
            "scientific": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "submission": False
        }
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "pilot_units": len(pilot_units), "holdout_units": len(holdout_units), "pilot_calls_if_authorized": pilot_calls, "provider_calls_executed": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
