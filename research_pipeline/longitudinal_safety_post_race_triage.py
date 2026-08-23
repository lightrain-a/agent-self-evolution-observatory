from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .human_terminal_state import load_independent_methods, load_parents
from .longitudinal_safety_discovery_cycle import load_discovery_cycle
from .paper_first_fresh_saturation import reduction_pattern_audit

SCHEMA_VERSION = "1.0"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "longitudinal-safety-post-race-triage-20260824.json"

# This table is intentionally explicit rather than keyword-driven.  Each row is
# a scientific cross-lineage reduction judgment over a current historical
# failure leaf.  Pattern matching alone is forbidden by the fresh-saturation
# reduction contract and cannot populate this table automatically.
TRIAGE_RULES: dict[str, dict[str, Any]] = {
    "failure-frontier-training-generator": {
        "disposition": "DEFER_TO_EXISTING_OBJECT",
        "reducers": ["failure-frontier-curriculum"],
        "reduction_patterns": [],
        "reason": (
            "The requested revival is already the D-2 scientific carrier: a cross-version, "
            "failure-conditioned mutation policy evaluated by held-out-version training utility "
            "against a same-feature direct mutation-yield predictor. A new frontier generator "
            "would duplicate that object rather than create a new mutation child."
        ),
        "reopen_condition": (
            "Only reopen as a distinct child if a frozen version-contrastive state or operator law "
            "forces a held-out next-version utility prediction that D-2's same-feature direct "
            "mutation-yield predictor and frozen mutation selector cannot express under matched "
            "operators, verifier truth, train tokens, and target-version budget."
        ),
    },
    "verified-risk-predicate-grammar": {
        "disposition": "MATERIAL_CHILD_REQUIRED",
        "reducers": ["irreversible-action-counterfactuals"],
        "reduction_patterns": [],
        "reason": (
            "The current leaf remains verified rule induction. F-2 already compiles counterfactual "
            "failure evidence into persistent precondition/forbidden-action clauses and requires a "
            "same-label capacity-matched direct risk shield. The review vector itself says the next "
            "object must stop being rule induction, so no current scientific object survives yet."
        ),
        "reopen_condition": (
            "Materialize a different learned object with an independent transition oracle that is "
            "never used for generation or acceptance, then give the same oracle labels, state "
            "information, capacity, simulator calls, and runtime checks to F-2/direct-shield controls. "
            "A held-out decision residual must survive before ProblemGate."
        ),
    },
    "version-differential-active-diagnosis": {
        "disposition": "MATERIAL_CHILD_REQUIRED",
        "reducers": [
            "lineage-aware-rollback",
            "active-causal-minimal-rollback",
            "workflow-branch-credit",
        ],
        "reduction_patterns": [],
        "reason": (
            "Learned query ordering is already rejected by the leaf's own review. The proposed escape "
            "is not yet instantiated: a persistent intervention-derived repair/rollback representation. "
            "Its nearest canonical simplifications already cover generic state-diff rollback (A-5), "
            "sparse-fault group-testing rollback (A-6), and intervention-backed failure-motif rewrite "
            "reuse (E-2). Diagnosis alone therefore cannot re-enter as a standalone object."
        ),
        "reopen_condition": (
            "Define and freeze the persistent post-diagnosis repair/rollback representation, then beat "
            "query-seeded ProbDD/PMA plus A-5 state-diff, A-6 group testing, and E-2 paired edit-effect "
            "reuse using identical historical faults, intervention budget, observable state, and repair "
            "action support. The residual must be in the representation's executable future behavior, "
            "not query order or diagnostic accuracy."
        ),
    },
    "counterfactual-correction-production-grammar": {
        "disposition": "MATERIAL_CHILD_REQUIRED",
        "reducers": ["compositional-update-compatibility", "intervention-validated-self-correction"],
        "reduction_patterns": [],
        "reason": (
            "The review already rejects marginal repair identification plus symbolic composition. Its "
            "suggested escape is causal interaction among corrections. Canonical A-4 already tests "
            "typed pair/order interaction rules against same-information order-aware risk plus "
            "equal-budget constrained repair, while C-5 already treats intervention-certified correction "
            "commitment as a separate persistent object. No correction-specific interaction variable has "
            "yet been defined that escapes those controls."
        ),
        "reopen_condition": (
            "Materialize a preregistered multi-correction interaction state (joint necessity, antagonism, "
            "or order dependence) with independent intervention truth, and require a held-out prediction "
            "or repair that survives A-4's same-information order-aware risk plus equal-budget repair as "
            "well as CausalFlow-derived repairs composed by NSI/SkillGraph under the same intervention budget."
        ),
    },
    "operator-heldout-marginal-gain-transport": {
        "disposition": "DEFER_TO_EXISTING_OBJECT",
        "reducers": ["failure-frontier-curriculum"],
        "reduction_patterns": [],
        "reason": (
            "The requested operator-level held-out version transport is already within D-2's frozen "
            "cross-version mutation-selector object and its same-feature direct mutation-yield baseline. "
            "Renaming the response target as marginal-gain transport does not create a separate carrier."
        ),
        "reopen_condition": (
            "Require an identifiable operator transformation or counterfactual invariant that makes a "
            "different held-out-version next-training-utility prediction from D-2's direct mutation-yield "
            "model when both receive identical operator descriptors, source-version outcomes, verifier "
            "truth, task family, and train-token budget."
        ),
    },
    "skill-interface-contract-compiler": {
        "disposition": "STOP_MATURE_REDUCTION",
        "reducers": ["compositional-update-compatibility"],
        "reduction_patterns": [],
        "reason": (
            "A probabilistic relational contract over cross-skill side effects is a typed update-interaction "
            "model. A-4 already gives the direct set/order-aware risk model identical interaction evidence "
            "and equal-budget repair search, and its CPU P0 found exact prediction/repair equivalence. "
            "Interface typing or contract serialization therefore cannot be the standalone mechanism."
        ),
        "reopen_condition": (
            "Only reopen with an independently observable latent side-effect state whose held-out "
            "composition prediction differs from a capacity-matched direct set/order-aware risk model "
            "given the same skill interfaces, interaction interventions, uncertainty targets, update "
            "identities, and repair budget."
        ),
    },
    "budget-split-contract-router-transpiler": {
        "disposition": "STOP_MATURE_REDUCTION",
        "reducers": ["budgeted-evolution-controller"],
        "reduction_patterns": ["operator-closure-reachability"],
        "reason": (
            "The review's proposed escape claims that a single budget-conditioned policy changes the set "
            "of repairs reachable under M while the strongest comparator receives the same diagnostics, "
            "contract, action space, calls, and supervision. With the same transition/action graph, a policy "
            "can change visitation or selection but not operator support/reachability. Canonical fresh "
            "saturation already records operator-closure reachability as a hard mature reduction, and A-2 "
            "shows the matched-budget adaptive-control comparison required after support is fixed."
        ),
        "reopen_condition": (
            "Reopen only if a frozen contract policy introduces a formally specified transition/operator "
            "constraint that changes reachable support without giving the candidate a larger action space, "
            "or forces a different finite-budget repair decision from a capacity-matched generic policy "
            "with identical diagnostics, action graph, calls, supervision, stopping authority, and generator."
        ),
    },
    "sparse-set-effect-update-collector": {
        "disposition": "STOP_MATURE_REDUCTION",
        "reducers": ["compositional-update-compatibility"],
        "reduction_patterns": [],
        "reason": (
            "The leaf's own review reduces sparse set effects to ordinary low-order interaction regression. "
            "A-4 is the same canonical interaction-control problem and has already tied a typed registry with "
            "a direct order-aware risk table plus equal-budget repair on unseen identities/triples. A new "
            "hypergraph/set-effect storage form is therefore not a surviving mechanism."
        ),
        "reopen_condition": (
            "Require a transferable update-semantic interaction law that makes an ex-ante held-out prediction "
            "unavailable to descriptor-conditioned quadratic/cubic sparse regressors and A-4 direct "
            "set/order-aware risk, all trained on the same interventions and given the same repair optimizer."
        ),
    },
    "randomized-memory-action-policy": {
        "disposition": "DEFER_TO_EXISTING_OBJECT",
        "reducers": ["retrieval-interference-auditor"],
        "reduction_patterns": [],
        "reason": (
            "The review asks for exactly the memory-specific carrier already represented by B-3: "
            "retrieval-mediated delayed effects and interference among memory entries, identified by "
            "nested retrieval/content/rank/co-retrieval interventions and followed by persistent repair. "
            "B-3 is currently support-censored rather than scientifically failed, so a renamed randomized "
            "memory-action policy would duplicate an unresolved canonical object."
        ),
        "reopen_condition": (
            "Resume through B-3 when fresh interaction support satisfies its frozen substrate gate. A "
            "separate child is allowed only if it names a different estimand and produces a same-log "
            "decision residual beyond B-3 pathway controls and a standard doubly robust contextual-bandit "
            "learner given identical randomized logs, memory actions, delayed outcomes, and support constraints."
        ),
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def build_post_race_triage(*, generated_at: str | None = None) -> dict[str, Any]:
    cycle = load_discovery_cycle()
    race = (cycle.get("historical_pool_audit") or {}).get("horse_race") or {}
    ranked = [dict(row) for row in race.get("top_mutation_parents") or []]
    ranked_ids = [str(row.get("candidate_id") or "") for row in ranked]

    terminal = {**load_parents(), **load_independent_methods()}
    reduction_patterns = {row["key"]: row for row in reduction_pattern_audit()}
    rows: list[dict[str, Any]] = []
    for rank_row in ranked:
        candidate_id = str(rank_row.get("candidate_id") or "")
        rule = TRIAGE_RULES.get(candidate_id)
        if rule is None:
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "tournament_rank": rank_row.get("tournament_rank"),
                    "disposition": "UNTRIAGED_FAIL_CLOSED",
                    "problem_gate_eligible": False,
                    "scientific_authority": False,
                }
            )
            continue

        reducer_rows = []
        for reducer_id in rule["reducers"]:
            reducer = terminal[reducer_id]
            reducer_rows.append(
                {
                    "idea_id": reducer_id,
                    "code": reducer.get("code"),
                    "terminal_state": reducer.get("terminal_state"),
                    "strongest_baseline": reducer.get("strongest_baseline"),
                    "exact_stop": reducer.get("exact_stop"),
                    "current_fact": reducer.get("current_fact"),
                }
            )
        pattern_rows = []
        for key in rule["reduction_patterns"]:
            pattern = reduction_patterns[key]
            pattern_rows.append(
                {
                    "key": key,
                    "audit_class": pattern.get("audit_class"),
                    "mature_theories": pattern.get("mature_theories"),
                    "veto": pattern.get("veto"),
                    "automatic_veto": pattern.get("automatic_veto"),
                }
            )

        rows.append(
            {
                "candidate_id": candidate_id,
                "title": rank_row.get("title"),
                "tournament_rank": rank_row.get("tournament_rank"),
                "source_round": rank_row.get("round"),
                "source_verdict": rank_row.get("external_verdict"),
                "source_required_action": rank_row.get("required_action"),
                "lineage_closure_status": rank_row.get("lineage_closure_status"),
                "disposition": rule["disposition"],
                "reason": rule["reason"],
                "canonical_reducers": reducer_rows,
                "mature_reduction_patterns": pattern_rows,
                "reopen_condition": rule["reopen_condition"],
                "problem_gate_eligible": False,
                "research_item_eligible": False,
                "provider_calls_authorized": 0,
                "gpu_authorized": False,
                "scientific_authority": False,
            }
        )

    counts = Counter(row["disposition"] for row in rows)
    current_survivors = [
        row["candidate_id"]
        for row in rows
        if row["disposition"] == "SURVIVES_POST_RACE_REDUCTION"
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "status": "POST_RACE_REDUCTION_TRIAGE_COMPLETE",
        "source_cycle_sha256": cycle.get("cycle_sha256"),
        "policy": {
            "tournament_rank_is_attention_priority_not_scientific_qualification": True,
            "descendant_closure_precedes_cross_lineage_reduction": True,
            "cross_lineage_same_information_reduction_precedes_child_generation": True,
            "manual_scientific_mapping_required": True,
            "keyword_or_pattern_match_alone_cannot_stop_candidate": True,
            "mature_reduction_pattern_requires_concrete_candidate_level_argument": True,
            "existing_support_hold_cannot_be_relabelled_as_method_failure": True,
            "material_child_must_be_a_new_scientific_object_not_a_rename": True,
            "zero_survivors_is_valid": True,
        },
        "summary": {
            "ranked_failure_leaves": len(ranked),
            "triaged": len(rows),
            "disposition_counts": dict(sorted(counts.items())),
            "current_post_race_survivors": len(current_survivors),
            "material_child_required": counts["MATERIAL_CHILD_REQUIRED"],
            "deferred_to_existing_object": counts["DEFER_TO_EXISTING_OBJECT"],
            "stopped_by_mature_reduction": counts["STOP_MATURE_REDUCTION"],
            "untriaged_fail_closed": counts["UNTRIAGED_FAIL_CLOSED"],
            "problem_gate_eligible": 0,
            "research_item_eligible": 0,
            "provider_calls_authorized": 0,
            "gpu_authorized": 0,
        },
        "current_post_race_survivors": current_survivors,
        "rows": rows,
        "next_action": (
            "Do not resurrect any of the nine ranked historical leaves as a current ResearchItem. "
            "Use the three MATERIAL_CHILD_REQUIRED reviewer vectors only as mutation prompts; any child "
            "must change the scientific object and pass its listed same-information reductions before "
            "debate or ProblemGate. Resume DEFER rows only through their existing canonical object."
        ),
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "research_item": False,
            "method": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
        },
    }
    payload["triage_sha256"] = _sha({k: v for k, v in payload.items() if k != "generated_at"})
    return payload


