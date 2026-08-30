from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R9_FREEZE = HERE / "c1-scmb-pilot-freeze-20260829.json"
R9_CONTRACT = HERE / "c1-scmb-pilot-contract-20260829.json"
R9_CLOSURE = HERE / "c1-scmb-pilot-closure-20260829.json"
NOVELTY = HERE / "c1-cast-novelty-audit-20260830.json"
B10 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
R9_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1")
PILOT_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1")
CONFIRM_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-c1-20260830-confirmatory-v1")
EXPECTED_19 = [510, 24, 166, 656, 351, 96, 117, 191, 273, 332, 263, 368, 512, 300, 439, 240, 793, 376, 313]
SPLIT_SALT = "C1-CAST-SPLIT-v1"
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"


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


P0_INSTRUCTION = (
    "Given the reusable memory, ultimate task, exact current browser state, and action schema, "
    "return the single immediate structured action that the memory most directly supports now. "
    "Use the memory only when it is relevant to this state. Do not invent unavailable facts."
)
P1_INSTRUCTION = (
    "Determine the one immediate structured browser action implied by the reusable memory for "
    "this exact task and state under the supplied action schema. Ignore guidance that is not "
    "currently applicable. Do not assume facts absent from the state."
)
SHARED_SUFFIX = """Return exactly one JSON object with this shape and no prose:
{
  "action": [
    {
      "<tool_name>": {
        "<argument>": "<value>"
      }
    }
  ],
  "next_goal": "<=20 words"
}

REUSABLE MEMORY:
{memory}

ULTIMATE TASK:
{task}

CURRENT BROWSER STATE:
{state}

ACTION SCHEMA:
{action_schema}
"""


def projector_template(instruction: str) -> str:
    return instruction + "\n\n" + SHARED_SUFFIX


