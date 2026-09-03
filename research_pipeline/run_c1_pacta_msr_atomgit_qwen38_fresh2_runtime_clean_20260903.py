#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file
from research_pipeline import run_c1_pacta_msr_runtime_20260902 as base_runtime
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_fresh2_runtime_20260903 import IMAGE_ROOT, bind

bind()
ROOTFUL_HOST = base_runtime.ROOTFUL_HOST
docker_metadata = base_runtime.docker_metadata
frozen_rows = base_runtime.frozen_rows
run = base_runtime.run

PARENT_ROOT = Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-runtime-20260903-v1')
PARENT_IMPORT = PARENT_ROOT / 'import-receipt.json'
PARENT_QUAL = PARENT_ROOT / 'normalization-qualification.json'
PARENT_IMPORT_SHA = 'e453b01f37d225260685d3a7dfb2adde0d78ec056c2a40858adeb2c98389710e'
PARENT_QUAL_SHA = '5294a440b89ce0f60eb60e37ef5820832c96cea3d6e1b8f7079a55d3d9dd9d29'
DEFAULT = Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-runtime-clean-20260903-v1')
CONTRACT = Path(__file__).resolve().parents[1] / 'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-runtime-clean-contract-20260903.json'


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parent_audit() -> dict[str, Any]:
    if sha256_file(PARENT_IMPORT) != PARENT_IMPORT_SHA:
        raise RuntimeError('STOP_PARENT_IMPORT_HASH_DRIFT')
    if sha256_file(PARENT_QUAL) != PARENT_QUAL_SHA:
        raise RuntimeError('STOP_PARENT_QUAL_HASH_DRIFT')
    imp = load(PARENT_IMPORT)
    qual = load(PARENT_QUAL)
    if imp.get('status') != 'MSR_20_IMPORT_PASS' or imp.get('imported') != 20:
        raise RuntimeError('STOP_PARENT_IMPORT_NOT_PASS')
    if not (
        qual.get('status') == 'HOLD_MSR_RUNTIME_SUPPORT_INCOMPLETE'
        and qual.get('qualified') == 19
        and qual.get('source_qualified') == 10
        and qual.get('future_qualified') == 9
    ):
        raise RuntimeError('STOP_PARENT_QUAL_GEOMETRY_DRIFT')
    failures = [x for x in qual['rows'] if not x.get('exact_base_normalization_pass')]
    if len(failures) != 1 or failures[0].get('instance_id') != 'psf__requests-1142':
        raise RuntimeError('STOP_PARENT_FAILURE_IDENTITY_DRIFT')
    return {'import_sha256': PARENT_IMPORT_SHA, 'qualification_sha256': PARENT_QUAL_SHA}


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError('repair root exists; no overwrite')
    parent = parent_audit()
    rows = frozen_rows()
    if len(rows) != 20:
        raise RuntimeError('STOP_IMAGE_GEOMETRY_DRIFT')
    root.mkdir(parents=True)
    out = {
        'schema_version': 1,
        'created_at_utc': now(),
        'status': 'FRESH2_RUNTIME_CLEAN_REPAIR_PREPARE_PASS',
        'contract_sha256': sha256_file(CONTRACT),
        'parent': parent,
        'image_count': 20,
        'provider_calls': 0,
        'scientific_source_tasks_used': 0,
        'future_task_executions': 0,
    }
    atomic_json(root / 'prepare.json', out)
    return out


def _exec(cid: str, cmd: str, timeout: int = 120) -> dict[str, Any]:
    return run(['docker', 'exec', '-w', '/testbed', cid, 'bash', '-lc', cmd], timeout)


