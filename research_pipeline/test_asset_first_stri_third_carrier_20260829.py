from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_native_reunion_probe import build_result


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def load_json(filename: str) -> dict:
    return json.loads((GENERATED / filename).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class STRIReasoningBankThirdCarrierTest(unittest.TestCase):
    def test_candidate_search_is_outcome_blind_and_selects_only_narrow_probe(self) -> None:
        qualification = load_json("asset-first-stri-third-carrier-qualification-20260829.json")
        self.assertTrue(qualification["selection_policy"]["outcome_shopping_prohibited"])
        statuses = {row["name"]: row["status"] for row in qualification["candidates"]}
        self.assertEqual(
            statuses,
            {
                "SAGE": "REJECT_NATIVE_ROBUST_CARRIER_FORMULATION_MISMATCH",
                "Dynamic Cheatsheet": "REJECT_THIRD_CARRIER_NO_IDENTITY_SEAM_USE_AS_STRUCTURAL_COMPARATOR",
                "ReasoningBank": "QUALIFY_FOR_ZERO_PROVIDER_NATIVE_WITHIN_CASE_REUNION_PROBE_ONLY",
            },
        )
        self.assertEqual(qualification["selected_candidate"], "ReasoningBank")
        self.assertIn("Do not modify", qualification["manuscript_policy"])

    def test_contract_binds_source_and_harness_before_outcome(self) -> None:
        contract = load_json("asset-first-stri-reasoningbank-native-reunion-contract-20260829.json")
        harness = ROOT / contract["harness"]["path"]
        self.assertEqual(contract["registration_timing"], "Before result execution")
        self.assertEqual(contract["source"]["commit"], "ed80611788292ea739f1effd31f16c53823b8a0d")
        self.assertEqual(contract["harness"]["sha256"], sha256(harness))
        self.assertEqual(contract["resource_budget"], {"provider_model_calls": 0, "gpu_seconds": 0})
        self.assertIn("not cross-case", contract["claim_ceiling"])

    def test_stored_result_is_exactly_reproducible(self) -> None:
        stored = load_json("asset-first-stri-reasoningbank-native-reunion-p0-result-20260829.json")
        self.assertEqual(build_result(), stored)
        self.assertEqual(
            stored["decision"],
            "NATIVE_WITHIN_CASE_REUNION_PASS_CASE_BOUNDARY_LOCALIZED",
        )
        self.assertTrue(all(stored["static_checks"].values()))
        self.assertTrue(all(stored["observations"].values()))
        self.assertEqual(stored["provider_model_calls"], 0)
        self.assertEqual(stored["gpu_seconds"], 0)

    def test_operator_pass_is_conditional_not_behavioral(self) -> None:
        result = load_json("asset-first-stri-reasoningbank-native-reunion-p0-result-20260829.json")
        arms = result["arms"]
        self.assertEqual(
            arms["A_monolithic_same_case"]["first_system_message_sha256"],
            arms["B_split_same_case"]["first_system_message_sha256"],
        )
        self.assertNotEqual(
            arms["A_monolithic_same_case"]["first_system_message_sha256"],
            arms["C_split_same_case_reordered"]["first_system_message_sha256"],
        )
        self.assertNotEqual(
            arms["A_monolithic_same_case"]["first_system_message_sha256"],
            arms["D_split_cross_case_top1"]["first_system_message_sha256"],
        )
        self.assertIn("does not establish", result["claim_ceiling"])

    def test_adjudication_binds_receipts_and_keeps_behavior_gate_closed(self) -> None:
        adjudication = load_json("asset-first-stri-reasoningbank-native-reunion-adjudication-20260829.json")
        for receipt in adjudication["receipts"].values():
            self.assertEqual(receipt["sha256"], sha256(ROOT / receipt["path"]))
        self.assertFalse(adjudication["failure_differential"]["implementation_failure"])
        self.assertFalse(adjudication["belief_update"]["claim_expansion"])
        self.assertFalse(adjudication["belief_update"]["behavioral_propagation_established"])
        self.assertEqual(
            adjudication["source_release_audit"]["status"],
            "P1_BEHAVIOR_HOLD_MISSING_FIRST_PARTY_MEMORY_ARTIFACT_AND_ENVIRONMENT",
        )
        self.assertFalse(adjudication["next_gate"]["full_benchmark_authorized"])
        self.assertFalse(adjudication["next_gate"]["gpu_run_authorized"])
        self.assertFalse(adjudication["next_gate"]["provider_calls_authorized"])


if __name__ == "__main__":
    unittest.main()
