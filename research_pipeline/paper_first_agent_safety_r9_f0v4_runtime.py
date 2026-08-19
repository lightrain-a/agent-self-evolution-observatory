from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import QUAL, atomic_json
from .paper_first_agent_safety_r9_f0_journal import acquire_lock, load_journal, release_lock
from .paper_first_agent_safety_r9_f0_runtime import run_episode
from .paper_first_agent_safety_r9_f0v4_contract import ANCHOR_STATE_ID, validate
from .paper_first_agent_safety_r9_f0_browser import verify_services


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def candidate_progress(state_id: str, plan: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    specs = [row for row in plan["episodes"] if row["state_id"] == state_id]
    require(len(specs) == len(QUAL), f"candidate plan cardinality drift:{state_id}")
    episodes = [journal["episodes"].get(row["episode_id"]) for row in specs]
    completed = [row for row in episodes if row is not None and row.get("status") == "completed"]
    inconclusive = [row for row in episodes if row is not None and row.get("status") == "protocol_inconclusive"]
    require(not inconclusive, f"protocol-inconclusive support episode:{state_id}")
    violations = [row for row in completed if row.get("harmbench_prediction") == 1]
    if violations:
        first = sorted(violations, key=lambda row: float(row.get("completed_at_unix") or 0))[0]
        return {
            "candidate_state_id": state_id,
            "status": "rejected",
            "completed": len(completed),
            "violation_episode_id": first["episode_id"],
            "violation_behavior_id": first["behavior_id"],
        }
    if len(completed) == len(specs):
        require(all(row.get("harmbench_prediction") == 0 for row in completed), f"nonbinary candidate outcome:{state_id}")
        return {"candidate_state_id": state_id, "status": "selected", "completed": len(completed)}
    return {"candidate_state_id": state_id, "status": "pending", "completed": len(completed)}


def _write_adjudication(out: Path, progress: dict[str, Any], contract: dict[str, Any]) -> None:
    atomic_json(out / "candidate-adjudications" / f"{progress['candidate_state_id']}.json", {
        "schema_version": "1.0",
        **progress,
        "contract_sha256": contract["frozen_contract_sha256"],
        "heldout_behavior_episodes_executed": 0,
        "scientific_authority": False,
    })


def _selection(out: Path, contract: dict[str, Any], plan: dict[str, Any], journal: dict[str, Any], state_id: str) -> dict[str, Any]:
    candidate = next(row for row in contract["support_construction"]["candidate_ladder"] if row["candidate_state_id"] == state_id)
    result = {
        "schema_version": "1.0",
        "status": "READY_R9_F0V4_SUPPORT_SELECTED",
        "contract_sha256": contract["frozen_contract_sha256"],
        "qualification_plan_sha256": plan["plan_sha256"],
        "selected_map_anchor_state_id": ANCHOR_STATE_ID,
        "selected_map_candidate_state_id": state_id,
        "selected_map_candidate_rank": candidate["rank"],
        "selected_map_pair_workflow_sha256": [contract["support_construction"]["anchor"]["workflow_sha256"], candidate["workflow_sha256"]],
        "reused_reddit_states": ["reddit-A", "reddit-B"],
        "new_qualification_counters": dict(journal["counters"]),
        "heldout_behavior_episodes_executed": 0,
        "future_execution_authorized": False,
        "scientific_authority": False,
    }
    atomic_json(out / "support-selection.json", result)
    return result


def _stop(out: Path, contract: dict[str, Any], plan: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "1.0",
        "status": "STOP_R9_F0V4_SUPPORT_CONSTRUCTION_NO_SAFE_NEAR_HISTORY",
        "contract_sha256": contract["frozen_contract_sha256"],
        "qualification_plan_sha256": plan["plan_sha256"],
        "principle_dead_end_certified": False,
        "failure_layer": "operationalization/support-realization",
        "new_qualification_counters": dict(journal["counters"]),
        "heldout_behavior_episodes_executed": 0,
        "future_execution_authorized": False,
        "scientific_authority": False,
    }
    atomic_json(out / "support-selection.json", result)
    return result


def run_support(args: argparse.Namespace) -> dict[str, Any]:
    support_root = Path(args.support_root)
    contract, plan = validate(
        support_root,
        awm_root=Path(args.awm_root),
        browserart_root=Path(args.browserart_root),
        effective_gate=Path(args.effective_gate),
        old_config=Path(args.old_config),
        old_execution=Path(args.old_execution),
        v3_execution=Path(args.v3_execution),
        parent_stop=Path(args.parent_stop),
    )
    out = Path(args.output_dir)
    lock = acquire_lock(out, plan)
    try:
        journal = load_journal(out, plan)
        require(not any(row.get("status") == "protocol_inconclusive" for row in journal["episodes"].values()),
                "protocol-inconclusive support episode forbids continuation")
        verify_services()
        rows = json.loads((Path(args.browserart_root) / "src/datasets/behaviors/hbb.json").read_text())
        by_id = {int(row["id"]): row for row in rows}
        behaviors = {}
        for bid in QUAL:
            row = by_id.get(bid)
            require(row is not None and row.get("evaluation_category") == "closed-ended", f"qualification behavior drift:{bid}")
            require(row.get("website") in {"local:email", "local:twitter", "local:review"}, f"qualification website drift:{bid}")
            behaviors[str(bid)] = row
        bundle = {"behaviors": behaviors}
        episode_args = SimpleNamespace(
            output_dir=str(out), browserart_root=args.browserart_root, awm_root=args.awm_root,
            states_dir=str(support_root / "states"), preflight_dir=str(support_root),
        )
        new = 0
        for candidate in contract["support_construction"]["candidate_ladder"]:
            state_id = candidate["candidate_state_id"]
            progress = candidate_progress(state_id, plan, journal)
            if progress["status"] == "selected":
                _write_adjudication(out, progress, contract)
                return _selection(out, contract, plan, journal, state_id)
            if progress["status"] == "rejected":
                _write_adjudication(out, progress, contract)
                continue
            specs = [row for row in plan["episodes"] if row["state_id"] == state_id]
            for spec in specs:
                old = journal["episodes"].get(spec["episode_id"])
                if old is not None:
                    require(old.get("status") == "completed", f"non-completed support episode blocks:{spec['episode_id']}")
                    if old.get("harmbench_prediction") == 1:
                        break
                    continue
                ep = run_episode(spec, bundle, journal, episode_args)
                new += 1
                if ep.get("harmbench_prediction") == 1:
                    progress = candidate_progress(state_id, plan, journal)
                    _write_adjudication(out, progress, contract)
                    if args.max_new_episodes and new >= args.max_new_episodes:
                        return _partial(new, progress, journal)
                    break
                if args.max_new_episodes and new >= args.max_new_episodes:
                    progress = candidate_progress(state_id, plan, journal)
                    _write_adjudication(out, progress, contract)
                    return _partial(new, progress, journal)
            progress = candidate_progress(state_id, plan, journal)
            _write_adjudication(out, progress, contract)
            if progress["status"] == "selected":
                return _selection(out, contract, plan, journal, state_id)
            require(progress["status"] == "rejected", f"candidate did not reach terminal support state:{state_id}")
        return _stop(out, contract, plan, journal)
    finally:
        release_lock(lock)


def _partial(new: int, progress: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "R9_F0V4_SUPPORT_QUALIFICATION_PARTIAL",
        "new_episodes_completed": new,
        "current_candidate": progress,
        "counters": journal["counters"],
        "heldout_behavior_episodes_executed": 0,
        "scientific_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("support-root", "awm-root", "browserart-root", "effective-gate", "old-config", "old-execution", "v3-execution", "parent-stop", "output-dir"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--max-new-episodes", type=int, default=0)
    print(json.dumps(run_support(parser.parse_args()), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
