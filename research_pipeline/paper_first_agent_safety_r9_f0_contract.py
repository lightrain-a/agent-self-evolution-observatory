from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .paper_first_agent_safety_r9_harness import (
    BROWSERART_PINNED_FILES,
    CANDIDATE_ID,
    CONTRACT_SHA256,
    R9_AGENT_MODEL_ID,
    R9_AGENT_MODEL_REVISION,
    R9_EVALUATOR_MODEL_ID,
    R9_EVALUATOR_MODEL_REVISION,
)

AWM_COMMIT = "8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1"
BROWSERART_COMMIT = "0d72180042f2a076c68e1114e7494cb3fc7dd30b"
CONFIG_FILE_SHA = "953a6a84ded256578a2c96743bd032f5ce65f1021de0a23977cd3129cfb68dcf"
CONFIG_INNER_SHA = "f698ed284eb3581c367df7b920a3105f95e8a85950763a24e31691d011c8b9c6"
EVIDENCE_PLAN_SHA = "4d5318e7d1ca9b90b73eb26d437537ddb199d135b89e1c11c74e385fe0609c22"
EFFECTIVE_GATE_SHA = "5d01ec8e1ab8e5c1a9c19d55d5550086d6cbefafedc6a4d5aee8019bcb77fb35"
STATE_SHA = {
    "shopping_admin-A": "4444e6788b897e0c652239842065fa91da1fd4037a372abf2fca723d62c3d6d7",
    "shopping_admin-B": "ec9ebca3a0275d9c80f38886e42729cd22b9540dc74a4fa6f22c6254990dde9f",
    "reddit-A": "964ac9cdd2c938dcd9982e1f77cd873c0639ba158c9c10332c02f0a1d89daf07",
    "reddit-B": "4a2c790a080f0bc7b3e1859f2aba3423ea39fc7b7f979000d99d3b8c5a1a9a99",
}
QUAL = [14, 16, 18]
HELD = [34, 21, 1, 8, 11, 22, 13, 33]
BRANCH_SEEDS = [11, 23, 37]
BRANCH_PROBES = {"11": [11, 8, 21], "23": [34, 33, 21], "37": [11, 21, 33]}
FUTURE_SHA = [
    "8af82cf981bfb0bc56acfb4d071db767929e574ad5db17d22e8d964fe2696b97",
    "cf7a3f9dcf159cddba19e84e5ab9ca33b77b4dee283b293713c17d9ecfe64363",
    "b1c83c5dd2bb66b5bd82a885096efb6781c2c6340e211d8c2df75a9b5e7641c0",
]
BUDGET = {
    "states": 4, "qualification_probes_per_state": 3, "branches_per_state": 3,
    "future_horizon_updates": 3, "future_probes_per_update": 1,
    "agent_model_calls_cap_per_episode": 4, "classifier_model_evaluations_per_episode": 1,
    "qualification_episodes": 12, "future_episodes": 36, "total_behavior_episodes": 48,
    "agent_model_calls_upper_bound": 192, "classifier_model_evaluations_upper_bound": 48,
    "total_model_evaluations_upper_bound": 240, "contract_max_model_calls": 256,
    "reserve": 16, "feasible": True,
}
ACTION_RE = re.compile(r"\b(click|fill|select_option|clear|hover|scroll|send_msg_to_user)\s*\(")


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def split_units(path: Path) -> list[dict[str, Any]]:
    text = Path(path).read_text(encoding="utf-8")
    parts = [x for x in re.split(r"(?=^Query: )", text, flags=re.M) if x.startswith("Query: ")]
    return [{"index": i, "text": x, "sha256": sha_bytes(x.encode()), "actions": len(ACTION_RE.findall(x))} for i, x in enumerate(parts)]


def qualification_seed(behavior_id: int) -> int:
    digest = hashlib.sha256(f"{CONTRACT_SHA256}:qualification:probe:{behavior_id}".encode()).hexdigest()
    return int(digest[:8], 16) & 0x7FFFFFFF


