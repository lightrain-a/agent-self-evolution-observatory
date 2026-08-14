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
            with patch("research_pipeline.problem_search_stage_runner._ark",return_value=response):
                result=runner.expand(pool=pool,run_root=run,lane="CONVERGENT_FAILURE",count=1,model="test",part=1,memory_path=mem)
            artifact=json.loads((run/"expand-CONVERGENT_FAILURE-p1.json").read_text(encoding="utf-8"))
        self.assertEqual(result["valid_seeds"],0)
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
