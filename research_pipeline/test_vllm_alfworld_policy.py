from __future__ import annotations

import unittest

from research_pipeline.vllm_alfworld_policy import VLLMAdmissiblePolicy


class VLLMAlfworldPolicyTest(unittest.TestCase):
    def _policy_without_network(self, seed: int | None) -> tuple[VLLMAdmissiblePolicy, list[dict]]:
        policy = VLLMAdmissiblePolicy.__new__(VLLMAdmissiblePolicy)
        policy.base_url = "http://unused"
        policy.model = "mock-model"
        policy.max_history = 6
        policy.policy_mode = "direct"
        policy.timeout_seconds = 1.0
        policy.seed = seed
        policy.cache_identical_prompts = False
        policy._response_cache = {}
        policy._cache_hits = 0
        policy._input_tokens = 0
        policy._output_tokens = 0
        policy._generation_calls = 0
        captured: list[dict] = []

        def fake_post(path: str, payload: dict):
            captured.append({"path": path, "payload": dict(payload)})
            return {
                "choices": [{"message": {"content": "look"}}],
                "usage": {"prompt_tokens": 4, "completion_tokens": 1},
            }

        policy._post = fake_post  # type: ignore[method-assign]
        return policy, captured

    def test_frozen_seed_is_forwarded_to_chat_completion(self) -> None:
        policy, captured = self._policy_without_network(20260822)
        action, invalid, _ = policy.choose("room", ["look"], [], "")
        self.assertEqual(action, "look")
        self.assertFalse(invalid)
        self.assertEqual(captured[0]["path"], "/v1/chat/completions")
        self.assertEqual(captured[0]["payload"]["seed"], 20260822)
        self.assertEqual(captured[0]["payload"]["temperature"], 0)

    def test_seed_is_omitted_when_transport_has_no_frozen_seed(self) -> None:
        policy, captured = self._policy_without_network(None)
        policy.choose("room", ["look"], [], "")
        self.assertNotIn("seed", captured[0]["payload"])

    def test_identical_prompt_cache_reuses_first_response_without_second_provider_call(self) -> None:
        policy, captured = self._policy_without_network(20260822)
        policy.cache_identical_prompts = True
        first = policy.choose("same room", ["look"], [], "")
        second = policy.choose("same room", ["look"], [], "")
        self.assertEqual(first, second)
        self.assertEqual(len(captured), 1)
        usage = policy.usage_snapshot()
        self.assertEqual(usage["generation_calls"], 1)
        self.assertEqual(usage["response_cache_hits"], 1)
        self.assertEqual(usage["response_cache_entries"], 1)

    def test_cache_key_changes_when_observation_changes(self) -> None:
        policy, captured = self._policy_without_network(20260822)
        policy.cache_identical_prompts = True
        policy.choose("room A", ["look"], [], "")
        policy.choose("room B", ["look"], [], "")
        self.assertEqual(len(captured), 2)


if __name__ == "__main__":
    unittest.main()
