from __future__ import annotations

import copy
import unittest

from .paper_first_zetta_timescale_support_audit import (
    CANDIDATE_ID,
    EVIDENCE_FILE_SHA256,
    OFFICIAL_COMMIT,
    SOURCE_REFS,
    TRACKED_FILE_COUNT,
    TRACKED_MANIFEST_SHA256,
    REQUIRED_UNIT,
    REOPEN_CONDITION,
    validate_support_audit,
)


class ZettaTimescaleSupportAuditTest(unittest.TestCase):
    def audit(self) -> dict:
        markers = {
            "recovery_only_rejected_unknown_critic": True,
            "critic_only_rejected_uncovered_rule": True,
            "atomic_delta_requires_one_critic_and_one_recovery": True,
            "runtime_modes_only_strict_or_active": True,
            "active_bundle_loaded_and_sha_checked": True,
        }
        return {
            "schema_version": "1.0",
            "status": "HOLD_SUPPORT_RELEASED_SCHEMA_BLOCKS_REQUIRED_UNIT",
            "candidate_id": CANDIDATE_ID,
            "source_refs": list(SOURCE_REFS),
            "official_commit": OFFICIAL_COMMIT,
            "origin_url": "https://github.com/air-embodied-brain/Zetta-Embodiment.git",
            "origin_matches_official": True,
            "worktree_clean": True,
            "origin_main_head": OFFICIAL_COMMIT,
            "tracked_file_count": TRACKED_FILE_COUNT,
            "tracked_manifest_sha256": TRACKED_MANIFEST_SHA256,
            "evidence_files": [
                {"path": path, "sha256": sha, "expected_sha256": sha, "matches_expected": True}
                for path, sha in EVIDENCE_FILE_SHA256.items()
            ],
            "schema_level_blocker": {
                "kind": "RELEASED_SUBSTRATE_SCHEMA_CONTRACT",
                "markers": markers,
                "required_intermediate_arms_contract_valid": False,
            },
            "required_unit": REQUIRED_UNIT,
            "reopen_only_if": REOPEN_CONDITION,
            "authority": {
                "problem_gate": False,
                "paper_design": False,
                "method": False,
                "experiment": False,
                "p0": False,
                "gpu": False,
            },
            "scientific_authority": False,
        }

    def test_schema_blocker_hold_is_zero_authority_and_reopenable(self) -> None:
        audit = self.audit()
        self.assertEqual(validate_support_audit(audit), [])
        self.assertEqual(audit["status"], "HOLD_SUPPORT_RELEASED_SCHEMA_BLOCKS_REQUIRED_UNIT")
        self.assertFalse(audit["schema_level_blocker"]["required_intermediate_arms_contract_valid"])
        self.assertTrue(all(value is False for value in audit["authority"].values()))
        self.assertFalse(audit["scientific_authority"])

    def test_revision_drift_cannot_preserve_stable_schema_hold(self) -> None:
        audit = self.audit()
        audit["origin_main_head"] = "0" * 40
        self.assertIn(
            "stable schema hold must bind exact official main revision",
            validate_support_audit(audit),
        )

    def test_evidence_digest_drift_cannot_preserve_stable_schema_hold(self) -> None:
        audit = copy.deepcopy(self.audit())
        audit["evidence_files"][0]["sha256"] = "0" * 64
        errors = validate_support_audit(audit)
        self.assertTrue(any(error.startswith("evidence file digest mismatch:") for error in errors))

    def test_nonofficial_or_dirty_checkout_cannot_preserve_stable_schema_hold(self) -> None:
        audit = self.audit();audit["origin_matches_official"] = False
        self.assertIn("stable schema hold must bind the official repository origin", validate_support_audit(audit))
        audit = self.audit();audit["worktree_clean"] = False
        self.assertIn("stable schema hold requires a clean audited checkout", validate_support_audit(audit))

    def test_support_audit_cannot_upgrade_problem_gate(self) -> None:
        audit = self.audit()
        audit["authority"]["problem_gate"] = True
        self.assertIn("support audit downstream authority must remain false", validate_support_audit(audit))


if __name__ == "__main__":
    unittest.main()
