from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from .config import PROJECT_ROOT


PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
RECEIPT = PROJECT_ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825" / "manuscript-strengthening-receipt.json"
SOURCE = PROJECT_ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825" / "source"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class C1StageResolvedStoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.story = (PROJECT_ROOT / "paper-story-reward-memory.js").read_text(encoding="utf-8")
        cls.golden = (PROJECT_ROOT / "current-paper-golden-c1.js").read_text(encoding="utf-8")
        cls.depth = (PROJECT_ROOT / "current-paper-depth-c1.js").read_text(encoding="utf-8")
        cls.reader = (PROJECT_ROOT / "paper-reader-data.js").read_text(encoding="utf-8")
        cls.page = (PROJECT_ROOT / "current-paper-pages-data.js").read_text(encoding="utf-8")
        cls.abstract = (SOURCE / "sections" / "00_abstract.tex").read_text(encoding="utf-8")
        cls.intro = (SOURCE / "sections" / "01_intro.tex").read_text(encoding="utf-8")
        cls.mechanism = (SOURCE / "sections" / "02_mechanism.tex").read_text(encoding="utf-8")
        cls.results = (SOURCE / "sections" / "04_variance_protocol.tex").read_text(encoding="utf-8")

    def test_receipt_is_zero_execution_and_artifacts_are_content_addressed(self) -> None:
        self.assertEqual(self.receipt["paper_id"], PAPER_ID)
        self.assertEqual(self.receipt["new_story"]["paper_archetype"], "causal_identification")
        self.assertEqual(self.receipt["execution"]["new_scientific_provider_calls"], 0)
        self.assertEqual(self.receipt["execution"]["new_gpu_scientific_runs"], 0)
        self.assertEqual(self.receipt["execution"]["new_scientific_experiments"], 0)
        self.assertFalse(any(self.receipt["authority"].values()))
        for key in ("pdf", "source_zip"):
            row = self.receipt["artifacts"][key]
            path = PROJECT_ROOT / row["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(sha256(path), row["sha256"])

    def test_forced_leverage_and_native_transport_are_distinct_estimands(self) -> None:
        split = self.receipt["new_story"]["estimand_split"]
        self.assertIn("exposure=1", split["forced_fixed_evidence"])
        self.assertIn("retrieval", split["native_pipeline"])
        combined = "\n".join((self.abstract, self.intro, self.mechanism, self.results))
        self.assertIn("forced", combined.lower())
        self.assertIn("leverage", combined.lower())
        self.assertIn("native", combined.lower())
        self.assertIn("retrieval exposure", combined.lower())
        self.assertIn("policy uptake", combined.lower())
        self.assertNotIn("variance amplification", combined.lower())

    def test_frozen_native_negative_boundaries_are_main_text_not_hidden(self) -> None:
        combined = "\n".join((self.abstract, self.intro, self.results))
        for marker in ("125/172", "0.02083", "0.4289", "34/36", "0.06944", "0.5801", "0/36", "0.125", "0.2253", "6/8"):
            self.assertIn(marker, combined)
        self.assertIn("opposite signs", combined.lower())

    def test_reader_and_story_do_not_revert_to_forced_equals_native_claim(self) -> None:
        self.assertIn("paper_archetype:\"causal_identification\"", self.story)
        self.assertIn("forced leverage", self.story.lower())
        self.assertIn("native transport", self.story.lower())
        self.assertIn("Forced leverage ≠ native transport", self.reader)
        self.assertIn("125/172", self.reader)
        self.assertIn("0.02083", self.reader)
        self.assertNotIn("propagates from memory construction to later behavior", self.reader)
        self.assertIn("retrieval, first-action uptake, and terminal outcome separately", self.page)
        self.assertIn("actual task outcome", self.page)
        self.assertIn("actual task outcome", self.story)
        self.assertIn("normal runtime", self.story.lower())
        self.assertIn("not two truths for one real shopping event", self.story.lower())

    def test_claim_hierarchy_preserves_method_stop_without_failing_measurement_paper(self) -> None:
        claims = {row["claim"]: row for row in self.receipt["claim_hierarchy"]}
        self.assertEqual(claims["write intervention"]["status"], "SUPPORTED")
        self.assertEqual(claims["forced latent leverage"]["status"], "SUPPORTED")
        self.assertEqual(claims["native Shopping branch-specific behavioral transport"]["status"], "ATTENUATED_UNRESOLVED")
        self.assertEqual(claims["CBRG method extension"]["status"], "STOP_MERGE_CURRENT_EXTENSION")
        self.assertIn("no behavioral method-effect experiment", claims["CBRG method extension"]["boundary"].lower())

    def test_diagnosis_to_repair_bridge_separates_relevance_from_authority(self) -> None:
        combined = "\n".join((self.story, self.golden, self.depth)).lower()
        self.assertIn("pacta-msr", combined)
        self.assertIn("matched state reveal", combined)
        self.assertIn("rate-matched random", combined)
        self.assertIn("behavioral authority", combined)
        self.assertIn("relevance", combined)
        self.assertIn("within-condition", combined)
        self.assertIn("prospective", combined)
        self.assertIn("method-effect claim", combined)
        self.assertIn("0.20", combined)
        self.assertNotIn("pacta-msr improves", combined)
        self.assertNotIn("pacta-msr outperforms", combined)


if __name__ == "__main__":
    unittest.main()
