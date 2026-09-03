#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file, sha256_text
from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh4_controlled_source_runtime as controlled

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-pool-20260903.json"
POOL_SHA = "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"
RUNTIME = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-runtime-20260903-v1/normalization-qualification.json")
Q02_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q02-source-budget-closure-20260902.json"
Q02_CLOSURE_SHA = "c41ebc9df5a28b1e6f2643195be2cdfd170318de5577ef2aff3b1891819959b6"
Q02_RESULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q02-budget-20260902-v1/q02-result.json")
Q02_RESULT_SHA = "c4c7c05f4e14d82fa8ef7d0d0ea2c31a8888295f96eb810b649150da1577b7ce"
Q03_CLOSURE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-output-mcp-closure-20260903.json"
Q03_CLOSURE_SHA = "af311a6a2785bff2d06cc12febf5288de5f4759a156d3ca4ac0407cd550837ea"
FROZEN_SCHEDULE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-source-schedule-20260903.json"
FROZEN_SCHEDULE_SHA = "43f0fcc39d773edee0ea1cfaeb25055374437839bc1037b28349849f39f87a9f"
PROBE_SPECS = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-probe-specs-20260903.json"
PROBE_SPECS_SHA = "fa94289f89f7cda882cfc4f00ae967fb377001dd370e6b7f9c7a9db66886dc17"
TRANSPORT_AMENDMENT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-source-transport-amendment-20260903.json"
TRANSPORT_AMENDMENT_SHA = "c1229439b0b0aa3e80e7c6e2747d49b5378263d93f5af192597735a5bcaa42da"
EXECUTION_CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-source-execution-contract-20260903.json"
EXECUTION_CONTRACT_SHA = "8b0396213645a04ccdc236702e8d0529f7583b62b5a91d633b43741c9dc95c50"
OFFICIAL = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
CONFIG = OFFICIAL / "third_party/src/minisweagent/config/extra/swebench.yaml"
CONFIG_SHA = "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41"
DEFAULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-source-20260903-v1")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SMOKE_TASK = (
    "Non-scientific runtime qualification only. Create /testbed/runtime_smoke_marker.py containing exactly "
    "print('ATOMGIT_MSR_SMOKE_OK'), run it and observe ATOMGIT_MSR_SMOKE_OK, then submit completion using the "
    "normal MiniSWEAgent completion command. Do not modify any other file."
)
SMOKE_MARKER = "ATOMGIT_MSR_SMOKE_OK"
SMOKE_STEP_LIMIT = 16
SOURCE_INPUT_TOKEN_HARD_CAP = 30_000_000
SOURCE_OUTPUT_TOKEN_HARD_CAP = 1_000_000


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush(); os.fsync(handle.fileno())


def provider_config_text() -> str:
    return controlled.q03.atomcode_config()


def provider_config_sha() -> str:
    return sha256_text(provider_config_text())


