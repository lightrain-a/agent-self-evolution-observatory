from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import random
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import run_c1_pacta_20260830 as v1
from c1_pacta_v11_action_schema import (
    canonical_schema,
    extract_minimal_action_schema,
    sha256_text,
    validate_action_object,
)

QUAL_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-q0-schema-20260830-v1")
PILOT_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-p0-fresh-7template-20260830-v1")
B10 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"
BRANCHES = ["success", "failure"]
ARMS = ["A0_NATIVE", "A1_SCB", "A2_SAP_ALWAYS", "A3_PACTA"]
REPS = 6


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def shab(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a[key] / len(left) - b[key] / len(right)) for key in keys)


def exact_projection(text: str, schema: str):
    payload = json.loads(text.strip())
    require(isinstance(payload, dict) and set(payload) == {"action", "next_goal"}, "projection must contain exactly action and next_goal")
    action = payload["action"]
    require(isinstance(action, list) and len(action) == 1, "projection must contain exactly one action")
    validate_action_object(action[0], schema)
    goal = payload["next_goal"]
    require(isinstance(goal, str) and len(goal.split()) <= 20, "next_goal exceeds 20 words or is not text")
    canonical = json.dumps(action[0], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return payload, canonical


def call_artifact(response, text: str) -> dict:
    return {
        "requested_model": response.get("requested_model"),
        "resolved_model": response.get("resolved_model"),
        "thinking_compatibility_fallback": response.get("thinking_compatibility_fallback"),
        "response_id": response.get("response_id"),
        "provider_status": response.get("status"),
        "raw_output": text,
        "raw_output_sha256": sha256_text(text),
        "usage": response.get("usage") or {},
        "completed_at": now(),
    }


def qualify_schema() -> int:
    require(git("status", "--porcelain") == "", "qualification worktree must be clean and committed")
    manifest = load(QUAL_RUN / "manifest.json")
    fixtures = load(QUAL_RUN / "fixtures.json")
    prompts = load(QUAL_RUN / "projector-prompts.json")
    schema_artifact = load(QUAL_RUN / "action-schema.json")
    schema = schema_artifact["projector_schema_canonical_json"]
    require(schema == canonical_schema(), "qualification schema drift")
    require(fixtures["scientific_state_used"] is False and len(fixtures["fixtures"]) == 20, "fixture geometry drift")
    manifest.update({
        "status": "NON_SCIENTIFIC_SCHEMA_QUALIFICATION_RUNNING",
        "execution_git_sha": git("rev-parse", "HEAD"),
        "started_at": now(),
    })
    dump(QUAL_RUN / "manifest.json", manifest)

    client, provider_summary = v1.client()
    dump(QUAL_RUN / "provider-summary.json", provider_summary)
    failures = []
    for fixture in fixtures["fixtures"]:
        for rendering in ("P0", "P1"):
            path = QUAL_RUN / "per_fixture" / f"{fixture['fixture_id']}__{rendering}.json"
            prompt = v1.expand_projection(
                prompts[rendering]["template"],
                fixture["memory"],
                fixture["task"],
                fixture["state"],
                schema,
            )
            if path.exists():
                artifact = load(path)
                require(artifact["prompt_sha256"] == sha256_text(prompt), f"qualification resume drift {fixture['fixture_id']}/{rendering}")
            else:
                response, text = v1.provider_call(client, prompt, 300, 0.0)
                artifact = {
                    "schema_version": "1.0",
                    "artifact_kind": "C1_PACTA_V11_NON_SCIENTIFIC_SCHEMA_FIXTURE",
                    "status": "FAIL",
                    "fixture_id": fixture["fixture_id"],
                    "rendering": rendering,
                    "non_scientific": True,
                    "prompt_sha256": sha256_text(prompt),
                    "prompt_template_sha256": prompts[rendering]["template_sha256"],
                    "action_schema_sha256": sha256_text(schema),
                    **call_artifact(response, text),
                }
                try:
                    parsed, canonical = exact_projection(text, schema)
                    artifact.update({"status": "PASS", "parsed": parsed, "canonical_action": canonical})
                except Exception as exc:
                    artifact.update({"failure_type": type(exc).__name__, "failure": str(exc)[:1600]})
                dump(path, artifact)
            if artifact["status"] != "PASS":
                failures.append({"fixture_id": fixture["fixture_id"], "rendering": rendering, "failure": artifact.get("failure")})
        completed = len(list((QUAL_RUN / "per_fixture").glob("*.json")))
        dump(QUAL_RUN / "progress.json", {"status": "RUNNING", "completed": completed, "expected": 40, "updated_at": now()})

    artifacts = [load(path) for path in sorted((QUAL_RUN / "per_fixture").glob("*.json"))]
    passed = (
        len(artifacts) == 40
        and not failures
        and all(row["status"] == "PASS" for row in artifacts)
        and all(row["requested_model"] == MODEL and row["resolved_model"] == RESOLVED for row in artifacts)
        and all(row["thinking_compatibility_fallback"] is False for row in artifacts)
    )
    result = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_SCHEMA_QUALIFICATION",
        "status": "SCHEMA_QUALIFICATION_PASS" if passed else "STOP_SCHEMA_QUALIFICATION",
        "scientific_state_used": False,
        "fixtures": 20,
        "calls": len(artifacts),
        "exact_schema_pass": sum(row["status"] == "PASS" for row in artifacts),
        "model_drift": sum(row["requested_model"] != MODEL or row["resolved_model"] != RESOLVED for row in artifacts),
        "thinking_fallback": sum(row["thinking_compatibility_fallback"] is not False for row in artifacts),
        "failures": failures,
        "action_schema_sha256": sha256_text(schema),
        "execution_git_sha": git("rev-parse", "HEAD"),
        "completed_at": now(),
    }
    dump(QUAL_RUN / "schema-qualification.json", result)
    manifest.update({"status": result["status"], "completed_at": result["completed_at"], "result_sha256": shaf(QUAL_RUN / "schema-qualification.json")})
    dump(QUAL_RUN / "manifest.json", manifest)
    dump(QUAL_RUN / "progress.json", {"status": result["status"], "completed": len(artifacts), "expected": 40, "updated_at": now()})
    print(json.dumps(result))
    return 0 if passed else 2


