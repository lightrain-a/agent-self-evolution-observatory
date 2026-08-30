from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .b1_memrl_alfworld_fresh_preflight import (
    FAILURE_HEADER,
    SUCCESS_HEADER,
    build_preflight,
    render_memory_patch,
)


class B1MemRLAlfworldFreshPreflightTest(unittest.TestCase):
    def test_rendered_intervention_keeps_body_fixed_and_backend_hidden(self) -> None:
        body = "Task: x\n\nraw trajectory body"
        content = render_memory_patch(body, "A1_CONTENT_ONLY", "success")
        backend = render_memory_patch(body, "A7_BACKEND_ONLY_LABEL", "failure")
        truthful = render_memory_patch(body, "A2_TRUTHFUL_VISIBLE_PROVENANCE", "success")
        flipped = render_memory_patch(body, "A5_FLIPPED_VISIBLE_PROVENANCE", "success")
        self.assertEqual(content, backend)
        self.assertIn(body, truthful)
        self.assertIn(body, flipped)
        self.assertIn(SUCCESS_HEADER, truthful)
        self.assertIn(FAILURE_HEADER, flipped)

    def test_current_fixed_assets_pass_g1_g8(self) -> None:
        project = Path(__file__).resolve().parents[1]
        payload = build_preflight(
            memrl_root=Path("/data/wyt/b1-memrl-audit-20260830"),
            alfworld_data=Path("/data/wyt/agent-self-evolution-observatory/alfworld"),
            model_path=Path("/data/wyt/models/indept/Qwen2.5-7B"),
            project_root=project,
            generated_at="2026-08-30T00:00:00+00:00",
        )
        self.assertEqual(payload["status"], "FRESH_SUBSTRATE_G1_G8_PREFLIGHT_PASS")
        self.assertEqual(payload["task_partition"]["source_n"], 24)
        self.assertEqual(payload["task_partition"]["pilot_target_n"], 6)
        self.assertEqual(payload["task_partition"]["confirmatory_target_n"], 12)
        self.assertTrue(payload["task_partition"]["all_partitions_disjoint"])
        self.assertTrue(all(row["pass"] for row in payload["gates"].values()))
        self.assertFalse(any(payload["authority"].values()))
        self.assertTrue(payload["intervention"]["backend_only_equals_content_only"])


if __name__ == "__main__":
    unittest.main()
