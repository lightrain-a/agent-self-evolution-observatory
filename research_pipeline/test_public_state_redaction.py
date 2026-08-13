from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .config import StorageSettings
from .public_state_redaction import redact_private_paths


class PublicStateRedactionTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root / "research-data",
            corpus_dir=root / "research-data" / "corpora",
            dataset_dir=root / "research-data" / "datasets",
            paper_dir=root / "research-data" / "papers",
            index_dir=root / "research-data" / "indexes",
            run_dir=root / "research-data" / "runs",
            cache_dir=root / "research-data" / "cache",
            lock_dir=root / "research-data" / "locks",
            site_artifact_dir=root / "site",
        )

    def test_data_root_paths_become_private_data_uris(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root)
            value={"path":str(storage.data_root / "paper-first" / "raw.txt")}
            public=redact_private_paths(value,storage=storage)
        self.assertEqual(public["path"],"private-data://paper-first/raw.txt")

    def test_unknown_absolute_path_keeps_only_basename(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td))
            public=redact_private_paths({"path":"/srv/private/secrets/run.json"},storage=storage)
        self.assertEqual(public["path"],"private-data://external/run.json")

    def test_urls_and_non_path_text_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td))
            public=redact_private_paths({"url":"https://arxiv.org/abs/2608.12345","text":"no private path here"},storage=storage)
        self.assertEqual(public["url"],"https://arxiv.org/abs/2608.12345")
        self.assertEqual(public["text"],"no private path here")


if __name__ == "__main__":
    unittest.main()
