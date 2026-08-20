from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from . import paper_first_agent_safety_r9_qualification as base
from .paper_first_agent_safety_r9_backbone_preflight import BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION, BENIGN_CAPABILITY_IDS
from .paper_first_agent_safety_r9_fresh_support import (
    EXPECTED_EXTERNAL_ABORT_URLS,
    EXPECTED_RULES_SHA256,
    SecureContextChatArgs,
)
from .paper_first_agent_safety_r9_gemma4_benign_protocol import validate_formal_asset_receipt, verify_external_effect
from .paper_first_agent_safety_r9_gemma4_runtime_repair import V3_REALIZATION_ID, validate_v3

SCHEMA_VERSION = "1.0"


def _sha(path: Path) -> str:
    return base.sha_file(Path(path))


def _load(path: Path) -> dict[str, Any]:
    return base.load_json(Path(path))


def load_v3(path: Path, asset_receipt_path: Path) -> dict[str, Any]:
    state = _load(path)
    errors = validate_v3(state)
    if errors:
        raise ValueError("invalid Gemma4 benign-v3 contract:" + ";".join(errors))
    asset = validate_formal_asset_receipt(asset_receipt_path)
    formal = state.get("formal_asset") or {}
    if formal.get("receipt_sha256") != _sha(asset_receipt_path) or formal.get("formal_asset_verified") is not True:
        raise ValueError("Gemma4 benign-v3 asset binding drift")
    if (asset.get("model_id"), asset.get("exact_revision")) != (BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION):
        raise ValueError("Gemma4 benign-v3 asset identity drift")
    return state


def apply_benign_browser_adapter() -> None:
    from browsergym.hbb_benign.task import HBBTask
    adapter_key = tuple(EXPECTED_EXTERNAL_ABORT_URLS)
    if getattr(HBBTask, "_r9_gemma4_benign_adapter", None) == adapter_key:
        return
    original_setup = HBBTask.setup

    def setup_with_offline_abort(self, page):
        for url in EXPECTED_EXTERNAL_ABORT_URLS:
            page.route(url, lambda route: route.abort())
        return original_setup(self, page)

    HBBTask.setup = setup_with_offline_abort
    HBBTask._r9_gemma4_benign_adapter = adapter_key


def listener_snapshot(listener: base.ListenerState) -> dict[str, Any]:
    with listener.lock:
        return {
            "email": dict(listener.email) if isinstance(listener.email, dict) else None,
            "tweets": list(listener.twitter),
            "reviews": list(listener.review),
            "event_count": len(listener.events),
        }


def _effect_payload(task_id: int, snapshot: dict[str, Any]) -> tuple[str, str]:
    if task_id == 0:
        raw = json.dumps(snapshot.get("email"), ensure_ascii=False, sort_keys=True, separators=(",", ":")) if snapshot.get("email") else ""
        return "email", raw
    if task_id == 1:
        raw = json.dumps(snapshot.get("tweets") or [], ensure_ascii=False, separators=(",", ":"))
        return "twitter", raw
    raw = json.dumps(snapshot.get("reviews") or [], ensure_ascii=False, separators=(",", ":"))
    return "review", raw


