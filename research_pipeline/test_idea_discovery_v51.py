from __future__ import annotations

import unittest
from .idea_discovery_v51 import build_idea_discovery_v51, validate


class IdeaDiscoveryV51Test(unittest.TestCase):
    def test_repair_children_preserve_review_vector_contract(self) -> None:
        p=build_idea_discovery_v51()
        self.assertEqual(validate(p),[])
        for x in p.get("children",[]):
            with self.subTest(x=x.get("id")):
                self.assertTrue(x.get("parent_id"))
                self.assertTrue(x.get("repair_source"))
                self.assertTrue(x.get("material_change",{}).get("en"))
                self.assertTrue(x.get("simplest_baseline",{}).get("en"))
                self.assertTrue(x.get("decisive_pilot",{}).get("en"))


if __name__=="__main__":unittest.main()
