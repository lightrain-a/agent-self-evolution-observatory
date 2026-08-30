from __future__ import annotations

import hashlib
import json
import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    canonical_json, sha256_file, sha256_text,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q2_prepare import (
    CONTRACT, FIXTURES, MANIFEST_DIR, SELECTION, validate_existing,
)


def payload_valid(path) -> bool:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = value.pop("payload_sha256")
    return expected == sha256_text(canonical_json(value))


class ReasoningBankP1Q2PreparationTest(unittest.TestCase):
    def test_q2_is_fresh_ranked_and_nonreplacement(self) -> None:
        fixture = json.loads(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual(
            [(row["selection_rank"], row["instance_id"]) for row in fixture["fixtures"]],
            [(3, "django__django-16100"), (4, "sympy__sympy-18211")],
        )
        self.assertTrue(fixture["checks"]["source_and_prior_pilot_disjoint"])
        self.assertTrue(fixture["checks"]["gold_patch_content_absent"])

    def test_contract_preserves_old_pilot_and_keeps_full_p1_closed(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertTrue(contract["outcome_discipline"]["old_ten_runs_immutable"])
        self.assertEqual(contract["selection"]["automatic_retry"], "forbidden")
        self.assertEqual(contract["selection"]["replacement_sampling"], "forbidden")
        self.assertFalse(contract["selection"]["uses_task_outcome"])
        self.assertFalse(contract["selection"]["uses_gold_patch"])
        self.assertFalse(contract["qualification"]["full_p1_execution_authorized"])
        self.assertFalse(contract["scientific_boundary"]["q2_task_outcome_observed"])

    def test_fixed_manifests_and_payload_hashes_verify(self) -> None:
        self.assertTrue(payload_valid(FIXTURES))
        self.assertTrue(payload_valid(CONTRACT))
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["bindings"]["q2_fixtures_sha256"], sha256_file(FIXTURES)
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
