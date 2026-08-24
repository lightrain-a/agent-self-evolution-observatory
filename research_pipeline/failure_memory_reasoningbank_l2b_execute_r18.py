#!/usr/bin/env python3
"""Execute the authorized B1/L2B 144-episode metadata-only intervention.

This runner implements the already-frozen R15 schedule. It is append-only and
fail-closed: once an episode is marked STARTED, it is never automatically
retried. Every episode receives a fresh official Shopping reset before the
STARTED marker. The source memory is frozen by R17; only the final status byte
(S/F) changes across paired arms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.failure_memory_reasoningbank_execution_authority_r16 import require_authority
from research_pipeline.failure_memory_reasoningbank_executor_contract_r15 import render_memory_file

EXPECTED_R15_SHA = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_R16_SHA = "f12b18c129c4e65c076b2f811b65a0a505bf618665f63c87fb883c6d4cf72b4b"
EXPECTED_R17_SHA = "58de4f998b16aace4ddfeef0693d88a347b293c032d997e0da471e6b92c69235"
EXPECTED_PRIVATE_MEMORIES_SHA = "2d056b69202653c2a61c16107f13f164707d2564db73cc858589d1c35f4f3dd2"
EXPECTED_EXECUTOR_MANIFEST = "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
EXECUTOR_MODEL = "b1-qwen25-32b-l2b-executor:latest"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_bound(path: Path, expected: str, name: str) -> dict[str, Any]:
    actual = sha_file(path)
    if actual != expected:
        raise RuntimeError(f"{name} SHA drift: {actual} != {expected}")
    return json.loads(path.read_text(encoding="utf-8"))


def http_get(url: str, timeout: int = 10) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return int(r.status), r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return int(e.code), e.read().decode("utf-8", errors="replace")


def reset_shopping(reset_base: str, shopping_base: str, *, poll_seconds: float = 3.0, timeout_seconds: int = 300) -> dict[str, Any]:
    reset_base = reset_base.rstrip("/")
    # If an old support reset is still running, wait for it to finish first;
    # that old reset does not count as this episode's required reset.
    deadline = time.monotonic() + timeout_seconds
    while True:
        code, body = http_get(reset_base + "/status?domain=shopping", timeout=10)
        if code == 200 and "Ready for duty" in body:
            break
        if code >= 400 and "Reset ongoing" not in body:
            raise RuntimeError(f"pre-reset status failed: HTTP {code}: {body[:300]}")
        if time.monotonic() >= deadline:
            raise RuntimeError("pre-reset wait timed out")
        time.sleep(poll_seconds)

    started_at = now()
    code, body = http_get(reset_base + "/reset?domain=shopping", timeout=10)
    if code != 200 or "Reset initiated" not in body:
        raise RuntimeError(f"reset trigger failed: HTTP {code}: {body[:300]}")
    deadline = time.monotonic() + timeout_seconds
    polls = 0
    while True:
        time.sleep(poll_seconds)
        polls += 1
        code, body = http_get(reset_base + "/status?domain=shopping", timeout=10)
        if code == 200 and "Ready for duty" in body:
            break
        if code >= 400:
            raise RuntimeError(f"reset status failed: HTTP {code}: {body[:500]}")
        if time.monotonic() >= deadline:
            raise RuntimeError("shopping reset timed out")
    health_code, _ = http_get(shopping_base.rstrip("/") + "/", timeout=20)
    if health_code not in {200, 301, 302}:
        raise RuntimeError(f"shopping health failed after reset: HTTP {health_code}")
    return {"started_at": started_at, "ready_at": now(), "polls": polls, "health_http": health_code}


def load_private_memories(path: Path, r17: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if sha_file(path) != EXPECTED_PRIVATE_MEMORIES_SHA:
        raise RuntimeError("private R17 memories SHA drift")
    rows = read_jsonl(path)
    if len(rows) != 36:
        raise RuntimeError("private R17 memories must contain 36 rows")
    by_id = {str(x["source_task_id"]): x for x in rows}
    if len(by_id) != 36:
        raise RuntimeError("private R17 memory source IDs not unique")
    manifest = {str(x["source_task_id"]): x for x in r17["source_memory_manifest"]}
    for tid, row in by_id.items():
        joined = "\n\n".join(row["memory_items"]).encode("utf-8")
        if sha_bytes(joined) != manifest[tid]["joined_memory_bytes_sha256"]:
            raise RuntimeError(f"private/public R17 memory SHA mismatch: {tid}")
    return by_id


def prepare_first_party_imports(rb_webarena_root: Path) -> tuple[Any, Any, Any, Any, Any]:
    sys.path.insert(0, str(rb_webarena_root))
    from agents.legacy.agent import GenericAgentArgs
    from agents.legacy.dynamic_prompting import Flags
    from agents.legacy.utils.chat_api import ChatModelArgs
    from browsergym.experiments import EnvArgs, ExpArgs
    return GenericAgentArgs, Flags, ChatModelArgs, EnvArgs, ExpArgs


def configure_environment(shopping_base: str, reset_base: str, playwright_browsers: Path) -> None:
    from urllib.parse import urlsplit
    s = urlsplit(shopping_base)
    hostbase = f"{s.scheme}://{s.hostname}"
    # WebArenaInstance asserts all URL variables are populated at construction.
    # The frozen cohort is Shopping-only, so only :7770 is an executed site.
    values = {
        "SHOPPING": shopping_base.rstrip("/"),
        "SHOPPING_ADMIN": hostbase + ":7780/admin",
        "REDDIT": hostbase + ":9999",
        "GITLAB": hostbase + ":8023",
        "WIKIPEDIA": hostbase + ":8888",
        "MAP": hostbase + ":3000",
        "HOMEPAGE": reset_base.rstrip("/"),
    }
    for k, v in values.items():
        os.environ[k] = v
        os.environ["WA_" + k] = v
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(playwright_browsers)
    os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:11444/v1"
    os.environ["OPENAI_API_KEY"] = "ollama"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def make_agent_env(GenericAgentArgs: Any, Flags: Any, ChatModelArgs: Any, EnvArgs: Any, task_id: str, memory_path: Path) -> tuple[Any, Any]:
    chat = ChatModelArgs(
        model_name="openai/" + EXECUTOR_MODEL,
        temperature=0.0,
        max_new_tokens=4096,
        max_total_tokens=32768,
        max_input_tokens=28672,
        n_retry_server=1,
    )
    flags = Flags(
        use_html=False,
        use_ax_tree=True,
        use_thinking=True,
        use_error_logs=True,
        use_memory=False,
        use_history=True,
        use_diff=False,
        use_past_error_logs=True,
        use_action_history=True,
        multi_actions=True,
        use_abstract_example=True,
        use_concrete_example=True,
        use_screenshot=False,
        enable_chat=True,
        demo_mode="default",
        memory_path=str(memory_path),
    )
    agent = GenericAgentArgs(chat_model_args=chat, flags=flags)
    env = EnvArgs(
        task_name=f"browsergym/webarena.{task_id}",
        task_seed=0,
        max_steps=30,
        headless=True,
        viewport={"width": 1500, "height": 1280},
        slow_mo=30,
    )
    return agent, env


def execute(args: argparse.Namespace) -> dict[str, Any]:
    authority = require_authority(args.authority)
    r15 = load_bound(args.r15, EXPECTED_R15_SHA, "R15")
    r16 = load_bound(args.r16, EXPECTED_R16_SHA, "R16")
    r17 = load_bound(args.r17, EXPECTED_R17_SHA, "R17")
    if r16["authority_artifact_sha256"] != authority["artifact_sha256"]:
        raise RuntimeError("R16 external authority artifact mismatch")
    if r17["downstream_gate"]["144_terminal_episode_execution_may_begin"] is not True:
        raise RuntimeError("R17 did not unlock downstream execution")
    if r15["executor"]["executor_manifest_digest"] != EXPECTED_EXECUTOR_MANIFEST:
        raise RuntimeError("R15 executor manifest drift")
    schedule = r15["cohort_and_rollouts"]["episode_schedule"]
    if len(schedule) != 144:
        raise RuntimeError("R15 schedule is not 144 episodes")
    memories = load_private_memories(args.memories, r17)
    configure_environment(args.shopping_base, args.reset_base, args.playwright_browsers)
    GenericAgentArgs, Flags, ChatModelArgs, EnvArgs, ExpArgs = prepare_first_party_imports(args.rb_webarena_root)

    args.run_root.mkdir(parents=True, exist_ok=True)
    attempts_path = args.run_root / "attempts.jsonl"
    progress_path = args.run_root / "progress.jsonl"
    attempts = read_jsonl(attempts_path)
    progress = read_jsonl(progress_path)
    attempted = [int(x["sequence_index"]) for x in attempts if x.get("status") == "STARTED"]
    complete = [int(x["sequence_index"]) for x in progress if x.get("status") == "COMPLETE"]
    if len(attempted) != len(set(attempted)) or len(complete) != len(set(complete)):
        raise RuntimeError("duplicate episode ledger row")
    if set(attempted) != set(complete):
        uncertain = sorted(set(attempted) - set(complete))
        raise RuntimeError(f"prior episode STARTED without durable COMPLETE; retry forbidden: {uncertain}")
    if any(x.get("status") != "COMPLETE" for x in progress):
        raise RuntimeError("progress contains non-complete row")
    expected_prefix = list(range(len(complete)))
    if sorted(complete) != expected_prefix:
        raise RuntimeError("completed episodes are not an exact R15 prefix")
    completion_calls = sum(int(x.get("executor_completion_count") or 0) for x in progress)
    if completion_calls > 4320:
        raise RuntimeError("executor completion budget already exceeded")
    if (args.run_root / "failure.json").exists():
        raise RuntimeError("R18 failure receipt exists; execution is permanently stopped")

    run_contract = {
        "schema_version": "1.0",
        "run_id": args.run_root.name,
        "created_at": now(),
        "status": "R18_IN_PROGRESS" if len(complete) < 144 else "R18_COMPLETE",
        "bindings": {"r15": EXPECTED_R15_SHA, "r16": EXPECTED_R16_SHA, "r17": EXPECTED_R17_SHA, "private_memories": EXPECTED_PRIVATE_MEMORIES_SHA, "executor_manifest": EXPECTED_EXECUTOR_MANIFEST},
        "authority_artifact_sha256": authority["artifact_sha256"],
        "shopping_base": args.shopping_base,
        "reset_base": args.reset_base,
        "policy": {"schedule_length": 144, "no_episode_retry_after_started": True, "reset_before_every_episode": True, "model_internal_retries": 1, "task_replacement": False, "endpoint_switch": False},
        "already_complete": complete,
    }
    atomic_json(args.run_root / "run-contract.json", run_contract)

    remaining = [x for x in schedule if int(x["sequence_index"]) not in set(complete)]
    limit = len(remaining) if args.max_new is None else min(args.max_new, len(remaining))
    for sched in remaining[:limit]:
        seq = int(sched["sequence_index"])
        if seq != len(read_jsonl(progress_path)):
            raise RuntimeError("R18 schedule prefix drift immediately before episode")
        task_id = str(sched["task_id"])
        source_id = str(sched["source_task_id"])
        arm = str(sched["arm"])
        if source_id not in memories:
            raise RuntimeError(f"missing R17 memory source {source_id}")

        # Required support reset happens before scientific exposure / STARTED.
        try:
            reset_receipt = reset_shopping(args.reset_base, args.shopping_base, poll_seconds=args.reset_poll, timeout_seconds=args.reset_timeout)
        except Exception as exc:
            atomic_json(args.run_root / "support-failure.json", {"sequence_index": seq, "task_id": task_id, "source_task_id": source_id, "status": "PRE_OUTCOME_RESET_SUPPORT_FAILURE", "recorded_at": now(), "error_class": type(exc).__name__, "error": str(exc)[:1000], "scientific_outcome_opened": False})
            raise
        atomic_json(args.run_root / "resets" / f"{seq:03d}.json", reset_receipt)

        joined = "\n\n".join(memories[source_id]["memory_items"])
        rendered = render_memory_file(joined, arm)
        memory_path = args.run_root / "episode-memory" / f"{seq:03d}.txt"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(rendered, encoding="utf-8")
        mem_sha = sha_file(memory_path)
        episode_id = f"seq{seq:03d}_task{task_id}_src{source_id}_rep{sched['repeat_id']}_{arm}"
        append_jsonl(attempts_path, {
            "sequence_index": seq,
            "episode_id": episode_id,
            "task_id": task_id,
            "source_task_id": source_id,
            "repeat_id": int(sched["repeat_id"]),
            "position_in_pair": int(sched["position_in_pair"]),
            "arm": arm,
            "status": "STARTED",
            "started_at": now(),
            "memory_file_sha256": mem_sha,
            "reset_receipt_sha256": sha_file(args.run_root / "resets" / f"{seq:03d}.json"),
        })

        agent_args, env_args = make_agent_env(GenericAgentArgs, Flags, ChatModelArgs, EnvArgs, task_id, memory_path)
        exp_args = ExpArgs(agent_args=agent_args, env_args=env_args, exp_name=episode_id, enable_debug=False, save_screenshot=False, save_som=False)
        episode_root = args.run_root / "browsergym"
        exp_args.prepare(episode_root)
        exp_args.run()
        summary_path = Path(exp_args.exp_dir) / "summary_info.json"
        if not summary_path.is_file():
            failure = {"sequence_index": seq, "episode_id": episode_id, "status": "FAILED_NO_SUMMARY_AFTER_SCIENTIFIC_EXPOSURE", "recorded_at": now(), "scientific_outcome_opened": True}
            atomic_json(args.run_root / "failure.json", failure)
            raise RuntimeError(f"R18 episode {seq} produced no BrowserGym summary; retry forbidden")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        err = summary.get("err_msg")
        if err:
            failure = {"sequence_index": seq, "episode_id": episode_id, "status": "FAILED_BROWSERGYM_AFTER_SCIENTIFIC_EXPOSURE", "recorded_at": now(), "scientific_outcome_opened": True, "summary_info_sha256": sha_file(summary_path), "err_msg": str(err)[:2000]}
            atomic_json(args.run_root / "failure.json", failure)
            raise RuntimeError(f"R18 episode {seq} BrowserGym error; retry forbidden: {str(err)[:300]}")
        score = float(summary.get("cum_reward") or 0.0)
        if score < 0.0 or score > 1.0:
            failure = {"sequence_index": seq, "episode_id": episode_id, "status": "FAILED_SCORE_RANGE_AFTER_SCIENTIFIC_EXPOSURE", "score": score, "recorded_at": now(), "scientific_outcome_opened": True}
            atomic_json(args.run_root / "failure.json", failure)
            raise RuntimeError(f"R18 episode {seq} score outside [0,1]")
        n_steps = int(summary.get("n_steps") or 0)
        new_total = completion_calls + n_steps
        if new_total > 4320:
            failure = {"sequence_index": seq, "episode_id": episode_id, "status": "FAILED_COMPLETION_BUDGET_AFTER_SCIENTIFIC_EXPOSURE", "new_total": new_total, "recorded_at": now(), "scientific_outcome_opened": True}
            atomic_json(args.run_root / "failure.json", failure)
            raise RuntimeError("R18 executor completion budget exceeded")
        completion_calls = new_total
        row = {
            "sequence_index": seq,
            "episode_id": episode_id,
            "task_id": task_id,
            "source_task_id": source_id,
            "repeat_id": int(sched["repeat_id"]),
            "position_in_pair": int(sched["position_in_pair"]),
            "arm": arm,
            "status": "COMPLETE",
            "completed_at": now(),
            "terminal_score": score,
            "executor_completion_count": n_steps,
            "terminated": bool(summary.get("terminated")),
            "truncated": bool(summary.get("truncated")),
            "summary_info_sha256": sha_file(summary_path),
            "memory_file_sha256": mem_sha,
            "browsergym_exp_dir": str(exp_args.exp_dir),
        }
        append_jsonl(progress_path, row)

    final_progress = read_jsonl(progress_path)
    out = {
        "schema_version": "1.0",
        "run_id": args.run_root.name,
        "updated_at": now(),
        "status": "R18_COMPLETE" if len(final_progress) == 144 else "R18_PARTIAL",
        "episodes_expected": 144,
        "episodes_complete": len(final_progress),
        "executor_completions": sum(int(x.get("executor_completion_count") or 0) for x in final_progress),
        "scientific_outcomes_opened": len(final_progress) > 0,
        "failure_receipt_present": (args.run_root / "failure.json").exists(),
        "ready_for_analysis": len(final_progress) == 144 and not (args.run_root / "failure.json").exists(),
    }
    atomic_json(args.run_root / "summary.json", out)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--r15", type=Path, required=True)
    p.add_argument("--r16", type=Path, required=True)
    p.add_argument("--r17", type=Path, required=True)
    p.add_argument("--memories", type=Path, required=True)
    p.add_argument("--rb-webarena-root", type=Path, required=True)
    p.add_argument("--playwright-browsers", type=Path, required=True)
    p.add_argument("--shopping-base", required=True)
    p.add_argument("--reset-base", required=True)
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--max-new", type=int, default=None)
    p.add_argument("--reset-poll", type=float, default=3.0)
    p.add_argument("--reset-timeout", type=int, default=300)
    a = p.parse_args()
    print(json.dumps(execute(a), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
