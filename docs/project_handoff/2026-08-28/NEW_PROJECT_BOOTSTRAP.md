# 新 ChatGPT Project 启动协议

这份文件用于把当前大型科研项目迁移到一个新的 ChatGPT Project / 新窗口。它不是聊天摘要，而是启动 Agent 恢复 canonical 状态的协议。

## 推荐入口

Canonical handoff tag：

`project-handoff-20260828-v2`

验证过的 69 服务器仓库：

`wyt@222.20.126.69:/home/wyt/code/agent-self-evolution-observatory`

Handoff 目录：

`docs/project_handoff/2026-08-28/`

注意：handoff tag 只是跨项目知识基线。实时研究状态必须重新从最新 `origin/main` 和对应研究对象的 exact artifacts 恢复。

## 建议新 Project 固定加载的最小文件

- `START_HERE.md`
- `PROJECT_INSTRUCTIONS.md`
- `CURRENT_STATE_RECOVERY.md`
- `GLOBAL_RESEARCH_INDEX.md`
- `SCIENTIFIC_OPERATING_SYSTEM.md`
- `FAILURE_AND_REPAIR_PLAYBOOK.md`
- `INFRA_AND_EXECUTION.md`
- `WRITING_AND_REVIEW.md`
- `MIGRATION_CHECKLIST.md`

具体论文开始工作后，再用 `PAPER_WORKING_SET_TEMPLATE.md` 建立小型 working set，不要把整个项目历史一直塞进单篇论文上下文。

## 可以直接复制到新窗口的完整启动提示词

