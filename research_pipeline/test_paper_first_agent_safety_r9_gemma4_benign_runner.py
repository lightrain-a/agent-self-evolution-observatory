from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_benign_runner import load_v2, run_benign_episode
from .paper_first_agent_safety_r9_qualification import ListenerState


class Gemma4BenignRunnerTest(unittest.TestCase):
    def test_current_v2_binds_current_formal_asset_receipt(self) -> None:
        contract = load_v2(
            Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"),
            Path("/data/wyt/agent-safety-discovery-20260818/model-assets/gemma4-26B-A4B-it-4d7ae4984b7db7de8f8457170b3f1a419ee76d52/.r9-gemma4-formal-asset-verification.json"),
        )
        self.assertTrue(contract["authority"]["benign_capability_execution"])
        self.assertFalse(contract["authority"]["development_safety_execution"])

    def test_runner_refuses_harmful_probe_id_before_any_runtime_import(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "refuses task"):
                run_benign_episode(
                    contract={"contract_sha256": "x"},
                    task_id=37,
                    episode_root=Path(td),
                    listener=ListenerState(),
                    base_url="http://127.0.0.1:1",
                    awm_root=Path("/nonexistent"),
                    browserart_root=Path("/nonexistent"),
                    safety_context_path=Path("/nonexistent"),
                )


if __name__ == "__main__":
    unittest.main()
