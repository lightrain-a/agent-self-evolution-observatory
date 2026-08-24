import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_writer_input_r13 import (
    executed_actions,
    extract_constants,
    serialize_trace,
)


class TestReasoningBankWriterInputR13(unittest.TestCase):
    def test_executed_actions_uses_only_action_channel(self):
        traj = {
            "steps": {
                "1": {
                    "input_messages": {"secret": "DOM"},
                    "output_messages": {
                        "tool_call_message": {
                            "tool_calls": [{
                                "name": "AgentOutput",
                                "args": {
                                    "current_state": {"memory": "must not leak"},
                                    "action": [{"click_element": {"index": 7}}],
                                },
                            }]
                        }
                    },
                }
            }
        }
        self.assertEqual(executed_actions(traj), [{"step": 1, "actions": [{"click_element": {"index": 7}}]}])
        trace = serialize_trace("Do X", traj)
        self.assertIn("click_element", trace)
        self.assertNotIn("must not leak", trace)
        self.assertNotIn("DOM", trace)

    def test_no_actions_fails_closed(self):
        with self.assertRaises(ValueError):
            executed_actions({"steps": {"1": {}}})

    def test_prompt_constant_extraction(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "p.py"
            p.write_text('SUCCESSFUL_SI="S"\nFAILED_SI="F"\nOTHER="X"\n')
            self.assertEqual(extract_constants(p), {"SUCCESSFUL_SI": "S", "FAILED_SI": "F"})


if __name__ == "__main__":
    unittest.main()
