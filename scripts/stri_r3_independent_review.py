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
RESULT = ROOT / 'generated/asset-first-stri-autoskill-p19-stage3-result-20260819.json'
MEDIATOR_RESULT = ROOT / 'generated/asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json'
OUTDIR = ROOT / 'generated/stri-r3-independent-review-20260819'

MODELS = {'deepseek': 'deepseek-v4-pro', 'kimi': 'kimi-k3'}


def schema(role: str) -> list[dict]:
    common = {
        'summary': {'type': 'string'},
        'strengths': {'type': 'array', 'items': {'type': 'string'}},
        'weaknesses': {'type': 'array', 'items': {'type': 'string'}},
        'remaining_high_risk': {'type': 'array', 'items': {'type': 'string'}},
        'claim_boundary_violations': {'type': 'array', 'items': {'type': 'string'}},
        'highest_value_next_action': {'type': 'string'},
    }
    if role == 'deepseek':
        props = {
            **common,
            'recommendation': {'type': 'string', 'enum': ['strong_reject','reject','weak_reject','borderline','weak_accept','accept','strong_accept']},
            'score_1_to_10': {'type': 'integer', 'minimum': 1, 'maximum': 10},
            'confidence_1_to_5': {'type': 'integer', 'minimum': 1, 'maximum': 5},
            'correctness': {'type': 'string'},
            'novelty': {'type': 'string'},
            'significance': {'type': 'string'},
            'empirical_sufficiency': {'type': 'string'},
            'autoskill_closes_old_significance_gap': {'type': 'string', 'enum': ['no','partially','substantially']},
            'submission_advice': {'type': 'string', 'enum': ['freeze','minor_revision','major_revision','new_experiment']},
            'fatal_flaws': {'type': 'array', 'items': {'type': 'string'}},
        }
    else:
        props = {
            **common,
            'evidence_chain_valid': {'type': 'boolean'},
            'strongest_alternative_explanation': {'type': 'string'},
            'id_placebo_assessment': {'type': 'string'},
            'quotient_control_assessment': {'type': 'string'},
            'single_substrate_limit': {'type': 'string'},
            'significance_effect': {'type': 'string', 'enum': ['none','small','material','large']},
            'extra_experiment_needed_before_submission': {'type': 'boolean'},
            'what_would_change_view': {'type': 'string'},
            'manuscript_positioning': {'type': 'string'},
            'evidence_blockers': {'type': 'array', 'items': {'type': 'string'}},
            'advisory_verdict': {'type': 'string', 'enum': ['stop','hold','revise','freeze']},
        }
    return [{
        'type': 'function',
        'name': 'submit_review',
        'description': 'Return the independent review in the required structured form.',
        'parameters': {
            'type': 'object',
            'properties': {'review': {'type': 'object', 'properties': props, 'required': list(props), 'additionalProperties': False}},
            'required': ['review'],
            'additionalProperties': False,
        },
    }]


def prompt(role: str, body: str, tables: str, result: dict) -> str:
    if role == 'deepseek':
        instruction = '''Act as a strict independent ICLR reviewer. Review ONLY the current manuscript below. You have not seen any prior reviews or scores. Evaluate correctness, novelty, significance, empirical sufficiency, and whether the paper is actually competitive at ICLR. Be skeptical but fair. The LP/cone math may be elementary; distinguish mathematical correctness from contribution depth. The current version includes an AutoSkill P19 four-arm representation intervention plus a fresh matched mediator-isolation extension (post-checkout add-back versus matched cleanup control); assess whether this materially strengthens the causal chain and the paper's significance rather than rewarding it merely for statistical significance. Do not demand a new experiment unless the current evidence is genuinely insufficient for the stated narrow claims. Treat the manuscript's explicit claim boundaries as binding. Return one structured review by calling submit_review exactly once.'''
    else:
        instruction = '''Act as an independent evidence-design/significance critic, not a general paper scorer. You have not seen any other review. Audit the causal/evidential chain of the new AutoSkill P19 experiment and ask whether it genuinely upgrades STRI from a control-plane/specification observation to a downstream behavioral consequence. Focus on representation intervention, retrieval-set crowd-out, ID placebo, quotient control, fresh-container execution, mechanical outcome definition, single-substrate limits, and alternative explanations. Decide whether another experiment is actually necessary before submission. Do not broaden claims beyond the manuscript. Return one structured review by calling submit_review exactly once.'''
    packet = {
        'paper_body_tex': body,
        'paper_tables_tex': tables,
        'autoskill_stage3_receipt': result,
        'autoskill_mediator_isolation_v2_receipt': json.loads(MEDIATOR_RESULT.read_text(encoding='utf-8')) if MEDIATOR_RESULT.exists() else None,
    }
    return instruction + '\n\nCURRENT REVIEW PACKET:\n' + json.dumps(packet, ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--role', choices=sorted(MODELS), required=True)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    role = args.role
    model = MODELS[role]

    load_env_file(CANON_ENV)
    key = os.environ.get('ARK_API_KEY', '').strip()
    if not key:
        raise RuntimeError('ARK_API_KEY missing after canonical env load')
    settings = ArkSettings(
        api_key=key,
        base_url=os.environ.get('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/plan/v3').rstrip('/'),
        default_model=model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    body = BODY.read_text(encoding='utf-8')
    tables = TABLES.read_text(encoding='utf-8')
    result = json.loads(RESULT.read_text(encoding='utf-8'))
    mediator = json.loads(MEDIATOR_RESULT.read_text(encoding='utf-8')) if MEDIATOR_RESULT.exists() else None
    packet_hash = hashlib.sha256((body + '\n' + tables + '\n' + json.dumps(result, sort_keys=True, ensure_ascii=False) + '\n' + json.dumps(mediator, sort_keys=True, ensure_ascii=False)).encode('utf-8')).hexdigest()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    tag = args.tag.strip() or role
    target = OUTDIR / f'{tag}.json'
    if target.exists():
        raise RuntimeError(f'refuse overwrite existing review: {target}')
    try:
        resp = client.respond(
            prompt(role, body, tables, result),
            model=model,
            max_output_tokens=7000,
            tools=schema(role),
            thinking='disabled',
            store=True,
            allow_thinking_compatibility_fallback=True,
        )
        calls = [c for c in resp.get('function_calls') or [] if c.get('name') == 'submit_review']
        if len(calls) != 1:
            raise RuntimeError(f'expected exactly one submit_review call, got {len(calls)}')
        review = json.loads(calls[0].get('arguments') or '{}').get('review') or {}
        payload = {
            'schema_version': '1.0',
            'role': role,
            'requested_model': model,
            'resolved_model': resp.get('resolved_model'),
            'response_id': resp.get('response_id'),
            'status': resp.get('status'),
            'usage': resp.get('usage') or {},
            'packet_sha256': packet_hash,
            'review': review,
            'scientific_authority': False,
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': 'SUCCESS', 'role': role, 'requested_model': model, 'resolved_model': payload['resolved_model'], 'response_id': payload['response_id'], 'review': review}, ensure_ascii=False))
        return 0
    except ArkResponseStateError as e:
        payload = {'schema_version': '1.0', 'role': role, 'status': 'NONVOTING_PROVIDER_STATE_FAILURE', 'packet_sha256': packet_hash, 'provider_receipt': e.receipt(), 'scientific_authority': False}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(payload, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
