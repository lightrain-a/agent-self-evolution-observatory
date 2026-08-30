from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_q3_acquire import (
    SPECS, descriptors,
)


class ReasoningBankP1Q3AcquisitionTest(unittest.TestCase):
    def test_fixed_manifests_define_expected_blob_set(self) -> None:
        blobs = descriptors()
        self.assertEqual(len(blobs), 15)
        self.assertEqual(sum(row["size"] for row in blobs.values()), 1_592_240_723)
        self.assertTrue(all(digest.startswith("sha256:") for digest in blobs))
        self.assertTrue(all(row["size"] > 0 for row in blobs.values()))

    def test_exact_amd64_manifest_digests_are_frozen(self) -> None:
        self.assertEqual(
            {spec["label"]: spec["digest"] for spec in SPECS},
            {
                "sphinx9230": "036fb5014ef0054831e7218af5addb8957f527fe4a01bf6d4b6e1eebfdd4fca1",
                "django11880": "4488d53c0526d3a4e679753beb3501d70253a1f687274ef9c2ed07e7225dde6c",
            },
        )


if __name__ == "__main__":
    unittest.main()
