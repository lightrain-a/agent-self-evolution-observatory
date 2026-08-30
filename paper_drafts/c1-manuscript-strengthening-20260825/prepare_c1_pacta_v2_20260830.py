from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B3 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json")
B4 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json")
B10 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
R9_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1")
V1_RUNS = [
    Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1"),
    Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-c1-20260830-confirmatory-v1"),
    Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-p0-fresh-7template-20260830-v1"),
]
RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1")
AUDIT = HERE / "c1-pacta-v2-novelty-audit-20260830.json"
V11_CONTRACT = HERE / "c1-pacta-v11-contract-20260830.json"
V11_CLOSURE = HERE / "c1-pacta-v11-pilot-closure-20260830.json"
SPLIT_SALT = "C1-PACTA-V2-PILOT-v1"
RANDOM_SALT = "C1-PACTA-V2-RANDOM-GATE-v1"
CANDIDATE_BY_TEMPLATE = {
    137: [352, 354, 355],
    138: [239, 241, 242],
    139: [269, 270, 271],
    156: [436, 437, 438],
    172: [506, 508],
    211: [261, 262],
}
FORBIDDEN = {
    313, 376, 368, 512, 300, 191,
    510, 117, 24, 332, 656, 240, 166, 263, 273, 793, 351, 96, 439,
    353, 238, 272, 653, 440, 792, 264,
}
SCB_INSTRUCTION = "Given the reusable memory, the ultimate task, and the current browser state, produce one concise current-state action implication. Use the memory only when relevant, do not invent facts, and state what the agent should prioritize next. Output one sentence, at most 60 words, with no explanation."


def now():
    return datetime.now(timezone.utc).isoformat()


