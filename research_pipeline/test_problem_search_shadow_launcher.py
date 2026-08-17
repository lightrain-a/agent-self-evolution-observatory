from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_discovery_contract import DISCOVERY_OPERATOR_VERSION
from .paper_first_shadow_search_admission import build_shadow_search_admission, primary_content_sha256, source_set_sha256
from .problem_search_control_snapshot import validate_shadow_run_control
from .problem_search_shadow_launcher import HANDOFF_STATUS, NO_FRESH_TARGET_STATUS, prepare_shadow_run


class ProblemSearchShadowLauncherTest(unittest.TestCase):
    def canonical(self, *, latest: bool = False, changed: bool = False):
        anomaly_text="Reward improves from 0.50 to 0.63 at 32 tokens but plateaus at 64 tokens."
        records=[
            {"ref":"arXiv:2608.00001","source_sha256":"1"*64,"fulltext_sha256":"3"*64,"primary_source_verified":True,"abstract":"a","publication_date":"2026-08-14","empirical_facts":[{"text":anomaly_text}],"typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]}},
            {"ref":"arXiv:2608.00002","source_sha256":"2"*64,"fulltext_sha256":"4"*64,"primary_source_verified":True,"abstract":"b","publication_date":"2026-08-14","empirical_facts":[],"typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]}},
        ]
        generated_at="2026-08-14T00:00:00+00:00"
        tx="a"*64
        primary={"status":"READY","generated_at":generated_at,"discovery_transaction_id":tx,"records":records,"summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"carrier_probe_complete":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","discovery_transaction_id":tx,"summary":{"generated":0,"written_to_auto_inbox":0}}
        queue={"discovery_transaction_id":tx,"summary":{"submitted":0,"audited":0,"inbox_errors":0}}
        shadow={"scientific_authority":False,"policy":{"shadow_only":True}}
        if latest:
            latest_records=json.loads(json.dumps(records))
            if changed:
                latest_records[0]["fulltext_sha256"]="9"*64
            shadow.update({"latest_run_id":"shadow-old","latest_run":{"run_id":"shadow-old","status":"SHADOW_TERMINAL_COMPLETE","source_generated_at":"2026-08-13T00:00:00+00:00","source_set_sha256":source_set_sha256(latest_records),"source_primary_content_sha256":primary_content_sha256(latest_records),"source_pool_sha256":"b"*64,"discovery_operator_version":DISCOVERY_OPERATOR_VERSION,"scientific_authority":False}})
        admission=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        return records,generated_at,admission

    def fixture(self, root: Path, *, admission_latest: bool = False, admission_changed: bool = False):
        records,generated_at,admission=self.canonical(latest=admission_latest,changed=admission_changed)
        private_pool=root/"primary-evidence-pool.json"
        private_pool.write_text(json.dumps({"schema_version":"1.0","generated_at":generated_at,"records":records,"scientific_authority":False}),encoding="utf-8")
        memory=root/"memory.json"
        memory.write_text(json.dumps({"scientific_authority":False,"live_source_coverage_effect":False,"cannot_mutate_canonical_generator_or_queue":True,"blocked_objects":[]}),encoding="utf-8")
        project=root/"project";project.mkdir();(project/"a.py").write_text("A=1\n",encoding="utf-8");(project/"b.py").write_text("B=2\n",encoding="utf-8")
        return admission,private_pool,memory,project,("a.py","b.py")

    def test_ready_admission_freezes_private_pool_and_creates_qualification_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root);run=root/"shadow-new"
            self.assertEqual(admission["status"],"READY_FOR_SHADOW_QUALIFICATION")
            state=prepare_shadow_run(run_root=run,private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            frozen=json.loads((run/"frozen-primary-evidence-pool.json").read_text());frozen_memory=json.loads((run/"shadow-dead-end-memory.json").read_text());receipt=json.loads((run/"shadow-run-qualification.json").read_text())
            self.assertEqual(state["status"],HANDOFF_STATUS)
            self.assertTrue(state["summary"]["frozen_pool_created"]);self.assertTrue(state["summary"]["frozen_memory_created"]);self.assertTrue(state["summary"]["qualification_created"])
            self.assertEqual(state["summary"]["automatic_provider_calls_authorized"],0);self.assertEqual(state["summary"]["model_calls_executed"],0)
            self.assertTrue(state["summary"]["fresh_fallback_required"]);self.assertEqual(state["summary"]["fresh_phenomenon_target_count"],1)
            self.assertEqual(frozen["source_primary_content_sha256"],admission["source_identity"]["current_primary_content_sha256"])
            self.assertEqual(receipt["source_primary_content_sha256"],frozen["source_primary_content_sha256"])
            self.assertEqual(receipt["stage_runner_required_schema"],"1.4")
            self.assertFalse(frozen_memory["scientific_authority"]);self.assertFalse(frozen_memory["live_source_coverage_effect"]);self.assertTrue(frozen_memory["cannot_mutate_canonical_generator_or_queue"])
            source_memory=json.loads(memory.read_text());source_memory["blocked_objects"].append({"basin":"later-update","scientific_authority":False});memory.write_text(json.dumps(source_memory),encoding="utf-8")
            validated=validate_shadow_run_control(run_root=run,pool_path=run/"frozen-primary-evidence-pool.json",memory_path=run/"shadow-dead-end-memory.json",project_root=project,control_files=files)
            self.assertEqual(validated["memory_sha256"],receipt["memory_sha256"])
            with self.assertRaisesRegex(ValueError,"memory digest drift"):
                validate_shadow_run_control(run_root=run,pool_path=run/"frozen-primary-evidence-pool.json",memory_path=memory,project_root=project,control_files=files)
            self.assertFalse(state["scientific_authority"]);self.assertTrue(all(value is False for value in state["authority"].values()))

    def test_no_active_asset_and_all_fresh_anomalies_closed_holds_before_qualification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root);run=root/"shadow-no-target"
            pool=json.loads(private_pool.read_text());text=pool["records"][0]["empirical_facts"][0]["text"];sha=hashlib.sha256(" ".join(text.split()).encode()).hexdigest()
            memory_payload=json.loads(memory.read_text());memory_payload["blocked_objects"]=[{
                "source_candidate_id":"CLOSED-ANOMALY",
                "dead_end_certified":True,
                "scientific_authority":False,
                "fresh_phenomenon_closure":{"source_ref":"arXiv:2608.00001","closed_evidence_sha256":[sha],"scientific_authority":False},
            }];memory.write_text(json.dumps(memory_payload),encoding="utf-8")
            state=prepare_shadow_run(run_root=run,private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            self.assertFalse(run.exists())
        self.assertEqual(state["status"],NO_FRESH_TARGET_STATUS)
        self.assertTrue(state["summary"]["fresh_fallback_required"]);self.assertEqual(state["summary"]["fresh_phenomenon_target_count"],0)
        self.assertEqual(state["summary"]["model_calls_executed"],0);self.assertFalse(state["summary"]["qualification_created"])
        self.assertFalse(state["scientific_authority"]);self.assertTrue(all(value is False for value in state["authority"].values()))

    def test_same_source_terminal_skip_creates_no_run_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root,admission_latest=True,admission_changed=False);run=root/"shadow-duplicate"
            self.assertEqual(admission["status"],"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL")
            state=prepare_shadow_run(run_root=run,private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            self.assertFalse(run.exists())
        self.assertEqual(state["status"],"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL")
        self.assertFalse(state["summary"]["frozen_pool_created"]);self.assertFalse(state["summary"]["frozen_memory_created"]);self.assertFalse(state["summary"]["qualification_created"])
        self.assertEqual(state["summary"]["model_calls_executed"],0)

    def test_private_pool_identity_mismatch_holds_without_creating_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root);run=root/"shadow-mismatch"
            payload=json.loads(private_pool.read_text());payload["records"][0]["fulltext_sha256"]="f"*64;private_pool.write_text(json.dumps(payload),encoding="utf-8")
            state=prepare_shadow_run(run_root=run,private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            self.assertFalse(run.exists())
        self.assertEqual(state["status"],"HOLD_CANONICAL_PRIVATE_POOL_IDENTITY_MISMATCH")
        self.assertEqual(state["summary"]["model_calls_executed"],0)

    def test_missing_private_pool_or_memory_holds_without_model_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root)
            missing_pool=root/"missing-pool.json";run1=root/"shadow-no-pool"
            state1=prepare_shadow_run(run_root=run1,private_pool_path=missing_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            missing_memory=root/"missing-memory.json";run2=root/"shadow-no-memory"
            state2=prepare_shadow_run(run_root=run2,private_pool_path=private_pool,memory_path=missing_memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            self.assertFalse(run1.exists());self.assertFalse(run2.exists())
        self.assertEqual(state1["status"],"HOLD_CANONICAL_PRIVATE_POOL_UNAVAILABLE")
        self.assertEqual(state2["status"],"HOLD_SHADOW_MEMORY_UNAVAILABLE")
        self.assertEqual(state1["summary"]["model_calls_executed"],0);self.assertEqual(state2["summary"]["model_calls_executed"],0)

    def test_invalid_memory_holds_without_creating_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root);run=root/"shadow-invalid-memory"
            payload=json.loads(memory.read_text());payload["scientific_authority"]=True;memory.write_text(json.dumps(payload),encoding="utf-8")
            state=prepare_shadow_run(run_root=run,private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)
            self.assertFalse(run.exists())
        self.assertEqual(state["status"],"HOLD_SHADOW_MEMORY_INVALID")
        self.assertEqual(state["summary"]["model_calls_executed"],0)

    def test_nonshadow_run_name_is_rejected_before_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);admission,private_pool,memory,project,files=self.fixture(root)
            with self.assertRaisesRegex(ValueError,"must start with shadow-"):
                prepare_shadow_run(run_root=root/"run-x",private_pool_path=private_pool,memory_path=memory,project_root=project,admission_state=admission,require_clean_control=False,control_files=files)


if __name__=="__main__":
    unittest.main()
