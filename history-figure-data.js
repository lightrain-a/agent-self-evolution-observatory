window.AGENT_HISTORY_FIGURE = {
  stages: [
    {
      code:"P0", period:"2017–2020", color:"#2f6b3c",
      title:{en:"Foundation-model precursors",zh:"基础模型前置阶段"},
      subtitle:{en:"Reusable representations and in-context adaptation",zh:"可复用表示与上下文适应"},
      bullets:{en:["Transformer and large-scale pretraining","Task transfer through fine-tuning","Few-shot adaptation through context","No persistent agent state yet"],zh:["Transformer 与大规模预训练","通过微调迁移到下游任务","通过上下文实现少样本适应","尚无持久 Agent 状态"]},
      target:{en:"Parameters → context",zh:"参数 → 上下文"},
      feedback:{en:"Static corpora and demonstrations",zh:"静态语料与示范"},
      limitation:{en:"Capability without autonomous experience loops",zh:"具备能力，但没有自主经验闭环"}
    },
    {
      code:"P1", period:"2021–2022", color:"#2460ad",
      title:{en:"Reasoning and self-bootstrapping",zh:"推理与自举改进"},
      subtitle:{en:"Models begin generating intermediate supervision",zh:"模型开始生成中间监督"},
      bullets:{en:["Chain-of-thought and self-consistency","Self-generated rationales and data","Instruction following and alignment","Mostly offline or single-task improvement"],zh:["思维链与一致性推理","自生成推理轨迹与数据","指令遵循与对齐","主要仍是离线或单任务改进"]},
      target:{en:"Prompt, trace, parameters",zh:"提示词、轨迹、参数"},
      feedback:{en:"Answers, rationales, human preference",zh:"答案、推理轨迹与人类偏好"},
      limitation:{en:"Weak persistence across tasks and environments",zh:"跨任务与环境的持久性较弱"}
    },
    {
      code:"P2", period:"2023", color:"#6540a4",
      title:{en:"Interactive experience loops",zh:"交互式经验闭环"},
      subtitle:{en:"Reason, act, observe, reflect, and reuse",zh:"推理、行动、观察、反思与复用"},
      bullets:{en:["Reasoning–action interaction","Verbal reinforcement and episodic memory","Self-supervised tool learning","Early reusable agent experience"],zh:["推理—行动交互","语言强化与情景记忆","自监督工具学习","早期可复用 Agent 经验"]},
      target:{en:"Trace, memory, tool",zh:"轨迹、记忆、工具"},
      feedback:{en:"Environment results and execution errors",zh:"环境结果与执行错误"},
      limitation:{en:"Hand-built scaffolds and fragile memories",zh:"Scaffold 依赖人工，记忆仍脆弱"}
    },
    {
      code:"P3", period:"2024", color:"#8b5b15",
      title:{en:"Persistent and system-level optimization",zh:"持久更新与系统级优化"},
      subtitle:{en:"Optimize prompts, memories, skills, and agent graphs",zh:"优化提示词、记忆、技能与 Agent 图"},
      bullets:{en:["LLMs used as optimizers","Learned retrospective feedback","Open-ended skill libraries","Visual tools and closed-loop updates"],zh:["将 LLM 作为优化器","学习型回顾反馈","开放式技能库","视觉工具与闭环更新"]},
      target:{en:"Memory, skill, workflow",zh:"记忆、技能、工作流"},
      feedback:{en:"Evaluated histories and iterative trials",zh:"已评估历史与迭代试验"},
      limitation:{en:"Selection bias, pollution, and search cost",zh:"选择偏差、污染与搜索成本"}
    },
    {
      code:"P4", period:"2025", color:"#087582",
      title:{en:"Environment-driven evolution",zh:"环境驱动进化"},
      subtitle:{en:"Curriculum, GUI/Web, workflow search, and visual critics",zh:"课程、GUI/Web、工作流搜索与视觉 Critic"},
      bullets:{en:["Online curriculum reinforcement learning","Automatic agent and workflow design","GUI/Web learning from interaction","Fine-grained visual critique and correction"],zh:["在线课程强化学习","自动 Agent 与工作流设计","GUI/Web 交互学习","细粒度视觉批评与纠错"]},
      target:{en:"Policy, workflow, visual reasoning",zh:"策略、工作流、视觉推理"},
      feedback:{en:"Tests, websites, tools, and visual evidence",zh:"测试、网站、工具与视觉证据"},
      limitation:{en:"Long-term reliability remains under-measured",zh:"长期可靠性仍缺乏充分测量"}
    },
    {
      code:"P5", period:"2026", color:"#c15612",
      title:{en:"Multimodal self-evolution and governance",zh:"多模态自进化与治理"},
      subtitle:{en:"Visual self-play, multimodal memory, skill ecosystems, and safety",zh:"视觉自博弈、多模态记忆、技能生态与安全"},
      bullets:{en:["VLM self-play and active exploration","Multimodal memory and dynamic graphs","Long-video tool-trajectory evolution","Formal verification, provenance, and governance"],zh:["VLM 自博弈与主动探索","多模态记忆与动态图结构","长视频工具轨迹进化","形式化验证、溯源与治理"]},
      target:{en:"Whole multimodal agent system",zh:"完整多模态 Agent 系统"},
      feedback:{en:"Multimodal worlds, evaluators, and release gates",zh:"多模态世界、评价器与发布门控"},
      limitation:{en:"Open-ended evolution is not yet safely demonstrated",zh:"尚未安全证明真正开放式进化"}
    }
  ],
  capabilities: [
    {name:{en:"Current-task correction",zh:"当前任务纠错"},values:[{l:1,t:{en:"Prompt/fine-tune",zh:"提示或微调"}},{l:3,t:{en:"Reasoning traces",zh:"推理轨迹"}},{l:4,t:{en:"Reflect and retry",zh:"反思并重试"}},{l:4,t:{en:"Optimizer loops",zh:"优化器闭环"}},{l:5,t:{en:"Environment feedback",zh:"环境反馈"}},{l:5,t:{en:"Multimodal correction",zh:"多模态纠错"}}]},
    {name:{en:"Persistent experience",zh:"持久经验"},values:[{l:0,t:{en:"None",zh:"无"}},{l:1,t:{en:"Offline data",zh:"离线数据"}},{l:3,t:{en:"Episodic memory",zh:"情景记忆"}},{l:4,t:{en:"Repair/consolidate",zh:"修复与巩固"}},{l:4,t:{en:"Task streams",zh:"任务流"}},{l:5,t:{en:"Multimodal memory",zh:"多模态记忆"}}]},
    {name:{en:"Reusable skills and tools",zh:"可复用技能与工具"},values:[{l:0,t:{en:"Hand-built",zh:"人工构建"}},{l:1,t:{en:"Prompted tools",zh:"提示式工具"}},{l:3,t:{en:"Tool learning",zh:"工具学习"}},{l:4,t:{en:"Growing skill library",zh:"增长型技能库"}},{l:4,t:{en:"Dynamic APIs",zh:"动态 API"}},{l:5,t:{en:"Skill ecosystems",zh:"技能生态"}}]},
    {name:{en:"Workflow and self-design",zh:"工作流与自设计"},values:[{l:0,t:{en:"Fixed pipeline",zh:"固定流程"}},{l:0,t:{en:"Human scaffold",zh:"人工 Scaffold"}},{l:1,t:{en:"Agent loop",zh:"Agent 闭环"}},{l:3,t:{en:"Prompt/system optimization",zh:"提示与系统优化"}},{l:5,t:{en:"Graph/workflow search",zh:"图与工作流搜索"}},{l:5,t:{en:"Harness evolution",zh:"Harness 进化"}}]},
    {name:{en:"Governed open-ended evolution",zh:"受治理的开放式进化"},values:[{l:0,t:{en:"Not applicable",zh:"不适用"}},{l:0,t:{en:"No release gate",zh:"无发布门控"}},{l:0,t:{en:"Local checks",zh:"局部检查"}},{l:1,t:{en:"Basic rollback",zh:"基础回滚"}},{l:2,t:{en:"Longitudinal tests",zh:"纵向测试"}},{l:4,t:{en:"Safety/provenance agenda",zh:"安全与溯源议程"}}]}
  ],
  directions: [
    {code:"D1",title:{en:"Experience admission and scope",zh:"经验准入与适用范围"},origin:"2023",growth:"2025–26",status:{en:"active",zh:"活跃"}},
    {code:"D2",title:{en:"Memory repair and consolidation",zh:"记忆修复与巩固"},origin:"2023",growth:"2024–26",status:{en:"maturing",zh:"持续成熟"}},
    {code:"D3",title:{en:"Skill/tool/permission lifecycle",zh:"技能、工具与权限生命周期"},origin:"2023",growth:"2025–26",status:{en:"fast growth",zh:"快速增长"}},
    {code:"D4",title:{en:"Routing, contracts, and composition",zh:"路由、契约与组合"},origin:"2024",growth:"2025–26",status:{en:"emerging",zh:"新兴"}},
    {code:"D5",title:{en:"Embodiment and world adaptation",zh:"具身与世界适应"},origin:"2023",growth:"2025–26",status:{en:"active",zh:"活跃"}},
    {code:"D6",title:{en:"Negative-evolution evaluation",zh:"负向进化评测"},origin:"2025",growth:"2026",status:{en:"critical gap",zh:"关键缺口"}},
    {code:"D7",title:{en:"Safety, provenance, risk propagation",zh:"安全、溯源与风险传播"},origin:"2024",growth:"2026",status:{en:"fast growth",zh:"快速增长"}},
    {code:"D8",title:{en:"Cost, oversight, meta-control",zh:"成本、监督与元控制"},origin:"2024",growth:"2026",status:{en:"early",zh:"早期"}},
    {code:"D9",title:{en:"Goals, personalization, endogenous drift",zh:"目标、个性化与内生漂移"},origin:"2024",growth:"2025–26",status:{en:"fragmented",zh:"分散发展"}},
    {code:"D10",title:{en:"Cross-agent transfer and plural lineages",zh:"跨 Agent 迁移与复数谱系"},origin:"2023",growth:"2026",status:{en:"early",zh:"早期"}}
  ],
  milestones: [
    {year:2017,short:"Transformer",title:"Attention Is All You Need",venue:"NeurIPS"},
    {year:2019,short:"BERT",title:"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",venue:"NAACL"},
    {year:2020,short:"GPT-3",title:"Language Models are Few-Shot Learners",venue:"NeurIPS"},
    {year:2022,short:"CoT",title:"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",venue:"NeurIPS"},
    {year:2022,short:"STaR",title:"STaR: Bootstrapping Reasoning With Reasoning",venue:"NeurIPS"},
    {year:2023,short:"ReAct",title:"ReAct: Synergizing Reasoning and Acting in Language Models",venue:"ICLR"},
    {year:2023,short:"Self-Instruct",title:"Self-Instruct: Aligning Language Models with Self-Generated Instructions",venue:"ACL"},
    {year:2023,short:"Toolformer",title:"Toolformer: Language Models Can Teach Themselves to Use Tools",venue:"NeurIPS"},
    {year:2023,short:"Reflexion",title:"Reflexion: Language Agents with Verbal Reinforcement Learning",venue:"NeurIPS"},
    {year:2024,short:"OPRO",title:"Large Language Models as Optimizers",venue:"ICLR"},
    {year:2024,short:"Retroformer",title:"Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization",venue:"ICLR Spotlight"},
    {year:2024,short:"Voyager",title:"Voyager: An Open-Ended Embodied Agent with Large Language Models",venue:"TMLR"},
    {year:2024,short:"CLOVA",title:"CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update",venue:"CVPR"},
    {year:2025,short:"ADAS",title:"Automated Design of Agentic Systems",venue:"ICLR"},
    {year:2025,short:"AFlow",title:"AFlow: Automating Agentic Workflow Generation",venue:"ICLR Oral"},
    {year:2025,short:"WebRL",title:"WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning",venue:"ICLR"},
    {year:2025,short:"VISCO",title:"VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning",venue:"CVPR"},
    {year:2025,short:"Critic-V",title:"Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning",venue:"CVPR"},
    {year:2025,short:"Dynamic API",title:"Visual Agentic AI for Spatial Reasoning with a Dynamic API",venue:"CVPR"},
    {year:2026,short:"VisPlay",title:"VisPlay: Self-Evolving Vision-Language Models",venue:"CVPR"},
    {year:2026,short:"META",title:"META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding",venue:"CVPR"},
    {year:2026,short:"EvoGraph-R1",title:"EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval",venue:"CVPR"},
    {year:2026,short:"History to Future",title:"History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation",venue:"CVPR"}
  ],
  shifts: [
    {from:{en:"Static task model",zh:"静态任务模型"},to:{en:"Interactive agent",zh:"交互式 Agent"},impact:{en:"Reason–act–observe loops",zh:"推理—行动—观察闭环"}},
    {from:{en:"Current-context fix",zh:"当前上下文修正"},to:{en:"Persistent experience",zh:"持久经验"},impact:{en:"Reuse across later tasks",zh:"跨后续任务复用"}},
    {from:{en:"Manual prompt",zh:"人工提示词"},to:{en:"Automatic optimization",zh:"自动优化"},impact:{en:"Feedback drives updates",zh:"反馈驱动更新"}},
    {from:{en:"Fixed tools",zh:"固定工具"},to:{en:"Learned skills/tools",zh:"学习型技能与工具"},impact:{en:"Executable capability growth",zh:"可执行能力增长"}},
    {from:{en:"Fixed workflow",zh:"固定工作流"},to:{en:"Agent/workflow search",zh:"Agent 与工作流搜索"},impact:{en:"System-level self-design",zh:"系统级自设计"}},
    {from:{en:"Text-only agent",zh:"纯文本 Agent"},to:{en:"Multimodal/embodied agent",zh:"多模态与具身 Agent"},impact:{en:"World-grounded evolution",zh:"面向世界的进化"}},
    {from:{en:"Autonomous proposal",zh:"自主提出更新"},to:{en:"Governed release",zh:"受治理发布"},impact:{en:"Audit, safety, rollback",zh:"审计、安全与回滚"}}
  ],
  enablers: [
    {title:{en:"Capable foundation models",zh:"高能力基础模型"},body:{en:"Reasoning, planning, code, and multimodal perception",zh:"推理、规划、代码与多模态感知"}},
    {title:{en:"Long context and memory",zh:"长上下文与外部记忆"},body:{en:"Cross-episode retrieval, reflection, and consolidation",zh:"跨回合检索、反思与巩固"}},
    {title:{en:"Tools, APIs, and environments",zh:"工具、API 与环境"},body:{en:"Executable feedback beyond text generation",zh:"超越文本生成的可执行反馈"}},
    {title:{en:"Verifiable feedback",zh:"可验证反馈"},body:{en:"Tests, task success, critics, and counterfactual checks",zh:"测试、任务成功、Critic 与反事实检查"}},
    {title:{en:"Agent frameworks and interfaces",zh:"Agent 框架与接口"},body:{en:"Reusable loops, graphs, routers, and harnesses",zh:"可复用闭环、图、路由与 Harness"}},
    {title:{en:"Open benchmarks and artifacts",zh:"开放基准与研究工件"},body:{en:"Comparable tasks, code, models, and version histories",zh:"可比较任务、代码、模型与版本历史"}}
  ],
  claimLadder: [
    {level:"L1",title:{en:"Self-correction",zh:"自纠错"},question:{en:"Can the current answer or action be repaired?",zh:"当前回答或动作能否被修正？"}},
    {level:"L2",title:{en:"Experience reuse",zh:"经验复用"},question:{en:"Does the lesson help a later related task?",zh:"经验能否帮助后续相关任务？"}},
    {level:"L3",title:{en:"Persistent evolution",zh:"持久进化"},question:{en:"Was memory, skill, workflow, or model state committed?",zh:"是否提交了记忆、技能、工作流或模型状态？"}},
    {level:"L4",title:{en:"System evolution",zh:"系统进化"},question:{en:"Can multiple components evolve without regression?",zh:"多个组件能否在无回退下共同进化？"}},
    {level:"L5",title:{en:"Governed open-ended evolution",zh:"受治理的开放式进化"},question:{en:"Is long-term improvement safe, auditable, and reversible?",zh:"长期改进是否安全、可审计且可逆？"}}
  ],
  challenges: [
    {title:{en:"Genuine persistence",zh:"真实持久性"},body:{en:"Separate lasting learning from retries and context growth.",zh:"区分持久学习与重试、上下文增长。"}},
    {title:{en:"Negative evolution",zh:"负向进化"},body:{en:"Detect harmful commits hidden by average success.",zh:"发现被平均成功率掩盖的有害提交。"}},
    {title:{en:"Causal lesson validity",zh:"经验因果有效性"},body:{en:"Reject shortcuts and overgeneralized explanations.",zh:"拒绝捷径与过度泛化解释。"}},
    {title:{en:"Compatibility",zh:"兼容性"},body:{en:"Control semantic breakage after independent updates.",zh:"控制组件独立更新后的语义破坏。"}},
    {title:{en:"Security and permissions",zh:"安全与权限"},body:{en:"Prevent poisoning, capability creep, and risk amplification.",zh:"防止投毒、能力越权与风险放大。"}},
    {title:{en:"Evaluation integrity",zh:"评测完整性"},body:{en:"Avoid evaluator co-adaptation and audit-aware behavior.",zh:"避免评价器共适应与审计感知行为。"}},
    {title:{en:"Cost and oversight",zh:"成本与监督"},body:{en:"Allocate limited compute and human review intelligently.",zh:"智能分配有限算力与人工审查。"}},
    {title:{en:"Open-world transfer",zh:"开放世界迁移"},body:{en:"Generalize across tasks, models, agents, and embodiments.",zh:"跨任务、模型、Agent 与具身形态泛化。"}}
  ]
};
