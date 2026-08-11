from __future__ import annotations

import argparse
import fcntl
import json
import os
import site
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings
from .p0_a1 import analyze as analyze_a1, synthetic_rows as synthetic_a1
from .p0_a2 import analyze as analyze_a2, synthetic_rows as synthetic_a2
from .p0_alfworld_adapter import run_lightweight_smoke, run_smoke
from .p0_alfworld_collect import collect_a1, collect_a2
from .p0_common import (
    CONFIG_DIR,
    READINESS_JS,
    READINESS_JSON,
    SUPPORTED_IDEAS,
    load_json,
    load_jsonl,
    register_result,
    result_payload,
    runtime_preflight,
    validate_collection_manifest,
    validate_measured_cost,
    write_csv,
    write_readiness,
)
from .pilot_registry import CURRENT_P0_GATE
from .pre_experiment_compiler import compile_from_path as compile_pre_experiment_from_path, write_card as write_pre_experiment_card
from .governance_protocol import evaluate_stage_contract
from .trace_preflight import pre_model_load_audit, validate_raw_trace_file


def config_path(idea_id: str) -> Path:
    names = {
        "update-trust-region": "p0_a1_config.json",
        "budgeted-evolution-controller": "p0_a2_config.json",
    }
    return CONFIG_DIR / names[idea_id]


