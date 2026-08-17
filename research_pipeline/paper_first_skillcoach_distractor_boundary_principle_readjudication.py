from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation

CANDIDATE_ID = "SKILLCOACH-DISTRACTOR-SELECTION-BOUNDARY"
SEARCH_PRIMITIVE = "UNEXPLAINED_BOUNDARY"
SOURCE_REF = "arXiv:2607.01874"
SOURCE_FULLTEXT_SHA256 = "98e09b6cf2748867e3843fe1ace5525225b0d87a2821316614b6942be12fd728"
DEGRADATION_EVIDENCE_SHA256 = "c263b77c4330f4f5ae08edaac22fd89c65f3cd721bdaae07996e6e1251b83be1"
NONCOLLAPSE_EVIDENCE_SHA256 = "0c02eb569a20f741682b392eee38cbd4cfa070b854d215e8bd7dde2a9d1ddb92"
MODEL_BOUNDARY_PARAGRAPH_SHA256 = "5e625d0c123eee1c626e13100ec450df4e3d4e8f00e2deb0bd6dae6469109431"
COLLAPSE_PARAGRAPH_SHA256 = "b9f08e92fdd40183089fd41cb0c942443bdac8d9e36b4133161d79185e26d8f9"
SEMANTIC_DISTRACTOR_PARAGRAPH_SHA256 = "26c4980a7d22ee8fd0efee1597f805576dd24cdb18fe305e53309734181eb12a"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "skillcoach-distractor-boundary-principle-readjudication-20260818.json"


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
    record = records.get(SOURCE_REF) or {}
    if record.get("fulltext_sha256") != SOURCE_FULLTEXT_SHA256:
        raise ValueError("SkillCoach fulltext provenance drift")

    scope = (
        "SkillCoach arXiv:2607.01874, restricted to the Section 4.4 evidence that selection F1 crosses a preregistered "
        "degradation threshold as frozen skill libraries grow and that GPT-5.5/Opus 4.7 remain outside the paper's collapse "
        "criterion at 50k distractors. The scoped claim to close is that these two observations by themselves identify an "
        "unexplained self-evolution mechanism or a new library-size phase transition."
    )
    counter = {
        "type": "COUNTER_MECHANISM_SUPPORTED",
        "statement": (
            "SkillCoach already provides a matched positive explanation for the scoped boundary. Section 4.4 freezes the agent "
            "and removes tool execution, environment failures, and verifier noise so the experiment is a pure candidate-selection "
            "stress test. At fixed library size (50 distractors), changing only distractor semantic type causes large F1 changes: "
            "high-similarity distractors are substantially more damaging than random unrelated distractors. Across the size sweep, "
            "stronger frozen selectors degrade later and may remain outside collapse through 50k, whereas weaker selectors cross "
            "collapse earlier. Thus the reported boundary is explained first by candidate-space semantic confusability interacting "
            "with frozen selector capability; it is a routing/retrieval robustness diagnostic, not evidence of an update or "
            "self-evolution mechanism."
        ),
        "opposite_prediction": (
            "If candidate-space confusability and frozen selector capability explain the boundary, then at the same distractor "
            "count more semantically similar candidates should lower selection F1, and stronger frozen selectors should tolerate "
            "larger libraries before degradation/collapse. SkillCoach reports both predictions: at 50 distractors high-similarity "
            "candidates lower F1 relative to random unrelated candidates for GPT-5.5, Opus 4.7, and DeepSeek V4 Flash, while "
            "model-specific degradation/collapse scales shift strongly with selector capability."
        ),
        "opposite_principle": (
            "A frozen agent's failure to select the correct artifact from a growing, semantically overlapping candidate set is "
            "first a candidate-confusability and selector-capacity problem. A library-size threshold is not a new self-evolution "
            "primitive unless an evolution-specific residual survives matched candidate-count, semantic-overlap, search-interface, "
            "and frozen-selector controls."
        ),
        "opposite_search_seed": (
            "Search for matched libraries with the same candidate count, semantic-confusability distribution, query/gold support, "
            "browser/search budget, and frozen selector, but different evolution histories or artifact-generation dynamics. Require "
            "a reproducible boundary shift that a same-information retrieval/ranking/confusability model cannot predict."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "counter_prediction_observed": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_REF,
            f"primary-fulltext:{SOURCE_REF}#sha256={SOURCE_FULLTEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={MODEL_BOUNDARY_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={COLLAPSE_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={SEMANTIC_DISTRACTOR_PARAGRAPH_SHA256}",
            f"fresh-primary-evidence:{SOURCE_REF}#sha256={DEGRADATION_EVIDENCE_SHA256}",
            f"fresh-primary-evidence:{SOURCE_REF}#sha256={NONCOLLAPSE_EVIDENCE_SHA256}",
        ],
        "alternative_explanations_ruled_out": [
            "The boundary is caused by tool execution, environment failure, or verifier noise: Section 4.4 explicitly removes those factors and isolates skill selection through a constrained browser-style interface.",
            "Library size alone is the identified mechanism: false; with the count fixed at 50, high-similarity distractors are substantially more harmful than random unrelated distractors.",
            "All models share one count-only collapse threshold: false; degradation and collapse scales differ strongly by frozen model, and GPT-5.5/Opus 4.7 remain outside collapse at 50k.",
            "The experiment observes a self-updating agent: false; the boundary sweep is a frozen-model selection stress test and does not manipulate an update/evolution process.",
            "Closing these boundary observations closes SkillCoach's process-supervision or SFT results: false; the closure is limited to the two exact library-size degradation/non-collapse evidence items."
        ],
        "reopen_condition": (
            "Reopen only with new primary or provenance-audited first-party evidence that matches candidate count, semantic-overlap "
            "or confusability distribution, gold-skill support, query distribution, browser/search interface and budget, frozen model, "
            "and evaluation metric, yet shows a reproducible boundary shift attributable to an artifact-evolution or self-evolution "
            "state that remains unexplained by same-information retrieval/ranking margin, candidate-confusability, selector-capacity, "
            "or ordinary distribution-shift baselines."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"SkillCoach boundary counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "title": "SkillCoach distractor boundaries reduce to frozen selector capacity under candidate-space confusability",
        "adjudication_date": "2026-08-18",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_ai_formulation_has_scientific_authority": False,
        "skillcoach_training_or_process_supervision_falsified": False,
        "dead_end_scope": scope,
        "fresh_phenomenon_closure": {
            "source_ref": SOURCE_REF,
            "closed_evidence_sha256": [DEGRADATION_EVIDENCE_SHA256, NONCOLLAPSE_EVIDENCE_SHA256],
            "closure_scope": "Section 4.4 library-size degradation threshold and 50k non-collapse evidence only",
            "scientific_authority": False,
        },
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "COUNTER_MECHANISM_SUPPORTED",
            "counter_explanation": counter,
            "audit": audit,
        },
        "scientific_interpretation": {
            "safe_claim": (
                "SkillCoach's library-size boundary is a useful deployment diagnostic, but the source itself shows that its scale "
                "is governed by frozen selector capability and semantic candidate confusability; the reported threshold does not "
                "by itself establish a new self-evolution mechanism."
            ),
            "do_not_say": [
                "large skill libraries are harmless",
                "SkillCoach's process supervision is invalid",
                "all evidence in arXiv:2607.01874 is closed",
                "distractor-boundary measurements have no deployment value",
            ],
            "new_search_basin": "evolution-specific-residual-after-confusability-matching",
        },
        "authority": {
            "ai_review_authorizes_dead_end": False,
            "source_internal_selection_stress_test_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "primary_fulltext": SOURCE_FULLTEXT_SHA256,
            "model_boundary_evidence": MODEL_BOUNDARY_PARAGRAPH_SHA256,
            "collapse_evidence": COLLAPSE_PARAGRAPH_SHA256,
            "semantic_distractor_evidence": SEMANTIC_DISTRACTOR_PARAGRAPH_SHA256,
            "closed_degradation_evidence": DEGRADATION_EVIDENCE_SHA256,
            "closed_noncollapse_evidence": NONCOLLAPSE_EVIDENCE_SHA256,
        },
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
