from __future__ import annotations

import glob
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))

from c1_pacta_v11_action_schema import canonical_schema
from c1_pacta_v21_first_action_parser import parse_first_action
from c1_pacta_v21_measurement import journal_provider_response, parse_journaled_response

RUN=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-q0-measurement-20260831-v1")
B10=Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-result.json")
ARCHIVES={
 "R9_SCMB":Path("/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1/per_case"),
 "PACTA_V2_SHADOW":Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1/shadow"),
 "PACTA_V2_CLEAN_FINAL":Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1/per_case"),
}

def now(): return datetime.now(timezone.utc).isoformat()
def sha_text(value): return hashlib.sha256(value.encode("utf-8")).hexdigest()
def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def dump(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def write_jsonl(path,rows):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text("".join(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n" for row in rows),encoding="utf-8"); tmp.replace(path)
def require(value,message):
 if not value: raise RuntimeError(message)

def archived_rows():
 rows=[]; counts={}
 b10=load(B10)
 counts["B10"]={"signature_only":len(b10["rollouts"]),"raw_available":0,"reason":"B10 result preserved normalized signatures but no raw provider text"}
 for source,folder in ARCHIVES.items():
  source_rows=[]
  for path in sorted(folder.glob("*.json")):
   row=load(path)
   if row.get("status")!="complete": continue
   raw=row.get("raw_text") if source=="R9_SCMB" else row.get("raw_response")
   if not isinstance(raw,str) or not raw: continue
   source_rows.append({
    "source":source,"path":str(path),"raw":raw,"legacy_signature":row["action_signature"],
    "raw_sha256":sha_text(raw),"artifact_sha256":hashlib.sha256(path.read_bytes()).hexdigest()
   })
  counts[source]={"clean_raw_available":len(source_rows)}
  rows.extend(source_rows)
 return rows,counts

def positive_fixtures():
 action='{"input_text":{"index":6,"text":"PS4 accessories"}}'
 return [
  ("malformed_current_state",'{"current_state":{"evaluation_previous_goal":tru,"action":['+action+'],"next_goal":"search"}}',"input_text"),
  ("missing_comma_outside_first_action",'{"current_state":{"x":"ok"},"action":['+action+'] "next_goal":"search"}',"input_text"),
  ("truncated_next_goal",'{"current_state":{"x":"ok"},"action":['+action+'],"next_goal":"search',"input_text"),
  ("trailing_prose",'{"current_state":{"x":"ok"},"action":['+action+']} trailing prose',"input_text"),
  ("malformed_later_fields",'{"current_state":{"x":"ok"},"action":['+action+'],"later":{"bad":[1,2,]}}',"input_text"),
 ]

def negative_fixtures():
 return [
  ("malformed_first_action",'{"action":[{"input_text":{"index":6,"text":x}}]}',"invalid JSON inside first action"),
  ("ambiguous_first_action",'{"action":[{"wait":,"action":[{"go_back":{}}]}',"first action incomplete before a later candidate"),
  ("multiple_tool_keys",'{"action":[{"wait":{"seconds":1},"go_back":{}}]}',"multiple tools"),
  ("truncated_action_args",'{"action":[{"input_text":{"index":6,"text":"x}],"next_goal":"x"}',"truncated args"),
  ("no_action",'{"current_state":{"next_goal":"x"}}',"no action"),
 ]

def main():
 require(not RUN.exists(),"qualification run already exists")
 RUN.mkdir(parents=True)
 archived,counts=archived_rows()
 results=[]; mismatches=[]
 for row in archived:
  try:
   parsed=parse_first_action(row["raw"])
   result={k:v for k,v in row.items() if k!="raw"}
   result.update({"new_signature":parsed.signature,"parser_mode":parsed.mode,"match":parsed.signature==row["legacy_signature"]})
  except Exception as exc:
   result={k:v for k,v in row.items() if k!="raw"}
   result.update({"new_signature":None,"parser_mode":"FAIL","match":False,"failure_type":type(exc).__name__,"failure":str(exc)})
  results.append(result)
  if not result["match"]: mismatches.append(result)

 positives=[]
 for fixture_id,text,expected in positive_fixtures():
  try:
   parsed=parse_first_action(text)
   row={"fixture_id":fixture_id,"status":"PASS" if parsed.signature==expected and parsed.mode=="first_action_only_recovery" else "FAIL",
        "expected":expected,"observed":parsed.signature,"mode":parsed.mode,"raw_sha256":sha_text(text)}
  except Exception as exc:
   row={"fixture_id":fixture_id,"status":"FAIL","expected":expected,"failure_type":type(exc).__name__,"failure":str(exc),"raw_sha256":sha_text(text)}
  positives.append(row)

 negatives=[]
 for fixture_id,text,reason in negative_fixtures():
  try:
   parsed=parse_first_action(text)
   row={"fixture_id":fixture_id,"status":"FAIL","reason":reason,"unexpected_signature":parsed.signature,"mode":parsed.mode,"raw_sha256":sha_text(text)}
  except Exception as exc:
   row={"fixture_id":fixture_id,"status":"PASS_FAIL_CLOSED","reason":reason,"failure_type":type(exc).__name__,"failure":str(exc),"raw_sha256":sha_text(text)}
  negatives.append(row)

 injection_path=RUN/"failure-injection"/"write-before-parse.json"
 injection_raw='{"current_state":{"x":"ok"},"action":[{"input_text":{"index":6,"text":"unterminated}}]}'
 fake_response={"response_id":"synthetic-response-id","status":"completed","requested_model":"doubao-seed-2.0-mini",
                "resolved_model":"doubao-seed-2-0-mini-260215","thinking_compatibility_fallback":False,"usage":{"input_tokens":1,"output_tokens":1}}
 request={"case_id":"synthetic-write-before-parse","prompt_sha256":sha_text("synthetic-prompt")}
 journal_provider_response(injection_path,request,fake_response,injection_raw)
 before=load(injection_path); after=parse_journaled_response(injection_path)
 injection_pass=(
  before["status"]=="provider_response_persisted_unparsed" and after["status"]=="failed_first_action_parser" and
  after["response_id"]=="synthetic-response-id" and after["raw_response"]==injection_raw and
  after["raw_response_sha256"]==sha_text(injection_raw) and after["prompt_sha256"]==request["prompt_sha256"]
 )

 archived_pass=len(archived)==636 and not mismatches
 positive_pass=all(row["status"]=="PASS" for row in positives)
 negative_pass=all(row["status"]=="PASS_FAIL_CLOSED" for row in negatives)
 passed=archived_pass and positive_pass and negative_pass and injection_pass
 write_jsonl(RUN/"archived-replay.jsonl",results)
 dump(RUN/"synthetic-positive.json",{"fixtures":positives})
 dump(RUN/"synthetic-negative.json",{"fixtures":negatives})
 result={
  "schema_version":"1.0","artifact_kind":"C1_PACTA_V21_MEASUREMENT_QUALIFICATION",
  "status":"PASS_MEASUREMENT_QUALIFICATION" if passed else "STOP_MEASUREMENT_QUALIFICATION",
  "scientific_provider_calls":0,"action_schema_sha256":sha_text(canonical_schema()),
  "archived_sources":counts,"archived_raw_outputs_replayed":len(archived),
  "archived_signature_matches":sum(row["match"] for row in results),"archived_mismatches":mismatches,
  "positive_fixtures":{"pass":sum(row["status"]=="PASS" for row in positives),"total":len(positives)},
  "negative_fixtures":{"fail_closed":sum(row["status"]=="PASS_FAIL_CLOSED" for row in negatives),"total":len(negatives)},
  "write_before_parse_failure_injection":{"pass":injection_pass,"artifact":str(injection_path),
    "raw_retained":after.get("raw_response")==injection_raw,"response_id_retained":after.get("response_id")=="synthetic-response-id"},
  "completed_at":now()
 }
 dump(RUN/"qualification.json",result)
 print(json.dumps(result,ensure_ascii=False))
 return 0 if passed else 2

if __name__=="__main__": raise SystemExit(main())
