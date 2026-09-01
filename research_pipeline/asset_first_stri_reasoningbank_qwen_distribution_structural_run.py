"""Freeze and execute retrieval, structural qualification, and final task allocation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_qualify import dataset_rows
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_retrieval import (
    FrozenQwenEmbedder, detailed_query, retrieval_receipt,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_structural import (
    complete_request, structural_receipt,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_analysis import high_relevance_set

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
FIDELITY = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-fidelity-audit-result-20260901.json"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
EMBEDDING_RECEIPT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-embedding-snapshot-receipt-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-contract-20260901.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"
EXPECTED_EMBEDDING_RECEIPT_SHA256 = "2afe395b37450143129bceb314a1b78f26bd2406024cf65dcb794d2b09f8f2b3"


def allocation_rule(design: str) -> dict[str, Any]:
    if design == "PRIMARY_4_REPOSITORY":
        return {
            "per_repo": "first 1 structurally qualified pilot; next 6 confirmatory",
            "pilot_count": 4, "confirmatory_count": 24,
            "required_structural_per_repo": [7, 7, 7, 7],
        }
    if design == "FALLBACK_3_REPOSITORY":
        return {
            "per_repo": (
                "first hash-ordered repository: first 2 structurally qualified pilot, "
                "next 8 confirmatory; other repositories: first 1 pilot, next 8 confirmatory"
            ),
            "pilot_count": 4, "confirmatory_count": 24,
            "required_structural_per_repo": [10, 9, 9],
        }
    raise RuntimeError("unknown dataset design")


def contract_payload() -> dict[str, Any]:
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    fidelity = json.loads(FIDELITY.read_text(encoding="utf-8"))
    q0 = json.loads(Q0.read_text(encoding="utf-8"))
    embedding = json.loads(EMBEDDING_RECEIPT.read_text(encoding="utf-8"))
    if fidelity["decision"] != "SOURCE_BANK_FIDELITY_QUALIFIED":
        raise RuntimeError("source bank fidelity gate closed")
    if q0["decision"] != "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFIED":
        raise RuntimeError("Q0 gate closed")
    if sha256_file(EMBEDDING_RECEIPT) != EXPECTED_EMBEDDING_RECEIPT_SHA256:
        raise RuntimeError("embedding receipt drift")
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "RETRIEVAL_AND_STRUCTURAL_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "ZERO_PROVIDER_RETRIEVAL_STRUCTURAL_QUALIFICATION_AUTHORIZED",
        "split_sha256": sha256_file(SPLIT), "source_bank_sha256": sha256_file(BANK),
        "fidelity_result_sha256": sha256_file(FIDELITY), "q0_sha256": sha256_file(Q0),
        "embedding_receipt_sha256": sha256_file(EMBEDDING_RECEIPT),
        "embedding_revision": embedding["revision"],
        "sampling": q0["recommended_sampling_resolution"],
        "calibration_task_ids": split["calibration_task_ids"],
        "structural_candidate_task_ids": split["structural_candidate_task_ids"],
        "allocation_rule": allocation_rule(split["dataset_design"]),
        "retrieval": {
            "source_documents": "raw source problem statements",
            "evaluation_queries": "official instruction-formatted evaluation problem statements",
            "pooling": "official masked average pooling",
            "normalization": "L2", "score": "query @ source.T * 100",
            "ordering": "Python stable descending sort", "top_k": 1,
            "repeat_hash_identity_required": True,
        },
        "structural_gate": {
            "minimum_nonempty_atomic_items": 2,
            "complete_R1_A_B_E_byte_equal": True,
            "complete_R1_D_differs_A": True,
            "same_underlying_evidence_hash": True,
        },
        "behavioral_calls_authorized": False,
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite structural contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload)}


def allocate(split: dict[str, Any], qualified: dict[str, bool]) -> tuple[list[str], list[str]]:
    pilots, confirmatory = [], []
    fallback = split["dataset_design"] == "FALLBACK_3_REPOSITORY"
    for repo_index, row in enumerate(split["repo_splits"]):
        eligible = [task_id for task_id in row["structural_candidate_task_ids"]
                    if qualified.get(task_id, False)]
        pilot_n, confirm_n = ((2, 8) if fallback and repo_index == 0 else
                              ((1, 8) if fallback else (1, 6)))
        if len(eligible) < pilot_n + confirm_n:
            raise RuntimeError(f"insufficient structurally qualified tasks for {row['repo']}")
        pilots.extend(eligible[:pilot_n])
        confirmatory.extend(eligible[pilot_n:pilot_n + confirm_n])
    if len(pilots) != 4 or len(confirmatory) != 24:
        raise RuntimeError("pilot/confirmatory count drift")
    return pilots, confirmatory


def run(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate structural qualification")
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("structural contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("structural contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    if contract["source_bank_sha256"] != sha256_file(BANK):
        raise RuntimeError("structural source bank binding drift")
    rows = dataset_rows()
    source_ids = [row["source_task_id"] for row in bank["entries"]]
    source_repositories = [row["source_repository"] for row in bank["entries"]]
    source_queries = [row["source_query"] for row in bank["entries"]]
    evaluation_ids = list(contract["calibration_task_ids"]) + list(contract["structural_candidate_task_ids"])
    evaluation_queries = [str(rows[task_id]["problem_statement"]) for task_id in evaluation_ids]
    embedder = FrozenQwenEmbedder()
    source_vectors = embedder.embed(source_queries)
    source_repeat = embedder.embed(source_queries)
    query_texts = [detailed_query(query) for query in evaluation_queries]
    query_vectors = embedder.embed(query_texts)
    query_repeat = embedder.embed(query_texts)
    source_hash = embedder.tensor_sha256(source_vectors)
    query_hash = embedder.tensor_sha256(query_vectors)
    deterministic = (
        source_hash == embedder.tensor_sha256(source_repeat)
        and query_hash == embedder.tensor_sha256(query_repeat)
    )
    if not deterministic:
        raise RuntimeError("retrieval embedding deterministic replay hash failed")
    by_source = {row["source_task_id"]: row for row in bank["entries"]}
    retrievals: dict[str, dict[str, Any]] = {}
    structural: dict[str, dict[str, Any]] = {}
    candidate_set = set(contract["structural_candidate_task_ids"])
    for index, task_id in enumerate(evaluation_ids):
        task = rows[task_id]
        retrieval = retrieval_receipt(
            instance_id=task_id,
            task_sha256=split["task_receipts"][task_id]["task_sha256"],
            query=str(task["problem_statement"]), source_ids=source_ids,
            source_repositories=source_repositories, source_vectors=source_vectors,
            query_vector=query_vectors[index:index + 1],
            source_bank_sha256=sha256_file(BANK))
        retrievals[task_id] = retrieval
        if task_id in candidate_set:
            selected = by_source[retrieval["top1_source_task_id"]]
            try:
                structural[task_id] = structural_receipt(
                    instance_id=task_id, task_sha256=retrieval["task_sha256"],
                    problem_statement=str(task["problem_statement"]),
                    retrieved_case={
                        "task_id": selected["source_task_id"],
                        "query": selected["source_query"],
                        "memory_items": selected["parsed_memory_items"],
                    },
                    sampling=contract["sampling"])
            except ValueError as error:
                structural[task_id] = {
                    "instance_id": task_id, "structurally_qualified": False,
                    "failure_layer": "structural_treatment", "message": str(error),
                    "behavioral_calls_made": 0, "credential_material_present": False,
                }
    qualified = {task_id: bool(row["structurally_qualified"])
                 for task_id, row in structural.items()}
    try:
        pilots, confirmatory = allocate(split, qualified)
        decision = "RETRIEVAL_STRUCTURAL_QUALIFIED_FINAL_TASKS_FROZEN"
    except RuntimeError as error:
        pilots, confirmatory = [], []
        decision = "HOLD_INSUFFICIENT_STRUCTURALLY_QUALIFIED_TASKS"
        allocation_failure = str(error)
    high_relevance = high_relevance_set(
        [retrievals[task_id] for task_id in confirmatory], 12) if confirmatory else []
    calibration_requests = {}
    for task_id in contract["calibration_task_ids"]:
        selected = by_source[retrievals[task_id]["top1_source_task_id"]]
        memory = "\n\n".join(selected["parsed_memory_items"])
        calibration_requests[task_id] = {
            "complete_R1": complete_request(
                str(rows[task_id]["problem_statement"]), memory, contract["sampling"]),
            "selected_memory_sha256": sha256_text(memory),
        }
        calibration_requests[task_id]["complete_R1_sha256"] = sha256_text(
            canonical_json(calibration_requests[task_id]["complete_R1"]))
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "RETRIEVAL_AND_STRUCTURAL_QUALIFICATION",
        "created_at_utc": utcnow(), "decision": decision,
        "contract_sha256": sha256_file(CONTRACT), "source_bank_sha256": sha256_file(BANK),
        "embedding_replay": {
            "source_vector_sha256": source_hash, "query_vector_sha256": query_hash,
            "repeat_hash_identity": deterministic, "source_count": len(source_ids),
            "evaluation_query_count": len(evaluation_ids),
        },
        "retrievals": retrievals, "structural_receipts": structural,
        "structurally_qualified_count": sum(qualified.values()),
        "pilot_task_ids": pilots, "confirmatory_task_ids": confirmatory,
        "high_relevance_sensitivity_task_ids": high_relevance,
        "calibration_requests": calibration_requests,
        "allocation_failure": locals().get("allocation_failure"),
        "checks": {
            "provider_policy_calls_zero": True,
            "confirmatory_behavioral_outcomes_observed": False,
            "retrieval_replay_deterministic": deterministic,
            "all_selected_pilot_structurally_qualified": all(qualified.get(x) for x in pilots),
            "all_selected_confirmatory_structurally_qualified": all(qualified.get(x) for x in confirmatory),
            "selected_R1_A_B_E_equal": all(
                structural[x]["complete_R1_sha256"]["A"]
                == structural[x]["complete_R1_sha256"]["B"]
                == structural[x]["complete_R1_sha256"]["E"]
                for x in pilots + confirmatory),
            "selected_R1_D_differs_A": all(
                structural[x]["complete_R1_sha256"]["D"]
                != structural[x]["complete_R1_sha256"]["A"]
                for x in pilots + confirmatory),
        },
        "scientific_boundary": {
            "evaluation_runtime_qualification_authorized": decision.endswith("FINAL_TASKS_FROZEN"),
            "calibration_authorized": False,
            "pilot_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    return {"decision": decision, "file_sha256": write_json(output, payload),
            "structurally_qualified_count": payload["structurally_qualified_count"],
            "pilot_count": len(pilots), "confirmatory_count": len(confirmatory)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else run(), sort_keys=True))


if __name__ == "__main__":
    main()
