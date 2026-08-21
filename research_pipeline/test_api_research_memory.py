from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from .api_memory_ablation import build_api_memory_ablation_plan
from .api_memory_store import database_path
from .api_research_memory import (
    build_api_research_memory_state,
    compile_api_memory_query_pack,
    invalidate_query_only_memory_run,
    lint_api_research_memory,
    record_api_memory_consumption,
    record_parsed_api_output,
    record_raw_api_output,
)
from .api_research_memory_import import import_run, object_rows


class ApiResearchMemoryTest(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def fixture(self, root: Path) -> Path:
        run = root / "source" / "shadow-test-r1"
        raw_root = run / "raw"
        raw_root.mkdir(parents=True)
        raw_a = '{"seeds":[{"seed_id":"S1","title":"seed"}]}'
        raw_b = '{"candidates":[{"candidate_id":"C1","title":"candidate"}]}'
        sha_a = hashlib.sha256(raw_a.encode()).hexdigest()
        sha_b = hashlib.sha256(raw_b.encode()).hexdigest()
        (raw_root / f"expand-CONTRADICTION-p1-{sha_a[:12]}.txt").write_text(
            raw_a, encoding="utf-8"
        )
        (raw_root / f"formulate-p1-{sha_b[:12]}.txt").write_text(
            raw_b, encoding="utf-8"
        )
        self.write_json(
            run / "expand-CONTRADICTION-p1.json",
            {
                "schema_version": "1.5",
                "lane": "CONTRADICTION",
                "part": 1,
                "requested_model": "model-a",
                "resolved_model": "model-a-v1",
                "raw_sha256": sha_a,
                "raw_archived_before_parse": True,
                "transport_attempts": [
                    {
                        "request_fingerprint": "a" * 64,
                        "prompt_sha256": "b" * 64,
                        "requested_model": "model-a",
                        "resolved_model": "model-a-v1",
                    }
                ],
                "seeds": [{"seed_id": "S1", "title": "seed"}],
                "scientific_authority": False,
            },
        )
        self.write_json(
            run / "formulate-p1.json",
            {
                "schema_version": "1.5",
                "part": 1,
                "requested_model": "model-b",
                "resolved_model": "model-b-v1",
                "raw_sha256": sha_b,
                "raw_archived_before_parse": True,
                "transport_attempts": [
                    {
                        "request_fingerprint": "c" * 64,
                        "prompt_sha256": "d" * 64,
                    }
                ],
                "candidates": [
                    {
                        "candidate_id": "C1",
                        "source_branch_id": "S1",
                        "title": "candidate",
                    }
                ],
                "reduction_pending": [],
                "rejected": [],
                "scientific_authority": False,
            },
        )
        self.write_json(
            run / "base.json",
            {
                "unique_seeds": [
                    {"seed_id": "S1", "title": "seed", "scientific_authority": False}
                ],
                "scientific_authority": False,
            },
        )
        self.write_json(
            run / "evidence-substrate-preflight-request.json",
            {
                "rows": [
                    {
                        "candidate_id": "C1",
                        "title": "candidate",
                        "reproduction_target": "bounded substrate only",
                        "scientific_authority": False,
                    }
                ],
                "scientific_authority": False,
            },
        )
        self.write_json(
            run / "api-collision-execution-manifest.json",
            {
                "schema_version": "1.0",
                "run_id": "shadow-test-r1",
                "transaction_kind": "shadow_parallel_search",
                "qualification_status": "READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT",
                "control_snapshot_sha256": "e" * 64,
                "frozen_pool_sha256": "f" * 64,
                "artifact_set_sha256": "1" * 64,
                "execution": {"total_logical_provider_attempts": 2},
                "search_funnel": {"preflight_candidates": 1},
                "scientific_authority": False,
            },
        )
        return run

    def test_import_is_durable_idempotent_and_zero_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = self.fixture(root)
            first = import_run(run, root=root / "persistent")
            second = import_run(run, root=root / "persistent")
            self.assertEqual(first["raw_calls"], 2)
            self.assertEqual(second["raw_calls"], 2)
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["status"], "API_RESEARCH_MEMORY_READY")
            self.assertEqual(state["summary"]["runs"], 1)
            self.assertEqual(state["summary"]["calls"], 2)
            self.assertEqual(state["summary"]["preflight_candidates"], 1)
            self.assertFalse(state["scientific_authority"])
            projected = state["graph_projection"]["candidates"][0]
            self.assertTrue(projected["downstream_authorization_blocked"])
            self.assertTrue(projected["candidate_id"].startswith("API::shadow-test-r1::"))
            self.assertEqual(len(projected["scientific_object_signature"]), 64)
            self.assertEqual(
                lint_api_research_memory(root=root / "persistent")["status"], "PASS"
            )
            with sqlite3.connect(database_path(root=root / "persistent")) as db:
                calls = db.execute(
                    "SELECT COUNT(*),SUM(scientific_authority),SUM(belief_authority) FROM api_calls"
                ).fetchone()
                self.assertEqual(calls, (2, 0, 0))

    def test_same_run_changed_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = self.fixture(root)
            import_run(run, root=root / "persistent")
            manifest = json.loads(
                (run / "api-collision-execution-manifest.json").read_text()
            )
            manifest["artifact_set_sha256"] = "2" * 64
            self.write_json(run / "api-collision-execution-manifest.json", manifest)
            with self.assertRaisesRegex(RuntimeError, "manifest conflict"):
                import_run(run, root=root / "persistent")

    def test_raw_output_is_archived_before_parse(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "scratch" / "incremental-r1"
            raw = run / "raw" / "expand-p1.txt"
            raw.parent.mkdir(parents=True)
            raw.write_text("unparsed provider bytes", encoding="utf-8")
            receipt = record_raw_api_output(
                run_root=run,
                stage="expand-CONTRADICTION-p1",
                raw_path=raw,
                resolved_model="model-v1",
                requested_model="model",
                request_fingerprint="a" * 64,
                prompt_sha256="b" * 64,
                root=root / "persistent",
            )
            self.assertEqual(receipt["status"], "RAW_ARCHIVED")
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["summary"]["calls"], 1)
            self.assertEqual(state["summary"]["artifacts"], 1)
            self.assertEqual(state["summary"]["fully_replay_addressed_calls"], 1)
            self.assertFalse(state["scientific_authority"])

    def test_successful_parse_is_persisted_immediately_with_zero_authority_object(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "scratch" / "incremental-r1"
            raw = run / "raw" / "review-p1.txt"
            raw.parent.mkdir(parents=True)
            raw.write_text('{"reviews":[{"candidate_id":"C1","verdict":"CLEAR"}]}', encoding="utf-8")
            archived = record_raw_api_output(
                run_root=run,
                stage="evidence-review-p1",
                raw_path=raw,
                resolved_model="reviewer-v1",
                requested_model="reviewer",
                request_fingerprint="a" * 64,
                prompt_sha256="b" * 64,
                root=root / "persistent",
            )
            parsed = record_parsed_api_output(
                run_root=run,
                stage="evidence-review-p1",
                raw_sha256=archived["raw_sha256"],
                structured_payload={"reviews": [{"candidate_id": "C1", "verdict": "CLEAR"}]},
                resolved_model="reviewer-v1",
                requested_model="reviewer",
                research_objects=[{
                    "object_type": "evidence_review",
                    "object_id": "C1::contract",
                    "stage": "independent_evidence_review",
                    "title": "candidate review",
                    "disposition": "CLEAR",
                    "payload": {"candidate_id": "C1", "frozen_exact_prediction": "p", "evidence_review": {"verdict": "CLEAR"}},
                }],
                root=root / "persistent",
            )
            self.assertEqual(parsed["status"], "PARSED_OUTPUT_PERSISTED")
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["summary"]["calls"], 1)
            self.assertEqual(state["summary"]["artifacts"], 1)
            self.assertEqual(state["summary"]["research_objects"], 1)
            self.assertEqual(state["summary"]["scientific_identities"], 1)
            with sqlite3.connect(database_path(root=root / "persistent")) as db:
                row = db.execute("SELECT outcome_status,parse_status,structured_sha256 FROM api_calls").fetchone()
                roles = {value[0] for value in db.execute("SELECT role FROM run_artifacts")}
            self.assertEqual(row[0:2], ("SUCCESS", "PARSED"))
            self.assertEqual(len(row[2]), 64)
            self.assertEqual(roles, {"raw_api_output", "parsed_api_output"})
            self.assertEqual(lint_api_research_memory(root=root / "persistent")["status"], "PASS")

    def test_completed_import_accepts_exact_incremental_object_writeback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = self.fixture(root)
            first = object_rows(run)[0]
            raw_path = next((run / "raw").glob("*.txt"))
            archived = record_raw_api_output(
                run_root=run,
                stage="incremental-object-probe",
                raw_path=raw_path,
                root=root / "persistent",
            )
            record_parsed_api_output(
                run_root=run,
                stage="incremental-object-probe",
                raw_sha256=archived["raw_sha256"],
                structured_payload={"probe": True},
                research_objects=[first],
                root=root / "persistent",
            )
            imported = import_run(run, root=root / "persistent")
            self.assertEqual(imported["status"], "API_RESEARCH_RUN_IMPORTED")
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["summary"]["research_objects"], len(object_rows(run)))
            self.assertEqual(state["summary"]["scientific_identities"], len(object_rows(run)))
            self.assertEqual(lint_api_research_memory(root=root / "persistent")["status"], "PASS")

    def test_cross_run_exact_contract_identity_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_a = self.fixture(root)
            import_run(run_a, root=root / "persistent")
            run_b = root / "source" / "shadow-test-r2"
            shutil.copytree(run_a, run_b)
            manifest_path = run_b / "api-collision-execution-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["run_id"] = "shadow-test-r2"
            self.write_json(manifest_path, manifest)
            import_run(run_b, root=root / "persistent")
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(
                state["summary"]["scientific_identities"],
                state["summary"]["research_objects"],
            )
            with sqlite3.connect(database_path(root=root / "persistent")) as db:
                signatures = db.execute(
                    """
                    SELECT i.scientific_signature
                    FROM research_objects o
                    JOIN scientific_identities i ON i.object_key=o.object_key
                    WHERE o.object_type='candidate' AND o.object_id='C1'
                    ORDER BY o.run_id
                    """
                ).fetchall()
            self.assertEqual(len(signatures), 2)
            self.assertEqual(signatures[0][0], signatures[1][0])

    def test_retrieval_variants_and_consumption_are_zero_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = self.fixture(root)
            import_run(run, root=root / "persistent")
            kwargs = {
                "purpose": "FORMULATION",
                "context": {
                    "title": "candidate bounded substrate",
                    "goal": "reproduce candidate with independent truth",
                },
                "run_id": "shadow-test-r2",
                "stage": "formulate-p1",
                "max_items": 4,
                "max_chars": 2200,
                "root": root / "persistent",
            }
            relevant = compile_api_memory_query_pack(variant="relevant", **kwargs)
            random = compile_api_memory_query_pack(variant="random", **kwargs)
            none = compile_api_memory_query_pack(variant="none", **kwargs)
            self.assertEqual(relevant["status"], "API_MEMORY_QUERY_COMPILED")
            self.assertGreater(relevant["summary"]["selected"], 0)
            self.assertTrue(relevant["query_id"])
            self.assertTrue(relevant["memory_instance_id"].startswith("api-memory-"))
            self.assertEqual(
                relevant["summary"]["available"], random["summary"]["available"]
            )
            self.assertEqual(none["summary"]["selected"], 0)
            self.assertFalse(relevant["scientific_authority"])
            receipt = record_api_memory_consumption(
                run_id="shadow-test-r2",
                stage="formulate-p1",
                pack=relevant,
                raw_sha256="a" * 64,
                output_object_ids=["C2"],
                outcome_status="FORMULATION_COMPILED",
                root=root / "persistent",
            )
            self.assertEqual(receipt["status"], "API_MEMORY_CONSUMPTION_RECORDED")
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["summary"]["memory_queries"], 3)
            self.assertEqual(state["summary"]["memory_consumptions"], 1)
            self.assertEqual(
                lint_api_research_memory(root=root / "persistent")["status"], "PASS"
            )

    def test_disabled_noncanonical_query_never_touches_existing_memory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            import_run(self.fixture(root), root=root / "persistent")
            before = build_api_research_memory_state(root=root / "persistent")
            pack = compile_api_memory_query_pack(
                purpose="IDEA_DISCOVERY",
                context={"lane": "CONTRADICTION"},
                run_id="scratch-run",
                stage="expand-CONTRADICTION-p1",
                enabled=False,
                root=root / "persistent",
            )
            after = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(pack["status"], "API_MEMORY_DISABLED_NONCANONICAL")
            self.assertEqual(pack["summary"]["selected"], 0)
            self.assertEqual(before["summary"]["raw_runs"], after["summary"]["raw_runs"])
            self.assertEqual(before["summary"]["raw_memory_queries"], after["summary"]["raw_memory_queries"])

    def test_query_only_development_stub_is_invalidated_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            import_run(self.fixture(root), root=root / "persistent")
            compile_api_memory_query_pack(
                purpose="FORMULATION",
                context={"candidate": "test"},
                run_id="scratch-query-only",
                stage="formulate-p1",
                root=root / "persistent",
            )
            before = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(before["summary"]["runs"], 2)
            receipt = invalidate_query_only_memory_run(
                run_id="scratch-query-only",
                reason="development test contamination",
                root=root / "persistent",
            )
            self.assertEqual(receipt["status"], "QUERY_ONLY_RUN_INVALIDATED")
            after = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(after["summary"]["runs"], 1)
            self.assertEqual(after["summary"]["raw_runs"], 2)
            self.assertEqual(after["summary"]["invalidated_runs"], 1)
            self.assertEqual(after["summary"]["memory_queries"], 0)
            self.assertEqual(after["summary"]["raw_memory_queries"], 1)
            self.assertEqual(lint_api_research_memory(root=root / "persistent")["status"], "PASS")

    def test_required_canonical_memory_missing_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "missing"
            with self.assertRaisesRegex(RuntimeError, "canonical API research memory missing"):
                compile_api_memory_query_pack(
                    purpose="IDEA_DISCOVERY",
                    context={"lane": "CONTRADICTION"},
                    run_id="shadow-test-r2",
                    stage="expand-CONTRADICTION-p1",
                    required=True,
                    root=root,
                )

    def test_ablation_plan_freezes_three_zero_authority_arms(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            import_run(self.fixture(root), root=root / "persistent")
            plan = build_api_memory_ablation_plan(
                purpose="IDEA_DISCOVERY",
                context={"topic": "candidate memory retrieval"},
                run_id_prefix="ablation-r1",
                stage="expand-CONTRADICTION-p1",
                max_items=3,
                max_chars=1600,
                root=root / "persistent",
            )
            self.assertEqual(plan["status"], "API_MEMORY_ABLATION_READY")
            self.assertEqual(set(plan["arms"]), {"relevant", "random", "none"})
            self.assertTrue(all(plan["invariants"].values()))
            self.assertEqual(plan["arms"]["none"]["summary"]["selected"], 0)
            self.assertEqual(plan["arms"]["relevant"]["summary"]["selected"], plan["arms"]["random"]["summary"]["selected"])
            self.assertIn("NOT_TOKEN_MATCHED", plan["comparison_semantics"]["relevant_vs_none"])
            self.assertFalse(plan["scientific_authority"])
            state = build_api_research_memory_state(root=root / "persistent")
            self.assertEqual(state["summary"]["runs"], 1)
            self.assertEqual(state["summary"]["memory_queries"], 0)


if __name__ == "__main__":
    unittest.main()
