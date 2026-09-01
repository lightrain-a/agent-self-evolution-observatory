from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_e2_r17_deepseek_v2_repair2_v3 import (
    EPSILON,
    exact_sign_flip_p,
    paired_t_ci_90,
)
from scripts.audit_e2_r17_deepseek_v2_repair2_v3_completion import (
    AUDIT_STATUS,
    EXPECTED_SOURCE_PAIRS,
    EXPECTED_SOURCE_STATES,
    audit_ledger,
)

ROOT = Path(__file__).resolve().parents[1]


class Repair2V3CloseoutTests(unittest.TestCase):
    def test_completion_cardinalities_are_frozen(self) -> None:
        self.assertEqual(
            dict(EXPECTED_SOURCE_PAIRS),
            {
                "repair1_inherited": 14,
                "repair2_m1_recovered": 1,
                "repair2_v3_fresh": 33,
            },
        )
        self.assertEqual(
            EXPECTED_SOURCE_STATES,
            {
                "repair1_inherited": 28,
                "repair2_m1_recovered": 2,
                "repair2_v3_fresh": 66,
            },
        )
        self.assertEqual(AUDIT_STATUS, "PASS_REPAIR2_V3_FULL_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS")

    def test_completion_audit_is_outcome_blind(self) -> None:
        source = (ROOT / "scripts/audit_e2_r17_deepseek_v2_repair2_v3_completion.py").read_text()
        self.assertNotIn('ref["score"]', source)
        self.assertIn('"scientific_scores_read": False', source)
        self.assertIn('"partial_effect_read": False', source)
        self.assertIn('"analyzer_run": False', source)

    def test_analyzer_checks_audit_before_first_score_access(self) -> None:
        source = (ROOT / "scripts/analyze_e2_r17_deepseek_v2_repair2_v3.py").read_text()
        audit_gate = source.index('require(audit.get("status") == AUDIT_STATUS')
        score_access = source.index('score = float(ref["score"])')
        self.assertLess(audit_gate, score_access)
        self.assertIn('analysis_auth.get("completion_audit_sha256") == audit_sha', source)
        self.assertIn('analysis_auth.get("analyzer_sha256") == sha_file(Path(__file__))', source)

    def test_analysis_authorization_has_no_execution_authority(self) -> None:
        source = (ROOT / "scripts/authorize_e2_r17_deepseek_v2_repair2_v3_analysis.py").read_text()
        for forbidden in (
            '"scientific_experiment": False',
            '"provider_io": False',
            '"updater": False',
            '"heldout_evaluation": False',
            '"gpt_scientific_execution": False',
            '"kimi_scientific_execution": False',
            '"qwen_scientific_execution": False',
            '"public_benchmark": False',
            '"second_backbone": False',
        ):
            self.assertIn(forbidden, source)

    def test_provider_ledger_requires_contiguous_unique_claims(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite3"
            connection = sqlite3.connect(db)
            connection.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
            connection.execute("CREATE TABLE claims (claim_id TEXT, unit_id TEXT, unit_call_index INTEGER, claimed_at_utc TEXT)")
            connection.executemany(
                "INSERT INTO metadata VALUES (?, ?)",
                [
                    ("contract_sha256", "c" * 64),
                    ("authorization_sha256", "a" * 64),
                    ("total_limit", "191"),
                    ("per_unit_limit", "11"),
                ],
            )
            connection.executemany(
                "INSERT INTO claims VALUES (?, ?, ?, ?)",
                [("1", "unit-a", 1, "t"), ("2", "unit-a", 2, "t")],
            )
            connection.commit()
            connection.close()
            claims: set[tuple[str, str, int]] = set()
            self.assertEqual(
                audit_ledger(
                    db=db,
                    state_key="state",
                    contract_sha="c" * 64,
                    execution_auth_sha="a" * 64,
                    expected_total_limit=191,
                    expected_per_unit_limit=11,
                    global_claims=claims,
                ),
                2,
            )
            connection = sqlite3.connect(db)
            connection.execute("UPDATE claims SET unit_call_index = 3 WHERE claim_id = '2'")
            connection.commit()
            connection.close()
            with self.assertRaises(RuntimeError):
                audit_ledger(
                    db=db,
                    state_key="state",
                    contract_sha="c" * 64,
                    execution_auth_sha="a" * 64,
                    expected_total_limit=191,
                    expected_per_unit_limit=11,
                    global_claims=set(),
                )

    def test_frozen_statistics_and_conclusions(self) -> None:
        self.assertAlmostEqual(EPSILON, 1.0 / 18.0)
        self.assertEqual(exact_sign_flip_p([0.0] * 12, direction="positive"), 1.0)
        mean, sd, low, high = paired_t_ci_90([1.0] * 12)
        self.assertEqual((mean, sd, low, high), (1.0, 0.0, 1.0, 1.0))
        source = (ROOT / "scripts/analyze_e2_r17_deepseek_v2_repair2_v3.py").read_text()
        statuses = (
            "GO_MRW_CAUSAL_EFFECT_SUPPORTED",
            "STOP_MRW_PRACTICALLY_NULL",
            "STOP_MRW_HARMFUL",
            "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        )
        for status in statuses:
            self.assertIn(status, source)
        self.assertIn('"execute_second_backbone": False', source)
        self.assertIn('"execute_public_benchmark": False', source)


if __name__ == "__main__":
    unittest.main()
