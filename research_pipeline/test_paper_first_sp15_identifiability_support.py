from __future__ import annotations
import unittest
from .paper_first_sp15_identifiability_support import build_sp15_identifiability_support, validate_sp15_identifiability_support

class SP15SupportTest(unittest.TestCase):
    def setUp(self): self.state=build_sp15_identifiability_support()
    def test_valid(self):
        self.assertEqual(validate_sp15_identifiability_support(self.state),[])
        s=self.state['summary']; self.assertEqual((s['primary_or_author_releases_audited'],s['query_level_identifiability_units'],s['support_status']),(5,0,'INSUFFICIENT_FOR_IDENTIFIABILITY_CLAIM'))
    def test_released_query_inventory(self):
        row=next(x for x in self.state['audited_sources'] if x['ref']=='arXiv:2606.03565'); a=row['released_data_audit']
        self.assertEqual((a['test_queries'],a['unique_exact_query_strings'],a['duplicate_exact_query_strings']),(5696,5696,0)); self.assertFalse(row['identifiability_unit_support'])
    def test_zero_authority(self):
        self.assertFalse(self.state['near_equivalent_scan']['scientific_authority'])
        for k in ('method_design_authorized','experiment_blueprint_authorized','local_validation_authorized','p0_authorized','gpu_authorized'): self.assertEqual(self.state['summary'][k],0)
if __name__=='__main__': unittest.main()
