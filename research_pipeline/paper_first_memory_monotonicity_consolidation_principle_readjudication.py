from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation


CANDIDATE_ID = "AUTO-1-MEMORY-MONOTONICITY-CONSOLIDATION"
SEARCH_PRIMITIVE = "ASSUMPTION_BREAK"
SOURCE_A = "arXiv:2608.11654"
SOURCE_B = "arXiv:2608.12428"
SOURCE_A_FULLTEXT_SHA256 = "aad633809bf2bd92f2fc9c6c63e693050a7bad5ae09808418e8374a056ea13dd"
SOURCE_B_FULLTEXT_SHA256 = "79a9c92991d928c4d8e4629a4a71ea8c92d2c56f8fe81e3a4a5ba6822f4b3a32"
SOURCE_A_MONOTONICITY_TEXT_SHA256 = "cf48ea56e9679e686974771a4bfb51f666f97827c115e11dee32f1bb68bf20c7"
SOURCE_A_LIMITATION_TEXT_SHA256 = "645dfe25fefa911e0c8cb6b03a6afc02ecf5339e1693cf8c36dd79fac51715a1"
SOURCE_B_DREAMING_ACCURACY_TEXT_SHA256 = "0e70938c7225ba7229c309f6849cdf7e593c661dace3c06261514130481f74d6"
SOURCE_B_DREAMING_SUMMARY_TEXT_SHA256 = "74cb6b7181d902c6d9456f3c1db6ac25b496f131df566c7764d3feb7d399a3e1"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
MINDMEMOS_CLOSURE = PROJECT_ROOT / "generated" / "mindmemos-dreaming-compression-principle-readjudication-20260817.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "memory-monotonicity-consolidation-principle-readjudication-20260818.json"

