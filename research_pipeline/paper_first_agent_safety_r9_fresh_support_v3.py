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
from .paper_first_agent_safety_r9_harness import CANDIDATE_ID, CONTRACT_SHA256

SCHEMA = "1.0"
REALIZATION_ID = "R9-FRESH-SUPPORT-SECURECLAW-V3"
EXPECTED_DEVELOPMENT_IDS = [0, 9, 36]
EXPECTED_QUALIFICATION_IDS = [2, 10, 38]
EXPECTED_HELDOUT_IDS = [34, 21, 1, 8, 11, 22, 13, 33]
EXPECTED_SECURECLAW_COMMIT = "bf17e2b3deb989e348b3a98080e33a7047e90ac3"
EXPECTED_RULES_SHA256 = "2a82bcb8d7fd9291852be27666dc8a3c496e3d2da0bb2756effd6045c6656ad4"
EXPECTED_EXTERNAL_ABORT_URLS = [
    "https://twitter.com/compose/twitter-logo.png",
    "https://picsum.photos/48",
    "https://picsum.photos/48?random=1",
    "https://kit.fontawesome.com/a076d05399.js",
]
EXPECTED_TWITTER_HTML_SHA256 = "63cfe828edac802957401a353de3bdcf92518d565c4ec229cb6fcfe87407a45d"
EXPECTED_HBB_TASK_SHA256 = "8796d13e900d01e0fe6c60d446b534b51397711f213e57030f094a9f8358a65a"


def sha_file(path: Path) -> str:
    return base.sha_file(Path(path))


def load_json(path: Path) -> dict[str, Any]:
    return base.load_json(Path(path))


def compose_system_context(*, rules_text: str, original_system: str) -> str:
    if not rules_text.endswith("\n"):
        raise ValueError("fresh-support rules file must end in exactly one recorded newline")
    return rules_text + "\n" + original_system


def load_fresh_contract(path: Path) -> dict[str, Any]:
    d = load_json(path)
    if d.get("realization_id") != REALIZATION_ID or d.get("candidate_id") != CANDIDATE_ID or d.get("contract_sha256") != CONTRACT_SHA256:
        raise ValueError("fresh-support contract identity drift")
    if d.get("status") != "PREREGISTERED_FRESH_SUPPORT_REALIZATION" or d.get("scientific_authority") is not False:
        raise ValueError("fresh-support contract must remain preregistered and zero-authority")
    panels = d.get("probe_panels") or {}
    dev = [int(x) for x in panels.get("development_headroom_ids") or []]
    qual = [int(x) for x in panels.get("fresh_qualification_ids") or []]
    held = [int(x) for x in panels.get("sealed_heldout_future_ids") or []]
    if dev != EXPECTED_DEVELOPMENT_IDS or qual != EXPECTED_QUALIFICATION_IDS or held != EXPECTED_HELDOUT_IDS:
        raise ValueError("fresh-support panel drift")
    if set(dev) & set(qual) or (set(dev) | set(qual)) & set(held):
        raise ValueError("fresh-support panels overlap")
    safety = d.get("safety_substrate") or {}
    if safety.get("upstream_commit") != EXPECTED_SECURECLAW_COMMIT or safety.get("rules_sha256") != EXPECTED_RULES_SHA256:
        raise ValueError("fresh-support SecureClaw pin drift")
    if safety.get("content_editing_forbidden") is not True or safety.get("applies_identically_to_all_states_all_current_and_future_steps") is not True:
        raise ValueError("fresh-support safety context invariance missing")
    browser_adapter = d.get("browser_runtime_adapter") or {}
    if (
        browser_adapter.get("type") != "PLAYWRIGHT_EXACT_EXTERNAL_REQUEST_ABORT_SET"
        or list(browser_adapter.get("urls") or []) != EXPECTED_EXTERNAL_ABORT_URLS
        or browser_adapter.get("pinned_twitter_html_sha256") != EXPECTED_TWITTER_HTML_SHA256
        or browser_adapter.get("pinned_hbb_task_py_sha256") != EXPECTED_HBB_TASK_SHA256
        or browser_adapter.get("html_modified") is not False
        or browser_adapter.get("task_config_modified") is not False
        or browser_adapter.get("local_dom_modified") is not False
        or browser_adapter.get("probe_specific") is not False
    ):
        raise ValueError("fresh-support browser runtime adapter drift")
    state_policy = d.get("state_policy") or {}
    states = [x for x in state_policy.get("state_identities") or [] if isinstance(x, dict)]
    if len(states) != 4 or state_policy.get("post_outcome_state_replacement_forbidden") is not True:
        raise ValueError("fresh-support state policy drift")
    for s in states:
        p = Path(str(s.get("workflow_path") or ""))
        if not p.is_file() or sha_file(p) != str(s.get("workflow_sha256") or ""):
            raise ValueError(f"fresh-support workflow drift:{s.get('state_id')}")
    return {"raw": d, "development_ids": dev, "qualification_ids": qual, "heldout_ids": held, "states": states}


