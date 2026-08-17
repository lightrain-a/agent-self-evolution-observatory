from __future__ import annotations

import json
from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS, reduction_pattern_audit
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES,
    SEARCH_PORTFOLIO_PRIMITIVES,
    FORBIDDEN_DISCOVERY_LANES,
    LANE_DISTINCT_SOURCE_MINIMUM,
    LANE_EVIDENCE_REQUIRED,
    LANE_MACHINE_CONTRACTS,
    LANE_SOURCE_ROLES,
)


def _lane_contract_payload(*, shadow_mode: bool = False) -> list[dict[str, Any]]:
    return [
        {
            "lane": lane,
            "source_roles": list(LANE_SOURCE_ROLES[lane]),
            "required_lane_evidence": list(LANE_EVIDENCE_REQUIRED[lane]),
            "machine_contract": LANE_MACHINE_CONTRACTS[lane],
        }
        for lane in (SEARCH_PORTFOLIO_PRIMITIVES if shadow_mode else DISCOVERY_LANES)
    ]


def generator_prompt(records: list[dict[str, Any]], dead_end_memory: dict[str, Any] | None = None) -> str:
    sources = [
        {
            "ref": row["ref"],
            "title": row["title"],
            "primary_url": row["primary_url"],
            "source_sha256": row["source_sha256"],
            "abstract": str(row.get("abstract") or "")[:2200],
            "empirical_facts": [
                {"section": str(fact.get("section") or ""), "evidence_tier": str(fact.get("evidence_tier") or ""), "text": str(fact.get("text") or "")[:520]}
                for fact in (row.get("empirical_facts") or [])[:4]
                if isinstance(fact, dict)
            ],
            "typed_evidence": {
                key: [{"section": str(fact.get("section") or ""), "evidence_tier": str(fact.get("evidence_tier") or ""), "text": str(fact.get("text") or "")[:520]} for fact in ((row.get("typed_evidence") or {}).get(key) or [])[:2] if isinstance(fact, dict)]
                for key in ("operational_assumptions", "measured_failures", "boundary_observations")
            },
        }
        for row in records[:32]
    ]
    reductions = [{"key": row["key"], "veto": row["veto"]} for row in REDUCTION_PATTERNS]
    lane_contracts = _lane_contract_payload()
    dead_end_memory = dead_end_memory or {"summary": {}, "recent_blocked_examples": [], "scientific_authority": False}
    shape = {
        "lane_search": [
            {
                "lane": "CONTRADICTION|CONVERGENT_FAILURE|ASSUMPTION_BREAK|UNEXPLAINED_BOUNDARY",
                "status": "NO_PAIR|REDUCIBLE|CANDIDATE",
                "source_refs": ["one or two unique arXiv refs according to the lane minimum"],
                "reason": "bounded search audit reason",
            }
        ],
        "candidates": [
            {
                "candidate_id": "AUTO-1",
                "title": "problem title",
                "discovery_lane": "CONTRADICTION|CONVERGENT_FAILURE|ASSUMPTION_BREAK|UNEXPLAINED_BOUNDARY",
                "empirical_evidence": {
                    "source_a": {"ref": "arXiv:...", "claim": "grounded source evidence", "evidence_role": "EMPIRICAL_FACT|OPERATIONAL_ASSUMPTION"},
                    "source_b": {"ref": "arXiv:...", "claim": "grounded source evidence", "evidence_role": "EMPIRICAL_FACT"},
                    "relation": "why these two evidence items instantiate the selected lane",
                },
                "lane_evidence": {"lane-specific-required-field": "..."},
                "irreducible_object": "formal/scientific object, not an algorithm",
                "mature_theory_baselines": [
                    {"name": "theory 1", "same_information_projection": "...", "ex_ante_prediction": "...", "distinguishing_prediction": "...", "cannot_express": "...", "reduction_class": "SOFT_COLLISION|NEEDS_EXACT_REDUCTION_TEST|TOO_GENERIC_TO_VETO|VALID_HARD_VETO", "exact_reduction_test": "..."},
                    {"name": "theory 2", "same_information_projection": "...", "ex_ante_prediction": "...", "distinguishing_prediction": "...", "cannot_express": "...", "reduction_class": "SOFT_COLLISION|NEEDS_EXACT_REDUCTION_TEST|TOO_GENERIC_TO_VETO|VALID_HARD_VETO", "exact_reduction_test": "..."},
                ],
                "reduction_falsifiability_contract": {"same_observable_information_checked": True, "ex_ante_exact_prediction_checked": True, "distinguishing_prediction_checked": True, "scope_boundary_checked": True, "all_exact_reduction_tests_resolved": True},
                "same_information_nonreducibility": {"claim": "...", "why_each_baseline_cannot_express_prediction": "..."},
                "exact_prediction": "...",
                "strongest_same_information_baseline": "...",
                "domain_transfer_audit": {"mature_source_domain": "...", "mature_object": "...", "why_not_domain_transfer": "..."},
                "saturation_scan": {"checked": True, "matched_patterns": [], "rejected_patterns": [{"key": "known-ledger-key", "reason": "why the exact ledger veto does not apply under the same information"}]},
                "cheapest_problem_falsifier": "...",
                "endpoint_headroom_requirement": "...",
            }
        ],
        "generation_notes": "may explicitly state that zero candidates survive",
    }
    return (
        "Strict evidence-first multi-lane ICLR research-PROBLEM generator for self-evolving LLM agents. "
        "Return zero to five research problems, never methods. Zero is preferred to a weak candidate. Do not force lane balance.\n\n"
        "ALLOWED DISCOVERY LANES are machine contracts, not stylistic labels:\n"
        + json.dumps(lane_contracts, ensure_ascii=False, separators=(",", ":"))
        + "\nFORBIDDEN LANES: "
        + json.dumps(list(FORBIDDEN_DISCOVERY_LANES), ensure_ascii=False)
        + ". MISSING_CELL is forbidden because open-world literature absence is not machine-provable; SHARED_LIMITATION is forbidden without empirical failure evidence; PURE_TOPIC_BRAINSTORM is forbidden because it has no primary-evidence anchor.\n\n"
        "Use ONLY the verified primary-source registry below. Every candidate must contain two independently groundable evidence ITEMS as source_a/source_b. Distinct-primary-source requirements are lane-specific: "
        + json.dumps({lane: LANE_DISTINCT_SOURCE_MINIMUM[lane] for lane in DISCOVERY_LANES}, ensure_ascii=False, separators=(",", ":"))
        + ". For UNEXPLAINED_BOUNDARY, source_a and source_b MAY cite the same primary paper when that single paper itself quantitatively establishes both the anomalous boundary/regime and the adjacent expected/control regime; the two claims/excerpts must still be distinct evidence items. "
        "Claims must be supported by the supplied primary abstract or one bounded deterministic full-text empirical-fact candidate. "
        "For ASSUMPTION_BREAK only, source_a may be an explicit OPERATIONAL_ASSUMPTION grounded in primary text; all other source roles are EMPIRICAL_FACT. "
        "Future-work statements, author wishes, keyword absence, and a missing literature cell are not admissible evidence. "
        "Empirical-fact candidates are discovery evidence, not automatic ground truth, and will be independently grounded before Problem Gate eligibility.\n\n"
        "ANOMALY-FIRST DISCOVERY OPERATOR: do NOT require the literature to have already assembled a cross-paper tension for us. First scan each primary paper for a quantitative sign reversal, nonmonotonicity, threshold, plateau, history dependence, composition effect, or surprising failure boundary. Then identify the smallest operational core and an adjacent/control regime. Ask what decisive comparison we can materialize ourselves from released units, first-party code, or an existing provenance-audited substrate. Only after that project identical observable information into at least two mature theories. "
        "For CONTRADICTION, shared_operationalization is NOT established by a shared high-level label such as skill, memory, rubric, prompt, or procedural prior. shared_intervention_semantics and shared_adaptation_stage must match the causal treatment surface: inference-time context injection/retrieval, offline data filtering, optimizer updates, parameter-efficient updates, and full-parameter SFT are distinct interventions unless the candidate explicitly conditions on rather than erases that difference. "
        "If either mature theory expresses the exact ex-ante prediction under the same information, discard the candidate. If the anomaly is real but the reduction is unresolved, freeze the cheapest distinguishing falsifier instead of inventing novelty. Domain transfer, mathematical renaming, another benchmark/metric/taxonomy/test-generator, or combining occupied atoms is not novelty. Every mature_theory_baselines item MUST include name, same_information_projection, ex_ante_prediction, distinguishing_prediction, cannot_express, reduction_class, and exact_reduction_test. Every emitted candidate MUST include reduction_falsifiability_contract. The first four checks (same observable information, ex-ante prediction, distinguishing prediction, scope boundary) MUST be true. all_exact_reduction_tests_resolved MUST be true only when no baseline or saturation item remains NEEDS_EXACT_REDUCTION_TEST; when an exact reduction is genuinely pending it MUST be false, the exact test and cheapest falsifier must be concrete, and the candidate is provisional: it may receive BLOCK-ONLY semantic/lane review but cannot pass Problem Gate until the reduction is resolved.\n\n"
        "HARD NEGATIVE-SPACE VETO:\n"
        + json.dumps(reductions, ensure_ascii=False, separators=(",", ":"))
        + "\nSATURATION FIELD CONTRACT: matched_patterns may contain ONLY exact known ledger keys that actually apply; any exact match hard-blocks the candidate. If you explicitly considered a known key and argue it does NOT apply, put {key:<exact known key>, reason:<why>} in rejected_patterns instead. Never append explanatory prose to matched_patterns.\n"
        + "\n\nREVIEWER-PROVEN DEAD-END MEMORY (search-control only; zero scientific authority):\n"
        + json.dumps(dead_end_memory, ensure_ascii=False, separators=(",", ":"))
        + "\nThese are prior candidates already BLOCKED by independent review. Do not regenerate a semantically equivalent object by swapping sources, renaming the object, or rephrasing the same reduction escape. In particular, if repeated_reduction_basin=true, actively search outside the top basin. A prior dead end may be reconsidered only when the CURRENT evidence contains a concrete new observable that directly defeats the recorded strongest reduction; mere new wording or a new domain is insufficient.\n"
        + "LANE SEARCH AUDIT: in the SAME single generator call, audit all four allowed discovery lanes exactly once, in lane_search_priority order when provided. Treat each lane as an evidence-tuple search, not a mandatory paper-pair search. Return status=NO_PAIR when no grounded evidence tuple satisfies the lane contract; REDUCIBLE when the strongest grounded tuple is already explained by the mature/negative-space stack; CANDIDATE only when at least one emitted candidate in that exact lane uses the same unique ref set. source_refs must be empty for NO_PAIR; for REDUCIBLE/CANDIDATE list the UNIQUE provided refs used by the tuple, with count meeting the lane-specific minimum and never exceeding two. In UNEXPLAINED_BOUNDARY this may therefore be a one-ref list. A lane audit never requires a candidate and carries zero scientific authority. Historically underexplored lanes are searched first, but their scientific gate is unchanged.\n"
        + "\n\nVERIFIED PRIMARY SOURCES (private abstracts + bounded full-text fact candidates; output only ref + grounded claim + evidence_role):\n"
        + json.dumps(sources, ensure_ascii=False, separators=(",", ":"))
        + "\n\nReturn syntactically valid JSON only, shape:\n"
        + json.dumps(shape, ensure_ascii=False, separators=(",", ":"))
        + "\nNo markdown/trailing commas. IDs AUTO-1..AUTO-5. Do not include authority fields; code forces them false."
    )


