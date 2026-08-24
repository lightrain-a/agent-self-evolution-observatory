from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_r19_execution_authority_r21 import EXPECTED, load_authority


class TestR19ExecutionAuthorityR21(unittest.TestCase):
    def _artifact(self) -> dict:
        return {
            "authority_type": "human-b1-r19-bounded-scientific-execution",
            "decision": "approve",
            "reviewed_by": "user",
            "reviewed_at": "2026-08-24T13:58:00+08:00",
            "source_message_ref": "active-project-conversation-2026-08-24T13:58+08:00",
            "source_message_sha256": "36c33de30c5a14be5a0902f7b7320b7b59c8e979f213f23c315ca5967d6946cd",
            "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
            **EXPECTED,
            "r19_scientific_execution_authorized": True,
            "experiment_authorized": True,
            "model_completions_authorized": True,
            "browser_actions_authorized": True,
            "evaluator_calls_authorized": True,
            "gpu_authorized": True,
            "single_confirmatory_attempt": True,
            "external_api_authorized": False,
            "r18_retry_authorized": False,
            "l3_authorized": False,
            "task_replacement_authorized": False,
            "memory_regeneration_authorized": False,
            "model_or_provider_switch_authorized": False,
            "threshold_change_authorized": False,
            "endpoint_change_authorized": False,
            "statistical_change_authorized": False,
            "outcome_adaptive_extension_authorized": False,
            "claim_expansion_authorized": False,
            "scientific_claim_authority": False,
            "submission_authority": False,
        }

    def _load(self, obj: dict):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "authority.json"
            p.write_text(json.dumps(obj), encoding="utf-8")
            return load_authority(p, repo_root=Path(__file__).resolve().parents[1])

    def test_exact_scope_authorizes_execution_not_claim(self):
        row = self._load(self._artifact())
        self.assertTrue(row["valid"])
        self.assertTrue(row["r19_scientific_execution_authorized"])
        self.assertTrue(row["experiment_authorized"])
        self.assertFalse(row["scientific_claim_authority"])
        self.assertFalse(row["l3_authorized"])
        self.assertEqual(row["budgets"]["terminal_episode_budget"], 140)
        self.assertEqual(row["budgets"]["total_local_model_completion_budget"], 4802)

    def test_budget_drift_fails_closed(self):
        obj = self._artifact(); obj["terminal_episode_budget"] = 141
        row = self._load(obj)
        self.assertFalse(row["valid"])
        self.assertIn("binding-mismatch:terminal_episode_budget", row["errors"])

    def test_r18_retry_or_claim_authority_fails_closed(self):
        obj = self._artifact(); obj["r18_retry_authorized"] = True; obj["scientific_claim_authority"] = True
        row = self._load(obj)
        self.assertFalse(row["valid"])
        self.assertIn("required-false:r18_retry_authorized", row["errors"])
        self.assertIn("required-false:scientific_claim_authority", row["errors"])

    def test_wrong_message_hash_fails_closed(self):
        obj = self._artifact(); obj["source_message_sha256"] = "0" * 64
        row = self._load(obj)
        self.assertFalse(row["valid"])
        self.assertIn("source-message-sha256-mismatch", row["errors"])


if __name__ == "__main__":
    unittest.main()
