from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from .positive_residual_assets import build_positive_residual_asset_registry
from .principle_adjudication import audit_dead_end_counter_explanation
from .paper_first_problem_search_portfolio import _expansion_prompt, _positive_residual_asset_records, _positive_residual_priors


class PositiveResidualAssetTest(unittest.TestCase):
    def test_b9_c2_residual_is_provenance_bound_and_zero_authority(self) -> None:
        registry=build_positive_residual_asset_registry()
        self.assertEqual(registry["asset_count"],1)
        self.assertFalse(registry["scientific_authority"])
        asset=registry["assets"][0]
        self.assertEqual(asset["asset_ref"],"positive-residual-asset:memory-effect-transport-b9-c2-20260816")
        self.assertEqual(asset["phenomenon_status"],"SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE")
        self.assertEqual(registry["registry_id"],"positive-residual-search-assets-v4")
        self.assertEqual(registry["active_asset_count"],0)
        self.assertEqual(asset["mechanism_status"],"NO_ACTIVE_MECHANISM_AFTER_LOCAL_TEMPORAL_AND_TREATMENT_SEMANTICS_REDUCTIONS")
        self.assertEqual(asset["search_status"],"ARCHIVED_NO_ACTIVE_MECHANISM_SEED")
        self.assertFalse(asset["search_active"])
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}",asset["source_sha256"]))
        self.assertEqual(asset["provenance"]["frozen_raw_traces_sha256"],"45d9954a14f370936b5e1129f985130f4b9ef2b742e72a4c6e1e01bc068b1fbf")
        self.assertEqual(asset["provenance"]["frozen_main_table_sha256"],"eb861663351041e1f1a297b6791c7d31b4ba18285c3a13f0603d5d80c09b324f")
        contract=asset["search_contract"]
        self.assertTrue(contract["prospective_prediction_required"])
        self.assertTrue(contract["pre_outcome_information_only"])
        self.assertTrue(any("full-trajectory" in row for row in contract["prohibited_rescues"]))
        self.assertTrue(contract["temporal_exposure_standalone_branch_closed"])
        self.assertTrue(contract["treatment_semantics_standalone_branch_closed"])
        self.assertFalse(contract["active_mechanism_seed"])
        self.assertIn("nonstationary or versioned treatment models",contract["mandatory_reduction_before_treatment_semantics_experiment"])
        self.assertIn("No active mechanism seed remains",contract["opposite_search_seed"])
        self.assertNotIn("temporally distributed exposure window",contract["opposite_search_seed"])
        self.assertEqual(len(asset["failed_mechanisms"]),4)
        self.assertEqual(asset["provenance"]["local_mechanism_readjudication"]["sha256"],"60a5f330049613f7163e2fee5bfa5f82e32283fed1951e32da83e9f11e712552")
        self.assertEqual(asset["provenance"]["temporal_exposure_readjudication"]["sha256"],"2656e6faf2132ebdac5842f8249eef90d5ae18aa3fef0a7c0956084c2dbaeff1")
        self.assertEqual(asset["provenance"]["treatment_semantics_readjudication"]["sha256"],"ed09316950002ca43b88c427da70dc22e30f6f17076ef7c3010c604ef6f1269e")
        self.assertFalse(asset["scientific_authority"])
        self.assertTrue(all(value is False for value in asset["authority"].values()))

    def test_temporal_exposure_is_closed_by_principle_reduction_not_negative_experiment(self) -> None:
        path=Path(__file__).resolve().parents[1]/"generated"/"positive-residual-memory-temporal-exposure-principle-readjudication-20260816.json"
        payload=json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["principle_dead_end_certified"])
        self.assertFalse(payload["experiment_run_for_this_readjudication"])
        self.assertFalse(payload["broader_parent_phenomenon_falsified"])
        counter=payload["principle_diagnosis"]["counter_explanation"]
        audit=audit_dead_end_counter_explanation(counter)
        self.assertTrue(audit["passed"],audit["blockers"])
        self.assertEqual(counter["type"],"SAME_INFORMATION_REDUCTION")
        self.assertEqual(counter["opposite_principle"],"Persistent context is a repeated intervention, not a new causal primitive.")
        self.assertIn("nonstationary/versioned-treatment",counter["reopen_condition"])

    def test_treatment_semantics_is_closed_by_same_information_parity_not_rollout(self) -> None:
        path=Path(__file__).resolve().parents[1]/"generated"/"positive-residual-memory-treatment-semantics-principle-readjudication-20260816.json"
        payload=json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["principle_dead_end_certified"])
        self.assertFalse(payload["experiment_run_for_this_readjudication"])
        self.assertFalse(payload["broader_parent_phenomenon_falsified"])
        counter=payload["principle_diagnosis"]["counter_explanation"]
        audit=audit_dead_end_counter_explanation(counter)
        self.assertTrue(audit["passed"],audit["blockers"])
        self.assertEqual(counter["type"],"SAME_INFORMATION_REDUCTION")
        self.assertIn("part of treatment identity",counter["opposite_principle"])
        self.assertIn("withholding information from the baseline is insufficient",counter["reopen_condition"])

    def test_archived_positive_residual_stays_in_registry_but_not_search_inputs(self) -> None:
        registry=build_positive_residual_asset_registry()
        memory={"positive_residual_asset_evidence":registry["assets"],"blocked_objects":[]}
        self.assertEqual(registry["asset_count"],1)
        self.assertEqual(registry["active_asset_count"],0)
        self.assertEqual(_positive_residual_asset_records(memory),[])
        self.assertEqual(_positive_residual_priors(memory),[])
        prompt=_expansion_prompt("UNEXPLAINED_BOUNDARY",[],4,memory)
        self.assertNotIn("POSITIVE-RESIDUAL EXECUTION REQUIREMENT",prompt)
        self.assertIn("POSITIVE_RESIDUAL_ASSETS=[]",prompt)


if __name__ == "__main__":
    unittest.main()
