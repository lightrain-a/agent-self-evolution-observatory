from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_reserve_source_common as c
from research_pipeline.agent_constraint_externality_direct_sfq_a0_cases import evaluate_case_from_state
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value


def completion_rows() -> list[dict[str, Any]]:
    if not c.LEDGER.is_file():
        return []
    return [row for row in c.live.ledger_rows(c.LEDGER) if row.get("event") == "COMPLETION"]


def selected_from(completion: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_id = {row["family_id"]: row for row in completion}
    selected = {"FG": [], "TNF": []}
    for cat, ids in c.ranked_ids().items():
        for fid in ids:
            row = by_id.get(fid)
            if row and row.get("usable_semantic_failure") is True:
                selected[cat].append(fid)
                if len(selected[cat]) == 3:
                    break
    return selected


def next_candidate(states: dict[str, str], completion: list[dict[str, Any]]) -> tuple[str | None, dict[str, list[str]]]:
    selected = selected_from(completion)
    ranks = c.ranked_ids()
    if all(len(selected[cat]) == 3 for cat in ("FG", "TNF")):
        return None, selected
    for pos in range(8):
        for cat in ("FG", "TNF"):
            if len(selected[cat]) >= 3:
                continue
            fid = ranks[cat][pos]
            state = states.get(c.unit_id(fid))
            if state is None:
                return fid, selected
            if state != "COMPLETION":
                raise c.Stop(f"replay forbidden after dispatch: {c.unit_id(fid)}:{state}")
    return None, selected


def terminal(status: str, *, completion: list[dict[str, Any]], selected: dict[str, list[str]], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-source-result-v1",
        "object_id": OBJECT_ID,
        "execution_id": c.EXECUTION_ID,
        "status": status,
        "completed_source_count": len(completion),
        "semantic_failure_count": sum(bool(row.get("usable_semantic_failure")) for row in completion),
        "target_success_count": sum(bool(row.get("target_success")) for row in completion),
        "selected_family_ids": selected,
        "selected_family_count": sum(len(value) for value in selected.values()),
        "ledger_sha256": sha256_file(c.LEDGER) if c.LEDGER.is_file() else None,
        "scientific_model_round_count": sum(int(row.get("model_round_count", 0)) for row in completion),
        "appworld_tool_call_total": sum(int(row.get("appworld_tool_call_count", 0)) for row in completion),
        "repair_generation_executed": False,
        "topology_execution_executed": False,
        "scientific_externality_outcomes_observed": 0,
        "authority": {
            "reserve_source_execution_closed": True,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "rq1_rq2": False,
            "paper_claim": False,
        },
        **(extra or {}),
    }
    payload["content_sha256"] = sha256_value(payload)
    c.writej(c.RESULT_OUTPUT, payload)
    return payload


def operational(status: str, *, next_family: str | None, quota: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": "ace-repeat-dev-reserve-source-operational-v1",
        "object_id": OBJECT_ID,
        "execution_id": c.EXECUTION_ID,
        "status": status,
        "next_family": next_family,
        "codingplan_usage": quota,
        "minimum_remaining_before_dispatch": c.MIN_REMAINING,
        "shared_reserve": c.SHARED_RESERVE,
        "scientific_externality_outcomes_observed": 0,
        "downstream_authority_opened": False,
    }
    payload["content_sha256"] = sha256_value(payload)
    c.writej(c.OP_OUTPUT, payload)
    return payload


def run_one(family: dict[str, Any]) -> dict[str, Any]:
    fid = family["family_id"]
    uid = c.unit_id(fid)
    case = family["source_case"]
    root = c.RUN_ROOT / fid.lower()
    if root.exists():
        raise c.Stop(f"unit root already exists: {root}")
    root.mkdir()
    atom, work, progress, trajectory, mcp_payload = c.prepare_unit(fid, root)
    proc = None
    try:
        proc, base, token = c.live.start_daemon(atom_home=atom, workdir=work, log_path=root / "atomcode-daemon.log")
        (atom / "mcp.json").write_text(json.dumps(mcp_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        c.live.http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})

        def before_submit() -> dict[str, Any]:
            state0 = c.readj(progress)
            if state0.get("status") != "TOOLS_LISTED":
                raise c.Stop("MCP tools not listed")
            quota = dict(c.live.codingplan_usage(base, token))
            if int(quota["remaining"]) < c.MIN_REMAINING:
                raise c.Stop("quota changed below pre-dispatch headroom")
            c.live.append_jsonl(c.LEDGER, {
                "schema_version": "ace-repeat-dev-reserve-source-ledger-v1",
                "object_id": OBJECT_ID,
                "execution_id": c.EXECUTION_ID,
                "event": "DISPATCH",
                "unit_id": uid,
                "family_id": fid,
                "case_id": case["case_id"],
                "provider": c.PROVIDER,
                "model_profile": c.MODEL_PROFILE,
                "model_id": c.MODEL_ID,
                "prompt_sha256": sha256_value(case["task_instruction"]),
                "initial_snapshot_sha256": state0["initial_snapshot_sha256"],
                "bundle_sha256": sha256_file(c.OUTPUT_BUNDLE),
                "codingplan_window_before": quota,
                "attempt": 1,
                "retry_allowed": False,
                "replacement_allowed": False,
                "time_ns": time.time_ns(),
            })
            return {"usage_before": quota}

        result = c.live.run_live_turn(
            base=base,
            token=token,
            instruction=case["task_instruction"],
            progress_path=progress,
            before_submit=before_submit,
            timeout_seconds=480,
        )
        after = dict(c.live.codingplan_usage(base, token))
        if result["prohibited_tool"] or result["error_message"] or result["stop_reason"] != "stopped":
            c.live.append_jsonl(c.LEDGER, {
                "schema_version": "ace-repeat-dev-reserve-source-ledger-v1",
                "object_id": OBJECT_ID,
                "execution_id": c.EXECUTION_ID,
                "event": "FAILURE",
                "unit_id": uid,
                "family_id": fid,
                "failure_class": "SOURCE_INTERFACE_OR_AGENT_LOOP_INVALID",
                "message": str(result["prohibited_tool"] or result["error_message"] or result["stop_reason"])[:400],
                "retry_attempted": False,
                "time_ns": time.time_ns(),
            })
            return {"technical_invalid": True, "family_id": fid}
    finally:
        if proc is not None:
            c.live.terminate_process(proc)

    state1 = c.readj(progress)
    calls = int(state1.get("tool_call_count", 0))
    try:
        if calls <= 0:
            raise c.Stop("zero AppWorld tool calls")
        audit = c.trajectory_audit(trajectory, calls)
        target_success = bool(evaluate_case_from_state(
            case,
            source_db_root=Path(state1["source_db_root"]),
            changes_db_root=Path(state1["changes_db_root"]),
            measurement_root=root / "measurement-full-dbs",
        ))
    except Exception as exc:
        c.live.append_jsonl(c.LEDGER, {
            "schema_version": "ace-repeat-dev-reserve-source-ledger-v1",
            "object_id": OBJECT_ID,
            "execution_id": c.EXECUTION_ID,
            "event": "FAILURE",
            "unit_id": uid,
            "family_id": fid,
            "failure_class": "SOURCE_TRAJECTORY_OR_EVALUATOR_INVALID",
            "message": f"{type(exc).__name__}: {exc}"[:400],
            "retry_attempted": False,
            "time_ns": time.time_ns(),
        })
        return {"technical_invalid": True, "family_id": fid}

    completion = {
        "schema_version": "ace-repeat-dev-reserve-source-ledger-v1",
        "object_id": OBJECT_ID,
        "execution_id": c.EXECUTION_ID,
        "event": "COMPLETION",
        "unit_id": uid,
        "family_id": fid,
        "case_id": case["case_id"],
        "category": "FG" if "-FG-" in fid else "TNF",
        "target_success": target_success,
        "usable_semantic_failure": not target_success,
        "tool_loop_completed": True,
        "appworld_tool_call_count": calls,
        "model_round_count": int(result["model_round_count"]),
        "prompt_tokens_total": int(result["prompt_tokens_total"]),
        "completion_tokens_total": int(result["completion_tokens_total"]),
        "trajectory_sha256": audit["trajectory_sha256"],
        "trajectory_row_count": audit["row_count"],
        "all_tool_dispatches_closed": True,
        "bridge_progress_sha256": sha256_file(progress),
        "codingplan_window_after": after,
        "time_ns": time.time_ns(),
    }
    c.live.append_jsonl(c.LEDGER, completion)
    return {"technical_invalid": False, "completion": completion}


def execute() -> dict[str, Any]:
    c.patch_live()
    auth = c.verified(c.AUTH_OUTPUT, "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_ONLY")
    contract = c.verified(c.EXEC_CONTRACT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_EXECUTION_AUTHORIZED")
    if not auth["authority"]["reserve_source_execution"] or auth["authority"].get("repair_generation"):
        raise c.Stop("reserve source authority scope drift")
    if contract.get("human_authorization_content_sha256") != auth.get("content_sha256"):
        raise c.Stop("human authorization binding drift")
    if contract.get("executor_sha256") != sha256_file(Path(__file__)):
        raise c.Stop("executor SHA drift")
    if contract.get("common_sha256") != sha256_file(Path(c.__file__)):
        raise c.Stop("common SHA drift")
    if contract.get("bridge_sha256") != sha256_file(c.BRIDGE):
        raise c.Stop("bridge SHA drift")
    if contract.get("protected_bundle_sha256") != sha256_file(c.OUTPUT_BUNDLE):
        raise c.Stop("bundle SHA drift")
    if contract.get("ranked_family_ids") != c.ranked_ids():
        raise c.Stop("rank order binding drift")

    c.RUN_ROOT.mkdir(parents=True, exist_ok=True)
    index = c.family_index()
    while True:
        states = c.live.ledger_states(c.LEDGER)
        completion = completion_rows()
        fid, selected = next_candidate(states, completion)
        if fid is None:
            if all(len(selected[cat]) == 3 for cat in ("FG", "TNF")):
                return terminal("ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PANEL_PASS_REPAIR_CLOSED", completion=completion, selected=selected)
            return terminal("ATOMGIT_REPEAT_DEV_RESERVE_INSUFFICIENT_SOURCE_FAILURE_SUPPORT_STOP", completion=completion, selected=selected)
        quota = c.usage()
        if int(quota["remaining"]) < c.MIN_REMAINING:
            return operational("ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_QUOTA_HOLD", next_family=fid, quota=quota)
        result = run_one(index[fid])
        if result["technical_invalid"]:
            completion = completion_rows()
            return terminal(
                "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_TECHNICAL_INVALID_STOP",
                completion=completion,
                selected=selected_from(completion),
                extra={"invalid_family_id": fid},
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--usage-only", action="store_true")
    args = parser.parse_args()
    if sum((args.preflight, args.execute, args.usage_only)) != 1:
        raise SystemExit("choose exactly one action")
    if args.usage_only:
        print(json.dumps({"status": "ZERO_REQUEST_USAGE_PROBE", "usage": c.usage(), "model_requests": 0}, sort_keys=True))
        return
    payload = c.preflight(Path(__file__)) if args.preflight else execute()
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
