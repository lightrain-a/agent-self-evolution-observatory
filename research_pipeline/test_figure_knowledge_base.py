from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from .figure_knowledge_base import SOURCES,build_knowledge_base,search_knowledge,selection_brief,validate_reference_selection
from .figure_knowledge_taxonomy import FAMILIES,classify


def receipts():
    result={}
    for key,policy in SOURCES.items():
        result[key]={'repo':policy['repo'],'sha':'a'*40,'date':'2026-09-27T00:00:00Z','tree':{'truncated':False,'sha':'c'*40,'tree':[]}}
    def add(key,path,blob='b'*40):result[key]['tree']['tree'].append({'path':path,'type':'blob','sha':blob,'size':123})
    add('vivid-figures-skill','catalog/cards/basic.raincloud.md')
    add('vivid-figures-skill','catalog/previews/basic.raincloud-1.png','1'*40)
    add('vivid-figures-skill','catalog/thumbnails/basic.raincloud-1.jpg','2'*40)
    add('vivid-figures-skill','catalog/sources/basic.raincloud/render.py')
    add('figures4papers','figure_Demo/figures/grouped_bar.png','3'*40)
    add('figures4papers','figure_Demo/figures/grouped_bar.pdf','4'*40)
    add('figures4papers','figure_Demo/plot_grouped_bar.py')
    add('The-Python-Graph-Gallery','static/graph/120_basic_lineplot1.png','5'*40)
    add('The-Python-Graph-Gallery','src/notebooks/120-basic-lineplot.ipynb','6'*40)
    add('The-Python-Graph-Gallery','static/logo/example-logo.png','7'*40)
    add('great-tables','assets/gt_sp500_table.svg','8'*40)
    add('great-tables','user_guide/06-summary-rows.qmd','9'*40)
    return result


