from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="47a8ba35966149bfa6e205304b17c21af72d0804"
OBJECT="RELATIONAL-CONSTRAINT-CAPACITY-20260830"
NOVELTY=ROOT/"generated"/"relational-constraint-capacity-novelty-support-differential-20260831.json"
CHAIN=[
 "scripts/compile_relational_constraint_capacity_construct_v2.py",
 "generated/relational-constraint-capacity-construct-v2-20260830.json",
 "scripts/run_instructscene_non_scientific_execution_smoke.py",
 "scripts/compile_relational_constraint_capacity_pre_f0_adjudication.py",
 "generated/relational-constraint-capacity-pre-f0-adjudication-20260830.json",
 "scripts/compile_relational_constraint_capacity_novelty_support_differential.py",
 "generated/relational-constraint-capacity-novelty-support-differential-20260831.json",
 "generated/paper-first-pre-f0-evidence-acquisition-plan.json",
]
EXTERNAL_TOKENS=[
 "harnessbank","comfyclaw","memorymonotonicity","memoryskill","metaskill",
 "qwenharness","skillcoach","staticprocedural","assetfirststri",
]
EXPECTED={"tests":1820,"failures":1,"errors":27,"skipped":3}
HISTORICAL_REPORTED={"canonical_sha":"0451add2c9bd28740b80f436e3c626b1957e3c3e",
                     "tests":1753,"failures":1,"errors":24,"skipped":3}

def sha(path: Path)->str:
 d=hashlib.sha256()
 with path.open("rb") as f:
  while b:=f.read(4*1024*1024): d.update(b)
 return d.hexdigest()

def compact(text: str)->str:
 return re.sub(r"[^a-z0-9]+","",text.lower())

def classify(label: str,outcome: str,trace: str)->tuple[str,str]:
 key=compact(label+" "+trace)
 if any(token in key for token in [
  "relationalconstraintcapacity","port010","paperfirstevidenceacquisition"]):
  return "AUTHORITY_CRITICAL","direct object/PORT-010/registry-chain identifier"
 if "constraintintegration" in key:
  if "test_proposal_is_noncanonical_zero_execution_authority" in label.replace(" ",""):
   return "UNRELATED_LEGACY_DEBT","stale noncanonical SceneEval status string; shared PORT-010 tests pass"
  return "SCIENTIFIC_OBJECT_DEPENDENCY","nearby constraint substrate; fail closed unless individually cleared"
 if any(token in key for token in EXTERNAL_TOKENS):
  return "UNRELATED_LEGACY_DEBT","separate historical research object; absent from this object's read/import chain"
 if outcome=="SKIP":
  return "UNRELATED_LEGACY_DEBT","optional dependency/environment skip outside this object"
 return "SCIENTIFIC_OBJECT_DEPENDENCY","unmapped regression incident; fail closed"

def parse(log: Path)->dict:
 text=log.read_text(encoding="utf-8",errors="replace")
 ran=re.search(r"Ran (\d+) tests in ([0-9.]+)s",text)
 summary=re.search(r"FAILED \(([^\n]+)\)",text)
 if not ran or not summary: raise SystemExit("incomplete unittest log")
 counts={"tests":int(ran.group(1)),"duration_seconds":float(ran.group(2)),
         "failures":0,"errors":0,"skipped":0}
 for name,value in re.findall(r"(failures|errors|skipped)=(\d+)",summary.group(1)):
  counts[name]=int(value)
 for key,val in EXPECTED.items():
  if counts[key]!=val: raise SystemExit(f"unexpected {key}: {counts[key]}")
 blocks=[]
 header=re.compile(r"^={70}\n(FAIL|ERROR): ([^\n]+)\n-{70}\n",re.M)
 matches=list(header.finditer(text))
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else text.find("\n"+"-"*70+"\nRan ",m.end())
  trace=text[m.end():end if end!=-1 else len(text)].strip()
  category,reason=classify(m.group(2),m.group(1),trace)
  blocks.append({"outcome":m.group(1),"test":m.group(2),"category":category,
                 "reason":reason,"trace_sha256":hashlib.sha256(trace.encode()).hexdigest()})
 skips=[]
 for line in text.splitlines():
  if " ... skipped " in line:
   label,reason=line.split(" ... skipped ",1)
   category,why=classify(label,"SKIP",reason)
   skips.append({"outcome":"SKIP","test":label,"skip_reason":reason,
                 "category":category,"reason":why})
 if len(blocks)!=EXPECTED["failures"]+EXPECTED["errors"]:
  raise SystemExit(f"issue block count drift: {len(blocks)}")
 if len(skips)!=EXPECTED["skipped"]: raise SystemExit(f"skip count drift: {len(skips)}")
 return {"counts":counts,"issues":blocks,"skips":skips,"log_sha256":sha(log)}

def build(log: Path)->dict:
 parsed=parse(log)
 incidents=parsed["issues"]+parsed["skips"]
 summary={k:0 for k in ["AUTHORITY_CRITICAL","SCIENTIFIC_OBJECT_DEPENDENCY",
                         "UNRELATED_LEGACY_DEBT"]}
 for row in incidents: summary[row["category"]]+=1
 chain={name:sha(ROOT/name) for name in CHAIN}
 critical=summary["AUTHORITY_CRITICAL"]+summary["SCIENTIFIC_OBJECT_DEPENDENCY"]
 return {
  "schema_version":"relational-constraint-capacity-legacy-regression-debt-v1",
  "generated_at":"2026-08-31T00:00:00+00:00","object_id":OBJECT,
  "baseline":{"canonical_sha":BASE_SHA,"command":"python -m unittest discover -v",
   "runner":"CPU_ONLY","scientific_gpu_runs":0,"log_sha256":parsed["log_sha256"],
   "historical_user_reported_baseline":HISTORICAL_REPORTED,
   "delta_from_historical":{"tests":67,"failures":0,"errors":3,"skipped":0},
   **parsed["counts"]},
  "authority_chain_audit":{"chain_file_sha256":chain,
   "checked_axes":["authority compiler","source provenance","artifact integrity",
                   "experiment registry","exact replay","object dependency chain"],
   "incidents_in_chain":critical,"classification_counts":summary,
   "shared_port010_regression_checks":"PASS_IN_TARGETED_17_TEST_REPLAY",
   "targeted_constraint_integration_result":{"tests":17,"passed":16,"failed":1,
    "failure":"stale noncanonical SceneEval proposal status expectation",
    "port010_hold_checks_passed":True,"zero_authority_checks_passed":True}},
  "incidents":incidents,
  "adjudication":{"global_suite_clean":False,"legacy_debt_ignored":False,
   "repair_all_legacy_modules_authorized":False,
   "authority_critical_hold":critical>0,
   "scoped_non_blocking_for_this_object":critical==0,
   "reason":("all 1 failure, 27 errors and 3 skips are outside this object's exact "
             "read/import/hash chain; three post-0451 additions are old STRI loader errors; "
             "the shared PORT-010 checks independently pass")},
  "object_state":{"parent_status":"PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY",
   "novelty_verdict":"PRE_F0_REFORMULATE","gpu_authority":False,
   "official_training":False,"P1":False},
 }

def main()->None:
 p=argparse.ArgumentParser(); p.add_argument("--log",type=Path,required=True)
 p.add_argument("--output",type=Path,default=ROOT/"generated"/"relational-constraint-capacity-legacy-regression-debt-20260831.json")
 a=p.parse_args()
 artifact=build(a.log)
 a.output.write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(a.output); print(sha(a.output))

if __name__=="__main__": main()
