from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_common import CONFIG_DIR, load_json


PROFILE_PATH = CONFIG_DIR / "experiment_orchestrator_profiles.json"
ACTIVE_STATES = {"running", "collected"}


@dataclass(frozen=True)
class ServerProfile:
    id: str
    ssh: str
    repo: str
    python: str
    data_root: str
    model_path: str
    extra_pythonpath: str
    alfworld_data: str
    enabled: bool = True
    priority: int = 100


@dataclass(frozen=True)
class GPUState:
    index: int
    uuid: str
    name: str
    memory_total_mib: int
    memory_free_mib: int
    utilization_gpu_pct: int


class RemoteError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-") or "run"


def load_profiles(path: Path = PROFILE_PATH) -> tuple[dict[str, Any], list[ServerProfile]]:
    payload = load_json(path)
    defaults = dict(payload.get("defaults") or {})
    profiles: list[ServerProfile] = []
    for row in payload.get("servers") or []:
        profiles.append(
            ServerProfile(
                id=str(row["id"]),
                ssh=str(row.get("ssh") or row["id"]),
                repo=str(row["repo"]),
                python=str(row["python"]),
                data_root=str(row["data_root"]),
                model_path=str(row["model_path"]),
                extra_pythonpath=str(row["extra_pythonpath"]),
                alfworld_data=str(row["alfworld_data"]),
                enabled=bool(row.get("enabled", True)),
                priority=int(row.get("priority", 100)),
            )
        )
    return defaults, profiles


def run_remote(profile: ServerProfile, command: str, timeout: int = 20) -> str:
    args = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={min(timeout, 10)}",
        profile.ssh,
        command,
    ]
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=timeout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
        output = getattr(error, "output", "") or ""
        raise RemoteError(f"{profile.id}: remote command failed: {output.strip() or error}") from error


def probe_gpus(profile: ServerProfile) -> list[GPUState]:
    text = run_remote(
        profile,
        "nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.free,utilization.gpu "
        "--format=csv,noheader,nounits",
    )
    rows: list[GPUState] = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 6:
            continue
        rows.append(
            GPUState(
                index=int(parts[0]),
                uuid=parts[1],
                name=parts[2],
                memory_total_mib=int(parts[3]),
                memory_free_mib=int(parts[4]),
                utilization_gpu_pct=int(parts[5]),
            )
        )
    return rows


def preflight(profile: ServerProfile) -> dict[str, Any]:
    q = shlex.quote
    command = (
        f"cd {q(profile.repo)} && {q(profile.python)} -m research_pipeline.p0_runner preflight "
        f"--model-path {q(profile.model_path)} --data-root {q(profile.data_root)} "
        f"--python {q(profile.python)} --extra-pythonpath {q(profile.extra_pythonpath)} "
        f"--alfworld-data {q(profile.alfworld_data)}"
    )
    text = run_remote(profile, command, timeout=45)
    start = text.find("{")
    if start < 0:
        raise RemoteError(f"{profile.id}: preflight returned no JSON")
    return json.loads(text[start:])


def remote_execution_states(profile: ServerProfile) -> list[dict[str, Any]]:
    code = f"""
import json
from pathlib import Path
root = Path({profile.data_root!r})
rows = []
state_dir = root / 'p0-executions'
if state_dir.exists():
    for path in sorted(state_dir.glob('*.json')):
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(row, dict):
                rows.append({{'path': str(path), **row}})
        except Exception:
            pass
legacy = root / 'p0-execution-state.json'
if legacy.exists():
    try:
        row = json.loads(legacy.read_text(encoding='utf-8'))
        if isinstance(row, dict):
            idea = str(row.get('idea_id') or '')
            if not any(str(item.get('idea_id') or '') == idea for item in rows):
                rows.append({{'path': str(legacy), **row, 'legacy': True}})
    except Exception:
        pass
print(json.dumps(rows, ensure_ascii=False))
""".strip()
    command = f"{shlex.quote(profile.python)} -c {shlex.quote(code)}"
    text = run_remote(profile, command)
    payload = json.loads(text.strip() or "[]")
    return [dict(row) for row in payload if isinstance(row, dict)]


