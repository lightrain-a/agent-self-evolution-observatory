from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM
from research_pipeline.e2_r17_provider_budget import (
    ProviderBudgetBindingError,
    ProviderBudgetExceeded,
    ProviderBudgetLedger,
)


class ProviderBudgetTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    @staticmethod
    def successful_response() -> dict[str, object]:
        return {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "text": "done",
            "function_calls": [],
            "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
            "response_id": "resp-secret",
            "status": "completed",
        }

    def make_ledger(self, root: Path, *, total: int, per_unit: int) -> ProviderBudgetLedger:
        return ProviderBudgetLedger(
            path=root / "provider_budget.sqlite3",
            contract_sha256="a" * 64,
            authorization_sha256="b" * 64,
            total_limit=total,
            per_unit_limit=per_unit,
            allow_create=True,
        )

    def test_eleventh_rollout_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=100, per_unit=10)
            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="task-1/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            for _ in range(10):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            with self.assertRaisesRegex(ProviderBudgetExceeded, "per-unit call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            snapshot = ledger.snapshot()
            self.assertEqual(snapshot.unit_claimed["task-1/rollout_0"], 10)
            self.assertEqual(snapshot.total_claimed, 10)
            receipts = llm.public_receipts()
            self.assertEqual(receipts[-1]["provider_budget_unit_call_index"], 10)
            self.assertEqual(receipts[-1]["provider_budget_total_claimed_after"], 10)

    def test_7681st_global_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=7680, per_unit=10)
            for index in range(7680):
                ledger.claim(f"prefill-{index // 10}")
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="new-task/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            with self.assertRaisesRegex(ProviderBudgetExceeded, "total call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 0)
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

    def test_contract_or_authorization_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provider_budget.sqlite3"
            ProviderBudgetLedger(
                path=path,
                contract_sha256="a" * 64,
                authorization_sha256="b" * 64,
                total_limit=20,
                per_unit_limit=10,
                allow_create=True,
            )
            with self.assertRaises(ProviderBudgetBindingError):
                ProviderBudgetLedger(
                    path=path,
                    contract_sha256="c" * 64,
                    authorization_sha256="b" * 64,
                    total_limit=20,
                    per_unit_limit=10,
                    allow_create=False,
                )


if __name__ == "__main__":
    unittest.main()
