import json, unittest
from research_pipeline.failure_memory_l2_support_reconstruction import *

def traj(refs):
    checks={"must_include":[{"ref":r} for r in refs]} if refs else {"fuzzy_match":[{"ref":"N/A"}]}
    return json.dumps({"rubric_results":[{"details":{"checks":checks}}]})

def row(tid,prompt,refs,success): return {"task_id":tid,"task_prompt":prompt,"trajectory_json":traj(refs),"is_successful":success}

class TestL2Support(unittest.TestCase):
    def records(self):
        r="List out reviewers, if exist, who mention about {}"; c=CRITICISM
        xs=[row("21",r.format("ear cups being small"),["A"],0),row("22",r.format("under water photo"),None,1),row("23",r.format("good fingerprint resistant"),["B"],0),row("24",r.format("price being unfair"),None,1),row("25",r.format("average print quality"),["C"],0),row("26",r.format("complain of the customer service"),["D"],1),row("163",c,["E"],0),row("164",c,["F"],1),row("165",c,["G"],0),row("166",c,None,1),row("167",c,["H"],0)]
        xs += [row(str(1000+i),f"irrelevant {i}",["Z"],i%2) for i in range(EXPECTED_SOURCE_ROWS-len(xs))]
        return xs
    def test_exact_reconstruction(self):
        m=build_manifest(self.records(),EXPECTED_SOURCE_SHA256,"fixture.parquet")
        self.assertEqual([],validate(m)); self.assertEqual(EXPECTED_ELIGIBLE,m["summary"]["eligible_task_ids"]); self.assertFalse(m["summary"]["support_gate_pass"])
        self.assertEqual(["23","164","167"],m["summary"]["prior_d2_exclusions_in_review_family"])
        self.assertIn("PRIOR_D2_TASK_ID_REUSE_FORBIDDEN",next(x for x in m["review_family_manifest"] if x["task_id"]=="164")["blockers"])
    def test_outcomes_do_not_select(self):
        a=self.records(); b=[dict(x,is_successful=not bool(x["is_successful"])) for x in a]
        ma=build_manifest(a,EXPECTED_SOURCE_SHA256,"a"); mb=build_manifest(b,EXPECTED_SOURCE_SHA256,"b")
        self.assertEqual(ma["summary"]["eligible_task_ids"],mb["summary"]["eligible_task_ids"]); self.assertEqual(ma["review_family_manifest"],mb["review_family_manifest"])
    def test_bad_digest_rejected(self):
        with self.assertRaises(ValueError): build_manifest(self.records(),"0"*64,"bad")
    def test_gates_non_authoritative(self):
        m=build_manifest(self.records(),EXPECTED_SOURCE_SHA256,"fixture"); c=build_reopen_contract(m); g=build_analysis_gate(m,c)
        self.assertFalse(c["current_execution_gate"]["model_calls_permitted"]); self.assertFalse(c["current_execution_gate"]["l3_transition_permitted"]); self.assertEqual("NO_VERDICT_SUPPORT_FAILURE",g["scientific_verdict"])

if __name__ == "__main__": unittest.main()
