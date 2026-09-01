from __future__ import annotations

import unittest

from research_pipeline.research_system import _load_external_failure_assets


class E2R17ExternalFailureAssetsTest(unittest.TestCase):
    def test_identifiability_and_evaluator_qualification_assets_are_zero_authority(self) -> None:
        by_signature = {
            row["signature"]: row for row in _load_external_failure_assets()
        }
        expected = {
            "identifiability:negative-control-nonequivalence-blocks-causal-interpretation",
            "measurement:evaluator-qualification-needs-competence-headroom-and-completion",
        }
        self.assertTrue(expected.issubset(by_signature))
        for signature in expected:
            row = by_signature[signature]
            self.assertFalse(row["scientific_authority"])
            self.assertEqual(row["idea_id"], "E2-R17")
            self.assertTrue(row["reusable_precheck"])
            self.assertTrue(row["does_not_imply"])


if __name__ == "__main__":
    unittest.main()
