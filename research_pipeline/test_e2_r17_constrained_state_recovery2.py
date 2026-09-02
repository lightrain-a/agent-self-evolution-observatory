from __future__ import annotations

import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("g0_base", "g1_verify", "g2_complete", "g3_complete_recover")
CONTRACT = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v2-contract-20260902.json"
AUTH = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v2-authorization-20260902.json"
PREFLIGHT = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v2-preflight-20260902.json"
ACTUAL_PATH = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v2-actual-path-preflight-20260902.json"
SUPERSESSION = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v1-supersession-20260902.json"
PARENT_BOUNDARY = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-parent-boundary-20260902.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ledger_claim_count(path: Path) -> int:
    if not path.exists():
        return 0
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return int(conn.execute("select count(*) from claims").fetchone()[0])
    finally:
        conn.close()


class TestE2R17ConstrainedStateRecovery2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load(CONTRACT)
        cls.auth = load(AUTH)
        cls.preflight = load(PREFLIGHT)
        cls.actual = load(ACTUAL_PATH)
        cls.boundary = load(PARENT_BOUNDARY)
        cls.supersession = load(SUPERSESSION)

    def test_frozen_authority_chain_is_exact(self) -> None:
        self.assertEqual(self.contract["status"], "FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO")
        self.assertEqual(self.auth["status"], "AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT")
        self.assertEqual(self.auth["contract_sha256"], sha(CONTRACT))
        authority = self.auth["authority"]
        self.assertTrue(authority["scientific_experiment"])
        self.assertTrue(authority["measurement_only"])
        self.assertTrue(authority["provider_io"])
        for forbidden in ("updater", "analyzer", "second_backbone", "public_benchmark", "e3_confirmation", "paper_promotion", "submission"):
            self.assertFalse(authority[forbidden], forbidden)

    def test_parent_boundary_and_supersession_are_outcome_blind(self) -> None:
        self.assertEqual(self.boundary["status"], "PASS_RECOVERY2_PARENT_BOUNDARY_OUTCOME_BLIND")
        self.assertFalse(self.boundary["scientific_scores_read"])
        self.assertFalse(self.boundary["partial_effect_read"])
        self.assertEqual(self.supersession["status"], "PASS_RECOVERY2_V2_SUPERSEDES_UNUSED_V1_AUTHORITY")
        self.assertEqual(self.supersession["provider_calls_under_v1"], 0)
        self.assertEqual(self.supersession["scientific_outcomes_under_v1"], 0)
        self.assertTrue(self.supersession["v1_execution_authority_revoked"])
        self.assertTrue(self.supersession["v1_run_root_absent"])
        self.assertTrue(self.supersession["v1_lineage_lease_absent"])

    def test_exact_remaining_set_is_27_without_completed_replay(self) -> None:
        rec = self.contract["recovery2"]
        heldout = list(self.contract["heldout_task_ids"])
        self.assertEqual(rec["inherited_completed_measurements"], 45)
        self.assertEqual(rec["new_measurements"], 27)
        self.assertFalse(rec["completed_unit_replay"])
        remaining: list[tuple[str, str]] = []
        completed = 0
        for arm in ARMS:
            binding = rec["parent_manifests"][arm]
            manifest = Path(binding["path"])
            self.assertTrue(manifest.is_file())
            self.assertEqual(sha(manifest), binding["sha256"])
            tasks = [str(row["task_id"]) for row in jsonl_rows(manifest)]
            self.assertEqual(len(tasks), len(set(tasks)))
            completed += len(tasks)
            remaining.extend((arm, task) for task in heldout if task not in tasks)
        self.assertEqual(completed, 45)
        self.assertEqual(len(remaining), 27)
        self.assertEqual(remaining.count(("g2_complete", "r17-b4-msp-p8")), 1)

    def test_budget_never_expands_beyond_original_191(self) -> None:
        rec = self.contract["recovery2"]
        parent_root = Path(rec["parent_run_root"])
        original_failed = Path(rec["original_failed_lineage"]["provider_ledger_path"])
        original_failed_claims = ledger_claim_count(original_failed)
        self.assertEqual(original_failed_claims, 3)
        child_limit = int(rec["child_provider_total_limit"])
        self.assertEqual(child_limit, 123)
        expected = {"g0_base": 55, "g1_verify": 60, "g2_complete": 65, "g3_complete_recover": 68}
        observed = {}
        for arm in ARMS:
            claims = ledger_claim_count(parent_root / "measurement" / arm / "provider_budget.sqlite3")
            if arm == "g3_complete_recover":
                claims += original_failed_claims
            observed[arm] = claims
            self.assertLessEqual(claims + child_limit, 191, arm)
        self.assertEqual(observed, expected)
        self.assertEqual(self.auth["execution_scope"]["provider_budget"], {"required": True, "total_limit": 123, "per_unit_limit": 11})

    def test_actual_actor_path_reaches_provider_boundary_for_all_four_arms(self) -> None:
        self.assertEqual(self.preflight["status"], "PASS_CONSTRAINED_STATE_MICRO_ZERO_PROVIDER_PREFLIGHT")
        self.assertEqual(self.actual["status"], "PASS_RECOVERY2_V2_ACTUAL_ACTOR_PATH_4_OF_4_ZERO_PROVIDER")
        self.assertEqual(self.actual["provider_calls"], 0)
        self.assertEqual(self.actual["provider_claims"], 0)
        rows = {row["arm"]: row for row in self.actual["arms"]}
        self.assertEqual(set(rows), set(ARMS))
        self.assertEqual(rows["g0_base"]["receipt_mode"], "none_initial_skill")
        for arm in ("g1_verify", "g2_complete", "g3_complete_recover"):
            self.assertEqual(rows[arm]["receipt_mode"], "deterministic_bound_receipt")
        for row in rows.values():
            self.assertEqual(row["status"], "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO")
            self.assertEqual(row["provider_calls"], 0)
            self.assertEqual(row["provider_claims"], 0)

    def test_analysis_code_is_separate_from_execution_authority(self) -> None:
        analyzer = ROOT / "scripts/analyze_e2_r17_constrained_state_micro.py"
        authorizer = ROOT / "scripts/authorize_e2_r17_constrained_state_micro_analysis.py"
        audit = ROOT / "scripts/audit_e2_r17_constrained_state_micro_recovery2_completion.py"
        self.assertTrue(analyzer.is_file() and authorizer.is_file() and audit.is_file())
        self.assertFalse(self.auth["authority"]["analyzer"])
        source = audit.read_text(encoding="utf-8")
        self.assertIn("scientific_scores_read", source)
        self.assertNotIn("ref['score']", source)
        self.assertNotIn('ref["score"]', source)


if __name__ == "__main__":
    unittest.main()
