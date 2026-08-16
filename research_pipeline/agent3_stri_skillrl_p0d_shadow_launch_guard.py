from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

PROJECT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path('/data/wyt/evidence-substrates/SkillRL-8e66726-runnable')
MODEL = pathlib.Path('/data/wyt/models/SkillRL-Alfworld-7B-SFT-ba9c962/checkpoint-140')
PYTHON = pathlib.Path('/data/wyt/envs/stri-vllm311/bin/python')
BASE_RUN = pathlib.Path('/data/wyt/agent-self-evolution-observatory/runs/agent3-stri-skillrl-p0d-shadow-20260816')
RUNNER = PROJECT / 'research_pipeline/asset_first_stri_skillrl_fixed_task_p0d.py'
GPU_CANDIDATES = tuple(range(8))
SESSIONS = ('ag3-stri-p0d-s0', 'ag3-stri-p0d-s1')
MODEL_SHARDS = {
    'model-00001-of-00009.safetensors': (1886423520, 'c2474c3652851fb82b796b5ed8b2c1ac44308fd783ffe418a923d5e1f2ddf36f'),
    'model-00002-of-00009.safetensors': (1864467800, 'a3664c32d79e954ba3e53999d932b4e75525e5918ae12b88f01d821180c61a21'),
    'model-00003-of-00009.safetensors': (1864467800, 'c03d1ec906536dc0f451c537c65524e1822ccbb406b7957b1ff3b62caa75a605'),
    'model-00004-of-00009.safetensors': (1864467824, '13d6885bcaf3d0b7e2877625d71807222c86975151cd570b11b541c9e74a09a0'),
    'model-00005-of-00009.safetensors': (1864467848, 'a518f9e0580dff92b9fb6f939e741319132c1587fc266ff42db017641a489ad4'),
    'model-00006-of-00009.safetensors': (1864467848, 'cf05a5bbf89029d1a05e75ccc005445c66e633729fbb235e18835ec14214af6f'),
    'model-00007-of-00009.safetensors': (1864467848, '21cae2d49adbb4971e20ba7b9b6d40b65c5809070e3cc849e65a2e0135e7439c'),
    'model-00008-of-00009.safetensors': (1068046456, '04a9e70ece01bacb30daa7d43b4f3f32eba139ac6fe26f46ed6642af3e0d1ff6'),
    'model-00009-of-00009.safetensors': (1089994880, '06006972c3be88e8a44fe21cfe2b0472b130780c781a741f8f90f1fe5ba3aae2'),
}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def model_ready(full_hash: bool) -> tuple[bool, list[dict]]:
    rows = []
    ok = True
    for name, (size, expected) in MODEL_SHARDS.items():
        path = MODEL / name
        exists = path.is_file()
        actual_size = path.stat().st_size if exists else None
        row = {'file': name, 'exists': exists, 'size': actual_size, 'expected_size': size}
        if not exists or actual_size != size:
            ok = False
        elif full_hash:
            got = sha256(path)
            row['sha256'] = got
            row['expected_sha256'] = expected
            if got != expected:
                ok = False
        rows.append(row)
    return ok, rows


def gpu_compute_pids(gpu: int) -> list[int]:
    uuid = subprocess.check_output(
        ['nvidia-smi', '-i', str(gpu), '--query-gpu=uuid', '--format=csv,noheader'], text=True
    ).strip()
    raw = subprocess.check_output(
        ['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'], text=True
    )
    out = []
    for line in raw.splitlines():
        fields = [x.strip() for x in line.split(',')]
        if len(fields) == 2 and fields[0] == uuid:
            out.append(int(fields[1]))
    return out


def tmux_exists(name: str) -> bool:
    return subprocess.run(['tmux', 'has-session', '-t', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def state(full_hash: bool) -> dict:
    ready, model_rows = model_ready(full_hash)
    gpu = {str(i): gpu_compute_pids(i) for i in GPU_CANDIDATES}
    free = [i for i in GPU_CANDIDATES if not gpu[str(i)]]
    runs = {}
    for seed in (0, 1):
        root = BASE_RUN / f'seed{seed}'
        runs[str(seed)] = {
            'root': str(root),
            'result_exists': (root / f'shard-{seed}.json').exists(),
            'raw_exists': (root / f'shard-{seed}.jsonl').exists(),
            'tmux': tmux_exists(SESSIONS[seed]),
        }
    pending = [
        seed for seed in (0, 1)
        if not runs[str(seed)]['result_exists']
        and not runs[str(seed)]['raw_exists']
        and not runs[str(seed)]['tmux']
    ]
    blocked_partial = [
        seed for seed in (0, 1)
        if runs[str(seed)]['raw_exists'] and not runs[str(seed)]['result_exists']
    ]
    return {
        'model_ready': ready,
        'model_rows': model_rows,
        'gpu_compute_pids': gpu,
        'free_gpus': free,
        'runs': runs,
        'pending_seeds': pending,
        'blocked_partial_seeds': blocked_partial,
        'launchable': ready and bool(free) and bool(pending) and not blocked_partial,
        'scientific_authority': False,
    }


def launch() -> dict:
    s = state(full_hash=True)
    if not s['launchable']:
        raise SystemExit(json.dumps({'launched': False, 'state': s}, ensure_ascii=False))
    BASE_RUN.mkdir(parents=True, exist_ok=True)
    launched = []
    selected_seeds = s['pending_seeds'][:len(s['free_gpus'])]
    selected_gpus = s['free_gpus'][:len(selected_seeds)]
    for seed, gpu in zip(selected_seeds, selected_gpus):
        session = SESSIONS[seed]
        # Recheck immediately before launch. External LLMPrint workers do not
        # honor our local lock and may occupy a GPU between the status scan and
        # engine creation. A newly occupied GPU is an infrastructure block, not
        # a scientific outcome, so fail closed before creating the run root.
        if gpu_compute_pids(gpu):
            continue
        root = BASE_RUN / f'seed{seed}'
        root.mkdir(parents=True, exist_ok=False)
        log = root / 'run.log'
        cmd = (
            f"CUDA_VISIBLE_DEVICES={gpu} ALFWORLD_DATA=/data/wyt/agent-self-evolution-p0-52-data/alfworld "
            f"P0_EXTRA_SITE=/data/wyt/envs/agent_evolution_p0_site_52 "
            f"{PYTHON} {RUNNER} run-shard --project {PROJECT} --source {SOURCE} --model {MODEL} "
            f"--run-root {root} --seed-index {seed} --gpu-cap-seconds 3600 > {log} 2>&1"
        )
        subprocess.check_call(['tmux', 'new-session', '-d', '-s', session, 'bash', '-lc', cmd])
        launched.append({'seed': seed, 'gpu': gpu, 'session': session, 'run_root': str(root), 'log': str(log)})
    return {'launched': True, 'runs': launched, 'scientific_authority': False}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=('status', 'launch'))
    ap.add_argument('--full-hash', action='store_true')
    args = ap.parse_args()
    if args.command == 'status':
        print(json.dumps(state(args.full_hash), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(launch(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
