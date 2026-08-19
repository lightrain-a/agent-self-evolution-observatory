from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import pickle
from pathlib import Path
from typing import Any

from . import paper_first_agent_safety_r9_qualification as base
from .paper_first_agent_safety_r9_backbone_preflight import BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION
from .paper_first_agent_safety_r9_gemma4_hbb_protocol_repair import V4_REALIZATION_ID, validate_v4
from .paper_first_agent_safety_r9_gemma4_v4_development import (
    DEFAULT_AWM_ROOT,
    DEFAULT_BROWSERART_ROOT,
    DEFAULT_V4_CONTRACT,
    _sha,
    load_v4,
)

SCHEMA_VERSION = "1.0"
RECOVERY_CLASS = "V4_EXISTING_BROWSERGYM_TRACE_LISTENER_EQUIVALENT_RECOVERY"
RECOVERABLE_PROBE_ID = 31
EXPECTED_TASK_SHA256 = "8796d13e900d01e0fe6c60d446b534b51397711f213e57030f094a9f8358a65a"
DEFAULT_PROBE_ROOT = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v4-20260819/development/gemma4-v4-dev-empty-workflow/probe-31")


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _single_run_dir(probe_root: Path) -> Path:
    runs = [p for p in (Path(probe_root) / "browsergym").iterdir() if p.is_dir()]
    if len(runs) != 1:
        raise ValueError(f"V4 recovery requires one BrowserGym run, got {len(runs)}")
    return runs[0]


def _call(action: str) -> tuple[str, list[str]]:
    tree = ast.parse(action, mode="eval")
    if not isinstance(tree.body, ast.Call) or not isinstance(tree.body.func, ast.Name):
        raise ValueError(f"V4 recovery action is not a simple function call:{action!r}")
    values: list[str] = []
    for arg in tree.body.args:
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
            raise ValueError(f"V4 recovery action argument is not a literal string:{action!r}")
        values.append(arg.value)
    return tree.body.func.id, values


def _load_steps(*, run_dir: Path, awm_root: Path, browserart_root: Path) -> list[Any]:
    base.configure_imports(Path(awm_root), Path(browserart_root))
    import browsergym.hbb.task as hbb_task
    task_path = Path(hbb_task.__file__)
    if _sha(task_path) != EXPECTED_TASK_SHA256:
        raise ValueError(f"V4 recovery loaded HBB task bytes drift:{task_path}")
    steps = []
    for path in sorted(Path(run_dir).glob("step_*.pkl.gz"), key=lambda p: int(p.name.split("_")[1].split(".")[0])):
        with gzip.open(path, "rb") as handle:
            steps.append(pickle.load(handle))
    return steps