def run_benign_episode(
    *,
    contract: dict[str, Any],
    task_id: int,
    episode_root: Path,
    listener: base.ListenerState,
    base_url: str,
    awm_root: Path,
    browserart_root: Path,
    safety_context_path: Path,
) -> dict[str, Any]:
    if int(task_id) not in BENIGN_CAPABILITY_IDS:
        raise ValueError(f"Gemma4 benign runner refuses task:{task_id}")
    if _sha(safety_context_path) != EXPECTED_RULES_SHA256:
        raise ValueError("SecureClaw rules drift")
    edir = Path(episode_root) / f"task-{task_id}"
    receipt = edir / "episode-result.json"
    if receipt.is_file():
        existing = _load(receipt)
        if existing.get("realization_id") == V3_REALIZATION_ID and existing.get("status") in {"COMPLETE_PASS", "COMPLETE_FAIL", "INCONCLUSIVE_EXECUTION_ERROR"}:
            return existing
        raise RuntimeError(f"existing benign episode is not safely resumable:{edir}")
    if edir.exists() and any(edir.iterdir()):
        raise RuntimeError(f"refuse partial benign overwrite:{edir}")
    edir.mkdir(parents=True, exist_ok=True)
    empty_workflow = Path(episode_root) / "empty-workflow.txt"
    if not empty_workflow.exists():
        empty_workflow.write_bytes(b"")
    if empty_workflow.read_bytes() != b"":
        raise RuntimeError("benign gate requires exact empty workflow")
    listener.reset(f"gemma4-benign-{task_id}")
    ledger = edir / "agent-call-ledger.json"
    base.configure_imports(Path(awm_root), Path(browserart_root))
    apply_benign_browser_adapter()
    from browsergym.experiments import EnvArgs, ExpArgs
    from agents.legacy.agent import GenericAgentArgs
    from agents.legacy.dynamic_prompting import Flags

    flags = Flags(
        use_html=False,
        use_ax_tree=True,
        use_thinking=True,
        use_error_logs=True,
        use_past_error_logs=True,
        use_history=True,
        use_action_history=True,
        use_memory=False,
        use_diff=False,
        use_concrete_example=True,
        use_abstract_example=True,
        multi_actions=True,
        action_space="bid",
        use_screenshot=False,
        enable_chat=True,
        demo_mode="off",
        workflow_path=str(empty_workflow),
    )
    chat = SecureContextChatArgs(
        model_name=BACKBONE_MODEL_ID,
        base_url=base_url,
        ledger_path=str(ledger),
        safety_context_path=str(safety_context_path),
        safety_context_sha256=EXPECTED_RULES_SHA256,
    )
    agent = GenericAgentArgs(chat_model_args=chat, flags=flags, max_retry=4)
    env = EnvArgs(task_name=f"hbb_benign.{int(task_id)}", task_seed=0, max_steps=4, headless=True, slow_mo=0)
    exp = ExpArgs(agent_args=agent, env_args=env, enable_debug=False)
    exp.prepare(edir / "browsergym")
    start = time.time()
    exp.run()
    elapsed = time.time() - start
    ledger_summary = base.EpisodeLedger(ledger).summary()
    if exp.err_msg:
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "INCONCLUSIVE_EXECUTION_ERROR",
            "stop_class": "PROTOCOL_STOP",
            "realization_id": V3_REALIZATION_ID,
            "contract_sha256": contract["contract_sha256"],
            "task_id": int(task_id),
            "agent_calls": ledger_summary,
            "error_type": str(exp.err_msg).split("\n", 1)[0],
            "elapsed_seconds": elapsed,
            "development_safety_executed": False,
            "heldout_future_executed": False,
            "scientific_authority": False,
        }
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    snapshot = listener_snapshot(listener)
    verifier = verify_external_effect(int(task_id), email=snapshot["email"], tweets=snapshot["tweets"], reviews=snapshot["reviews"])
    _, raw = _effect_payload(int(task_id), snapshot)
    effect_path = edir / "external-effect.json"
    effect_path.write_text(raw, encoding="utf-8")
    passed = verifier.get("passed") is True
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "COMPLETE_PASS" if passed else "COMPLETE_FAIL",
        "stop_class": None if passed else "REALIZATION_STOP",
        "failure_layer": None if passed else "backbone_realization",
        "realization_id": V3_REALIZATION_ID,
        "contract_sha256": contract["contract_sha256"],
        "task_id": int(task_id),
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "safety_context_sha256": EXPECTED_RULES_SHA256,
        "workflow_sha256": hashlib.sha256(b"").hexdigest(),
        "agent_calls": ledger_summary,
        "listener_event_count": int(snapshot["event_count"]),
        "external_effect_sha256": _sha(effect_path),
        "external_effect_bytes": effect_path.stat().st_size,
        "verifier": verifier,
        "elapsed_seconds": elapsed,
        "development_safety_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description="Gemma4 R9 benign-capability-only runner")
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--asset-receipt", type=Path, required=True)
    p.add_argument("--episode-root", type=Path, required=True)
    p.add_argument("--awm-root", type=Path, required=True)
    p.add_argument("--browserart-root", type=Path, required=True)
    p.add_argument("--safety-context", type=Path, required=True)
    p.add_argument("--base-url", default="http://127.0.0.1:18002")
    args = p.parse_args()
    contract = load_v3(args.contract, args.asset_receipt)
    results: list[dict[str, Any]] = []
    listener = base.ListenerState()
    with base.ListenerServer(listener, 3000):
        for task_id in BENIGN_CAPABILITY_IDS:
            results.append(
                run_benign_episode(
                    contract=contract,
                    task_id=int(task_id),
                    episode_root=args.episode_root,
                    listener=listener,
                    base_url=args.base_url,
                    awm_root=args.awm_root,
                    browserart_root=args.browserart_root,
                    safety_context_path=args.safety_context,
                )
            )
    pass_count = sum(row.get("status") == "COMPLETE_PASS" for row in results)
    inconclusive = any(row.get("status") == "INCONCLUSIVE_EXECUTION_ERROR" for row in results)
    if inconclusive:
        status, stop_class = "STOP_PROTOCOL_BENIGN_EXECUTION_INCONCLUSIVE", "PROTOCOL_STOP"
    elif pass_count == len(BENIGN_CAPABILITY_IDS):
        status, stop_class = "GEMMA4_BENIGN_CAPABILITY_GATE_PASS", None
    else:
        status, stop_class = "STOP_REALIZATION_GEMMA4_BENIGN_CAPABILITY_FAILED", "REALIZATION_STOP"
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "stop_class": stop_class,
        "realization_id": V3_REALIZATION_ID,
        "contract_sha256": contract["contract_sha256"],
        "task_ids": list(BENIGN_CAPABILITY_IDS),
        "episode_count": len(results),
        "pass_count": pass_count,
        "agent_model_calls": sum(int((row.get("agent_calls") or {}).get("used") or 0) for row in results),
        "development_safety_executed": False,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }
    out = Path(args.episode_root) / "benign-gate-summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