def reviewer_prompt(candidates: list[dict[str, Any]], evidence_by_ref: dict[str, dict[str, Any]], *, shadow_mode: bool = False) -> str:
    reductions = [{"key": row["key"], "mature_theories": row["mature_theories"], "veto": row["veto"], "audit_class": row["audit_class"]} for row in reduction_pattern_audit()]
    lane_contracts = _lane_contract_payload(shadow_mode=shadow_mode)
    stripped = [{k: v for k, v in row.items() if k not in {"semantic_reduction_review", "authority"}} for row in candidates]
    refs: list[str] = []
    for row in candidates:
        evidence = row.get("empirical_evidence") or {}
        for source_key in ("source_a", "source_b"):
            ref = str((evidence.get(source_key) or {}).get("ref") or "").strip()
            if ref and ref not in refs:
                refs.append(ref)
    evidence_rows = []
    for ref in refs:
        record = evidence_by_ref.get(ref) or {}
        evidence_rows.append(
            {
                "ref": ref,
                "title": record.get("title"),
                "source_sha256": record.get("source_sha256"),
                "abstract": record.get("abstract"),
                "empirical_facts": [
                    {"section": str(fact.get("section") or ""), "evidence_tier": str(fact.get("evidence_tier") or ""), "text": str(fact.get("text") or "")[:520]}
                    for fact in (record.get("empirical_facts") or [])[:4]
                    if isinstance(fact, dict)
                ],
                "typed_evidence": {
                    key: [{"section": str(fact.get("section") or ""), "evidence_tier": str(fact.get("evidence_tier") or ""), "text": str(fact.get("text") or "")[:520]} for fact in ((record.get("typed_evidence") or {}).get(key) or [])[:2] if isinstance(fact, dict)]
                    for key in ("operational_assumptions", "measured_failures", "boundary_observations")
                },
            }
        )
    return (
        "Independent BLOCK-ONLY multi-lane semantic reduction + source-grounding reviewer. You cannot authorize Paper Design, methods, experiments, P0, or GPU. "
        "For each candidate perform THREE independent checks: "
        "(1) source grounding: each of the two stated evidence-item claims must be independently supported by its supplied primary abstract or one bounded full-text empirical-fact candidate; source_a/source_b may share a ref only when the lane's distinct-source minimum allows it, and the reviewer evidence_source label is audit metadata because code deterministically locates the exact excerpt; "
        "(2) lane contract: the two grounded evidence-item claims, evidence roles, relation, and lane_evidence must genuinely satisfy the selected discovery lane. For CONTRADICTION, verify shared intervention semantics and adaptation stage, not merely a shared noun or endpoint metric: inference-time context/retrieval, offline filtering, optimizer/weight updates, parameter-efficient tuning, and full-parameter training are different treatment surfaces unless the candidate preserves that distinction as an explicit conditioned variable; "
        "(3) mature reduction: audit the candidate under the Reduction Falsifiability Contract. A theory/pattern name alone is NOT a veto. "
        "A VALID_HARD_VETO requires the same observable information, an ex-ante exact candidate-level prediction, a testable distinguishing/reduction test, and explicit scope boundary. "
        "If an exact reduction remains unresolved, use NEEDS_EXACT_REDUCTION_TEST and BLOCK. If similarity is real but not an exact reduction, use SOFT_COLLISION or TOO_GENERIC_TO_VETO; those classes do not by themselves force BLOCK. "
        "If source grounding or the lane contract fails, verdict=BLOCK. CLEAR only means both evidence items are grounded, the lane-specific distinct-source minimum is satisfied, lane_contract_verified=true, and no proven/pending exact mature reduction remains; it never means scientific approval.\n\n"
        "LANE CONTRACTS:\n"
        + json.dumps(lane_contracts, ensure_ascii=False, separators=(",", ":"))
        + "\n\nLEDGER:\n"
        + json.dumps(reductions, ensure_ascii=False, separators=(",", ":"))
        + "\n\nPRIMARY EVIDENCE:\n"
        + json.dumps(evidence_rows, ensure_ascii=False, separators=(",", ":"))
        + "\n\nCANDIDATES:\n"
        + json.dumps(stripped, ensure_ascii=False, separators=(",", ":"))
        + '\n\nReturn JSON only: {"reviews":[{"candidate_id":"...","verdict":"CLEAR|BLOCK","lane_contract_verified":true,"lane_contract_reason":"...","source_claim_support":{"source_a":{"supported":true,"evidence_source":"abstract|fulltext","evidence_excerpt":"exact words from supplied primary evidence"},"source_b":{"supported":true,"evidence_source":"abstract|fulltext","evidence_excerpt":"exact words from supplied primary evidence"}},"matched_patterns":["known-key"],"reduction_class":"VALID_HARD_VETO|NEEDS_EXACT_REDUCTION_TEST|SOFT_COLLISION|TOO_GENERIC_TO_VETO|NONE","exact_reduction_test":"specific candidate-level reduction/distinguishing test or none","strongest_reduction":"mature theory/object or none","reason":"..."}]}. '
        "Each supported source claim requires one SHORT exact contiguous excerpt (4-30 words). matched_patterns should list only relevant known keys; its presence alone does not determine the verdict. If a mature reduction is outside the ledger, matched_patterns may be [] but strongest_reduction must name it and reduction_class must still be explicit."
    )
