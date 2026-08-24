from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_readiness(
    r18c: dict[str, Any],
    candidate: dict[str, Any],
    evaluator: dict[str, Any],
    alias: dict[str, Any],
    contract: dict[str, Any],
    public_status: dict[str, Any],
    hashes: dict[str, str],
) -> dict[str, Any]:
    if r18c["scientific_verdict"] != "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE":
        raise RuntimeError("R18c verdict drift")
    if r18c["frozen_policy_application"]["single_confirmatory_attempt_consumed"] is not True:
        raise RuntimeError("R18 attempt not consumed")
    if candidate["capacity"]["R19_independent_template_units"] != 35:
        raise RuntimeError("R19 candidate capacity drift")
    if evaluator["summary"]["native_evaluators_constructed"] != 35 or evaluator["summary"]["native_evaluators_called"] != 0:
        raise RuntimeError("R19 evaluator preflight drift")
    if alias["ollama_registry"]["all_required_aliases_manifest_identical"] is not True or alias["tokenizer"]["all_lookup_pass"] is not True:
        raise RuntimeError("R19 alias/tokenizer preflight drift")
    if contract["execution_gate"]["execution_permitted"] is not False:
        raise RuntimeError("R19 unexpectedly executable")
    if public_status["claim_boundary"]["O5_disposition"] != "REQUIRES_SCIENTIFIC_REOPEN":
        raise RuntimeError("O5 disposition drift")

    closed = {
        "R18_prior_attempt_closed_no_retry": True,
        "R19_35_task_cohort_frozen": True,
        "R18_exposed_template_excluded": True,
        "R17_exact_memory_bytes_reused_without_regeneration": True,
        "all_R19_downstream_tasks_source_distinct": True,
        "shopping_live_substrate_previously_verified": True,
        "35_native_evaluators_constructed_zero_call": True,
        "agent_and_evaluator_alias_manifest_equality_preflight_pass": True,
        "gpt4_and_gpt4_1106_preview_tokenizer_lookup_pass": True,
        "140_episode_schedule_frozen": True,
        "task_level_primary_analysis_frozen": True,
        "agent_and_fuzzy_evaluator_budgets_frozen": True,
        "post_exposure_no_retry_policy_frozen": True,
        "claim_boundary_frozen": True,
    }
    if not all(closed.values()):
        raise RuntimeError("readiness closed-gate invariant failed")

    missing = {
        "new_explicit_scientific_authority": False,
        "new_explicit_experiment_model_call_authority": False,
        "repeat_zero_call_alias_tokenizer_and_live_reset_preflight_immediately_before_run": False,
        "authorized_nonbenchmark_gpt4_synthetic_completion_smoke": False,
        "authorized_nonbenchmark_gpt4_1106_preview_synthetic_completion_smoke": False,
    }

    requested_scope = {
        "object": "R19 new 35-template L2B experiment; not a retry of R18",
        "cohort": {
            "independent_tasks": 35,
            "terminal_episodes": 140,
            "new_downstream_tasks_relative_to_R9": 30,
            "retained_never_executed_downstream_tasks": 5,
            "R18c_exposed_template_excluded": True,
        },
        "treatment": "STATUS_S versus STATUS_F only; frozen memory record ID/order and memory_items bytes identical across arms",
        "memory": "reuse R17 exact frozen memory bytes; no regeneration or editing",
        "executor": "frozen local Qwen executor and digest-identical gpt-4/gpt-4-1106-preview aliases as specified by R19 contract",
        "support_smokes_before_benchmark": 2,
        "benchmark_agent_completion_upper_bound": 4200,
        "benchmark_fuzzy_evaluator_completion_upper_bound": 600,
        "maximum_new_local_model_completions_including_smokes": 4802,
        "primary_analysis": "two-sided task-level sign-flip, 100000 permutations; |mean delta| >= 0.15 and p < 0.05; full 140 episodes required",
        "forbidden": [
            "retry or reuse R18 as the confirmatory attempt",
            "include template136/task166 in R19",
            "change tasks after outcomes",
            "regenerate or edit memory after outcomes",
            "replace model/manifest/provider after scientific exposure",
            "change effect floor, alpha, randomization method, or endpoint after outcomes",
            "use incomplete R19 as negative/no-effect authority",
            "pool R5, historical bridge, R18, or R19 as one sample",
            "claim exact Python>=3.13 runtime replication",
            "claim first-party default Gemini policy replication",
            "claim financial AgentDojo L3 transport",
            "claim broad cross-model or cross-runtime provenance generality",
        ],
    }

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-READINESS-GATE",
        "recorded_date": "2026-08-24",
        "status": "READY_FOR_NEW_R19_AUTHORITY_NOT_READY_FOR_EXECUTION",
        "role": "FINAL_PRE_AUTHORITY_READINESS_GATE",
        "bindings": hashes,
        "closed_preoutcome_gates": closed,
        "still_required": missing,
        "readiness": {
            "engineering_contract_ready": True,
            "scientific_object_ready_for_explicit_authority_decision": True,
            "execution_ready_now": False,
            "current_scientific_authority": False,
            "current_experiment_model_call_authority": False,
            "R18_authority_reusable": False,
            "R18_attempt_retriable": False,
            "R19_is_new_experiment": True,
        },
        "exact_scope_if_future_authority_is_granted": requested_scope,
        "authority_semantics": {
            "generic_continuation_language_is_not_treated_as_new_R19_scientific_authority": True,
            "new_authority_must_explicitly_identify_R19_or_equivalent_scope": True,
            "new_authority_must_cover_scientific_execution_and_model_browser_evaluator_calls": True,
            "new_authority_must_not_imply_claim_support_in_advance": True,
        },
        "next_if_authorized": [
            "Re-run zero-call alias/tokenizer and live Shopping reset/BrowserGym support preflights.",
            "Run exactly two fixed nonbenchmark synthetic completion smokes: gpt-4 and gpt-4-1106-preview; inspect only transport success/non-empty response, not semantic content.",
            "If both smokes pass before benchmark exposure, execute the frozen 140-episode R19 schedule exactly once.",
            "Require all 140 valid terminal episodes for confirmatory analysis; otherwise apply the frozen fail-closed policy.",
        ],
        "scientific_verdict": "NO_VERDICT_PRE_AUTHORITY_READINESS_ONLY",
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
    for name in ("r18c", "candidate", "evaluator", "alias", "contract", "public_status"):
        p.add_argument("--" + name.replace("_", "-"), dest=name, type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-readiness.json"))
    args = p.parse_args()
    names = ("r18c", "candidate", "evaluator", "alias", "contract", "public_status")
    paths = {name: getattr(args, name) for name in names}
    docs = {name: load(path) for name, path in paths.items()}
    hashes = {name + "_sha256": sha256_file(path) for name, path in paths.items()}
    out = build_readiness(
        docs["r18c"], docs["candidate"], docs["evaluator"], docs["alias"], docs["contract"], docs["public_status"], hashes
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "engineering_ready": out["readiness"]["engineering_contract_ready"],
        "authority_decision_ready": out["readiness"]["scientific_object_ready_for_explicit_authority_decision"],
        "execution_ready": out["readiness"]["execution_ready_now"],
        "authority": out["authority"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
