from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT
from .paper_first_p0_promotions import PROMOTION_BY_INCUBATION, PROMOTIONS

DEFAULT_JSON=PROJECT_ROOT/'generated'/'paper-first-idea-incubation.json'
DEFAULT_JS=PROJECT_ROOT/'generated'/'paper-first-idea-incubation.js'
POLICY={
 'schema_version':'1.1','paper_first_only':True,'novelty_premortem_precedes_method_implementation':True,
 'incubation_cannot_self_authorize_p0_or_gpu':True,'explicit_human_promotion_required_for_p0':True,
 'p0_lifecycle_does_not_equal_execution_authority':True,'blocked_candidates_remain_visible':True,
 'review_cutoff':'2026-08-12',
}

def _i(id,title_zh,title_en,theme,verdict,problem,novelty,principle,method,baseline,falsifier,nearest,risk):
 return {'id':id,'title':{'zh':title_zh,'en':title_en},'theme':theme,'verdict':verdict,
  'paper_problem':problem,'novelty_boundary':novelty,'principle':principle,'method':method,
  'strongest_baseline':baseline,'local_falsifier':falsifier,'nearest_work':nearest,'collision_risk':risk,
  'p0_authorized':False,'gpu_authorized':False}

CANDIDATES=(
 _i('PF-1','面向未来可学习性的自进化','Future-Learnability-Preserving Self-Evolution','longitudinal-adaptation','ADVANCE_TO_PAPER_DESIGN',
  '当前收益和旧能力保持都正常的持久更新，仍可能降低 Agent 下一次适应新任务的学习斜率/样本效率。',
  'CPE 看旧能力保持；continual-RL plasticity 看策略未来重学。剩余边界是 LLM Agent 自进化的 update-admission：显式保护下一次自进化能力。',
  '当前能力是 state value，未来可学习性是 option value；一次更新可以保住前者却损害后者。',
  'Future Learnability Probe Gate：对 incumbent/candidate 做匹配当前收益+retention 后，在密封 future-probe family 上执行同一受限后续适应，比较 adaptation AUC / improvement-per-example。',
  'Capability-Preserving Evolution / 普通 regression gate，只匹配当前收益和旧能力。',
  '找当前收益与 retention 匹配的更新对；在 2–3 个留出 micro-task family 上做相同 tiny adaptation。只有 future-learning AUC 超过 seed 噪声且预测后续适应时才 GO。',
  [{'ref':'arXiv:2605.09315','title':'Do Self-Evolving Agents Forget?'},{'ref':'arXiv:2604.15414','title':'Beyond Single-Model Optimization'}],
  'medium：必须证明 future learnability 不是 retention/current gain 的重命名。'),
 _i('PF-2','跨 Agent 更新表面的因果修复路由','Causal Routing Across Agent Update Surfaces','credit-assignment','ADVANCE_TO_PAPER_DESIGN',
  '同一个失败可能通过 prompt/memory、skill/workflow、tool/code 或 weights 修复；现有方法多预先固定更新表面，缺少跨表面的 repair ownership。',
  'WML 在 workflow/skill 内定位最小 edit；MOSS 选择 source-level。剩余问题是提交实现之前，哪个 persistent surface 才是最低作用域且因果充分的修复位置。',
  '最佳修复表面是能稳定消除失败、迁移到留出样本、且 collateral change 最小的最低作用域干预。',
  'Cross-Surface Intervention Router：在 3 类声明式表面上生成等信息最小修复，做 paired replay + held-out transfer，以 intervention outcome 而非 LLM 标签选择表面。',
  'WML smallest-edit、固定单表面 MOSS-style repair、同证据 LLM surface selector。',
  '构造 24–40 个具有独立 repair ownership 的失败；对每个 eligible surface 做匹配干预。只有 outcome 能稳定识别最小表面且优于 fixed/LLM routing 才 GO。',
  [{'ref':'arXiv:2607.20999','title':'Workflow-Localized Mechanism Learning'},{'ref':'arXiv:2605.22794','title':'MOSS'},{'ref':'arXiv:2607.13104','title':'Self-Improvements in Modern Agentic Systems'}],
  'low-medium：若只是 LLM 分类器，或一个表面对所有 failure 都支配，novelty 消失。'),
 _i('PF-3','证据门控的跨层经验固化','Evidence-Gated Cross-Level Experience Consolidation','experience-representation','REVISE_NOVELTY_BOUNDARY',
  '外部 memory/skill 可回滚但占 context；rule/adapter/weights 更便宜却可能丢失稀有策略。真正问题是何时值得向更高压缩层固化。',
  'Experience Compression Spectrum 已明确提出 adaptive cross-level compression 的 missing diagonal；Skill-SD/Skill-to-LoRA 已覆盖 internalization。必须把 novelty 收紧到非平凡的 consolidation decision rule。',
  '只有跨上下文重复证据表明细节不再必要时才提高压缩层级；过早固化首先损伤稀有恢复行为。',
  'Consolidation Evidence Ladder：episode→skill→compact rule/adapter，多级保存；只有 reuse/transfer/rare-case retention 证书通过才晋升。',
  'always external、always distill、fixed-frequency distill、最佳固定 representation level。',
  '在一个小型 skill-agent 任务上比较 1/2/4 个独立复用上下文后的 external skill vs rule/LoRA；只有 adaptive gate 优于所有 fixed policy 才 ADVANCE。',
  [{'ref':'arXiv:2604.15877','title':'Experience Compression Spectrum'},{'ref':'arXiv:2604.10674','title':'Skill-SD'},{'ref':'arXiv:2606.16769','title':'Skill-to-LoRA'}],
  'high：目前很像 survey open problem + 已有 internalization 的组合。'),
 _i('PF-4','保持可诊断性的自进化','Diagnosability-Preserving Self-Evolution','observability-reliability','ADVANCE_TO_PAPER_DESIGN',
  '更新可以提高 task success，却让未来失败更难定位：trace 区分度下降、错误信号被吞掉或 provenance 不足。',
  'AHE 用 observability 驱动 harness evolution；silent-failure/REFLECT 研究故障诊断。新边界是把 diagnosability 本身作为更新后必须保持的 commit invariant。',
  'Agent 不应通过消耗“诊断下一次失败所需证据”换取当前能力。',
  'Diagnostic Preservation Certificate：密封 failure-probe + 固定外部 observer，比较更新前后 failure-cause separability 与 provenance coverage；任务收益为正且诊断性不退化才 commit。',
  'task regression + trace completeness；AHE-style observability 仅作为优化输入。',
  '小型 coding/tool agent 注入 3–4 类 failure cause；找 success 匹配但 post-update cause-localization AUROC 不同的修改对。差异必须可重复且预测 repair cost。',
  [{'ref':'arXiv:2604.25850','title':'Agentic Harness Engineering'},{'ref':'arXiv:2606.14589','title':'When Errors Become Narratives'},{'ref':'arXiv:2606.09071','title':'REFLECT'}],
  'medium：必须证明不是普通 trace-completeness 或 AHE observability。'),
 _i('PF-5','行为变化前沿的验证义务','Behavior-Frontier Verification Obligations','verification','REVISE_NOVELTY_BOUNDARY',
  '固定 regression suite 测旧行为，但候选自更新会产生 candidate-specific 行为变化；是否应从 incumbent↔candidate divergence 自动生成新验证义务？',
  'MOSS 已有 replay/health probe，Self-Harness 有 held-out regression，SEAL 有 sealed audit。只剩 candidate-specific changed/reachable behavior 的测试生成边界。',
  '测试预算应该集中到候选真正改变行为的区域。',
  'Behavior-Divergence Test Frontier：配对 incumbent/candidate trace，定位实质 state-action divergence，在这些区域生成有独立真值的 bounded tests。',
  'MOSS replay、Self-Harness held-out、SEAL、matched-budget random/adversarial test generation。',
  '20–30 个 harness/code edit 上，在相同测试数下比较 divergence-targeted/fixed/random/adversarial；只有发现独有真实 regression 且 precision/recall 显著更高才 ADVANCE。',
  [{'ref':'arXiv:2605.22794','title':'MOSS'},{'ref':'arXiv:2607.24300','title':'Self-Authored Verification Is Unreliable'},{'ref':'arXiv:2606.09498','title':'Self-Harness'}],
  'high：很容易退化成另一个 regression-test generator。'),
 _i('PF-6','自进化中的失败模式迁移','Failure-Mode Transport Under Self-Evolution','longitudinal-reliability','ADVANCE_TO_PAPER_DESIGN',
  '总成功率上升时，剩余失败可能迁向更 silent、更 severe 或更难恢复的类别；aggregate metric 会把这种 harmful substitution 藏起来。',
  'failure-driven improvement 已观察 remaining-error distribution shift；false-success/meltdown 刻画静态失败类。新问题是持久更新前后 failure probability mass 的配对纵向 transport。',
  '更新应按失败质量在 severity/observability/recoverability 类别间的迁移，而不只按总失败率判断。',
  'Failure Transport Matrix：用独立环境真值配对 incumbent/candidate，估计注册 failure classes 之间的 transport matrix 与风险加权 delta；成功率升但质量迁向 silent/severe 类时拒绝。',
  'aggregate success/regression、capability retention、静态 silent-failure detector。',
  '选有环境真值的 Agent 场景，预注册 4–6 类 failure，评估 10–20 个候选 update；只有 success gain 相近但 transport risk 稳定不同才 GO。',
  [{'ref':'arXiv:2606.31270','title':'Learning from Failure'},{'ref':'arXiv:2606.09863','title':'From Confident Closing to Silent Failure'},{'ref':'arXiv:2605.19149','title':'Agent Meltdowns'}],
  'medium：必须做 paired transport，不可只加一个 failure-weighted metric。'),
 _i('PF-7','Agent 更新后的影响感知证据重验证','Impact-Aware Evidence Revalidation After Agent Updates','evidence-lifecycle','REVISE_NOVELTY_BOUNDARY',
  '更新后部分旧证据仍有效，依赖已改变行为路径的证据则失效；全部重跑太贵，全部相信不安全。',
  'AHE 绑定 edit/prediction，MOSS replay failure batch，SEAL 固定 external audit；剩余边界是 evidence-scope dependency 与 selective invalidation。',
  '证据具有作用域；更新必须使所有受影响证据失效，同时不必重跑真正独立的证据。',
  'Evidence Impact Graph：claim/test↔component/behavior/assumption/artifact 依赖图，从 update diff 得到 impact set，重跑覆盖全部 affected claims 的最小证据切集。',
  'full revalidation、fixed smoke suite、component-name impact heuristic。',
  '回放具有 known regression 的历史 update；只有 selective set 保持 near-full detection recall 且显著省成本才 ADVANCE。',
  [{'ref':'arXiv:2604.25850','title':'Agentic Harness Engineering'},{'ref':'arXiv:2605.22794','title':'MOSS'},{'ref':'arXiv:2607.24300','title':'SEAL'}],
  'high：目前接近 software impact analysis + agent provenance，需要更强 agent-specific theorem/failure mode。'),
 _i('PF-8','自进化中的自写验证器漂移','Self-Authored Verifier Drift During Evolution','evaluation-integrity','BLOCK_COLLISION',
  'Agent 同时修改 policy 与负责评价 policy 的 tests/verifier 时，可能出现自评分上升而真实部署退化。',
  '该问题已被 SEAL 的 verifier–deployment gap 直接覆盖，也与本项目 C-2 evaluator-coadaptation / C-3 reward-invariance 高度重叠。',
  '独立真值必须位于可变 Agent 之外。','不设计新方法；作为 collision memory 保留。',
  'SEAL + 现有 C-2/C-3。','不授权 pilot；novelty collision 已足以 BLOCK。',
  [{'ref':'arXiv:2607.24300','title':'Self-Authored Verification Is Unreliable'}],
  'terminal collision'),
)

