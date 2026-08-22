window.PUBLISHED_PAPER_EVIDENCE = Object.assign(window.PUBLISHED_PAPER_EVIDENCE || {}, {
  "Reflexion: Language Agents with Verbal Reinforcement Learning": {
    simple:{zh:"普通重试 / ReAct：失败后重新跑，最多保留当前上下文里的思考和环境反馈；下一次尝试没有一条持久的“我上次为什么失败”经验。",en:"Plain retry / ReAct reruns after failure and may use only the current trace; the next attempt has no persistent lesson about why the previous one failed."},
    observed:{zh:"NeurIPS 2023 正式摘要给出的代表性数字是 HumanEval pass@1 = 91%，高于当时 GPT-4 的 80%；论文还在 ALFWorld、HotPotQA 等序列决策与推理任务上比较普通重试、ReAct 和不同反馈来源。",en:"The NeurIPS 2023 abstract reports 91% pass@1 on HumanEval versus 80% for GPT-4 at the time, alongside sequential-decision and reasoning evaluations such as ALFWorld and HotPotQA."},
    proved:{zh:"说明“把反馈压缩成语言反思并写入 episodic memory”可以在不改 Actor 权重时显著改善后续尝试，而且这条机制跨代码、推理和交互任务可复现。",en:"It supports that verbal reflection stored in episodic memory can improve later attempts without changing actor weights across coding, reasoning, and interactive tasks."},
    notProved:{zh:"它主要证明同一任务的多次尝试会改善；没有证明这条反思跨任务长期保留后仍总是有益，也没有系统测旧记忆污染、过期和回滚。",en:"It mainly establishes improvement across repeated attempts; it does not establish durable cross-task benefit, stale-memory safety, or rollback."},
    source:{zh:"已核：NeurIPS 2023 正式页面 / 官方代码",en:"Checked: NeurIPS 2023 proceedings / official code"}
  },
  "Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization": {
    simple:{zh:"Reflexion 式启发式反思：Actor 失败后直接让通用 LLM 写一段反思，再把反思塞回下一次 Prompt；反思器本身不根据环境 reward 学“什么样的反思真的有用”。",en:"Heuristic Reflexion asks a general LLM to write a reflection after failure and reuses it next time; the reflector itself is not trained from environment reward."},
    observed:{zh:"ICLR 2024 结果中，GPT-4 Actor 在 HotPotQA、4 次 retry 时 Retroformer 为 54%，Reflexion 52%、ReAct 40%；ALFWorld 可到 100%，Reflexion 85.07%、ReAct 77.61%；WebShop 为 46%、44%、42%。",en:"ICLR 2024 reports, with a GPT-4 actor, 54% on HotPotQA at four retries versus 52% Reflexion and 40% ReAct; 100% on ALFWorld versus 85.07% and 77.61%; and 46% on WebShop versus 44% and 42%."},
    proved:{zh:"说明反思内容本身可以作为可学习策略：用环境 reward + policy gradient 训练 retrospective model，能比固定启发式反思更稳定地产生行动性反馈。",en:"It supports treating reflection generation as a learnable policy: environment reward plus policy-gradient training can outperform fixed heuristic reflection."},
    notProved:{zh:"WebShop 的增益只有几个百分点，不能把所有环境都概括成“大幅提升”；也没有证明反思器持续在线更新很多轮后不会漂移。",en:"WebShop gains are only a few points, so the effect is not uniformly large; long-run online drift of the retrospective model is not established."},
    source:{zh:"已核：ICLR 2024 正式结果 / 官方代码",en:"Checked: ICLR 2024 results / official code"}
  },
  "Voyager: An Open-Ended Embodied Agent with Large Language Models": {
    simple:{zh:"固定技能 / 纯 ReAct：每个 Minecraft 任务都从头规划和试错；成功轨迹不会被编译成可执行代码技能，下一次遇到相似子问题还要重新想。",en:"With fixed skills or plain ReAct, each Minecraft task is replanned from scratch; successful trajectories are not compiled into reusable executable code."},
    observed:{zh:"TMLR 正式摘要报告：相比先前 SOTA，Voyager 获得约 3.1× 更多 unique items、科技树关键里程碑最高快 15.3×、探索距离约 2.3×；技能库还能迁移到新的 Minecraft 世界解决未见任务。",en:"The TMLR abstract reports roughly 3.1× more unique items, up to 15.3× faster tech-tree milestones, and about 2.3× longer travel than prior SOTA, with skill-library transfer to a new Minecraft world."},
    proved:{zh:"说明“自动课程 + 环境反馈迭代 + 可执行技能库”能让开放世界中的能力积累出现复用和复利，而且不需要参数微调。",en:"It supports compounding capability through an automatic curriculum, environment-feedback iteration, and an executable skill library without parameter fine-tuning."},
    notProved:{zh:"它发生在 Minecraft 且依赖 GPT-4 黑盒调用；不能直接推出技能库在真实机器人、网页或长期版本冲突下仍同样安全有效。",en:"The evidence is Minecraft-specific and uses GPT-4 black-box calls; it does not establish equivalent safety or transfer in robots, web agents, or long version histories."},
    source:{zh:"已核：TMLR 2024 正式摘要 / 项目页",en:"Checked: TMLR 2024 abstract / project page"}
  },
  "CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update": {
    simple:{zh:"冻结工具库：LLM 只负责编排现有视觉工具；工具认不出新概念时，系统最多重新规划，但 LOC、SEG、VQA 等工具本身不更新。",en:"A frozen tool library lets the LLM only compose existing visual tools; when a tool lacks new knowledge, replanning cannot update LOC, SEG, or VQA themselves."},
    observed:{zh:"CVPR 2024 论文报告，相比既有 tool-usage 方法，CLOVA 在视觉问答和多图推理约 +5%，knowledge tagging 约 +10%，image editing 约 +20%。",en:"The CVPR 2024 paper reports about +5% on visual QA and multi-image reasoning, +10% on knowledge tagging, and +20% on image editing over existing tool-usage methods."},
    proved:{zh:"说明把 human feedback 先做 global-local 诊断，再只更新被定位的视觉工具，可以让工具型视觉 Agent 获得任务后持续学习能力。",en:"It supports diagnosing feedback globally/locally and updating the implicated visual tools as a viable closed-loop continual-learning mechanism."},
    notProved:{zh:"这些任务仍是受控视觉能力更新；没有证明自动更新任意外部 API 的权限安全，也没有覆盖多版本依赖和精确回滚。",en:"The evidence concerns controlled visual-tool updates, not permission-safe arbitrary API evolution, dependency lineage, or exact rollback."},
    source:{zh:"已核：CVPR 2024 正式论文 / 官方代码",en:"Checked: CVPR 2024 publication / official code"}
  },
  "Automated Design of Agentic Systems": {
    simple:{zh:"人工 Agent 设计：研究者预先决定 CoT、Self-Refine、Debate 等模块怎样组合，再逐个手工比较；搜索空间基本受人的模板限制。",en:"Manual agent design fixes how CoT, Self-Refine, Debate, and other modules are combined, then compares hand-authored designs."},
    observed:{zh:"ICLR 2025 的 Meta Agent Search 在多域都超过手工 Agent：DROP F1 相对最强手工基线提高 13.6 分，MGSM accuracy 提高 14.4 个百分点；从 MGSM 迁移到 GSM8K / GSM-Hard 时分别提高 25.9 / 13.2 个百分点。",en:"ICLR 2025 reports +13.6 F1 points on DROP and +14.4 accuracy points on MGSM over strong hand-designed baselines; transfer from MGSM to GSM8K / GSM-Hard improves by 25.9 / 13.2 points."},
    proved:{zh:"说明把 Agent 直接表示成代码，并让 meta-agent 基于历史 archive 继续编程新 Agent，可以发现人没有手写出来、且能跨域/跨模型迁移的结构。",en:"It supports code-level agent search with an archive-driven meta-agent discovering structures that outperform hand designs and transfer across domains/models."},
    notProved:{zh:"搜索仍依赖有限 benchmark 与高成本执行，且论文自己提醒模型生成代码存在安全风险；不能推出“自动搜索到的 Agent 可以直接部署”。",en:"Search remains benchmark- and execution-budget dependent, and model-generated code introduces safety risks; discovered agents are not automatically deployment-safe."},
    source:{zh:"已核：ICLR 2025 正式页面 / ADAS 项目页",en:"Checked: ICLR 2025 proceedings / ADAS project"}
  },
  "AFlow: Automating Agentic Workflow Generation": {
    simple:{zh:"人工固定 workflow，或只优化 Prompt：节点类型和控制流基本由人预先决定，优化器最多在现有模板附近做局部改动。",en:"Manual workflows or prompt-only optimization keep node types and control flow largely fixed and explore only local variants."},
    observed:{zh:"ICLR 2025 正式摘要：6 个 benchmark 上平均比当时 SOTA 自动工作流方法高 5.7%；在部分任务上，小模型工作流能超过 GPT-4o，同时只用其约 4.55% 的美元推理成本。",en:"The ICLR 2025 abstract reports a 5.7% average gain over SOTA automated-workflow baselines across six benchmarks; on some tasks a smaller model beats GPT-4o at about 4.55% of its dollar inference cost."},
    proved:{zh:"说明 code-represented workflow + MCTS + 执行反馈可以有效搜索 Agent 图，而不只是手调 Prompt。",en:"It supports execution-guided MCTS over code-represented workflows as a useful search axis beyond prompt tuning."},
    notProved:{zh:"平均提升不代表每个任务都同样明显；搜索过程仍有验证集过拟合、成本和结构安全问题。",en:"Average improvement is not uniform across tasks; validation overfitting, search cost, and structural safety remain open."},
    source:{zh:"已核：ICLR 2025 正式页面 / 官方代码",en:"Checked: ICLR 2025 proceedings / official code"}
  }
});
