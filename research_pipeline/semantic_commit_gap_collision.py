from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "semantic-commit-gap-collision-20260824.json"
V19_ASSET = PROJECT_ROOT / "research_pipeline" / "v19r003_forced_switch_failure_assets_20260824.json"
SEARCH_MEMORY = PROJECT_ROOT / "generated" / "research-memory-wiki.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_semantic_commit_gap_collision(*, generated_at: str | None = None) -> dict[str, Any]:
    v19 = _load(V19_ASSET)
    memory = _load(SEARCH_MEMORY)
    memory_by_id = {str(row.get("memory_id") or ""): row for row in memory.get("entries") or [] if isinstance(row, dict)}

    uptake_closure = memory_by_id["MEM-SEAR-58fcdf68f1ecde2502"]
    skill_failure_closure = memory_by_id["MEM-SEAR-dfa3fa70da275fca56"]
    semantic_asset = v19["semantic_observability_asset"]
    action_asset = v19["action_turn_asset"]

    stages = [
        {
            "stage": 1,
            "name": "ACTION_ENDPOINT_REACHED",
            "question": "Did the bounded agent actually reach and invoke the declared update action rather than consume the turn budget in planning/diagnostics?",
            "current_evidence": action_asset["signature"],
            "disposition": "PROTOCOL_EXECUTION_GATE",
            "scientific_object": False,
            "reduction": "A missing declared action endpoint is protocol/runtime nonexecution, not evidence about the update mechanism.",
        },
        {
            "stage": 2,
            "name": "PERSISTED_STATE_DELTA_VERIFIED",
            "question": "Did the accepted action produce an independently observable persisted state/parameter/artifact delta?",
            "current_evidence": semantic_asset["signature"],
            "disposition": "SUPPORT_OPERATIONALIZATION_GATE",
            "scientific_object": False,
            "reduction": "A syntactically successful action with no verifiable persistent delta is an observability/support failure. It must be rejected before a scientific unit, not counted as a behavioral outcome.",
        },
        {
            "stage": 3,
            "name": "PERSISTED_ARTIFACT_SEMANTICALLY_VALID",
            "question": "Given a real persisted delta, is the resulting memory/skill/tool/workflow state faithful, complete, compatible, and valid for later execution?",
            "disposition": "MATURE_TRANSITION_OR_TRANSACTION_VALIDATION",
            "scientific_object": False,
            "reduction": "Memory-transition verification and semantic-transaction/contract validation already treat write correctness, preservation, staged commit, recovery, and compatibility as explicit objects.",
        },
        {
            "stage": 4,
            "name": "FUTURE_ENACTMENT_OR_UPTAKE",
            "question": "Given a valid persisted artifact that is available/retrieved, does the future executor actually use it in the intended action trajectory?",
            "disposition": "MATURE_UPTAKE_ENACTABILITY_REDUCTION",
            "scientific_object": False,
            "reduction": "Canonical skill evidence and current literature already separate retrieval/identification, realized uptake/use, and downstream success; task-artifact compatibility and instruction following explain many loaded-artifact failures once uptake is observed.",
        },
    ]

    closest_work = [
        {
            "title": "TRUSTMEM: Learning Trustworthy Memory Consolidation for LLM Agents with Long-Term Memory",
            "source": "arXiv:2606.25161",
            "published": "2026-06-23",
            "collision_layer": "stage-3 memory transition validity",
            "relevance": "Uses a Memory Transition Verifier for coverage, preservation, and faithfulness of generated write/revise/delete memory transitions.",
        },
        {
            "title": "Cordon: Semantic Transactions for Tool-Using LLM Agents",
            "source": "arXiv:2606.17573",
            "published": "2026-06-16",
            "collision_layer": "stage-3 commit semantics",
            "relevance": "Introduces task-level semantic transactions with staged state/effects, validation, commit, rollback, recovery, and audit.",
        },
        {
            "title": "Diagnosing Retrieval vs. Utilization Bottlenecks in LLM Agent Memory",
            "source": "arXiv:2603.02473",
            "published": "2026-03-02",
            "collision_layer": "stage-4 retrieval versus utilization",
            "relevance": "Separates write strategy, retrieval quality, and memory utilization behavior rather than treating end-to-end success as one stage.",
        },
        {
            "title": "SkillJuror: Measuring How Agent Skill Organization Changes Runtime Behavior",
            "source": "arXiv:2606.11543",
            "published": "2026-06-10",
            "collision_layer": "stage-4 realized skill uptake",
            "relevance": "Measures effective uptake events and trajectory-level skill-resource use under semantically controlled skill variants.",
        },
        {
            "title": "Demystifying Agent Skills: Why They Work-Until They Don't",
            "source": "arXiv:2608.14036",
            "published": "2026-08-14",
            "collision_layer": "stage-4 retrieval/use/success decoupling",
            "relevance": "Treats skill identification/actual use and downstream success as distinct measurements; exact annotated invocation is not sufficient or necessary for success.",
        },
        {
            "title": "Agent Skills Can Be Harmful: An Empirical Study of Skill-Induced Failures in LLM Agents",
            "source": "arXiv:2608.11888",
            "published": "2026-08-12",
            "collision_layer": "stage-4 task-artifact compatibility and execution",
            "relevance": "Uses paired skill/no-skill or matched-skill executions to attribute functional failures and finds implementation omissions/conflicts from seemingly relevant loaded skills.",
        },
        {
            "title": "Practice Makes Unsafe: Skill Misevolution in Self-Improving LLM Agents",
            "source": "arXiv:2608.12851",
            "published": "2026-08-13",
            "collision_layer": "write-retrieve-execute lifecycle",
            "relevance": "Separates unsafe artifact authoring, later retrieval/reuse, and fresh-session harm across a persistent skill lifecycle.",
        },
        {
            "title": "Memento-Skills: Let Agents Design Agents",
            "source": "arXiv:2603.18743",
            "published": "2026-03-19",
            "collision_layer": "persistent skill write/read loop",
            "relevance": "Externalizes evolving skills as persistent files with explicit read/write continual-learning phases.",
        },
    ]

    same_information_reduction = {
        "status": "REDUCED",
        "candidate_claim": "There is a new semantic commit gap between an agent declaring/persisting a self-update and that update changing future behavior.",
        "strongest_reduction": (
            "The proposed gap decomposes into already-observable lifecycle stages. Failure before a verified persisted delta is protocol/support operationalization. "
            "Failure of the persisted object itself is transition/transaction validity. Failure after a valid artifact is exposed to the executor is uptake/enactability, "
            "task-artifact compatibility, negative transfer, and instruction-following unless an additional matched residual survives."
        ),
        "canonical_support": [
            semantic_asset["signature"],
            uptake_closure["memory_id"],
            skill_failure_closure["memory_id"],
            "repo:research_pipeline/paper_first_fresh_saturation.py#artifact-uptake-after-retrieval",
            "repo:research_pipeline/paper_first_fresh_saturation.py#model-scaffold-enactability",
            "repo:research_pipeline/paper_first_fresh_saturation.py#self-model-lineage-desynchronization",
        ],
        "current_source_support": [row["source"] for row in closest_work],
        "decision": "STOP_CURRENT_SEMANTIC_COMMIT_GAP_FORMULATION",
    }

    reopen = {
        "status": "NOT_CURRENTLY_SUPPORTED",
        "required_residual": (
            "Construct provenance-audited matched future executions where the persisted artifact bytes, artifact metadata visible to the executor, semantic validity, retrieval/exposure, "
            "task state, executor/model, prompt/interface, action support, compute, and generic instruction-following difficulty are matched, but the causal history of whether the "
            "artifact was self-written versus externally installed differs. Require a preregistered difference in realized future enactment that remains after giving the strongest "
            "same-information uptake/enactability and self-model/history baseline every observable provenance/history feature."
        ),
        "why_this_is_material": (
            "Only such a provenance-conditioned enactment residual would move the object beyond write success, transition validity, retrieval/use, compatibility, and ordinary retained-history/self-model effects."
        ),
        "cheapest_falsifier_before_any_model_call": (
            "First prove that the target runtime can produce matched final states with byte-identical artifacts and identical executor-visible metadata/context while varying only self-write provenance. "
            "If provenance cannot be varied without changing observable history/context, or a direct history-conditioned policy can represent the same decision, STOP without provider/GPU execution."
        ),
    }

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "candidate_id": "SCG-001",
        "title": "Semantic Commit Gap: persisted self-update versus future enactment",
        "status": "STOP_CURRENT_FORMULATION_MATURE_LIFECYCLE_REDUCTION",
        "source_failure_asset": semantic_asset["signature"],
        "source_candidate": v19["candidate_id"],
        "policy": {
            "failure_memory_is_search_seed_not_scientific_positive_evidence": True,
            "support_stop_cannot_be_promoted_to_problem_evidence": True,
            "lifecycle_stages_must_be_separated_before_naming_a_new_gap": True,
            "same_information_reduction_precedes_problem_gate": True,
            "latest_primary_collision_check_required": True,
            "zero_survivor_is_valid": True,
            "no_v19_holdout_or_paid_execution_consumed": True,
        },
        "four_stage_decomposition": stages,
        "canonical_collision_evidence": {
            "v19_action_turn_failure": action_asset,
            "v19_semantic_observability_failure": semantic_asset,
            "uptake_search_closure": {
                "memory_id": uptake_closure["memory_id"],
                "title": uptake_closure["title"],
                "summary": uptake_closure["summary"],
                "reopen_condition": uptake_closure["reopen_condition"],
            },
            "skill_failure_search_closure": {
                "memory_id": skill_failure_closure["memory_id"],
                "title": skill_failure_closure["title"],
                "summary": skill_failure_closure["summary"],
                "reopen_condition": skill_failure_closure["reopen_condition"],
            },
        },
        "closest_work": closest_work,
        "same_information_reduction": same_information_reduction,
        "reopen_condition": reopen,
        "summary": {
            "stages": len(stages),
            "current_scientific_object_survives": 0,
            "problem_gate_eligible": 0,
            "research_item_eligible": 0,
            "debate_eligible": 0,
            "provider_calls_authorized": 0,
            "gpu_authorized": 0,
            "sealed_v19_units_consumed": 0,
        },
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "research_item": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
        },
    }
    payload["collision_sha256"] = _sha({k: v for k, v in payload.items() if k != "generated_at"})
    return payload


