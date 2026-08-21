from __future__ import annotations

import unittest

from .candidate_attention_tournament import (
    DIMENSIONS,
    compile_review_batch,
    finalize_attention_tournament,
    prepare_attention_tournament,
    reallocate_unstarted_evidence_plan,
)


def machine(n: int = 6) -> dict:
    rows=[]
    for i in range(n):
        rows.append({
            "candidate_id":f"C{i+1}",
            "title":f"Candidate {i+1}",
            "discovery_lane":"TEST",
            "blockers":["unresolved-exact-reduction-test:1"],
            "irreducible_object":f"persistent agent object {i+1}",
            "endpoint_headroom_requirement":"nondegenerate endpoint",
            "exact_prediction":f"prediction {i+1}",
            "strongest_same_information_baseline":f"baseline {i+1}",
            "cheapest_problem_falsifier":f"bounded falsifier {i+1}",
            "scientific_authority":False,
        })
    return {"problem_falsifier_queue":rows,"scientific_authority":False}


def review_for(plan: dict, label: str, flip: bool = False) -> dict:
    pair_ids=[p["pair_id"] for p in plan["pair_schedule"]]
    reviews=[]
    for i,pid in enumerate(pair_ids):
        winner="B" if flip and i % 2 == 0 else "A"
        reviews.append({
            "pair_id":pid,
            "dimension_winners":{d:winner for d in DIMENSIONS},
            "attention_winner":winner,
            "confidence":"MEDIUM",
            "reason":"attention ordering only",
        })
    return compile_review_batch(plan,{"reviews":reviews},reviewer_label=label,resolved_model=label,pair_ids=pair_ids)


class CandidateAttentionTournamentTest(unittest.TestCase):
    def test_prepare_freezes_balanced_pair_schedule_and_zero_authority(self) -> None:
        plan=prepare_attention_tournament(machine(6),comparisons_per_candidate=3,proximity_threshold=0.99)
        self.assertEqual(plan["status"],"ATTENTION_TOURNAMENT_PREPARED")
        self.assertEqual(len(plan["pair_schedule"]),9)
        self.assertEqual(set(plan["pair_degree"].values()),{3})
        self.assertEqual(len({p["pair_id"] for p in plan["pair_schedule"]}),9)
        self.assertFalse(plan["scientific_authority"])
        self.assertFalse(plan["authority"]["candidate_elimination"])

    def test_proximity_groups_similar_candidates_without_elimination(self) -> None:
        m=machine(4)
        m["problem_falsifier_queue"][1].update({
            "title":m["problem_falsifier_queue"][0]["title"],
            "irreducible_object":m["problem_falsifier_queue"][0]["irreducible_object"],
            "exact_prediction":m["problem_falsifier_queue"][0]["exact_prediction"],
            "strongest_same_information_baseline":m["problem_falsifier_queue"][0]["strongest_same_information_baseline"],
            "cheapest_problem_falsifier":m["problem_falsifier_queue"][0]["cheapest_problem_falsifier"],
        })
        plan=prepare_attention_tournament(m,comparisons_per_candidate=2,proximity_threshold=0.8)
        self.assertEqual(plan["proximity_family_by_candidate"]["C1"],plan["proximity_family_by_candidate"]["C2"])
        self.assertEqual(plan["candidate_count"],4)
        self.assertTrue(plan["policy"]["automatic_candidate_elimination_forbidden"])

    def test_finalize_requires_two_complete_reviewers_and_outputs_attention_only(self) -> None:
        plan=prepare_attention_tournament(machine(6),comparisons_per_candidate=2,proximity_threshold=0.99)
        a=review_for(plan,"reviewer-a")
        with self.assertRaisesRegex(ValueError,"at least two"):
            finalize_attention_tournament(plan,[a])
        b=review_for(plan,"reviewer-b",flip=True)
        out=finalize_attention_tournament(plan,[a,b],active_slots=3)
        self.assertEqual(out["status"],"ATTENTION_TOURNAMENT_COMPLETE")
        self.assertEqual(len(out["ranking"]),6)
        self.assertEqual(len(out["recommended_active_attention"]),3)
        self.assertFalse(out["scientific_authority"])
        self.assertTrue(out["policy"]["ranking_controls_attention_order_only"])

    def test_reallocation_only_allowed_before_any_evidence_work(self) -> None:
        plan=prepare_attention_tournament(machine(6),comparisons_per_candidate=2,proximity_threshold=0.99)
        result=finalize_attention_tournament(plan,[review_for(plan,"a"),review_for(plan,"b",True)],active_slots=2)
        evidence={"entries":[{"candidate_id":f"C{i+1}","status":"NEEDS_BOUNDED_EVIDENCE_DESIGN" if i<4 else "DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":i<4,"execution_authorized":False} for i in range(6)],"portfolio":{"selection":"bounded-top-k"},"scientific_authority":False}
        out=reallocate_unstarted_evidence_plan(evidence,result,active_slots=2)
        self.assertEqual(sum(e["design_selected"] for e in out["entries"]),2)
        self.assertTrue(all(e["selection_basis"]=="PAIRWISE_ATTENTION_TOURNAMENT_ZERO_AUTHORITY" for e in out["entries"]))
        progressed={**evidence,"entries":[dict(evidence["entries"][0],status="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT"),*evidence["entries"][1:]]}
        with self.assertRaisesRegex(ValueError,"forbidden after evidence"):
            reallocate_unstarted_evidence_plan(progressed,result,active_slots=2)


if __name__ == "__main__": unittest.main()
