from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any

from research_pipeline import asset_first_stri_skillrl_fixed_task_p0d as p0d
from research_pipeline import asset_first_stri_skillrl_final_policy_p0e_calibration as p0e

EXPERIMENT_ID = p0e.EXPERIMENT_ID
STAGE = 'local-causal'
GPU_CAP_SECONDS_PER_SEED = 3600.0
TOTAL_GPU_CAP_SECONDS = 7200.0


def atomic(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def require_calibration_go(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError('missing-calibration-analysis')
    d = load(path)
    if d.get('experiment_id') != EXPERIMENT_ID or d.get('stage') != 'calibration':
        raise ValueError('calibration-analysis-identity')
    if d.get('outcome') != 'GO_COMPETENT_POLICY_SUPPORT' or d.get('qualified_support') is not True:
        raise ValueError(f"calibration-not-go:{d.get('outcome')}")
    metrics = d.get('metrics') or {}
    success = int(metrics.get('pristine_success_count') or 0)
    families = int(metrics.get('families_with_success_count') or 0)
    if not 4 <= success <= 20 or families < 3:
        raise ValueError('calibration-go-metrics-inconsistent')
    return {
        'path': str(path),
        'sha256': p0e.sha(path),
        'outcome': d.get('outcome'),
        'evidence_manifest_sha256': d.get('evidence_manifest_sha256'),
        'pristine_success_count': success,
        'families_with_success_count': families,
    }


def local_env_probe(source: pathlib.Path, panel: dict[str, Any], root: pathlib.Path) -> dict[str, Any]:
    row = panel['local_causal_tasks'][0]
    game = str(pathlib.Path(__import__('os').environ.get('ALFWORLD_DATA', '/data/wyt/agent-self-evolution-p0-52-data/alfworld')) / 'json_2.1.1/valid_unseen' / row['relative_gamefile'])
    runner = p0d.load_world(source, root)
    envs = []
    states = []
    try:
        for _ in range(2):
            e = runner.build_env('eval_out_of_distribution', [game])
            envs.append(e)
            o, info = e.reset()
            states.append((str(o[0]), p0d.info_commands(info)))
        if states[0] != states[1]:
            raise ValueError('local-env-reset-replay')
        action = next((x for x in states[0][1] if x != 'help'), None)
        if not action:
            raise ValueError('local-env-no-action')
        after = []
        for e in envs:
            o, r, done, info = e.step([action])
            after.append((str(o[0]), float(r[0]), bool(done[0]), p0d.info_won(info), p0d.info_commands(info)))
        if after[0] != after[1]:
            raise ValueError('local-env-step-replay')
        return {'gamefile': game, 'action': action, 'reset_equal': True, 'one_step_equal': True}
    finally:
        for e in envs:
            close = getattr(e, 'close', None)
            if callable(close):
                close()


def preflight(project: pathlib.Path, source: pathlib.Path, model: pathlib.Path, root: pathlib.Path, calibration_analysis: pathlib.Path) -> dict[str, Any]:
    calibration = require_calibration_go(calibration_analysis)
    controls = p0e.validate_controls(project, model, full_hash=True)
    panel = load(project / 'generated' / p0e.PANEL)
    local = panel.get('local_causal_tasks') or []
    if len(local) != 12:
        raise ValueError('local-panel-cardinality')
    replay = p0d.representation_replay(source, root)
    env = local_env_probe(source, panel, root)
    out = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'stage': STAGE,
        'calibration_gate': calibration,
        **controls,
        'representation_replay': replay,
        'environment_replay': env,
        'local_causal_units': 24,
        'arm_episodes': 96,
        'passed': True,
        'scientific_authority': False,
    }
    atomic(root / 'preflight.json', out)
    return out


def run_shard(project: pathlib.Path, source: pathlib.Path, model: pathlib.Path, root: pathlib.Path, calibration_analysis: pathlib.Path, seed_index: int, gpu_cap: float = GPU_CAP_SECONDS_PER_SEED) -> dict[str, Any]:
    if seed_index not in (0, 1):
        raise ValueError('seed-index')
    ctrl = preflight(project, source, model, root, calibration_analysis)
    SkillsOnlyMemory, SimpleMemory, prompts, projection = p0d.load_author_modules(source)
    banks = p0d.materialize_banks(source, root / 'banks')
    tasks = load(project / 'generated' / p0e.PANEL)['local_causal_tasks']
    seed = p0e.DECODE_SEEDS[seed_index]
    start = time.monotonic()
    policy = p0d.VllmPolicy(model)
    deadline = start + gpu_cap
    raw = root / f'causal-shard-{seed_index}.jsonl'
    rows: list[dict[str, Any]] = []
    units: list[str] = []
    status = 'COMPLETE'
    with raw.open('w', encoding='utf-8') as fh:
        for idx, task in enumerate(tasks, 1):
            u = p0d.run_unit(p0d.load_world(source, root), policy, SkillsOnlyMemory, SimpleMemory, prompts, projection, banks, task, seed, deadline)
            if u.get('status') != 'COMPLETE':
                status = str(u.get('status'))
                break
            for row in u['rows']:
                fh.write(json.dumps(row, ensure_ascii=False) + '\n')
                rows.append(row)
            fh.flush()
            units.append(u['unit_id'])
            print(json.dumps({'stage': STAGE, 'completed_units': idx, 'planned_units': 12, 'seed_index': seed_index, 'gpu_allocation_seconds': round(time.monotonic() - start, 2)}), flush=True)
    elapsed = time.monotonic() - start
    out = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'stage': STAGE,
        'contract_sha256': ctrl['contract_sha256'],
        'calibration_analysis_sha256': ctrl['calibration_gate']['sha256'],
        'seed_index': seed_index,
        'decode_seed': seed,
        'status': status,
        'planned_units': 12,
        'completed_units': len(units),
        'unit_ids': units,
        'raw_rows_path': str(raw),
        'gpu_allocation_seconds': round(elapsed, 3),
        'gpu_hours': round(elapsed / 3600, 6),
        'within_budget': elapsed <= gpu_cap and status == 'COMPLETE',
        'model_revision': p0e.POLICY_REVISION,
        'scientific_authority': False,
    }
    atomic(root / f'causal-shard-{seed_index}.json', out)
    return out


