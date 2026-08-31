from __future__ import annotations
import json
from pathlib import Path
import pytest
from research_pipeline.c1_pacta_rb_qwen397 import (atomic_json,build_final_schedule,build_shadow_schedule,
 choose_budget,discover_qwen397,freeze_model_binding,gate,parse_first_decision,pilot_split,
 rate_matched_random,sha256_file,validate_fresh_pool,writer_twins_valid)
ROOT=Path(__file__).resolve().parents[1];PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
def units(n=6):
 return [{"unit_id":f"repo{i}__source=>repo{i}__future","task_family":f"repo{i}","source_trajectory_path":None,
  "source_trajectory_sha256":None,"prior_reasoningbank_scientific_output":False} for i in range(n)]
def test_model_discovery_prefers_fixed_snapshot():
 assert discover_qwen397(["qwen3.5-397b-a17b","qwen3.5-397b-a17b-20260801"])=="qwen3.5-397b-a17b-20260801"
def test_model_discovery_accepts_stable_only_and_rejects_other_models():
 assert discover_qwen397(["qwen3.5-397b-a17b"])=="qwen3.5-397b-a17b"
 with pytest.raises(ValueError):discover_qwen397(["qwen3.5-122b-a10b"])
def test_three_probe_model_binding_and_drift():
 rows=[{"requested_model":"m","resolved_model":"r","endpoint":"e","fallback":False} for _ in range(3)]
 assert freeze_model_binding(rows)["resolved_or_returned_model"]=="r";rows[-1]["resolved_model"]="r2"
 with pytest.raises(ValueError):freeze_model_binding(rows)
def test_first_decision_parser_is_exact_and_deterministic():
 text="THOUGHT: inspect\n\n```bash\nrg -n 'target' src\n```"
 assert parse_first_decision(text)=="rg -n 'target' src"
 with pytest.raises(ValueError):parse_first_decision(text+"\n"+text)
def test_write_before_parse_failure_keeps_raw(tmp_path):
 path=tmp_path/"raw.json";atomic_json(path,{"raw_response":"broken envelope","persisted_before_parse":True})
 with pytest.raises(ValueError):parse_first_decision("broken envelope")
 assert json.loads(path.read_text())["raw_response"]=="broken envelope"
def test_action_budget_selects_smallest_full_twenty():
 good={"provider_success":True,"status":"completed","parse_success":True,"persisted_before_parse":True,
  "model_drift":False,"fallback":False,"ambiguous":False}
 assert choose_budget({512:[dict(good) for _ in range(19)],1024:[dict(good) for _ in range(20)]})==1024
def test_action_budget_fails_if_no_full_cell():
 with pytest.raises(ValueError):choose_budget({})
def test_freshness_requires_real_content_addressed_trajectory(tmp_path):
 u=units(1)[0];assert validate_fresh_pool([u])["valid_unit_count"]==0
 p=tmp_path/"trajectory.json";p.write_text("{}");u["source_trajectory_path"]=str(p);u["source_trajectory_sha256"]=sha256_file(p)
 assert validate_fresh_pool([u])["valid_unit_count"]==1;u["prior_reasoningbank_scientific_output"]=True
 assert validate_fresh_pool([u])["valid_unit_count"]==0
def test_pilot_split_refuses_planned_ids_without_trajectories():
 split=pilot_split(units(11));assert split["pilot"]==[] and len(split["sealed"])==11
def test_writer_twin_invariance_and_memory_difference():
 base={"trajectory_sha256":"t","source_task_sha256":"q","requested_model":"m","resolved_model":"m","temperature":0,"context_sha256":"c"}
 s={**base,"branch":"success","memory_sha256":"s"};f={**base,"branch":"failure","memory_sha256":"f"}
 assert writer_twins_valid(s,f);f["trajectory_sha256"]="other";assert not writer_twins_valid(s,f)
def test_shadow_schedule_geometry_and_interleaving():
 rows=build_shadow_schedule(units());assert len(rows)==144 and len({r["case_id"] for r in rows})==144
 assert {r["branch"] for r in rows}=={"success","failure"} and {r["block"] for r in rows}=={1,2}
def test_gate_strict_definition_and_missingness():
 assert gate({"S1":["a"]*6,"S2":["a"]*6,"F1":["b"]*6,"F2":["b"]*6})["G"] is True
 assert gate({"S1":["a"]*6,"S2":["a"]*6,"F1":["a"]*6,"F2":["a"]*6})["G"] is False
 with pytest.raises(ValueError):gate({"S1":[]})
def test_rate_matched_random_is_deterministic_and_exact_k():
 ids=[u["unit_id"] for u in units()];assert rate_matched_random(ids,3)==rate_matched_random(ids,3);assert len(rate_matched_random(ids,3))==3
def test_final_schedule_geometry_and_arm_semantics():
 us=units();ids=[u["unit_id"] for u in us];p=set(ids[:2]);r=set(ids[2:4]);rows=build_final_schedule(us,p,r)
 assert len(rows)==288 and len({x["case_id"] for x in rows})==288
 for x in rows:
  expected=x["arm"]=="A1_SCB_ALWAYS" or (x["arm"]=="A2_RATE_MATCHED_RANDOM" and x["unit_id"] in r) or (x["arm"]=="A3_PACTA" and x["unit_id"] in p)
  assert x["uses_scb"]==expected
def test_claim_authority_closes_before_science():
 closure=json.loads((PAPER/"c1-pacta-rb-qwen397-pilot-closure-20260831.json").read_text())
 claim=json.loads((PAPER/"c1-pacta-rb-qwen397-claim-audit-20260831.json").read_text())
 assert closure["status"]=="HOLD_FRESH_SUPPORT_INSUFFICIENT"
 assert closure["scientific_tokens"]=={"estimated_cost":0,"input":0,"output":0}
 assert claim["status"]=="NO_NEW_SCIENTIFIC_EVIDENCE" and claim["active_manuscript"]=="R9"
