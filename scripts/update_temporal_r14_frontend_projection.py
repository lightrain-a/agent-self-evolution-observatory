#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'generated'/'stanford-r2-objection-matrix.json'
J=ROOT/'generated'/'stanford-r2-objection-matrix.js'
PID='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK'

def main():
    d=json.loads(P.read_text(encoding='utf-8'))
    p=d['papers'][PID]
    p['read']={
      'zh':'Round 2 的历史文字 verdict 是 Weak Accept。R14 已执行 G₀ 与 exact-output Rsurf，并把论文收窄成 attribution audit；当前窄 claim 已通过 Research OS，新的 Stanford R14 review 已提交、结果待回。',
      'en':'The historical Round-2 textual verdict is Weak Accept. R14 executes G0 and exact-output Rsurf and narrows the paper to an attribution audit; the current narrow claim is Research-OS clean and a fresh Stanford R14 review is pending.'}
    p['next']={
      'zh':'不再自动扩实验。等待 R14 新外审；只有新意见对当前窄 claim 提出 decision-critical 缺口时才考虑 reopen。',
      'en':'Do not expand experiments automatically. Wait for the fresh R14 external review and reopen only if it identifies a decision-critical gap in the current narrow claim.'}
    for o in p['objections']:
        oid=o['id']
        if oid=='TEMP-O4':
            o.update({'d':'RESOLVED','why':{
              'zh':'R14 已执行 same-surface no-op G₀。结果反而证明 full-track neutrality 不能自动运输到每个 stratum，因此论文把 G₀ 改成 placebo/surface diagnostic，并把 T−G₀ 与 G₀−N 分开；当前 claim 不再依赖“behavior-neutral generic”假设。',
              'en':'R14 executes same-surface no-op G0. The result shows full-track neutrality does not automatically transport to every stratum, so G0 is reframed as a placebo/surface diagnostic and T−G0 is kept separate from G0−N; the current claim no longer depends on a behavior-neutral-generic assumption.'},'action':'NONE','e':'R14 G0 A1/A2/Kimi execution + contrast decomposition; current claim audit 13/13','canon':'R14_CURRENT_CANONICAL'})
            o.pop('reopen',None)
        elif oid=='TEMP-O5':
            o.update({'d':'PERMANENT_CLAIM_BOUNDARY','why':{
              'zh':'R14 已执行 exact-output Rsurf，只能识别 forced one-answer harness 的 integration-surface placement；它不是独立 temporal retriever。论文明确删除 skill-vs-temporal-RAG equivalence / superiority claim，真正独立 retriever 留作更宽 future claim 的 reopen，而不是当前缺口。',
              'en':'R14 executes exact-output Rsurf, which only identifies integration-surface placement under the forced one-answer harness and is not an independent temporal retriever. The paper explicitly removes skill-vs-temporal-RAG equivalence/superiority claims; a real independent retriever is a reopen condition for a broader future claim, not a gap in the current one.'},'action':'NONE','e':'R14 Rsurf 18-endpoint frozen-margin check + explicit retrieval-equivalence disclaimer','canon':'R14_CURRENT_CANONICAL'})
            o['reopen']={
              'zh':'只有未来要主张 temporal-retrieval equivalence / superiority 时，才需要同 raw candidates 的独立 retriever/reranker。',
              'en':'Only a future temporal-retrieval equivalence/superiority claim requires an independent retriever/reranker over the same raw candidates.'}
        elif oid=='TEMP-O6':
            o['why']={'zh':'R14 进一步收窄：DeepSeek grounding 每 cell n=5 仅 directional；Kimi grounding 被降级；EIA 仅 post-hoc compatibility probe；Rsurf non-ceiling n=4 unresolved。','en':'R14 narrows further: DeepSeek grounding is directional with n=5 per cell; Kimi grounding is downgraded; EIA is only a post-hoc compatibility probe; Rsurf non-ceiling n=4 remains unresolved.'}
            o['canon']='R14_CURRENT_CANONICAL'
    # recompute global disposition summary without changing the historical objection count
    counts=Counter()
    total=0
    for paper in d['papers'].values():
        for o in paper.get('objections',[]):
            total+=1; counts[o.get('d','')]+=1
    d['summary'].update({
      'papers':len(d['papers']),
      'objections':total,
      'resolved':counts['RESOLVED'],
      'existing_evidence_actionable':counts['EXISTING_EVIDENCE_ACTIONABLE'],
      'requires_scientific_reopen':counts['REQUIRES_SCIENTIFIC_REOPEN'],
      'permanent_claim_boundary':counts['PERMANENT_CLAIM_BOUNDARY'],
      'automatic_actions':0})
    d['rechecked_at_utc']='2026-08-24T05:43:19.300739+00:00'
    d['recheck']='Round 2 reviewer text preserved; current Temporal dispositions reconciled to canonical R14. Fresh R14 external review pending.'
    P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    J.write_text('window.STANFORD_R2_OBJECTION_MATRIX = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps({'summary':d['summary'],'temporal':[(o['id'],o['d']) for o in p['objections']]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
