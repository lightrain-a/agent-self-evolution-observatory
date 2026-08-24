#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ADJ=ROOT/'generated/temporal-skill-extension-adjudication-20260824.json'
TEX=ROOT/'paper_drafts/e2-temporal-skill-r16-20260824/sections/07_appendix.tex'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=json.loads(ADJ.read_text());t=TEX.read_text()
 checks=[
 ('C01',a['routing']['current_paper_main_claim_change'].startswith('NO'),'R15 core attribution claim is not replaced by extension outcomes.'),
 ('C02','mechanism-agnostic evidence organizer' in t and 'filtering by release date' in t,'Benign B is defined as useful but forbidden from executing the target temporal mechanism.'),
 ('C03','EIA WPSR ($n=4$)' in t and '.375 & 1.000 & 1.000' in t,'Fresh EIA N/B/T endpoint-mean result is exposed.'),
 ('C04','BLS CPI ($n=4$)' in t and '.375 & .750 & 1.000' in t,'BLS cross-domain N/B/T endpoint-mean result is exposed.'),
 ('C05','Repeats are averaged within endpoint' in t,'Execution repeats are not promoted to independent scientific units.'),
 ('C06','TOOL is actually invoked on 2/4 endpoints' in t and 'TOOL--CONTEXT is zero on every endpoint' in t,'Actual multi-turn tool-use null is visible with endogenous call rate.'),
 ('C07','not a pure placement estimand' in t,'Multi-turn TOOL-vs-CONTEXT is not overclaimed as pure placement identification.'),
 ('C08','These observations motivated, but do not confirm' in t,'EIA/BLS planning gains are labeled exploratory/data-induced.'),
 ('C09','Single-turn N succeeds on 1/4 endpoints and planning-only also succeeds on 1/4' in t,'Prospectively frozen Fed planning falsifier is exposed.'),
 ('C10','one win, N has one win, and two endpoints tie' in t and 'mean difference zero' in t,'Fed paired null is reported rather than hidden.'),
 ('C11','We therefore \\emph{stop} the proposed planning/deliberation paper direction' in t,'Failed next-paper candidate is explicitly stopped.'),
 ('C12','not retroactively described as preregistered evidence' in t,'Follow-up evidence is not retroactively inserted into the primary preregistration.'),
 ('C13','R14' not in t and 'R15' not in t and 'Stanford' not in t and 'Research OS' not in t,'Anonymous manuscript does not expose internal revision/reviewer workflow.'),
 ]
 payload={'schema_version':'1.0','receipt_type':'temporal-r16-extension-claim-audit','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r16','checks':[{'id':i,'pass':bool(p),'check':d} for i,p,d in checks],'summary':{'checks':len(checks),'passed':sum(bool(p) for _,p,_ in checks),'failed':sum(not bool(p) for _,p,_ in checks)},'adjudication_sha256':sha(ADJ),'appendix_sha256':sha(TEX),'new_model_calls_for_r16_paper_repair':0,'new_provider_calls_for_r16_paper_repair':0,'scientific_authority':False,'submission_authority':False};payload['summary']['pass']=payload['summary']['failed']==0
 out=ROOT/'generated/temporal-skill-r16-extension-claim-audit-20260824.json';out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print(json.dumps(payload,ensure_ascii=False,indent=2));
 if not payload['summary']['pass']:raise SystemExit('R16 extension claim audit failed')
if __name__=='__main__':main()
