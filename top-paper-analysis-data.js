window.TOP_PAPER_ANALYSES = {
  "Attention Is All You Need": {
    problem:{en:"Recurrent and convolutional sequence models make long-range dependency modeling indirect and limit parallel training. The paper asks whether sequence transduction can be built without recurrence.",zh:"循环与卷积序列模型对长程依赖的建模路径较间接，而且限制并行训练。论文要回答能否完全不依赖循环结构完成序列转换。"},
    advantage:{en:"Compared with recurrent models, the Transformer exposes direct token-to-token interactions and parallelizes training; compared with convolutional stacks, long-range communication does not require many layers.",zh:"相较循环模型，Transformer 允许任意 Token 直接交互并可并行训练；相较卷积堆叠，长程信息传递不需要经过很多层。"},
    intuition:{en:"A token representation can be formed by attending to all other tokens with content-dependent weights, while positional encodings supply order information.",zh:"每个 Token 可以根据内容相关权重聚合全部其他 Token 的信息，再用位置编码补充顺序信息。"},
    rationale:{en:"Multi-head attention can represent several relational patterns at once, and residual/feed-forward blocks transform the aggregated context into task-relevant features.",zh:"多头注意力能够同时表示多种关系模式，残差与前馈模块再把聚合后的上下文转化为任务相关表示。"},
    flow:{en:"Embed tokens and positions → apply stacked multi-head self-attention and feed-forward blocks → use encoder-decoder attention in the decoder → predict the next output token.",zh:"编码 Token 与位置 → 堆叠多头自注意力和前馈模块 → 在解码器中使用编码器—解码器注意力 → 预测下一个输出 Token。"},
    validation:{en:"Evaluate on large-scale machine-translation benchmarks, compare quality and training cost with recurrent/convolutional systems, and ablate attention heads, depth, and positional choices.",zh:"在大规模机器翻译基准上评测，与循环和卷积系统比较质量及训练成本，并消融注意力头数、深度和位置编码。"}
  },
  "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding": {
    problem:{en:"Left-to-right language models cannot jointly condition every representation on both left and right context, limiting general-purpose language understanding pretraining.",zh:"从左到右的语言模型无法让每个表示同时利用左右上下文，从而限制通用语言理解预训练。"},
    advantage:{en:"Compared with one-directional pretraining and task-specific feature engineering, BERT provides deeply bidirectional representations that can be adapted with a small task head.",zh:"相较单向预训练和任务专属特征工程，BERT 提供深层双向表示，通常只需增加很小的任务头即可适配。"},
    intuition:{en:"Masking a subset of tokens prevents the model from trivially seeing the target while allowing the remaining representation to use context from both directions.",zh:"随机遮蔽部分 Token 可以避免直接看到预测目标，同时允许其余表示利用双向上下文。"},
    rationale:{en:"Large unlabeled corpora contain reusable syntactic and semantic structure; bidirectional contextual prediction can encode that structure before supervised fine-tuning.",zh:"大规模无标注语料包含可复用的句法与语义结构，双向上下文预测可以在监督微调前把这些结构编码进模型。"},
    flow:{en:"Pretrain a Transformer encoder with masked-token and sentence-level objectives → attach a lightweight task-specific output layer → fine-tune the full model on labeled downstream data.",zh:"使用掩码词和句级目标预训练 Transformer 编码器 → 添加轻量任务输出层 → 在下游标注数据上微调整个模型。"},
    validation:{en:"Test on sentence-level language-understanding suites and extractive question answering, comparing with feature-based and generative pretraining baselines.",zh:"在句级语言理解套件和抽取式问答上测试，并与特征式方法及生成式预训练基线比较。"}
  },
  "Language Models are Few-Shot Learners": {
    problem:{en:"Most NLP systems require task-specific labeled data and gradient updates. The paper asks whether one sufficiently large language model can adapt from natural-language instructions and examples alone.",zh:"多数 NLP 系统需要任务专属标注数据和梯度更新。论文考察足够大的语言模型能否仅通过自然语言指令和示例完成适配。"},
    advantage:{en:"Compared with fine-tuning, in-context learning changes behavior without modifying weights; compared with zero-shot prompting, demonstrations communicate the task format and decision boundary.",zh:"相较微调，上下文学习无需修改权重；相较零样本提示，示例能够传达任务格式和决策边界。"},
    intuition:{en:"At scale, next-token prediction may learn reusable latent task patterns, allowing the prompt itself to specify a temporary task.",zh:"当规模足够大时，下一 Token 预测可能学到可复用的潜在任务模式，使提示词本身能够临时定义任务。"},
    rationale:{en:"A broad pretraining distribution exposes the model to many input-output regularities; demonstrations select and instantiate a relevant regularity at inference time.",zh:"广泛的预训练分布让模型接触大量输入—输出规律，推理时的示例负责选择并实例化相关规律。"},
    flow:{en:"Pretrain a large autoregressive language model → place instructions and zero, one, or several demonstrations in context → generate the answer with no parameter update.",zh:"预训练大规模自回归语言模型 → 在上下文中放入指令以及零个、一个或多个示例 → 在不更新参数的情况下生成答案。"},
    validation:{en:"Compare zero-shot, one-shot, and few-shot performance across a broad collection of language, reasoning, and generation tasks and across model scales.",zh:"在广泛的语言、推理和生成任务上比较零样本、单样本和少样本表现，并分析不同模型规模。"}
  },
  "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models": {
    problem:{en:"Direct answer prompting often fails on tasks requiring multiple latent reasoning steps because the model is not shown how intermediate computation should be represented.",zh:"直接答案提示在需要多步隐式计算的任务上经常失败，因为模型没有看到中间推理应该如何表达。"},
    advantage:{en:"Compared with retraining or specialized symbolic solvers, chain-of-thought prompting is a lightweight prompt-only intervention that can transfer across reasoning tasks.",zh:"相较重新训练或专门符号求解器，思维链提示只是轻量的提示词干预，并可迁移到多类推理任务。"},
    intuition:{en:"Worked examples that include intermediate reasoning teach the model to externalize and sequence computations before producing the final answer.",zh:"包含中间推理的示范会教模型在给出最终答案前，把计算过程显式展开并按顺序组织。"},
    rationale:{en:"Large models already contain many reasoning primitives; exposing intermediate states reduces the burden of compressing an entire solution into one output transition.",zh:"大模型已经包含许多推理原语，显式中间状态能够减少把完整解法压缩到一次输出转换中的困难。"},
    flow:{en:"Provide several question–reasoning–answer demonstrations → prompt a new question → generate a natural-language reasoning trace → emit the final answer.",zh:"提供若干“问题—推理—答案”示范 → 输入新问题 → 生成自然语言推理轨迹 → 输出最终答案。"},
    validation:{en:"Evaluate arithmetic, symbolic, and commonsense reasoning across model scales, comparing direct prompting and chain-of-thought demonstrations.",zh:"在算术、符号和常识推理任务上跨模型规模评测，并与直接提示进行比较。"}
  },
  "STaR: Bootstrapping Reasoning With Reasoning": {
    problem:{en:"High-quality rationale annotations are expensive, while model-generated rationales are noisy. The paper seeks a way to bootstrap reasoning supervision from answer labels.",zh:"高质量推理标注成本很高，而模型自生成的推理又存在噪声。论文希望仅利用答案标签自举推理监督。"},
    advantage:{en:"Compared with fully annotated chain-of-thought training, STaR needs far fewer human rationales; compared with naive self-training, correctness filtering and rationalization reduce noisy supervision.",zh:"相较完整思维链标注训练，STaR 需要更少人工推理；相较朴素自训练，正确性过滤和反向合理化可降低噪声。"},
    intuition:{en:"Rationales that lead to known correct answers are more likely to encode useful reasoning patterns and can become training data for the next iteration.",zh:"能够导向已知正确答案的推理，更可能包含有用推理模式，可作为下一轮训练数据。"},
    rationale:{en:"Iterative filtering creates a positive feedback loop: a better reasoner generates more valid rationales, which then provide stronger supervision.",zh:"迭代过滤形成正反馈：更好的推理器会生成更多有效推理，而这些推理又提供更强监督。"},
    flow:{en:"Generate rationales for training questions → keep correct-answer traces → rationalize failed examples using the known answer → fine-tune on the collected traces → repeat.",zh:"为训练问题生成推理 → 保留答案正确的轨迹 → 利用已知答案为失败样本补充合理化推理 → 用收集轨迹微调 → 重复迭代。"},
    validation:{en:"Measure iterative gains on reasoning datasets, comparing answer-only training, naive rationale generation, and the full filtering/rationalization loop.",zh:"在推理数据集上测量迭代收益，并比较仅答案训练、朴素推理生成和完整过滤—合理化闭环。"}
  },
  "ReAct: Synergizing Reasoning and Acting in Language Models": {
    problem:{en:"Reasoning-only agents can hallucinate facts, while action-only policies may lack explicit plans and error diagnosis. The paper unifies reasoning and environment interaction.",zh:"仅推理 Agent 容易幻觉，仅动作策略又可能缺少显式计划与错误诊断。论文试图统一推理和环境交互。"},
    advantage:{en:"Compared with chain-of-thought alone, ReAct can acquire external evidence; compared with opaque action policies, it exposes an interpretable reasoning trace that guides tool use.",zh:"相较单独思维链，ReAct 能获取外部证据；相较不透明动作策略，它暴露可解释的推理轨迹来指导工具使用。"},
    intuition:{en:"Alternating thought, action, and observation lets the agent revise its belief and plan whenever the environment returns new information.",zh:"交替执行思考、动作和观察，使 Agent 能在环境返回新信息时持续修正信念与计划。"},
    rationale:{en:"External observations ground factual claims, while explicit reasoning maintains longer-horizon task context and decides which action is informative.",zh:"外部观察为事实主张提供 Grounding，显式推理则维持长程任务上下文并决定哪个动作最有信息价值。"},
    flow:{en:"Read the task → generate a thought → issue a tool or environment action → observe the result → update the next thought/action → stop with an answer or completed trajectory.",zh:"读取任务 → 生成思考 → 发出工具或环境动作 → 观察结果 → 更新下一步思考与动作 → 输出答案或完成轨迹。"},
    validation:{en:"Compare on knowledge-intensive question answering and interactive decision tasks against chain-of-thought, acting-only, and imitation/RL baselines.",zh:"在知识密集问答和交互决策任务上，与思维链、仅动作和模仿／强化学习基线比较。"}
  },
  "Self-Instruct: Aligning Language Models with Self-Generated Instructions": {
    problem:{en:"Instruction-tuning datasets require costly human authoring and cover only a limited range of tasks. The paper asks whether a language model can expand its own instruction data.",zh:"指令微调数据需要昂贵人工编写，而且覆盖任务有限。论文考察语言模型能否自行扩展指令数据。"},
    advantage:{en:"Compared with fully human-authored instruction collections, Self-Instruct scales data generation cheaply; compared with unfiltered synthetic data, it removes duplicates and malformed tasks.",zh:"相较完全人工指令集，Self-Instruct 能低成本扩展数据；相较未过滤合成数据，它会去除重复和格式错误任务。"},
    intuition:{en:"A capable pretrained model can propose new task instructions and examples by recombining patterns already present in its pretraining distribution.",zh:"有能力的预训练模型可以重组预训练分布中的模式，提出新的任务指令和示例。"},
    rationale:{en:"Iterative generation from a diverse seed set broadens task coverage, while heuristic and model-based filters keep the resulting supervision usable.",zh:"从多样种子集迭代生成可以扩展任务覆盖，启发式与模型过滤则保证监督数据可用。"},
    flow:{en:"Start from seed tasks → prompt the model to generate new instructions and instances → filter invalid or near-duplicate items → mix accepted data → instruction-tune the model.",zh:"从种子任务开始 → 提示模型生成新指令和样本 → 过滤无效或近重复内容 → 混合接受的数据 → 进行指令微调。"},
    validation:{en:"Evaluate instruction following on held-out tasks and human judgments, with ablations for filtering, seed size, and synthetic-data composition.",zh:"在留出指令任务和人工评价上评测，并消融过滤、种子规模和合成数据组成。"}
  },
  "Toolformer: Language Models Can Teach Themselves to Use Tools": {
    problem:{en:"Language models cannot reliably perform arithmetic, lookup, or time-sensitive retrieval internally, and supervised tool-call annotations are expensive.",zh:"语言模型难以仅靠内部参数可靠完成算术、查询或时效检索，而工具调用标注又很昂贵。"},
    advantage:{en:"Compared with manually labeled tool-use datasets, Toolformer creates supervision automatically; compared with always-on retrieval, it learns when and how a call is useful.",zh:"相较人工工具调用数据，Toolformer 自动生成监督；相较始终调用外部工具，它学习何时以及怎样调用才有用。"},
    intuition:{en:"A candidate API call is useful when inserting its returned result makes the surrounding text substantially easier for the language model to predict.",zh:"如果插入 API 返回结果后，周围文本对语言模型明显更容易预测，那么该候选调用就是有用的。"},
    rationale:{en:"Language-model likelihood provides a self-supervised utility signal for selecting tool calls without task-specific reward labels.",zh:"语言模型似然可作为自监督效用信号，在没有任务专属奖励标注时筛选工具调用。"},
    flow:{en:"Sample candidate API-call positions and arguments → execute calls → insert results → keep calls that improve likelihood → fine-tune the model on the augmented text.",zh:"采样候选 API 调用位置与参数 → 执行调用 → 插入结果 → 保留能提升似然的调用 → 用增强文本微调模型。"},
    validation:{en:"Test zero/few-shot language tasks requiring calculators, search, calendars, or translation, and compare with the same model without tool training and with ablated filtering.",zh:"在需要计算器、检索、日历或翻译的零／少样本任务上测试，并与无工具训练模型及过滤消融比较。"}
  },
  "Reflexion: Language Agents with Verbal Reinforcement Learning": {
    problem:{en:"Agents often repeat the same failure because outcome feedback disappears after an episode, while weight-based reinforcement learning is expensive and slow.",zh:"Agent 常因回合结束后反馈消失而重复同类错误，而基于权重的强化学习成本高且速度慢。"},
    advantage:{en:"Compared with parameter updates, Reflexion stores immediately editable verbal lessons; compared with blind retries, it conditions the next attempt on diagnosed failure causes.",zh:"相较参数更新，Reflexion 保存可立即编辑的语言经验；相较盲目重试，它让下一次尝试显式依赖失败诊断。"},
    intuition:{en:"Natural-language reflection can compress task feedback into a reusable rule that guides planning in later attempts.",zh:"自然语言反思可以把任务反馈压缩成可复用规则，指导后续尝试中的规划。"},
    rationale:{en:"The underlying model already understands language instructions, so a verbal memory can modify behavior without changing weights.",zh:"基础模型本身能够理解语言指令，因此语言记忆可在不改权重的情况下改变行为。"},
    flow:{en:"Run an episode → obtain task feedback → generate a verbal reflection → store it in episodic memory → include relevant reflections in the next attempt.",zh:"运行一个回合 → 获取任务反馈 → 生成语言反思 → 写入情景记忆 → 在下一次尝试中加入相关反思。"},
    validation:{en:"Evaluate repeated-attempt improvement on sequential decision, reasoning, and coding tasks against ordinary retries, chain-of-thought, and weight-updating alternatives.",zh:"在序列决策、推理和代码任务上评测多次尝试的改进，并与普通重试、思维链和权重更新方法比较。"}
  },
  "Self-Refine: Iterative Refinement with Self-Feedback": {
    problem:{en:"A model's first response may contain correctable defects, but external critics or training data are not always available at inference time.",zh:"模型首个回答可能包含可修正缺陷，但推理时并不总能获得外部 Critic 或训练数据。"},
    advantage:{en:"Compared with fine-tuning, Self-Refine needs no parameter update; compared with external-critic pipelines, it uses the same model for generation, feedback, and revision.",zh:"相较微调，Self-Refine 无需参数更新；相较外部 Critic 流程，它使用同一模型完成生成、反馈和修订。"},
    intuition:{en:"Recognizing a specific defect in an existing output can be easier than generating a perfect output from scratch.",zh:"识别已有输出中的具体缺陷，可能比从零生成完美答案更容易。"},
    rationale:{en:"Separating generation, critique, and refinement creates explicit intermediate objectives and lets the model condition on its previous output and feedback.",zh:"将生成、批评和修订分开，会形成显式中间目标，并让模型利用旧输出与反馈作为上下文。"},
    flow:{en:"Generate an initial answer → prompt the model for actionable feedback → revise using the answer and feedback → repeat until a stopping rule is met.",zh:"生成初始答案 → 提示模型给出可执行反馈 → 利用旧答案与反馈修订 → 重复直到满足停止规则。"},
    validation:{en:"Measure iterative improvement across generation, reasoning, and structured-output tasks, using task metrics and human judgments against one-pass and alternative-feedback baselines.",zh:"在生成、推理和结构化输出任务上测量迭代改进，并用任务指标和人工评价与单次生成及其他反馈基线比较。"}
  },
  "Large Language Models as Optimizers": {
    problem:{en:"Many prompt and black-box optimization problems lack gradients and require expensive manual search.",zh:"许多提示词和黑盒优化问题没有梯度，只能依赖昂贵人工搜索。"},
    advantage:{en:"Compared with numerical optimizers, OPRO can operate directly on natural-language candidates and feedback; compared with manual prompt engineering, it systematically reuses optimization history.",zh:"相较数值优化器，OPRO 可直接处理自然语言候选与反馈；相较人工提示词工程，它系统复用优化历史。"},
    intuition:{en:"An LLM can infer improvement directions when shown previous candidate solutions together with their scores.",zh:"当看到历史候选解及其分数时，LLM 可以推断下一步改进方向。"},
    rationale:{en:"The prompt acts as a textual optimization state, allowing pattern recognition over successful and unsuccessful candidates without explicit gradients.",zh:"提示词充当文本化优化状态，使模型无需显式梯度即可识别成功与失败候选中的模式。"},
    flow:{en:"Encode the objective and scored history in a meta-prompt → ask the LLM for new candidates → evaluate them externally → append scores to history → iterate.",zh:"把目标和带分数的历史写入元提示 → 让 LLM 生成新候选 → 外部评测 → 把分数加入历史 → 继续迭代。"},
    validation:{en:"Apply the loop to prompt optimization and mathematical objective search, comparing with random, evolutionary, and hand-designed search strategies.",zh:"将闭环用于提示词优化和数学目标搜索，并与随机、进化和人工设计搜索策略比较。"}
  },
  "Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization": {
    problem:{en:"Handwritten reflection prompts may produce inconsistent advice and do not directly learn which retrospective feedback improves future trajectories.",zh:"人工反思提示可能产生不稳定建议，而且不会直接学习哪类回顾反馈真正改善后续轨迹。"},
    advantage:{en:"Compared with fixed self-reflection, Retroformer trains a dedicated retrospective model from task rewards; compared with full agent fine-tuning, it localizes learning in the feedback component.",zh:"相较固定自反思，Retroformer 从任务奖励训练专门回顾模型；相较完整 Agent 微调，它把学习局限在反馈组件。"},
    intuition:{en:"Reward can supervise not only actions but also the quality of language feedback that will guide the next attempt.",zh:"奖励不仅能监督动作，也能监督将指导下一次尝试的语言反馈质量。"},
    rationale:{en:"A learned retrospective policy can adapt feedback style and content to recurring failure patterns instead of relying on one generic prompt.",zh:"学习式回顾策略可针对反复出现的失败模式调整反馈形式和内容，而非依赖单一通用提示。"},
    flow:{en:"Collect agent trajectories and rewards → generate retrospective feedback → optimize the feedback model with policy gradients → condition later trajectories on learned feedback.",zh:"收集 Agent 轨迹和奖励 → 生成回顾反馈 → 用策略梯度优化反馈模型 → 让后续轨迹条件化于学习到的反馈。"},
    validation:{en:"Compare task success and learning curves on interactive agent benchmarks against fixed reflection, no-reflection, and alternative optimization baselines.",zh:"在交互 Agent 基准上比较任务成功率和学习曲线，并与固定反思、无反思及其他优化基线比较。"}
  },
  "Voyager: An Open-Ended Embodied Agent with Large Language Models": {
    problem:{en:"Open-ended embodied environments lack a fixed task list, and agents with fixed skills struggle to accumulate competence over long exploration horizons.",zh:"开放式具身环境没有固定任务清单，而固定技能 Agent 难以在长期探索中持续积累能力。"},
    advantage:{en:"Compared with static prompting, Voyager combines curriculum generation, environment-grounded iteration, and a persistent executable skill library; compared with end-to-end RL, it can reuse code-level skills with fewer interactions.",zh:"相较静态提示，Voyager 结合课程生成、环境反馈迭代和持久可执行技能库；相较端到端强化学习，它能用较少交互复用代码级技能。"},
    intuition:{en:"Progress can compound if the agent continually selects tasks near its capability frontier and turns successful trajectories into reusable programs.",zh:"若 Agent 持续选择接近能力边界的任务，并把成功轨迹转成可复用程序，能力就可能复利式增长。"},
    rationale:{en:"An automatic curriculum maintains exploration pressure, while a tested skill library prevents the agent from solving the same subproblem repeatedly.",zh:"自动课程保持探索压力，经过测试的技能库则避免反复解决同一子问题。"},
    flow:{en:"Propose a frontier task → plan and execute in Minecraft → use environment feedback for iterative prompting → synthesize and test a skill program → store it for later retrieval.",zh:"提出能力边界任务 → 在 Minecraft 中规划执行 → 根据环境反馈迭代提示 → 合成并测试技能程序 → 存入技能库供后续检索。"},
    validation:{en:"Measure exploration coverage, technology-tree progress, travel distance, and unseen-task performance against prompting, planning, and ablated skill/curriculum variants.",zh:"测量探索覆盖、科技树进度、移动距离和未见任务表现，并与提示、规划以及去除技能／课程的变体比较。"}
  },
  "CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update": {
    problem:{en:"A visual assistant with a fixed tool set can fail when a tool is missing, implemented incorrectly, or invoked under the wrong conditions.",zh:"固定工具集的视觉助手会在工具缺失、实现错误或调用条件不正确时失败。"},
    advantage:{en:"Compared with fixed visual-programming systems, CLOVA can revise tool implementations or usage strategies from execution feedback; compared with full model retraining, updates remain modular.",zh:"相较固定视觉编程系统，CLOVA 可根据执行反馈修订工具实现或调用策略；相较完整模型重训，更新保持模块化。"},
    intuition:{en:"Execution traces expose whether failure comes from planning, tool choice, or tool behavior, making targeted repair possible.",zh:"执行轨迹能够暴露失败来自规划、工具选择还是工具行为，从而支持定向修复。"},
    rationale:{en:"Visual tools have explicit inputs, outputs, and observable effects, so their failures can be diagnosed and tested more directly than opaque model weights.",zh:"视觉工具具有显式输入、输出和可观测效果，因此其失败比不透明模型权重更容易诊断和测试。"},
    flow:{en:"Parse a visual request → compose a tool plan → execute tools → inspect failures and feedback → update tool code or usage policy → rerun the task.",zh:"解析视觉请求 → 组合工具计划 → 执行工具 → 检查失败与反馈 → 更新工具代码或调用策略 → 重新运行任务。"},
    validation:{en:"Evaluate diverse visual reasoning/manipulation tasks, comparing fixed tools, no-update variants, and targeted tool or strategy updates with ablations by failure source.",zh:"在多类视觉推理和操作任务上评测，与固定工具、无更新变体及定向工具／策略更新比较，并按失败来源消融。"}
  },
  "Automated Design of Agentic Systems": {
    problem:{en:"Agent architectures are usually hand-designed, making exploration of prompts, modules, control flow, and multi-agent composition slow and biased by human intuition.",zh:"Agent 架构通常由人工设计，导致对提示词、模块、控制流和多 Agent 组合的探索缓慢且受人工直觉限制。"},
    advantage:{en:"Compared with prompt optimization, ADAS searches entire executable agent programs; compared with one fixed architecture, it maintains an archive of diverse high-performing designs.",zh:"相较提示词优化，ADAS 搜索完整可执行 Agent 程序；相较单一固定架构，它维护多样高性能设计档案。"},
    intuition:{en:"A meta-agent can use language-model code generation and benchmark feedback to propose novel compositions that humans may not enumerate.",zh:"元 Agent 可以结合代码生成和基准反馈，提出人工未必会枚举出的新组合。"},
    rationale:{en:"Agent systems are modular and executable, so candidate designs can be generated, run, scored, and retained in an iterative search loop.",zh:"Agent 系统具有模块化和可执行性，因此候选设计能够被生成、运行、评分并在迭代搜索中保留。"},
    flow:{en:"Describe available primitives and evaluation tasks → let a meta-agent generate agent code → execute and score candidates → add strong/diverse designs to an archive → use the archive to condition later proposals.",zh:"描述可用原语和评测任务 → 让元 Agent 生成 Agent 代码 → 执行并评分候选 → 将强且多样的设计加入档案 → 用档案指导后续提案。"},
    validation:{en:"Compare discovered systems with manually designed agents and search baselines across several benchmarks, testing transfer of discovered architectures and component ablations.",zh:"在多个基准上将发现的系统与人工 Agent 和搜索基线比较，并测试架构迁移及组件消融。"}
  },
  "AFlow: Automating Agentic Workflow Generation": {
    problem:{en:"Choosing and wiring agent operators into a workflow is combinatorial, and manually designed workflows may not transfer across tasks or models.",zh:"选择并连接 Agent 操作器形成工作流是组合优化问题，人工工作流也可能无法跨任务或模型迁移。"},
    advantage:{en:"Compared with fixed workflow templates, AFlow searches workflow structures using execution feedback; compared with unconstrained program generation, modular operators narrow the search space.",zh:"相较固定工作流模板，AFlow 根据执行反馈搜索结构；相较无约束程序生成，模块化操作器缩小搜索空间。"},
    intuition:{en:"Different tasks benefit from different decompositions, evaluator placements, and iteration patterns, so workflow topology should be optimized rather than assumed.",zh:"不同任务适合不同分解方式、评价器位置和迭代模式，因此工作流拓扑应被优化而不是预设。"},
    rationale:{en:"Executable workflows provide a direct task score, allowing search to retain structural choices that repeatedly improve outcomes.",zh:"可执行工作流提供直接任务分数，使搜索能够保留反复改善结果的结构选择。"},
    flow:{en:"Define workflow operators → generate or mutate candidate graphs → execute them on development tasks → score and select promising workflows → iterate and validate on held-out tasks.",zh:"定义工作流操作器 → 生成或变异候选图 → 在开发任务上执行 → 评分并选择有希望的工作流 → 迭代并在留出任务验证。"},
    validation:{en:"Evaluate across reasoning and agent benchmarks against manually designed workflows, prompt-only optimization, and automated agent-design baselines, with operator/topology ablations.",zh:"在推理与 Agent 基准上，与人工工作流、仅提示词优化和自动 Agent 设计基线比较，并消融操作器与拓扑。"}
  },
  "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning": {
    problem:{en:"Web-agent reinforcement learning faces sparse rewards and a fixed task distribution that may be too easy or too hard as the agent changes.",zh:"Web Agent 强化学习面临稀疏奖励，而且固定任务分布会随着 Agent 能力变化而变得过易或过难。"},
    advantage:{en:"Compared with static curricula, WebRL updates task selection from current experience; compared with imitation-only training, it optimizes behavior using environment outcomes.",zh:"相较静态课程，WebRL 根据当前经验更新任务选择；相较仅模仿训练，它利用环境结果优化行为。"},
    intuition:{en:"Training is most efficient when the curriculum tracks the agent's evolving competence and emphasizes tasks near the learning frontier.",zh:"当课程跟随 Agent 不断变化的能力，并强调学习边界附近任务时，训练最有效。"},
    rationale:{en:"Online success/failure statistics reveal which tasks are informative at each stage, turning environment interaction into both policy and curriculum feedback.",zh:"在线成功／失败统计揭示每阶段最有信息量的任务，使环境交互同时成为策略和课程反馈。"},
    flow:{en:"Collect web trajectories and rewards → estimate task difficulty/value → update the online curriculum → train the web policy with reinforcement learning → repeat as competence changes.",zh:"收集网页轨迹与奖励 → 估计任务难度和价值 → 更新在线课程 → 用强化学习训练网页策略 → 随能力变化重复。"},
    validation:{en:"Test on interactive web benchmarks, comparing fixed curricula, imitation learning, standard RL, and curriculum ablations through success, sample efficiency, and generalization.",zh:"在交互网页基准上测试，与固定课程、模仿学习、标准强化学习及课程消融比较成功率、样本效率和泛化。"}
  },
  "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning": {
    problem:{en:"Visual self-correction is often judged only by whether the final answer changes, hiding whether the model identified the actual reasoning or grounding error.",zh:"视觉自纠错常只看最终答案是否改变，无法判断模型是否真正定位推理或 Grounding 错误。"},
    advantage:{en:"Compared with answer-level correction benchmarks, VISCO separates error localization, critique quality, and correction; compared with text-only critique, it requires visual evidence.",zh:"相较答案级纠错基准，VISCO 分离错误定位、批评质量和修正；相较纯文本批评，它要求依赖视觉证据。"},
    intuition:{en:"Reliable improvement requires first identifying which visual evidence or reasoning step is wrong before attempting a corrected answer.",zh:"可靠改进需要先识别错误的视觉证据或推理步骤，再尝试给出修正答案。"},
    rationale:{en:"Fine-grained annotations and controlled error cases make critique failures measurable instead of conflating them with final-answer accuracy.",zh:"细粒度标注和受控错误案例使 Critique 失败可以被单独测量，而不与最终答案准确率混在一起。"},
    flow:{en:"Construct visual questions with annotated reasoning errors → ask models to locate and explain the error → request a correction → score critique and corrected reasoning separately.",zh:"构造带标注推理错误的视觉问题 → 要求模型定位并解释错误 → 请求修正 → 分别评价 Critique 和修正后的推理。"},
    validation:{en:"Benchmark multiple VLMs and prompting/critic strategies on localization, critique, and correction metrics, including analyses of error type and visual grounding.",zh:"用定位、批评和修正指标评测多种 VLM 与提示／Critic 策略，并分析错误类型和视觉 Grounding。"}
  },
  "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning": {
    problem:{en:"A VLM that critiques itself may reproduce the same perceptual and reasoning blind spots that caused its original answer.",zh:"让 VLM 自我批评可能复现造成原始答案的同一感知与推理盲点。"},
    advantage:{en:"Compared with self-critique, Critic-V uses a dedicated critic role or model; compared with answer-only supervision, it provides localized corrective signals.",zh:"相较自我批评，Critic-V 使用专门 Critic 角色或模型；相较仅答案监督，它提供局部纠正信号。"},
    intuition:{en:"Separating solver and critic objectives can create complementary error detection, especially when the critic is trained on explicit multimodal failure examples.",zh:"分离求解器和 Critic 目标可以形成互补错误检测，尤其当 Critic 经过显式多模态失败样本训练时。"},
    rationale:{en:"A specialized evaluator can spend capacity on checking visual evidence and reasoning consistency rather than simultaneously producing the answer.",zh:"专门评价器可把容量用于检查视觉证据和推理一致性，而无需同时承担答案生成。"},
    flow:{en:"Generate a multimodal solution → pass the problem, evidence, and trace to a VLM critic → identify and explain errors → feed corrective supervision back to the solver → regenerate or train.",zh:"生成多模态解答 → 将问题、证据和轨迹交给 VLM Critic → 识别并解释错误 → 把纠正监督反馈给求解器 → 重新生成或训练。"},
    validation:{en:"Compare multimodal reasoning accuracy and error detection against no-critic, self-critic, and alternative evaluator baselines, with critic and feedback ablations.",zh:"在多模态推理准确率和错误检测上，与无 Critic、自 Critic 和其他评价器比较，并消融 Critic 与反馈。"}
  },
  "Visual Agentic AI for Spatial Reasoning with a Dynamic API": {
    problem:{en:"Fixed visual APIs cannot anticipate every spatial operation required by varied reasoning tasks, while direct VLM reasoning can be brittle on precise geometry.",zh:"固定视觉 API 无法预先覆盖各种空间推理所需操作，而 VLM 直接推理在精确几何上可能不稳定。"},
    advantage:{en:"Compared with a fixed tool library, a dynamic API can expose task-specific operations; compared with end-to-end verbal reasoning, explicit spatial tools produce inspectable intermediate results.",zh:"相较固定工具库，动态 API 可提供任务特定操作；相较端到端语言推理，显式空间工具产生可检查中间结果。"},
    intuition:{en:"Complex spatial questions can be decomposed into a small sequence of executable perceptual and geometric primitives selected for the current task.",zh:"复杂空间问题可以分解为针对当前任务选择的一小组可执行感知与几何原语。"},
    rationale:{en:"External operations make coordinates, regions, and relations explicit, reducing the need for the VLM to represent precise spatial computation only in hidden states.",zh:"外部操作显式表示坐标、区域和关系，减少 VLM 仅在隐藏状态中完成精确空间计算的压力。"},
    flow:{en:"Parse the spatial question → expose or compose relevant API operations → execute operations on the image → feed structured results back to the agent → synthesize the answer.",zh:"解析空间问题 → 暴露或组合相关 API 操作 → 在图像上执行 → 将结构化结果反馈给 Agent → 综合答案。"},
    validation:{en:"Evaluate spatial-reasoning datasets against direct VLM prompting and fixed-tool systems, with ablations for API composition, operation choice, and intermediate feedback.",zh:"在空间推理数据集上与 VLM 直接提示及固定工具系统比较，并消融 API 组合、操作选择和中间反馈。"}
  },
  "VisPlay: Self-Evolving Vision-Language Models": {
    problem:{en:"Large collections of unlabeled images are difficult to convert into challenging, useful supervision for improving vision-language reasoning.",zh:"大量无标注图像难以转化为具有挑战性且真正有用的视觉语言推理监督。"},
    advantage:{en:"Compared with fixed synthetic-question generation, VisPlay co-adapts a questioner and solver; compared with externally labeled data, it generates supervision directly from unlabeled images.",zh:"相较固定合成提问，VisPlay 让提问者与求解器共同适应；相较外部标注数据，它直接从无标注图像生成监督。"},
    intuition:{en:"A questioner rewarded for difficulty and diversity can continually generate tasks near the solver's current capability frontier.",zh:"若提问者因难度与多样性获得奖励，它就能持续生成接近求解器当前能力边界的任务。"},
    rationale:{en:"Questioner–solver self-play creates an endogenous curriculum: solver progress changes which questions are informative, which in turn changes future training data.",zh:"提问者—求解器自博弈形成内生课程：求解器进步会改变有信息量的问题，进而改变后续训练数据。"},
    flow:{en:"Sample an unlabeled image → questioner proposes visual questions → solver answers → score difficulty, validity, and diversity → select data → update questioner and solver iteratively.",zh:"采样无标注图像 → 提问者生成视觉问题 → 求解器回答 → 评价难度、有效性和多样性 → 筛选数据 → 迭代更新提问者与求解器。"},
    validation:{en:"Measure gains on multimodal reasoning benchmarks against fixed synthetic data, self-training, and no-self-play baselines, with questioner/reward/data-selection ablations.",zh:"在多模态推理基准上，与固定合成数据、自训练和无自博弈基线比较，并消融提问者、奖励和数据选择。"}
  },
  "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding": {
    problem:{en:"Long-video reasoning generates lengthy, fragmented tool trajectories that are costly to repeat and difficult to transfer across videos.",zh:"长视频推理产生冗长、碎片化的工具轨迹，重复执行成本高，也难以跨视频迁移。"},
    advantage:{en:"Compared with fixed tool chains, META consolidates successful trajectories into reusable macro-tools; compared with storing raw traces, it creates shorter executable abstractions.",zh:"相较固定工具链，META 把成功轨迹巩固为可复用宏工具；相较保存原始轨迹，它形成更短的可执行抽象。"},
    intuition:{en:"Repeated tool subsequences encode stable reasoning procedures that can be compressed and adapted to new long-video tasks.",zh:"反复出现的工具子序列编码稳定推理流程，可以被压缩并适配到新的长视频任务。"},
    rationale:{en:"Macro-tools reduce planning horizon and execution cost while preserving the observable intermediate operations needed for debugging.",zh:"宏工具缩短规划时域和执行成本，同时保留调试所需的可观测中间操作。"},
    flow:{en:"Collect successful long-video tool trajectories → identify reusable subsequences → synthesize macro-tools → adapt/select them for new videos → update the library from new outcomes.",zh:"收集成功的长视频工具轨迹 → 识别可复用子序列 → 合成宏工具 → 在新视频中适配／选择 → 根据新结果更新工具库。"},
    validation:{en:"Evaluate long-video understanding accuracy, tool calls, latency, and transfer against raw trajectory reuse and fixed tool pipelines, with macro-tool construction ablations.",zh:"评测长视频理解准确率、工具调用、延迟和迁移，并与原始轨迹复用及固定工具流程比较，消融宏工具构建。"}
  },
  "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval": {
    problem:{en:"Static retrieval graphs become incomplete or stale as multimodal evidence and reasoning needs change, and ordinary pairwise graphs may miss higher-order relations.",zh:"随着多模态证据和推理需求变化，静态检索图会不完整或过期，普通二元图也可能遗漏高阶关系。"},
    advantage:{en:"Compared with static GraphRAG, EvoGraph-R1 edits its graph from retrieval and reasoning feedback; compared with simple vector memory, hyperedges represent multi-entity multimodal relations.",zh:"相较静态 GraphRAG，EvoGraph-R1 根据检索与推理反馈编辑图；相较简单向量记忆，超边可表示多实体多模态关系。"},
    intuition:{en:"Retrieval successes and failures reveal which nodes, relations, or hyperedges should be added, revised, or removed.",zh:"检索成功与失败能够揭示哪些节点、关系或超边应被新增、修订或删除。"},
    rationale:{en:"An explicit graph provides editable structure and provenance, allowing feedback to change the knowledge organization rather than only the query embedding.",zh:"显式图结构可编辑且可溯源，使反馈能够改变知识组织，而不仅是改变查询嵌入。"},
    flow:{en:"Extract multimodal entities and relations → build a knowledge hypergraph → retrieve subgraphs for a query → reason and score outcomes → edit graph structure from feedback → repeat.",zh:"提取多模态实体与关系 → 构建知识超图 → 为查询检索子图 → 推理并评价结果 → 根据反馈编辑图结构 → 重复迭代。"},
    validation:{en:"Compare multimodal retrieval and reasoning against vector retrieval and static graph baselines, measuring answer quality, retrieval quality, and graph-edit ablations.",zh:"在多模态检索与推理上与向量检索和静态图基线比较，测量答案质量、检索质量并消融图编辑。"}
  },
  "History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation": {
    problem:{en:"Zero-shot vision-language navigation agents often treat each episode independently and fail to reuse prior routes or anticipate future states.",zh:"零样本视觉语言导航 Agent 常把每个回合独立处理，无法复用历史路线或预判未来状态。"},
    advantage:{en:"Compared with memoryless navigation, the method reuses prior experience; compared with history-only memory, future-oriented thought explicitly evaluates likely next states and actions.",zh:"相较无记忆导航，该方法复用历史经验；相较仅历史记忆，它通过未来导向思考显式评估可能的后续状态与动作。"},
    intuition:{en:"Past navigation episodes contain reusable spatial and action patterns, while imagined future consequences help select among currently plausible actions.",zh:"历史导航回合包含可复用空间与动作模式，对未来结果的想象则帮助在当前可行动作中选择。"},
    rationale:{en:"Combining retrieval of similar experience with forward-looking reasoning can reduce repeated mistakes without requiring task-specific parameter training.",zh:"将相似经验检索与前瞻推理结合，可在无需任务专属参数训练时减少重复错误。"},
    flow:{en:"Encode the current observation and instruction → retrieve relevant historical experience → generate future-oriented candidate thoughts → score/select an action → store new trajectory evidence for later episodes.",zh:"编码当前观察与指令 → 检索相关历史经验 → 生成面向未来的候选思考 → 评分并选择动作 → 保存新轨迹证据供后续回合使用。"},
    validation:{en:"Evaluate zero-shot navigation success and path efficiency on vision-language navigation benchmarks against memoryless, retrieval-only, and planning baselines, with history/future-thought ablations.",zh:"在视觉语言导航基准上评测零样本成功率和路径效率，并与无记忆、仅检索和规划基线比较，消融历史与未来思考。"}
  }
};
