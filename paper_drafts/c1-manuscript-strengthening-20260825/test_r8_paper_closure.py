from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_R6 = HERE / "source"
SRC_R7 = HERE / "source-r7"
SRC_R8 = HERE / "source-r8"

R6_PDF_SHA = "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70"
R7_PDF_SHA = "a5ce511a11a7781ca5374e0f54f7830454927874ca8dc6112c87e6106ab20167"
R7_ZIP_SHA = "91af2cd961a0633b31e2ba38fb1e3f2abcf6db4013dd44977d7b1d2cf8fcc76e"
R8_PDF_SHA = "271ceab8b74555bbd891740c963dd9af71c29cb039f218a842f13a57c435bec6"
R8_ZIP_SHA = "95771a4c4efeae7f37a0a10ba030c216f5137d467a5af174907f2d9556894f81"
AUDIT_SHA = "e910240ebeb5ebd93f0ab2ee46778199099c95a3222fe3039edb22d998de8c43"
RUNNER_SHA = "858f52d4477789139948fe57565a99846abaa26b71dee963968a86017c08f025"
REGISTRY_SHA = "b5d6023122c1427193e4e0e9244d917c9ac866eb7f1ed1f92f46062fe40f625f"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class C1R8PaperClosureTest(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((HERE / name).read_text(encoding="utf-8"))

    def test_r6_and_r7_remain_immutable(self) -> None:
        self.assertEqual(sha(HERE / "C1-stage-resolved-r6-final.pdf"), R6_PDF_SHA)
        self.assertEqual((SRC_R6 / "main.pdf").read_bytes(), (HERE / "C1-stage-resolved-r6-final.pdf").read_bytes())
        self.assertEqual(sha(HERE / "C1-stage-resolved-r7-review-repair.pdf"), R7_PDF_SHA)
        self.assertEqual(sha(HERE / "C1-stage-resolved-r7-review-repair-source.zip"), R7_ZIP_SHA)

    def test_r8_artifacts_are_separate_and_sealed(self) -> None:
        self.assertTrue(SRC_R8.is_dir())
        self.assertTrue(SRC_R7.is_dir())
        self.assertEqual(sha(HERE / "C1-stage-resolved-r8-negative-repair.pdf"), R8_PDF_SHA)
        self.assertEqual(sha(HERE / "C1-stage-resolved-r8-negative-repair-source.zip"), R8_ZIP_SHA)
        self.assertNotEqual((SRC_R8 / "sections" / "04_variance_protocol.tex").read_bytes(), (SRC_R7 / "sections" / "04_variance_protocol.tex").read_bytes())
        self.assertEqual((SRC_R8 / "sections" / "03_f0.tex").read_bytes(), (SRC_R7 / "sections" / "03_f0.tex").read_bytes())
        self.assertEqual((SRC_R8 / "sections" / "03a_prompt_control.tex").read_bytes(), (SRC_R7 / "sections" / "03a_prompt_control.tex").read_bytes())

    def test_r8_claim_audit_is_replayable_and_cas_bound(self) -> None:
        audit = HERE / "claim-audit-r8-provenance-seal-20260829.json"
        runner = HERE / "run_claim_audit_r8.py"
        registry = HERE / "claim-audit-r8-registry-20260829.json"
        self.assertEqual(sha(audit), AUDIT_SHA)
        self.assertEqual(sha(runner), RUNNER_SHA)
        self.assertEqual(sha(registry), REGISTRY_SHA)
        self.assertEqual((HERE / "provenance" / "sha256" / f"{AUDIT_SHA}.json").read_bytes(), audit.read_bytes())
        self.assertEqual((HERE / "provenance" / "runners" / "sha256" / f"{RUNNER_SHA}.py").read_bytes(), runner.read_bytes())
        self.assertEqual((HERE / "provenance" / "registries" / "sha256" / f"{REGISTRY_SHA}.json").read_bytes(), registry.read_bytes())
        proc = subprocess.run([sys.executable, str(runner), "--check"], cwd=HERE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn('"status": "REPLAY_PASS"', proc.stdout)
        self.assertIn('"claims_passed": 26', proc.stdout)

    def test_r8_manifest_consumes_new_pilot_without_unlocking_full(self) -> None:
        manifest = self.load("c1-r8-package-manifest-20260829.json")
        self.assertEqual(manifest["status"], "R8_NEGATIVE_REPAIR_PILOT_PAPER_PACKAGE_SEALED")
        self.assertTrue(manifest["scientific_results_changed"])
        self.assertFalse(manifest["scientific_contract_changed"])
        self.assertFalse(manifest["claim_expansion"])
        self.assertTrue(manifest["claim_narrowing"])
        evidence = manifest["new_scientific_evidence"]
        self.assertEqual(evidence["pilot_calls_complete"], 312)
        self.assertEqual(evidence["pilot_failed_cases"], 0)
        self.assertFalse(evidence["pilot_gate_pass"])
        self.assertFalse(evidence["confirmatory_full_executed"])
        self.assertEqual(evidence["confirmatory_holdout_new_calls"], 0)
        self.assertFalse(any(manifest["authority"].values()))

    def test_r8_paper_qa_passes_and_main_text_is_within_limit(self) -> None:
        qa = self.load("paper-qa-r8-20260829.json")
        self.assertEqual(qa["status"], "PASS")
        checks = qa["checks"]
        self.assertEqual(checks["claim_audit_replay"], "26/26 PASS")
        self.assertEqual(checks["total_pdf_pages"], 12)
        self.assertTrue(checks["main_text_with_conclusion_within_9_pages"])
        self.assertEqual(checks["latex_undefined_or_overfull_warnings"], 0)
        self.assertEqual(checks["bibtex_warnings"], 0)
        self.assertEqual(checks["render_margin_smoke"], "PASS")
        self.assertTrue(checks["fonts_embedded"])

    def test_r8_preserves_negative_repair_boundary(self) -> None:
        text = "\n".join((SRC_R8 / "sections" / name).read_text(encoding="utf-8") for name in [
            "00_abstract.tex", "01_intro.tex", "02_mechanism.tex", "04_variance_protocol.tex", "06_limitations_conclusion.tex", "07_appendix.tex"
        ])
        lower = text.lower()
        for marker in ["312", "0.09615", "3/13", "23-state confirmatory", "diagnosis identifies where evidence weakens", "diagnosis is not repair"]:
            self.assertIn(marker.lower(), lower)
        self.assertIn("negative diagnosis-guided repair pilot", lower)
        self.assertIn("not supported as an actionable repair", lower)
        self.assertNotIn("falsified repair realization", lower)
        self.assertNotIn("falsifies only", lower)
        self.assertIn("the 23-state confirmatory experiment is not run", lower)


if __name__ == "__main__":
    unittest.main()
