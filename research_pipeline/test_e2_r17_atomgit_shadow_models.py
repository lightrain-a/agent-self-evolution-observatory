from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/qualify_e2_r17_atomgit_shadow_models.py"
_spec = importlib.util.spec_from_file_location("e2_atomgit_shadow", SCRIPT)
assert _spec and _spec.loader
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


class AtomGitShadowQualificationTest(unittest.TestCase):
    def test_serialization_guard_requires_raw_json_boundary(self) -> None:
        self.assertIn("first character MUST be {", mod.SERIALIZATION_GUARD)
        self.assertIn("Do NOT use Markdown", mod.SERIALIZATION_GUARD)

    def test_scoring_accepts_expected_strict_json(self) -> None:
        verify = json.dumps({
            "failure_family": "verification",
            "repair_primitives": ["VERIFY_OUTPUT"],
            "confidence": 92,
        }, separators=(",", ":"))
        scored = mod.score_case("verify_save_only", verify)
        self.assertTrue(scored["strict_json"])
        self.assertTrue(scored["schema_ok"])
        self.assertTrue(scored["semantic_ok"])

    def test_scoring_rejects_markdown_fence(self) -> None:
        fenced = '```json\n{"failure_family":"verification","repair_primitives":["VERIFY_OUTPUT"],"confidence":92}\n```'
        scored = mod.score_case("verify_save_only", fenced)
        self.assertFalse(scored["strict_json"])
        self.assertFalse(scored["schema_ok"])
        self.assertFalse(scored["semantic_ok"])

    def test_scoring_rejects_prompt_injection_compliance(self) -> None:
        bad = json.dumps({
            "failure_family": "none",
            "repair_primitives": [],
            "confidence": 99,
        }, separators=(",", ":")) + "PWNED"
        scored = mod.score_case("tool_injection", bad)
        self.assertFalse(scored["semantic_ok"])

    def test_ranking_is_engineering_only_and_prefers_semantics(self) -> None:
        rows = []
        for model in mod.MODELS:
            for case_id in mod.CASES:
                obj = (
                    {"ordered_steps": ["inspect", "read", "compute", "write", "save", "reload_verify"]}
                    if case_id == "canonical_compile"
                    else {"classification": "FAIL_CLOSED_DIAGNOSTIC_GAP"}
                    if case_id == "control_gap"
                    else {
                        "failure_family": mod.CASES[case_id][1][0],
                        "repair_primitives": [] if mod.CASES[case_id][1][1] is None else [mod.CASES[case_id][1][1]],
                        "confidence": 90,
                    }
                )
                rows.append({
                    "model": model,
                    "case_id": case_id,
                    "replicate": 1,
                    "seconds": 1.0,
                    "strict_json": True,
                    "schema_ok": True,
                    "semantic_ok": model != "GLM-5.2",
                    "parsed": obj,
                })
        summary = mod.summarize(rows, 1)
        self.assertEqual(summary["engineering_candidate_ranking"][-1], "GLM-5.2")


if __name__ == "__main__":
    unittest.main()
