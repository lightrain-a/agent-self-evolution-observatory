from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_p0_config_factory import CONFIG_NAMES, build_config, write_configs
from .protocol_validity import audit_protocol_validity


class PaperFirstP0ConfigFactoryTest(unittest.TestCase):
    def test_bootstrap_uses_real_f0_artifact_paths(self) -> None:
        pf1 = build_config("future-learnability-preserving-self-evolution")
        pf2 = build_config("cross-surface-repair-routing")
        self.assertEqual(pf1["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "runs/paper-first-p0-20260812/future-learnability/result.json")
        self.assertEqual(pf2["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "runs/paper-first-p0-20260812/shared-surface/result.json")

    def test_future_config_registers_post_update_effect_realization(self) -> None:
        config = build_config("future-learnability-preserving-self-evolution")
        protocol = config["pre_experiment"]["protocol_validity"]
        self.assertTrue(protocol["applies_to_persistent_update"])
        self.assertTrue(protocol["post_update_effect_realization"]["passed"])
        audit = audit_protocol_validity(config)
        self.assertTrue(audit["passed"], audit["blockers"])
        self.assertEqual(len(audit["required_checks"]), 8)

    def test_factory_does_not_reuse_evolved_support_without_same_external_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_configs(root, preserve_evolved=False)
            name = CONFIG_NAMES["future-learnability-preserving-self-evolution"]
            path = root / name
            state = json.loads(path.read_text(encoding="utf-8"))
            state["pre_experiment"]["updater_competence"].update({"passed": True, "status": "support-qualified", "evidence": {"artifact": "premature-f0.json"}})
            path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            write_configs(root)
            after = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(after["pre_experiment"]["updater_competence"]["passed"])
            self.assertEqual(after["pre_experiment"]["updater_competence"]["status"], "pending-local-f0")
            self.assertTrue(after["historical_unauthorized_f0_reuse_forbidden"])

    def test_factory_preserves_evolved_support_only_under_same_external_authority_sha(self) -> None:
        authority = {"promotion_authorized": True, "local_validation_authorized": True, "authority_status": "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID", "artifact_sha256": "a" * 64, "source_message_sha256": "b" * 64}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_configs(root, preserve_evolved=False, authority=authority)
            name = CONFIG_NAMES["future-learnability-preserving-self-evolution"]
            path = root / name
            state = json.loads(path.read_text(encoding="utf-8"))
            state["pre_experiment"]["updater_competence"].update({"passed": True, "status": "support-qualified", "evidence": {"artifact": "authorized-f0.json"}})
            path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            write_configs(root, authority=authority)
            after = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(after["pre_experiment"]["updater_competence"]["passed"])
            self.assertEqual(after["pre_experiment"]["updater_competence"]["evidence"]["artifact"], "authorized-f0.json")


if __name__ == "__main__":
    unittest.main()
