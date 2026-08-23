from __future__ import annotations

import unittest

from .ark_provider import ArkResponseStateError
from .posttrain_strategy_deepseek_driver import (
    AgentLoopBudget,
    TOOLS,
    run_deepseek_tool_loop,
)
from .posttrain_strategy_intervention import (
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
)

STRATEGY = (
    "Use supervised fine-tuning only as a small formatting warm-up. Reserve the main training "
    "budget for reinforcement learning, and omit SFT if the base model already satisfies the "
    "required output-format contract."
)
EXECUTION = (
    "Keep the training paradigm, data-source type, and stage structure fixed. For the next training "
    "only, halve the current learning rate and leave the rest of the strategy unchanged."
)
CONFLICT_FREE = (
    "Preserve the current checkpoint and completed training. Add a reinforcement-learning stage for "
    "the remaining budget without requiring rollback of already completed work."
)
BASE = "Improve the assigned base model on AIME 2025."


def call(name: str, arguments: dict) -> dict:
    return {"type": "function_call", "name": name, "arguments": arguments}


def response(*calls: dict, tokens: int = 20, text: str = "") -> dict:
    return {
        "response_id": f"resp-{id(calls)}",
        "status": "completed",
        "requested_model": "deepseek-v4-pro",
        "resolved_model": "deepseek-v4-pro-test",
        "text": text,
        "function_calls": list(calls),
        "usage": {"output_tokens": tokens},
    }


class FakeProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def respond(self, prompt: str, **kwargs):
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("unexpected provider call")
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class FakeExecutor:
    def __init__(self, training_updates=None):
        self.training_updates = list(training_updates or [])
        self.calls = []

    def execute(self, name: str, arguments: dict):
        self.calls.append((name, arguments))
        if name == "run_training":
            verified = self.training_updates.pop(0) if self.training_updates else False
            return {
                "exit_code": 0,
                "parameter_update_verified": verified,
                "checkpoint": "checkpoint-1" if verified else None,
            }
        if name == "run_evaluation":
            return {"evaluator_sha256": "c" * 64, "completed": True}
        if name == "inspect_workspace":
            return {"path": arguments["path"], "content_sha256": "d" * 64}
        raise AssertionError(name)


