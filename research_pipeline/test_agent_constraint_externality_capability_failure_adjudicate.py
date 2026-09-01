from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_capability_failure_adjudicate import (
    FAILURE_CLASSIFICATION,
    VERDICT,
    build_failure_adjudication,
    write_failure_artifacts,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    DEFAULT_BASE_URL,
    OBJECT_ID,
    PROVIDER_ID,
    AppendOnlyLedger,
    EpisodeUnit,
    ProviderReceipt,
    RunnerError,
    sha256_file,
)


class CapabilityFailureAdjudicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.ledger_path = self.root / "capability-ledger.jsonl"
        self.snapshot_path = self.root / "snapshot.json"
        self.source_db_path = self.root / "source-gmail.db"
        self.output_db_path = self.root / "output-gmail.db"
        self.snapshot_path.write_text(
            json.dumps(
                {
                    "schema_version": "ace-qwen-provider-model-snapshot-v1",
                    "object_id": OBJECT_ID,
                    "resolved_request_model": ALLOWED_ALIAS,
                    "catalog_provider_request_count": 1,
                }
            ),
            encoding="utf-8",
        )
        with sqlite3.connect(self.source_db_path) as connection:
            connection.execute(
                "CREATE TABLE emails (id INTEGER PRIMARY KEY, subject TEXT)"
            )
        self.output_db_path.touch()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def unit() -> EpisodeUnit:
        return EpisodeUnit(
            namespace="capability",
            key=(ALLOWED_ALIAS, "ACE-FG-05", 1),
            stage="CAPABILITY_CALIBRATION",
            family_id="ACE-FG-05",
            repeat=1,
        )

    @staticmethod
    def receipt(index: int) -> ProviderReceipt:
        return ProviderReceipt(
            response_id=f"response-{index}",
            requested_model=ALLOWED_ALIAS,
            resolved_model=ALLOWED_ALIAS,
            provider=PROVIDER_ID,
            base_url=DEFAULT_BASE_URL,
            output=[],
        )

    def dispatch(self, ledger: AppendOnlyLedger) -> None:
        ledger.dispatch(
            self.unit(),
            prompt_sha256="a" * 64,
            snapshot_sha256="b" * 64,
            repair_sha256=None,
            requested_model=ALLOWED_ALIAS,
            provider=PROVIDER_ID,
            base_url=DEFAULT_BASE_URL,
        )

    def test_counts_requests_and_closes_all_authority_without_replay(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        self.dispatch(ledger)
        ledger.fail(
            self.unit(),
            failure_class="OperationalError",
            message="no such table: emails",
            receipts=[self.receipt(index) for index in range(5)],
        )

        result = build_failure_adjudication(
            ledger_path=self.ledger_path,
            snapshot_path=self.snapshot_path,
            source_db_path=self.source_db_path,
            output_db_path=self.output_db_path,
            expected_table="emails",
        )

        self.assertEqual(result["status"], VERDICT)
        self.assertEqual(result["scheduled_agent_episode_count"], 8)
        self.assertEqual(result["agent_episode_count"], 1)
        self.assertEqual(result["terminal_agent_episode_count"], 1)
        self.assertEqual(result["provider_request_total"], 6)
        self.assertEqual(
            result["gate"]["failure_classification"],
            FAILURE_CLASSIFICATION,
        )
        self.assertTrue(
            result["gate"]["evaluator_failure_evidence"][
                "source_has_expected_table"
            ]
        )
        self.assertEqual(
            result["gate"]["evaluator_failure_evidence"][
                "evaluator_output_db_bytes"
            ],
            0,
        )
        self.assertEqual(result["scientific_outcomes_observed"], 0)
        self.assertFalse(result["scientific_unit_replayed"])
        self.assertFalse(result["measurement_only_recovery"])
        self.assertEqual(result["provider_calls_initiated_by_adjudicator"], 0)
        self.assertTrue(all(value is False for value in result["authority"].values()))

        result_path = self.root / "result.json"
        manifest_path = self.root / "manifest.json"
        write_failure_artifacts(
            result,
            result_path=result_path,
            snapshot_path=self.snapshot_path,
            manifest_path=manifest_path,
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["provider_request_total"], 6)
        self.assertEqual(manifest["scientific_outcomes_observed"], 0)
        self.assertEqual(
            manifest["files"][str(result_path)]["sha256"],
            sha256_file(result_path),
        )

    def test_unknown_after_dispatch_is_not_auto_adjudicated(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        self.dispatch(ledger)

        with self.assertRaisesRegex(RunnerError, "UNKNOWN_AFTER_DISPATCH"):
            build_failure_adjudication(
                ledger_path=self.ledger_path,
                snapshot_path=self.snapshot_path,
                source_db_path=self.source_db_path,
                output_db_path=self.output_db_path,
                expected_table="emails",
            )

    def test_evaluator_evidence_must_match_failure(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        self.dispatch(ledger)
        ledger.fail(
            self.unit(),
            failure_class="OperationalError",
            message="no such table: messages",
            receipts=[self.receipt(1)],
        )

        with self.assertRaisesRegex(RunnerError, "do not prove"):
            build_failure_adjudication(
                ledger_path=self.ledger_path,
                snapshot_path=self.snapshot_path,
                source_db_path=self.source_db_path,
                output_db_path=self.output_db_path,
                expected_table="emails",
            )


if __name__ == "__main__":
    unittest.main()
