from __future__ import annotations

import unittest

from research_pipeline.b3_minteval_wiki_support import build_wiki_history_candidates, select_source_disjoint_wiki_candidates


class B3MintevalWikiSupportTest(unittest.TestCase):
    def fixture(self, article="A"):
        contexts=[]
        for i,name in enumerate(["Alpha","Beta","Gamma","Delta","Epsilon","Zeta"]):
            contexts.append({
                "timestamp":f"2026-01-0{i+1}T00:00:00Z",
                "content":(("Mountains rivers forests oceans weather geography. "*80)+f"\nTarget ruler name is {name}. The ruler governed Exampleland.\n"+("Music art painting sculpture theatre literature. "*80)),
            })
        return {
            "id":article,
            "contexts":contexts,
            "questions":[{
                "answer":"Delta",
                "metadata":"{\"n_steps_back\": 2}",
                "question":"What ruler name does the version of the article 2 edits before the latest version use for the ruler of Exampleland?",
                "question_type":"history",
            }],
        }

    def test_target_is_fixed_by_metadata_not_gold(self):
        rows=build_wiki_history_candidates([self.fixture()])
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["target_index"],3)
        self.assertFalse(row["selection_used_model_outputs"])
        self.assertFalse(row["selection_used_gold_answer"])
        self.assertEqual(len(row["arm_memories"]["none"]),3)
        self.assertEqual(len(row["arm_memories"]["AB"]),3)
        self.assertNotEqual(row["stale_memory_A"]["index"],row["stale_memory_B"]["index"])

    def test_gold_change_does_not_change_pair_selection(self):
        a=self.fixture(); b=self.fixture(); b["questions"][0]["answer"]="NOT_THE_TARGET"
        ra=build_wiki_history_candidates([a])[0]
        rb=build_wiki_history_candidates([b])[0]
        self.assertEqual(ra["candidate_id"],rb["candidate_id"])
        self.assertEqual(ra["support_memory"],rb["support_memory"])
        self.assertEqual(ra["stale_memory_A"],rb["stale_memory_A"])
        self.assertEqual(ra["stale_memory_B"],rb["stale_memory_B"])

    def test_source_disjoint_selection(self):
        a=build_wiki_history_candidates([self.fixture("A")])[0]
        b=dict(a); b["candidate_id"]="same-article-other"; b["question_index"]=9
        c=build_wiki_history_candidates([self.fixture("B")])[0]
        out=select_source_disjoint_wiki_candidates([a,b,c],limit=10)
        self.assertEqual([x["history_id"] for x in out],["A","B"])


if __name__ == "__main__":
    unittest.main()
