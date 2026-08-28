from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .asset_first_stri_skillpro_p0 import (
    DEFAULT_THRESHOLD,
    EXPECTED_SOURCE_SHA256,
    assign_identities,
    build_result,
    frozen_arms,
    frozen_semantic_evidence,
    readiness_coordinates,
    semantic_evidence_hash,
    source_contract_audit,
    weak_compositions,
)


class STRISkillProP0Test(unittest.TestCase):
    def test_six_vs_three_plus_three_is_evolution_fragmented(self) -> None:
        canonical = readiness_coordinates([6], threshold=6)
        split = readiness_coordinates([3, 3], threshold=6)
        self.assertTrue(canonical["quotient_ready"])
        self.assertTrue(canonical["native_any_identity_ready"])
        self.assertTrue(split["quotient_ready"])
        self.assertFalse(split["native_any_identity_ready"])
        self.assertEqual(split["regime"], "evolution_fragmented")
        self.assertEqual(split["q"], 1.0)
        self.assertEqual(split["p"], 0.5)

    def test_frozen_arms_preserve_semantic_evidence(self) -> None:
        result = frozen_arms(threshold=DEFAULT_THRESHOLD)
        expected = result["frozen_semantic_evidence_sha256"]
        for name in ("canonical", "id_placebo", "exact_split", "pre_gate_quotient", "late_dedup"):
            self.assertEqual(result["arms"][name]["semantic_evidence_sha256"], expected, name)

    def test_frozen_arm_predictions(self) -> None:
        result = frozen_arms(threshold=6)["arms"]
        self.assertEqual(result["canonical"]["ready_identities"], ["skill_c"])
        self.assertEqual(result["id_placebo"]["ready_identities"], ["skill_c_renamed"])
        self.assertEqual(result["exact_split"]["ready_identities"], [])
        self.assertTrue(result["exact_split"]["semantic_ready"])
        self.assertEqual(result["pre_gate_quotient"]["ready_identities"], ["skill_c_a"])
        self.assertEqual(result["late_dedup"]["ready_before_dedup"], [])
        self.assertEqual(result["late_dedup"]["ready_after_identity_only_dedup"], [])
        self.assertFalse(result["zero_evidence"]["semantic_ready"])

    def test_identity_attribution_is_excluded_from_semantic_hash(self) -> None:
        evidence = frozen_semantic_evidence(6)
        one = assign_identities(evidence, ["a"] * 6)
        split = assign_identities(evidence, ["a"] * 3 + ["b"] * 3)
        self.assertEqual(semantic_evidence_hash(one), semantic_evidence_hash(split))

    def test_weak_compositions_are_complete_for_small_case(self) -> None:
        comps = list(weak_compositions(3, 2))
        self.assertEqual(comps, [(0, 3), (1, 2), (2, 1), (3, 0)])

    def test_source_contract_audit_fails_closed_on_wrong_hashes_but_recognizes_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Skills").mkdir()
            evolution = '''
from collections import defaultdict
class SkillEvolution:
    def __init__(self, llm_agent, threshold: int = 6, epsilon: float = 0.2):
        self.threshold = threshold
        # 按 Skill Name 存储积累的经验轨迹
        self.experience_buffer = defaultdict(list)
    def run(self, new_experiences, all_skills):
        for exp in new_experiences:
            skill_names = exp.skill.split(";")
            for sk_name in skill_names:
                self.experience_buffer[sk_name].append(exp)
        for sk in all_skills:
            buffered_exps = self.experience_buffer.get(sk.name, [])
            if len(buffered_exps) >= self.threshold:
                pass
'''
            pool = '''
def _semantic_dedup_inplace(self, skills, score_fn, log_remove, stage="semantic-duplicate", thr: float = 0.95):
    pass

def maintain(self):
    self._semantic_dedup_inplace(self.skills, score_fn=lambda x: 0, log_remove=lambda x: None, thr=0.95)
'''
            run = '''
def train(self):
    self.skill_evolver.run_skill_evolution_with_verification()
    self.skill_pool.maintain()
'''
            structures = '''
class Skill:
    name: str = "NewSkill"
class Experience:
    skill: str
'''
            (root / "Skills" / "skill_evolution.py").write_text(evolution, encoding="utf-8")
            (root / "Skills" / "skill_pool.py").write_text(pool, encoding="utf-8")
            (root / "run.py").write_text(run, encoding="utf-8")
            (root / "data_structures.py").write_text(structures, encoding="utf-8")
            audit = source_contract_audit(root)
            self.assertTrue(audit["all_required_anchors_present"])
            self.assertFalse(audit["source_sha256_match_frozen_pin"])
            self.assertNotEqual(audit["source_sha256"], EXPECTED_SOURCE_SHA256)

    def test_build_result_without_source_never_claims_behavior(self) -> None:
        result = build_result()
        self.assertTrue(result["all_checks_pass"])
        boundary = result["scientific_boundary"]
        self.assertFalse(boundary["claim_expansion"])
        self.assertFalse(boundary["behavioral_claim_authorized"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)


if __name__ == "__main__":
    unittest.main()
