from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_global_relation_recall import _card, run_global_relation_recall


class GlobalRelationRecallTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root,
            corpus_dir=root / "corpora",
            dataset_dir=root / "datasets",
            paper_dir=root / "papers",
            index_dir=root / "indexes",
            run_dir=root / "runs",
            cache_dir=root / "cache",
            lock_dir=root / "locks",
            site_artifact_dir=root / "site",
        )

    def primary(self) -> dict:
        return {"status":"READY","summary":{"source_coverage_exhausted":True}}

    def generator(self) -> dict:
        return {
            "status":"GENERATED_AWAIT_PROBLEM_GATE",
            "saturation_memory":{"portable_review_receipts":[
                {"run_id":"r1","source_refs":["arXiv:1","arXiv:2"],"scientific_authority":False},
                {"run_id":"r2","source_refs":["arXiv:3","arXiv:4"],"scientific_authority":False},
            ]},
        }

    def records(self) -> list[dict]:
        rows=[]
        for i in range(1,5):
            rows.append({"ref":f"arXiv:{i}","title":f"Paper {i}","abstract":f"Agent evidence {i}","primary_source_verified":True,"lane_keys":["skill_harness"],"empirical_facts":[{"text":f"Observed metric {i} changes by {10+i} percent."}],"typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]}})
        return rows

    def test_primary_abstract_is_preserved_when_fulltext_evidence_is_absent(self) -> None:
        record={"ref":"arXiv:1","title":"Paper 1","abstract":"Primary abstract carries the bounded empirical relation evidence.","lane_keys":["skill_harness"],"empirical_facts":[],"typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]}}
        card=_card(record)
        self.assertEqual(card["abstract"],record["abstract"])
        self.assertEqual(card["empirical"],[])

    def relation(self, proposals: bool = True, resolved: str = "doubao-seed-evolving"):
        def responder(**kwargs):
            lanes={}
            if proposals:
                lanes["CONTRADICTION"]=[{"source_a":"arXiv:1","source_b":"arXiv:3","relation":"The two observations require a shared measurement check.","why_lane":"Both are empirical results and may conflict after operational alignment.","missing_piece":"shared operationalization"}]
            return {"text":json.dumps({"lanes":lanes,"diagnosis":"bounded recall"}),"resolved_model":resolved}
        return responder

    def lane(self, verdict: str = "PASS", resolved: str = "glm-5-2-260617"):
        def responder(**kwargs):
            item={"proposal_id":"REL-CONTRADICTION-1","verdict":verdict,"reason":"strict lane review","missing":"" if verdict=="PASS" else "shared measurement"}
            return {"text":json.dumps({"reviews":[item],"diagnosis":"lane review"}),"resolved_model":resolved}
        return responder

    def reduction(self, verdict: str = "REDUCIBLE", resolved: str = "deepseek-v4-flash-ga-260731"):
        def responder(**kwargs):
            residual="" if verdict=="REDUCIBLE" else "A concrete residual prediction remains after same-information projection."
            item={"proposal_id":"REL-CONTRADICTION-1","verdict":verdict,"exact_prediction":"Prediction under matched information.","matched_patterns":[],"strongest_reduction":"mature object" if verdict=="REDUCIBLE" else "none","residual_prediction":residual}
            return {"text":json.dumps({"reviews":[item],"diagnosis":"reduction review"}),"resolved_model":resolved}
        return responder

    def test_incomplete_cache_holds_with_zero_model_calls(self) -> None:
        calls=[]
        def forbidden(**kwargs): calls.append(1); raise AssertionError("model call forbidden")
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records()[:2],previous_state={},relation_responder=forbidden,lane_responder=forbidden,reduction_responder=forbidden,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"HOLD_RELATION_CACHE_INCOMPLETE")
        self.assertEqual(calls,[])
        self.assertEqual(state["cache_missing_count"],2)
        self.assertFalse(state["policy"]["automatic_problem_gate_authority"])

    def test_zero_proposal_scan_completes_without_downstream_calls(self) -> None:
        calls=[]; relation=self.relation(False)
        def relation_only(**kwargs): calls.append("relation"); return relation(**kwargs)
        def forbidden(**kwargs): calls.append("forbidden"); raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=relation_only,lane_responder=forbidden,reduction_responder=forbidden,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"GLOBAL_RELATION_RECALL_COMPLETE")
        self.assertEqual(calls,["relation"])
        self.assertEqual(state["summary"]["relation_proposals"],0)
        self.assertEqual(state["last_completed_scan"]["relation_universe_digest"],state["relation_coverage"]["relation_universe_digest"])

    def test_lane_pass_is_reduction_reviewed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=self.relation(),lane_responder=self.lane(),reduction_responder=self.reduction(),now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"GLOBAL_RELATION_RECALL_COMPLETE")
        self.assertEqual((state["summary"]["lane_pass"],state["summary"]["reduction_reviewed"],state["summary"]["reducible"],state["summary"]["not_reduced"]),(1,1,1,0))
        self.assertFalse(state["summary"]["focused_problem_generator_reopen_required"])

    def test_not_reduced_only_requests_focused_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=self.relation(),lane_responder=self.lane(),reduction_responder=self.reduction("NOT_REDUCED"),now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["summary"]["not_reduced"],1)
        self.assertTrue(state["summary"]["focused_problem_generator_reopen_required"])
        for key in ("automatic_problem_gate_authority","automatic_method_authority","automatic_experiment_authority","automatic_p0_authority"):
            self.assertFalse(state["policy"][key])

    def test_same_relation_universe_reuses_completed_scan_with_zero_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));now=datetime(2026,8,13,tzinfo=timezone.utc)
            first=run_global_relation_recall(storage=storage,primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=self.relation(),lane_responder=self.lane(),reduction_responder=self.reduction(),now=now)
            calls=[]
            def forbidden(**kwargs): calls.append(1); raise AssertionError
            second=run_global_relation_recall(storage=storage,primary_state=self.primary(),generator_state=self.generator(),cache_records=[],previous_state=first,relation_responder=forbidden,lane_responder=forbidden,reduction_responder=forbidden,now=now)
        self.assertEqual(second["status"],"SKIPPED_RELATION_UNIVERSE_UNCHANGED")
        self.assertEqual(calls,[])
        self.assertEqual(second["last_completed_scan"]["run_id"],first["run_id"])
        self.assertEqual(second["summary"]["lane_pass"],1)

    def test_lane_reviewer_must_resolve_independently(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=self.relation(resolved="same-model"),lane_responder=self.lane(resolved="same-model"),reduction_responder=self.reduction(),now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"LANE_REVIEW_ERROR_ZERO_AUTHORITY")
        self.assertIn("not-independent",state["error"])
        self.assertEqual(state["summary"]["scientifically_authorized"],0)


if __name__=="__main__":unittest.main()
