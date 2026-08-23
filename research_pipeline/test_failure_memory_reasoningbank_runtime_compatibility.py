from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_runtime_compatibility import extract_version, package_block


class TestReasoningBankRuntimeCompatibility(unittest.TestCase):
    def test_package_block_extracts_exact_package(self) -> None:
        text = '''
[[package]]
name = "playwright"
version = "1.44.0"
dependencies = [{ name = "greenlet" }]

[[package]]
name = "greenlet"
version = "3.0.3"
sdist = { hash = "sha256:abc" }
'''
        self.assertEqual(extract_version(package_block(text, "playwright")), "1.44.0")
        self.assertEqual(extract_version(package_block(text, "greenlet")), "3.0.3")

    def test_missing_package_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            package_block('[[package]]\nname = "other"\nversion = "1"\n', "greenlet")


if __name__ == "__main__":
    unittest.main()
