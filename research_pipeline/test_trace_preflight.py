from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .trace_preflight import pre_model_load_audit, validate_raw_trace_file

class TraceContractTest(unittest.TestCase):
 def test_complete_trace_passes_and_missing_raw_choice_fails(self):
  base={'task_id':'t','task_goal':'g','task_family':'f','initial_observation':'o','observations':['o'],'actions':['a'],'raw_choices':['a'],'success':1,'steps':1,'model_calls':1}
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'raw.jsonl'; p.write_text(json.dumps({'role':'r','trace':base})+'\n')
   self.assertTrue(validate_raw_trace_file(p)['pass'])
   bad=dict(base); bad.pop('raw_choices'); p.write_text(json.dumps({'role':'r','trace':bad})+'\n')
   self.assertFalse(validate_raw_trace_file(p)['pass'])
 def test_pre_model_audit_passes_before_gpu_and_types_runtime_failure(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); model=root/'model'; data=root/'alfworld'; extra=root/'site'; out=root/'run'; model.mkdir(); extra.mkdir(); out.mkdir()
   for name in ('config.json','tokenizer.json','model.safetensors.index.json'): (model/name).write_text('{}')
   for rel in ('json_2.1.1/train','json_2.1.1/valid_seen','json_2.1.1/valid_unseen'): (data/rel).mkdir(parents=True)
   (data/'logic').mkdir(); (data/'logic/alfred.pddl').write_text('pddl'); (data/'logic/alfred.twl2').write_text('twl2')
   cfg=root/'config.json'; cfg.write_text('{}'); src=root/'runner.py'; src.write_text('pass')
   with patch('research_pipeline.trace_preflight.importlib.util.find_spec',return_value=object()):
    row=pre_model_load_audit('idea','p0-support',cfg,model,data,extra,out,[src])
   self.assertTrue(row['pass']); self.assertIsNone(row['failure_kind'])
   with patch('research_pipeline.trace_preflight.importlib.util.find_spec',return_value=None):
    failed=pre_model_load_audit('idea','p0-support',cfg,model,data,extra,out,[src])
   self.assertFalse(failed['pass']); self.assertEqual(failed['failure_kind'],'RUNTIME_ERROR')
if __name__=='__main__': unittest.main()
