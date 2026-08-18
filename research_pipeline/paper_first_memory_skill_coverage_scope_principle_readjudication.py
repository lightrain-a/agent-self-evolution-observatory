from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation


CANDIDATE_ID = "AUTO-1-MEMORY-SKILL-COVERAGE-SCOPE"
SEARCH_PRIMITIVE = "ASSUMPTION_BREAK"
SOURCE_A = "arXiv:2608.11654"
SOURCE_B = "arXiv:2608.11888"
SOURCE_A_FULLTEXT_SHA256 = "aad633809bf2bd92f2fc9c6c63e693050a7bad5ae09808418e8374a056ea13dd"
SOURCE_B_FULLTEXT_SHA256 = "b59fdd9d3b2baaa6d8b453661dd29445ecddb555b13452489a815171a3b42dc9"
SOURCE_A_MONOTONICITY_SHA256 = "cf48ea56e9679e686974771a4bfb51f666f97827c115e11dee32f1bb68bf20c7"
SOURCE_A_LIMITATION_SHA256 = "645dfe25fefa911e0c8cb6b03a6afc02ecf5339e1693cf8c36dd79fac51715a1"
SOURCE_B_TIF_SHA256 = "38ed2a663bd34ddfd440342e0acef44ca0254a9419bd2df15a83f945c7fdced1"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "memory-skill-coverage-scope-principle-readjudication-20260818.json"


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
    source_a = records.get(SOURCE_A) or {}
    source_b = records.get(SOURCE_B) or {}
    if source_a.get("fulltext_sha256") != SOURCE_A_FULLTEXT_SHA256:
        raise ValueError("formal-memory fulltext provenance drift")
    if source_b.get("fulltext_sha256") != SOURCE_B_FULLTEXT_SHA256:
        raise ValueError("skill-harm fulltext provenance drift")

    scope = (
        "AUTO-1 ASSUMPTION_BREAK restricted to arXiv:2608.11654's idealized generation-operator monotonicity "
        "('more memory is never worse, so coverage is non-decreasing in the stored set') and arXiv:2608.11888's "
        "paired skill-induced functional failures, claiming that loading a relevant procedural skill retracts a previously "
        "correct action and therefore falsifies the formal memory assumption or defines a new procedural-memory retraction primitive."
    )
    counter = {
        "type": "SAME_INFORMATION_REDUCTION",
        "statement": (
            "The claimed assumption break compares different scientific quantities. arXiv:2608.11654 defines memory as an "
            "event subset whose generation operator produces a knowledge span, and its monotonicity assumption is a structural "
            "assumption about coverage/answerability under set inclusion. The same paper explicitly separates coverage from "
            "correctness and states that the assumptions hold only approximately in practice: real extraction is at best locally "
            "monotone and a conflicting claim can overturn earlier conclusions, including previously correct coverage. "
            "arXiv:2608.11888 instead measures end-to-end execution correctness and cost under paired skill/no-skill or matched-skill "
            "configurations. Its dominant functional failures are Task-Implementation Faults, and the paper attributes them to "
            "topically relevant reusable defaults/examples/templates that conflict with or incompletely cover task-required fields, "
            "APIs, paths, output formats, domain rules, or environment constraints. Thus the skill-harm result is real but does not "
            "falsify the formal set-coverage assumption: it changes execution utility on a different causal/measurement surface, "
            "while the formal source already records conflict-driven non-monotonic practical behavior. The remaining failure is "
            "expressible by task-skill compatibility/negative transfer plus the coverage-versus-correctness distinction without a "
            "new procedural-memory retraction primitive."
        ),
        "opposite_prediction": (
            "If the scope/measurement reduction is correct, a loaded skill may lower task execution success even when the stored "
            "event/knowledge span does not shrink: harm should concentrate where skill content introduces conflicting, partial, or "
            "over-broad procedural guidance relative to concrete task requirements. Conversely, a genuine falsification of the "
            "formal monotonicity assumption would require the framework's own answerability/coverage quantity to decrease when the "
            "stored event set is enlarged under a matched generation operator, not merely an endpoint execution failure under a "
            "different procedural configuration. The two sources report exactly the former situation, not the latter."
        ),
        "opposite_principle": (
            "Representation-level coverage monotonicity is not end-to-end execution-utility monotonicity. An ASSUMPTION_BREAK "
            "requires an operational bridge showing that both sources vary and measure the same formal object; procedural skill "
            "harm cannot falsify a set-coverage assumption when correctness/conflict semantics and executor behavior are outside "
            "that monotonic quantity and are already acknowledged as non-monotonic in the formal source."
        ),
        "opposite_search_seed": (
            "Search for a true coverage-level counterexample: provenance-audited matched memory sets A subset B under the same "
            "generation operator, query distribution, correctness/conflict semantics, executor, and evaluation contract, where the "
            "formal answerability/coverage utility decreases after adding B\\A. Alternatively, for procedural skills, match task-skill "
            "compatibility/conflict, skill content, realized uptake, executor, and budget and require an additional preregistered "
            "retraction variable beyond ordinary negative transfer and instruction-following. Do not reopen from another paired "
            "skill-induced endpoint failure alone."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "same_information_reduction_verified": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_A,
            f"primary-fulltext:{SOURCE_A}#sha256={SOURCE_A_FULLTEXT_SHA256}",
            f"primary-evidence:{SOURCE_A}#sha256={SOURCE_A_MONOTONICITY_SHA256}",
            f"primary-evidence:{SOURCE_A}#sha256={SOURCE_A_LIMITATION_SHA256}",
            SOURCE_B,
            f"primary-fulltext:{SOURCE_B}#sha256={SOURCE_B_FULLTEXT_SHA256}",
            f"primary-evidence:{SOURCE_B}#sha256={SOURCE_B_TIF_SHA256}",
            "repo:generated/auto1-relevant-skill-misexecution-principle-readjudication-20260817.json",
            "repo:generated/memory-monotonicity-consolidation-principle-readjudication-20260818.json",
        ],
        "alternative_explanations_ruled_out": [
            "The formal monotonicity statement is an empirical law over end-to-end task correctness: false; the paper defines it on the generation operator's knowledge-span coverage and explicitly says coverage is not correctness.",
            "The formal framework assumes practical extraction is globally monotone even with conflicts: false; it states real extraction is at best locally monotone and conflicting claims can overturn earlier conclusions and previously correct coverage.",
            "The skill-induced failures are not causal or paired: false; arXiv:2608.11888 uses same-task no-skill or semantically matched-skill references as pseudo-oracles and confirms target/reference execution differences.",
            "Topical relevance establishes formal compatibility and leaves a novel retraction mechanism unexplained: false; the skill paper's dominant TIF account and future-work guidance explicitly identify conflicting or incomplete defaults, examples, templates, paths, formats, rules, and environment assumptions as the relevant compatibility surface.",
            "Calling a loaded skill a memory event makes the two quantities identical: false; even under that representation, the formal source separates coverage/answerability from correctness and acknowledges conflict-driven non-monotonic behavior at the end-to-end layer."
        ],
        "reopen_condition": (
            "Reopen only with primary or provenance-audited first-party evidence that either (a) directly measures the formal "
            "answerability/coverage utility and shows it decreases for a strict stored-event superset under the same generation "
            "operator, query distribution, conflict/correctness semantics, executor, and budget, or (b) for procedural skills, "
            "matches task-requirement-level compatibility/conflict, exact skill content, realized action-level uptake, executor, "
            "budget, and generic instruction-following difficulty yet finds a preregistered retraction feature with residual "
            "predictive power beyond same-information negative-transfer/compatibility baselines. Another aggregate or paired "
            "skill-harm count is insufficient."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"memory-skill coverage-scope counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "title": "Formal memory coverage monotonicity and skill-induced execution harm live on different operational surfaces",
        "adjudication_date": "2026-08-18",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_ai_review_has_scientific_authority": False,
        "broader_skill_harm_or_memory_nonmonotonicity_falsified": False,
        "dead_end_scope": scope,
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "SAME_INFORMATION_REDUCTION",
            "counter_explanation": counter,
            "audit": audit,
        },
        "scientific_interpretation": {
            "safe_claim": (
                "The paired skill-induced failures are real, but they do not falsify the formal memory paper's idealized "
                "coverage monotonicity assumption. The sources measure different objects, and both sources already support "
                "conflict/compatibility explanations for practical non-monotonic execution behavior."
            ),
            "do_not_say": [
                "skills cannot harm agents",
                "memory utility is always monotone",
                "the formal memory framework explains every procedural skill failure",
                "all evidence in either source is closed",
            ],
            "new_search_basin": "coverage-level-monotonicity-counterexample-or-compatibility-matched-retraction-residual",
        },
        "authority": {
            "ai_review_authorizes_dead_end": False,
            "primary_same_information_scope_reduction_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "source_a_fulltext": SOURCE_A_FULLTEXT_SHA256,
            "source_b_fulltext": SOURCE_B_FULLTEXT_SHA256,
            "source_a_monotonicity": SOURCE_A_MONOTONICITY_SHA256,
            "source_a_limitation": SOURCE_A_LIMITATION_SHA256,
            "source_b_tif": SOURCE_B_TIF_SHA256,
        },
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
