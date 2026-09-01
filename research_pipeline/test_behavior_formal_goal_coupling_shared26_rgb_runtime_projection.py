from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import behavior_formal_goal_coupling_shared26_rgb_runtime_projection as projection


class RgbRuntimeProjectionTest(unittest.TestCase):
    def _source_info(self) -> dict:
        features = {
            key: {"dtype": "video", "shape": [1]}
            for key in (*projection.REQUIRED_RGB_FEATURES, *projection.REMOVED_DEPTH_FEATURES)
        }
        features["observation.state"] = {"dtype": "float32", "shape": [4]}
        return {"codebase_version": "v3.0", "features": features, "fps": 30}

    def test_projected_info_removes_exact_depth_only(self) -> None:
        source = self._source_info()
        result = projection.projected_info(source)
        self.assertEqual(set(source["features"]) - set(result["features"]), set(projection.REMOVED_DEPTH_FEATURES))
        for key in projection.REQUIRED_RGB_FEATURES:
            self.assertEqual(result["features"][key], source["features"][key])
        projection.verify_projection_delta(source, result)

    def test_build_projection_symlinks_payload_and_changes_only_info(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source"
            runtime = base / "runtime"
            (source / "data").mkdir(parents=True)
            (source / "videos").mkdir()
            (source / "meta/episodes").mkdir(parents=True)
            info = self._source_info()
            (source / "meta/info.json").write_text(json.dumps(info) + "\n")
            for name in ("stats.json", "tasks.jsonl", "tasks.parquet"):
                (source / "meta" / name).write_text(name)

            with patch.object(projection, "SOURCE_ROOT", source), patch.object(projection, "RUNTIME_ROOT", runtime), patch.object(
                projection, "SOURCE_INFO_SHA256", projection.sha256_file(source / "meta/info.json")
            ):
                result = projection.build_projection(source, runtime)

            self.assertTrue((runtime / "data").is_symlink())
            self.assertTrue((runtime / "videos").is_symlink())
            self.assertTrue((runtime / "meta/episodes").is_symlink())
            projected = json.loads((runtime / "meta/info.json").read_text())
            self.assertEqual(set(info["features"]) - set(projected["features"]), set(projection.REMOVED_DEPTH_FEATURES))
            self.assertEqual(result["source_feature_count"] - result["projected_feature_count"], 3)


if __name__ == "__main__":
    unittest.main()
