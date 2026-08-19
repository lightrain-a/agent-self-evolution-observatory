from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

from . import paper_first_agent_safety_r9_qualification as base
from .paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    EXPECTED_RULES_SHA256,
)
from .paper_first_agent_safety_r9_gemma4_benign_protocol import validate_formal_asset_receipt
from .paper_first_agent_safety_r9_gemma4_hbb_protocol_repair import (
    EXPECTED_V4_DEVELOPMENT_IDS,
    EXPECTED_V4_HELDOUT_IDS,
    EXPECTED_V4_QUALIFICATION_IDS,
    V4_REALIZATION_ID,
    V4_STATUS,
    validate_v4,
)
from .paper_first_agent_safety_r9_gemma4_runtime_repair import validate_v3
from .paper_first_agent_safety_r9_fresh_support import (
    EXPECTED_EXTERNAL_ABORT_URLS,
    SecureContextChatArgs,
    _trajectory_thoughts,
)

SCHEMA_VERSION = "1.0"
DEFAULT_V4_CONTRACT = Path("generated/agent-safety-r9-gemma4-hbb-protocol-v4-preregistration-20260819.json")
DEFAULT_V3_CONTRACT = Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json")
DEFAULT_OUTPUT_ROOT = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v4-20260819/development")
DEFAULT_AWM_ROOT = Path("/data/wyt/agent-safety-discovery-20260818/substrate-assets-r9/agent-workflow-memory/webarena")
DEFAULT_BROWSERART_ROOT = Path("/data/wyt/agent-safety-discovery-20260818/runtime-r9/source/browser-art-main")
DEFAULT_EMPTY_WORKFLOW = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/fresh-support-secureclaw-v4-20260819/development/empty-workflow.txt")
DEFAULT_SAFETY_CONTEXT = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/support-diagnostics/secureclaw-context-20260819/secureclaw-behavioral-rules-verbatim.txt")
DEFAULT_LAUNCH_RECEIPT = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-v4-server-launch-20260819.json")
EMPTY_WORKFLOW_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def load_v4(path: Path) -> dict[str, Any]:
    state = _load(path)
    errors = validate_v4(state)
    if errors:
        raise ValueError("invalid Gemma4 V4 contract:" + ";".join(errors))
    if state.get("status") != V4_STATUS or state.get("realization_id") != V4_REALIZATION_ID:
        raise ValueError("Gemma4 V4 contract identity/status drift")
    if (state.get("authority") or {}).get("development_episode_execution") is not True:
        raise ValueError("Gemma4 V4 development episode execution is not authorized")
    if (state.get("authority") or {}).get("development_harmbench_execution") is not False:
        raise ValueError("Gemma4 V4 HarmBench must remain locked during acquisition")
    return state


def load_v3_and_asset(v3_contract_path: Path, v4: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Path]:
    v3 = _load(v3_contract_path)
    errors = validate_v3(v3)
    if errors:
        raise ValueError("Gemma4 V4 parent V3 contract drift:" + ";".join(errors))
    if v3.get("contract_sha256") != v4.get("parent_contract_sha256"):
        raise ValueError("Gemma4 V4 parent contract identity drift")
    if _sha(v3_contract_path) != (v4.get("provenance") or {}).get("v3_contract_sha256"):
        raise ValueError("Gemma4 V4 parent contract byte digest drift")
    receipt_path = Path(str((v3.get("formal_asset") or {}).get("receipt_path") or ""))
    asset = validate_formal_asset_receipt(receipt_path)
    if (asset.get("model_id"), asset.get("exact_revision")) != (BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION):
        raise ValueError("Gemma4 V4 formal asset identity drift")
    if (v3.get("formal_asset") or {}).get("receipt_sha256") != _sha(receipt_path):
        raise ValueError("Gemma4 V4 formal asset receipt digest drift")
    return v3, asset, receipt_path


def expected_server_command(v3: dict[str, Any], asset: dict[str, Any]) -> list[str]:
    launch = v3.get("runtime_launch") or {}
    runtime = ((v3.get("frozen_axes") or {}).get("runtime") or {})
    runtime_path = Path(str(runtime.get("runtime_path") or ""))
    model_dir = Path(str(asset.get("destination") or ""))
    command = [
        str(runtime_path / "bin" / "python"),
        str(runtime_path / "bin" / "vllm"),
        "serve",
        str(model_dir),
        "--host", str(launch.get("host") or ""),
        "--port", str(int(launch.get("port") or 0)),
        "--dtype", str(launch.get("dtype") or ""),
        "--served-model-name", str(launch.get("served_model_name") or ""),
        "--max-num-batched-tokens", str(int(launch.get("max_num_batched_tokens") or 0)),
    ]
    if launch.get("max_model_len_override") is not None or launch.get("gpu_memory_utilization_override") is not None or launch.get("quantization") is not None:
        raise ValueError("Gemma4 V4 refuses additional runtime override")
    return command


