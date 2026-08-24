from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, ArkResponseStateError
from research_pipeline.config import load_env_file

HERE = Path(__file__).resolve().parent
CANON_ENV = Path('/home/wyt/code/agent-self-evolution-observatory/.env')
PDF = HERE / 'paper.pdf'
MODELS = {
    'strict': 'deepseek-v4-pro',
    'evidence': 'kimi-k3',
}


def schema(role: str) -> list[dict]:
    common = {
        'summary': {'type': 'string'},
        'strengths': {'type': 'array', 'items': {'type': 'string'}},
        'weaknesses': {'type': 'array', 'items': {'type': 'string'}},
        'remaining_high_risk': {'type': 'array', 'items': {'type': 'string'}},
        'claim_boundary_violations': {'type': 'array', 'items': {'type': 'string'}},
        'highest_value_next_action': {'type': 'string'},
    }
    if role == 'strict':
        props = {
            **common,
            'recommendation': {'type': 'string', 'enum': ['strong_reject','reject','weak_reject','borderline','weak_accept','accept','strong_accept']},
            'score_1_to_10': {'type': 'integer', 'minimum': 1, 'maximum': 10},
            'confidence_1_to_5': {'type': 'integer', 'minimum': 1, 'maximum': 5},
            'correctness': {'type': 'string'},
            'novelty': {'type': 'string'},
            'significance': {'type': 'string'},
            'empirical_sufficiency': {'type': 'string'},
            'writing_and_clarity': {'type': 'string'},
            'submission_advice': {'type': 'string', 'enum': ['freeze','minor_revision','major_revision','new_experiment']},
            'fatal_flaws': {'type': 'array', 'items': {'type': 'string'}},
        }
    else:
        props = {
            **common,
            'evidence_chain_valid': {'type': 'boolean'},
            'strongest_alternative_explanation': {'type': 'string'},
            'write_time_causality_assessment': {'type': 'string'},
            'terminal_evidence_assessment': {'type': 'string'},
            'no_memory_control_assessment': {'type': 'string'},
            'cross_writer_boundary_assessment': {'type': 'string'},
            'full_bank_reduction_assessment': {'type': 'string'},
            'extra_experiment_needed_before_submission': {'type': 'boolean'},
            'what_would_change_view': {'type': 'string'},
            'advisory_verdict': {'type': 'string', 'enum': ['stop','hold','revise','freeze']},
        }
    return [{
        'type': 'function',
        'name': 'submit_review',
        'description': 'Return exactly one independent review in the required structured form.',
        'parameters': {
            'type': 'object',
            'properties': {
                'review': {
                    'type': 'object',
                    'properties': props,
                    'required': list(props),
                    'additionalProperties': False,
                }
            },
            'required': ['review'],
            'additionalProperties': False,
        },
    }]


def pdf_text() -> str:
    import subprocess
    return subprocess.check_output(['pdftotext', '-layout', str(PDF), '-'], text=True)


def prompt(role: str, manuscript: str) -> str:
    if role == 'strict':
        instruction = '''Act as a strict independent ICLR reviewer. Review ONLY the current manuscript below. You have not seen any prior reviews, scores, revision history, objection matrices, or author-side interpretations. Evaluate correctness, novelty, significance, empirical sufficiency, writing, and whether the paper is actually competitive at ICLR. Be skeptical but fair. Do not reward a paper merely because it reports statistically significant results; enforce any preregistered practical-effect threshold stated by the manuscript. Treat explicit limitations and claim boundaries as binding. Do not demand a new experiment unless the current evidence is genuinely insufficient for the stated narrow claims. Return exactly one structured review by calling submit_review once.'''
    else:
        instruction = '''Act as an independent causal-evidence critic for an ICLR submission. You have not seen any prior reviews or scores. Audit only the manuscript below. Focus on whether the identical-trajectory reward-conditioned write intervention identifies a persistent-state channel; whether the downstream terminal evidence is properly matched; whether the no-memory control changes the interpretation; whether the cross-writer replication is reported without post-hoc threshold relaxation; and whether the full-bank corruption reduction is a valid simplification rather than an excuse for missing experiments. Distinguish source-faithful/live-environment transport debt from the paper's narrower fixed-evidence causal claim. Decide whether another experiment is genuinely needed before submission. Return exactly one structured review by calling submit_review once.'''
    return instruction + '\n\nCURRENT MANUSCRIPT:\n' + manuscript


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--role', choices=sorted(MODELS), required=True)
    ap.add_argument('--tag', default='')
    ap.add_argument('--outdir', type=Path, required=True, help='Private directory for raw reviewer/provider receipts; do not point this at the repository.')
    args = ap.parse_args()
    role = args.role
    model = MODELS[role]

    manuscript = pdf_text()
    packet_sha = hashlib.sha256(manuscript.encode('utf-8')).hexdigest()
    outdir = args.outdir.expanduser().resolve()
    try:
        outdir.relative_to(ROOT.resolve())
        raise RuntimeError('raw blind-review output directory must be external to the repository')
    except ValueError:
        pass
    outdir.mkdir(parents=True, exist_ok=True)
    tag = args.tag.strip() or role
    target = outdir / f'{tag}.json'
    if target.exists():
        raise RuntimeError(f'refuse overwrite existing review: {target}')

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
    try:
        resp = client.respond(
            prompt(role, manuscript),
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
            'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
            'review_type': 'blind-independent-iclr-review',
            'role': role,
            'requested_model': model,
            'resolved_model': resp.get('resolved_model'),
            'provider_status': resp.get('status'),
            'usage': resp.get('usage') or {},
            'manuscript_text_sha256': packet_sha,
            'paper_pdf_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
            'review': review,
            'scientific_authority': False,
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status':'SUCCESS','role':role,'requested_model':model,'resolved_model':payload['resolved_model'],'review':review}, ensure_ascii=False))
        return 0
    except ArkResponseStateError as e:
        payload = {
            'schema_version': '1.0',
            'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
            'review_type': 'blind-independent-iclr-review',
            'role': role,
            'status': 'NONVOTING_PROVIDER_STATE_FAILURE',
            'manuscript_text_sha256': packet_sha,
            'provider_receipt': e.receipt(),
            'scientific_authority': False,
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(payload, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
