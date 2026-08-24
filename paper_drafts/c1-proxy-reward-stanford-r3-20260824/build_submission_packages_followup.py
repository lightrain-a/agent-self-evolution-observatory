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
DOWNLOADS = REPO / 'downloads'
RUN8 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b8-raw-trajectory-baseline-20260824')
RUN9 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b9-partial-reference-coverage-20260824')
PDF_OUT = DOWNLOADS / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-followup-20260824.pdf'
SOURCE_OUT = DOWNLOADS / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-followup-20260824-source.zip'
SUPP_OUT = DOWNLOADS / 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-followup-20260824-supplement.zip'
FORBIDDEN = ['/home/', '/data/', 'wyt@', '222.20.', '202.69.', '10.42.', 'ARK_API_KEY', 'source_message_ref', 'resp_']
PRIVATE_FRAGS = ('path', 'run_root', 'artifact_path', 'provider_env_file', 'source_message_ref', 'response_id')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def writej(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lk = str(key).lower()
            if any(frag in lk for frag in PRIVATE_FRAGS) and not lk.endswith('sha256'):
                continue
            if lk == 'api_key_in_output':
                continue
            out[key] = sanitize(item)
        return out
    if isinstance(value, list):
        return [sanitize(x) for x in value]
    if isinstance(value, str) and any(token in value for token in FORBIDDEN):
        return '<private-redacted>'
    return value


def public_projection(path: Path) -> dict[str, Any]:
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


def privacy_scan(root: Path) -> list[str]:
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


def build_supplement(tree: Path, source_zip_sha: str, pdf_sha: str) -> None:
    evidence = tree / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    local = {
        'manuscript-qa.json': HERE / 'manuscript-qa.json',
        'baseline-aligned-expansion-evidence.json': HERE / 'baseline-aligned-expansion-evidence.json',
        'baseline-aligned-followup-evidence.json': HERE / 'baseline-aligned-followup-evidence.json',
        'baseline-followup-revision-receipt.json': HERE / 'baseline-followup-revision-receipt.json',
        'f2r1-chronology-receipt.json': HERE / 'f2r1-chronology-receipt.json',
        'o5-manuscript-evidence.json': HERE / 'o5-manuscript-evidence.json',
        'o6-final-evidence.json': HERE / 'o6-final-evidence.json',
        'o6-full-bank-corruption-reduction.json': HERE / 'o6-full-bank-corruption-reduction.json',
    }
    for name, path in local.items():
        writej(evidence / name, sanitize(load(path)))
    remote = {
        'b8-raw-trajectory-contract-public.json': RUN8 / 'b8-contract.json',
        'b8-raw-trajectory-result-public.json': RUN8 / 'b8-result.json',
        'b8-tie-aware-geometry-public.json': RUN8 / 'b8-tie-aware-geometry.json',
        'b9-endpoint-headroom-contract-public.json': RUN9 / 'b9-contract.json',
        'b9-endpoint-headroom-result-public.json': RUN9 / 'b9-result.json',
    }
    for name, path in remote.items():
        writej(evidence / name, public_projection(path))

    qa = load(HERE / 'manuscript-qa.json')
    followup = load(HERE / 'baseline-aligned-followup-evidence.json')
    prior = load(HERE / 'baseline-aligned-expansion-evidence.json')
    receipt = load(HERE / 'baseline-followup-revision-receipt.json')
    b8 = followup['experiments']['B8_raw_writer_input_trajectory_baseline']
    b9 = followup['experiments']['B9_partial_reference_endpoint_headroom']
    projection = {
        'schema_version': '1.0',
        'receipt_type': 'supplement-current-projection',
        'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
        'revision': 'iclr-baseline-followup-raw-trajectory-endpoint-20260824',
        'title': receipt['title'],
        'current_pdf_sha256': pdf_sha,
        'current_source_zip_sha256': source_zip_sha,
        'claim_expansion': False,
        'external_review_calls_current_followup': 0,
        'write_complete_pairs': prior['experiments']['B2_write_breadth']['combined_complete_pairs'],
        'forced_swap_mean_abs_effect': 0.15625,
        'forced_swap_p': 0.00074,
        'original_bank_retrieval_hits': '8/188',
        'expanded_bank_retrieval_hits': '125/172',
        'native_branch_mean_abs_effect': prior['experiments']['B4_native_retrieval_matched_branch_transport']['mean_absolute_success_rate_difference'],
        'native_branch_p': prior['experiments']['B4_native_retrieval_matched_branch_transport']['permutation_p'],
        'native_no_memory_effect': prior['experiments']['B5_native_support_no_memory']['mean_absolute_memory_presence_effect'],
        'native_no_memory_p': prior['experiments']['B5_native_support_no_memory']['permutation_p'],
        'raw_trajectory_rewrite_effect': b8['mean_absolute_rewrite_vs_raw_effect'],
        'raw_trajectory_p': b8['permutation_p'],
        'raw_trajectory_practical_floor': b8['practical_floor'],
        'raw_trajectory_gate_pass': b8['gate_pass'],
        'all_four_equal_tasks': b8['all_four_equal_tasks'],
        'partial_reference_success_failure_all': b9['mean_absolute_success_failure_partial_difference_all'],
        'partial_reference_success_failure_multi_reference': b9['mean_absolute_success_failure_partial_difference_multi_reference'],
        'partial_reference_confirmatory_gate': b9['confirmatory_gate'],
        'followup_new_provider_calls_exact': qa['new_provider_calls_exact'],
        'baseline_program_provider_posts_total': qa['baseline_program_provider_posts_total'],
        'baseline_program_usable_completions_total': qa['baseline_program_scientifically_usable_completions_total'],
        'baseline_program_terminal_rollouts_total': qa['baseline_program_terminal_rollouts_total'],
        'full_paper_observable_provider_posts_lower_bound': qa['updated_full_paper_observable_provider_posts_lower_bound'],
        'main_text_pages': qa['main_text_pages'],
        'references_begin_page': qa['references_begin_page'],
        'pdf_pages_total': qa['pdf_pages_total'],
        'cross_policy_status': prior['claim_boundary']['cross_policy_terminal_transfer_status'],
        'canonical_stable_registry_overwritten': False,
        'scientific_authority': False,
        'experiment_authority': False,
        'submission_authority': False,
    }
    writej(tree / 'CURRENT-PROJECTION.json', projection)

    (tree / 'README.md').write_text(
        """# Reward Errors Become Persistent State — raw-trajectory / endpoint follow-up supplement

This anonymous supplement extends, but does not overwrite, the prior baseline-aligned expansion evidence.

The follow-up adds two bounded checks on the 36-task native-retrieval support. **Raw writer-input trajectory baseline (B8):** 144/144 Doubao calls complete with zero provider failures. The preregistered mean rewrite-versus-raw effect is 0.045139 with permutation p=0.00775, below the unchanged 0.15 practical-effect floor. A tie-aware derived audit shows that 31/36 tasks have identical success-memory, failure-memory, raw-trajectory, and no-memory point estimates. **Endpoint-headroom diagnostic (B9):** zero new provider calls; fractional reference coverage re-scores 432 archived success/failure/no-memory outputs. Mean absolute S/F separation is 0.019511 overall and 0.028274 on the 16 multi-reference tasks. This metric was introduced after observing binary saturation and is diagnostic only; it does not replace the preregistered B4/B5 gate.

The prior expansion remains immutable: 498 observable provider POSTs and 464 scientifically usable completions. B8 adds 144 new scientifically usable terminal calls. Across the baseline program there are therefore 642 observable POSTs, 608 scientifically usable completions, and 576 scientifically usable terminal rollouts. The full-paper observable provider-POST lower bound is at least 1,483. No training or local GPU fine-tuning is used.

Private host paths, credentials, provider response IDs/raw text, and human-authorization files are excluded. Run `python verify_current_supplement.py` to validate the public projection.
""",
        encoding='utf-8',
    )

    verifier = r'''from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');x=L('baseline-aligned-expansion-evidence.json');f=L('baseline-aligned-followup-evidence.json');r=L('baseline-followup-revision-receipt.json');p=json.load(open(R/'CURRENT-PROJECTION.json'))
b8=L('b8-raw-trajectory-result-public.json')['payload'];b9=L('b9-endpoint-headroom-result-public.json')['payload'];g=L('b8-tie-aware-geometry-public.json')['payload']
checks=[
 q['status']=='PASS',q['revision']=='ICLR-BASELINE-ALIGNED-FOLLOWUP-RAW-TRAJECTORY-ENDPOINT-20260824',sum(q['checks'].values())==len(q['checks'])==36,q['abstract_words_approx']==220,q['main_text_pages']==9,q['references_begin_page']==10,q['pdf_pages_total']==17,
 x['status']=='BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP',x['execution_accounting']['new_provider_posts']==498,x['execution_accounting']['new_scientifically_usable_provider_completions']==464,x['execution_accounting']['updated_full_paper_observable_provider_posts_lower_bound']==1339,
 f['status']=='BASELINE_FOLLOWUP_COMPLETE_RAW_TRAJECTORY_AND_ENDPOINT_DIAGNOSTIC',f['execution_accounting']['followup_new_provider_posts']==144,f['execution_accounting']['baseline_program_provider_posts_total']==642,f['execution_accounting']['baseline_program_scientifically_usable_completions_total']==608,f['execution_accounting']['baseline_program_scientifically_usable_terminal_rollouts_total']==576,f['execution_accounting']['full_paper_observable_provider_posts_lower_bound_after_followup']==1483,
 b8['status']=='B8_EXECUTION_COMPLETE',b8['summary']['provider_calls_complete']==144,b8['summary']['provider_failures']==0,abs(b8['summary']['observed_mean_absolute_rewrite_vs_raw_effect']-.045139)<1e-12,abs(b8['summary']['three_arm_permutation_p_ge_observed']-.00775)<1e-12,b8['summary']['primary_gate_pass'] is False,
 g['status']=='DERIVED_GEOMETRY_COMPLETE_ZERO_PROVIDER_CALLS',g['exact_rate_equalities']['all_four_equal_tasks']==31,g['runner_secondary_field_disposition']['use_in_manuscript'] is False,
 b9['status']=='B9_DIAGNOSTIC_COMPLETE',b9['provider_calls']==0,abs(b9['summary_all_36']['mean_absolute_success_failure_partial_difference']-.019511)<1e-12,abs(b9['summary_multi_reference_16']['mean_absolute_success_failure_partial_difference']-.028274)<1e-12,b9['headroom']['binary_joint_floor_cells']==18,b9['headroom']['partial_joint_floor_cells']==10,
 r['status']=='BASELINE_FOLLOWUP_INTEGRATED_QA_PASS',r['external_review_calls_current_followup']==0,r['canonical_stable_registry_overwritten'] is False,
 p['revision']=='iclr-baseline-followup-raw-trajectory-endpoint-20260824',p['claim_expansion'] is False,p['raw_trajectory_gate_pass'] is False,abs(p['raw_trajectory_rewrite_effect']-.045139)<1e-12,abs(p['partial_reference_success_failure_all']-.019511)<1e-12,p['partial_reference_confirmatory_gate'] is None,p['full_paper_observable_provider_posts_lower_bound']==1483,p['cross_policy_status']=='SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS',p['canonical_stable_registry_overwritten'] is False,
]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
    (tree / 'verify_current_supplement.py').write_text(verifier, encoding='utf-8')


def main() -> int:
    qa = load(HERE / 'manuscript-qa.json')
    if qa.get('status') != 'PASS' or qa.get('revision') != 'ICLR-BASELINE-ALIGNED-FOLLOWUP-RAW-TRAJECTORY-ENDPOINT-20260824':
        raise RuntimeError('current follow-up QA is not PASS')
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / 'paper.pdf', PDF_OUT)
    with tempfile.TemporaryDirectory(prefix='c1-followup-package-') as td:
        tmp = Path(td)
        src = tmp / 'source'
        copy_source(src)
        zip_tree(src, SOURCE_OUT)
        source_sha = sha(SOURCE_OUT)
        pdf_sha = sha(PDF_OUT)
        supp = tmp / 'supplement'
        build_supplement(supp, source_sha, pdf_sha)
        hits = privacy_scan(supp)
        if hits:
            raise RuntimeError('supplement privacy scan failed: ' + '; '.join(hits[:20]))
        zip_tree(supp, SUPP_OUT)
    print(json.dumps({
        'pdf': {'path': str(PDF_OUT), 'sha256': sha(PDF_OUT)},
        'source_zip': {'path': str(SOURCE_OUT), 'sha256': sha(SOURCE_OUT)},
        'supplement_zip': {'path': str(SUPP_OUT), 'sha256': sha(SUPP_OUT)},
        'privacy_scan': 'PASS',
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
