from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter


class MindMemOSArkPlanAdapterTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    def test_raw_call_record_is_content_addressed_and_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                record_dir=Path(tmp),
            )
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": "summary text",
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                "response_id": "resp-secret-raw-id",
                "status": "completed",
            }
            response = asyncio.run(
                adapter.chat(
                    task="skill_trajectory_summary",
                    messages=[{"role": "user", "content": "trajectory"}],
                )
            )
            self.assertEqual(response.content, "summary text")
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["provider_retry_limit"], 0)
            record = Path(receipts[0]["record_path"])
            payload = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual(payload["response_text"], "summary text")
            self.assertEqual(payload["prompt_sha256"], receipts[0]["prompt_sha256"])
            self.assertFalse(payload["raw_response_id_included"])
            self.assertNotIn("resp-secret-raw-id", record.read_text(encoding="utf-8"))

    def test_parse_correction_is_explicit_not_hidden_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                max_parse_attempts=2,
                record_dir=Path(tmp),
            )
            outputs = iter(["not-json", '{"ok": true}'])
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": next(outputs),
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                "response_id": "private-id",
                "status": "completed",
            }

            def parser(text: str):
                return json.loads(text)

            response = asyncio.run(
                adapter.chat(
                    task="skill_patch_apply",
                    messages=[{"role": "user", "content": "apply"}],
                    format_parser=parser,
                    feedback_on_parse_error=True,
                )
            )
            self.assertEqual(response.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 2)
            self.assertTrue(receipts[0]["parse_error"])
            self.assertFalse(receipts[1]["parse_error"])
            self.assertTrue(all(not row["hidden_provider_retry_used"] for row in receipts))
            self.assertEqual([row["attempt"] for row in receipts], [0, 1])

    def test_resolved_model_drift_is_recorded_then_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                record_dir=Path(tmp),
            )
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "different-model",
                "text": "x",
                "usage": {},
                "response_id": "id",
                "status": "completed",
            }
            with self.assertRaisesRegex(RuntimeError, "resolved-model-drift"):
                asyncio.run(adapter.chat(task="skill_patch_propose", messages=[{"role": "user", "content": "x"}]))
            self.assertEqual(adapter.public_receipts()[0]["resolved_model"], "different-model")
            self.assertTrue(Path(adapter.public_receipts()[0]["record_path"]).exists())


if __name__ == "__main__":
    unittest.main()
