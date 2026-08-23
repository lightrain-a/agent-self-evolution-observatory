from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .longitudinal_safety_post_race_triage import load_post_race_triage

SCHEMA_VERSION = "1.0"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "longitudinal-safety-material-child-race-20260824.json"

# These are deterministic scientific-object mutations of the three
# MATERIAL_CHILD_REQUIRED reviewer vectors. They are not candidates with
# ProblemGate authority. Each child is immediately challenged by a stronger
# same-information function-class reduction before any method design.
CHILDREN: tuple[dict[str, Any], ...] = (
    {
        "child_id": "goal-queryable-transition-successor-model",
        "parent_id": "verified-risk-predicate-grammar",
        "title": "Goal-Queryable Transition Successor Model",
        "material_change": (
            "Replace verified predicate/rule induction with a persistent learned successor kernel over "
            "state-action transitions. Safety or reachability specifications are supplied only after the "
            "kernel is frozen, so the stored object is transition semantics rather than a fixed risk rule."
        ),
        "scientific_object": "frozen goal-queryable state-action successor kernel",
        "observable": "independent held-out transition oracle plus post-freeze goal/specification queries",
        "deployment_boundary": "new goal or safety specification arrives after model freezing; no target-spec labels may be used for retraining",
        "strongest_reduction": {
            "name": "same-data generic transition model plus planner",
            "same_information": (
                "identical source transitions, state/action representation, model capacity, uncertainty targets, "
                "post-freeze specification, planning budget, and independent transition truth"
            ),
            "exact_reduction": (
                "Once the learned object is a goal-queryable successor kernel, a generic capacity-matched transition "
                "model trained on the same transitions exposes exactly the same sufficient object to the same planner. "
                "The candidate has escaped verified rule induction only by becoming ordinary model-based dynamics learning."
            ),
            "canonical_boundary": "F-1 Decision-Conditioned World-Model Residual Adapter / ordinary model-based planning",
        },
        "cheapest_falsifier": (
            "Before collecting any agent rollout, give a generic transition learner the identical transition table and "
            "post-freeze specifications. If both systems expose the same successor distribution/set to the same planner, "
            "there is no distinct self-evolution mechanism to test."
        ),
        "decision": "STOP_REDUCTION_EXISTING_WORLD_MODEL_OBJECT",
        "reopen_condition": (
            "Require a persistent transition-derived state that yields a post-freeze decision unavailable to a generic "
            "same-capacity transition model/planner with identical transition data, uncertainty, goal specification, and budget."
        ),
    },
    {
        "child_id": "version-contrastive-repair-transport-operator",
        "parent_id": "version-differential-active-diagnosis",
        "title": "Version-Contrastive Repair Transport Operator",
        "material_change": (
            "Replace learned diagnostic-query ordering with a persistent operator that maps a version delta plus an "
            "intervention-response signature to one executable repair patch for a later unseen version. The deployed "
            "object therefore changes future behavior rather than only diagnosis order."
        ),
        "scientific_object": "frozen version-contrastive repair transport operator",
        "observable": "version delta, matched intervention-response vector, independent post-repair execution truth",
        "deployment_boundary": "zero target-version candidate search; exactly one transported patch may be emitted after the frozen diagnosis transcript",
        "strongest_reduction": {
            "name": "same-input generic conditional patch generator",
            "same_information": (
                "identical version delta, intervention-response signature, historical fault/repair pairs, repair action "
                "space, generator capacity, optimization budget, and zero-search target-version deployment"
            ),
            "exact_reduction": (
                "For a fixed observable input x=(version delta, intervention response, failure context) and executable "
                "patch output y, the proposed transport operator is only one parameterization of the same conditional "
                "mapping learned by an unrestricted capacity-matched patch generator. Calling x 'version contrast' does "
                "not create an identifiable mechanism unless an additional invariant restricts future queries."
            ),
            "canonical_boundary": "E-1/E-2 direct paired edit-effect reuse plus generic conditional repair",
        },
        "cheapest_falsifier": (
            "Compile the proposed operator and a generic conditional generator to their finite observable input/output "
            "relation under the same repair grammar. If the generic generator can represent every emitted patch without "
            "extra target-version information or search, stop before execution."
        ),
        "decision": "STOP_SAME_INFORMATION_CONDITIONAL_GENERATOR",
        "reopen_condition": (
            "Specify a preregistered transport invariant or query family that forces an ex-ante patch/effect prediction "
            "outside the same-information conditional generator's representable relation, then test that invariant on "
            "unseen versions without target-version optimization."
        ),
    },
    {
        "child_id": "interventional-correction-state-machine",
        "parent_id": "counterfactual-correction-production-grammar",
        "title": "Interventional Correction-State Machine",
        "material_change": (
            "Replace independent atomic repairs plus grammar composition with a persistent correction-interaction state "
            "updated by multi-action interventions. The state encodes jointly necessary, antagonistic, and order-sensitive "
            "correction effects and changes the next admissible correction after each executed repair."
        ),
        "scientific_object": "frozen intervention-identified correction interaction state machine",
        "observable": "same-start multi-correction interventions, execution-state transitions, correction history, independent task truth",
        "deployment_boundary": "no new productions or test-time search; the frozen state machine chooses/suppresses the next correction",
        "strongest_reduction": {
            "name": "same-history set/order-aware risk model plus bounded conditional sequence policy",
            "same_information": (
                "identical correction actions, full executed correction history, multi-action intervention outcomes, typed "
                "preconditions/effects, state observations, capacity, and repair budget"
            ),
            "exact_reduction": (
                "On a bounded correction horizon, the state machine's next-action decision is a deterministic/stochastic "
                "function of the same correction history and state. A capacity-matched history-conditioned policy can "
                "compile the same mapping, while A-4 already gives direct set/order-aware interaction risk the same "
                "interventions and equal-budget repair. A named latent correction state therefore adds no identified object."
            ),
            "canonical_boundary": "A-4 typed update interaction / C-5 correction commitment / generic finite-state control",
        },
        "cheapest_falsifier": (
            "Enumerate the bounded correction histories admitted by the frozen action grammar and compile the state "
            "machine's next-action table. Give the same table inputs and intervention labels to an unrestricted bounded "
            "history policy; if it reproduces every action/support decision, stop without agent execution."
        ),
        "decision": "STOP_HISTORY_CONDITIONED_POLICY_REDUCTION",
        "reopen_condition": (
            "Require an independently observed correction-state variable that makes two units with identical full "
            "correction history, typed effects, environment state, action support, and budget demand different next "
            "corrections, or an executable invariant the same-history policy cannot satisfy by construction."
        ),
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def build_material_child_race(*, generated_at: str | None = None) -> dict[str, Any]:
    triage = load_post_race_triage()
    parent_rows = {
        str(row.get("candidate_id") or ""): row
        for row in triage.get("rows") or []
        if row.get("disposition") == "MATERIAL_CHILD_REQUIRED"
    }
    children: list[dict[str, Any]] = []
    for template in CHILDREN:
        parent_id = str(template["parent_id"])
        parent = parent_rows.get(parent_id)
        if parent is None:
            raise ValueError(f"material-child parent unavailable or disposition drifted: {parent_id}")
        row = dict(template)
        row.update(
            {
                "parent_tournament_rank": parent.get("tournament_rank"),
                "parent_reopen_condition": parent.get("reopen_condition"),
                "source_post_race_triage_sha256": triage.get("triage_sha256"),
                "problem_gate_eligible": False,
                "research_item_eligible": False,
                "provider_calls_authorized": 0,
                "gpu_authorized": False,
                "scientific_authority": False,
            }
        )
        children.append(row)

    counts = Counter(row["decision"] for row in children)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "status": "MATERIAL_CHILD_RACE_ZERO_SURVIVOR",
        "source_post_race_triage_sha256": triage.get("triage_sha256"),
        "policy": {
            "only_material_child_required_parents_are_mutated": True,
            "child_must_change_scientific_object": True,
            "same_information_function_class_reduction_precedes_execution": True,
            "generic_baseline_receives_identical_observables_supervision_action_support_and_budget": True,
            "representation_or_naming_difference_is_not_mechanism": True,
            "zero_api_cheapest_falsifier_precedes_debate": True,
            "stopped_child_does_not_create_discovery_lesson_automatically": True,
            "zero_survivors_is_valid": True,
        },
        "summary": {
            "material_parents": len(parent_rows),
            "children_generated": len(children),
            "children_reduced_before_execution": len(children),
            "survivors": 0,
            "debate_eligible": 0,
            "problem_gate_eligible": 0,
            "research_item_eligible": 0,
            "provider_calls_authorized": 0,
            "gpu_authorized": 0,
            "decision_counts": dict(sorted(counts.items())),
        },
        "children": children,
        "next_action": (
            "Do not rename or add modules to these three children. Their requested object changes were attempted and "
            "still reduce under same-information comparators. Return to fresh-source or cross-failure mutation search; "
            "a future child must name a pre-outcome observable, invariant, intervention, or deployment query that forces "
            "a different ex-ante prediction from these generic comparators before debate."
        ),
        "scientific_authority": False,
        "authority": {
            "debate": False,
            "problem_gate": False,
            "research_item": False,
            "method": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
        },
    }
    payload["race_sha256"] = _sha({k: v for k, v in payload.items() if k != "generated_at"})
    return payload


def validate_material_child_race(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    triage = load_post_race_triage()
    summary = payload.get("summary") or {}
    policy = payload.get("policy") or {}
    children = payload.get("children") or []
    expected_parents = {
        str(row.get("candidate_id") or "")
        for row in triage.get("rows") or []
        if row.get("disposition") == "MATERIAL_CHILD_REQUIRED"
    }
    if payload.get("source_post_race_triage_sha256") != triage.get("triage_sha256"):
        errors.append("source-triage-drift")
    if {str(row.get("parent_id") or "") for row in children} != expected_parents:
        errors.append("material-parent-coverage-drift")
    if len(children) != 3 or summary.get("children_generated") != 3:
        errors.append("three-material-children-required")
    if summary.get("survivors") != 0 or summary.get("debate_eligible") != 0:
        errors.append("unexpected-child-survivor")
    if summary.get("problem_gate_eligible") != 0 or summary.get("research_item_eligible") != 0:
        errors.append("illegal-promotion")
    if summary.get("provider_calls_authorized") != 0 or summary.get("gpu_authorized") != 0:
        errors.append("execution-authority-leak")
    required_policy = (
        "child_must_change_scientific_object",
        "same_information_function_class_reduction_precedes_execution",
        "generic_baseline_receives_identical_observables_supervision_action_support_and_budget",
        "representation_or_naming_difference_is_not_mechanism",
        "zero_api_cheapest_falsifier_precedes_debate",
        "zero_survivors_is_valid",
    )
    if any(policy.get(key) is not True for key in required_policy):
        errors.append("material-child-policy-incomplete")
    for row in children:
        cid = str(row.get("child_id") or "missing")
        if not row.get("material_change") or not row.get("scientific_object"):
            errors.append("child-object-change-missing:" + cid)
        reduction = row.get("strongest_reduction") or {}
        if not reduction.get("same_information") or not reduction.get("exact_reduction"):
            errors.append("child-reduction-incomplete:" + cid)
        if not row.get("cheapest_falsifier") or not row.get("reopen_condition"):
            errors.append("child-falsifier-incomplete:" + cid)
        if row.get("problem_gate_eligible") is not False or row.get("research_item_eligible") is not False:
            errors.append("child-promotion:" + cid)
        if row.get("provider_calls_authorized") != 0 or row.get("gpu_authorized") is not False:
            errors.append("child-execution-authority:" + cid)
        if not str(row.get("decision") or "").startswith("STOP_"):
            errors.append("child-not-stopped:" + cid)
    return sorted(set(errors))


def load_material_child_race(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid material-child race JSON:{path}") from exc
    errors = validate_material_child_race(payload)
    if errors:
        raise ValueError("invalid material child race: " + ";".join(errors))
    return payload


def write_material_child_race(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_material_child_race()
    errors = validate_material_child_race(payload)
    if errors:
        raise ValueError("invalid material child race: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = write_material_child_race()
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "race_sha256": payload["race_sha256"]}, ensure_ascii=False, sort_keys=True))
