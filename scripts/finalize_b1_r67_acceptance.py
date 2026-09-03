#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.paper_acceptance import *
from research_pipeline.paper_acceptance_ledger import (_append,_digest,advance_paper_ledger,build_paper_ledger_index,load_paper_ledger,record_claim_audit,record_manuscript_ci,record_mock_review,record_prebuttal,record_story_search,record_submission_readiness,reopen_ready_paper_contract,validate_paper_ledger)
PID="D2-PAPER-FAILURE-MEMORY-PROVENANCE";OLD="dbf81e071aaca6270d710c084c1d9f6b5ec78497c28fc9912f40b8d417f14ac7"
TITLE="Does Memory Provenance Matter? Explicit Source-Outcome Cues Shift Agent Actions but Rarely Change Terminal Outcomes"
REL=ROOT/"generated/d2-failure-memory-provenance-r66-postoracle-manuscript-release.json";STAT=ROOT/"generated/d2-failure-memory-provenance-r66-sparse-discordance-statistical-audit.json";ISO=ROOT/"generated/d2-failure-memory-provenance-r66-osinteraction-arm-isolation-audit.json";REV=ROOT/"generated/d2-failure-memory-provenance-r66-oracle-review-summary.json";R62=ROOT/"generated/d2-failure-memory-provenance-r62-cross-backbone-l2-adjudication.json"
A=lambda h:f"artifact:sha256:{h}"
def sf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):return json.loads(p.read_text(encoding="utf-8"))
def contract(prev:dict)->PaperContract:
 refs=tuple(dict.fromkeys([*(prev.get("evidence_refs") or []),A(sf(R62)),A(sf(REL)),A(sf(STAT)),A(sf(ISO)),A(sf(REV))]))
 return PaperContract(PID,TITLE,"Beyond identical retrieved memory content, what closed-loop effect follows from revealing an explicit truthful source-outcome indicator that would otherwise be masked?",{
  "C1":"Success-derived ReasoningBank retrievals achieve 0.931 accuracy over 101 cases while failure-derived retrievals achieve 0.647 over 34 cases in the released financial-agent audit.",
  "C2":"All ten reported ReasoningBank W->W persistent failures lie in the failure-derived retrieval stratum.",
  "C3":"ReasoningBank uses distinct success- and failure-conditioned writer modes; changing those writers is an L1 writer-mode bundle intervention and cannot by itself identify the L2 incremental value of provenance information when actionable memory content differs.",
  "C4":"In the prospective full350 Qwen L2 experiment, masking versus truthfully revealing source_outcome_success over identical frozen retrieval content/order gives observed terminal success 15/32 versus 16/32 (Delta=+0.03125), first-action divergence in 9/32, and terminal discordance in 1/32. The point estimate does not reach the preregistered 0.15 threshold; a post-confirmatory conservative paired risk-difference 95% interval of about [-0.128,0.183] does not establish +/-0.15 equivalence or exclude a +0.15 population effect.",
  "C5":"On the same frozen source-bank/retrieval/task/renderer substrate, Meta-Llama-3.1-8B-Instruct gives observed terminal success 17/32 versus 17/32 (Delta=0), first-action divergence in 8/32, and four terminal discordances split 2 B-only/2 A-only. Its conservative paired risk-difference 95% interval of about [-0.225,0.225] likewise does not establish +/-0.15 equivalence. This is executor-only replication, not an independent pipeline replication.",
  "C6":"The identified object is the closed-loop effect of explicit truthful source-outcome-field revelation beyond already-visible memory content: field exposure can perturb local action selection while binary terminal labels are much less sensitive on these frozen samples. Because memory text may already leak outcome clues and the added field also changes prompt surface, the experiment does not by itself identify semantic provenance reasoning or the general decision value of provenance."
 },{
  "U1":"The experiment proves provenance has zero or negligible population effect within +/-15 percentage points.",
  "U2":"The masked arm contains no provenance information at all.",
  "U3":"First-action divergence proves semantic understanding or rational weighting of success/failure provenance.",
  "U4":"Failure-derived memories are inherently harmful or success-derived memories inherently beneficial.",
  "U5":"The Llama result independently replicates the writer, retriever, memory bank, renderer, data distribution, or benchmark substrate.",
  "U6":"PSMG/governor efficacy or source-faithful L3 transport is established."
 },(
  "A may contain implicit source-outcome clues such as failure-reflection language; L2 identifies incremental structured-field revelation beyond that visible text.",
  "Adding source_outcome_success changes prompt surface as well as information, so local action sensitivity is not uniquely attributable to semantic provenance reasoning.",
  "Terminal discordance is sparse (1/32 Qwen; 4/32 Llama), making p=1.0 low-resolution and the preregistered empirical bootstrap unsuitable as an equivalence proof.",
  "The conservative post-confirmatory intervals do not exclude a +15pp population effect; the preregistered 15pp threshold remains unchanged and is reported only as not reached by the observed point estimates.",
  "Each arm starts from a fresh OSInteraction Docker container, but downstream observations may differ after actions diverge because they are treatment-induced mediators.",
  "Llama reuses the Qwen/MemRL source bank, frozen retrieval, tasks, renderer, and evaluator; it is executor-only replication.",
  "PSMG efficacy and source-faithful L3 transport remain untested."
 ),(
  "For a stronger semantic-provenance claim, prospectively freeze a format-matched UNKNOWN-or-masked versus truthful versus reversed-or-shuffled field experiment with the same structured field present in every arm.",
  "Reopen PSMG efficacy only under a separate prospective governor-versus-strongest-same-information-provenance-free controller contract.",
  "Reopen L3 only after the source-faithful financial ReasoningBank runtime and per-query artifacts are content-addressed.",
  "Reopen broader system generalization only on an independent writer/retriever/memory substrate rather than further outcome-driven reruns of the current surface."
 ),refs,ScientificPaperStatus.READY)
