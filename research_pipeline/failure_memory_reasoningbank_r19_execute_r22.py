#!/usr/bin/env python3
"""Execute the authorized B1/R19 140-episode metadata-only intervention.

R19 is a new experiment after the stopped R18 attempt. The runner is append-only
and fail-closed. It reuses the exact R17 source-memory bytes, changes only the
single S/F status byte across arms, resets Shopping before every episode, and
follows the frozen 140-episode R19 schedule. Once an episode is marked STARTED,
any unresolved failure ends the whole confirmatory attempt with no retry.
"""
from __future__ import annotations

import argparse
import gzip
import json
import pickle
from pathlib import Path
from typing import Any

from research_pipeline.failure_memory_reasoningbank_executor_contract_r15 import render_memory_file
from research_pipeline.failure_memory_reasoningbank_l2b_execute_r18 import (
    append_jsonl,
    atomic_json,
    configure_environment,
    load_private_memories,
    make_agent_env,
    now,
    prepare_first_party_imports,
    read_jsonl,
    reset_shopping,
    sha_file,
)
from research_pipeline.failure_memory_reasoningbank_r19_execution_authority_r21 import require_authority

EXPECTED_R19_CONTRACT_SHA = "ed803f0958002ab2095563a56cff6328a054ff4c4d7bd9fc18fc97bb3bdc3282"
EXPECTED_R21_AUTHORITY_RECEIPT_SHA = "f7ad4044e80e7fce30e7e63940eebafac6af7af2b7fa08ea38169f797ceb905f"
EXPECTED_R17_SHA = "58de4f998b16aace4ddfeef0693d88a347b293c032d997e0da471e6b92c69235"
EXPECTED_PRIVATE_MEMORIES_SHA = "2d056b69202653c2a61c16107f13f164707d2564db73cc858589d1c35f4f3dd2"
EXPECTED_SUPPORT_SHA = "cb5cf78c753ff38b8ab40e5c761e8aaa57fd14922d8c4186aed43c0b7f7e5f05"
EXPECTED_SMOKES_SHA = "77c34fd1bdd92434e4e9669a7544e3c60f0f1311f21a5d92ad609a779cda56c4"
EXPECTED_EXECUTOR_MANIFEST = "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
FUZZY_EVALUATOR_TASKS = frozenset({"336", "796", "50", "359", "24"})
AGENT_COMPLETION_BUDGET = 4200
FUZZY_EVALUATOR_COMPLETION_BUDGET = 600
EPISODES = 140


