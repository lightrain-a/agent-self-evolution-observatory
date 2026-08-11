from __future__ import annotations

import json
import unittest
from pathlib import Path

from .p0_alfworld_contract import estimate_a1_episodes


class P0A3ProbeRepairConfigTest(unittest.TestCase):
    def test_probe_repair_plan_is_small_frozen_and_blocked_by_updater_competence(self) -> None:
        path=Path(__file__).with_name("p0_a3_probe_repair_config.json")
        cfg=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(cfg["idea_id"],"regression-gated-self-evolution")
        self.assertFalse(cfg["execution_authorized"])
        self.assertFalse(cfg["prerequisites"]["updater_competence_pass"])
        self.assertTrue(cfg["prerequisites"]["mastered_probe_panel_pass"])
        self.assertEqual(cfg["scope"]["mastered_probe_panel"]["panel_size"],6)
        estimate=estimate_a1_episodes(cfg,8)
        self.assertEqual(estimate["worst_case_total"],124)
        self.assertLessEqual(estimate["worst_case_total"],cfg["resource_cap"]["episodes"])
        self.assertTrue(cfg["analysis"]["fresh_candidate_validation_required"])
        self.assertTrue(cfg["analysis"]["method_result_from_this_qualification_forbidden"])


if __name__=="__main__":
    unittest.main()
