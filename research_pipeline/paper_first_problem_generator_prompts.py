from __future__ import annotations

import json
from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS


def generator_prompt(records: list[dict[str, Any]]) -> str:
    sources=[{
        "ref":row["ref"],"title":row["title"],"primary_url":row["primary_url"],
        "source_sha256":row["source_sha256"],"abstract":str(row.get("abstract") or "")[:2200],
    } for row in records[:16]]
    reductions=[{"key":row["key"],"veto":row["veto"]} for row in REDUCTION_PATTERNS]
    shape={"candidates":[{
        "candidate_id":"AUTO-1","title":"problem title",
        "empirical_contradiction":{
            "source_a":{"ref":"arXiv:...","claim":"fact reported by source A"},
            "source_b":{"ref":"arXiv:...","claim":"fact reported by source B"},
            "tension":"why the two reported facts create a scientific contradiction"},
        "irreducible_object":"formal/scientific object, not an algorithm",
        "mature_theory_baselines":[
            {"name":"theory 1","same_information_projection":"...","reduction_test":"..."},
            {"name":"theory 2","same_information_projection":"...","reduction_test":"..."}],
        "same_information_nonreducibility":{"claim":"...","why_each_baseline_cannot_express_prediction":"..."},
        "exact_prediction":"...","strongest_same_information_baseline":"...",
        "domain_transfer_audit":{"mature_source_domain":"...","mature_object":"...","why_not_domain_transfer":"..."},
        "saturation_scan":{"checked":True,"matched_patterns":[]},
        "cheapest_problem_falsifier":"...","endpoint_headroom_requirement":"..."}],
        "generation_notes":"may explicitly state that zero candidates survive"}
    return (
        "Strict contradiction-first ICLR research-problem generator for self-evolving LLM agents. "
        "Return zero to five research PROBLEMS, never methods. Zero is preferred to a weak candidate.\n\n"
        "Use ONLY the verified primary-source registry below. A contradiction must cite two distinct refs exactly as provided. "
        "Claims must be supported by the supplied abstract; future-work statements are not empirical facts.\n\n"
        "Before naming a new object, project identical observable information into at least two mature theories. "
        "If either theory expresses the exact prediction, discard the candidate. Domain transfer, mathematical renaming, another benchmark/metric/taxonomy/test-generator, or combining occupied atoms is not novelty.\n\n"
        "HARD NEGATIVE-SPACE VETO:\n"+json.dumps(reductions,ensure_ascii=False,separators=(",",":"))+
        "\n\nVERIFIED PRIMARY SOURCES (private abstracts; output only ref + paraphrased claim):\n"+
        json.dumps(sources,ensure_ascii=False,separators=(",",":"))+
        "\n\nReturn syntactically valid JSON only, shape:\n"+json.dumps(shape,ensure_ascii=False,separators=(",",":"))+
        "\nNo markdown/trailing commas. IDs AUTO-1..AUTO-5. Do not include authority fields; code forces them false."
    )


def reviewer_prompt(candidates: list[dict[str, Any]], evidence_by_ref: dict[str, dict[str, Any]]) -> str:
    reductions=[{"key":row["key"],"mature_theories":row["mature_theories"],"veto":row["veto"]} for row in REDUCTION_PATTERNS]
    stripped=[{k:v for k,v in row.items() if k not in {"semantic_reduction_review","authority"}} for row in candidates]
    refs=[]
    for row in candidates:
        contradiction=row.get("empirical_contradiction") or {}
        for source_key in ("source_a","source_b"):
            ref=str((contradiction.get(source_key) or {}).get("ref") or "").strip()
            if ref and ref not in refs:
                refs.append(ref)
    evidence=[]
    for ref in refs:
        record=evidence_by_ref.get(ref) or {}
        evidence.append({
            "ref":ref,
            "title":record.get("title"),
            "source_sha256":record.get("source_sha256"),
            "abstract":record.get("abstract"),
        })
    return (
        "Independent BLOCK-ONLY semantic reduction + source-grounding reviewer. You cannot authorize Paper Design, methods, experiments, P0, or GPU. "
        "For each candidate: (1) verify each stated source claim is actually supported by its supplied primary abstract; (2) test whether the exact prediction is already expressible by the negative-space ledger or any mature same-information theory. "
        "For each source claim marked supported, return one SHORT exact contiguous excerpt copied from that abstract (4-30 words). If no exact abstract excerpt supports the claim, mark supported=false and BLOCK. "
        "CLEAR means only that both source claims are grounded and no mature reduction was found in this review; it never means scientific approval.\n\nLEDGER:\n"+
        json.dumps(reductions,ensure_ascii=False,separators=(",",":"))+"\n\nPRIMARY ABSTRACTS:\n"+
        json.dumps(evidence,ensure_ascii=False,separators=(",",":"))+"\n\nCANDIDATES:\n"+
        json.dumps(stripped,ensure_ascii=False,separators=(",",":"))+
        '\n\nReturn JSON only: {"reviews":[{"candidate_id":"...","verdict":"CLEAR|BLOCK","source_claim_support":{"source_a":{"supported":true,"evidence_excerpt":"exact words from abstract"},"source_b":{"supported":true,"evidence_excerpt":"exact words from abstract"}},"matched_patterns":["known-key"],"strongest_reduction":"mature theory/object or none","reason":"..."}]}. '
        "If BLOCK uses a mature reduction not in the ledger, matched_patterns may be [] but strongest_reduction must name it."
    )