class FigureKnowledgeTests(unittest.TestCase):
    def setUp(self):self.receipts=receipts();self.kb=build_knowledge_base(self.receipts)
    def test_all_visual_files_accounted_for(self):
        self.assertEqual(self.kb['summary']['visual_files'],7)
        self.assertEqual(self.kb['summary']['indexed_visual_files'],7)
        self.assertTrue(all(r['unindexed_visual_files']==0 for r in self.kb['coverage']))
    def test_thumbnail_is_not_extra_recipe(self):
        rows=[e for e in self.kb['entries'] if e['source_id']=='vivid']
        self.assertEqual(len(rows),1)
        self.assertEqual(len(rows[0]['previews']),1);self.assertEqual(len(rows[0]['thumbnails']),1)
        self.assertTrue(rows[0]['previews'][0]['thumbnail_url'].endswith('.jpg'))
    def test_pdf_is_alternate_not_fake_image(self):
        e=next(e for e in self.kb['entries'] if e['source_id']=='f4p')
        self.assertEqual(len(e['previews']),1);self.assertEqual(len(e['documents']),1)
    def test_tutorials_and_support_are_not_lost(self):
        kinds={e['kind'] for e in self.kb['entries']}
        self.assertIn('TUTORIAL',kinds);self.assertIn('SUPPORT_ASSET',kinds);self.assertIn('TABLE_GUIDE',kinds)
    def test_refuses_truncated_tree(self):
        self.receipts['figures4papers']['tree']['truncated']=True
        with self.assertRaises(ValueError):build_knowledge_base(self.receipts)
    def test_refuses_wrong_repository(self):
        self.receipts['figures4papers']['repo']='wrong/repo'
        with self.assertRaises(ValueError):build_knowledge_base(self.receipts)
    def test_refuses_floating_commit(self):
        self.receipts['figures4papers']['sha']='main'
        with self.assertRaises(ValueError):build_knowledge_base(self.receipts)
    def test_english_chinese_search(self):
        for query in ('raincloud','雨云'):
            self.assertTrue(any('raincloud' in e['families'] for e in search_knowledge(self.kb,query)))
    def test_shap_does_not_match_shape(self):
        rows=search_knowledge(self.kb,'shap')
        self.assertTrue(all('shap' in e['families'] for e in rows))
        real=json.loads((Path(__file__).resolve().parents[1]/'generated/figure-knowledge-base.json').read_text())
        rows=search_knowledge(real,'SHAP',limit=50)
        self.assertTrue(rows);self.assertTrue(all('shap' in e['families'] for e in rows))

    def test_data_preparation_accepts_versioned_reference_brief(self):
        import tempfile
        from .data_preparation_examples import create_demo_inputs
        from .experiment_data_preparation import compile_bundle
        real=json.loads((Path(__file__).resolve().parents[1]/'generated/figure-knowledge-base.json').read_text())
        e=real['entries'][0]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);manifest=create_demo_inputs(root)
            manifest['figure_reference_brief']={'entries':[{'entry_id':e['id'],'content_version':e['content_version'],'commit':e['commit']}]}
            state,_=compile_bundle(manifest,root)
            self.assertEqual(state['external_reference_selection']['role'],'DESIGN_REFERENCES_NOT_EXPERIMENTAL_RESULTS')
            self.assertEqual(state['external_reference_selection']['entries'][0]['entry_id'],e['id'])
            self.assertEqual(state['experiments_launched'],0)
            manifest['figure_reference_brief']['entries'][0]['commit']='old'
            with self.assertRaises(ValueError):compile_bundle(manifest,root)

    def test_data_filter_not_renderer_limit(self):
        rows=search_knowledge(self.kb,'',data_kinds=['samples'])
        self.assertTrue(any(e['source_id']=='vivid' for e in rows))
        self.assertTrue(all(e['implementation_status']=='REFERENCE_INDEX_NOT_INSTALLED' for e in rows))
    def test_numbered_variant_classification(self):
        self.assertIn('line',classify('120_Basic_lineplot1.png'))
        self.assertIn('violin',classify('512-violinplot-custom.png'))
        self.assertIn('shap',classify('template.shap_contribution.md'))
    def test_no_fake_human_visual_review(self):
        self.assertTrue(all(e['visual_reviewed'] is False for e in self.kb['entries']))
        self.assertEqual(self.kb['summary']['upstream_code_executed'],0)
        self.assertEqual(self.kb['summary']['images_mirrored'],0)
    def test_stable_ids_change_content_version(self):
        newer=copy.deepcopy(self.receipts);newer['figures4papers']['sha']='d'*40
        a=next(e for e in self.kb['entries'] if e['source_id']=='f4p')
        b=next(e for e in build_knowledge_base(newer)['entries'] if e['source_id']=='f4p')
        self.assertEqual(a['id'],b['id']);self.assertNotEqual(a['content_version'],b['content_version'])
    def test_selection_brief_has_data_and_license(self):
        e=self.kb['entries'][0];brief=selection_brief(self.kb,[e['id']],'compare distributions',['group','samples'])
        self.assertEqual(brief['requested_layout']['columns'],4)
        self.assertFalse(brief['executes_code']);self.assertFalse(brief['scientific_authority'])
        self.assertTrue(brief['entries'][0]['family_guidance']);self.assertTrue(brief['entries'][0]['license'])
    def test_selection_rejects_unknown_and_duplicate(self):
        with self.assertRaises(ValueError):selection_brief(self.kb,['nonexistent'],'',[])
        eid=self.kb['entries'][0]['id']
        with self.assertRaises(ValueError):selection_brief(self.kb,[eid,eid],'',[])
    def test_exported_selection_requires_current_version(self):
        e=self.kb['entries'][0]
        brief={'entries':[{'entry_id':e['id'],'content_version':e['content_version'],'commit':e['commit']}]}
        self.assertEqual(validate_reference_selection(self.kb,brief),[e['id']])
        brief['entries'][0]['commit']='old'
        with self.assertRaises(ValueError):validate_reference_selection(self.kb,brief)
    def test_exact_asset_duplicate_marked_but_not_deleted(self):
        self.receipts['figures4papers']['tree']['tree'].append({'type':'blob','path':'assets/alias.png','sha':'3'*40,'size':123})
        kb=build_knowledge_base(self.receipts)
        mapped=next(c for c in kb['coverage'] if c['source_id']=='f4p')['path_to_entry']
        self.assertIn('assets/alias.png',mapped)
    def test_every_family_has_selection_guidance(self):
        for fid,f in FAMILIES.items():
            self.assertTrue(f['label']);self.assertTrue(f['question']);self.assertTrue(f['caution'])
            if fid!='unclassified':self.assertTrue(f['required_fields'])
    def test_generated_real_coverage_is_consistent(self):
        root=Path(__file__).resolve().parents[1]
        coverage=json.loads((root/'generated/figure-knowledge-coverage.json').read_text())
        data=json.loads((root/'generated/figure-knowledge-base.json').read_text())
        self.assertEqual(len(data['entries']),data['summary']['entries'])
        self.assertEqual(sum(len(r['path_to_entry']) for r in coverage['coverage']),data['summary']['visual_files'])
        vivid=next(r for r in coverage['coverage'] if r['source_id']=='vivid')
        self.assertEqual(vivid['entry_kinds']['RECIPE_CARD'],146)
        self.assertEqual(vivid['released_recipe_previews'],148)
        self.assertEqual(vivid['attached_thumbnails'],148)
        self.assertEqual(len({e['id'] for e in data['entries']}),len(data['entries']))
        self.assertGreater(data['summary']['selectable_examples'],1000)

if __name__=='__main__':unittest.main()