def load_bound(path: Path, expected: str, name: str) -> dict[str, Any]:
    actual = sha_file(path)
    if actual != expected:
        raise RuntimeError(f"{name} SHA drift: {actual} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def completion_count_from_agent_info(info: dict[str, Any]) -> int:
    """Return exact first-party LLM completions represented by one action attempt.

    For a valid parsed action, n_retry counts failed parses before the successful
    completion, so completions = 1+n_retry. If all max retries fail, the agent
    stores action=None plus err_msg and n_retry=max_retry; then completions=n_retry.
    """
    retry = int(float(info.get("n_retry", 0)))
    if info.get("action") is None and info.get("err_msg"):
        return retry
    return 1 + retry


def count_agent_completions(exp_dir: Path) -> dict[str, int]:
    total = 0
    action_attempts = 0
    parser_retry_completions = 0
    for path in sorted(exp_dir.glob("step_*.pkl.gz")):
        with gzip.open(path, "rb") as f:
            step = pickle.load(f)
        info = getattr(step, "agent_info", None)
        if not isinstance(info, dict) or "n_retry" not in info:
            continue
        c = completion_count_from_agent_info(info)
        if c < 1:
            raise RuntimeError(f"invalid completion count in {path.name}: {c}")
        total += c
        action_attempts += 1
        parser_retry_completions += max(0, c - 1)
    return {
        "agent_completions": total,
        "action_attempts": action_attempts,
        "parser_retry_completions": parser_retry_completions,
    }


def execute(a: argparse.Namespace) -> dict[str, Any]:
    authority = require_authority(a.authority)
    contract = load_bound(a.contract, EXPECTED_R19_CONTRACT_SHA, "R19 contract")
    authority_receipt = load_bound(a.authority_receipt, EXPECTED_R21_AUTHORITY_RECEIPT_SHA, "R21 authority receipt")
    support = load_bound(a.support_receipt, EXPECTED_SUPPORT_SHA, "R21 support receipt")
    smokes = load_bound(a.synthetic_smokes, EXPECTED_SMOKES_SHA, "R21 synthetic smokes")
    r17 = load_bound(a.r17, EXPECTED_R17_SHA, "R17")

    artifact = authority["artifact_sha256"]
    for name, obj in [("authority", authority_receipt), ("support", support), ("smokes", smokes)]:
        bound = (obj.get("authority_artifact_sha256") or (obj.get("bindings") or {}).get("authority_artifact_sha256"))
        if bound != artifact:
            raise RuntimeError(f"{name}/human authority mismatch")
    if smokes.get("status") != "R19_TWO_FIXED_NONBENCHMARK_SYNTHETIC_COMPLETION_SMOKES_PASS":
        raise RuntimeError("synthetic support gate not passed")
    if support.get("status") != "R19_PREBENCHMARK_ZERO_COMPLETION_SUPPORT_GATE_PASS":
        raise RuntimeError("zero-completion support gate not passed")
    if contract["executor"]["executor_manifest_digest"] != EXPECTED_EXECUTOR_MANIFEST:
        raise RuntimeError("executor manifest drift")
    if contract["source_memories"]["new_writer_calls"] != 0 or contract["source_memories"]["memory_regeneration"] is not False:
        raise RuntimeError("R19 source-memory policy drift")
    schedule = list(contract["rollouts"]["episode_schedule"])
    if len(schedule) != EPISODES or [int(x["sequence_index"]) for x in schedule] != list(range(EPISODES)):
        raise RuntimeError("R19 schedule drift")

    memories = load_private_memories(a.memories, r17)
    configure_environment(a.shopping_base, a.reset_base, a.playwright_browsers)
    GenericAgentArgs, Flags, ChatModelArgs, EnvArgs, ExpArgs = prepare_first_party_imports(a.rb_webarena_root)

    a.run_root.mkdir(parents=True, exist_ok=True)
    attempts_path = a.run_root / "attempts.jsonl"
    progress_path = a.run_root / "progress.jsonl"
    attempts = read_jsonl(attempts_path)
    progress = read_jsonl(progress_path)
    attempted = [int(x["sequence_index"]) for x in attempts if x.get("status") == "STARTED"]
    complete = [int(x["sequence_index"]) for x in progress if x.get("status") == "COMPLETE"]
    if len(attempted) != len(set(attempted)) or len(complete) != len(set(complete)):
        raise RuntimeError("duplicate episode ledger row")
    if set(attempted) != set(complete):
        raise RuntimeError(f"prior STARTED without durable COMPLETE; R19 retry forbidden: {sorted(set(attempted)-set(complete))}")
    if sorted(complete) != list(range(len(complete))):
        raise RuntimeError("completed episodes are not an exact R19 prefix")
    if (a.run_root / "failure.json").exists():
        raise RuntimeError("R19 post-exposure failure receipt exists; confirmatory attempt is stopped")

    agent_total = sum(int(x.get("agent_completion_count") or 0) for x in progress)
    evaluator_total = sum(int(x.get("fuzzy_evaluator_completion_count") or 0) for x in progress)
    if agent_total > AGENT_COMPLETION_BUDGET or evaluator_total > FUZZY_EVALUATOR_COMPLETION_BUDGET:
        raise RuntimeError("R19 model completion budget already exceeded")

    run_contract = {
        "schema_version": "1.0",
        "run_id": a.run_root.name,
        "created_at": now(),
        "status": "R19_IN_PROGRESS" if len(complete) < EPISODES else "R19_COMPLETE",
        "bindings": {
            "r19_contract": EXPECTED_R19_CONTRACT_SHA,
            "r21_authority_receipt": EXPECTED_R21_AUTHORITY_RECEIPT_SHA,
            "r17": EXPECTED_R17_SHA,
            "private_memories": EXPECTED_PRIVATE_MEMORIES_SHA,
            "prebenchmark_support": EXPECTED_SUPPORT_SHA,
            "synthetic_smokes": EXPECTED_SMOKES_SHA,
            "executor_manifest": EXPECTED_EXECUTOR_MANIFEST,
        },
        "authority_artifact_sha256": artifact,
        "endpoint_redacted": True,
        "policy": {
            "schedule_length": EPISODES,
            "no_retry_after_started": True,
            "reset_before_every_episode": True,
            "task_replacement": False,
            "memory_regeneration": False,
            "model_or_provider_switch": False,
            "endpoint_switch": False,
            "threshold_or_statistical_change": False,
            "agent_completion_budget": AGENT_COMPLETION_BUDGET,
            "fuzzy_evaluator_completion_budget": FUZZY_EVALUATOR_COMPLETION_BUDGET,
        },
        "already_complete": complete,
    }
    atomic_json(a.run_root / "run-contract.json", run_contract)

    remaining = [x for x in schedule if int(x["sequence_index"]) not in set(complete)]
    limit = len(remaining) if a.max_new is None else min(a.max_new, len(remaining))
    for sched in remaining[:limit]:
        seq = int(sched["sequence_index"])
        task_id = str(sched["task_id"])
        source_id = str(sched["source_task_id"])
        arm = str(sched["arm"])
        if seq != len(read_jsonl(progress_path)):
            raise RuntimeError("R19 schedule prefix drift immediately before episode")
        if source_id not in memories:
            raise RuntimeError(f"missing R17 memory source {source_id}")

        # Required reset is support work and happens before STARTED/scientific exposure.
        try:
            reset_receipt = reset_shopping(a.reset_base, a.shopping_base, poll_seconds=a.reset_poll, timeout_seconds=a.reset_timeout)
        except Exception as exc:
            atomic_json(a.run_root / "pre-exposure-support-failure.json", {
                "sequence_index": seq, "task_id": task_id, "source_task_id": source_id,
                "status": "R19_PRE_EXPOSURE_RESET_SUPPORT_FAILURE", "recorded_at": now(),
                "error_class": type(exc).__name__, "error": str(exc)[:1000],
                "scientific_exposure": False, "exact_retry_not_automatically_executed": True,
            })
            raise
        atomic_json(a.run_root / "resets" / f"{seq:03d}.json", reset_receipt)

        joined = "\n\n".join(memories[source_id]["memory_items"])
        rendered = render_memory_file(joined, arm)
        memory_path = a.run_root / "episode-memory" / f"{seq:03d}.txt"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(rendered, encoding="utf-8")
        mem_sha = sha_file(memory_path)
        episode_id = f"seq{seq:03d}_task{task_id}_src{source_id}_rep{sched['repeat_id']}_{arm}"
        append_jsonl(attempts_path, {
            "sequence_index": seq, "episode_id": episode_id, "template_id": str(sched["template_id"]),
            "task_id": task_id, "source_task_id": source_id, "repeat_id": int(sched["repeat_id"]),
            "position_in_pair": int(sched["position_in_pair"]), "arm": arm, "status": "STARTED",
            "started_at": now(), "memory_file_sha256": mem_sha,
            "reset_receipt_sha256": sha_file(a.run_root / "resets" / f"{seq:03d}.json"),
        })

        agent_args, env_args = make_agent_env(GenericAgentArgs, Flags, ChatModelArgs, EnvArgs, task_id, memory_path)
        exp_args = ExpArgs(agent_args=agent_args, env_args=env_args, exp_name=episode_id, enable_debug=False, save_screenshot=False, save_som=False)
        episode_root = a.run_root / "browsergym"
        exp_args.prepare(episode_root)
        exp_args.run()
        exp_dir = Path(exp_args.exp_dir)
        summary_path = exp_dir / "summary_info.json"
        if not summary_path.is_file():
            atomic_json(a.run_root / "failure.json", {
                "sequence_index": seq, "episode_id": episode_id,
                "status": "R19_FAILED_NO_SUMMARY_AFTER_SCIENTIFIC_EXPOSURE", "recorded_at": now(),
                "scientific_exposure": True, "retry_forbidden": True,
            })
            raise RuntimeError(f"R19 episode {seq} produced no summary; retry forbidden")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary.get("err_msg"):
            atomic_json(a.run_root / "failure.json", {
                "sequence_index": seq, "episode_id": episode_id,
                "status": "R19_FAILED_BROWSERGYM_AFTER_SCIENTIFIC_EXPOSURE", "recorded_at": now(),
                "scientific_exposure": True, "retry_forbidden": True,
                "summary_info_sha256": sha_file(summary_path), "err_msg": str(summary.get("err_msg"))[:2000],
            })
            raise RuntimeError(f"R19 episode {seq} BrowserGym error; retry forbidden")

        score = float(summary.get("cum_reward") or 0.0)
        if score < 0.0 or score > 1.0:
            atomic_json(a.run_root / "failure.json", {
                "sequence_index": seq, "episode_id": episode_id,
                "status": "R19_FAILED_SCORE_RANGE_AFTER_SCIENTIFIC_EXPOSURE", "recorded_at": now(),
                "scientific_exposure": True, "retry_forbidden": True, "score": score,
            })
            raise RuntimeError(f"R19 episode {seq} score outside [0,1]")

        counts = count_agent_completions(exp_dir)
        n_steps = int(summary.get("n_steps") or 0)
        fuzzy_calls = n_steps if task_id in FUZZY_EVALUATOR_TASKS else 0
        if agent_total + counts["agent_completions"] > AGENT_COMPLETION_BUDGET:
            atomic_json(a.run_root / "failure.json", {
                "sequence_index": seq, "episode_id": episode_id,
                "status": "R19_FAILED_AGENT_COMPLETION_BUDGET_AFTER_SCIENTIFIC_EXPOSURE",
                "recorded_at": now(), "scientific_exposure": True, "retry_forbidden": True,
                "prior_total": agent_total, "episode_count": counts["agent_completions"],
            })
            raise RuntimeError("R19 agent completion budget exceeded")
        if evaluator_total + fuzzy_calls > FUZZY_EVALUATOR_COMPLETION_BUDGET:
            atomic_json(a.run_root / "failure.json", {
                "sequence_index": seq, "episode_id": episode_id,
                "status": "R19_FAILED_FUZZY_EVALUATOR_BUDGET_AFTER_SCIENTIFIC_EXPOSURE",
                "recorded_at": now(), "scientific_exposure": True, "retry_forbidden": True,
                "prior_total": evaluator_total, "episode_count": fuzzy_calls,
            })
            raise RuntimeError("R19 fuzzy evaluator completion budget exceeded")
        agent_total += counts["agent_completions"]
        evaluator_total += fuzzy_calls

        append_jsonl(progress_path, {
            "sequence_index": seq, "episode_id": episode_id, "template_id": str(sched["template_id"]),
            "task_id": task_id, "source_task_id": source_id, "repeat_id": int(sched["repeat_id"]),
            "position_in_pair": int(sched["position_in_pair"]), "arm": arm, "status": "COMPLETE",
            "completed_at": now(), "terminal_score": score, "browsergym_n_steps": n_steps,
            "agent_completion_count": counts["agent_completions"],
            "agent_parser_retry_completions": counts["parser_retry_completions"],
            "fuzzy_evaluator_completion_count": fuzzy_calls,
            "terminated": bool(summary.get("terminated")), "truncated": bool(summary.get("truncated")),
            "summary_info_sha256": sha_file(summary_path), "memory_file_sha256": mem_sha,
            "browsergym_exp_dir": str(exp_dir),
        })

    final_progress = read_jsonl(progress_path)
    out = {
        "schema_version": "1.0", "run_id": a.run_root.name, "updated_at": now(),
        "status": "R19_COMPLETE" if len(final_progress) == EPISODES else "R19_PARTIAL",
        "episodes_expected": EPISODES, "episodes_complete": len(final_progress),
        "agent_completions": sum(int(x.get("agent_completion_count") or 0) for x in final_progress),
        "fuzzy_evaluator_completions": sum(int(x.get("fuzzy_evaluator_completion_count") or 0) for x in final_progress),
        "scientific_outcomes_opened": len(final_progress) > 0,
        "failure_receipt_present": (a.run_root / "failure.json").exists(),
        "pre_exposure_support_failure_present": (a.run_root / "pre-exposure-support-failure.json").exists(),
        "ready_for_analysis": len(final_progress) == EPISODES and not (a.run_root / "failure.json").exists(),
    }
    atomic_json(a.run_root / "summary.json", out)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--authority-receipt", type=Path, required=True)
    p.add_argument("--support-receipt", type=Path, required=True)
    p.add_argument("--synthetic-smokes", type=Path, required=True)
    p.add_argument("--r17", type=Path, required=True)
    p.add_argument("--memories", type=Path, required=True)
    p.add_argument("--rb-webarena-root", type=Path, required=True)
    p.add_argument("--playwright-browsers", type=Path, required=True)
    p.add_argument("--shopping-base", required=True)
    p.add_argument("--reset-base", required=True)
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--max-new", type=int, default=None)
    p.add_argument("--reset-poll", type=float, default=2.0)
    p.add_argument("--reset-timeout", type=int, default=300)
    a = p.parse_args()
    print(json.dumps(execute(a), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
