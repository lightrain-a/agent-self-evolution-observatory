from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"generated"/"relational-constraint-capacity-legacy-regression-debt-20260831.json"
EXPECTED="7e623a8c4ce24eb80b3cc2265b7d4bd6bd2d0da829e909ff83b339a7d313d7cf"

def sha(path: Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

class LegacyRegressionDebtTest(unittest.TestCase):
 def setUp(self)->None:
  self.a=json.loads(ART.read_text(encoding="utf-8"))

 def test_content_address_and_exact_baseline(self)->None:
  self.assertEqual(sha(ART),EXPECTED)
  b=self.a["baseline"]
  self.assertEqual(b["canonical_sha"],"47a8ba35966149bfa6e205304b17c21af72d0804")
  self.assertEqual(b["command"],"python -m unittest discover -v")
  self.assertEqual(b["runner"],"CPU_ONLY")
  self.assertEqual(b["historical_user_reported_baseline"],{
   "canonical_sha":"0451add2c9bd28740b80f436e3c626b1957e3c3e",
   "tests":1753,"failures":1,"errors":24,"skipped":3})
  self.assertEqual(b["delta_from_historical"],{
   "tests":67,"failures":0,"errors":3,"skipped":0})
  self.assertEqual(b["tests"],1820)
  self.assertEqual(b["failures"],1)
  self.assertEqual(b["errors"],27)
  self.assertEqual(b["skipped"],3)
  self.assertRegex(b["log_sha256"],r"^[0-9a-f]{64}$")

 def test_every_incident_is_explicitly_classified(self)->None:
  rows=self.a["incidents"]
  self.assertEqual(len(rows),31)
  self.assertEqual(sum(r["outcome"]=="FAIL" for r in rows),1)
  self.assertEqual(sum(r["outcome"]=="ERROR" for r in rows),27)
  self.assertEqual(sum(r["outcome"]=="SKIP" for r in rows),3)
  allowed={"AUTHORITY_CRITICAL","SCIENTIFIC_OBJECT_DEPENDENCY",
           "UNRELATED_LEGACY_DEBT"}
  self.assertEqual({r["category"] for r in rows}, {"UNRELATED_LEGACY_DEBT"})
  self.assertTrue(all(r["category"] in allowed and r["reason"] for r in rows))

 def test_authority_chain_is_untouched_and_debt_is_scoped(self)->None:
  audit=self.a["authority_chain_audit"]
  self.assertEqual(audit["incidents_in_chain"],0)
  self.assertEqual(audit["classification_counts"],{
   "AUTHORITY_CRITICAL":0,"SCIENTIFIC_OBJECT_DEPENDENCY":0,
   "UNRELATED_LEGACY_DEBT":31})
  self.assertEqual(len(audit["chain_file_sha256"]),8)
  self.assertTrue(all(len(v)==64 for v in audit["chain_file_sha256"].values()))
  targeted=audit["targeted_constraint_integration_result"]
  self.assertEqual(targeted["tests"],17)
  self.assertEqual(targeted["passed"],16)
  self.assertTrue(targeted["port010_hold_checks_passed"])
  self.assertTrue(targeted["zero_authority_checks_passed"])

 def test_global_debt_is_recorded_not_repaired_or_ignored(self)->None:
  a=self.a["adjudication"]
  self.assertFalse(a["global_suite_clean"])
  self.assertFalse(a["legacy_debt_ignored"])
  self.assertFalse(a["repair_all_legacy_modules_authorized"])
  self.assertFalse(a["authority_critical_hold"])
  self.assertTrue(a["scoped_non_blocking_for_this_object"])
  text=" ".join(r["test"] for r in self.a["incidents"])
  self.assertNotIn("relational_constraint_capacity",text.lower())
  self.assertNotIn("port010",text.lower())

 def test_object_remains_reformulate_without_authority(self)->None:
  state=self.a["object_state"]
  self.assertEqual(state["parent_status"],
                   "PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY")
  self.assertEqual(state["novelty_verdict"],"PRE_F0_REFORMULATE")
  self.assertFalse(state["gpu_authority"])
  self.assertFalse(state["official_training"])
  self.assertFalse(state["P1"])

if __name__=="__main__": unittest.main()
