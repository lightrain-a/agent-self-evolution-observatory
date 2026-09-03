from __future__ import annotations

import hashlib
import json
import unittest

from research_pipeline import failure_memory_memrl_full350_contract_r53 as contract
from research_pipeline.failure_memory_memrl_source_execute_r53 import (
    _materialize_full350_ids,
    _verify_receipt_hash,
)


class Full350R53Test(unittest.TestCase):
    def test_generated_contract_manifest_authority_are_sealed(self) -> None:
        for path in (contract.CONTRACT, contract.MANIFEST, contract.AUTH):
            row = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(_verify_receipt_hash(row), path.name)

    def test_manifest_freezes_full_universe_digest_without_manual_id_list(self) -> None:
        row = json.loads(contract.MANIFEST.read_text(encoding="utf-8"))
        sb = row["execution_manifest"]["source_build"]
        self.assertEqual(sb["selected_count"], 350)
        self.assertEqual(sb["selected_ids_sha256"], contract.SOURCE_ORDER_SHA256)
        self.assertEqual(sb["selection_seed_string"], contract.SOURCE_SEED)
        self.assertNotIn("selected_ids", sb)

    def test_authority_opens_source_only(self) -> None:
        row = json.loads(contract.AUTH.read_text(encoding="utf-8"))
        scope = row["authorized_scope"]
        self.assertTrue(scope["source_build"]["authorized"])
        self.assertEqual(scope["source_build"]["exact_selected_source_tasks"], 350)
        self.assertFalse(scope["fresh_validation_selection"]["authorized_after_source_complete"])
        self.assertFalse(scope["utilization"]["authorized"])
        self.assertFalse(scope["AB_confirmatory"]["authorized"])

    def test_materialization_is_hash_ordered_and_count_guarded(self) -> None:
        dataset = {str(i): {} for i in range(350)}
        seed = contract.SOURCE_SEED
        expected = sorted(dataset, key=lambda x: hashlib.sha256(f"{seed}|{x}".encode()).hexdigest())
        sb = {
            "selection_seed_string": seed,
            "selected_ids_sha256": hashlib.sha256("\n".join(expected).encode()).hexdigest(),
        }
        self.assertEqual(_materialize_full350_ids(dataset, sb), expected)
        with self.assertRaises(RuntimeError):
            _materialize_full350_ids({str(i): {} for i in range(349)}, sb)

    def test_program_excludes_old_validation_and_cd(self) -> None:
        row = json.loads(contract.CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(row["pilot_boundary"]["old_40_validation_clusters_eligible_for_R53"])
        self.assertFalse(row["PSMG_CD"]["execution"])
        self.assertEqual(row["AB_confirmatory"]["arms"], ["A_content_only", "B_raw_provenance"])


if __name__ == "__main__":
    unittest.main()
