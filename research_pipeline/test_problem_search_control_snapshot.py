from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .problem_search_control_snapshot import (
    STAGE_RUNNER_ARTIFACT_SCHEMA,
    build_shadow_run_qualification,
    compute_control_snapshot,
    validate_shadow_run_control,
    write_shadow_run_qualification,
)


class ProblemSearchControlSnapshotTest(unittest.TestCase):
    def fixture(self, root: Path):
        project=root/"project";project.mkdir()
        (project/"a.py").write_text("A=1\n",encoding="utf-8")
        (project/"b.py").write_text("B=2\n",encoding="utf-8")
        run=root/"shadow-test";run.mkdir()
        pool=run/"frozen-primary-evidence-pool.json"
        set_sha=hashlib.sha256("arXiv:2608.00001".encode()).hexdigest()
        pool.write_text(json.dumps({"generated_at":"2026-08-14T00:00:00+00:00","source_pool_sha256":"1"*64,"source_set_sha256":set_sha,"frozen_pool_sha256":"3"*64,"records":[{"ref":"arXiv:2608.00001","source_sha256":"4"*64,"fulltext_sha256":"5"*64}]}),encoding="utf-8")
        memory=run/"shadow-dead-end-memory.json"
        memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[{"basin":"semantic-lane-contract-x","scientific_authority":False}]}),encoding="utf-8")
        return project,run,pool,memory,("a.py","b.py")

    def test_snapshot_digest_changes_when_control_bytes_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,_,_,_,files=self.fixture(Path(td))
            first=compute_control_snapshot(project_root=project,control_files=files)
            (project/"a.py").write_text("A=9\n",encoding="utf-8")
            second=compute_control_snapshot(project_root=project,control_files=files)
        self.assertEqual(first["stage_runner_artifact_schema"],STAGE_RUNNER_ARTIFACT_SCHEMA)
        self.assertNotEqual(first["control_snapshot_sha256"],second["control_snapshot_sha256"])

    def test_qualification_binds_schema_control_pool_and_memory_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,run,pool,memory,files=self.fixture(Path(td))
            state=write_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)
            second=write_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)
        self.assertEqual(state,second)
        self.assertEqual(state["stage_runner_required_schema"],STAGE_RUNNER_ARTIFACT_SCHEMA)
        self.assertEqual(state["frozen_pool_sha256"],"3"*64)
        self.assertRegex(state["source_primary_content_sha256"],r"^[0-9a-f]{64}$")
        self.assertEqual(state["records"],1)
        self.assertEqual(state["dead_end_objects"],1)
        self.assertEqual(state["semantic_dead_ends"],1)
        self.assertRegex(state["control_snapshot_sha256"],r"^[0-9a-f]{64}$")
        self.assertFalse(state["scientific_authority"])
        self.assertTrue(state["policy"]["control_snapshot_drift_stops_before_provider_call"])

    def test_validation_fails_closed_on_control_pool_memory_or_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,run,pool,memory,files=self.fixture(Path(td))
            write_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)
            self.assertTrue(validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files))
            (project/"a.py").write_text("A=7\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"control snapshot drift"):
                validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files)
            (project/"a.py").write_text("A=1\n",encoding="utf-8")
            p=json.loads(pool.read_text());p["frozen_pool_sha256"]="4"*64;pool.write_text(json.dumps(p),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"frozen-pool digest drift"):
                validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files)
            p["frozen_pool_sha256"]="3"*64;pool.write_text(json.dumps(p),encoding="utf-8")
            receipt_path=run/"shadow-run-qualification.json";receipt=json.loads(receipt_path.read_text());original_content=receipt["source_primary_content_sha256"];receipt["source_primary_content_sha256"]="6"*64;receipt_path.write_text(json.dumps(receipt),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"source identity drift detected:source_primary_content_sha256"):
                validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files)
            receipt["source_primary_content_sha256"]=original_content;receipt_path.write_text(json.dumps(receipt),encoding="utf-8")
            m=json.loads(memory.read_text());m["blocked_objects"].append({"basin":"x"});memory.write_text(json.dumps(m),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"memory digest drift"):
                validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files)
            m["blocked_objects"].pop();memory.write_text(json.dumps(m),encoding="utf-8")
            receipt=json.loads((run/"shadow-run-qualification.json").read_text());receipt["stage_runner_required_schema"]="1.3";(run/"shadow-run-qualification.json").write_text(json.dumps(receipt),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"stage-runner schema drift"):
                validate_shadow_run_control(run_root=run,pool_path=pool,memory_path=memory,project_root=project,control_files=files)

    def test_qualification_rejects_source_set_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,run,pool,memory,files=self.fixture(Path(td))
            payload=json.loads(pool.read_text());payload["source_set_sha256"]="2"*64;pool.write_text(json.dumps(payload),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"source-set digest mismatch"):
                build_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)

    def test_qualification_rejects_invalid_primary_content_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,run,pool,memory,files=self.fixture(Path(td))
            payload=json.loads(pool.read_text());payload["records"][0]["source_sha256"]="bad";pool.write_text(json.dumps(payload),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"primary-content digest invalid"):
                build_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)

    def test_shadow_run_requires_receipt_but_legacy_nonshadow_test_root_can_be_unqualified(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            shadow=root/"shadow-new";shadow.mkdir()
            with self.assertRaisesRegex(ValueError,"qualified shadow run receipt"):
                validate_shadow_run_control(run_root=shadow,project_root=root,control_files=())
            legacy=root/"run";legacy.mkdir()
            self.assertEqual(validate_shadow_run_control(run_root=legacy,project_root=root,control_files=()),{})

    def test_qualification_refuses_existing_scientific_stage_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project,run,pool,memory,files=self.fixture(Path(td))
            (run/"expand-CONTRADICTION-p1.json").write_text("{}",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"before any expansion"):
                build_shadow_run_qualification(run_root=run,pool_path=pool,memory_path=memory,project_root=project,require_clean_control=False,control_files=files)


if __name__=="__main__":
    unittest.main()
