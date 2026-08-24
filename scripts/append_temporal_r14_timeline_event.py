#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/'generated'
PID='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK'
SRC=GEN/'temporal-skill-r14-stanford-submission-public-20260824.json'
OUT=GEN/'research-timeline.json'; JS=GEN/'research-timeline.js'

def china_date(iso:str)->str:
    try:return datetime.fromisoformat(iso).astimezone(timezone(timedelta(hours=8))).date().isoformat()
    except Exception:return iso[:10]

def main():
    t=json.loads(OUT.read_text(encoding='utf-8')); s=json.loads(SRC.read_text(encoding='utf-8'))
    reg=json.loads((GEN/'paper-registry.json').read_text(encoding='utf-8'))
    p=next(x for x in reg['papers'] if x.get('paper_id')==PID)
    digest=hashlib.sha256(SRC.read_bytes()).hexdigest()
    occurred=s['submitted_at_utc']
    seed='|'.join((occurred,'paper',PID,'SUBMITTED_FOR_EXTERNAL_REVIEW',SRC.name))
    eid=hashlib.sha256(seed.encode()).hexdigest()[:16]
    event={
      'event_id':eid,'occurred_at':occurred,'time_precision':'exact','event_class':'paper','importance':'detail','origin':'artifact_full_history',
      'research_id':PID,'research_label_zh':'E2 · Temporal Skill · R14','title':s['title'],'title_zh':'E2 R14 已提交 Stanford 外部审稿，结果待回','state_before':'SUBMISSION_READY','state_after':'SUBMITTED_FOR_EXTERNAL_REVIEW',
      'summary':{'en':'E2 R14 was submitted to Stanford Agentic Reviewer; the fresh review result is pending.','zh':'E2 R14 已重新提交 Stanford Agentic Reviewer；当前只记录送审成功，新的 review 结果仍待返回。'},
      'why':{'en':'This records the latest external-review handoff without pre-filling a score or verdict.','zh':'用于把最新外部审稿 handoff 放入研究时间轴；结果返回前不预填分数或 verdict。'},
      'limitation':{'en':'External review is advisory only; the token and email remain private and this event creates no scientific authority.','zh':'外审只提供 advisory signal；review token 与邮箱保持私有，这条时间轴记录不增加科研权限。'},
      'next_action':'Wait for the fresh Stanford R14 review and adjudicate only its decision-critical objections.','next_action_zh':'等待 R14 新外审；只对 decision-critical objection 做后续裁决，不自动扩实验。','reopen_condition':'','reopen_condition_zh':'外审本身不能自动重开实验；如需新实验仍须单独满足 Research OS gate。',
      'evidence':[{'label':'revision','value':'R14'},{'label':'PDF SHA256','value':s['pdf_sha256']},{'label':'pages','value':s['pdf_pages']},{'label':'review result','value':'PENDING'}],
      'authority':{'scientific':False,'scope':'read-only external-review submission record','scope_zh':'只读外审送审记录；无科研、实验、GPU 或投稿状态授权。','projection_can_change_state':False},
      'sources':[{'path':str(SRC.relative_to(ROOT)),'sha256':digest,'public':True}],
      'links':[{'label':'论文','href':'selected-paper.html'},{'label':f'Paper {PID}','href':f'selected-paper.html?paper={PID}'}],
      'canonical_refs':{'research_items':[],'experiments':[],'papers':[{'paper_id':PID,'source_research_item':p.get('source_research_item_id',''),'paper_stage':p.get('paper_stage') or p.get('current_state'),'scientific_status':p.get('scientific_status'),'submission_ready':p.get('submission_ready')}],'categories':[]}
    }
    events=[x for x in t.get('events',[]) if x.get('event_id')!=eid and not any(src.get('path')==str(SRC.relative_to(ROOT)) for src in x.get('sources',[]) if isinstance(src,dict))]
    events.append(event);events.sort(key=lambda x:(x.get('occurred_at',''),x.get('importance')=='key',x.get('event_id','')),reverse=True)
    classes=Counter(x.get('event_class') for x in events);dates=Counter(china_date(x.get('occurred_at','')) for x in events)
    old=t.get('summary',{}); summary=dict(old)
    summary.update({'events':len(events),'dated_structured_artifacts_projected':int(old.get('dated_structured_artifacts_projected',0))+1,'runtime_memory_events':sum(x.get('origin')=='research_memory_db' or x.get('research_id')=='Research Memory' for x in events),'key_events':sum(x.get('importance')=='key' for x in events),'authority_bearing_scoped_events':sum(bool((x.get('authority') or {}).get('scientific')) for x in events),'canonical_research_bound_events':sum(bool((x.get('canonical_refs') or {}).get('research_items')) for x in events),'canonical_experiment_bound_events':sum(bool((x.get('canonical_refs') or {}).get('experiments')) for x in events),'canonical_paper_bound_events':sum(bool((x.get('canonical_refs') or {}).get('papers')) for x in events),'canonical_research_items_with_events':len({r.get('code') for x in events for r in (x.get('canonical_refs') or {}).get('research_items',[]) if r.get('code')}),'canonical_papers_with_events':len({r.get('paper_id') for x in events for r in (x.get('canonical_refs') or {}).get('papers',[]) if r.get('paper_id')}),'days':len(dates),'class_counts':dict(sorted(classes.items())),'date_counts':dict(sorted(dates.items(),reverse=True))})
    t['generated_at']=max((x.get('occurred_at','') for x in events),default=t.get('generated_at',''));t['summary']=summary;t['events']=events
    OUT.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');JS.write_text('window.RESEARCH_TIMELINE = '+json.dumps(t,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps({'event_id':eid,'events':len(events),'paper_events':summary['class_counts'].get('paper'),'canonical_papers_with_events':summary['canonical_papers_with_events'],'occurred_at':occurred},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
