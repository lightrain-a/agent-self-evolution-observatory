from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"

PATHS = {
    "capability": GENERATED / "agent-constraint-externality-capability-contract-20260831.json",
    "f0": GENERATED / "agent-constraint-externality-f0-frozen-protocol-20260831.json",
    "readiness": GENERATED / "agent-constraint-externality-f0-readiness-20260831.json",
    "manifest": GENERATED / "agent-constraint-externality-f0-preflight-manifest-20260831.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppWorldConstraintF0PreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {name: load(path) for name, path in PATHS.items()}

    def test_identity_and_zero_outcome_boundary(self) -> None:
        for payload in self.data.values():
            self.assertEqual(payload["object_id"], OBJECT_ID)
        for name in ("capability", "f0", "manifest"):
            self.assertEqual(
                self.data[name]["scientific_outcomes_observed"], 0
            )
            self.assertEqual(self.data[name]["provider_calls"], 0)
            self.assertEqual(self.data[name]["gpu_runs"], 0)
        readiness = self.data["readiness"]
        self.assertFalse(readiness["f0_executed"])
        self.assertEqual(readiness["f0_outcomes_observed"], 0)
        self.assertFalse(readiness["p1_authorized"])

    def test_disjoint_outcome_blind_split(self) -> None:
        capability_ids = set(self.data["capability"]["family_ids"])
        f0_ids = set(self.data["f0"]["family_ids"])
        self.assertEqual(len(capability_ids), 4)
        self.assertEqual(len(f0_ids), 8)
        self.assertFalse(capability_ids & f0_ids)
        self.assertEqual(len(capability_ids | f0_ids), 12)
        self.assertTrue(self.data["f0"]["split_is_disjoint_from_capability"])

    def test_model_selection_is_frozen_before_f0(self) -> None:
        capability = self.data["capability"]
        self.assertEqual(
            capability["model_selection_order"],
            ["doubao-seed-2.0-lite", "deepseek-v4-flash", "deepseek-v4-pro"],
        )
        self.assertEqual(
            capability["selection_rule"],
            "FIRST_CANDIDATE_MEETING_ALL_FLOOR_AND_CEILING_RULES",
        )
        self.assertEqual(capability["execution"]["provider_max_retries"], 0)
        self.assertFalse(capability["execution"]["application_retry"])
        self.assertTrue(capability["execution"]["no_episode_replacement"])

    def test_f0_is_exactly_once_and_within_requested_envelope(self) -> None:
        f0 = self.data["f0"]
        probe = f0["probe_phase"]
        self.assertEqual(probe["arms"], ["INDEPENDENT", "LOW", "HIGH"])
        self.assertEqual(probe["branches"], ["NO_UPDATE", "UPDATE"])
        self.assertEqual(probe["seeds"], [1201, 1202, 1203])
        self.assertEqual(probe["planned_episode_envelope"], 144)
        exactly_once = f0["exactly_once"]
        self.assertEqual(exactly_once["provider_max_retries"], 0)
        self.assertFalse(exactly_once["application_retry"])
        self.assertTrue(exactly_once["append_only_ledger"])
        self.assertTrue(exactly_once["duplicate_key_is_fatal"])
        self.assertTrue(exactly_once["retry_or_replacement_forbidden"])
        self.assertFalse(probe["partial_effects_readable_during_execution"])

    def test_repair_is_target_only_and_content_addressed(self) -> None:
        source = self.data["f0"]["source_phase"]
        forbidden = set(source["forbidden_updater_input"])
        self.assertIn("NON_TARGET_OUTCOMES", forbidden)
        self.assertIn("TOPOLOGY_LABEL", forbidden)
        self.assertIn("F0_EFFECT", forbidden)
        self.assertFalse(source["human_edit_after_generation"])
        self.assertIn("sha256", source["freeze_fields"])
        self.assertIn("exact_bytes", source["freeze_fields"])
        self.assertEqual(source["minimum_eligible_repair_families"], 6)

    def test_post_f0_expansion_remains_closed(self) -> None:
        authority = self.data["f0"]["post_f0_authority"]
        self.assertEqual(authority["toolsandbox_only_after"], "F0_MECHANISM_SUPPORT")
        self.assertEqual(
            authority["appworld_ul_only_after"],
            "F0_AND_TOOLSANDBOX_MECHANISM_SUPPORT",
        )
        self.assertFalse(authority["full_p1"])
        self.assertFalse(authority["workarena"])
        self.assertFalse(authority["multi_backbone"])
        self.assertFalse(authority["paper_claim"])

    def test_provider_summary_has_no_secret_and_readiness_is_honest(self) -> None:
        readiness = self.data["readiness"]
        provider = readiness["provider"]
        self.assertFalse(provider["api_key_in_output"])
        serialized = json.dumps(readiness, sort_keys=True)
        self.assertNotIn("Bearer ", serialized)
        self.assertEqual(readiness["execution_override"]["max_retries"], 0)
        self.assertIn(
            readiness["status"],
            {
                "CAPABILITY_CALIBRATION_BLOCKED_PROVIDER_NOT_CONFIGURED",
                "CAPABILITY_CALIBRATION_READY_NOT_EXECUTED",
            },
        )

    def test_manifest_hashes_are_self_consistent(self) -> None:
        manifest = self.data["manifest"]
        self.assertFalse(manifest["authority"]["f0"])
        self.assertFalse(manifest["authority"]["p1"])
        for relative, metadata in manifest["files"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256(path), metadata["sha256"])
            self.assertEqual(path.stat().st_size, metadata["bytes"])


if __name__ == "__main__":
    unittest.main()
