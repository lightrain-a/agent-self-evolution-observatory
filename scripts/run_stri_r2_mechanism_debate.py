from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, ArkResponseStateError
from research_pipeline.config import load_env_file

CANON_ENV = Path('/home/wyt/code/agent-self-evolution-observatory/.env')
BODY = ROOT / 'paper_drafts/stri-20260816-narrow-body.tex'
TABLES = ROOT / 'paper_drafts/stri-20260816-tables.tex'
R19_STOP = ROOT / 'generated/asset-first-stri-autoskill-multitask-pilot-closure-r19-20260824.json'
P19 = ROOT / 'generated/asset-first-stri-autoskill-p19-stage3-result-20260819.json'
MEDIATOR = ROOT / 'generated/asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json'
OLD_DS = ROOT / 'generated/stri-r3-independent-review-20260819/deepseek-post-isolation.json'
OLD_KIMI = ROOT / 'generated/stri-r3-independent-review-20260819/kimi.json'
OUT = ROOT / 'generated/stri-r2-mechanism-redesign-debate-20260825'
PACKET = ROOT / 'generated/asset-first-stri-r2-mechanism-redesign-packet-20260825.json'

MODELS = {
    'architect': 'kimi-k3',
    'critic': 'deepseek-v4-pro',
    'synthesizer': 'kimi-k3',
    'adjudicator': 'deepseek-v4-pro',
}

ICLR_ANALOGUES = [
    {
        'title': 'GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models',
        'venue': 'ICLR 2025 Poster',
        'source': 'https://openreview.net/forum?id=AjXkRZIvjB',
        'mechanism_template': 'Hold the underlying reasoning task template fixed and perturb superficial instantiation/clauses; use controlled counterfactual variants to expose fragility that aggregate benchmark accuracy hides.',
        'closure_pattern': 'measurement anomaly -> semantics-preserving perturbation -> systematic failure -> revised scientific interpretation of what benchmark success means.',
    },
    {
        'title': 'Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Parameters for Reasoning',
        'venue': 'ICLR 2025 Oral',
        'source': 'https://openreview.net/forum?id=4FWAwZtd2n',
        'mechanism_template': 'Decompose test-time scaling into two mechanisms; identify prompt difficulty as the conditioning variable that changes which compute strategy is effective; derive an adaptive compute allocation policy.',
        'closure_pattern': 'heterogeneous phenomenon -> latent conditioning variable -> mechanism-specific scaling curves -> adaptive intervention -> FLOPs-matched consequence.',
    },
    {
        'title': 'Representation Shattering in Transformers: A Synthetic Study with Knowledge Editing',
        'venue': 'ICLR 2025 submission / mechanistic analysis reference',
        'source': 'https://openreview.net/forum?id=MjFoQAhnl3',
        'mechanism_template': 'Propose a precise latent failure mechanism (editing distorts structured representations beyond the target), construct a synthetic environment where the structure is identifiable, measure representation distortion, and reproduce the phenomenon in pretrained models.',
        'closure_pattern': 'downstream failure -> latent representation hypothesis -> identifiable synthetic substrate -> internal measurement -> naturalistic corroboration.',
    },
    {
        'title': 'The Buffer Mechanism for Multi-Step Information Reasoning in Language Models',
        'venue': 'ICLR 2025 submission / mechanism reference',
        'source': 'https://openreview.net/forum?id=5Ky0W6sp8W',
        'mechanism_template': 'Define an internal mechanism, build a controlled symbolic task exposing its predicted behavior, connect the mechanism to model components, then intervene algorithmically and measure training/generalization consequences.',
        'closure_pattern': 'mechanistic hypothesis -> controlled substrate -> component-level evidence -> targeted algorithmic intervention -> measurable gain.',
    },
]

