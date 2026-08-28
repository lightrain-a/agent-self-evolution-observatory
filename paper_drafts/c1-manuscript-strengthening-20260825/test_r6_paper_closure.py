from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class C1R6PaperClosureTest(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((HERE / name).read_text(encoding="utf-8"))

    def test_r6_sealed_artifacts_are_content_addressed(self) -> None:
        self.assertEqual(sha(HERE / "C1-stage-resolved-r6-final.pdf"), "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70")
        self.assertEqual(sha(HERE / "C1-stage-resolved-r6-final-source.zip"), "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b")
        self.assertEqual((SRC / "main.pdf").read_bytes(), (HERE / "C1-stage-resolved-r6-final.pdf").read_bytes())

    def test_claim_audit_is_replayable_and_complete(self) -> None:
        audit = self.load("claim-audit-r6-provenance-seal-20260828.json")
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["summary"], {"claims_total": 35, "claims_passed": 35, "claims_failed": 0})
        audit_sha = "715721a221a2bfb942fffa43c65aba52f1754ce3d1f99006f13bc32ef4b6e332"
        runner_sha = "7e4bde4dafdecb9d2fa0d39e98e889382dd47661c78ab7d33c997bcad0eb5743"
        registry_sha = "ad034d2da0bc99af0506aca1686c9adb5e8247875fb10a3de5b63cda1397cfbc"
        self.assertEqual(sha(HERE / "claim-audit-r6-provenance-seal-20260828.json"), audit_sha)
        self.assertEqual((HERE / "provenance" / "sha256" / f"{audit_sha}.json").read_bytes(), (HERE / "claim-audit-r6-provenance-seal-20260828.json").read_bytes())
        self.assertEqual((HERE / "provenance" / "runners" / "sha256" / f"{runner_sha}.py").read_bytes(), (HERE / "run_claim_audit_r6.py").read_bytes())
        self.assertEqual((HERE / "provenance" / "registries" / "sha256" / f"{registry_sha}.json").read_bytes(), (HERE / "claim-audit-r6-registry-20260828.json").read_bytes())

    def test_provenance_reconciliation_preserves_history_without_rewriting_it(self) -> None:
        row = self.load("c1-r6-provenance-reconciliation-20260828.json")
        self.assertEqual(row["status"], "R5_TO_R6_PROVENANCE_RECONCILED_PASS")
        self.assertEqual(row["historical_r5"]["targeted_repair_recheck_sha256"], "4cf54f084d96a9079f46e3008acfd5489b6c478aff67a3421bd69cc5467bb3c5")
        self.assertEqual(row["historical_r5"]["stale_internal_sensitivity_sha256"], "22ffb994b77a32b309da4d0bf945a3b5ad4fe43ce96476b11e5ecb98a1ea9ef0")
        self.assertEqual(row["canonical_r6"]["sensitivity_sha256"], "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba")
        self.assertTrue(row["historical_r5"]["historical_bytes_rewritten"] is False)
        self.assertTrue(row["adjudication"]["scientific_contract_changed"] is False)
        self.assertTrue(row["adjudication"]["scientific_result_changed"] is False)
        self.assertEqual(row["authority"], {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False})

    def test_pdf_qa_is_nine_of_nine_and_rebuild_exact(self) -> None:
        qa = self.load("paper-qa-r6-provenance-reconciled-20260828.json")
        self.assertEqual(qa["status"], "PASS")
        self.assertEqual((qa.get("summary") or {}).get("checks_passed"), 10)
        self.assertEqual((qa.get("summary") or {}).get("checks_total"), 10)
        self.assertTrue((qa.get("summary") or {}).get("claim_audit_content_addressed"))
        self.assertTrue((qa.get("summary") or {}).get("source_rebuild_byte_equal"))
        self.assertEqual((qa.get("summary") or {}).get("main_text_pages"), 9)
        self.assertEqual((qa.get("summary") or {}).get("references_start_page"), 10)
        self.assertEqual((qa.get("summary") or {}).get("total_pdf_pages"), 13)
        self.assertTrue(all((qa.get("checks") or {}).values()))
        self.assertEqual(qa["authority"], {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False})


if __name__ == "__main__":
    unittest.main()
