from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_q2_acquire import (
    SPECS, descriptors,
)


class ReasoningBankP1Q2AcquisitionTest(unittest.TestCase):
    def test_fixed_manifests_define_expected_blob_set(self) -> None:
        blobs = descriptors()
        self.assertEqual(len(blobs), 15)
        self.assertEqual(sum(row["size"] for row in blobs.values()), 1_635_261_485)
        self.assertTrue(all(digest.startswith("sha256:") for digest in blobs))
        self.assertTrue(all(row["size"] > 0 for row in blobs.values()))

    def test_exact_amd64_manifest_digests_are_frozen(self) -> None:
        self.assertEqual(
            {spec["label"]: spec["digest"] for spec in SPECS},
            {
                "django16100": "07524a702c042e0baa5725c35e2e1ae8c8f50a221682b5bf21ff26438fc46fdd",
                "sympy18211": "c92da16cfc8ba1c304c3fd0bf991aba569cc5eaa99a85fb3953c60f09de2c7ca",
            },
        )


if __name__ == "__main__":
    unittest.main()
