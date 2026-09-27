"""Tests check research-bookkeeping, not vulnerability reproduction or novelty."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from .skill_security_round1 import (SCOPE_FILE,load,validate_sources,validate_program,public_state,
    literature_markdown,private_markdown,candidate_packet,write_public)
from .skill_security_round1_sources import SOURCES,NATIVE_OBSERVATIONS


def fixture():
    scope=load(SCOPE_FILE)
    idea={'id':'TEST-PRIVATE','title':'PRIVATE_SENTINEL_NOT_FOR_PUBLICATION','question':'Fixture question',
        'status':'PRIORITY_NATIVE_QUALIFICATION','source_ids':['D01','D02'],'surfaces':['AS04'],
        'nearest_collision':'Fixture nearest work','conditional_difference':'Unverified fixture difference',
        'native_reproduction':'NOT_RUN','novelty':'UNCONFIRMED','scientific_status':'PROPOSED_NOT_VALIDATED',
        'attacker':'Fixture package-only control','example':'Inert local test only',
        'hypotheses':[{'id':'H1','claim':'Fixture H1','prediction':'Expected A'}, {'id':'H2','claim':'Fixture H2','prediction':'Expected B'}],
        'p0':{'mode':'SOURCE_AUDIT','units':'one inert fixture','budget':{'initial_provider_calls':0,'no_automatic_launch':True},
              'controls':['no skill'],'measure':['inert event'],'stop':'Documented behavior only => stop novelty claim'},
        'next_action':'Read native source','paper_boundary':'Fixture only'}
    return {**scope,'ideas':[idea],'research_executions':0,'provider_calls':0}


class SkillSecurityTests(unittest.TestCase):
    def test_source_identity_and_count(self):
        ids=validate_sources();self.assertEqual(len(ids),39);self.assertEqual(sum(s['kind']=='PAPER' for s in SOURCES),24)
    def test_primary_read_depth_and_boundary_required(self):
        self.assertTrue(all(s['read_level'] and s['supports'] and s['does_not_establish'] for s in SOURCES))
        self.assertTrue(all(s['primary_source'] and not s['reproduced_by_us'] for s in SOURCES))
    def test_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):validate_sources(SOURCES+[SOURCES[0]])
    def test_future_evidence_rejected(self):
        sources=copy.deepcopy(SOURCES);sources[0]['checked_on']='2099-01-01'
        with self.assertRaises(ValueError):validate_sources(sources)
    def test_no_self_certified_reproduction(self):
        sources=copy.deepcopy(SOURCES);sources[0]['reproduced_by_us']=True
        with self.assertRaises(ValueError):validate_sources(sources)
    def test_all_surfaces_have_sources(self):
        state=public_state();ids={s['id'] for s in SOURCES}
        self.assertEqual(len(state['surfaces']),12)
        self.assertTrue(all(set(s['sources'])<=ids for s in state['surfaces']))
    def test_native_observations_are_not_vulnerabilities(self):
        self.assertTrue(all(n['not_a_vulnerability_receipt'] for n in NATIVE_OBSERVATIONS))
        self.assertEqual(public_state()['summary']['reproduced_vulnerabilities'],0)
    def test_round2_stays_deferred(self):
        state=public_state();self.assertEqual(state['scope']['round'],1)
        self.assertEqual(state['scope']['round2'],'DEFERRED_DEFENSE_DESIGN')
        self.assertFalse(any(state['scope']['authority'].values()))
    def test_private_proposals_not_public(self):
        text=json.dumps(public_state(),ensure_ascii=False)
        self.assertNotIn('PRIVATE_SENTINEL',text);self.assertNotIn('conditional_difference',text)
        self.assertNotIn('hypotheses',text);self.assertNotIn('SS-R1-01',text)
    def test_source_scan_flags_not_exploit_prevalence(self):
        source=next(s for s in SOURCES if s['id']=='P01')
        self.assertIn('scanner',source['author_measurement']['interpretation'])
        self.assertIn('不是',source['does_not_establish'])
    def test_known_issue_and_advisory_separate(self):
        kinds={s['id']:s['kind'] for s in SOURCES}
        self.assertEqual(kinds['A01'],'MAINTAINER_ADVISORY');self.assertEqual(kinds['A02'],'ISSUE_REPORT')
    def test_plan_validation_not_scientific_pass(self):
        result=validate_program(fixture());self.assertEqual(result['novelty_confirmed'],0)
        self.assertFalse(result['experiment_authority']);self.assertIn('NOT_SCIENTIFIC_PASS',result['status'])
    def test_unknown_reference_rejected(self):
        p=fixture();p['ideas'][0]['source_ids']=['UNKNOWN']
        with self.assertRaises(ValueError):validate_program(p)
    def test_novelty_promotion_rejected(self):
        p=fixture();p['ideas'][0]['novelty']='CONFIRMED'
        with self.assertRaises(ValueError):validate_program(p)
    def test_reproduction_promotion_rejected(self):
        p=fixture();p['ideas'][0]['native_reproduction']='PASS'
        with self.assertRaises(ValueError):validate_program(p)
    def test_alternative_predictions_required(self):
        p=fixture();p['ideas'][0]['hypotheses'][1]['prediction']='Expected A'
        with self.assertRaises(ValueError):validate_program(p)
    def test_controls_and_stop_required(self):
        p=fixture();p['ideas'][0]['p0']['stop']=''
        with self.assertRaises(ValueError):validate_program(p)
    def test_execution_authority_cannot_be_added(self):
        p=fixture();p['scope']['authority']['experiment']=True
        with self.assertRaises(ValueError):validate_program(p)
    def test_private_packet_integrates_existing_planning_schema(self):
        p=fixture();packet=candidate_packet(p,'TEST-PRIVATE')
        self.assertEqual(packet['method_formation']['scientific_status'],'NOT_EVALUATED')
        self.assertEqual(packet['method_formation']['p0']['execution_status'],'NOT_EXECUTED')
        self.assertFalse(packet['automatic_promotion']);self.assertFalse(packet['provider_authority'])
    def test_known_collision_not_exported_for_execution(self):
        p=fixture();p['ideas'][0]['status']='COLLIDES_AS_STATED'
        with self.assertRaises(ValueError):candidate_packet(p,'TEST-PRIVATE')
    def test_private_markdown_preserves_collisions(self):
        text=private_markdown(fixture());self.assertIn('UNCONFIRMED',text);self.assertIn('NOT_RUN',text)
        self.assertIn('Fixture nearest work',text)
    def test_public_exports_only_reference_material(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);write_public(root)
            text=(root/'generated/skill-security-round1.json').read_text()
            self.assertNotIn('PRIVATE_SENTINEL',text)
            md=(root/'docs/skill-security-round1-survey.md').read_text()
            for source in SOURCES:self.assertIn(source['url'],md)
            self.assertIn('当前仍为0条本轮复现漏洞',md)
    def test_deterministic_no_hidden_network_calls(self):
        self.assertEqual(public_state(),public_state())
        self.assertEqual(public_state()['summary']['provider_calls'],0)

if __name__=='__main__':unittest.main()