def build_paper_first_idea_incubation():
 counts=Counter(str(r['verdict']) for r in CANDIDATES); rows=[]
 for raw in CANDIDATES:
  row=dict(raw); idea_id=PROMOTION_BY_INCUBATION.get(str(row['id']))
  if idea_id:
   spec=PROMOTIONS[idea_id]; row.update({'p0_authorized':True,'gpu_authorized':False,'p0_idea_id':idea_id,'p0_code':spec['code'],'p0_group':spec['group'],'p0_entry_basis':'explicit-user-paper-first-p0-promotion'})
  rows.append(row)
 return {'schema_version':'1.1','review_date':'2026-08-12','policy':POLICY,
  'summary':{'candidates':len(CANDIDATES),'advance_to_paper_design':counts['ADVANCE_TO_PAPER_DESIGN'],
   'revise_novelty_boundary':counts['REVISE_NOVELTY_BOUNDARY'],'blocked_collision':counts['BLOCK_COLLISION'],
   'p0_authorized':sum(bool(r.get('p0_authorized')) for r in rows),'gpu_authorized':sum(bool(r.get('gpu_authorized')) for r in rows),'themes':len({r['theme'] for r in CANDIDATES})},
  'candidates':rows}

def validate_paper_first_idea_incubation(p):
 rows=list(p.get('candidates') or []); ids=[str(r.get('id') or '') for r in rows]; errors=[]
 if len(rows)<6: errors.append('incubation queue too narrow')
 if len(ids)!=len(set(ids)) or any(not x.startswith('PF-') for x in ids): errors.append('invalid incubation ids')
 allowed={'ADVANCE_TO_PAPER_DESIGN','REVISE_NOVELTY_BOUNDARY','BLOCK_COLLISION'}
 if any(r.get('verdict') not in allowed for r in rows): errors.append('unknown incubation verdict')
 if any(not r.get('nearest_work') or not r.get('novelty_boundary') or not r.get('local_falsifier') for r in rows): errors.append('incomplete paper-first premortem')
 if (p.get('summary') or {}).get('p0_authorized')!=4 or (p.get('summary') or {}).get('gpu_authorized')!=0: errors.append('expected four explicit-human P0 promotions and zero direct GPU authority')
 if any(r.get('p0_authorized') and r.get('verdict')!='ADVANCE_TO_PAPER_DESIGN' for r in rows): errors.append('only ADVANCE candidates may be explicitly promoted to P0')
 if (p.get('summary') or {}).get('advance_to_paper_design')!=4: errors.append('expected four advances in current premortem')
 return errors

def write_paper_first_idea_incubation(json_path=DEFAULT_JSON,js_path=DEFAULT_JS):
 p=build_paper_first_idea_incubation(); e=validate_paper_first_idea_incubation(p)
 if e: raise ValueError('Invalid paper-first incubation:\n- '+'\n- '.join(e))
 json_path.parent.mkdir(parents=True,exist_ok=True); json_path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 js_path.write_text('window.PAPER_FIRST_IDEA_INCUBATION = '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 return p

if __name__=='__main__': print(json.dumps(write_paper_first_idea_incubation(),ensure_ascii=False,indent=2))
