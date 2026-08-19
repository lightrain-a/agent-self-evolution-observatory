from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from . import paper_first_agent_safety_r9_qualification as base
from .paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    EXPECTED_DEVELOPMENT_IDS,
    EXPECTED_QUALIFICATION_IDS,
)
from .paper_first_agent_safety_r9_fresh_support import EXPECTED_EXTERNAL_ABORT_URLS, EXPECTED_RULES_SHA256, compose_system_context
from .paper_first_agent_safety_r9_gemma4_gate0_adjudication import STATUS as GATE0_STATUS, validate_gate0_pass
from .paper_first_agent_safety_r9_gemma4_runtime_repair import V3_REALIZATION_ID, validate_v3
from .paper_first_agent_safety_r9_harness import R9_HELDOUT_BEHAVIOR_IDS

SCHEMA_VERSION = "1.0"
SUMMARY_STATUS = "GEMMA4_DEVELOPMENT_SAFETY_EPISODES_COMPLETE"
STATE_ID = "gemma4-dev-empty-workflow"


def _load(path: Path) -> dict[str, Any]:
    return base.load_json(Path(path))


def _sha(path: Path) -> str:
    return base.sha_file(Path(path))


def load_authorized_contract(contract_path: Path, gate0_path: Path) -> dict[str, Any]:
    contract = _load(contract_path)
    errors = validate_v3(contract)
    if errors:
        raise ValueError("Gemma4 development v3 contract drift:" + ";".join(errors))
    gate0 = _load(gate0_path)
    gate_errors = validate_gate0_pass(gate0)
    if gate_errors:
        raise ValueError("Gemma4 development Gate0 authority drift:" + ";".join(gate_errors))
    if gate0.get("status") != GATE0_STATUS or gate0.get("contract_sha256") != contract.get("contract_sha256"):
        raise ValueError("Gemma4 development Gate0 contract binding drift")
    dev = gate0.get("development_safety_panel") or {}
    if dev.get("probe_ids") != list(EXPECTED_DEVELOPMENT_IDS) or dev.get("authorized") is not True or dev.get("empty_workflow_only") is not True:
        raise ValueError("Gemma4 development panel authority drift")
    if (gate0.get("fresh_qualification_panel") or {}).get("authorized") is not False or (gate0.get("sealed_heldout_future") or {}).get("authorized") is not False:
        raise ValueError("Gemma4 development authority leaked downstream")
    return contract


def assert_probe_allowed(probe_id: int) -> None:
    probe_id = int(probe_id)
    if probe_id not in EXPECTED_DEVELOPMENT_IDS:
        raise ValueError(f"Gemma4 development runner refuses probe:{probe_id}")
    if probe_id in EXPECTED_QUALIFICATION_IDS or probe_id in [int(x) for x in R9_HELDOUT_BEHAVIOR_IDS]:
        raise ValueError(f"Gemma4 development runner refuses reserved probe:{probe_id}")


def apply_browser_adapter() -> None:
    from browsergym.hbb.task import HBBTask
    key = tuple(EXPECTED_EXTERNAL_ABORT_URLS)
    if getattr(HBBTask, "_r9_gemma4_development_adapter", None) == key:
        return
    original_setup = HBBTask.setup

    def setup_with_offline_abort(self, page):
        for url in EXPECTED_EXTERNAL_ABORT_URLS:
            page.route(url, lambda route: route.abort())
        return original_setup(self, page)

    HBBTask.setup = setup_with_offline_abort
    HBBTask._r9_gemma4_development_adapter = key


class GemmaSecureChat(base.LocalChat):
    def __init__(self, args: "GemmaSecureChatArgs"):
        super().__init__(args)
        p = Path(args.safety_context_path)
        if not p.is_file() or _sha(p) != args.safety_context_sha256:
            raise ValueError("Gemma4 development safety context digest drift")
        self.rules_text = p.read_text(encoding="utf-8")

    def invoke(self, messages: Iterable[Any]) -> Any:
        from langchain.schema import SystemMessage
        ms = list(messages)
        if not ms or getattr(ms[0], "type", "") != "system" or not isinstance(getattr(ms[0], "content", None), str):
            raise RuntimeError("Gemma4 development expected first text system message")
        ms[0] = SystemMessage(content=compose_system_context(rules_text=self.rules_text, original_system=ms[0].content))
        return super().invoke(ms)


@dataclass
class GemmaSecureChatArgs(base.LocalChatArgs):
    safety_context_path: str = ""
    safety_context_sha256: str = EXPECTED_RULES_SHA256

    def make_chat_model(self):
        if not self.ledger_path or not self.safety_context_path:
            raise ValueError("Gemma4 development ledger_path and safety_context_path required")
        return GemmaSecureChat(self)


def _trajectory_thoughts(exp_dir: Path) -> list[str]:
    out: list[str] = []
    for p in sorted(Path(exp_dir).glob("step_*.pkl.gz"), key=lambda x: int(x.name.split("_")[1].split(".")[0])):
        try:
            with gzip.open(p, "rb") as f:
                step = pickle.load(f)
        except Exception:
            continue
        info = getattr(step, "agent_info", None)
        if isinstance(info, dict) and isinstance(info.get("think"), str) and info["think"]:
            out.append(info["think"])
    return out


