from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_falsifier_preflight import (
    build_support_inventory_request,
    compile_problem_falsifier_preflight,
    write_problem_falsifier_preflight,
    write_support_inventory_request,
)


class ProblemFalsifierPreflightTest(unittest.TestCase):
    def machine(self) -> dict:
        candidate={
            "candidate_id":"SHADOW-P01-C01",
            "title":"Pending residual",
            "discovery_lane":"UNEXPLAINED_BOUNDARY",
            "source_branch_id":"B1",
            "empirical_evidence":{
                "source_a":{"ref":"arXiv:2608.00001"},
                "source_b":{"ref":"arXiv:2608.00001"},
            },
        }
        return {
            "schema_version":"1.2-shadow",
            "scientific_authority":False,
            "authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            "reduction_pending":[{"candidate_id":"SHADOW-P01-C01","candidate":candidate}],
            "problem_falsifier_queue":[{
                "candidate_id":"SHADOW-P01-C01",
                "title":"Pending residual",
                "discovery_lane":"UNEXPLAINED_BOUNDARY",
                "source_branch_id":"B1",
                "exact_prediction":"The residual survives a matched comparison.",
                "strongest_same_information_baseline":"mature matched baseline",
                "cheapest_problem_falsifier":"Compare the matched units while varying only the claimed moderator.",
                "scientific_authority":False,
            }],
        }

    def hold_inventory(self) -> dict:
        return {
            "inventory_origin":"unit-test-primary-asset-audit",
            "rows":[{
                "candidate_id":"SHADOW-P01-C01",
                "disposition":"HOLD_SUPPORT_UNAVAILABLE",
                "required_unit":"Matched released units exposing the moderator and outcome.",
                "asset_audit":"The primary release does not expose the matched unit-level table.",
                "primary_refs":["arXiv:2608.00001"],
                "reopen_only_if":"The authors release the required matched unit-level table.",
            }],
            "scientific_authority":False,
        }

    def test_request_is_zero_authority_and_does_not_claim_availability(self) -> None:
        request=build_support_inventory_request(self.machine(),run_id="shadow-rx")
        self.assertEqual(request["status"],"PROBLEM_FALSIFIER_SUPPORT_INVENTORY_REQUEST_READY")
        self.assertEqual(request["summary"]["queued"],1)
        row=request["rows"][0]
        self.assertEqual(row["primary_refs"],["arXiv:2608.00001"])
        self.assertIn("Determine whether",row["support_inventory_question"])
        self.assertIn("materialize", row["support_inventory_question"])
        self.assertTrue(request["policy"]["direct_released_unit_table_not_required_for_reconstructible_truth"])
        self.assertTrue(request["policy"]["first_party_code_may_materialize_independent_support_truth"])
        self.assertFalse(request["scientific_authority"])
        self.assertFalse(request["authority"]["paper_design"])
        self.assertTrue(request["policy"]["support_inventory_request_cannot_claim_asset_availability"])

    def test_hold_compiles_without_scientific_falsification_or_execution_authority(self) -> None:
        state=compile_problem_falsifier_preflight(self.machine(),self.hold_inventory(),run_id="shadow-rx",inventory_sha256="a"*64)
        self.assertEqual((state["summary"]["queued"],state["summary"]["support_qualified"],state["summary"]["hold_support_unavailable"],state["summary"]["falsifier_executed"]),(1,0,1,0))
        self.assertEqual(state["rows"][0]["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertIn("release",state["rows"][0]["reopen_only_if"].lower())
        self.assertTrue(state["policy"]["support_unavailable_is_not_scientific_falsification"])
        self.assertFalse(state["authority"]["experiment"])
        self.assertFalse(state["authority"]["gpu"])

    def test_support_qualified_requires_positive_units_and_content_manifest_but_still_no_execution_authority(self) -> None:
        inventory={"inventory_origin":"verified-private-support-inventory","rows":[{
            "candidate_id":"SHADOW-P01-C01","disposition":"SUPPORT_QUALIFIED",
            "required_unit":"Matched unit-level records.","asset_audit":"Verified from the author-released artifact.",
            "primary_refs":["arXiv:2608.00001"],"qualified_units":12,"unit_manifest_sha256":"b"*64,
            "support_scope":"Twelve matched units expose the required moderator and outcome under the frozen candidate definition.",
        }],"scientific_authority":False}
        state=compile_problem_falsifier_preflight(self.machine(),inventory,run_id="shadow-rx",inventory_sha256="c"*64)
        row=state["rows"][0]
        self.assertEqual(state["summary"]["support_qualified"],1)
        self.assertEqual(row["qualified_units"],12)
        self.assertFalse(row["falsifier_execution_authorized"])
        bad=json.loads(json.dumps(inventory));bad["rows"][0]["qualified_units"]=0
        with self.assertRaisesRegex(ValueError,"positive qualified_units"):
            compile_problem_falsifier_preflight(self.machine(),bad,run_id="shadow-rx")

    def test_reconstructed_support_requires_executed_materialization_provenance_and_anti_leakage_flags(self) -> None:
        inventory={"inventory_origin":"first-party-reconstruction-audit","rows":[{
            "candidate_id":"SHADOW-P01-C01","disposition":"SUPPORT_QUALIFIED",
            "required_unit":"Matched unit-level records.","asset_audit":"Materialized from frozen first-party code after the operationalization was frozen.",
            "primary_refs":["arXiv:2608.00001"],"support_mode":"FIRST_PARTY_CODE_RECONSTRUCTION",
            "qualified_units":8,"unit_manifest_sha256":"b"*64,
            "support_scope":"Eight materialized units expose the frozen moderator and outcome without changing the candidate pool.",
            "reconstruction_receipt":{
                "substrate_id":"author/repo",
                "source_or_substrate_revision":"deadbeef",
                "materialization_command":"python reproduce.py --frozen-contract contract.json",
                "provenance_sha256":"d"*64,
                "operationalization_frozen_before_outcomes":True,
                "independent_truth":True,
                "synthetic_substitution":False,
                "candidate_mechanism_injected":False,
                "candidate_pool_changed":False,
                "hidden_outcome_retuning":False,
            },
        }],"scientific_authority":False}
        state=compile_problem_falsifier_preflight(self.machine(),inventory,run_id="shadow-rx",inventory_sha256="c"*64)
        row=state["rows"][0]
        self.assertEqual(row["support_mode"],"FIRST_PARTY_CODE_RECONSTRUCTION")
        self.assertEqual(row["qualified_units"],8)
        self.assertEqual(row["reconstruction_receipt"]["provenance_sha256"],"d"*64)
        self.assertFalse(row["falsifier_execution_authorized"])

        missing=json.loads(json.dumps(inventory));missing["rows"][0].pop("reconstruction_receipt")
        with self.assertRaisesRegex(ValueError,"reconstruction_receipt"):
            compile_problem_falsifier_preflight(self.machine(),missing,run_id="shadow-rx")
        leaked=json.loads(json.dumps(inventory));leaked["rows"][0]["reconstruction_receipt"]["candidate_mechanism_injected"]=True
        with self.assertRaisesRegex(ValueError,"anti-leakage"):
            compile_problem_falsifier_preflight(self.machine(),leaked,run_id="shadow-rx")

    def test_existing_provenance_substrate_uses_the_same_reconstruction_contract(self) -> None:
        inventory={"inventory_origin":"existing-substrate-reconstruction-audit","rows":[{
            "candidate_id":"SHADOW-P01-C01","disposition":"SUPPORT_QUALIFIED",
            "required_unit":"Matched unit-level records.","asset_audit":"Materialized from an existing provenance-audited local substrate.",
            "primary_refs":["arXiv:2608.00001"],"support_mode":"EXISTING_PROVENANCE_SUBSTRATE",
            "qualified_units":6,"unit_manifest_sha256":"e"*64,
            "support_scope":"Six independent units under the frozen source-grounded operationalization.",
            "reconstruction_receipt":{
                "substrate_id":"local/replay-v3",
                "source_or_substrate_revision":"manifest-20260815",
                "materialization_command":"python replay.py --contract frozen.json",
                "provenance_sha256":"f"*64,
                "operationalization_frozen_before_outcomes":True,
                "independent_truth":True,
                "synthetic_substitution":False,
                "candidate_mechanism_injected":False,
                "candidate_pool_changed":False,
                "hidden_outcome_retuning":False,
            },
        }],"scientific_authority":False}
        row=compile_problem_falsifier_preflight(self.machine(),inventory,run_id="shadow-rx")["rows"][0]
        self.assertEqual(row["support_mode"],"EXISTING_PROVENANCE_SUBSTRATE")
        self.assertEqual(row["qualified_units"],6)

    def test_inventory_must_cover_queue_exactly_and_stay_grounded_to_candidate_refs(self) -> None:
        missing={"inventory_origin":"x","rows":[],"scientific_authority":False}
        with self.assertRaisesRegex(ValueError,"cover problem falsifier queue exactly"):
            compile_problem_falsifier_preflight(self.machine(),missing,run_id="shadow-rx")
        wrong=self.hold_inventory();wrong["rows"][0]["primary_refs"]=["arXiv:2608.99999"]
        with self.assertRaisesRegex(ValueError,"not grounded"):
            compile_problem_falsifier_preflight(self.machine(),wrong,run_id="shadow-rx")

    def test_file_cli_helpers_preserve_inventory_sha_and_do_not_touch_machine_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"shadow-rx";root.mkdir();machine=root/"machine-audit.json";inventory=root/"support.json"
            machine.write_text(json.dumps(self.machine()),encoding="utf-8");inventory.write_text(json.dumps(self.hold_inventory()),encoding="utf-8")
            before=hashlib.sha256(machine.read_bytes()).hexdigest()
            request=write_support_inventory_request(run_root=root)
            state=write_problem_falsifier_preflight(run_root=root,support_inventory_path=inventory)
            self.assertEqual(request["summary"]["inventory_requests"],1)
            self.assertEqual(state["support_inventory_sha256"],hashlib.sha256(inventory.read_bytes()).hexdigest())
            self.assertEqual(before,hashlib.sha256(machine.read_bytes()).hexdigest())
            self.assertTrue((root/"problem-falsifier-support-inventory-request.json").exists())
            self.assertTrue((root/"problem-falsifier-preflight.json").exists())


if __name__=="__main__":
    unittest.main()
