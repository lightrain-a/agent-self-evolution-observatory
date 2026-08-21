from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.d5_evaluation_aliasing_gemma_balanced import analyze_stage_a, analyze_stage_b
from research_pipeline.d5_state_sufficiency_f0 import ARMS


class D5EvaluationAliasingGemmaBalancedTest(unittest.TestCase):
    @staticmethod
    def _contract() -> dict:
        mids = ["m1", "m2", "m3", "m4"]
        return {
            "memory_pool": {"memory_ids": mids},
            "stage_a": {
                "episodes": 48,
                "tasks": [
                    {"target_family": "f1", "task_relpath": "a1"},
                    {"target_family": "f2", "task_relpath": "a2"},
                    {"target_family": "f3", "task_relpath": "a3"},
                    {"target_family": "f4", "task_relpath": "a4"},
                ],
            },
            "stage_b": {
                "tasks": [
                    {"target_family": "f1", "task_relpath": "b1"},
                    {"target_family": "f2", "task_relpath": "b2"},
                    {"target_family": "f3", "task_relpath": "b3"},
                    {"target_family": "f4", "task_relpath": "b4"},
                ],
            },
        }

    @staticmethod
    def _task_rows(task: str, triples: dict[str, tuple[int, int, int]]) -> list[dict]:
        rows = []
        for mid, (retrieved, placebo, no_memory) in triples.items():
            values = {"retrieved": retrieved, "placebo": placebo, "no-memory": no_memory}
            for arm in ARMS:
                rows.append({
                    "memory_id": mid,
                    "task_relpath": task,
                    "arm": arm,
                    "success": values[arm],
                    "actions": ["look"] if arm == "no-memory" else [f"{arm}-{mid}"],
                })
        return rows

    def test_frozen_v3_contract_uses_balanced_pool_cached_runtime_and_fresh_panel(self) -> None:
        c = json.loads(Path('generated/d5-evaluation-aliasing-gemma-balanced-v3-contract.json').read_text(encoding='utf-8'))
        self.assertEqual(c['experiment_id'], 'D5-EVALUATION-ALIASING-GEMMA-BALANCED-v3')
        self.assertEqual(c['runtime']['request_seed'], 20260822)
        self.assertTrue(c['runtime']['cache_identical_prompts'])
        self.assertTrue(c['runtime']['exclusive_transaction_lock_required'])
        self.assertEqual(len(c['memory_pool']['memory_ids']), 4)
        self.assertEqual({row['source_family'] for row in c['memory_pool']['memories']}, {
            'pick_and_place_simple', 'pick_clean_then_place_in_recep',
            'pick_cool_then_place_in_recep', 'pick_heat_then_place_in_recep',
        })
        self.assertTrue(all(row['candidate_role'] == 'heldout_candidate' for row in c['memory_pool']['memories']))
        self.assertGreaterEqual(len(c['task_selection']['eligible_target_families']), 4)
        self.assertEqual(len(c['stage_a']['tasks']), len(c['task_selection']['eligible_target_families']))
        self.assertEqual(len(c['stage_b']['tasks']), len(c['task_selection']['eligible_target_families']))
        all_tasks = [row['task_relpath'] for stage in ('stage_a', 'stage_b') for row in c[stage]['tasks']]
        for exposed_name in (
            'pick_and_place_simple-Pencil-None-Shelf-308',
            'pick_clean_then_place_in_recep-Cloth-None-CounterTop-424',
            'pick_cool_then_place_in_recep-Mug-None-Cabinet-10',
            'pick_and_place_simple-PepperShaker-None-Drawer-10',
        ):
            self.assertFalse(any(exposed_name in task for task in all_tasks))

    def test_partial_singletons_are_monotone_stop(self) -> None:
        c = self._contract()
        triples = {
            'm1': (0, 0, 0), 'm2': (1, 0, 0),
            'm3': (0, 1, 0), 'm4': (1, 1, 0),
        }
        result = analyze_stage_a(self._task_rows('a1', triples), c)
        self.assertEqual(result['status'], 'EARLY_STOP_NO_ALIAS_CLASS_REMAINS')
        self.assertFalse(result['stage_b_authorized'])
        self.assertEqual(result['remaining_stage_a_rows_not_required'], 36)

    def test_full_nondegenerate_alias_opens_stage_b(self) -> None:
        c = self._contract()
        rows = []
        for task, values in [
            ('a1', {'m1': (1,1,1), 'm2': (1,1,1), 'm3': (0,0,1), 'm4': (1,0,1)}),
            ('a2', {'m1': (0,0,0), 'm2': (0,0,0), 'm3': (1,0,0), 'm4': (0,1,0)}),
            ('a3', {'m1': (1,1,1), 'm2': (1,1,1), 'm3': (0,1,1), 'm4': (1,0,1)}),
            ('a4', {'m1': (0,0,0), 'm2': (0,0,0), 'm3': (1,1,0), 'm4': (0,1,0)}),
        ]:
            rows.extend(self._task_rows(task, values))
        result = analyze_stage_a(rows, c)
        self.assertEqual(result['decision'], 'PASS_OPEN_SEALED_STAGE_B')
        self.assertEqual(result['qualified_alias_classes'][0]['members'], ['m1', 'm2'])
        self.assertTrue(result['qualified_alias_classes'][0]['nondegenerate'])

    def test_complete_floor_alias_is_not_qualified(self) -> None:
        c = self._contract()
        rows = []
        for task in ('a1','a2','a3','a4'):
            rows.extend(self._task_rows(task, {mid:(0,0,0) for mid in ('m1','m2','m3','m4')}))
        result = analyze_stage_a(rows, c)
        self.assertEqual(result['decision'], 'STOP_GEMMA_BALANCED_NO_NONDEGENERATE_ALIAS')
        self.assertFalse(result['stage_b_authorized'])

    def test_stage_b_go_requires_two_future_families(self) -> None:
        c = self._contract()
        stage_a = {"qualified_alias_classes": [{"alias_id":"A1","members":["m1","m2"],"nondegenerate":True}]}
        rows = []
        for index, task in enumerate(('b1','b2','b3','b4')):
            for mid in ('m1','m2'):
                for arm in ARMS:
                    success = int(arm == 'retrieved' and mid == 'm2' and index in {0,1})
                    rows.append({"memory_id":mid,"task_relpath":task,"arm":arm,"success":success,"actions":["look"] if arm=='no-memory' else [arm]})
        result = analyze_stage_b(rows, c, stage_a)
        self.assertEqual(result['decision'], 'GO_PROSPECTIVE_CONFIRMATION')
        self.assertEqual(result['go_alias_classes'], ['A1'])


if __name__ == '__main__':
    unittest.main()
