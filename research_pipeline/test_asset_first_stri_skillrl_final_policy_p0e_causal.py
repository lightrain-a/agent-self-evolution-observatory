from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from research_pipeline import asset_first_stri_skillrl_final_policy_p0e_causal as causal


class SkillRLP0ECausalTest(unittest.TestCase):
    def _write_json(self, path: pathlib.Path, payload: dict) -> None:
        path.write_text(json.dumps(payload) + '\n', encoding='utf-8')

    def test_calibration_gate_requires_go(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / 'analysis.json'
            self._write_json(p, {
                'experiment_id': causal.EXPERIMENT_ID,
                'stage': 'calibration',
                'outcome': 'STOP_NO_COMPETENT_POLICY_SUPPORT',
                'qualified_support': False,
                'metrics': {'pristine_success_count': 1, 'families_with_success_count': 1},
                'evidence_manifest_sha256': 'x',
            })
            with self.assertRaisesRegex(ValueError, 'calibration-not-go'):
                causal.require_calibration_go(p)

    def test_calibration_gate_accepts_consistent_go(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / 'analysis.json'
            self._write_json(p, {
                'experiment_id': causal.EXPERIMENT_ID,
                'stage': 'calibration',
                'outcome': 'GO_COMPETENT_POLICY_SUPPORT',
                'qualified_support': True,
                'metrics': {'pristine_success_count': 8, 'families_with_success_count': 4},
                'evidence_manifest_sha256': 'evidence',
            })
            got = causal.require_calibration_go(p)
            self.assertEqual(got['pristine_success_count'], 8)
            self.assertEqual(got['families_with_success_count'], 4)

    def _row(self, unit: str, family: str, arm: str, won: int, *, a_sem: str = 'semA') -> dict:
        sem = 'semB' if arm == 'B_displacement_clone' else a_sem
        mem = 'mpC' if arm == 'C_identity_placebo' else ('mpB' if arm == 'B_displacement_clone' else 'mpA')
        action = f'action-{unit}'
        response = [f'resp-{unit}']
        return {
            'unit_id': unit,
            'task_family': family,
            'arm': arm,
            'won': won,
            'general_semantic_set_sha256': sem,
            'memory_prompt_sha256': mem,
            'projected_actions_sha256': action,
            'response_sha256s': response,
            'steps': 3,
        }

    def _analyze(self, families: list[str], a_wins: list[int], b_wins: list[int]):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            raw = root / 'aggregate.jsonl'
            rows = []
            for i in range(24):
                unit = f'u{i:02d}'
                family = families[i]
                A = int(a_wins[i])
                B = int(b_wins[i])
                rows.extend([
                    self._row(unit, family, 'A_pristine', A),
                    self._row(unit, family, 'B_displacement_clone', B),
                    self._row(unit, family, 'C_identity_placebo', A),
                    self._row(unit, family, 'D_exact_quotient', A),
                ])
            raw.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
            agg = root / 'aggregate.json'
            self._write_json(agg, {
                'experiment_id': causal.EXPERIMENT_ID,
                'stage': causal.STAGE,
                'status': 'COMPLETE',
                'completed_units': 24,
                'within_budget': True,
                'gpu_allocation_seconds': 100.0,
                'gpu_hours': 0.03,
                'calibration_analysis_sha256': 'cal-sha',
                'raw_rows_path': str(raw),
            })
            out = root / 'analysis.json'
            result = causal.analyze(agg, out)
            return result

    def test_go_requires_treatment_beyond_placebo(self) -> None:
        families = [f'f{i // 4}' for i in range(24)]
        A = [1] * 12 + [0] * 12
        B = A.copy()
        for i in range(6):
            B[i] = 0
        result = self._analyze(families, A, B)
        self.assertTrue(result['qualified'])
        self.assertEqual(result['outcome'], 'GO_C4_FIXED_POLICY_DOWNSTREAM_EVIDENCE')
        self.assertLess(result['metrics']['B_vs_A_mcnemar_p'], 0.05)
        self.assertGreaterEqual(result['metrics']['B_vs_A_disagreement_minus_C_vs_A'], 0.125)
        self.assertGreaterEqual(result['metrics']['family_replicated_flip_count'], 2)

    def test_family_support_is_required_for_qualification(self) -> None:
        families = ['only-family'] * 4 + [f'f{i}' for i in range(20)]
        A = [1] * 4 + [0] * 20
        B = A.copy()
        result = self._analyze(families, A, B)
        self.assertFalse(result['qualified'])
        self.assertIn('pristine-success-family-support:1', result['qualification_errors'])
        self.assertEqual(result['outcome'], 'INCONCLUSIVE')


if __name__ == '__main__':
    unittest.main()
