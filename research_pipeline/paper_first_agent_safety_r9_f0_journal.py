from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import BUDGET, atomic_json


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def journal_path(out: Path) -> Path:
    return out / "runtime-journal.json"


def load_journal(out: Path, plan: dict[str, Any]) -> dict[str, Any]:
    path = journal_path(out)
    if path.exists():
        data = json.loads(path.read_text())
        require(data.get("plan_sha256") == plan["plan_sha256"], "journal plan drift")
        return data
    data = {
        "schema_version": "1.0",
        "status": "R9_F0_RUNTIME_JOURNAL_ACTIVE",
        "plan_sha256": plan["plan_sha256"],
        "counters": {
            "behavior_episode_starts": 0,
            "agent_model_calls_reserved": 0,
            "classifier_evaluations_reserved": 0,
            "completed_episodes": 0,
            "protocol_inconclusive_episodes": 0,
        },
        "episodes": {},
        "scientific_authority": False,
    }
    atomic_json(path, data)
    return data


def persist(out: Path, journal: dict[str, Any], episode: dict[str, Any] | None = None) -> None:
    if episode is not None:
        atomic_json(out / "episodes" / f"{episode['episode_id']}.json", episode)
    atomic_json(journal_path(out), journal)


def begin(out: Path, journal: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    eid = spec["episode_id"]
    require(eid not in journal["episodes"], f"episode rerun forbidden:{eid}")
    ep = {**spec, "status": "started", "started_at_unix": time.time(),
          "agent_model_calls_reserved": 0, "classifier_evaluations_reserved": 0,
          "actions_executed": 0, "steps": [], "scientific_authority": False}
    journal["episodes"][eid] = ep
    journal["counters"]["behavior_episode_starts"] += 1
    persist(out, journal, ep)
    return ep


def reserve_agent(out: Path, journal: dict[str, Any], ep: dict[str, Any]) -> None:
    require(ep["agent_model_calls_reserved"] < ep["max_agent_model_calls"], "episode agent cap exceeded")
    require(journal["counters"]["agent_model_calls_reserved"] < BUDGET["agent_model_calls_upper_bound"], "global agent budget exceeded")
    total = journal["counters"]["agent_model_calls_reserved"] + journal["counters"]["classifier_evaluations_reserved"]
    require(total < BUDGET["contract_max_model_calls"], "contract model-call cap exceeded")
    ep["agent_model_calls_reserved"] += 1
    journal["counters"]["agent_model_calls_reserved"] += 1
    persist(out, journal, ep)


def reserve_classifier(out: Path, journal: dict[str, Any], ep: dict[str, Any]) -> None:
    require(ep["classifier_evaluations_reserved"] == 0, "classifier retry forbidden")
    require(journal["counters"]["classifier_evaluations_reserved"] < BUDGET["classifier_model_evaluations_upper_bound"], "classifier budget exceeded")
    total = journal["counters"]["agent_model_calls_reserved"] + journal["counters"]["classifier_evaluations_reserved"]
    require(total < BUDGET["contract_max_model_calls"], "contract model-call cap exceeded")
    ep["classifier_evaluations_reserved"] = 1
    journal["counters"]["classifier_evaluations_reserved"] += 1
    persist(out, journal, ep)


def inconclusive(out: Path, journal: dict[str, Any], ep: dict[str, Any], err: BaseException | str) -> None:
    if ep.get("status") == "protocol_inconclusive":
        return
    ep["status"] = "protocol_inconclusive"
    ep["inconclusive_reason"] = (f"{type(err).__name__}:{err}" if isinstance(err, BaseException) else str(err))[:1000]
    ep["completed_at_unix"] = time.time()
    journal["counters"]["protocol_inconclusive_episodes"] += 1
    journal["status"] = "HOLD_R9_F0_PROTOCOL_INCONCLUSIVE"
    persist(out, journal, ep)


def complete(out: Path, journal: dict[str, Any], ep: dict[str, Any], prediction: int, raw_label: str, text: str, source: str) -> None:
    require(prediction in (0, 1), "prediction must be binary")
    ep.update(status="completed", completed_at_unix=time.time(), harmbench_prediction=prediction,
              safety_violation=prediction == 1, harmbench_raw_label=raw_label,
              text_output=text, text_output_source=source)
    journal["counters"]["completed_episodes"] += 1
    persist(out, journal, ep)


def recover_classifier_realization(out: Path, journal: dict[str, Any], ep: dict[str, Any], *,
                                   prediction: int, raw_label: str, text: str, source: str,
                                   recovery: dict[str, Any]) -> None:
    require(ep.get("status") == "protocol_inconclusive", "recovery requires protocol-inconclusive episode")
    require(ep.get("classifier_evaluations_reserved") == 1, "recovery requires existing classifier reservation")
    require("harmbench_prediction" not in ep, "recovery forbidden after classifier result")
    require(prediction in (0, 1), "prediction must be binary")
    prior = {
        "status": "protocol_inconclusive",
        "reason": ep.get("inconclusive_reason"),
        "completed_at_unix": ep.get("completed_at_unix"),
    }
    ep.update(
        status="completed",
        completed_at_unix=time.time(),
        harmbench_prediction=prediction,
        safety_violation=prediction == 1,
        harmbench_raw_label=raw_label,
        text_output=text,
        text_output_source=source,
        realization_recovered=True,
        prior_protocol_inconclusive=prior,
        realization_recovery=dict(recovery),
    )
    ep.pop("inconclusive_reason", None)
    require(journal["counters"]["protocol_inconclusive_episodes"] > 0, "inconclusive counter underflow")
    journal["counters"]["protocol_inconclusive_episodes"] -= 1
    journal["counters"]["completed_episodes"] += 1
    if journal["counters"]["protocol_inconclusive_episodes"] == 0:
        journal["status"] = "R9_F0_RUNTIME_JOURNAL_ACTIVE"
    persist(out, journal, ep)


def acquire_lock(out: Path, plan: dict[str, Any]) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / ".runtime.lock"
    if path.exists():
        old = json.loads(path.read_text())
        pid = int(old.get("pid") or 0)
        try:
            os.kill(pid, 0)
            alive = pid > 0
        except OSError:
            alive = False
        require(not alive, f"executor already active pid={pid}")
        journal = load_journal(out, plan)
        changed = False
        for ep in journal["episodes"].values():
            if ep.get("status") == "started":
                inconclusive(out, journal, ep, "executor ended after episode reservation")
                changed = True
        if changed:
            raise RuntimeError("stale started episode reconciled as protocol-inconclusive")
        path.unlink(missing_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.write(fd, (json.dumps({"pid": os.getpid(), "plan_sha256": plan["plan_sha256"]}) + "\n").encode())
    os.close(fd)
    return path


def release_lock(path: Path) -> None:
    try:
        data = json.loads(path.read_text())
        if int(data.get("pid") or 0) == os.getpid():
            path.unlink(missing_ok=True)
    except FileNotFoundError:
        pass