class DeepSeekDriverDryTest(unittest.TestCase):
    def run_loop(self, provider, executor, arm=ARM_POST_STRATEGY, budget=None):
        return run_deepseek_tool_loop(
            client=provider,
            executor=executor,
            arm=arm,
            base_prompt=BASE,
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
            budget=budget,
        )

    def test_post_strategy_is_blind_before_boundary_and_injected_after_verified_update(self):
        provider = FakeProvider(
            [
                response(call("run_training", {"method": "sft", "stage": "warmup", "config": {"lr": 1e-4}, "rationale": "establish first update"})),
                response(call("finish", {"summary": "continued under injected strategy"})),
            ]
        )
        executor = FakeExecutor(training_updates=[True])
        result = self.run_loop(provider, executor)
        self.assertTrue(result["boundary_reached"])
        self.assertTrue(result["phase2_injected"])
        self.assertEqual(2, result["provider_calls"])
        self.assertNotIn(STRATEGY, provider.calls[0]["prompt"])
        self.assertNotIn("POST_STRATEGY", provider.calls[0]["prompt"])
        self.assertIn(STRATEGY, provider.calls[1]["prompt"])
        self.assertIn("PTB_INTERVENTION_BOUNDARY_READY", provider.calls[1]["prompt"])
        self.assertFalse(result["scientific_authority"])
        self.assertFalse(result["paid_probe_authorized_by_this_function"])

    def test_pre_strategy_has_same_payload_before_boundary(self):
        provider = FakeProvider(
            [
                response(call("run_training", {"method": "rl", "stage": "main", "config": {"lr": 5e-6}, "rationale": "follow binding strategy"})),
                response(call("finish", {"summary": "done"})),
            ]
        )
        executor = FakeExecutor(training_updates=[True])
        result = self.run_loop(provider, executor, arm=ARM_PRE_STRATEGY)
        self.assertIn(STRATEGY, provider.calls[0]["prompt"])
        self.assertNotIn(STRATEGY, provider.calls[1]["prompt"].split("## Verified continuation after parameter-update boundary", 1)[-1])
        self.assertTrue(result["pre_strategy_present_in_initial_prompt"])

    def test_unverified_training_does_not_open_boundary(self):
        provider = FakeProvider(
            [
                response(call("run_training", {"method": "sft", "stage": "attempt1", "config": {"lr": 1e-5}, "rationale": "try"})),
                response(call("run_training", {"method": "sft", "stage": "attempt2", "config": {"lr": 1e-4}, "rationale": "retry"})),
                response(call("finish", {"summary": "done"})),
            ]
        )
        executor = FakeExecutor(training_updates=[False, True])
        result = self.run_loop(provider, executor)
        self.assertNotIn(STRATEGY, provider.calls[0]["prompt"])
        self.assertNotIn(STRATEGY, provider.calls[1]["prompt"])
        self.assertIn(STRATEGY, provider.calls[2]["prompt"])
        self.assertEqual(2, len([row for row in result["transcript"] if row.get("tool") == "run_training"]))
        self.assertEqual(1, len([row for row in result["transcript"] if row.get("kind") == "boundary"]))

    def test_finish_before_boundary_is_rejected(self):
        provider = FakeProvider([response(call("finish", {"summary": "premature"}))])
        executor = FakeExecutor()
        with self.assertRaisesRegex(RuntimeError, "finish before verified parameter-update boundary"):
            self.run_loop(provider, executor)
        self.assertEqual([], executor.calls)

    def test_second_preboundary_tool_call_is_not_executed_after_boundary_opens(self):
        provider = FakeProvider(
            [
                response(
                    call("run_training", {"method": "sft", "stage": "first", "config": {"lr": 1e-4}, "rationale": "first real update"}),
                    call("run_training", {"method": "rl", "stage": "should-not-run", "config": {"lr": 1e-6}, "rationale": "would violate boundary"}),
                ),
                response(call("finish", {"summary": "done"})),
            ]
        )
        executor = FakeExecutor(training_updates=[True, True])
        self.run_loop(provider, executor)
        self.assertEqual(1, len(executor.calls))
        self.assertEqual("first", executor.calls[0][1]["stage"])

    def test_provider_call_budget_fails_closed(self):
        provider = FakeProvider(
            [response(call("run_training", {"method": "sft", "stage": "no-delta", "config": {"lr": 0.0}, "rationale": "dry"}))]
        )
        executor = FakeExecutor(training_updates=[False])
        budget = AgentLoopBudget(max_provider_calls=1, max_output_tokens_per_call=100, max_reported_output_tokens=100)
        with self.assertRaisesRegex(RuntimeError, "provider-call budget exhausted"):
            self.run_loop(provider, executor, budget=budget)
        self.assertEqual(1, len(provider.calls))

    def test_reported_output_token_budget_fails_before_tool_execution(self):
        provider = FakeProvider(
            [response(call("run_training", {"method": "sft", "stage": "x", "config": {"lr": 1e-4}, "rationale": "x"}), tokens=101)]
        )
        executor = FakeExecutor(training_updates=[True])
        budget = AgentLoopBudget(max_provider_calls=2, max_output_tokens_per_call=100, max_reported_output_tokens=100)
        with self.assertRaisesRegex(RuntimeError, "output-token budget exceeded"):
            self.run_loop(provider, executor, budget=budget)
        self.assertEqual([], executor.calls)

    def test_existing_incomplete_provider_receipt_is_not_reposted_by_driver(self):
        error = ArkResponseStateError(
            "incomplete",
            {"id": "resp-existing", "status": "incomplete", "model": "deepseek-v4-pro-test", "incomplete_details": {"reason": "length"}},
            "deepseek-v4-pro",
        )
        provider = FakeProvider([error])
        executor = FakeExecutor()
        with self.assertRaises(ArkResponseStateError):
            self.run_loop(provider, executor)
        self.assertEqual(1, len(provider.calls))
        self.assertEqual([], executor.calls)

    def test_api_surface_has_no_raw_shell_tool(self):
        names = {tool["name"] for tool in TOOLS}
        self.assertEqual(names, {"inspect_workspace", "run_training", "run_evaluation", "finish"})
        self.assertFalse(names.intersection({"shell", "bash", "run_command", "execute_command"}))

    def test_inspect_workspace_path_escape_is_rejected_before_executor(self):
        provider = FakeProvider([response(call("inspect_workspace", {"path": "../../generated/secret.json"}))])
        executor = FakeExecutor()
        with self.assertRaisesRegex(ValueError, "inside the declared task workspace"):
            self.run_loop(provider, executor)
        self.assertEqual([], executor.calls)

    def test_raw_command_fields_in_training_config_are_rejected(self):
        provider = FakeProvider(
            [response(call("run_training", {"method": "sft", "stage": "x", "config": {"command": "cat /etc/passwd"}, "rationale": "x"}))]
        )
        executor = FakeExecutor()
        with self.assertRaisesRegex(ValueError, "raw command/script fields are forbidden"):
            self.run_loop(provider, executor)
        self.assertEqual([], executor.calls)


if __name__ == "__main__":
    unittest.main()
