"""Outcome-blind task-specific top-1 retrieval with the pinned official Qwen branch."""
from __future__ import annotations

import hashlib
from typing import Any, Sequence

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from research_pipeline.asset_first_stri_reasoningbank_p1_core import canonical_json, sha256_text
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_retrieval_substrate import (
    REVISION, SNAPSHOT,
)

OFFICIAL_RETRIEVAL_TASK = (
    "Given the prior software engineering queries, your task is to analyze a current "
    "query's intent and select relevant prior queries that could help resolve it."
)


def detailed_query(query: str) -> str:
    return f"Instruct: {OFFICIAL_RETRIEVAL_TASK}\nQuery: {query}"


def l2_normalize(values: torch.Tensor) -> torch.Tensor:
    return F.normalize(values, p=2, dim=-1)


def stable_top_scores(ids: Sequence[str], source_vectors: torch.Tensor,
                      query_vector: torch.Tensor) -> list[tuple[str, float]]:
    if source_vectors.ndim != 2 or query_vector.shape != (1, source_vectors.shape[1]):
        raise ValueError("retrieval embedding shape mismatch")
    scores = (query_vector @ source_vectors.T).squeeze(0) * 100.0
    rows = list(zip(ids, [float(value) for value in scores.tolist()]))
    rows.sort(key=lambda row: row[1], reverse=True)
    return rows


def retrieval_receipt(*, instance_id: str, task_sha256: str, query: str,
                      source_ids: Sequence[str], source_repositories: Sequence[str],
                      source_vectors: torch.Tensor, query_vector: torch.Tensor,
                      source_bank_sha256: str) -> dict[str, Any]:
    rows = stable_top_scores(source_ids, source_vectors, query_vector)
    if len(rows) < 2:
        raise ValueError("top-2 observability requires at least two source cases")
    top1, top2 = rows[:2]
    index = list(source_ids).index(top1[0])
    task_repo = instance_id.split("__", 1)[0]
    source_repo = str(source_repositories[index])
    scores = [{"source_task_id": source_id, "similarity": score}
              for source_id, score in rows]
    return {
        "schema_version": 1, "instance_id": instance_id,
        "task_sha256": task_sha256, "query_sha256": sha256_text(query),
        "source_bank_sha256": source_bank_sha256,
        "embedding_model": "Qwen/Qwen3-Embedding-8B",
        "embedding_revision": REVISION,
        "retrieval_formula": "L2-normalized query @ L2-normalized cached source.T * 100",
        "ranking": "Python stable descending score sort",
        "top_k": 1, "top1_source_task_id": top1[0],
        "top1_relevance": top1[1], "top2_source_task_id": top2[0],
        "top2_relevance": top2[1], "top1_top2_margin": top1[1] - top2[1],
        "source_repository": source_repo,
        "same_repository_indicator": source_repo == task_repo,
        "all_scores": scores,
        "score_vector_sha256": sha256_text(canonical_json(scores)),
        "provider_policy_calls": 0, "behavioral_outcomes_observed": False,
        "credential_material_present": False,
    }


class FrozenQwenEmbedder:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            SNAPSHOT, local_files_only=True, padding_side="left")
        self.model = AutoModel.from_pretrained(
            SNAPSHOT, local_files_only=True, torch_dtype="auto")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device).eval()

    def embed(self, texts: Sequence[str], *, batch_size: int = 8) -> torch.Tensor:
        vectors = []
        for start in range(0, len(texts), batch_size):
            batch_texts = list(texts[start:start + batch_size])
            batch = self.tokenizer(
                batch_texts, max_length=1024, padding=True, truncation=True,
                return_tensors="pt")
            batch = {key: value.to(self.device) for key, value in batch.items()}
            with torch.no_grad():
                output = self.model(**batch)
                hidden = output.last_hidden_state
                masked = hidden.masked_fill(
                    ~batch["attention_mask"][..., None].bool(), 0.0)
                pooled = masked.sum(dim=1) / batch["attention_mask"].sum(dim=1)[..., None]
            vectors.append(l2_normalize(pooled).to("cpu", dtype=torch.float32))
        return torch.cat(vectors, dim=0)

    @staticmethod
    def tensor_sha256(tensor: torch.Tensor) -> str:
        value = tensor.detach().to("cpu", dtype=torch.float32).contiguous().numpy().tobytes()
        return hashlib.sha256(value).hexdigest()
