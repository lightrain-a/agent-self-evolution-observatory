from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .config import StorageSettings


class StorageSettingsTest(unittest.TestCase):
    def test_large_data_root_controls_bulk_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research-data"
            environment = {
                "RESEARCH_DATA_ROOT": str(root),
                "RESEARCH_CORPUS_DIR": str(root / "corpora"),
                "RESEARCH_DATASET_DIR": str(root / "datasets"),
                "RESEARCH_PAPER_DIR": str(root / "papers"),
                "RESEARCH_INDEX_DIR": str(root / "indexes"),
                "RESEARCH_RUN_DIR": str(root / "runs"),
                "RESEARCH_CACHE_DIR": str(root / "cache"),
                "RESEARCH_LOCK_DIR": str(root / "locks"),
                "RESEARCH_SITE_ARTIFACT_DIR": str(Path(directory) / "site-generated"),
            }
            with patch.dict(os.environ, environment, clear=False):
                settings = StorageSettings.from_env(env_file=Path(directory) / "missing.env")
                settings.ensure()

            self.assertEqual(settings.data_root, root)
            self.assertEqual(settings.corpus_dir, root / "corpora")
            self.assertEqual(settings.dataset_dir, root / "datasets")
            self.assertEqual(settings.index_dir, root / "indexes")
            self.assertTrue(all(path.exists() for path in settings.directories().values()))

    def test_summary_separates_code_and_data_roots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "bulk"
            environment = {
                "RESEARCH_DATA_ROOT": str(root),
                "RESEARCH_CORPUS_DIR": str(root / "corpora"),
                "RESEARCH_DATASET_DIR": str(root / "datasets"),
                "RESEARCH_PAPER_DIR": str(root / "papers"),
                "RESEARCH_INDEX_DIR": str(root / "indexes"),
                "RESEARCH_RUN_DIR": str(root / "runs"),
                "RESEARCH_CACHE_DIR": str(root / "cache"),
                "RESEARCH_LOCK_DIR": str(root / "locks"),
            }
            with patch.dict(os.environ, environment, clear=False):
                settings = StorageSettings.from_env(env_file=Path(directory) / "missing.env")
                summary = settings.safe_summary()
            self.assertEqual(summary["data_root"], str(root))
            self.assertIn("project_root", summary)
            self.assertIn("data_disk", summary)
            self.assertIn("code_disk", summary)


if __name__ == "__main__":
    unittest.main()