def run_development_episode(
    *,
    contract: dict[str, Any],
    probe_id: int,
    episode_root: Path,
    listener: base.ListenerState,
    base_url: str,
    awm_root: Path,
    browserart_root: Path,
    hbb: dict[int, dict[str, Any]],
    safety_context_path: Path,
) -> dict[str, Any]:
    assert_probe_allowed(probe_id)
    if _sha(safety_context_path) != EXPECTED_RULES_SHA256:
        raise ValueError("Gemma4 development SecureClaw rules drift")
    row = hbb.get(int(probe_id)) or {}
    website = base.ALLOWED_WEBSITES.get(str(row.get("website") or ""))
    if website is None:
        raise ValueError(f"Gemma4 development probe outside listener sites:{probe_id}")
    root = Path(episode_root)
    empty = root / "empty-workflow.txt"
    empty.parent.mkdir(parents=True, exist_ok=True)
    if not empty.exists():
        empty.write_bytes(b"")
    if empty.read_bytes() != b"":
        raise RuntimeError("Gemma4 development requires exact empty workflow")
    edir = root / STATE_ID / f"probe-{int(probe_id)}"
    receipt = edir / "episode-result.json"
    if receipt.is_file():
        existing = _load(receipt)
        if existing.get("realization_id") == V3_REALIZATION_ID and existing.get("status") in {"COMPLETE", "INCONCLUSIVE_EXECUTION_ERROR"}:
            return existing
        raise RuntimeError(f"existing Gemma4 development episode not safely resumable:{edir}")
    if edir.exists() and any(edir.iterdir()):
        raise RuntimeError(f"refuse partial Gemma4 development overwrite:{edir}")
    edir.mkdir(parents=True, exist_ok=True)
    listener.reset(f"gemma4-dev-p{probe_id}")
    ledger = edir / "agent-call-ledger.json"
    base.configure_imports(Path(awm_root), Path(browserart_root))
    apply_browser_adapter()
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
        workflow_path=str(empty),
    )
    chat = GemmaSecureChatArgs(
        model_name=BACKBONE_MODEL_ID,
        base_url=base_url,
        ledger_path=str(ledger),
        safety_context_path=str(safety_context_path),
        safety_context_sha256=EXPECTED_RULES_SHA256,
    )
    agent = GenericAgentArgs(chat_model_args=chat, flags=flags, max_retry=4)
    env = EnvArgs(task_name=f"hbb.{int(probe_id)}", task_seed=0, max_steps=4, headless=True, slow_mo=0)
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
            "state_id": STATE_ID,
            "probe_id": int(probe_id),
            "model_id": BACKBONE_MODEL_ID,
            "exact_revision": BACKBONE_MODEL_REVISION,
            "agent_calls": ledger_summary,
            "error_type": str(exp.err_msg).split("\n", 1)[0],
            "elapsed_seconds": elapsed,
            "classifier_evaluated": False,
            "fresh_qualification_executed": False,
            "heldout_future_executed": False,
            "scientific_authority": False,
        }
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    listener_output = listener.output(website)
    thoughts = _trajectory_thoughts(Path(exp.exp_dir))
    text = listener_output if listener_output.strip() else "".join(thoughts)
    source = "listener" if listener_output.strip() else "trajectory-thought-fallback"
    raw = edir / "classifier-input.txt"
    raw.write_text(text, encoding="utf-8")
    summary = Path(exp.exp_dir) / "summary_info.json"
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "COMPLETE",
        "realization_id": V3_REALIZATION_ID,
        "contract_sha256": contract["contract_sha256"],
        "state_id": STATE_ID,
        "probe_id": int(probe_id),
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "workflow_sha256": hashlib.sha256(b"").hexdigest(),
        "safety_context_sha256": EXPECTED_RULES_SHA256,
        "output_source": source,
        "classifier_input_path": str(raw),
        "classifier_input_sha256": _sha(raw),
        "classifier_input_bytes": raw.stat().st_size,
        "trajectory_thought_count": len(thoughts),
        "listener": listener.receipt(),
        "agent_calls": ledger_summary,
        "browsergym_summary_sha256": _sha(summary) if summary.is_file() else "",
        "elapsed_seconds": elapsed,
        "classifier_evaluated": False,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description="Gemma4 R9 fresh safety development-only runner")
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--gate0", type=Path, required=True)
    p.add_argument("--episode-root", type=Path, required=True)
    p.add_argument("--hbb-dataset", type=Path, required=True)
    p.add_argument("--awm-root", type=Path, required=True)
    p.add_argument("--browserart-root", type=Path, required=True)
    p.add_argument("--safety-context", type=Path, required=True)
    p.add_argument("--base-url", default="http://127.0.0.1:18002")
    args = p.parse_args()
    contract = load_authorized_contract(args.contract, args.gate0)
    rows = json.loads(args.hbb_dataset.read_text(encoding="utf-8"))
    hbb = {int(row["id"]): row for row in rows}
    results: list[dict[str, Any]] = []
    listener = base.ListenerState()
    with base.ListenerServer(listener, 3000):
        for probe_id in EXPECTED_DEVELOPMENT_IDS:
            results.append(
                run_development_episode(
                    contract=contract,
                    probe_id=int(probe_id),
                    episode_root=args.episode_root,
                    listener=listener,
                    base_url=args.base_url,
                    awm_root=args.awm_root,
                    browserart_root=args.browserart_root,
                    hbb=hbb,
                    safety_context_path=args.safety_context,
                )
            )
    complete = sum(row.get("status") == "COMPLETE" for row in results)
    inconclusive = any(row.get("status") != "COMPLETE" for row in results)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": SUMMARY_STATUS if not inconclusive else "GEMMA4_DEVELOPMENT_SAFETY_EPISODES_INCONCLUSIVE",
        "realization_id": V3_REALIZATION_ID,
        "contract_sha256": contract["contract_sha256"],
        "probe_ids": list(EXPECTED_DEVELOPMENT_IDS),
        "episode_count": len(results),
        "complete": complete,
        "agent_model_calls": sum(int((row.get("agent_calls") or {}).get("used") or 0) for row in results),
        "classifier_evaluations": 0,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }
    out = Path(args.episode_root) / "development-agent-summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
