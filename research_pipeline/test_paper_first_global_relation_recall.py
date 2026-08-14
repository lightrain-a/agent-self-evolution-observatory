from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_global_relation_recall import _card, run_global_relation_recall, write_global_relation_recall_state
from .paper_first_relation_coverage import relation_universe_digest


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

    def test_provider_error_preserves_last_completed_scan_boundary(self) -> None:
        previous=self.previous_scan_for_first_receipt()
        def limited(**kwargs):
            raise RuntimeError("Ark HTTP 429: RequestBurstTooFast")
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state=previous,relation_responder=limited,lane_responder=self.lane(),reduction_responder=self.reduction(),now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"RELATION_PROVIDER_ERROR_ZERO_AUTHORITY")
        self.assertEqual(state["last_completed_scan"],previous["last_completed_scan"])
        self.assertEqual(state["summary"]["scientifically_authorized"],0)

    def previous_scan_for_first_receipt(self) -> dict:
        first=self.generator()["saturation_memory"]["portable_review_receipts"][0]
        digest=relation_universe_digest([first])
        return {
            "summary":{"not_reduced":0,"focused_problem_generator_reopen_required":False,"relation_universe_digest":digest},
            "proposals":[],
            "last_completed_scan":{"run_id":"r1","relation_universe_digest":digest,"relation_coverage":{"reviewed_receipt_sources":2,"possible_source_pairs":1,"coobserved_source_pairs":1,"pair_coverage_fraction":1.0},"summary":{"not_reduced":0},"scientific_authority":False},
            "scientific_authority":False,
        }

    def test_stale_relation_universe_scans_only_pairs_touching_new_source(self) -> None:
        prompts=[]
        relation=self.relation()
        def capture(**kwargs): prompts.append(kwargs["prompt"]); return relation(**kwargs)
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state=self.previous_scan_for_first_receipt(),relation_responder=capture,lane_responder=self.lane(),reduction_responder=self.reduction(),now=datetime(2026,8,14,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"GLOBAL_RELATION_RECALL_COMPLETE")
        self.assertTrue(state["delta_scan"]["enabled"])
        self.assertEqual(state["delta_scan"]["required_new_endpoint_count"],2)
        self.assertEqual(state["last_completed_scan"]["mode"],"delta_only_new_endpoint")
        self.assertEqual(state["last_completed_scan"]["prior_scan_run_id"],"r1")
        self.assertEqual(state["proposals"][0]["source_refs"],["arXiv:1","arXiv:3"])
        self.assertIn("REQUIRED_NEW_ENDPOINTS",prompts[0])
        self.assertIn("arXiv:3",prompts[0]);self.assertIn("arXiv:4",prompts[0])
        self.assertTrue(state["policy"]["delta_only_scan_forbids_old_old_pairs"])
        self.assertFalse(state["scientific_authority"])

    def test_delta_scan_rejects_old_old_pair_before_lane_reviewer(self) -> None:
        calls=[]
        def old_old(**kwargs):
            calls.append("relation")
            return {"text":json.dumps({"lanes":{"CONTRADICTION":[{"source_a":"arXiv:1","source_b":"arXiv:2","relation":"old-old relation","why_lane":"old-only","missing_piece":""}]},"diagnosis":"bad delta"}),"resolved_model":"doubao-seed-evolving"}
        def forbidden(**kwargs): calls.append("downstream"); raise AssertionError("downstream reviewer forbidden")
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state=self.previous_scan_for_first_receipt(),relation_responder=old_old,lane_responder=forbidden,reduction_responder=forbidden,now=datetime(2026,8,14,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"RELATION_PROVIDER_ERROR_ZERO_AUTHORITY")
        self.assertIn("misses-required-delta-endpoint",state["error"])
        self.assertEqual(calls,["relation"])

    def test_unreconstructable_prior_scan_boundary_blocks_all_model_calls(self) -> None:
        previous=self.previous_scan_for_first_receipt();previous["last_completed_scan"]["relation_universe_digest"]="f"*64
        calls=[]
        def forbidden(**kwargs): calls.append(1); raise AssertionError("model call forbidden")
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state=previous,relation_responder=forbidden,lane_responder=forbidden,reduction_responder=forbidden,now=datetime(2026,8,14,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"HOLD_RELATION_DELTA_BOUNDARY_UNRECONSTRUCTABLE")
        self.assertEqual(calls,[])
        self.assertFalse(state["scientific_authority"])

    def eligible_admission(self) -> dict:
        return {
            "schema_version":"1.0","status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN",
            "policy":{"scientific_authority":False,"automatic_model_scan_authority":False,"manual_execution_requires_explicit_operator_flag":True,"manual_eligibility_is_not_scientific_authority":True,"relation_scan_cannot_authorize_problem_gate":True,"relation_scan_cannot_authorize_method_experiment_p0_gpu":True,"preconditions_are_deterministic_search_control_only":True},
            "summary":{"checks":15,"passed":15,"failed":0,"manual_scan_eligible":True,"automatic_model_scan_authorized":False},
            "failed_checks":[],"freshness_status":"STALE_RELATION_UNIVERSE","delta_status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","scientific_authority":False,
        }

    def test_writer_rejects_missing_explicit_manual_intent_before_models_or_files(self) -> None:
        calls=[]
        def forbidden(**kwargs): calls.append(1); raise AssertionError("model call forbidden")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);json_path=root/"public.json";js_path=root/"public.js"
            with self.assertRaisesRegex(RuntimeError,"explicit manual scan intent"):
                write_global_relation_recall_state(json_path,js_path,storage=self.storage(root),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=forbidden,lane_responder=forbidden,reduction_responder=forbidden)
            self.assertEqual(calls,[]);self.assertFalse(json_path.exists());self.assertFalse(js_path.exists())

    def test_writer_rejects_failed_admission_before_models_or_files(self) -> None:
        calls=[]
        def forbidden(**kwargs): calls.append(1); raise AssertionError("model call forbidden")
        def hold(**kwargs): return {"status":"HOLD_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":False},"failed_checks":["new-typed-evidence-delta-nonzero"],"scientific_authority":False}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);json_path=root/"public.json";js_path=root/"public.js"
            with self.assertRaisesRegex(RuntimeError,"writer admission blocked"):
                write_global_relation_recall_state(json_path,js_path,storage=self.storage(root),explicit_manual_scan_intent=True,admission_builder=hold,primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=forbidden,lane_responder=forbidden,reduction_responder=forbidden)
            self.assertEqual(calls,[]);self.assertFalse(json_path.exists());self.assertFalse(js_path.exists())

    def test_writer_records_manual_admission_when_explicit_and_eligible(self) -> None:
        calls=[];relation=self.relation(False)
        def relation_only(**kwargs): calls.append("relation"); return relation(**kwargs)
        def forbidden(**kwargs): calls.append("downstream"); raise AssertionError("downstream forbidden")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);json_path=root/"public.json";js_path=root/"public.js"
            state=write_global_relation_recall_state(json_path,js_path,storage=self.storage(root),explicit_manual_scan_intent=True,admission_builder=lambda **kwargs:self.eligible_admission(),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=relation_only,lane_responder=forbidden,reduction_responder=forbidden,now=datetime(2026,8,14,tzinfo=timezone.utc))
            self.assertEqual(calls,["relation"]);self.assertTrue(json_path.exists());self.assertTrue(js_path.exists())
            self.assertTrue(state["policy"]["explicit_manual_writer_admission_required"])
            self.assertTrue((state.get("writer_admission") or {}).get("summary",{}).get("manual_scan_eligible"))
            self.assertFalse((state.get("writer_admission") or {}).get("summary",{}).get("automatic_model_scan_authorized"))

    def test_lane_reviewer_must_resolve_independently(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state=run_global_relation_recall(storage=self.storage(Path(td)),primary_state=self.primary(),generator_state=self.generator(),cache_records=self.records(),previous_state={},relation_responder=self.relation(resolved="same-model"),lane_responder=self.lane(resolved="same-model"),reduction_responder=self.reduction(),now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"LANE_REVIEW_ERROR_ZERO_AUTHORITY")
        self.assertIn("not-independent",state["error"])
        self.assertEqual(state["summary"]["scientifically_authorized"],0)


if __name__=="__main__":unittest.main()