def materialize_states():
    b10 = load(B10)
    split = load(PILOT_RUN / "split.json")
    units = split["pilot"]
    sys.path.insert(0, str(b10["vendor_path"]))
    import pyarrow.parquet as pq

    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    require(shaf(parquet) == b10["source_bindings"]["parquet"]["sha256"], "parquet drift")
    table = {int(row["task_id"]): row for row in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()}
    schema = canonical_schema()
    states = {}
    for unit in units:
        task_id = int(unit["future_task"])
        row = table[task_id]
        task = str(row["task_prompt"])
        require(sha256_text(task) == unit["task_prompt_sha256"], f"task drift {task_id}")
        trajectory = json.loads(str(row["trajectory_json"]))
        step = (trajectory.get("steps") or {}).get("1")
        contents = ((step.get("input_messages") or {}).get("contents") or [])
        system = str(contents[0].get("content") or "")
        last = str(contents[-1].get("content") or "")
        marker = "[Current state starts here]"
        require(marker in last, f"current state marker absent {task_id}")
        state = last.split(marker, 1)[1].strip()
        require(sha256_text(system) == unit["system_instruction_sha256"], f"system drift {task_id}")
        require(sha256_text(state) == unit["current_state_sha256"], f"state drift {task_id}")
        extracted = extract_minimal_action_schema(system)
        require(extracted == schema and sha256_text(extracted) == unit["action_schema_sha256"], f"action schema drift {task_id}")
        memory = {}
        for branch in BRANCHES:
            path = Path(unit[f"{branch}_memory_wrapper_path"])
            require(path.is_file() and shaf(path) == unit[f"{branch}_memory_wrapper_sha256"], f"memory drift {task_id}/{branch}")
            memory[branch] = path.read_text(encoding="utf-8")
        states[task_id] = {"unit": unit, "system": system, "action_schema": extracted, "task": task, "state": state, "memory": memory}
    return states


