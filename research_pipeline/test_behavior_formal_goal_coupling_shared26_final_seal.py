from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import behavior_formal_goal_coupling_shared26_final_seal as seal


def _manifest(rows: list[dict]) -> dict:
    total = sum(row["lfs_size_bytes"] for row in rows)
    return {
        "object_id": seal.OBJECT_ID,
        "bindings": {"dataset_revision": seal.DATASET_REVISION},
        "required_payload": rows,
        "summary": {
            "required_payload_file_count": len(rows),
            "required_payload_bytes": total,
        },
    }


def _row(path: str, content: bytes) -> dict:
    return {
        "path": path,
        "lfs_size_bytes": len(content),
        "lfs_oid_sha256": hashlib.sha256(content).hexdigest(),
    }


class FinalSealTest(unittest.TestCase):
    def test_inspect_root_pass(self) -> None:
        a = b"alpha"
        b = b"beta-data"
        rows = [_row("a.bin", a), _row("nested/b.bin", b)]
        with tempfile.TemporaryDirectory() as td, patch.object(seal, "EXPECTED_FILE_COUNT", 2), patch.object(
            seal, "EXPECTED_BYTES", len(a) + len(b)
        ):
            root = Path(td)
            (root / "a.bin").write_bytes(a)
            (root / "nested").mkdir()
            (root / "nested/b.bin").write_bytes(b)

            result = seal.inspect_root(_manifest(rows), root)

        self.assertTrue(result["passed"])
        self.assertEqual(result["verified_file_count"], 2)
        self.assertEqual(result["verified_bytes"], len(a) + len(b))
        self.assertEqual(result["partial_file_count"], 0)

    def test_inspect_root_fails_closed_on_bad_or_partial(self) -> None:
        a = b"alpha"
        b = b"beta-data"
        rows = [_row("a.bin", a), _row("nested/b.bin", b)]
        with tempfile.TemporaryDirectory() as td, patch.object(seal, "EXPECTED_FILE_COUNT", 2), patch.object(
            seal, "EXPECTED_BYTES", len(a) + len(b)
        ):
            root = Path(td)
            (root / "a.bin").write_bytes(b"wrong")
            (root / "nested").mkdir()
            (root / "nested/b.bin.part").write_bytes(b)

            result = seal.inspect_root(_manifest(rows), root)

        self.assertFalse(result["passed"])
        self.assertEqual(result["size_mismatch_count"], 0)
        self.assertEqual(result["sha_mismatch_count"], 1)
        self.assertEqual(result["missing_file_count"], 1)
        self.assertEqual(result["partial_file_count"], 1)


if __name__ == "__main__":
    unittest.main()
