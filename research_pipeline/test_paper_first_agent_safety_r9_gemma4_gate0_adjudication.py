from __future__ import annotations

import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_gate0_adjudication import build_gate0_pass, validate_gate0_pass


class Gemma4Gate0AdjudicationTest(unittest.TestCase):
    def test_current_gate0_pass_authorizes_only_development_panel(self) -> None:
        state = build_gate0_pass(
            contract_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"),
            benign_root=Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v3-20260819/benign"),
        )
        self.assertEqual(validate_gate0_pass(state), [])
        self.assertEqual(state["development_safety_panel"]["probe_ids"], [37, 12, 4])
        self.assertTrue(state["development_safety_panel"]["authorized"])
        self.assertFalse(state["fresh_qualification_panel"]["authorized"])
        self.assertFalse(state["sealed_heldout_future"]["authorized"])
        self.assertFalse(state["scientific_authority"])

    def test_validator_rejects_heldout_leak(self) -> None:
        state = build_gate0_pass(
            contract_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"),
            benign_root=Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v3-20260819/benign"),
        )
        state["sealed_heldout_future"]["authorized"] = True
        self.assertIn("Gemma4 Gate0 leaked qualification/heldout authority", validate_gate0_pass(state))


if __name__ == "__main__":
    unittest.main()