def sha_text(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    tmp.replace(path)


def require(value, message):
    if not value:
        raise RuntimeError(message)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def prior_outputs(run: Path, task: int):
    if not run.exists():
        return []
    needle = f"task-{task}__"
    found = []
    for folder in ("projection", "per_case", "shadow", "binder", "scb"):
        base = run / folder
        if base.exists():
            found.extend(str(p) for p in base.glob(f"*{needle}*"))
    return sorted(found)


def main():
    candidates = {x for xs in CANDIDATE_BY_TEMPLATE.values() for x in xs}
    require(len(candidates) == 16 and len(CANDIDATE_BY_TEMPLATE) == 6, "fresh pool geometry drift")
    require(not (candidates & FORBIDDEN), "historical sample overlap")
    require(not RUN.exists(), f"run already exists: {RUN}")
    audit = load(AUDIT)
    require(audit["verdict"] == "PASS_NOVEL_RESIDUAL" and not audit["fatal_collision_found"], "novelty audit is not open")
    v11_contract = load(V11_CONTRACT)
    v11_closure = load(V11_CLOSURE)
    require(v11_closure["claim_authority"]["method_status"] == "PACTA_V11_NOT_QUALIFIED", "v1.1 closure drift")

    b3, b4, b10 = load(B3), load(B4), load(B10)
    retrieval = {int(row["task_id"]): row for row in b3["all_rows"]}
    wrappers = {(int(row["source_task"]), str(row["condition"])): row for row in b4["objects"]}
    require(candidates <= set(retrieval), "candidate retrieval rows missing")
    sys.path.insert(0, str(b10["vendor_path"]))
    import pyarrow.parquet as pq
    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    require(sha_file(parquet) == b10["source_bindings"]["parquet"]["sha256"], "source parquet drift")
    table = {int(row["task_id"]): row for row in pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()}
    require(candidates <= set(table), "candidate trajectory rows missing")

    pool = []
    for template, tasks in sorted(CANDIDATE_BY_TEMPLATE.items()):
        for task in tasks:
            source = retrieval[task]
            require(int(source["intent_template_id"]) == template, f"template drift {task}")
            require(bool(source["trajectory_available"]) and bool(source["threshold_hit"]), f"trajectory/retrieval failure {task}")
            require(bool(source["is_shopping"]) and not bool(source["is_source_task"]), f"substrate drift {task}")
            raw = table[task]
            trajectory = json.loads(str(raw["trajectory_json"]))
            step = (trajectory.get("steps") or {}).get("1")
            require(step is not None, f"step1 missing {task}")
            contents = ((step.get("input_messages") or {}).get("contents") or [])
            require(len(contents) >= 2, f"input packet missing {task}")
            system = str(contents[0].get("content") or "")
            last = str(contents[-1].get("content") or "")
            marker = "[Current state starts here]"
            require(marker in last, f"state marker missing {task}")
            state = last.split(marker, 1)[1].strip()
            task_prompt = str(raw["task_prompt"])
            source_task = int(source["top1_source_task"])
            unit = {
                "future_task": task,
                "intent_template_id": template,
                "selected_source_task": source_task,
                "trajectory_available": True,
                "retrieval_threshold_hit": True,
                "retrieval_similarity": source["top1_similarity"],
                "retrieval_margin": source["top1_margin"],
                "evaluator_class": source["evaluator_class"],
                "split_hash": sha_text(f"{SPLIT_SALT}|{template}|{task}"),
                "random_gate_hash": sha_text(f"{RANDOM_SALT}|{template}|{task}"),
                "task_prompt_sha256": sha_text(task_prompt),
                "current_state_sha256": sha_text(state),
                "system_instruction_sha256": sha_text(system),
                "prior_pacta_outputs": [],
                "prior_scmb_outputs": prior_outputs(R9_RUN, task),
            }
            for run in V1_RUNS:
                unit["prior_pacta_outputs"].extend(prior_outputs(run, task))
            require(not unit["prior_pacta_outputs"], f"prior PACTA output {task}")
            require(not unit["prior_scmb_outputs"], f"prior SCMB output {task}")
            for branch in ("success", "failure"):
                wrapper = wrappers[(source_task, branch)]
                memory_path = Path(wrapper["native_wrapper_path"])
                require(memory_path.is_file() and sha_file(memory_path) == wrapper["native_wrapper_sha256"], f"wrapper drift {source_task}/{branch}")
                unit[f"{branch}_memory_wrapper_path"] = str(memory_path)
                unit[f"{branch}_memory_wrapper_sha256"] = wrapper["native_wrapper_sha256"]
            pool.append(unit)

    pilot = [min((u for u in pool if u["intent_template_id"] == t), key=lambda u: u["split_hash"]) for t in sorted(CANDIDATE_BY_TEMPLATE)]
    expected = [352, 239, 271, 437, 506, 261]
    require([u["future_task"] for u in pilot] == expected, "pilot selection drift")
    unused = [u for u in pool if u not in pilot]
    random_ranking = sorted(pilot, key=lambda u: u["random_gate_hash"])

    contract = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V2_FROZEN_CONTRACT",
        "experiment_id": "C1-PACTA-V2-DOWNSTREAM-POLICY-SHADOW-PILOT-20260830",
        "status": "FROZEN_BEFORE_SUPPORT_OR_SCIENTIFIC_PROVIDER_CALLS",
        "lineage": {
            "PACTA_v1": "INVALID_UNQUALIFIED_INTERFACE_EXECUTION",
            "PACTA_v11": "OPERATIONALIZATION_AND_GATE_REALIZATION_STOP_NOT_MECHANISM_RESULT",
            "v1_v11_artifacts_modified": False,
            "historical_policy_responses_excluded": True
        },
        "scientific_object": {
            "name": "PACTA-v2",
            "binder": "exact R9 State-Conditioned Binding, unchanged",
            "shadow_surface": "downstream policy first-action distribution",
            "replicate_blocks_per_branch": 2,
            "samples_per_block": 6,
            "B1": "TV(S1,F1)",
            "B2": "TV(S2,F2)",
            "WS": "TV(S1,S2)",
            "WF": "TV(F1,F2)",
            "gate": "G = min(B1,B2) > max(WS,WF)",
            "epsilon": None,
            "factual_transport_open": "raw factual memory + factual SCB",
            "factual_transport_closed": "raw factual memory only"
        },
        "models": {
            "binder": {"requested":"doubao-seed-2.0-mini","resolved":"doubao-seed-2-0-mini-260215","temperature":0.0,"max_output_tokens":180,"thinking":"disabled","retries":0,"substitution":False},
            "shadow_and_final_policy": {"requested":"doubao-seed-2.0-mini","resolved":"doubao-seed-2-0-mini-260215","temperature":0.2,"max_output_tokens":900,"thinking":"disabled","retries":0,"substitution":False}
        },
        "scb": {"instruction": SCB_INSTRUCTION, "source": "exact R9 implementation family", "changed": False},
        "arms": {
            "A0_NATIVE": "raw branch memory only",
            "A1_SCB_ALWAYS": "raw branch memory plus branch SCB",
            "A2_RANDOM_RATE_MATCHED": "SCB transported for the first K states in the pre-output frozen random ranking; native otherwise",
            "A3_PACTA_V2": "SCB transported iff the frozen policy-surface gate opens; native otherwise"
        },
        "random_gate": {"salt": RANDOM_SALT, "K": "observed PACTA-v2 gate-open count after complete shadow calibration", "ranking_frozen_before_shadow_output": True},
        "observable": {"U":"B10-normalized first-action TV between success and failure final-policy distributions", "primary":"D_select_i = U_A3_PACTA_V2 - U_A2_RANDOM_RATE_MATCHED"},
        "shadow_realization": {"expected_calls":144,"complete_required":144,"model_drift":0,"missingness":0,"parser_failure":0,"input_hash_failure":0},
        "gate_geometry": {"open_min":2,"open_max":5,"degenerate_status":"HOLD_GATE_DEGENERATE"},
        "final_policy": {"expected_calls":288,"rollouts_per_state_arm_branch":6,"shadow_samples_excluded":True},
        "pilot_gate": {
            "mean_D_select_min":0.05,
            "positive_state_count_gt_negative":True,
            "mean_A3_minus_A0_gt_zero":True,
            "mean_A3_minus_A1_ge_zero":True
        },
        "stop_after_pilot": True,
        "confirmatory_authorized": False,
        "terminal_authorized": False,
        "R10_success_rewrite_authorized": False
    }
    split = {
        "schema_version":"1.0",
        "artifact_kind":"C1_PACTA_V2_FRESH_PILOT_SPLIT",
        "status":"FROZEN_OUTCOME_BLIND",
        "salt":SPLIT_SALT,
        "candidate_pool":pool,
        "pilot":pilot,
        "pilot_ids":expected,
        "unused_without_outcome_access":unused,
        "outcome_accessed_for_selection":False
    }
    ranking = {
        "schema_version":"1.0",
        "artifact_kind":"C1_PACTA_V2_RANDOM_GATE_RANKING",
        "status":"FROZEN_BEFORE_SHADOW_OUTPUT",
        "salt":RANDOM_SALT,
        "ranking":[{"rank":i,"future_task":u["future_task"],"intent_template_id":u["intent_template_id"],"sha256":u["random_gate_hash"]} for i,u in enumerate(random_ranking,1)],
        "K":"not known until frozen PACTA-v2 shadow gate geometry is realized"
    }
    freeze = {
        "schema_version":"1.0",
        "artifact_kind":"C1_PACTA_V2_METHOD_SAMPLE_STATISTICS_FREEZE",
        "status":"FROZEN_BEFORE_SUPPORT_OR_SCIENTIFIC_PROVIDER_CALLS",
        "origin_main_sha":git("rev-parse","origin/main"),
        "design_parent_sha":git("rev-parse","HEAD"),
        "pilot_ids":expected,
        "shadow_schedule_geometry":"6 states x 2 branches x 2 blocks x 6 samples = 144",
        "final_schedule_geometry":"6 states x 4 arms x 2 branches x 6 samples = 288 if and only if gate non-degenerate",
        "binder_frozen_before_shadow":True,
        "shadow_schedule_frozen_before_shadow_output":True,
        "random_ranking_frozen_before_shadow_output":True,
        "statistics_frozen":True,
        "provider_identity_frozen":True,
        "no_retries_topup_imputation_replacement":True
    }
    preflight = {
        "schema_version":"1.0",
        "artifact_kind":"C1_PACTA_V2_ZERO_PROVIDER_PREFLIGHT",
        "status":"PASS_ZERO_PROVIDER_FRESH_PACKET_PREFLIGHT",
        "checks":{
            "candidate_states":16,
            "candidate_templates":6,
            "pilot_states":6,
            "pilot_templates":6,
            "historical_sample_overlap":0,
            "trajectory_available":"16/16",
            "retrieval_threshold_hit":"16/16",
            "wrapper_hashes_verified":"32/32",
            "task_state_system_hashes_materialized":"16/16",
            "prior_PACTA_outputs":0,
            "prior_SCMB_outputs":0,
            "selection_outcome_blind":True
        }
    }

    RUN.mkdir(parents=True)
    for name, value in (
        ("contract.json",contract),("split.json",split),("fresh-pool.json",{"pool":pool}),
        ("random-gate-ranking.json",ranking),("freeze.json",freeze),("preflight.json",preflight)
    ):
        dump(HERE / f"c1-pacta-v2-{name.replace('.json','')}-20260830.json", value)
        dump(RUN / name, value)
    shutil.copy2(AUDIT, RUN / "novelty-audit.json")
    input_rows = []
    for u in pilot:
        for branch in ("success","failure"):
            input_rows.append({
                "future_task":u["future_task"],"intent_template_id":u["intent_template_id"],"branch":branch,
                "task_prompt_sha256":u["task_prompt_sha256"],"current_state_sha256":u["current_state_sha256"],
                "system_instruction_sha256":u["system_instruction_sha256"],"memory_wrapper_sha256":u[f"{branch}_memory_wrapper_sha256"]
            })
    write_jsonl(RUN / "input-index.jsonl", input_rows)
    dump(RUN / "manifest.json", {
        "schema_version":"1.0","run_id":RUN.name,"status":"FROZEN_AWAITING_SUPPORT_PROBE",
        "origin_main_sha":git("rev-parse","origin/main"),"design_git_sha":git("rev-parse","HEAD"),
        "expected_binder_calls":12,"expected_shadow_calls":144,"conditional_final_calls":288,
        "pilot_ids":expected,"created_at":now(),"confirmatory_executed":False,"terminal_executed":False
    })
    print(json.dumps({"status":"PREPARED","run":str(RUN),"pilot_ids":expected,"random_ranking":[u["future_task"] for u in random_ranking]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
