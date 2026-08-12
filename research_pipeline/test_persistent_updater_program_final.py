from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from .persistent_updater_program_final import build_persistent_updater_program_final,write_persistent_updater_program_final

class PersistentUpdaterProgramFinalTest(unittest.TestCase):
 def test_terminal_authority_keeps_batch_locked_and_a2_hold(self):
  row=build_persistent_updater_program_final()
  self.assertEqual(row['verdict'],'STOP_CURRENT_PERSISTENT_UPDATER_PROGRAM')
  self.assertFalse(row['batch_experiment_authorized'])
  self.assertFalse(row['second_backbone_authorized'])
  self.assertEqual(row['states']['A1'],'MERGED_DIAGNOSTIC_ONLY')
  self.assertEqual(row['states']['A2'],'KEEP_PROBLEM_HOLD_NO_QUALIFIED_UPDATER')
  self.assertEqual(row['final_ai_adjudication']['web_gpt'],row['verdict'])
  self.assertEqual(row['final_ai_adjudication']['deepseek_v4_flash'],row['verdict'])
  self.assertFalse(row['final_ai_adjudication']['new_problem_proposed'])
 def test_public_writer_is_sanitized_and_machine_readable(self):
  with tempfile.TemporaryDirectory() as td:
   jp=Path(td)/'x.json';sp=Path(td)/'x.js';row=write_persistent_updater_program_final(jp,sp)
   self.assertEqual(json.loads(jp.read_text())['authority_sha256'],row['authority_sha256'])
   text=sp.read_text();self.assertIn('STOP_CURRENT_PERSISTENT_UPDATER_PROGRAM',text)
   self.assertNotIn('/home/hdd/',text)
   self.assertNotIn('/data/wyt/',text)
if __name__=='__main__':unittest.main()