CURRENT_DIAGNOSIS = {
    'current_object': 'Skill-Taxonomy Representation Invariance (STRI)',
    'current_formal_core': 'support matrix A, package mass w, representation-independent target q, and R*(A;q) as exact package-support-cone realizability / worst-case distortion certificate',
    'current_strength': 'exact clone quotient theorem; support-geometry certificate; multiple positive/negative support regimes; extensive robustness/baselines; bounded AutoSkill representation->retrieval->behavior existence proof',
    'current_weakness': 'the main causal chain is still largely representation->selection/exposure/retrieval. Calling it a self-evolution mechanism would be overreach unless identity is shown to enter the persistent update loop and change future state.',
    'candidate_upgrade': 'Representation-Induced Evolution Drift / Evolutionary Control Geometry: skill taxonomy is a control coordinate system for persistent self-evolution, not harmless metadata.',
    'candidate_chain': 'semantics-preserving identity perturbation -> control-coordinate change -> update/reward/write/mutation allocation -> future persistent state divergence -> optional downstream behavioral divergence',
    'candidate_intervention': 'quotient evolution operator: aggregate update/control mass at semantic-equivalence-class level before redistributing to package identities; compare against package-ID-native evolution under identical task stream/information/budget.',
    'critical_guardrail': 'R19 showed 9/9 retrieval sensitivity but a preregistered two-unit behavior pilot failed its split-specific action-signature gate. Any R2 story must preserve this STOP and cannot claim task-general behavioral propagation.',
}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def build_packet() -> dict:
    body = BODY.read_text(encoding='utf-8')
    tables = TABLES.read_text(encoding='utf-8')
    packet = {
        'schema_version': '1.0',
        'paper_id': 'E1.STRI',
        'purpose': 'Zero-authority mechanism-redesign consultation before any new R2 experiment.',
        'current_manuscript_sha256': hashlib.sha256(body.encode()).hexdigest(),
        'current_tables_sha256': hashlib.sha256(tables.encode()).hexdigest(),
        'current_diagnosis': CURRENT_DIAGNOSIS,
        'iclr_mechanism_analogues': ICLR_ANALOGUES,
        'r19_heldout_stop': load(R19_STOP),
        'p19_bounded_result': load(P19),
        'p19_mediator_result': load(MEDIATOR),
        'previous_deepseek_review': load(OLD_DS).get('review', {}),
        'previous_kimi_review': load(OLD_KIMI).get('review', {}),
        'manuscript_body_tex': body,
        'manuscript_tables_tex': tables,
        'constraints': {
            'no_task_utility_claim_without_new_evidence': True,
            'no_population_safety_claim': True,
            'no_task_general_behavior_claim_after_r19_stop': True,
            'semantic_first_currently_constructive_not_validated_repair': True,
            'r_star_is_not_solver_novelty': True,
            'consultation_has_no_scientific_experiment_gpu_or_submission_authority': True,
            'new_experiment_must_be_frozen_before_outcomes_and_have_explicit_stop_gate': True,
        },
        'scientific_authority': False,
    }
    canonical = json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packet['packet_sha256'] = hashlib.sha256(canonical).hexdigest()
    PACKET.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return packet


