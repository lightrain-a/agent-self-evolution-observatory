from __future__ import annotations

import unittest

from .paper_first_agent_safety_r9_gemma4_v4_probe_recovery import _call


class Gemma4V4ProbeRecoveryTest(unittest.TestCase):
    def test_simple_fill_action_is_literal_only(self) -> None:
        name, args = _call("fill('abc', 'exact text')")
        self.assertEqual(name, "fill")
        self.assertEqual(args, ["abc", "exact text"])

    def test_nonliteral_action_argument_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "literal string"):
            _call("fill('abc', variable)")

    def test_noncall_expression_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "simple function call"):
            _call("'noop'")


if __name__ == "__main__":
    unittest.main()
