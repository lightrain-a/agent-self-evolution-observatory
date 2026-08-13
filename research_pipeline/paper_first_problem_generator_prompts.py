from __future__ import annotations

import json
from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS, reduction_pattern_audit
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES,
    FORBIDDEN_DISCOVERY_LANES,
    LANE_EVIDENCE_REQUIRED,
    LANE_MACHINE_CONTRACTS,
    LANE_SOURCE_ROLES,
)


def _lane_contract_payload() -> list[dict[str, Any]]:
    return [
        {
            "lane": lane,
            "source_roles": list(LANE_SOURCE_ROLES[lane]),
            "required_lane_evidence": list(LANE_EVIDENCE_REQUIRED[lane]),
            "machine_contract": LANE_MACHINE_CONTRACTS[lane],
        }
        for lane in DISCOVERY_LANES
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
                "source_refs": ["arXiv:...", "arXiv:..."],
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
                    {"name": "theory 1", "same_information_projection": "...", "reduction_test": "..."},
                    {"name": "theory 2", "same_information_projection": "...", "reduction_test": "..."},
                ],
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
        "Use ONLY the verified primary-source registry below. Every candidate must cite two distinct refs exactly as provided. "
        "Claims must be supported by the supplied primary abstract or one bounded deterministic full-text empirical-fact candidate. "
        "For ASSUMPTION_BREAK only, source_a may be an explicit OPERATIONAL_ASSUMPTION grounded in primary text; all other source roles are EMPIRICAL_FACT. "
        "Future-work statements, author wishes, keyword absence, and a missing literature cell are not admissible evidence. "
        "Empirical-fact candidates are discovery evidence, not automatic ground truth, and will be independently grounded before Problem Gate eligibility.\n\n"
        "Before naming a new object, project identical observable information into at least two mature theories. "
        "If either theory expresses the exact prediction, discard the candidate. Domain transfer, mathematical renaming, another benchmark/metric/taxonomy/test-generator, or combining occupied atoms is not novelty.\n\n"
        "HARD NEGATIVE-SPACE VETO:\n"
        + json.dumps(reductions, ensure_ascii=False, separators=(",", ":"))
        + "\nSATURATION FIELD CONTRACT: matched_patterns may contain ONLY exact known ledger keys that actually apply; any exact match hard-blocks the candidate. If you explicitly considered a known key and argue it does NOT apply, put {key:<exact known key>, reason:<why>} in rejected_patterns instead. Never append explanatory prose to matched_patterns.\n"
        + "\n\nREVIEWER-PROVEN DEAD-END MEMORY (search-control only; zero scientific authority):\n"
        + json.dumps(dead_end_memory, ensure_ascii=False, separators=(",", ":"))
        + "\nThese are prior candidates already BLOCKED by independent review. Do not regenerate a semantically equivalent object by swapping sources, renaming the object, or rephrasing the same reduction escape. In particular, if repeated_reduction_basin=true, actively search outside the top basin. A prior dead end may be reconsidered only when the CURRENT evidence contains a concrete new observable that directly defeats the recorded strongest reduction; mere new wording or a new domain is insufficient.\n"
        + "LANE SEARCH AUDIT: in the SAME single generator call, audit all four allowed discovery lanes exactly once, in lane_search_priority order when provided. For each lane return status=NO_PAIR when no two current primary sources already satisfy its evidence contract; REDUCIBLE when the strongest grounded pair is already explained by the mature/negative-space stack; CANDIDATE only when at least one emitted candidate in that exact lane uses the same two refs. source_refs must be empty for NO_PAIR, exactly two distinct provided refs for REDUCIBLE or CANDIDATE. A lane audit never requires a candidate and carries zero scientific authority. Historically underexplored lanes are searched first, but their scientific gate is unchanged.\n"
        + "\n\nVERIFIED PRIMARY SOURCES (private abstracts + bounded full-text fact candidates; output only ref + grounded claim + evidence_role):\n"
        + json.dumps(sources, ensure_ascii=False, separators=(",", ":"))
        + "\n\nReturn syntactically valid JSON only, shape:\n"
        + json.dumps(shape, ensure_ascii=False, separators=(",", ":"))
        + "\nNo markdown/trailing commas. IDs AUTO-1..AUTO-5. Do not include authority fields; code forces them false."
    )


def reviewer_prompt(candidates: list[dict[str, Any]], evidence_by_ref: dict[str, dict[str, Any]]) -> str:
    reductions = [{"key": row["key"], "mature_theories": row["mature_theories"], "veto": row["veto"], "audit_class": row["audit_class"]} for row in reduction_pattern_audit()]
    lane_contracts = _lane_contract_payload()
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
        "(1) source grounding: each stated source claim must be supported by its supplied primary abstract or one bounded full-text empirical-fact candidate; the reviewer evidence_source label is audit metadata because code deterministically locates the exact excerpt; "
        "(2) lane contract: the two grounded source claims, evidence roles, relation, and lane_evidence must genuinely satisfy the selected discovery lane; "
        "(3) mature reduction: audit the candidate under the Reduction Falsifiability Contract. A theory/pattern name alone is NOT a veto. "
        "A VALID_HARD_VETO requires the same observable information, an ex-ante exact candidate-level prediction, a testable distinguishing/reduction test, and explicit scope boundary. "
        "If an exact reduction remains unresolved, use NEEDS_EXACT_REDUCTION_TEST and BLOCK. If similarity is real but not an exact reduction, use SOFT_COLLISION or TOO_GENERIC_TO_VETO; those classes do not by themselves force BLOCK. "
        "If source grounding or the lane contract fails, verdict=BLOCK. CLEAR only means both sources are grounded, lane_contract_verified=true, and no proven/pending exact mature reduction remains; it never means scientific approval.\n\n"
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
