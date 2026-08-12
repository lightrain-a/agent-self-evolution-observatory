from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / 'generated' / 'paper-first-collision-review.json'
DEFAULT_JS = PROJECT_ROOT / 'generated' / 'paper-first-collision-review.js'

POLICY = {
    'schema_version': '1.0',
    'review_date': '2026-08-12',
    'primary_sources_only_for_decision': True,
    'broad_causal_memory_novelty_is_rejected': True,
    'car_causalflow_plus_cmi_combination_must_be_a_strong_baseline_not_the_claim': True,
    'fresh_collision_review_cannot_authorize_local_validation': True,
    'ai_premortem_required_after_collision_survival': True,
}

SOURCES = [
    {
        'id': 'car-2026',
        'title': 'Causal Agent Replay: Counterfactual Attribution for LLM-Agent Failures',
        'source_ref': 'arXiv:2606.08275',
        'primary_url': 'https://arxiv.org/abs/2606.08275',
        'scope': 'Intervenes on agent trajectory steps and replays forward to attribute outcome changes; provides the closest trajectory-level causal replay machinery.',
        'collision': 'Strong mechanism collision for replay/intervention, but it does not study persistent memory as the treatment or cross-context transportability of a memory effect.',
    },
    {
        'id': 'causalflow-2026',
        'title': 'CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures',
        'source_ref': 'arXiv:2605.25338',
        'primary_url': 'https://arxiv.org/abs/2605.25338',
        'scope': 'Uses step-level counterfactual interventions to identify failure-inducing steps and generate minimal repairs.',
        'collision': 'Further removes replay/intervention/repair as a novelty axis. Any surviving contribution must be the context-conditioned transportability estimand/certificate for a persistent-memory treatment, not counterfactual replay itself.',
    },
    {
        'id': 'cmi-2026',
        'title': 'Causal Intervention-Based Memory Selection for Long-Horizon LLM Agents',
        'source_ref': 'arXiv:2605.17641',
        'primary_url': 'https://arxiv.org/abs/2605.17641',
        'scope': 'Estimates endpoint causal usefulness of candidate memories under controlled memory interventions for selection.',
        'collision': 'Strong treatment-level collision; endpoint usefulness must be a baseline. It does not decompose an early branch-mediated effect or test its transportability across downstream contexts.',
    },
    {
        'id': 'shiftbench-2026',
        'title': 'ShiftBench: Measuring Recovery of Agent Memory Under Distribution Shift',
        'source_ref': 'OpenReview:CCSztIjmOy',
        'primary_url': 'https://openreview.net/forum?id=CCSztIjmOy',
        'scope': 'Shows memory-policy ranking reversals under distribution shift using recovery-oriented evaluation.',
        'collision': 'Establishes that aggregate memory rankings can reverse under shift, but does not identify a causal branch mediator or a treatment-effect transport certificate.',
    },
    {
        'id': 'continual-memory-2026',
        'title': 'When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents',
        'source_ref': 'arXiv:2604.27003',
        'primary_url': 'https://arxiv.org/abs/2604.27003',
        'scope': 'Studies memory-level continual-learning trade-offs and negative transfer in ALFWorld and BabyAI.',
        'collision': 'Strong empirical collision on memory negative transfer and context dependence; does not provide trajectory-mediated causal identifiability or transportability decomposition.',
    },
    {
        'id': 'memopilot-2026',
        'title': 'From Player to Master: Enhancing Test-Time Learning of LLM Agents via Reinforcement Learning over Memory',
        'source_ref': 'OpenReview:gNWNtstp3r',
        'primary_url': 'https://openreview.net/forum?id=gNWNtstp3r',
        'scope': 'Learns a memory-update copilot from downstream performance for sequential test-time learning.',
        'collision': 'Strong learned-memory-update baseline family. The proposed paper must not claim novelty from learning memory updates and does not reopen updater training.',
    },
    {
        'id': 'trajectory-informed-memory-2026',
        'title': 'Trajectory-Informed Memory Generation for Self-Improving Agent Systems',
        'source_ref': 'arXiv:2603.10600',
        'primary_url': 'https://arxiv.org/abs/2603.10600',
        'scope': 'Extracts structured learnings from execution trajectories with decision attribution and retrieves them as memory.',
        'collision': 'Strong trajectory-to-memory collision; the surviving boundary cannot be trajectory analysis or provenance alone and must remain causal effect transportability.',
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_fresh_collision_review() -> dict[str, Any]:
    return {
        'schema_version': '1.0',
        'generated_at': _now(),
        'paper_id': 'trajectory-mediated-memory-effect-transport',
        'decision': 'PASS_NARROW_TRAJECTORY_MEDIATED_TRANSPORTABILITY',
        'confidence': 'medium',
        'broad_claims_rejected': [
            'causal memory selection is novel',
            'trajectory replay for agent causality is novel',
            'memory negative transfer or ranking reversal is novel',
            'learning a memory updater is novel',
            'trajectory-derived memory is novel',
        ],
        'surviving_novelty_axis': (
            'identifiability and transportability of the causal effect of one persistent-memory treatment: '
            'separate reproducible early branch steering from downstream context amplification/sign reversal, '
            'then certify when an endpoint memory effect may be transported across contexts'
        ),
        'irreducible_difference': (
            'CMI-like endpoint memory interventions do not identify a context-conditioned mediated transport effect; '
            'CAR/CausalFlow-style step interventions do not ask whether a persistent-memory treatment effect remains transportable '
            'across downstream contexts. Their straightforward combination with a context model is a required baseline and is not itself the contribution.'
        ),
        'highest_collision_risk': (
            'A reviewer may view the proposal as CMI memory intervention plus CAR/CausalFlow replay plus context stratification. '
            'The paper survives only if the mediated-effect transportability estimand/certificate creates a distinct falsifiable question and beats that composed baseline.'
        ),
        'required_baseline_families': [
            'CMI-style endpoint memory causal usefulness',
            'CAR-style trajectory intervention/step attribution adapted to memory retrieval',
            'CMI + CAR/CausalFlow + context-model composed baseline under the same replay budget',
            'target-family/context-stratified endpoint effect',
            'first-divergence timing/signature heuristic',
            'ShiftBench-style shift/recovery stratification where applicable',
        ],
        'sources': list(SOURCES),
        'next_gate': 'independent AI paper-premortem; local validation remains locked',
        'local_validation_authorized': False,
        'policy': POLICY,
    }


def write_fresh_collision_review(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_fresh_collision_review()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    js_path.write_text('window.PAPER_FIRST_COLLISION_REVIEW = ' + json.dumps(state, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    return state


if __name__ == '__main__':
    print(json.dumps(write_fresh_collision_review(), ensure_ascii=False, indent=2))
