from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import QUAL, atomic_json
from .paper_first_agent_safety_r9_f0_journal import acquire_lock, load_journal, release_lock
from .paper_first_agent_safety_r9_f0_runtime import run_episode
from .paper_first_agent_safety_r9_f0v3_contract import validate
from .paper_first_agent_safety_r9_f0_browser import verify_services


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def pair_progress(pair_id: str, plan: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    specs = [row for row in plan["episodes"] if row["pair_id"] == pair_id]
    require(len(specs) == 2 * len(QUAL), f"pair plan cardinality drift:{pair_id}")
    episodes = [journal["episodes"].get(row["episode_id"]) for row in specs]
    completed = [row for row in episodes if row is not None and row.get("status") == "completed"]
    inconclusive = [row for row in episodes if row is not None and row.get("status") == "protocol_inconclusive"]
    require(not inconclusive, f"protocol-inconclusive support episode:{pair_id}")
    violations = [row for row in completed if row.get("harmbench_prediction") == 1]
    if violations:
        first = sorted(violations, key=lambda row: float(row.get("completed_at_unix") or 0))[0]
        return {
            "pair_id": pair_id,
            "status": "rejected",
            "completed": len(completed),
            "violation_episode_id": first["episode_id"],
            "violation_state_id": first["state_id"],
            "violation_behavior_id": first["behavior_id"],
        }
    if len(completed) == len(specs):
        require(all(row.get("harmbench_prediction") == 0 for row in completed), f"nonbinary pair outcome:{pair_id}")
        return {"pair_id": pair_id, "status": "selected", "completed": len(completed)}
    return {"pair_id": pair_id, "status": "pending", "completed": len(completed)}


def _write_pair_adjudication(out: Path, progress: dict[str, Any], contract: dict[str, Any]) -> None:
    row = {
        "schema_version": "1.0",
        **progress,
        "contract_sha256": contract["frozen_contract_sha256"],
        "heldout_behavior_episodes_executed": 0,
        "scientific_authority": False,
    }
    atomic_json(out / "pair-adjudications" / f"{progress['pair_id']}.json", row)


def _selection(out: Path, contract: dict[str, Any], plan: dict[str, Any], journal: dict[str, Any], pair_id: str) -> dict[str, Any]:
    pair = next(row for row in contract["support_repair"]["map_candidate_pair_ladder"] if row["pair_id"] == pair_id)
    result = {
        "schema_version": "1.0",
        "status": "READY_R9_F0V3_SUPPORT_SELECTED",
        "contract_sha256": contract["frozen_contract_sha256"],
        "qualification_plan_sha256": plan["plan_sha256"],
        "selected_map_pair_id": pair_id,
        "selected_map_states": [row["state_id"] for row in pair["states"]],
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
        "status": "STOP_R9_F0V3_SUPPORT_REPAIR_NO_QUALIFIED_MAP_PAIR",
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
            output_dir=str(out),
            browserart_root=args.browserart_root,
            awm_root=args.awm_root,
            states_dir=str(support_root / "states"),
            preflight_dir=str(support_root),
        )
        new = 0
        for pair in contract["support_repair"]["map_candidate_pair_ladder"]:
            pair_id = pair["pair_id"]
            progress = pair_progress(pair_id, plan, journal)
            if progress["status"] == "selected":
                _write_pair_adjudication(out, progress, contract)
                return _selection(out, contract, plan, journal, pair_id)
            if progress["status"] == "rejected":
                _write_pair_adjudication(out, progress, contract)
                continue
            specs = [row for row in plan["episodes"] if row["pair_id"] == pair_id]
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
                    break
                if args.max_new_episodes and new >= args.max_new_episodes:
                    progress = pair_progress(pair_id, plan, journal)
                    _write_pair_adjudication(out, progress, contract)
                    return {
                        "status": "R9_F0V3_SUPPORT_QUALIFICATION_PARTIAL",
                        "new_episodes_completed": new,
                        "current_pair": progress,
                        "counters": journal["counters"],
                        "heldout_behavior_episodes_executed": 0,
                        "scientific_authority": False,
                    }
            progress = pair_progress(pair_id, plan, journal)
            _write_pair_adjudication(out, progress, contract)
            if progress["status"] == "selected":
                return _selection(out, contract, plan, journal, pair_id)
            require(progress["status"] == "rejected", f"pair did not reach terminal support state:{pair_id}")
        return _stop(out, contract, plan, journal)
    finally:
        release_lock(lock)


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("support-root", "awm-root", "browserart-root", "effective-gate", "old-config", "old-execution", "parent-stop", "output-dir"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--max-new-episodes", type=int, default=0)
    print(json.dumps(run_support(parser.parse_args()), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
