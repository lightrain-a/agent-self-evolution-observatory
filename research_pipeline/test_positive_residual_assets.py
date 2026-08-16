from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from .positive_residual_assets import build_positive_residual_asset_registry
from .principle_adjudication import audit_dead_end_counter_explanation
from .paper_first_problem_search_portfolio import _expansion_prompt, _positive_residual_asset_records, _positive_residual_priors, _valid_seed


class PositiveResidualAssetTest(unittest.TestCase):
    def test_b9_c2_residual_is_provenance_bound_and_zero_authority(self) -> None:
        registry=build_positive_residual_asset_registry()
        self.assertEqual(registry["asset_count"],1)
        self.assertFalse(registry["scientific_authority"])
        asset=registry["assets"][0]
        self.assertEqual(asset["asset_ref"],"positive-residual-asset:memory-effect-transport-b9-c2-20260816")
        self.assertEqual(asset["phenomenon_status"],"SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE")
        self.assertEqual(registry["registry_id"],"positive-residual-search-assets-v3")
        self.assertEqual(asset["mechanism_status"],"LOCAL_MECHANISMS_STOPPED_TEMPORAL_EXPOSURE_REDUCED_TO_LONGITUDINAL_TREATMENT")
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}",asset["source_sha256"]))
        self.assertEqual(asset["provenance"]["frozen_raw_traces_sha256"],"45d9954a14f370936b5e1129f985130f4b9ef2b742e72a4c6e1e01bc068b1fbf")
        self.assertEqual(asset["provenance"]["frozen_main_table_sha256"],"eb861663351041e1f1a297b6791c7d31b4ba18285c3a13f0603d5d80c09b324f")
        contract=asset["search_contract"]
        self.assertTrue(contract["prospective_prediction_required"])
        self.assertTrue(contract["pre_outcome_information_only"])
        self.assertTrue(any("full-trajectory" in row for row in contract["prohibited_rescues"]))
        self.assertTrue(contract["temporal_exposure_standalone_branch_closed"])
        self.assertIn("nonstationary or versioned treatment models",contract["mandatory_reduction_before_treatment_semantics_experiment"])
        self.assertIn("mutates the executable semantics/version identity",contract["opposite_search_seed"])
        self.assertNotIn("temporally distributed exposure window",contract["opposite_search_seed"])
        self.assertEqual(len(asset["failed_mechanisms"]),4)
        self.assertEqual(asset["provenance"]["local_mechanism_readjudication"]["sha256"],"60a5f330049613f7163e2fee5bfa5f82e32283fed1951e32da83e9f11e712552")
        self.assertEqual(asset["provenance"]["temporal_exposure_readjudication"]["sha256"],"2656e6faf2132ebdac5842f8249eef90d5ae18aa3fef0a7c0956084c2dbaeff1")
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
        self.assertIn("DO NOT propose K-step mediation, ON/OFF exposure windows",prompt)
        priors=_positive_residual_priors(memory)
        self.assertTrue(priors[0]["temporal_exposure_standalone_branch_closed"])
        self.assertIn("nonstationary or versioned treatment models",priors[0]["mandatory_reduction_before_treatment_semantics_experiment"])
        seed={"discovery_lane":"UNEXPLAINED_BOUNDARY","title":"Prospective memory effect boundary","problem_seed":"Which pre-outcome state property predicts a memory endpoint effect only in contexts where the old transport and first-action mechanisms fail?","structural_signature":"memory|pre-outcome-state|context|endpoint-effect","empirical_evidence":{"source_a":{"ref":ref,"claim":"Controlled nonzero effects survive the failed transport representation.","evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":ref,"claim":"Earliest-action mediation is unsupported on execution-valid C2 units.","evidence_role":"EMPIRICAL_FACT"},"relation":"The same provenance asset establishes a surviving phenomenon and two failed mechanism realizations."},"lane_evidence":{"shared_measurement":"controlled memory effect on frozen units","boundary_observation":"the parent endpoint effect survives","adjacent_regime":"the historical transport and earliest-action mechanisms fail","unexplained_transition":"a prospective pre-outcome carrier remains unidentified"}}
        self.assertTrue(_valid_seed(seed,{ref:record}))
        self.assertFalse(record["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
