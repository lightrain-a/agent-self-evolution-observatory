from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_codingplan_deepseek_capability import (
    ACTIVE_BUNDLE,
    ADDENDUM,
    CAPABILITY_FAMILIES,
    PROVIDER_QUAL,
    TOOL_CAP,
    build_addendum,
    build_provider_qualification,
    units,
)
from research_pipeline.agent_constraint_externality_codingplan_provider import (
    CONTEXT_WINDOW,
    MAX_OUTPUT_TOKENS,
    RETRY_MAX_ATTEMPTS,
    RESOLVED_MODEL,
    SAMPLING_CONTROL,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class CodingPlanDeepSeekCapabilityA2Test(unittest.TestCase):
    def test_full_panel_is_eight_new_model_units(self) -> None:
        rows = units()
        self.assertEqual(len(rows), 8)
        self.assertEqual({r.family_id for r in rows}, set(CAPABILITY_FAMILIES))
        self.assertEqual(len({r.unit_id for r in rows}), 8)
        self.assertTrue(all(RESOLVED_MODEL in r.unit_id for r in rows))
        self.assertEqual(TOOL_CAP, 16)

    def test_provider_limits_are_frozen_for_request_efficiency(self) -> None:
        q = build_provider_qualification()
        self.assertEqual(q["context_window"], 512000)
        self.assertEqual(q["max_output_tokens"], 128000)
        self.assertEqual(q["retry_max_attempts"], 1)
        self.assertEqual(q["sampling_control"], SAMPLING_CONTROL)
        unsigned = dict(q); claimed = unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_addendum_changes_provider_model_only_not_gate_or_substrate(self) -> None:
        q = build_provider_qualification(); a = build_addendum(q)
        self.assertEqual(a["status"], "CODINGPLAN_DEEPSEEK_CAPABILITY_A2_AUTHORIZED")
        self.assertEqual(a["model"]["resolved_model"], RESOLVED_MODEL)
        self.assertEqual(a["model"]["context_window"], CONTEXT_WINDOW)
        self.assertEqual(a["model"]["max_output_tokens"], MAX_OUTPUT_TOKENS)
        self.assertEqual(a["model"]["retry_max_attempts"], RETRY_MAX_ATTEMPTS)
        self.assertEqual(a["panel"]["episodes"], 8)
        self.assertEqual(a["panel"]["tool_call_cap"], 16)
        self.assertEqual(a["gate"]["tool_loop_completion_min"], 0.75)
        self.assertEqual(a["gate"]["target_success_min"], 0.50)
        self.assertEqual(a["gate"]["target_success_max"], 0.875)
        self.assertFalse(a["authority"]["f0"])
        self.assertTrue(ACTIVE_BUNDLE.is_file())
        unsigned = dict(a); claimed = unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_frozen_files_match_builders(self) -> None:
        self.assertEqual(json.loads(PROVIDER_QUAL.read_text()), build_provider_qualification())
        q = build_provider_qualification()
        self.assertEqual(json.loads(ADDENDUM.read_text()), build_addendum(q))


if __name__ == "__main__":
    unittest.main()
