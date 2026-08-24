#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
SOURCE_TASKS = ["21", "22", "23", "25"]
FUTURE_TASKS = ["164", "385", "387", "388"]

SOURCE_ROOT = Path("/home/wyt/code/agent-self-evolution-observatory-discovery-benchmark-20260821/generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena")
MEMORY_PY = SOURCE_ROOT / "src/walt/benchmarks/wa/memory.py"
RETRIEVER_PY = SOURCE_ROOT / "src/walt/browser_use/custom/retriever/SimpleRetriever.py"
AEVAL_PY = SOURCE_ROOT / "src/walt/benchmarks/wa/aeval.py"
SHOPPING_CONFIG = SOURCE_ROOT / "experiment_configs/wa/wa_reasoningbank/shuffle1/run1/shopping.yaml"
F2R1 = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f2r1-confirmatory.json")
O5 = HERE / "o5-manuscript-evidence.json"
O6 = HERE / "o6-final-evidence.json"
STAGE2_RUNNER = HERE / "run_o6_cross_writer_stage2.py"
OUTPUT = HERE / "o6-full-bank-corruption-reduction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_text(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise RuntimeError(f"source contract drift: {label}")


def main() -> int:
    memory_text = MEMORY_PY.read_text(encoding="utf-8")
    retriever_text = RETRIEVER_PY.read_text(encoding="utf-8")
    aeval_text = AEVAL_PY.read_text(encoding="utf-8")
    config_text = SHOPPING_CONFIG.read_text(encoding="utf-8")
    stage2_text = STAGE2_RUNNER.read_text(encoding="utf-8")

    source_checks = {
        "retrieval_index_uses_task_description_only": 'task_pools = [v["task_description"] for v in self.reasoningbank_memory.values()]' in memory_text,
        "retrieval_query_is_current_intent": 'self.result = _retrieve_docs(retriever, intent, self.args, task_logger)' in memory_text,
        "retrieved_task_description_maps_to_memory_after_retrieval": 'related_memory_items = reverse_reasoningbank_memory[r]' in memory_text,
        "reward_label_selects_writer_mode": 'mode = "success" if int(score) == 1 else "failure"' in memory_text,
        "memory_entry_keeps_task_intent_as_retrieval_key": 'additive_textual_memory._add_document(task_id, intent, reasoningbank_memory_summary)' in memory_text,
        "default_retriever_model_minilm": 'parser.add_argument("--retriever_model_name", type=str, default="all-MiniLM-L6-v2")' in aeval_text,
        "default_top_k_one": 'parser.add_argument("--retriever_top_k", type=int, default=1)' in aeval_text,
        "default_threshold_point_three": 'parser.add_argument("--retriever_threshold", type=float, default=0.3)' in aeval_text,
        "simple_retriever_embeds_documents_not_memory_payload": 'new_embeddings = self.embedder.encode(new_docs_to_add, convert_to_numpy=True)' in retriever_text,
        "simple_retriever_topk_threshold": 'similarities, indices = self.index.search(query_embedding, top_k)' in retriever_text and 'if sim >= threshold:' in retriever_text,
        "shopping_config_reasoningbank": 'method: reasoningbank' in config_text,
        "shopping_config_memory_human_message": 'memory_as_human_message: true' in config_text,
        "shopping_config_does_not_override_topk": 'retriever_top_k' not in config_text,
        "shopping_config_does_not_override_threshold": 'retriever_threshold' not in config_text,
        "current_fixed_evidence_prompt_is_not_source_wrapper": 'REUSABLE MEMORY:' in stage2_text and 'Retrieved from past task' not in stage2_text,
    }
    if not all(source_checks.values()):
        bad = [k for k,v in source_checks.items() if not v]
        raise RuntimeError("source checks failed: " + ", ".join(bad))

    f2 = load(F2R1)
    o5 = load(O5)
    o6 = load(O6)
    cell_support = {(str(r["source_memory_task"]), str(r["future_task"])) for r in f2["cell_results"]}
    expected_support = {(s,f) for s in SOURCE_TASKS for f in FUTURE_TASKS}
    if cell_support != expected_support:
        raise RuntimeError("F2R1 4x4 support drift")
    if int(o5["execution_accounting"]["recovery_scientifically_usable_units"]) != 32:
        raise RuntimeError("O5 no-memory support drift")
    if o6["claim_boundary"]["terminal_cross_writer_generalization_supported"] is not False:
        raise RuntimeError("O6 cross-writer boundary drift")

    # Structural proof over every 4-bit reward-corruption mask. Retrieval source is left symbolic:
    # for any fixed top-1 choice s*, injected reward mode depends only on mask[s*].
    masks = []
    for bits in itertools.product(("success", "failure"), repeat=len(SOURCE_TASKS)):
        mask = dict(zip(SOURCE_TASKS, bits))
        masks.append(mask)

    symbolic_rows = []
    factorization_pass = True
    for selected_source in SOURCE_TASKS:
        contexts = {}
        for mask in masks:
            selected_label = mask[selected_source]
            key = tuple(mask[s] for s in SOURCE_TASKS)
            contexts[key] = f"source={selected_source}|label={selected_label}"
        unique_contexts = sorted(set(contexts.values()))
        expected = [f"source={selected_source}|label=failure", f"source={selected_source}|label=success"]
        ok = unique_contexts == expected
        factorization_pass = factorization_pass and ok
        symbolic_rows.append({
            "selected_source": selected_source,
            "masks_enumerated": len(contexts),
            "unique_injected_memory_conditions": unique_contexts,
            "unique_condition_count": len(unique_contexts),
            "all_nonselected_mask_bits_causally_inert_given_retrieval": ok,
        })
    # Threshold miss is also mask invariant because the retriever sees only task descriptions.
    symbolic_rows.append({
        "selected_source": None,
        "masks_enumerated": len(masks),
        "unique_injected_memory_conditions": ["no_memory"],
        "unique_condition_count": 1,
        "all_mask_bits_causally_inert_given_retrieval": True,
    })
    if not factorization_pass:
        raise RuntimeError("symbolic top-1 factorization failed")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "matched-simplification-reduction",
        "paper_id": PAPER_ID,
        "objection_id": "PROXY-O6",
        "candidate_extension": "end-to-end full-memory-bank corruption-mask replication",
        "status": "STOP_FULL_BANK_CORRUPTION_MASK_INTERACTION_BY_TOP1_LABEL_INVARIANT_RETRIEVAL_REDUCTION",
        "source_bindings": {
            "webarena_reasoningbank_memory_py_sha256": sha(MEMORY_PY),
            "webarena_simple_retriever_py_sha256": sha(RETRIEVER_PY),
            "webarena_aeval_py_sha256": sha(AEVAL_PY),
            "webarena_reasoningbank_shopping_config_sha256": sha(SHOPPING_CONFIG),
            "f2r1_confirmatory_sha256": sha(F2R1),
            "o5_no_memory_evidence_sha256": sha(O5),
            "o6_cross_writer_evidence_sha256": sha(O6),
            "current_stage2_runner_sha256": sha(STAGE2_RUNNER),
        },
        "released_mechanism_facts": {
            "source_checks": source_checks,
            "retrieval_key": "task_description",
            "reward_conditioned_memory_document_used_in_retrieval_embedding": False,
            "default_retriever_model": "all-MiniLM-L6-v2",
            "default_top_k": 1,
            "default_similarity_threshold": 0.3,
            "reward_label_changes": "memory writer mode and resulting document payload",
            "reward_label_does_not_change": ["task_id", "task_description retrieval key", "retriever query intent", "retriever top_k", "retriever threshold"],
            "injected_memory_count_when_retrieval_succeeds": 1,
        },
        "symbolic_factorization": {
            "source_set": SOURCE_TASKS,
            "future_set": FUTURE_TASKS,
            "corruption_masks": 16,
            "proof_statement": "For any future task f and any top-1 retrieval result R(f)=s*, the released retriever computes R from task-description embeddings that are invariant to the reward corruption mask. The injected memory payload is therefore M[s*, mask[s*]]. All mask bits for sources other than s* are causally inert for that episode. If thresholding returns no source, all mask bits are inert and the episode is no-memory.",
            "enumeration": symbolic_rows,
            "multi_memory_interaction_identifiable_under_released_top1_mechanism": False,
            "mask_can_change_retrieval_identity": False,
            "mask_can_change_number_of_retrieved_memories": False,
            "nonselected_memory_bits_can_affect_injected_prompt": False,
        },
        "relationship_to_existing_evidence": {
            "f2r1_covers_all_four_source_by_four_future_single_memory_label_contrasts": True,
            "o5_covers_no_memory_branch_under_current_fixed_evidence_prompt": True,
            "current_fixed_evidence_prompt_byte_equivalent_to_source_reasoningbank_wrapper": False,
            "therefore_existing_outcomes_are_not_claimed_as_source_faithful_end_to_end_retrieval_replay": True,
            "what_is_reduced": "the scientific rationale for a multi-bit/full-bank corruption-interaction sweep on the released top-1 label-invariant retrieval substrate",
            "what_remains_distinct": "source-faithful retrieval/interface transport and live-browser continuation; this is a transport/replication question rather than a corruption-interaction question",
        },
        "economy_decision": {
            "new_provider_calls_authorized": 0,
            "new_rollouts_authorized": 0,
            "decision": "STOP_BEFORE_PROVIDER_CALLS",
            "reason": "A full-bank mask sweep cannot expose interactions among corrupted memories when only one label-invariant-keyed memory is retrieved. Expanding the bank adds source-coverage/generalization, not a new corruption interaction variable.",
        },
        "reopen_only_if": [
            "the exact target substrate retrieves more than one memory per future episode (top_k > 1 with multiple injected items)",
            "retrieval keys or embeddings depend on reward-conditioned memory content or label",
            "reward condition changes bank admission/deletion/membership before retrieval in a way not reducible to a single selected entry",
            "a compositional memory interface jointly injects multiple corrupted entries",
        ],
        "scope_boundary": {
            "changing_top_k_or_retrieval_key_to_create_interaction_would_change_substrate": True,
            "such_a_change_requires_new_paper_contract_not_targeted_C1_repair": True,
            "live_webarena_endpoint_support_debt_unchanged": True,
            "cross_writer_failed_terminal_generalization_gate_unchanged": True,
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "claim_expansion_authority": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "released_mechanism_facts": payload["released_mechanism_facts"],
        "factorization_pass": factorization_pass,
        "symbolic_rows": symbolic_rows,
        "decision": payload["economy_decision"],
        "what_remains_distinct": payload["relationship_to_existing_evidence"]["what_remains_distinct"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
