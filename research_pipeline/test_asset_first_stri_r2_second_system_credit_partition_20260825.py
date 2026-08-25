from __future__ import annotations

import unittest
from pathlib import Path

from .asset_first_stri_r2_second_system_credit_partition_20260825 import build

RETHINK = Path('/data/wyt/agent2-asset-first-external/rethinkskill-r2-20260825')
SKILLSVOTE = Path('/data/wyt/agent2-asset-first-external/skills-vote-r2-20260825')


class STRIR2SecondSystemCreditPartitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build(RETHINK, SKILLSVOTE)

    def test_rethinkskill_is_fail_closed_as_same_object_replication(self) -> None:
        row = self.state['rethinkskill']
        self.assertFalse(row['qualifies_as_identity_partition_realization'])
        self.assertEqual(row['disposition'], 'CLOSEST_WORK_CONTROL_NOT_PARALLEL_IDENTITY_BUCKET_REALIZATION')

    def test_skillsvote_request_topology_counterfactual(self) -> None:
        sv = self.state['skillsvote']
        self.assertTrue(sv['counterfactual_pass'])
        h = sv['headline']
        self.assertEqual((h['canonical_edit_requests'], h['split_edit_requests'], h['quotient_edit_requests']), (1, 2, 1))
        self.assertEqual(h['canonical_evidence_per_request'], [8])
        self.assertEqual(h['split_evidence_per_request'], [4, 4])
        self.assertEqual(h['quotient_evidence_per_request'], [8])
        self.assertEqual(len(set(sv['semantic_payload_hashes_without_skill_link'].values())), 1)

    def test_cross_system_scope_is_structural_only(self) -> None:
        self.assertEqual(self.state['decision'], 'QUALIFY_SKILLSVOTE_REQUEST_PARTITION_ANALOGUE_ONLY')
        self.assertFalse(self.state['second_exact_phase_law_replication'])
        self.assertTrue(self.state['second_structural_partition_before_update_analogue'])
        self.assertEqual(self.state['new_model_calls'], 0)
        self.assertEqual(self.state['new_agent_runs'], 0)
        self.assertFalse(self.state['claim_expansion'])
        self.assertFalse(self.state['scientific_authority'])


if __name__ == '__main__':
    unittest.main()
