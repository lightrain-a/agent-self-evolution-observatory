window.PAPER_METHOD_NOTES = {
  "Attention Is All You Need": {
    en:"Replaces recurrence with multi-head self-attention so sequence representations can be learned in parallel.",
    zh:"用多头自注意力替代循环结构，使序列表示能够并行学习。"
  },
  "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding": {
    en:"Pretrains bidirectional representations with masked-token and sentence-level objectives, then fine-tunes them for downstream tasks.",
    zh:"通过掩码词与句级目标预训练双向表示，再面向下游任务微调。"
  },
  "Language Models are Few-Shot Learners": {
    en:"Scales autoregressive language modeling and adapts behavior from demonstrations placed directly in the prompt.",
    zh:"扩展自回归语言建模规模，并通过提示词中的示例直接适应新任务。"
  },
  "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models": {
    en:"Adds intermediate natural-language reasoning examples to prompts so large models generate explicit multi-step solutions.",
    zh:"在提示词中加入中间推理示例，使大模型生成显式多步解题过程。"
  },
  "STaR: Bootstrapping Reasoning With Reasoning": {
    en:"Lets a model generate rationales, keeps rationales that lead to correct answers, and repeatedly fine-tunes on the filtered set.",
    zh:"让模型生成推理过程，保留能够得到正确答案的推理，再反复用筛选结果微调。"
  },
  "ReAct: Synergizing Reasoning and Acting in Language Models": {
    en:"Interleaves verbal reasoning with tool or environment actions so observations can revise the next reasoning step.",
    zh:"交替执行语言推理与工具或环境动作，让新观测修正下一步推理。"
  },
  "Self-Instruct: Aligning Language Models with Self-Generated Instructions": {
    en:"Bootstraps instruction-following data by generating, filtering, and expanding instructions with the language model itself.",
    zh:"由语言模型自行生成、过滤并扩展指令数据，以自举方式提升指令遵循能力。"
  },
  "Toolformer: Language Models Can Teach Themselves to Use Tools": {
    en:"Self-supervises candidate API calls inside text and retains calls whose returned results improve language-model likelihood.",
    zh:"在文本中自监督插入候选 API 调用，只保留返回结果能改善语言建模的调用。"
  },
  "Reflexion: Language Agents with Verbal Reinforcement Learning": {
    en:"Converts task feedback into verbal reflections stored in episodic memory and reuses them in later attempts.",
    zh:"把任务反馈转化为语言反思并写入情景记忆，在后续尝试中复用。"
  },
  "Self-Refine: Iterative Refinement with Self-Feedback": {
    en:"Uses the same model to produce an output, critique it, and iteratively revise it without additional training.",
    zh:"使用同一模型生成结果、自我批评并多轮修订，不需要额外训练。"
  },
  "Large Language Models as Optimizers": {
    en:"Represents optimization history in text and asks an LLM to propose new candidate solutions or prompts with higher scores.",
    zh:"把优化历史表示为文本，让 LLM 提出得分更高的新候选解或提示词。"
  },
  "Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization": {
    en:"Learns a retrospective feedback model from task rewards and uses its feedback to improve future agent trajectories.",
    zh:"从任务奖励中学习回顾式反馈模型，再用该反馈改进后续 Agent 轨迹。"
  },
  "Voyager: An Open-Ended Embodied Agent with Large Language Models": {
    en:"Combines automatic curriculum generation, iterative environment feedback, and a growing executable skill library in Minecraft.",
    zh:"在 Minecraft 中结合自动课程生成、环境迭代反馈和持续增长的可执行技能库。"
  },
  "CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update": {
    en:"Plans with visual tools, reflects on execution failures, and updates tool implementations or usage strategies in a closed loop.",
    zh:"使用视觉工具进行规划，对执行失败进行反思，并闭环更新工具实现或调用策略。"
  },
  "Automated Design of Agentic Systems": {
    en:"Uses a meta-agent to generate and evaluate new agent programs, maintaining an archive of higher-performing designs.",
    zh:"使用元 Agent 生成并评测新的 Agent 程序，并维护高性能设计档案。"
  },
  "AFlow: Automating Agentic Workflow Generation": {
    en:"Represents agent workflows as code-like structures and uses search with execution feedback to discover better workflows.",
    zh:"把 Agent 工作流表示为类代码结构，并利用执行反馈搜索更优工作流。"
  },
  "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning": {
    en:"Builds an online curriculum from web-agent experience and applies reinforcement learning on progressively selected tasks.",
    zh:"从 Web Agent 经验中构建在线课程，并在逐步选择的任务上进行强化学习。"
  },
  "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning": {
    en:"Constructs fine-grained visual-reasoning errors and evaluates whether models can locate, explain, and correct those errors.",
    zh:"构造细粒度视觉推理错误，评测模型能否定位、解释并修正这些错误。"
  },
  "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning": {
    en:"Trains or uses dedicated vision-language critics to identify errors and provide corrective supervision to multimodal reasoners.",
    zh:"训练或使用专门的视觉语言 Critic 识别错误，并向多模态推理器提供纠正监督。"
  },
  "Visual Agentic AI for Spatial Reasoning with a Dynamic API": {
    en:"Lets a visual agent compose or select task-specific spatial operations through a dynamically available API.",
    zh:"让视觉 Agent 通过动态可用的 API 组合或选择任务特定的空间操作。"
  },
  "VisPlay: Self-Evolving Vision-Language Models": {
    en:"Jointly trains an image-conditioned questioner and a multimodal solver so unlabeled images generate progressively useful self-play data.",
    zh:"联合训练图像条件提问者和多模态求解器，使无标注图像产生逐步有用的自博弈数据。"
  },
  "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding": {
    en:"Consolidates successful tool-use trajectories into reusable macro-tools and adapts them for long-video reasoning.",
    zh:"把成功的工具使用轨迹巩固为可复用宏工具，并用于长视频推理适应。"
  },
  "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval": {
    en:"Builds and iteratively edits a multimodal knowledge hypergraph using retrieval and reasoning feedback.",
    zh:"根据检索与推理反馈构建并迭代编辑多模态知识超图。"
  },
  "History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation": {
    en:"Stores navigation experience and generates future-oriented thoughts to improve zero-shot vision-language navigation decisions.",
    zh:"存储导航经验并生成面向未来的思考，以改进零样本视觉语言导航决策。"
  }
};
