from __future__ import annotations

import unittest

from research_pipeline.agent_safety_g1_human_semantic_firstpass import (
    EXPECTED_IDS,
    PACKET_SHA256,
    HumanSemanticError,
    merge_first_pass,
    validate_response,
)


def response(role: str, rater_id: str, *, label: str = "TASK_DIRECTED_INTERACTION") -> dict:
    return {
        "schema_version": "1.0",
        "paper_id": "AGENT-SAFETY-R9",
        "packet_sha256": PACKET_SHA256,
        "response_role": role,
        "rater_id": rater_id,
        "labels": [
            {
                "blind_id": blind_id,
                "primary_label": label,
                "confidence": "HIGH",
                "insufficient_context": False,
                "notes": "",
            }
            for blind_id in EXPECTED_IDS
        ],
        "attestation": {
            "human_reviewer": True,
            "independent_first_pass": True,
            "no_ai_assistance_for_labels": True,
            "did_not_view_private_key_or_machine_labels": True,
            "did_not_discuss_labels_with_other_first_pass_rater_before_freeze": True,
            "all_24_items_labeled_without_replacement": True,
        },
        "completed_at_local": "2026-09-06T23:30:00+08:00",
        "notes": "",
    }


class HumanSemanticFirstPassTest(unittest.TestCase):
    def test_exact_agreement_ready_for_unblinding(self) -> None:
        out = merge_first_pass(response("RATER_A", "A01"), response("RATER_B", "B01"))
        self.assertEqual(out["exact_agreement_count"], 24)
        self.assertEqual(out["exact_agreement_rate"], 1.0)
        self.assertEqual(out["cohen_kappa"], 1.0)
        self.assertEqual(out["blind_adjudication_required_ids"], [])
        self.assertTrue(out["machine_label_unblinding_authorized"])
        self.assertEqual(out["status"], "HUMAN_FIRST_PASS_FROZEN_READY_FOR_MACHINE_UNBLINDING")

    def test_label_disagreement_requires_blind_adjudication(self) -> None:
        a = response("RATER_A", "A01")
        b = response("RATER_B", "B01")
        b["labels"][3]["primary_label"] = "REFUSAL_OR_SAFE_HANDLING"
        out = merge_first_pass(a, b)
        self.assertEqual(out["label_disagreement_ids"], ["S04"])
        self.assertEqual(out["blind_adjudication_required_ids"], ["S04"])
        self.assertFalse(out["machine_label_unblinding_authorized"])
        self.assertIsNone(out["rows"][3]["first_pass_consensus_label"])

    def test_insufficient_context_blocks_consensus_even_if_labels_match(self) -> None:
        a = response("RATER_A", "A01")
        b = response("RATER_B", "B01")
        for obj in (a, b):
            obj["labels"][0]["primary_label"] = "OTHER_OR_DRIFT"
            obj["labels"][0]["confidence"] = "LOW"
            obj["labels"][0]["insufficient_context"] = True
        out = merge_first_pass(a, b)
        self.assertEqual(out["insufficient_context_ids"], ["S01"])
        self.assertEqual(out["blind_adjudication_required_ids"], ["S01"])
        self.assertIsNone(out["rows"][0]["first_pass_consensus_label"])

    def test_distinct_raters_required(self) -> None:
        with self.assertRaisesRegex(HumanSemanticError, "distinct anonymous rater IDs"):
            merge_first_pass(response("RATER_A", "SAME"), response("RATER_B", "SAME"))

    def test_packet_sha_mismatch_fails_closed(self) -> None:
        a = response("RATER_A", "A01")
        a["packet_sha256"] = "0" * 64
        with self.assertRaisesRegex(HumanSemanticError, "packet SHA mismatch"):
            validate_response(a, expected_role="RATER_A")

    def test_duplicate_or_replaced_panel_fails_closed(self) -> None:
        a = response("RATER_A", "A01")
        a["labels"][1]["blind_id"] = "S01"
        with self.assertRaisesRegex(HumanSemanticError, "duplicate blind_id"):
            validate_response(a, expected_role="RATER_A")

    def test_false_attestation_fails_closed(self) -> None:
        a = response("RATER_A", "A01")
        a["attestation"]["no_ai_assistance_for_labels"] = False
        with self.assertRaisesRegex(HumanSemanticError, "attestation false/missing:no_ai_assistance_for_labels"):
            validate_response(a, expected_role="RATER_A")


if __name__ == "__main__":
    unittest.main()
