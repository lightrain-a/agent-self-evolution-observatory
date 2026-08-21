from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.d5_evaluation_aliasing_protocol import analyze_stage_a, analyze_stage_b, compile_contract
from research_pipeline.d5_state_sufficiency_f0 import ARMS, MEMORY_IDS


class D5EvaluationAliasingProtocolTest(unittest.TestCase):
    @staticmethod
    def _rows_for_task(task: str, triples: dict[str, tuple[int, int, int]]) -> list[dict]:
        rows = []
        for mid in MEMORY_IDS:
            retrieved, placebo, no_memory = triples[mid]
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

    @staticmethod
    def _contract() -> dict:
        return {
            "stage_a": {
                "episodes": 27,
                "tasks": [
                    {"target_family": "f1", "task_relpath": "a1"},
                    {"target_family": "f2", "task_relpath": "a2"},
                    {"target_family": "f3", "task_relpath": "a3"},
                ],
            },
            "stage_b": {
                "episodes": 27,
                "tasks": [
                    {"target_family": "f1", "task_relpath": "b1"},
                    {"target_family": "f2", "task_relpath": "b2"},
                    {"target_family": "f3", "task_relpath": "b3"},
                ],
                "go_min_divergent_tasks": 2,
                "go_min_divergent_target_families": 2,
            },
        }

    def test_superseded_qwen_freeze_still_uses_currently_unexposed_tasks(self) -> None:
        stored = json.loads(Path('generated/d5-evaluation-aliasing-qwen-v2-contract.json').read_text(encoding='utf-8'))
        supersession = json.loads(Path('generated/d5-evaluation-aliasing-qwen-v2-supersession.json').read_text(encoding='utf-8'))
        self.assertEqual(stored['status'], 'FROZEN_BEFORE_COMMON_PANEL_OUTCOMES')
        self.assertEqual(supersession['outcome_calls_executed'], 0)
        self.assertEqual(supersession['superseded_contract_material_sha256'], stored['contract_sha256'])
        self.assertEqual(len(stored['stage_a']['tasks']), 3)
        self.assertEqual(len(stored['stage_b']['tasks']), 3)

    def test_stage_a_mismatch_stops_immediately(self) -> None:
        contract = self._contract()
        same = {mid: (1, 1, 1) for mid in MEMORY_IDS}
        mismatch = {mid: (0, 0, 0) for mid in MEMORY_IDS}
        mismatch[MEMORY_IDS[1]] = (0, 1, 0)
        rows = self._rows_for_task('a1', same) + self._rows_for_task('a2', mismatch)
        result = analyze_stage_a(rows, contract)
        self.assertEqual(result['decision'], 'STOP_QWEN_REALIZATION_NO_COMMON_EVALUATION_EQUIVALENCE')
        self.assertFalse(result['stage_b_authorized'])
        self.assertEqual(result['remaining_rows_not_required'], 9)

    def test_stage_a_complete_floor_is_rejected(self) -> None:
        contract = self._contract()
        rows = []
        floor = {mid: (0, 0, 0) for mid in MEMORY_IDS}
        for task in ('a1', 'a2', 'a3'):
            rows.extend(self._rows_for_task(task, floor))
        result = analyze_stage_a(rows, contract)
        self.assertEqual(result['decision'], 'STOP_QWEN_REALIZATION_DEGENERATE_CURRENT_SIGNATURE')
        self.assertFalse(result['nondegenerate'])
        self.assertFalse(result['stage_b_authorized'])

    def test_stage_a_nondegenerate_common_signature_opens_stage_b(self) -> None:
        contract = self._contract()
        rows = []
        for task, value in [('a1', 1), ('a2', 0), ('a3', 1)]:
            same = {mid: (value, value, value) for mid in MEMORY_IDS}
            rows.extend(self._rows_for_task(task, same))
        result = analyze_stage_a(rows, contract)
        self.assertEqual(result['decision'], 'PASS_OPEN_SEALED_STAGE_B')
        self.assertTrue(result['nondegenerate'])
        self.assertTrue(result['stage_b_authorized'])

    def test_stage_b_requires_two_tasks_across_two_families(self) -> None:
        contract = self._contract()
        rows = []
        for task_index, task in enumerate(('b1', 'b2', 'b3')):
            for memory_index, mid in enumerate(MEMORY_IDS):
                for arm in ARMS:
                    success = int(arm == 'retrieved' and task_index in {0, 1} and memory_index == 2)
                    rows.append({
                        'memory_id': mid,
                        'task_relpath': task,
                        'arm': arm,
                        'success': success,
                        'actions': ['look'] if arm == 'no-memory' else [arm],
                    })
        result = analyze_stage_b(rows, contract)
        self.assertEqual(result['decision'], 'GO_PROSPECTIVE_CONFIRMATION')
        self.assertEqual(result['divergent_task_count'], 2)
        self.assertEqual(result['divergent_target_families'], ['f1', 'f2'])


if __name__ == '__main__':
    unittest.main()
