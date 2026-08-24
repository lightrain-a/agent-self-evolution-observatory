from __future__ import annotations
import json, unittest
from pathlib import Path

CK=Path('generated/d2-failure-memory-provenance-l2b-r19-partial-checkpoint-r30.json')
CSV=Path('generated/d2-failure-memory-provenance-l2b-r19-csv-durability-r30.json')
R29=Path('generated/d2-failure-memory-provenance-l2b-r19-seq026-preexposure-retry-r29.json')

class TestR19CheckpointR30(unittest.TestCase):
    def test_r30_identity_retry_chain_and_no_interim(self):
        ck=json.loads(CK.read_text(encoding='utf-8')); csv=json.loads(CSV.read_text(encoding='utf-8')); r29=json.loads(R29.read_text(encoding='utf-8'))
        self.assertEqual(ck['receipt_id'],'D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PARTIAL-CHECKPOINT-R30')
        self.assertEqual(csv['receipt_id'],'D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-CSV-DURABILITY-R30')
        self.assertEqual(r29['status'],'SEQ026_PREEXPOSURE_RESET_FAILURE_EXACT_RETRY_CONSUMED_THEN_COMPLETE')
        self.assertEqual(ck['execution']['episodes_complete'],28); self.assertEqual(ck['execution']['complete_independent_tasks'],7); self.assertEqual(ck['execution']['next_sequence_index'],28)
        self.assertTrue(ck['retry_state']['sequence26_exact_retry_consumed']); self.assertFalse(ck['retry_state']['sequence26_additional_retry_permitted'])
        self.assertFalse(ck['interim_policy']['task_deltas_computed']); self.assertFalse(ck['interim_policy']['effect_mean_computed']); self.assertFalse(ck['interim_policy']['p_value_computed']); self.assertFalse(ck['interim_policy']['claim_update_allowed'])
        self.assertEqual(csv['private_csv']['attempts_rows'],28); self.assertEqual(csv['private_csv']['progress_rows'],28)
        self.assertFalse(csv['private_csv']['contents_embedded_publicly']); self.assertFalse(csv['private_csv']['private_paths_embedded_publicly'])

    def test_r29_retry_cannot_be_reopened(self):
        r29=json.loads(R29.read_text(encoding='utf-8'))
        self.assertTrue(r29['retry_adjudication']['exact_retry_consumed'])
        self.assertFalse(r29['retry_adjudication']['additional_preexposure_retry_for_sequence26_permitted'])
        self.assertFalse(r29['failed_attempt']['scientific_exposure'])
        self.assertFalse(r29['durable_result']['terminal_score_exposed_in_receipt'])

if __name__=='__main__': unittest.main()
