from __future__ import annotations

import re
import unittest

from .positive_residual_assets import build_positive_residual_asset_registry
from .paper_first_problem_search_portfolio import _expansion_prompt, _positive_residual_asset_records, _valid_seed


class PositiveResidualAssetTest(unittest.TestCase):
    def test_b9_c2_residual_is_provenance_bound_and_zero_authority(self) -> None:
        registry=build_positive_residual_asset_registry()
        self.assertEqual(registry["asset_count"],1)
        self.assertFalse(registry["scientific_authority"])
        asset=registry["assets"][0]
        self.assertEqual(asset["asset_ref"],"positive-residual-asset:memory-effect-transport-b9-c2-20260816")
        self.assertEqual(asset["phenomenon_status"],"SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE")
        self.assertEqual(registry["registry_id"],"positive-residual-search-assets-v2")
        self.assertEqual(asset["mechanism_status"],"FOUR_LOCAL_OR_REPRESENTATIONAL_EXPLANATIONS_STOPPED")
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}",asset["source_sha256"]))
        self.assertEqual(asset["provenance"]["frozen_raw_traces_sha256"],"45d9954a14f370936b5e1129f985130f4b9ef2b742e72a4c6e1e01bc068b1fbf")
        self.assertEqual(asset["provenance"]["frozen_main_table_sha256"],"eb861663351041e1f1a297b6791c7d31b4ba18285c3a13f0603d5d80c09b324f")
        contract=asset["search_contract"]
        self.assertTrue(contract["prospective_prediction_required"])
        self.assertTrue(contract["pre_outcome_information_only"])
        self.assertTrue(any("full-trajectory" in row for row in contract["prohibited_rescues"]))
        self.assertIn("time-varying treatment effects / distributed-lag causal models",contract["mandatory_reduction_before_temporal_exposure_experiment"])
        self.assertIn("temporally distributed exposure window",contract["opposite_search_seed"])
        self.assertEqual(len(asset["failed_mechanisms"]),4)
        self.assertEqual(asset["provenance"]["local_mechanism_readjudication"]["sha256"],"60a5f330049613f7163e2fee5bfa5f82e32283fed1951e32da83e9f11e712552")
        self.assertFalse(asset["scientific_authority"])
        self.assertTrue(all(value is False for value in asset["authority"].values()))

    def test_shadow_search_record_keeps_experiment_as_primary_evidence_not_authority(self) -> None:
        registry=build_positive_residual_asset_registry()
        memory={"positive_residual_asset_evidence":registry["assets"]}
        records=_positive_residual_asset_records(memory)
        self.assertEqual(len(records),1)
        record=records[0]
        self.assertTrue(record["primary_source_verified"])
        self.assertTrue(record["primary_url"].startswith("https://github.com/"))
        self.assertFalse(record["scientific_authority"])
        self.assertGreaterEqual(len(record["empirical_facts"]),5)

    def test_unexplained_boundary_executes_positive_residual_prior_without_authority(self) -> None:
        registry=build_positive_residual_asset_registry();memory={"positive_residual_asset_evidence":registry["assets"],"blocked_objects":[]}
        records=_positive_residual_asset_records(memory);record=records[0];ref=record["ref"]
        prompt=_expansion_prompt("UNEXPLAINED_BOUNDARY",[],4,memory)
        self.assertIn("POSITIVE-RESIDUAL EXECUTION REQUIREMENT",prompt)
        self.assertIn(ref,prompt)
        self.assertIn("prospective prediction from pre-outcome information",prompt)
        seed={"discovery_lane":"UNEXPLAINED_BOUNDARY","title":"Prospective memory effect boundary","problem_seed":"Which pre-outcome state property predicts a memory endpoint effect only in contexts where the old transport and first-action mechanisms fail?","structural_signature":"memory|pre-outcome-state|context|endpoint-effect","empirical_evidence":{"source_a":{"ref":ref,"claim":"Controlled nonzero effects survive the failed transport representation.","evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":ref,"claim":"Earliest-action mediation is unsupported on execution-valid C2 units.","evidence_role":"EMPIRICAL_FACT"},"relation":"The same provenance asset establishes a surviving phenomenon and two failed mechanism realizations."},"lane_evidence":{"shared_measurement":"controlled memory effect on frozen units","boundary_observation":"the parent endpoint effect survives","adjacent_regime":"the historical transport and earliest-action mechanisms fail","unexplained_transition":"a prospective pre-outcome carrier remains unidentified"}}
        self.assertTrue(_valid_seed(seed,{ref:record}))
        self.assertFalse(record["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
