from __future__ import annotations

import unittest

from .idea_discovery_v53 import build_idea_discovery_v53, validate


class IdeaDiscoveryV53Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_idea_discovery_v53()

    def test_final_boundary_round_is_complete(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual((summary["children"], summary["reviewed"], summary["pending"]), (4, 4, 0))
        self.assertEqual((summary["pass"], summary["revise"], summary["block"]), (3, 1, 0))

    def test_every_child_is_material_and_bilingual(self) -> None:
        self.assertEqual(validate(self.payload), [])
        for child in self.payload["children"]:
            self.assertEqual(child.get("repair_source"), "v52-final-boundary")
            self.assertTrue(child["material_change"]["zh"])
            self.assertTrue(child["material_change"]["en"])
            self.assertTrue(child["simplest_baseline"]["zh"])
            self.assertTrue(child["decisive_pilot"]["zh"])


if __name__ == "__main__":
    unittest.main()
