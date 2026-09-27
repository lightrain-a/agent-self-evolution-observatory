#!/usr/bin/env python3
"""Read a frozen Git revision into a temporary text-only checkout and inventory it.

Does not checkout or modify the author's working tree, compile TeX, or publish text.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.paper_writing_sources import manuscript_inventory,safe_path
from research_pipeline.paper_writing_loop import write_json


def inspect(repo:Path,revision:str,main:str):
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True)
    commit=git('rev-parse','--verify',revision+'^{commit}').strip()
    paths=git('ls-tree','-r','--name-only',commit).splitlines()
    with tempfile.TemporaryDirectory(prefix='paper-writing-inventory-') as directory:
        root=Path(directory)
        for name in paths:
            if not name.endswith('.tex'):continue
            target=safe_path(root,name);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(git('show',commit+':'+name),encoding='utf-8')
        inventory=manuscript_inventory(root,main)
    return {'source_commit':commit,'inventory':inventory,'source_checkout_modified':False,'tex_compiled':False,'private_source_text_in_receipt':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--ref',default='origin/main');p.add_argument('--main',default='main.tex');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=inspect(a.repo,a.ref,a.main);write_json(a.output,result)
    print(json.dumps({'source_commit':result['source_commit'],'source_files':len(result['inventory']['files']),'unresolved':result['inventory']['unresolved'],'source_checkout_modified':False},ensure_ascii=False))

if __name__=='__main__':main()
