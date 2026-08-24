from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_r19_reopen_candidate import normal_two_sided_power


class TestR19ReopenCandidate(unittest.TestCase):
    def test_n35_medium_variance_sensitivity(self):
        self.assertAlmostEqual(normal_two_sided_power(35, 0.3), 0.8408786, places=5)

    def test_n35_not_unconditionally_powered_at_high_variance(self):
        self.assertLess(normal_two_sided_power(35, 0.4), 0.8)

    def test_n35_retains_high_power_at_low_variance(self):
        self.assertGreater(normal_two_sided_power(35, 0.2), 0.99)


if __name__ == "__main__":
    unittest.main()
