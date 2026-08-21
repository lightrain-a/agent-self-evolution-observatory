from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from .api_memory_store import database_path
from .api_research_memory import (
    build_api_research_memory_state,
    lint_api_research_memory,
    record_raw_api_output,
)
from .api_research_memory_import import import_run


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
            self.assertTrue(
                state["graph_projection"]["candidates"][0][
                    "downstream_authorization_blocked"
                ]
            )
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


if __name__ == "__main__":
    unittest.main()
