from __future__ import annotations

import json, tempfile, unittest, warnings
from pathlib import Path

from research_pipeline.agent_constraint_externality_appworld_runtime import prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_codingplan_appworld_mcp_server import ScientificAppWorldMcpServer
from research_pipeline.agent_constraint_externality_codingplan_mcp_harness import CONTEXT_WINDOW, MAX_OUTPUT_TOKENS, MAX_ROUNDS, RETRY_MAX_ATTEMPTS, TOOL_CALL_CAP, write_config
from research_pipeline.agent_constraint_externality_codingplan_qwen38_mcp_run import units
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'cache/substrates/appworld-official-20260831'
BUNDLE=ROOT/'generated/agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle'

class CodingPlanQwen38McpTest(unittest.TestCase):
    def test_budget_and_panel_are_frozen(self):
        self.assertEqual(CONTEXT_WINDOW,262144); self.assertEqual(MAX_OUTPUT_TOKENS,65536); self.assertEqual(RETRY_MAX_ATTEMPTS,1); self.assertEqual(TOOL_CALL_CAP,16); self.assertEqual(MAX_ROUNDS,20)
        xs=units(); self.assertEqual(len(xs),8); self.assertEqual(len({x.unit_id for x in xs}),8); self.assertTrue(all('codingplan-mcp-v1' in x.unit_id for x in xs))
        self.assertLessEqual(MAX_ROUNDS*8,500)
    def test_config_is_request_efficient_and_zero_retry(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'c.toml'; write_config(p); t=p.read_text()
            for s in ['context_window=262144','max_tokens=65536','retry_max_attempts=1','max_rounds=20']: self.assertIn(s,t)
    def test_real_appworld_mcp_server_exposes_and_persists_one_tool_call(self):
        spec=load_protected_spec(BUNDLE); fam=next(x for x in spec['families'] if x['family_id']=='ACE-FG-05'); arm=next(x for x in fam['arms'] if x['coupling_level']=='LOW')
        with tempfile.TemporaryDirectory() as d, warnings.catch_warnings():
            warnings.simplefilter('ignore'); root=Path(d); task='acemcptest_1'; mat=prepare_appworld_runtime_root(APP,root,family=fam,arm=arm,task_id=task); state=root/'state.json'
            s=ScientificAppWorldMcpServer(runtime_root=root,task_id=task,experiment_name='ace-mcp-test',seed=1,allowed_apps=set(fam['fixture']['apps']),tool_call_cap=16,state_manifest=state,initial_snapshot_sha256=mat['initial_snapshot_sha256'],instruction_sha256=mat['instruction_sha256'],family_id='ACE-FG-05')
            try:
                names={x['name'] for x in s.list_tools()}; self.assertIn('supervisor__show_profile',names); out=s.call_tool('supervisor__show_profile',{}); self.assertFalse(out['isError'])
            finally: s.close()
            st=json.loads(state.read_text()); self.assertEqual(st['status'],'CLOSED'); self.assertEqual(st['tool_call_count'],1); self.assertEqual(st['executed_tool_names'],['supervisor__show_profile']); self.assertFalse(st['cap_reached'])

if __name__=='__main__': unittest.main()
