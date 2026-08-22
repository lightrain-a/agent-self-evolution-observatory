from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from .paper_portfolio_audit import source_watermark as portfolio_watermark


def _registry_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "build_paper_registry.py"
    spec = importlib.util.spec_from_file_location("build_paper_registry", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PaperProjectionDeterminismTest(unittest.TestCase):
    def test_portfolio_watermark_depends_on_canonical_updated_at_not_build_clock(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acceptance = root / "paper-acceptance"
            freezes = root / "paper-submission-freezes"
            acceptance.mkdir()
            freezes.mkdir()
            (acceptance / "A.json").write_text(json.dumps({"updated_at": "2026-08-20T01:00:00+00:00"}))
            (acceptance / "B.json").write_text(json.dumps({"updated_at": "2026-08-21T02:00:00+00:00"}))
            (freezes / "A.json").write_text(json.dumps({"updated_at": "2026-08-22T03:00:00+00:00"}))
            self.assertEqual(portfolio_watermark(root), "2026-08-22T03:00:00+00:00")
            self.assertEqual(portfolio_watermark(root), "2026-08-22T03:00:00+00:00")

    def test_registry_watermark_ignores_derived_index_and_changes_only_with_source(self) -> None:
        module = _registry_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acceptance = root / "paper-acceptance"
            freezes = root / "paper-submission-freezes"
            acceptance.mkdir()
            freezes.mkdir()
            paper = acceptance / "A.json"
            paper.write_text(json.dumps({"updated_at": "2026-08-20T01:00:00+00:00"}))
            (freezes / "current-freeze-index.json").write_text(json.dumps({"updated_at": "2099-01-01T00:00:00+00:00"}))
            self.assertEqual(module.source_watermark(acceptance, freezes), "2026-08-20T01:00:00+00:00")
            paper.write_text(json.dumps({"updated_at": "2026-08-23T04:00:00+00:00"}))
            self.assertEqual(module.source_watermark(acceptance, freezes), "2026-08-23T04:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
