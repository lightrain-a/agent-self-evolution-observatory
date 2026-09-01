#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path('/data/wyt/e2-r17-compute-shielding/SpreadsheetBench')
SUBSTRATE = Path('/data/wyt/evidence-substrates/MindMemOS-20260817')
ARCHIVE_SHA = '10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949'
DATASET_SHA = 'bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7'
TAG = 'E2-R17-F1-DEVELOPMENT-TASKS-v1'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def git_commit(path: Path) -> str:
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()


def run_tests() -> dict:
    proc = subprocess.run(
        ['python', '-m', 'unittest', 'research_pipeline.test_e2_r17_compute_shielding_runner', '-q'],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {'pass': proc.returncode == 0, 'returncode': proc.returncode, 'output_tail': proc.stdout[-1200:]}


def main() -> None:
    dataset_path = DATA / 'spreadsheetbench_verified_400/dataset.json'
    rows = json.loads(dataset_path.read_text(encoding='utf-8'))
    ranked = sorted(rows, key=lambda row: hashlib.sha256(f'{TAG}|{row["id"]}'.encode()).hexdigest())
    selected = [str(row['id']) for row in ranked[:4]]
    xlsx_count = sum(1 for _ in (DATA / 'spreadsheetbench_verified_400').rglob('*.xlsx'))
    adapter = json.loads((ROOT / 'generated/e2-r17-mindmemos-ark-adapter-qualification-20260825.json').read_text())
    substrate = json.loads((ROOT / 'generated/e2-r17-mindmemos-substrate-qualification-20260825.json').read_text())
    tests = run_tests()
    checks = {
        'substrate_receipt_pass': str(substrate.get('status') or '').startswith('PASS'),
        'substrate_commit_matches_receipt': git_commit(SUBSTRATE) == substrate.get('commit'),
        'archive_sha_exact': sha(DATA / 'spreadsheetbench_verified_400.tar.gz') == ARCHIVE_SHA,
        'dataset_sha_exact': sha(dataset_path) == DATASET_SHA,
        'dataset_records_400': len(rows) == 400,
        'xlsx_files_800': xlsx_count == 800,
        'development_task_selection_outcome_blind': True,
        'development_task_count_4': len(selected) == 4,
        'runner_semantics_tests_pass': tests['pass'],
        'provider_retry_disabled': adapter.get('provider_retry_disabled') is True,
        'benchmark_outcome_not_accessed_by_adapter_smoke': adapter.get('benchmark_data_accessed') is False,
    }
    provider_ready = adapter.get('status') == 'PASS'
    payload = {
        'schema_version': '1.0',
        'artifact_type': 'e2-r17-compute-shielding-f0-r3-gate',
        'paper_parent': 'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK',
        'child': 'E2-R17-COMPUTE-SHIELDING',
        'scientific_object': 'acting-optimal compute can be learning-suboptimal because test-time rescue censors reusable failure signals',
        'status': 'READY_FOR_F1' if all(checks.values()) and provider_ready else 'HOLD_PROVIDER_SUBSCRIPTION' if all(checks.values()) and adapter.get('status') == 'HOLD_PROVIDER_SUBSCRIPTION' else 'HOLD_F0_GATE',
        'checks': checks,
        'provider_gate': {
            'status': adapter.get('status'),
            'qualification_sha256': sha(ROOT / 'generated/e2-r17-mindmemos-ark-adapter-qualification-20260825.json'),
            'requested_model': (adapter.get('model_identity') or {}).get('requested'),
            'required_resolved_model': (adapter.get('model_identity') or {}).get('required_resolved'),
            'route': (adapter.get('model_identity') or {}).get('route'),
        },
        'data_contract': {
            'source': 'SpreadsheetBench Verified-400',
            'archive_sha256': ARCHIVE_SHA,
            'dataset_sha256': DATASET_SHA,
            'records': len(rows),
            'xlsx_files': xlsx_count,
            'selection_tag': TAG,
            'development_task_ids': selected,
            'task_prompt_or_outcome_inspected_for_selection': False,
        },
        'substrate_contract': {
            'name': 'MindMemOS',
            'path': str(SUBSTRATE),
            'remote': substrate.get('remote'),
            'commit': substrate.get('commit'),
            'qualification_sha256': sha(ROOT / 'generated/e2-r17-mindmemos-substrate-qualification-20260825.json'),
            'bound_file_sha256': substrate.get('bound_file_sha256'),
            'upstream_test_packaging_warning': substrate.get('upstream_test_packaging_warning'),
            'skill_evolver': 'src/mindmemos/mindmemos/pipelines/skill/evolution.py::SkillEvolver',
            'spreadsheet_env': 'src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py::SpreadsheetBenchEnv',
        },
        'compute_contract': {
            'low_k': 1,
            'high_k': 4,
            'selector': 'max score, stable lowest rollout index tie-break',
            'all_subruns_are_receipts': True,
            'only_selected_subrun_is_deployed': True,
            'nonselected_failures_may_not_feed_updater': True,
            'shadow_is_independent_k1_same_task_same_preupdate_skill_state': True,
            'hardmine_cannot_reconstruct_rescued_failure': True,
        },
        'f1_arms': ['L/L', 'H/H', 'H/L-shadow', 'H/H-hardmine'],
        'f1_promotion_rule': [
            'H/H online reward > L/L online reward',
            'H/H frozen-skill quality < L/L frozen-skill quality',
            'H/L-shadow frozen-skill quality > H/H',
            'H/L-shadow recovery > H/H-hardmine recovery',
        ],
        'scientific_unit': 'one learned skill state from one independently seeded evolution stream',
        'repeats_are_scientific_n': False,
        'f1_execution_authorized': False,
        'reason_f1_not_authorized': 'provider gate must PASS and an execution artifact must bind exact tasks/seeds/call budget before model calls',
        'runner_sha256': sha(ROOT / 'research_pipeline/e2_r17_compute_shielding_runner.py'),
        'runner_test_sha256': sha(ROOT / 'research_pipeline/test_e2_r17_compute_shielding_runner.py'),
        'ark_adapter_sha256': sha(ROOT / 'research_pipeline/e2_r17_mindmemos_ark_adapter.py'),
        'runner_test_result': tests,
        'scientific_authority': False,
        'experiment_authority': False,
        'gpu_authority': False,
        'submission_authority': False,
    }
    payload['body_sha256'] = csha(payload)
    out = ROOT / 'generated/e2-r17-compute-shielding-f0-r3-gate-20260825.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': payload['status'], 'checks_passed': sum(checks.values()), 'checks': len(checks), 'tasks': selected, 'body_sha256': payload['body_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
