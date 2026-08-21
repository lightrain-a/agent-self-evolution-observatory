from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .relation_scan_boundary_manifest import (
    boundary_receipts,
    build_relation_scan_boundary_manifest,
    relation_universe_digest,
    validate_relation_scan_boundary_manifest,
)


class RelationScanBoundaryManifestTest(unittest.TestCase):
    def test_archived_receipts_recover_exact_zero_authority_scan_boundary(self) -> None:
        archived_receipts = [
            {
                "run_id": "20260801T000000Z",
                "source_refs": ["arXiv:1", "arXiv:2", "arXiv:3"],
                "scientific_authority": False,
            },
            {
                "run_id": "20260802T000000Z",
                "source_refs": ["arXiv:2", "arXiv:3", "arXiv:4"],
                "scientific_authority": False,
            },
        ]
        digest = relation_universe_digest(archived_receipts)
        generator = {
            "saturation_memory": {"portable_review_receipts": archived_receipts}
        }
        relation = {
            "last_completed_scan": {
                "run_id": "20260803T000000Z",
                "relation_universe_digest": digest,
                "relation_coverage": {
                    "reviewed_receipt_sources": 4,
                    "coobserved_source_pairs": 5,
                },
            },
            "raw_artifacts": {"relation": {"sha256": "a" * 64}},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generator_path = root / "generator.json"
            relation_path = root / "relation.json"
            generator_path.write_text(json.dumps(generator), encoding="utf-8")
            relation_path.write_text(json.dumps(relation), encoding="utf-8")
            manifest = build_relation_scan_boundary_manifest(
                archived_generator_path=generator_path,
                relation_path=relation_path,
            )
        self.assertEqual(validate_relation_scan_boundary_manifest(manifest), [])
        self.assertEqual(manifest["scan_binding"]["reviewed_sources"], 4)
        self.assertEqual(manifest["scan_binding"]["coobserved_source_pairs"], 5)
        self.assertEqual(len(boundary_receipts(manifest, relation)), 2)
        self.assertFalse(manifest["scientific_authority"])
        self.assertTrue(all(value is False for value in manifest["authority"].values()))

    def test_tampered_manifest_fails_closed(self) -> None:
        manifest = {
            "status": "RELATION_SCAN_BOUNDARY_INVALID",
            "scientific_authority": False,
            "authority": {"provider_calls": False},
        }
        self.assertTrue(validate_relation_scan_boundary_manifest(manifest))
        self.assertEqual(boundary_receipts(manifest, {}), [])


if __name__ == "__main__":
    unittest.main()
