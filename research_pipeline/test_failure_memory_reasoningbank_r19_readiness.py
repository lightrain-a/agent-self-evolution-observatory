from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_r19_readiness import build_readiness


class TestR19Readiness(unittest.TestCase):
    def _docs(self):
        r18c={
            "scientific_verdict":"NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE",
            "frozen_policy_application":{"single_confirmatory_attempt_consumed":True},
        }
        candidate={
            "capacity":{"R19_independent_template_units":35},
        }
        evaluator={
            "summary":{"native_evaluators_constructed":35,"native_evaluators_called":0},
        }
        alias={
            "ollama_registry":{"all_required_aliases_manifest_identical":True},
            "tokenizer":{"all_lookup_pass":True},
        }
        contract={
            "execution_gate":{"execution_permitted":False},
        }
        public_status={
            "claim_boundary":{"O5_disposition":"REQUIRES_SCIENTIFIC_REOPEN"},
        }
        return r18c,candidate,evaluator,alias,contract,public_status

    def test_ready_for_authority_not_execution(self):
        docs=self._docs()
        r=build_readiness(*docs,{"x_sha256":"a"*64})
        self.assertTrue(r["readiness"]["engineering_contract_ready"])
        self.assertTrue(r["readiness"]["scientific_object_ready_for_explicit_authority_decision"])
        self.assertFalse(r["readiness"]["execution_ready_now"])
        self.assertFalse(r["authority"]["scientific"])
        self.assertTrue(r["authority_semantics"]["generic_continuation_language_is_not_treated_as_new_R19_scientific_authority"])

    def test_executable_contract_fails_closed(self):
        docs=list(self._docs())
        docs[4]={"execution_gate":{"execution_permitted":True}}
        with self.assertRaises(RuntimeError):
            build_readiness(*docs,{"x_sha256":"a"*64})

    def test_wrong_o5_disposition_fails_closed(self):
        docs=list(self._docs())
        docs[5]={"claim_boundary":{"O5_disposition":"RESOLVED"}}
        with self.assertRaises(RuntimeError):
            build_readiness(*docs,{"x_sha256":"a"*64})


if __name__ == "__main__":
    unittest.main()
