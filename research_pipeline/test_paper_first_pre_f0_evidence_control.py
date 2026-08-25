from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .candidate_identity import attach_candidate_identity
from .config import StorageSettings
from .paper_first_pre_f0_evidence_control import control_snapshot, design, harness_implementation, prepare, primary_asset_release, recompile_operationalization, review, substrate_preflight, validate_public_state


def storage(root:Path)->StorageSettings:
    return StorageSettings(data_root=root,corpus_dir=root/"corpora",dataset_dir=root/"datasets",paper_dir=root/"papers",index_dir=root/"indexes",run_dir=root/"runs",cache_dir=root/"cache",lock_dir=root/"locks",site_artifact_dir=root/"site")


def inputs(root:Path)->tuple[Path,Path,Path,Path,Path]:
    queue_path=root/"queue.json";support_path=root/"support.json";plan_path=root/"plan.json";public_json=root/"public.json";public_js=root/"public.js"
    row=attach_candidate_identity({"candidate_id":"PORT-013","title":"syntactic binding","discovery_lane":"CONVERGENT_FAILURE","source_branch_id":"B1","primary_refs":["arXiv:2608.17684","arXiv:2607.26809"],"irreducible_object":"procedural memory binds literal action envelopes instead of semantic intent","paperability_axes":{"E":{"status":"SUPPORTED"}},"surviving_paperability_axes":["E"],"non_principle_surviving_axes":["E"],"route_reason":"EXACT_REDUCTION_PENDING","reduction_blockers":["unresolved-exact-reduction-test:1"],"exact_prediction":"varied envelopes transfer better","strongest_same_information_baseline":"domain adaptation","cheapest_problem_falsifier":"compare varied versus single envelope acquisition","endpoint_headroom_requirement":"nondegenerate transfer gap","next_if_positive":"RERUN_EXACT_SAME_INFORMATION_REDUCTION","scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}})
    queue={"schema_version":"1.0","source_generator_run_id":"g1","source_generator_status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","status":"PRE_F0_QUEUE_READY","policy":{},"summary":{"queued":1},"rows":[row],"scientific_authority":False,"authority":{"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    support_row={"candidate_id":"PORT-013","candidate_identity_version":row["candidate_identity_version"],"candidate_snapshot_sha256":row["candidate_snapshot_sha256"],"disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"matched native function-call units","asset_audit":"author artifacts not released","primary_refs":row["primary_refs"],"bounded_first_party_evidence_design_allowed":True,"reopen_only_if":"first-party matched units exist","scientific_authority":False}
    support={"schema_version":"1.0-pre-f0","status":"PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE","support_inventory_sha256":"a"*64,"summary":{"queued":1,"support_qualified":0,"hold_support_unavailable":1,"falsifier_executed":0},"rows":[support_row],"scientific_authority":False,"authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
    queue_path.write_text(json.dumps(queue),encoding="utf-8");support_path.write_text(json.dumps(support),encoding="utf-8")
    return queue_path,support_path,plan_path,public_json,public_js


def design_payload(candidate_id:str)->dict:
    return {"designs":[{"candidate_id":candidate_id,"changed_variable":"","source_specificity":"SOURCE_SPECIFIC_REQUIRED","acquisition_mode":"PRIMARY_ASSET_REUSE","reproduction_target":"reproduce the envelope mismatch boundary on the frozen author units","independent_truth":"author task truth and execution trace truth frozen independently of the candidate","causal_unit":"matched skill acquisition and held-out execution unit","observable":"native function-call transfer utility","intervention":"vary only the acquisition envelope while preserving semantic skill content","same_information_lock":"all arms use the same semantic content, tasks, executor observations, and budget","matched_baseline_execution":"run domain adaptation on the exact same units and information","anti_bake_in_controls":[],"decision_criteria":{"baseline_reduction_supported":"matched domain adaptation explains the transfer difference","candidate_residual_survives":"envelope variation retains a distinguishing transfer residual after the baseline","inconclusive":"qualified units do not separate baseline and residual"},"single_variable_repair_if_inconclusive":"increase paired repeats only","execution_adapter":"PRIMARY_ASSET_ONLY","budget":{"max_units":24,"max_wall_minutes":30,"max_gpu_hours":0.0,"max_model_calls":0}}]}


class CanonicalPreF0EvidenceControlTest(unittest.TestCase):
    def test_prepare_binds_queue_support_plan_and_candidate_snapshot(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root)
            state=prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1)
            self.assertEqual(state["status"],"EVIDENCE_DESIGN_PENDING")
            self.assertEqual(validate_public_state(state),[])
            self.assertEqual(len(state["candidate_snapshot_sha256s"]),1)
            before=state["control_snapshot_sha256"]
            payload=json.loads(queue.read_text());payload["rows"][0]["title"]="mutated scientific identity";queue.write_text(json.dumps(payload),encoding="utf-8")
            with self.assertRaises((ValueError,Exception)):
                control_snapshot(queue_path=queue,support_path=support,plan_path=plan)
            self.assertTrue(before)

    def test_design_calls_provider_once_then_moves_to_operationalization_recompile(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root);prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1);calls=[]
            def provider(**kwargs):
                calls.append(kwargs);return {"text":json.dumps(design_payload("PORT-013")),"resolved_model":"kimi-k3","transport_attempts":[]}
            memory={"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"b"*64,"query_pack_sha256":"c"*64,"selected_memory_ids":[],"summary":{"selected":0},"text":"","scientific_authority":False}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",side_effect=provider),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                out=design(storage=storage(root/"private"),queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            compiled=json.loads(plan.read_text())
            self.assertEqual(len(calls),1)
            self.assertEqual(compiled["status"],"EVIDENCE_OPERATIONALIZATION_RECOMPILE_PENDING")
            self.assertEqual(compiled["entries"][0]["status"],"NEEDS_OPERATIONALIZATION_RECOMPILE")
            self.assertFalse(compiled["entries"][0]["execution_authorized"])
            self.assertEqual(out["last_stage"]["resolved_model"],"kimi-k3")
            self.assertEqual(out["last_stage"]["provider_calls_executed"],1)
            self.assertEqual(validate_public_state(out),[])
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt") as again:
                with self.assertRaisesRegex(ValueError,"no pending design"):
                    design(storage=storage(root/"private"),queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
                again.assert_not_called()

    def test_review_uses_independent_model_and_source_specific_verdict_waits_after_first_party_design(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root);prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1);private=storage(root/"private")
            first_party=design_payload("PORT-013");d=first_party["designs"][0];d.update({"source_specificity":"REPRODUCIBLE_FIRST_PARTY","acquisition_mode":"FIRST_PARTY_SANDBOX","anti_bake_in_controls":["external truth","frozen units","candidate cannot generate outcomes"]})
            def first(**kwargs):return {"text":json.dumps(first_party),"resolved_model":"kimi-k3","transport_attempts":[]}
            memory={"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"b"*64,"query_pack_sha256":"c"*64,"selected_memory_ids":[],"summary":{"selected":0},"text":"","scientific_authority":False}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",side_effect=first),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                design(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            self.assertEqual(json.loads(plan.read_text())["status"],"EVIDENCE_REVIEW_PENDING")
            calls=[]
            def reviewer(**kwargs):
                calls.append(kwargs);return {"text":json.dumps({"reviews":[{"candidate_id":"PORT-013","verdict":"SOURCE_SPECIFIC_REQUIRED","checks":{},"reason":"the frozen contrast intrinsically requires the original source units","required_revision":""}]}),"resolved_model":"deepseek-v4-pro","transport_attempts":[]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",side_effect=reviewer):
                out=review(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js)
            compiled=json.loads(plan.read_text());self.assertEqual(len(calls),1);self.assertEqual(calls[0]["requested_model"],"deepseek-v4-pro");self.assertEqual(compiled["entries"][0]["status"],"NEEDS_OPERATIONALIZATION_RECOMPILE");self.assertEqual(out["last_stage"]["resolved_model"],"deepseek-v4-pro")

    def test_single_operationalization_recompile_can_close_to_primary_asset_wait(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root);prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1);private=storage(root/"private")
            memory={"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"b"*64,"query_pack_sha256":"c"*64,"selected_memory_ids":[],"summary":{"selected":0},"text":"","scientific_authority":False}
            def first(**kwargs):return {"text":json.dumps(design_payload("PORT-013")),"resolved_model":"kimi-k3","transport_attempts":[]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",side_effect=first),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                design(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            calls=[]
            def second(**kwargs):
                calls.append(kwargs);return {"text":json.dumps({"recompiles":[{"candidate_id":"PORT-013","verdict":"INTRINSIC_SOURCE_SPECIFIC","reason":"The frozen prediction explicitly requires skills acquired in the named AWM/WebArena envelope process and native function-calling transfer units; replacing those units would change the measured scientific object."}]}),"resolved_model":"kimi-k3","transport_attempts":[]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",side_effect=second),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                out=recompile_operationalization(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            compiled=json.loads(plan.read_text());self.assertEqual(len(calls),1);self.assertEqual(compiled["status"],"EVIDENCE_WAIT_OR_HOLD");self.assertEqual(compiled["entries"][0]["status"],"WAIT_PRIMARY_ASSET_RELEASE");self.assertEqual(compiled["summary"]["wait_primary_asset"],1);self.assertFalse(compiled["entries"][0]["execution_authorized"]);self.assertEqual(out["last_stage"]["provider_calls_executed"],1);self.assertEqual(validate_public_state(out),[])
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt") as again:
                with self.assertRaisesRegex(ValueError,"no operationalization recompile pending"):
                    recompile_operationalization(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
                again.assert_not_called()


    def test_primary_asset_release_reopens_only_design_review_without_provider_or_execution_authority(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root);prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1);private=storage(root/"private")
            first_party=design_payload("PORT-013");d=first_party["designs"][0];d.update({"source_specificity":"REPRODUCIBLE_FIRST_PARTY","acquisition_mode":"FIRST_PARTY_SANDBOX","anti_bake_in_controls":["external truth","frozen units","candidate cannot generate outcomes"]})
            memory={"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"b"*64,"query_pack_sha256":"c"*64,"selected_memory_ids":[],"summary":{"selected":0},"text":"","scientific_authority":False}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",return_value={"text":json.dumps(first_party),"resolved_model":"kimi-k3","transport_attempts":[]}),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                design(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            checks={"independent_truth_valid":False,"scientific_object_preserved":False,"no_mechanism_bake_in":False,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":False,"operationalization_equivalence_valid":False}
            blocked={"reviews":[{"candidate_id":"PORT-013","verdict":"BLOCK_BAKE_IN","checks":checks,"reason":"synthetic treatment label replaces the missing primary asset","required_revision":""}]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",return_value={"text":json.dumps(blocked),"resolved_model":"deepseek-v4-pro","transport_attempts":[]}):
                review(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="deepseek-v4-pro")
            held=json.loads(plan.read_text());row=held["entries"][0]
            self.assertEqual(held["status"],"EVIDENCE_WAIT_OR_HOLD");self.assertEqual(row["status"],"HOLD_EVIDENCE_REVIEW_BLOCKED")
            receipt={"receipts":[{"candidate_id":"PORT-013","candidate_snapshot_sha256":row["candidate_snapshot_sha256"],"blocked_contract_sha256":row["contract_sha256"],"release_kind":"FIRST_PARTY_PRIMARY_ASSET_DELTA","authoritative_source":"https://huggingface.co/datasets/example/primary","authoritative_revision":"1"*40,"materialized_asset_kind":"released query JSON metadata","materialized_unit_count":254,"asset_manifest_sha256":"2"*64,"schema_fields":["query_type","verifier_type","verification_criteria"],"newly_independent_variables":["query_type"],"remaining_missing_requirements":["per-case target-model outcome"],"materialization_verified":True,"synthetic_substitute":False,"transport_source":"https://mirror.example/primary@revision","transport_is_authority":False,"scientific_authority":False,"execution_authority":False,"reopen_scope":"DESIGN_REVIEW_ONLY"}]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt") as provider:
                out=primary_asset_release(receipt_payload=receipt,storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js);provider.assert_not_called()
            reopened=json.loads(plan.read_text());row=reopened["entries"][0]
            self.assertEqual(reopened["status"],"EVIDENCE_DESIGN_PENDING");self.assertEqual(row["status"],"NEEDS_BOUNDED_EVIDENCE_DESIGN")
            self.assertFalse(row["execution_authorized"]);self.assertEqual(row["primary_asset_release_receipt"]["reopen_scope"],"DESIGN_REVIEW_ONLY")
            self.assertEqual(row["primary_asset_release_receipt"]["remaining_missing_requirements"],["per-case target-model outcome"])
            self.assertEqual(out["last_stage"]["stage"],"primary-asset-release");self.assertEqual(out["last_stage"]["provider_calls_executed"],0);self.assertEqual(validate_public_state(out),[])


    def test_substrate_preflight_compiles_minimal_harness_without_provider_or_downstream_authority(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);queue,support,plan,pub,js=inputs(root);prepare(queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,max_active=1);private=storage(root/"private")
            first_party=design_payload("PORT-013");d=first_party["designs"][0];d.update({"source_specificity":"REPRODUCIBLE_FIRST_PARTY","acquisition_mode":"FIRST_PARTY_SANDBOX","execution_adapter":"SUBSTRATE_PREFLIGHT_REQUIRED","anti_bake_in_controls":["external truth","frozen units","candidate cannot generate outcomes"]})
            memory={"purpose":"EXPERIMENT_DESIGN","wiki_sha256":"b"*64,"query_pack_sha256":"c"*64,"selected_memory_ids":[],"summary":{"selected":0},"text":"","scientific_authority":False}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",return_value={"text":json.dumps(first_party),"resolved_model":"kimi-k3","transport_attempts":[]}),patch("research_pipeline.paper_first_pre_f0_evidence_control._evidence_memory_pack",return_value=memory):
                design(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="kimi-k3")
            checks={"independent_truth_valid":True,"scientific_object_preserved":True,"no_mechanism_bake_in":True,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":True,"operationalization_equivalence_valid":True}
            review_payload={"reviews":[{"candidate_id":"PORT-013","verdict":"CLEAR_FOR_SUBSTRATE_PREFLIGHT","checks":checks,"reason":"reviewed first-party contract is bounded and independent","required_revision":""}]}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt",return_value={"text":json.dumps(review_payload),"resolved_model":"deepseek-v4-pro","transport_attempts":[]}):
                review(storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js,model="deepseek-v4-pro")
            row=json.loads(plan.read_text())["entries"][0]
            receipt={"schema_version":"1.0","receipts":[{"candidate_id":"PORT-013","contract_sha256":row["contract_sha256"],"disposition":"MINIMAL_HARNESS_IMPLEMENTATION_READY","reason":"official BrowserGym provides independent task truth and native function schemas but the benchmark backend must be materialized in a run-local sandbox","inventory_summary":"BrowserGym core and Playwright are already pinned; MiniWoB backend and fixed MiniWoB++ assets are installable without scientific outcome access","harness_plan_sha256":"d"*64,"implementation_scope":"materialize only the pinned MiniWoB backend, native tool adapter, frozen envelope renderers, truth recorder, and matched baseline plumbing","budget_feasible":True}],"scientific_authority":False}
            with patch("research_pipeline.paper_first_pre_f0_evidence_control._ark_with_provider_receipt") as provider:
                out=substrate_preflight(receipt_payload=receipt,storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js)
                provider.assert_not_called()
            compiled=json.loads(plan.read_text());entry=compiled["entries"][0]
            self.assertEqual(compiled["status"],"EVIDENCE_HARNESS_IMPLEMENTATION_PENDING")
            self.assertEqual(entry["status"],"NEEDS_MINIMAL_HARNESS_IMPLEMENTATION")
            self.assertFalse(entry["execution_authorized"])
            self.assertTrue(entry["authority"]["bounded_harness_implementation"])
            for key in ("scientific_claim","live_problem_gate","paper_design","method","p0","full_experiment"):
                self.assertFalse(entry["authority"][key])
            self.assertEqual(out["last_stage"]["provider_calls_executed"],0)
            self.assertEqual(validate_public_state(out),[])
            impl={"schema_version":"1.0","receipts":[{"candidate_id":"PORT-013","contract_sha256":entry["contract_sha256"],"harness_manifest_sha256":"e"*64,"implementation_summary":"run-local pinned BrowserGym MiniWoB harness passed schema/truth/equivalence smoke without outcome comparison","sandboxed":True,"probe_passed":True,"budget_feasible":True}],"scientific_authority":False}
            ready=harness_implementation(receipt_payload=impl,storage=private,queue_path=queue,support_path=support,plan_path=plan,json_path=pub,js_path=js)
            compiled=json.loads(plan.read_text());entry=compiled["entries"][0]
            self.assertEqual(compiled["status"],"EVIDENCE_EXECUTION_READY")
            self.assertEqual(entry["status"],"READY_FOR_BOUNDED_EVIDENCE_ACQUISITION")
            self.assertTrue(entry["execution_authorized"])
            self.assertTrue(entry["authority"]["bounded_evidence_acquisition"])
            self.assertFalse(entry["authority"]["paper_design"])
            self.assertEqual(ready["last_stage"]["provider_calls_executed"],0)
            self.assertEqual(validate_public_state(ready),[])


if __name__=="__main__":unittest.main()
