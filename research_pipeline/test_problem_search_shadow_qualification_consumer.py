from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .paper_first_shadow_continuation_frontier import build_shadow_continuation_frontier
from .paper_first_shadow_search_admission import DISCOVERY_OPERATOR_VERSION, build_shadow_search_admission, primary_content_sha256, source_set_sha256
from .problem_search_shadow_qualification_consumer import consume_shadow_qualification_handoff


class ShadowQualificationConsumerTest(unittest.TestCase):
    def control_states(self, *, same_source: bool):
        records=[
            {"ref":"arXiv:2608.00001","source_sha256":"1"*64,"fulltext_sha256":"3"*64},
            {"ref":"arXiv:2608.00002","source_sha256":"2"*64,"fulltext_sha256":"4"*64},
        ]
        tx="a"*64;generated_at="2026-08-14T00:00:00+00:00"
        primary={"status":"READY","generated_at":generated_at,"discovery_transaction_id":tx,"records":records,"summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"carrier_probe_complete":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","discovery_transaction_id":tx,"summary":{"generated":0,"written_to_auto_inbox":0}}
        queue={"discovery_transaction_id":tx,"summary":{"submitted":0,"audited":0,"inbox_errors":0}}
        latest_records=json.loads(json.dumps(records))
        if not same_source:
            latest_records[0]["fulltext_sha256"]="9"*64
        shadow={"latest_run_id":"shadow-old","latest_run":{"run_id":"shadow-old","status":"SHADOW_TERMINAL_COMPLETE","discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"source_generated_at":"2026-08-13T00:00:00+00:00","source_set_sha256":source_set_sha256(latest_records),"source_primary_content_sha256":primary_content_sha256(latest_records),"source_pool_sha256":"b"*64,"scientific_authority":False},"scientific_authority":False,"policy":{"shadow_only":True}}
        admission=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        watch={"status":"SUPPORT_RELEASE_WATCH_COMPLETE","summary":{"support_holds":0,"recheck_required":0},"scientific_authority":False}
        asset={"status":"SUPPORT_ASSET_RECHECK_QUEUE_EMPTY","summary":{"support_holds":0,"queued":0},"scientific_authority":False}
        handoff={"status":"SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY","summary":{"queued_asset_rechecks":0,"support_inventory_recheck_ready":0,"provenance_incomplete":0},"scientific_authority":False}
        frontier=build_shadow_continuation_frontier(admission=admission,support_watch=watch,asset_queue=asset,support_handoff=handoff)
        return admission,frontier

    def write_state(self, path: Path, *, same_source: bool):
        admission,frontier=self.control_states(same_source=same_source)
        path.write_text(json.dumps({"paper_first_shadow_search_admission":admission,"paper_first_shadow_continuation_frontier":frontier}),encoding="utf-8")
        return admission,frontier

    def test_wait_frontier_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);state_path=root/"state.json";_,frontier=self.write_state(state_path,same_source=True);calls=[]
            self.assertTrue(str(frontier["status"]).startswith("WAIT_EXTERNAL_"))
            result=consume_shadow_qualification_handoff(public_state_path=state_path,source_repo=root,canonical_private_pool=root/"missing.json",worktree_parent=root/"worktrees",create_worktree=lambda *args:calls.append(args))
        self.assertEqual(result["status"],"SKIPPED_SHADOW_QUALIFICATION_FRONTIER_NOT_READY")
        self.assertEqual(calls,[])
        self.assertEqual(result["summary"]["model_calls_executed"],0)
        self.assertEqual(result["summary"]["expansion_started"],0)

    def test_ready_frontier_prepares_one_pinned_zero_provider_qualification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);state_path=root/"state.json";admission,frontier=self.write_state(state_path,same_source=False);pool=root/"primary.json";pool.write_text("{}",encoding="utf-8");parent=root/"worktrees";created=[]
            self.assertEqual(frontier["status"],"READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION")
            source=admission["source_identity"]
            def create(repo,target,commit):
                created.append((repo,target,commit));target.mkdir(parents=True);(target/"generated").mkdir();(target/"generated"/"paper-first-search-portfolio-design-adjudication.json").write_text("{}",encoding="utf-8")
            def qualify(**kwargs):
                self.assertEqual(kwargs["admission_state"],admission)
                run=kwargs["run_root"];run.mkdir(parents=True)
                receipt={"status":"READY_FOR_SHADOW_EXPANSION","scientific_authority":False,"main_commit":"c"*40,"stage_runner_required_schema":"1.4","control_snapshot_sha256":"d"*64,"source_set_sha256":source["current_source_set_sha256"],"source_primary_content_sha256":source["current_primary_content_sha256"],"frozen_pool_sha256":"e"*64,"memory_sha256":"f"*64}
                (run/"shadow-run-qualification.json").write_text(json.dumps(receipt),encoding="utf-8")
                return {"status":"READY_FOR_SHADOW_EXPANSION_ZERO_PROVIDER_HANDOFF","summary":{"model_calls_executed":0}}
            with patch("research_pipeline.problem_search_shadow_qualification_consumer._git_head",return_value="c"*40):
                result=consume_shadow_qualification_handoff(public_state_path=state_path,source_repo=root,canonical_private_pool=pool,worktree_parent=parent,create_worktree=create,qualifier=qualify)
        self.assertEqual(result["status"],"SHADOW_QUALIFICATION_PREPARED_ZERO_PROVIDER")
        self.assertEqual(len(created),1)
        self.assertEqual(result["summary"]["qualification_prepared"],1)
        self.assertEqual(result["summary"]["model_calls_executed"],0)
        self.assertEqual(result["summary"]["expansion_started"],0)
        self.assertEqual(result["provenance"]["stage_runner_required_schema"],"1.4")
        self.assertFalse(result["scientific_authority"])

    def test_existing_matching_qualification_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);state_path=root/"state.json";admission,_=self.write_state(state_path,same_source=False);pool=root/"primary.json";pool.write_text("{}",encoding="utf-8");parent=root/"worktrees";source=admission["source_identity"]
            import hashlib
            request=hashlib.sha256(f"{source['current_source_set_sha256']}\n{source['current_primary_content_sha256']}".encode()).hexdigest()[:16]
            worktree=parent/f"agent-self-evolution-shadow-qual-{request}";run=worktree/"generated"/"research-data"/"paper-first-problem-discovery"/"search-portfolios"/f"shadow-auto-{request}";run.mkdir(parents=True)
            receipt={"status":"READY_FOR_SHADOW_EXPANSION","scientific_authority":False,"main_commit":"c"*40,"stage_runner_required_schema":"1.4","control_snapshot_sha256":"d"*64,"source_set_sha256":source["current_source_set_sha256"],"source_primary_content_sha256":source["current_primary_content_sha256"],"frozen_pool_sha256":"e"*64,"memory_sha256":"f"*64}
            (run/"shadow-run-qualification.json").write_text(json.dumps(receipt),encoding="utf-8")
            with patch("research_pipeline.problem_search_shadow_qualification_consumer._git_head",return_value="9"*40):
                result=consume_shadow_qualification_handoff(public_state_path=state_path,source_repo=root,canonical_private_pool=pool,worktree_parent=parent,create_worktree=lambda *args:self.fail("must not recreate worktree"),qualifier=lambda **kwargs:self.fail("must not requalify"))
        self.assertEqual(result["status"],"SHADOW_QUALIFICATION_ALREADY_PREPARED")
        self.assertEqual(result["summary"]["worktree_created"],0)
        self.assertEqual(result["summary"]["model_calls_executed"],0)
        self.assertEqual(result["provenance"]["qualified_commit"],"c"*40)

    def test_partial_existing_worktree_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);state_path=root/"state.json";admission,_=self.write_state(state_path,same_source=False);pool=root/"primary.json";pool.write_text("{}",encoding="utf-8");parent=root/"worktrees";source=admission["source_identity"]
            import hashlib
            request=hashlib.sha256(f"{source['current_source_set_sha256']}\n{source['current_primary_content_sha256']}".encode()).hexdigest()[:16]
            (parent/f"agent-self-evolution-shadow-qual-{request}").mkdir(parents=True)
            with patch("research_pipeline.problem_search_shadow_qualification_consumer._git_head",return_value="c"*40):
                result=consume_shadow_qualification_handoff(public_state_path=state_path,source_repo=root,canonical_private_pool=pool,worktree_parent=parent,create_worktree=lambda *args:self.fail("must not overwrite partial state"))
        self.assertEqual(result["status"],"HOLD_EXISTING_SHADOW_QUALIFICATION_WORKTREE_INVALID")
        self.assertEqual(result["summary"]["model_calls_executed"],0)


if __name__=="__main__":
    unittest.main()