def analyze_rows(idea_id: str, rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    if idea_id == "update-trust-region":
        return analyze_a1(rows, config)
    if idea_id == "budgeted-evolution-controller":
        return analyze_a2(rows, config)
    raise ValueError(f"unsupported P0 idea: {idea_id}")


def synthetic_rows(idea_id: str) -> list[dict[str, Any]]:
    return synthetic_a1() if idea_id == "update-trust-region" else synthetic_a2()


def dry_run(idea_id: str, output_dir: Path | None = None) -> dict[str, Any]:
    config = load_json(config_path(idea_id))
    analysis = analyze_rows(idea_id, synthetic_rows(idea_id), config)
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_csv(output_dir / "main_table.csv", analysis["table"])
        synthetic_result = result_payload(analysis, config)
        synthetic_result["synthetic_fixture"] = True
        (output_dir / "synthetic-do-not-register.json").write_text(json.dumps(synthetic_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return analysis


def analyze_file(
    idea_id: str,
    input_path: Path,
    config_file: Path,
    output_dir: Path,
    cost_file: Path | None,
    manifest_file: Path | None,
    register: bool,
) -> dict[str, Any]:
    config = load_json(config_file)
    analysis = analyze_rows(idea_id, load_jsonl(input_path), config)
    cost = load_json(cost_file) if cost_file else None
    if cost is not None:
        cost_errors = validate_measured_cost(config, cost)
        if cost_errors:
            raise ValueError("invalid measured cost: " + "; ".join(cost_errors))
    if register:
        if cost is None:
            raise ValueError("real P0 registration requires --cost")
        if manifest_file is None:
            raise ValueError("real P0 registration requires --manifest")
        manifest = load_json(manifest_file)
        manifest_errors = validate_collection_manifest(idea_id, config, input_path, cost, manifest)
        if manifest_errors:
            raise ValueError("invalid collection manifest: " + "; ".join(manifest_errors))
    config_phase = str(config.get("phase") or "P0")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(output_dir / "main_table.csv", analysis.get("table") or [])
    if config_phase != "P0":
        if register:
            raise ValueError(f"{config_phase} analysis cannot be registered as a Pilot result")
        result = {
            "schema_version": "1.0",
            "artifact_kind": "screening-analysis",
            "idea_id": idea_id,
            "phase": config_phase,
            "decision": analysis.get("decision"),
            "analysis": analysis,
            "cost": cost or {},
            "next_action": "resolve-pre-experiment-blockers-before-confirmatory-p0",
        }
    else:
        result = result_payload(analysis, config, cost)
        if register:
            result["registered_path"] = str(register_result(result))
    (output_dir / "decision.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_execution_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def execution_state_path(data_root: Path, idea_id: str) -> Path:
    return data_root / "p0-executions" / f"{idea_id}.json"


@contextmanager
def p0_execution_lock(data_root: Path, idea_id: str = "legacy"):
    """Serialize only the same P0 idea; distinct ideas may run concurrently."""
    state_path = execution_state_path(data_root, idea_id)
    lock_path = state_path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"another real P0 process already holds the execution lock for {idea_id}") from error
        prior_states: list[dict[str, Any]] = []
        if state_path.exists():
            try:
                prior_states.append(load_json(state_path))
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        legacy_path = data_root / "p0-execution-state.json"
        if legacy_path.exists():
            try:
                legacy = load_json(legacy_path)
                if str(legacy.get("idea_id") or "") == idea_id:
                    prior_states.append(legacy)
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        if any(str(prior.get("status") or "") in {"running", "collected"} for prior in prior_states):
            raise RuntimeError(
                f"previous P0 execution for {idea_id} is unresolved; finish/register it or explicitly repair its state before relaunch"
            )
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def collect_real_p0(
    idea_id: str,
    experiment_config: Path | None,
    alfworld_config: Path,
    model_path: Path,
    data_root: Path,
    extra_pythonpath: Path,
    alfworld_data: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if CURRENT_P0_GATE.get(idea_id) != "ready":
        raise RuntimeError(f"{idea_id} is not scientifically authorized for P0")
    if experiment_config is None:
        raise RuntimeError("real P0 collect/execute requires an explicit frozen --config and 8/8 Pre-Experiment Card")
    config_file = experiment_config
    config_payload = load_json(config_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    frozen_config = output_dir / "frozen-config.json"
    if frozen_config.exists() and frozen_config.stat().st_size:
        existing = load_json(frozen_config)
        if existing != config_payload:
            raise RuntimeError(f"refusing to reuse output_dir with a different frozen config: {frozen_config}")
    else:
        tmp_config = frozen_config.with_suffix(frozen_config.suffix + ".tmp")
        tmp_config.write_text(json.dumps(config_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp_config.replace(frozen_config)
    governance = evaluate_stage_contract(idea_id, config_payload, data_root)
    (output_dir / "governance-stage-contract.json").write_text(json.dumps(governance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not governance.get("execution_authorized"):
        raise RuntimeError(f"{idea_id} blocked by Research Governance v2: " + ", ".join(governance.get("blockers") or []))
    pre_experiment = compile_pre_experiment_from_path(idea_id, frozen_config, data_root)
    card_path = write_pre_experiment_card(pre_experiment, data_root)
    if not pre_experiment["execution_authorized"]:
        raise RuntimeError(
            f"{idea_id} is blocked by Pre-Experiment Compiler: " + ", ".join(pre_experiment["blockers"])
        )
    expected_model = str((pre_experiment.get("expected_runtime") or {}).get("competence_model_name") or "").strip()
    if expected_model and expected_model.lower() not in str(model_path).lower():
        raise RuntimeError(
            f"{idea_id} qualified model mismatch: expected {expected_model}, runtime path is {model_path}"
        )
    (output_dir / "pre-experiment-card.json").write_text(json.dumps({**pre_experiment, "card_path": str(card_path)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pre_model = pre_model_load_audit(
        idea_id, str(governance["stage"]), frozen_config, model_path, alfworld_data, extra_pythonpath, output_dir,
        (CONFIG_DIR / "p0_runner.py", CONFIG_DIR / "p0_alfworld_adapter.py"),
    )
    if not pre_model.get("pass"):
        raise RuntimeError("P0 pre-model-load audit failed: " + ", ".join(pre_model.get("blockers") or []))
    smoke_path = data_root / "p0-runtime-smoke.json"
    readiness = runtime_preflight(model_path, data_root, Path(sys.executable), extra_pythonpath, alfworld_data, smoke_path)
    if not readiness["launch_ready"]:
        reasons = list(readiness["blockers"])
        if not readiness["smoke_rollout"]["ready"]:
            reasons.append("alfworld-smoke-rollout-required")
        raise RuntimeError("P0 launch is not ready: " + ", ".join(reasons))
    if extra_pythonpath.exists():
        site.addsitedir(str(extra_pythonpath))
        os.environ["P0_EXTRA_SITE"] = str(extra_pythonpath)
    os.environ["ALFWORLD_DATA"] = str(alfworld_data)
    run_phase = str(load_json(config_file).get("phase") or "P0")
    collector = collect_a1 if idea_id == "update-trust-region" else collect_a2
    state_path = execution_state_path(data_root, idea_id)
    state = {
        "schema_version": "1.0",
        "idea_id": idea_id,
        "run_id": output_dir.name,
        "phase": run_phase,
        "status": "running",
        "started_at": _utc_now(),
        "output_dir": str(output_dir),
        "runtime_contract_hash": readiness["runtime_contract_hash"],
        "pre_experiment_card": str(card_path),
        "frozen_config": str(frozen_config),
        "pre_experiment_gates": f"{pre_experiment['passed_gates']}/{pre_experiment['gate_count']}",
        "stage": "starting",
        "progress": {},
    }
    _write_execution_state(state_path, state)
    write_readiness(runtime_preflight(model_path, data_root, Path(sys.executable), extra_pythonpath, alfworld_data, smoke_path))
    try:
        def progress_callback(progress: dict[str, Any]) -> None:
            state["stage"] = str(progress.get("stage") or state.get("stage") or "running")
            state["progress"] = progress
            state["updated_at"] = _utc_now()
            _write_execution_state(state_path, state)

        collector_kwargs: dict[str, Any] = {"progress_callback": progress_callback}
        if idea_id == "budgeted-evolution-controller":
            collector_kwargs["data_root"] = data_root
        manifest = collector(frozen_config, alfworld_config, model_path, output_dir, **collector_kwargs)
        trace_audit = validate_raw_trace_file(output_dir / "raw-traces.jsonl")
        (output_dir / "trace-contract-audit.json").write_text(json.dumps(trace_audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        state["trace_contract_audit"] = str(output_dir / "trace-contract-audit.json")
        if not trace_audit.get("pass"):
            state.update({"failure_kind": "PROVENANCE_INCONCLUSIVE", "scientific_result_available": False, "diagnosis": "raw trace contract incomplete"})
            _write_execution_state(state_path, state)
            raise RuntimeError("raw trace contract failed; scientific registration is forbidden")
    except Exception as error:
        state.update({"status": "failed", "finished_at": _utc_now(), "error_type": type(error).__name__, "failed_stage": "collect"})
        _write_execution_state(state_path, state)
        write_readiness(runtime_preflight(model_path, data_root, Path(sys.executable), extra_pythonpath, alfworld_data, smoke_path))
        raise
    state.update({"status": "collected", "stage": "collected", "collected_at": _utc_now(), "manifest": str(output_dir / "manifest.json")})
    _write_execution_state(state_path, state)
    write_readiness(runtime_preflight(model_path, data_root, Path(sys.executable), extra_pythonpath, alfworld_data, smoke_path))
    return manifest, readiness, config_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P0 preflight, dry-run, analysis, and registry writer.")
    sub = parser.add_subparsers(dest="command", required=True)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    preflight.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    preflight.add_argument("--python", type=Path, default=Path("/data/wyt/envs/vlm_test/bin/python"))
    preflight.add_argument("--extra-pythonpath", type=Path, default=Path("/data/wyt/envs/agent_evolution_p0_site"))
    preflight.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    preflight.add_argument("--write-site", action="store_true")
    preflight.add_argument("--json", type=Path, default=READINESS_JSON)
    preflight.add_argument("--js", type=Path, default=READINESS_JS)

    dry = sub.add_parser("dry-run")
    dry.add_argument("idea_id", choices=sorted(SUPPORTED_IDEAS))
    dry.add_argument("--output-dir", type=Path)

    analyze = sub.add_parser("analyze")
    analyze.add_argument("idea_id", choices=sorted(SUPPORTED_IDEAS))
    analyze.add_argument("--input", type=Path, required=True)
    analyze.add_argument("--config", type=Path, required=True)
    analyze.add_argument("--output-dir", type=Path, required=True)
    analyze.add_argument("--cost", type=Path)
    analyze.add_argument("--manifest", type=Path)
    analyze.add_argument("--register", action="store_true")

    smoke = sub.add_parser("smoke")
    smoke.add_argument("--alfworld-config", type=Path, default=CONFIG_DIR / "p0_alfworld_config.yaml")
    smoke.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    smoke.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    smoke.add_argument("--extra-pythonpath", type=Path, default=Path("/data/wyt/envs/agent_evolution_p0_site"))
    smoke.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    smoke.add_argument("--output", type=Path)

    collect = sub.add_parser("collect")
    collect.add_argument("idea_id", choices=sorted(SUPPORTED_IDEAS))
    collect.add_argument("--config", type=Path)
    collect.add_argument("--alfworld-config", type=Path, default=CONFIG_DIR / "p0_alfworld_config.yaml")
    collect.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    collect.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    collect.add_argument("--extra-pythonpath", type=Path, default=Path("/data/wyt/envs/agent_evolution_p0_site"))
    collect.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    collect.add_argument("--output-dir", type=Path, required=True)

    execute = sub.add_parser("execute")
    execute.add_argument("idea_id", choices=sorted(SUPPORTED_IDEAS))
    execute.add_argument("--config", type=Path)
    execute.add_argument("--alfworld-config", type=Path, default=CONFIG_DIR / "p0_alfworld_config.yaml")
    execute.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    execute.add_argument("--data-root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    execute.add_argument("--extra-pythonpath", type=Path, default=Path("/data/wyt/envs/agent_evolution_p0_site"))
    execute.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    execute.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def run_real_p0_transaction(args: argparse.Namespace) -> dict[str, Any]:
    if args.config is None:
        raise RuntimeError("real P0 collect/execute requires an explicit frozen --config; implicit legacy defaults are disabled")
    requested_config = args.config
    requested_payload = load_json(requested_config)
    requested_phase = str(requested_payload.get("phase") or "P0")
    if args.command == "execute" and requested_phase != "P0":
        raise RuntimeError(
            f"{requested_phase} is screening/qualification-only and cannot register a Pilot result; "
            "use collect, then escalate to a frozen confirmatory P0 config"
        )
    manifest, readiness, experiment_config = collect_real_p0(
        args.idea_id,
        args.config,
        args.alfworld_config,
        args.model_path,
        args.data_root,
        args.extra_pythonpath,
        args.alfworld_data,
        args.output_dir,
    )
    if args.command == "collect":
        return manifest

    state_path = execution_state_path(args.data_root, args.idea_id)
    state = load_json(state_path)
    try:
        result = analyze_file(
            args.idea_id,
            args.output_dir / str(manifest["analysis_input"]),
            experiment_config,
            args.output_dir,
            args.output_dir / "cost.json",
            args.output_dir / "manifest.json",
            True,
        )
    except Exception as error:
        state.update({"status": "failed", "finished_at": _utc_now(), "error_type": type(error).__name__, "failed_stage": "analyze-register"})
        _write_execution_state(state_path, state)
        write_readiness(runtime_preflight(args.model_path, args.data_root, Path(sys.executable), args.extra_pythonpath, args.alfworld_data, args.data_root / "p0-runtime-smoke.json"))
        raise
    state.update({
        "status": "registered",
        "stage": "registered",
        "finished_at": _utc_now(),
        "result": result["result"],
        "registered_path": result.get("registered_path", ""),
    })
    _write_execution_state(state_path, state)
    from .research_system import write_research_system_state
    write_research_system_state()
    refreshed = runtime_preflight(args.model_path, args.data_root, Path(sys.executable), args.extra_pythonpath, args.alfworld_data, args.data_root / "p0-runtime-smoke.json")
    write_readiness(refreshed)
    return {"manifest": manifest, "result": result, "research_system_refreshed": True}


def run_smoke_transaction(args: argparse.Namespace) -> dict[str, Any]:
    readiness = runtime_preflight(args.model_path, args.data_root, Path(sys.executable), args.extra_pythonpath, args.alfworld_data, args.output)
    if not readiness["environment_ready"]:
        raise RuntimeError("P0 runtime is not ready for smoke: " + ", ".join(readiness["blockers"]))
    if args.extra_pythonpath.exists():
        site.addsitedir(str(args.extra_pythonpath))
        os.environ["P0_EXTRA_SITE"] = str(args.extra_pythonpath)
    os.environ["ALFWORLD_DATA"] = str(args.alfworld_data)
    row = run_lightweight_smoke(args.alfworld_config, args.model_path, "eval_out_of_distribution")
    model_probe = row.get("model_probe") or {}
    passed = bool(
        row.get("gamefile")
        and int(row.get("steps") or 0) == 1
        and not row.get("parser_invalid")
        and row.get("observation_ready")
        and model_probe.get("chat_template_ready")
        and len(model_probe.get("shards") or []) >= 1
    )
    payload = {
        "schema_version": "1.1",
        "smoke_kind": "lightweight-model-artifact-plus-env-step",
        "status": "pass" if passed else "fail",
        "model_path": str(args.model_path),
        "runtime_contract_hash": readiness["runtime_contract_hash"],
        "alfworld_data": str(args.alfworld_data),
        "gamefile": row.get("gamefile", ""),
        "steps": int(row.get("steps") or 0),
        "won": int(row.get("won") or 0),
        "parser_invalid": bool(row.get("parser_invalid")),
        "command_count": int(row.get("command_count") or 0),
        "tokenizer_class": model_probe.get("tokenizer_class", ""),
        "chat_template_ready": bool(model_probe.get("chat_template_ready")),
        "shard_probe_count": len(model_probe.get("shards") or []),
        "shard_probes": model_probe.get("shards") or [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readiness(runtime_preflight(args.model_path, args.data_root, Path(sys.executable), args.extra_pythonpath, args.alfworld_data, args.output))
    if not passed:
        raise RuntimeError("ALFWorld smoke rollout did not produce a valid non-empty episode")
    return payload


def main() -> None:
    args = parse_args()
    if args.command == "preflight":
        payload = runtime_preflight(args.model_path, args.data_root, args.python, args.extra_pythonpath, args.alfworld_data)
        if args.write_site:
            write_readiness(payload, args.json, args.js)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.command == "dry-run":
        print(json.dumps(dry_run(args.idea_id, args.output_dir), ensure_ascii=False, indent=2))
    elif args.command == "smoke":
        if args.output is None:
            args.output = args.data_root / "p0-runtime-smoke.json"
        with p0_execution_lock(args.data_root, "runtime-smoke"):
            payload = run_smoke_transaction(args)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.command in {"collect", "execute"}:
        with p0_execution_lock(args.data_root, args.idea_id):
            payload = run_real_p0_transaction(args)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(analyze_file(args.idea_id, args.input, args.config, args.output_dir, args.cost, args.manifest, args.register), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
