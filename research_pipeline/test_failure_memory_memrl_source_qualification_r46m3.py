from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline import failure_memory_memrl_source_qualification_r46m3 as m3


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


class R46M3SnapshotInterfaceTests(unittest.TestCase):
    def make_snapshot(self, root: Path, selected: list[str], visible: int = 0) -> tuple[Path, Path]:
        cp = root / "checkpoint"
        (cp / "cube").mkdir(parents=True)
        (cp / "qdrant" / "collection" / "live").mkdir(parents=True)
        memories = []
        for i, tid in enumerate(selected):
            memories.append({
                "id": f"m{i}",
                "vector": [0.0],
                "payload": {
                    "id": f"m{i}",
                    "memory": f"memory-{tid}",
                    "metadata": {"sample_index": int(tid), "task_id": int(tid), "success": i % 2 == 0},
                },
            })
        textual = cp / "cube" / "textual_memory.json"
        textual.write_text(json.dumps(memories), encoding="utf-8")
        (cp / "qdrant" / "meta.json").write_text(json.dumps({"collections": {"live": {}}}), encoding="utf-8")
        (cp / "qdrant" / "collection" / "live" / "storage.sqlite").write_bytes(b"qdrant")
        meta = {
            "checkpoint_id": f"source-{len(selected):03d}-{selected[-1]}",
            "textual_memory_md5": _md5(textual),
            "visible_memories": visible,
        }
        (cp / "snapshot_meta.json").write_text(json.dumps(meta), encoding="utf-8")
        ledger = root / "completed.jsonl"
        rows = []
        for i, tid in enumerate(selected):
            rows.append({
                "position": i,
                "task_id": tid,
                "success": i % 2 == 0,
                "checkpoint_snapshot_root": str(cp if i == len(selected) - 1 else root / f"unused-{i}"),
                "checkpoint_textual_memory_md5": meta["textual_memory_md5"] if i == len(selected) - 1 else "unused",
            })
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return cp, ledger

    def test_zero_visible_counter_is_not_used_when_snapshot_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            selected = ["1", "2"]
            cp, ledger = self.make_snapshot(root, selected, visible=0)
            work = root / "work"
            m3._WORKING_COPY_ROOT = work
            m3._SNAPSHOT_AUDIT = None
            returned, last = m3.snapshot_backed_last_checkpoint(ledger, selected)
            self.assertEqual(returned, work)
            self.assertEqual(last["task_id"], "2")
            self.assertTrue(work.is_dir())
            self.assertEqual(m3._SNAPSHOT_AUDIT["snapshot_meta_visible_memories_diagnostic"], 0)
            self.assertFalse(m3._SNAPSHOT_AUDIT["visible_memories_field_used_for_qualification"])
            self.assertEqual(m3._SNAPSHOT_AUDIT["actual_textual_memory_entries"], 2)
            self.assertEqual(m3._SNAPSHOT_AUDIT["source_success_memories"], 1)
            self.assertEqual(m3._SNAPSHOT_AUDIT["source_failure_memories"], 1)
            self.assertEqual(m3._key_snapshot_hashes(cp), m3._SNAPSHOT_AUDIT["original_preload_key_hashes"])

    def test_missing_polarity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            selected = ["1", "2"]
            cp, ledger = self.make_snapshot(root, selected, visible=0)
            textual = cp / "cube" / "textual_memory.json"
            rows = json.loads(textual.read_text())
            for row in rows:
                row["payload"]["metadata"]["success"] = True
            textual.write_text(json.dumps(rows), encoding="utf-8")
            meta = json.loads((cp / "snapshot_meta.json").read_text())
            meta["textual_memory_md5"] = _md5(textual)
            (cp / "snapshot_meta.json").write_text(json.dumps(meta), encoding="utf-8")
            ledger_rows = [json.loads(x) for x in ledger.read_text().splitlines()]
            ledger_rows[-1]["checkpoint_textual_memory_md5"] = meta["textual_memory_md5"]
            ledger.write_text("".join(json.dumps(row) + "\n" for row in ledger_rows), encoding="utf-8")
            m3._WORKING_COPY_ROOT = root / "work"
            with self.assertRaisesRegex(RuntimeError, "provenance-polarity-missing"):
                m3.snapshot_backed_last_checkpoint(ledger, selected)

    def test_textual_memory_md5_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            selected = ["1", "2"]
            cp, ledger = self.make_snapshot(root, selected, visible=0)
            (cp / "cube" / "textual_memory.json").write_text("[]", encoding="utf-8")
            m3._WORKING_COPY_ROOT = root / "work"
            with self.assertRaisesRegex(RuntimeError, "textual-memory-md5-drift"):
                m3.snapshot_backed_last_checkpoint(ledger, selected)

    def test_existing_working_copy_forbids_ambiguous_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            selected = ["1", "2"]
            _cp, ledger = self.make_snapshot(root, selected, visible=0)
            work = root / "work"
            work.mkdir()
            m3._WORKING_COPY_ROOT = work
            with self.assertRaisesRegex(RuntimeError, "working-copy-already-exists"):
                m3.snapshot_backed_last_checkpoint(ledger, selected)


if __name__ == "__main__":
    unittest.main()