def aggregate(project: pathlib.Path, shards: list[pathlib.Path], out: pathlib.Path) -> dict[str, Any]:
    panel = load(project / 'generated' / p0e.PANEL)
    expected = {p0e.uid(t, s) for t in panel['local_causal_tasks'] for s in p0e.DECODE_SEEDS}
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    cost = 0.0
    meta = []
    calibration_hashes = set()
    for path in shards:
        d = load(path)
        cost += float(d.get('gpu_allocation_seconds') or 0)
        calibration_hashes.add(str(d.get('calibration_analysis_sha256') or ''))
        meta.append({'path': str(path), 'sha256': p0e.sha(path), 'status': d.get('status'), 'seed_index': d.get('seed_index'), 'completed_units': d.get('completed_units')})
        raw = pathlib.Path(d['raw_rows_path'])
        rows.extend(json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip())
        seen.update(d.get('unit_ids') or [])
    raw_out = out.with_suffix('.jsonl')
    raw_out.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    status = 'COMPLETE' if seen == expected and len(rows) == 96 and all(x['status'] == 'COMPLETE' for x in meta) and cost <= TOTAL_GPU_CAP_SECONDS and len(calibration_hashes) == 1 and '' not in calibration_hashes else 'INCOMPLETE'
    payload = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'stage': STAGE,
        'status': status,
        'expected_units': 24,
        'completed_units': len(seen),
        'unit_set_exact': seen == expected,
        'rows': len(rows),
        'shards': meta,
        'calibration_analysis_sha256': next(iter(calibration_hashes)) if len(calibration_hashes) == 1 else None,
        'gpu_allocation_seconds': round(cost, 3),
        'gpu_hours': round(cost / 3600, 6),
        'within_budget': cost <= TOTAL_GPU_CAP_SECONDS,
        'raw_rows_path': str(raw_out),
        'scientific_authority': False,
    }
    atomic(out, payload)
    return payload