def tool_schema(role: str) -> list[dict]:
    if role == 'architect':
        props = {
            'diagnosis_current_story': {'type':'string'},
            'latent_scientific_object': {'type':'string'},
            'why_this_is_deeper_than_current_stri': {'type':'string'},
            'mechanism_chain': {'type':'array','items':{'type':'string'}},
            'formal_objects': {'type':'array','items':{'type':'object','properties':{
                'symbol':{'type':'string'},'meaning':{'type':'string'},'why_needed':{'type':'string'}},'required':['symbol','meaning','why_needed'],'additionalProperties':False}},
            'candidate_designs': {'type':'array','minItems':2,'maxItems':2,'items':{'type':'object','properties':{
                'name':{'type':'string'},'scientific_object':{'type':'string'},'changed_assumption':{'type':'string'},
                'mechanism':{'type':'string'},'decisive_intervention':{'type':'string'},'minimal_experiment':{'type':'string'},
                'theoretical_result_needed':{'type':'string'},'existing_evidence_reused':{'type':'array','items':{'type':'string'}},
                'falsifier':{'type':'string'},'main_risk':{'type':'string'}},
                'required':['name','scientific_object','changed_assumption','mechanism','decisive_intervention','minimal_experiment','theoretical_result_needed','existing_evidence_reused','falsifier','main_risk'],'additionalProperties':False}},
            'recommended_design': {'type':'string'},
            'what_to_demote_or_remove': {'type':'array','items':{'type':'string'}},
            'what_not_to_do': {'type':'array','items':{'type':'string'}},
            'minimum_closed_loop': {'type':'string'},
            'advisory_verdict': {'type':'string','enum':['REDESIGN_PROMISING','CURRENT_STORY_PREFERABLE','STOP_REDIRECTION']},
        }
    elif role == 'critic':
        props = {
            'current_stri_score_1_to_10': {'type':'integer','minimum':1,'maximum':10},
            'redesign_ceiling_score_1_to_10': {'type':'integer','minimum':1,'maximum':10},
            'is_evolution_drift_merely_a_rename': {'type':'boolean'},
            'strongest_reduction_attack': {'type':'string'},
            'closest_conceptual_collision': {'type':'string'},
            'missing_latent_variable_or_intervention': {'type':'string'},
            'candidate_critiques': {'type':'array','items':{'type':'object','properties':{
                'name':{'type':'string'},'depth':{'type':'string'},'fatal_or_major_issue':{'type':'string'},'repair':{'type':'string'}},
                'required':['name','depth','fatal_or_major_issue','repair'],'additionalProperties':False}},
            'required_causal_chain_for_iclr_mechanism_claim': {'type':'array','items':{'type':'string'}},
            'minimum_evidence_for_evolution_drift_title': {'type':'array','items':{'type':'string'}},
            'what_is_already_sufficient': {'type':'array','items':{'type':'string'}},
            'what_should_be_demoted': {'type':'array','items':{'type':'string'}},
            'forbidden_overclaims': {'type':'array','items':{'type':'string'}},
            'single_highest_value_next_action': {'type':'string'},
            'advisory_verdict': {'type':'string','enum':['GO_REDESIGN_GATE','REVISE_REDESIGN','KEEP_CURRENT_STRI','STOP']},
        }
    elif role == 'synthesizer':
        props = {
            'final_scientific_object': {'type':'string'},
            'one_sentence_insight': {'type':'string'},
            'why_not_just_retrieval_bias': {'type':'string'},
            'formal_model': {'type':'array','items':{'type':'object','properties':{
                'equation_or_definition':{'type':'string'},'interpretation':{'type':'string'},'testable_prediction':{'type':'string'}},
                'required':['equation_or_definition','interpretation','testable_prediction'],'additionalProperties':False}},
            'causal_graph': {'type':'array','items':{'type':'string'}},
            'intervention_matrix': {'type':'array','items':{'type':'object','properties':{
                'arm':{'type':'string'},'representation':{'type':'string'},'retrieval_control':{'type':'string'},'update_control':{'type':'string'},'purpose':{'type':'string'}},
                'required':['arm','representation','retrieval_control','update_control','purpose'],'additionalProperties':False}},
            'minimal_pilot': {'type':'object','properties':{
                'unit_of_analysis':{'type':'string'},'steps':{'type':'integer'},'primary_endpoint':{'type':'string'},
                'secondary_endpoints':{'type':'array','items':{'type':'string'}},'pass_gate':{'type':'string'},'stop_gate':{'type':'string'},
                'why_outcome_blind_selection_is_possible':{'type':'string'}},
                'required':['unit_of_analysis','steps','primary_endpoint','secondary_endpoints','pass_gate','stop_gate','why_outcome_blind_selection_is_possible'],'additionalProperties':False},
            'theory_upgrade': {'type':'string'},
            'paper_story_6_steps': {'type':'array','minItems':6,'maxItems':6,'items':{'type':'string'}},
            'existing_evidence_keep': {'type':'array','items':{'type':'string'}},
            'existing_evidence_demote': {'type':'array','items':{'type':'string'}},
            'title_candidates': {'type':'array','items':{'type':'string'}},
            'claim_boundaries': {'type':'array','items':{'type':'string'}},
            'advisory_verdict': {'type':'string','enum':['READY_FOR_FROZEN_PILOT_DESIGN','NEEDS_MORE_THEORY_FIRST','KEEP_CURRENT_PAPER']},
        }
    else:
        props = {
            'materially_deeper_than_r19': {'type':'boolean'},
            'why_or_why_not': {'type':'string'},
            'remaining_reduction_attack': {'type':'string'},
            'formalism_depth_assessment': {'type':'string'},
            'intervention_identifiability_assessment': {'type':'string'},
            'minimal_pilot_is_decisive': {'type':'boolean'},
            'pilot_failure_would_mean': {'type':'string'},
            'pilot_success_would_mean': {'type':'string'},
            'paper_rewrite_before_pilot_authorized_advisory': {'type':'boolean'},
            'exact_missing_evidence_before_evolution_drift_claim': {'type':'array','items':{'type':'string'}},
            'highest_value_falsifier': {'type':'string'},
            'expected_iclr_position_if_pilot_passes': {'type':'string'},
            'expected_iclr_position_if_pilot_fails': {'type':'string'},
            'advisory_verdict': {'type':'string','enum':['GO_FROZEN_PILOT_DESIGN','REVISE_THEORY','KEEP_R19','STOP_REDESIGN']},
        }
    return [{'type':'function','name':'submit_redesign_review','description':'Return the structured zero-authority redesign assessment.','parameters':{
        'type':'object','properties':{'review':{'type':'object','properties':props,'required':list(props),'additionalProperties':False}},
        'required':['review'],'additionalProperties':False}}]


