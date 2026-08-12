from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_p0_config_factory import CONFIG_NAMES, build_config, write_configs


class PaperFirstP0ConfigFactoryTest(unittest.TestCase):
    def test_bootstrap_uses_real_f0_artifact_paths(self) -> None:
        pf1 = build_config("future-learnability-preserving-self-evolution")
        pf2 = build_config("cross-surface-repair-routing")
        self.assertEqual(pf1["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "runs/paper-first-p0-20260812/future-learnability/result.json")
        self.assertEqual(pf2["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "runs/paper-first-p0-20260812/shared-surface/result.json")

    def test_factory_never_rolls_back_evolved_support_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_configs(root, preserve_evolved=False)
            name = CONFIG_NAMES["future-learnability-preserving-self-evolution"]
            path = root / name
            state = json.loads(path.read_text(encoding="utf-8"))
            state["pre_experiment"]["updater_competence"].update({"passed": True, "status": "support-qualified", "evidence": {"artifact": "frozen-support.json"}})
            path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            write_configs(root)
            after = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(after["pre_experiment"]["updater_competence"]["passed"])
            self.assertEqual(after["pre_experiment"]["updater_competence"]["status"], "support-qualified")
            self.assertEqual(after["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "frozen-support.json")


if __name__ == "__main__":
    unittest.main()
