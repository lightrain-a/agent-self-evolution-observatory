from __future__ import annotations

import unittest

from .p15_order_effect_harness import (
    TASKS,
    adjudicate,
    all_units,
    conditions_for_task,
    evaluate_solution,
    offline_probe,
    validate_solution_ast,
)


REFERENCE = {
    "T1": '''import unicodedata\nfrom collections import defaultdict\ndef solve(records):\n    sums=defaultdict(int)\n    for r in records:\n        k=unicodedata.normalize("NFKC",r["team"]).strip().casefold()\n        sums[k]+=r["score"]\n    return [{"team":k,"score":v} for k,v in sorted(sums.items(),key=lambda x:(-x[1],x[0]))]\n''',
    "T2": '''from decimal import Decimal, InvalidOperation\nfrom collections import defaultdict\ndef solve(records):\n    sums=defaultdict(Decimal)\n    for r in records:\n        try: v=Decimal(r["amount"])\n        except (InvalidOperation,TypeError): continue\n        if not v.is_finite(): continue\n        sums[r["category"]]+=v\n    return [{"category":k,"amount":format(v,".2f")} for k,v in sorted(sums.items(),key=lambda x:(-x[1],x[0]))]\n''',
    "T3": '''import unicodedata\nfrom decimal import Decimal, InvalidOperation\ndef solve(records):\n    seen_keys=set();out=[]\n    for r in records:\n        k=unicodedata.normalize("NFKC",r["sku"]).strip().casefold()\n        try: v=Decimal(r["price"])\n        except (InvalidOperation,TypeError): continue\n        if not v.is_finite() or k in seen_keys: continue\n        seen_keys.add(k);out.append({"sku":k,"price":format(v,".2f")})\n    return out\n''',
    "T4": '''import unicodedata\ndef solve(records):\n    seen_keys=set();out=[]\n    for r in records:\n        key=(unicodedata.normalize("NFKC",r["name"]).strip().casefold(),unicodedata.normalize("NFKC",r["tag"]).strip().casefold())\n        if key in seen_keys: continue\n        seen_keys.add(key);out.append({"name":key[0],"tag":key[1]})\n    return sorted(out,key=lambda x:(x["name"],x["tag"]))\n''',
    "T5": '''from decimal import Decimal, InvalidOperation\nfrom collections import defaultdict\ndef solve(records):\n    seen_keys=set();sums=defaultdict(Decimal)\n    for r in records:\n        try: v=Decimal(r["value"])\n        except (InvalidOperation,TypeError): continue\n        if not v.is_finite() or r["event_id"] in seen_keys: continue\n        seen_keys.add(r["event_id"]);sums[r["group"]]+=v\n    return {k:format(v,".2f") for k,v in sums.items()}\n''',
}


class P15OrderEffectHarnessTest(unittest.TestCase):
    def test_offline_probe_freezes_50_units_and_six_same_skill_permutations(self):
        probe=offline_probe()
        self.assertEqual(probe["status"],"P15_OFFLINE_HARNESS_PROBE_PASS")
        self.assertEqual(probe["unit_count"],50)
        self.assertEqual(len(all_units()),50)
        for task_id in TASKS:
            rows=conditions_for_task(task_id)
            self.assertEqual(sum(r["kind"]=="PERMUTATION" for r in rows),6)
            self.assertEqual({tuple(sorted(r["skills"])) for r in rows if r["kind"]=="PERMUTATION"},{tuple(sorted(TASKS[task_id]["skills"]))})

    def test_reference_solutions_pass_independent_unit_tests(self):
        for task_id,code in REFERENCE.items():
            result=evaluate_solution(task_id,code)
            self.assertTrue(result["valid_execution"],task_id)
            self.assertTrue(result["task_success"],task_id)
            for skill in TASKS[task_id]["skills"]:
                self.assertTrue(result["uptake"][skill],(task_id,skill,result["uptake"]))

    def test_ast_rejects_file_process_and_top_level_execution(self):
        bad="import os\nos.system('echo no')\ndef solve(records):\n    return records\n"
        audit=validate_solution_ast(bad)
        self.assertFalse(audit["valid"])
        self.assertTrue(any("forbidden-import" in e or "forbidden-top-level" in e for e in audit["errors"]))

    def test_adjudication_reduction_when_all_permutations_invariant(self):
        rows=[]
        for unit in all_units():
            rows.append({"unit_id":unit["unit_id"],"valid_execution":True,"task_success":True,"uptake":{skill:True for skill in TASKS[unit["task_id"]]["skills"]}})
        out=adjudicate(rows)
        self.assertEqual(out["outcome"],"REDUCTION_SUPPORTED")
        self.assertEqual(out["divergent_tasks"],0)

    def test_adjudication_residual_requires_two_success_divergent_tasks_and_uptake(self):
        rows=[]
        for unit in all_units():
            success=True
            uptake={skill:True for skill in TASKS[unit["task_id"]]["skills"]}
            if unit["task_id"] in {"T1","T2"} and unit["kind"]=="PERMUTATION" and unit["condition_id"] in {"PERM-2","PERM-4","PERM-6"}:
                success=False
                first=TASKS[unit["task_id"]]["skills"][0];uptake[first]=False
            rows.append({"unit_id":unit["unit_id"],"valid_execution":True,"task_success":success,"uptake":uptake})
        out=adjudicate(rows)
        self.assertEqual(out["outcome"],"RESIDUAL_SURVIVES")
        self.assertGreaterEqual(out["divergent_tasks"],2)

    def test_adjudication_invalid_unit_is_inconclusive(self):
        rows=[]
        for unit in all_units():
            rows.append({"unit_id":unit["unit_id"],"valid_execution":unit["unit_id"]!="T1-PERM-1","task_success":True,"uptake":{}})
        out=adjudicate(rows)
        self.assertEqual(out["outcome"],"INCONCLUSIVE")
        self.assertIn("T1-PERM-1",out["invalid_units"])


if __name__=="__main__":unittest.main()