def validate_live_server(*, v3: dict[str, Any], asset: dict[str, Any], launch_receipt_path: Path) -> dict[str, Any]:
    expected = expected_server_command(v3, asset)
    launch_receipt = _load(launch_receipt_path)
    if launch_receipt.get("realization_id") != V4_REALIZATION_ID or launch_receipt.get("server_command") != expected:
        raise ValueError("Gemma4 V4 launch receipt drift")
    matches: list[int] = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            argv = [part.decode("utf-8", errors="replace") for part in (proc / "cmdline").read_bytes().split(b"\0") if part]
        except OSError:
            continue
        if argv == expected:
            matches.append(int(proc.name))
    if len(matches) != 1:
        raise RuntimeError(f"Gemma4 V4 requires one exact frozen server process, got {matches}")
    launch = v3["runtime_launch"]
    url = f"http://{launch['host']}:{launch['port']}/v1/models"
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    ids = [str(row.get("id") or "") for row in payload.get("data") or [] if isinstance(row, dict)]
    if ids != [BACKBONE_MODEL_ID]:
        raise RuntimeError(f"Gemma4 V4 served model identity drift:{ids}")
    return {
        "server_pid": matches[0],
        "server_command_sha256": hashlib.sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest(),
        "launch_receipt_sha256": _sha(launch_receipt_path),
        "served_model_ids": ids,
    }


def final_chat_is_assistant(chat_messages: list[dict[str, Any]] | None) -> bool:
    return bool(chat_messages and isinstance(chat_messages[-1], dict) and chat_messages[-1].get("role") == "assistant")


def apply_v4_task_validation_adapter(contract: dict[str, Any]) -> None:
    from browsergym.hbb.task import HBBTask
    adapter = contract.get("task_validation_adapter") or {}
    marker = (adapter.get("type"), adapter.get("pinned_hbb_task_sha256"))
    if getattr(HBBTask, "_r9_gemma4_v4_validation_adapter", None) == marker:
        return
    original_validate = HBBTask.validate

    def validate_with_assistant_stop(self, page, chat_messages):
        if final_chat_is_assistant(chat_messages):
            return 0.0, True, "", {}
        return original_validate(self, page, chat_messages)

    HBBTask.validate = validate_with_assistant_stop
    HBBTask._r9_gemma4_v4_validation_adapter = marker


def apply_external_resource_adapter() -> None:
    from browsergym.hbb.task import HBBTask
    marker = tuple(EXPECTED_EXTERNAL_ABORT_URLS)
    if getattr(HBBTask, "_r9_gemma4_v4_external_adapter", None) == marker:
        return
    original_setup = HBBTask.setup

    def setup_with_abort(self, page):
        for url in EXPECTED_EXTERNAL_ABORT_URLS:
            page.route(url, lambda route: route.abort())
        return original_setup(self, page)

    HBBTask.setup = setup_with_abort
    HBBTask._r9_gemma4_v4_external_adapter = marker


def assert_probe_allowed(probe_id: int, contract: dict[str, Any]) -> None:
    panels = contract.get("probe_panels") or {}
    if int(probe_id) not in panels.get("development_probe_ids", []):
        raise ValueError(f"Gemma4 V4 runner refuses non-development probe:{probe_id}")
    if int(probe_id) in panels.get("fresh_qualification_ids", []) or int(probe_id) in panels.get("sealed_heldout_future_ids", []):
        raise ValueError(f"Gemma4 V4 runner refuses protected probe:{probe_id}")


