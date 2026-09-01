from __future__ import annotations

import ast
import asyncio
import inspect
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_repair2_manifest import (
    _validate_eval_manifest,
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)

ROOT = Path(__file__).resolve().parents[1]
COMPAT = ROOT / "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json"
QUARANTINE = ROOT / "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json"
COMPAT_SHA = "61e243027e6d42f7923e249f6c88267e6db07ed4bccb32d5a50c8d13bf1695bb"
QUARANTINE_SHA = "1908a3dfc472f835c204f7f9d5a66a9ee4b37093adb09a8d0c0f297b4b1abd7a"
REPAIR1_CONTRACT_SHA = "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80"
REPAIR1_AUTH_SHA = "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5"


class Repair2Tests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="deepseek-v4-pro",
            timeout_seconds=30,
            max_retries=0,
        )

    def adapter(self, root: Path, outputs: list[str]) -> tuple[MindMemOSArkPlanChatAdapter, list[str]]:
        ledger = ProviderBudgetLedger(
            path=root / "budget.sqlite3",
            contract_sha256="a" * 64,
            authorization_sha256="b" * 64,
            total_limit=191,
            per_unit_limit=11,
            allow_create=True,
        )
        adapter = MindMemOSArkPlanChatAdapter(
            settings=self.settings(),
            requested_model="deepseek-v4-pro",
            required_resolved_model="deepseek-v4-pro-ga-260813",
            max_parse_attempts=2,
            record_dir=root / "calls",
            provider_budget_ledger=ledger,
            provider_budget_unit_id="s/rep0/win_c/update",
        )
        prompts: list[str] = []
        iterator = iter(outputs)

        def respond(prompt: str, *args, **kwargs):
            prompts.append(prompt)
            return {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": next(iterator),
                "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
                "response_id": f"id-{len(prompts)}",
                "status": "completed",
            }

        adapter.client.respond = respond
        return adapter, prompts

    def nine_nominal_calls(self, adapter: MindMemOSArkPlanChatAdapter) -> None:
        for index in range(9):
            task = "skill_trajectory_summary" if index < 8 else "skill_patch_propose"
            asyncio.run(adapter.chat(task=task, messages=[{"role": "user", "content": "x"}]))

    def test_a_first_attempt_success_exactly_ten_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, _ = self.adapter(Path(tmp), ["ok"] * 9 + ['{"ok":true}'])
            self.nine_nominal_calls(adapter)
            result = asyncio.run(adapter.chat(
                task="skill_patch_apply",
                messages=[{"role": "user", "content": "apply"}],
                format_parser=json.loads,
                feedback_on_parse_error=True,
            ))
            self.assertEqual(result.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 10)
            self.assertFalse(any(row["parse_error"] for row in receipts))
            self.assertEqual(receipts[-1]["attempt"], 0)

    def test_b_one_explicit_correction_exactly_eleven_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, prompts = self.adapter(Path(tmp), ["ok"] * 9 + ["bad", '{"ok":true}'])
            self.nine_nominal_calls(adapter)
            exact_error = "line 12 does not match old_string_prefix"

            def parser(text: str):
                if text == "bad":
                    raise ValueError(exact_error)
                return json.loads(text)

            result = asyncio.run(adapter.chat(
                task="skill_patch_apply",
                messages=[{"role": "user", "content": "apply"}],
                format_parser=parser,
                feedback_on_parse_error=True,
            ))
            self.assertEqual(result.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 11)
            self.assertEqual([receipts[-2]["attempt"], receipts[-1]["attempt"]], [0, 1])
            self.assertIn(exact_error, prompts[-1])
            self.assertTrue(receipts[-2]["parse_error"])
            self.assertFalse(receipts[-1]["parse_error"])
            self.assertTrue(all(not row["hidden_provider_retry_used"] for row in receipts))

    def test_c_second_failure_stops_without_third_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, prompts = self.adapter(Path(tmp), ["ok"] * 9 + ["bad0", "bad1"])
            self.nine_nominal_calls(adapter)

            def parser(text: str):
                raise ValueError(f"cannot apply {text}")

            with self.assertRaisesRegex(ValueError, "cannot apply bad1"):
                asyncio.run(adapter.chat(
                    task="skill_patch_apply",
                    messages=[{"role": "user", "content": "apply"}],
                    format_parser=parser,
                    feedback_on_parse_error=True,
                ))
            self.assertEqual(len(adapter.public_receipts()), 11)
            self.assertEqual(len(prompts), 11)
            self.assertEqual([row["attempt"] for row in adapter.public_receipts()[-2:]], [0, 1])

    def test_d_real_repair1_prefix_manifest_revalidates_without_provider_call(self) -> None:
        contract = json.loads((ROOT / "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json").read_text())
        rows = validate_compatibility_manifest(
            path=COMPAT,
            expected_sha=COMPAT_SHA,
            repair1_contract_sha=REPAIR1_CONTRACT_SHA,
            repair1_authorization_sha=REPAIR1_AUTH_SHA,
            heldout_task_ids=contract["heldout"]["task_ids"],
        )
        self.assertEqual(len(rows), 14)
        self.assertEqual(sum(len(row["arms"]) for row in rows), 28)
        self.assertTrue(all(row["source"] == "repair1_inherited" for row in rows))

    def test_e_partial_repair1_state_is_quarantined_not_inherited(self) -> None:
        quarantine = validate_quarantine(QUARANTINE, QUARANTINE_SHA)
        self.assertFalse(quarantine["update_completed_exists"])
        self.assertFalse(quarantine["skill_post_exists"])
        self.assertFalse(quarantine["paired_win_c_started"])
        self.assertEqual(quarantine["disposition"], "PRESERVE; EXCLUDE FROM VALID MANIFEST; REPAIR2 FRESH-RUNS BOTH ARMS")

    def row(self, stream: str, replicate: int, source: str = "repair2_fresh") -> dict:
        arms = {}
        for arm in ("win_c", "mrw"):
            arms[arm] = {
                "state_root": f"/fresh/{stream}/replicate_{replicate}/{arm}",
                "skill_sha256": "a" * 64,
                "update_receipt_sha256": "b" * 64,
                "eval_manifest_path": f"/fresh/{stream}/replicate_{replicate}/{arm}/eval.jsonl",
                "eval_manifest_sha256": "c" * 64,
            }
        return {
            "unit_id": f"{stream}/rep{replicate}",
            "stream_id": stream,
            "replicate_id": replicate,
            "source": source,
            "arms": arms,
        }

    def quarantine(self) -> dict:
        return {
            "stream_id": "s0",
            "replicate_id": 2,
            "state_root": "/repair1/s0/replicate_2/mrw",
        }

    def test_f_quarantine_state_cannot_enter_valid_manifest(self) -> None:
        row = self.row("s0", 2, "repair1_inherited")
        row["arms"]["mrw"]["state_root"] = self.quarantine()["state_root"]
        with self.assertRaisesRegex(RuntimeError, "quarantined"):
            validate_valid_rows([row], streams=["s0"], quarantine=self.quarantine(), require_complete=False)

    def test_g_incomplete_pair_is_not_scientific_valid(self) -> None:
        row = self.row("s0", 0)
        del row["arms"]["mrw"]
        with self.assertRaisesRegex(RuntimeError, "incomplete pair"):
            validate_valid_rows([row], streams=["s0"], quarantine=self.quarantine(), require_complete=False)

    def test_h_exactly_four_pairs_per_stream_and_48_total(self) -> None:
        streams = [f"s{i}" for i in range(12)]
        rows = [self.row(stream, replicate) for stream in streams for replicate in range(4)]
        validate_valid_rows(rows, streams=streams, quarantine=self.quarantine(), require_complete=True)
        with self.assertRaisesRegex(RuntimeError, "exactly 48|exactly four"):
            validate_valid_rows(rows[:-1], streams=streams, quarantine=self.quarantine(), require_complete=True)

    def test_i_inheritance_validator_never_reads_score_field(self) -> None:
        tree = ast.parse(inspect.getsource(_validate_eval_manifest))
        score_subscripts = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Subscript)
            and isinstance(node.slice, ast.Constant)
            and node.slice.value in {"score", "effect", "J", "D", "success_count"}
        ]
        self.assertEqual(score_subscripts, [])


if __name__ == "__main__":
    unittest.main()
