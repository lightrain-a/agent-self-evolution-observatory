from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from c1_pacta_v11_action_schema import TOOL_SPEC, canonical_schema, extract_minimal_action_schema, sha256_text

B3 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json")
B4 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json")
B10 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json")
R9_CONTRACT = HERE / "c1-scmb-pilot-contract-20260829.json"
V1_PROMPTS = HERE / "c1-pacta-projector-prompts-20260830.json"
V1_CONTRACT = HERE / "c1-pacta-contract-20260830.json"
V1_CLOSURE = HERE / "c1-pacta-pilot-closure-20260830.json"
V1_PILOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-p0-20260830-pilot-v1")
V1_CONFIRM = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-c1-20260830-confirmatory-v1")
R9_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1")
QUAL_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-q0-schema-20260830-v1")
PILOT_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v11-p0-fresh-7template-20260830-v1")

MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"
SALT = "C1-PACTA-V11-PILOT-v1"
CANDIDATE_BY_TEMPLATE = {
    137: [352, 353, 354, 355],
    138: [238, 239, 241, 242],
    139: [269, 270, 271, 272],
    153: [653],
    156: [436, 437, 438, 440],
    172: [506, 508, 792],
    211: [261, 262, 264],
}
CANDIDATES = {task for tasks in CANDIDATE_BY_TEMPLATE.values() for task in tasks}
V1_CONSUMED = {313, 376, 368, 512, 300, 191, 510, 117, 24, 332, 656, 240, 166, 263, 273, 793, 351, 96, 439}


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


def prior_outputs(run: Path, task: int, groups: tuple[str, ...]) -> list[str]:
    if not run.exists():
        return []
    needle = f"task-{task}__"
    found = []
    for group in groups:
        folder = run / group
        if folder.exists():
            found.extend(str(path) for path in folder.glob(f"*{needle}*"))
    return sorted(found)


def synthetic_fixtures() -> list[dict]:
    rows = [
        ("click-search", "When a search button is visible, click it.", "Open the product search.", "[7]<button>Search</button>"),
        ("click-reviews", "Open the Reviews tab before reading reviews.", "Inspect product reviews.", "[14]<a>Reviews</a>"),
        ("click-cart", "Use the Add to Cart button for the chosen item.", "Add the selected item.", "[22]<button>Add to Cart</button>"),
        ("click-next", "Use the Next button to continue pagination.", "Open the next results page.", "[31]<button>Next</button>"),
        ("input-query", "Type the requested product name into the search field.", "Search for a blue mug.", "[5]<input>Search products</input>"),
        ("input-email", "Enter the supplied email in the email field.", "Enter alex@example.com.", "[8]<input>Email</input>"),
        ("input-quantity", "Replace the quantity field with the requested value.", "Set quantity to 3.", "[11]<input>Quantity</input>"),
        ("input-name", "Fill the recipient name in the visible input.", "Enter recipient name Kai.", "[3]<input>Recipient name</input>"),
        ("extract-names", "Use content extraction for dense result text.", "Extract all visible product names.", "Product grid with many non-interactive cards."),
        ("extract-prices", "Use content extraction to collect prices from the page.", "Extract product names and prices.", "Dense catalog page with price text."),
        ("extract-reviews", "Extract review authors and matching snippets.", "Collect reviews mentioning fingerprints.", "Reviews page with many review blocks."),
        ("send-enter", "After filling a search box, send the Enter key.", "Submit the current search.", "Search input is focused and contains blue mug."),
        ("send-escape", "Close the current popup by sending Escape.", "Dismiss the popup.", "A modal dialog is open."),
        ("dropdown-color", "Select the requested color from the dropdown.", "Choose White.", "[18]<select>Color</select>"),
        ("dropdown-size", "Select the requested size from the dropdown.", "Choose Large.", "[19]<select>Size</select>"),
        ("go-back", "Return to the previous browser page when the current page is wrong.", "Return to previous results.", "Current page is an unrelated product detail."),
        ("go-url", "Navigate directly to the supplied allowed URL.", "Open the store home page.", "Current page is blank."),
        ("scroll", "Scroll down when more results are below the viewport.", "Continue inspecting results.", "Bottom of visible viewport; more items exist below."),
        ("wait", "Wait briefly when the page is still loading.", "Allow the results to finish loading.", "Loading indicator is visible."),
        ("done", "When the requested information is already visible and collected, finish successfully.", "Return the collected answer.", "All requested product names have been collected."),
    ]
    return [
        {"fixture_id": f"synthetic-{index:02d}-{name}", "non_scientific": True, "memory": memory, "task": task, "state": state}
        for index, (name, memory, task, state) in enumerate(rows, 1)
    ]


