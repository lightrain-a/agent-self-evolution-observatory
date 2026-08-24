import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_execution_authority_r16 import (
    EXPECTED_EXECUTOR_MANIFEST,
    EXPECTED_R13_SHA256,
    EXPECTED_R14_SHA256,
    EXPECTED_R15_SHA256,
    EXPECTED_SOURCE_MESSAGE_SHA256,
    EXPECTED_WRITER_MANIFEST,
    load_human_authority,
)


class TestReasoningBankExecutionAuthorityR16(unittest.TestCase):
    def payload(self):
        return {
            "authority_type": "human-b1-l2b-bounded-execution",
            "decision": "approve",
            "reviewed_by": "human-user",
            "reviewed_at": "2026-08-24T10:58:00+08:00",
            "source_message_ref": "active-project-conversation-2026-08-24T10:58+08:00",
            "source_message_sha256": EXPECTED_SOURCE_MESSAGE_SHA256,
            "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
            "r13_writer_input_sha256": EXPECTED_R13_SHA256,
            "r14_writer_model_sha256": EXPECTED_R14_SHA256,
            "r15_executor_contract_sha256": EXPECTED_R15_SHA256,
            "execution_authorized": True,
            "writer_generation_authorized": True,
            "downstream_l2b_authorized": True,
            "local_model_calls_authorized": True,
            "browser_actions_authorized": True,
            "evaluator_calls_authorized": True,
            "gpu_lease_authorized": True,
            "single_confirmatory_attempt": True,
            "writer_request_budget": 36,
            "terminal_episode_budget": 144,
            "executor_completion_budget": 4320,
            "total_local_model_request_budget": 4356,
            "allowed_writer_manifest_digest": EXPECTED_WRITER_MANIFEST,
            "allowed_executor_manifest_digest": EXPECTED_EXECUTOR_MANIFEST,
            "external_api_authorized": False,
            "l3_authorized": False,
            "threshold_change_authorized": False,
            "task_replacement_authorized": False,
            "outcome_adaptive_extension_authorized": False,
            "claim_expansion_authorized": False,
            "scientific_authority": False,
            "submission_authority": False,
        }

    def write(self, root: Path, payload):
        p = root / "permit.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return p

    def test_valid_external_permit_is_execution_only(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as repo:
            p = self.write(Path(td), self.payload())
            row = load_human_authority(p, repo_root=Path(repo))
            self.assertTrue(row["valid"])
            self.assertTrue(row["execution_authorized"])
            self.assertFalse(row["scientific_authority"])
            self.assertFalse(row["l3_authorized"])

    def test_budget_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as repo:
            x = self.payload(); x["terminal_episode_budget"] = 145
            row = load_human_authority(self.write(Path(td), x), repo_root=Path(repo))
            self.assertFalse(row["valid"])
            self.assertIn("binding-mismatch:terminal_episode_budget", row["errors"])

    def test_scientific_authority_true_is_rejected(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as repo:
            x = self.payload(); x["scientific_authority"] = True
            row = load_human_authority(self.write(Path(td), x), repo_root=Path(repo))
            self.assertFalse(row["valid"])
            self.assertIn("required-false:scientific_authority", row["errors"])

    def test_in_repo_permit_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = root / "repo"; repo.mkdir()
            p = self.write(repo, self.payload())
            row = load_human_authority(p, repo_root=repo)
            self.assertFalse(row["valid"])
            self.assertIn("authority-artifact-must-be-external-to-repository", row["errors"])


if __name__ == "__main__":
    unittest.main()
