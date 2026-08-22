window.PUBLISHED_PAPER_EVIDENCE = Object.assign(window.PUBLISHED_PAPER_EVIDENCE || {}, {
  "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning": {
    simple:{zh:"固定训练任务池 + 稀疏终局 reward：一直从同一批网页任务采样，不管当前 Agent 已经会了还是仍完全不会。",en:"A fixed web-task pool with sparse terminal reward samples from the same distribution regardless of the agent's current competence."},
    observed:{zh:"ICLR 2025：WebArena-Lite 上 Llama-3.1-8B 从 4.8% 提到 42.4%，GLM-4-9B 从 6.1% 提到 43.0%；同时超过 GPT-4-Turbo 17.6%、GPT-4o 13.9% 和 AutoWebGLM 18.2%。",en:"ICLR 2025 reports WebArena-Lite success rising from 4.8% to 42.4% for Llama-3.1-8B and 6.1% to 43.0% for GLM-4-9B, above GPT-4-Turbo 17.6%, GPT-4o 13.9%, and AutoWebGLM 18.2%."},
    proved:{zh:"说明把失败尝试转成新任务、配合 robust outcome reward model 与自适应 RL，可以让开放小模型的网页能力随着当前失败边界一起进化。",en:"It supports generating curriculum tasks from failures, combined with outcome reward modeling and adaptive RL, as an effective way to evolve open web agents."},
    notProved:{zh:"这是训练阶段的在线课程闭环，不等于部署后任何网页变化都能安全持续更新；对旧任务回退和长期 reward drift 的保障仍有限。",en:"This is an online training curriculum, not a guarantee of safe continual post-deployment adaptation or zero regression under reward drift."},
    source:{zh:"已核：ICLR 2025 正式版 / 论文摘要",en:"Checked: ICLR 2025 publication / paper abstract"}
  },
  "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning": {
    simple:{zh:"整条答案只给一个“对/错”分数，或者让模型笼统说“再检查一下”；不判断 CoT 的哪一步错、是视觉感知错还是推理错。",en:"Give the whole answer one scalar correct/incorrect score or a generic self-critique without locating which CoT step or visual fact is wrong."},
    observed:{zh:"CVPR 2025 的 VISCO 含 1,645 个样例、5,604 条 step annotation，评测 24 个 LVLM。顶级模型在有人类 critique 时能纠正超过 70% 的错误，但自生成 critique 明显更弱，甚至出现负增益；LookBack 最多把 critique/correction 提高 13.5%。",en:"VISCO contains 1,645 examples and 5,604 step annotations across 24 LVLMs. Top models correct over 70% of errors with human critique, while self-generated critique can hurt; LookBack improves critique/correction by up to 13.5%."},
    proved:{zh:"它把“能不能自我改进”拆成更细的瓶颈：真正限制 correction 的往往是 critique 质量，尤其视觉感知错误、拒绝判错和错误传播判断。",en:"It isolates critique quality as a key bottleneck to self-correction, especially visual-perception errors, reluctance to reject, and exaggerated error propagation."},
    notProved:{zh:"VISCO 是评测/修正协议，不是跨任务持久更新系统；更好的单次 critique 不代表长期记忆或模型版本一定更安全。",en:"VISCO is an evaluation/correction protocol, not a persistent cross-task update mechanism; better critique does not imply safer long-term memory or model versions."},
    source:{zh:"已核：CVPR 2025 正式页面 / VISCO 官方项目",en:"Checked: CVPR 2025 proceedings / VISCO project"}
  },
  "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning": {
    simple:{zh:"同一个 VLM 既答题又自我检查，或者只用一个 scalar reward；Reasoner 和 Critic 没有能力分工，批评也没有专门训练。",en:"Use the same VLM for both reasoning and self-checking, or only a scalar reward; no independently trained critic specializes in constructive feedback."},
    observed:{zh:"CVPR 2025 摘要报告 Critic-V 在 8 个多模态 benchmark 中有 5 个超过既有方法（包括 GPT-4V）。更细的结果也显示收益并非全正：例如 Qwen2-VL-7B 在 RealWorldQA 可从 70.1 提到 74.9，但 MMStar 从 60.7 降到 56.2。",en:"The CVPR 2025 abstract reports wins on 5 of 8 multimodal benchmarks. Detailed results show non-uniform effects: Qwen2-VL-7B rises 70.1→74.9 on RealWorldQA but drops 60.7→56.2 on MMStar."},
    proved:{zh:"说明独立、偏好优化过的 Critic 能给 Reasoner 更细的语言反馈，并在多数 benchmark 改善推理；同时也直接说明 Critic 不是“加上就一定更好”。",en:"It supports a separately preference-optimized critic as useful on many benchmarks while directly showing that critic feedback is not uniformly beneficial."},
    notProved:{zh:"5/8 胜出不等于跨任务无回退；尤其存在负增益 benchmark，因此持续使用 Critic 前仍需要回归门。",en:"Winning 5/8 does not imply regression-free transfer; negative benchmark deltas motivate explicit regression gates."},
    source:{zh:"已核：CVPR 2025 正式摘要 / 结果表",en:"Checked: CVPR 2025 abstract / results table"}
  },
  "Visual Agentic AI for Spatial Reasoning with a Dynamic API": {
    simple:{zh:"ViperGPT / VisProg 式静态 API：人提前定义 detect、crop、VQA 等函数；新问题只能组合已有函数，遇到新的空间子问题无法临时发明接口。",en:"Static APIs such as ViperGPT/VisProg predefine detect/crop/VQA functions; new spatial subproblems must be expressed using the fixed set."},
    observed:{zh:"CVPR 2025：VADAR 在 CLEVR 为 53.6%，ViperGPT 26.2%、VisProg 31.2%；Omni3D-Bench 为 40.4%，ViperGPT 26.7%、VisProg 13.5%，但仍略低于 GPT-4o 42.9%。把视觉模块换成 oracle 后，VADAR 达 83.0% / 94.4%。",en:"CVPR 2025 reports 53.6% on CLEVR versus 26.2% ViperGPT and 31.2% VisProg; 40.4% on Omni3D-Bench versus 26.7% and 13.5%, while slightly below GPT-4o at 42.9%. With oracle visual modules VADAR reaches 83.0% / 94.4%."},
    proved:{zh:"说明动态生成 Python API 能扩大可表达的空间推理程序；oracle 实验还把主要瓶颈定位到视觉 specialist，而不是程序结构本身。",en:"It supports dynamically generated Python APIs as expanding the space of expressible spatial programs, with oracle tests locating much of the remaining bottleneck in visual specialists."},
    notProved:{zh:"优势集中在 3D 空间推理；GQA 这类偏外观的一步问题上 VADAR 46.1% 低于 GPT-4o 54.9%，不能泛化成“动态 API 对所有视觉任务都更强”。",en:"The advantage is concentrated in 3D spatial reasoning; on appearance-heavy GQA VADAR (46.1%) trails GPT-4o (54.9%)."},
    source:{zh:"已核：CVPR 2025 正式页面 / VADAR 项目与结果",en:"Checked: CVPR 2025 proceedings / VADAR project and results"}
  },
  "Self-Evolving Visual Concept Library using Vision-Language Critics": {
    simple:{zh:"固定 concept library，或者为了变强就让 LLM 一次性多生成一些概念；没有利用分类器当前最容易混淆的类别来定向补概念。",en:"Keep a fixed concept library, or simply ask an LLM for more concepts once, without targeting the classifier's current confusion pairs."},
    observed:{zh:"CVPR 2025 的 ESCHER 在 fine-tuned LM4CV 上 7 个数据集全部提升：例如 CUB-200 从 63.26→83.17，Stanford Cars 86.84→93.76，CIFAR-100 84.48→89.63；“只增加同数量概念”明显达不到这一提升。少样本 8-shot 则有混合结果。",en:"ESCHER improves all seven fine-tuned LM4CV datasets, e.g. CUB-200 63.26→83.17, Stanford Cars 86.84→93.76, CIFAR-100 84.48→89.63; merely adding the same number of concepts is weaker. Eight-shot few-shot results are mixed."},
    proved:{zh:"说明 VLM critic 反馈能把概念扩展从随机“多写一些描述”变成针对混淆对的 library learning；消融也支持 critic/history 的作用。",en:"It supports VLM-critic feedback turning concept expansion into targeted library learning rather than random descriptor growth, with ablations supporting critic/history contributions."},
    notProved:{zh:"few-shot 低样本并非全面获益，因此不能把“概念库会自进化”解释成所有数据规模和下游任务都单调提升。",en:"Few-shot results are not uniformly positive, so concept evolution is not a monotonic improvement guarantee across data regimes."},
    source:{zh:"已核：CVPR 2025 正式页面 / 结果表",en:"Checked: CVPR 2025 proceedings / source-rendered results"}
  },
  "Multi-agent Architecture Search via Agentic Supernet": {
    simple:{zh:"固定一个多 Agent 拓扑给所有问题：无论问题简单还是复杂，都调用同样数量的 Agent、相同通信边和相同工具。",en:"Use one fixed multi-agent topology for every query, with the same agents, edges, and tool calls regardless of difficulty."},
    observed:{zh:"ICML 2025：MaAS 在 6 个 benchmark 上只需既有手工/自动多 Agent 系统约 6%–45% 的推理成本，同时性能高 0.54%–11.82%，并展示跨数据集和跨 LLM backbone 迁移。",en:"ICML 2025 reports 6–45% of the inference cost of handcrafted/automated multi-agent systems while improving performance by 0.54–11.82% across six benchmarks, with cross-dataset and cross-backbone transfer."},
    proved:{zh:"说明“搜索一个静态最优团队”不是唯一做法；可以学习 agentic supernet，再按 query 动态采样不同复杂度团队，实现性能—成本联合适配。",en:"It supports learning an agentic supernet and sampling query-dependent architectures rather than deploying one static optimal team."},
    notProved:{zh:"它优化的是查询级资源分配和架构，不等于多个长期 Agent 之间的记忆传播、污染控制和治理已经解决。",en:"It optimizes query-level architecture/resource allocation, not long-lived cross-agent memory propagation, contamination, or governance."},
    source:{zh:"已核：ICML 2025 PMLR / 官方会议信息",en:"Checked: ICML 2025 PMLR / official conference page"}
  }
});
