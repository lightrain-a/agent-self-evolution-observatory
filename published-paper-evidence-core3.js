window.PUBLISHED_PAPER_EVIDENCE = Object.assign(window.PUBLISHED_PAPER_EVIDENCE || {}, {
  "From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents": {
    simple:{zh:"只测 recall：问 Agent“用户以前说过什么”，答对旧事实就算记忆好；即使它继续使用已经被用户修改或删除的旧信息，也不会被额外惩罚。",en:"Recall-only evaluation rewards remembering past facts without separately penalizing use of facts that were later updated or deleted."},
    observed:{zh:"ACL 2026 Findings 的 Memora 覆盖 weeks→months 长对话，分 remembering、reasoning、recommending，并用 FAMA 同时奖励记住有效信息、惩罚使用失效记忆。4 个 LLM + 6 个 memory agent 的评测显示失效记忆被频繁复用，memory agent 的总体改善仍有限。",en:"ACL 2026 Findings evaluates weeks-to-months conversations with remembering, reasoning, recommending, and FAMA. Across four LLMs and six memory agents, invalid memories are frequently reused and overall memory-agent improvements remain limited."},
    proved:{zh:"说明长期记忆不能只用“能不能召回”评价，forgetting / update consistency 本身就是一等指标；很多现有 memory agent 在这一点上仍失败。",en:"It supports evaluating forgetting and update consistency as first-class properties rather than recall alone, revealing failures in current memory agents."},
    notProved:{zh:"它是 benchmark，不提供一个已经解决失效记忆问题的通用算法；也不能据此说某种 memory architecture 在所有用户流上最优。",en:"It is a benchmark, not a universal solution to invalid-memory handling, and does not identify one memory architecture as universally best."},
    source:{zh:"已核：ACL 2026 Findings / Memora 官方仓库",en:"Checked: ACL 2026 Findings / Memora repository"}
  },
  "A²Flow: Automating Agentic Workflow Generation via Self-Adaptive Abstraction Operators": {
    simple:{zh:"AFlow 类方法先由人定义一套 operator，例如 CoT、Review、Ensemble；搜索只负责决定这些固定积木怎么连。",en:"AFlow-style search starts from manually predefined operators such as CoT, Review, or Ensemble and only searches how to wire them."},
    observed:{zh:"AAAI 2026 正式摘要：A²Flow 在 general benchmark 平均 +2.4%，在 embodied benchmark 平均 +19.3%，同时资源使用降低 37%。消融显示去掉初始 operator 生成、深层抽象、聚类或 memory 都会退化。",en:"AAAI 2026 reports +2.4% average on general benchmarks, +19.3% on embodied benchmarks, and 37% lower resource use; ablations show each operator-extraction/memory stage contributes."},
    proved:{zh:"说明 operator 本身也可以从 case 中抽取、聚类和深层抽象，而不必永久由人预定义；这把自动化从“搜连接方式”推进到“积木本身也自动学”。",en:"It supports learning the operators themselves from cases through generation, clustering, and abstraction rather than permanently fixing the operator vocabulary."},
    notProved:{zh:"在 HumanEval / MBPP 等已有强 Python 工具先验的任务上提升较小；因此不能说自适应 operator 在所有 workflow 域都同样必要。",en:"Gains are smaller where strong predefined tool priors already exist, so adaptive operators are not equally necessary in every workflow domain."},
    source:{zh:"已核：AAAI 2026 正式页面 / 结果摘要",en:"Checked: AAAI 2026 proceedings / result summary"}
  },
  "FusionFlow: Enabling Deep Structural Exploration for Automated Agentic Workflow Generation": {
    simple:{zh:"单链局部改进：从一个 workflow 出发，每轮只改一个节点或一条边，或者沿一棵树向下扩；预算有限时很难跳到结构完全不同的深层组合。",en:"Single-lineage local refinement edits one node/edge at a time or expands one tree, making deep structural jumps hard under a limited budget."},
    observed:{zh:"ACL 2026 正式摘要报告：在 6 个 reasoning benchmark 上，FusionFlow 一致超过现有自动 workflow generation 方法；消融把主要增益归因于“融合多个独立演化 workflow”带来的结构跃迁。正式摘要没有给一个可安全概括的统一平均百分点，因此这里不伪造总提升。",en:"The ACL 2026 abstract reports consistent wins over prior automated workflow-generation methods on six reasoning benchmarks, with ablations attributing the key gain to fusing independently evolved workflows. It does not expose one safe aggregate margin in the abstract."},
    proved:{zh:"说明在有限搜索预算下，多条 lineage 的 workflow fusion 能突破单条局部搜索的深度限制。",en:"It supports multi-lineage workflow fusion as a way to reach deeper structures than single-lineage local refinement under bounded search."},
    notProved:{zh:"一致领先仍不等于任意任务都更好；而且 fusion 增加了候选依赖和验证复杂度，长期版本治理仍未解决。",en:"Consistent benchmark wins do not imply universal superiority, and fusion increases dependency/validation complexity that still needs lifecycle governance."},
    source:{zh:"已核：ACL 2026 Anthology 正式摘要",en:"Checked: ACL 2026 Anthology"}
  },
  "SkillGen: Learning Domain Skills for In-Context Sequential Decision Making": {
    simple:{zh:"把整条成功轨迹或若干 demonstration 直接放进 Prompt；每一步看到的都是大段历史，无法区分哪几个动作真正贡献了任务进展。",en:"Put whole successful trajectories or demonstrations into the prompt, without distinguishing which action segments actually drove progress."},
    observed:{zh:"AAAI 2026 对 ALFWorld、BabyAI、ScienceWorld 和多种开源/闭源 LLM 的实验中，SkillGen 的 progress rate 平均提升约 5.9%–16.5%。",en:"Across ALFWorld, BabyAI, ScienceWorld and multiple open/proprietary LLMs, SkillGen reports average progress-rate gains of about 5.9–16.5%."},
    proved:{zh:"说明用 temporal-difference credit assignment 找 high-utility action，再抽成 step-wise domain skill，比整轨迹 ICL 更能聚焦决策关键经验。",en:"It supports TD credit assignment to identify high-utility actions and retrieve step-wise domain skills as more focused than whole-trajectory ICL."},
    notProved:{zh:"它主要优化 in-context skill 提示，不等于技能已经成为带版本、验证和退役机制的长期可执行资产。",en:"It mainly optimizes in-context skill prompting, not a fully versioned, validated, retireable persistent skill asset."},
    source:{zh:"已核：AAAI 2026 / 正式对应摘要",en:"Checked: AAAI 2026 / matched publication abstract"}
  },
  "VisPlay: Self-Evolving Vision-Language Models": {
    simple:{zh:"RL 依赖人工标注问题/答案或任务专属可验证 reward；没有标签的新图像通常不能直接变成训练课程。",en:"Standard VLM RL relies on labeled QA pairs or task-specific verifiable rewards, so unlabeled images do not automatically become a curriculum."},
    observed:{zh:"CVPR 2026 正式摘要：同一个 base VLM 被分成 Questioner 与 Reasoner 两个角色，用 47K 无标签图像和 GRPO 共同训练；在 Qwen2.5-VL 与 MiMo-VL 两个模型族、8 个 benchmark（含 MM-Vet、MMMU）上都得到视觉推理、组合泛化和 hallucination 的一致改善。摘要没有给统一平均增益，因此这里不造单一数字。",en:"The CVPR 2026 abstract reports consistent gains in visual reasoning, compositional generalization, and hallucination reduction across two model families and eight benchmarks using 47K unlabeled images and joint Questioner/Reasoner GRPO; no single aggregate margin is exposed in the abstract."},
    proved:{zh:"说明“让模型自己出题 + 自己解题 + 难度/多样性 reward”可以把无标签图像转成不断变化的自训练课程。",en:"It supports self-generated visual questions plus solver feedback and difficulty/diversity rewards as a scalable curriculum from unlabeled images."},
    notProved:{zh:"自生成 silver answer 仍可能把共同错误放大；8 个 benchmark 的一致改善也不等于长期训练不会 reward hacking 或遗忘旧能力。",en:"Silver-answer self-training can still amplify shared errors; benchmark gains do not establish long-run immunity to reward hacking or forgetting."},
    source:{zh:"已核：CVPR 2026 Open Access / 官方代码",en:"Checked: CVPR 2026 Open Access / official code"}
  }
});