def build_recovery(
    *, v4_contract_path: Path = DEFAULT_V4_CONTRACT, probe_root: Path = DEFAULT_PROBE_ROOT,
    awm_root: Path = DEFAULT_AWM_ROOT, browserart_root: Path = DEFAULT_BROWSERART_ROOT,
) -> dict[str, Any]:
    contract = load_v4(Path(v4_contract_path))
    if validate_v4(contract):
        raise ValueError("V4 recovery contract drift")
    if RECOVERABLE_PROBE_ID not in (contract.get("probe_panels") or {}).get("development_probe_ids", []):
        raise ValueError("V4 recovery probe is no longer in development panel")
    probe_root = Path(probe_root)
    receipt = probe_root / "episode-result.json"
    classifier_input = probe_root / "classifier-input.txt"
    if receipt.exists() or classifier_input.exists():
        raise ValueError("V4 recovery only applies before episode receipt/classifier input exists")
    ledger_path = probe_root / "agent-call-ledger.json"
    ledger = _load(ledger_path)
    if int(ledger.get("used") or 0) != 4 or len(ledger.get("calls") or []) != 4:
        raise ValueError("V4 recovery requires exact four-call ledger")
    run_dir = _single_run_dir(probe_root)
    summary_path = run_dir / "summary_info.json"
    summary = _load(summary_path)
    if summary.get("err_msg") not in (None, "") or int(summary.get("n_steps") or 0) != 4:
        raise ValueError("V4 recovery BrowserGym run is not a completed four-step trace")
    steps = _load_steps(run_dir=run_dir, awm_root=awm_root, browserart_root=browserart_root)
    if len(steps) != 5:
        raise ValueError(f"V4 recovery expected five persisted states, got {len(steps)}")
    actions = [str(getattr(step, "action", "") or "") for step in steps[:4]]
    parsed = [_call(action) for action in actions]
    if [name for name, _ in parsed] != ["click", "fill", "click", "send_msg_to_user"]:
        raise ValueError(f"V4 recovery action sequence drift:{[name for name, _ in parsed]}")
    fill_args = parsed[1][1]
    click_args = parsed[2][1]
    if len(fill_args) != 2 or len(click_args) != 1 or not fill_args[1].strip():
        raise ValueError("V4 recovery fill/click action arguments drift")
    filled_text = fill_args[1]
    fill_bid, submit_bid = fill_args[0], click_args[0]
    obs_before_submit = getattr(steps[2], "obs", {}) or {}
    axtree = str(obs_before_submit.get("axtree_txt") or "")
    if fill_bid not in axtree or submit_bid not in axtree or filled_text not in axtree:
        raise ValueError("V4 recovery pre-submit AXTree does not bind exact filled text and submit control")
    submit_line = next((line for line in axtree.splitlines() if submit_bid in line), "")
    if "button" not in submit_line.lower() or "tweet" not in submit_line.lower():
        raise ValueError("V4 recovery submit control is not the Twitter Tweet button")
    obs_after_submit = getattr(steps[3], "obs", {}) or {}
    after_axtree = str(obs_after_submit.get("axtree_txt") or "")
    if filled_text in after_axtree:
        raise ValueError("V4 recovery tweet text did not clear after submit")
    experiment_log = run_dir / "experiment.log"
    log_text = experiment_log.read_text(encoding="utf-8", errors="replace")
    if log_text.count("POST http://127.0.0.1:18002/v1/chat/completions") != 4:
        raise ValueError("V4 recovery server-call count drift")
    return {
        "schema_version": SCHEMA_VERSION,
        "recovery_class": RECOVERY_CLASS,
        "realization_id": V4_REALIZATION_ID,
        "contract_sha256": contract["parent_contract_sha256"],
        "v4_preregistration_sha256": _sha(v4_contract_path),
        "probe_id": RECOVERABLE_PROBE_ID,
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "agent_calls": {"cap": int(ledger.get("cap") or 4), "used": 4, "remaining": 0},
        "output_source": "recovered-twitter-listener-equivalent-single-fill-input-event",
        "classifier_text": filled_text,
        "classifier_input_sha256": hashlib.sha256(filled_text.encode("utf-8")).hexdigest(),
        "classifier_input_bytes": len(filled_text.encode("utf-8")),
        "classifier_evaluated": False,
        "recovery_proof": {
            "action_function_sequence": [name for name, _ in parsed],
            "fill_bid": fill_bid,
            "submit_bid": submit_bid,
            "pre_submit_axtree_contains_exact_text": True,
            "submit_control_is_tweet_button": True,
            "post_submit_axtree_text_cleared": True,
            "twitter_listener_semantics": "ListenerState.output('twitter') concatenates /saveTweet body.tweetText; the BrowserART page posts tweetText on textarea input and clears value after submit without dispatching another input event.",
            "browsergym_summary_err_msg": summary.get("err_msg"),
            "browsergym_steps": int(summary.get("n_steps") or 0),
        },
        "browsergym_summary_sha256": _sha(summary_path),
        "experiment_log_sha256": _sha(experiment_log),
        "agent_call_ledger_sha256": _sha(ledger_path),
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "scientific_authority": False,
    }


def write_recovery(*, v4_contract_path: Path = DEFAULT_V4_CONTRACT, probe_root: Path = DEFAULT_PROBE_ROOT,
                   awm_root: Path = DEFAULT_AWM_ROOT, browserart_root: Path = DEFAULT_BROWSERART_ROOT) -> dict[str, Any]:
    state = build_recovery(v4_contract_path=v4_contract_path, probe_root=probe_root, awm_root=awm_root, browserart_root=browserart_root)
    probe_root = Path(probe_root)
    raw = state.pop("classifier_text")
    classifier_path = probe_root / "classifier-input.txt"
    classifier_path.write_text(raw, encoding="utf-8")
    receipt = {
        **state,
        "status": "COMPLETE",
        "classifier_input_path": str(classifier_path),
        "trajectory_thought_count": None,
        "elapsed_seconds": None,
        "receipt_recovered_without_model_calls": True,
    }
    (probe_root / "episode-result.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover V4 probe31 receipt from already-existing BrowserGym artifacts only")
    parser.add_argument("--v4-contract", type=Path, default=DEFAULT_V4_CONTRACT)
    parser.add_argument("--probe-root", type=Path, default=DEFAULT_PROBE_ROOT)
    parser.add_argument("--awm-root", type=Path, default=DEFAULT_AWM_ROOT)
    parser.add_argument("--browserart-root", type=Path, default=DEFAULT_BROWSERART_ROOT)
    args = parser.parse_args()
    receipt = write_recovery(v4_contract_path=args.v4_contract, probe_root=args.probe_root, awm_root=args.awm_root, browserart_root=args.browserart_root)
    print(json.dumps({
        "status": receipt["status"],
        "recovery_class": receipt["recovery_class"],
        "probe_id": receipt["probe_id"],
        "classifier_input_sha256": receipt["classifier_input_sha256"],
        "classifier_evaluated": False,
        "new_model_calls": 0,
        "qualification_executed": False,
        "heldout_executed": False,
        "scientific_authority": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
