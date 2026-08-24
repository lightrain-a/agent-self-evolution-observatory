#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = HERE / 'source'
DL = REPO / 'downloads'
RUN11 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b11-outcome-blind-procedural-20260824')
PDF = DL / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b11-20260824.pdf'
SOURCE = DL / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b11-20260824-source.zip'
SUPP = DL / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b11-20260824-supplement.zip'
FORBIDDEN = ['/home/', '/data/', 'wyt@', '222.20.', '202.69.', '10.42.', 'ARK_API_KEY', 'source_message_ref', 'resp_']
PRIVATE_KEYS = ('path', 'run_root', 'artifact_path', 'provider_env_file', 'source_message_ref', 'response_id')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def writej(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lk = str(key).lower()
            if any(fragment in lk for fragment in PRIVATE_KEYS) and not lk.endswith('sha256'):
                continue
            if lk in {'api_key_in_output'}:
                continue
            out[key] = sanitize(item)
        return out
    if isinstance(value, list):
        return [sanitize(x) for x in value]
    if isinstance(value, str) and any(token in value for token in FORBIDDEN):
        return '<private-redacted>'
    return value


def public(path: Path) -> dict[str, Any]:
    return {
        'schema_version': '1.0',
        'projection_type': 'anonymous-public-projection',
        'source_artifact_sha256': sha(path),
        'payload': sanitize(load(path)),
    }


def copy_source(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ['main.tex', 'references.bib', 'iclr2027_conference.bst', 'iclr2027_conference.sty', 'natbib.sty', 'fancyhdr.sty', 'build_figures.py']:
        shutil.copy2(SRC / name, dst / name)
    shutil.copytree(SRC / 'figures', dst / 'figures')
    shutil.copytree(SRC / 'sections', dst / 'sections')


def zip_tree(root: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(root.parent))


def scan(root: Path) -> list[str]:
    hits: list[str] = []
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() in {'.pdf', '.png', '.jpg', '.jpeg', '.zip'}:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN:
            if token in text:
                hits.append(f'{path.relative_to(root)}::{token}')
    return hits


def build_supplement(root: Path, source_sha: str, pdf_sha: str) -> None:
    ev = root / 'evidence'
    ev.mkdir(parents=True, exist_ok=True)
    locals_ = {
        'manuscript-qa.json': HERE / 'manuscript-qa.json',
        'stage-resolved-b11-revision-receipt.json': HERE / 'stage-resolved-b11-revision-receipt.json',
        'story-v4-argument-search-20260824.json': HERE / 'story-v4-argument-search-20260824.json',
        'b11-scientific-evidence.json': HERE / 'b11-scientific-evidence.json',
        'b11-concentration-evidence.json': HERE / 'b11-concentration-evidence.json',
        'transport-localization-evidence.json': HERE / 'transport-localization-evidence.json',
        'baseline-aligned-followup-evidence.json': HERE / 'baseline-aligned-followup-evidence.json',
        'baseline-aligned-expansion-evidence.json': HERE / 'baseline-aligned-expansion-evidence.json',
        'f2r1-chronology-receipt.json': HERE / 'f2r1-chronology-receipt.json',
        'o6-final-evidence.json': HERE / 'o6-final-evidence.json',
    }
    for name, path in locals_.items():
        writej(ev / name, sanitize(load(path)))

    remote = {
        'b11-program-contract-public.json': RUN11 / 'b11-program-contract.json',
        'b11-writer-result-public.json': RUN11 / 'b11-writer-result.json',
        'b11-neutral-memory-manifest-public.json': RUN11 / 'b11-neutral-memory-manifest.json',
        'b11-terminal-result-public.json': RUN11 / 'b11-terminal-result.json',
        'b11-concentration-diagnostic-public.json': RUN11 / 'b11-concentration-diagnostic.json',
    }
    for name, path in remote.items():
        writej(ev / name, public(path))

    csv_dir = root / 'csv'
    csv_dir.mkdir(parents=True, exist_ok=True)
    for name in ['b11-writer-calls.csv', 'b11-terminal-rollouts.csv', 'b11-cell-results.csv']:
        shutil.copy2(RUN11 / name, csv_dir / name)

    qa = load(HERE / 'manuscript-qa.json')
    b11 = load(HERE / 'b11-scientific-evidence.json')
    conc = load(HERE / 'b11-concentration-evidence.json')
    rec = load(HERE / 'stage-resolved-b11-revision-receipt.json')
    story = load(HERE / 'story-v4-argument-search-20260824.json')
    t = b11['terminal_stage']
    w = b11['writer_stage']
    c = conc['summary']
    projection = {
        'schema_version': '1.0',
        'receipt_type': 'supplement-current-projection',
        'paper_id': rec['paper_id'],
        'revision': 'iclr-stage-resolved-b11-20260824',
        'title': rec['title'],
        'story_winner': story['winner']['id'],
        'story_winner_score': story['winner']['score'],
        'current_pdf_sha256': pdf_sha,
        'current_source_zip_sha256': source_sha,
        'claim_expansion': False,
        'external_review_calls_current_revision': 0,
        'write_complete_pairs': 20,
        'forced_terminal_effect': .15625,
        'forced_terminal_p': .00074,
        'expanded_bank_retrieval_hits': '125/172',
        'native_terminal_sf_effect': .020833,
        'native_first_action_sf_tv': .069444,
        'native_first_action_p': .580094,
        'outcome_blind_writer_complete_calls': w['complete_calls'],
        'outcome_blind_terminal_complete_calls': t['complete_calls'],
        'reward_conditioned_vs_neutral_effect': t['mean_absolute_reward_conditioned_vs_neutral_effect'],
        'reward_conditioned_vs_neutral_p': t['permutation_p'],
        'reward_conditioned_vs_neutral_floor': t['practical_effect_floor'],
        'reward_conditioned_vs_neutral_gate_pass': t['primary_gate_pass'],
        'zero_effect_tasks': t['zero_effect_tasks'],
        'all_five_arms_equal_tasks': t['all_five_arms_equal_tasks'],
        'top_effect_task': c['top1_effect_task'],
        'top_effect_absolute_mass_share': c['top1_share_of_absolute_effect_mass'],
        'top_effect_squared_mass_share': c['top1_share_of_squared_effect_mass'],
        'leave_top_task_out_mean_effect': c['minimum_leave_one_task_out_mean_effect'],
        'sources_with_nonzero_effect': c['sources_with_nonzero_effect'],
        'csv_writer_rows': 20,
        'csv_terminal_rows': 144,
        'csv_cell_rows': 36,
        'new_provider_calls_exact': qa['new_provider_calls_exact'],
        'new_writer_calls': qa['new_scientifically_usable_writer_calls'],
        'new_terminal_rollouts': qa['new_terminal_rollouts'],
        'baseline_program_provider_posts_total': qa['baseline_program_provider_posts_total'],
        'baseline_program_usable_completions_total': qa['baseline_program_scientifically_usable_completions_total'],
        'baseline_program_writer_calls_total': qa['baseline_program_writer_calls_total'],
        'baseline_program_terminal_rollouts_total': qa['baseline_program_terminal_rollouts_total'],
        'baseline_program_process_rollouts_total': qa['baseline_program_process_rollouts_total'],
        'full_paper_observable_provider_posts_lower_bound': qa['updated_full_paper_observable_provider_posts_lower_bound'],
        'main_text_pages': qa['main_text_pages'],
        'references_begin_page': qa['references_begin_page'],
        'pdf_pages_total': qa['pdf_pages_total'],
        'additional_neutral_first_action_experiment_verdict': story['additional_experiment_adjudication']['verdict'],
        'additional_provider_calls_avoided': story['additional_experiment_adjudication']['provider_calls_avoided'],
        'canonical_stable_registry_overwritten': False,
        'scientific_authority': False,
        'experiment_authority': False,
        'submission_authority': False,
    }
    writej(root / 'CURRENT-PROJECTION.json', projection)

    (root / 'README.md').write_text(
        '''# Reward Errors Change Memory Before They Change Policy — stage-resolved B11 supplement

This anonymous supplement extends the C1 evidence with an outcome-blind structured-memory control and a stage-resolved story audit.

**Outcome-blind writer.** The same 20 source tasks and action-summary bytes are rewritten with the same DeepSeek-V4-Flash writer family and the same Title/Description/Content schema, but without success/failure, reward, score, or outcome semantics. All 20 calls complete, including all 11 sources selected by the native retriever.

**Native neutral-memory terminal arm.** On the same 36 native tasks, 144/144 calls complete. Mean reward-conditioned-versus-neutral effect is 0.045139 with permutation p=0.0048, below the unchanged 0.15 practical floor. Thirty-two tasks have zero effect and 30/36 have identical success, failure, neutral, raw-trajectory, and no-memory point estimates.

**Concentration boundary.** The detected small effect is highly localized. Task 229 contributes 61.5% of absolute effect mass and 87.7% of squared effect mass; removing it lowers the mean to 0.017857. Only 2/11 native-selected sources contain any nonzero future task. This diagnostic is descriptive and does not alter the preregistered gate.

**CSV provenance.** The supplement includes deterministic projections with 20 writer rows, 144 terminal-rollout rows, and 36 cell rows. The scientific source of truth remains the immutable response-first/per-stage JSON evidence; the CSVs make interruption recovery and downstream audit easier.

The current story is stage-resolved: write -> exposure -> branch-specific policy uptake -> outcome. A 144-call neutral first-action arm is intentionally deferred because it is unnecessary for the current narrow branch-specific claim; it is reopened only if the paper expands to generic structured-memory presence or formal mediation.

B11 adds 164 scientifically usable provider calls. The full-paper observable provider-POST lower bound is at least 2,079. No training or local GPU fine-tuning is used. Stable canonical PaperRegistry is not overwritten and no daytime external review is triggered.

Run `python verify_current_supplement.py` to validate the public projection.
''',
        encoding='utf-8',
    )

    verifier = r'''from pathlib import Path
import json,sys,csv
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');b=L('b11-scientific-evidence.json');c=L('b11-concentration-evidence.json');s=L('story-v4-argument-search-20260824.json');r=L('stage-resolved-b11-revision-receipt.json');wr=L('b11-writer-result-public.json')['payload'];tr=L('b11-terminal-result-public.json')['payload'];p=json.load(open(R/'CURRENT-PROJECTION.json'))
def rows(n):
 with open(R/'csv'/n,newline='',encoding='utf-8') as f:return sum(1 for _ in csv.DictReader(f))
w=b['writer_stage'];t=b['terminal_stage'];a=b['execution_accounting'];cc=c['summary']
checks=[
 q['status']=='PASS',q['revision']=='ICLR-STAGE-RESOLVED-B11-20260824',sum(q['checks'].values())==len(q['checks'])==43,q['abstract_words_approx']==191,q['main_text_pages']==9,q['references_begin_page']==10,q['pdf_pages_total']==19,q['new_provider_calls_exact']==164,q['new_scientifically_usable_writer_calls']==20,q['new_terminal_rollouts']==144,q['updated_full_paper_observable_provider_posts_lower_bound']==2079,
 s['status']=='STORY_SEARCH_COMPLETE_WINNER_FROZEN',s['winner']['id']=='S1-WRITE-TO-UPTAKE-BOTTLENECK',s['winner']['score']==98,s['additional_experiment_adjudication']['verdict']=='DEFER_NOT_NEEDED_FOR_CURRENT_CLAIM',s['additional_experiment_adjudication']['provider_calls_avoided']==144,
 b['status']=='B11_OUTCOME_BLIND_STRUCTURED_CONTROL_COMPLETE',w['complete_calls']==20,w['provider_failures']==0,w['required_native_sources_complete']==11,abs(w['mean_neutral_to_success_token_jaccard_distance']-.61179)<1e-12,abs(w['mean_neutral_to_failure_token_jaccard_distance']-.690062)<1e-12,w['neutral_title_set_equals_success_sources']==0,w['neutral_title_set_equals_failure_sources']==0,
 t['complete_calls']==144,t['provider_failures']==0,abs(t['mean_absolute_reward_conditioned_vs_neutral_effect']-.045139)<1e-12,abs(t['permutation_p']-.0048)<1e-12,abs(t['practical_effect_floor']-.15)<1e-12,t['primary_gate_pass'] is False,t['zero_effect_tasks']==32,t['all_five_arms_equal_tasks']==30,
 c['status']=='B11_ZERO_CALL_CONCENTRATION_COMPLETE',c['provider_calls']==0,cc['top1_effect_task']==229,abs(cc['top1_share_of_absolute_effect_mass']-.615385)<1e-12,abs(cc['top1_share_of_squared_effect_mass']-.876712)<1e-12,abs(cc['top2_share_of_squared_effect_mass']-.931507)<1e-12,abs(cc['minimum_leave_one_task_out_mean_effect']-.017857)<1e-12,cc['sources_with_nonzero_effect']==2,cc['native_selected_source_count']==11,
 wr['status']=='B11_WRITER_COMPLETE',wr['summary']['provider_calls_complete']==20,wr['summary']['provider_failures']==0,tr['status']=='B11_TERMINAL_EXECUTION_COMPLETE',tr['summary']['provider_calls_complete']==144,tr['summary']['provider_failures']==0,abs(tr['summary']['observed_mean_absolute_reward_conditioned_vs_neutral_effect']-.045139)<1e-12,tr['summary']['primary_gate_pass'] is False,
 a['b11_total_provider_posts']==164,a['b11_scientifically_usable_provider_completions']==164,a['full_paper_observable_provider_posts_lower_bound_after_b11']==2079,
 rows('b11-writer-calls.csv')==20,rows('b11-terminal-rollouts.csv')==144,rows('b11-cell-results.csv')==36,
 r['status']=='STAGE_RESOLVED_B11_INTEGRATED_QA_PASS',r['title']=='Reward Errors Change Memory Before They Change Policy',r['external_review_calls_current_revision']==0,r['canonical_stable_registry_overwritten'] is False,
 p['revision']=='iclr-stage-resolved-b11-20260824',p['story_winner']=='S1-WRITE-TO-UPTAKE-BOTTLENECK',p['claim_expansion'] is False,p['reward_conditioned_vs_neutral_gate_pass'] is False,abs(p['reward_conditioned_vs_neutral_effect']-.045139)<1e-12,abs(p['top_effect_absolute_mass_share']-.615385)<1e-12,abs(p['leave_top_task_out_mean_effect']-.017857)<1e-12,p['full_paper_observable_provider_posts_lower_bound']==2079,p['canonical_stable_registry_overwritten'] is False,
]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
    (root / 'verify_current_supplement.py').write_text(verifier, encoding='utf-8')


def main() -> int:
    qa = load(HERE / 'manuscript-qa.json')
    if qa.get('status') != 'PASS' or qa.get('revision') != 'ICLR-STAGE-RESOLVED-B11-20260824':
        raise RuntimeError('B11 QA not pass')
    if not (RUN11 / 'b11-writer-calls.csv').is_file() or not (RUN11 / 'b11-terminal-rollouts.csv').is_file() or not (RUN11 / 'b11-cell-results.csv').is_file():
        raise RuntimeError('B11 CSV projection missing')
    DL.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / 'paper.pdf', PDF)
    with tempfile.TemporaryDirectory(prefix='c1-b11-package-') as td:
        tmp = Path(td)
        src = tmp / 'source'
        copy_source(src)
        zip_tree(src, SOURCE)
        source_sha = sha(SOURCE)
        pdf_sha = sha(PDF)
        supp = tmp / 'supplement'
        build_supplement(supp, source_sha, pdf_sha)
        hits = scan(supp)
        if hits:
            raise RuntimeError('supplement privacy scan failed: ' + '; '.join(hits[:20]))
        zip_tree(supp, SUPP)
    print(json.dumps({
        'pdf': {'path': str(PDF), 'sha256': sha(PDF)},
        'source_zip': {'path': str(SOURCE), 'sha256': sha(SOURCE)},
        'supplement_zip': {'path': str(SUPP), 'sha256': sha(SUPP)},
        'privacy_scan': 'PASS',
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
