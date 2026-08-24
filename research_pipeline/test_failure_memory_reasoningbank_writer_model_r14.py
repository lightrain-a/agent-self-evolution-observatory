import copy
import unittest

from research_pipeline.failure_memory_reasoningbank_writer_model_r14 import build_receipt


class TestReasoningBankWriterModelR14(unittest.TestCase):
    def parent(self):
        return {
            "writer_contract": {"writer_model_family": "Qwen2.5-32B", "temperature": 0.0},
            "summary": {"source_tasks": 36, "model_calls_executed": 0},
        }

    def parsed(self):
        return {
            "layers": [
                {
                    "media_type": "application/vnd.ollama.image.model",
                    "digest": "sha256:eabc98a9bcbfce7fd70f3e07de599f8fda98120fefed5881934161ede8bd1a41",
                    "size_bytes": 19851336288,
                    "sha256_verified": True,
                }
            ]
        }

    def show(self):
        return {
            "details": {
                "format": "gguf",
                "family": "qwen2",
                "parameter_size": "32.8B",
                "quantization_level": "Q4_K_M",
            },
            "model_info": {"general.parameter_count": 32763876352},
        }

    def registry(self):
        return {"data": [{"id": "qwen2.5:32b"}]}

    def test_accepts_content_addressed_realization_without_authority(self):
        r = build_receipt(self.parent(), "a" * 64, self.parsed(), self.show(), "b" * 64, self.registry(), "c" * 64, "ollama version is 0.18.2")
        self.assertTrue(r["execution_gate"]["exact_writer_model_artifact_bound"])
        self.assertFalse(r["execution_gate"]["writer_calls_permitted"])
        self.assertEqual(r["execution_gate"]["writer_calls_executed"], 0)
        self.assertFalse(r["historical_relationship"]["claim_exact_binary_identity_with_R6"])
        self.assertFalse(r["authority"]["model_calls"])

    def test_rejects_quantization_drift(self):
        show = copy.deepcopy(self.show())
        show["details"]["quantization_level"] = "Q8_0"
        with self.assertRaises(RuntimeError):
            build_receipt(self.parent(), "a" * 64, self.parsed(), show, "b" * 64, self.registry(), "c" * 64, "0.18.2")

    def test_rejects_parent_with_writer_calls(self):
        parent = self.parent()
        parent["summary"]["model_calls_executed"] = 1
        with self.assertRaises(RuntimeError):
            build_receipt(parent, "a" * 64, self.parsed(), self.show(), "b" * 64, self.registry(), "c" * 64, "0.18.2")


if __name__ == "__main__":
    unittest.main()
