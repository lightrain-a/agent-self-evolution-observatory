from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_program_state import (
    CLOSED_CANDIDATES,
    build_agent_safety_program_state,
    validate_agent_safety_program_state,
    write_agent_safety_program_state,
)
from .paper_first_agent_safety_r9_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    R9_FORMAL_HF_RECEIPT_CLASS,
    R9_FORMAL_RUNTIME_ASSET_GATE_CLASS,
    R9_NON_AUTHORITATIVE_CACHE_RECEIPT_CLASS,
)


class AgentSafetyProgramStateTest(unittest.TestCase):
    def fixture_r9(self, root: Path) -> tuple[Path, Path, Path]:
        r9 = root / "shadow-agent-safety-20260818-r9"
        r9.mkdir()
        candidate_body = {
            "irreducible_object": "future first-violation hazard among currently safe matched persistent states",
            "endpoint_headroom_requirement": "current safety ASR must leave enough event headroom",
        }
        (r9 / "formulate-p1.json").write_text(
            json.dumps({"reduction_pending": [{
                "candidate_id": CANDIDATE_ID,
                "candidate": candidate_body,
                "exact_prediction": "matched histories have different survival curves",
                "strongest_same_information_baseline": "current-state distribution-shift hazard predictor",
                "cheapest_problem_falsifier": "branch matched safe states under frozen benign future updates",
            }]}), encoding="utf-8"
        )
        entry = {
            "candidate_id": CANDIDATE_ID,
            "status": "NEEDS_MINIMAL_HARNESS_IMPLEMENTATION",
            "contract_sha256": CONTRACT_SHA256,
            "frozen_exact_prediction": "matched histories have different survival curves",
            "frozen_same_information_baseline": "current-state distribution-shift hazard predictor",
            "frozen_falsifier_expression": "branch matched safe states under frozen benign future updates",
            "frozen_endpoint_headroom_requirement": "ASR < 0.3 before branching",
            "execution_authorized": False,
            "design": {
                "source_specificity": "REPRODUCIBLE_FIRST_PARTY",
                "acquisition_mode": "FIRST_PARTY_REPLAY",
                "same_information_lock": "candidate and baseline share current observables",
            },
            "design_provenance": {"resolved_model": "kimi-k3"},
            "evidence_review": {"verdict": "CLEAR_FOR_SUBSTRATE_PREFLIGHT", "reviewer_model": "deepseek-v4-pro-260425"},
            "substrate_preflight": {
                "disposition": "MINIMAL_HARNESS_IMPLEMENTATION_READY",
                "reason": "official source primitives exist; only glue is missing",
                "inventory_summary": "AWM persistence + BrowserART probes are available",
            },
            "authority": {
                "scientific_claim": False,
                "live_problem_gate": False,
                "paper_design": False,
                "method": False,
                "experiment": False,
                "p0": False,
                "gpu": False,
                "bounded_harness_implementation": True,
            },
        }
        (r9 / "evidence-acquisition-plan.json").write_text(json.dumps({"status": "EVIDENCE_HARNESS_IMPLEMENTATION_PENDING", "entries": [entry]}), encoding="utf-8")
        (r9 / "evidence-review-p1.json").write_text(json.dumps({"reviews": [{"candidate_id": CANDIDATE_ID, "verdict": "CLEAR_FOR_SUBSTRATE_PREFLIGHT", "reviewer_model": "deepseek-v4-pro-260425"}]}), encoding="utf-8")
        (r9 / "evidence-substrate-preflight.json").write_text(json.dumps({"rows": [{"candidate_id": CANDIDATE_ID, "disposition": "MINIMAL_HARNESS_IMPLEMENTATION_READY"}]}), encoding="utf-8")
        primary = {"records": [
            {"ref": "arXiv:2604.16968", "title": "On Safety Risks in Experience-Driven Self-Evolving Agents", "primary_url": "https://arxiv.org/abs/2604.16968", "empirical_facts": [{"text": "benign experience increases safety risk"}]},
            {"ref": "arXiv:2608.12851", "title": "Practice Makes Unsafe", "primary_url": "https://arxiv.org/abs/2608.12851", "empirical_facts": [{"text": "skill lifecycle separates authoring retrieval and execution"}]},
            {"ref": "arXiv:2608.01759", "title": "Benign Alone, Harmful Together", "primary_url": "https://arxiv.org/abs/2608.01759", "empirical_facts": [{"text": "benign experiences can compose into harm"}]},
            {"ref": "arXiv:2608.05563", "title": "When Experience Becomes Instruction", "primary_url": "https://arxiv.org/abs/2608.05563", "empirical_facts": [{"text": "trajectory evidence can be promoted into persistent instruction"}]},
        ]}
        (r9 / "frozen-primary-evidence-pool.json").write_text(json.dumps(primary), encoding="utf-8")
        blocked = [{
            "source_candidate_id": cid,
            "title": f"closed {cid}",
            "memory_class": "PRINCIPLE_DEAD_END",
            "reason": f"same-information reduction closes {cid}",
            "reopen_only_if": f"new matched evidence reopens {cid}",
        } for cid in CLOSED_CANDIDATES]
        (r9 / "shadow-dead-end-memory.json").write_text(json.dumps({"blocked_objects": blocked}), encoding="utf-8")
        canonical = root / "canonical-primary.json"
        canonical.write_text(json.dumps({"records": [{"ref": "arXiv:2608.11888", "title": "Agent Skills Can Be Harmful", "primary_url": "https://arxiv.org/abs/2608.11888", "empirical_facts": [{"text": "loaded skills can causally induce implementation faults"}]}]}), encoding="utf-8")
        smoke = root / "smoke.json"
        smoke.write_text(json.dumps({
            "status": "ZERO_PROVIDER_HARNESS_SMOKE_PASS",
            "candidate_id": CANDIDATE_ID,
            "contract_sha256": CONTRACT_SHA256,
            "provider_calls_executed": 0,
            "gpu_calls_executed": 0,
            "execution_authorized": False,
            "branch_initial_state_equal": True,
            "branch_future_schedule_equal": True,
        }), encoding="utf-8")
        return r9, canonical, smoke

    def promote_runtime_ready(self, r9: Path, root: Path) -> tuple[Path, Path]:
        plan_path = r9 / "evidence-acquisition-plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        entry = plan["entries"][0]
        entry["status"] = "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION"
        entry["execution_authorized"] = True
        entry["authority"]["bounded_evidence_acquisition"] = True
        entry["harness_implementation"] = {
            "harness_manifest_sha256": "a" * 64,
            "sandboxed": True,
            "probe_passed": True,
            "budget_feasible": True,
            "scientific_authority": False,
        }
        plan["status"] = "EVIDENCE_EXECUTION_READY"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        harness_manifest = root / "harness-manifest.json"
        harness_manifest.write_text(json.dumps({
            "candidate_id": CANDIDATE_ID,
            "contract_sha256": CONTRACT_SHA256,
            "harness_commit": "fixture-harness",
            "execution_invariants": {
                "probe_split": {"qualification_ids": ["14", "16", "18"], "heldout_ids": ["34", "21", "1", "8", "11", "22", "13", "33"], "qualification_count": 3, "heldout_count": 8, "disjoint": True},
                "budget": {"states": 4, "history_strata": 2, "future_horizon_updates": 3, "total_model_evaluations_upper_bound": 240, "contract_max_model_calls": 256, "reserve": 16},
            },
            "pinned_models": {"agent": {"model_id": "Qwen/Qwen3-8B"}, "evaluator": {"model_id": "cais/HarmBench-Llama-2-13b-cls"}},
            "source_pins": {"awm_commit": "a", "browserart_commit": "b"},
            "policy": {"effective_execution_requires_runtime_gate_ready": True},
        }), encoding="utf-8")
        runtime_gate = root / "runtime-asset-gate.json"
        runtime_gate.write_text(json.dumps({
            "status": "READY_RUNTIME_MODEL_ASSETS_PINNED",
            "candidate_id": CANDIDATE_ID,
            "contract_sha256": CONTRACT_SHA256,
            "execution_authorized": True,
            "scientific_authority": False,
            "formal_gate": {
                "artifact_class": R9_FORMAL_RUNTIME_ASSET_GATE_CLASS,
                "status": "READY_RUNTIME_MODEL_ASSETS_PINNED",
                "execution_authorized": True,
                "fallback_allowed": False,
                "blockers": [],
                "verification_contract": {"accepted_receipt_class": R9_FORMAL_HF_RECEIPT_CLASS},
                "model_assets": [
                    {"role": "agent", "hf_exact_revision_verified": True, "receipt_class": R9_FORMAL_HF_RECEIPT_CLASS},
                    {"role": "evaluator", "hf_exact_revision_verified": True, "receipt_class": R9_FORMAL_HF_RECEIPT_CLASS},
                ],
            },
        }), encoding="utf-8")
        return harness_manifest, runtime_gate

    def test_public_projection_keeps_science_and_execution_locked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            r9, canonical, smoke = self.fixture_r9(Path(td))
            state = build_agent_safety_program_state(r9_root=r9, canonical_primary_state_path=canonical, harness_smoke_path=smoke)
            self.assertEqual(validate_agent_safety_program_state(state), [])
            self.assertEqual(state["candidate_stage"], "NEEDS_MINIMAL_HARNESS_IMPLEMENTATION")
            self.assertEqual(state["substrate"]["harness_smoke_status"], "ZERO_PROVIDER_HARNESS_SMOKE_PASS")
            self.assertEqual(len(state["survey"]), 5)
            self.assertEqual({row["candidate_id"] for row in state["closed_basins"]}, set(CLOSED_CANDIDATES))
            self.assertFalse(state["execution_authorized"])
            self.assertFalse(state["authority"]["bounded_evidence_acquisition"])
            self.assertTrue(state["next_gate"]["required"])

    def test_survey_supplement_restores_related_work_without_primary_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            canonical_payload = json.loads(canonical.read_text(encoding="utf-8"))
            canonical_payload["records"] = [row for row in canonical_payload.get("records", []) if row.get("ref") != "arXiv:2608.11888"]
            canonical.write_text(json.dumps(canonical_payload), encoding="utf-8")
            supplement = root / "survey-supplement.json"
            supplement.write_text(json.dumps({
                "scope": "RELATED_PRIMARY_LITERATURE_SURVEY_ONLY",
                "scientific_authority": False,
                "primary_transaction_authority": False,
                "records": [{
                    "ref": "arXiv:2608.11888",
                    "title": "Agent Skills Can Be Harmful",
                    "primary_url": "https://arxiv.org/abs/2608.11888",
                    "source_scope": "OFFICIAL_ARXIV_RELATED_WORK",
                    "empirical_facts": [{"text": "307 skill-induced failures"}],
                    "scientific_authority": False,
                    "primary_transaction_authority": False,
                }],
            }), encoding="utf-8")
            state = build_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                survey_supplement_path=supplement,
                harness_smoke_path=smoke,
            )
            self.assertEqual(validate_agent_safety_program_state(state), [])
            row = next(item for item in state["survey"] if item["ref"] == "arXiv:2608.11888")
            self.assertEqual(row["source_scope"], "OFFICIAL_ARXIV_RELATED_WORK")
            self.assertFalse(state["execution_authorized"])
            self.assertFalse(state["scientific_authority"])

    def test_survey_supplement_cannot_carry_primary_or_scientific_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            supplement = root / "bad-survey-supplement.json"
            supplement.write_text(json.dumps({
                "scope": "RELATED_PRIMARY_LITERATURE_SURVEY_ONLY",
                "scientific_authority": False,
                "primary_transaction_authority": True,
                "records": [],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "survey-only and zero-authority"):
                build_agent_safety_program_state(
                    r9_root=r9,
                    canonical_primary_state_path=canonical,
                    survey_supplement_path=supplement,
                    harness_smoke_path=smoke,
                )

    def test_writer_emits_json_and_js_from_same_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            json_path = root / "state.json"
            js_path = root / "state.js"
            state = write_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                harness_smoke_path=smoke,
                json_path=json_path,
                js_path=js_path,
            )
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["contract_sha256"], state["contract_sha256"])
            self.assertTrue(js_path.read_text(encoding="utf-8").startswith("window.AGENT_SAFETY_PROGRAM_STATE = "))

    def test_malformed_positive_execution_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            plan = json.loads((r9 / "evidence-acquisition-plan.json").read_text(encoding="utf-8"))
            plan["entries"][0]["execution_authorized"] = True
            (r9 / "evidence-acquisition-plan.json").write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed bounded evidence authority"):
                build_agent_safety_program_state(r9_root=r9, canonical_primary_state_path=canonical, harness_smoke_path=smoke)

    def test_runtime_asset_pass_allows_only_qualification_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            state = build_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                harness_smoke_path=smoke,
                harness_manifest_path=harness_manifest,
                runtime_asset_gate_path=runtime_gate,
            )
            self.assertEqual(validate_agent_safety_program_state(state), [])
            self.assertEqual(state["candidate_stage"], "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION")
            self.assertTrue(state["execution_authorized"])
            self.assertTrue(state["authority"]["bounded_evidence_acquisition"])
            self.assertTrue(state["authority"]["qualification_probe_execution"])
            self.assertFalse(state["authority"]["heldout_future_probe_execution"])
            self.assertFalse(state["authority"]["paper_design"])
            self.assertFalse(state["authority"]["p0"])
            self.assertEqual(state["runtime"]["status"], "READY_RUNTIME_MODEL_ASSETS_PINNED")
            self.assertEqual(state["canonical_protocol"]["execution_invariants"]["budget"]["history_strata"], 2)
            self.assertEqual(state["canonical_protocol"]["execution_invariants"]["budget"]["total_model_evaluations_upper_bound"], 240)
            self.assertEqual(state["next_gate"]["name"], "CURRENT_SAFETY_QUALIFICATION_GATE")

    def test_public_validator_rejects_ready_without_formal_receipt_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            state = build_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                harness_smoke_path=smoke,
                harness_manifest_path=harness_manifest,
                runtime_asset_gate_path=runtime_gate,
            )
            state["runtime"]["artifact_class"] = ""
            self.assertIn(
                "agent-safety public runtime READY lacks formal HF receipt authority",
                validate_agent_safety_program_state(state),
            )

    def test_nonformal_ready_receipt_cannot_authorize_public_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            gate = json.loads(runtime_gate.read_text(encoding="utf-8"))
            gate["formal_gate"]["model_assets"][0]["receipt_class"] = R9_NON_AUTHORITATIVE_CACHE_RECEIPT_CLASS
            runtime_gate.write_text(json.dumps(gate), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed positive execution authority"):
                build_agent_safety_program_state(
                    r9_root=r9,
                    canonical_primary_state_path=canonical,
                    harness_smoke_path=smoke,
                    harness_manifest_path=harness_manifest,
                    runtime_asset_gate_path=runtime_gate,
                )

    def test_cache_content_readjudication_is_explicitly_non_authoritative(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            gate = json.loads(runtime_gate.read_text(encoding="utf-8"))
            gate["status"] = "HOLD_RUNTIME_MODEL_ASSETS_UNAVAILABLE_OR_UNPINNED"
            gate["execution_authorized"] = False
            gate["formal_gate"]["status"] = gate["status"]
            gate["formal_gate"]["execution_authorized"] = False
            gate["formal_gate"]["blockers"] = ["official-hf-metadata-unavailable"]
            runtime_gate.write_text(json.dumps(gate), encoding="utf-8")
            readjudication = root / "cache-check.json"
            readjudication.write_text(json.dumps({
                "candidate_id": CANDIDATE_ID,
                "contract_sha256": CONTRACT_SHA256,
                "status": R9_NON_AUTHORITATIVE_CACHE_RECEIPT_CLASS,
                "receipt_class": R9_NON_AUTHORITATIVE_CACHE_RECEIPT_CLASS,
                "formal_gate_eligible": False,
                "execution_authorized": False,
                "scientific_authority": False,
            }), encoding="utf-8")
            state = build_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                harness_smoke_path=smoke,
                harness_manifest_path=harness_manifest,
                runtime_asset_gate_path=runtime_gate,
                provenance_readjudication_path=readjudication,
            )
            self.assertFalse(state["execution_authorized"])
            self.assertEqual(state["runtime"]["official_metadata_connectivity"], "HOLD")
            self.assertEqual(state["runtime"]["provenance_receipt_class"], R9_NON_AUTHORITATIVE_CACHE_RECEIPT_CLASS)
            self.assertEqual(state["canonical_protocol"]["execution_invariants"]["budget"]["history_strata"], 2)

    def test_runtime_asset_hold_overrides_generic_plan_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            gate = json.loads(runtime_gate.read_text(encoding="utf-8"))
            gate["status"] = "HOLD_RUNTIME_MODEL_ASSETS_UNAVAILABLE_OR_UNPINNED"
            gate["execution_authorized"] = False
            gate["formal_gate"]["status"] = gate["status"]
            gate["formal_gate"]["execution_authorized"] = False
            gate["formal_gate"]["blockers"] = ["agent-verification-receipt-missing"]
            runtime_gate.write_text(json.dumps(gate), encoding="utf-8")
            state = build_agent_safety_program_state(
                r9_root=r9,
                canonical_primary_state_path=canonical,
                harness_smoke_path=smoke,
                harness_manifest_path=harness_manifest,
                runtime_asset_gate_path=runtime_gate,
            )
            self.assertEqual(validate_agent_safety_program_state(state), [])
            self.assertFalse(state["execution_authorized"])
            self.assertEqual(state["current_stage"], "RUNTIME_MODEL_ASSET_HOLD")
            self.assertEqual(state["candidate_stage"], "HOLD_RUNTIME_MODEL_ASSETS_UNAVAILABLE_OR_UNPINNED")
            self.assertEqual(state["generic_candidate_stage"], "READY_FOR_BOUNDED_EVIDENCE_ACQUISITION")
            self.assertEqual(state["next_gate"]["name"], "RUNTIME_MODEL_ASSET_PROVENANCE_GATE")

    def test_downstream_authority_is_rejected_even_after_runtime_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r9, canonical, smoke = self.fixture_r9(root)
            harness_manifest, runtime_gate = self.promote_runtime_ready(r9, root)
            plan = json.loads((r9 / "evidence-acquisition-plan.json").read_text(encoding="utf-8"))
            plan["entries"][0]["authority"]["method"] = True
            (r9 / "evidence-acquisition-plan.json").write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unauthorized downstream science"):
                build_agent_safety_program_state(
                    r9_root=r9,
                    canonical_primary_state_path=canonical,
                    harness_smoke_path=smoke,
                    harness_manifest_path=harness_manifest,
                    runtime_asset_gate_path=runtime_gate,
                )


if __name__ == "__main__":
    unittest.main()
