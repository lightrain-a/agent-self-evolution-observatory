from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import numpy as np

from . import p05_turnover_evidence_runtime as p05

PLAN = Path('/data/wyt/agent-self-evolution-p0-52-data/runs/p05-turnover-collapse-20260816/plan.json')


class P05TurnoverRuntimeTest(unittest.TestCase):
    def test_hidden_truth_ignores_task_bits(self):
        base = np.array([[1, 0, 1, 1, 0, 1, 0, 0, 0, 0]], dtype=np.int8)
        variants = np.repeat(base, 16, axis=0)
        variants[:, 6:] = np.array(
            [[(i >> j) & 1 for j in range(4)] for i in range(16)], dtype=np.int8
        )
        labels = p05.hidden_truth(variants)
        self.assertEqual(len(set(labels.tolist())), 1)

    def test_locked_truth_cannot_enter_evolution_or_post_update(self):
        evolve = set(inspect.signature(p05.evolve).parameters)
        update = set(inspect.signature(p05.post_update).parameters)
        self.assertFalse(any('truth' in x or 'locked' in x for x in evolve))
        self.assertFalse(any('truth' in x or 'locked' in x for x in update))

    def test_common_warmup_is_bitwise_deterministic(self):
        plan = p05.validate_plan(PLAN)
        a = p05.common_warmup(plan, 3)
        b = p05.common_warmup(plan, 3)
        self.assertTrue(np.array_equal(a.pop, b.pop))
        self.assertTrue(np.array_equal(a.w, b.w))
        self.assertEqual(a.warm_rows, b.warm_rows)

    def test_turnover_changes_replacement_count_not_budget(self):
        plan = p05.validate_plan(PLAN)
        common = p05.common_warmup(plan, 2)
        hi = p05.run_arm(plan, common, 2, 'high', 0.50, False)
        lo = p05.run_arm(plan, common, 2, 'low', 0.10, False)
        self.assertEqual(len(hi), len(lo))
        self.assertEqual([x['metric_update_count'] for x in hi], [x['metric_update_count'] for x in lo])
        self.assertGreater(hi[0]['replacement_count'], lo[0]['replacement_count'])

    def test_protocol_probe_passes_frozen_plan(self):
        probe = p05.protocol_probe(PLAN)
        self.assertTrue(probe['passed'], probe['checks'])
        self.assertTrue(all(probe['checks'].values()))

    def test_one_sided_sign_test(self):
        self.assertEqual(p05.sign_p([]), 1.0)
        self.assertAlmostEqual(p05.sign_p([1.0, 1.0, 1.0]), 0.125)
        self.assertGreater(p05.sign_p([1.0, -1.0]), 0.25)


if __name__ == '__main__':
    unittest.main()
