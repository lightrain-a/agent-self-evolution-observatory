from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_safety_development import assert_probe_allowed, load_authorized_contract, run_development_episode
from .paper_first_agent_safety_r9_qualification import ListenerState


class Gemma4SafetyDevelopmentTest(unittest.TestCase):
    def test_current_gate0_authorizes_exact_development_panel(self) -> None:
        contract = load_authorized_contract(
            Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"),
            Path("generated/agent-safety-r9-gemma4-gate0-pass-20260819.json"),
        )
        self.assertEqual(contract["probe_selection"]["development_safety_ids"], [37, 12, 4])
        for probe_id in [37, 12, 4]:
            assert_probe_allowed(probe_id)

    def test_runner_refuses_qualification_and_heldout_before_runtime_import(self) -> None:
        for probe_id in [35, 20, 6, 34, 21, 1]:
            with self.assertRaises(ValueError):
                assert_probe_allowed(probe_id)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "refuses probe"):
                run_development_episode(
                    contract={"contract_sha256": "x"},
                    probe_id=35,
                    episode_root=Path(td),
                    listener=ListenerState(),
                    base_url="http://127.0.0.1:1",
                    awm_root=Path("/nonexistent"),
                    browserart_root=Path("/nonexistent"),
                    hbb={},
                    safety_context_path=Path("/nonexistent"),
                )


if __name__ == "__main__":
    unittest.main()
