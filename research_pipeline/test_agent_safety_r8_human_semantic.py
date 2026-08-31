import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_safety_r8_human_semantic import (
    BLIND_IDS,
    PACKET_SHA256,
    HumanLabelValidationError,
    compare_raters,
    finalize_blinded_human_labels,
    make_adjudication_template,
    validate_rater_response,
)


def _response(role: str, rater_id: str, overrides=None):
    overrides = overrides or {}
    labels = []
    for blind_id in BLIND_IDS:
        label = overrides.get(blind_id, "REFUSAL_OR_SAFE_HANDLING")
        labels.append(
            {
                "blind_id": blind_id,
                "primary_label": label,
                "confidence": "HIGH",
                "insufficient_context": False,
                "notes": "synthetic validator fixture only",
            }
        )
    return {
        "schema_version": "1.0",
        "paper_id": "AGENT-SAFETY-R9",
        "packet_sha256": PACKET_SHA256,
        "response_role": role,
        "rater_id": rater_id,
        "labels": labels,
        "attestation": {
            "human_reviewer": True,
            "independent_first_pass": True,
            "no_ai_assistance_for_labels": True,
            "did_not_view_private_key_or_machine_labels": True,
            "did_not_discuss_labels_with_other_first_pass_rater_before_freeze": True,
            "all_24_items_labeled_without_replacement": True,
        },
        "completed_at_local": "TEST_ONLY",
        "notes": "synthetic validator fixture; not scientific evidence",
    }


def _dump(root: Path, name: str, payload):
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class AgentSafetyR8HumanSemanticTest(unittest.TestCase):
    def test_valid_pair_no_adjudication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = _dump(root, "a.json", _response("RATER_A", "fixture-a"))
            b = _dump(root, "b.json", _response("RATER_B", "fixture-b"))
            summary = compare_raters(a, b)
            self.assertEqual(summary["exact_primary_label_agreement_count"], 24)
            self.assertEqual(summary["cohen_kappa_three_class"], 1.0)
            self.assertEqual(summary["primary_label_disagreement_ids"], [])
            final = finalize_blinded_human_labels(a, b)
            self.assertEqual(final["binary_event_projection_count"], 0)
            self.assertFalse(final["private_key_opened"])

    def test_conflict_requires_third_adjudicator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = _dump(root, "a.json", _response("RATER_A", "fixture-a"))
            b = _dump(
                root,
                "b.json",
                _response("RATER_B", "fixture-b", {"S03": "TASK_DIRECTED_INTERACTION"}),
            )
            summary = compare_raters(a, b)
            self.assertEqual(summary["primary_label_disagreement_ids"], ["S03"])
            with self.assertRaises(HumanLabelValidationError):
                finalize_blinded_human_labels(a, b)
            template = make_adjudication_template(a, b)
            self.assertEqual([row["blind_id"] for row in template["labels"]], ["S03"])
            template["adjudicator_id"] = "fixture-c"
            template["labels"][0]["primary_label"] = "TASK_DIRECTED_INTERACTION"
            template["labels"][0]["confidence"] = "HIGH"
            for key in template["attestation"]:
                template["attestation"][key] = True
            template["completed_at_local"] = "TEST_ONLY"
            c = _dump(root, "c.json", template)
            final = finalize_blinded_human_labels(a, b, c)
            row = next(row for row in final["final_labels"] if row["blind_id"] == "S03")
            self.assertEqual(row["decision_source"], "THIRD_ADJUDICATOR")
            self.assertEqual(row["binary_event_projection"], 1)

    def test_adjudicator_cannot_rewrite_frozen_source_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = _dump(root, "a.json", _response("RATER_A", "fixture-a"))
            b = _dump(
                root,
                "b.json",
                _response("RATER_B", "fixture-b", {"S03": "TASK_DIRECTED_INTERACTION"}),
            )
            template = make_adjudication_template(a, b)
            template["adjudicator_id"] = "fixture-c"
            template["labels"][0]["rater_a_label"] = "OTHER_OR_DRIFT"
            template["labels"][0]["primary_label"] = "TASK_DIRECTED_INTERACTION"
            template["labels"][0]["confidence"] = "HIGH"
            for key in template["attestation"]:
                template["attestation"][key] = True
            template["completed_at_local"] = "TEST_ONLY"
            c = _dump(root, "c.json", template)
            with self.assertRaises(HumanLabelValidationError):
                finalize_blinded_human_labels(a, b, c)

    def test_insufficient_context_rule_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obj = _response("RATER_A", "fixture-a")
            obj["labels"][0]["insufficient_context"] = True
            obj["labels"][0]["confidence"] = "HIGH"
            path = _dump(root, "bad.json", obj)
            with self.assertRaises(HumanLabelValidationError):
                validate_rater_response(path)

    def test_hidden_metadata_field_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obj = _response("RATER_A", "fixture-a")
            obj["labels"][0]["arm"] = "hidden"
            path = _dump(root, "bad.json", obj)
            with self.assertRaises(HumanLabelValidationError):
                validate_rater_response(path)

    def test_incomplete_attestation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obj = _response("RATER_A", "fixture-a")
            obj["attestation"]["no_ai_assistance_for_labels"] = False
            path = _dump(root, "bad.json", obj)
            with self.assertRaises(HumanLabelValidationError):
                validate_rater_response(path)


if __name__ == "__main__":
    unittest.main()
