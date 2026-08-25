from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import port010_vwe_firstparty_preanalysis as p


class Port010VweFirstPartyPreanalysisTest(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path]:
        metadata = root / "metadata"
        source = root / "source"
        metadata.mkdir(parents=True)
        source.mkdir(parents=True)
        rows = [
            {"id": "001", "source_dir": "10___type8", "query_type": "Complex description", "query_tag": "type8", "query_category": p.QUERY_CATEGORY, "verifier_type": p.VERIFIER_TYPE},
            {"id": "002", "source_dir": "10___type6", "query_type": "Scene guidance", "query_tag": "type6", "query_category": p.QUERY_CATEGORY, "verifier_type": p.VERIFIER_TYPE},
            {"id": "003", "source_dir": "10___type5", "query_type": "Scene critique", "query_tag": "type5", "query_category": p.QUERY_CATEGORY, "verifier_type": p.VERIFIER_TYPE},
            {"id": "004", "source_dir": "20___type6", "query_type": "Scene guidance", "query_tag": "type6", "query_category": p.QUERY_CATEGORY, "verifier_type": p.VERIFIER_TYPE},
        ]
        (metadata / "index.json").write_text(json.dumps(rows), encoding="utf-8")
        for row in rows:
            case = metadata / row["id"]
            case.mkdir()
            (case / "query.json").write_text(
                json.dumps(
                    {
                        "description": f"place objects near the center for {row['id']}",
                        "query_category": row["query_category"],
                        "query_tag": row["query_tag"],
                        "query_type": row["query_type"],
                        "theme": "fixture",
                        "verification_criteria": [],
                        "verifier_type": row["verifier_type"],
                    }
                ),
                encoding="utf-8",
            )
        for rel in ("eval.py", "verifier/eval.py", "verifier/unverified_verifier.py", "verifier/prompts.py", "main.py"):
            path = source / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# pinned fixture\n", encoding="utf-8")
        return metadata, source

    def compile_fixture(self, metadata: Path, source: Path) -> dict:
        with patch.object(p, "EXPECTED_TEST_CASES", 4), patch.object(p, "EXPECTED_TARGET_CASES", 1), patch.object(p, "EXPECTED_TARGET_GROUPS", 1), patch.object(p, "EXPECTED_ANALYSIS_CASES", 3), patch.object(p, "EXPECTED_CONTROL_CASES", 2):
            return p.compile_preanalysis(metadata_root=metadata, source_root=source)

    def test_freezes_within_source_same_route_cohort_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            metadata, source = self.fixture(Path(td))
            out = self.compile_fixture(metadata, source)
        self.assertEqual(out["status"], "PREOUTCOME_MATCHED_DESIGN_PROPOSAL_ONLY")
        self.assertFalse(out["scientific_authority"])
        self.assertFalse(out["execution_authority"])
        self.assertFalse(out["design_review_authority"])
        self.assertFalse(out["outcomes_read"])
        self.assertEqual(out["cohort"]["cases"], 3)
        self.assertEqual(out["cohort"]["target_cases"], 1)
        self.assertEqual(out["cohort"]["control_cases"], 2)
        self.assertEqual(out["cohort"]["source_groups"], 1)
        self.assertEqual({row["source_group"] for row in out["cohort"]["rows"]}, {"10"})
        self.assertEqual(out["pre_registered_analysis"]["mechanism_decomposition"]["intent_understanding_failure"], "official H3_VU score < 4")
        self.assertTrue(any("No main.py/eval.py" in item for item in out["remaining_gates"]))

    def test_rejects_outcome_bearing_metadata_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            metadata, source = self.fixture(Path(td))
            (metadata / "001" / "final_map.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outcome-bearing"):
                self.compile_fixture(metadata, source)

    def test_source_group_parser_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "delimiter"):
            p._source_group("10-type8")


if __name__ == "__main__":
    unittest.main()
