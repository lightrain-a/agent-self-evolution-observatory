import unittest

from research_pipeline.failure_memory_reasoningbank_writer_execute_r17 import structural_parse


class TestReasoningBankWriterExecuteR17(unittest.TestCase):
    def test_structural_parse_accepts_first_party_markdown(self):
        text = (
            "# Memory Item 1\n"
            "## Title Search carefully\n"
            "## Description Use when a product list must be checked.\n"
            "## Content Verify each constraint before stopping.\n\n"
            "# Memory Item 2\n"
            "## Title Recover from broad search\n"
            "## Description Use when results are too broad.\n"
            "## Content Navigate to the dedicated category before extracting."
        )
        p = structural_parse(text)
        self.assertEqual(p["heading_count"], 2)
        self.assertEqual("\n\n".join(p["memory_items"]), text)

    def test_structural_parse_rejects_missing_section(self):
        text = "# Memory Item 1\n## Title X\n## Description Y"
        with self.assertRaises(RuntimeError):
            structural_parse(text)

    def test_structural_parse_rejects_four_items(self):
        text = "\n\n".join(
            f"# Memory Item {i}\n## Title T\n## Description D\n## Content C" for i in range(1, 5)
        )
        with self.assertRaises(RuntimeError):
            structural_parse(text)

    def test_structural_parse_rejects_nonsequential_items(self):
        text = (
            "# Memory Item 1\n## Title T\n## Description D\n## Content C\n\n"
            "# Memory Item 3\n## Title T\n## Description D\n## Content C"
        )
        with self.assertRaises(RuntimeError):
            structural_parse(text)


if __name__ == "__main__":
    unittest.main()
