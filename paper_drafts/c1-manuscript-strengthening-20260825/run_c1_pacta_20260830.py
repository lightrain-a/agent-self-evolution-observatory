from __future__ import annotations

import csv
import fcntl
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file

PILOT_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1")
CONFIRM_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-c1-20260830-confirmatory-v1")
B10 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
ENV = Path("/home/wyt/code/agent-self-evolution-observatory/.env")
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"
ARMS = ["A0_NATIVE", "A1_SCB", "A2_SAP_ALWAYS", "A3_PACTA"]
BRANCHES = ["success", "failure"]
REPS = 6


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def shab(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def shat(value: str) -> str:
    return shab(value.encode("utf-8"))


def shaf(path: Path) -> str:
    return shab(path.read_bytes())


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tv(left, right) -> float:
    a, b = Counter(left), Counter(right)
    na, nb = len(left), len(right)
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in keys)


# Exact legacy B10/F1D first-action normalization.
def action_signature(payload) -> str:
    current = payload.get("current_state") or {}
    actions = payload.get("action") or (current.get("action") if isinstance(current, dict) else None) or []
    if not actions or not isinstance(actions[0], dict):
        return "NO_ACTION"
    action = actions[0]
    name = next(iter(action), "UNKNOWN")
    args = action.get(name) or {}
    if name == "click_element" and isinstance(args, dict):
        return f"click_element:{args.get('index')}"
    return name


# Exact R9 reuse of the B10-compatible policy parser, including its recovery path.
def parse_policy_output(text: str):
    try:
        payload = extract_json_object(text)
        signature = action_signature(payload)
        current = payload.get("current_state") or {}
        goal = str(current.get("next_goal") or "") if isinstance(current, dict) else str(payload.get("next_goal") or "")
        return signature, goal, False
    except Exception as exc:
        match = re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]', text, re.S)
        if not match:
            raise exc
        name, body = match.group(1), match.group(2)
        if name == "click_element":
            index = re.search(r'"index"\s*:\s*(\d+)', body)
            if not index:
                raise exc
            signature = f"click_element:{index.group(1)}"
        else:
            signature = name
        goal_match = re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"', text, re.S)
        goal = ""
        if goal_match:
            try:
                goal = json.loads('"' + goal_match.group(1) + '"')
            except Exception:
                goal = goal_match.group(1)
        return signature, goal, True


