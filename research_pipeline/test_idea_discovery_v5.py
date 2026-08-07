from __future__ import annotations

import unittest
from .idea_discovery_v5 import build_idea_discovery_v5, validate


class IdeaDiscoveryV5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = build_idea_discovery_v5()

    def test_pool_shape(self) -> None:
        s = self.bank["summary"]
        self.assertEqual(s["raw_candidates"], 36)
        self.assertEqual((s["finalist"], s["revival"], s["repair"], s["component"]), (24, 8, 2, 2))
        self.assertEqual(len(self.bank["finalists"]), 32)
        self.assertEqual(validate(self.bank), [])

    def test_revival_and_component_boundaries(self) -> None:
        revivals = [x for x in self.bank["all_candidates"] if x["internal_status"] == "revival"]
        self.assertTrue(all((x.get("revival_condition") or {}).get("en") for x in revivals))
        components = [x for x in self.bank["all_candidates"] if x["internal_status"] == "component"]
        self.assertEqual(len(components), 2)

    def test_every_candidate_has_simplification_contract(self) -> None:
        for x in self.bank["all_candidates"]:
            with self.subTest(x=x["id"]):
                self.assertTrue(x["strongest_baseline"]["en"])
                self.assertTrue(x["necessity_logic"]["en"])
                self.assertLessEqual(len(x["components"]), 3)

    def test_repository_patterns_are_official_github(self) -> None:
        self.assertGreaterEqual(len(self.bank["repository_patterns"]), 13)
        self.assertTrue(all(x["official_repo"].startswith("https://github.com/") for x in self.bank["repository_patterns"]))


if __name__ == "__main__":
    unittest.main()
