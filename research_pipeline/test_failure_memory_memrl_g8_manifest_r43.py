from __future__ import annotations

import unittest

from .failure_memory_memrl_g8_manifest_r43 import build, validate


class MemRLG8ManifestR43Test(unittest.TestCase):
    def setUp(self) -> None:
        self.d = build()

    def test_current_gate_is_fully_frozen_preoutcome(self) -> None:
        self.assertTrue(all(self.d["inherited_gate_state"][k] for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")))
        self.assertTrue(self.d["G8"]["pass"])
        self.assertEqual(self.d["G8"]["confirmatory_outcomes_observed_before_freeze"], 0)
        self.assertFalse(any(self.d["authority"].values()))

    def test_models_image_units_and_arms_are_frozen(self) -> None:
        m = self.d["execution_manifest"]
        self.assertEqual(m["models"]["llm"]["artifact_manifest_sha256"], "c7e4242ce0f2ebd0700ce3c0ff8e24044a2dddc29f68ef8358993f66e60c153c")
        self.assertEqual(m["models"]["embedding"]["artifact_manifest_sha256"], "ddd2853514c3aadf62ae9efd1751aac4ea3a7b8414b0da654b45f6915894a9e0")
        self.assertEqual(m["runtime_image"]["id"], "sha256:a42dc29f8d95292f261a309a21ba21ceff3a9edef516c54d40e5e9b51f253f1a")
        self.assertEqual(m["runtime_image"]["execution_tag"], "local-os/default:latest")
        self.assertTrue(m["runtime_image"]["execution_tag_same_content_identity"])
        self.assertEqual(m["source_build"]["selected_count"], 128)
        self.assertEqual(m["source_build"]["num_sections"], 1)
        self.assertEqual(m["utilization_qualification"]["selected_cluster_count"], 8)
        self.assertTrue(m["utilization_qualification"]["disjoint_from_primary"])
        self.assertEqual(m["confirmatory_units"]["selected_cluster_count"], 32)
        self.assertEqual(set(m["arms"]), {"A_content_only", "B_raw_provenance", "C_PSMG", "D_nonprovenance_controller"})
        self.assertEqual(m["host"]["runtime_tree_sha256"], "353284315ca6481db3010ff83a5791424f0fcbb4d3d1830b46b3bfba9626dd28")
        self.assertEqual(m["host"]["runtime_manifest_sha256"], "ed146d1f040aaabbf8053ec821ba40e71085d98988b88ff5470ff465d6112cb6")
        self.assertEqual(m["host"]["runtime_manifest_file_sha256"], "532c0da4ab3bcfaa9f02b18caa00cb77c62766c6b61ece5dc205dab18b4e1cc3")
        self.assertEqual(m["host"]["environment"]["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertTrue(m["host"]["environment"]["runtime_target_is_read_only_after_freeze"])
        self.assertEqual(m["models"]["embedding"]["runtime_dimension"], 3072)
        self.assertTrue(m["models"]["embedding"]["dimension_bridge_preserves_l2_norm_and_pairwise_cosine_exactly"])
        self.assertEqual(m["external_runtime_adapter"]["network_scope"], "loopback-only")
        self.assertEqual(m["memoryos_internal"]["chunker_tokenizer_or_token_counter"], "character")
        self.assertTrue(m["memoryos_internal"]["network_dependent_gpt2_default_forbidden"])
        self.assertEqual(m["memoryos_internal"]["synthetic_stack_receipt_sha256"], "abd02364984657e25430b26fe111225566adc1ae9bfc658f14392f93b092133e")

    def test_manifest_is_structurally_valid(self) -> None:
        self.assertEqual(validate(self.d), [])
        self.assertTrue(self.d["claim_policy"]["G8_pass_is_execution_readiness_not_scientific_result"])
        self.assertFalse(self.d["claim_policy"]["new_behavioral_result"])


if __name__ == "__main__":
    unittest.main()
