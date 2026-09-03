from __future__ import annotations

import unittest

from . import failure_memory_memrl_source_qualification_r46m1 as r46m1
from . import failure_memory_memrl_utilization_r47 as r47_base
from . import failure_memory_memrl_utilization_r47m1 as r47m1


class ReplacementDownstreamAdaptersTest(unittest.TestCase):
    def test_r46_uses_replacement_source_helper(self) -> None:
        self.assertTrue(r46m1._build_service_and_runner.__module__.endswith("failure_memory_memrl_source_execute_r45m1"))
        self.assertIs(r46m1.build, r46m1.base.build)
        self.assertEqual(r46m1.STATUS_PASS, r46m1.base.STATUS_PASS)
        self.assertEqual(r46m1.STATUS_STOP, r46m1.base.STATUS_STOP)

    def test_r47_scientific_helpers_are_unchanged(self) -> None:
        self.assertIs(r47m1.arm_order, r47_base.arm_order)
        self.assertIs(r47m1.u4_map, r47_base.u4_map)
        self.assertIs(r47m1.plan, r47_base.plan)
        self.assertIs(r47m1.reverse_blocks, r47_base.reverse_blocks)
        self.assertIs(r47m1.memctx, r47_base.memctx)
        self.assertIs(r47m1.analyze, r47_base.analyze)
        self.assertEqual(r47m1.ARMS, ["U0_no_memory", "U1_true_memory", "U2_null_memory", "U3_reversed_memory", "U4_shuffled_memory"])

    def test_r47_only_updates_replacement_binding_expectations(self) -> None:
        self.assertEqual(r47_base.G8, r47m1.REPLACEMENT_MANIFEST_STATUS)
        self.assertEqual(r47_base.AUTH, r47m1.REPLACEMENT_AUTHORITY_STATUS)
        self.assertEqual(
            r47m1.EXPECTED_LOOPBACK_SERVER_SHA256,
            "f2b4b49b179856cdd02d244fba81ab7c558e747954170285da0eef6119336d92",
        )


if __name__ == "__main__":
    unittest.main()
