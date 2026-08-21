from __future__ import annotations

import unittest

from .candidate_actionability_overlay import compile_actionability_overlay, reschedule_freshly_promoted_deferred


class CandidateActionabilityOverlayTest(unittest.TestCase):
    def fixture(self):
        tournament={
            "scientific_authority":False,
            "tournament_result_sha256":"a"*64,
            "ranking":[
                {"candidate_id":"C1","attention_rank":1,"attention_score":1.0,"dimension_scores":{},"proximity_family":"F1"},
                {"candidate_id":"C2","attention_rank":2,"attention_score":0.8,"dimension_scores":{},"proximity_family":"F2"},
                {"candidate_id":"C3","attention_rank":3,"attention_score":0.7,"dimension_scores":{},"proximity_family":"F3"},
            ],
        }
        evidence={"entries":[
            {"candidate_id":"C1","status":"READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT"},
            {"candidate_id":"C2","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"},
            {"candidate_id":"C3","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET"},
        ]}
        return tournament,evidence

    def test_budget_hold_does_not_change_scientific_rank_but_removes_execute_slot(self):
        tournament,evidence=self.fixture()
        out=compile_actionability_overlay(
            tournament,evidence,
            substrate_receipts=[{"candidate_id":"C1","disposition":"BUDGET_INFEASIBLE","reason":"fixed budget contradiction"}],
            next_slots=2,
        )
        row=next(x for x in out["rows"] if x["candidate_id"]=="C1")
        self.assertEqual(row["scientific_attention_rank"],1)
        self.assertEqual(row["action_lane"],"HOLD_BUDGET")
        self.assertFalse(row["scientific_rank_changed_by_overlay"])
        self.assertEqual(out["recommended_next_attention"],["C2","C3"])
        self.assertFalse(out["scientific_authority"])

    def test_runtime_revocation_overrides_stale_ready_status_without_authority(self):
        tournament,evidence=self.fixture()
        out=compile_actionability_overlay(
            tournament,evidence,
            runtime_revocations=[{"candidate_id":"C1","status":"EXECUTION_AUTHORIZATION_REVOKED_ZERO_AUTHORITY","execution_authorized":False,"reason":"runtime invalid"}],
            next_slots=1,
        )
        row=next(x for x in out["rows"] if x["candidate_id"]=="C1")
        self.assertEqual(row["effective_operational_status"],"HOLD_HARNESS_RUNTIME_SUPPORT")
        self.assertEqual(row["action_lane"],"HOLD_RUNTIME_SUPPORT")
        self.assertEqual(out["recommended_next_attention"],["C2"])

    def test_minimal_harness_implementation_is_actionable_before_new_design(self):
        tournament,evidence=self.fixture()
        evidence["entries"][0]["status"]="NEEDS_MINIMAL_HARNESS_IMPLEMENTATION"
        evidence["entries"][1]["status"]="NEEDS_BOUNDED_EVIDENCE_DESIGN"
        out=compile_actionability_overlay(tournament,evidence,next_slots=2)
        row=next(x for x in out["rows"] if x["candidate_id"]=="C1")
        self.assertEqual(row["action_lane"],"CONTINUE_HARNESS_IMPLEMENTATION")
        self.assertEqual(out["recommended_next_attention"][:2],["C1","C2"])

    def test_candidate_sets_must_match(self):
        tournament,evidence=self.fixture()
        evidence["entries"].pop()
        with self.assertRaisesRegex(ValueError,"candidate sets differ"):
            compile_actionability_overlay(tournament,evidence)

    def test_fresh_slot_scheduler_only_reorders_never_started_promotions(self):
        original={"entries":[
            {"candidate_id":"C1","status":"READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT","design_selected":True},
            {"candidate_id":"C2","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":False},
            {"candidate_id":"C3","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":False},
            {"candidate_id":"C4","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":False},
        ],"portfolio":{"max_active_candidates":2},"scientific_authority":False,"policy":{}}
        updated={"entries":[
            {"candidate_id":"C1","status":"HOLD_SUBSTRATE_BUDGET_INFEASIBLE","design_selected":True},
            {"candidate_id":"C2","status":"NEEDS_BOUNDED_EVIDENCE_DESIGN","design_selected":True},
            {"candidate_id":"C3","status":"NEEDS_BOUNDED_EVIDENCE_DESIGN","design_selected":True},
            {"candidate_id":"C4","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":False},
        ],"portfolio":{"max_active_candidates":2},"scientific_authority":False,"policy":{}}
        overlay={"overlay_sha256":"f"*64,"recommended_next_attention":["C4","C3"],"rows":[
            {"candidate_id":"C4","scientific_attention_rank":1},
            {"candidate_id":"C3","scientific_attention_rank":2},
            {"candidate_id":"C2","scientific_attention_rank":3},
            {"candidate_id":"C1","scientific_attention_rank":4},
        ]}
        out=reschedule_freshly_promoted_deferred(original,updated,overlay,max_active=2)
        selected=[row["candidate_id"] for row in out["entries"] if row.get("status")=="NEEDS_BOUNDED_EVIDENCE_DESIGN"]
        self.assertEqual(set(selected),{"C4","C3"})
        self.assertEqual(next(row for row in out["entries"] if row["candidate_id"]=="C2")["status"],"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET")
        self.assertEqual(out["portfolio"]["newly_selected_candidates"],["C4","C3"])

    def test_fresh_slot_scheduler_refuses_progressed_deferred_candidate(self):
        original={"entries":[{"candidate_id":"C1","status":"DEFERRED_BY_ACTIVE_PORTFOLIO_BUDGET","design_selected":False}],"scientific_authority":False,"policy":{}}
        updated={"entries":[{"candidate_id":"C1","status":"NEEDS_BOUNDED_EVIDENCE_DESIGN","design_selected":True,"design":{"x":1}}],"scientific_authority":False,"policy":{}}
        overlay={"overlay_sha256":"f"*64,"recommended_next_attention":["C1"],"rows":[{"candidate_id":"C1","scientific_attention_rank":1}]}
        with self.assertRaisesRegex(ValueError,"cannot touch progressed"):
            reschedule_freshly_promoted_deferred(original,updated,overlay,max_active=1)


if __name__=="__main__":unittest.main()