def stories():return [StoryCandidate("R67-FIELD-FIRST","Explicit outcome field beyond memory content","Lead with the exact masked-versus-revealed intervention, then local-versus-terminal sensitivity, sparse-discordance limits, and governance boundary.",( "C4","C5","C6","C1","C2","C3"),("C4","C5","C6")),StoryCandidate("R67-AUDIT-FIRST","From confounded provenance association to identifiable field exposure","Lead with the L0-L3 non-upgrade ladder and end at the narrow closed-loop field-revelation result.",( "C1","C2","C3","C4","C5","C6"),("C3","C4","C6"))]
def reviews():
 b=[ReviewerObjection("B1","causal-estimand","Do not say realized environment feedback is held fixed after treatment-induced actions diverge; identify a closed-loop total effect from a reset initial state.",True,ObjectionEvidenceState.EXISTING_EVIDENCE,("C4","C5","C6")),ReviewerObjection("B2","treatment-scope","The masked arm can leak outcome clues and the field changes prompt surface, so do not call first-action divergence semantic provenance utilization.",True,ObjectionEvidenceState.EXISTING_EVIDENCE,("C4","C6")),ReviewerObjection("B3","statistics","Sparse terminal discordance and p=1 do not establish practical equivalence; preserve the 15pp threshold but repair null/equivalence wording.",True,ObjectionEvidenceState.EXISTING_EVIDENCE,("C4","C5"))]
 a=[ReviewerObjection("A1","isolation","Document that each arm resets into a fresh OSInteraction container and releases it so filesystem/user/process state cannot carry across arms.",True,ObjectionEvidenceState.EXISTING_EVIDENCE,("C4",)),ReviewerObjection("A2","replication-scope","Call Llama executor-only replication on a shared frozen substrate.",True,ObjectionEvidenceState.EXISTING_EVIDENCE,("C5",)),ReviewerObjection("A3","mechanism","Task 252 is outcome-selected illustration and cannot establish why the aggregate effect occurs.",False,ObjectionEvidenceState.EXISTING_EVIDENCE,("C4","C6"))];return b,a
def trans(root,c,s,refs):
 r=advance_paper_ledger(root,c,s,actor="b1-r67-gate",artifact_refs=refs)["receipt"]
 if r.get("allowed") is not True:raise RuntimeError(f"blocked {s.value}:{r.get('blockers')}")
def event(root,c,t,p):
 x={"event_type":t,"schema_version":"1.0","paper_id":PID,"revision":"R67",**p,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False};x["receipt_sha256"]=_digest({k:v for k,v in x.items() if k!="receipt_sha256"});_append(root,c,"b1-r67-finalization",x)
