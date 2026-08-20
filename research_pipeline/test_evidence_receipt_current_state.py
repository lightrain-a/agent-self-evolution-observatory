from __future__ import annotations

import copy
import unittest

from .evidence_receipt_current_state import (
    CANONICAL_FAILURE_LAYERS,
    compile_evidence_receipt_projection,
    validate_evidence_receipt_projection,
)


class EvidenceReceiptCurrentStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = {
            "status": "ADJUDICATED",
            "identity": {"candidate_id": "SYNTHETIC-CANDIDATE"},
            "paper_evidence_ready": True,
            "additional_behavior_execution_authorized": False,
            "claim_scope": {
                "supported": "A bounded synthetic observation is supported.",
                "not_supported": ["No population claim is supported."],
            },
            "measurements": {"trials": 4, "events": 1},
            "failure_classification": {
                layer: [] for layer in CANONICAL_FAILURE_LAYERS
            },
        }
        self.spec = {
            "projection_id": "SYNTHETIC-RECEIPT-PROJECTION",
            "program_id": "SYNTHETIC-PROGRAM",
            "candidate_id": "SYNTHETIC-CANDIDATE",
            "receipt_status": "ADJUDICATED",
            "current_stage": "PAPER_EVIDENCE_READY",
            "candidate_stage": "SUPPORTED_BOUNDEDLY",
            "receipt_candidate_path": "identity.candidate_id",
            "paper_evidence_ready_path": "paper_evidence_ready",
            "required_flags": {
                "paper_evidence_ready": True,
                "additional_behavior_execution_authorized": False,
            },
            "failure_layers_path": "failure_classification",
            "claim_scope": {
                "supported_path": "claim_scope.supported",
                "not_supported_path": "claim_scope.not_supported",
                "expected_not_supported_count": 1,
                "limitation": "Synthetic scope only.",
            },
            "evidence_blocks": {
                "observations": {
                    "trials": {"path": "measurements.trials", "type": "int"},
                    "events": {"path": "measurements.events", "type": "int"},
                }
            },
            "authority_denials": [
                "scientific_claim",
                "method",
                "experiment",
                "p0",
                "gpu",
            ],
        }
        self.reopen = {
            "condition_id": "SYNTHETIC-REOPEN",
            "condition": "Collect a pre-registered independent control.",
            "automatic_reopen": False,
            "new_behavior_execution_authorized": False,
            "scientific_authority": False,
        }

    def compile(self):
        return compile_evidence_receipt_projection(
            self.receipt,
            spec=self.spec,
            receipt_ref="repo://generated/synthetic.json#sha256=abc",
            dependency_refs={"claim_table": "sha256:def"},
            reopen_condition=self.reopen,
            generated_at="2026-08-20T00:00:00+00:00",
        )

    def test_compiles_non_agent_safety_receipt_without_domain_code(self) -> None:
        projection = self.compile()
        self.assertEqual(projection["evidence_blocks"]["observations"], {"trials": 4, "events": 1})
        self.assertEqual(projection["claim_boundary"]["supported_claim"], self.receipt["claim_scope"]["supported"])
        self.assertFalse(projection["execution_authorized"])
        self.assertFalse(any(projection["authority"].values()))
        self.assertEqual(validate_evidence_receipt_projection(projection, spec=self.spec), [])

    def test_compilation_is_deterministic(self) -> None:
        self.assertEqual(self.compile(), self.compile())

    def test_authoritative_reopen_is_rejected(self) -> None:
        reopen = dict(self.reopen, automatic_reopen=True)
        with self.assertRaisesRegex(ValueError, "fail-closed"):
            compile_evidence_receipt_projection(
                self.receipt,
                spec=self.spec,
                receipt_ref="repo://generated/synthetic.json#sha256=abc",
                dependency_refs={},
                reopen_condition=reopen,
                generated_at="2026-08-20T00:00:00+00:00",
            )

    def test_failure_layer_order_drift_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["failure_classification"] = {
            layer: [] for layer in reversed(CANONICAL_FAILURE_LAYERS)
        }
        with self.assertRaisesRegex(ValueError, "canonical six failure layers"):
            compile_evidence_receipt_projection(
                receipt,
                spec=self.spec,
                receipt_ref="repo://generated/synthetic.json#sha256=abc",
                dependency_refs={},
                reopen_condition=self.reopen,
                generated_at="2026-08-20T00:00:00+00:00",
            )

    def test_payload_mutation_is_detected(self) -> None:
        projection = self.compile()
        projection["evidence_blocks"]["observations"]["events"] = 2
        self.assertIn(
            "generic receipt projection payload hash drift",
            validate_evidence_receipt_projection(projection, spec=self.spec),
        )


if __name__ == "__main__":
    unittest.main()
