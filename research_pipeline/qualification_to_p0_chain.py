from __future__ import annotations

import argparse
import json
import shlex
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .experiment_orchestrator import (
    active_idea_locations,
    build_launch_plan,
    inspect_cluster,
    launch_plan,
    load_profiles,
    profile_by_id,
    remote_execution_states,
    run_remote,
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def remote_exists(profile, path: str) -> bool:
    return run_remote(profile, f"test -f {shlex.quote(path)} && echo yes || echo no").strip() == "yes"


def remote_json(profile, path: str) -> dict[str, Any]:
    code = f"import json; print(json.dumps(json.load(open({path!r})), ensure_ascii=False))"
    return json.loads(run_remote(profile, f"{shlex.quote(profile.python)} -c {shlex.quote(code)}").strip())


def wait_for_shards(profile, shard_dirs: list[str], state_path: Path, poll_seconds: int) -> None:
    while True:
        ready = [remote_exists(profile, f"{directory}/summary.json") for directory in shard_dirs]
        write_state(state_path, {"updated_at": now(), "stage": "waiting-qualification-shards", "shards_ready": ready, "shard_dirs": shard_dirs})
        if all(ready):
            return
        time.sleep(poll_seconds)


def aggregate_remote(profile, shard_dirs: list[str], aggregate_path: str) -> dict[str, Any]:
    q = shlex.quote
    command = (
        f"cd {q(profile.repo)} && P0_EXTRA_SITE={q(profile.extra_pythonpath)} {q(profile.python)} "
        f"-m research_pipeline.aggregate_agent_qualification "
        + " ".join(q(path) for path in shard_dirs)
        + f" --gate-config {q(profile.repo + '/research_pipeline/p0_agent_qualification_config.json')} --output {q(aggregate_path)}"
    )
    text = run_remote(profile, command, timeout=60)
    start = text.find("{")
    if start < 0:
        raise RuntimeError("qualification aggregation returned no JSON")
    return json.loads(text[start:])


def wait_for_p0(profile, idea_id: str, expected_output_dir: str, state_path: Path, poll_seconds: int) -> dict[str, Any]:
    """Wait only for the execution created/adopted by this chain, ignoring stale same-idea state."""
    while True:
        states = remote_execution_states(profile)
        matches = [
            row for row in states
            if str(row.get("idea_id") or "") == idea_id
            and str(row.get("output_dir") or "") == expected_output_dir
        ]
        current = matches[0] if matches else {}
        write_state(state_path, {"updated_at": now(), "stage": "screening-running", "expected_output_dir": expected_output_dir, "execution_state": current})
        status = str(current.get("status") or "")
        if status in {"collected", "registered", "failed"}:
            return current
        time.sleep(poll_seconds)


def analyze_screening(profile, output_dir: str, config_name: str, idea_id: str) -> dict[str, Any]:
    q = shlex.quote
    frozen = f"{output_dir}/frozen-config.json"
    config = frozen if remote_exists(profile, frozen) else f"{profile.repo}/research_pipeline/{config_name}"
    analysis_input = "candidate-evaluation.jsonl" if idea_id == "update-trust-region" else "fixed-sequences.jsonl"
    command = (
        f"cd {q(profile.repo)} && P0_EXTRA_SITE={q(profile.extra_pythonpath)} {q(profile.python)} -m research_pipeline.p0_runner analyze {q(idea_id)} "
        f"--input {q(output_dir + '/' + analysis_input)} --config {q(config)} --output-dir {q(output_dir)} "
        f"--cost {q(output_dir + '/cost.json')} --manifest {q(output_dir + '/manifest.json')}"
    )
    text = run_remote(profile, command, timeout=120)
    start = text.find("{")
    if start < 0:
        raise RuntimeError("screening analysis returned no JSON")
    return json.loads(text[start:])


def run(args: argparse.Namespace) -> dict[str, Any]:
    defaults, profiles = load_profiles(args.profiles)
    profile = profile_by_id(profiles, args.server)
    state_path = args.state
    shard_dirs = list(args.shard_dirs)
    wait_for_shards(profile, shard_dirs, state_path, args.poll_seconds)

    aggregate = aggregate_remote(profile, shard_dirs, args.aggregate_output)
    write_state(state_path, {"updated_at": now(), "stage": "qualification-aggregated", "qualification": aggregate})
    if not bool((aggregate.get("gate") or {}).get("passed")):
        result = {"updated_at": now(), "stage": "stopped-base-agent-not-qualified", "qualification": aggregate, "screening_launched": False}
        write_state(state_path, result)
        return result

    cluster = inspect_cluster(profiles)
    expected_suffix = "/runs/" + args.screening_run_label
    active = active_idea_locations(cluster, args.idea_id)
    adopted = next((row for row in active if str(row.get("output_dir") or "").endswith(expected_suffix)), None)
    if adopted is not None:
        launch_profile = profile_by_id(profiles, str(adopted["server_id"]))
        launched = {
            "server_id": adopted["server_id"],
            "output_dir": adopted["output_dir"],
            "tmux_status": "adopted-active-execution",
        }
        write_state(state_path, {"updated_at": now(), "stage": "screening-adopted", "qualification": aggregate, "launch": launched})
    else:
        plan = build_launch_plan(
            args.idea_id,
            profiles,
            cluster,
            defaults,
            allow_repeat=True,
            run_label=args.screening_run_label,
            mode="collect",
            config_name=args.screening_config,
        )
        launched = launch_plan(plan, profiles)
        launch_profile = profile_by_id(profiles, str(launched["server_id"]))
        write_state(state_path, {"updated_at": now(), "stage": "screening-launched", "qualification": aggregate, "launch": launched})

    execution = wait_for_p0(launch_profile, args.idea_id, str(launched["output_dir"]), state_path, args.poll_seconds)
    if str(execution.get("status") or "") != "collected":
        result = {"updated_at": now(), "stage": "screening-execution-stopped", "qualification": aggregate, "execution_state": execution}
        write_state(state_path, result)
        return result

    analysis = analyze_screening(launch_profile, str(execution["output_dir"]), args.screening_config, args.idea_id)
    result = {
        "updated_at": now(),
        "stage": "screening-analyzed-await-human",
        "qualification": aggregate,
        "execution_state": execution,
        "screening": analysis,
        "automatic_confirmatory_launch": False,
    }
    write_state(state_path, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Qualification -> screening P0 chain; never auto-launches confirmatory P0.")
    parser.add_argument("--profiles", type=Path, default=Path(__file__).with_name("experiment_orchestrator_profiles.json"))
    parser.add_argument("--server", default="60")
    parser.add_argument("--shard-dirs", nargs="+", required=True)
    parser.add_argument("--aggregate-output", required=True)
    parser.add_argument("--idea-id", default="update-trust-region")
    parser.add_argument("--screening-config", default="p0_a1_screening_config.json")
    parser.add_argument("--screening-run-label", default="a1-screening-qwen-react-family")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(run(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
