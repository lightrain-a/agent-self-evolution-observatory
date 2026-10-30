#!/usr/bin/env python3
"""Dependency-free source/HTML audit for the manuscript-backed reader index."""
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.cards=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if 'data-atlas-item' in a:self.cards.append(a.get('data-kind'))
  if 'href' in a:self.links.append(a['href'])

def main():
 d=json.loads((ROOT/'rsi/experiment-catalog.json').read_text(encoding='utf-8'))
 assert re.fullmatch(r'[a-f0-9]{40}',d['source_commit'])
 assert len({x['id'] for x in d['datasets']})==len(d['datasets'])==54
 assert len({x['id'] for x in d['records']})==len(d['records'])==180
 assert sum(len(x['uses']) for x in d['datasets'])==71
 assert sum(u['kind']=='application' for x in d['datasets'] for u in x['uses'])==59
 ids={r['id'] for r in d['records'] if r['kind']=='paper'}
 for x in d['datasets']:
  for u in x['uses']:
   assert u['kind'] in {'application','introduction','protocol'}
   assert u['source']['url'].startswith('https://')
   assert set(u['study_ids'])<=ids
   assert u['role'].strip()
 locomo=next(x for x in d['datasets'] if x['id']=='locomo')
 assert {u['paper'] for u in locomo['uses']}=={'A-Mem','Memory-R1'}
 assert all(u['kind']=='application' for u in locomo['uses'])
 assert all(u['kind']=='protocol' for x in d['datasets'] if x['id']=='sipbench' for u in x['uses'])
 p=Page();page=(ROOT/'rsi/experimental-atlas.html').read_text(encoding='utf-8');p.feed(page)
 assert len(p.ids)==len(set(p.ids)), 'Duplicate HTML ID'
 assert Counter(p.cards)=={'datasets':54,'paper':60,'metric':64,'control':18,'family':38}
 assert d['source_commit'] in page
 assert all('dataset-'+x['id'] in p.ids for x in d['datasets'])
 assert all('record-'+r['id'] in p.ids for r in d['records'])
 assert 'experimental-atlas' in (ROOT/'rsi/page-router.js').read_text()
 assert 'experimental-atlas.html' in (ROOT/'rsi/site-nav.js').read_text()
 for name in ('experimental-atlas.js','experimental-atlas.css','experiment-catalog.json'):
  assert (ROOT/'rsi'/name).is_file()
 print('Experimental atlas passed: 54 resource entries, 71 typed relations, 180 preserved register entries; source '+d['source_commit'])
if __name__=='__main__':main()
