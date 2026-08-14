from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import problem_search_stage_runner as runner


class ProblemSearchStageRunnerMemoryTest(unittest.TestCase):
    def memory(self, candidate_id: str = "SHADOW-P12-C01") -> dict:
        return {
            "shadow_dead_end_memory": {
                "memory_id": "test-shadow-memory",
                "blocked_objects": [
                    {
                        "source_candidate_id": candidate_id,
                        "basin": "current-source-hard-veto-test",
                        "strongest_reduction": "generic identifiability over an omitted compiled-context variable",
                        "current_source_refs": ["arXiv:2605.10114"],
                        "reopen_only_if": "A same-information residual survives explicit instrumentation.",
                        "scientific_authority": False,
                    }
                ],
                "live_source_coverage_effect": False,
                "cannot_mutate_canonical_generator_or_queue": True,
                "scientific_authority": False,
            }
        }

    def test_missing_explicit_memory_uses_generated_design_adjudication_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "design.json"
            path.write_text(json.dumps(self.memory()), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", path):
                memory = runner._shadow_dead_end_memory(None)
        self.assertEqual(memory["blocked_objects"][0]["source_candidate_id"], "SHADOW-P12-C01")
        self.assertFalse(memory["scientific_authority"])

    def test_explicit_memory_path_overrides_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            default = root / "default.json"
            explicit = root / "explicit.json"
            default.write_text(json.dumps(self.memory("DEFAULT")), encoding="utf-8")
            explicit.write_text(json.dumps(self.memory("EXPLICIT")), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", default):
                memory = runner._shadow_dead_end_memory(explicit)
        self.assertEqual(memory["blocked_objects"][0]["source_candidate_id"], "EXPLICIT")

    def test_missing_default_memory_is_empty_search_control(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing.json"
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", missing):
                self.assertEqual(runner._shadow_dead_end_memory(None), {})

    def test_illegal_default_memory_authority_fails_closed(self) -> None:
        payload = self.memory()
        payload["shadow_dead_end_memory"]["scientific_authority"] = True
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", path):
                with self.assertRaisesRegex(ValueError, "zero-authority"):
                    runner._shadow_dead_end_memory(None)

    def test_qualified_expand_defaults_to_run_local_pool_and_memory_for_validation_and_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/"shadow-qualified";run.mkdir();local_pool=run/"frozen-primary-evidence-pool.json";local_memory=run/"shadow-dead-end-memory.json";global_memory=root/"global-memory.json"
            local_pool.write_text(json.dumps({"frozen_pool_sha256":"a"*64,"records":[]}),encoding="utf-8")
            local_memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[],"memory_id":"RUN_LOCAL"}),encoding="utf-8")
            global_memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[],"memory_id":"GLOBAL"}),encoding="utf-8")
            response={"text":json.dumps({"seeds":[]}),"resolved_model":"test-model"}
            def prompt(lane,records,count,memory):
                self.assertEqual(memory.get("memory_id"),"RUN_LOCAL")
                return "prompt"
            with patch.object(runner,"DEFAULT_SHADOW_DEAD_END_MEMORY_PATH",global_memory),patch("research_pipeline.problem_search_stage_runner.validate_shadow_run_control",return_value={"control_snapshot_sha256":"f"*64}) as validate,patch("research_pipeline.problem_search_stage_runner._expansion_prompt",side_effect=prompt),patch("research_pipeline.problem_search_stage_runner._ark",return_value=response):
                result=runner.expand(pool=None,run_root=run,lane="CONTRADICTION",count=1,model="test",part=1,memory_path=None)
            validate.assert_called_once_with(run_root=run,pool_path=local_pool,memory_path=local_memory)
            artifact=json.loads((run/"expand-CONTRADICTION-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(result["valid_seeds"],0)
        self.assertEqual(artifact["control_snapshot_sha256"],"f"*64)

    def test_missing_pool_without_run_local_frozen_pool_fails_before_provider(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)/"shadow-missing-pool";run.mkdir()
            with patch("research_pipeline.problem_search_stage_runner._ark") as provider:
                with self.assertRaisesRegex(ValueError,"run-local frozen-primary-evidence-pool"):
                    runner.expand(pool=None,run_root=run,lane="CONTRADICTION",count=1,model="test",part=1,memory_path=None)
            provider.assert_not_called()

    def test_same_pool_semantic_dead_end_is_machine_filtered_after_model_output(self) -> None:
        pool_sha="a"*64
        dead_claim_a="A weak optimizer cannot operate through the unchanged open-ended optimization interface."
        dead_claim_b="A weak coding agent fails to converge on all three verifier extension tasks."
        memory={"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[{"source_candidate_id":"R3-LANE","basin":"semantic-lane-contract-deadbeef","search_primitive":"CONVERGENT_FAILURE","current_source_refs":["arXiv:2608.09629","arXiv:2608.11340"],"evidence_claims":[dead_claim_a,dead_claim_b],"problem_text":"Capability-dependent collapse of open-ended self-evolving optimizers","frozen_pool_sha256":pool_sha,"strongest_reduction":"cross-model instruction compatibility","reason":"no shared bounded condition","reopen_only_if":"new primary evidence supplies the missing lane contract","scientific_authority":False}]}
        seed={"title":"Capability-dependent inability to operate an open self-evolution interface","problem_seed":"When does optimizer capability make an open self-evolution interface non-operable?","scientific_tension":"The same interface works for strong models and fails for weak ones.","problem_family":"optimizer-enactability","structural_signature":"capability|interface|nonconvergence|self-evolution","agent_specific_constraint":"fixed objective and budget","empirical_evidence":{"source_a":{"ref":"arXiv:2608.09629","claim":dead_claim_a,"evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":"arXiv:2608.11340","claim":dead_claim_b,"evidence_role":"EMPIRICAL_FACT"},"relation":"both fail under a bounded self-evolution loop"},"lane_evidence":{"shared_condition":"fixed objective and budget","method_a":"open-ended optimizer","method_b":"network verifier evolution","failure_a":"cannot operate","failure_b":"fails to converge","independence_basis":"independent artifact families"},"scores":{"importance":80,"specificity":80,"seed_distance":80,"evidence_grounding":80}}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";mem=root/"memory.json";run=root/"run"
            pool.write_text(json.dumps({"frozen_pool_sha256":pool_sha,"records":[{"ref":"arXiv:2608.09629"},{"ref":"arXiv:2608.11340"}]}),encoding="utf-8")
            mem.write_text(json.dumps(memory),encoding="utf-8")
            response={"text":json.dumps({"seeds":[seed],"notes":"test"}),"resolved_model":"test-model"}
            with patch("research_pipeline.problem_search_stage_runner._ark",return_value=response),patch("research_pipeline.problem_search_stage_runner.validate_shadow_run_control",return_value={"control_snapshot_sha256":"f"*64}):
                result=runner.expand(pool=pool,run_root=run,lane="CONVERGENT_FAILURE",count=1,model="test",part=1,memory_path=mem)
            artifact=json.loads((run/"expand-CONVERGENT_FAILURE-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(result["valid_seeds"],0)
        self.assertEqual(artifact["schema_version"],runner.STAGE_RUNNER_ARTIFACT_SCHEMA)
        self.assertEqual(artifact["control_snapshot_sha256"],"f"*64)
        self.assertEqual(artifact["semantic_dead_end_block_count"],1)
        self.assertEqual(artifact["semantic_dead_end_blocks"][0]["source_candidate_id"],"R3-LANE")
        self.assertFalse(artifact["semantic_dead_end_blocks"][0]["scientific_authority"])

    def test_semantic_dead_end_machine_filter_reopens_on_new_frozen_pool(self) -> None:
        seed={"discovery_lane":"CONVERGENT_FAILURE","title":"optimizer capability threshold","problem_seed":"same object","scientific_tension":"same tension","structural_signature":"same signature","empirical_evidence":{"source_a":{"ref":"arXiv:1","claim":"weak optimizer cannot operate interface"},"source_b":{"ref":"arXiv:2","claim":"weak agent fails to converge"}}}
        memory={"blocked_objects":[{"source_candidate_id":"OLD","basin":"semantic-lane-contract-x","search_primitive":"CONVERGENT_FAILURE","current_source_refs":["arXiv:1","arXiv:2"],"evidence_claims":["weak optimizer cannot operate interface","weak agent fails to converge"],"problem_text":"optimizer capability threshold","frozen_pool_sha256":"a"*64,"scientific_authority":False}]}
        self.assertIsNotNone(runner._semantic_dead_end_seed_blocker(seed,memory,"a"*64))
        self.assertIsNone(runner._semantic_dead_end_seed_blocker(seed,memory,"b"*64))

    def test_evolution_cannot_reenter_same_pool_semantic_dead_end(self) -> None:
        pool_sha="a"*64
        claim_a="A weak optimizer cannot operate through the unchanged open-ended optimization interface."
        claim_b="A weak coding agent fails to converge on all three verifier extension tasks."
        memory={"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[{"source_candidate_id":"R3-LANE","basin":"semantic-lane-contract-deadbeef","search_primitive":"CONVERGENT_FAILURE","current_source_refs":["arXiv:2608.09629","arXiv:2608.11340"],"evidence_claims":[claim_a,claim_b],"problem_text":"Capability-dependent collapse of open-ended self-evolving optimizers","frozen_pool_sha256":pool_sha,"scientific_authority":False}]}
        parent={"seed_id":"PARENT","discovery_lane":"CONVERGENT_FAILURE","title":"Capability-dependent collapse of open-ended self-evolving optimizers","problem_seed":"optimizer capability threshold","scientific_tension":"same interface works for strong models and fails for weak ones","problem_family":"optimizer-enactability","structural_signature":"capability|interface|nonconvergence|self-evolution","agent_specific_constraint":"fixed objective and budget","empirical_evidence":{"source_a":{"ref":"arXiv:2608.09629","claim":claim_a,"evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":"arXiv:2608.11340","claim":claim_b,"evidence_role":"EMPIRICAL_FACT"},"relation":"both fail under bounded self-evolution"},"lane_evidence":{"shared_condition":"fixed objective and budget","method_a":"open-ended optimizer","method_b":"network verifier evolution","failure_a":"cannot operate","failure_b":"fails to converge","independence_basis":"independent artifact families"},"scores":{"importance":80,"specificity":80,"seed_distance":80,"evidence_grounding":80}}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";mem=root/"memory.json";run=root/"run";run.mkdir()
            pool.write_text(json.dumps({"frozen_pool_sha256":pool_sha,"records":[{"ref":"arXiv:2608.09629"},{"ref":"arXiv:2608.11340"}]}),encoding="utf-8")
            mem.write_text(json.dumps(memory),encoding="utf-8")
            (run/"base.json").write_text(json.dumps({"parents":[parent]}),encoding="utf-8")
            response={"text":json.dumps({"children":[{"parent_id":"PARENT","title":"Capability-dependent collapse of open-ended self-evolving optimizers"}]}),"resolved_model":"test-model"}
            with patch("research_pipeline.problem_search_stage_runner._ark",return_value=response):
                result=runner.evolve(pool=pool,run_root=run,generation=1,part=1,batch_size=1,model="test",memory_path=mem)
            artifact=json.loads((run/"evolve-g1-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(result["valid_children"],0)
        self.assertEqual(artifact["semantic_dead_end_block_count"],1)
        self.assertEqual(artifact["semantic_dead_end_blocks"][0]["source_candidate_id"],"R3-LANE")

    def test_formulation_cannot_reenter_same_pool_semantic_dead_end(self) -> None:
        pool_sha="a"*64
        claim_a="A weak optimizer cannot operate through the unchanged open-ended optimization interface."
        claim_b="A weak coding agent fails to converge on all three verifier extension tasks."
        memory={"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[{"source_candidate_id":"R3-LANE","basin":"semantic-lane-contract-deadbeef","search_primitive":"CONVERGENT_FAILURE","current_source_refs":["arXiv:2608.09629","arXiv:2608.11340"],"evidence_claims":[claim_a,claim_b],"problem_text":"Capability-dependent collapse of open-ended self-evolving optimizers","frozen_pool_sha256":pool_sha,"scientific_authority":False}]}
        parent={"seed_id":"PARENT","discovery_lane":"CONVERGENT_FAILURE","title":"different initial wording","problem_seed":"different initial object","scientific_tension":"different initial tension","problem_family":"optimizer-enactability","structural_signature":"different|initial|signature","agent_specific_constraint":"fixed objective and budget","empirical_evidence":{"source_a":{"ref":"arXiv:2608.09629","claim":claim_a,"evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":"arXiv:2608.11340","claim":claim_b,"evidence_role":"EMPIRICAL_FACT"},"relation":"both fail under bounded self-evolution"},"lane_evidence":{"shared_condition":"fixed objective and budget","method_a":"open-ended optimizer","method_b":"network verifier evolution","failure_a":"cannot operate","failure_b":"fails to converge","independence_basis":"independent artifact families"},"scores":{"importance":80,"specificity":80,"seed_distance":80,"evidence_grounding":80}}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";mem=root/"memory.json";run=root/"run";run.mkdir()
            pool.write_text(json.dumps({"frozen_pool_sha256":pool_sha,"records":[{"ref":"arXiv:2608.09629"},{"ref":"arXiv:2608.11340"}]}),encoding="utf-8")
            mem.write_text(json.dumps(memory),encoding="utf-8")
            (run/"base.json").write_text(json.dumps({"parents":[parent]}),encoding="utf-8")
            response={"text":json.dumps({"candidates":[{"candidate_id":"MODEL-1","source_branch_id":"PARENT","title":"Capability-dependent collapse of open-ended self-evolving optimizers","irreducible_object":"optimizer capability threshold for the unchanged open-ended interface","exact_prediction":"weak optimizers fail to enact the route while strong optimizers succeed"}],"rejected":[]}),"resolved_model":"test-model"}
            with patch("research_pipeline.problem_search_stage_runner._ark",return_value=response):
                result=runner.formulate(pool=pool,run_root=run,part=1,batch_size=1,budget=1,model="test",memory_path=mem)
            artifact=json.loads((run/"formulate-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(result["candidates"],0)
        self.assertEqual(artifact["semantic_dead_end_block_count"],1)
        self.assertEqual(artifact["semantic_dead_end_blocks"][0]["source_candidate_id"],"R3-LANE")

    def test_formulation_precheck_has_three_fail_closed_routes(self) -> None:
        candidate={"candidate_id":"SHADOW-P01-C01","exact_prediction":"matched prediction","strongest_same_information_baseline":"mature baseline","cheapest_problem_falsifier":"run matched falsifier"}
        exact_only={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","saturation-exact-reduction-pending:procedural-memory-nonmonotonicity","unresolved-exact-reduction-test:1"]}
        with patch("research_pipeline.problem_search_stage_runner._normalize",return_value=candidate),patch("research_pipeline.problem_search_stage_runner.audit_shadow_problem_candidate",return_value=exact_only):
            route,normalized,audit=runner._formulation_precheck(candidate,{})
        self.assertEqual(route,"reduction-pending");self.assertIs(normalized,candidate);self.assertEqual(audit,exact_only)
        underformed={"passed":False,"blockers":["domain-transfer-audit-incomplete","unresolved-exact-reduction-test:1"]}
        with patch("research_pipeline.problem_search_stage_runner._normalize",return_value=candidate),patch("research_pipeline.problem_search_stage_runner.audit_shadow_problem_candidate",return_value=underformed):
            route,_,_=runner._formulation_precheck(candidate,{})
        self.assertEqual(route,"rejected")
        clear={"passed":True,"blockers":[]}
        with patch("research_pipeline.problem_search_stage_runner._normalize",return_value=candidate),patch("research_pipeline.problem_search_stage_runner.audit_shadow_problem_candidate",return_value=clear):
            route,_,_=runner._formulation_precheck(candidate,{})
        self.assertEqual(route,"machine-ready")

    def test_formulate_separates_machine_ready_reduction_pending_and_rejected(self) -> None:
        parent={"seed_id":"PARENT","discovery_lane":"UNEXPLAINED_BOUNDARY","title":"parent","problem_seed":"question","scientific_tension":"tension","problem_family":"family","structural_signature":"sig","agent_specific_constraint":"constraint","empirical_evidence":{"source_a":{"ref":"arXiv:1","claim":"A","evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":"arXiv:1","claim":"B","evidence_role":"EMPIRICAL_FACT"},"relation":"relation"},"lane_evidence":{"shared_measurement":"m","boundary_observation":"b","adjacent_regime":"a","unexplained_transition":"u"},"scores":{"importance":80,"specificity":80,"seed_distance":80,"evidence_grounding":80}}
        model_rows=[{"candidate_id":"MODEL-PENDING","source_branch_id":"PARENT","title":"pending","exact_prediction":"p","strongest_same_information_baseline":"b","cheapest_problem_falsifier":"f"},{"candidate_id":"MODEL-READY","source_branch_id":"PARENT","title":"ready"},{"candidate_id":"MODEL-BAD","source_branch_id":"PARENT","title":"bad"}]
        exact_audit={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"]};clear_audit={"passed":True,"blockers":[]};bad_audit={"passed":False,"blockers":["domain-transfer-audit-incomplete"]}
        def precheck(row,registry):
            if row["title"]=="pending":return "reduction-pending",{**row,"exact_prediction":"p","strongest_same_information_baseline":"b","cheapest_problem_falsifier":"f"},exact_audit
            if row["title"]=="ready":return "machine-ready",row,clear_audit
            return "rejected",row,bad_audit
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";mem=root/"memory.json";run=root/"run";run.mkdir()
            pool.write_text(json.dumps({"frozen_pool_sha256":"a"*64,"records":[{"ref":"arXiv:1"}]}),encoding="utf-8");mem.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[]}),encoding="utf-8");(run/"base.json").write_text(json.dumps({"parents":[parent]}),encoding="utf-8")
            response={"text":json.dumps({"candidates":model_rows,"rejected":[]}),"resolved_model":"test-model"}
            with patch("research_pipeline.problem_search_stage_runner._ark",return_value=response),patch("research_pipeline.problem_search_stage_runner._formulation_precheck",side_effect=precheck):
                result=runner.formulate(pool=pool,run_root=run,part=1,batch_size=1,budget=1,model="test",memory_path=mem)
            artifact=json.loads((run/"formulate-p1.json").read_text(encoding="utf-8"))
        self.assertEqual((result["candidates"],result["reduction_pending"],result["rejected"]),(1,1,1))
        self.assertEqual(artifact["candidates"][0]["candidate_id"],"SHADOW-P01-C02")
        self.assertEqual(artifact["reduction_pending"][0]["candidate_id"],"SHADOW-P01-C01")
        self.assertEqual(artifact["rejected"][0]["candidate_id"],"SHADOW-P01-C03")
        self.assertEqual(artifact["rejected"][0]["rejection_origin"],"deterministic-formulation-precheck")
        self.assertFalse(artifact["reduction_pending"][0]["scientific_authority"])

    def test_machine_audit_keeps_exact_reduction_uncertainty_out_of_blocked_count(self) -> None:
        candidate={"candidate_id":"SHADOW-P01-C01","model_candidate_id":"MODEL-1","title":"pending","discovery_lane":"UNEXPLAINED_BOUNDARY","source_branch_id":"B1","exact_prediction":"p","strongest_same_information_baseline":"b","cheapest_problem_falsifier":"f"}
        audit={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","saturation-exact-reduction-pending:procedural-memory-nonmonotonicity","unresolved-exact-reduction-test:1"]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";run=root/"run";run.mkdir();pool.write_text(json.dumps({"records":[]}),encoding="utf-8")
            (run/"formulate-p1.json").write_text(json.dumps({"part":1,"candidates":[],"reduction_pending":[{"candidate_id":"SHADOW-P01-C01","model_candidate_id":"MODEL-1","candidate":candidate}]}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._normalize",side_effect=lambda raw,registry:raw),patch("research_pipeline.problem_search_stage_runner.audit_shadow_problem_candidate",return_value=audit):
                summary=runner.machine_audit(pool=pool,run_root=run)
            artifact=json.loads((run/"machine-audit.json").read_text(encoding="utf-8"))
            evidence=json.loads((run/"evidence-acquisition-plan.json").read_text(encoding="utf-8"))
        self.assertEqual((summary["reviewable"],summary["reduction_pending"],summary["blocked"],summary["problem_falsifier_eligible"]),(0,1,0,1))
        self.assertEqual((summary["provisional_problem_candidates"],summary["evidence_design_selected"]),(1,1))
        self.assertEqual((evidence["summary"]["provisional_problem_candidates"],evidence["summary"]["design_pending"]),(1,1))
        self.assertFalse(evidence["scientific_authority"])
        self.assertFalse(evidence["authority"]["paper_design"])
        self.assertEqual(artifact["problem_falsifier_queue"][0]["candidate_id"],"SHADOW-P01-C01")
        self.assertEqual(artifact["reduction_pending"][0]["route_origin"],"formulation-reduction-pending")
        self.assertTrue(artifact["policy"]["reduction_pending_is_not_scientific_block_or_pass"])

    def test_machine_audit_routes_legacy_exact_reduction_candidate_without_false_block(self) -> None:
        candidate={"candidate_id":"SHADOW-P01-C01","model_candidate_id":"MODEL-1","title":"legacy pending","discovery_lane":"UNEXPLAINED_BOUNDARY","exact_prediction":"p","strongest_same_information_baseline":"b","cheapest_problem_falsifier":"f"}
        audit={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";run=root/"run";run.mkdir();pool.write_text(json.dumps({"records":[]}),encoding="utf-8");(run/"formulate-p1.json").write_text(json.dumps({"part":1,"candidates":[candidate]}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._normalize",side_effect=lambda raw,registry:raw),patch("research_pipeline.problem_search_stage_runner.audit_shadow_problem_candidate",return_value=audit):
                summary=runner.machine_audit(pool=pool,run_root=run)
        self.assertEqual((summary["reduction_pending"],summary["blocked"]),(1,0))

    def test_problem_falsifier_route_accepts_only_exact_reduction_uncertainty(self) -> None:
        candidate={"exact_prediction":"matched prediction","strongest_same_information_baseline":"procedural-memory nonmonotonicity","cheapest_problem_falsifier":"run one matched retrieval-set intervention"}
        eligible={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","saturation-exact-reduction-pending:procedural-memory-nonmonotonicity","unresolved-exact-reduction-test:1"]}
        self.assertTrue(runner._problem_falsifier_eligible(candidate,eligible))
        closest={"passed":False,"blockers":["closest-work-collision","unresolved-exact-reduction-test:1"]}
        self.assertFalse(runner._problem_falsifier_eligible(candidate,closest))
        invalid={"passed":False,"blockers":["invalid-saturation-scan-entry:x","unresolved-exact-reduction-test:1"]}
        self.assertFalse(runner._problem_falsifier_eligible(candidate,invalid))

    def test_problem_falsifier_route_requires_concrete_prediction_baseline_and_falsifier(self) -> None:
        audit={"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"]}
        self.assertFalse(runner._problem_falsifier_eligible({"exact_prediction":"x","strongest_same_information_baseline":"y","cheapest_problem_falsifier":""},audit))
        self.assertFalse(runner._problem_falsifier_eligible({"exact_prediction":"x","strongest_same_information_baseline":"","cheapest_problem_falsifier":"z"},audit))

    def test_provider_timeout_is_recorded_without_inventing_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pool=root/"pool.json";memory=root/"memory.json";run=root/"run"
            pool.write_text(json.dumps({"frozen_pool_sha256":"a"*64,"records":[]}),encoding="utf-8")
            memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[]}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._ark",side_effect=RuntimeError("HTTPS read timed out after 120 seconds")):
                with self.assertRaisesRegex(RuntimeError,"timed out"):
                    runner.expand(pool=pool,run_root=run,lane="CONTRADICTION",count=1,model="test-model",part=1,memory_path=memory)
            receipts=list(run.glob("error-expand-CONTRADICTION-p1-provider-*.json"))
            self.assertEqual(len(receipts),1)
            receipt=json.loads(receipts[0].read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"],"PROVIDER_TIMEOUT_ZERO_AUTHORITY")
            self.assertEqual(receipt["requested_model"],"test-model")
            self.assertFalse(receipt["complete_response_received"])
            self.assertEqual(receipt["raw_sha256"],"")
            self.assertFalse(receipt["scientific_authority"])
            self.assertFalse(receipt["authority"]["paper_design"])
            self.assertFalse((run/"expand-CONTRADICTION-p1.json").exists())
            self.assertFalse((run/"raw").exists())

    def test_provider_receipt_preserves_formulation_branch_ids(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)
            with patch("research_pipeline.problem_search_stage_runner._ark",side_effect=RuntimeError("provider unavailable")):
                with self.assertRaisesRegex(RuntimeError,"provider unavailable"):
                    runner._ark_with_provider_receipt(run_root=run,stem="formulate-p2",requested_model="test-model",context={"part":2,"branch_ids":["B1","B2"]},prompt="x",max_output_tokens=10,temperature=0.0)
            receipt=json.loads(next(run.glob("error-formulate-p2-provider-*.json")).read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"],"PROVIDER_ERROR_ZERO_AUTHORITY")
            self.assertEqual(receipt["branch_ids"],["B1","B2"])
            self.assertEqual(receipt["raw_sha256"],"")

    def test_mixed_control_snapshot_artifact_is_rejected_before_downstream_stage(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)/"run";run.mkdir()
            (run/"expand-CONTRADICTION-p1.json").write_text(json.dumps({"schema_version":runner.STAGE_RUNNER_ARTIFACT_SCHEMA,"control_snapshot_sha256":"e"*64,"lane":"CONTRADICTION","part":1,"seeds":[],"semantic_dead_end_block_count":0}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._assert_run_control",return_value="f"*64):
                with self.assertRaisesRegex(ValueError,"mixed shadow control snapshot artifact"):
                    runner.assemble(run_root=run)

    def test_artifact_schema_drift_is_rejected_before_downstream_stage(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)/"run";run.mkdir()
            (run/"expand-CONTRADICTION-p1.json").write_text(json.dumps({"schema_version":"1.3","control_snapshot_sha256":"f"*64,"lane":"CONTRADICTION","part":1,"seeds":[],"semantic_dead_end_block_count":0}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._assert_run_control",return_value="f"*64):
                with self.assertRaisesRegex(ValueError,"artifact schema drift"):
                    runner.assemble(run_root=run)

    def test_old_shadow_qualification_schema_stops_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/"shadow-old";run.mkdir();pool=run/"frozen-primary-evidence-pool.json";memory=run/"shadow-dead-end-memory.json"
            pool.write_text(json.dumps({"frozen_pool_sha256":"a"*64,"records":[{"ref":"arXiv:2608.00001"}]}),encoding="utf-8")
            memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[]}),encoding="utf-8")
            (run/"shadow-run-qualification.json").write_text(json.dumps({"status":"READY_FOR_SHADOW_EXPANSION","scientific_authority":False,"stage_runner_required_schema":"1.3","authority":{"canonical_generator":False,"canonical_queue":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._ark") as provider,patch("sys.argv",["problem_search_stage_runner","expand","--run-root",str(run),"--pool",str(pool),"--memory",str(memory),"--lane","CONTRADICTION","--part","1","--count","1"]):
                with self.assertRaisesRegex(ValueError,"stage-runner schema drift"):
                    runner.main()
            provider.assert_not_called()

    def test_unqualified_shadow_run_stops_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/"shadow-new";run.mkdir();pool=run/"frozen-primary-evidence-pool.json";memory=run/"shadow-dead-end-memory.json"
            pool.write_text(json.dumps({"frozen_pool_sha256":"a"*64,"records":[{"ref":"arXiv:2608.00001"}]}),encoding="utf-8")
            memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[]}),encoding="utf-8")
            with patch("research_pipeline.problem_search_stage_runner._ark") as provider,patch("sys.argv",["problem_search_stage_runner","expand","--run-root",str(run),"--pool",str(pool),"--memory",str(memory),"--lane","CONTRADICTION","--part","1","--count","1"]):
                with self.assertRaisesRegex(ValueError,"qualified shadow run receipt"):
                    runner.main()
            provider.assert_not_called()

    def test_qualification_stop_marker_blocks_future_stage_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)
            (run/"shadow-run-qualification-stop.json").write_text(json.dumps({"status":"STOP_BEFORE_ASSEMBLE_CONTROL_SNAPSHOT_SUPERSEDED"}),encoding="utf-8")
            with patch("sys.argv",["problem_search_stage_runner","assemble","--run-root",str(run)]):
                with self.assertRaisesRegex(SystemExit,"STOP_BEFORE_ASSEMBLE_CONTROL_SNAPSHOT_SUPERSEDED"):
                    runner.main()

    def test_malformed_model_output_is_archived_before_parse_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pool = root / "pool.json"
            memory = root / "memory.json"
            run = root / "run"
            pool.write_text(json.dumps({"records": []}), encoding="utf-8")
            memory.write_text(json.dumps({
                "scientific_authority": False,
                "live_source_coverage_effect": False,
                "cannot_mutate_canonical_generator_or_queue": True,
                "blocked_objects": [],
            }), encoding="utf-8")
            response = {"text": '{"seeds":[{"broken":1}', "resolved_model": "test-model"}
            with patch("research_pipeline.problem_search_stage_runner._ark", return_value=response):
                with self.assertRaises(json.JSONDecodeError):
                    runner.expand(pool=pool, run_root=run, lane="CONTRADICTION", count=1, model="test", part=1, memory_path=memory)
            raw_files = list((run / "raw").glob("expand-CONTRADICTION-p1-*.txt"))
            error_files = list(run.glob("error-expand-CONTRADICTION-p1-*.json"))
            self.assertEqual(len(raw_files), 1)
            self.assertEqual(len(error_files), 1)
            error = json.loads(error_files[0].read_text(encoding="utf-8"))
            self.assertEqual(error["status"], "PARSE_ERROR_ZERO_AUTHORITY")
            self.assertEqual(error["resolved_model"], "test-model")
            self.assertTrue(error["raw_sha256"].startswith(raw_files[0].stem.rsplit("-", 1)[-1]))
            self.assertFalse(error["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
