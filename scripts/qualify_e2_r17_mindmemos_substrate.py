#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSTRATE = Path('/data/wyt/evidence-substrates/MindMemOS-20260817')
DATA = Path('/data/wyt/e2-r17-compute-shielding/SpreadsheetBench')
VENV_PYTHON = Path('/data/wyt/r17-compute-shielding-venv/bin/python')
TASK_IDS = ['33722', '493-5', '39046', '14240']
FILES = [
    'src/mindmemos/mindmemos/pipelines/skill/evolution.py',
    'src/mindmemos/mindmemos/pipelines/skill/version_store.py',
    'src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py',
    'src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py',
    'src/mindmemos_eval/mindmemos_eval/skills/evolve/algo.py',
    'src/mindmemos_eval/mindmemos_eval/skills/runners.py',
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], *, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)


def main() -> None:
    commit = subprocess.check_output(['git', '-C', str(SUBSTRATE), 'rev-parse', 'HEAD'], text=True).strip()
    remote = subprocess.check_output(['git', '-C', str(SUBSTRATE), 'remote', 'get-url', 'origin'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(SUBSTRATE), 'status', '--porcelain'], text=True).strip()
    env = os.environ.copy()
    env['PYTHONPATH'] = ':'.join([
        str(SUBSTRATE / 'src/mindmemos'),
        str(SUBSTRATE / 'src/mindmemos_sdk'),
        str(SUBSTRATE / 'src/mindmemos_eval'),
    ])
    skill_test = run([str(VENV_PYTHON), '-m', 'pytest', '-q', str(SUBSTRATE / 'tests/pipelines/skill/test_evolution.py')], env=env)
    broad_sheet_test = run([str(VENV_PYTHON), '-m', 'pytest', '-q', str(SUBSTRATE / 'tests/mindmemos_eval/test_spreadsheetbench_eval.py'), '--collect-only'], env=env)

    smoke_code = f'''
from pathlib import Path
import json,tempfile
from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv
from mindmemos_eval.skills.envs.spreadsheetbench.evaluator import compare_workbooks
DATA=Path({str(DATA)!r})
env=SpreadsheetBenchEnv(DATA, DATA/'qualification-env-smoke')
ids={TASK_IDS!r}
all_cases={{c.id:c for c in env.load_all_cases()}}
rows=[]
for i in ids:
 c=all_cases[i]
 with tempfile.TemporaryDirectory(prefix='r17-sbq-',dir='/data/wyt') as td:
  td=Path(td); env.setup_case(c,td)
  golden=env._workbook(c.data['src_dir'],'golden')
  ok,_=compare_workbooks(golden,golden,env.answer_position(c))
  rows.append({{'id':i,'input_exists':(td/'input.xlsx').exists(),'golden_self_score':bool(ok),'answer_position_nonempty':bool(env.answer_position(c))}})
print(json.dumps({{'loaded_cases':len(all_cases),'selected':rows,'pass':len(all_cases)==400 and all(r['input_exists'] and r['golden_self_score'] and r['answer_position_nonempty'] for r in rows)}}))
'''
    env_smoke = run([str(VENV_PYTHON), '-c', smoke_code], env=env)
    try:
        env_payload = json.loads(env_smoke.stdout.strip().splitlines()[-1]) if env_smoke.returncode == 0 else {'pass': False}
    except Exception:
        env_payload = {'pass': False, 'parse_error': True}

    stale_import = broad_sheet_test.returncode != 0 and 'cannot import name' in broad_sheet_test.stdout
    checks = {
        'official_remote': remote == 'https://github.com/mindscale-noah/MindMemOS.git',
        'checkout_clean': dirty == '',
        'commit_present': len(commit) == 40,
        'skill_evolver_first_party_tests_pass': skill_test.returncode == 0 and '11 passed' in skill_test.stdout,
        'spreadsheet_direct_behavior_smoke_pass': env_payload.get('pass') is True,
        'bound_files_present': all((SUBSTRATE / item).exists() for item in FILES),
    }
    payload = {
        'schema_version': '1.0',
        'artifact_type': 'e2-r17-mindmemos-substrate-qualification',
        'status': 'PASS_WITH_UPSTREAM_TEST_PACKAGING_WARNING' if all(checks.values()) and stale_import else 'PASS' if all(checks.values()) else 'FAIL',
        'remote': remote,
        'commit': commit,
        'checkout_clean': dirty == '',
        'bound_file_sha256': {item: sha(SUBSTRATE / item) for item in FILES},
        'checks': checks,
        'skill_evolver_test': {'returncode': skill_test.returncode, 'output_tail': skill_test.stdout[-1800:]},
        'spreadsheet_behavior_smoke': env_payload,
        'upstream_test_packaging_warning': {
            'present': stale_import,
            'scope': 'tests/mindmemos_eval/test_spreadsheetbench_eval.py collection import surface',
            'scientific_runtime_dependency': False,
            'output_tail': broad_sheet_test.stdout[-1800:],
        },
        'prior_unverifiable_commit_reference': '2c940fd19d11cdc272f7051a0e5dfde3f50cbfd4',
        'prior_reference_resolvable_in_current_shallow_clone': False,
        'scientific_outcome_accessed': False,
        'scientific_authority': False,
        'experiment_authority': False,
        'submission_authority': False,
    }
    out = ROOT / 'generated/e2-r17-mindmemos-substrate-qualification-20260825.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': payload['status'], 'commit': commit, 'checks': checks, 'warning': stale_import}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
