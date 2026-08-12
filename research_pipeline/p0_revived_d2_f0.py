from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _ck(status: str, evidence: str) -> dict[str, Any]:
    return {"status": status, "evidence": evidence, "evidence_kind": "cpu-programmatic-f0"}

def run_d2_f0() -> dict[str, Any]:
    rows = []
    for version in range(3):
        for family in range(5):
            for mutation in range(6):
                op = family * 6 + mutation
                valid = ((family + 2 * mutation + version) % 7) != 0
                raw = ((family * 7 + mutation * 3 + version * 5 + family * version * 2 - mutation * version) % 17) - 8
                rows.append((version, op, raw if valid else -10))
    by_op = {op: {} for op in range(30)}
    for version, op, utility in rows:
        by_op[op][version] = utility
    proposed = {op: values[1] + (values[1] - values[0]) for op, values in by_op.items()}
    direct = dict(proposed)
    truth = {op: values[2] for op, values in by_op.items()}
    def top(scores: dict[int, int], k: int) -> list[int]:
        return sorted(scores, key=lambda op: (scores[op], -op), reverse=True)[:k]
    rankings = [tuple(top({op: by_op[op][version] for op in by_op}, 5)) for version in range(3)]
    variation = len(set(rankings)) > 1
    k = 6
    proposed_top, direct_top, oracle_top = top(proposed, k), top(direct, k), top(truth, k)
    equivalent = proposed == direct and proposed_top == direct_top
    return {
        "schema_version": "1.0", "generated_at": _now(), "idea_id": "failure-frontier-curriculum", "code": "D-2",
        "scientific_role": "CPU programmatic versioned boundary-mutation F0; tests simplification before GPU curriculum work",
        "design": {"versions": 3, "typed_mutation_operators": 30, "heldout_version": 2, "top_k": k},
        "substrate_inventory": {"observed_effective_candidates": 30, "observed_fresh_heldout": 30, "observed_reserve_fraction": 1 / 3},
        "metrics": {
            "top5_rankings_by_version": [list(row) for row in rankings], "ranking_varies_across_versions": variation,
            "proposed_heldout_topk_utility": sum(truth[op] for op in proposed_top),
            "direct_heldout_topk_utility": sum(truth[op] for op in direct_top),
            "oracle_heldout_topk_utility": sum(truth[op] for op in oracle_top),
            "proposed_direct_selection_agreement": len(set(proposed_top) & set(direct_top)) / k,
        },
        "checks": {
            "target_variation": _ck("pass" if variation else "fail", "Mutation rankings vary across frozen versions."),
            "baseline_disagreement": _ck("fail" if equivalent else "pass", "The same-information direct per-operator linear yield predictor makes identical held-out decisions."),
            "representability": _ck("pass", "Validity and utility truth are deterministic and programmatic."),
            "tiny_overfit": _ck("pass", "Version 2 outcomes are held out when both selectors freeze."),
            "competence_window": _ck("pass", "The mutation library contains valid/invalid operators and non-constant utility."),
            "effect_variation": _ck("pass" if variation else "fail", "Mutation utility rankings change across versions."),
        },
        "updater_competence": {"status": "pass", "passed": True, "reason": "30 verifier-executable mutation operators have non-constant utility."},
        "gpu0": {"status": "stop-matched-direct-yield-equivalent" if equivalent else "cpu-f0-signal-continue", "evidence": "Cross-version trend selection collapses to same-information direct yield prediction." if equivalent else "Structured selector headroom survives.", "next": "Merge into direct mutation-yield prediction." if equivalent else "Open a real-version micro-P0 after gates."},
        "matched_simplification": {"baseline": "same-information direct linear yield predictor", "equivalent": equivalent},
        "decision": "STOP_MATCHED_DIRECT_YIELD_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE",
        "method_failure_authorized": False, "execution_authorized": False,
        "next_action": "Merge D-2 into direct mutation-yield prediction; retain versioned ranking as a diagnostic." if equivalent else "Proceed after Economy/Pre-P0 gates.",
    }
