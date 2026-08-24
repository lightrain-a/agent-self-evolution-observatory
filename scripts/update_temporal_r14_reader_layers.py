#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PID='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK'

def replace_entry(path: Path, payload: dict):
    lines=path.read_text(encoding='utf-8').splitlines()
    prefix=json.dumps(PID,ensure_ascii=False)+':'
    found=0
    for i,line in enumerate(lines):
        if line.startswith(prefix):
            comma=',' if line.rstrip().endswith(',') else ''
            lines[i]=json.dumps(PID,ensure_ascii=False)+':'+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+comma
            found+=1
    if found!=1: raise RuntimeError(f'{path}: expected one {PID} entry, found {found}')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    reader={
      'short':'Temporal Attribution',
      'question':{'zh':'一个 temporal skill 看起来有效时，收益究竟是真正 repair、同 surface 的 output effect、placebo/surface perturbation，还是 integration surface？','en':'When a temporal skill appears effective, is the gain true repair, a same-surface output effect, placebo/surface perturbation, or the integration surface?'},
      'conclusion':{'zh':'不能把它们合成一个“skill effect”。R14 用 T−N、T−G₀、G₀−N、T−Rsurf 分开记账：C3 cutoff 的 +28pp 两臂结果被改判为 no repair；EIA 暴露 surface interaction；Rsurf 只保留 low-sensitivity frozen-margin surface check。','en':'They cannot be collapsed into one “skill effect.” R14 separates T−N, T−G0, G0−N, and T−Rsurf: the +28pp C3 cutoff two-arm result becomes no repair, EIA exposes surface interaction, and Rsurf supports only a low-sensitivity frozen-margin surface check.'},
      'science':{'zh':'Reusable-skill attribution audit + verdict reversal','en':'Reusable-skill attribution audit + verdict reversal'},
      'method':[{'zh':'N：判断相对原 Agent 的 net repair','en':'N: determine net repair over the original agent'},{'zh':'G₀：同 surface no-op，分开 T−G₀ 与 G₀−N','en':'G0: same-surface no-op, separating T−G0 from G0−N'},{'zh':'Rsurf：复用 exact output，只改变 forced one-answer integration surface','en':'Rsurf: reuse the exact output and change only the forced one-answer integration surface'}],
      'evidence':[
        {'m':'4W1T vs 5T','t':{'zh':'两臂假阳性被 N 改判','en':'N reverses a two-arm false positive'},'d':{'zh':'DeepSeek C3 cutoff：T/G/N=100/72/100；endpoint T−G=4胜1平，而 T−N=0胜5平，因此 no repair。','en':'DeepSeek C3 cutoff: T/G/N=100/72/100; endpoint T−G is 4W/1T while T−N is 0W/5T, so there is no repair.'}},
        {'m':'+37.5 = +62.5 − 25','t':{'zh':'EIA surface interaction','en':'EIA surface interaction'},'d':{'zh':'fresh EIA 中 T−N=+37.5、T−G₀=+62.5、G₀−N=−25；它只能作为 post-hoc compatibility probe。','en':'Fresh EIA gives T−N=+37.5, T−G0=+62.5, G0−N=−25; it is only a post-hoc compatibility probe.'}},
        {'m':'0.0pp · 1W/16T/1L','t':{'zh':'Exact-output Rsurf','en':'Exact-output Rsurf'},'d':{'zh':'18 个 pre-frozen DeepSeek endpoint 的 mean T−Rsurf=0；±10pp TOST 通过，但 sensitivity≈53%、ceiling-heavy、strictly non-ceiling n=4 unresolved。','en':'Across 18 pre-frozen DeepSeek endpoints mean T−Rsurf=0; the ±10pp TOST passes, but sensitivity≈53%, the portfolio is ceiling-heavy, and strictly non-ceiling n=4 remains unresolved.'}},
        {'m':'2,056 / 35 / 3','t':{'zh':'完整 source-native ledger','en':'Complete source-native ledger'},'d':{'zh':'2,056 条 runtime-valid row、35 个 endpoint、3 个一手机构系统；所有 fresh G₀/R calls 保留 CSV/raw/checkpoint。','en':'2,056 runtime-valid rows, 35 endpoints, and three first-party institutional systems; all fresh G0/R calls preserve CSV/raw/checkpoints.'}}
      ],
      'figure':{'title':{'zh':'R14：同一个“skill gain”拆成不同 attribution','en':'R14: decompose one apparent skill gain into distinct attributions'},'groups':[
        {'label':{'zh':'C3 cutoff · verdict reversal','en':'C3 cutoff · verdict reversal'},'items':[{'label':'Stress G','v':72,'display':'72%','role':'control'},{'label':'Original N','v':100,'display':'100%','role':'baseline'},{'label':'Targeted T','v':100,'display':'100%','role':'target'}]},
        {'label':{'zh':'EIA fresh · surface interaction','en':'EIA fresh · surface interaction'},'items':[{'label':'G0','v':37.5,'display':'37.5%','role':'control'},{'label':'N','v':62.5,'display':'62.5%','role':'baseline'},{'label':'T','v':100,'display':'100%','role':'target'}]}
      ],'callouts':[{'tone':'null','label':{'zh':'Rsurf 边界','en':'Rsurf boundary'},'value':{'zh':'mean residual 0 · sensitivity≈53% · non-ceiling n=4 unresolved','en':'mean residual 0 · sensitivity≈53% · non-ceiling n=4 unresolved'}}],'note':{'zh':'第一组说明 T>G 不等于 repair；第二组说明 T−G₀ 不能在 G₀−N≠0 时当作 pure operation effect。','en':'The first group shows T>G is not repair; the second shows T−G0 is not a pure operation effect when G0−N≠0.'}},
      'limitation':{'zh':'DeepSeek grounding 每 cell 只有 5 endpoint、Kimi grounding 被降级、EIA 是 post-hoc compatibility probe；Rsurf 只测 forced one-answer exact-output placement，不能外推 temporal-RAG equivalence 或 multi-turn callable advantage。','en':'DeepSeek grounding has only five endpoints per cell, Kimi grounding is downgraded, and EIA is a post-hoc compatibility probe; Rsurf only tests forced one-answer exact-output placement and cannot establish temporal-RAG equivalence or multi-turn callable advantage.'}
    }
    replace_entry(ROOT/'paper-reader-data.js',reader)

    nearest=[
      {'t':'Not All Skills Help: Measuring and Repairing Agent Knowledge','u':'https://arxiv.org/abs/2606.15390','d':{'zh':'randomized masking 已覆盖 per-skill causal contribution；R14 只能守 attribution decomposition。','en':'Randomized masking already covers per-skill causal contribution; R14 must stay on attribution decomposition.'}},
      {'t':'Counterfactual Trace Auditing of LLM Agent Skills','u':'https://arxiv.org/abs/2605.11946','d':{'zh':'paired with/without-skill trace 已覆盖普通 skill causality。','en':'Paired with/without-skill traces already cover ordinary skill causality.'}},
      {'t':'ContinualSkillBench: Can LLM Agents Truly Evolve Their Capabilities?','u':'https://arxiv.org/abs/2608.03874','d':{'zh':'reusable procedure utility 已有 continual evaluation；本文不再卖 skill utility。','en':'Reusable-procedure utility already has continual evaluation; this paper no longer sells skill utility.'}},
      {'t':'Agent Skills Can Be Harmful: An Empirical Study of Skill-Induced Failures in LLM Agents','u':'https://arxiv.org/abs/2608.11888','d':{'zh':'matched/no-skill attribution 已存在；R14 的残差是 net repair / surface perturbation / exact-output surface credit 的分解。','en':'Matched/no-skill attribution already exists; R14’s residual is the decomposition of net repair, surface perturbation, and exact-output surface credit.'}}
    ]
    novelty={
      'score':3.4,'label':{'zh':'中等 · 方法型 attribution audit','en':'moderate · methodological attribution audit'},'risk':'MEDIUM_HIGH','evidence':'STRONG','priority':4,
      'headline':{'zh':'“skills help”“paired skill causality”“temporal RAG”都已拥挤；R14 能保住的是：更强 control 如何改变 reusable-skill credit assignment 与 scientific verdict。','en':'Skills-help claims, paired skill causality, and temporal RAG are crowded; R14’s surviving axis is how stronger controls change reusable-skill credit assignment and scientific verdicts.'},
      'axis':{'zh':'从 procedure-bottleneck 收窄到 attribution audit：T−N=net repair；T−G₀ 与 G₀−N 分开；T−Rsurf 只测 forced one-answer exact-output surface placement。','en':'Narrow from procedure-bottleneck framing to attribution audit: T−N is net repair; T−G0 and G0−N remain separate; T−Rsurf only tests forced one-answer exact-output surface placement.'},
      'dims':{'problem':{'zh':'一个 apparent skill effect 到底应该把 credit 给谁？','en':'Where should credit for an apparent skill effect go?'},'treatment':{'zh':'N / stress-helper G / same-surface G₀ / exact-output Rsurf。','en':'N / stress-helper G / same-surface G0 / exact-output Rsurf.'},'controlled_variable':{'zh':'冻结 endpoint/evidence/model/scorer/procedure source；Rsurf 保持 exact output。','en':'Freeze endpoint/evidence/model/scorer/procedure source; Rsurf preserves the exact output.'},'estimand':{'zh':'net repair、same-surface output、surface perturbation、integration-surface residual。','en':'Net repair, same-surface output, surface perturbation, and integration-surface residual.'},'falsifier':{'zh':'T>G 但 T=N→no repair；G₀−N≠0→T−G₀ 不是 pure operation effect；Rsurf low-sensitivity boundary 必须保留。','en':'T>G but T=N→no repair; G0−N≠0→T−G0 is not a pure operation effect; the low-sensitivity Rsurf boundary must remain.'}},
      'nearest':nearest,
      'gap':{'zh':'Related Work 必须主动让出 causal skill utility、matched/no-skill control、skill compilation 与 temporal retrieval；只保留 attribution audit / verdict reversal。','en':'Related Work must explicitly surrender causal skill utility, matched/no-skill controls, skill compilation, and temporal retrieval, retaining only the attribution audit and verdict reversals.'},
      'question':{'zh':'当前判断：R14 的 verdict-reversal + surface-interaction + exact-output surface audit 是否足以构成 ICLR 方法/评测型贡献？新的 Stanford R14 外审正在等待。','en':'Current question: is R14’s verdict reversal + surface interaction + exact-output surface audit sufficient for an ICLR methodological/evaluation contribution? A fresh Stanford R14 review is pending.'},
      'next':{'zh':'不扩实验；保持 R14 narrow claim，等待新 Stanford 结果。','en':'Do not expand experiments; preserve the narrow R14 claim and wait for the fresh Stanford result.'},
      'reviewer_attack':{'verdict':'KEEP_NARROW','pressure_titles':['Anything2Skill: Compiling External Knowledge into Reusable Skills for Agents','Counterfactual Trace Auditing of LLM Agent Skills','Not All Skills Help: Measuring and Repairing Agent Knowledge'],'strongest_attack':{'zh':'Anything2Skill、paired skill auditing、causal masking 与 temporal retrieval 已让“procedure 有用 / skill 有因果作用 / RAG vs skill”失去 novelty；如果把 Rsurf 夸成独立 temporal retriever，R14 会直接过界。','en':'Anything2Skill, paired skill auditing, causal masking, and temporal retrieval already crowd procedure utility, causal skill effects, and RAG-vs-skill claims; treating Rsurf as an independent temporal retriever would immediately overclaim.'},'surrender':{'zh':'让出 skill acquisition、paired causality、matched/no-skill control、procedure-over-RAG、container superiority 与一般 temporal retrieval equivalence。','en':'Surrender skill acquisition, paired causality, matched/no-skill controls, procedure-over-RAG, container superiority, and general temporal-retrieval equivalence.'},'defended_residual':{'zh':'用四个 contrast 明确区分 net repair / same-surface output / placebo perturbation / one-answer integration surface，并展示这些 control 如何改判实际 verdict。','en':'Use four contrasts to separate net repair, same-surface output, placebo perturbation, and one-answer integration surface, showing how these controls change actual verdicts.'},'manuscript_action':{'zh':'贡献段只卖 attribution audit 与 verdict changes；EIA 保持 post-hoc probe，Rsurf 保持 low-sensitivity frozen-margin boundary。','en':'Sell only the attribution audit and verdict changes; keep EIA as a post-hoc probe and Rsurf as a low-sensitivity frozen-margin boundary.'}}
    }
    replace_entry(ROOT/'paper-novelty-audit-data.js',novelty)
    print('updated reader + novelty layers for',PID)
if __name__=='__main__': main()