def role_instruction(role: str) -> str:
    base = '''You are participating in a zero-authority scientific redesign debate for an ICLR-targeted paper. Do not reward added terminology, equations, or experiment count by themselves. The redesign is useful only if it identifies a genuinely new latent scientific object, makes an ex-ante prediction the current STRI story does not already make, and supports a decisive intervention. Preserve the R19 negative held-out pilot and all stated claim boundaries. You cannot authorize experiments, GPU, submission, or scientific claims. Return exactly one submit_redesign_review function call.'''
    if role == 'architect':
        return base + '''\nAct as Kimi, a mechanism theorist. Build at most two materially distinct redesigns. Seek a compact but deep mechanism, not an engineering stack. Explicitly decide whether "representation-induced evolution drift" is real scientific progress or a relabeling of retrieval bias. Your formalism should make a new falsifiable prediction about persistent update dynamics and should specify the smallest intervention that could kill the idea.'''
    if role == 'critic':
        return base + '''\nAct as DeepSeek, a strict ICLR area-chair style critic. Attack the architect's proposal. Try to reduce it to known routing/retrieval bias, duplicated-action symmetry, state aggregation, mixture-of-experts gating, or ordinary nonstationary learning. Demand a causal chain with a persistent-state intervention if the paper uses "self-evolution" language. Rank substance over mathematical ornamentation.'''
    if role == 'synthesizer':
        return base + '''\nAct as Kimi again after round 1. A fresh DeepSeek R2 critique could not be obtained because the provider returned a non-voting subscription support failure; therefore use the packet's archived independent DeepSeek review only as a historical reviewer vector, together with the supplied ICLR mechanism templates. Do not describe that archived review as a fresh R2 vote. Produce one repaired design only. It must connect a persistent update operator to a semantics-preserving identity intervention, define a measurable trajectory-level latent variable, specify controls separating retrieval from update allocation, and include a hard pilot STOP. Use existing R19 evidence only where logically inherited.'''
    return base + '''\nAct as DeepSeek for final adjudication. Judge the synthesized design against the current R19 story and the supplied ICLR mechanism templates. Decide whether the redesign is materially deeper, whether the proposed pilot is actually identifying a new mechanism rather than restating retrieval bias, and what result would force the project back to R19.'''


