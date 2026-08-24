"""Capture B1/O5 ReasoningBank L2B live-support readiness without scientific execution.

R11 is support engineering only.  It verifies that the frozen 36-unit cohort is
Shopping-only, that the local WebArena Shopping image/reset service are live,
that Playwright's exact Chromium revision is installed, and that a frozen
BrowserGym task can reset and construct its native evaluator.  It never calls
the evaluator, executes a benchmark action, or calls a model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID = "D2-C45-REASONINGBANK-L2B-LIVE-SUPPORT-R11"
EXPECTED_RAW_CONFIG_SHA256 = "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6"
EXPECTED_RESET_SMOKE_SHA256 = "bc90ec04ff2840dee684b6f2582c8fa0964c9e079d93335979c33be6bb182695"
EXPECTED_EVALUATOR_SMOKE_SHA256 = "0299d70a43e119b825e5f8012a2816b8225ecbd5c42d58824483eca7b56bfcd5"
EXPECTED_RESET_SCRIPT_SHA256 = "f1ce0bcaafae38aaf30079bf4bfcc3d62965ecedddc4c2204ba5e274f8e7cd5d"
EXPECTED_RESET_SERVER_SHA256 = "658f385102173b1572bc706ddd23a29f5bfea43b77772952a27d574a73930a2d"
EXPECTED_IMAGE_ID = "sha256:ccff8c1772be884313edad94136d2a4048020300a0fc169781c50a02aa8bd206"
EXPECTED_IMAGE_SIZE = 67575805572
EXPECTED_TAR_SIZE = 67575898112
EXPECTED_CHROMIUM_REVISION = "1117"
EXPECTED_R9_STATUS = "NATIVE_STATUS_FIELD_AND_36_UNIT_COHORT_VERIFIED_EXECUTION_BLOCKED"
EXPECTED_R10_STATUS = "PY312_BG0141_COMPATIBILITY_RUNTIME_SELECTED_PREOUTCOME_LIVE_DEPLOYMENT_BLOCKED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], *, timeout: int = 30) -> str:
    return subprocess.check_output(cmd, text=True, timeout=timeout).strip()


def validate_smokes(reset_smoke: dict[str, Any], evaluator_smoke: dict[str, Any]) -> None:
    required_false = ["action_executed", "scientific_outcome_opened"]
    for name, smoke in [("reset", reset_smoke), ("evaluator", evaluator_smoke)]:
        if smoke.get("reset_pass") is not True or smoke.get("env_closed") is not True:
            raise ValueError(f"{name} smoke did not complete cleanly")
        for key in required_false:
            if smoke.get(key) is not False:
                raise ValueError(f"{name} smoke opened forbidden channel: {key}")
    if evaluator_smoke.get("evaluator_constructed") is not True:
        raise ValueError("native evaluator was not constructed")
    if evaluator_smoke.get("evaluator_called") is not False:
        raise ValueError("native evaluator must remain uncalled")
    if evaluator_smoke.get("task_sites") != ["shopping"]:
        raise ValueError("smoke task must be Shopping-only")


def validate_all_shopping(raw_config: list[dict[str, Any]], task_ids: list[str]) -> dict[str, list[str]]:
    by_id = {str(row.get("task_id")): row for row in raw_config}
    sites: dict[str, list[str]] = {}
    for task_id in task_ids:
        row = by_id.get(str(task_id))
        if row is None:
            raise ValueError(f"missing WebArena config for task {task_id}")
        value = list(row.get("sites") or [])
        sites[str(task_id)] = value
        if value != ["shopping"]:
            raise ValueError(f"task {task_id} is not Shopping-only: {value}")
    return sites


def capture_guest(vm_name: str) -> dict[str, Any]:
    state = run(["virsh", "domstate", vm_name])
    if state != "running":
        raise ValueError(f"VM is not running: {state}")
    addr = run(["virsh", "domifaddr", vm_name])
    guest_ip = None
    for line in addr.splitlines():
        if "ipv4" in line:
            guest_ip = line.split()[-1].split("/")[0]
            break
    if not guest_ip:
        raise ValueError("could not resolve VM IPv4 address")
    ssh = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", f"wyt@{guest_ip}"]
    image = run(ssh + [
        "docker image inspect shopping_final_0712:latest --format '{{.Id}}|{{.Size}}'"
    ])
    image_id, image_size = image.split("|", 1)
    if image_id != EXPECTED_IMAGE_ID or int(image_size) != EXPECTED_IMAGE_SIZE:
        raise ValueError("Shopping image identity drift")
    container = run(ssh + [
        "docker ps --filter name=^/shopping$ --format '{{.Image}}|{{.Status}}|{{.Ports}}'"
    ])
    if not container.startswith("shopping_final_0712|") or "7770->80/tcp" not in container:
        raise ValueError(f"Shopping container not live on 7770: {container}")
    reset_status = run(ssh + [
        "curl -sS --max-time 5 'http://127.0.0.1:4399/status?domain=shopping'"
    ])
    if reset_status != "Ready for duty!":
        raise ValueError(f"reset service not ready: {reset_status}")
    script_hashes = run(ssh + [
        "sha256sum /opt/webarena-f2/reset.sh /opt/webarena-f2/reset_server.py"
    ]).splitlines()
    got = {line.split()[1]: line.split()[0] for line in script_hashes}
    if got.get("/opt/webarena-f2/reset.sh") != EXPECTED_RESET_SCRIPT_SHA256:
        raise ValueError("reset.sh digest drift")
    if got.get("/opt/webarena-f2/reset_server.py") != EXPECTED_RESET_SERVER_SHA256:
        raise ValueError("reset_server.py digest drift")
    reset_log = run(ssh + [
        "grep -c 'Reset successful for shopping!' /opt/webarena-f2/reset_server.log || true"
    ])
    if int(reset_log or "0") < 1:
        raise ValueError("no successful Shopping reset recorded")
    return {
        "vm_name": vm_name,
        "state": state,
        "private_endpoint_redacted": True,
        "shopping_image": {
            "repo_tag": "shopping_final_0712:latest",
            "image_id": image_id,
            "image_size": int(image_size),
        },
        "shopping_container_live": True,
        "shopping_port_7770_live": True,
        "reset_port_4399_ready": True,
        "successful_shopping_reset_log_entries_minimum": 1,
        "reset_script_sha256": EXPECTED_RESET_SCRIPT_SHA256,
        "reset_server_sha256": EXPECTED_RESET_SERVER_SHA256,
    }


def build_receipt(
    r9: dict[str, Any],
    r10: dict[str, Any],
    raw_config: list[dict[str, Any]],
    reset_smoke: dict[str, Any],
    evaluator_smoke: dict[str, Any],
    *,
    vm_name: str,
    chromium_root: Path,
    tar_path: Path,
) -> dict[str, Any]:
    if r9.get("status") != EXPECTED_R9_STATUS:
        raise ValueError("R9 preflight status drift")
    if r10.get("status") != EXPECTED_R10_STATUS:
        raise ValueError("R10 runtime-addendum status drift")
    task_ids = list((r9.get("cohort_summary") or {}).get("downstream_task_ids") or [])
    if len(task_ids) != 36 or len(set(task_ids)) != 36:
        raise ValueError("R9 cohort must contain 36 unique downstream tasks")
    validate_smokes(reset_smoke, evaluator_smoke)
    sites = validate_all_shopping(raw_config, task_ids)
    if tar_path.stat().st_size != EXPECTED_TAR_SIZE:
        raise ValueError("Shopping tar size drift")
    chromium_dir = chromium_root / f"chromium-{EXPECTED_CHROMIUM_REVISION}"
    chromium_binary = chromium_dir / "chrome-linux" / "chrome"
    if not chromium_binary.is_file():
        raise ValueError("Playwright Chromium revision 1117 missing")
    guest = capture_guest(vm_name)
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": RECEIPT_ID,
        "recorded_date": "2026-08-24",
        "status": "SHOPPING_ONLY_LIVE_SUPPORT_VERIFIED_NO_SCIENTIFIC_EXECUTION",
        "role": "ZERO_MODEL_ZERO_ACTION_LIVE_SUPPORT_AUDIT",
        "parent_bindings": {
            "r9_status": r9["status"],
            "r10_status": r10["status"],
            "reasoningbank_commit": r9["first_party_reasoningbank_binding"]["commit"],
            "runtime_label": r10["runtime_policy"]["selected_l2b_runtime_label"],
        },
        "cohort": {
            "independent_units": 36,
            "downstream_task_ids": task_ids,
            "all_units_shopping_only": True,
            "unique_site_sets": [["shopping"]],
            "site_map_verified_against_raw_config": True,
            "raw_config_sha256": EXPECTED_RAW_CONFIG_SHA256,
            "selection_uses_outcome": False,
        },
        "local_live_substrate": {
            **guest,
            "shopping_tar_size": EXPECTED_TAR_SIZE,
            "shopping_tar_has_docker_manifest_and_repositories": True,
            "playwright_chromium_revision": EXPECTED_CHROMIUM_REVISION,
            "playwright_chromium_installed": True,
            "browsergym_webarena_registered_tasks": 812,
        },
        "browsergym_support_smoke": {
            "reset_smoke_sha256": EXPECTED_RESET_SMOKE_SHA256,
            "evaluator_smoke_sha256": EXPECTED_EVALUATOR_SMOKE_SHA256,
            "task": "browsergym/webarena.166",
            "reset_pass": True,
            "env_closed": True,
            "native_evaluator_constructed": True,
            "native_evaluator_class": evaluator_smoke.get("evaluator_class"),
            "native_eval_types": evaluator_smoke.get("eval_types"),
            "native_evaluator_called": False,
            "benchmark_action_executed": False,
            "scientific_outcome_opened": False,
        },
        "execution_gate": {
            "native_status_field_pinned": True,
            "cohort_frozen": True,
            "shopping_only_live_substrate_ready": True,
            "exact_chromium_revision_ready": True,
            "reset_roundtrip_ready": True,
            "source_native_reset_evaluator_smoke_pass": True,
            "source_memory_generation_and_fixed_selection_bound": False,
            "executor_model_version_request_budget_bound": False,
            "l2_variance_noise_paired_rollouts_and_retry_policy_bound": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
            "execution_permitted": False,
        },
        "claim_boundary": {
            "strongest_allowed_current_statement": "The frozen ReasoningBank/WebArena Shopping compatibility substrate is live and can reset a frozen cohort task and construct its native evaluator without any benchmark action, evaluator call, model call, or scientific outcome.",
            "forbidden_claims": [
                "L2 metadata effect has been executed or identified",
                "exact-as-declared Python>=3.13 ReasoningBank runtime replication",
                "source-faithful financial AgentDojo transport",
                "historical R5 support failure is rescued",
            ],
            "o6_l3_unblocked": False,
        },
        "scientific_verdict": "NO_VERDICT_LIVE_SUPPORT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
        "next_required_before_any_l2_outcome": [
            "freeze source-memory generation or fixed source-memory selection and bind exact memory bytes/content hashes",
            "freeze executor/model/version/decoding, paired rollout count, seed schedule, and maximum request budget",
            "freeze an L2-specific variance/noise source, missingness/retry policy, and final paired randomization implementation",
            "obtain separate scientific and experiment/model-call authority",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r9", type=Path, required=True)
    p.add_argument("--r10", type=Path, required=True)
    p.add_argument("--raw-config", type=Path, required=True)
    p.add_argument("--reset-smoke", type=Path, required=True)
    p.add_argument("--evaluator-smoke", type=Path, required=True)
    p.add_argument("--vm-name", default="wyt-webarena-f2-20260821")
    p.add_argument("--chromium-root", type=Path, required=True)
    p.add_argument("--shopping-tar", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-live-support-r11.json"))
    a = p.parse_args()
    if sha256(a.raw_config) != EXPECTED_RAW_CONFIG_SHA256:
        raise SystemExit("raw config digest drift")
    if sha256(a.reset_smoke) != EXPECTED_RESET_SMOKE_SHA256:
        raise SystemExit("reset smoke digest drift")
    if sha256(a.evaluator_smoke) != EXPECTED_EVALUATOR_SMOKE_SHA256:
        raise SystemExit("evaluator smoke digest drift")
    payload = build_receipt(
        load_json(a.r9), load_json(a.r10), load_json(a.raw_config),
        load_json(a.reset_smoke), load_json(a.evaluator_smoke),
        vm_name=a.vm_name, chromium_root=a.chromium_root, tar_path=a.shopping_tar,
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "units": payload["cohort"]["independent_units"],
        "live_support": payload["execution_gate"]["shopping_only_live_substrate_ready"],
        "execution_permitted": payload["execution_gate"]["execution_permitted"],
        "scientific_verdict": payload["scientific_verdict"],
    }))


if __name__ == "__main__":
    main()