def inspect_server(profile: ServerProfile) -> dict[str, Any]:
    result: dict[str, Any] = {"server_id": profile.id, "ssh": profile.ssh, "priority": profile.priority}
    if not profile.enabled:
        result.update({"reachable": False, "enabled": False, "error": "disabled"})
        return result
    try:
        result["gpus"] = [gpu.__dict__ for gpu in probe_gpus(profile)]
        ready = preflight(profile)
        result["preflight"] = {
            "environment_ready": bool(ready.get("environment_ready")),
            "launch_ready": bool(ready.get("launch_ready")),
            "blockers": list(ready.get("blockers") or []),
            "runtime_contract_hash": str(ready.get("runtime_contract_hash") or ""),
            "python_versions": dict(ready.get("python_versions") or {}),
            "smoke_ready": bool((ready.get("smoke_rollout") or {}).get("ready")),
        }
        result["execution_states"] = remote_execution_states(profile)
        result["reachable"] = True
        result["enabled"] = True
    except Exception as error:
        result.update({"reachable": False, "enabled": True, "error": str(error)})
    return result


def inspect_cluster(profiles: list[ServerProfile]) -> list[dict[str, Any]]:
    return [inspect_server(profile) for profile in sorted(profiles, key=lambda row: (row.priority, row.id))]


