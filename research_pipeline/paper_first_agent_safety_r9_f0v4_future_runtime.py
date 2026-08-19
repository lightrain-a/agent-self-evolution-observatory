from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import BRANCH_SEEDS, atomic_json
from .paper_first_agent_safety_r9_f0_journal import acquire_lock, load_journal, release_lock
from .paper_first_agent_safety_r9_f0_runtime import run_episode
from .paper_first_agent_safety_r9_f0v4_future_contract import validate
from .paper_first_agent_safety_r9_f0_browser import verify_services


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def summarize_future(out: Path, contract: dict[str, Any], plan: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    completed = [row for row in journal["episodes"].values() if row.get("phase") == "future" and row.get("status") == "completed"]
    require(len(completed) == 36, "future summary requires all 36 completed episodes")
    by_key = {(row["state_id"], int(row["branch_seed"]), int(row["future_step"])): row for row in completed}
    survival = {}
    for state in contract["selected_states"]:
        sid = state["state_id"]
        survival[sid] = {}
        for seed in BRANCH_SEEDS:
            rows = [by_key[(sid, int(seed), step)] for step in (1, 2, 3)]
            preds = [int(row["harmbench_prediction"]) for row in rows]
            first = next((i + 1 for i, value in enumerate(preds) if value == 1), None)
            survival[sid][str(seed)] = {
                "predictions_by_step": preds,
                "first_violation_step": first,
                "event_observed": first is not None,
                "survival_time": first if first is not None else 3,
                "censored_at_horizon": first is None,
                "episode_ids": [row["episode_id"] for row in rows],
            }
    pairs = {}
    for pair in contract["state_pairs"]:
        pairs[pair["pair_id"]] = {
            "left_state_id": pair["left"],
            "right_state_id": pair["right"],
            "left_branch_outcomes": survival[pair["left"]],
            "right_branch_outcomes": survival[pair["right"]],
        }
    summary = {
        "schema_version": "1.0",
        "status": "READY_R9_F0V4_FUTURE_OUTCOMES",
        "contract_sha256": contract["frozen_contract_sha256"],
        "future_plan_sha256": plan["plan_sha256"],
        "completed_future_episodes": 36,
        "survival": survival,
        "pairs": pairs,
        "counters": dict(journal["counters"]),
        "statistical_adjudication_pending": True,
        "scientific_authority": False,
    }
    atomic_json(out / "future-outcomes-summary.json", summary)
    return summary


def run_future(args: argparse.Namespace) -> dict[str, Any]:
    future_root = Path(args.future_root)
    contract, plan = validate(
        future_root,
        support_root=Path(args.support_root),
        support_execution=Path(args.support_execution),
        old_states_dir=Path(args.old_states_dir),
        awm_root=Path(args.awm_root),
        browserart_root=Path(args.browserart_root),
        effective_gate=Path(args.effective_gate),
        old_config=Path(args.old_config),
        old_execution=Path(args.old_execution),
        v3_execution=Path(args.v3_execution),
        v3_stop=Path(args.v3_stop),
    )
    out = Path(args.output_dir)
    lock = acquire_lock(out, plan)
    try:
        journal = load_journal(out, plan)
        require(not any(row.get("status") == "protocol_inconclusive" for row in journal["episodes"].values()), "protocol-inconclusive future episode forbids continuation")
        verify_services()
        rows = json.loads((Path(args.browserart_root) / "src/datasets/behaviors/hbb.json").read_text())
        by_id = {int(row["id"]): row for row in rows}
        behavior_ids = sorted({int(row["behavior_id"]) for row in plan["episodes"]})
        behaviors = {}
        for bid in behavior_ids:
            row = by_id.get(bid)
            require(row is not None and row.get("evaluation_category") == "closed-ended", f"heldout behavior drift:{bid}")
            require(row.get("website") in {"local:email", "local:twitter", "local:review"}, f"heldout website drift:{bid}")
            behaviors[str(bid)] = row
        bundle = {"behaviors": behaviors}
        episode_args = SimpleNamespace(
            output_dir=str(out), browserart_root=args.browserart_root, awm_root=args.awm_root,
            states_dir=str(Path(args.support_root) / "states"), preflight_dir=str(future_root),
        )
        new = 0
        for spec in plan["episodes"]:
            old = journal["episodes"].get(spec["episode_id"])
            if old is not None:
                require(old.get("status") == "completed", f"non-completed future episode blocks:{spec['episode_id']}")
                continue
            run_episode(spec, bundle, journal, episode_args)
            new += 1
            if args.max_new_episodes and new >= args.max_new_episodes:
                return {
                    "status": "R9_F0V4_FUTURE_PARTIAL",
                    "new_episodes_completed": new,
                    "total_completed": journal["counters"]["completed_episodes"],
                    "counters": journal["counters"],
                    "scientific_authority": False,
                }
        return summarize_future(out, contract, plan, journal)
    finally:
        release_lock(lock)


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("future-root", "support-root", "support-execution", "old-states-dir", "awm-root", "browserart-root", "effective-gate", "old-config", "old-execution", "v3-execution", "v3-stop", "output-dir"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--max-new-episodes", type=int, default=0)
    print(json.dumps(run_future(parser.parse_args()), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
