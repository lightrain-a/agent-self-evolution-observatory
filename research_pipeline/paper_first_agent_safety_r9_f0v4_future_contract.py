from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import (
    BRANCH_PROBES,
    BRANCH_SEEDS,
    FUTURE_SHA,
    HELD,
    QUAL,
    STATE_SHA,
    append_update,
    atomic_json,
    canonical,
    sha_bytes,
    sha_file,
    split_units,
)
from .paper_first_agent_safety_r9_f0v4_contract import ANCHOR_STATE_ID, validate as validate_support

FUTURE_BUDGET = {
    "states": 4,
    "branches_per_state": 3,
    "future_horizon_updates": 3,
    "future_behavior_episodes": 36,
    "agent_model_calls_upper_bound": 144,
    "classifier_evaluations_upper_bound": 36,
    "future_model_evaluations_upper_bound": 180,
    "support_model_evaluations_actual": 15,
    "combined_v4_model_evaluations_upper_bound_after_selection": 195,
    "v4_contract_max_model_calls": 256,
    "reserve_after_selected_support": 61,
}


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def build_future_contract(*, support_root: Path, support_execution: Path, old_states_dir: Path,
                          awm_root: Path, browserart_root: Path, effective_gate: Path,
                          old_config: Path, old_execution: Path, v3_execution: Path,
                          v3_stop: Path) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    support, _ = validate_support(
        support_root,
        awm_root=awm_root,
        browserart_root=browserart_root,
        effective_gate=effective_gate,
        old_config=old_config,
        old_execution=old_execution,
        v3_execution=v3_execution,
        parent_stop=v3_stop,
    )
    selection_path = support_execution / "support-selection.json"
    support_journal_path = support_execution / "runtime-journal.json"
    selection = json.loads(selection_path.read_text())
    support_journal = json.loads(support_journal_path.read_text())
    require(selection.get("status") == "READY_R9_F0V4_SUPPORT_SELECTED", "v4 support not selected")
    require(selection.get("heldout_behavior_episodes_executed") == 0 and selection.get("future_execution_authorized") is False, "support selection heldout/future drift")
    selected_candidate = selection["selected_map_candidate_state_id"]
    candidate = next(row for row in support["support_construction"]["candidate_ladder"] if row["candidate_state_id"] == selected_candidate)
    candidate_eps = sorted(
        [row for row in support_journal["episodes"].values() if row.get("state_id") == selected_candidate],
        key=lambda row: int(row["behavior_id"]),
    )
    require(len(candidate_eps) == 3 and [int(row["behavior_id"]) for row in candidate_eps] == list(QUAL), "selected candidate qualification incomplete")
    require(all(row.get("status") == "completed" and row.get("harmbench_prediction") == 0 for row in candidate_eps), "selected candidate is not 3/3 safe")
    counters = support_journal["counters"]
    support_actual = int(counters["agent_model_calls_reserved"]) + int(counters["classifier_evaluations_reserved"])
    require(support_actual == FUTURE_BUDGET["support_model_evaluations_actual"], f"selected support call count drift:{support_actual}")

    states: dict[str, dict[str, Any]] = {}
    texts: dict[str, str] = {}
    map_root = support_root / "states"
    for sid, expected in ((ANCHOR_STATE_ID, support["support_construction"]["anchor"]["workflow_sha256"]), (selected_candidate, candidate["workflow_sha256"])):
        path = map_root / f"{sid}.txt"
        require(path.is_file() and sha_file(path) == expected, f"selected map state drift:{sid}")
        text = path.read_text(encoding="utf-8")
        texts[sid] = text
        states[sid] = {"state_id": sid, "site_stratum": "map", "workflow_sha256": expected, "source_path": str(path)}
    for sid in ("reddit-A", "reddit-B"):
        path = old_states_dir / f"{sid}.txt"
        require(path.is_file() and sha_file(path) == STATE_SHA[sid], f"reused reddit state drift:{sid}")
        text = path.read_text(encoding="utf-8")
        texts[sid] = text
        states[sid] = {"state_id": sid, "site_stratum": "reddit", "workflow_sha256": STATE_SHA[sid], "source_path": str(path)}

    old = json.loads(old_config.read_text())
    future = old["future_updates"]
    require(future.get("mode") == "released-benign-workflow-unit-append" and future.get("same_schedule_for_all_states") is True and future.get("update_generation_model_calls") == 0, "future update contract drift")
    units = split_units(awm_root / "webarena" / "workflow" / "gitlab.txt")
    require(len(units) == 6, "gitlab unit-count drift")
    schedule = future["schedule"]
    require(len(schedule) == 3, "future horizon drift")
    future_units = []
    for step, (row, expected_sha) in enumerate(zip(schedule, FUTURE_SHA), start=1):
        unit = units[int(row["source_index"])]
        require(row.get("step") == step and row.get("source_file") == "gitlab.txt" and row.get("unit_sha256") == expected_sha == unit["sha256"], f"future unit drift:{step}")
        future_units.append({"step": step, **unit})

    future_texts: dict[str, str] = {}
    state_steps: dict[str, list[dict[str, Any]]] = {}
    for sid, base in texts.items():
        text = base
        state_steps[sid] = []
        for unit in future_units:
            text = append_update(text, unit["text"])
            key = f"{sid}__step{unit['step']}"
            future_texts[key] = text
            state_steps[sid].append({
                "step": unit["step"],
                "workflow_sha256": sha_bytes(text.encode()),
                "appended_unit_sha256": unit["sha256"],
            })

    state_order = [ANCHOR_STATE_ID, selected_candidate, "reddit-A", "reddit-B"]
    pairs = [
        {"pair_id": "map", "left": ANCHOR_STATE_ID, "right": selected_candidate},
        {"pair_id": "reddit", "left": "reddit-A", "right": "reddit-B"},
    ]
    episodes = []
    for sid in state_order:
        for seed in BRANCH_SEEDS:
            probes = BRANCH_PROBES[str(seed)]
            require(len(probes) == 3 and all(bid in HELD and bid not in QUAL for bid in probes), f"heldout branch split drift:{seed}")
            for step, bid in enumerate(probes, start=1):
                wf = state_steps[sid][step - 1]
                episodes.append({
                    "phase": "future",
                    "episode_id": f"v4future__{sid}__branch{seed}__step{step}__b{bid}",
                    "state_id": sid,
                    "site_stratum": states[sid]["site_stratum"],
                    "behavior_id": bid,
                    "seed": seed,
                    "branch_seed": seed,
                    "future_step": step,
                    "workflow_sha256": wf["workflow_sha256"],
                    "appended_unit_sha256": wf["appended_unit_sha256"],
                    "execution_condition": "READY_R9_F0V4_SUPPORT_SELECTED",
                    "max_agent_model_calls": 4,
                    "classifier_model_evaluations": 1,
                })
    require(len(episodes) == 36 and len({row["episode_id"] for row in episodes}) == 36, "future episode ledger drift")
    require(sum(row["max_agent_model_calls"] for row in episodes) == 144 and sum(row["classifier_model_evaluations"] for row in episodes) == 36, "future budget drift")

    contract = {
        "schema_version": "4.1",
        "status": "FROZEN_R9_F0V4_FUTURE_CONTRACT",
        "candidate_id": support["candidate_id"],
        "support_contract_sha256": support["frozen_contract_sha256"],
        "support_selection_sha256": sha_file(selection_path),
        "support_runtime_journal_sha256": sha_file(support_journal_path),
        "scientific_question_unchanged": True,
        "selected_states": [states[sid] for sid in state_order],
        "state_pairs": pairs,
        "current_safety_support": {
            "map_anchor": support["support_construction"]["anchor_reused_qualification"],
            "map_candidate": {"state_id": selected_candidate, "episode_ids": [row["episode_id"] for row in candidate_eps], "predictions": {str(row["behavior_id"]): 0 for row in candidate_eps}},
            "reddit_pair": support["reused_reddit_pair"],
        },
        "future_updates": future,
        "branching": old["branching"],
        "heldout_ids": list(HELD),
        "qualification_ids": list(QUAL),
        "agent": old["agent"],
        "evaluator": old["evaluator"],
        "budget": FUTURE_BUDGET,
        "heldout_outcomes_used_for_support_selection": False,
        "completed_episode_rerun_forbidden": True,
        "fallback_allowed": False,
        "source_pins": old["pinned_sources"],
    }
    contract["frozen_contract_sha256"] = sha_bytes(canonical(contract))
    plan = {
        "schema_version": "4.1",
        "status": "R9_F0V4_FUTURE_PLAN_FROZEN",
        "contract_sha256": contract["frozen_contract_sha256"],
        "episodes": episodes,
        "budget": FUTURE_BUDGET,
        "scientific_authority": False,
    }
    plan["plan_sha256"] = sha_bytes(canonical(plan))
    return contract, future_texts, plan


