from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .p0_alfworld_adapter import ALFWorldGameRunner, load_config

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-replay-feasibility.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-replay-feasibility.js"
DEFAULT_TRACE_ROOT = Path("/data/wyt/agent-self-evolution-p0-52-data/runs/p0-c-shared-substrate-v1")
DEFAULT_ALFWORLD_CONFIG = PROJECT_ROOT / "research_pipeline" / "p0_alfworld_config.yaml"

POLICY = {
    "schema_version": "1.0",
    "scientific_authority": "environment-only feasibility; cannot establish paper novelty or C2/C3",
    "minimum_tasks": 20,
    "minimum_task_families": 4,
    "prefix_steps": 5,
    "public_state_fields": ["observation", "reward", "done", "admissible_commands"],
    "historical_observation_must_match": True,
    "fresh_replay_pair_must_match": True,
    "every_frozen_action_must_be_admissible": True,
    "state_facts_required": False,
    "state_facts_reason": "ALFWorld/TextWorld wrapper used by the project does not expose symbolic facts through a stable public info field.",
    "no_model_loading": True,
    "no_method_or_certificate_training": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_source_traces(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("shard-*/source-traces.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            trace = row.get("trace") or {}
            if len(trace.get("actions") or []) < int(POLICY["prefix_steps"]):
                continue
            rows.append({"source_path": str(path), "trace": trace})
    return rows


def _select(rows: list[dict[str, Any]], n: int = 20) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str((row.get("trace") or {}).get("task_family") or "unknown")].append(row)
    families = sorted(grouped)
    selected: list[dict[str, Any]] = []
    cursor = 0
    while len(selected) < n and families:
        family = families[cursor % len(families)]
        bucket = grouped[family]
        if bucket:
            selected.append(bucket.pop(0))
        if not bucket:
            families = [f for f in families if grouped[f]]
            cursor = 0
        else:
            cursor += 1
    return selected


def _snapshot(obs: str, score: float, done: bool, info: dict[str, Any]) -> dict[str, Any]:
    commands = sorted(str(x) for x in ((info.get("admissible_commands") or [[]])[0] or []))
    return {
        "observation": str(obs),
        "reward": float(score),
        "done": bool(done),
        "admissible_commands": commands,
    }


def _replay(runner: ALFWorldGameRunner, game: str, actions: list[str], split: str) -> dict[str, Any]:
    env = runner.build_env(split, [game])
    try:
        obs, info = env.reset()
        states: list[dict[str, Any]] = []
        initial = _snapshot(str(obs[0]), 0.0, False, info)
        states.append(initial)
        admissible_flags: list[bool] = []
        for action in actions:
            commands = set(initial["admissible_commands"] if len(states) == 1 else states[-1]["admissible_commands"])
            admissible_flags.append(str(action) in commands)
            obs, scores, dones, info = env.step([str(action)])
            states.append(_snapshot(str(obs[0]), float(scores[0]), bool(dones[0]), info))
        return {
            "states": states,
            "all_actions_admissible": all(admissible_flags),
            "admissible_flags": admissible_flags,
            "sequence_sha256": _hash(states),
        }
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()


def run_replay_feasibility(
    trace_root: Path = DEFAULT_TRACE_ROOT,
    alfworld_config: Path = DEFAULT_ALFWORLD_CONFIG,
) -> dict[str, Any]:
    source_rows = _load_source_traces(trace_root)
    selected = _select(source_rows, int(POLICY["minimum_tasks"]))
    config = load_config(alfworld_config)
    config.setdefault("general", {})["save_path"] = str(trace_root / "paper-first-replay-feasibility-runtime")
    runner = ALFWorldGameRunner(config)
    units: list[dict[str, Any]] = []
    steps = int(POLICY["prefix_steps"])
    for index, row in enumerate(selected):
        trace = row["trace"]
        game = str(trace.get("task_id") or trace.get("gamefile") or "")
        actions = [str(x) for x in (trace.get("actions") or [])[:steps]]
        historical_obs = [str(x) for x in (trace.get("observations") or [])[: steps + 1]]
        first = _replay(runner, game, actions, "eval_in_distribution")
        second = _replay(runner, game, actions, "eval_in_distribution")
        first_obs = [state["observation"] for state in first["states"]]
        second_obs = [state["observation"] for state in second["states"]]
        public_equal = first["states"] == second["states"]
        history_equal = first_obs == historical_obs and second_obs == historical_obs
        unit = {
            "unit_id": f"replay-{index:02d}",
            "task_family": str(trace.get("task_family") or "unknown"),
            "gamefile": game,
            "actions": actions,
            "prefix_steps": len(actions),
            "historical_observation_equal": history_equal,
            "fresh_replay_public_state_equal": public_equal,
            "all_actions_admissible_first": bool(first["all_actions_admissible"]),
            "all_actions_admissible_second": bool(second["all_actions_admissible"]),
            "first_sequence_sha256": first["sequence_sha256"],
            "second_sequence_sha256": second["sequence_sha256"],
            "historical_observation_sha256": _hash(historical_obs),
            "first_observation_sha256": _hash(first_obs),
            "second_observation_sha256": _hash(second_obs),
            "pass": bool(
                history_equal
                and public_equal
                and first["all_actions_admissible"]
                and second["all_actions_admissible"]
                and len(actions) == steps
            ),
        }
        units.append(unit)
    family_counts = Counter(str(row.get("task_family") or "unknown") for row in units)
    passed = sum(bool(row.get("pass")) for row in units)
    enough = len(units) >= int(POLICY["minimum_tasks"]) and len(family_counts) >= int(POLICY["minimum_task_families"])
    decision = "ENVIRONMENT_REPLAY_FEASIBILITY_PASS" if enough and passed == len(units) else "ENVIRONMENT_REPLAY_FEASIBILITY_FAIL"
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": "trajectory-mediated-memory-effect-transport",
        "decision": decision,
        "summary": {
            "selected_tasks": len(units),
            "task_families": len(family_counts),
            "family_counts": dict(family_counts),
            "passed_units": passed,
            "failed_units": len(units) - passed,
            "historical_observation_match": sum(bool(row["historical_observation_equal"]) for row in units),
            "fresh_replay_public_state_match": sum(bool(row["fresh_replay_public_state_equal"]) for row in units),
            "all_actions_admissible": sum(bool(row["all_actions_admissible_first"] and row["all_actions_admissible_second"]) for row in units),
            "state_facts_available": False,
        },
        "units": units,
        "next_gate": (
            "return to paper-design/AI adjudication; C2/C3 remain locked"
            if decision == "ENVIRONMENT_REPLAY_FEASIBILITY_PASS"
            else "revise or stop replay-based paper realization; no C2/C3"
        ),
        "local_scientific_validation_authorized": False,
        "full_experiment_authorized": False,
        "policy": POLICY,
    }


def write_replay_feasibility(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = run_replay_feasibility()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_REPLAY_FEASIBILITY = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_replay_feasibility(), ensure_ascii=False, indent=2))