def parse_projection(text: str, action_schema: str):
    payload = extract_json_object(text)
    require(isinstance(payload, dict) and set(payload) == {"action", "next_goal"}, "projection must contain exactly action and next_goal")
    action = payload["action"]
    require(isinstance(action, list) and len(action) == 1, "projection must contain exactly one action")
    require(isinstance(action[0], dict) and len(action[0]) == 1, "projection action object must have exactly one tool")
    tool_name = next(iter(action[0]))
    require(isinstance(action[0][tool_name], dict), "projection tool arguments must be an object")
    require(tool_name in action_schema, f"projected tool {tool_name} absent from action schema")
    next_goal = payload["next_goal"]
    require(isinstance(next_goal, str) and len(next_goal.split()) <= 20, "next_goal exceeds 20 words or is not text")
    canonical = json.dumps(action[0], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return payload, canonical


def client():
    load_env_file(ENV)
    raw = ArkSettings.from_env()
    settings = ArkSettings(api_key=raw.api_key, base_url=raw.base_url, default_model=raw.default_model, timeout_seconds=180, max_retries=0)
    return ArkResponsesClient(settings), settings.safe_summary()


def provider_call(cl, prompt: str, max_tokens: int, temperature: float):
    response = cl.respond(
        prompt,
        model=MODEL,
        max_output_tokens=max_tokens,
        temperature=temperature,
        thinking="disabled",
        store=True,
        allow_thinking_compatibility_fallback=False,
    )
    require(response.get("requested_model") == MODEL, "requested model drift")
    require(response.get("resolved_model") == RESOLVED, "resolved model drift")
    require(response.get("thinking_compatibility_fallback") is False, "thinking fallback")
    text = str(response.get("text") or "")
    require(bool(text.strip()), "empty provider text")
    return response, text


def materialize_states(run: Path, phase: str):
    b10 = load(B10)
    split = load(run / "split.json")
    units = split["pilot" if phase == "pilot" else "confirmatory"]
    sys.path.insert(0, str(b10["vendor_path"]))
    import pyarrow.parquet as pq

    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    require(shaf(parquet) == b10["source_bindings"]["parquet"]["sha256"], "parquet drift")
    table = pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"])
    raw = {int(row["task_id"]): row for row in table.to_pylist()}
    states = {}
    for unit in units:
        tid = int(unit["future_task"])
        row = raw[tid]
        task = str(row["task_prompt"])
        require(shat(task) == unit["task_prompt_sha256"], f"task drift {tid}")
        trajectory = json.loads(str(row["trajectory_json"]))
        step = (trajectory.get("steps") or {}).get("1")
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        system = str(contents[0].get("content") or "")
        last = str(contents[-1].get("content") or "")
        marker = "[Current state starts here]"
        require(marker in last, f"current-state marker missing {tid}")
        state = last.split(marker, 1)[1].strip()
        require(shat(system) == unit["system_instruction_sha256"], f"system drift {tid}")
        require(shat(state) == unit["current_state_sha256"], f"state drift {tid}")
        memories = {}
        for branch in BRANCHES:
            path = Path(unit[f"{branch}_memory_wrapper_path"])
            require(path.is_file() and shaf(path) == unit[f"{branch}_memory_wrapper_sha256"], f"memory drift {tid}/{branch}")
            memories[branch] = path.read_text(encoding="utf-8")
        states[tid] = {"unit": unit, "system": system, "task": task, "state": state, "memory": memories}
    return states


def expand_projection(template: str, memory: str, task: str, state: str, schema: str) -> str:
    return template.replace("{memory}", memory).replace("{task}", task).replace("{state}", state).replace("{action_schema}", schema)


def scb_prompt(instruction: str, memory: str, task: str, state: str) -> str:
    return instruction + "\n\nREUSABLE MEMORY:\n" + memory + "\n\nULTIMATE TASK:\n" + task + "\n\nCURRENT BROWSER STATE:\n" + state


def policy_prompt(system: str, task: str, state: str, memory: str, note: str | None, structured: bool = False) -> str:
    if note is None:
        extra = ""
    else:
        label = "STRUCTURED ACTION IMPLICATION" if structured else "ADAPTED SUPPORT"
        extra = f"\n\n{label}:\n{note.strip()}"
    return f"""SYSTEM INSTRUCTION:
{system}

REUSABLE MEMORY:
{memory.strip()}{extra}

ULTIMATE TASK:
{task}

CURRENT BROWSER STATE:
{state}

Choose the next browser-agent action now. Return only the JSON object required by the system instruction."""


def execute_projections(cl, run: Path, states, prompts):
    geometry, failures = {}, []
    for tid, state in states.items():
        outputs = {}
        for branch in BRANCHES:
            outputs[branch] = {}
            for rendering in ["P0", "P1"]:
                short = "S" if branch == "success" else "F"
                path = run / "projection" / f"task-{tid}__branch-{short}__{rendering}.json"
                prompt = expand_projection(prompts[rendering]["template"], state["memory"][branch], state["task"], state["state"], state["system"])
                if path.exists():
                    artifact = load(path)
                    require(artifact["prompt_sha256"] == shat(prompt), f"projection resume prompt drift {tid}/{branch}/{rendering}")
                else:
                    response, text = provider_call(cl, prompt, 300, 0.0)
                    artifact = {
                        "schema_version": "1.0",
                        "artifact_kind": "C1_PACTA_PROJECTION",
                        "status": "projection_parse_or_realization_failure",
                        "future_task": tid,
                        "branch": branch,
                        "rendering": rendering,
                        "prompt_sha256": shat(prompt),
                        "prompt_template_sha256": prompts[rendering]["template_sha256"],
                        "memory_sha256": shat(state["memory"][branch]),
                        "task_sha256": shat(state["task"]),
                        "state_sha256": shat(state["state"]),
                        "action_schema_sha256": shat(state["system"]),
                        "requested_model": response.get("requested_model"),
                        "resolved_model": response.get("resolved_model"),
                        "response_id": response.get("response_id"),
                        "provider_status": response.get("status"),
                        "raw_output": text,
                        "raw_output_sha256": shat(text),
                        "usage": response.get("usage") or {},
                        "completed_at": now(),
                    }
                    try:
                        payload, canonical = parse_projection(text, state["system"])
                        artifact.update({"status": "complete", "parsed": payload, "parsed_action": payload["action"][0], "canonical_action": canonical, "next_goal": payload["next_goal"]})
                    except Exception as exc:
                        artifact.update({"failure_type": type(exc).__name__, "failure": str(exc)[:1600]})
                    dump(path, artifact)
                outputs[branch][rendering] = artifact
        good = all(outputs[b][p].get("status") == "complete" for b in BRANCHES for p in ["P0", "P1"])
        stable_s = good and outputs["success"]["P0"]["canonical_action"] == outputs["success"]["P1"]["canonical_action"]
        stable_f = good and outputs["failure"]["P0"]["canonical_action"] == outputs["failure"]["P1"]["canonical_action"]
        contrast = good and outputs["success"]["P0"]["canonical_action"] != outputs["failure"]["P0"]["canonical_action"]
        gate = bool(stable_s and stable_f and contrast)
        if not good:
            failures.append(tid)
        geometry[tid] = {
            "future_task": tid,
            "projection_complete": good,
            "stableS": bool(stable_s),
            "stableF": bool(stable_f),
            "contrast": bool(contrast),
            "G": gate,
            "z0S": outputs["success"]["P0"].get("canonical_action"),
            "z1S": outputs["success"]["P1"].get("canonical_action"),
            "z0F": outputs["failure"]["P0"].get("canonical_action"),
            "z1F": outputs["failure"]["P1"].get("canonical_action"),
        }
    dump(run / "projection-geometry.json", {"status": "COMPLETE", "states": list(geometry.values()), "failure_states": failures, "completed_at": now()})
    return geometry, failures


def execute_scb(cl, run: Path, states, contract):
    notes = {}
    instruction = contract["scb_baseline"]["instruction"]
    for tid, state in states.items():
        notes[tid] = {}
        for branch in BRANCHES:
            path = run / "scb" / f"task-{tid}__branch-{branch}.json"
            prompt = scb_prompt(instruction, state["memory"][branch], state["task"], state["state"])
            if path.exists():
                artifact = load(path)
                require(artifact["status"] == "complete" and artifact["prompt_sha256"] == shat(prompt), f"SCB resume drift {tid}/{branch}")
            else:
                response, text = provider_call(cl, prompt, 180, 0.0)
                artifact = {
                    "schema_version": "1.0",
                    "artifact_kind": "C1_PACTA_R9_SCB_BASELINE",
                    "status": "complete",
                    "future_task": tid,
                    "branch": branch,
                    "prompt_sha256": shat(prompt),
                    "memory_sha256": shat(state["memory"][branch]),
                    "text": text.strip(),
                    "text_sha256": shat(text.strip()),
                    "word_count": len(text.split()),
                    "requested_model": response.get("requested_model"),
                    "resolved_model": response.get("resolved_model"),
                    "response_id": response.get("response_id"),
                    "provider_status": response.get("status"),
                    "usage": response.get("usage") or {},
                    "completed_at": now(),
                }
                dump(path, artifact)
            notes[tid][branch] = artifact["text"]
    return notes


def structured_note(run: Path, tid: int, branch: str):
    short = "S" if branch == "success" else "F"
    artifact = load(run / "projection" / f"task-{tid}__branch-{short}__P0.json")
    if artifact.get("status") != "complete":
        return None
    return json.dumps(artifact["parsed"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def freeze_policy_schedule(run: Path, phase: str, states, geometry, notes):
    rows = []
    for tid, state in states.items():
        unit = state["unit"]
        for arm in ARMS:
            for branch in BRANCHES:
                projection = structured_note(run, tid, branch)
                if arm == "A0_NATIVE":
                    note, structured = None, False
                elif arm == "A1_SCB":
                    note, structured = notes[tid][branch], False
                elif arm == "A2_SAP_ALWAYS":
                    note, structured = projection, projection is not None
                else:
                    note = projection if geometry[tid]["G"] else None
                    structured = note is not None
                prompt = policy_prompt(state["system"], state["task"], state["state"], state["memory"][branch], note, structured)
                for rollout in range(1, REPS + 1):
                    case_id = f"task-{tid}__{arm}__{branch}_memory__r{rollout}"
                    rows.append({
                        "case_id": case_id,
                        "phase": phase,
                        "future_task": tid,
                        "intent_template_id": unit["intent_template_id"],
                        "selected_source_task": unit["selected_source_task"],
                        "arm": arm,
                        "branch": branch,
                        "rollout": rollout,
                        "gate_open": geometry[tid]["G"],
                        "used_structured_projection": structured,
                        "used_scb_note": arm == "A1_SCB",
                        "prompt": prompt,
                        "prompt_sha256": shat(prompt),
                        "memory_sha256": shat(state["memory"][branch]),
                        "support_sha256": "" if note is None else shat(note),
                    })
    rows.sort(key=lambda row: shat(f"C1-PACTA-{phase.upper()}-POLICY-SCHEDULE-v1|{row['case_id']}"))
    for index, row in enumerate(rows, 1):
        row["order"] = index
    schedule = run / "policy-schedule.jsonl"
    if schedule.exists():
        existing = [json.loads(line) for line in schedule.read_text(encoding="utf-8").splitlines() if line.strip()]
        require([r["prompt_sha256"] for r in existing] == [r["prompt_sha256"] for r in rows], "policy schedule drift")
    else:
        write_jsonl(schedule, rows)
    dump(run / "policy-input-manifest.json", {"status": "FROZEN_BEFORE_POLICY_OUTPUT", "cases": len(rows), "schedule_sha256": shaf(schedule), "created_at": now()})
    return rows


def execute_policy(cl, run: Path, rows):
    failures = []
    for row in rows:
        path = run / "per_case" / f"{row['case_id']}.json"
        if path.exists():
            artifact = load(path)
            require(artifact.get("status") == "complete" and artifact["prompt_sha256"] == row["prompt_sha256"], f"policy resume drift {row['case_id']}")
            continue
        try:
            response, text = provider_call(cl, row["prompt"], 900, 0.2)
            signature, goal, recovered = parse_policy_output(text)
            artifact = {k: v for k, v in row.items() if k != "prompt"}
            artifact.update({
                "schema_version": "1.0",
                "artifact_kind": "C1_PACTA_POLICY_RESPONSE",
                "status": "complete",
                "requested_model": response.get("requested_model"),
                "resolved_model": response.get("resolved_model"),
                "response_id": response.get("response_id"),
                "provider_status": response.get("status"),
                "raw_response": text,
                "raw_response_sha256": shat(text),
                "action_signature": signature,
                "next_goal_sha256": shat(goal) if goal else "",
                "parse_recovered": recovered,
                "usage": response.get("usage") or {},
                "completed_at": now(),
            })
            dump(path, artifact)
        except Exception as exc:
            artifact = {k: v for k, v in row.items() if k != "prompt"}
            artifact.update({"status": "failed", "failure_type": type(exc).__name__, "failure": str(exc)[:2000], "completed_at": now()})
            dump(path, artifact)
            failures.append(artifact)
            break
        if row["order"] % 12 == 0:
            dump(run / "progress.json", {"status": "RUNNING", "completed": len(list((run / "per_case").glob("*.json"))), "expected": len(rows), "updated_at": now()})
    if failures:
        dump(run / "progress.json", {"status": "STOP_ON_FIRST_FAILURE", "completed": len(list((run / "per_case").glob("*.json"))), "expected": len(rows), "failure": failures[0], "updated_at": now()})
        raise RuntimeError(f"policy execution stopped: {failures[0]['failure_type']}: {failures[0]['failure']}")
    cases = [load(path) for path in sorted((run / "per_case").glob("*.json"))]
    require(len(cases) == len(rows) and all(case["status"] == "complete" for case in cases), "policy cases incomplete")
    dump(run / "progress.json", {"status": "EXECUTION_COMPLETE", "completed": len(cases), "expected": len(rows), "failed": 0, "updated_at": now()})
    return cases


def phase_analysis(run: Path, phase: str, states, geometry, projection_failures, cases):
    per_state = []
    for tid, state in states.items():
        row = {
            "future_task": tid,
            "intent_template_id": state["unit"]["intent_template_id"],
            "selected_source_task": state["unit"]["selected_source_task"],
            "G": geometry[tid]["G"],
            "stableS": geometry[tid]["stableS"],
            "stableF": geometry[tid]["stableF"],
            "contrast": geometry[tid]["contrast"],
            "projection_complete": geometry[tid]["projection_complete"],
        }
        for arm in ARMS:
            success = [case["action_signature"] for case in cases if case["future_task"] == tid and case["arm"] == arm and case["branch"] == "success"]
            failure = [case["action_signature"] for case in cases if case["future_task"] == tid and case["arm"] == arm and case["branch"] == "failure"]
            require(len(success) == REPS and len(failure) == REPS, f"replicate count drift {tid}/{arm}")
            row[f"U_{arm}"] = tv(success, failure)
        row["D_gate"] = row["U_A3_PACTA"] - row["U_A2_SAP_ALWAYS"]
        row["D_scb"] = row["U_A3_PACTA"] - row["U_A1_SCB"]
        row["N"] = row["U_A3_PACTA"] - row["U_A0_NATIVE"]
        per_state.append(row)
    means = {f"mean_U_{arm}": sum(row[f"U_{arm}"] for row in per_state) / len(per_state) for arm in ARMS}
    means.update({
        "mean_D_gate": sum(row["D_gate"] for row in per_state) / len(per_state),
        "mean_D_scb": sum(row["D_scb"] for row in per_state) / len(per_state),
        "mean_N": sum(row["N"] for row in per_state) / len(per_state),
    })
    with (run / f"{phase}-per-state.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_state[0]))
        writer.writeheader()
        writer.writerows(per_state)
    return per_state, means


def pilot_gate(run: Path, per_state, means, projection_failures, cases):
    open_rows = [row for row in per_state if row["G"]]
    open_count = len(open_rows)
    mean_open = sum(row["D_gate"] for row in open_rows) / open_count if open_count else None
    positive_open = sum(row["D_gate"] > 0 for row in open_rows)
    fallback_rows = [row for row in per_state if not row["projection_complete"]]
    checks = {
        "state_packets_invariant_6_of_6": len(per_state) == 6,
        "model_drift_zero": all(case.get("resolved_model") == RESOLVED for case in cases),
        "projection_failure_states_le_1": len(projection_failures) <= 1,
        "gate_non_degenerate_2_to_5": 2 <= open_count <= 5,
        "gate_open_mean_D_gate_ge_0_05": mean_open is not None and mean_open >= 0.05,
        "gate_open_positive_at_least_half": open_count > 0 and positive_open / open_count >= 0.5,
        "overall_mean_A3_minus_A0_gt_0": means["mean_N"] > 0,
        "no_parse_or_fallback_advantage": all(row["D_gate"] <= 0 for row in fallback_rows),
    }
    passed = all(checks.values())
    status = "PILOT_SIGNAL_PASS" if passed else ("HOLD_GATE_DEGENERATE" if not checks["gate_non_degenerate_2_to_5"] else "PILOT_HOLD_OR_STOP")
    analysis = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_PILOT_ANALYSIS",
        "status": status,
        "method": "PACTA",
        "development_label": "CAST",
        "execution": {
            "states": 6,
            "projection_calls": 24,
            "scb_calls": 12,
            "policy_calls": len(cases),
            "model_drift": sum(case.get("resolved_model") != RESOLVED for case in cases),
            "policy_parse_recovered": sum(bool(case.get("parse_recovered")) for case in cases),
            "projection_failure_states": projection_failures,
            "confirmatory_executed": False,
        },
        "gate_geometry": {"open_count": open_count, "closed_count": 6 - open_count, "open_ids": [row["future_task"] for row in open_rows], "mean_D_gate_open": mean_open, "positive_D_gate_open": positive_open},
        "effect_summary": means,
        "gate": {"checks": checks, "pass": passed, "thresholds_unchanged": True},
        "heterogeneity": per_state,
        "claim_boundary": "Pilot is an identifiability/signal screen only and carries no confirmatory or utility claim.",
    }
    dump(run / "pilot-analysis.json", analysis)
    return analysis


def sign_flip_test(values, repetitions=100000, seed=20260830):
    observed = sum(values) / len(values)
    rng = random.Random(seed)
    exceed = 0
    for _ in range(repetitions):
        statistic = sum(value if rng.getrandbits(1) else -value for value in values) / len(values)
        if statistic >= observed - 1e-15:
            exceed += 1
    return observed, (exceed + 1) / (repetitions + 1)


def confirmatory_gate(run: Path, per_state, means, projection_failures, cases):
    values = [row["D_gate"] for row in per_state]
    observed, p_value = sign_flip_test(values)
    open_rows = [row for row in per_state if row["G"]]
    mean_open = sum(row["D_gate"] for row in open_rows) / len(open_rows) if open_rows else None
    checks = {
        "mean_D_gate_ge_0_05": observed >= 0.05,
        "one_sided_p_lt_0_05": p_value < 0.05,
        "mean_U_A3_gt_mean_U_A0": means["mean_U_A3_PACTA"] > means["mean_U_A0_NATIVE"],
        "gate_open_mean_D_gate_gt_0": mean_open is not None and mean_open > 0,
        "model_drift_zero": all(case.get("resolved_model") == RESOLVED for case in cases),
        "state_packets_invariant_13_of_13": len(per_state) == 13,
    }
    passed = all(checks.values())
    analysis = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_CONFIRMATORY_ANALYSIS",
        "status": "CONFIRMATORY_FIRST_ACTION_PASS" if passed else "CONFIRMATORY_FIRST_ACTION_FAIL",
        "execution": {"states": 13, "projection_calls": 52, "scb_calls": 26, "policy_calls": len(cases), "projection_failure_states": projection_failures, "terminal_executed": False},
        "primary": {"contrast": "A3_PACTA - A2_SAP_ALWAYS", "mean_D_gate": observed, "one_sided_sign_flip_p": p_value, "repetitions": 100000, "seed": 20260830},
        "secondary": {"mean_D_scb": means["mean_D_scb"], "mean_N": means["mean_N"], "mean_U_A3": means["mean_U_A3_PACTA"], "mean_U_A2": means["mean_U_A2_SAP_ALWAYS"], "mean_U_A1": means["mean_U_A1_SCB"], "mean_U_A0": means["mean_U_A0_NATIVE"]},
        "gate_geometry": {"open_count": len(open_rows), "closed_count": 13 - len(open_rows), "open_ids": [row["future_task"] for row in open_rows], "mean_D_gate_open": mean_open},
        "gate": {"checks": checks, "pass": passed},
        "heterogeneity": per_state,
        "claim_boundary": "Primary endpoint remains A3 minus A2 regardless of secondary contrast magnitude.",
    }
    dump(run / "confirmatory-analysis.json", analysis)
    return analysis


def failure_differential(run: Path, phase: str, analysis, means, geometry, projection_failures):
    comparison = {
        "A2_and_A3_effective": means["mean_U_A2_SAP_ALWAYS"] > means["mean_U_A0_NATIVE"] and means["mean_U_A3_PACTA"] > means["mean_U_A0_NATIVE"],
        "A3_better_than_A2": means["mean_D_gate"] > 0,
        "A3_worse_than_A2": means["mean_D_gate"] < 0,
        "gate_open_fraction": sum(bool(value["G"]) for value in geometry.values()) / len(geometry),
    }
    gate_count = sum(bool(value["G"]) for value in geometry.values())
    layers = {
        "execution": False,
        "provider": False,
        "projection_schema": bool(projection_failures),
        "projection_instability": sum(not (value["stableS"] and value["stableF"]) for value in geometry.values()),
        "gate_degeneracy": not (2 <= gate_count <= len(geometry) - 1) if phase == "pilot" else None,
        "measurement": False,
        "generic_action_projection": comparison["A2_and_A3_effective"],
        "counterfactual_gate_mechanism": "supported" if analysis["gate"]["pass"] else ("negative" if comparison["A3_worse_than_A2"] else "unresolved_or_insufficient"),
        "terminal_utility": "not_tested",
    }
    dump(run / f"{phase}-failure-differential.json", {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_FAILURE_DIFFERENTIAL",
        "phase": phase,
        "scientific_pass": analysis["gate"]["pass"],
        "layers": layers,
        "competing_explanation": comparison,
    })


def run_phase(cl, run: Path, phase: str):
    contract = load(run / "contract.json")
    prompts = load(run / "projector-prompts.json")
    support = load(PILOT_RUN / "model-support.json")
    require(support["status"] == "SUPPORT_PASS" and support["resolved_model"] == RESOLVED, "provider support not qualified")
    states = materialize_states(run, phase)
    geometry, projection_failures = execute_projections(cl, run, states, prompts)
    notes = execute_scb(cl, run, states, contract)
    rows = freeze_policy_schedule(run, phase, states, geometry, notes)
    cases = execute_policy(cl, run, rows)
    per_state, means = phase_analysis(run, phase, states, geometry, projection_failures, cases)
    analysis = pilot_gate(run, per_state, means, projection_failures, cases) if phase == "pilot" else confirmatory_gate(run, per_state, means, projection_failures, cases)
    failure_differential(run, phase, analysis, means, geometry, projection_failures)
    return analysis


def main() -> int:
    lock_path = PILOT_RUN / ".execution.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("a+")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    audit = load(HERE / "c1-cast-novelty-audit-20260830.json")
    require(audit["verdict"] == "PASS_NOVEL_RESIDUAL", "novelty gate is not open")
    require(git("status", "--porcelain") == "", "execution worktree must be clean and committed")
    execution_sha = git("rev-parse", "HEAD")
    origin_main = git("rev-parse", "origin/main")
    manifest = load(PILOT_RUN / "manifest.json")
    manifest.update({"status": "SCIENTIFIC_EXECUTION_STARTED", "execution_git_sha": execution_sha, "origin_main_sha_at_execution": origin_main, "started_at": now()})
    dump(PILOT_RUN / "manifest.json", manifest)

    cl, summary = client()
    dump(PILOT_RUN / "provider-summary.json", summary)
    pilot = run_phase(cl, PILOT_RUN, "pilot")
    if not pilot["gate"]["pass"]:
        dump(PILOT_RUN / "final-verdict.json", {
            "status": pilot["status"],
            "method_claim_status": "PACTA_CANDIDATE_NOT_QUALIFIED",
            "active_manuscript": "R9",
            "confirmatory_executed": False,
            "terminal_executed": False,
            "execution_git_sha": execution_sha,
            "completed_at": now(),
        })
        print(json.dumps({"status": pilot["status"], "confirmatory": "NOT_EXECUTED", "terminal": "NOT_EXECUTED"}))
        return 0

    shutil.copy2(PILOT_RUN / "model-support.json", CONFIRM_RUN / "model-support.json")
    confirm_manifest = load(CONFIRM_RUN / "manifest.json")
    confirm_manifest.update({"status": "UNSEALED_AUTOMATICALLY_AFTER_FROZEN_PILOT_PASS", "pilot_analysis_sha256": shaf(PILOT_RUN / "pilot-analysis.json"), "execution_git_sha": execution_sha, "unsealed_at": now()})
    dump(CONFIRM_RUN / "manifest.json", confirm_manifest)
    pilot["execution"]["confirmatory_executed"] = True
    dump(PILOT_RUN / "pilot-analysis.json", pilot)

    confirm = run_phase(cl, CONFIRM_RUN, "confirmatory")
    if not confirm["gate"]["pass"]:
        final = {
            "status": "PACTA_PILOT_SIGNAL_CONFIRMATORY_FAIL",
            "method_claim_status": "pilot signal does not survive sealed confirmatory",
            "active_manuscript": "R9",
            "confirmatory_executed": True,
            "terminal_executed": False,
            "execution_git_sha": execution_sha,
            "completed_at": now(),
        }
    else:
        final = {
            "status": "PACTA_FIRST_ACTION_CONFIRMATORY_PASS_TERMINAL_QUALIFICATION_REQUIRED",
            "method_claim_status": "selective feedback-conditioned behavioral transport supported; task utility not yet supported",
            "active_manuscript": "R10_candidate_pending_terminal_or_bounded_claim",
            "confirmatory_executed": True,
            "terminal_executed": False,
            "terminal_status": "PENDING_EVALUATOR_PATH_QUALIFICATION",
            "execution_git_sha": execution_sha,
            "completed_at": now(),
        }
    dump(CONFIRM_RUN / "final-verdict.json", final)
    print(json.dumps({"status": final["status"], "confirmatory_mean_D_gate": confirm["primary"]["mean_D_gate"], "p": confirm["primary"]["one_sided_sign_flip_p"], "terminal": final.get("terminal_status", "NOT_EXECUTED")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
