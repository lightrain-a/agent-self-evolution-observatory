from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FORBIDDEN_PUBLIC_SUBSTRINGS = [
    "/data/",
    "/home/",
    "wyt@",
    "10.42.",
    "192.168.",
    "active-project-conversation",
    "source_message_ref",
    "run_root",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_public(docs: dict[str, dict[str, Any]], hashes: dict[str, str]) -> dict[str, Any]:
    r12, r13, r14, r15 = (docs[x] for x in ("r12", "r13", "r14", "r15"))
    r16, r17, r18a, r18b, r18c = (docs[x] for x in ("r16", "r17", "r18a", "r18b", "r18c"))
    r19c, r19e, r19a, r19x = (docs[x] for x in ("r19_candidate", "r19_evaluator", "r19_alias", "r19_contract"))

    if r17["status"] != "UNIFORM_36_MEMORY_REALIZATION_COMPLETE_EXACT_BYTES_BOUND":
        raise RuntimeError("R17 status drift")
    if r18c["scientific_verdict"] != "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE":
        raise RuntimeError("R18c status drift")
    if r19x["execution_gate"]["execution_permitted"] is not False:
        raise RuntimeError("R19 unexpectedly executable")

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "public_status_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-PUBLIC-STATUS-R19",
        "recorded_date": "2026-08-24",
        "status": "L2B_R18_NO_VERDICT_R19_NEW_EXPERIMENT_CANDIDATE_NOT_AUTHORIZED",
        "purpose": "Public, double-blind-safe projection of the post-R11 L2B evidence state. It contains no raw memory text, browser action content, internal paths, host addresses, or authority-source identifiers.",
        "source_receipt_sha256": hashes,
        "historical_R5_and_bridge": {
            "R5_exact_information_support": "5/10, zero calls, NO_VERDICT_SUPPORT_FAILURE",
            "six_task_explicit_cue_bridge": "144/144 calls, terminal difference 0, permutation p=1 in both directions, INCONCLUSIVE_NO_NEGATIVE_AUTHORITY",
            "pooling_with_R17_R18_R19": False,
        },
        "R12_R15_preexecution_closure": {
            "R12_local_exact_memory_coverage_before_new_writer": r12["summary"]["exact_reasoningbank_memory_coverage_for_execution"],
            "R13_writer_inputs": {
                "source_tasks": r13["summary"]["source_tasks"],
                "compact_steps": r13["summary"]["total_executed_steps_in_compact_inputs"],
                "action_objects": r13["summary"]["total_executed_action_objects"],
                "all_content_addressed": r13["summary"]["all_writer_inputs_content_addressed"],
            },
            "R14_writer_model": {
                "status": r14["status"],
                "manifest_digest": r14["prospective_writer_realization"]["manifest_digest"],
                "family": r14["prospective_writer_realization"]["family"],
                "parameter_size": r14["prospective_writer_realization"]["parameter_size"],
                "quantization": r14["prospective_writer_realization"]["quantization"],
                "historical_R6_binary_identity_claimed": False,
            },
            "R15_executor_contract": {
                "status": r15["status"],
                "executor_manifest_digest": r15["executor"]["executor_manifest_digest"],
                "independent_tasks": r15["cohort_and_rollouts"]["independent_tasks"],
                "terminal_episodes": r15["cohort_and_rollouts"]["total_terminal_episodes"],
                "primary_test": r15["primary_analysis"]["primary_test"],
                "effect_floor": r15["primary_analysis"]["practical_effect_floor_abs_delta"],
                "alpha": r15["primary_analysis"]["alpha"],
            },
        },
        "R16_R18_attempt": {
            "bounded_execution_authority_existed_for_R17_R18": r16["status"] == "EXTERNAL_HUMAN_BOUNDED_EXECUTION_AUTHORITY_VALID",
            "R17_writer_realization": {
                "status": r17["status"],
                "source_tasks_complete": r17["execution"]["source_tasks_complete"],
                "writer_calls": r17["execution"]["model_calls_executed"],
                "transport_retries": r17["execution"]["transport_retries"],
                "semantic_retries": r17["execution"]["semantic_retries"],
                "exact_memory_bytes_bound": r17["structure"]["exact_memory_bytes_bound_for_all_36_sources"],
                "raw_memory_text_in_public_projection": False,
            },
            "R18_support_chain": [
                {
                    "stage": "R18a",
                    "status": r18a["status"],
                    "scientific_exposure": False,
                    "scientific_verdict": r18a["scientific_verdict"],
                },
                {
                    "stage": "R18b",
                    "status": r18b["status"],
                    "executor_completions": 0,
                    "scientific_verdict": r18b["scientific_verdict"],
                },
                {
                    "stage": "R18c",
                    "status": r18c["status"],
                    "scientific_exposure": True,
                    "terminal_score_valid": r18c["failure"]["terminal_score_valid"],
                    "browsergym_steps_before_support_failure": r18c["failure"]["browsergym_n_steps"],
                    "failure_class": r18c["failure"]["class"],
                    "action_content_in_public_projection": False,
                    "scientific_verdict": r18c["scientific_verdict"],
                    "retry_current_attempt": False,
                    "continue_remaining_schedule": False,
                },
            ],
            "current_R18_confirmatory_attempt": "STOPPED_NO_VERDICT",
            "support_failure_is_scientific_negative": False,
        },
        "R19_new_experiment_candidate": {
            "status": r19c["status"],
            "scientific_relationship": r19c["scientific_relationship"],
            "independent_template_units": r19c["capacity"]["R19_independent_template_units"],
            "new_downstream_ids_relative_to_R9": r19c["capacity"]["new_downstream_ids_relative_to_R9"],
            "retained_unexposed_R9_downstream_ids": r19c["capacity"]["retained_unexposed_R9_downstream_ids"],
            "R18c_exposed_templates_excluded": r19c["capacity"]["R18c_exposed_templates_excluded"],
            "all_source_distinct_from_downstream": r19c["capacity"]["all_source_distinct_from_downstream"],
            "all_downstream_unique": r19c["capacity"]["all_downstream_ids_unique"],
            "shopping_only": r19c["capacity"]["all_downstream_tasks_shopping_only"],
            "source_status_counts": r19c["capacity"]["source_native_status_counts"],
            "power_sensitivity": r19c["power_sensitivity_only"]["scenarios"],
            "unconditional_80pct_power_claim": False,
        },
        "R19_support_preflights": {
            "native_evaluators": {
                "status": r19e["status"],
                "constructed": r19e["summary"]["native_evaluators_constructed"],
                "called": r19e["summary"]["native_evaluators_called"],
                "semantic_config_matches": r19e["summary"]["semantic_config_matches"],
                "fuzzy_evaluator_tasks": r19e["summary"]["potential_llm_fuzzy_evaluator_tasks"],
                "max_fuzzy_evaluator_calls": r19e["summary"]["maximum_fuzzy_evaluator_model_calls_under_4_episodes_x_30_steps"],
            },
            "aliases_and_tokenizers": {
                "status": r19a["status"],
                "executor_manifest_digest": r19a["ollama_registry"]["executor_manifest_digest"],
                "all_aliases_manifest_identical": r19a["ollama_registry"]["all_required_aliases_manifest_identical"],
                "tokenizer_lookup_pass": r19a["tokenizer"]["all_lookup_pass"],
                "model_completions_in_preflight": 0,
            },
        },
        "R19_frozen_contract": {
            "status": r19x["status"],
            "independent_tasks": r19x["cohort"]["independent_tasks"],
            "terminal_episodes": r19x["rollouts"]["total_terminal_episodes"],
            "agent_completion_upper_bound": r19x["model_call_budget"]["agent_completion_upper_bound"],
            "fuzzy_evaluator_completion_upper_bound": r19x["model_call_budget"]["fuzzy_evaluator_completion_upper_bound"],
            "prebenchmark_synthetic_support_completions": r19x["model_call_budget"]["pre_benchmark_synthetic_support_completion_upper_bound"],
            "maximum_new_local_model_completions_if_authorized": r19x["model_call_budget"]["maximum_total_new_local_model_completions_if_authorized"],
            "primary_test": r19x["primary_analysis"]["primary_test"],
            "effect_floor": r19x["primary_analysis"]["practical_effect_floor_abs_delta"],
            "alpha": r19x["primary_analysis"]["alpha"],
            "new_explicit_scientific_authority": False,
            "new_explicit_experiment_authority": False,
            "execution_permitted": False,
        },
        "claim_boundary": {
            "O5_disposition": "REQUIRES_SCIENTIFIC_REOPEN",
            "current_L2_scientific_verdict": "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE",
            "R19_is_capacity_and_contract_evidence_not_effect_evidence": True,
            "historical_R5_bridge_cannot_rescue": True,
            "no_exact_Python313_claim": True,
            "no_first_party_default_Gemini_policy_replication_claim": True,
            "no_financial_AgentDojo_L3_claim": True,
            "no_general_cross_model_or_cross_runtime_provenance_claim": True,
        },
        "public_redaction": {
            "raw_memory_text": False,
            "browser_action_content": False,
            "internal_run_paths": False,
            "host_or_ip_addresses": False,
            "authority_source_identifiers": False,
        },
    }


def assert_public_safe(obj: dict[str, Any]) -> None:
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    hits = [x for x in FORBIDDEN_PUBLIC_SUBSTRINGS if x in text]
    if hits:
        raise RuntimeError(f"public projection leakage: {hits}")


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("r12", "r13", "r14", "r15", "r16", "r17", "r18a", "r18b", "r18c", "r19_candidate", "r19_evaluator", "r19_alias", "r19_contract"):
        p.add_argument("--" + name.replace("_", "-"), dest=name, type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-public-status-r19.json"))
    args = p.parse_args()
    names = ("r12", "r13", "r14", "r15", "r16", "r17", "r18a", "r18b", "r18c", "r19_candidate", "r19_evaluator", "r19_alias", "r19_contract")
    paths = {name: getattr(args, name) for name in names}
    docs = {name: load(path) for name, path in paths.items()}
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    out = build_public(docs, hashes)
    assert_public_safe(out)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "R18": out["R16_R18_attempt"]["current_R18_confirmatory_attempt"],
        "R19_n": out["R19_new_experiment_candidate"]["independent_template_units"],
        "R19_execution": out["R19_frozen_contract"]["execution_permitted"],
        "public_safe": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
