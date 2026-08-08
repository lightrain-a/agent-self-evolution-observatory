from __future__ import annotations

import unittest

from .final_advisor_audit import TARGET, build_final_advisor_audit


class FinalAdvisorAuditTest(unittest.TestCase):
    def test_final_gate_is_strict_and_complete(self) -> None:
        payload = build_final_advisor_audit()
        self.assertEqual(payload["target"], TARGET)
        self.assertEqual(payload["summary"]["total"], TARGET)
        self.assertEqual(payload["summary"]["pass"], TARGET)
        self.assertEqual(payload["summary"]["revise"], 0)
        self.assertEqual(payload["summary"]["block"], 0)
        self.assertTrue(payload["summary"]["ready"])
        self.assertEqual(payload["summary"]["unanimous_internal_pass"], TARGET)
        self.assertEqual(payload["summary"]["fresh_collision_rechecks"], TARGET)
        self.assertEqual(payload["summary"]["targeted_r32_rechecks"], 6)
        self.assertEqual(len({row["idea_id"] for row in payload["ideas"]}), TARGET)
        self.assertTrue(all(row["verdict"] == "pass" for row in payload["ideas"]))
        self.assertTrue(all(row["collision_gate"] == "pass" for row in payload["ideas"]))
        self.assertTrue(all(all(v == "pass" for v in row["reviewers"].values()) for row in payload["ideas"]))

    def test_historical_blocks_are_not_reintroduced(self) -> None:
        payload = build_final_advisor_audit()
        current_ids = {row["idea_id"] for row in payload["ideas"]}
        retired_ids = {row["idea_id"] for row in payload["retired_from_advisor_pool"]}
        self.assertNotIn("regression-gated-self-evolution", current_ids)
        self.assertNotIn("effect-transport-lesson-specializer-v5", current_ids)
        self.assertIn("regression-gated-self-evolution", retired_ids)
        self.assertIn("effect-transport-lesson-specializer-v5", retired_ids)


if __name__ == "__main__":
    unittest.main()
