from __future__ import annotations
import argparse,hashlib,json,pathlib
from research_pipeline.ark_provider import ArkResponsesClient,extract_json_object

MODEL='deepseek-v4-flash'
EXPERIMENT_ID='STRI-SKILLRL-FINAL-POLICY-COMPETENCY-P0E-20260816'
CHECKS=(
 'independent_truth','competence_gate_nonadaptive','substrate_change_principled',
 'model_merge_provenance_valid','task_partition_outcome_blind','treatment_placebo_identifiable',
 'stochastic_control_valid','statistics_valid','anti_bake_in','claim_boundary_valid')

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:pathlib.Path):return json.loads(p.read_text(encoding='utf-8'))

def prompt(contract:dict,panel:dict,manifest:dict,dead_end:dict)->str:
 return f'''You are an independent scientific contract reviewer. You did not design this experiment.
This review is advisory and cannot authorize paper claims, methods, full experiments, or GPU by itself.
Review only the frozen bounded P0-E contract below. The previous P0-D result was INCONCLUSIVE because the SFT warm-start had final-success support 1/24; it must NOT be treated as a negative STRI result. P0-E changes exactly one scientific substrate: the single author-released final RL policy, and first runs a disjoint competence gate before any causal B/C/D intervention.

Return ONLY one JSON object with exactly:
{{
 "verdict":"CLEAR_FOR_BOUNDED_EXECUTION"|"REVISE"|"BLOCK",
 "confidence":"high"|"medium"|"low",
 "checks":{{{','.join(json.dumps(k)+':true|false' for k in CHECKS)}}},
 "reason":"...",
 "required_revision":"...",
 "claim_if_calibration_go":"...",
 "claim_if_calibration_stop":"...",
 "claim_if_causal_go":"...",
 "claim_if_causal_stop":"..."
}}

Be strict about: (1) support/positivity is a qualification prerequisite rather than post-hoc rescue; (2) calibration/local/confirmation task partitions are disjoint and outcome-blind; (3) failure of competence calibration forbids alternative model/checkpoint/task search; (4) A/D stochastic coupling is legitimate only after byte-identical prompt verification, while B/C remain independent; (5) final success/won is independent truth; (6) author final RL policy is a principled substrate change from the failed warm-start; (7) model merge provenance is pre-outcome and pinned; (8) GO/STOP thresholds were frozen before P0-E outcomes; (9) exact-clone evidence cannot establish SQC superiority or partial-overlap novelty. If any check is false, verdict cannot be CLEAR. Output consistency is mandatory: use REVISE only when you can name a concrete actionable required_revision (and at least one relevant check should be false); if all checks are true and no concrete revision is required, verdict MUST be CLEAR_FOR_BOUNDED_EXECUTION and required_revision MUST be the empty string "". Do not write "None", "N/A", or similar placeholders.

CONTRACT:
{json.dumps(contract,ensure_ascii=False,indent=2)}

PANEL:
{json.dumps(panel,ensure_ascii=False,indent=2)}

PRE-OUTCOME MODEL MANIFEST:
{json.dumps(manifest,ensure_ascii=False,indent=2)}

P0-D PRINCIPLED DEAD-END:
{json.dumps(dead_end,ensure_ascii=False,indent=2)}'''

def run(project:pathlib.Path,output:pathlib.Path,raw_path:pathlib.Path)->dict:
 g=project/'generated';cp=g/'asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json';pp=g/'asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json';mp=g/'asset-first-stri-skillrl-final-policy-p0e-model-manifest-20260816.json';dp=g/'asset-first-stri-skillrl-p0d-dead-end-diagnosis-20260816.json'
 contract,panel,manifest,dead=map(load,(cp,pp,mp,dp))
 if contract.get('status')!='FROZEN_FOR_BOUNDED_EXECUTION_REVIEW':raise ValueError('contract-not-final-frozen-for-review')
 client=ArkResponsesClient();res=client.respond(prompt(contract,panel,manifest,dead),model=MODEL,max_output_tokens=5000,temperature=0.0,thinking='disabled')
 raw=str(res.get('text') or '');raw_path.parent.mkdir(parents=True,exist_ok=True);raw_path.write_text(raw+'\n',encoding='utf-8');payload=extract_json_object(raw);checks=payload.get('checks') or {};all_checks=all(checks.get(k) is True for k in CHECKS);verdict=str(payload.get('verdict') or '')
 compiled={'schema_version':'1.0','candidate_id':'skill-taxonomy-representation-invariance','experiment_id':EXPERIMENT_ID,'artifact_kind':'independent-scientific-contract-review','reviewed_contract_sha256':sha(cp),'reviewed_panel_sha256':sha(pp),'reviewed_model_manifest_sha256':sha(mp),'reviewed_dead_end_sha256':sha(dp),'verdict':'CLEAR_FOR_BOUNDED_EXECUTION' if verdict=='CLEAR_FOR_BOUNDED_EXECUTION' and all_checks and not str(payload.get('required_revision') or '').strip() else ('BLOCK' if verdict=='BLOCK' else 'REVISE'),'confidence':payload.get('confidence'),'checks':{k:checks.get(k) is True for k in CHECKS},'reason':str(payload.get('reason') or ''),'required_revision':str(payload.get('required_revision') or ''),'claim_if_calibration_go':str(payload.get('claim_if_calibration_go') or ''),'claim_if_calibration_stop':str(payload.get('claim_if_calibration_stop') or ''),'claim_if_causal_go':str(payload.get('claim_if_causal_go') or ''),'claim_if_causal_stop':str(payload.get('claim_if_causal_stop') or ''),'reviewer_requested_model':MODEL,'reviewer_model':str(res.get('resolved_model') or MODEL),'raw_path':str(raw_path),'raw_sha256':sha(raw_path),'scientific_authority':False,'authority':{'paper_novelty':False,'method':False,'full_experiment':False,'gpu':False}}
 output.write_text(json.dumps(compiled,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return compiled

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=pathlib.Path,default=pathlib.Path('.'));ap.add_argument('--output',type=pathlib.Path,default=pathlib.Path('generated/asset-first-stri-skillrl-final-policy-p0e-review-20260816.json'));ap.add_argument('--raw',type=pathlib.Path,default=pathlib.Path('generated/research-data/runs/stri-skillrl-final-policy-p0e-review-20260816/deepseek-v4-flash.raw.txt'));a=ap.parse_args();print(json.dumps(run(a.project,a.output,a.raw),ensure_ascii=False))
if __name__=='__main__':main()