def apply_browser_runtime_adapter(contract: dict[str, Any]) -> None:
    from browsergym.hbb.task import HBBTask
    adapter_key = tuple(EXPECTED_EXTERNAL_ABORT_URLS)
    if getattr(HBBTask, "_r9_fresh_support_adapter", None) == adapter_key:
        return
    original_setup = HBBTask.setup
    def setup_with_offline_abort(self, page):
        for url in EXPECTED_EXTERNAL_ABORT_URLS:
            page.route(url, lambda route: route.abort())
        return original_setup(self, page)
    HBBTask.setup = setup_with_offline_abort
    HBBTask._r9_fresh_support_adapter = adapter_key


def assert_probe_allowed(*, probe: int, mode: str, contract: dict[str, Any]) -> None:
    allowed = contract["development_ids"] if mode == "development" else contract["qualification_ids"] if mode == "qualification" else []
    if probe not in allowed:
        raise ValueError(f"fresh-support runner refuses probe {probe} in mode {mode}")
    if probe in contract["heldout_ids"]:
        raise ValueError(f"fresh-support runner refuses held-out probe:{probe}")


class SecureContextChat(base.LocalChat):
    def __init__(self, args: "SecureContextChatArgs"):
        super().__init__(args)
        p = Path(args.safety_context_path)
        if not p.is_file() or sha_file(p) != args.safety_context_sha256:
            raise ValueError("fresh-support safety context digest drift")
        self.rules_text = p.read_text(encoding="utf-8")

    def invoke(self, messages: Iterable[Any]) -> Any:
        from langchain.schema import SystemMessage
        ms = list(messages)
        if not ms or getattr(ms[0], "type", "") != "system" or not isinstance(getattr(ms[0], "content", None), str):
            raise RuntimeError("fresh-support adapter expected first text system message")
        ms[0] = SystemMessage(content=compose_system_context(rules_text=self.rules_text, original_system=ms[0].content))
        return super().invoke(ms)


@dataclass
class SecureContextChatArgs(base.LocalChatArgs):
    safety_context_path: str = ""
    safety_context_sha256: str = EXPECTED_RULES_SHA256

    def make_chat_model(self):
        if not self.ledger_path or not self.safety_context_path:
            raise ValueError("fresh-support ledger_path and safety_context_path are required")
        return SecureContextChat(self)


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


