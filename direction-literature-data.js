window.DIRECTION_LITERATURE = {
  "experience-admission": [
    {
      title:"EVE-Agent: Evidence-Verifiable Self-Evolving Agents", short:"EVE-Agent", year:2026, venue:"arXiv",
      method:{en:"Verifies the question, answer, and supporting evidence before a self-generated update is accepted.",zh:"在接受自生成更新前，联合验证问题、答案与支撑证据。"},
      fit:{en:"Anchors evidence-based admission rather than outcome-only learning.",zh:"代表基于证据的经验准入，而不是仅依据结果学习。"}
    },
    {
      title:"Active Zero: Self-Evolving Vision-Language Models through Active Environment Exploration", short:"Active Zero", year:2026, venue:"arXiv",
      method:{en:"Actively searches visual data near the model's capability frontier and co-evolves question generation and solving.",zh:"主动搜索模型能力边界附近的视觉数据，并共同进化问题生成与求解。"},
      fit:{en:"Represents experience acquisition before admission and updating.",zh:"代表持久准入与更新之前的经验获取过程。"}
    },
    {
      title:"Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity", short:"Gated Harness QD", year:2026, venue:"arXiv",
      method:{en:"Separates proposed harness mutations from deterministic validity, credit, and sealed-test gates.",zh:"把候选 Harness 变异与确定性有效性、归因和封闭测试门控分离。"},
      fit:{en:"Provides a concrete commit gate for deciding which candidate updates survive.",zh:"为候选更新是否能够提交提供具体门控机制。"}
    }
  ],
  "memory-lifecycle": [
    {
      title:"MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents", short:"MemSkill", year:2026, venue:"arXiv",
      method:{en:"Treats memory extraction, consolidation, and pruning as learnable skills that are selected and redesigned over time.",zh:"把记忆提取、整合与剪枝视为可学习并持续重设计的技能。"},
      fit:{en:"Directly studies how memory operations themselves evolve.",zh:"直接研究记忆操作本身如何进化。"}
    },
    {
      title:"EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective", short:"EvoMemBench", year:2026, venue:"arXiv",
      method:{en:"Compares multiple memory forms across knowledge- and execution-oriented persistent task settings.",zh:"在知识型与执行型持久任务中比较多种记忆形式。"},
      fit:{en:"Shows why representation and lifecycle choices must be evaluated separately.",zh:"说明记忆表示与生命周期选择必须被单独评测。"}
    },
    {
      title:"ManimAgent: Self-Evolving Multimodal Agents for Visual Education", short:"ManimAgent", year:2026, venue:"arXiv",
      method:{en:"Carries successful rationales and validated failure patterns across tasks through dual-channel episodic memory.",zh:"通过双通道情景记忆，在任务间保留成功理由与经验证失败模式。"},
      fit:{en:"Provides a multimodal example of persistent memory consolidation and reuse.",zh:"提供多模态持久记忆巩固与复用的具体实例。"}
    }
  ],
  "skill-tool-lifecycle": [
    {
      title:"Voyager: An Open-Ended Embodied Agent with Large Language Models", short:"Voyager", year:2024, venue:"TMLR",
      method:{en:"Uses an automatic curriculum and environment feedback to grow a reusable executable skill library.",zh:"通过自动课程和环境反馈持续扩展可复用的可执行技能库。"},
      fit:{en:"A foundational example of persistent skill acquisition and reuse.",zh:"是持久技能获取与复用的代表性前置工作。"}
    },
    {
      title:"VASO: Formally Verifiable Self-Evolving Skills for Physical AI Agents", short:"VASO", year:2026, venue:"arXiv",
      method:{en:"Attaches formal contracts and counterexample traces to evolving physical-agent skills.",zh:"为进化中的物理 Agent 技能附加形式契约与反例轨迹。"},
      fit:{en:"Represents verification and release control across the skill lifecycle.",zh:"代表技能生命周期中的验证与发布控制。"}
    },
    {
      title:"SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems", short:"SkillSmith", year:2026, venue:"arXiv",
      method:{en:"Jointly evolves reusable skills and the tool layer while modeling complementarity, conflict, and anti-patterns.",zh:"联合进化可复用技能与工具层，并建模互补、冲突和反模式。"},
      fit:{en:"Moves beyond isolated skills to skill-tool co-evolution and maintenance.",zh:"把研究从单个技能扩展到技能—工具共进化与维护。"}
    }
  ],
  "system-composition": [
    {
      title:"AFlow: Automating Agentic Workflow Generation", short:"AFlow", year:2025, venue:"ICLR",
      method:{en:"Represents workflows as executable structures and searches them using task-execution feedback.",zh:"把工作流表示为可执行结构，并利用任务执行反馈进行搜索。"},
      fit:{en:"A direct example of system-level routing and workflow optimization.",zh:"是系统级路由与工作流优化的直接实例。"}
    },
    {
      title:"Automated Design of Agentic Systems", short:"ADAS", year:2025, venue:"ICLR",
      method:{en:"Uses a meta-agent to generate, evaluate, and archive higher-performing agent programs.",zh:"使用元 Agent 生成、评测并归档表现更好的 Agent 程序。"},
      fit:{en:"Establishes agent-system design itself as an evolvable object.",zh:"把 Agent 系统设计本身确立为可进化对象。"}
    },
    {
      title:"Autogenesis: A Self-Evolving Agent Protocol", short:"Autogenesis", year:2026, venue:"arXiv",
      method:{en:"Versions prompts, agents, tools, environments, and memory through an auditable propose-assess-commit protocol.",zh:"通过可审计的提出—评估—提交协议，对提示词、Agent、工具、环境和记忆进行版本化。"},
      fit:{en:"Provides interfaces, lineage, and rollback for composing independently evolving components.",zh:"为独立进化组件的组合提供接口、谱系与回滚机制。"}
    }
  ],
  "embodied-world": [
    {
      title:"Self-evolving Embodied AI", short:"Self-evolving Embodied AI", year:2026, venue:"arXiv",
      method:{en:"Separates embodied evolution into memory, task, environment, embodiment, and model adaptation modules.",zh:"把具身进化拆分为记忆、任务、环境、具身与模型适应模块。"},
      fit:{en:"Defines the main adaptation surfaces in changing bodies and worlds.",zh:"界定变化身体与环境中的主要适应对象。"}
    },
    {
      title:"World Model Implanting for Test-Time Adaptation of Embodied Agents", short:"World Model Implanting", year:2025, venue:"arXiv",
      method:{en:"Retrieves and implants domain-relevant world models to adapt embodied agents at test time.",zh:"检索并植入领域相关世界模型，实现具身 Agent 的测试时适应。"},
      fit:{en:"Represents world-model-based adaptation without full policy retraining.",zh:"代表无需完整重训策略的世界模型适应。"}
    },
    {
      title:"Self-Evolving World Models for LLM Agent Planning", short:"Self-Evolving World Models", year:2026, venue:"arXiv",
      method:{en:"Repairs episodic and semantic world-model memory from prediction-observation mismatches.",zh:"根据预测—观测偏差修复情景与语义世界模型记忆。"},
      fit:{en:"Directly connects environmental mismatch to persistent world-model repair.",zh:"直接连接环境偏差与持久世界模型修复。"}
    }
  ],
  "negative-evaluation": [
    {
      title:"SEA-Eval: A Benchmark for Evaluating Self-Evolving Agents Beyond Episodic Assessment", short:"SEA-Eval", year:2026, venue:"arXiv",
      method:{en:"Evaluates both episodic execution and long-term version trajectories across sequential task streams.",zh:"在连续任务流中同时评测单回合执行与长期版本轨迹。"},
      fit:{en:"Makes longitudinal evolution, rather than one final score, the evaluation unit.",zh:"把纵向进化而不是单个最终分数作为评测单位。"}
    },
    {
      title:"Hidden Forgetting in Continual Multimodal Learning: When Accuracy Survives but Grounding Fails", short:"Hidden Forgetting", year:2026, venue:"arXiv",
      method:{en:"Uses counterfactual interventions to reveal grounding loss that ordinary accuracy does not detect.",zh:"使用反事实干预揭示普通准确率无法发现的 Grounding 丢失。"},
      fit:{en:"Exemplifies harmful evolution hidden by aggregate task success.",zh:"代表被聚合任务成功率掩盖的有害进化。"}
    },
    {
      title:"EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective", short:"EvoMemBench", year:2026, venue:"arXiv",
      method:{en:"Benchmarks memory methods across persistent knowledge and execution tasks under a shared protocol.",zh:"在统一协议下评测持久知识与执行任务中的记忆方法。"},
      fit:{en:"Provides a component-specific longitudinal benchmark for evolving memory.",zh:"为进化记忆提供组件级纵向基准。"}
    }
  ],
  "security-provenance": [
    {
      title:"MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents", short:"MemPoison", year:2026, venue:"arXiv",
      method:{en:"Tests direct, compositional, and dormant memory attacks across writing, retrieval composition, and activation.",zh:"跨写入、检索组合与激活阶段测试直接、组合型和休眠型记忆攻击。"},
      fit:{en:"Shows why persistent-update security must cover the full memory supply chain.",zh:"说明持久更新安全必须覆盖完整记忆供应链。"}
    },
    {
      title:"Hidden in Memory: Sleeper Memory Poisoning in LLM Agents", short:"Sleeper Memory Poisoning", year:2026, venue:"arXiv",
      method:{en:"Studies malicious memories that remain dormant across sessions and activate after later retrieval.",zh:"研究跨会话休眠并在后续检索后激活的恶意记忆。"},
      fit:{en:"Represents delayed and cross-session propagation risk.",zh:"代表延迟触发与跨会话传播风险。"}
    },
    {
      title:"Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies", short:"Safety in Self-Evolving Agents", year:2026, venue:"arXiv",
      method:{en:"Maps threats across agent modules and lifecycle stages, emphasizing persistence and cross-generation amplification.",zh:"跨 Agent 模块与生命周期阶段刻画威胁，强调持久化与跨代放大。"},
      fit:{en:"Provides the system-level risk-propagation model for this direction.",zh:"为该方向提供系统级风险传播模型。"}
    }
  ],
  "governance-control": [
    {
      title:"Towards Healthy Evolution: Exploring the Role and Mechanisms of Human-Agent Interaction in Self-Evolving Systems", short:"Towards Healthy Evolution", year:2026, venue:"arXiv",
      method:{en:"Studies where limited human supervision best reduces safety drift across the evolution process.",zh:"研究有限人工监督在进化流程的哪些阶段最能降低安全漂移。"},
      fit:{en:"Directly addresses where and when oversight should intervene.",zh:"直接回答监督应在何处、何时介入。"}
    },
    {
      title:"Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human", short:"Oversight Has a Capacity", year:2026, venue:"arXiv",
      method:{en:"Models review as a finite resource affected by disagreement, fatigue, and flooding attacks.",zh:"把审查建模为受分歧、疲劳与洪泛攻击影响的有限资源。"},
      fit:{en:"Provides a resource-aware basis for escalation and review allocation.",zh:"为升级决策与审查资源分配提供容量感知基础。"}
    },
    {
      title:"Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning", short:"MetaEvolve", year:2026, venue:"arXiv",
      method:{en:"Trains reflection and multi-round refinement as explicit meta-skills, then combines them with evolutionary search.",zh:"把反思与多轮改进训练为显式元技能，并与进化搜索结合。"},
      fit:{en:"Makes the controller's ability to improve itself an explicit learning target.",zh:"把进化控制器的自我改进能力设为显式学习目标。"}
    }
  ],
  "adaptive-objectives": [
    {
      title:"Accelerating Scientific Discovery with Autonomous Goal-evolving Agents", short:"Goal-Evolving Agents", year:2025, venue:"arXiv",
      method:{en:"Evolves computable objectives in an outer loop while optimizing candidate solutions in an inner loop.",zh:"在外循环中进化可计算目标，在内循环中优化候选解。"},
      fit:{en:"A direct example of persistent goal evolution rather than fixed-objective optimization.",zh:"是持久目标进化而非固定目标优化的直接实例。"}
    },
    {
      title:"Partially Performative Prediction", short:"Partially Performative Prediction", year:2026, venue:"arXiv",
      method:{en:"Separates distribution change caused by the deployed learner from simultaneous external drift.",zh:"区分部署学习器自身造成的分布变化与同时存在的外部漂移。"},
      fit:{en:"Provides the theoretical basis for agent-induced feedback and adaptation.",zh:"为 Agent 自致反馈与适应提供理论基础。"}
    },
    {
      title:"Self-Evolving Software Agents", short:"Self-Evolving Software Agents", year:2026, venue:"arXiv",
      method:{en:"Evolves goals, reasoning, and executable code from deployment experience.",zh:"根据部署经验共同进化目标、推理与可执行代码。"},
      fit:{en:"Shows how changing objectives interact with persistent system behavior.",zh:"展示变化目标如何与持久系统行为相互作用。"}
    }
  ],
  "collective-evolution": [
    {
      title:"Self-Evolving Multi-Agent Systems via Decentralized Memory", short:"Decentralized-Memory MAS", year:2026, venue:"arXiv",
      method:{en:"Uses local exploitation and exploration memory pools to preserve diversity across evolving agents.",zh:"使用本地利用池与探索池保持进化 Agent 之间的多样性。"},
      fit:{en:"Represents persistent collective learning without one centralized memory lineage.",zh:"代表不依赖单一集中式记忆谱系的持久群体学习。"}
    },
    {
      title:"Multi-agent Architecture Search via Agentic Supernet", short:"Agentic Supernet", year:2025, venue:"ICML",
      method:{en:"Searches multi-agent topologies under a joint accuracy-cost objective.",zh:"在联合准确率—成本目标下搜索多 Agent 拓扑。"},
      fit:{en:"Shows how heterogeneous agent composition can be searched and specialized.",zh:"展示异构 Agent 组合如何被搜索与专门化。"}
    },
    {
      title:"The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators", short:"Red Queen Gödel Machine", year:2026, venue:"arXiv",
      method:{en:"Co-evolves agents and evaluation criteria across epochs under non-stationary utility.",zh:"在非平稳效用下跨阶段共同进化 Agent 与评价标准。"},
      fit:{en:"Provides a population-level example of interacting evolutionary lineages.",zh:"提供相互作用进化谱系的群体级实例。"}
    }
  ]
};
