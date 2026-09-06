from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from research_pipeline import agent_constraint_externality_atomgit_repair_common as c
from research_pipeline import agent_constraint_externality_atomgit_repair_execute as e
from research_pipeline.agent_constraint_externality_runner_core import sha256_value

class RepairGenerationStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls)->None:
        cls.proj=c.projection()

    def test_exact_six_payloads_are_target_only(self):
        ids=c.selected_ids(self.proj); self.assertEqual(6,len(ids))
        for fid in ids:
            p=c.writer_payload(self.proj,fid); text=json.dumps(p,ensure_ascii=False,sort_keys=True).lower()
            self.assertNotIn('"access_token"',text); self.assertNotIn('"password"',text); self.assertNotIn('spare-',text); self.assertNotIn('ace-dev-dummy',text)
            for term in c.FORBIDDEN_REPAIR_TERMS: self.assertNotIn(term,text)
            self.assertEqual({'TARGET_CONSTRAINT_SPEC','TARGET_TASK_INSTRUCTION','TARGET_FAILURE_SLICE','TARGET_TOOL_TRAJECTORY'},set(p))

    def test_target_constraint_has_one_target_only(self):
        for fid in c.selected_ids(self.proj):
            t=c.target_constraint(fid); self.assertEqual('TARGET',t['role']); self.assertTrue(t['semantic_description'])

    def test_runtime_contract_is_one_round_no_tools(self):
        text=c.config(); self.assertIn('max_rounds = 1',text); self.assertIn('retry_max_attempts = 1',text); self.assertIn('Do not use tools',text)
        self.assertEqual(1,c.MODEL_ROUND_CAP); self.assertEqual(6,c.REPAIR_REQUEST_CAP)

    def test_freeze_repair_normalizes_only_terminal_whitespace(self):
        old=c.REPAIRS
        with tempfile.TemporaryDirectory(dir=c.ROOT) as d:
            c.REPAIRS=Path(d)
            try:
                r=e.freeze_repair('ACE-DEV-FG-999','step one\r\nstep two\n',{'generation_request_sha256':'x'})
                repair=Path(d)/'ace-dev-fg-999-repair.bin'; self.assertEqual(b'step one\nstep two',repair.read_bytes()); self.assertFalse(r['human_edited'])
            finally: c.REPAIRS=old

    def test_ledger_state_machine_rejects_duplicate_dispatch(self):
        old=c.LEDGER
        with tempfile.TemporaryDirectory() as d:
            c.LEDGER=Path(d)/'l.jsonl'
            try:
                row={'unit_id':'u','event':'DISPATCH'}; c.append_ledger(row); c.append_ledger(row)
                with self.assertRaises(c.RepairStop): c.ledger_states()
            finally: c.LEDGER=old

    def test_projection_family_hashes_are_stable(self):
        for fid in c.selected_ids(self.proj): self.assertEqual(sha256_value(self.proj['families'][fid]),sha256_value(self.proj['families'][fid]))

    def test_g1_release_is_explicit(self):
        text=c.G1_RELEASE.read_text(encoding='utf-8'); self.assertIn('It may be reassigned only to another independently authorized scientific object.',text); self.assertIn('ATOMGIT_Q0_PROTOCOL_INCONCLUSIVE_STOP_ALL',text)

if __name__=='__main__': unittest.main()
