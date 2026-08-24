#!/usr/bin/env python3
"""Freeze the B1/L2B downstream executor, rollout schedule, and analysis contract.

Support-only: this script must not call the writer, executor, browser actions, or evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_RB_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_EXECUTOR_MANIFEST = "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
EXPECTED_MODEL_LAYER = "sha256:eabc98a9bcbfce7fd70f3e07de599f8fda98120fefed5881934161ede8bd1a41"
EXPECTED_EXECUTOR_TAG = "b1-qwen25-32b-l2b-executor:latest"
MEMORY_LEGEND = "ReasoningBank status code: S means source trajectory success; F means source trajectory fail."
SOURCE_FILES = {
    "run.py": "f9edcac62cc612f48db9859c60f71b7479aa126beda802437dd82d81030817b3",
    "agents/legacy/agent.py": "00ab439e7245ad4ac41aed75bfbd2a1a6db8be9efc01ac526360606e098d9a99",
    "agents/legacy/dynamic_prompting.py": "74c7fa8cac1bb734a4c15a318776f9f992c497a279f46b3f4e01600db1bf8074",
    "agents/legacy/utils/chat_api.py": "6f7013bfcdbaf30b2c37c786bbd819a9b8cc9dc58f6096a02b516cc1e7c9b7dc",
    "agents/legacy/utils/prompt_templates.py": "a92c9cfcde964246f78727bf91030f530da4ea68497516493efbceaa0ac6e420",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render_memory_file(memory_items_joined: str, arm: str) -> str:
    if arm not in {"STATUS_S", "STATUS_F"}:
        raise ValueError(arm)
    if not memory_items_joined.strip():
        raise RuntimeError("empty memory bytes are not admissible")
    code = "S" if arm == "STATUS_S" else "F"
    return memory_items_joined.strip() + "\n\n" + MEMORY_LEGEND + f"\nstatus: {code}\n"


def differing_indices(a: bytes, b: bytes) -> list[int]:
    if len(a) != len(b):
        raise RuntimeError("arm render lengths differ")
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def build_schedule(downstream_ids: list[str], source_ids: list[str]) -> list[dict[str, Any]]:
    if len(downstream_ids) != 36 or len(source_ids) != 36 or len(set(downstream_ids)) != 36:
        raise RuntimeError("R15 requires exactly 36 unique downstream units")
    rows: list[dict[str, Any]] = []
    seq = 0
    for idx, (task_id, source_id) in enumerate(zip(downstream_ids, source_ids)):
        base = ["STATUS_S", "STATUS_F"] if idx % 2 == 0 else ["STATUS_F", "STATUS_S"]
        for repeat in range(2):
            order = base if repeat == 0 else list(reversed(base))
            for pos, arm in enumerate(order):
                rows.append({
                    "sequence_index": seq,
                    "cohort_index": idx,
                    "task_id": str(task_id),
                    "source_task_id": str(source_id),
                    "repeat_id": repeat,
                    "position_in_pair": pos,
                    "arm": arm,
                    "task_seed": 0,
                    "reset_before_episode": True,
                })
                seq += 1
    if len(rows) != 144:
        raise RuntimeError("expected 144 episodes")
    for task_id in downstream_ids:
        task_rows = [r for r in rows if r["task_id"] == str(task_id)]
        if [r["arm"] for r in task_rows].count("STATUS_S") != 2 or [r["arm"] for r in task_rows].count("STATUS_F") != 2:
            raise RuntimeError(f"unbalanced arms for task {task_id}")
        firsts = [r["arm"] for r in task_rows if r["position_in_pair"] == 0]
        if sorted(firsts) != ["STATUS_F", "STATUS_S"]:
            raise RuntimeError(f"arm-order not counterbalanced for task {task_id}")
    return rows


def validate_source_files(root: Path) -> dict[str, str]:
    out = {}
    for rel, expected in SOURCE_FILES.items():
        p = root / rel
        actual = sha256(p)
        if actual != expected:
            raise RuntimeError(f"first-party source drift: {rel} {actual} != {expected}")
        out[rel] = actual
    return out


def build_contract(
    r9: dict[str, Any],
    r11: dict[str, Any],
    r13: dict[str, Any],
    r14: dict[str, Any],
    executor_manifest_sha: str,
    executor_show: dict[str, Any],
    executor_show_sha: str,
    transport: dict[str, Any],
    transport_sha: str,
    source_hashes: dict[str, str],
) -> dict[str, Any]:
    cohort = r9["cohort"]
    if cohort["independent_units"] != 36 or not cohort["full_cohort_required_if_executed"]:
        raise RuntimeError("R9 cohort drift")
    if r11["cohort"]["independent_units"] != 36 or not r11["cohort"]["all_units_shopping_only"]:
        raise RuntimeError("R11 live-support drift")
    if not r11["execution_gate"]["shopping_only_live_substrate_ready"]:
        raise RuntimeError("live Shopping substrate is not ready")
    if not r14["execution_gate"]["exact_writer_model_artifact_bound"] or r14["execution_gate"]["writer_calls_executed"] != 0:
        raise RuntimeError("R14 writer-model gate drift")
    if r13["summary"]["source_tasks"] != 36 or r13["summary"]["model_calls_executed"] != 0:
        raise RuntimeError("R13 writer-input gate drift")
    if executor_manifest_sha != EXPECTED_EXECUTOR_MANIFEST.removeprefix("sha256:"):
        raise RuntimeError("executor manifest drift")
    if executor_show.get("details", {}).get("quantization_level") != "Q4_K_M":
        raise RuntimeError("executor quantization drift")
    if "32768" not in str(executor_show.get("parameters", "")):
        raise RuntimeError("executor num_ctx is not pinned to 32768")
    if transport.get("status") != "FIRST_PARTY_GENERIC_AGENT_LOCAL_OPENAI_TRANSPORT_CONSTRUCTED_NO_COMPLETION":
        raise RuntimeError("transport smoke status drift")
    if transport.get("model") != EXPECTED_EXECUTOR_TAG or transport.get("temperature") != 0.0:
        raise RuntimeError("transport model/temperature drift")
    if transport.get("base_url") != "http://127.0.0.1:11444/v1/":
        raise RuntimeError("transport base URL drift")
    if any(transport.get(k) for k in ["completion_called", "browser_action_executed", "evaluator_called", "scientific_outcome_opened"]):
        raise RuntimeError("transport smoke opened an outcome")

    s = render_memory_file("# Memory Item 1\n## Title Placeholder", "STATUS_S").encode()
    f = render_memory_file("# Memory Item 1\n## Title Placeholder", "STATUS_F").encode()
    diff = differing_indices(s, f)
    if len(diff) != 1 or s[diff[0]:diff[0]+1] != b"S" or f[diff[0]:diff[0]+1] != b"F":
        raise RuntimeError("renderer is not a one-byte treatment")

    schedule = build_schedule(cohort["downstream_task_ids"], cohort["source_task_ids"])

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "contract_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-EXECUTOR-R15",
        "recorded_date": "2026-08-24",
        "status": "EXECUTOR_ROLLOUT_RANDOMIZATION_AND_FAIL_CLOSED_POLICY_FROZEN_NO_OUTCOMES",
        "role": "PRE_OUTCOME_EXECUTION_CONTRACT",
        "source_bindings": {
            "reasoningbank_commit": EXPECTED_RB_COMMIT,
            "first_party_executor_source_sha256": source_hashes,
            "r9_adapter_contract_sha256": r9.get("_sha256"),
            "r11_live_support_sha256": r11.get("_sha256"),
            "r13_writer_input_sha256": r13.get("_sha256"),
            "r14_writer_model_sha256": r14.get("_sha256"),
            "executor_transport_smoke_sha256": transport_sha,
            "executor_show_metadata_sha256": executor_show_sha,
        },
        "metadata_intervention_renderer": {
            "memory_items_source": "the exact frozen memory_items_joined UTF-8 bytes produced in the uniform R13/R14 writer stage",
            "first_party_agent_memory_semantics": "agent.py reads memory_path, strips outer whitespace, appends a constant memory-use instruction, then appends the memory file contents verbatim to the system prompt",
            "constant_legend": MEMORY_LEGEND,
            "STATUS_S_suffix": MEMORY_LEGEND + "\nstatus: S",
            "STATUS_F_suffix": MEMORY_LEGEND + "\nstatus: F",
            "renderer_template": "{memory_items_joined.strip()}\\n\\n" + MEMORY_LEGEND + "\\nstatus: {S|F}\\n",
            "arm_render_length_equal": True,
            "treatment_byte_difference_count": 1,
            "treatment_byte": {"STATUS_S": "S", "STATUS_F": "F"},
            "selected_source_record_id_equal_across_arms": True,
            "memory_items_bytes_equal_across_arms": True,
            "retrieval_disabled_for_confirmatory_execution": True,
            "fixed_source_assignment_from_R9": True,
        },
        "executor": {
            "agent_architecture": "first-party ReasoningBank WebArena GenericAgentArgs / BrowserGym",
            "model_transport": "first-party ChatOpenAI via OPENAI_BASE_URL to local Ollama OpenAI-compatible endpoint",
            "model_tag": EXPECTED_EXECUTOR_TAG,
            "executor_manifest_digest": EXPECTED_EXECUTOR_MANIFEST,
            "underlying_model_layer_digest": EXPECTED_MODEL_LAYER,
            "quantization": "Q4_K_M",
            "context_length": 32768,
            "temperature": 0.0,
            "max_new_tokens": 4096,
            "max_total_tokens": 32768,
            "max_input_tokens": 28672,
            "internal_server_retries": 1,
            "sampling_seed": None,
            "sampling_seed_reason": "temperature=0 removes intentional sampling; no post-outcome seed selection is permitted",
            "historical_relationship": {
                "R4_executor_family": "qwen2.5:32b",
                "R4_temperature": 0.6,
                "R15_temperature_deviation": "0.0 chosen prospectively to minimize within-task sampling noise and strengthen the metadata-only identification contrast",
                "first_party_run_py_default_model": "gemini-2.5-flash",
                "first_party_run_py_default_temperature": 0.7,
                "claim_source_default_executor_replication": False,
                "claim_scope": "ReasoningBank/WebArena compatibility-substrate provenance intervention using first-party agent architecture and a content-addressed local Qwen2.5-32B executor",
            },
        },
        "browsergym_runtime": {
            "task_family": "browsergym/webarena.<task_id>",
            "task_seed": 0,
            "max_steps": 30,
            "headless": True,
            "viewport": {"width": 1500, "height": 1280},
            "slow_mo_ms": 30,
            "flags": transport["flags"],
            "package_versions": transport["packages"],
            "reset_before_every_episode": True,
            "shopping_only": True,
        },
        "cohort_and_rollouts": {
            "independent_tasks": 36,
            "downstream_task_ids": cohort["downstream_task_ids"],
            "source_task_ids": cohort["source_task_ids"],
            "paired_repeats_per_arm_per_task": 2,
            "arms": ["STATUS_S", "STATUS_F"],
            "total_terminal_episodes": 144,
            "maximum_executor_completions": 4320,
            "writer_requests_before_downstream_if_authorized": 36,
            "maximum_total_local_model_requests_writer_plus_executor": 4356,
            "task_order": "exact R9 downstream_task_ids order",
            "arm_order": "counterbalanced within every task: repeat 1 reverses repeat 0; cohort-index parity chooses the first order",
            "episode_schedule": schedule,
            "outcome_adaptive_early_stop": False,
            "post_outcome_task_replacement": False,
            "post_outcome_sample_extension": False,
        },
        "source_memory_stage_gate": {
            "writer_information_contract_frozen_R13": True,
            "writer_model_realization_frozen_R14": True,
            "uniform_36_of_36_generation_required": True,
            "first_complete_parseable_writer_response_frozen": True,
            "semantic_quality_selection_or_regeneration_forbidden": True,
            "content_address_each_writer_response_and_memory_items_joined_before_any_downstream_episode": True,
            "all_36_exact_memory_bytes_required_before_any_downstream_episode": True,
            "if_any_source_memory_missing_or_unparseable_after_allowed_pre-outcome_transport_retry": "STOP_NO_DOWNSTREAM_OUTCOMES_SUPPORT_FAILURE",
        },
        "completion_and_retry_policy": {
            "confirmatory_analysis_requires_all_144_terminal_episodes": True,
            "pre_outcome_support_retry": "one exact retry allowed only if failure occurs before the first model completion, browser action, or evaluator call of that episode",
            "after_any_scientific_exposure": "no retry, no replacement, no endpoint switch; any unresolved support failure makes the whole confirmatory execution NO_VERDICT_SUPPORT_FAILURE",
            "model_internal_retry_count": 1,
            "provider_or_model_substitution": False,
            "task_substitution": False,
            "threshold_change": False,
        },
        "primary_analysis": {
            "unit": "task",
            "per_task_score_STATUS_S": "mean terminal WebArena score over the two frozen STATUS_S repeats",
            "per_task_score_STATUS_F": "mean terminal WebArena score over the two frozen STATUS_F repeats",
            "per_task_delta": "score_STATUS_S - score_STATUS_F",
            "estimand": "mean of the 36 task-level deltas",
            "primary_test": "two-sided task-level sign-flip randomization test",
            "permutations": 100000,
            "rng": "NumPy Generator(PCG64(seed=20260824))",
            "p_value": "(1 + count(abs(permuted_mean) >= abs(observed_mean))) / (100000 + 1)",
            "alpha": 0.05,
            "practical_effect_floor_abs_delta": 0.15,
            "support_if": "abs(mean_delta) >= 0.15 and p_two_sided < 0.05",
            "otherwise": "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY",
            "directional_sign_claim_predeclared": False,
            "paired_bootstrap_ci": {"repetitions": 100000, "seed": 20260825, "level": 0.95},
            "variance_policy": "No variance-adaptive sample sizing. The full capacity-capped 36-task cohort and two repeats per arm are frozen before outcomes; R9 power numbers remain sensitivity analyses, not a power guarantee.",
        },
        "claim_boundary": {
            "strongest_allowed_positive_claim": "On the frozen ReasoningBank/WebArena Shopping compatibility substrate, exposing success-versus-failure source provenance metadata while holding source memory bytes and source assignment fixed changes terminal executable behavior/performance.",
            "forbidden": [
                "exact first-party Gemini executor replication",
                "exact-as-declared Python>=3.13 ReasoningBank runtime replication",
                "source-faithful financial AgentDojo transport",
                "general provenance effect across models or runtimes",
                "pooling with R5 or the historical six-task generic cue bridge",
            ],
            "o6_l3_unblocked": False,
        },
        "execution_gate": {
            "native_metadata_field_pinned": True,
            "36_task_cohort_frozen": True,
            "live_shopping_substrate_ready": True,
            "writer_inputs_frozen": True,
            "writer_model_artifact_bound": True,
            "executor_model_artifact_bound": True,
            "executor_transport_constructed_no_completion": True,
            "rollout_and_arm_order_frozen": True,
            "request_budget_frozen": True,
            "variance_missingness_retry_randomization_policy_frozen": True,
            "exact_memory_bytes_bound": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
            "execution_permitted": False,
        },
        "scientific_verdict": "NO_VERDICT_EXECUTION_CONTRACT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r9", type=Path, required=True)
    p.add_argument("--r11", type=Path, required=True)
    p.add_argument("--r13", type=Path, required=True)
    p.add_argument("--r14", type=Path, required=True)
    p.add_argument("--executor-manifest", type=Path, required=True)
    p.add_argument("--executor-show", type=Path, required=True)
    p.add_argument("--transport-smoke", type=Path, required=True)
    p.add_argument("--reasoningbank-webarena-root", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-executor-contract-r15.json"))
    args = p.parse_args()

    def load_with_sha(path: Path) -> dict[str, Any]:
        x = json.loads(path.read_text(encoding="utf-8")); x["_sha256"] = sha256(path); return x

    r9, r11, r13, r14 = map(load_with_sha, [args.r9, args.r11, args.r13, args.r14])
    executor_manifest_sha = sha256(args.executor_manifest)
    executor_show = json.loads(args.executor_show.read_text(encoding="utf-8"))
    transport = json.loads(args.transport_smoke.read_text(encoding="utf-8"))
    source_hashes = validate_source_files(args.reasoningbank_webarena_root)
    payload = build_contract(
        r9, r11, r13, r14,
        executor_manifest_sha,
        executor_show, sha256(args.executor_show),
        transport, sha256(args.transport_smoke),
        source_hashes,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "tasks": payload["cohort_and_rollouts"]["independent_tasks"],
        "episodes": payload["cohort_and_rollouts"]["total_terminal_episodes"],
        "executor": payload["executor"]["model_tag"],
        "temperature": payload["executor"]["temperature"],
        "execution_permitted": payload["execution_gate"]["execution_permitted"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
