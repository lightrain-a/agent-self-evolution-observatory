from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .candidate_identity import attach_candidate_identity
from .paper_first_problem_falsifier_preflight import (
    build_support_inventory_request,
    build_support_inventory_request_from_pre_f0_queue,
    compile_pre_f0_problem_falsifier_preflight,
    compile_problem_falsifier_preflight,
    load_pre_f0_problem_falsifier_preflight,
    write_pre_f0_problem_falsifier_preflight,
    write_pre_f0_support_inventory_request,
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

    def pre_f0(self) -> dict:
        return {
            "schema_version":"1.0","status":"PRE_F0_QUEUE_READY","scientific_authority":False,
            "policy":{"cheap_falsifier_is_evidence_acquisition_not_problem_gate":True,"exact_reduction_required_before_problem_gate":True},
            "authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            "rows":[{
                "candidate_id":"PORT-001","title":"Pre-F0 residual","discovery_lane":"ASSUMPTION_BREAK","source_branch_id":"B-R1",
                "primary_refs":["arXiv:2608.00001","arXiv:2608.00002"],
                "exact_prediction":"The frozen residual reverses under the matched intervention.",
                "strongest_same_information_baseline":"Matched same-information baseline.",
                "cheapest_problem_falsifier":"Run the frozen matched falsifier on the released unit pair.",
                "next_if_positive":"RERUN_EXACT_SAME_INFORMATION_REDUCTION","scientific_authority":False,
                "authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            }],
        }

    def identity_fields(self, row: dict) -> dict:
        identified=attach_candidate_identity(row)
        return {
            "candidate_identity_version": identified["candidate_identity_version"],
            "candidate_snapshot_sha256": identified["candidate_snapshot_sha256"],
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

    def test_pre_f0_support_request_preserves_primary_refs_and_zero_authority(self) -> None:
        pre=self.pre_f0();request=build_support_inventory_request_from_pre_f0_queue(pre,run_id="pre-f0-r1")
        self.assertEqual(request["source"],"CANONICAL_PRE_F0_QUEUE")
        self.assertEqual(request["summary"]["queued"],1)
        self.assertEqual(request["rows"][0]["primary_refs"],["arXiv:2608.00001","arXiv:2608.00002"])
        self.assertEqual(request["rows"][0]["candidate_identity_version"],"candidate-content-v1")
        self.assertFalse(request["scientific_authority"]);self.assertFalse(request["authority"]["experiment"])
        inv={"inventory_origin":"pre-f0-asset-audit","rows":[{"candidate_id":"PORT-001",**self.identity_fields(pre["rows"][0]),"disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"Executable matched unit.","asset_audit":"The required harness parity is not released.","primary_refs":["arXiv:2608.00001"],"reopen_only_if":"The missing first-party harness is released."}],"scientific_authority":False}
        state=compile_pre_f0_problem_falsifier_preflight(pre,inv,run_id="pre-f0-r1",inventory_sha256="d"*64)
        self.assertEqual(state["summary"]["hold_support_unavailable"],1);self.assertEqual(state["summary"]["support_qualified"],0);self.assertFalse(state["authority"]["experiment"])

    def test_pre_f0_receipt_rejects_reused_port_ordinal_from_different_candidate_snapshot(self) -> None:
        pre=self.pre_f0();other=json.loads(json.dumps(pre["rows"][0]));other["title"]="A different candidate from a later search generation";other["source_branch_id"]="OTHER-BRANCH"
        wrong_identity=self.identity_fields(other)
        inventory={"inventory_origin":"cross-run-id-collision-test","rows":[{
            "candidate_id":"PORT-001",**wrong_identity,"disposition":"HOLD_SUPPORT_UNAVAILABLE",
            "required_unit":"Executable matched unit.","asset_audit":"A valid-looking receipt from a different PORT-001 generation.",
            "primary_refs":["arXiv:2608.00001"],"reopen_only_if":"The missing first-party harness is released.",
        }],"scientific_authority":False}
        with self.assertRaisesRegex(ValueError,"candidate snapshot identity mismatch"):
            compile_pre_f0_problem_falsifier_preflight(pre,inventory,run_id="pre-f0-r1")

    def test_pre_f0_file_helpers_write_request_and_compiled_hold(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);request_path=root/"request.json";inventory_path=root/"inventory.json";preflight_path=root/"preflight.json"
            pre=self.pre_f0();inv={"inventory_origin":"pre-f0-asset-audit","rows":[{"candidate_id":"PORT-001",**self.identity_fields(pre["rows"][0]),"disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"Executable matched unit.","asset_audit":"The required harness parity is not released.","primary_refs":["arXiv:2608.00001"],"reopen_only_if":"The missing first-party harness is released."}],"scientific_authority":False};inventory_path.write_text(json.dumps(inv),encoding="utf-8");expected_sha=hashlib.sha256(inventory_path.read_bytes()).hexdigest()
            request=write_pre_f0_support_inventory_request(pre_f0_queue=pre,output_path=request_path);state=write_pre_f0_problem_falsifier_preflight(pre_f0_queue=pre,support_inventory_path=inventory_path,output_path=preflight_path);loaded=load_pre_f0_problem_falsifier_preflight(preflight_path)
        self.assertEqual(request["summary"]["inventory_requests"],1);self.assertEqual(state["summary"]["hold_support_unavailable"],1);self.assertEqual(loaded["support_inventory_sha256"],expected_sha)

    def test_hold_compiles_without_scientific_falsification_or_execution_authority(self) -> None:
        state=compile_problem_falsifier_preflight(self.machine(),self.hold_inventory(),run_id="shadow-rx",inventory_sha256="a"*64)
        self.assertEqual((state["summary"]["queued"],state["summary"]["support_qualified"],state["summary"]["hold_support_unavailable"],state["summary"]["falsifier_executed"]),(1,0,1,0))
        self.assertEqual(state["rows"][0]["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertIn("release",state["rows"][0]["reopen_only_if"].lower())
        self.assertTrue(state["policy"]["support_unavailable_is_not_scientific_falsification"])
        self.assertFalse(state["authority"]["experiment"])
        self.assertFalse(state["authority"]["gpu"])

    def test_support_audit_binding_requires_exact_digest_identity_and_contract(self) -> None:
        audit_path=Path(__file__).parents[1]/"generated"/"zetta-timescale-support-audit-20260819.json"
        audit=json.loads(audit_path.read_text(encoding="utf-8"));digest=hashlib.sha256(audit_path.read_bytes()).hexdigest()
        pre=json.loads(json.dumps(self.pre_f0()));pre["rows"][0]["candidate_id"]="PORT-003";pre["rows"][0]["primary_refs"]=audit["source_refs"]
        inventory={"inventory_origin":"zetta-schema-audit-test","rows":[{
            "candidate_id":"PORT-003",**self.identity_fields(pre["rows"][0]),"disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":audit["required_unit"],
            "asset_audit":"The released schema blocks the frozen intermediate intervention arms.","primary_refs":audit["source_refs"],
            "support_audit_artifact":"generated/zetta-timescale-support-audit-20260819.json","support_audit_sha256":digest,
            "reopen_only_if":audit["reopen_only_if"],
        }],"scientific_authority":False}
        row=compile_pre_f0_problem_falsifier_preflight(pre,inventory,run_id="pre-f0-r1")["rows"][0]
        self.assertEqual(row["support_audit_sha256"],digest);self.assertFalse(row["scientific_authority"])
        bad=json.loads(json.dumps(inventory));bad["rows"][0]["support_audit_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"artifact digest mismatch"):
            compile_pre_f0_problem_falsifier_preflight(pre,bad,run_id="pre-f0-r1")
        bad=json.loads(json.dumps(inventory));bad["rows"][0]["reopen_only_if"]="A different reopen contract."
        with self.assertRaisesRegex(ValueError,"reopen contract mismatch"):
            compile_pre_f0_problem_falsifier_preflight(pre,bad,run_id="pre-f0-r1")

    def test_support_audit_binding_rejects_wrong_candidate_identity(self) -> None:
        audit_path=Path(__file__).parents[1]/"generated"/"zetta-timescale-support-audit-20260819.json"
        audit=json.loads(audit_path.read_text(encoding="utf-8"));digest=hashlib.sha256(audit_path.read_bytes()).hexdigest()
        inventory={"inventory_origin":"wrong-audit-binding-test","rows":[{
            "candidate_id":"SHADOW-P01-C01","disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":audit["required_unit"],
            "asset_audit":"A deliberately wrong receipt binding for the unit test.","primary_refs":["arXiv:2608.00001"],
            "support_audit_artifact":"generated/zetta-timescale-support-audit-20260819.json","support_audit_sha256":digest,
            "reopen_only_if":audit["reopen_only_if"],
        }],"scientific_authority":False}
        with self.assertRaisesRegex(ValueError,"candidate identity mismatch"):
            compile_problem_falsifier_preflight(self.machine(),inventory,run_id="shadow-rx")

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

    def test_release_change_only_hold_routes_to_watch_without_problem_authority(self) -> None:
        project_root=Path(__file__).resolve().parents[1]
        audit_path=project_root/"generated"/"zetta-timescale-support-audit-20260819.json"
        audit=json.loads(audit_path.read_text(encoding="utf-8"))
        audit_sha=hashlib.sha256(audit_path.read_bytes()).hexdigest()
        queue=self.pre_f0();row=queue["rows"][0]
        row.update({
            "candidate_id":"PORT-003",
            "title":"Timescale-isolated ablation",
            "primary_refs":["arXiv:2608.09096","arXiv:2608.16590"],
        })
        inventory={"inventory_origin":"unit-test-zetta-schema-audit","rows":[{
            "candidate_id":"PORT-003",
            **self.identity_fields(row),
            "disposition":"HOLD_SUPPORT_UNAVAILABLE",
            "required_unit":audit["required_unit"],
            "asset_audit":"The released Zetta schema couples Critic and Recovery and blocks the required intermediate arms.",
            "primary_refs":["arXiv:2608.09096","arXiv:2608.16590"],
            "support_audit_artifact":"generated/zetta-timescale-support-audit-20260819.json",
            "support_audit_sha256":audit_sha,
            "release_watch_targets":[{
                "source_ref":"arXiv:2608.16590",
                "url":"https://github.com/air-embodied-brain/Zetta-Embodiment",
                "declaration_kind":"FIRST_PARTY_REPOSITORY",
                "baseline_revision":"6129934d53ea00ac306c14723874321dc3667246",
                "scientific_authority":False,
            }],
            "bounded_first_party_evidence_design_allowed":False,
            "reopen_only_if":audit["reopen_only_if"],
        }],"scientific_authority":False}
        state=compile_pre_f0_problem_falsifier_preflight(queue,inventory,run_id="pre-f0-r1",inventory_sha256="a"*64)
        compiled=state["rows"][0]
        self.assertEqual(compiled["next_route"],"WAIT_FIRST_PARTY_RELEASE_CHANGE")
        self.assertEqual(compiled["support_recheck_mode"],"FIRST_PARTY_RELEASE_CHANGE_ONLY")
        self.assertFalse(compiled["bounded_first_party_evidence_design_allowed"])
        self.assertEqual(compiled["release_watch_targets"][0]["baseline_revision"],"6129934d53ea00ac306c14723874321dc3667246")
        self.assertEqual(state["summary"]["support_qualified"],0)
        self.assertEqual(state["summary"]["problem_gate_authorized"],0)
        self.assertTrue(all(value is False for value in state["authority"].values()))

        bad=json.loads(json.dumps(inventory))
        bad["rows"][0]["release_watch_targets"][0]["url"]="https://github.com/example/not-zetta"
        with self.assertRaisesRegex(ValueError,"does not match audited official repo"):
            compile_pre_f0_problem_falsifier_preflight(queue,bad,run_id="pre-f0-r1")

        bad_revision=json.loads(json.dumps(inventory))
        bad_revision["rows"][0]["release_watch_targets"][0]["baseline_revision"]="0"*40
        with self.assertRaisesRegex(ValueError,"does not match audited repo revision"):
            compile_pre_f0_problem_falsifier_preflight(queue,bad_revision,run_id="pre-f0-r1")


if __name__=="__main__":
    unittest.main()