def append_update(base: str, unit: str) -> str:
    return base.rstrip() + "\n\n" + unit.rstrip() + "\n"


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def validate_bundle(config_path: Path, states_dir: Path, awm_root: Path, browserart_root: Path,
                    evidence_plan: Path, effective_gate: Path) -> dict[str, Any]:
    require(sha_file(config_path) == CONFIG_FILE_SHA, "frozen config file digest drift")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    inner = dict(cfg); claimed = inner.pop("frozen_config_sha256", "")
    require(claimed == CONFIG_INNER_SHA == sha_bytes(canonical(inner)), "frozen config self-hash drift")
    require(cfg.get("candidate_id") == CANDIDATE_ID and cfg.get("contract_sha256") == CONTRACT_SHA256, "candidate/contract drift")
    require(cfg.get("pinned_sources") == {"awm_commit": AWM_COMMIT, "browserart_commit": BROWSERART_COMMIT}, "source pin drift")
    head = subprocess.check_output(["git", "-C", str(awm_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == AWM_COMMIT, "local AWM checkout drift")
    require(sha_file(evidence_plan) == EVIDENCE_PLAN_SHA, "evidence plan digest drift")
    ep = json.loads(evidence_plan.read_text()); rows = [x for x in ep.get("entries", []) if x.get("candidate_id") == CANDIDATE_ID]
    require(ep.get("status") == "EVIDENCE_EXECUTION_READY" and len(rows) == 1 and rows[0].get("execution_authorized") is True, "generic evidence plan not ready")
    require(sha_file(effective_gate) == EFFECTIVE_GATE_SHA, "effective gate digest drift")
    gate = json.loads(effective_gate.read_text())
    require(gate.get("status") == "READY_R9_BOUNDED_EVIDENCE_EXECUTION" and gate.get("effective_execution_authorized") is True and gate.get("blockers") == [] and gate.get("fallback_allowed") is False, "effective gate not READY")

    sc = cfg["state_construction"]; states = sc["states"]
    require(len(states) == 4 and {x["state_id"] for x in states} == set(STATE_SHA), "stale/noncanonical state set")
    require(sc.get("current_state_pair_selection_uses_outcomes") is False and "no replacement" in sc.get("current_safety_inclusion_rule", "").lower(), "outcome-free state gate drift")
    require(len(sc.get("pair_metrics", [])) == 2 and all(x.get("hard_match_pass") for x in sc["pair_metrics"]), "pair-match gate drift")
    wf = awm_root / "webarena" / "workflow"
    parsed = {name: split_units(wf / f"{name}.txt") for name in ("shopping_admin", "reddit", "gitlab")}
    require([len(parsed[x]) for x in ("shopping_admin", "reddit", "gitlab")] == [7, 6, 6], "AWM unit-count drift")
    verified_states = {}
    for row in states:
        sid, site = row["state_id"], row["site_stratum"]
        selected = [parsed[site][int(i)] for i in row["history_unit_indices"]]
        require([u["sha256"] for u in selected] == row["history_unit_sha256"], f"history unit drift:{sid}")
        text = "\n\n".join(u["text"].rstrip() for u in selected) + "\n"
        path = states_dir / f"{sid}.txt"
        require(path.read_text(encoding="utf-8") == text, f"state serializer drift:{sid}")
        require(sha_file(path) == row["workflow_sha256"] == STATE_SHA[sid], f"state digest drift:{sid}")
        verified_states[sid] = {"state_id": sid, "site_stratum": site, "path": str(path), "sha256": STATE_SHA[sid]}

    future = cfg["future_updates"]
    require(future.get("mode") == "released-benign-workflow-unit-append" and future.get("same_schedule_for_all_states") is True and future.get("update_generation_model_calls") == 0, "future-update contract drift")
    schedule = future.get("schedule", []); require(len(schedule) == 3, "future horizon drift")
    future_units = []
    for step, (item, expected) in enumerate(zip(schedule, FUTURE_SHA), start=1):
        unit = parsed["gitlab"][int(item["source_index"])]
        require(item.get("step") == step and item.get("source_file") == "gitlab.txt" and item.get("unit_sha256") == expected == unit["sha256"], f"future unit drift:{step}")
        future_units.append({"step": step, **unit})

    split = cfg["safety_probe_split"]
    require(split.get("qualification_ids") == QUAL and split.get("heldout_ids") == HELD and split.get("split_uses_outcomes") is False and split.get("disjoint") is True, "probe split drift")
    branching = cfg["branching"]
    require(branching.get("seeds") == BRANCH_SEEDS and branching.get("heldout_probe_schedule_by_seed") == BRANCH_PROBES and branching.get("common_random_numbers_across_states") is True, "branch schedule drift")
    for seed in BRANCH_SEEDS:
        order = sorted(HELD, key=lambda bid: hashlib.sha256(f"{CONTRACT_SHA256}:branch:{seed}:probe:{bid}".encode()).hexdigest())
        require(order[:3] == branching["heldout_probe_schedule_by_seed"][str(seed)], f"branch schedule derivation drift:{seed}")
    require(cfg.get("budget") == BUDGET, "48-episode/240-evaluation budget drift")
    agent, evaluator = cfg["agent"], cfg["evaluator"]
    require(agent.get("backbone") == R9_AGENT_MODEL_ID and agent.get("temperature") == 0.1 and agent.get("max_agent_model_calls_per_behavior_episode") == 4 and agent.get("fallback_allowed") is False, "agent contract drift")
    require(evaluator.get("hf_model") == R9_EVALUATOR_MODEL_ID and evaluator.get("temperature") == 0.0 and evaluator.get("fallback_allowed") is False, "evaluator contract drift")
    require(R9_AGENT_MODEL_REVISION == "b968826d9c46dd6066d109eabc6255188de91218" and R9_EVALUATOR_MODEL_REVISION == "0cd31cdc8b53209dd5b153b20026ff085901bb14", "compiled model revision drift")
    for rel, digest in BROWSERART_PINNED_FILES.items():
        require((browserart_root / rel).is_file() and sha_file(browserart_root / rel) == digest, f"BrowserART source drift:{rel}")
    rows = json.loads((browserart_root / "src/datasets/behaviors/hbb.json").read_text())
    by_id = {int(x["id"]): x for x in rows}
    for bid in QUAL + HELD:
        row = by_id.get(bid)
        require(row is not None and row.get("evaluation_category") == "closed-ended" and row.get("website") in {"local:email", "local:twitter", "local:review"}, f"frozen probe eligibility drift:{bid}")
    return {"status": "READY_R9_F0_CANONICAL_BUNDLE", "candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256,
            "states": verified_states, "future_units": future_units, "behaviors": {str(x): by_id[x] for x in QUAL + HELD},
            "provider_calls_executed": 0, "gpu_calls_executed": 0, "harmful_behavior_executions": 0, "scientific_authority": False}


def build_plan(bundle: dict[str, Any]) -> dict[str, Any]:
    episodes = []
    for sid in STATE_SHA:
        for bid in QUAL:
            seed = qualification_seed(bid)
            episodes.append({"phase": "qualification", "episode_id": f"qual__{sid}__b{bid}__s{seed}", "state_id": sid,
                             "site_stratum": bundle["states"][sid]["site_stratum"], "behavior_id": bid, "seed": seed,
                             "workflow_sha256": STATE_SHA[sid], "execution_condition": "always", "max_agent_model_calls": 4,
                             "classifier_model_evaluations": 1})
    future_workflow_sha = {}
    for sid in STATE_SHA:
        text = Path(bundle["states"][sid]["path"]).read_text()
        future_workflow_sha[sid] = []
        for unit in bundle["future_units"]:
            text = append_update(text, unit["text"])
            future_workflow_sha[sid].append({"step": unit["step"], "sha256": sha_bytes(text.encode()), "text": text, "unit_sha256": unit["sha256"]})
    for sid in STATE_SHA:
        for seed in BRANCH_SEEDS:
            for step, bid in enumerate(BRANCH_PROBES[str(seed)], start=1):
                wf = future_workflow_sha[sid][step - 1]
                episodes.append({"phase": "future", "episode_id": f"future__{sid}__branch{seed}__step{step}__b{bid}", "state_id": sid,
                                 "site_stratum": bundle["states"][sid]["site_stratum"], "behavior_id": bid, "seed": seed, "branch_seed": seed,
                                 "future_step": step, "workflow_sha256": wf["sha256"], "appended_unit_sha256": wf["unit_sha256"],
                                 "execution_condition": "state_qualified_on_all_three_frozen_qualification_probes", "max_agent_model_calls": 4,
                                 "classifier_model_evaluations": 1})
    require(len(episodes) == 48 and len({x["episode_id"] for x in episodes}) == 48, "episode ledger cardinality drift")
    require(sum(x["max_agent_model_calls"] for x in episodes) == 192 and sum(x["classifier_model_evaluations"] for x in episodes) == 48, "episode ledger budget drift")
    plan = {"schema_version": "1.0", "status": "R9_F0_WRITE_AHEAD_PLAN_FROZEN", "candidate_id": CANDIDATE_ID,
            "contract_sha256": CONTRACT_SHA256, "frozen_config_inner_sha256": CONFIG_INNER_SHA,
            "qualification_seed_rule": "uint31(sha256(contract + ':qualification:probe:' + behavior_id)[:8])",
            "qualification_seeds": {str(x): qualification_seed(x) for x in QUAL},
            "replacement_state_after_qualification_outcomes_forbidden": True, "completed_episode_rerun_forbidden": True,
            "agent_max_retry": 1, "openai_client_max_retries": 0, "browser_max_steps": 4,
            "episodes": episodes, "budget": BUDGET, "scientific_authority": False}
    plan["plan_sha256"] = sha_bytes(canonical(plan))
    return plan


def write_zero_model_ledger(bundle: dict[str, Any], plan: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True); wfdir = output_dir / "future-workflows"; wfdir.mkdir(exist_ok=True)
    generated = []
    for sid in STATE_SHA:
        text = Path(bundle["states"][sid]["path"]).read_text()
        for unit in bundle["future_units"]:
            text = append_update(text, unit["text"]); path = wfdir / f"{sid}__step{unit['step']}.txt"; path.write_text(text)
            generated.append({"state_id": sid, "step": unit["step"], "path": str(path), "sha256": sha_file(path)})
    atomic_json(output_dir / "canonical-bundle-validation.json", bundle); atomic_json(output_dir / "episode-plan.json", plan)
    receipt = {"schema_version": "1.0", "status": "READY_R9_F0_ZERO_MODEL_LEDGER", "candidate_id": CANDIDATE_ID,
               "contract_sha256": CONTRACT_SHA256, "plan_sha256": plan["plan_sha256"], "episode_count": 48,
               "qualification_episode_count": 12, "future_episode_slots": 36, "generated_future_workflows": generated,
               "provider_calls_executed": 0, "gpu_calls_executed": 0, "harmful_behavior_executions": 0,
               "execution_started": False, "scientific_authority": False}
    atomic_json(output_dir / "zero-model-ledger-smoke.json", receipt); return receipt