def main() -> int:
    audit = load(NOVELTY)
    require(audit["verdict"] == "PASS_NOVEL_RESIDUAL", "novelty residual did not pass")
    require(audit["name_verdict"] == "RENAME_CAST_TO_PACTA", "name collision resolution missing")
    r9f, r9c, r9close, b10 = load(R9_FREEZE), load(R9_CONTRACT), load(R9_CLOSURE), load(B10)
    units = list(r9f["selection"]["template_holdout"])
    ids = [int(u["future_task"]) for u in units]
    require(set(ids) == set(EXPECTED_19) and len(ids) == 19, "R9 holdout identity drift")
    require(r9close["execution"]["fresh_19_holdout_calls"] == 0, "R9 closure reports holdout calls")
    observed = []
    if R9_RUN.exists():
        for p in R9_RUN.rglob("*.json"):
            name = p.name
            for tid in EXPECTED_19:
                if f"task-{tid}__" in name:
                    observed.append(str(p))
    require(not observed, f"R9 holdout outcome files found: {observed[:3]}")

    for u in units:
        u["cast_split_hash"] = shat(f"{SPLIT_SALT}|{u['intent_template_id']}|{u['future_task']}")
    ordered = sorted(units, key=lambda u: u["cast_split_hash"])
    pilot = ordered[:6]
    confirm = ordered[6:]
    require([u["future_task"] for u in pilot] == [313, 376, 368, 512, 300, 191], "pilot split drift")
    require([u["future_task"] for u in confirm] == [510, 117, 24, 332, 656, 240, 166, 263, 273, 793, 351, 96, 439], "confirmatory split drift")

    prompts = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_PROJECTOR_PROMPTS",
        "status": "FROZEN_BEFORE_PROJECTOR_OR_POLICY_OUTPUT",
        "method": {"name": "PACTA", "expansion": "Paired Action-Contrast Transport Authority", "development_label": "CAST"},
        "model": {"requested": MODEL, "expected_resolved": RESOLVED, "temperature": 0.0, "thinking": "disabled", "retries": 0, "substitution": False},
        "input_fields": ["REUSABLE MEMORY", "ULTIMATE TASK", "CURRENT BROWSER STATE", "ACTION SCHEMA"],
        "output_observable": "canonicalized action[0] only; next_goal and rationale are excluded from the gate",
        "P0": {"instruction": P0_INSTRUCTION, "template": projector_template(P0_INSTRUCTION), "template_sha256": shat(projector_template(P0_INSTRUCTION))},
        "P1": {"instruction": P1_INSTRUCTION, "template": projector_template(P1_INSTRUCTION), "template_sha256": shat(projector_template(P1_INSTRUCTION))},
    }
    split = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_OUTCOME_BLIND_SPLIT",
        "status": "PILOT_6_CONFIRMATORY_13_FROZEN_BEFORE_ANY_PACTA_OUTPUT",
        "salt": SPLIT_SALT,
        "hash_rule": 'SHA256("C1-CAST-SPLIT-v1" | intent_template_id | future_task), with literal | delimiters',
        "source_holdout": EXPECTED_19,
        "pilot": pilot,
        "confirmatory": confirm,
        "outcome_accessed": False,
    }
    amendment = {
        "schema_version": "1.0",
        "artifact_kind": "C1_CAST_HOLDOUT_REALLOCATION_AMENDMENT",
        "method_frozen_name": "PACTA",
        "status": "AUTHORIZED_REALLOCATION_OF_ZERO-OUTCOME_STATES",
        "historical_object": "SCMB confirmatory",
        "historical_status": "closed after the R9 pilot failed its cross-state consistency gate",
        "new_object": "mechanistically distinct PACTA prospective pilot and sealed confirmatory",
        "state_count": 19,
        "state_ids": EXPECTED_19,
        "verified_new_scmb_policy_outcomes": 0,
        "prohibitions": ["do not modify R9", "do not call these states SCMB confirmatory", "do not use PACTA pilot outcomes to change the sealed confirmatory design"],
        "authorized_at": now(),
    }
    contract = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_FROZEN_CONTRACT",
        "paper_id": r9c["paper_id"],
        "experiment_id": "C1-PACTA-FRESH-UPTAKE-20260830",
        "status": "FROZEN_BEFORE_PROVIDER_SUPPORT_AND_SCIENTIFIC_CALLS",
        "story_boundary": "persistent memory difference obtains behavioral authority only after write, native exposure, and first-action uptake are separated; localization is post-exposure/pre-uptake and is not causal mediation",
        "adaptation_gap": "state relevance does not imply that a feedback-induced memory difference is action-discriminative in the current state",
        "method": {
            "name": "PACTA",
            "expansion": "Paired Action-Contrast Transport Authority",
            "development_label": "CAST",
            "components": ["state-action projection", "same-trajectory outcome-flipped shadow twin", "Stable Counterfactual Action-Contrast Gate"],
            "gate": "stableS AND stableF AND canonical(P0_success) != canonical(P0_failure)",
            "closed_behavior": "raw factual/native memory only; memory is not suppressed",
            "open_behavior": "raw factual memory plus the factual P0 structured action implication",
            "canonicalization": 'json.dumps(action[0], sort_keys=True, separators=(",", ":"), ensure_ascii=False)',
        },
        "arms": {
            "A0_NATIVE": "raw retrieved memory only with the native policy prompt",
            "A1_SCB": "exact R9 state-conditioned binder instruction and implementation family",
            "A2_SAP_ALWAYS": "raw memory plus factual P0 structured action implication whenever P0 parses; otherwise native fallback",
            "A3_PACTA": "identical to A2 when the frozen stable counterfactual action-contrast gate opens; otherwise identical to A0",
        },
        "scb_baseline": {
            "instruction": r9c["binder"]["A2_instruction"],
            "model": r9c["binder"]["model"],
            "expected_resolved": r9c["binder"]["expected_resolved"],
            "temperature": r9c["binder"]["temperature"],
            "max_output_tokens": r9c["binder"]["max_output_tokens"],
            "thinking": r9c["binder"]["thinking"],
            "retries": r9c["binder"]["retries"],
        },
        "projector": prompts["model"],
        "policy": {"requested": MODEL, "expected_resolved": RESOLVED, "temperature": 0.2, "max_output_tokens": 900, "thinking": "disabled", "retries": 0, "substitution": False, "rollouts_per_branch_arm_state": 6},
        "observable": {
            "U": "empirical TV between success-memory and failure-memory frozen-B10 first-action signature distributions within state and arm",
            "B10_contract_path": str(B10),
            "B10_contract_sha256": shaf(B10),
            "B10_runner_sha256": b10["code"]["runner"]["sha256"],
            "projector_gate_observable": "full canonical action object; never rationale or next_goal",
        },
        "contrasts": {"primary": "D_gate_i = U_A3_PACTA - U_A2_SAP_ALWAYS", "secondary_scb": "U_A3_PACTA - U_A1_SCB", "secondary_native": "U_A3_PACTA - U_A0_NATIVE"},
        "pilot_gate": {
            "state_packets_invariant": "6/6",
            "model_drift": 0,
            "max_projection_failure_states": 1,
            "gate_open_min": 2,
            "gate_open_max": 5,
            "gate_open_mean_D_gate_min": 0.05,
            "gate_open_positive_fraction_min": 0.5,
            "overall_mean_A3_minus_A0_strictly_positive": True,
            "parse_or_fallback_advantage_forbidden": True,
        },
        "confirmatory_gate": {
            "states": 13,
            "primary_mean_D_gate_min": 0.05,
            "test": "one-sided paired sign-flip/randomization",
            "repetitions": 100000,
            "seed": 20260830,
            "p_lt": 0.05,
            "mean_A3_gt_mean_A0": True,
            "gate_open_mean_D_gate_gt": 0.0,
        },
        "terminal_unlock": "only after confirmatory first-action PASS and evaluator-path qualification for every confirmatory state",
        "forbidden": ["old B10 36 states", "TGRP 13-state pilot", "SCMB 12-state pilot", "gate tuning", "projector wording tuning", "canonicalization tuning", "threshold tuning", "model substitution", "sample replacement", "terminal inspection before first-action confirmation", "R8/R9 modification"],
    }
    authority = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_HUMAN_AUTHORITY",
        "source": "human author message dated 2026-08-30",
        "authorized": ["novelty audit", "offline preflight", "support requalification", "6-state pilot", "13-state confirmatory iff pilot frozen gate passes", "bounded terminal iff confirmatory and evaluator qualification pass", "analysis", "Research OS writeback", "branch commit and push"],
        "not_authorized": ["backbone change", "dataset change", "outcome-based sample replacement", "threshold tuning", "second method family", "GPU training", "merge main", "submission"],
    }
    freeze = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_METHOD_AND_SAMPLE_FREEZE",
        "status": "FROZEN_BEFORE_ANY_PACTA_PROVIDER_CALL",
        "novelty_audit_sha256": shaf(NOVELTY),
        "r9_freeze_sha256": shaf(R9_FREEZE),
        "r9_closure_sha256": shaf(R9_CLOSURE),
        "prompt_hashes": {"P0": prompts["P0"]["template_sha256"], "P1": prompts["P1"]["template_sha256"]},
        "split": {"salt": SPLIT_SALT, "pilot_ids": [u["future_task"] for u in pilot], "confirmatory_ids": [u["future_task"] for u in confirm]},
        "algorithm_frozen": True,
        "statistics_frozen": True,
        "provider_identity_frozen": True,
        "action_canonicalization_frozen": True,
    }

    outputs = {
        HERE / "c1-pacta-projector-prompts-20260830.json": prompts,
        HERE / "c1-pacta-split-20260830.json": split,
        HERE / "C1_CAST_HOLDOUT_REALLOCATION_AMENDMENT.json": amendment,
        HERE / "c1-pacta-contract-20260830.json": contract,
        HERE / "c1-pacta-human-authorization-20260830.json": authority,
        HERE / "c1-pacta-freeze-20260830.json": freeze,
    }
    for path, value in outputs.items():
        dump(path, value)

    for phase, run, phase_units in [("pilot", PILOT_RUN, pilot), ("confirmatory", CONFIRM_RUN, confirm)]:
        run.mkdir(parents=True, exist_ok=True)
        for name, value in [
            ("contract.json", contract),
            ("split.json", split),
            ("projector-prompts.json", prompts),
            ("reallocation-amendment.json", amendment),
            ("human-authority.json", authority),
            ("freeze.json", freeze),
        ]:
            dump(run / name, value)
        index = []
        for u in phase_units:
            row = {
                "phase": phase,
                "future_task": u["future_task"],
                "intent_template_id": u["intent_template_id"],
                "selected_source_task": u["selected_source_task"],
                "split_hash": u["cast_split_hash"],
                "task_prompt_sha256": u["task_prompt_sha256"],
                "system_instruction_sha256": u["system_instruction_sha256"],
                "current_state_sha256": u["current_state_sha256"],
                "success_memory_wrapper_path": u["success_memory_wrapper_path"],
                "success_memory_wrapper_sha256": u["success_memory_wrapper_sha256"],
                "failure_memory_wrapper_path": u["failure_memory_wrapper_path"],
                "failure_memory_wrapper_sha256": u["failure_memory_wrapper_sha256"],
                "evaluator_class": u["evaluator_class"],
            }
            for branch in ["success", "failure"]:
                p = Path(row[f"{branch}_memory_wrapper_path"])
                require(p.is_file(), f"missing memory wrapper {p}")
                require(shaf(p) == row[f"{branch}_memory_wrapper_sha256"], f"memory drift {p}")
            index.append(row)
        write_jsonl(run / "input-index.jsonl", index)
        manifest = {
            "schema_version": "1.0",
            "run_id": run.name,
            "phase": phase,
            "status": "FROZEN_READY_FOR_SUPPORT" if phase == "pilot" else "SEALED_CONFIRMATORY_NOT_AUTHORIZED_UNTIL_PILOT_PASS",
            "prepared_at": now(),
            "preparation_git_sha": git("rev-parse", "HEAD"),
            "origin_main_sha": git("rev-parse", "origin/main"),
            "contract_sha256": shaf(run / "contract.json"),
            "split_sha256": shaf(run / "split.json"),
            "projector_prompts_sha256": shaf(run / "projector-prompts.json"),
            "input_index_sha256": shaf(run / "input-index.jsonl"),
            "state_ids": [u["future_task"] for u in phase_units],
            "expected_projection_calls": len(phase_units) * 4,
            "expected_scb_calls": len(phase_units) * 2,
            "expected_policy_calls": len(phase_units) * 4 * 2 * 6,
            "terminal_locked": True,
        }
        dump(run / "manifest.json", manifest)

    print(json.dumps({
        "status": "PACTA_FROZEN_OFFLINE",
        "method_name": "PACTA",
        "pilot": [u["future_task"] for u in pilot],
        "confirmatory": [u["future_task"] for u in confirm],
        "r9_holdout_outcomes": 0,
        "prompt_hashes": freeze["prompt_hashes"],
        "origin_main": git("rev-parse", "origin/main"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