def derive_native_inventory(table: dict[int, dict]) -> dict:
    counts: Counter[str] = Counter()
    profiles: dict[str, Counter[tuple]] = defaultdict(Counter)
    for task, row in table.items():
        if task in CANDIDATES:
            continue
        trajectory = json.loads(str(row["trajectory_json"]))
        for step in (trajectory.get("steps") or {}).values():
            output = step.get("output_messages") or {}
            message = output.get("tool_call_message") or {}
            for tool_call in message.get("tool_calls") or []:
                args = tool_call.get("args") or {}
                for action in args.get("action") or []:
                    if not isinstance(action, dict):
                        continue
                    for name, action_args in action.items():
                        if not isinstance(action_args, dict):
                            continue
                        counts[name] += 1
                        profile = tuple(sorted((key, type(value).__name__) for key, value in action_args.items()))
                        profiles[name][profile] += 1
    require(set(counts) == set(TOOL_SPEC), f"native tool inventory drift: observed={sorted(counts)} expected={sorted(TOOL_SPEC)}")
    return {
        "pool_tasks_excluded": sorted(CANDIDATES),
        "observed_calls": sum(counts.values()),
        "tool_counts": dict(sorted(counts.items())),
        "argument_type_profiles": {
            name: [{"arguments": {key: value_type for key, value_type in profile}, "count": count} for profile, count in sorted(counter.items())]
            for name, counter in sorted(profiles.items())
        },
    }


