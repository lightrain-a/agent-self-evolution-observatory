from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation

CANDIDATE_ID = "COMFYCLAW-PROMPT-ONLY-REFINEMENT-BOUNDARY"
SEARCH_PRIMITIVE = "UNEXPLAINED_BOUNDARY"
SOURCE_REF = "arXiv:2607.01709"
SOURCE_FULLTEXT_SHA256 = "18f97f89b8b61afc4c57f2141886d440f1e2998e47526d5a5cd9642e9479ffb5"
TARGET_EVIDENCE_SHA256 = "c1edb9836a1b0773d35b84501e2b7bb2150cfadf7cec9260f57e1297cd48b68c"
GRAPH_INTERFACE_PARAGRAPH_SHA256 = "6cc78786fb71bdcfc51e720b7c7f07f3c6d3e112cedf82033d38a6066e97beeb"
VERIFIER_FEEDBACK_PARAGRAPH_SHA256 = "88d016fd3173d186d318a1b5e644ed1ba7b7e30a07b567b752048a6bc764c05c"
EDIT_COMPOSITION_PARAGRAPH_SHA256 = "006626c37d296235805be8715e7936de8aa11f1e8b78ae58e3ecac8a1afe1997"
STRUCTURAL_REPAIR_PARAGRAPH_SHA256 = "516b29015b6e9ffaadf8d838bf3471836600d799e0ebcb910ce730aeb592be55"
BEST_SO_FAR_PARAGRAPH_SHA256 = "019c506308985550a60bcb59fa74708abbade1c7bb6c46a43b2e96cc0595bdba"
VERIFIER_DRIVEN_REPAIR_PARAGRAPH_SHA256 = "ccb85ce8728d6f1dd7297e6deb7648636a3d2da1acb999699efa436fde032e4e"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "comfyclaw-prompt-only-refinement-principle-readjudication-20260818.json"


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
        raise ValueError("ComfyClaw fulltext provenance drift")

    scope = (
        "ComfyClaw arXiv:2607.01709, restricted to the exact qualitative evidence item 'Closed-loop workflow refinement "
        "repairs failures that prompt-only rewriting often cannot.' The scoped claim to close is that this observation by "
        "itself exposes an unexplained self-evolution mechanism beyond ordinary action-space expansion and feedback control."
    )
    counter = {
        "type": "COUNTER_MECHANISM_SUPPORTED",
        "statement": (
            "The same primary source already identifies why the closed loop can repair cases that prompt-only rewriting cannot. "
            "ComfyClaw changes the available intervention surface: its graph interface can revise both text and the executable "
            "pipeline, including LoRA insertion/weights, regional attention and masks, sampler/guidance parameters, graph topology, "
            "and multi-pass refinement. Across 35,612 workflow events, only 39.3% are prompt-text edits and 60.7% operate on those "
            "non-prompt surfaces. The verifier additionally supplies localized failure descriptions and concrete workflow edits; "
            "the source's qualitative trajectories show those suggestions triggering structural repairs and a best-so-far buffer "
            "protecting against non-monotone retries. Thus the prompt-only gap is source-internally explained by a strictly larger "
            "action/intervention space plus localized feedback control, not left as unexplained negative space."
        ),
        "opposite_prediction": (
            "If action-space expansion plus localized verifier feedback explains the prompt-only gap, successful repairs should "
            "frequently require interventions unavailable to text rewriting and should follow failure-specific feedback rather than "
            "blind repetition. The source reports exactly this: 60.7% of edits are non-prompt, including hyperparameters, regional/"
            "mask topology, LoRA/checkpoint choices and multi-pass design; concrete examples stack two LoRAs, add regional attention, "
            "change regional splits, remove ineffective LoRAs after verifier failures, and recover from worse intermediate attempts."
        ),
        "opposite_principle": (
            "A richer controller repairing failures that a restricted prompt-only controller cannot is not a new self-evolution "
            "mechanism unless a residual survives matched action space, intervention budget, verifier information, and retry/best-so-"
            "far control. Treatment-surface capability must be matched before the remaining gap can be interpreted mechanistically."
        ),
        "opposite_search_seed": (
            "Reopen only on matched controllers that expose the same graph edits, LoRA/regional/mask/hyperparameter operations, "
            "verifier-localized feedback, retry budget and best-so-far retention, but differ in an evolution-specific state or learned "
            "update mechanism. Require a replicated repair or generalization residual that survives these same-information controls."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "counter_prediction_observed": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_REF,
            f"primary-fulltext:{SOURCE_REF}#sha256={SOURCE_FULLTEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={GRAPH_INTERFACE_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={VERIFIER_FEEDBACK_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={EDIT_COMPOSITION_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={STRUCTURAL_REPAIR_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={BEST_SO_FAR_PARAGRAPH_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={VERIFIER_DRIVEN_REPAIR_PARAGRAPH_SHA256}",
            f"fresh-primary-evidence:{SOURCE_REF}#sha256={TARGET_EVIDENCE_SHA256}",
        ],
        "alternative_explanations_ruled_out": [
            "The closed loop differs from prompt-only only by more attempts: false; the source explicitly exposes graph, LoRA, regional/mask, parameter, and multi-pass interventions that prompt-only cannot perform.",
            "The repair loop is blind retry: false; each iteration consumes requirement-level, localized verifier failures and concrete workflow-edit suggestions.",
            "The qualitative examples rely only on prompt rewriting: false; the paper documents LoRA stacking, regional-attention insertion, regional-split changes and removal of ineffective LoRAs.",
            "The improvement can be read as monotone hill climbing alone: false; the source documents worse intermediate attempts and a best-so-far buffer that preserves the best valid candidate while later iterations recover.",
            "Closing this prompt-only boundary falsifies ComfyClaw skill evolution: false; the closure is limited to the exact repair-vs-prompt-only evidence item and does not close the separate evolved-skill usage or skill-evolution benefit questions."
        ],
        "reopen_condition": (
            "Reopen only with new primary or provenance-audited first-party evidence matching graph-edit action space, LoRA/regional/"
            "mask/hyperparameter operations, verifier feedback, iteration and render budget, best-so-far retention, image backbone, "
            "agent model, prompt difficulty and evaluation information, while varying an evolution-specific state/mechanism and "
            "showing a replicated repair residual beyond ordinary feedback-control and action-space-capability explanations."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"ComfyClaw prompt-only counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "title": "ComfyClaw prompt-only repair gap reduces to richer workflow interventions plus localized verifier feedback",
        "adjudication_date": "2026-08-18",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_ai_formulation_has_scientific_authority": False,
        "comfyclaw_skill_evolution_falsified": False,
        "dead_end_scope": scope,
        "fresh_phenomenon_closure": {
            "source_ref": SOURCE_REF,
            "closed_evidence_sha256": [TARGET_EVIDENCE_SHA256],
            "closure_scope": "the exact prompt-only-vs-closed-loop workflow repair qualitative boundary only",
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
                "ComfyClaw's closed loop repairs prompt-only failures because it is not a prompt-only treatment: it combines a "
                "larger executable workflow-edit action space with localized verifier feedback and best-so-far retry control."
            ),
            "do_not_say": [
                "workflow refinement is useless",
                "ComfyClaw skill evolution is not beneficial",
                "all evidence in arXiv:2607.01709 is closed",
                "feedback-guided graph editing can never yield a novel residual",
            ],
            "new_search_basin": "evolution-residual-after-action-space-and-feedback-matching",
        },
        "authority": {
            "ai_review_authorizes_dead_end": False,
            "source_internal_action_space_and_feedback_evidence_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "primary_fulltext": SOURCE_FULLTEXT_SHA256,
            "graph_interface_evidence": GRAPH_INTERFACE_PARAGRAPH_SHA256,
            "verifier_feedback_evidence": VERIFIER_FEEDBACK_PARAGRAPH_SHA256,
            "edit_composition_evidence": EDIT_COMPOSITION_PARAGRAPH_SHA256,
            "structural_repair_evidence": STRUCTURAL_REPAIR_PARAGRAPH_SHA256,
            "best_so_far_evidence": BEST_SO_FAR_PARAGRAPH_SHA256,
            "verifier_driven_repair_evidence": VERIFIER_DRIVEN_REPAIR_PARAGRAPH_SHA256,
            "closed_fresh_evidence": TARGET_EVIDENCE_SHA256,
        },
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