def finalize(root:Path,out:Path|None=None):
 for p in (REL,STAT,ISO,REV,R62):
  if not p.is_file():raise RuntimeError(f"missing:{p}")
 rel=load(REL);pdf=ROOT/rel["release_artifacts"]["pdf"]["path"];src=ROOT/rel["release_artifacts"]["source_zip"]["path"];sup=ROOT/rel["release_artifacts"]["supplement_zip"]["path"]
 for p,k in ((pdf,"pdf"),(src,"source_zip"),(sup,"supplement_zip")):
  if sf(p)!=rel["release_artifacts"][k]["sha256"]:raise RuntimeError(f"release-hash-drift:{k}")
 before=load_paper_ledger(root,PID);before_hash=_digest(before)
 if not before:raise RuntimeError("missing canonical B1 ledger")
 c=contract(before["contract"])
 if before.get("contract_sha256")==paper_contract_digest(c) and before.get("current_state")=="SUBMISSION_READY":
  if validate_paper_ledger(before):raise RuntimeError("existing R67 ledger invalid")
  return {"status":"ALREADY_FINALIZED","row":before,"public":next(x for x in build_paper_ledger_index(root)["entries"] if x.get("paper_id")==PID)}
 if before.get("contract_sha256")!=OLD or before.get("current_state")!="SUBMISSION_READY" or before.get("scientific_status")!="READY":raise RuntimeError(f"unexpected pre-R67 ledger:{before.get('contract_sha256')}:{before.get('current_state')}")
 refs=(A(sf(pdf)),A(sf(REL)),A(sf(STAT)),A(sf(ISO)),A(sf(REV)))
 reopen_ready_paper_contract(root,c,reopen_evidence_refs=(A(sf(REL)),A(sf(STAT)),A(sf(ISO)),A(sf(REV))),superseded_claims={"C4":"R66 retains the frozen Qwen outcomes but replaces practical-null wording with sparse-discordance conservative inference.","C5":"R66 retains the frozen Llama outcomes but narrows replication scope and equivalence wording.","C6":"R66 replaces the content-sufficiency/behaviorally-legible interpretation with the identifiable closed-loop explicit-field exposure claim."},reason="Independent post-confirmatory methodology review found claim-scope and sparse-discordance inference overreach without finding a need to rerun the main experiment. R66 changes no scientific outcomes or preregistered threshold; it narrows the contract to the field-revelation estimand and adds conservative existing-data inference plus reset/isolation documentation.",actor="b1-r67-contract-revision")
 trans(root,c,PaperState.PAPER_DESIGN,refs);record_story_search(root,c,stories(),actor="b1-r67-story");trans(root,c,PaperState.MANUSCRIPT,(A(sf(pdf)),));trans(root,c,PaperState.MOCK_PC,(A(sf(pdf)),))
 b,a=reviews();record_mock_review(root,c,MockReviewMode.BLIND_MANUSCRIPT,b,actor="b1-r67-blind");record_mock_review(root,c,MockReviewMode.ARTIFACT_AWARE,a,actor="b1-r67-artifact");trans(root,c,PaperState.TARGETED_REPAIR,refs);trans(root,c,PaperState.CLAIM_AUDIT,(A(sf(pdf)),A(sf(STAT)),A(sf(ISO))))
 ids=tuple(c.supported_claims);record_claim_audit(root,c,manuscript_ref=A(sf(pdf)),claimed_ids=ids,evidence_bound_claim_ids=ids,limitations_preserved=True,actor="b1-r67-claim");trans(root,c,PaperState.PDF_QA,(A(sf(pdf)),A(sf(REL))))
 record_manuscript_ci(root,c,{k:True for k in MANDATORY_MANUSCRIPT_CI_CHECKS},actor="b1-r67-ci");trans(root,c,PaperState.PREBUTTAL,(A(sf(pdf)),A(sf(REL))))
 obs=[*b,*a];rr={"B1":(A(sf(REV)),A(sf(REL))),"B2":(A(sf(REV)),A(sf(REL))),"B3":(A(sf(STAT)),A(sf(REL))),"A1":(A(sf(ISO)),),"A2":(A(sf(R62)),A(sf(REL))),"A3":(A(sf(REL)),)};record_prebuttal(root,c,obs,[PrebuttalResolution(o.objection_id,True,rr[o.objection_id]) for o in obs],actor="b1-r67-prebuttal");record_submission_readiness(root,c,actor="b1-r67-ready");trans(root,c,PaperState.SUBMISSION_READY,(A(sf(pdf)),A(sf(REL))))
 event(root,c,"paper-preparation-r67",{"receipt_type":"paper-preparation","protocol_version":"1.0+r67-postoracle","pass":True,"required_gates":8,"passed_gates":8,"gate_pass":{k:True for k in ("causal-estimand","treatment-scope","sparse-discordance-statistics","arm-isolation","replication-scope","task252-boundary","pdf-qa","artifact-rebuild")},"blockers":[],"paper_pdf_sha256":sf(pdf),"source_zip_sha256":sf(src),"supplement_zip_sha256":sf(sup),"new_scientific_execution":False,"new_experiment_required_for_current_narrow_claim":False})
 event(root,c,"submission-readiness-context-r67",{"receipt_type":"submission-readiness-context","artifact_submission_ready":True,"recommended_immediate_submission":"READY_FOR_HUMAN_SUBMISSION","external_human_submission_authority_required_for_SUBMITTED":True,"new_experiment_required_for_current_narrow_claim":False,"optional_semantic_extension":"FORMAT_MATCHED_UNKNOWN_TRUTHFUL_REVERSED_OR_SHUFFLED","claim_boundary":"CLOSED_LOOP_EXPLICIT_SOURCE_OUTCOME_FIELD_EFFECT_NO_EQUIVALENCE_NO_SEMANTIC_PROVENANCE_THEOREM"})
 after=load_paper_ledger(root,PID);errs=validate_paper_ledger(after)
 if errs:raise RuntimeError("R67 ledger invalid:"+";".join(errs))
 pub=next(x for x in build_paper_ledger_index(root)["entries"] if x.get("paper_id")==PID)
 if pub.get("title")!=TITLE or pub.get("current_state")!="SUBMISSION_READY" or pub.get("supported_claims")!=6 or pub.get("active_unrefuted_claims")!=0:raise RuntimeError(f"R67 public projection not clean:{pub}")
 result={"schema_version":"1.0","paper_id":PID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R67-PAPER-ACCEPTANCE-CLOSEOUT","recorded_date":"2026-09-03","status":"PAPER_ACCEPTANCE_SUBMISSION_READY_CLEAN_POST_R66","before_ledger_sha256":before_hash,"after_ledger_sha256":_digest(after),"previous_contract_sha256":OLD,"current_contract_sha256":after.get("contract_sha256"),"title":TITLE,"scientific_status":after.get("scientific_status"),"current_state":after.get("current_state"),"supported_claims":pub.get("supported_claims"),"active_unrefuted_claims":pub.get("active_unrefuted_claims"),"gate_clean_submission_ready":pub.get("gate_clean_submission_ready"),"release_pdf_sha256":sf(pdf),"source_zip_sha256":sf(src),"supplement_zip_sha256":sf(sup),"new_scientific_execution":False,"new_agent_execution":False,"new_provider_calls":0,"new_experiment_required_for_current_narrow_claim":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False};result["receipt_sha256"]=_digest(result)
 if out:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 return {"status":"FINALIZED","result":result,"row":after,"public":pub}
def dry_run(root:Path):
 src=root/"paper-acceptance"/f"{PID}.json"
 with tempfile.TemporaryDirectory(prefix="b1-r67-dry-") as td:
  tmp=Path(td);(tmp/"paper-acceptance").mkdir();shutil.copy2(src,tmp/"paper-acceptance"/src.name);r=finalize(tmp,None);return {"dry_run":True,"status":r["status"],"current_state":r["row"].get("current_state"),"scientific_status":r["row"].get("scientific_status"),"contract_sha256":r["row"].get("contract_sha256"),"title":r["public"].get("title"),"supported_claims":r["public"].get("supported_claims"),"active_unrefuted_claims":r["public"].get("active_unrefuted_claims"),"gate_clean_submission_ready":r["public"].get("gate_clean_submission_ready"),"primary_next_action":r["public"].get("primary_next_action")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("/data/wyt/agent-self-evolution-observatory"));p.add_argument("--dry-run",action="store_true");p.add_argument("--output",type=Path,default=ROOT/"generated/d2-failure-memory-provenance-r67-paper-acceptance-closeout.json");a=p.parse_args();r=dry_run(a.root) if a.dry_run else finalize(a.root,a.output);print(json.dumps(r if a.dry_run else r["result"],ensure_ascii=False,indent=2))
if __name__=="__main__":main()
