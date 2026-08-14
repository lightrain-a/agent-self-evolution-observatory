from __future__ import annotations

import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

from .paper_first_legacy_reduction_migration import compile_legacy_reduction_migration,public_migration_summary,validate_public_migration


class LegacyReductionMigrationTest(unittest.TestCase):
    def test_terminal_parent_is_reaudited_without_mutation_and_only_pending_migrates(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run=root/"shadow-old";run.mkdir()
            pool={"records":[{"ref":"arXiv:2608.00001"}]}
            (run/"frozen-primary-evidence-pool.json").write_text(json.dumps(pool),encoding="utf-8")
            (run/"machine-audit.json").write_text(json.dumps({"summary":{"blocked":2}}),encoding="utf-8")
            (run/"shadow-terminal-current-source-gate.json").write_text(json.dumps({"status":"SHADOW_TERMINAL_COMPLETE"}),encoding="utf-8")
            (run/"formulate-p1.json").write_text(json.dumps({"part":1,"candidates":[{"candidate_id":"C1","exact_prediction":"p1","strongest_same_information_baseline":"b1","cheapest_problem_falsifier":"f1"},{"candidate_id":"C2","exact_prediction":"p2","strongest_same_information_baseline":"b2","cheapest_problem_falsifier":"f2"}]}),encoding="utf-8")
            before={p.name:p.read_bytes() for p in run.iterdir()}
            def normalize(raw,registry): return raw
            def audit(candidate,**kwargs):
                return {"passed":False,"blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"] if candidate["candidate_id"]=="C1" else ["domain-transfer-audit-incomplete"]}
            with patch("research_pipeline.paper_first_legacy_reduction_migration._normalize",side_effect=normalize),patch("research_pipeline.paper_first_legacy_reduction_migration.audit_shadow_problem_candidate",side_effect=audit),patch("research_pipeline.paper_first_legacy_reduction_migration._problem_falsifier_eligible",side_effect=lambda c,a:c["candidate_id"]=="C1"),patch("research_pipeline.paper_first_legacy_reduction_migration.compute_control_snapshot",return_value={"control_snapshot_sha256":"a"*64}):
                state=compile_legacy_reduction_migration(source_run=run,project_root=root)
            after={p.name:p.read_bytes() for p in run.iterdir()}
        self.assertEqual(before,after)
        self.assertEqual(state["status"],"LEGACY_REDUCTION_EVIDENCE_MIGRATION_READY")
        self.assertEqual((state["summary"]["source_formulated"],state["summary"]["current_reduction_pending"],state["summary"]["current_blocked"]),(2,1,1))
        self.assertEqual(state["summary"]["provisional_problem_candidates"],1)
        public=public_migration_summary(state)
        self.assertNotIn("machine_projection",public)
        self.assertNotIn("evidence_plan",public)
        self.assertEqual(validate_public_migration(public),[])
        self.assertFalse(public["authority"]["paper_design"])

    def test_parent_with_evidence_semantics_cannot_be_migrated_again(self):
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)/"shadow-new";run.mkdir()
            (run/"shadow-terminal-current-source-gate.json").write_text(json.dumps({"status":"SHADOW_TERMINAL_COMPLETE"}),encoding="utf-8")
            (run/"evidence-acquisition-plan.json").write_text("{}",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"legacy migration forbidden"):
                compile_legacy_reduction_migration(source_run=run)


if __name__=="__main__":unittest.main()
