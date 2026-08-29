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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class C1R7PaperClosureTest(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((HERE / name).read_text(encoding="utf-8"))

    def test_r6_source_and_replay_remain_immutable(self) -> None:
        self.assertEqual(sha(HERE / "C1-stage-resolved-r6-final.pdf"), "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70")
        self.assertEqual((SRC_R6 / "main.pdf").read_bytes(), (HERE / "C1-stage-resolved-r6-final.pdf").read_bytes())
        proc = subprocess.run([sys.executable, str(HERE / "run_claim_audit_r6.py"), "--check"], cwd=HERE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn('"status": "REPLAY_PASS"', proc.stdout)

    def test_r7_artifacts_are_sealed_and_content_addressed(self) -> None:
        self.assertEqual(sha(HERE / "C1-stage-resolved-r7-review-repair.pdf"), "a5ce511a11a7781ca5374e0f54f7830454927874ca8dc6112c87e6106ab20167")
        self.assertEqual(sha(HERE / "C1-stage-resolved-r7-review-repair-source.zip"), "91af2cd961a0633b31e2ba38fb1e3f2abcf6db4013dd44977d7b1d2cf8fcc76e")
        audit_sha = "baad7e26fa297412c3959bb58d2df5bdd04d3de52d1175f6b0ea5e14d8caf4cf"
        runner_sha = "7d5bea14b3ca0e7fe7738ec182c3afb6f73bdf644a932b2966ec9b21f3ac8ac3"
        registry_sha = "4f9c7992437464c79d4c2ba71bfabe8f8e66638d72529c408eb8b11fbb3d8ebe"
        self.assertEqual(sha(HERE / "claim-audit-r7-provenance-seal-20260829.json"), audit_sha)
        self.assertEqual((HERE / "provenance" / "sha256" / f"{audit_sha}.json").read_bytes(), (HERE / "claim-audit-r7-provenance-seal-20260829.json").read_bytes())
        self.assertEqual((HERE / "provenance" / "runners" / "sha256" / f"{runner_sha}.py").read_bytes(), (HERE / "run_claim_audit_r7.py").read_bytes())
        self.assertEqual((HERE / "provenance" / "registries" / "sha256" / f"{registry_sha}.json").read_bytes(), (HERE / "claim-audit-r7-registry-20260829.json").read_bytes())

    def test_r7_is_paper_only_and_source_separated(self) -> None:
        manifest = self.load("c1-r7-package-manifest-20260829.json")
        self.assertEqual(manifest["status"], "R7_PAPER_ONLY_REVIEW_REPAIR_PACKAGE_SEALED")
        self.assertTrue(manifest["paper_only_revision"])
        self.assertFalse(manifest["scientific_contract_changed"])
        self.assertFalse(manifest["scientific_results_changed"])
        self.assertFalse(manifest["claim_expansion"])
        self.assertEqual(manifest["execution"]["new_scientific_provider_calls"], 0)
        self.assertEqual(manifest["execution"]["new_gpu_scientific_runs"], 0)
        self.assertEqual(manifest["execution"]["new_scientific_experiments"], 0)
        self.assertTrue(SRC_R7.is_dir())
        self.assertNotEqual((SRC_R6 / "sections" / "02_mechanism.tex").read_bytes(), (SRC_R7 / "sections" / "02_mechanism.tex").read_bytes())

    def test_r7_preserves_review_repair_boundaries(self) -> None:
        mechanism = (SRC_R7 / "sections" / "02_mechanism.tex").read_text(encoding="utf-8")
        results = (SRC_R7 / "sections" / "04_variance_protocol.tex").read_text(encoding="utf-8")
        limits = (SRC_R7 / "sections" / "06_limitations_conclusion.tex").read_text(encoding="utf-8")
        joined = "\n".join((mechanism, results, limits))
        self.assertIn("treatment-residual exposure", joined)
        self.assertIn("first unsupported measured native stage", joined)
        self.assertIn("not a causal mediation coefficient", joined)
        self.assertIn("Multiplicity and interpretation", mechanism)
        self.assertIn("36 such matched comparison units", mechanism)
        self.assertIn("branch-differentiating content is actually consumed downstream", limits)


if __name__ == "__main__":
    unittest.main()
