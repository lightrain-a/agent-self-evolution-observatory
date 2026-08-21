from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .paper_assertion_policy import audit_manuscript_directory


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(cond: bool, message: str, checks: list[dict[str, Any]]) -> None:
    checks.append({"check": message, "pass": bool(cond)})
    if not cond:
        raise AssertionError(message)


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--paper-dir',type=Path,required=True)
    p.add_argument('--sentinel',type=Path,required=True)
    p.add_argument('--retro',type=Path,required=True)
    p.add_argument('--certificate',type=Path,required=True)
    p.add_argument('--claim-ledger',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    checks=[]
    sentinel=json.loads(a.sentinel.read_text()); retro=json.loads(a.retro.read_text()); cert=json.loads(a.certificate.read_text()); ledger=json.loads(a.claim_ledger.read_text())
    tex='\n'.join(path.read_text(encoding='utf-8') for path in [a.paper_dir/'main.tex',*sorted((a.paper_dir/'sections').glob('*.tex'))])
    pdf=a.paper_dir/'main.pdf'
    require(pdf.exists(),'compiled PDF exists',checks)
    pages=int(subprocess.check_output(['pdfinfo',str(pdf)],text=True).split('Pages:')[1].splitlines()[0].strip())
    require(pages<=9,'PDF page count <= 9',checks)
    require(sentinel['summary']['ordinal_memory_pass']==18 and sentinel['summary']['ordinal_memory_total']==18,'sentinel ordinal = 18/18',checks)
    require(sentinel['summary']['shuffled_memory_pass']==0 and sentinel['summary']['shuffled_memory_total']==36,'sentinel shuffled = 0/36',checks)
    require(cert['status']=='OBSERVED_GROUND_TRUTH_INVALIDATION_CERTIFIED','direct invalidation certificate is certified',checks)
    require(cert['summary']['direct_writer_reader_chain_certified'] is True,'direct writer-reader chain certified',checks)
    require(retro['summary']['lower_bound_exposed_reader_units_in_memory_shuffles']==887,'retrospective exposed units = 887',checks)
    require(retro['summary']['lower_bound_exposed_reader_failures_in_memory_shuffles']==424,'retrospective exposed failures = 424',checks)
    expected={('wa_awm','shuffle1'):0.444987,('wa_awm','shuffle2'):0.345621,('wa_rbank','shuffle1'):0.148604,('wa_rbank','shuffle2'):0.175033}
    by={(r['method'],r['order']):r for r in retro['order_contrasts']}
    for key,value in expected.items():
        require(abs(by[key]['fraction_observed_gap_removed_by_sensitive_reader_exclusion']-value)<1e-9,f'{key} gap-reduction fraction matches',checks)
    for token in ('18/18','0/36','887','424','44.5','34.6','14.9','17.5'):
        require(token in tex,f'headline token {token} appears in manuscript',checks)
    require('environment carryover does not explain the full' in a.claim_ledger.read_text(encoding='utf-8').lower(),'claim ledger explicitly rejects full-explanation claim',checks)
    claim_verdicts={r['claim_id']:r['verdict'] for r in ledger['claims']}
    require(claim_verdicts=={'C1':'SUPPORTED','C2':'SUPPORTED','C3':'SUPPORTED','C4':'SUPPORTED_ACTIVE','C5':'REFUTED','C6':'ACTIVE_UNREFUTED_HYPOTHESIS'},'claim ledger verdicts frozen',checks)
    c6=next(r for r in ledger['claims'] if r['claim_id']=='C6')
    require(c6.get('evidence_state')=='INCONCLUSIVE','C6 evidence state remains separate from manuscript stance',checks)
    require(c6.get('claim_narrowing_required') is False,'unrefuted C6 does not trigger claim narrowing',checks)
    style_audit=audit_manuscript_directory(a.paper_dir)
    require(style_audit['passed'] is True,'paper assertion/style policy passes',checks)
    log=(a.paper_dir/'main.log').read_text(encoding='utf-8',errors='replace')
    require('undefined citations' not in log.lower(),'no undefined citations',checks)
    require('undefined references' not in log.lower(),'no undefined references',checks)
    require('overfull' not in log.lower(),'no overfull boxes',checks)
    pdftext=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace')
    require('Anonymous authors' in pdftext,'ICLR anonymous author placeholder present',checks)
    require(re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}',pdftext) is None,'no author email leaked',checks)
    require(all(token.lower() not in pdftext.lower() for token in ('/home/wyt','222.20.126.69','lightrain')),'no internal path host or project identity leaked',checks)
    normalized_pdftext=re.sub(r'[^a-z0-9]+','',pdftext.lower())
    require('istheagentfragile' in normalized_pdftext and 'auditingtaskordereffects' in normalized_pdftext,'paper title present',checks)
    source_files=[a.paper_dir/'main.tex',a.paper_dir/'references.bib',*sorted((a.paper_dir/'sections').glob('*.tex')),*sorted((a.paper_dir/'figures').glob('*.pdf'))]
    evidence_files=[a.sentinel,a.retro,a.certificate,a.claim_ledger,Path('generated/d5-order-environment-interference-audit.json'),Path('generated/d5-env-order-child-birth-receipt.json'),Path('generated/d5-env-order-paper-design.json')]
    report={'schema_version':'1.1','status':'PASS','summary':{'checks':len(checks),'passed':sum(c['pass'] for c in checks),'pages':pages,'pdf_sha256':sha(pdf),'pdf_bytes':pdf.stat().st_size},'checks':checks,'style_audit':style_audit,'manuscript_files':[{'path':str(x),'sha256':sha(x)} for x in source_files if x.exists()],'evidence_files':[{'path':str(x),'sha256':sha(x)} for x in evidence_files if x.exists()],'scientific_authority':False}
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'summary':report['summary']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
