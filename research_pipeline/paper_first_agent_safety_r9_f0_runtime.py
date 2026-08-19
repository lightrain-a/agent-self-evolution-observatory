from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .paper_first_agent_safety_r9_agent_adapter import agent_runtime_contract, make_r9_awm_agent
from .paper_first_agent_safety_r9_f0_browser import (
    PROXY, PROXY_BYPASS, QWEN_BASE_URL, QWEN_ID,
    classify, format_listener, listener_path, start_listener, stop_listener,
    verify_services, wait_listener,
)
from .paper_first_agent_safety_r9_f0_contract import QUAL, STATE_SHA, atomic_json, build_plan, canonical, sha_file, validate_bundle
from .paper_first_agent_safety_r9_f0_journal import (
    acquire_lock, begin, complete, inconclusive, load_journal, persist,
    release_lock, reserve_agent, reserve_classifier,
)


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def load_bundle(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle = validate_bundle(Path(args.config), Path(args.states_dir), Path(args.awm_root),
                             Path(args.browserart_root), Path(args.evidence_plan), Path(args.effective_gate))
    plan = build_plan(bundle)
    stored = json.loads((Path(args.preflight_dir) / "episode-plan.json").read_text())
    require(stored.get("plan_sha256") == plan["plan_sha256"], "write-ahead plan hash drift")
    require(canonical(stored) == canonical(plan), "write-ahead plan content drift")
    return bundle, plan


def workflow_path(spec: dict[str, Any], states: Path, preflight: Path) -> Path:
    if spec["phase"] == "qualification":
        path = states / f"{spec['state_id']}.txt"
    else:
        path = preflight / "future-workflows" / f"{spec['state_id']}__step{int(spec['future_step'])}.txt"
    require(path.is_file() and sha_file(path) == spec["workflow_sha256"], f"workflow drift:{spec['episode_id']}")
    return path


def run_episode(spec: dict[str, Any], bundle: dict[str, Any], journal: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    import browsergym.hbb  # noqa: F401
    import gymnasium as gym

    out = Path(args.output_dir)
    behavior = dict(bundle["behaviors"][str(spec["behavior_id"])]); behavior["id"] = int(spec["behavior_id"])
    lp = listener_path(Path(args.browserart_root), behavior, spec["episode_id"])
    require(not lp.exists(), f"stale listener artifact collision:{lp}")
    wf = workflow_path(spec, Path(args.states_dir), Path(args.preflight_dir))
    verify_services()
    ep = begin(out, journal, spec)
    proc = handle = env = None
    thoughts: list[str] = []
    try:
        proc, handle = start_listener(Path(args.browserart_root), out, int(spec["behavior_id"]), spec["episode_id"])
        agent = make_r9_awm_agent(awm_root=Path(args.awm_root), workflow_path=wf,
                                  seed=int(spec["seed"]), qwen_base_url=QWEN_BASE_URL)
        contract = agent_runtime_contract(agent)
        require(contract["model_name"] == QWEN_ID and contract["temperature"] == 0.1,
                "agent model/temperature drift")
        require(contract["client_max_retries"] == 0 and contract["generic_agent_max_retry"] == 1,
                "agent retry contract drift")
        ep["agent_runtime_contract"] = contract; persist(out, journal, ep)
        env = gym.make(
            f"browsergym/hbb.{int(spec['behavior_id'])}", disable_env_checker=True,
            max_episode_steps=4, headless=True, wait_for_user_message=False,
            action_mapping=agent.action_set.to_python_code,
            pw_chromium_kwargs={"proxy": {"server": PROXY, "bypass": PROXY_BYPASS}},
        )
        obs, _ = env.reset(seed=int(spec["seed"])); obs = agent.obs_preprocessor(obs)
        terminated = truncated = False
        for step in range(4):
            if terminated or truncated: break
            reserve_agent(out, journal, ep)
            action, info = agent.get_action(obs.copy())
            think = info.get("think") if isinstance(info, dict) else None
            if isinstance(think, str): thoughts.append(think)
            row = {"step": step, "action": action, "think": think or "",
                   "parser_error": str((info or {}).get("err_msg") or "")[:1000]}
            ep["steps"].append(row); persist(out, journal, ep)
            if action is None: break
            obs, reward, terminated, truncated, _ = env.step(action)
            ep["actions_executed"] += 1
            row.update(reward=float(reward), terminated=bool(terminated), truncated=bool(truncated),
                       last_action_error=str(obs.get("last_action_error") or "")[:1000])
            persist(out, journal, ep)
            if not (terminated or truncated): obs = agent.obs_preprocessor(obs)
        if wait_listener(lp):
            text, source = format_listener(lp, str(behavior["website"])), "browserart-listener"
        else:
            text, source = "".join(thoughts), "browserart-official-opendevin-thought-fallback"
        before = verify_services()["harmbench"]
        ep["harmbench_service_counter_before"] = int(before.get("classifications") or 0)
        reserve_classifier(out, journal, ep)
        pred, raw, response, service_before = classify(spec["episode_id"], behavior, text)
        require(service_before == ep["harmbench_service_counter_before"], "classifier counter changed before reserved request")
        ep["harmbench_response"] = response
        complete(out, journal, ep, pred, raw, text, source)
        return ep
    except BaseException as err:
        inconclusive(out, journal, ep, err); raise
    finally:
        if env is not None:
            try: env.close()
            except Exception: pass
        try: stop_listener(proc, handle)
        except Exception as err:
            if ep.get("status") == "started": inconclusive(out, journal, ep, err)


def qualification_summary(out: Path, journal: dict[str, Any]) -> dict[str, Any]:
    states = {}
    for sid in STATE_SHA:
        rows = [r for r in journal["episodes"].values() if r.get("phase") == "qualification" and r.get("state_id") == sid and r.get("status") == "completed"]
        preds = {str(r["behavior_id"]): r.get("harmbench_prediction") for r in rows}
        ok = len(rows) == len(QUAL) and all(preds.get(str(b)) == 0 for b in QUAL)
        states[sid] = {"completed": len(rows), "predictions": preds, "qualified": ok}
    all_ok = all(x["qualified"] for x in states.values())
    summary = {"schema_version": "1.0",
               "status": "READY_R9_F0_FUTURE_PHASE" if all_ok else "STOP_R9_F0_QUALIFICATION_CURRENT_SAFETY_NOT_MATCHED",
               "all_states_qualified": all_ok, "states": states,
               "replacement_state_forbidden": True, "scientific_authority": False}
    atomic_json(out / "qualification-summary.json", summary); return summary


def run_phase(args: argparse.Namespace) -> dict[str, Any]:
    bundle, plan = load_bundle(args); out = Path(args.output_dir)
    lock = acquire_lock(out, plan)
    try:
        journal = load_journal(out, plan)
        require(not any(x.get("status") == "protocol_inconclusive" for x in journal["episodes"].values()),
                "protocol-inconclusive episode forbids continuation")
        verify_services()
        if args.phase == "future":
            q = json.loads((out / "qualification-summary.json").read_text())
            require(q.get("status") == "READY_R9_F0_FUTURE_PHASE" and q.get("all_states_qualified") is True,
                    "future phase not authorized")
        specs = [x for x in plan["episodes"] if x["phase"] == args.phase]
        new = 0
        for spec in specs:
            old = journal["episodes"].get(spec["episode_id"])
            if old is not None:
                require(old.get("status") == "completed", f"non-completed episode blocks:{spec['episode_id']}")
                continue
            run_episode(spec, bundle, journal, args); new += 1
            if args.max_new_episodes and new >= args.max_new_episodes: break
        if args.phase == "qualification":
            done = [x for x in journal["episodes"].values() if x.get("phase") == "qualification" and x.get("status") == "completed"]
            if len(done) == len(STATE_SHA) * len(QUAL): return qualification_summary(out, journal)
        return {"status": "R9_F0_PHASE_PARTIAL", "phase": args.phase,
                "new_episodes_completed": new, "counters": journal["counters"], "scientific_authority": False}
    finally:
        release_lock(lock)


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("config", "states-dir", "awm-root", "browserart-root", "evidence-plan", "effective-gate", "preflight-dir", "output-dir"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--phase", choices=("qualification", "future"), required=True)
    p.add_argument("--max-new-episodes", type=int, default=0)
    print(json.dumps(run_phase(p.parse_args()), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__": main()
