import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from .data_preparation_examples import create_demo_inputs
from .data_preparation_tables import load_bound_json,compile_table,table_exports,layout_change,digest
from .data_preparation_figures import validate_asset,plan_candidates,CATALOG
from .data_preparation_svg import render_svg
from .experiment_data_preparation import compile_bundle,build_bundle,import_feedback,build_preparation_portfolio,render_bundle_html,feedback_summary,write_handoff,import_feedback_file


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.manifest=create_demo_inputs(self.root)
        self.spec=self.manifest['tables'][0]
        self.records=[{**load_bound_json(self.root,r),'_bound_ref':r} for r in self.spec['result_refs']]
        self.assets=[{**load_bound_json(self.root,r),'_bound_ref':r} for r in self.manifest['figure_asset_refs']]
    def tearDown(self): self.tmp.cleanup()
    def cell(self,t,r,c):return next(x for x in t['cells'] if x['row_id']==r and x['column_id']==c)
    def test_empty_skeleton_is_not_zero(self):
        table=compile_table(self.spec,[])
        self.assertTrue(all(c['value'] is None for c in table['cells']))
        self.assertEqual(table['status'],'TABLE_PARTIAL')
    def test_complete_counts_delta_and_average(self):
        table=compile_table(self.spec,self.records)
        self.assertEqual(self.cell(table,'Variant A','within-a')['value'],55)
        self.assertEqual(self.cell(table,'Variant A','within-a')['delta'],15)
        self.assertEqual(self.cell(table,'Reference','within-avg')['value'],37.5)
    def test_real_zero_not_missing(self):
        self.records[0]['successes']=0
        self.assertEqual(self.cell(compile_table(self.spec,self.records),'Reference','within-a')['display'],'0.0')
    def test_partial_does_not_make_final_average(self):
        self.records[1]['status']='PARTIAL'
        table=compile_table(self.spec,self.records)
        self.assertIsNone(self.cell(table,'Reference','within-b')['value'])
        self.assertEqual(self.cell(table,'Reference','within-avg')['coverage'],[1,2])
        self.assertEqual(self.cell(table,'Reference','within-avg')['display'],'—')
    def test_protocol_mismatch_invalidates(self):
        self.records[0]['protocol_id']='other'
        self.assertEqual(self.cell(compile_table(self.spec,self.records),'Reference','within-a')['status'],'INVALID')
    def test_invalid_denominator(self):
        for value in [0,-1,True,19]:
            records=copy.deepcopy(self.records);records[0]['total']=value
            self.assertEqual(self.cell(compile_table(self.spec,records),'Reference','within-a')['status'],'INVALID')
    def test_incomplete_baseline_no_delta(self):
        self.records[0]['status']='RUNNING'
        c=self.cell(compile_table(self.spec,self.records),'Variant A','within-a')
        self.assertEqual(c['value'],55);self.assertIsNone(c['delta'])
    def test_duplicate_result_rejected(self):
        with self.assertRaises(ValueError):compile_table(self.spec,self.records+[self.records[0]])
    def test_unbound_result_not_accepted(self):
        self.records[0].pop('_bound_ref')
        self.assertEqual(self.cell(compile_table(self.spec,self.records),'Reference','within-a')['status'],'INVALID')
    def test_mixed_metric_average_rejected(self):
        spec=copy.deepcopy(self.spec);spec['columns'][1]['metric_id']='latency'
        with self.assertRaises(ValueError):compile_table(spec,self.records)
    def test_macro_micro_are_distinct(self):
        spec=copy.deepcopy(self.spec);spec['columns'][1]['expected_total']=40
        records=copy.deepcopy(self.records)
        for r in records:
            if r['column_id']=='within-b':r['total']=40
        macro=self.cell(compile_table(spec,records),'Reference','within-avg')['value']
        spec['columns'][2]['aggregate']='micro'
        micro=self.cell(compile_table(spec,records),'Reference','within-avg')['value']
        self.assertNotEqual(macro,micro)
    def test_layout_reorder_preserves_cell_bindings(self):
        new=copy.deepcopy(self.spec);new['rows'].reverse();new['columns'].reverse()
        self.assertEqual(layout_change(self.spec,new,'move averages')['kind'],'LAYOUT_ONLY')
        t=compile_table(new,self.records)
        self.assertEqual(self.cell(t,'Variant A','within-a')['value'],55)
    def test_protocol_edit_routes_back_to_experiments(self):
        new=copy.deepcopy(self.spec);new['columns'][0]['split_id']='new'
        self.assertTrue(layout_change(self.spec,new,'new split')['requires_experiment_change_ledger'])
    def test_source_drift_is_not_silent(self):
        source=self.root/'synthetic-evidence.json';source.write_text(source.read_text()+' ')
        with self.assertRaises(ValueError):load_bound_json(self.root,self.spec['result_refs'][0])
        state,_=compile_bundle(self.manifest,self.root)
        self.assertTrue(state['source_errors']);self.assertEqual(state['status'],'PREVIEW_WITH_GAPS')
    def test_source_path_escape_rejected(self):
        for path in ['../elsewhere.json','/etc/passwd','synthetic-evidence.txt']:
            with self.assertRaises(ValueError):load_bound_json(self.root,{'path':path,'sha256':'x'})
    def test_csv_tex_and_groups(self):
        table=compile_table(self.spec,self.records);csv,tex=table_exports(table)
        self.assertIn('Within Avg',csv);self.assertIn('Cross Avg',csv)
        self.assertIn('multicolumn{3}{c}{Within group}',tex)
    def test_default_two_candidates_one_question(self):
        plan=plan_candidates(self.assets)
        self.assertEqual(plan['columns'],2)
        self.assertEqual(len(plan['groups']),1)
        self.assertEqual(len(plan['groups'][0]['candidates']),2)
        self.assertEqual(len(plan['not_rendered_due_to_round_budget']),len(self.assets)-1)
    def test_explicit_legacy_twelve_distinct_types(self):
        plan=plan_candidates(self.assets,rounds=3,columns=4)
        types=[c['recipe'] for g in plan['groups'] for c in g['candidates']]
        self.assertEqual(len(types),12);self.assertEqual(len(set(types)),12)
        self.assertEqual(plan['columns'],4)
    def test_does_not_force_four(self):
        p=plan_candidates([self.assets[3]],columns=4)
        self.assertEqual(p['groups'][0]['unfilled_slots'],2)
    def test_samples_not_inferred_from_means(self):
        asset=copy.deepcopy(self.assets[0]);asset['kind']='samples'
        self.assertIn('missing-group',validate_asset(asset))
    def test_pairing_explicit(self):
        asset=copy.deepcopy(self.assets[1]);asset.pop('pairing_definition')
        self.assertIn('pairing-not-declared',validate_asset(asset))
    def test_interval_definition_required(self):
        asset=copy.deepcopy(self.assets[6]);asset.pop('interval_source')
        self.assertIn('interval-definition-missing',validate_asset(asset))
    def test_all_renderers_are_valid_svg(self):
        plan=plan_candidates(self.assets,rounds=7,columns=4);amap={a['id']:a for a in self.assets}
        rendered=[]
        for g in plan['groups']:
            for c in g['candidates']:
                svg=render_svg(amap[c['asset_id']],c);ET.fromstring(svg)
                self.assertIn('SYNTHETIC DEMO',svg);self.assertIn(c['data_sha256'],svg)
                self.assertNotIn('nan',svg.lower());rendered.append(c['recipe'])
        self.assertEqual(set(rendered),{r[0] for r in CATALOG})
    def test_stable_ids_do_not_depend_on_screen_order(self):
        a=plan_candidates(self.assets[:3],rounds=3);b=plan_candidates(list(reversed(self.assets[:3])),rounds=3)
        ids=lambda p:{c['id'] for g in p['groups'] for c in g['candidates']}
        self.assertEqual(ids(a),ids(b))
    def test_data_or_style_change_invalidates_candidate_id(self):
        a=plan_candidates(self.assets[:1]);changed=copy.deepcopy(self.assets[:1]);changed[0]['rows'][0]['value']+=1
        b=plan_candidates(changed);c=plan_candidates(self.assets[:1],style={'font_family':'serif'})
        self.assertNotEqual(a['groups'][0]['candidates'][0]['id'],b['groups'][0]['candidates'][0]['id'])
        self.assertNotEqual(a['groups'][0]['candidates'][0]['id'],c['groups'][0]['candidates'][0]['id'])
    def feedback(self,state):
        c=state['figures']['groups'][0]['candidates'][0]
        return {'paper_id':state['paper_id'],'snapshot_sha256':state['snapshot_sha256'],'events':[{'id':c['id'],'data_sha256':c['data_sha256'],'spec_sha256':c['spec_sha256'],'action':'KEEP','at':'fixture'}]}
    def test_feedback_import_idempotent(self):
        state,_=compile_bundle(self.manifest,self.root);f=self.feedback(state)
        once=import_feedback(state,f);twice=import_feedback(state,f,once)
        self.assertEqual(once,twice);self.assertFalse(once['scientific_authority'])
    def test_stale_feedback_rejected(self):
        state,_=compile_bundle(self.manifest,self.root);f=self.feedback(state);f['snapshot_sha256']='old'
        with self.assertRaises(ValueError):import_feedback(state,f)
    def test_unknown_selection_rejected(self):
        state,_=compile_bundle(self.manifest,self.root);f=self.feedback(state);f['events'][0]['id']='no-such-figure'
        with self.assertRaises(ValueError):import_feedback(state,f)
    def test_bundle_and_browser_draft_boundary(self):
        state,path=build_bundle(self.manifest,self.root,self.root/'out')
        self.assertEqual(len(list((path/'figures').glob('*.svg'))),12)
        html=(path/'index.html').read_text()
        self.assertIn('repeat(4,minmax(240px,1fr))',html);self.assertIn('BROWSER_DRAFT_NOT_SERVER_ACCEPTED',html)
        self.assertTrue((path/'provenance.json').exists());self.assertFalse(state['source_data_included'])
    def test_html_escape_and_script_payload(self):
        manifest=copy.deepcopy(self.manifest);manifest['title']='<script>alert(1)</script>'
        state,_=compile_bundle(manifest,self.root)
        self.assertNotIn('<script>alert(1)</script>',render_bundle_html(state))
    def test_no_manifest_no_fabricated_paper(self):
        state=build_preparation_portfolio(self.root)
        self.assertEqual(state['rows'],[]);self.assertEqual(state['model_calls'],0)
    def test_table_figure_cross_binding_detects_mismatch(self):
        source=self.root/'synthetic-evidence.json';raw=json.loads(source.read_text())
        raw['assets'][0]['table_bindings']=[{'table_id':self.spec['id'],'row_id':'Reference','column_id':'within-a','asset_row_id':'0','field':'value'}]
        raw['assets'][0]['rows'][0]['value']=99
        source.write_text(json.dumps(raw));sha=hashlib.sha256(source.read_bytes()).hexdigest()
        for ref in self.manifest['figure_asset_refs']+self.spec['result_refs']:ref['sha256']=sha
        state,_=compile_bundle(self.manifest,self.root)
        self.assertTrue(any(e['kind']=='TABLE_FIGURE_BINDING_ERROR' for e in state['source_errors']))
        self.assertIn('DEMO-categories',[r['asset_id'] for r in state['figures']['blocked_assets']])
    def test_handoff_needs_current_selection_and_intact_svg(self):
        state,path=build_bundle(self.manifest,self.root,self.root/'out')
        self.assertIn('no-current-operator-selection',write_handoff(state,path,{'events':[]})['blockers'])
        ledger=import_feedback(state,self.feedback(state));handoff=write_handoff(state,path,ledger)
        self.assertEqual(handoff['status'],'MATERIALS_SELECTED_VISUAL_REVIEW_PENDING')
        self.assertFalse(handoff['manuscript_prose_written'])
        svg=path/handoff['selected_figures'][0]['path'];svg.write_text('tampered')
        self.assertTrue(write_handoff(state,path,ledger)['blockers'])
    def test_feedback_file_lock_prevents_overwrite(self):
        state,_=compile_bundle(self.manifest,self.root);path=self.root/'reviews.json'
        (self.root/'reviews.json.lock').mkdir()
        with self.assertRaises(ValueError):import_feedback_file(state,self.feedback(state),path)
        self.assertFalse(path.exists())
    def test_new_snapshot_marks_old_feedback_stale(self):
        a,_=compile_bundle(self.manifest,self.root);ledger=import_feedback(a,self.feedback(a))
        self.manifest['figure_style']['font_family']='serif'
        b,_=compile_bundle(self.manifest,self.root);summary=feedback_summary(b,ledger)
        self.assertEqual(summary['selected'],[]);self.assertEqual(summary['stale_events'],1)
    def test_unregistered_result_is_not_silently_ignored(self):
        records=copy.deepcopy(self.records);records[0]['column_id']='unknown'
        with self.assertRaises(ValueError):compile_table(self.spec,records)
    def test_series_duplicate_x_needs_declared_aggregation(self):
        a=copy.deepcopy(self.assets[3]);a['rows'][1]['x']=a['rows'][0]['x']
        self.assertIn('duplicate-series-x-requires-explicit-aggregation',validate_asset(a))
    def test_bubble_requires_size_unit(self):
        a=copy.deepcopy(self.assets[4]);a.pop('size_unit')
        self.assertEqual([c['recipe'] for c in plan_candidates([a])['groups'][0]['candidates']],['scatter'])
    def test_slope_equal_endpoints_do_not_overlap_labels(self):
        a=self.assets[1];plan=plan_candidates([a]);c=next(c for c in plan['groups'][0]['candidates'] if c['recipe']=='slope')
        tree=ET.fromstring(render_svg(a,c))
        labels=[n for n in tree.iter() if n.tag.endswith('text') and (n.text or '').startswith('Unit ')]
        self.assertEqual(len(labels),len(a['rows']))
        self.assertEqual(len({n.attrib['y'] for n in labels}),len(labels))

    def test_pure_compilation(self):
        original=copy.deepcopy(self.manifest)
        a,_=compile_bundle(self.manifest,self.root);b,_=compile_bundle(self.manifest,self.root)
        self.assertEqual(self.manifest,original);self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
