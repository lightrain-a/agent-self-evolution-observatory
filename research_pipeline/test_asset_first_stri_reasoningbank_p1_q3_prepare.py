from __future__ import annotations

import hashlib
import json
import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    canonical_json, sha256_file, sha256_text,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_prepare import (
    CONTRACT, FIXTURES, MANIFEST_DIR, SELECTION, validate_existing,
)


def payload_valid(path) -> bool:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = value.pop("payload_sha256")
    return expected == sha256_text(canonical_json(value))


class ReasoningBankP1Q3PreparationTest(unittest.TestCase):
    def test_q3_is_fresh_ranked_and_nonreplacement(self) -> None:
        fixture = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual(
            [(row["selection_rank"], row["instance_id"]) for row in fixture["fixtures"]],
            [(5, "sphinx-doc__sphinx-9230"), (6, "django__django-11880")],
        )
        self.assertTrue(fixture["checks"]["source_and_prior_pilot_disjoint"])
        self.assertTrue(fixture["checks"]["gold_patch_content_absent"])

    def test_contract_preserves_old_pilot_and_keeps_full_p1_closed(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertTrue(contract["outcome_discipline"]["old_ten_runs_immutable"])
        self.assertTrue(contract["outcome_discipline"]["q2_runs_immutable"])
        self.assertTrue(contract["outcome_discipline"]["failed_q2_runs_preserved"])
        self.assertTrue(
            contract["outcome_discipline"][
                "parser_implementation_only_after_q3_preregistration"
            ]
        )
        self.assertEqual(contract["selection"]["automatic_retry"], "forbidden")
        self.assertEqual(contract["selection"]["replacement_sampling"], "forbidden")
        self.assertFalse(contract["selection"]["uses_task_outcome"])
        self.assertFalse(contract["selection"]["uses_gold_patch"])
        self.assertFalse(contract["qualification"]["full_p1_execution_authorized"])
        self.assertFalse(contract["scientific_boundary"]["q3_task_outcome_observed"])
        self.assertEqual(
            contract["bindings"]["swebench_wheel_sha256"],
            "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62",
        )
        self.assertEqual(
            set(contract["bindings"]["official_parser_source"]),
            {"parse_log_django", "parse_log_sphinx"},
        )

    def test_fixed_manifests_and_payload_hashes_verify(self) -> None:
        self.assertTrue(payload_valid(FIXTURES))
        self.assertTrue(payload_valid(CONTRACT))
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["bindings"]["q3_fixtures_sha256"], sha256_file(FIXTURES)
        )
        for spec in SELECTION:
            for kind, expected in (
                ("index", spec["index_digest"]),
                ("amd64", spec["amd64_manifest_digest"]),
            ):
                path = MANIFEST_DIR / f"{spec['label']}-{kind}.json"
                actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_existing_artifacts_validate(self) -> None:
        self.assertEqual(validate_existing(), [])


if __name__ == "__main__":
    unittest.main()