def prepare(output_root: Path, **kwargs: Any) -> dict[str, Any]:
    contract, future_texts, plan = build_future_contract(**kwargs)
    wfdir = output_root / "future-workflows"
    wfdir.mkdir(parents=True, exist_ok=True)
    for key, text in future_texts.items():
        (wfdir / f"{key}.txt").write_text(text, encoding="utf-8")
    atomic_json(output_root / "frozen-future-contract.json", contract)
    atomic_json(output_root / "future-plan.json", plan)
    receipt = {
        "schema_version": "1.0",
        "status": "READY_R9_F0V4_FUTURE_EXECUTION",
        "contract_sha256": contract["frozen_contract_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "future_episode_count": 36,
        "future_model_evaluations_upper_bound": FUTURE_BUDGET["future_model_evaluations_upper_bound"],
        "combined_v4_model_evaluations_upper_bound_after_selection": FUTURE_BUDGET["combined_v4_model_evaluations_upper_bound_after_selection"],
        "contract_max_model_calls": FUTURE_BUDGET["v4_contract_max_model_calls"],
        "heldout_behavior_episodes_executed": 0,
        "future_execution_authorized": True,
        "provider_calls_executed": 0,
        "gpu_calls_executed": 0,
        "scientific_authority": False,
    }
    atomic_json(output_root / "future-execution-gate.json", receipt)
    return receipt


def validate(output_root: Path, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    expected, future_texts, plan = build_future_contract(**kwargs)
    stored = json.loads((output_root / "frozen-future-contract.json").read_text())
    stored_plan = json.loads((output_root / "future-plan.json").read_text())
    gate = json.loads((output_root / "future-execution-gate.json").read_text())
    require(canonical(stored) == canonical(expected), "future contract content drift")
    require(canonical(stored_plan) == canonical(plan), "future plan content drift")
    require(gate.get("status") == "READY_R9_F0V4_FUTURE_EXECUTION" and gate.get("future_execution_authorized") is True and gate.get("heldout_behavior_episodes_executed") == 0, "future execution gate not READY")
    for key, text in future_texts.items():
        path = output_root / "future-workflows" / f"{key}.txt"
        require(path.read_text(encoding="utf-8") == text, f"future workflow serializer drift:{key}")
        sid, step_token = key.rsplit("__step", 1)
        spec = next(row for row in plan["episodes"] if row["state_id"] == sid and int(row["future_step"]) == int(step_token))
        require(sha_file(path) == spec["workflow_sha256"], f"future workflow digest drift:{key}")
    return stored, stored_plan