def validate_post_race_triage(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = payload.get("policy") or {}
    summary = payload.get("summary") or {}
    rows = payload.get("rows") or []
    cycle = load_discovery_cycle()
    if payload.get("scientific_authority") is not False:
        errors.append("scientific-authority-leak")
    if payload.get("source_cycle_sha256") != cycle.get("cycle_sha256"):
        errors.append("source-cycle-drift")
    if len(rows) != 9 or summary.get("ranked_failure_leaves") != 9:
        errors.append("top-nine-not-fully-triaged")
    if set(row.get("candidate_id") for row in rows) != set(TRIAGE_RULES):
        errors.append("triage-candidate-set-drift")
    if summary.get("current_post_race_survivors") != 0:
        errors.append("unexpected-post-race-survivor")
    if summary.get("problem_gate_eligible") != 0 or summary.get("research_item_eligible") != 0:
        errors.append("illegal-promotion")
    if summary.get("provider_calls_authorized") != 0 or summary.get("gpu_authorized") != 0:
        errors.append("execution-authority-leak")
    required_policy = (
        "tournament_rank_is_attention_priority_not_scientific_qualification",
        "cross_lineage_same_information_reduction_precedes_child_generation",
        "keyword_or_pattern_match_alone_cannot_stop_candidate",
        "existing_support_hold_cannot_be_relabelled_as_method_failure",
        "material_child_must_be_a_new_scientific_object_not_a_rename",
        "zero_survivors_is_valid",
    )
    if any(policy.get(key) is not True for key in required_policy):
        errors.append("post-race-policy-incomplete")
    for row in rows:
        if row.get("problem_gate_eligible") is not False or row.get("research_item_eligible") is not False:
            errors.append("row-promotion:" + str(row.get("candidate_id")))
        if row.get("provider_calls_authorized") != 0 or row.get("gpu_authorized") is not False:
            errors.append("row-execution-authority:" + str(row.get("candidate_id")))
        if not row.get("reason") or not row.get("reopen_condition"):
            errors.append("row-reduction-incomplete:" + str(row.get("candidate_id")))
        for pattern in row.get("mature_reduction_patterns") or []:
            if pattern.get("automatic_veto") is not False:
                errors.append("automatic-pattern-veto:" + str(row.get("candidate_id")))
    return sorted(set(errors))


def load_post_race_triage(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid post-race triage JSON:{path}") from exc
    errors = validate_post_race_triage(payload)
    if errors:
        raise ValueError("invalid post-race triage: " + ";".join(errors))
    return payload


def write_post_race_triage(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_post_race_triage()
    errors = validate_post_race_triage(payload)
    if errors:
        raise ValueError("invalid post-race triage: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    payload = write_post_race_triage(args.output)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "summary": payload["summary"],
                "triage_sha256": payload["triage_sha256"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