def qualify_one(row: dict[str, Any], imported: dict[str, Any]) -> dict[str, Any]:
    keys = ('role', 'unit_id', 'instance_id', 'base_commit', 'index_digest', 'amd64_digest')
    out = {k: row[k] for k in keys}
    out['digest_ref'] = imported.get('digest_ref', '')
    out['image_id'] = imported.get('image_id', '')
    out['import_pass'] = bool(imported.get('import_pass'))
    out['digest_inspect_pass'] = bool(imported.get('digest_inspect_pass'))
    if not out['import_pass'] or not out['digest_inspect_pass']:
        out.update({'container_start_pass': False, 'exact_base_normalization_pass': False, 'invalid_reason': 'parent import/digest failure'})
        return out

    env = os.environ.copy()
    env['DOCKER_HOST'] = ROOTFUL_HOST
    name = 'c1-fresh2-clean-' + os.urandom(6).hex()
    start = subprocess.run(
        ['docker', 'run', '-d', '--pull=never', '--name', name, '-w', '/testbed', '--rm', out['digest_ref'], 'sleep', '30m'],
        text=True, capture_output=True, timeout=180, env=env, check=False,
    )
    out['container_start_pass'] = start.returncode == 0
    if not out['container_start_pass']:
        out.update({'exact_base_normalization_pass': False, 'invalid_reason': start.stderr[-800:]})
        return out
    cid = start.stdout.strip()
    base = row['base_commit']
    try:
        head = _exec(cid, 'git rev-parse HEAD')
        tracked = _exec(cid, 'git diff --quiet && git diff --cached --quiet')
        untracked = _exec(cid, "git ls-files --others --exclude-standard")
        untracked_paths = [x.strip() for x in untracked['output'].splitlines() if x.strip()]
        allowed_untracked = all(x == 'build' or x.startswith('build/') for x in untracked_paths)
        exists = _exec(cid, f'git cat-file -e {base}^{{commit}}')
        ancestor = _exec(cid, f'git merge-base --is-ancestor {base} HEAD')
        tools = _exec(cid, 'test -d /testbed && command -v bash && command -v git && command -v python')
        reset = _exec(cid, f'git reset --hard {base}')
        clean = _exec(cid, 'git clean -fd -- build')
        post = _exec(cid, 'git rev-parse HEAD')
        post_status = _exec(cid, 'git status --porcelain=v1 --untracked-files=all')
        out.update({
            'observed_initial_head': head['output'].strip(),
            'initial_tracked_tree_clean': tracked['returncode'] == 0,
            'initial_untracked_count': len(untracked_paths),
            'initial_untracked_paths_sha256': __import__('hashlib').sha256('\n'.join(untracked_paths).encode()).hexdigest(),
            'initial_untracked_only_build': allowed_untracked,
            'base_commit_exists': exists['returncode'] == 0,
            'base_is_ancestor': ancestor['returncode'] == 0,
            'runtime_tools_pass': tools['returncode'] == 0,
            'reset_pass': reset['returncode'] == 0,
            'targeted_clean_command': 'git clean -fd -- build',
            'targeted_clean_pass': clean['returncode'] == 0,
            'targeted_clean_output': clean['output'],
            'post_reset_head': post['output'].strip(),
            'post_reset_head_exact': post['output'].strip() == base,
            'post_reset_working_tree_clean': post_status['returncode'] == 0 and not post_status['output'].strip(),
        })
        out['exact_base_normalization_pass'] = all([
            out['import_pass'], out['digest_inspect_pass'], out['container_start_pass'],
            out['initial_tracked_tree_clean'], out['initial_untracked_only_build'],
            out['base_commit_exists'], out['base_is_ancestor'], out['runtime_tools_pass'],
            out['reset_pass'], out['targeted_clean_pass'], out['post_reset_head_exact'],
            out['post_reset_working_tree_clean'],
        ])
        if not out['exact_base_normalization_pass']:
            out['invalid_reason'] = 'targeted build-clean exact-base pre/postcondition failed'
    finally:
        subprocess.run(['docker', 'rm', '-f', cid], text=True, capture_output=True, timeout=120, env=env, check=False)
    return out


def qualify(root: Path) -> dict[str, Any]:
    if not (root / 'prepare.json').is_file():
        raise RuntimeError('prepare first')
    if (root / 'normalization-qualification.json').exists():
        raise RuntimeError('qualification exists; no overwrite')
    parent_audit()
    imports = {x['instance_id']: x for x in load(PARENT_IMPORT)['rows']}
    rows = []
    journal = root / 'normalization-journal.jsonl'
    for row in frozen_rows():
        result = qualify_one(row, imports[row['instance_id']])
        with journal.open('a', encoding='utf-8') as h:
            h.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + '\n')
            h.flush(); os.fsync(h.fileno())
        rows.append(result)
        print(json.dumps({'instance_id': result['instance_id'], 'role': result['role'], 'pass': result['exact_base_normalization_pass'], 'untracked': result.get('initial_untracked_count')}), flush=True)
    n = sum(bool(x['exact_base_normalization_pass']) for x in rows)
    out = {
        'schema_version': 1,
        'created_at_utc': now(),
        'status': 'FRESH2_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN' if n == 20 else 'HOLD_FRESH2_RUNTIME_CLEAN_REPAIR_INCOMPLETE',
        'qualified': n,
        'total': 20,
        'source_qualified': sum(x['role'] == 'source' and x['exact_base_normalization_pass'] for x in rows),
        'future_qualified': sum(x['role'] == 'future' and x['exact_base_normalization_pass'] for x in rows),
        'rows': rows,
        'provider_calls': 0,
        'scientific_source_tasks_used': 0,
        'future_task_executions': 0,
    }
    atomic_json(root / 'normalization-qualification.json', out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=DEFAULT)
    ap.add_argument('--phase', choices=('prepare', 'qualify'), required=True)
    a = ap.parse_args()
    result = {'prepare': prepare, 'qualify': qualify}[a.phase](a.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