def validate_semantic_commit_gap_collision(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = payload.get("policy") or {}
    summary = payload.get("summary") or {}
    if payload.get("status") != "STOP_CURRENT_FORMULATION_MATURE_LIFECYCLE_REDUCTION":
        errors.append("semantic-commit-gap-not-stopped")
    if payload.get("scientific_authority") is not False:
        errors.append("scientific-authority-leak")
    if len(payload.get("four_stage_decomposition") or []) != 4:
        errors.append("four-stage-decomposition-missing")
    if any(row.get("scientific_object") is not False for row in payload.get("four_stage_decomposition") or []):
        errors.append("stage-scientific-object-leak")
    required_policy = (
        "failure_memory_is_search_seed_not_scientific_positive_evidence",
        "support_stop_cannot_be_promoted_to_problem_evidence",
        "lifecycle_stages_must_be_separated_before_naming_a_new_gap",
        "same_information_reduction_precedes_problem_gate",
        "latest_primary_collision_check_required",
        "zero_survivor_is_valid",
        "no_v19_holdout_or_paid_execution_consumed",
    )
    if any(policy.get(key) is not True for key in required_policy):
        errors.append("semantic-commit-gap-policy-incomplete")
    if (payload.get("same_information_reduction") or {}).get("status") != "REDUCED":
        errors.append("same-information-reduction-not-closed")
    if not (payload.get("reopen_condition") or {}).get("required_residual"):
        errors.append("reopen-condition-missing")
    for key in ("current_scientific_object_survives", "problem_gate_eligible", "research_item_eligible", "debate_eligible", "provider_calls_authorized", "gpu_authorized", "sealed_v19_units_consumed"):
        if int(summary.get(key) or 0) != 0:
            errors.append("authority-or-consumption-leak:" + key)
    if len(payload.get("closest_work") or []) < 6:
        errors.append("closest-work-map-too-small")
    return sorted(set(errors))


def write_semantic_commit_gap_collision(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_semantic_commit_gap_collision()
    errors = validate_semantic_commit_gap_collision(payload)
    if errors:
        raise ValueError("invalid semantic commit gap collision: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_semantic_commit_gap_collision(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = _load(path)
    errors = validate_semantic_commit_gap_collision(payload)
    if errors:
        raise ValueError("invalid semantic commit gap collision: " + ";".join(errors))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    payload = write_semantic_commit_gap_collision(args.output)
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "collision_sha256": payload["collision_sha256"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
