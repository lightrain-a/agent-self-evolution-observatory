from __future__ import annotations

import re
import unittest

from .machine_school_idea_factory import build_machine_school_bank, validate_bank


class MachineSchoolIdeaBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_machine_school_bank()
        cls.summary = cls.payload["summary"]

    def test_internal_screen_counts(self) -> None:
        self.assertEqual(self.summary["raw"], 24)
        self.assertEqual(self.summary["internal_pass"], 11)
        self.assertEqual(self.summary["internal_revise"], 7)
        self.assertEqual(self.summary["internal_reject"], 6)
        self.assertEqual(validate_bank(self.payload), [])

    def test_external_review_is_complete(self) -> None:
        self.assertEqual(self.summary["external_reviewed"], 11)
        self.assertEqual(self.summary["external_pass"], 1)
        self.assertEqual(self.summary["external_revise"], 7)
        self.assertEqual(self.summary["external_block"], 3)
        self.assertTrue(all(idea["external_verdict"] in {"pass", "revise", "block"} for idea in self.payload["passed_ideas"]))

    def test_final_order_and_shortlist(self) -> None:
        passed = self.payload["passed_ideas"]
        self.assertEqual([idea["external_rank"] for idea in passed], list(range(1, 12)))
        self.assertEqual(passed[0]["id"], "regression-probe-half-life")
        self.assertEqual(passed[0]["final_status"], "pilot-now")
        self.assertEqual([idea["id"] for idea in self.payload["teacher_shortlist"]], [
            "regression-probe-half-life",
            "version-differential-failure-localization",
            "model-swap-compatibility-certificate",
            "update-aware-permission-downgrade",
            "cross-form-capability-transfer-gap",
            "delayed-regression-exams",
            "privilege-recovery-curriculum",
            "behavior-triggered-privilege-lease",
        ])

    def test_resource_and_falsifiability_fields(self) -> None:
        for idea in self.payload["all_candidates"]:
            with self.subTest(idea=idea["id"]):
                self.assertLessEqual(idea["budget"]["max_gpus"], 2)
                self.assertLessEqual(idea["budget"]["gpu_hours"], 32)
                self.assertTrue(idea["pilot"]["zh"])
                self.assertTrue(idea["stop_condition"]["zh"])
                self.assertTrue(idea["nearest_work"])
                for field in ("purpose", "core_idea", "collision_boundary", "hypothesis", "strongest_baseline", "pilot", "stop_condition"):
                    self.assertTrue(idea[field]["en"])
                    self.assertIsNone(re.search(r"[\u4e00-\u9fff]", idea[field]["en"]), f"Chinese leaked into English {field}: {idea['id']}")


if __name__ == "__main__":
    unittest.main()
