#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
OUT=GENERATED/'advisor-meeting-data.js'
manifest=json.loads((GENERATED/'advisor-paper-pack-manifest.json').read_text())

meeting_fields={
'E1':dict(best_case='用精确证书刻画：语义等价的 skill 打包/身份不应改变实际可访问的技能控制面，并定位 capacity-limited dynamic retrieval 下的表示不稳定。',advisor_question='真实 Agent skill ecosystem 中，capacity-limited dynamic retrieval 是否足够常见、足够重要，使这个 abstraction 值得 standalone paper？'),
'B1':dict(best_case='在 retrieved content/order 固定时，直接审计显式 source-outcome 信息到底改变多少局部动作与终端结果，把 provenance 的增量价值从 memory content 中分离出来。',advisor_question='在 terminal effect 稀疏的边界下，这个 provenance audit 是否仍足够 standalone，还是应与 Paper A 合并成更强的因果链？'),
'C1':dict(best_case='把“记忆写入了却没改变行为”拆成 write → native exposure → uptake → endpoint 的阶段证据，定位 persistent-memory transport 在哪里衰减。',advisor_question='stage-resolved diagnosis 本身是否足够构成 paper-level contribution，还是必须升级成 prospective repair/routing method？'),
'G1':dict(best_case='在安全干预改变 task-local capability 时，用 shared-capability witness 把“更安全”与“只是不会/拒绝做任务”分开，再比较 Updated vs Frozen 的纵向安全变化。',advisor_question='capability-matched safety evaluation 是足够强的 methodology problem，还是应收窄成特定 web-agent evaluation protocol？'),
'E2':dict(best_case='同一 evidence package 可以生成不同 persistent state；把 state generation 本身从 evidence selection 中分离出来，审计 self-evolution 的 regeneration instability。',advisor_question='“acting/serving evidence → persistent state”中的 generator-factor instability 是否是现实 self-evolving agent 的核心问题，正确 abstraction 应落在哪个 community vocabulary？'),
'PAPER_A':dict(best_case='从“memory 会影响动作”推进到“这种影响是否忠实追随 source experience”，用 no-op / unrelated / same-content provenance controls 做 causal fidelity audit。',advisor_question='Influence–Fidelity 是否应该独立成 embodied-memory identification paper，还是作为 B1/Paper B 的机制证据更合适？'),
'CONSTRAINT_EXTERNALITY':dict(best_case='同一个局部 repair 在保持 target gain 时可能对非目标约束产生 collateral regression；用 matched UPDATE/NO_UPDATE 和预声明 coupling topology 分离这种外部性。',advisor_question='constraint externality 的核心贡献更应该是 measurement、prediction 还是 mitigation/control？'),
'PAPER_B':dict(best_case='用 exact persistent-state fork（Committed-Update vs Frozen-Preupdate）和 source/verification/future 分离，定义真正跨 episode 的 embodied self-evolution。',advisor_question='persistent embodied memory 的 longitudinal identification 是否值得作为独立主 paper，还是应与 Paper A 合并成一个完整 causal story？'),
'3D':dict(best_case='在 relation count、对象、谓词和 decoder 全部匹配时，只改变 Chain/Hub endpoint-sharing topology，再用 oracle-graph substitution 定位 Text→Graph 与 Graph→Scene bottleneck。',advisor_question='relation topology 是真实 3D instruction complexity 的关键变量，还是 controlled benchmark 中才突出的分析轴？')}

order=['E1','B1','C1','G1','E2','PAPER_A','CONSTRAINT_EXTERNALITY','PAPER_B','3D']
papers=[]
for d in manifest['papers']:
    pid=d['paper_id']
    review_path=GENERATED/f"stanford-{pid.lower()}-review.json"
    review=json.loads(review_path.read_text()) if review_path.exists() else None
    public_pdf='downloads/advisor-20260906/'+d['filename']
    row={
      'paper_id':pid,'order':order.index(pid)+1,'title':d['title'],'paper_status':d['paper_status'],
      'pages':d['pages'],'pdf_sha256':d['pdf_sha256'],'pdf':public_pdf,
      'paper_candidate_ref':d['paper_candidate_ref'],'scientific_canonical_ref':d['scientific_canonical_ref'],
      'science_delta':d['delta'],'best_case':meeting_fields[pid]['best_case'],'advisor_question':meeting_fields[pid]['advisor_question'],
      'stanford':{'status':'PROCESSING'}
    }
    if review:
      row['stanford']={k:review.get(k) for k in ['status','numerical_score','textual_signal','review_date','advisor_digest','token_fingerprint_sha256_16']}
      if review.get('status')=='SUBMITTED': row['stanford']['status']='PROCESSING'
    papers.append(row)

shared=[
 {'id':'persistent-memory-object','label':'Persistent-memory object / state semantics','papers':['B1','C1','E2','PAPER_A','PAPER_B'],'question':'这些论文是否共享了一个未经充分验证的 persistent-state / memory semantics 前提？一个 closure 是否能同时给多篇降风险？'},
 {'id':'provenance-fidelity','label':'Provenance / source-fidelity distinction','papers':['B1','PAPER_A','PAPER_B'],'question':'provenance、source fidelity 与 longitudinal persistent utility 是否应拆成三篇，还是应形成 parent-child / merge 结构？'},
 {'id':'controlled-update','label':'Controlled update and capability preservation','papers':['G1','CONSTRAINT_EXTERNALITY'],'question':'安全 capability confound 与 update collateral 是否共享一个更高层 controlled-update scientific object？'},
 {'id':'representation-support','label':'Representation / identity support','papers':['E1','E2','C1'],'question':'identity/representation changes 是否只是各自 substrate artifact，还是 self-evolution control surface 的共同系统问题？'}]

schedule=[['14:00','14:15','Portfolio Dashboard + Common-Cause Risk Scan'],['14:15','14:40','E1'],['14:40','15:30','Memory / Provenance / Evolution family'],['15:30','15:55','G1 + Constraint Externality'],['15:55','16:10','3D'],['16:10','16:35','Exception-based nine-paper closure sweep'],['16:35','16:53','Cost / Dependencies / Scheduling'],['16:53','17:00','Read-back']]
data={'schema_version':'1.0','generated_at':'2026-09-05','meeting':{'id':'2026-09-06-advisor','main_ref':manifest['meeting_candidate_main'],'status':manifest.get('paper_pack_status'),'review_route':'exception-and-boundary-review'},'papers':papers,'shared_risks':shared,'schedule':[{'start':a,'end':b,'label':c} for a,b,c in schedule]}
OUT.write_text('window.ADVISOR_MEETING_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(OUT)
print('papers',len(papers),'review_ready',sum((p['stanford'].get('status')=='READY') for p in papers))
