"""All manuscript/evidence values here are explicit unit-test fixtures, not findings."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from .paper_writing_sources import file_ref,manuscript_inventory,read_bound,tex_symbols,load_visual_handoff
from .paper_writing_loop import prepare_job,job_prompt,audit_response,stage_response,apply_candidate,generate_once
from .paper_writing_visuals import compile_placements
from .paper_writing_contracts import classify_feedback


class WritingLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/'sec').mkdir()
        (self.root/'main.tex').write_text('\\documentclass{article}\n% \\input{old}\n\\begin{document}\n\\input{sec/introduction}\n\\input{sec/method}\n\\end{document}\n')
        self.before='\\section{Introduction}\n\\label{sec:intro}\nThe method uses 16 tasks, but the gains are not universal~\\citep{verified}. See Section~\\ref{sec:method}.\n'
        (self.root/'sec/introduction.tex').write_text(self.before)
        (self.root/'sec/method.tex').write_text('\\section{Method}\n\\label{sec:method}\nThe method selects an existing option.\n')
        (self.root/'results.json').write_text('{"fixture_only":true,"value":16}')
        self.manifest={'paper_id':'TEST-NOT-A-PAPER','section_id':'intro','section_role':'introduction','mode':'LOCAL_POLISH','user_instruction':'只做小幅润色，不要大改；保持结果边界。',
                       'target':file_ref(self.root,'sec/introduction.tex'),'main':'main.tex',
                       'protected_refs':[file_ref(self.root,'results.json')],'must_preserve_phrases':['not universal']}
    def tearDown(self):self.temp.cleanup()
    def job(self):return prepare_job(self.manifest,self.root)
    def response(self,job,tex=None):
        return {'job_sha256':job['job_sha256'],'section_id':job['section_id'],'diagnosis':['Test fixture: use a concrete verb.'],
                'replacement_tex':tex if tex is not None else self.before.replace('uses 16 tasks','evaluates 16 tasks'),
                'used_claim_ids':[],'used_reference_ids':[],'changes':[],'evidence_requests':[],'unresolved':[]}
    def candidate(self,job,response=None):return stage_response(job,response or self.response(job),self.root/'candidates')
    def decision(self,c):return {'action':'ACCEPT','candidate_sha256':c['candidate_sha256'],'reviewer':'TEST-OPERATOR','read_diff':True,'scope_reviewed':True,'evidence_reviewed':True}
    def add_graph(self):
        graph={'paper_id':self.manifest['paper_id'],'nodes':[{'node_type':'CLAIM','claim_id':'C1','claim_text':'Fixture only.','affirmative_prose_allowed':True,'adjudication_status':'SUPPORTED','must_preserve_negative_or_inconclusive':False}]}
        (self.root/'graph.json').write_text(json.dumps(graph));self.manifest['claim_graph_ref']=file_ref(self.root,'graph.json')
    def test_inventory_uses_active_includes(self):
        inv=manuscript_inventory(self.root)
        self.assertEqual(inv['include_order'],['main.tex','sec/introduction.tex','sec/method.tex']);self.assertEqual(inv['unresolved'],[])
    def test_missing_include_is_not_ignored(self):
        (self.root/'main.tex').write_text('\\input{missing}\n')
        with self.assertRaises(ValueError):self.job()
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):read_bound(self.root,{'path':'../file','sha256':'x'})
    def test_source_hash_checked_before_writing(self):
        (self.root/'sec/introduction.tex').write_text('different')
        with self.assertRaises(ValueError):self.job()
    def test_packet_preserves_user_scope_and_current_source(self):
        job=self.job();prompt=job_prompt(job)
        self.assertIn('不要大改',prompt);self.assertIn('not universal',prompt);self.assertEqual(job['mode'],'LOCAL_POLISH');self.assertFalse(job['provider_called'])
    def test_local_response_is_candidate_not_final(self):
        job=self.job();audit=audit_response(job,self.response(job))
        self.assertEqual(audit['blockers'],[]);self.assertFalse(audit['semantic_truth_verified']);self.assertFalse(audit['actual_pdf_reviewed'])
    def test_local_number_change_blocked(self):
        job=self.job();audit=audit_response(job,self.response(job,self.before.replace('16','17')))
        self.assertIn('local-polish-changed-numbers',audit['blockers'])
    def test_local_citation_change_blocked(self):
        job=self.job();audit=audit_response(job,self.response(job,self.before.replace('{verified}','{madeup}')))
        self.assertIn('unverified-citation-key',audit['blockers'])
    def test_explicit_boundary_cannot_disappear(self):
        job=self.job();audit=audit_response(job,self.response(job,self.before.replace('not universal','universal')))
        self.assertTrue(any('boundary-phrase' in b for b in audit['blockers']))
    def test_local_section_title_preserved(self):
        job=self.job();audit=audit_response(job,self.response(job,self.before.replace('Introduction','Motivation')))
        self.assertIn('local-polish-changed-section-structure',audit['blockers'])
    def test_unknown_claim_blocked(self):
        job=self.job();response=self.response(job);response['used_claim_ids']=['invented']
        self.assertIn('unregistered-claim-id',audit_response(job,response)['blockers'])
    def test_execution_directives_blocked(self):
        job=self.job();response=self.response(job,self.before+'\\immediate\\write18{echo unsafe}')
        self.assertIn('replacement-includes-preamble-or-execution-command',audit_response(job,response)['blockers'])
    def test_staging_never_applies(self):
        job=self.job();candidate=self.candidate(job)
        self.assertEqual((self.root/'sec/introduction.tex').read_text(),self.before)
        self.assertTrue((Path(candidate['output_path'])/'revision.diff').exists())
    def test_apply_requires_explicit_review(self):
        job=self.job();c=self.candidate(job);decision=self.decision(c);decision['read_diff']=False
        with self.assertRaises(ValueError):apply_candidate(job,c,decision,self.root,self.root/'receipts')
    def test_apply_is_scoped_and_receipted(self):
        job=self.job();c=self.candidate(job);method=(self.root/'sec/method.tex').read_text()
        receipt=apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
        self.assertIn('evaluates 16 tasks',(self.root/'sec/introduction.tex').read_text())
        self.assertEqual((self.root/'sec/method.tex').read_text(),method)
        self.assertEqual(receipt['independent_post_edit_review'],'REQUIRED');self.assertEqual(receipt['latex_build'],'NOT_RUN')
    def test_concurrent_new_results_block_old_revision(self):
        job=self.job();c=self.candidate(job);(self.root/'results.json').write_text('{"fixture_only":true,"value":18}')
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
        self.assertEqual((self.root/'sec/introduction.tex').read_text(),self.before)
    def test_concurrent_other_section_change_is_not_overwritten(self):
        job=self.job();c=self.candidate(job);(self.root/'sec/method.tex').write_text('new coauthor text')
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
        self.assertEqual((self.root/'sec/method.tex').read_text(),'new coauthor text')
    def test_tampered_candidate_rejected(self):
        job=self.job();c=self.candidate(job);c['response']['replacement_tex']='tampered'
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
    def test_locked_apply_no_overwrite(self):
        job=self.job();c=self.candidate(job);(self.root/'.paper-writing-apply.lock').mkdir()
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
    def test_outline_never_writes(self):
        self.manifest['mode']='OUTLINE';job=self.job();response=self.response(job,'');c=self.candidate(job,response)
        self.assertEqual(c['audit']['status'],'PLAN_READY')
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
    def test_material_rewrite_needs_graph(self):
        self.manifest['mode']='REWRITE'
        with self.assertRaises(ValueError):self.job()
    def test_reference_roles_are_not_interchangeable(self):
        (self.root/'example.txt').write_text('Example paper result 99 is not our result.')
        self.manifest['references']=[{'id':'E1','role':'writing_exemplar','ref':file_ref(self.root,'example.txt')}]
        job=self.job();self.assertEqual(job['reference_packet'][0]['role'],'writing_exemplar')
        self.assertIn('Exemplar numbers are not our results',job_prompt(job))
    def test_provider_is_one_bounded_call(self):
        job=self.job();calls=[]
        def caller(prompt,**kwargs):calls.append(kwargs);return {'text':json.dumps(self.response(job)),'model':'test-model'}
        response,receipt=generate_once(job,caller,model='test-model',max_output_tokens=1024)
        self.assertEqual(len(calls),1);self.assertEqual(receipt['provider_calls'],1)
        self.assertEqual(response['section_id'],'intro');self.assertEqual((self.root/'sec/introduction.tex').read_text(),self.before)
    def test_long_prompt_does_not_make_provider_call(self):
        calls=[]
        with self.assertRaises(ValueError):generate_once(self.job(),lambda *a,**k:calls.append(1),model='test',max_input_chars=1)
        self.assertEqual(calls,[])
    def test_explicit_target_span_preserves_rest(self):
        self.manifest['target'].update(start_line=3,end_line=3);job=self.job()
        response=self.response(job,job['before_tex'].replace('uses','evaluates'));c=self.candidate(job,response)
        apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
        self.assertTrue((self.root/'sec/introduction.tex').read_text().startswith('\\section{Introduction}\n\\label{sec:intro}\n'))
    def test_feedback_types_not_all_full_rewrite(self):
        route=classify_feedback('微调图例，附录和正文有冲突，成本口径要一致')
        self.assertTrue(route['local_scope_requested']);self.assertIn('APPENDIX_ALIGN',route['routes']);self.assertFalse(route['automatic_full_rewrite'])
    def bridge_fixture(self,role='EXPLORATORY'):
        # Explicit unit-test fixtures, not real experiment data.
        (self.root/'figure.png').write_bytes(b'test-fixture-only')
        image=file_ref(self.root,'figure.png');raw=file_ref(self.root,'results.json');snapshot='a'*64
        prep={'paper_id':self.manifest['paper_id'],'snapshot_sha256':snapshot,'tables':[],
              'figures':{'groups':[{'candidates':[{'id':'F1','claim_id':'C1','question':'Fixture question','scope':'unit test','data_role':role,'data_sha256':'b'*64,'source_ref':raw}]}]},
              'artifact_sha256':{'figure.png':image['sha256']}}
        handoff={'paper_id':self.manifest['paper_id'],'snapshot_sha256':snapshot,'status':'MATERIALS_SELECTED_VISUAL_REVIEW_PENDING','blockers':[],
                 'selected_figures':[{'candidate_id':'F1','path':'figure.png','sha256':image['sha256']}],'tables':[]}
        (self.root/'preparation.json').write_text(json.dumps(prep));(self.root/'handoff.json').write_text(json.dumps(handoff))
        self.manifest['preparation_ref']=file_ref(self.root,'preparation.json');self.manifest['handoff_ref']=file_ref(self.root,'handoff.json')
        return image
    def test_selected_figure_reaches_section_packet_and_latex(self):
        image=self.bridge_fixture();self.add_graph();self.manifest['mode']='REWRITE'
        self.manifest['visual_placements']=[{'kind':'figure','visual_id':'F1','label':'fig:fixture','caption':'Unit test only.','latex_artifact_ref':image}]
        job=self.job();snippet=job['visual_insertions']['snippets'][0]['latex']
        response=self.response(job,self.before+'\n'+snippet);audit=audit_response(job,response)
        self.assertEqual(audit['blockers'],[]);self.assertIn('figure.png',job_prompt(job))
        self.assertTrue(job['figure_table_handoff']['original_source_refs'])
    def test_gallery_or_synthetic_figure_cannot_be_evidence(self):
        self.bridge_fixture('SYNTHETIC_DEMO')
        with self.assertRaises(ValueError):self.job()
    def test_missing_approved_figure_snippet_is_blocked(self):
        image=self.bridge_fixture();self.add_graph();self.manifest['mode']='REWRITE'
        self.manifest['visual_placements']=[{'kind':'figure','visual_id':'F1','label':'fig:fixture','caption':'Unit test only.','latex_artifact_ref':image}]
        job=self.job();audit=audit_response(job,self.response(job))
        self.assertTrue(any('snippet-missing' in x for x in audit['blockers']))
    def test_raw_data_drift_is_watched_through_visual_handoff(self):
        self.bridge_fixture();self.manifest['protected_refs']=[];job=self.job();c=self.candidate(job)
        (self.root/'results.json').write_text('{"fixture_only":true,"value":99}')
        with self.assertRaises(ValueError):apply_candidate(job,c,self.decision(c),self.root,self.root/'receipts')
    def test_framework_can_plan_without_fake_supported_claims(self):
        self.manifest.update(mode='DRAFT',evidence_mode='FRAMEWORK');job=self.job()
        self.assertEqual(job['claim_surface']['affirmative_claims'],[])
        self.assertIn('forbids affirmative claims about uncompleted experiments',job_prompt(job))
    def test_review_packet_is_not_completed_review(self):
        from .paper_writing_loop import independent_review_packet
        job=self.job();c=self.candidate(job);review=independent_review_packet(job,c)
        self.assertEqual(review['candidate_sha256'],c['candidate_sha256']);self.assertEqual(review['review_status'],'NOT_RUN')
        self.assertEqual(review['order'][:3],['FACT','LOGIC','CLAIM_EVIDENCE'])
    def test_include_order_not_alphabetical(self):
        (self.root/'main.tex').write_text('\\input{sec/method}\n\\input{sec/introduction}\n')
        self.assertEqual(manuscript_inventory(self.root)['include_order'],['main.tex','sec/method.tex','sec/introduction.tex'])
    def test_svg_needs_export_before_latex_insert(self):
        bridge={'figures':[{'id':'F1','artifact_ref':{'path':'test.svg','sha256':'x'}}]}
        with self.assertRaises(ValueError):compile_placements(self.root,bridge,[{'kind':'figure','visual_id':'F1','label':'fig:test','caption':'Test fixture.'}])
    def test_only_selected_visual_can_be_inserted(self):
        with self.assertRaises(ValueError):compile_placements(self.root,None,[{'kind':'figure','visual_id':'unselected','label':'fig:test','caption':'Fixture.'}])
    def test_valid_export_snippet_preserves_provenance(self):
        (self.root/'fixture.png').write_bytes(b'unit-test-placeholder-not-an-image')
        ref=file_ref(self.root,'fixture.png');bridge={'figures':[{'id':'F1','artifact_ref':ref}]}
        result=compile_placements(self.root,bridge,[{'kind':'figure','visual_id':'F1','label':'fig:test','caption':'Unit test only.'}])
        self.assertIn('\\includegraphics',result['snippets'][0]['latex']);self.assertEqual(result['watch_refs'],[ref])

if __name__=='__main__':unittest.main()