def previous_payload(role: str) -> dict:
    out = {}
    if role in {'critic','synthesizer','adjudicator'}:
        p = OUT / 'round1-kimi-architect.json'
        if p.exists(): out['round1_kimi_architect'] = load(p).get('review')
    if role in {'synthesizer','adjudicator'}:
        p = OUT / 'round2-deepseek-critic.json'
        if p.exists(): out['round2_deepseek_critic'] = load(p).get('review')
    if role == 'adjudicator':
        p = OUT / 'round3-kimi-synthesis.json'
        if p.exists(): out['round3_kimi_synthesis'] = load(p).get('review')
    return out


def target_for(role: str) -> Path:
    names = {
        'architect':'round1-kimi-architect.json',
        'critic':'round2-deepseek-critic.json',
        'synthesizer':'round3-kimi-synthesis.json',
        'adjudicator':'round4-deepseek-adjudication.json',
    }
    return OUT / names[role]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--role', choices=list(MODELS), required=True)
    args = ap.parse_args()
    role = args.role
    packet = build_packet()
    context = {
        'redesign_packet': packet,
        'prior_debate_rounds': previous_payload(role),
    }
    prompt = role_instruction(role) + '\n\nDEBATE PACKET:\n' + json.dumps(context, ensure_ascii=False)
    prompt_sha = hashlib.sha256(prompt.encode()).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    target = target_for(role)
    if target.exists():
        raise RuntimeError(f'refuse overwrite existing debate round: {target}')
    load_env_file(CANON_ENV)
    key = os.environ.get('ARK_API_KEY','').strip()
    if not key:
        raise RuntimeError('ARK_API_KEY missing after canonical env load')
    settings = ArkSettings(api_key=key, base_url=os.environ.get('ARK_BASE_URL','https://ark.cn-beijing.volces.com/api/plan/v3').rstrip('/'), default_model=MODELS[role], timeout_seconds=300.0, max_retries=0)
    client = ArkResponsesClient(settings)
    try:
        resp = client.respond(prompt, model=MODELS[role], max_output_tokens=7500, tools=tool_schema(role), thinking='disabled', store=True, allow_thinking_compatibility_fallback=True)
        calls = [c for c in resp.get('function_calls') or [] if c.get('name') == 'submit_redesign_review']
        if len(calls) != 1:
            raise RuntimeError(f'expected one function call, got {len(calls)}')
        review = json.loads(calls[0].get('arguments') or '{}').get('review') or {}
        payload = {
            'schema_version':'1.0','paper_id':'E1.STRI','role':role,'round':{'architect':1,'critic':2,'synthesizer':3,'adjudicator':4}[role],
            'requested_model':MODELS[role],'resolved_model':resp.get('resolved_model'),'response_id':resp.get('response_id'),'status':resp.get('status'),
            'usage':resp.get('usage') or {},'packet_sha256':packet['packet_sha256'],'prompt_sha256':prompt_sha,'review':review,
            'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False,
        }
        payload['receipt_sha256'] = hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':'SUCCESS','role':role,'resolved_model':payload['resolved_model'],'receipt_sha256':payload['receipt_sha256'],'review':review},ensure_ascii=False))
        return 0
    except ArkResponseStateError as exc:
        payload={'schema_version':'1.0','paper_id':'E1.STRI','role':role,'status':'NONVOTING_PROVIDER_STATE_FAILURE','packet_sha256':packet['packet_sha256'],'prompt_sha256':prompt_sha,'provider_receipt':exc.receipt(),'scientific_authority':False}
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(payload,ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