def execute_projections(client, states, prompts):
    geometry = {}
    failures = []
    for task_id, state in states.items():
        outputs = {}
        for branch in BRANCHES:
            outputs[branch] = {}
            for rendering in ("P0", "P1"):
                short = "S" if branch == "success" else "F"
                path = PILOT_RUN / "projection" / f"task-{task_id}__branch-{short}__{rendering}.json"
                prompt = v1.expand_projection(
                    prompts[rendering]["template"],
                    state["memory"][branch],
                    state["task"],
                    state["state"],
                    state["action_schema"],
                )
                if path.exists():
                    artifact = load(path)
                    require(artifact["prompt_sha256"] == sha256_text(prompt), f"projection resume drift {task_id}/{branch}/{rendering}")
                else:
                    response, text = v1.provider_call(client, prompt, 300, 0.0)
                    artifact = {
                        "schema_version": "1.0",
                        "artifact_kind": "C1_PACTA_V11_PROJECTION",
                        "status": "projection_parse_or_realization_failure",
                        "future_task": task_id,
                        "branch": branch,
                        "rendering": rendering,
                        "prompt_sha256": sha256_text(prompt),
                        "prompt_template_sha256": prompts[rendering]["template_sha256"],
                        "memory_sha256": sha256_text(state["memory"][branch]),
                        "task_sha256": sha256_text(state["task"]),
                        "state_sha256": sha256_text(state["state"]),
                        "system_instruction_sha256": sha256_text(state["system"]),
                        "action_schema_sha256": sha256_text(state["action_schema"]),
                        **call_artifact(response, text),
                    }
                    try:
                        parsed, canonical = exact_projection(text, state["action_schema"])
                        artifact.update({
                            "status": "complete",
                            "parsed": parsed,
                            "parsed_action": parsed["action"][0],
                            "canonical_action": canonical,
                            "next_goal": parsed["next_goal"],
                        })
                    except Exception as exc:
                        artifact.update({"failure_type": type(exc).__name__, "failure": str(exc)[:1600]})
                    dump(path, artifact)
                outputs[branch][rendering] = artifact
        good = all(outputs[branch][rendering].get("status") == "complete" for branch in BRANCHES for rendering in ("P0", "P1"))
        stable_s = good and outputs["success"]["P0"]["canonical_action"] == outputs["success"]["P1"]["canonical_action"]
        stable_f = good and outputs["failure"]["P0"]["canonical_action"] == outputs["failure"]["P1"]["canonical_action"]
        contrast = good and outputs["success"]["P0"]["canonical_action"] != outputs["failure"]["P0"]["canonical_action"]
        if not good:
            failures.append(task_id)
        geometry[task_id] = {
            "future_task": task_id,
            "projection_complete": good,
            "stableS": bool(stable_s),
            "stableF": bool(stable_f),
            "contrast": bool(contrast),
            "G": bool(stable_s and stable_f and contrast),
            "z0S": outputs["success"]["P0"].get("canonical_action"),
            "z1S": outputs["success"]["P1"].get("canonical_action"),
            "z0F": outputs["failure"]["P0"].get("canonical_action"),
            "z1F": outputs["failure"]["P1"].get("canonical_action"),
        }
        completed = len(list((PILOT_RUN / "projection").glob("*.json")))
        dump(PILOT_RUN / "progress.json", {"status": "PROJECTING", "projection_completed": completed, "projection_expected": 28, "updated_at": now()})
    dump(PILOT_RUN / "projection-geometry.json", {
        "status": "COMPLETE",
        "states": list(geometry.values()),
        "failure_states": failures,
        "completed_at": now(),
    })
    return geometry, failures


def execute_scb(client, states, contract):
    instruction = contract["unchanged"]["scb_baseline"]["instruction"]
    notes = {}
    for task_id, state in states.items():
        notes[task_id] = {}
        for branch in BRANCHES:
            path = PILOT_RUN / "scb" / f"task-{task_id}__branch-{branch}.json"
            prompt = v1.scb_prompt(instruction, state["memory"][branch], state["task"], state["state"])
            if path.exists():
                artifact = load(path)
                require(artifact["status"] == "complete" and artifact["prompt_sha256"] == sha256_text(prompt), f"SCB resume drift {task_id}/{branch}")
            else:
                response, text = v1.provider_call(client, prompt, 180, 0.0)
                artifact = {
                    "schema_version": "1.0",
                    "artifact_kind": "C1_PACTA_V11_R9_SCB_BASELINE",
                    "status": "complete",
                    "future_task": task_id,
                    "branch": branch,
                    "prompt_sha256": sha256_text(prompt),
                    "memory_sha256": sha256_text(state["memory"][branch]),
                    "text": text.strip(),
                    "text_sha256": sha256_text(text.strip()),
                    "word_count": len(text.split()),
                    **call_artifact(response, text),
                }
                dump(path, artifact)
            notes[task_id][branch] = artifact["text"]
    return notes


