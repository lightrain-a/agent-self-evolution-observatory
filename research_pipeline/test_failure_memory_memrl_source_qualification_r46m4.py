from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_memrl_source_qualification_r46m4 import rebase_working_copy_pointers


class R46M4PointerRepairTests(unittest.TestCase):
    def test_rebases_only_absolute_snapshot_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "working"
            (root / "cube").mkdir(parents=True)
            (root / "qdrant").mkdir()
            meta = {
                "user_id": "u",
                "checkpoint_id": "source-128-78",
                "cube_dir": "/original/cube",
                "qdrant_dir": "/original/qdrant",
                "textual_memory_md5": "abc",
                "visible_memories": 0,
            }
            (root / "snapshot_meta.json").write_text(json.dumps(meta), encoding="utf-8")
            audit = rebase_working_copy_pointers(root)
            out = json.loads((root / "snapshot_meta.json").read_text())
            self.assertEqual(out["cube_dir"], str((root / "cube").resolve()))
            self.assertEqual(out["qdrant_dir"], str((root / "qdrant").resolve()))
            self.assertEqual(out["user_id"], "u")
            self.assertEqual(out["checkpoint_id"], "source-128-78")
            self.assertEqual(out["textual_memory_md5"], "abc")
            self.assertEqual(out["visible_memories"], 0)
            self.assertEqual(audit["changed_fields"], ["cube_dir", "qdrant_dir"])
            self.assertTrue(audit["nonpointer_fields_byte_semantics_preserved"])

    def test_rejects_missing_absolute_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "working"
            (root / "cube").mkdir(parents=True)
            (root / "qdrant").mkdir()
            (root / "snapshot_meta.json").write_text(json.dumps({"cube_dir": "", "qdrant_dir": "/x"}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "absolute-pointers-missing"):
                rebase_working_copy_pointers(root)

    def test_rejects_already_rebased_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "working"
            (root / "cube").mkdir(parents=True)
            (root / "qdrant").mkdir()
            (root / "snapshot_meta.json").write_text(json.dumps({
                "cube_dir": str((root / "cube").resolve()),
                "qdrant_dir": str((root / "qdrant").resolve()),
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "pointer-already-rebased"):
                rebase_working_copy_pointers(root)


if __name__ == "__main__":
    unittest.main()
