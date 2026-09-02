from __future__ import annotations

import unittest
from pathlib import Path

from scripts.audit_e2_r17_e3_p0_substrate import EXPECTED_FAMILIES, P0_STATUS

ROOT = Path(__file__).resolve().parents[1]


class E2R17E3P0SubstrateTests(unittest.TestCase):
    def test_families_are_predeclared_and_complete(self) -> None:
        self.assertEqual(
            EXPECTED_FAMILIES,
            {
                "agj": "aggregation_join",
                "fmv": "formula_materialization",
                "ioc": "input_output_contract",
                "msp": "multi_step_pipeline",
                "ska": "schema_key_alignment",
                "tsr": "target_sheet_range",
            },
        )
        self.assertEqual(P0_STATUS, "P0_STRUCTURAL_SUBSTRATE_PASS_D0_POWER_PENDING")

    def test_p0_audit_is_outcome_blind(self) -> None:
        source = (ROOT / "scripts/audit_e2_r17_e3_p0_substrate.py").read_text(encoding="utf-8")
        self.assertNotIn('["score"]', source)
        self.assertNotIn("['score']", source)
        self.assertIn('"scientific_outcomes_read": False', source)
        self.assertIn('"v2_effects_read_by_p0": False', source)
        self.assertIn('"provider_calls": 0', source)

    def test_p0_grants_no_execution_authority(self) -> None:
        source = (ROOT / "scripts/audit_e2_r17_e3_p0_substrate.py").read_text(encoding="utf-8")
        for forbidden in (
            '"provider_io": False',
            '"new_search_pool_acquisition": False',
            '"v2_family_analysis": False',
            '"d0_calibration": False',
            '"confirmatory_execution": False',
            '"heldout_evaluation": False',
            '"gpu": False',
            '"second_backbone": False',
            '"public_benchmark": False',
            '"paper_promotion": False',
            '"submission": False',
        ):
            self.assertIn(forbidden, source)

    def test_heldout_set_is_all_unused_block4_not_subsampled(self) -> None:
        source = (ROOT / "scripts/audit_e2_r17_e3_p0_substrate.py").read_text(encoding="utf-8")
        self.assertIn('"ALL_PREVIOUSLY_UNSPLIT_BLOCK4_TASKS_NO_SUBSAMPLING"', source)
        self.assertIn("len(e3_probe) == 36", source)
        self.assertIn("family: 6 for family in EXPECTED_FAMILIES", source)


if __name__ == "__main__":
    unittest.main()