def structured_note(task_id: int, branch: str):
    short = "S" if branch == "success" else "F"
    artifact = load(PILOT_RUN / "projection" / f"task-{task_id}__branch-{short}__P0.json")
    require(artifact["status"] == "complete", f"missing structured projection {task_id}/{branch}")
    return json.dumps(artifact["parsed"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def freeze_policy_schedule(states, geometry, notes):
    rows = []
    for task_id, state in states.items():
        unit = state["unit"]
        for arm in ARMS:
            for branch in BRANCHES:
                projection = structured_note(task_id, branch)
                if arm == "A0_NATIVE":
                    note, structured = None, False
                elif arm == "A1_SCB":
                    note, structured = notes[task_id][branch], False
                elif arm == "A2_SAP_ALWAYS":
                    note, structured = projection, True
                else:
                    note = projection if geometry[task_id]["G"] else None
                    structured = note is not None
                prompt = v1.policy_prompt(
                    state["system"],
                    state["task"],
                    state["state"],
                    state["memory"][branch],
                    note,
                    structured,
                )
                for rollout in range(1, REPS + 1):
                    case_id = f"task-{task_id}__{arm}__{branch}_memory__r{rollout}"
                    rows.append({
                        "case_id": case_id,
                        "phase": "pilot",
                        "future_task": task_id,
                        "intent_template_id": unit["intent_template_id"],
                        "selected_source_task": unit["selected_source_task"],
                        "arm": arm,
                        "branch": branch,
                        "rollout": rollout,
                        "gate_open": geometry[task_id]["G"],
                        "used_structured_projection": structured,
                        "used_scb_note": arm == "A1_SCB",
                        "prompt": prompt,
                        "prompt_sha256": sha256_text(prompt),
                        "memory_sha256": sha256_text(state["memory"][branch]),
                        "support_sha256": "" if note is None else sha256_text(note),
                    })
    rows.sort(key=lambda row: sha256_text(f"C1-PACTA-V11-PILOT-POLICY-SCHEDULE-v1|{row['case_id']}"))
    for order, row in enumerate(rows, 1):
        row["order"] = order
    require(len(rows) == 336, "policy geometry drift")
    schedule = PILOT_RUN / "policy-schedule.jsonl"
    if schedule.exists():
        existing = [json.loads(line) for line in schedule.read_text(encoding="utf-8").splitlines() if line.strip()]
        require([row["prompt_sha256"] for row in existing] == [row["prompt_sha256"] for row in rows], "policy schedule drift")
    else:
        write_jsonl(schedule, rows)
    dump(PILOT_RUN / "policy-input-manifest.json", {
        "status": "FROZEN_BEFORE_POLICY_OUTPUT",
        "cases": len(rows),
        "schedule_sha256": shaf(schedule),
        "created_at": now(),
    })
    return rows


def execute_policy(client, rows):
    for row in rows:
        path = PILOT_RUN / "per_case" / f"{row['case_id']}.json"
        if path.exists():
            artifact = load(path)
            require(artifact["status"] == "complete" and artifact["prompt_sha256"] == row["prompt_sha256"], f"policy resume drift {row['case_id']}")
            continue
        try:
            response, text = v1.provider_call(client, row["prompt"], 900, 0.2)
            signature, goal, recovered = v1.parse_policy_output(text)
            artifact = {key: value for key, value in row.items() if key != "prompt"}
            artifact.update({
                "schema_version": "1.0",
                "artifact_kind": "C1_PACTA_V11_POLICY_RESPONSE",
                "status": "complete",
                **call_artifact(response, text),
                "raw_response": text,
                "raw_response_sha256": sha256_text(text),
                "action_signature": signature,
                "next_goal_sha256": sha256_text(goal) if goal else "",
                "parse_recovered": recovered,
            })
            artifact.pop("raw_output", None)
            artifact.pop("raw_output_sha256", None)
            dump(path, artifact)
        except Exception as exc:
            artifact = {key: value for key, value in row.items() if key != "prompt"}
            artifact.update({"status": "failed", "failure_type": type(exc).__name__, "failure": str(exc)[:2000], "completed_at": now()})
            dump(path, artifact)
            dump(PILOT_RUN / "progress.json", {
                "status": "STOP_ON_FIRST_POLICY_FAILURE",
                "completed": len(list((PILOT_RUN / "per_case").glob("*.json"))),
                "expected": 336,
                "failure": artifact,
                "updated_at": now(),
            })
            raise
        completed = len(list((PILOT_RUN / "per_case").glob("*.json")))
        if completed % 6 == 0:
            dump(PILOT_RUN / "progress.json", {"status": "POLICY_RUNNING", "completed": completed, "expected": 336, "updated_at": now()})
    cases = [load(path) for path in sorted((PILOT_RUN / "per_case").glob("*.json"))]
    require(len(cases) == 336 and all(case["status"] == "complete" for case in cases), "policy cases incomplete")
    dump(PILOT_RUN / "progress.json", {"status": "POLICY_COMPLETE", "completed": 336, "expected": 336, "updated_at": now()})
    return cases


def analyze(states, geometry, projection_failures, cases):
    per_state = []
    for task_id, state in states.items():
        row = {
            "future_task": task_id,
            "intent_template_id": state["unit"]["intent_template_id"],
            "selected_source_task": state["unit"]["selected_source_task"],
            "G": geometry[task_id]["G"],
            "stableS": geometry[task_id]["stableS"],
            "stableF": geometry[task_id]["stableF"],
            "contrast": geometry[task_id]["contrast"],
            "projection_complete": geometry[task_id]["projection_complete"],
        }
        for arm in ARMS:
            success = [case["action_signature"] for case in cases if case["future_task"] == task_id and case["arm"] == arm and case["branch"] == "success"]
            failure = [case["action_signature"] for case in cases if case["future_task"] == task_id and case["arm"] == arm and case["branch"] == "failure"]
            require(len(success) == REPS and len(failure) == REPS, f"replicate count drift {task_id}/{arm}")
            row[f"U_{arm}"] = tv(success, failure)
        row["D_gate"] = row["U_A3_PACTA"] - row["U_A2_SAP_ALWAYS"]
        row["A3_minus_A1"] = row["U_A3_PACTA"] - row["U_A1_SCB"]
        row["A2_minus_A1"] = row["U_A2_SAP_ALWAYS"] - row["U_A1_SCB"]
        row["A2_minus_A0"] = row["U_A2_SAP_ALWAYS"] - row["U_A0_NATIVE"]
        row["A3_minus_A0"] = row["U_A3_PACTA"] - row["U_A0_NATIVE"]
        per_state.append(row)

    means = {f"mean_U_{arm}": sum(row[f"U_{arm}"] for row in per_state) / len(per_state) for arm in ARMS}
    for contrast in ("D_gate", "A3_minus_A1", "A2_minus_A1", "A2_minus_A0", "A3_minus_A0"):
        means[f"mean_{contrast}"] = sum(row[contrast] for row in per_state) / len(per_state)
    open_rows = [row for row in per_state if row["G"]]
    open_count = len(open_rows)
    mean_open = sum(row["D_gate"] for row in open_rows) / open_count if open_count else None
    positive_open = sum(row["D_gate"] > 0 for row in open_rows)
    projection_artifacts = [load(path) for path in sorted((PILOT_RUN / "projection").glob("*.json"))]
    scb_artifacts = [load(path) for path in sorted((PILOT_RUN / "scb").glob("*.json"))]
    model_drift = sum(
        row.get("requested_model") != MODEL or row.get("resolved_model") != RESOLVED
        for row in projection_artifacts + scb_artifacts + cases
    )
    checks = {
        "projection_exact_schema_28_of_28": len(projection_artifacts) == 28 and not projection_failures and all(row["status"] == "complete" for row in projection_artifacts),
        "model_drift_zero": model_drift == 0,
        "packet_drift_zero": len(states) == 7,
        "gate_non_degenerate_2_to_6": 2 <= open_count <= 6,
        "gate_open_mean_D_gate_ge_0_05": mean_open is not None and mean_open >= 0.05,
        "gate_open_positive_fraction_ge_half": open_count > 0 and positive_open / open_count >= 0.5,
        "mean_A3_minus_A0_gt_zero": means["mean_A3_minus_A0"] > 0,
    }
    passed = all(checks.values())
    if not checks["gate_non_degenerate_2_to_6"]:
        status = "HOLD_GATE_DEGENERATE"
    elif passed:
        status = "PACTA_V11_PRELIMINARY_MECHANISM_SIGNAL"
    else:
        status = "PACTA_V11_PILOT_HOLD_OR_STOP"

    with (PILOT_RUN / "pilot-per-state.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_state[0]))
        writer.writeheader()
        writer.writerows(per_state)
    analysis = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_PILOT_ANALYSIS",
        "status": status,
        "execution": {
            "states": 7,
            "templates": 7,
            "projection_calls": len(projection_artifacts),
            "scb_calls": len(scb_artifacts),
            "policy_calls": len(cases),
            "model_drift": model_drift,
            "packet_drift": 0,
            "policy_parse_recovered": sum(bool(case.get("parse_recovered")) for case in cases),
            "confirmatory_executed": False,
            "terminal_executed": False,
        },
        "gate_geometry": {
            "open_count": open_count,
            "closed_count": 7 - open_count,
            "open_ids": [row["future_task"] for row in open_rows],
            "closed_ids": [row["future_task"] for row in per_state if not row["G"]],
            "mean_D_gate_open": mean_open,
            "positive_D_gate_open": positive_open,
            "positive_fraction_D_gate_open": positive_open / open_count if open_count else None,
        },
        "effect_summary": means,
        "primary": {
            "contrast": "A3_PACTA - A2_SAP_ALWAYS",
            "mean_D_gate_all_states": means["mean_D_gate"],
            "mean_D_gate_open_states": mean_open,
        },
        "secondary": {
            "mean_A3_minus_A0": means["mean_A3_minus_A0"],
            "mean_A3_minus_A1": means["mean_A3_minus_A1"],
            "mean_A2_minus_A1": means["mean_A2_minus_A1"],
            "mean_A2_minus_A0": means["mean_A2_minus_A0"],
        },
        "gate": {"checks": checks, "pass": passed, "thresholds_unchanged": True},
        "heterogeneity": per_state,
        "claim_boundary": "Seven-template Pilot is proof-of-concept only. It cannot authorize R10, terminal utility, or same-substrate confirmatory execution.",
    }
    dump(PILOT_RUN / "pilot-analysis.json", analysis)
    return analysis


def failure_differential(analysis):
    means = analysis["effect_summary"]
    gate_open = analysis["gate_geometry"]["open_count"]
    a2_gain = means["mean_A2_minus_A0"]
    a3_gain = means["mean_A3_minus_A0"]
    d_gate = analysis["primary"]["mean_D_gate_open_states"]
    if gate_open in (0, 1, 7):
        mechanism = "not_qualified_gate_degenerate"
    elif d_gate is not None and d_gate <= 0:
        mechanism = "not_supported_A3_not_better_than_A2"
    elif a2_gain > 0 and a3_gain > 0 and abs(means["mean_D_gate"]) < 1e-12:
        mechanism = "structured_action_projection_signal_without_gate_increment"
    elif analysis["gate"]["pass"]:
        mechanism = "preliminary_pilot_signal_only"
    else:
        mechanism = "unresolved_or_insufficient"
    result = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FAILURE_DIFFERENTIAL",
        "scientific_pass": analysis["gate"]["pass"],
        "layers": {
            "execution": False,
            "provider": False,
            "schema_qualification": False,
            "projection_schema": not analysis["gate"]["checks"]["projection_exact_schema_28_of_28"],
            "projection_instability_states": sum(not (row["stableS"] and row["stableF"]) for row in analysis["heterogeneity"]),
            "gate_degeneracy": not analysis["gate"]["checks"]["gate_non_degenerate_2_to_6"],
            "measurement": False,
            "generic_action_projection": "positive" if a2_gain > 0 else ("negative" if a2_gain < 0 else "no_aggregate_gain"),
            "counterfactual_gate_mechanism": mechanism,
            "terminal_utility": "not_tested",
        },
        "comparisons": {
            "mean_A2_minus_A0": a2_gain,
            "mean_A3_minus_A0": a3_gain,
            "mean_D_gate_all_states": means["mean_D_gate"],
            "mean_D_gate_open_states": d_gate,
        },
        "strongest_competing_explanation": (
            "Any common A2/A3 gain with negligible A3-A2 increment is attributable to structured action projection rather than the counterfactual transport gate."
        ),
    }
    dump(PILOT_RUN / "pilot-failure-differential.json", result)
    return result


def write_prepolicy_stop(status: str, states, geometry, projection_failures, execution_sha: str):
    open_ids = [task_id for task_id, row in geometry.items() if row["G"]]
    projection_artifacts = [load(path) for path in sorted((PILOT_RUN / "projection").glob("*.json"))]
    analysis = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_PILOT_ANALYSIS",
        "status": status,
        "execution": {
            "states": 7,
            "projection_calls": len(projection_artifacts),
            "scb_calls": 0,
            "policy_calls": 0,
            "confirmatory_executed": False,
            "terminal_executed": False,
        },
        "gate_geometry": {
            "open_count": len(open_ids),
            "closed_count": 7 - len(open_ids),
            "open_ids": open_ids,
            "closed_ids": [task_id for task_id in states if task_id not in open_ids],
        },
        "projection_failure_states": projection_failures,
        "effect_summary": {
            "mean_U_A0_NATIVE": None,
            "mean_U_A1_SCB": None,
            "mean_U_A2_SAP_ALWAYS": None,
            "mean_U_A3_PACTA": None,
            "mean_D_gate": None,
            "reason": "Policy geometry was not started after an irreversible frozen realization or gate-geometry failure.",
        },
        "gate": {"pass": False, "thresholds_unchanged": True},
        "heterogeneity": list(geometry.values()),
        "claim_boundary": "Operationalization/gate-realization stop before a qualified policy comparison; no PACTA mechanism update.",
    }
    dump(PILOT_RUN / "pilot-analysis.json", analysis)
    dump(PILOT_RUN / "pilot-failure-differential.json", {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FAILURE_DIFFERENTIAL",
        "scientific_pass": False,
        "layers": {
            "execution": False,
            "provider": False,
            "schema_qualification": False,
            "projection_schema": bool(projection_failures),
            "projection_instability_states": sum(not (row["stableS"] and row["stableF"]) for row in geometry.values()),
            "gate_degeneracy": not (2 <= len(open_ids) <= 6),
            "measurement": False,
            "generic_action_projection": "not_tested",
            "counterfactual_gate_mechanism": "not_qualified",
            "terminal_utility": "not_tested",
        },
    })
    final = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FINAL_VERDICT",
        "status": status,
        "method_claim_status": "PACTA_V11_NOT_QUALIFIED",
        "active_manuscript": "R9",
        "confirmatory_executed": False,
        "terminal_executed": False,
        "execution_git_sha": execution_sha,
        "completed_at": now(),
    }
    dump(PILOT_RUN / "final-verdict.json", final)
    return final