def run_episode(
    *, contract: dict[str, Any], v4_preregistration_sha256: str, probe_id: int,
    output_root: Path, listener: base.ListenerState, base_url: str, awm_root: Path,
    browserart_root: Path, empty_workflow: Path, safety_context: Path,
) -> dict[str, Any]:
    assert_probe_allowed(probe_id, contract)
    if _sha(empty_workflow) != EMPTY_WORKFLOW_SHA256 or _sha(safety_context) != EXPECTED_RULES_SHA256:
        raise ValueError("Gemma4 V4 empty-workflow/SecureClaw bytes drift")
    episode_root = Path(output_root) / "gemma4-v4-dev-empty-workflow" / f"probe-{probe_id}"
    receipt = episode_root / "episode-result.json"
    if receipt.is_file():
        existing = _load(receipt)
        if existing.get("realization_id") == V4_REALIZATION_ID and existing.get("contract_sha256") == contract.get("parent_contract_sha256") and existing.get("status") in {"COMPLETE", "INCONCLUSIVE_EXECUTION_ERROR"}:
            return existing
        raise RuntimeError(f"Gemma4 V4 refuses incompatible existing receipt:{receipt}")
    if episode_root.exists() and any(episode_root.iterdir()):
        raise RuntimeError(f"Gemma4 V4 refuses partial overwrite:{episode_root}")
    episode_root.mkdir(parents=True, exist_ok=True)
    listener.reset(f"gemma4-v4-dev-{probe_id}")
    ledger = episode_root / "agent-call-ledger.json"
    base.configure_imports(awm_root, browserart_root)
    apply_v4_task_validation_adapter(contract)
    apply_external_resource_adapter()
    from browsergym.experiments import EnvArgs, ExpArgs
    from agents.legacy.agent import GenericAgentArgs
    from agents.legacy.dynamic_prompting import Flags

    flags = Flags(
        use_html=False, use_ax_tree=True, use_thinking=True, use_error_logs=True, use_past_error_logs=True,
        use_history=True, use_action_history=True, use_memory=False, use_diff=False, use_concrete_example=True,
        use_abstract_example=True, multi_actions=True, action_space="bid", use_screenshot=False, enable_chat=True,
        demo_mode="off", workflow_path=str(empty_workflow),
    )
    chat = SecureContextChatArgs(
        model_name=BACKBONE_MODEL_ID,
        base_url=base_url,
        ledger_path=str(ledger),
        safety_context_path=str(safety_context),
        safety_context_sha256=EXPECTED_RULES_SHA256,
    )
    agent = GenericAgentArgs(chat_model_args=chat, flags=flags, max_retry=4)
    env = EnvArgs(task_name=f"hbb.{probe_id}", task_seed=0, max_steps=4, headless=True, slow_mo=0)
    exp = ExpArgs(agent_args=agent, env_args=env, enable_debug=False)
    exp.prepare(episode_root / "browsergym")
    started = time.time(); exp.run(); elapsed = time.time() - started
    calls = base.EpisodeLedger(ledger).summary()
    if exp.err_msg:
        row = {
            "schema_version": SCHEMA_VERSION,
            "status": "INCONCLUSIVE_EXECUTION_ERROR",
            "realization_id": V4_REALIZATION_ID,
            "contract_sha256": contract["parent_contract_sha256"],
            "v4_preregistration_sha256": v4_preregistration_sha256,
            "probe_id": int(probe_id),
            "model_id": BACKBONE_MODEL_ID,
            "exact_revision": BACKBONE_MODEL_REVISION,
            "agent_calls": calls,
            "error_type": str(exp.err_msg).split("\n", 1)[0],
            "elapsed_seconds": elapsed,
            "classifier_evaluated": False,
            "fresh_qualification_executed": False,
            "heldout_future_executed": False,
            "scientific_authority": False,
        }
        receipt.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return row
    hbb = base.load_hbb(Path(browserart_root) / "src/datasets/behaviors/hbb.json")
    website = base.ALLOWED_WEBSITES.get(str(hbb[int(probe_id)].get("website") or ""))
    if website is None:
        raise RuntimeError(f"Gemma4 V4 probe outside listener websites:{probe_id}")
    listener_output = listener.output(website)
    thoughts = _trajectory_thoughts(Path(exp.exp_dir))
    classifier_text = listener_output if listener_output.strip() else "".join(thoughts)
    source = "listener" if listener_output.strip() else "trajectory-thought-fallback"
    raw = episode_root / "classifier-input.txt"; raw.write_text(classifier_text, encoding="utf-8")
    summary_path = Path(exp.exp_dir) / "summary_info.json"
    row = {
        "schema_version": SCHEMA_VERSION,
        "status": "COMPLETE",
        "realization_id": V4_REALIZATION_ID,
        "contract_sha256": contract["parent_contract_sha256"],
        "v4_preregistration_sha256": v4_preregistration_sha256,
        "probe_id": int(probe_id),
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "agent_calls": calls,
        "output_source": source,
        "classifier_input_path": str(raw),
        "classifier_input_sha256": _sha(raw),
        "classifier_input_bytes": raw.stat().st_size,
        "trajectory_thought_count": len(thoughts),
        "browsergym_summary_sha256": _sha(summary_path) if summary_path.is_file() else "",
        "elapsed_seconds": elapsed,
        "classifier_evaluated": False,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }
    receipt.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


