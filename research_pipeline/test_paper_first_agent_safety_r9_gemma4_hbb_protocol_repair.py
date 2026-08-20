from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .paper_first_agent_safety_r9_gemma4_development_readjudication import STATUS as READJUDICATION_STATUS
from .paper_first_agent_safety_r9_gemma4_hbb_protocol_repair import (
    EXPECTED_V4_DEVELOPMENT_IDS,
    EXPECTED_V4_HELDOUT_IDS,
    EXPECTED_V4_QUALIFICATION_IDS,
    V4_REALIZATION_ID,
    V4_STATUS,
    build_v4_preregistration,
    derive_v4_development_panel,
    validate_v4,
)
from .paper_first_agent_safety_r9_gemma4_gate0_adjudication import STATUS as GATE0_STATUS
from .paper_first_agent_safety_r9_gemma4_runtime_repair import V3_REALIZATION_ID


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Gemma4HBBProtocolRepairTest(unittest.TestCase):
    def make_hbb(self, root: Path) -> Path:
        rows = [{"id": i, "website": "local:email", "semantic_category": "content/other"} for i in range(100)]
        for i in [31, 32, 33, 34, 35]:
            rows[i].update(website="local:twitter", semantic_category="content/harassment_and_bully")
        for i in [36, 38]:
            rows[i].update(website="local:review", semantic_category="content/harassment_and_bully")
        rows[37].update(website="local:email", semantic_category="content/harassment_and_bully")
        for i in [8, 9, 10, 11, 12, 13, 14, 20]:
            rows[i].update(website="local:twitter", semantic_category="content/misinformation")
        for i in [15, 16, 17, 18, 19]:
            rows[i].update(website="local:email", semantic_category="content/misinformation")
        for i in [0, 1, 2, 4, 5, 6]:
            rows[i].update(website="local:email", semantic_category="content/phishing")
        path = root / "hbb.json"; path.write_text(json.dumps(rows), encoding="utf-8")
        return path

    def fixture(self, root: Path) -> dict:
        readj = root / "readj.json"; readj.write_text(json.dumps({"status": READJUDICATION_STATUS, "stop_class": "PROTOCOL_STOP", "failure_layer": "task_validation_semantics"}))
        v3 = root / "v3.json"; v3.write_text(json.dumps({
            "realization_id": V3_REALIZATION_ID,
            "contract_sha256": "c" * 64,
            "runtime_launch": {
                "host": "127.0.0.1", "port": 18002, "dtype": "bfloat16",
                "served_model_name": "google/gemma-4-26B-A4B-it",
                "max_num_batched_tokens": 2496,
                "max_model_len_override": None,
                "gpu_memory_utilization_override": None,
                "quantization": None,
            },
        }))
        gate0 = root / "gate0.json"; gate0.write_text(json.dumps({"status": GATE0_STATUS, "contract_sha256": "c" * 64}))
        hbb = self.make_hbb(root)
        task = root / "task.py"; task.write_text("pinned validate bug fixture\n")
        dev = root / "v3-dev"; dev.mkdir()
        return {
            "readjudication_path": readj,
            "v3_contract_path": v3,
            "gate0_path": gate0,
            "hbb_dataset_path": hbb,
            "hbb_task_path": task,
            "v3_development_root": dev,
            "hbb_sha": sha(hbb),
            "task_sha": sha(task),
        }

    def build(self, paths: dict) -> dict:
        with (
            patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.validate_readjudication", return_value=[]),
            patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.validate_v3", return_value=[]),
            patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.validate_gate0_pass", return_value=[]),
            patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.EXPECTED_HBB_DATASET_SHA256", paths["hbb_sha"]),
            patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.EXPECTED_HBB_TASK_SHA256", paths["task_sha"]),
        ):
            return build_v4_preregistration(
                readjudication_path=paths["readjudication_path"],
                v3_contract_path=paths["v3_contract_path"],
                gate0_path=paths["gate0_path"],
                hbb_dataset_path=paths["hbb_dataset_path"],
                hbb_task_path=paths["hbb_task_path"],
                v3_development_root=paths["v3_development_root"],
                generated_at="2026-08-19T15:30:00+00:00",
            )

    def test_fresh_panel_is_mechanically_selected_after_v3_quarantine(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            rows = json.loads(self.make_hbb(Path(td)).read_text())
            panel = derive_v4_development_panel(rows)
            self.assertEqual(panel["development_probe_ids"], EXPECTED_V4_DEVELOPMENT_IDS)
            self.assertEqual([x["selected_site"] for x in panel["selection_details"]], ["local:twitter", "local:email", "local:email"])
            self.assertFalse(panel["selection_uses_outcomes"])

    def test_v4_changes_only_assistant_stop_semantics_and_authorizes_episodes_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paths = self.fixture(Path(td)); state = self.build(paths)
            with patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.EXPECTED_HBB_TASK_SHA256", paths["task_sha"]):
                self.assertEqual(validate_v4(state), [])
            self.assertEqual(state["status"], V4_STATUS)
            self.assertEqual(state["realization_id"], V4_REALIZATION_ID)
            self.assertEqual(state["probe_panels"]["development_probe_ids"], EXPECTED_V4_DEVELOPMENT_IDS)
            self.assertEqual(state["probe_panels"]["fresh_qualification_ids"], EXPECTED_V4_QUALIFICATION_IDS)
            self.assertEqual(state["probe_panels"]["sealed_heldout_future_ids"], EXPECTED_V4_HELDOUT_IDS)
            self.assertTrue(state["authority"]["development_episode_execution"])
            self.assertFalse(state["authority"]["development_harmbench_execution"])
            self.assertTrue(state["agent_interface"]["awm_parser_unchanged"])
            self.assertFalse(state["task_validation_adapter"]["classifier_input_extraction_changed"])

    def test_carried_qualification_must_still_be_unexecuted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paths = self.fixture(Path(td))
            p = paths["v3_development_root"] / "x" / "probe-35"; p.mkdir(parents=True); (p / "episode-result.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "qualification probe was already executed"):
                self.build(paths)

    def test_v4_validator_rejects_parser_or_runtime_rescue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paths = self.fixture(Path(td)); state = self.build(paths)
            state["agent_interface"]["awm_parser_unchanged"] = False
            state["runtime_launch"]["max_model_len_override"] = 8192
            with patch("research_pipeline.paper_first_agent_safety_r9_gemma4_hbb_protocol_repair.EXPECTED_HBB_TASK_SHA256", paths["task_sha"]):
                errors = validate_v4(state)
            self.assertIn("Gemma4 V4 AWM interface drift", errors)
            self.assertIn("Gemma4 V4 runtime drift", errors)


if __name__ == "__main__":
    unittest.main()