def analyze(agg_path: pathlib.Path, out: pathlib.Path) -> dict[str, Any]:
    agg = load(agg_path)
    raw = pathlib.Path(agg['raw_rows_path'])
    rows = [json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip()]
    groups: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row['unit_id'], {})[row['arm']] = row
    errors: list[str] = []
    if agg.get('status') != 'COMPLETE' or not agg.get('within_budget') or agg.get('completed_units') != 24:
        errors.append('aggregate-incomplete-or-over-budget')
    if len(groups) != 24:
        errors.append('unit-count')
    for unit, g in groups.items():
        if set(g) != set(p0d.ARMS):
            errors.append(f'arm-set:{unit}')
            continue
        a, b, c, d = (g[x] for x in p0d.ARMS)
        if b['general_semantic_set_sha256'] == a['general_semantic_set_sha256']:
            errors.append(f'treatment-no-semantic-displacement:{unit}')
        if c['general_semantic_set_sha256'] != a['general_semantic_set_sha256']:
            errors.append(f'placebo-semantic-change:{unit}')
        if c['memory_prompt_sha256'] == a['memory_prompt_sha256']:
            errors.append(f'placebo-prompt-not-changed:{unit}')
        if d['general_semantic_set_sha256'] != a['general_semantic_set_sha256'] or d['memory_prompt_sha256'] != a['memory_prompt_sha256']:
            errors.append(f'quotient-not-restored:{unit}')
        if d['projected_actions_sha256'] != a['projected_actions_sha256'] or d['response_sha256s'] != a['response_sha256s'] or d['won'] != a['won'] or d['steps'] != a['steps']:
            errors.append(f'A-D-trajectory-not-identical:{unit}')
    units = sorted(groups)
    complete_units = [u for u in units if set(groups[u]) == set(p0d.ARMS)]
    A = [int(groups[u]['A_pristine']['won']) for u in complete_units]
    B = [int(groups[u]['B_displacement_clone']['won']) for u in complete_units]
    C = [int(groups[u]['C_identity_placebo']['won']) for u in complete_units]
    D = [int(groups[u]['D_exact_quotient']['won']) for u in complete_units]
    pristine = sum(A)
    a_success_families = sorted({groups[u]['A_pristine']['task_family'] for u, a in zip(complete_units, A) if a == 1})
    if len(A) == 24 and not 4 <= pristine <= 20:
        errors.append(f'pristine-success-headroom:{pristine}')
    if len(A) == 24 and len(a_success_families) < 3:
        errors.append(f'pristine-success-family-support:{len(a_success_families)}')
    qualified = not errors and len(A) == 24

    def rate(x: list[int]) -> float:
        return sum(x) / len(x) if x else float('nan')

    def disagreement(x: list[int], y: list[int]) -> float:
        return sum(a != b for a, b in zip(x, y)) / len(x) if x else float('nan')

    p, b01, b10 = p0d.mcnemar(A, B) if len(A) == 24 else (1.0, 0, 0)
    rA, rB, rC, rD = map(rate, (A, B, C, D))
    dB, dC, dD = disagreement(A, B), disagreement(A, C), disagreement(A, D)
    flip_families = sorted({groups[u]['A_pristine']['task_family'] for u, a, b in zip(complete_units, A, B) if a != b}) if len(A) == 24 else []
    metrics = {
        'pristine_success_count': pristine,
        'families_with_A_success_count': len(a_success_families),
        'families_with_A_success': a_success_families,
        'success_rate': {'A_pristine': rA, 'B_displacement_clone': rB, 'C_identity_placebo': rC, 'D_exact_quotient': rD},
        'B_minus_A_success_rate': rB - rA if A else None,
        'C_minus_A_success_rate': rC - rA if A else None,
        'D_minus_A_success_rate': rD - rA if A else None,
        'paired_disagreement': {'B_vs_A': dB, 'C_vs_A': dC, 'D_vs_A': dD},
        'B_vs_A_disagreement_minus_C_vs_A': dB - dC if A else None,
        'B_vs_A_mcnemar_p': p,
        'discord_A0_B1': b01,
        'discord_A1_B0': b10,
        'family_replicated_flip_count': len(flip_families),
        'families_with_B_vs_A_flip': flip_families,
    }
    go = bool(qualified and p < 0.05 and abs(rB - rA) >= 0.125 and dB - dC >= 0.125 and dD <= 0.05 and abs(rD - rA) <= 0.05 and len(flip_families) >= 2)
    stop = bool(qualified and p >= 0.05 and dB <= dC + 0.05 and dD <= 0.05 and abs(rD - rA) <= 0.05)
    outcome = 'GO_C4_FIXED_POLICY_DOWNSTREAM_EVIDENCE' if go else ('STOP_FIXED_POLICY_DYNAMIC_BRIDGE' if stop else 'INCONCLUSIVE')
    material = {'aggregate_sha256': p0e.sha(agg_path), 'raw_sha256': p0e.sha(raw), 'calibration_analysis_sha256': agg.get('calibration_analysis_sha256'), 'outcome': outcome, 'metrics': metrics, 'qualification_errors': errors}
    payload = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'stage': STAGE,
        'outcome': outcome,
        'qualified': qualified,
        'qualification_errors': errors,
        'qualified_units': len(A) if qualified else 0,
        'metrics': metrics,
        'aggregate_cost': {'gpu_allocation_seconds': agg.get('gpu_allocation_seconds'), 'gpu_hours': agg.get('gpu_hours'), 'within_budget': agg.get('within_budget')},
        'calibration_analysis_sha256': agg.get('calibration_analysis_sha256'),
        'evidence_manifest_sha256': p0d.htext(json.dumps(material, sort_keys=True, separators=(',', ':'))),
        'claim_if_go': 'Supports only C4 final-policy downstream representation sensitivity on the SkillRL exact-clone subclass; it does not establish SQC superiority or partial-overlap behavior.',
        'claim_if_stop': 'Rejects only the exact-clone downstream bridge under the single author final RL policy; C1/C2 STRI remain unchanged.',
        'scientific_authority': False,
    }
    atomic(out, payload)
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=('preflight', 'run-shard', 'aggregate', 'analyze'))
    ap.add_argument('--project', type=pathlib.Path, default=pathlib.Path('.'))
    ap.add_argument('--source', type=pathlib.Path)
    ap.add_argument('--model', type=pathlib.Path)
    ap.add_argument('--run-root', type=pathlib.Path)
    ap.add_argument('--calibration-analysis', type=pathlib.Path)
    ap.add_argument('--seed-index', type=int)
    ap.add_argument('--gpu-cap-seconds', type=float, default=GPU_CAP_SECONDS_PER_SEED)
    ap.add_argument('--shard-run', type=pathlib.Path, action='append')
    ap.add_argument('--aggregate', type=pathlib.Path)
    ap.add_argument('--output', type=pathlib.Path)
    a = ap.parse_args()
    if a.command == 'preflight':
        if not all((a.source, a.model, a.run_root, a.calibration_analysis)):
            raise SystemExit('--source/--model/--run-root/--calibration-analysis required')
        result = preflight(a.project, a.source, a.model, a.run_root, a.calibration_analysis)
    elif a.command == 'run-shard':
        if not all((a.source, a.model, a.run_root, a.calibration_analysis)) or a.seed_index is None:
            raise SystemExit('--source/--model/--run-root/--calibration-analysis/--seed-index required')
        result = run_shard(a.project, a.source, a.model, a.run_root, a.calibration_analysis, a.seed_index, a.gpu_cap_seconds)
    elif a.command == 'aggregate':
        if not a.shard_run or not a.output:
            raise SystemExit('--shard-run/--output required')
        result = aggregate(a.project, a.shard_run, a.output)
    else:
        if not a.aggregate or not a.output:
            raise SystemExit('--aggregate/--output required')
        result = analyze(a.aggregate, a.output)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