def run_fresh_episode(
    *,
    contract: dict[str, Any],
    mode: str,
    state: dict[str, Any],
    probe: int,
    episode_root: Path,
    listener: base.ListenerState,
    qwen_url: str,
    awm_root: Path,
    browserart_root: Path,
    hbb: dict[int, dict[str, Any]],
    safety_context_path: Path,
) -> dict[str, Any]:
    assert_probe_allowed(probe=probe, mode=mode, contract=contract)
    sid = str(state["state_id"])
    workflow = Path(str(state["workflow_path"]))
    expected = str(state["workflow_sha256"])
    if not workflow.is_file() or sha_file(workflow) != expected:
        raise RuntimeError(f"fresh-support workflow mutated:{sid}")
    if sha_file(safety_context_path) != EXPECTED_RULES_SHA256:
        raise RuntimeError("fresh-support safety context mutated")
    edir = Path(episode_root) / sid / f"probe-{probe}"
    receipt = edir / "episode-result.json"
    if receipt.is_file():
        d = load_json(receipt)
        if d.get("status") == "COMPLETE" and d.get("realization_id") == REALIZATION_ID and d.get("safety_context_sha256") == EXPECTED_RULES_SHA256:
            return d
        raise RuntimeError(f"existing fresh-support episode is not safely resumable:{edir}")
    if edir.exists() and any(edir.iterdir()):
        raise RuntimeError(f"refuse partial fresh-support overwrite:{edir}")
    edir.mkdir(parents=True, exist_ok=True)
    listener.reset(f"{sid}-p{probe}")
    ledger = edir / "agent-call-ledger.json"
    base.configure_imports(Path(awm_root), Path(browserart_root))
    apply_browser_runtime_adapter(contract)
    from browsergym.experiments import EnvArgs, ExpArgs
    from agents.legacy.agent import GenericAgentArgs
    from agents.legacy.dynamic_prompting import Flags

    flags = Flags(
        use_html=False, use_ax_tree=True, use_thinking=True, use_error_logs=True, use_past_error_logs=True,
        use_history=True, use_action_history=True, use_memory=False, use_diff=False, use_concrete_example=True,
        use_abstract_example=True, multi_actions=True, action_space="bid", use_screenshot=False, enable_chat=True,
        demo_mode="off", workflow_path=str(workflow),
    )
    chat = SecureContextChatArgs(
        model_name="Qwen/Qwen3-8B", base_url=qwen_url, ledger_path=str(ledger),
        safety_context_path=str(safety_context_path), safety_context_sha256=EXPECTED_RULES_SHA256,
    )
    agent = GenericAgentArgs(chat_model_args=chat, flags=flags, max_retry=4)
    env = EnvArgs(task_name=f"hbb.{probe}", task_seed=0, max_steps=4, headless=True, slow_mo=0)
    exp = ExpArgs(agent_args=agent, env_args=env, enable_debug=False)
    exp.prepare(edir / "browsergym")
    start = time.time(); exp.run(); elapsed = time.time() - start
    ledger_summary = base.EpisodeLedger(ledger).summary()
    if exp.err_msg:
        d = {
            "schema_version": SCHEMA, "status": "INCONCLUSIVE_EXECUTION_ERROR", "realization_id": REALIZATION_ID,
            "candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "mode": mode,
            "state_id": sid, "probe_id": probe, "workflow_sha256": expected,
            "safety_context_sha256": EXPECTED_RULES_SHA256, "agent_calls": ledger_summary,
            "error_type": str(exp.err_msg).split("\n", 1)[0], "elapsed_seconds": elapsed, "scientific_authority": False,
        }
        receipt.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return d
    row = hbb[probe]
    website = base.ALLOWED_WEBSITES.get(str(row.get("website") or ""))
    if website is None:
        raise RuntimeError(f"fresh-support probe outside listener websites:{probe}")
    listener_output = listener.output(website)
    t = _trajectory_thoughts(Path(exp.exp_dir))
    text = listener_output if listener_output.strip() else "".join(t)
    source = "listener" if listener_output.strip() else "trajectory-thought-fallback"
    raw = edir / "classifier-input.txt"; raw.write_text(text, encoding="utf-8")
    summary = Path(exp.exp_dir) / "summary_info.json"
    d = {
        "schema_version": SCHEMA, "status": "COMPLETE", "realization_id": REALIZATION_ID,
        "candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "mode": mode,
        "state_id": sid, "site_stratum": str(state.get("site_stratum") or ""), "probe_id": probe,
        "workflow_sha256": expected, "safety_context_sha256": EXPECTED_RULES_SHA256,
        "output_source": source, "classifier_input_path": str(raw), "classifier_input_sha256": sha_file(raw),
        "classifier_input_bytes": raw.stat().st_size, "trajectory_thought_count": len(t), "listener": listener.receipt(),
        "agent_calls": ledger_summary, "browsergym_summary_sha256": sha_file(summary) if summary.is_file() else "",
        "elapsed_seconds": elapsed, "classifier_evaluated": False, "scientific_authority": False,
    }
    receipt.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return d


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--mode", choices=("development", "qualification"), required=True)
    p.add_argument("--episode-root", type=Path, required=True)
    p.add_argument("--hbb-dataset", type=Path, required=True)
    p.add_argument("--awm-root", type=Path, required=True)
    p.add_argument("--browserart-root", type=Path, required=True)
    p.add_argument("--safety-context", type=Path, required=True)
    p.add_argument("--qwen-base-url", default="http://127.0.0.1:18001")
    args = p.parse_args()
    c = load_fresh_contract(args.contract)
    hbb_rows = json.loads(args.hbb_dataset.read_text(encoding="utf-8")); hbb = {int(x["id"]): x for x in hbb_rows}
    if args.mode == "development":
        empty = args.episode_root / "empty-workflow.txt"; empty.parent.mkdir(parents=True, exist_ok=True); empty.write_bytes(b"")
        states = [{"state_id": "fresh-dev-empty-workflow", "site_stratum": "development", "workflow_path": str(empty), "workflow_sha256": hashlib.sha256(b"").hexdigest()}]
        probes = c["development_ids"]
    else:
        states = c["states"]; probes = c["qualification_ids"]
    listener = base.ListenerState(); results: list[dict[str, Any]] = []
    with base.ListenerServer(listener, 3000):
        for state in states:
            for probe in probes:
                results.append(run_fresh_episode(contract=c, mode=args.mode, state=state, probe=probe, episode_root=args.episode_root,
                    listener=listener, qwen_url=args.qwen_base_url, awm_root=args.awm_root, browserart_root=args.browserart_root,
                    hbb=hbb, safety_context_path=args.safety_context))
    summary = {
        "schema_version": SCHEMA, "realization_id": REALIZATION_ID, "mode": args.mode,
        "status": f"FRESH_SUPPORT_{args.mode.upper()}_EPISODES_COMPLETE" if all(x.get("status") == "COMPLETE" for x in results) else f"FRESH_SUPPORT_{args.mode.upper()}_EPISODES_INCONCLUSIVE",
        "episode_count": len(results), "complete": sum(x.get("status") == "COMPLETE" for x in results),
        "agent_model_calls": sum(int((x.get("agent_calls") or {}).get("used") or 0) for x in results),
        "heldout_future_executed": False, "scientific_authority": False,
    }
    out = args.episode_root / f"{args.mode}-agent-summary.json"; out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
