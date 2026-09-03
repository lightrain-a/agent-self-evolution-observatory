from __future__ import annotations

import unittest

from .failure_memory_memrl_loopback_binding_repair_r45m1 import (
    EXPECTED_SERVER_SHA256,
    build,
)


class LoopbackBindingRepairR45M1Test(unittest.TestCase):
    def test_v2_changes_only_infrastructure_projection(self) -> None:
        repair, manifest2, diff, auth2 = build()
        self.assertEqual(repair["status"], "PREEXPOSURE_INFRASTRUCTURE_BINDING_REPAIR_PASS")
        self.assertTrue(diff["scientific_projection_byte_identical"])
        self.assertEqual(diff["non_whitelisted_scientific_difference_count"], 0)
        adapter = manifest2["execution_manifest"]["external_runtime_adapter"]
        self.assertEqual(adapter["loopback_server_sha256"], EXPECTED_SERVER_SHA256)
        self.assertEqual(
            adapter["loopback_server_path"],
            "research_pipeline/failure_memory_memrl_local_openai_server_r45m1.py",
        )
        self.assertEqual(
            (auth2.get("pre_authority_accounting") or {}).get("scientific_source_units_executed"),
            0,
        )

    def test_scientific_fields_are_not_reclassified(self) -> None:
        _repair, _manifest2, diff, _auth2 = build()
        allowed = set(diff["allowed_infrastructure_paths"])
        self.assertIn("external_runtime_adapter.loopback_server_path", allowed)
        self.assertIn("external_runtime_adapter.loopback_server_sha256", allowed)
        self.assertNotIn("source_build.system_prompt", allowed)
        self.assertNotIn("source_build.selected_ids", allowed)
        self.assertNotIn("utilization_qualification.arms", allowed)
        self.assertNotIn("confirmatory_units.representative_ids", allowed)


if __name__ == "__main__":
    unittest.main()
