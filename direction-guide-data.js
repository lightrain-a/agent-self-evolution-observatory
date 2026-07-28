window.DIRECTION_GUIDE = {
  macroGroups:[
    {
      id:"learn", code:"Q1", title:{en:"What should the agent learn?",zh:"Agent 到底应该学什么？"},
      plain:{en:"First decide whether an experience is trustworthy and useful, then check whether learning it produced hidden harm.",zh:"先判断一段经验是否可信、是否值得学，再检查学完之后有没有产生隐藏伤害。"},
      directionIds:["experience-admission","negative-evaluation"]
    },
    {
      id:"commit", code:"Q2", title:{en:"What should the experience become?",zh:"经验应该变成什么？"},
      plain:{en:"A useful lesson may become memory, a reusable skill, a tool, a workflow rule, or a model update; these forms have different costs and risks.",zh:"有用经验可以变成记忆、可复用技能、工具、工作流规则或模型更新，不同形式的成本和风险完全不同。"},
      directionIds:["memory-lifecycle","skill-tool-lifecycle","system-composition"]
    },
    {
      id:"adapt", code:"Q3", title:{en:"What is changing around the agent?",zh:"Agent 周围到底发生了什么变化？"},
      plain:{en:"The body, environment, user, objective, or other agents may change; the system must identify the source before adapting.",zh:"身体、环境、用户、目标或其他 Agent 都可能变化，系统必须先分清变化来源再适应。"},
      directionIds:["embodied-world","adaptive-objectives","collective-evolution"]
    },
    {
      id:"govern", code:"Q4", title:{en:"How can evolution remain safe and affordable?",zh:"怎样让进化保持安全、可控且负担得起？"},
      plain:{en:"Persistent updates need provenance, security checks, rollback, compute budgeting, and limited human oversight.",zh:"持久更新需要溯源、安全检查、回滚、算力预算与有限人工监督。"},
      directionIds:["security-provenance","governance-control"]
    }
  ],
  runningExample:{
    title:{en:"One running example: a GUI agent learns “the Submit button is at the bottom right”",zh:"贯穿案例：GUI Agent 学到“提交按钮在右下角”"},
    intro:{en:"The same event leads to ten different research questions. The directions are not ten competing methods; they study different parts of the evolution lifecycle.",zh:"同一件事可以引出十个不同研究问题。这十个方向不是十种互相竞争的方法，而是在研究自进化生命周期的不同环节。"}
  },
  directions:{
    "experience-admission":{
      plain:{en:"Decide whether a lesson deserves to enter long-term state and where it is valid.",zh:"判断一条经验该不该进入长期状态，以及它在哪些条件下才有效。"},
      object:{en:"Candidate experience and its applicability boundary",zh:"候选经验及其适用边界"},
      example:{en:"Was success really caused by the button location? Does the lesson still hold on another layout or screen size?",zh:"成功真的是因为按钮位置吗？换布局、分辨率后这条经验还成立吗？"},
      distinction:{en:"It acts before or at admission; it does not decide the final memory format or defend the entire update supply chain.",zh:"它研究经验进入系统前后的准入，不负责选择最终记忆形式，也不覆盖整条安全供应链。"}
    },
    "memory-lifecycle":{
      plain:{en:"Keep stored experience useful as facts, scenes, and task conditions change.",zh:"让已经存下来的经验在事实、场景和任务条件变化后仍然可用。"},
      object:{en:"Memory representation, freshness, consolidation, and deletion",zh:"记忆表示、新鲜度、巩固与删除"},
      example:{en:"Should the agent store a screenshot, a crop, a text rule, or a graph relation? When the UI changes, which part should be repaired?",zh:"Agent 应保存整张截图、局部裁剪、文本规则还是图关系？界面变化后究竟修哪一部分？"},
      distinction:{en:"It assumes a lesson has been accepted and studies how to represent and maintain it; admission is handled by D1.",zh:"它假设经验已经被接受，研究如何表示和维护；是否准入由 D1 处理。"}
    },
    "skill-tool-lifecycle":{
      plain:{en:"Turn repeated experience into executable capability and manage that capability across versions.",zh:"把重复经验变成可执行能力，并管理能力的版本、验证、权限与退役。"},
      object:{en:"Reusable skill/tool artifact, contract, and authorization",zh:"可复用技能／工具产物、契约与授权"},
      example:{en:"The agent creates a “submit-form” skill. What are its preconditions? What permissions does it need? What happens when the website changes?",zh:"Agent 创建“提交表单”技能。它的前置条件是什么？需要什么权限？网站变化后怎样修复或退役？"},
      distinction:{en:"Memory records what happened; a skill or tool executes a reusable procedure and therefore introduces stronger interface and permission risks.",zh:"记忆记录发生了什么；技能或工具会执行可复用过程，因此带来更强的接口与权限风险。"}
    },
    "system-composition":{
      plain:{en:"Choose which component to update and ensure separately evolved components still work together.",zh:"选择应该更新哪个组件，并保证分别进化的组件组合后仍然能工作。"},
      object:{en:"Update route, cross-component semantics, and interaction effects",zh:"更新路由、跨组件语义与交互效应"},
      example:{en:"Should the lesson update memory, a skill, the planner, or LoRA? If the vision module changes coordinates, will the old click tool still understand them?",zh:"这条经验应更新记忆、技能、规划器还是 LoRA？视觉模块改了坐标定义后，旧点击工具还能理解吗？"},
      distinction:{en:"It studies relations among update surfaces, whereas D2 and D3 study the local lifecycle of one surface.",zh:"它研究不同更新表面之间的关系；D2、D3 主要研究单个表面的局部生命周期。"}
    },
    "embodied-world":{
      plain:{en:"Adapt when the observed world, sensor, body, dynamics, or available viewpoint changes.",zh:"当环境、传感器、身体、动力学或可观察视角变化时进行适应。"},
      object:{en:"Embodiment calibration, active observation, and world-model fragments",zh:"具身标定、主动观察与局部世界模型"},
      example:{en:"The button moved because the page changed, or the cursor is offset because the screen scale changed. Which kind of change occurred?",zh:"按钮移动可能是页面变了，也可能是屏幕缩放导致光标偏移。到底是哪一种变化？"},
      distinction:{en:"The main uncertainty comes from the external or physical world; D9 instead focuses on changing users, goals, and deployment-induced data.",zh:"它的核心不确定性来自外部或物理世界；D9 关注用户、目标和部署自身造成的数据变化。"}
    },
    "negative-evaluation":{
      plain:{en:"Measure cases where the agent appears better on average but has actually evolved in a harmful way.",zh:"测量“平均表现看似更好，但实际上发生了有害进化”的情况。"},
      object:{en:"Version trajectories, hidden regressions, evaluator failure, and recovery",zh:"版本轨迹、隐性回退、评价器失败与恢复"},
      example:{en:"The new lesson improves one form but causes wrong clicks on many old layouts. Final average success hides the damage.",zh:"新经验让一种表单更好，却让很多旧布局出现误点击；最终平均成功率可能掩盖伤害。"},
      distinction:{en:"It is primarily a measurement and benchmark direction; D7 develops mechanisms that prevent or contain the harm.",zh:"它首先是测量与基准方向；D7 研究如何预防或遏制这些伤害。"}
    },
    "security-provenance":{
      plain:{en:"Track where updates came from and stop poisoned or uncertain knowledge from spreading through descendants.",zh:"追踪更新来自哪里，并阻止投毒或不确定知识沿后代版本传播。"},
      object:{en:"Evidence-to-artifact lineage, poisoning channel, propagation graph, and rollback",zh:"证据到产物的谱系、投毒通道、传播图与回滚"},
      example:{en:"A malicious page teaches a false button rule, which becomes memory, then a skill, then is shared to other agents. How do we locate and remove every descendant?",zh:"恶意网页教出错误按钮规则，随后变成记忆、技能并共享给其他 Agent。如何定位并删除所有派生产物？"},
      distinction:{en:"It secures the persistent-update supply chain; D6 only tells us that harmful evolution occurred, and D8 decides how much resource to spend checking it.",zh:"它保护持久更新供应链；D6 负责发现伤害，D8 决定投入多少资源进行检查。"}
    },
    "governance-control":{
      plain:{en:"Decide when evolution is worth the compute or human attention and when the system should stop, defer, or escalate.",zh:"决定一次进化是否值得消耗算力或人工注意力，以及何时停止、延迟或升级审查。"},
      object:{en:"Evolution controller, budget allocation, review queue, and stopping rule",zh:"进化控制器、预算分配、审查队列与停止规则"},
      example:{en:"Should every new button location trigger expensive replay and human review, or only high-risk, recurring cases?",zh:"每个新按钮位置都要做昂贵重放和人工审查，还是只处理高风险、重复出现的情况？"},
      distinction:{en:"It allocates scarce resources across other directions rather than defining the memory, skill, or security mechanism itself.",zh:"它为其他方向分配稀缺资源，而不是直接定义记忆、技能或安全机制。"}
    },
    "adaptive-objectives":{
      plain:{en:"Adapt goals and user models when preferences change or the agent's own actions change future data.",zh:"当用户偏好变化，或 Agent 自身行为改变未来数据时，适应目标与用户模型。"},
      object:{en:"User preference, goal hierarchy, external drift, and performative feedback",zh:"用户偏好、目标层级、外部漂移与自致反馈"},
      example:{en:"A user now prefers keyboard submission, or the agent's repeated clicks cause the website to personalize the layout. Is this user drift, environment drift, or agent-induced change?",zh:"用户现在偏好键盘提交，或 Agent 反复点击让网站个性化了布局。这是用户变化、环境变化，还是 Agent 自己造成的变化？"},
      distinction:{en:"It studies what the agent should optimize and how deployment changes data; D5 focuses on physical/world state and D8 on resource policy.",zh:"它研究 Agent 应优化什么、部署如何改变数据；D5 关注物理／世界状态，D8 关注资源策略。"}
    },
    "collective-evolution":{
      plain:{en:"Share, branch, merge, and route persistent knowledge across multiple heterogeneous agents.",zh:"在多个异构 Agent 之间共享、分支、合并与路由持久知识。"},
      object:{en:"Cross-agent transfer unit, compatibility, lineage portfolio, and specialization",zh:"跨 Agent 迁移单元、兼容性、谱系组合与专门化"},
      example:{en:"Can a browser agent's form-submission lesson help a mobile agent? Should one universal agent absorb it, or should separate specialist versions be kept?",zh:"浏览器 Agent 的表单提交经验能否帮助移动端 Agent？应合并进一个通用 Agent，还是保留不同专家版本？"},
      distinction:{en:"It concerns persistent learning across agents and versions, not one-shot multi-agent voting or ordinary ensemble inference.",zh:"它研究跨 Agent 与版本的持久学习，不是一次性多 Agent 投票或普通推理集成。"}
    }
  }
};
