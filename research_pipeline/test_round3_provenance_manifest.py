from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .round3_provenance_manifest import (
    AUTHORITY,
    POLICY,
    SCHEMA_VERSION,
    _sha,
    load_round3_provenance_manifest,
    validate_round3_provenance_manifest,
)


class Round3ProvenanceManifestTest(unittest.TestCase):
    def _valid_manifest(self) -> dict:
        state = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": "2026-08-21T00:00:00+00:00",
            "status": "ROUND3_PROVENANCE_COMPLETE",
            "policy": dict(POLICY),
            "transaction": {"status": "COMMITTED"},
            "summary": {},
            "coverage": {"record_level_lineage_complete": True},
            "generation_slots": [],
            "raw_seed_dispositions": [],
            "branch_nodes": [],
            "formulation_inputs": [],
            "candidate_routes": [],
            "scientific_authority": False,
            "authority": dict(AUTHORITY),
        }
        state["manifest_content_sha256"] = _sha(
            {
                key: value
                for key, value in state.items()
                if key not in {"generated_at", "manifest_content_sha256"}
            }
        )
        return state

    def test_validator_accepts_complete_zero_authority_manifest(self) -> None:
        state = self._valid_manifest()
        self.assertEqual(validate_round3_provenance_manifest(state), [])

    def test_validator_fails_closed_on_authority_or_content_tamper(self) -> None:
        state = self._valid_manifest()
        state["authority"]["experiment"] = True
        errors = validate_round3_provenance_manifest(state)
        self.assertIn("authority-leak", errors)
        self.assertIn("content-hash-mismatch", errors)

    def test_loader_quarantines_invalid_manifest_without_scientific_authority(self) -> None:
        state = self._valid_manifest()
        state["manifest_content_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            loaded = load_round3_provenance_manifest(path)
        self.assertEqual(loaded["status"], "ROUND3_PROVENANCE_INVALID")
        self.assertFalse(loaded["scientific_authority"])
        self.assertFalse(loaded["coverage"]["record_level_lineage_complete"])
        self.assertTrue(all(value is False for value in loaded["authority"].values()))


if __name__ == "__main__":
    unittest.main()
