from __future__ import annotations

import unittest

from .r3_final_audit import build_r3_final_audit, validate_r3_final_audit


class R3FinalAuditTest(unittest.TestCase):
    def test_final_counts_and_ids(self) -> None:
        payload = build_r3_final_audit()
        self.assertEqual(validate_r3_final_audit(payload), [])
        self.assertEqual(payload["summary"], {
            "total": 22,
            "pass": 0,
            "revise": 20,
            "block": 2,
            "final_ready": 0,
        })
        by_id = {row["idea_id"]: row for row in payload["ideas"]}
        self.assertEqual(by_id["regression-gated-self-evolution"]["verdict"], "block")
        self.assertEqual(by_id["effect-transport-lesson-specializer-v5"]["verdict"], "block")
        self.assertTrue(all(row["confidence"] == "high" for row in payload["ideas"]))


if __name__ == "__main__":
    unittest.main()
