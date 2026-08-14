from __future__ import annotations

import copy
import unittest

from .paper_first_shadow_continuation_frontier import build_shadow_continuation_frontier, validate_shadow_continuation_frontier


class ShadowContinuationFrontierTest(unittest.TestCase):
    def states(self):
        admission={"status":"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL","summary":{"qualification_allowed":False},"scientific_authority":False}
        watch={"status":"SUPPORT_RELEASE_WATCH_COMPLETE","summary":{"support_holds":4,"recheck_required":0},"scientific_authority":False}
        queue={"status":"SUPPORT_ASSET_RECHECK_QUEUE_EMPTY","summary":{"support_holds":4,"queued":0},"scientific_authority":False}
        handoff={"status":"SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY","summary":{"queued_asset_rechecks":0,"support_inventory_recheck_ready":0,"provenance_incomplete":0},"scientific_authority":False}
        return admission,watch,queue,handoff

    def test_current_zero_action_state_is_explicit_external_wait(self):
        a,w,q,h=self.states();state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        self.assertEqual(validate_shadow_continuation_frontier(state),[])
        self.assertEqual(state["status"],"WAIT_EXTERNAL_PRIMARY_OR_SUPPORT_RELEASE_CHANGE")
        self.assertEqual(state["next_control_action"],"wait-external-change")
        self.assertEqual((state["summary"]["active_control_actions"],state["summary"]["external_wait"]),(0,1))
        self.assertEqual(state["summary"]["automatic_provider_calls_authorized"],0)
        self.assertFalse(state["scientific_authority"])

    def test_new_primary_content_routes_only_to_zero_provider_qualification(self):
        a,w,q,h=self.states();a=copy.deepcopy(a);a["status"]="READY_FOR_SHADOW_QUALIFICATION";a["summary"]["qualification_allowed"]=True
        state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        self.assertEqual(state["status"],"READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION")
        self.assertEqual((state["summary"]["shadow_qualification_ready"],state["summary"]["active_control_actions"]),(1,1))
        self.assertEqual(validate_shadow_continuation_frontier(state),[])

    def test_release_change_waiting_for_queue_compile_precedes_new_shadow_qualification(self):
        a,w,q,h=self.states();a=copy.deepcopy(a);a["status"]="READY_FOR_SHADOW_QUALIFICATION";a["summary"]["qualification_allowed"]=True;w=copy.deepcopy(w);w["summary"]["recheck_required"]=1
        state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        self.assertEqual(state["status"],"READY_FOR_ASSET_RECHECK_QUEUE_COMPILE")
        self.assertEqual(state["next_control_action"],"compile-durable-asset-recheck-queue")

    def test_ready_support_handoff_precedes_shadow_qualification(self):
        a,w,q,h=self.states();a=copy.deepcopy(a);a["status"]="READY_FOR_SHADOW_QUALIFICATION";a["summary"]["qualification_allowed"]=True;q=copy.deepcopy(q);q["summary"]["queued"]=1;h=copy.deepcopy(h);h["summary"].update({"queued_asset_rechecks":1,"support_inventory_recheck_ready":1})
        state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        self.assertEqual(state["status"],"READY_FOR_SUPPORT_INVENTORY_RECHECK")
        self.assertEqual(validate_shadow_continuation_frontier(state),[])

    def test_provenance_hold_blocks_support_handoff(self):
        a,w,q,h=self.states();q=copy.deepcopy(q);q["summary"]["queued"]=1;h=copy.deepcopy(h);h["summary"].update({"queued_asset_rechecks":1,"provenance_incomplete":1})
        state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        self.assertEqual(state["status"],"HOLD_SUPPORT_RECHECK_PROVENANCE")
        self.assertEqual(state["summary"]["active_control_actions"],0)

    def test_frontier_cannot_authorize_any_scientific_or_provider_work(self):
        a,w,q,h=self.states();state=build_shadow_continuation_frontier(admission=a,support_watch=w,asset_queue=q,support_handoff=h)
        broken=copy.deepcopy(state);broken["summary"]["provider_calls_authorized"]=1
        self.assertTrue(any("cannot authorize" in error for error in validate_shadow_continuation_frontier(broken)))


if __name__=="__main__":
    unittest.main()