def main() -> int:
    require(len(CANDIDATES) == 23 and len(CANDIDATE_BY_TEMPLATE) == 7, "candidate geometry drift")
    require(not (CANDIDATES & V1_CONSUMED), "PACTA-v1 sample overlap")
    require(not QUAL_RUN.exists() and not PILOT_RUN.exists(), "v1.1 run directory already exists")

    b3, b4, b10 = load(B3), load(B4), load(B10)
    prompts = load(V1_PROMPTS)
    v1_contract = load(V1_CONTRACT)
    v1_closure = load(V1_CLOSURE)
    require(prompts["P0"]["template_sha256"] == "d4f1f4aeafac058b83930499ea10a2db0b70db9f5a76131fcd4ff8e0486de295", "P0 wording drift")
    require(prompts["P1"]["template_sha256"] == "cfe5f1957da06a674d7c90e4c7e7753505482c7f17de9ecd28191e4fd3c44caf", "P1 wording drift")
    require(v1_closure["claim_authority"]["method_status"] == "PACTA_CANDIDATE_NOT_QUALIFIED", "v1 closure drift")
    require(v1_closure["pilot"]["policy_calls_completed_before_early_stop"] == 18, "v1 partial count drift")

    wrappers = {(int(row["source_task"]), str(row["condition"])): row for row in b4["objects"]}
    retrieval = {int(row["task_id"]): row for row in b3["all_rows"]}
    require(CANDIDATES <= set(retrieval), "candidate missing from retrieval source")
    for template, tasks in CANDIDATE_BY_TEMPLATE.items():
        for task in tasks:
            row = retrieval[task]
            require(int(row["intent_template_id"]) == template, f"template drift {task}")
            require(bool(row["threshold_hit"]) and bool(row["trajectory_available"]), f"retrieval/trajectory failure {task}")
            require(bool(row["is_shopping"]) and not bool(row["is_source_task"]), f"substrate drift {task}")

    sys.path.insert(0, str(b10["vendor_path"]))
    import pyarrow.parquet as pq

    parquet = Path(b10["source_bindings"]["parquet"]["path"])
    require(shaf(parquet) == b10["source_bindings"]["parquet"]["sha256"], "source parquet drift")
    raw_rows = pq.read_table(parquet, columns=["task_id", "task_prompt", "trajectory_json"]).to_pylist()
    table = {int(row["task_id"]): row for row in raw_rows}
    require(CANDIDATES <= set(table), "candidate trajectory missing")
    inventory = derive_native_inventory(table)

    schema_text = canonical_schema()
    schema_sha = sha256_text(schema_text)
    pool = []
    systems: dict[str, str] = {}
    for template, tasks in CANDIDATE_BY_TEMPLATE.items():
        for task in tasks:
            source = retrieval[task]
            source_task = int(source["top1_source_task"])
            raw = table[task]
            trajectory = json.loads(str(raw["trajectory_json"]))
            step = (trajectory.get("steps") or {}).get("1")
            require(step is not None, f"step1 absent {task}")
            contents = ((step.get("input_messages") or {}).get("contents") or [])
            require(len(contents) >= 2, f"input packet absent {task}")
            system = str(contents[0].get("content") or "")
            last = str(contents[-1].get("content") or "")
            marker = "[Current state starts here]"
            require(marker in last, f"current state marker absent {task}")
            state = last.split(marker, 1)[1].strip()
            task_prompt = str(raw["task_prompt"])
            extracted = extract_minimal_action_schema(system)
            require(extracted == schema_text, f"schema extraction drift {task}")
            system_sha = sha256_text(system)
            systems[system_sha] = system

            unit = {
                "future_task": task,
                "intent_template_id": template,
                "selected_source_task": source_task,
                "retrieval_threshold_hit": True,
                "trajectory_available": True,
                "retrieval_similarity": source["top1_similarity"],
                "retrieval_margin": source["top1_margin"],
                "evaluator_class": source["evaluator_class"],
                "split_hash": sha256_text(f"{SALT}|{template}|{task}"),
                "task_prompt_sha256": sha256_text(task_prompt),
                "system_instruction_sha256": system_sha,
                "current_state_sha256": sha256_text(state),
                "action_schema_sha256": schema_sha,
                "prior_pacta_projection_or_policy_outputs": [],
                "prior_scmb_scientific_outputs": [],
            }
            unit["prior_pacta_projection_or_policy_outputs"] = prior_outputs(V1_PILOT, task, ("projection", "per_case")) + prior_outputs(V1_CONFIRM, task, ("projection", "per_case"))
            unit["prior_scmb_scientific_outputs"] = prior_outputs(R9_RUN, task, ("binder", "per_case"))
            require(not unit["prior_pacta_projection_or_policy_outputs"], f"prior PACTA output {task}")
            require(not unit["prior_scmb_scientific_outputs"], f"prior SCMB output {task}")
            for branch, condition in (("success", "success"), ("failure", "failure")):
                wrapper = wrappers[(source_task, condition)]
                path = Path(wrapper["native_wrapper_path"])
                require(path.is_file() and shaf(path) == wrapper["native_wrapper_sha256"], f"wrapper drift {source_task}/{condition}")
                unit[f"{branch}_memory_wrapper_path"] = str(path)
                unit[f"{branch}_memory_wrapper_sha256"] = wrapper["native_wrapper_sha256"]
            pool.append(unit)

    require(len(systems) == 1, f"native system instruction differs across pool: {sorted(systems)}")
    pilot = [min((unit for unit in pool if unit["intent_template_id"] == template), key=lambda row: row["split_hash"]) for template in sorted(CANDIDATE_BY_TEMPLATE)]
    expected = [353, 238, 272, 653, 440, 792, 264]
    require([unit["future_task"] for unit in pilot] == expected, "pilot hash selection drift")
    unused = [unit for unit in pool if unit not in pilot]

    action_schema_artifact = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_ACTION_SCHEMA",
        "status": "DETERMINISTIC_MINIMAL_AFFORDANCE_SCHEMA_FROZEN",
        "single_variable_repair": "ACTION_SCHEMA_EXTRACTION",
        "projector_schema": json.loads(schema_text),
        "projector_schema_canonical_json": schema_text,
        "action_schema_sha256": schema_sha,
        "source_system_instruction_sha256": next(iter(systems)),
        "separate_hashes_required": True,
        "forbidden_content_absent": [
            "current_state response envelope",
            "native output-format instructions",
            "memory instructions",
            "task-solving instructions",
            "reasoning instructions",
            "next_goal envelope requirements",
            "other system prose",
        ],
        "native_inventory_evidence_excluding_23_candidate_tasks": inventory,
        "extraction_module_path": str(HERE / "c1_pacta_v11_action_schema.py"),
        "extraction_module_sha256": shaf(HERE / "c1_pacta_v11_action_schema.py"),
    }
    fixtures = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_SYNTHETIC_SCHEMA_FIXTURES",
        "status": "FROZEN_NON_SCIENTIFIC_BEFORE_PROVIDER_CALLS",
        "scientific_state_used": False,
        "expected_calls": 40,
        "fixtures": synthetic_fixtures(),
    }
    require(len(fixtures["fixtures"]) == 20, "fixture count drift")

    split = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FRESH_TEMPLATE_PILOT_SPLIT",
        "status": "FROZEN_BEFORE_SCHEMA_QUALIFICATION_OR_SCIENTIFIC_OUTPUT",
        "salt": SALT,
        "hash_rule": 'SHA256("C1-PACTA-V11-PILOT-v1"|intent_template_id|future_task), with literal | delimiters',
        "candidate_pool": pool,
        "pilot": pilot,
        "unused_without_outcome_access": unused,
        "pilot_ids": expected,
        "outcome_accessed_for_selection": False,
    }

    contract = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_FROZEN_CONTRACT",
        "paper_id": v1_contract["paper_id"],
        "experiment_id": "C1-PACTA-V11-FRESH-7TEMPLATE-UPTAKE-20260830",
        "status": "FROZEN_SINGLE_VARIABLE_REPAIR_BEFORE_PROVIDER_CALLS",
        "lineage": {
            "PACTA_v1": "INVALID_UNQUALIFIED_INTERFACE_EXECUTION",
            "PACTA_v11": "single-variable ACTION_SCHEMA_EXTRACTION repair",
            "v1_execution_git_sha": v1_closure["provenance"]["execution_git_sha"],
            "v1_partial_policy_responses_excluded": 18,
        },
        "single_variable_repair": {
            "before": "ACTION_SCHEMA = full native system instruction",
            "after": "ACTION_SCHEMA = deterministically extracted minimal browser tool affordance schema",
        },
        "unchanged": {
            "P0_sha256": prompts["P0"]["template_sha256"],
            "P1_sha256": prompts["P1"]["template_sha256"],
            "gate": v1_contract["method"]["gate"],
            "canonicalization": v1_contract["method"]["canonicalization"],
            "arms": v1_contract["arms"],
            "scb_baseline": v1_contract["scb_baseline"],
            "projector": v1_contract["projector"],
            "policy": v1_contract["policy"],
            "observable": v1_contract["observable"],
        },
        "schema_qualification": {
            "fixtures": 20,
            "renderings": ["P0", "P1"],
            "expected_calls": 40,
            "exact_schema_required": 40,
            "model_drift": 0,
            "thinking_fallback": 0,
            "failure_status": "STOP_SCHEMA_QUALIFICATION",
        },
        "pilot": {
            "states": 7,
            "templates": 7,
            "projection_calls": 28,
            "scb_calls": 14,
            "policy_calls": 336,
            "rollouts_per_state_arm_branch": 6,
            "projection_exact_schema_required": 28,
            "model_drift": 0,
            "packet_drift": 0,
            "gate_open_min": 2,
            "gate_open_max": 6,
            "primary": "D_gate_i = U_A3_PACTA - U_A2_SAP_ALWAYS",
            "gate_open_mean_D_gate_min": 0.05,
            "gate_open_positive_fraction_min": 0.5,
            "secondary_native": "mean(U_A3_PACTA - U_A0_NATIVE) > 0",
            "report_only": ["A3-A1", "A2-A1", "A2-A0"],
            "interpretation": "proof-of-concept only",
        },
        "stop_after_pilot": True,
        "terminal_authorized": False,
        "same_substrate_confirmatory_authorized": False,
    }
    freeze = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_METHOD_SAMPLE_STATISTICS_FREEZE",
        "status": "FROZEN_BEFORE_SCHEMA_QUALIFICATION",
        "origin_main_sha": git("rev-parse", "origin/main"),
        "base_v1_commit": git("rev-parse", "origin/experiment/c1-cast-20260830"),
        "prompt_hashes": {"P0": prompts["P0"]["template_sha256"], "P1": prompts["P1"]["template_sha256"]},
        "action_schema_sha256": schema_sha,
        "pilot_ids": expected,
        "algorithm_unchanged_except_action_schema_extraction": True,
        "statistics_frozen": True,
        "provider_identity_frozen": True,
        "sample_frozen": True,
    }
    preflight = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PACTA_V11_ZERO_PROVIDER_PREFLIGHT",
        "status": "PASS_ZERO_PROVIDER_FRESH_PACKET_PREFLIGHT",
        "checks": {
            "candidate_states": 23,
            "candidate_templates": 7,
            "pilot_states": 7,
            "pilot_templates": 7,
            "v1_sample_overlap": 0,
            "trajectory_available": "23/23",
            "retrieval_threshold_hit": "23/23",
            "memory_wrappers_hash_verified": "46/46",
            "task_state_system_hashes_materialized": "23/23",
            "system_schema_hashes_separate": True,
            "prior_PACTA_projection_or_policy_outputs": 0,
            "prior_SCMB_scientific_outputs": 0,
            "provider_calls": 0,
            "unused_state_outcomes_accessed": 0,
        },
        "source_bindings": {
            "B3_sha256": shaf(B3),
            "B4_sha256": shaf(B4),
            "B10_sha256": shaf(B10),
            "parquet_sha256": shaf(parquet),
            "v1_closure_sha256": shaf(V1_CLOSURE),
        },
    }

    repo_outputs = {
        HERE / "c1-pacta-v11-action-schema-20260830.json": action_schema_artifact,
        HERE / "c1-pacta-v11-schema-fixtures-20260830.json": fixtures,
        HERE / "c1-pacta-v11-split-20260830.json": split,
        HERE / "c1-pacta-v11-contract-20260830.json": contract,
        HERE / "c1-pacta-v11-freeze-20260830.json": freeze,
        HERE / "c1-pacta-v11-preflight-20260830.json": preflight,
    }
    for path, value in repo_outputs.items():
        dump(path, value)

    QUAL_RUN.mkdir(parents=True)
    for name, value in (
        ("action-schema.json", action_schema_artifact),
        ("fixtures.json", fixtures),
        ("contract.json", contract),
        ("freeze.json", freeze),
        ("projector-prompts.json", prompts),
    ):
        dump(QUAL_RUN / name, value)
    dump(QUAL_RUN / "manifest.json", {
        "schema_version": "1.0",
        "run_id": QUAL_RUN.name,
        "phase": "non_scientific_schema_qualification",
        "status": "FROZEN_READY",
        "scientific_state_used": False,
        "expected_calls": 40,
        "preparation_git_sha": git("rev-parse", "HEAD"),
        "origin_main_sha": git("rev-parse", "origin/main"),
        "action_schema_sha256": schema_sha,
        "system_instruction_sha256": next(iter(systems)),
        "projector_prompts_sha256": shaf(QUAL_RUN / "projector-prompts.json"),
    })

    PILOT_RUN.mkdir(parents=True)
    for name, value in (
        ("action-schema.json", action_schema_artifact),
        ("contract.json", contract),
        ("freeze.json", freeze),
        ("split.json", split),
        ("projector-prompts.json", prompts),
        ("preflight.json", preflight),
    ):
        dump(PILOT_RUN / name, value)
    pilot_by_task = {row["future_task"]: row for row in pilot}
    index = []
    for task in expected:
        row = dict(pilot_by_task[task])
        row["phase"] = "pilot"
        index.append(row)
    write_jsonl(PILOT_RUN / "input-index.jsonl", index)
    dump(PILOT_RUN / "manifest.json", {
        "schema_version": "1.0",
        "run_id": PILOT_RUN.name,
        "phase": "fresh_7template_pilot",
        "status": "LOCKED_UNTIL_SCHEMA_QUALIFICATION_40_OF_40",
        "preparation_git_sha": git("rev-parse", "HEAD"),
        "origin_main_sha": git("rev-parse", "origin/main"),
        "state_ids": expected,
        "expected_projection_calls": 28,
        "expected_scb_calls": 14,
        "expected_policy_calls": 336,
        "terminal_locked": True,
        "same_substrate_confirmatory_locked": True,
    })

    print(json.dumps({
        "status": preflight["status"],
        "pilot": expected,
        "candidate_pool": len(pool),
        "action_schema_sha256": schema_sha,
        "system_instruction_sha256": next(iter(systems)),
        "prompt_hashes": freeze["prompt_hashes"],
        "provider_calls": 0,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
