from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone

from .paper_first_discovery_frontier import build_paper_first_discovery_frontier, validate_paper_first_discovery_frontier


class PaperFirstDiscoveryFrontierTest(unittest.TestCase):
    def states(self) -> dict:
        return {
            "primary_state": {"status":"READY","summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"unreviewed_lane_linked_sources":0,"carrier_probe_pending":0,"carrier_probe_complete":True}},
            "generator_state": {"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","summary":{"generated":0,"written_to_auto_inbox":0}},
            "queue_state": {"summary":{"submitted":0,"audited":0,"passed_problem_gate":0,"paper_design_eligible":0,"inbox_errors":0}},
            "relation_freshness_state": {"status":"CURRENT_RELATION_UNIVERSE","summary":{"universe_stale":False,"current_not_reduced_unknown":False,"focused_problem_generator_reopen_allowed":False}},
            "relation_admission_state": {"status":"HOLD_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":False,"automatic_model_scan_authorized":False}},
            "shadow_admission_state": {"status":"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL","summary":{"same_source_transaction":True,"qualification_allowed":False,"automatic_provider_calls_authorized":0}},
            "object_candidate_state": {"summary":{"activation_authorized":0,"pending_cache":0}},
            "support_release_watch_state": {"summary":{"recheck_required":0,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0}},
            "support_asset_recheck_state": {"summary":{"queued":0,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0}},
            "shadow_portfolio_state": {"latest_run":{"status":"SHADOW_TERMINAL_COMPLETE","summary":{"evidence_design_pending":0,"evidence_execution_ready":0,"evidence_residual_survives":0,"evidence_branch_repair_ready":0}}},
            "evidence_migration_state": {"status":"NOT_RUN","summary":{}},
        }

    def build(self, states: dict | None = None):
        return build_paper_first_discovery_frontier(**(states or self.states()), now=datetime(2026,8,14,tzinfo=timezone.utc))

    def test_all_closed_compiles_wait_external_trigger_frontier(self) -> None:
        state=self.build()
        self.assertEqual(state["status"],"WAIT_EXTERNAL_EVIDENCE_TRIGGERS")
        self.assertEqual(state["summary"]["open_internal_frontiers"],0)
        self.assertEqual(state["summary"]["external_triggers"],5)
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])
        self.assertTrue(state["policy"]["wait_external_status_is_not_scientific_exhaustion"])
        self.assertTrue(state["policy"]["trigger_satisfaction_must_reenter_original_control_plane"])
        self.assertTrue(all(row["scientific_authority"] is False and row["automatic_model_call_authorized"] is False for row in state["triggers"]))

    def test_operator_recompile_zero_candidates_is_closed_live_generator(self) -> None:
        states=self.states();states["generator_state"]={"status":"GENERATED_ZERO_CANDIDATES","summary":{"generated":0,"written_to_auto_inbox":0}}
        state=self.build(states)
        self.assertEqual(state["status"],"WAIT_EXTERNAL_EVIDENCE_TRIGGERS")
        self.assertTrue(state["summary"]["live_generator_closed"])
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_generator_candidate_fully_blocked_by_queue_is_closed_live_review(self) -> None:
        states=self.states();states["generator_state"]={"status":"GENERATED_AWAIT_PROBLEM_GATE","summary":{"generated":1,"written_to_auto_inbox":1}};states["queue_state"]={"summary":{"submitted":1,"audited":1,"passed_problem_gate":0,"blocked_problem_gate":1,"paper_design_eligible":0,"inbox_errors":0}}
        state=self.build(states)
        self.assertTrue(state["summary"]["live_generator_closed"])
        self.assertTrue(state["summary"]["live_queue_closed"])
        self.assertEqual(state["status"],"WAIT_EXTERNAL_EVIDENCE_TRIGGERS")
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_new_live_source_backlog_opens_live_source_frontier_not_model_authority(self) -> None:
        states=self.states();states["primary_state"]["summary"].update({"source_coverage_exhausted":False,"unreviewed_lane_linked_sources":2})
        state=self.build(states)
        self.assertEqual(state["status"],"LIVE_SOURCE_DISCOVERY_PENDING")
        self.assertIn("live-source-frontier-open",state["blockers"])
        self.assertEqual(state["summary"]["automatic_model_calls_authorized"],0)
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_internal_bounded_evidence_work_prevents_false_external_wait(self) -> None:
        states=self.states();states["shadow_portfolio_state"]["latest_run"].update({"status":"SHADOW_EVIDENCE_ACQUISITION_PENDING","summary":{"evidence_design_pending":2,"evidence_execution_ready":1,"evidence_residual_survives":0,"evidence_branch_repair_ready":0}})
        state=self.build(states)
        self.assertEqual(state["status"],"EVIDENCE_ACQUISITION_PENDING")
        self.assertFalse(state["summary"]["evidence_acquisition_closed"])
        self.assertEqual(state["summary"]["evidence_internal_open"],3)
        self.assertIn("bounded-evidence-acquisition-open",state["blockers"])
        self.assertEqual(state["summary"]["automatic_model_calls_authorized"],0)
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_legacy_migration_opens_internal_evidence_without_reopening_shadow_search(self) -> None:
        states=self.states();states["evidence_migration_state"]={"status":"LEGACY_REDUCTION_EVIDENCE_MIGRATION_READY","summary":{"evidence_design_pending":4,"evidence_execution_ready":0,"evidence_residual_survives":0,"evidence_branch_repair_ready":0}}
        state=self.build(states)
        self.assertEqual(state["status"],"EVIDENCE_ACQUISITION_PENDING")
        self.assertEqual(state["summary"]["migration_evidence_internal_open"],4)
        self.assertEqual(state["summary"]["shadow_evidence_internal_open"],0)
        self.assertEqual(state["summary"]["evidence_internal_open"],4)
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_asset_recheck_queue_has_priority_over_shadow_and_relation_waits(self) -> None:
        states=self.states();states["support_asset_recheck_state"]["summary"]["queued"]=1
        state=self.build(states)
        self.assertEqual(state["status"],"SUPPORT_ASSET_RECHECK_PENDING")
        self.assertIn("support-release-or-asset-recheck-open",state["blockers"])
        self.assertEqual(state["summary"]["automatic_problem_gate_authorized"],0)

    def test_shadow_qualification_pending_is_visible_without_provider_authority(self) -> None:
        states=self.states();states["shadow_admission_state"]={"status":"READY_FOR_SHADOW_QUALIFICATION","summary":{"same_source_transaction":False,"qualification_allowed":True,"automatic_provider_calls_authorized":0}}
        state=self.build(states)
        self.assertEqual(state["status"],"SHADOW_QUALIFICATION_PENDING")
        self.assertEqual(state["summary"]["automatic_model_calls_authorized"],0)

    def test_exhausted_relation_lane_review_is_external_wait_not_internal_retry(self) -> None:
        states=self.states();states["relation_freshness_state"]={"status":"STALE_RELATION_UNIVERSE","summary":{"universe_stale":True,"current_not_reduced_unknown":True,"focused_problem_generator_reopen_allowed":False}};states["relation_admission_state"]={"status":"HOLD_RELATION_REVIEW_RETRY_EXHAUSTED","summary":{"manual_scan_eligible":False,"automatic_model_scan_authorized":False,"relation_lane_review_retry_exhausted":True}}
        state=self.build(states)
        self.assertEqual(state["status"],"WAIT_EXTERNAL_RELATION_EXECUTION_CHANGE")
        self.assertEqual(state["summary"]["open_internal_frontiers"],0)
        self.assertFalse(state["summary"]["relation_current_closed"])
        self.assertTrue(state["summary"]["relation_execution_censored"])
        self.assertTrue(state["summary"]["relation_control_closed_for_now"])
        self.assertEqual(state["summary"]["external_triggers"],6)
        self.assertNotIn("relation-frontier-open-or-stale",state["blockers"])
        self.assertTrue(any(row["trigger"]=="RELATION_LANE_REVIEW_EXECUTION_CONTRACT_CHANGE" for row in state["triggers"]))
        self.assertEqual(state["summary"]["automatic_model_calls_authorized"],0)
        self.assertEqual(validate_paper_first_discovery_frontier(state),[])

    def test_stale_relation_is_pending_but_does_not_authorize_scan(self) -> None:
        states=self.states();states["relation_freshness_state"]={"status":"STALE_RELATION_UNIVERSE","summary":{"universe_stale":True,"current_not_reduced_unknown":True,"focused_problem_generator_reopen_allowed":False}};states["relation_admission_state"]={"status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":True,"automatic_model_scan_authorized":False}}
        state=self.build(states)
        self.assertEqual(state["status"],"RELATION_CONTROL_PENDING")
        self.assertEqual(state["summary"]["automatic_model_calls_authorized"],0)

    def test_validator_rejects_authority_and_false_wait_external(self) -> None:
        state=self.build();broken=copy.deepcopy(state);broken["summary"]["automatic_model_calls_authorized"]=1
        self.assertTrue(any("cannot authorize" in row for row in validate_paper_first_discovery_frontier(broken)))
        false_wait=copy.deepcopy(state);false_wait["summary"]["support_release_closed"]=False
        self.assertTrue(any("wait-external" in row for row in validate_paper_first_discovery_frontier(false_wait)))


if __name__=="__main__":unittest.main()
