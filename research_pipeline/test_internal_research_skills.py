from __future__ import annotations

import unittest

from .internal_research_skills import (
    CANONICAL_INTERNAL_SKILLS,
    EXTERNAL_SKILL_DISTILLATION,
    build_internal_research_skill_state,
    compile_internal_skill_job,
    route_internal_skills,
    validate_internal_skill_library,
)


class InternalResearchSkillsTest(unittest.TestCase):
    def test_all_eight_external_packs_are_distilled_with_zero_runtime_dependency(self) -> None:
        state = build_internal_research_skill_state()
        self.assertEqual(state["status"], "INTERNAL_RESEARCH_SKILLS_READY")
        self.assertEqual(state["summary"]["external_skill_packs_reviewed"], 8)
        self.assertEqual(state["summary"]["external_skill_packs_distilled"], 8)
        self.assertEqual(state["summary"]["external_skill_packs_left_catalogued"], 0)
        self.assertEqual(state["summary"]["external_runtime_dependencies"], 0)
        self.assertEqual(state["summary"]["canonical_internal_skills"], 7)
        self.assertEqual(validate_internal_skill_library(), [])
        self.assertTrue(all(row["decision"] == "DISTILLED" for row in EXTERNAL_SKILL_DISTILLATION))
        self.assertTrue(all(row["discarded"] for row in EXTERNAL_SKILL_DISTILLATION))

    def test_autoresearch_and_install_all_surfaces_are_not_internalized(self) -> None:
        ai_pack = next(row for row in EXTERNAL_SKILL_DISTILLATION if row["source_pack"] == "AI-Research-SKILLs")
        discarded = " ".join(ai_pack["discarded"]).lower()
        self.assertIn("autoresearch", discarded)
        self.assertIn("install-all", discarded)
        internal = str(CANONICAL_INTERNAL_SKILLS).lower()
        self.assertNotIn("continuous-loop authority", internal)
        ml = next(row for row in CANONICAL_INTERNAL_SKILLS if row["skill_id"] == "ai-ml-experiment-engineering")
        self.assertIn("become-autoresearch-orchestrator", ml["forbidden_actions"])

    def test_domain_skills_require_explicit_domain_capability(self) -> None:
        held = compile_internal_skill_job(
            "causal-empirical-analysis",
            {"capability_types": ["statistics"], "provided_inputs": ["target_estimand", "treatment_or_exposure", "outcome", "identification_assumptions", "data_provenance"]},
        )
        self.assertEqual(held["status"], "INTERNAL_SKILL_JOB_HOLD")
        self.assertIn("domain-skill-requires-explicit-capability:causal-inference", held["blockers"])
        ready = compile_internal_skill_job(
            "causal-empirical-analysis",
            {"capability_types": ["causal-inference", "statistics"], "provided_inputs": ["target_estimand", "treatment_or_exposure", "outcome", "identification_assumptions", "data_provenance"]},
        )
        self.assertEqual(ready["status"], "INTERNAL_SKILL_JOB_READY")
        self.assertFalse(ready["scientific_authority"])
        self.assertFalse(ready["experiment_authority"])

    def test_router_uses_minimal_domain_specific_local_skills(self) -> None:
        citation = route_internal_skills({"task_family": "citation-audit", "capability_types": ["citation", "literature"]})
        self.assertEqual(citation["status"], "INTERNAL_SKILL_ROUTE_READY")
        self.assertEqual([row["skill_id"] for row in citation["selected_skills"]], ["source-evidence-integrity"])
        ml = route_internal_skills({"task_family": "ai-ml-experiment", "capability_types": ["ml-research", "experiment", "coding"]})
        self.assertEqual(ml["status"], "INTERNAL_SKILL_ROUTE_READY")
        self.assertEqual([row["skill_id"] for row in ml["selected_skills"]], ["ai-ml-experiment-engineering"])
        self.assertEqual(ml["external_runtime_dependencies"], 0)

    def test_writer_surfaces_missing_inputs_and_cannot_change_scientific_truth(self) -> None:
        skill = next(row for row in CANONICAL_INTERNAL_SKILLS if row["skill_id"] == "evidence-first-manuscript")
        self.assertIn("missing-inputs-surfaced", skill["quality_gates"])
        self.assertIn("invent-data", skill["forbidden_actions"])
        self.assertIn("invent-reference", skill["forbidden_actions"])
        self.assertIn("edit-scientific-truth", skill["forbidden_actions"])
        job = compile_internal_skill_job(
            "evidence-first-manuscript",
            {"capability_types": ["writing"], "provided_inputs": ["frozen_claim_boundary", "paper_archetype_or_story_contract", "venue_constraints"]},
        )
        self.assertEqual(job["status"], "INTERNAL_SKILL_JOB_HOLD")
        self.assertIn("missing-skill-input:claim_evidence_graph", job["blockers"])


if __name__ == "__main__":
    unittest.main()