# Provider outputs are diagnostic provenance only.  The closure below is rebuilt
# from primary/full-text provenance plus an already principle-certified closure.
SOURCE_GENERATOR_RUN_ID = "20260817T182752Z"
SOURCE_GENERATOR_RAW_SHA256 = "a7439d5da3981c3ca1b28046a40c996c1b796e24f57c686b37173d29ddcbab61"
SOURCE_REVIEWER_RAW_SHA256 = "5bbce62683095de66166ec95f8697d4362b5acf1c63c8629f50cf8f39819d826"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_readjudication() -> dict[str, Any]:
    primary = _load(PRIMARY_STATE)
    records = {str(row.get("ref") or ""): row for row in primary.get("records") or [] if isinstance(row, dict)}
    if (records.get(SOURCE_A) or {}).get("fulltext_sha256") != SOURCE_A_FULLTEXT_SHA256:
        raise ValueError("formal-memory fulltext provenance drift")
    if (records.get(SOURCE_B) or {}).get("fulltext_sha256") != SOURCE_B_FULLTEXT_SHA256:
        raise ValueError("MindMemOS fulltext provenance drift")

    prior = _load(MINDMEMOS_CLOSURE)
    prior_counter = ((prior.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    if prior.get("candidate_id") != "MINDMEMOS-DREAMING-COMPRESSION-PLATEAU" or prior.get("principle_dead_end_certified") is not True:
        raise ValueError("MindMemOS selective-consolidation closure unavailable")
    if prior_counter.get("same_information_reduction_verified") is not True or prior_counter.get("positive_support") is not True:
        raise ValueError("MindMemOS selective-consolidation reduction is not principle-certified")

    prior_sha = _sha(MINDMEMOS_CLOSURE)
    scope = (
        "The scoped AUTO-1 ASSUMPTION_BREAK claim that the idealized self-containment/monotonicity assumptions in "
        "arXiv:2608.11654 are independently falsified by arXiv:2608.12428 because MindMemOS dreaming compresses "
        "roughly one fifth of active memory while improving accuracy, thereby requiring a new capacity-constrained "
        "non-monotonic memory-utility object beyond conflict-aware selective forgetting, belief revision, and the "
        "formal paper's own acknowledged non-monotonic conflict limitation."
    )
    counter = {
        "type": "SAME_INFORMATION_REDUCTION",
        "statement": (
            "The proposed assumption break is absorbed before a new experiment is needed. The formal memory paper's "
            "monotonicity/self-containment assumptions are idealized properties of its generation operator, and the same "
            "paper explicitly records the relevant limitation: real extraction is at best locally monotone and a conflicting "
            "claim can overturn earlier conclusions. MindMemOS dreaming does not supply a semantics-blind deletion treatment; "
            "it merges redundant records and resolves conflicts, while the observed roughly 20% active-memory reduction is a "
            "post-consolidation outcome. The existing principle-certified MindMemOS closure independently verifies that, on "
            "FactConsolidation, accuracy gains with lower active-memory volume are predicted by conflict-aware selective "
            "forgetting/belief revision when duplicate, stale, or contradictory evidence is consolidated. Therefore the two "
            "primary results do not identify an independent ASSUMPTION_BREAK or a new capacity-utility primitive under the "
            "same information."
        ),
        "opposite_prediction": (
            "Under a fixed memory store, query set, temporal order, provenance, and conflict graph, downstream accuracy should "
            "track which duplicate/stale/contradictory evidence is consolidated and whether answer-critical valid evidence is "
            "preserved, not raw retained-memory count or the resulting compression fraction alone. Different compression ratios "
            "can have the same utility when they preserve the same answer-relevant conflict resolution, while the same ratio can "
            "have different utility when it removes different evidence. A standalone non-monotonic capacity curve should vanish "
            "after conflict-resolution semantics and answer-relevant retention are matched."
        ),
        "opposite_principle": (
            "Representation size is not the causal treatment when consolidation changes redundancy and conflict semantics. "
            "Idealized set-inclusion monotonicity cannot be declared independently falsified by a representation-changing "
            "selective-consolidation operator that the formal framework already flags as a non-monotonic conflict case; "
            "conflict-aware selective forgetting/belief revision must be reduced first."
        ),
        "opposite_search_seed": (
            "Search only for a provenance-audited intervention that separates retention/compression quantity from conflict-"
            "resolution semantics. Either independently vary retained volume while holding the exact answer-critical evidence, "
            "conflict graph, consolidation decisions, retrieval state, model, queries, and budget fixed, or vary conflict-"
            "resolution quality at matched retained volume. Require a preregistered held-out residual beyond a same-information "
            "conflict-aware selective-forgetting/belief-revision/rate-distortion baseline. Do not reopen from another natural "
            "compression ratio or from merging duplicates/superseded facts."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "same_information_reduction_verified": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_A,
            f"primary-fulltext:{SOURCE_A}#sha256={SOURCE_A_FULLTEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_A}#sha256={SOURCE_A_MONOTONICITY_TEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_A}#sha256={SOURCE_A_LIMITATION_TEXT_SHA256}",
            SOURCE_B,
            f"primary-fulltext:{SOURCE_B}#sha256={SOURCE_B_FULLTEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_B}#sha256={SOURCE_B_DREAMING_ACCURACY_TEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_B}#sha256={SOURCE_B_DREAMING_SUMMARY_TEXT_SHA256}",
            f"repo:generated/{MINDMEMOS_CLOSURE.name}#sha256={prior_sha}",
        ],
        "alternative_explanations_ruled_out": [
            "The formal paper states monotonicity as an unqualified empirical law over real consolidation systems: false; the paper itself records locally non-monotone extraction and conflict-driven overturning as a limitation/research problem.",
            "MindMemOS dreaming is random or semantics-blind deletion: false; its primary description states that dreaming merges redundant records and resolves conflicts, and the existing first-party closure verifies targeted consolidation semantics.",
            "The roughly 20% archive ratio is an independently manipulated capacity treatment: false; the principle-certified MindMemOS closure establishes that AMCR is a post-action summary of targeted consolidation rather than a controlled compression sweep.",
            "Reversing the sign from 'adding memory can hurt' to 'removing memory can help' creates a new causal primitive: false under the current evidence, because both are expressible through conflict-aware non-monotonic belief change once the same conflict information is available.",
        ],
        "reopen_condition": (
            "Reopen only with primary or first-party evidence that independently manipulates retention/compression quantity while "
            "matching conflict-resolution semantics, answer-critical evidence identity, temporal order, provenance, retrieval "
            "state, model, query set, and budget, or independently manipulates conflict-resolution quality at matched retained "
            "volume. The resulting ex-ante utility prediction must survive a same-information conflict-aware selective-forgetting, "
            "belief-revision, and rate-distortion baseline; a natural consolidation ratio or another duplicate/conflict merge is "
            "insufficient."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"memory-monotonicity counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "title": "Memory-monotonicity assumption break collapses under the source framework's own conflict limitation",
        "adjudication_date": "2026-08-18",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_proposal_had_scientific_authority": False,
        "source_generator_run_id": SOURCE_GENERATOR_RUN_ID,
        "source_generator_raw_sha256": SOURCE_GENERATOR_RAW_SHA256,
        "source_reviewer_raw_sha256": SOURCE_REVIEWER_RAW_SHA256,
        "source_ai_review_has_scientific_authority": False,
        "broader_memory_nonmonotonicity_falsified": False,
        "dead_end_scope": scope,
        "merged_reduction_basin": "MINDMEMOS-DREAMING-COMPRESSION-PLATEAU",
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "SAME_INFORMATION_REDUCTION",
            "counter_explanation": counter,
            "audit": audit,
        },
        "scientific_interpretation": {
            "safe_claim": (
                "The two source observations are real, but they do not establish an independent assumption-break object: the "
                "formal framework already acknowledges conflict-driven non-monotonicity, and MindMemOS dreaming is a targeted "
                "conflict/redundancy consolidation process whose compression ratio is not an independently varied treatment."
            ),
            "do_not_say": [
                "memory utility is always monotone",
                "selective forgetting can never reveal a new capacity effect",
                "MindMemOS accuracy gains are caused only by deleting memories",
                "the formal monotonicity assumption is empirically valid for every real memory system",
            ],
            "new_search_basin": "retention-quantity-vs-conflict-semantics-factorization",
        },
        "authority": {
            "ai_review_authorizes_dead_end": False,
            "primary_same_information_counter_explanation_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "mindmemos_prior_closure": prior_sha,
        },
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
