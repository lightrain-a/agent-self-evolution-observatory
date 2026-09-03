from __future__ import annotations

import copy
import hashlib
import json
import unittest

from .failure_memory_memrl_host_migration_r45m1 import (
    ALLOWED_INFRASTRUCTURE_PATHS,
    apply_infrastructure,
    audit,
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class HostMigrationR45M1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = {
            "host": {
                "logical_name": "old",
                "ssh_identity": "old@60",
                "gpu_assignment": {"llm": "cuda:0", "embedding": "cuda:1", "environment": "cpu/docker"},
                "python": "/old/python",
                "pythonpath": "/old/site",
                "runtime_tree_sha256": "a",
                "runtime_manifest_sha256": "b",
                "runtime_manifest_file_sha256": "c",
            },
            "source": {"checkout": "/old/source", "revision": "frozen"},
            "models": {
                "llm": {"root": "/old/llm", "device": "cuda:0", "temperature": 0.0},
                "embedding": {"root": "/old/embed", "device": "cuda:1", "pooling": "frozen"},
            },
            "runtime_image": {
                "qualified_tag": "old:q",
                "execution_tag": "old:e",
                "id": "sha256:old",
                "execution_tag_same_content_identity": True,
            },
            "source_build": {"selected_ids": ["1", "2"], "temperature": 0.0},
        }
        self.infrastructure = {
            "host": {
                "logical_name": "ubuntu",
                "ssh_identity": "wyt@222.20.126.231",
                "gpu_assignment": {"llm": "cuda:0", "embedding": "cuda:0", "environment": "cpu/docker"},
            },
            "python_runtime": {
                "python": "/new/python",
                "pythonpath": "/new/site",
                "tree_sha256": "d",
                "manifest_sha256": "e",
                "manifest_file_sha256": "f",
            },
            "source": {"checkout": "/new/source"},
            "models": {
                "llm": {"root": "/new/llm", "device": "cuda:0"},
                "embedding": {"root": "/new/embed", "device": "cuda:0"},
            },
            "docker": {
                "qualified_tag": "new:q",
                "execution_tag": "new:e",
                "id": "sha256:new",
                "same_content_identity": True,
            },
        }

    def test_only_whitelisted_fields_change(self) -> None:
        replacement = apply_infrastructure(self.original, self.infrastructure)
        row = audit(self.original, replacement)
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["non_whitelisted_scientific_difference_count"], 0)
        self.assertTrue(row["scientific_projection_byte_identical"])
        self.assertTrue({x["path"] for x in row["differences"]} <= ALLOWED_INFRASTRUCTURE_PATHS)

    def test_scientific_change_is_closed(self) -> None:
        replacement = apply_infrastructure(self.original, self.infrastructure)
        replacement["source_build"]["temperature"] = 0.5
        row = audit(self.original, replacement)
        self.assertEqual(row["status"], "STOP_SCIENTIFIC_PROTOCOL_DRIFT")
        self.assertEqual(
            [x["path"] for x in row["non_whitelisted_scientific_differences"]],
            ["source_build.temperature"],
        )

    def test_frozen_selected_ids_are_not_infrastructure(self) -> None:
        replacement = apply_infrastructure(self.original, self.infrastructure)
        replacement["source_build"]["selected_ids"] = ["2", "1"]
        row = audit(self.original, replacement)
        self.assertEqual(row["non_whitelisted_scientific_difference_count"], 1)


if __name__ == "__main__":
    unittest.main()