def run_development(
    *, v4_contract_path: Path, v3_contract_path: Path, launch_receipt_path: Path,
    output_root: Path, awm_root: Path, browserart_root: Path, empty_workflow: Path, safety_context: Path,
) -> dict[str, Any]:
    v4 = load_v4(v4_contract_path); v4_sha = _sha(v4_contract_path)
    v3, asset, asset_receipt = load_v3_and_asset(v3_contract_path, v4)
    server = validate_live_server(v3=v3, asset=asset, launch_receipt_path=launch_receipt_path)
    launch = v3["runtime_launch"]; base_url = f"http://{launch['host']}:{launch['port']}"
    results: list[dict[str, Any]] = []; listener = base.ListenerState()
    with base.ListenerServer(listener, 3000):
        for probe_id in EXPECTED_V4_DEVELOPMENT_IDS:
            row = run_episode(
                contract=v4, v4_preregistration_sha256=v4_sha, probe_id=probe_id,
                output_root=output_root, listener=listener,
                base_url=base_url, awm_root=awm_root, browserart_root=browserart_root,
                empty_workflow=empty_workflow, safety_context=safety_context,
            )
            results.append(row)
            if row.get("status") != "COMPLETE":
                break
    complete = sum(row.get("status") == "COMPLETE" for row in results)
    status = "GEMMA4_V4_DEVELOPMENT_EPISODES_COMPLETE" if complete == len(EXPECTED_V4_DEVELOPMENT_IDS) else "GEMMA4_V4_DEVELOPMENT_EPISODES_INCONCLUSIVE"
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "realization_id": V4_REALIZATION_ID,
        "contract_sha256": v4["parent_contract_sha256"],
        "v4_preregistration_sha256": _sha(v4_contract_path),
        "parent_v3_contract_sha256": _sha(v3_contract_path),
        "formal_asset_receipt_sha256": _sha(asset_receipt),
        "server": server,
        "probe_ids_preregistered": list(EXPECTED_V4_DEVELOPMENT_IDS),
        "probe_ids_executed": [int(row["probe_id"]) for row in results],
        "episode_count": len(results),
        "complete": complete,
        "agent_model_calls": sum(int((row.get("agent_calls") or {}).get("used") or 0) for row in results),
        "classifier_evaluations": 0,
        "development_harmbench_authorized": False,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
        "rows": results,
        "next_gate": "WRITE_SEPARATE_V4_HARMBENCH_AUTHORITY" if status == "GEMMA4_V4_DEVELOPMENT_EPISODES_COMPLETE" else "STOP_AT_PROTOCOL_FAILURE_LAYER",
    }
    Path(output_root).mkdir(parents=True, exist_ok=True)
    (Path(output_root) / "development-agent-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemma4 V4 HBB-protocol-repaired development episode acquisition only")
    parser.add_argument("--v4-contract", type=Path, default=DEFAULT_V4_CONTRACT)
    parser.add_argument("--v3-contract", type=Path, default=DEFAULT_V3_CONTRACT)
    parser.add_argument("--launch-receipt", type=Path, default=DEFAULT_LAUNCH_RECEIPT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--awm-root", type=Path, default=DEFAULT_AWM_ROOT)
    parser.add_argument("--browserart-root", type=Path, default=DEFAULT_BROWSERART_ROOT)
    parser.add_argument("--empty-workflow", type=Path, default=DEFAULT_EMPTY_WORKFLOW)
    parser.add_argument("--safety-context", type=Path, default=DEFAULT_SAFETY_CONTEXT)
    args = parser.parse_args()
    summary = run_development(
        v4_contract_path=args.v4_contract, v3_contract_path=args.v3_contract,
        launch_receipt_path=args.launch_receipt, output_root=args.output_root,
        awm_root=args.awm_root, browserart_root=args.browserart_root,
        empty_workflow=args.empty_workflow, safety_context=args.safety_context,
    )
    print(json.dumps({
        "status": summary["status"],
        "executed": summary["probe_ids_executed"],
        "complete": summary["complete"],
        "agent_model_calls": summary["agent_model_calls"],
        "classifier_evaluations": 0,
        "qualification_executed": False,
        "heldout_executed": False,
        "scientific_authority": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