def active_idea_locations(cluster: list[dict[str, Any]], idea_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for server in cluster:
        for state in server.get("execution_states") or []:
            if str(state.get("idea_id") or "") == idea_id and str(state.get("status") or "").lower() in ACTIVE_STATES:
                matches.append({"server_id": server.get("server_id"), **state})
    return matches


def registered_idea_locations(cluster: list[dict[str, Any]], idea_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for server in cluster:
        for state in server.get("execution_states") or []:
            if str(state.get("idea_id") or "") == idea_id and str(state.get("status") or "").lower() == "registered":
                matches.append({"server_id": server.get("server_id"), **state})
    return matches


def choose_slot(
    cluster: list[dict[str, Any]],
    *,
    min_free_memory_mib: int,
    max_gpu_utilization_pct: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates: list[tuple[int, int, int, str, dict[str, Any], dict[str, Any]]] = []
    for server in cluster:
        if not server.get("reachable"):
            continue
        pf = server.get("preflight") or {}
        if not pf.get("launch_ready"):
            continue
        for gpu in server.get("gpus") or []:
            free = int(gpu.get("memory_free_mib") or 0)
            util = int(gpu.get("utilization_gpu_pct") or 0)
            if free < min_free_memory_mib or util > max_gpu_utilization_pct:
                continue
            # Lower server priority and lower utilization win; then prefer more free memory.
            candidates.append(
                (
                    int(server.get("priority") or 100),
                    util,
                    -free,
                    str(server.get("server_id") or ""),
                    server,
                    gpu,
                )
            )
    if not candidates:
        raise RuntimeError("no launch-ready GPU slot satisfies the requested memory/utilization limits")
    _, _, _, _, server, gpu = min(candidates, key=lambda row: row[:4])
    return server, gpu


def profile_by_id(profiles: list[ServerProfile], server_id: str) -> ServerProfile:
    for profile in profiles:
        if profile.id == server_id:
            return profile
    raise KeyError(server_id)


def remote_pre_experiment_card(profile: ServerProfile, idea_id: str, remote_config: str) -> dict[str, Any]:
    code = f"""
import json
from pathlib import Path
from research_pipeline.pre_experiment_compiler import compile_from_path, write_card
card = compile_from_path({idea_id!r}, Path({remote_config!r}), Path({profile.data_root!r}))
card['card_path'] = str(write_card(card, Path({profile.data_root!r})))
print(json.dumps(card, ensure_ascii=False))
""".strip()
    command = f"cd {shlex.quote(profile.repo)} && {shlex.quote(profile.python)} -c {shlex.quote(code)}"
    text = run_remote(profile, command, timeout=45)
    payload = json.loads(text.strip())
    if not isinstance(payload, dict):
        raise RemoteError(f"{profile.id}: Pre-Experiment Compiler returned invalid payload")
    return payload


def build_launch_plan(
    idea_id: str,
    profiles: list[ServerProfile],
    cluster: list[dict[str, Any]],
    defaults: dict[str, Any],
    *,
    allow_repeat: bool = False,
    run_label: str = "",
    mode: str = "execute",
    config_name: str = "",
) -> dict[str, Any]:
    active = active_idea_locations(cluster, idea_id)
    if active:
        where = ", ".join(f"{row['server_id']}:{row.get('status')}" for row in active)
        raise RuntimeError(f"{idea_id} already has an unresolved execution: {where}")
    registered = registered_idea_locations(cluster, idea_id)
    if registered and not allow_repeat:
        where = ", ".join(f"{row['server_id']}:{row.get('result', 'registered')}" for row in registered)
        raise RuntimeError(f"{idea_id} already has a registered P0 ({where}); use --allow-repeat only for an intentional repaired protocol")

    server, gpu = choose_slot(
        cluster,
        min_free_memory_mib=int(defaults.get("min_free_memory_mib", 18000)),
        max_gpu_utilization_pct=int(defaults.get("max_gpu_utilization_pct", 25)),
    )
    profile = profile_by_id(profiles, str(server["server_id"]))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = slug(run_label or f"{idea_id}-{timestamp}")
    output_dir = f"{profile.data_root}/runs/{run_id}"
    log_path = f"{profile.data_root}/{run_id}.log"
    session = slug(f"ae-{idea_id}-{timestamp}")[:80]
    q = shlex.quote
    if mode not in {"collect", "execute"}:
        raise ValueError(f"unsupported launch mode: {mode}")
    if not config_name:
        raise RuntimeError("scientific launch requires an explicit frozen config and 8/8 Pre-Experiment Card")
    remote_config = f"{profile.repo}/research_pipeline/{Path(config_name).name}"
    config_arg = f" --config {q(remote_config)}"
    pre_experiment = remote_pre_experiment_card(profile, idea_id, remote_config)
    if not pre_experiment.get("execution_authorized"):
        raise RuntimeError(
            f"{idea_id} blocked by Pre-Experiment Compiler on server {profile.id}: "
            + ", ".join(pre_experiment.get("blockers") or [])
        )
    expected_runtime = pre_experiment.get("expected_runtime") or {}
    expected_model = str(expected_runtime.get("competence_model_name") or "").strip()
    if expected_model and expected_model.lower() not in profile.model_path.lower():
        raise RuntimeError(
            f"{idea_id} qualified model mismatch on server {profile.id}: expected {expected_model}, runtime path is {profile.model_path}"
        )
    inner = (
        f"cd {q(profile.repo)} && "
        f"export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES={q(str(gpu['uuid']))} "
        f"ALFWORLD_DATA={q(profile.alfworld_data)} P0_EXTRA_SITE={q(profile.extra_pythonpath)}; "
        f"{q(profile.python)} -m research_pipeline.p0_runner {q(mode)} {q(idea_id)}{config_arg} "
        f"--model-path {q(profile.model_path)} --data-root {q(profile.data_root)} "
        f"--extra-pythonpath {q(profile.extra_pythonpath)} --alfworld-data {q(profile.alfworld_data)} "
        f"--output-dir {q(output_dir)} > {q(log_path)} 2>&1"
    )
    remote_command = f"tmux new-session -d -s {q(session)} {q(inner)}"
    return {
        "schema_version": "1.0",
        "planned_at": utc_now(),
        "idea_id": idea_id,
        "server_id": profile.id,
        "ssh": profile.ssh,
        "gpu_index": int(gpu["index"]),
        "gpu_uuid": str(gpu["uuid"]),
        "gpu_name": str(gpu["name"]),
        "runtime_model_path": profile.model_path,
        "gpu_free_mib": int(gpu["memory_free_mib"]),
        "gpu_utilization_pct": int(gpu["utilization_gpu_pct"]),
        "runtime_contract_hash": str((server.get("preflight") or {}).get("runtime_contract_hash") or ""),
        "pre_experiment_card": pre_experiment,
        "pre_experiment_status": f"{pre_experiment.get('passed_gates', 0)}/{pre_experiment.get('gate_count', 8)}",
        "run_id": run_id,
        "mode": mode,
        "config_name": Path(config_name).name if config_name else "",
        "remote_config": remote_config,
        "output_dir": output_dir,
        "log_path": log_path,
        "tmux_session": session,
        "remote_command": remote_command,
        "registered_prior": registered,
    }


def build_qualification_plan(
    profiles: list[ServerProfile],
    cluster: list[dict[str, Any]],
    defaults: dict[str, Any],
    *,
    model_path: str,
    run_label: str,
    server_id: str = "",
    gpu_index: int | None = None,
    split: str = "eval_in_distribution",
    num_envs: int = 24,
    max_steps: int = 50,
    seed: int = 42,
    policy_mode: str = "react-family",
    num_shards: int = 1,
    shard_index: int = 0,
) -> dict[str, Any]:
    if server_id:
        server = next((row for row in cluster if str(row.get("server_id")) == server_id), None)
        if server is None or not server.get("reachable"):
            raise RuntimeError(f"qualification server {server_id} is not reachable")
        if not (server.get("preflight") or {}).get("launch_ready"):
            raise RuntimeError(f"qualification server {server_id} is not launch-ready")
        gpus = list(server.get("gpus") or [])
        if gpu_index is None:
            eligible = [g for g in gpus if int(g.get("memory_free_mib") or 0) >= int(defaults.get("min_free_memory_mib", 18000)) and int(g.get("utilization_gpu_pct") or 0) <= int(defaults.get("max_gpu_utilization_pct", 25))]
            if not eligible:
                raise RuntimeError(f"no free qualification GPU on server {server_id}")
            gpu = max(eligible, key=lambda row: int(row.get("memory_free_mib") or 0))
        else:
            gpu = next((row for row in gpus if int(row.get("index")) == int(gpu_index)), None)
            if gpu is None:
                raise RuntimeError(f"GPU index {gpu_index} not found on server {server_id}")
    else:
        server, gpu = choose_slot(
            cluster,
            min_free_memory_mib=int(defaults.get("min_free_memory_mib", 18000)),
            max_gpu_utilization_pct=int(defaults.get("max_gpu_utilization_pct", 25)),
        )
    profile = profile_by_id(profiles, str(server["server_id"]))
    q = shlex.quote
    verify_model = f"test -f {q(model_path + '/config.json')} && test -f {q(model_path + '/model.safetensors.index.json')}"
    run_remote(profile, verify_model)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = slug(run_label or f"qualification-{Path(model_path).name}-{timestamp}")
    output_dir = f"{profile.data_root}/qualification/{run_id}"
    log_path = f"{profile.data_root}/qualification-{run_id}.log"
    session = slug(f"ae-qual-{run_id}-{timestamp}")[:80]
    inner = (
        f"cd {q(profile.repo)} && "
        f"export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES={q(str(gpu['uuid']))} "
        f"ALFWORLD_DATA={q(profile.alfworld_data)} P0_EXTRA_SITE={q(profile.extra_pythonpath)}; "
        f"{q(profile.python)} -m research_pipeline.agent_competence_qualification "
        f"--model-path {q(model_path)} --alfworld-config {q(profile.repo + '/research_pipeline/p0_alfworld_config.yaml')} "
        f"--output-dir {q(output_dir)} --split {q(split)} --num-envs {int(num_envs)} --max-steps {int(max_steps)} "
        f"--seed {int(seed)} --policy-mode {q(policy_mode)} --num-shards {int(num_shards)} --shard-index {int(shard_index)} > {q(log_path)} 2>&1"
    )
    return {
        "schema_version": "1.0",
        "planned_at": utc_now(),
        "job_type": "agent-qualification",
        "server_id": profile.id,
        "ssh": profile.ssh,
        "gpu_index": int(gpu["index"]),
        "gpu_uuid": str(gpu["uuid"]),
        "gpu_name": str(gpu["name"]),
        "model_path": model_path,
        "policy_mode": policy_mode,
        "split": split,
        "num_envs": int(num_envs),
        "max_steps": int(max_steps),
        "seed": int(seed),
        "num_shards": int(num_shards),
        "shard_index": int(shard_index),
        "run_id": run_id,
        "output_dir": output_dir,
        "log_path": log_path,
        "tmux_session": session,
        "remote_command": f"tmux new-session -d -s {q(session)} {q(inner)}",
    }


def launch_plan(plan: dict[str, Any], profiles: list[ServerProfile]) -> dict[str, Any]:
    profile = profile_by_id(profiles, str(plan["server_id"]))
    run_remote(profile, str(plan["remote_command"]), timeout=15)
    session = str(plan["tmux_session"])
    verify = run_remote(profile, f"tmux has-session -t {shlex.quote(session)} 2>/dev/null && echo running || echo missing")
    return {**plan, "launch_checked_at": utc_now(), "tmux_status": verify.strip()}


def mark_remote_execution_failed(profile: ServerProfile, idea_id: str, reason: str) -> None:
    code = f"""
import json
from datetime import datetime, timezone
from pathlib import Path
path = Path({profile.data_root!r}) / 'p0-executions' / ({idea_id!r} + '.json')
if path.exists():
    row = json.loads(path.read_text(encoding='utf-8'))
    row.update({{
        'status': 'failed',
        'finished_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'failure_kind': 'orchestrator-stop',
        'scientific_result_available': False,
        'diagnosis': {reason!r},
    }})
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
    tmp.replace(path)
""".strip()
    run_remote(profile, f"{shlex.quote(profile.python)} -c {shlex.quote(code)}")


def stop_plan(plan: dict[str, Any], profiles: list[ServerProfile]) -> dict[str, Any]:
    profile = profile_by_id(profiles, str(plan["server_id"]))
    session = str(plan["tmux_session"])
    run_remote(profile, f"tmux kill-session -t {shlex.quote(session)} 2>/dev/null || true")
    return {**plan, "stopped_at": utc_now(), "tmux_status": "stopped"}


def summarize_cluster(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    servers = []
    active: list[dict[str, Any]] = []
    registered: list[dict[str, Any]] = []
    for row in cluster:
        free_slots = [
            gpu
            for gpu in row.get("gpus") or []
            if int(gpu.get("memory_free_mib") or 0) >= 18000 and int(gpu.get("utilization_gpu_pct") or 0) <= 25
        ]
        servers.append(
            {
                "server_id": row.get("server_id"),
                "reachable": bool(row.get("reachable")),
                "launch_ready": bool((row.get("preflight") or {}).get("launch_ready")),
                "free_candidate_gpus": len(free_slots),
                "gpus": row.get("gpus") or [],
                "error": row.get("error", ""),
            }
        )
        for state in row.get("execution_states") or []:
            combined = {"server_id": row.get("server_id"), **state}
            status = str(state.get("status") or "").lower()
            if status in ACTIVE_STATES:
                active.append(combined)
            elif status == "registered":
                registered.append(combined)
    return {"generated_at": utc_now(), "servers": servers, "active": active, "registered": registered}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-server experiment scheduler for small P0 runs.")
    parser.add_argument("--profiles", type=Path, default=PROFILE_PATH)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    plan = sub.add_parser("plan")
    plan.add_argument("idea_id")
    plan.add_argument("--allow-repeat", action="store_true")
    plan.add_argument("--run-label", default="")
    plan.add_argument("--mode", choices=["collect", "execute"], default="execute")
    plan.add_argument("--config", default="")
    launch = sub.add_parser("launch")
    launch.add_argument("idea_id")
    launch.add_argument("--allow-repeat", action="store_true")
    launch.add_argument("--run-label", default="")
    launch.add_argument("--mode", choices=["collect", "execute"], default="execute")
    launch.add_argument("--config", default="")
    for command in ("qual-plan", "qual-launch"):
        qual = sub.add_parser(command)
        qual.add_argument("--model-path", required=True)
        qual.add_argument("--run-label", required=True)
        qual.add_argument("--server", default="")
        qual.add_argument("--gpu-index", type=int)
        qual.add_argument("--split", default="eval_in_distribution")
        qual.add_argument("--num-envs", type=int, default=24)
        qual.add_argument("--max-steps", type=int, default=50)
        qual.add_argument("--seed", type=int, default=42)
        qual.add_argument("--policy-mode", choices=["direct", "react-lite", "react-family"], default="react-family")
        qual.add_argument("--num-shards", type=int, default=1)
        qual.add_argument("--shard-index", type=int, default=0)
    stop = sub.add_parser("stop")
    stop.add_argument("--server", required=True)
    stop.add_argument("--session", required=True)
    stop.add_argument("--idea", default="")
    stop.add_argument("--reason", default="stopped by experiment orchestrator")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    defaults, profiles = load_profiles(args.profiles)
    cluster = inspect_cluster(profiles)
    if args.command == "status":
        print(json.dumps(summarize_cluster(cluster), ensure_ascii=False, indent=2))
        return
    if args.command == "stop":
        profile = profile_by_id(profiles, str(args.server))
        session = str(args.session)
        run_remote(profile, f"tmux kill-session -t {shlex.quote(session)} 2>/dev/null || true")
        if str(args.idea or ""):
            mark_remote_execution_failed(profile, str(args.idea), str(args.reason))
        print(json.dumps({"server_id": profile.id, "tmux_session": session, "idea_id": str(args.idea or ""), "status": "stop-requested", "stopped_at": utc_now()}, ensure_ascii=False, indent=2))
        return
    if args.command in {"qual-plan", "qual-launch"}:
        plan = build_qualification_plan(
            profiles,
            cluster,
            defaults,
            model_path=str(args.model_path),
            run_label=str(args.run_label),
            server_id=str(args.server or ""),
            gpu_index=args.gpu_index,
            split=str(args.split),
            num_envs=int(args.num_envs),
            max_steps=int(args.max_steps),
            seed=int(args.seed),
            policy_mode=str(args.policy_mode),
            num_shards=int(args.num_shards),
            shard_index=int(args.shard_index),
        )
        if args.command == "qual-plan":
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(launch_plan(plan, profiles), ensure_ascii=False, indent=2))
        return
    plan = build_launch_plan(
        args.idea_id,
        profiles,
        cluster,
        defaults,
        allow_repeat=bool(args.allow_repeat),
        run_label=str(args.run_label or ""),
        mode=str(args.mode),
        config_name=str(args.config or ""),
    )
    if args.command == "plan":
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    print(json.dumps(launch_plan(plan, profiles), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
