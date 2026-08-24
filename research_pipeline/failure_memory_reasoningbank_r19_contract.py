from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

EXPECTED_R15_SHA = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_R17_SHA = "58de4f998b16aace4ddfeef0693d88a347b293c032d997e0da471e6b92c69235"
EXECUTOR_MANIFEST = "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
PERMUTATION_SEED = 20260824
BOOTSTRAP_SEED = 20260825
PERMUTATIONS = 100_000
BOOTSTRAPS = 100_000
MAX_STEPS = 30
REPEATS_PER_ARM = 2
FUZZY_TASKS_EXPECTED = 5


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_schedule(cohort: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(cohort) != 35:
        raise RuntimeError("R19 contract expects exactly 35 template units")
    out: list[dict[str, Any]] = []
    seq = 0
    for idx, row in enumerate(cohort):
        task = str(row["r19_downstream_task_id"])
        source = str(row["source_task_id"])
        first = ("STATUS_S", "STATUS_F") if idx % 2 == 0 else ("STATUS_F", "STATUS_S")
        orders = (first, tuple(reversed(first)))
        for repeat_id, order in enumerate(orders):
            for position, arm in enumerate(order):
                out.append(
                    {
                        "sequence_index": seq,
                        "cohort_index": idx,
                        "template_id": str(row["template_id"]),
                        "task_id": task,
                        "source_task_id": source,
                        "repeat_id": repeat_id,
                        "position_in_pair": position,
                        "arm": arm,
                        "task_seed": 0,
                        "reset_before_episode": True,
                    }
                )
                seq += 1
    if len(out) != 140:
        raise RuntimeError("R19 schedule must contain 140 episodes")
    return out


def build_contract(
    r15: dict[str, Any],
    r17: dict[str, Any],
    r18c: dict[str, Any],
    candidate: dict[str, Any],
    evaluator: dict[str, Any],
    alias: dict[str, Any],
    bindings: dict[str, str],
) -> dict[str, Any]:
    if candidate["status"] != "R19_35_TEMPLATE_HYBRID_FRESH_COHORT_AVAILABLE_NEW_AUTHORITY_REQUIRED":
        raise RuntimeError("R19 candidate not qualified")
    if candidate["reopen_gate"]["execution_permitted_now"] is not False:
        raise RuntimeError("R19 candidate unexpectedly authorizes execution")
    if r18c["scientific_verdict"] != "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE":
        raise RuntimeError("R18c adjudication drift")
    if r18c["frozen_policy_application"]["single_confirmatory_attempt_consumed"] is not True:
        raise RuntimeError("prior confirmatory attempt not marked consumed")
    if r17["status"] != "UNIFORM_36_MEMORY_REALIZATION_COMPLETE_EXACT_BYTES_BOUND":
        raise RuntimeError("R17 exact memory realization unavailable")
    if evaluator["status"] != "R19_35_OF_35_NATIVE_EVALUATORS_CONSTRUCTED_ZERO_CALL":
        raise RuntimeError("R19 evaluator preflight not passed")
    if evaluator["summary"]["potential_llm_fuzzy_evaluator_tasks"] != FUZZY_TASKS_EXPECTED:
        raise RuntimeError("R19 fuzzy evaluator count drift")
    if alias["status"] != "R19_AGENT_EVALUATOR_ALIASES_AND_TOKENIZERS_PREFLIGHT_PASS_ZERO_COMPLETION":
        raise RuntimeError("R19 alias/tokenizer preflight not passed")
    if alias["ollama_registry"]["executor_manifest_digest"] != EXECUTOR_MANIFEST:
        raise RuntimeError("R19 alias executor manifest drift")

    cohort = list(candidate["cohort"])
    schedule = build_schedule(cohort)
    mem_by_source = {str(x["source_task_id"]): x for x in r17["source_memory_manifest"]}
    memory_rows = []
    for row in cohort:
        sid = str(row["source_task_id"])
        if sid not in mem_by_source:
            raise RuntimeError(f"R17 memory missing R19 source {sid}")
        m = mem_by_source[sid]
        if m["joined_memory_bytes_sha256"] != row["source_memory_joined_bytes_sha256"]:
            raise RuntimeError(f"R19 candidate/R17 memory hash mismatch for {sid}")
        memory_rows.append(
            {
                "template_id": str(row["template_id"]),
                "source_task_id": sid,
                "downstream_task_id": str(row["r19_downstream_task_id"]),
                "memory_record_sha256": m["memory_record_sha256"],
                "joined_memory_bytes_sha256": m["joined_memory_bytes_sha256"],
            }
        )

    executor = deepcopy(r15["executor"])
    if executor["executor_manifest_digest"] != EXECUTOR_MANIFEST:
        raise RuntimeError("R15 executor manifest drift")
    runtime = deepcopy(r15["browsergym_runtime"])
    renderer = deepcopy(r15["metadata_intervention_renderer"])

    agent_completion_cap = len(schedule) * MAX_STEPS
    fuzzy_evaluator_completion_cap = FUZZY_TASKS_EXPECTED * 4 * MAX_STEPS
    benchmark_completion_cap = agent_completion_cap + fuzzy_evaluator_completion_cap
    support_smoke_completion_cap = 2

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "contract_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-CONFIRMATORY-CONTRACT",
        "recorded_date": "2026-08-24",
        "status": "R19_PREOUTCOME_CONTRACT_FROZEN_NEW_AUTHORITY_AND_SYNTHETIC_SMOKES_REQUIRED",
        "role": "NEW_EXPERIMENT_PRE_OUTCOME_CONTRACT_NO_EXECUTION_AUTHORITY",
        "scientific_relationship": "NEW_EXPERIMENT_AFTER_R18_STOP_NOT_RETRY_NOT_R5_RESCUE",
        "bindings": bindings,
        "prior_attempt_boundary": {
            "R18c_status": r18c["status"],
            "R18c_scientific_verdict": r18c["scientific_verdict"],
            "R18_single_confirmatory_attempt_consumed": True,
            "R18c_exposed_template_id": "136",
            "R18c_exposed_task_id": "166",
            "R18_R18b_R18c_failure_chain_must_be_disclosed": True,
            "R18c_action_step_reward_artifacts_used_for_R19_selection": False,
            "R18c_task_template_excluded_from_R19": True,
            "R16_authority_reusable": False,
        },
        "cohort": {
            "independent_tasks": 35,
            "templates": [str(x["template_id"]) for x in cohort],
            "downstream_task_ids": [str(x["r19_downstream_task_id"]) for x in cohort],
            "source_task_ids": [str(x["source_task_id"]) for x in cohort],
            "new_downstream_ids_relative_to_R9": candidate["capacity"]["new_downstream_ids_relative_to_R9"],
            "retained_unexposed_R9_downstream_ids": candidate["capacity"]["retained_unexposed_R9_downstream_ids"],
            "all_source_distinct_from_downstream": True,
            "shopping_only": True,
            "all_native_evaluators_preconstructed_zero_call": True,
            "full_35_task_cohort_required_for_confirmatory_analysis": True,
            "outcome_adaptive_task_replacement": False,
            "post_outcome_sample_extension": False,
        },
        "source_memories": {
            "reuse_R17_exact_pre_outcome_memory_bytes": True,
            "new_writer_calls": 0,
            "memory_regeneration": False,
            "memory_edit": False,
            "records": memory_rows,
        },
        "metadata_intervention_renderer": renderer,
        "executor": {
            **executor,
            "agent_openai_model_name_for_R19": "openai/gpt-4",
            "agent_ollama_alias": "gpt-4:latest",
            "evaluator_hardcoded_openai_model_name": "gpt-4-1106-preview",
            "evaluator_ollama_alias": "gpt-4-1106-preview:latest",
            "both_aliases_manifest_identical_to_R15_executor": True,
            "automatic_model_or_manifest_substitution": False,
        },
        "browsergym_runtime": runtime,
        "rollouts": {
            "paired_repeats_per_arm_per_task": REPEATS_PER_ARM,
            "arms": ["STATUS_S", "STATUS_F"],
            "total_terminal_episodes": len(schedule),
            "task_order": "exact R19 cohort order",
            "arm_order": "counterbalanced within every task: repeat 1 reverses repeat 0; cohort-index parity chooses repeat-0 first arm",
            "episode_schedule": schedule,
            "reset_before_every_episode": True,
            "task_seed": 0,
        },
        "model_call_budget": {
            "new_writer_completions": 0,
            "agent_completion_upper_bound": agent_completion_cap,
            "fuzzy_evaluator_tasks": FUZZY_TASKS_EXPECTED,
            "fuzzy_evaluator_completion_upper_bound": fuzzy_evaluator_completion_cap,
            "benchmark_local_model_completion_upper_bound": benchmark_completion_cap,
            "pre_benchmark_synthetic_support_completion_upper_bound": support_smoke_completion_cap,
            "maximum_total_new_local_model_completions_if_authorized": benchmark_completion_cap + support_smoke_completion_cap,
            "evaluator_calls_are_not_independent_samples": True,
        },
        "mandatory_prebenchmark_support_gate": {
            "repeat_R19_alias_registry_and_tokenizer_preflight": True,
            "repeat_live_Shopping_reset_and_BrowserGym_zero-action_smoke": True,
            "two_synthetic_nonbenchmark_completions_after_new_authority": [
                {
                    "alias": "gpt-4",
                    "purpose": "verify agent OpenAI-compatible completion transport",
                    "benchmark_content_in_prompt": False,
                    "acceptance": "HTTP success and non-empty assistant content only; semantic content ignored",
                },
                {
                    "alias": "gpt-4-1106-preview",
                    "purpose": "verify evaluator hardcoded model-name completion transport",
                    "benchmark_content_in_prompt": False,
                    "acceptance": "HTTP success and non-empty assistant content only; semantic content ignored",
                },
            ],
            "synthetic_smokes_executed_now": False,
            "failure_before_any_benchmark_episode": "support failure; do not open R19 scientific outcomes",
        },
        "completion_and_retry_policy": {
            "confirmatory_analysis_requires_all_140_terminal_episodes": True,
            "pre_episode_support_failure_before_first_model_completion_browser_action_or_evaluator_call": "one exact retry allowed only under the newly authorized R19 contract, without task/model/memory/threshold change",
            "after_any_R19_scientific_exposure": "no retry, no replacement, no endpoint switch; unresolved support failure makes R19 NO_VERDICT_SUPPORT_FAILURE",
            "model_internal_retry_count": 1,
            "provider_or_model_substitution": False,
            "task_substitution": False,
            "threshold_change": False,
        },
        "primary_analysis": {
            "unit": "task",
            "independent_n": 35,
            "episode_count_is_independent_n": False,
            "per_task_score_STATUS_S": "mean terminal WebArena score over the two frozen STATUS_S repeats",
            "per_task_score_STATUS_F": "mean terminal WebArena score over the two frozen STATUS_F repeats",
            "per_task_delta": "score_STATUS_S - score_STATUS_F",
            "estimand": "mean of the 35 task-level deltas",
            "primary_test": "two-sided task-level sign-flip randomization test",
            "permutations": PERMUTATIONS,
            "rng": f"NumPy Generator(PCG64(seed={PERMUTATION_SEED}))",
            "p_value": "(1 + count(abs(permuted_mean) >= abs(observed_mean))) / (100000 + 1)",
            "alpha": 0.05,
            "practical_effect_floor_abs_delta": 0.15,
            "support_if": "all 140 episodes complete AND abs(mean_delta) >= 0.15 AND p_two_sided < 0.05",
            "otherwise": "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY",
            "directional_sign_claim_predeclared": False,
            "paired_bootstrap_ci": {"repetitions": BOOTSTRAPS, "seed": BOOTSTRAP_SEED, "level": 0.95},
            "variance_policy": "No variance-adaptive sample sizing; n=35 and two repeats per arm are frozen before any R19 outcome. The power numbers in the R19 capacity receipt remain sensitivity analyses only.",
        },
        "secondary_descriptive": {
            "first_executable_action_divergence": True,
            "directional_STATUS_S_vs_STATUS_F": True,
            "may_replace_or_rescue_primary_terminal_gate": False,
        },
        "claim_boundary": {
            "strongest_allowed_positive_claim_if_gate_passes": "On a new 35-template ReasoningBank/WebArena Shopping compatibility-substrate cohort, exposing only source-outcome provenance status while reusing fixed pre-outcome R17 memory bytes changes terminal task performance under the frozen local Qwen executor.",
            "new_independent_memory_realization_claim": False,
            "first_party_default_Gemini_policy_replication_claim": False,
            "exact_Python313_runtime_claim": False,
            "financial_AgentDojo_L3_claim": False,
            "general_cross_model_or_cross_runtime_provenance_claim": False,
        },
        "execution_gate": {
            "R18_current_attempt_closed": True,
            "R19_cohort_frozen": True,
            "R17_memory_bytes_bound": True,
            "R19_evaluator_preflight_pass": True,
            "R19_alias_tokenizer_preflight_pass": True,
            "R19_schedule_analysis_and_budgets_frozen": True,
            "new_explicit_scientific_authority": False,
            "new_explicit_experiment_model_call_authority": False,
            "two_synthetic_support_completions_passed": False,
            "execution_permitted": False,
        },
        "scientific_verdict": "NO_VERDICT_R19_CONTRACT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_completions": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r15", type=Path, required=True)
    p.add_argument("--r17", type=Path, required=True)
    p.add_argument("--r18a", type=Path, required=True)
    p.add_argument("--r18b", type=Path, required=True)
    p.add_argument("--r18c", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--evaluator-preflight", type=Path, required=True)
    p.add_argument("--alias-preflight", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json"))
    args = p.parse_args()
    if sha256_file(args.r15) != EXPECTED_R15_SHA:
        raise RuntimeError("R15 digest mismatch")
    if sha256_file(args.r17) != EXPECTED_R17_SHA:
        raise RuntimeError("R17 digest mismatch")
    paths = {
        "r15": args.r15,
        "r17": args.r17,
        "r18a": args.r18a,
        "r18b": args.r18b,
        "r18c": args.r18c,
        "candidate": args.candidate,
        "evaluator_preflight": args.evaluator_preflight,
        "alias_preflight": args.alias_preflight,
    }
    docs = {k: json.loads(v.read_text(encoding="utf-8")) for k, v in paths.items()}
    bindings = {k + "_sha256": sha256_file(v) for k, v in paths.items()}
    contract = build_contract(
        docs["r15"], docs["r17"], docs["r18c"], docs["candidate"], docs["evaluator_preflight"], docs["alias_preflight"], bindings
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": contract["status"],
        "n": contract["cohort"]["independent_tasks"],
        "episodes": contract["rollouts"]["total_terminal_episodes"],
        "agent_cap": contract["model_call_budget"]["agent_completion_upper_bound"],
        "evaluator_cap": contract["model_call_budget"]["fuzzy_evaluator_completion_upper_bound"],
        "execution_permitted": contract["execution_gate"]["execution_permitted"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