```text
你现在接手的是“蒸馏”科研项目的后续工作。这个旧项目已经非常大，所以不要主要依赖 ChatGPT 旧聊天记忆、摘要或模型记忆来恢复状态；请以版本化 canonical handoff + 当前 Git/artifact 为准。

【一、先恢复 handoff】
优先使用 MCP-Yu 连接：
wyt@222.20.126.69:/home/wyt/code/agent-self-evolution-observatory

先 fetch/检查 Git，但不要修改共享 dirty checkout。
跨项目迁移知识基线使用 annotated tag：
project-handoff-20260828-v2

handoff 路径：
docs/project_handoff/2026-08-28/

请先按顺序阅读：
1. START_HERE.md
2. PROJECT_INSTRUCTIONS.md
3. CURRENT_STATE_RECOVERY.md
4. GLOBAL_RESEARCH_INDEX.md
5. RESEARCH_PORTFOLIO.md
6. SCIENTIFIC_OPERATING_SYSTEM.md
7. FAILURE_AND_REPAIR_PLAYBOOK.md
8. INFRA_AND_EXECUTION.md
9. WRITING_AND_REVIEW.md
10. WORKING_STYLE_AND_DECISION_RULES.md
11. MIGRATION_CHECKLIST.md
12. handoff_manifest.json

不要因为 tag 的 base revision 是某个历史 SHA，就把它当成当前最新状态。handoff 是知识和规则的基线；实际工作前必须重新 fetch origin，并从当前 origin/main、exact research object、最新 dated/content-addressed artifacts 恢复实时状态。

【二、状态恢复的信任顺序】
来源冲突时按以下优先级：
1. 当前 exact Git revision + content-addressed primary evidence；
2. 检查过 generated_at/source revision、并确认没有更新 dated artifacts 的 machine-readable canonical state；
3. versioned manifests / claim ledgers / adjudications；
4. handoff package；
5. Obsidian/人工摘要；
6. ChatGPT 旧聊天和模型记忆。

任何名为 current、latest、PASS、ready 的文件都不能只凭文件名相信，必须检查时间、source revision、hash/object identity、上游证据和 authority。

【三、先确定我当前要求你做的 paper/track】
使用 GLOBAL_RESEARCH_INDEX.md 路由，不要把所有研究线混在一起。
一旦确定具体 paper/track，只加载该论文当前真正需要的 working set，并用 PAPER_WORKING_SET_TEMPLATE.md 的结构维护：
- scientific question；
- active claims；
- latest admissible evidence；
- revoked/off-mainline evidence；
- unresolved objections；
- current gate；
- planned experiment；
- paper/code/run locations；
- next smallest falsifiable action。

特别注意：历史上跑偏、被撤销或已经退出当前主线的实验结果可以保留作为历史证据，但必须标记为 revoked from current narrative authority，不能因为它们仍在仓库里就在后续写作时重新影响论文主线。

【四、科研主线必须保持】
我们希望形成的不是“发现一个现象 + 加几个工程技巧 + 多报几个指标”，而是尽量形成：
scientific object → mechanism model → falsifiable prediction / regime boundary → controlled intervention → scientific/engineering decision。

每个新实验必须回答一个明确的科学不确定性，并在运行前写明：
- 为什么要跑；
- primary hypothesis；
- success 时意味着什么；
- failure 时意味着什么；
- 什么结果会使 claim 收窄、HOLD 或被否证。

不能用更多模型、更多数据集、更多指标代替真正的 scientific insight。

【五、实验纪律】
执行遵循 smoke → pilot → full：
- smoke 只证明 pipeline 能跑，不证明科学结论；
- pilot 要先证明问题可辨识、效应值得完整实验检验；
- pilot 不成立时先做 failure differential diagnosis，不直接靠堆算力救结果；
- full experiment 只有在科学门禁和执行 authority 都明确时才启动。

失败时优先区分：
formulation / substrate / representation / optimization / baseline / execution / principle failure。
修复尽量做 single-variable、可证伪的改变。禁止一个结果不好后同时改 prompt、reward、threshold、dataset、model、evaluator，再把新结果解释成单一机制的因果证据。

如果论文面向广泛受众/顶会，优先使用公开、主流、可复现的 benchmark/substrate 和强 baseline；同时保留 simple baseline/control，不能只和方便赢的方法比较。

where attenuation occurs 不自动等于 why attenuation occurs；operational localization 不能直接写成 mechanism causation。若 treatment 同时改变多个因素，claim 必须相应收窄，除非额外实验把变量解耦。

【六、实验运行必须边跑边保存】
长实验开始前必须固化 manifest/config，并在运行过程中持续保存：
- Git/code revision；
- dataset/revision/split；
- model/revision；
- prompt/template；
- evaluator/revision；
- seeds；
- environment；
- per-case outputs；
- trajectories/logs；
- intermediate summaries；
- failure cases；
- resume/replay information；
- provenance/hash where applicable。

不能只在实验最后保存一个 aggregate score，否则中途失败后会失去科研证据。

实验完成后必须做分析，不允许“拿到结果看完就走”。分析至少包括：效应大小、方差/CI、失败模式、异质性、baseline 是否吸收增益、是否符合预先 mechanism prediction、claim 应该加强/收窄/HOLD/否证，以及这轮经验应写回系统的哪条规则。

【七、证据和权限严格分开】
始终区分：
artifact exists ≠ artifact valid ≠ supports claim ≠ adjudicated ≠ experiment authorized ≠ GPU/provider authorized ≠ paper ready ≠ submission authorized。

receipt PASS、QA PASS、review score、metadata、某个文件已经生成，都不能自动授予下一层权限。
没有明确 authority 时，不要自行开放 GPU/API/full experiment/submission。

【八、Git/服务器操作规则】
- 先 fetch origin 并报告 exact revision；
- 不写共享 dirty checkout；
- 修改使用 isolated worktree/branch；
- 不覆盖其他并发 agent/user 的变更；
- 修改后检查 diff，运行 targeted validation；
- 小粒度 commit；
- 没有实际发生过的 commit/push/merge/run/upload/submission/review，绝不能声称已经完成；
- 不把 password、API key、cookie、SSH private key 等凭证写入聊天、handoff、论文或仓库文档。

【九、论文写作规则】
先维护 claim ↔ evidence ledger，再写强结论。
相关工作比较表不仅列模块，要显示 scientific residual：已有方法解释了什么、没有解释什么、我们的新增 insight/identification 是什么。
实验表不能只显示自己的变体；同一科学问题若结果可以映射到统一 evaluation，应尽量把公开 strong baselines 放到同一比较框架。
论文故事线优先让不了解该方向的人快速理解：问题为什么重要 → 现有方法为什么不够 → 新科学对象/机制是什么 → 什么预测可以证伪 → 实验如何验证 → 得到什么边界/决策。

【十、首次恢复后不要立即盲目继续实验】
完成上述读取和 live-state recovery 后，先向我汇报以下 7 项：
1. 你认为我当前指的是哪篇 paper/track；
2. 当前恢复到的 exact canonical revision；
3. 该 track 最新、可采信的 evidence/state artifacts；
4. 当前 scientific gate/disposition；
5. 最强的 unresolved scientific objection；
6. 下一步最小、可证伪的动作；
7. 当前是否存在明确 execution authority。

如果我的新窗口第一句话没有指定具体 paper，就先给我一个非常精简的 GLOBAL_RESEARCH_INDEX 路由视图，列出仍活跃的主要 paper/track、各自当前 gate 和下一步，不要一次性展开所有历史细节，等我选择后再进入对应 working set。

完成恢复后继续主动推进，不要因为任务复杂就停在口头方案；但也不要为了“继续做”而越过科学门禁、权限边界或论文主线。
```

## 新项目长期保存什么

ChatGPT Memory/Project Instructions 只保存少量长期稳定规则：

- canonical handoff 优先于旧聊天；
- 科学证据和执行权限分离；
- 不写 dirty shared checkout；
- 先 pilot 后 full；
- 跑偏证据要显式撤销 narrative authority；
- 具体论文状态从 Git/artifact 恢复。

不要把实时 PID、当前 run 状态、某篇论文今天的临时 gate、服务器密码/API key 等塞进长期模型记忆。

## 推荐项目目录习惯

```text
handoff/                 # 全局稳定规则与迁移协议
papers/<paper_id>/       # 单篇论文 working set
experiments/<exp_id>/    # 原子实验 contract / manifest / artifacts
reviews/                 # adversarial review / claim audit
archive/                 # superseded / revoked / off-mainline snapshots
```

目标不是生成一个无限膨胀的 context 文件，而是让下一次 Agent 能快速恢复“正确且最小的当前上下文”。