def run_pilot() -> int:
    require(git("status", "--porcelain") == "", "pilot worktree must be clean and committed")
    qualification = load(QUAL_RUN / "schema-qualification.json")
    require(
        qualification["status"] == "SCHEMA_QUALIFICATION_PASS"
        and qualification["calls"] == 40
        and qualification["exact_schema_pass"] == 40
        and qualification["model_drift"] == 0
        and qualification["thinking_fallback"] == 0,
        "schema qualification did not pass 40/40",
    )
    execution_sha = git("rev-parse", "HEAD")
    require(qualification["execution_git_sha"] == execution_sha, "design commit differs between qualification and pilot")

    lock_path = PILOT_RUN / ".execution.lock"
    lock = lock_path.open("a+")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = load(PILOT_RUN / "manifest.json")
    manifest.update({
        "status": "SCIENTIFIC_PILOT_RUNNING",
        "schema_qualification_sha256": shaf(QUAL_RUN / "schema-qualification.json"),
        "execution_git_sha": execution_sha,
        "origin_main_sha_at_execution": git("rev-parse", "origin/main"),
        "started_at": now(),
    })
    dump(PILOT_RUN / "manifest.json", manifest)

    client, provider_summary = v1.client()
    dump(PILOT_RUN / "provider-summary.json", provider_summary)
    states = materialize_states()
    prompts = load(PILOT_RUN / "projector-prompts.json")
    contract = load(PILOT_RUN / "contract.json")
    geometry, projection_failures = execute_projections(client, states, prompts)
    projection_artifacts = [load(path) for path in sorted((PILOT_RUN / "projection").glob("*.json"))]
    projection_drift = sum(
        row.get("requested_model") != MODEL
        or row.get("resolved_model") != RESOLVED
        or row.get("thinking_compatibility_fallback") is not False
        for row in projection_artifacts
    )
    if len(projection_artifacts) != 28 or projection_failures or projection_drift:
        final = write_prepolicy_stop("STOP_PROJECTION_REALIZATION", states, geometry, projection_failures, execution_sha)
        manifest.update({"status": final["status"], "completed_at": final["completed_at"]})
        dump(PILOT_RUN / "manifest.json", manifest)
        print(json.dumps(final))
        return 0

    gate_open = sum(row["G"] for row in geometry.values())
    if not 2 <= gate_open <= 6:
        final = write_prepolicy_stop("HOLD_GATE_DEGENERATE", states, geometry, projection_failures, execution_sha)
        manifest.update({"status": final["status"], "completed_at": final["completed_at"]})
        dump(PILOT_RUN / "manifest.json", manifest)
        print(json.dumps(final))
        return 0

    notes = execute_scb(client, states, contract)
    schedule = freeze_policy_schedule(states, geometry, notes)
    cases = execute_policy(client, schedule)
    analysis = analyze(states, geometry, projection_failures, cases)
    differential = failure_differential(analysis)
    if analysis["gate"]["pass"]:
        status = "PACTA_V11_PRELIMINARY_MECHANISM_SIGNAL_STOP_FOR_INDEPENDENT_CARRIER"
        method_status = "PRELIMINARY_PILOT_SIGNAL_NOT_CONFIRMED"
    else:
        status = "PACTA_V11_PILOT_HOLD_OR_STOP"
        method_status = "PACTA_V11_NOT_QUALIFIED"
    final = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FINAL_VERDICT",
        "status": status,
        "method_claim_status": method_status,
        "active_manuscript": "R9",
        "R10_authorized": False,
        "confirmatory_executed": False,
        "same_substrate_confirmatory_forbidden": True,
        "terminal_executed": False,
        "terminal_locked": True,
        "execution_git_sha": execution_sha,
        "pilot_analysis_sha256": shaf(PILOT_RUN / "pilot-analysis.json"),
        "failure_differential_sha256": shaf(PILOT_RUN / "pilot-failure-differential.json"),
        "completed_at": now(),
    }
    dump(PILOT_RUN / "final-verdict.json", final)
    manifest.update({"status": status, "completed_at": final["completed_at"], "pilot_analysis_sha256": final["pilot_analysis_sha256"]})
    dump(PILOT_RUN / "manifest.json", manifest)
    print(json.dumps({
        "status": status,
        "pilot_gate_pass": analysis["gate"]["pass"],
        "gate_geometry": analysis["gate_geometry"],
        "effects": analysis["effect_summary"],
        "counterfactual_gate_mechanism": differential["layers"]["counterfactual_gate_mechanism"],
        "confirmatory": "NOT_EXECUTED",
        "terminal": "NOT_EXECUTED",
    }))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("qualify-schema", "pilot"))
    args = parser.parse_args()
    if args.phase == "qualify-schema":
        return qualify_schema()
    return run_pilot()


if __name__ == "__main__":
    raise SystemExit(main())
