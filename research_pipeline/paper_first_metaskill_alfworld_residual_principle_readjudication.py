from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation


CANDIDATE_ID = "METASKILL-ALFWORLD-SLOW-LOOP-RESIDUAL"
SEARCH_PRIMITIVE = "UNEXPLAINED_BOUNDARY"
SOURCE_REF = "arXiv:2607.05297"
SOURCE_FULLTEXT_SHA256 = "84e40d16a13395870ca336bd8999e727d20aacc134f1fb821292a7452bc6fb8a"
TARGET_EVIDENCE_SHA256 = "c28f8e64348e3cdb498f08606d3ce0d849710e2c9707b7ba9a6b65d9e39ef6d0"
APPENDIX_COMPONENT_ABLATION_SHA256 = "ce524eda4377e0a18709b37e600f9388731c94baa1d81a07eb2abef5e3344dd4"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "metaskill-alfworld-slow-loop-residual-principle-readjudication-20260818.json"


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
        raise ValueError("MetaSkill-Evolve fulltext provenance drift")

    scope = (
        "MetaSkill-Evolve arXiv:2607.05297, restricted to the ALFWorld evidence-level claim that the slow meta-skill loop's "
        "+1.92-point gain over the 92.31 Single-Level/task-skill-saturated baseline is an unexplained residual that could define "
        "a new self-evolution mechanism after ordinary ceiling, finite-sample, or reweighting explanations are considered."
    )
    counter = {
        "type": "COUNTER_MECHANISM_SUPPORTED",
        "statement": (
            "The scoped +1.92 ALFWorld residual is already decomposed by the same primary source. Appendix E reports that the "
            "full two-timescale system reaches 94.23, while removing only cross-branch retrieval returns accuracy to 92.31, "
            "exactly the Single-Level baseline; the authors explicitly state that cross-branch transfer of reusable sub-routines "
            "accounts for the whole +1.92 improvement. Freezing the slow loop (no meta-updates) also returns to 92.31 exactly, "
            "while removing the edit-proposal policy drops performance from 94.23 to 86.54. Thus the observed aggregate residual "
            "is not unexplained negative space: source-internal component interventions positively identify the operative "
            "cross-branch/meta-update pathway and leave no reported residual requiring a new standalone mechanism."
        ),
        "opposite_prediction": (
            "If the ALFWorld +1.92 gain is carried by the source's cross-branch slow-loop mechanism rather than by an additional "
            "unmodeled residual, then disabling cross-branch retrieval or disabling meta-updates should erase that gain and return "
            "the system to the Single-Level operating point. The reported ablations do exactly this: both no-cross-branch and "
            "no-meta-updates are 92.31 versus 94.23 for the full system; removing the edit-proposal policy is even more damaging "
            "at 86.54."
        ),
        "opposite_principle": (
            "An aggregate improvement is not an unexplained self-evolution residual when the source's own matched component "
            "interventions already remove the entire gain. Source-internal causal/component decomposition must be exhausted before "
            "promoting that same gain into a new paper problem."
        ),
        "opposite_search_seed": (
            "Search for a different evidence-level phenomenon, or reopen this one only if new primary/first-party evidence under "
            "the same frozen executor and ALFWorld protocol shows a reproducible residual after cross-branch transfer, slow-loop "
            "meta-updates, and edit-proposal-policy effects are explicitly matched or intervened on. Do not reopen from the same "
            "+1.92 aggregate row, another wording of task-skill saturation, or an unablated two-timescale comparison."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "counter_prediction_observed": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_REF,
            f"primary-fulltext:{SOURCE_REF}#sha256={SOURCE_FULLTEXT_SHA256}",
            f"primary-fulltext-evidence:{SOURCE_REF}#sha256={APPENDIX_COMPONENT_ABLATION_SHA256}",
            f"fresh-primary-evidence:{SOURCE_REF}#sha256={TARGET_EVIDENCE_SHA256}",
        ],
        "alternative_explanations_ruled_out": [
            "The +1.92 gain remains after removing cross-branch transfer: false; no-cross-branch is 92.31, exactly the Single-Level baseline.",
            "The slow loop is unnecessary and the +1.92 is merely task-skill evolution: false; no-meta-updates is also 92.31, exactly the Single-Level row.",
            "The source offers only an aggregate correlation with no mechanism intervention: false; Appendix E separately ablates cross-branch retrieval, meta-updates, and the edit-proposal policy on ALFWorld.",
            "Closing this residual means MetaSkill-Evolve has no useful mechanism or that all MetaSkill evidence is closed: false; the closure is restricted to the exact +1.92 ALFWorld residual evidence item and leaves adjacent source phenomena eligible."
        ],
        "reopen_condition": (
            "Reopen only with new primary or provenance-audited first-party evidence that holds the frozen Gemma executor, ALFWorld "
            "task/evaluation protocol, task-skill state, rollout budget, and evaluation information comparable while independently "
            "matching or intervening on cross-branch retrieval, slow-loop meta-updates, and edit-proposal-policy behavior, and still "
            "finds a replicated held-out gain or sign change not expressed by those source-identified components or ordinary "
            "ceiling/finite-sample effects."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"MetaSkill ALFWorld residual counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "title": "MetaSkill ALFWorld +1.92 residual is already explained by the source's own component ablations",
        "adjudication_date": "2026-08-18",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_ai_formulation_has_scientific_authority": False,
        "broader_two_timescale_meta_skill_value_falsified": False,
        "dead_end_scope": scope,
        "fresh_phenomenon_closure": {
            "source_ref": SOURCE_REF,
            "closed_evidence_sha256": [TARGET_EVIDENCE_SHA256],
            "closure_scope": "the ALFWorld +1.92 slow-loop residual over the 92.31 Single-Level/task-skill-saturated baseline only",
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
                "The ALFWorld +1.92 observation is real, but it is not unexplained: MetaSkill-Evolve's own ablations return "
                "no-cross-branch and no-meta-updates to the 92.31 Single-Level baseline and explicitly attribute the full residual "
                "to cross-branch transfer within the slow loop."
            ),
            "do_not_say": [
                "two-timescale meta-skill evolution is useless",
                "cross-branch transfer can never produce a novel phenomenon",
                "all evidence in arXiv:2607.05297 is closed",
                "the +1.92 gain is statistically false",
            ],
            "new_search_basin": "residual-beyond-source-component-ablation",
        },
        "authority": {
            "ai_review_authorizes_dead_end": False,
            "source_internal_component_ablation_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "primary_fulltext": SOURCE_FULLTEXT_SHA256,
            "appendix_component_ablation_evidence": APPENDIX_COMPONENT_ABLATION_SHA256,
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