def verify(runtime_qualification_sha: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not SHA_RE.fullmatch(runtime_qualification_sha):
        raise RuntimeError("STOP_FRESH4_SOURCE_RUNTIME_SHA_FORMAT")
    fixed = (
        (POOL, POOL_SHA, "fresh4 pool"),
        (Q02_CLOSURE, Q02_CLOSURE_SHA, "Q0.2 closure"),
        (Q02_RESULT, Q02_RESULT_SHA, "Q0.2 result"),
        (Q03_CLOSURE, Q03_CLOSURE_SHA, "Q0.3 controlled output closure"),
        (FROZEN_SCHEDULE, FROZEN_SCHEDULE_SHA, "fresh4 source schedule"),
        (PROBE_SPECS, PROBE_SPECS_SHA, "fresh4 probe specs"),
        (TRANSPORT_AMENDMENT, TRANSPORT_AMENDMENT_SHA, "fresh4 transport amendment"),
        (EXECUTION_CONTRACT, EXECUTION_CONTRACT_SHA, "fresh4 execution contract"),
        (CONFIG, CONFIG_SHA, "official MiniSWEAgent config"),
    )
    for path, expected, label in fixed:
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"STOP_FRESH4_SOURCE_INPUT_HASH_DRIFT:{label}")
    if not RUNTIME.is_file() or sha256_file(RUNTIME) != runtime_qualification_sha:
        raise RuntimeError("STOP_FRESH4_SOURCE_RUNTIME_HASH_DRIFT")
    head = subprocess.run(["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise RuntimeError("STOP_FRESH4_SOURCE_CARRIER_COMMIT_DRIFT")

    q02 = load(Q02_CLOSURE); q02_result = load(Q02_RESULT); q03 = load(Q03_CLOSURE)
    if (
        q02.get("status") != "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS"
        or q02.get("resolved_model") != controlled.q03.MODEL_ID
        or q02.get("selected_source_budget") != controlled.SOURCE_MAX_COMPLETION_TOKENS
        or q02.get("first_decision_budget") != controlled.PACTA_FIRST_DECISION_BUDGET
        or q02.get("invocation_timeout_seconds") != controlled.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS
    ):
        raise RuntimeError("STOP_FRESH4_SOURCE_Q02_NOT_QUALIFIED")
    if q02_result.get("status") != "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS" or q02_result.get("pass") is not True:
        raise RuntimeError("STOP_FRESH4_SOURCE_Q02_RESULT_INVALID")
    if q03.get("status") != "ATOMGIT_QWEN38_Q03_CONTROLLED_OUTPUT_MCP_PASS":
        raise RuntimeError("STOP_FRESH4_SOURCE_Q03_NOT_QUALIFIED")

    pool = load(POOL); runtime = load(RUNTIME); frozen = load(FROZEN_SCHEDULE); probes = load(PROBE_SPECS); amendment = load(TRANSPORT_AMENDMENT)
    if pool.get("candidate_count") != 10 or pool.get("repository_count") != 9 or pool.get("prior_exclusion_count") != 89:
        raise RuntimeError("STOP_FRESH4_SOURCE_POOL_GEOMETRY")
    all_ids = [x for unit in pool["units"] for x in (unit["source_task_id"], unit["future_task_id"])]
    if len(all_ids) != 20 or len(set(all_ids)) != 20:
        raise RuntimeError("STOP_FRESH4_SOURCE_TASK_ID_GEOMETRY")
    if (
        runtime.get("status") != "FRESH4_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN"
        or runtime.get("qualified") != 20
        or runtime.get("source_qualified") != 10
        or runtime.get("future_qualified") != 10
    ):
        raise RuntimeError("STOP_FRESH4_SOURCE_RUNTIME_SUPPORT")
    if frozen.get("status") != "FRESH4_SOURCE_SCHEDULE_FROZEN_PRE_SOURCE_OUTCOME" or len(frozen.get("rows") or []) != 10:
        raise RuntimeError("STOP_FRESH4_SOURCE_SCHEDULE_INVALID")
    if frozen.get("allowed_tool") != controlled.ALLOWED_TOOL or frozen.get("host_tools_allowed") is not False:
        raise RuntimeError("STOP_FRESH4_SOURCE_SCHEDULE_TOOL_POLICY_DRIFT")
    if probes.get("status") != "FRESH4_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME" or len(probes.get("rows") or []) != 10:
        raise RuntimeError("STOP_FRESH4_SOURCE_PROBE_SPECS_INVALID")
    channel = amendment.get("source_output_channel") or {}
    if (
        amendment.get("status") != "FROZEN_PRE_SOURCE_OUTCOME"
        or channel.get("allowed_tool") != controlled.ALLOWED_TOOL
        or channel.get("kind") != "text"
        or channel.get("command_execution_by_bridge") is not False
        or channel.get("command_execution_by_frozen_docker_loop") is not True
        or channel.get("host_native_tools_allowed") is not False
        or channel.get("model_rounds_per_logical_output") != 1
    ):
        raise RuntimeError("STOP_FRESH4_SOURCE_TRANSPORT_AMENDMENT_DRIFT")

    by_runtime = {row["instance_id"]: row for row in runtime["rows"]}
    rows: list[dict[str, Any]] = []
    for unit in pool["units"]:
        rr = by_runtime.get(unit["source_task_id"])
        if not rr or rr.get("role") != "source" or not rr.get("exact_base_normalization_pass") or not rr.get("digest_ref"):
            raise RuntimeError("STOP_FRESH4_SOURCE_RUNTIME_MISSING:" + unit["source_task_id"])
        rows.append({**unit, "digest_ref": rr["digest_ref"]})
    return rows, q02


def schedule(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source = {row["source_task_id"]: row for row in rows}
    out: list[dict[str, Any]] = []
    for item in load(FROZEN_SCHEDULE)["rows"]:
        unit = by_source.get(item["source_task_id"])
        if unit is None:
            raise RuntimeError("STOP_FRESH4_SOURCE_SCHEDULE_POOL_MISMATCH:" + item["source_task_id"])
        if (
            item.get("unit_id") != unit["unit_id"]
            or item.get("source_task_sha256") != unit["source_task_sha256"]
            or item.get("source_base_commit") != unit["source_base_commit"]
            or item.get("logical_attempts") != 1
            or item.get("replacement") is not False
            or item.get("future_task_executed") is not False
        ):
            raise RuntimeError("STOP_FRESH4_SOURCE_SCHEDULE_ROW_DRIFT:" + item["source_task_id"])
        out.append({
            "sequence": item["sequence"], "unit_id": unit["unit_id"],
            "source_task_id": unit["source_task_id"], "future_task_id": unit["future_task_id"],
            "repository": unit["task_family"], "sampling_stratum": item.get("sampling_stratum"),
            "task_sha256": unit["source_task_sha256"], "base_commit": unit["source_base_commit"],
            "digest_ref": unit["digest_ref"], "order_key": item["order_key"],
            "logical_attempts": 1, "selected_memory": "", "future_task_executed": False,
            "replacement": False,
        })
    if [row["sequence"] for row in out] != list(range(1, 11)):
        raise RuntimeError("STOP_FRESH4_SOURCE_SEQUENCE_DRIFT")
    return out


def _assert_root_binding(root: Path, runtime_sha: str) -> None:
    contract = load(root / "contract.json")
    if contract.get("runtime_qualification_sha256") != runtime_sha:
        raise RuntimeError("STOP_FRESH4_SOURCE_ROOT_RUNTIME_BINDING_DRIFT")
    if contract.get("provider_id") != controlled.PROVIDER_ID or contract.get("bridge_schema") != controlled.BRIDGE_SCHEMA:
        raise RuntimeError("STOP_FRESH4_SOURCE_ROOT_PROVIDER_BINDING_DRIFT")
    if sha256_file(root / "provider-config.toml") != provider_config_sha():
        raise RuntimeError("STOP_FRESH4_SOURCE_PROVIDER_CONFIG_DRIFT")


def prepare(root: Path, runtime_sha: str) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("fresh4 source root exists; no overwrite")
    rows, _ = verify(runtime_sha); sched = schedule(rows); root.mkdir(parents=True)
    provider_config = root / "provider-config.toml"
    provider_config.write_text(provider_config_text(), encoding="utf-8"); os.chmod(provider_config, 0o600)
    (root / "empty-provider-workdir").mkdir()
    contract = {
        "schema_version": 1, "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-SOURCE-T0-20260903",
        "status": "FROZEN_BEFORE_SOURCE_POLICY",
        "provider_id": controlled.PROVIDER_ID, "bridge_schema": controlled.BRIDGE_SCHEMA,
        "profile": controlled.q03.MODEL_PROFILE, "resolved_model": controlled.q03.MODEL_ID,
        "sampling_control": controlled.SAMPLING_CONTROL,
        "source_max_completion_tokens": controlled.SOURCE_MAX_COMPLETION_TOKENS,
        "pacta_first_decision_budget": controlled.PACTA_FIRST_DECISION_BUDGET,
        "atomcode_subprocess_timeout_seconds": controlled.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
        "allowed_tool": controlled.ALLOWED_TOOL, "output_kind": controlled.SOURCE_OUTPUT_KIND,
        "provider_config_sha256": provider_config_sha(),
        "fresh_pool_sha256": POOL_SHA, "runtime_qualification_sha256": runtime_sha,
        "q02_closure_sha256": Q02_CLOSURE_SHA, "q02_result_sha256": Q02_RESULT_SHA,
        "q03_closure_sha256": Q03_CLOSURE_SHA, "frozen_source_schedule_sha256": FROZEN_SCHEDULE_SHA,
        "frozen_probe_specs_sha256": PROBE_SPECS_SHA, "transport_amendment_sha256": TRANSPORT_AMENDMENT_SHA,
        "execution_contract_sha256": EXECUTION_CONTRACT_SHA,
        "scheduled_source_units": 10, "repository_count": 9, "logical_attempts_per_source": 1,
        "provider_wrapper_retries": 0, "replacement": False, "top_up": False,
        "environment_command_timeout_seconds": 60, "step_limit": 250,
        "smoke": {"non_scientific": True, "step_limit": SMOKE_STEP_LIMIT, "marker": SMOKE_MARKER, "must_pass_before_source": True},
        "source_input_token_hard_cap": SOURCE_INPUT_TOKEN_HARD_CAP, "source_output_token_hard_cap": SOURCE_OUTPUT_TOKEN_HARD_CAP,
        "future_task_executions": 0, "writer_calls": 0, "binder_calls": 0, "probe_calls": 0, "shadow_calls": 0, "final_calls": 0,
    }
    atomic_json(root / "contract.json", contract)
    atomic_json(root / "acquisition-schedule.json", {
        "schema_version": 1, "created_at_utc": now(), "status": "FROZEN",
        "frozen_schedule_sha256": FROZEN_SCHEDULE_SHA, "schedule": sched, "scheduled_count": 10,
        "repository_count": 9, "replacement": False, "top_up": False, "future_task_executions": 0,
    })
    return {"status": "FRESH4_ATOMGIT_MSR_SOURCE_EXECUTION_PREPARED", "scheduled": 10,
            "contract_sha256": sha256_file(root / "contract.json"), "schedule_sha256": sha256_file(root / "acquisition-schedule.json"),
            "provider_config_sha256": provider_config_sha()}


def prelaunch(root: Path, runtime_sha: str) -> dict[str, Any]:
    verify(runtime_sha); _assert_root_binding(root, runtime_sha)
    if (root / "prelaunch-qualification.json").exists(): raise RuntimeError("prelaunch exists; no overwrite")
    rows = []
    for item in load(root / "acquisition-schedule.json")["schedule"]:
        qroot = root / "prelaunch" / item["source_task_id"]; container = None; passed = False; error = None
        try:
            container = controlled.base.Fresh3Container(item["digest_ref"], item["base_commit"], qroot); passed = True
        except Exception as exc: error = f"{type(exc).__name__}: {exc}"
        finally:
            if container is not None: container.cleanup()
        rows.append({"source_task_id": item["source_task_id"], "pass": passed, "error": error,
                     "normalization_path": str(qroot / "exact-base-normalization.json") if passed else None,
                     "normalization_sha256": sha256_file(qroot / "exact-base-normalization.json") if passed else None})
    result = {"schema_version": 1, "created_at_utc": now(),
              "status": "FRESH4_ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS" if all(x["pass"] for x in rows) else "HOLD_FRESH4_ATOMGIT_MSR_SOURCE_PRELAUNCH",
              "qualified": sum(x["pass"] for x in rows), "total": 10, "rows": rows, "provider_calls": 0, "future_task_executions": 0}
    atomic_json(root / "prelaunch-qualification.json", result); return result


def smoke(root: Path, runtime_sha: str) -> dict[str, Any]:
    verify(runtime_sha); _assert_root_binding(root, runtime_sha)
    if load(root / "prelaunch-qualification.json").get("status") != "FRESH4_ATOMGIT_MSR_SOURCE_PRELAUNCH_PASS": raise RuntimeError("prelaunch not passed")
    if (root / "smoke-result.json").exists() or (root / "smoke").exists(): raise RuntimeError("smoke exists; no retry/overwrite")
    first = load(root / "acquisition-schedule.json")["schedule"][0]
    config = yaml.safe_load(CONFIG.read_text()); smoke_config = copy.deepcopy(config); smoke_config["agent"]["step_limit"] = SMOKE_STEP_LIMIT
    run = controlled.execute_trajectory(instance="FRESH4_ATOMGIT_MSR_NONSCIENTIFIC_SMOKE", task=SMOKE_TASK,
        digest_ref=first["digest_ref"], unit_root=root / "smoke", config=smoke_config,
        provider_config_path=root / "provider-config.toml", provider_workdir=root / "empty-provider-workdir", base_commit=first["base_commit"])
    jrows = [json.loads(line) for line in (root / "smoke" / "step-journal.jsonl").read_text().splitlines() if line.strip()]
    actions = [str(x.get("parsed_action") or "") for x in jrows if x.get("parsed_action")]
    marker_seen = False
    for path in (root / "smoke" / "raw").glob("observation-*.json"):
        try: observation = json.loads(path.read_text())
        except Exception: continue
        if SMOKE_MARKER in str(observation.get("output") or ""): marker_seen = True; break
    passed = (run.get("failure_layer") is None and run.get("terminal_status") == "Submitted"
              and 2 <= int(run.get("provider_logical_calls") or 0) <= SMOKE_STEP_LIMIT
              and any("runtime_smoke_marker.py" in a for a in actions) and marker_seen)
    result = {"schema_version": 1, "created_at_utc": now(),
              "status": "FRESH4_ATOMGIT_MSR_MULTISTEP_SMOKE_PASS" if passed else "STOP_FRESH4_ATOMGIT_MSR_MULTISTEP_SMOKE",
              "pass": passed, "terminal_status": run.get("terminal_status"), "provider_calls": run.get("provider_logical_calls"),
              "marker_file_action": any("runtime_smoke_marker.py" in a for a in actions), "marker_observation_seen": marker_seen,
              "run_sha256": sha256_file(root / "smoke" / "run.json"), "scientific_source_tasks_used": 0, "future_task_executions": 0}
    atomic_json(root / "smoke-result.json", result); return result


def acquire(root: Path, runtime_sha: str) -> dict[str, Any]:
    verify(runtime_sha); _assert_root_binding(root, runtime_sha)
    if load(root / "smoke-result.json").get("status") != "FRESH4_ATOMGIT_MSR_MULTISTEP_SMOKE_PASS": raise RuntimeError("smoke not passed")
    rows, _ = verify(runtime_sha); by_source = {x["source_task_id"]: x for x in rows}; config = yaml.safe_load(CONFIG.read_text())
    results: list[dict[str, Any]] = []; stop_reason = None
    for item in load(root / "acquisition-schedule.json")["schedule"]:
        unit = by_source[item["source_task_id"]]
        run = controlled.execute_trajectory(instance=unit["source_task_id"], task=unit["source_task"], digest_ref=item["digest_ref"],
            unit_root=root / f"source-{unit['source_task_id']}", config=config,
            provider_config_path=root / "provider-config.toml", provider_workdir=root / "empty-provider-workdir", base_commit=item["base_commit"])
        results.append(run); append(root / "acquisition-journal.jsonl", run)
        print(json.dumps({"source": unit["source_task_id"], "validity": run["validity_status"], "terminal": run["terminal_status"],
                          "logical_calls": run["provider_logical_calls"], "codingplan_requests": run["codingplan_requests"]}), flush=True)
        if run.get("failure_layer") is not None: stop_reason = f"{unit['source_task_id']}:{run['failure_layer']}"; break
        if sum(int(x.get("input_tokens") or 0) for x in results) > SOURCE_INPUT_TOKEN_HARD_CAP: stop_reason = "SOURCE_INPUT_TOKEN_HARD_CAP"; break
        if sum(int(x.get("output_tokens") or 0) for x in results) > SOURCE_OUTPUT_TOKEN_HARD_CAP: stop_reason = "SOURCE_OUTPUT_TOKEN_HARD_CAP"; break
    valid = [x for x in results if x["validity_status"] == "TRAJECTORY_BACKED_VALID"]
    complete = len(results) == 10 and len(valid) == 10
    audit = {"schema_version": 1, "created_at_utc": now(),
             "decision": "FRESH4_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED" if complete else "HOLD_FRESH4_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE",
             "rows": results, "attempted": len(results), "valid": len(valid),
             "valid_repositories": len({by_source[x["source_task_id"]]["task_family"] for x in valid}),
             "stop_reason": stop_reason, "codingplan_requests": sum(int(x.get("codingplan_requests") or 0) for x in results),
             "input_tokens": sum(int(x.get("input_tokens") or 0) for x in results), "output_tokens": sum(int(x.get("output_tokens") or 0) for x in results),
             "future_task_executions": 0, "writer_calls": 0, "binder_calls": 0, "probe_calls": 0, "shadow_calls": 0, "final_calls": 0,
             "pool_retired": not complete and len(results) > 0, "replacement": False, "top_up": False,
             "source_gate": "all 10 provenance-valid via Q0.3 controlled-output MCP; any consumed-invalid source retires the entire fresh4 pool; no replacement or top-up",
             "claim_authority": "NO_MSR_METHOD_EFFECT_EVIDENCE"}
    atomic_json(root / "support-audit.json", audit); return audit


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--phase", choices=("prepare", "prelaunch", "smoke", "acquire"), required=True)
    parser.add_argument("--runtime-qualification-sha", required=True); args = parser.parse_args()
    fn = {"prepare": prepare, "prelaunch": prelaunch, "smoke": smoke, "acquire": acquire}[args.phase]
    result = fn(args.root, args.runtime_qualification_sha)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__": main()
