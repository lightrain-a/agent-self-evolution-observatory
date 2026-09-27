#!/usr/bin/env python3
"""Refresh public GitHub tree metadata, then rebuild the complete figure index.

No repository code or images are downloaded/executed. Incomplete network retrieval
fails before replacing the current knowledge base. Use --from-receipts for offline
rebuilds. No scheduled network calls are installed.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.figure_knowledge_base import SOURCES,build_knowledge_base,write_knowledge


def retrieve(key):
    repo=SOURCES[key]['repo']
    def get(suffix):
        req=Request('https://api.github.com/repos/'+repo+suffix,headers={'User-Agent':'Research-Figure-Knowledge-Index','Accept':'application/vnd.github+json'})
        with urlopen(req,timeout=20) as response:return json.load(response)
    meta=get('');commit=get('/commits?per_page=1')[0]
    tree=get('/git/trees/'+commit['sha']+'?recursive=1')
    if tree.get('truncated') is not False:raise ValueError('Refusing incomplete tree for '+repo)
    return key,{'repo':repo,'branch':meta['default_branch'],'sha':commit['sha'],
                'date':commit['commit']['committer']['date'],'license':meta.get('license'),'tree':tree}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--refresh',action='store_true',help='Explicit network refresh of four public repository metadata trees')
    p.add_argument('--from-receipts',type=Path,help='Directory with one previously fetched tree JSON per source')
    args=p.parse_args();receipt_file=ROOT/'research_pipeline'/'figure_knowledge_source_receipts.json'
    if args.from_receipts:
        receipts={k:json.loads((args.from_receipts/(k+'.json')).read_text()) for k in SOURCES}
    elif args.refresh:
        with ThreadPoolExecutor(max_workers=4) as pool:receipts=dict(pool.map(retrieve,SOURCES))
    elif receipt_file.exists():receipts=json.loads(receipt_file.read_text())
    else:p.error('No saved receipts; use --refresh or --from-receipts')
    kb=build_knowledge_base(receipts)
    receipt_file.write_text(json.dumps(receipts,separators=(',',':'))+'\n',encoding='utf-8')
    write_knowledge(kb,ROOT)
    print(json.dumps(kb['summary'],ensure_ascii=False))

if __name__=='__main__':main()
