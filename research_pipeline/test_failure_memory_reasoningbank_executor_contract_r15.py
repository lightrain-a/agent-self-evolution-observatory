import copy
import unittest

from research_pipeline.failure_memory_reasoningbank_executor_contract_r15 import (
    build_contract,
    build_schedule,
    differing_indices,
    render_memory_file,
)


class TestReasoningBankExecutorContractR15(unittest.TestCase):
    def ids(self):
        return [str(i) for i in range(36)]

    def r9(self):
        return {
            "_sha256": "1" * 64,
            "cohort": {
                "independent_units": 36,
                "downstream_task_ids": self.ids(),
                "source_task_ids": [str(i + 100) for i in range(36)],
                "full_cohort_required_if_executed": True,
            },
        }

    def r11(self):
        return {
            "_sha256": "2" * 64,
            "cohort": {"independent_units": 36, "all_units_shopping_only": True},
            "execution_gate": {"shopping_only_live_substrate_ready": True},
        }

    def r13(self):
        return {"_sha256": "3" * 64, "summary": {"source_tasks": 36, "model_calls_executed": 0}}

    def r14(self):
        return {
            "_sha256": "4" * 64,
            "execution_gate": {"exact_writer_model_artifact_bound": True, "writer_calls_executed": 0},
        }

    def show(self):
        return {"details": {"quantization_level": "Q4_K_M"}, "parameters": "num_ctx 32768"}

    def transport(self):
        return {
            "status": "FIRST_PARTY_GENERIC_AGENT_LOCAL_OPENAI_TRANSPORT_CONSTRUCTED_NO_COMPLETION",
            "model": "b1-qwen25-32b-l2b-executor:latest",
            "temperature": 0.0,
            "base_url": "http://127.0.0.1:11444/v1/",
            "completion_called": False,
            "browser_action_executed": False,
            "evaluator_called": False,
            "scientific_outcome_opened": False,
            "flags": {"action_space": "bid"},
            "packages": {"browsergym-webarena": "0.14.1"},
        }

    def test_renderer_differs_by_exactly_one_byte(self):
        s = render_memory_file("abc", "STATUS_S").encode()
        f = render_memory_file("abc", "STATUS_F").encode()
        d = differing_indices(s, f)
        self.assertEqual(len(d), 1)
        self.assertEqual(s[d[0]:d[0]+1], b"S")
        self.assertEqual(f[d[0]:d[0]+1], b"F")

    def test_schedule_is_144_and_counterbalanced_per_task(self):
        rows = build_schedule(self.ids(), [str(i + 100) for i in range(36)])
        self.assertEqual(len(rows), 144)
        for tid in self.ids():
            r = [x for x in rows if x["task_id"] == tid]
            self.assertEqual(sum(x["arm"] == "STATUS_S" for x in r), 2)
            self.assertEqual(sum(x["arm"] == "STATUS_F" for x in r), 2)
            self.assertEqual(sorted(x["arm"] for x in r if x["position_in_pair"] == 0), ["STATUS_F", "STATUS_S"])

    def test_contract_binds_executor_but_does_not_authorize_execution(self):
        c = build_contract(
            self.r9(), self.r11(), self.r13(), self.r14(),
            "5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216",
            self.show(), "5" * 64, self.transport(), "6" * 64, {"agent.py": "7" * 64},
        )
        self.assertEqual(c["cohort_and_rollouts"]["total_terminal_episodes"], 144)
        self.assertEqual(c["executor"]["temperature"], 0.0)
        self.assertTrue(c["execution_gate"]["executor_model_artifact_bound"])
        self.assertFalse(c["execution_gate"]["execution_permitted"])
        self.assertFalse(c["authority"]["model_calls"])

    def test_contract_rejects_transport_that_called_completion(self):
        t = copy.deepcopy(self.transport())
        t["completion_called"] = True
        with self.assertRaises(RuntimeError):
            build_contract(
                self.r9(), self.r11(), self.r13(), self.r14(),
                "5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216",
                self.show(), "5" * 64, t, "6" * 64, {"agent.py": "7" * 64},
            )


if __name__ == "__main__":
    unittest.main()
