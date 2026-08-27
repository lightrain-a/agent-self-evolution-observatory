from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_support_release_watch import release_watch_contract_sha
from .paper_first_support_asset_recheck import (
    build_support_asset_recheck_queue,
    public_support_asset_recheck_summary,
    validate_support_asset_resolution_state,
    write_private_support_asset_recheck_queue,
    write_private_support_asset_resolutions,
)


class SupportAssetRecheckQueueTest(unittest.TestCase):
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

    def design(self, candidate_id: str = "C1") -> dict:
        return {
            "shadow_dead_end_memory": {
                "scientific_authority": False,
                "blocked_objects": [{
                    "source_candidate_id": candidate_id,
                    "basin": "near-miss-terminal-support-hold-deadbeef",
                    "disposition": "HOLD_SUPPORT_UNAVAILABLE",
                    "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
                    "required_unit": "matched released trajectory units",
                    "reopen_only_if": "The authors release the matched units.",
                    "strongest_reduction": "generic partial identification",
                    "evidence_basis": ["arXiv:2608.00001"],
                    "source_run_id": "shadow-r1",
                    "source_stage_manifest_sha256": "a" * 64,
                    "scientific_authority": False,
                }],
            },
            "scientific_authority": False,
        }

    def watch(self, status: str = "RECHECK_REQUIRED_RELEASE_CHANGED") -> dict:
        return {
            "schema_version": "1.0",
            "status": "SUPPORT_RELEASE_WATCH_COMPLETE",
            "rows": [{
                "candidate_id": "C1",
                "status": status,
                "declaration_kind": "PROJECT_PAGE",
                "url": "https://lab.github.io/project/",
                "fingerprint": "b" * 64,
                "scientific_authority": False,
            }],
            "scientific_authority": False,
        }

    def test_split_hold_memory_routes_reused_candidate_id_by_source_ref(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            first = self.design("C1")["shadow_dead_end_memory"]["blocked_objects"][0]
            first = {**first, "source_run_id": "shadow-r1", "dead_end_certified": False, "memory_class": "REOPENABLE_HOLD"}
            second = {**first, "source_run_id": "shadow-r2", "basin": "near-miss-terminal-support-hold-cafebabe", "evidence_basis": ["arXiv:2608.00002"], "required_unit": "second matched released unit"}
            design = {"shadow_dead_end_memory": {"scientific_authority": False, "blocked_objects": [], "hold_objects": [first, second]}, "scientific_authority": False}
            watch = self.watch(); watch["rows"][0]["source_ref"] = "arXiv:2608.00002"
            state = build_support_asset_recheck_queue(storage=storage, watch_state=watch, design_state=design, previous_state={}, now=datetime(2026, 8, 14, tzinfo=timezone.utc))
        self.assertEqual(state["summary"]["support_holds"], 2)
        self.assertEqual(state["summary"]["queued"], 1)
        row = state["entries"][0]
        self.assertEqual(row["candidate_id"], "C1")
        self.assertEqual(row["source_run_id"], "shadow-r2")
        self.assertEqual(row["source_refs"], ["arXiv:2608.00002"])
        self.assertEqual(row["required_unit"], "second matched released unit")
        self.assertEqual(len(row["support_hold_key"]), 64)

    def test_fresh_phenomenon_support_hold_routes_release_change_to_recheck(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            hold = self.design("FRESH-C1")["shadow_dead_end_memory"]["blocked_objects"][0]
            hold = {
                **hold,
                "basin": "fresh-phenomenon-support-hold-deadbeef",
                "memory_class": "REOPENABLE_HOLD",
                "dead_end_certified": False,
                "evidence_basis": ["arXiv:2607.00001"],
            }
            design = {"shadow_dead_end_memory": {"scientific_authority": False, "blocked_objects": [], "hold_objects": [hold]}, "scientific_authority": False}
            watch = self.watch(); watch["rows"][0].update({"candidate_id": "FRESH-C1", "source_ref": "arXiv:2607.00001"})
            state = build_support_asset_recheck_queue(storage=storage, watch_state=watch, design_state=design, previous_state={}, now=datetime(2026, 8, 14, tzinfo=timezone.utc))
        self.assertEqual(state["summary"]["support_holds"], 1)
        self.assertEqual(state["summary"]["queued"], 1)
        self.assertEqual(state["entries"][0]["candidate_id"], "FRESH-C1")
        self.assertEqual(state["entries"][0]["source_refs"], ["arXiv:2607.00001"])
        self.assertFalse(state["entries"][0]["scientific_authority"])

    def test_effective_pre_f0_hold_release_change_routes_to_same_asset_recheck_queue(self) -> None:
        baseline="1"*40;snapshot="3"*64
        target={"source_ref":"arXiv:2608.15265","url":"https://github.com/usail-hkust/VibeWorlding-Gym","declaration_kind":"FIRST_PARTY_REPOSITORY","baseline_revision":baseline,"scientific_authority":False}
        contract_sha=release_watch_contract_sha(candidate_id="PORT-010",candidate_snapshot_sha256=snapshot,targets=[target],required_reopen_components=["query_units","per_case_outcomes"])
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));storage.site_artifact_dir.mkdir(parents=True,exist_ok=True)
            preflight={"schema_version":"1.0","run_id":"pre-f0-vwe","support_inventory_sha256":"a"*64,"scientific_authority":False,"authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},"rows":[{
                "candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,"disposition":"HOLD_SUPPORT_UNAVAILABLE","scientific_authority":False,
                "primary_refs":["arXiv:2608.15265"],"required_unit":"VWE query units plus per-case target-model outcomes.","reopen_only_if":"Both frozen release components exist.",
                "bounded_first_party_evidence_design_allowed":True,"next_route":"BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET",
            }]}
            evidence={"scientific_authority":False,"entries":[{"candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,"status":"HOLD_EVIDENCE_REVIEW_BLOCKED","execution_authorized":False,"scientific_authority":False,"release_watch_contract":{
                "candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,"targets":[target],"required_reopen_components":["query_units","per_case_outcomes"],"contract_sha256":contract_sha,"scientific_authority":False,
            }}]}
            (storage.site_artifact_dir/"paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight),encoding="utf-8")
            (storage.site_artifact_dir/"paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence),encoding="utf-8")
            watch={"rows":[{"candidate_id":"PORT-010","source_ref":"arXiv:2608.15265","url":target["url"],"declaration_kind":"FIRST_PARTY_REPOSITORY","fingerprint":"5"*64,"status":"RECHECK_REQUIRED_RELEASE_CHANGED","scientific_authority":False}],"scientific_authority":False}
            state=build_support_asset_recheck_queue(storage=storage,watch_state=watch,design_state={"scientific_authority":False},previous_state={},now=datetime(2026,8,27,tzinfo=timezone.utc))
            digest=state["entries"][0]["latest_trigger_digest"]
            resolution={"schema_version":"1.0","status":"SUPPORT_ASSET_RESOLUTIONS_RECORDED","scientific_authority":False,"resolutions":[{"candidate_id":"PORT-010","resolved_trigger_digest":digest,"disposition":"RECHECKED_RELEASE_IRRELEVANT","resolution_reason":"The changed source revision contains license/notice changes only and no frozen outcome component.","support_inventory_reaudit_required":False,"support_qualified":False,"generator_reopen_authorized":False,"problem_gate_authorized":False,"scientific_authority":False}]}
            cleared=build_support_asset_recheck_queue(storage=storage,watch_state={"rows":[],"scientific_authority":False},design_state={"scientific_authority":False},previous_state=state,resolution_state=resolution,now=datetime(2026,8,27,tzinfo=timezone.utc))
        self.assertEqual(state["status"],"SUPPORT_ASSET_RECHECK_QUEUE_READY");self.assertEqual(state["summary"]["queued"],1)
        self.assertEqual(state["entries"][0]["candidate_id"],"PORT-010");self.assertFalse(state["entries"][0]["scientific_authority"])
        self.assertEqual(cleared["status"],"SUPPORT_ASSET_RECHECK_QUEUE_EMPTY")
        self.assertEqual(cleared["summary"]["resolution_irrelevant_release"],1)
        self.assertEqual(cleared["summary"]["support_qualified"],0)

    def test_release_change_creates_zero_authority_asset_recheck_task(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = build_support_asset_recheck_queue(
                storage=self.storage(Path(td)), watch_state=self.watch(), design_state=self.design(), previous_state={},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
            )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_QUEUE_READY")
        self.assertEqual((state["summary"]["queued"], state["summary"]["new_triggers"]), (1, 1))
        row = state["entries"][0]
        self.assertEqual(row["queue_status"], "AWAIT_ASSET_RECHECK")
        self.assertEqual(row["source_refs"], ["arXiv:2608.00001"])
        self.assertEqual(row["required_unit"], "matched released trajectory units")
        self.assertIn("first-party reconstruction", row["recheck_instruction"])
        self.assertTrue(state["policy"]["support_inventory_recheck_considers_direct_or_reconstructed_truth"])
        self.assertTrue(state["policy"]["reconstruction_requires_materialized_units_and_provenance"])
        for key in ("support_qualified", "generator_reopen_authorized", "problem_gate_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized", "scientific_authority"):
            self.assertFalse(row[key])

    def test_unresolved_task_survives_watcher_cooldown(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td)); now = datetime(2026, 8, 14, tzinfo=timezone.utc)
            first = build_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), previous_state={}, now=now)
            cooldown = self.watch("SKIPPED_COOLDOWN")
            cooldown["rows"][0]["previous_status"] = "RECHECK_REQUIRED_RELEASE_CHANGED"
            second = build_support_asset_recheck_queue(storage=storage, watch_state=cooldown, design_state=self.design(), previous_state=first, now=now)
        self.assertEqual(second["summary"]["queued"], 1)
        self.assertEqual(second["summary"]["new_triggers"], 0)
        self.assertEqual(second["summary"]["carried_forward"], 1)
        self.assertEqual(second["entries"][0]["queue_id"], first["entries"][0]["queue_id"])
        self.assertEqual(second["entries"][0]["latest_trigger_digest"], first["entries"][0]["latest_trigger_digest"])

    def test_matching_explicit_resolution_clears_only_the_resolved_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));now=datetime(2026,8,14,tzinfo=timezone.utc)
            first=build_support_asset_recheck_queue(storage=storage,watch_state=self.watch(),design_state=self.design(),previous_state={},now=now)
            digest=first["entries"][0]["latest_trigger_digest"]
            resolution={"schema_version":"1.0","status":"SUPPORT_ASSET_RESOLUTIONS_RECORDED","scientific_authority":False,"resolutions":[{"candidate_id":"C1","resolved_trigger_digest":digest,"disposition":"RECHECKED_SUPPORT_STILL_UNAVAILABLE","resolution_reason":"The changed release still does not expose the frozen matched trajectory unit.","support_inventory_reaudit_required":False,"support_qualified":False,"generator_reopen_authorized":False,"problem_gate_authorized":False,"scientific_authority":False}]}
            self.assertEqual(validate_support_asset_resolution_state(resolution),[])
            cleared=build_support_asset_recheck_queue(storage=storage,watch_state={"rows":[],"scientific_authority":False},design_state=self.design(),previous_state=first,resolution_state=resolution,now=now)
            changed=self.watch();changed["rows"][0]["fingerprint"]="c"*64
            reopened=build_support_asset_recheck_queue(storage=storage,watch_state=changed,design_state=self.design(),previous_state=first,resolution_state=resolution,now=now)
        self.assertEqual(cleared["status"],"SUPPORT_ASSET_RECHECK_QUEUE_EMPTY")
        self.assertEqual((cleared["summary"]["queued"],cleared["summary"]["resolved"],cleared["summary"]["resolution_still_unavailable"]),(0,1,1))
        self.assertEqual(reopened["status"],"SUPPORT_ASSET_RECHECK_QUEUE_READY")
        self.assertEqual((reopened["summary"]["queued"],reopened["summary"]["new_triggers"],reopened["summary"]["resolved"]),(1,1,0))
        self.assertNotEqual(reopened["entries"][0]["latest_trigger_digest"],digest)

    def test_support_inventory_recheck_is_not_a_resolution_disposition(self) -> None:
        resolution={"schema_version":"1.0","status":"SUPPORT_ASSET_RESOLUTIONS_RECORDED","scientific_authority":False,"resolutions":[{"candidate_id":"C1","resolved_trigger_digest":"d"*64,"disposition":"SUPPORT_INVENTORY_REAUDIT_READY","resolution_reason":"This must stay in the queue-to-handoff path rather than clearing the durable task.","support_inventory_reaudit_required":True,"support_qualified":False,"generator_reopen_authorized":False,"problem_gate_authorized":False,"scientific_authority":False}]}
        self.assertTrue(any("disposition invalid" in error for error in validate_support_asset_resolution_state(resolution)))
        private=build_support_asset_recheck_queue(storage=self.storage(Path('/tmp/unused-support-handoff-policy')),watch_state=self.watch(),design_state=self.design(),previous_state={},now=datetime(2026,8,14,tzinfo=timezone.utc))
        self.assertTrue(private["policy"]["support_inventory_recheck_remains_queue_handoff_not_resolution"])
        self.assertEqual(private["summary"]["support_qualified"],0)

    def test_resolution_writer_requires_bound_trigger_and_zero_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));path=storage.data_root/"paper-first-problem-discovery"/"support-release-watch"/"asset-recheck-resolutions.json"
            row={"candidate_id":"C1","resolved_trigger_digest":"d"*64,"disposition":"RECHECKED_RELEASE_IRRELEVANT","resolution_reason":"The release changed documentation/tooling only and does not contain the frozen required unit.","support_inventory_reaudit_required":False,"support_qualified":False,"generator_reopen_authorized":False,"problem_gate_authorized":False,"scientific_authority":False}
            state=write_private_support_asset_resolutions([row],storage=storage,path=path)
            self.assertTrue(path.exists())
            self.assertEqual(validate_support_asset_resolution_state(state),[])
            broken=dict(row);broken["support_qualified"]=True
            with self.assertRaisesRegex(ValueError,"cannot qualify support"):
                write_private_support_asset_resolutions([broken],storage=storage,path=path)

    def test_non_recheck_watch_state_does_not_create_task(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = build_support_asset_recheck_queue(
                storage=self.storage(Path(td)), watch_state=self.watch("BASELINE_CAPTURED"), design_state=self.design(), previous_state={},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
            )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_QUEUE_EMPTY")
        self.assertEqual(state["entries"], [])
        self.assertEqual(state["summary"]["queued"], 0)

    def test_task_is_not_carried_when_candidate_is_no_longer_current_support_hold(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td)); now = datetime(2026, 8, 14, tzinfo=timezone.utc)
            first = build_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), previous_state={}, now=now)
            resolved_design = {"shadow_dead_end_memory": {"blocked_objects": [], "scientific_authority": False}, "scientific_authority": False}
            second = build_support_asset_recheck_queue(storage=storage, watch_state={"rows": [], "scientific_authority": False}, design_state=resolved_design, previous_state=first, now=now)
        self.assertEqual(second["entries"], [])
        self.assertEqual(second["summary"]["support_holds"], 0)

    def test_public_summary_exposes_counts_not_private_queue_entries(self) -> None:
        private = build_support_asset_recheck_queue(
            storage=self.storage(Path('/tmp/unused-support-recheck-test')),
            watch_state=self.watch(), design_state=self.design(), previous_state={}, now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        public = public_support_asset_recheck_summary(private)
        text = str(public)
        self.assertEqual(public["summary"]["queued"], 1)
        self.assertFalse(public["scientific_authority"])
        self.assertNotIn("entries", public)
        for marker in ("arXiv:2608.00001", "github.io", "matched released trajectory units", "C1"):
            self.assertNotIn(marker, text)

    def test_private_writer_persists_empty_or_ready_queue_only_under_private_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            state = write_private_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), now=datetime(2026, 8, 14, tzinfo=timezone.utc))
            path = storage.data_root / "paper-first-problem-discovery" / "support-release-watch" / "asset-recheck-queue.json"
            self.assertTrue(path.exists())
            self.assertEqual(state["summary"]["queued"], 1)
            self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
