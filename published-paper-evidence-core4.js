window.PUBLISHED_PAPER_EVIDENCE = Object.assign(window.PUBLISHED_PAPER_EVIDENCE || {}, {
  "META: Meta Evolution of Tool Trajectory Adaptation for Long-Video Understanding": {
    simple:{zh:"每个长视频问题都重新串 micro-tools：定位帧、OCR、VQA、时序比较等步骤一次性生成，用完即丢；同样的多步模式下次继续重建。",en:"Rebuild a chain of micro-tools for every long-video query, discarding repeated multi-step patterns after use."},
    observed:{zh:"CVPR 2026 正式摘要：META 不更新模型参数，而是从成功 tool trajectory 抽 macro-tool、从失败轨迹提 failure prior，再做 symbolic consolidation / pruning；在长视频 benchmark 上达到 SOTA。正式摘要未给单一汇总百分点。",en:"The CVPR 2026 abstract reports training-free macro-tool extraction from successful trajectories, failure-prior distillation, and symbolic consolidation/pruning, reaching SOTA on long-video benchmarks without parameter updates; no single aggregate margin is stated."},
    proved:{zh:"说明可复用的“工具调用子程序”本身可以成为持久进化对象，并通过压缩与剪枝缩短后续推理路径。",en:"It supports reusable tool-call subsequences as a persistent evolution object that can shorten later reasoning through consolidation and pruning."},
    notProved:{zh:"长视频工具轨迹的成功不等于任意 API 都可安全自动组合；macro-tool 的权限、版本兼容和跨环境失效仍需额外治理。",en:"Long-video success does not establish permission-safe arbitrary API composition, version compatibility, or cross-environment validity."},
    source:{zh:"已核：CVPR 2026 Open Access 正式摘要",en:"Checked: CVPR 2026 Open Access"}
  },
  "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval": {
    simple:{zh:"静态 GraphRAG：离线把文档抽成图，查询时只检索已有子图；图里缺事实、关系错了或需要外部新证据时，查询过程本身不会修图。",en:"Static GraphRAG builds a graph offline and only retrieves from it; missing facts or wrong relations are not repaired during a query."},
    observed:{zh:"CVPR 2026 正式摘要：EvoGraph-R1 把检索建模成 MDP，Agent 可 GraphRetrieve、WebSearch、GraphEdit、Answer；在 multimodal VQA 与 text QA 上相对 RAG、GraphRAG、search-augmented baseline 提升 accuracy、coverage 和 traceability，并报告 SOTA。摘要未给单一统一百分点。",en:"CVPR 2026 formulates retrieval as an MDP with GraphRetrieve, WebSearch, GraphEdit, and Answer; it reports gains over RAG/GraphRAG/search baselines in accuracy, coverage, and traceability on multimodal VQA and text QA, without one aggregate margin in the abstract."},
    proved:{zh:"说明知识图可以从“只读索引”变成 Agent 可边推理边修改的环境，新增证据、纠错、剪噪都进入同一个闭环。",en:"It supports treating the graph as an editable reasoning environment rather than a read-only index, unifying evidence addition, correction, pruning, and answering."},
    notProved:{zh:"query-specific graph evolution 是否会长期污染共享知识库、不同问题之间怎样隔离编辑，并没有被 accuracy / SOTA 自动解决。",en:"Accuracy/SOTA does not automatically solve long-term shared-graph contamination or isolation of edits across queries."},
    source:{zh:"已核：CVPR 2026 Open Access / EvoGraph-R1 项目",en:"Checked: CVPR 2026 Open Access / project page"}
  },
  "Learning to Adapt: Self-Improving Web Agent via Cognitive-Aware Exploration": {
    simple:{zh:"人工执行 pipeline + 专家轨迹：开发者规定网页探索/规划流程，再收大量成功 demonstration 教 Agent；Agent 自己不知道当前能力缺口在哪里。",en:"Use a handcrafted execution pipeline plus expensive expert trajectories; the agent does not autonomously locate its current cognitive gaps."},
    observed:{zh:"CVPR 2026 的 SCALE 用 Selector、Predictor、Judger 三个对抗角色主动找能力缺口，并用 SCALE-Hop 做全局图探索；最终从 19 个真实网站收集 SCALE-20k 结构化 demonstration，正式摘要报告多种 MLLM 在多类网页环境中的 performance 与 generalization 均显著提高。摘要没有单一统一百分点。",en:"CVPR 2026 uses Selector, Predictor, Judger plus SCALE-Hop, collecting SCALE-20k from 19 real websites; the abstract reports significant performance and generalization gains across multiple MLLMs and web environments, without one aggregate margin."},
    proved:{zh:"说明探索任务本身可以由 Agent 的“当前能力缺口”驱动，而不是只靠人工课程或专家轨迹。",en:"It supports driving exploration from the agent's detected capability gaps rather than only human curricula or expert trajectories."},
    notProved:{zh:"SCALE-20k 仍是收集后训练/适配的数据闭环；对网站长期漂移、不可逆动作和部署时更新门控仍不能直接推出结论。",en:"SCALE-20k remains a collected training/adaptation loop and does not itself establish deployment-time gates for drift or irreversible web actions."},
    source:{zh:"已核：CVPR 2026 Open Access 正式摘要",en:"Checked: CVPR 2026 Open Access"}
  },
  "History to Future: Evolving Agent with Experience and Thought for Zero-shot Vision-and-Language Navigation": {
    simple:{zh:"当前步 naive reasoning：只看当前图像、指令和有限历史决定下一步；失败任务不会系统总结成经验，也不显式预测未来 landmark / 动作。",en:"Naive current-step reasoning uses the current observation/instruction with limited history, without structured failure experience or explicit future landmark/action prediction."},
    observed:{zh:"CVPR 2026 的 EvoNav 同时加入 Future CoT 与 History CoE。论文报告相对对照方法约 +20% SR、+21% OSR、+17% SPL，并在 simulator 与 real-world VLN-CE 都验证。",en:"CVPR 2026 combines Future CoT and History CoE and reports about +20% SR, +21% OSR, and +17% SPL over counterparts, with simulator and real-world VLN-CE evaluation."},
    proved:{zh:"说明“回看历史失败 + 预测未来行动/landmark”可以联合改善零样本导航决策，而不是只靠当前 observation 做反应式选择。",en:"It supports combining retrospective trajectory experience with prospective action/landmark reasoning for stronger zero-shot navigation decisions."},
    notProved:{zh:"H-CoE 是导航经验，不等于通用长期 memory lifecycle；这些增益也不能直接外推到工具调用或不同动力学机器人。",en:"H-CoE is navigation-specific experience, not a general memory lifecycle, and the gains do not directly transfer to tool agents or different robot dynamics."},
    source:{zh:"已核：CVPR 2026 正式版 / 项目结果",en:"Checked: CVPR 2026 publication / project results"}
  },
  "Phoenix: A Motion-based Self-Reflection Framework for Fine-grained Robotic Action Correction": {
    simple:{zh:"高层 subgoal self-reflection：失败后只说“应该把杯子放到机器下方”这类语义目标，再让原低层 policy 自己想具体位移；高层诊断和毫米级动作之间有落差。",en:"High-level subgoal reflection says what should be achieved but leaves the original low-level policy to infer precise corrective motion."},
    observed:{zh:"CVPR 2025：9 个 RoboMimic 任务平均 success，Phoenix 57.8%，subgoal self-reflection 48.0%，无 self-correction 的 motion-conditioned 46.9%。真实 drawer-open 中，in-distribution 为 75% vs 60%，pose disruption 为 55% vs 35%；交互学习后 in-distribution 可从 60% 提到 75%。",en:"CVPR 2025 reports 57.8% average success across nine RoboMimic tasks versus 48.0% subgoal self-reflection and 46.9% motion-conditioned without correction. In real drawer opening it reaches 75% vs 60% in-distribution and 55% vs 35% under pose disruption."},
    proved:{zh:"说明把 semantic reflection 先转成 motion instruction，再由 motion-conditioned diffusion policy 输出高频动作，能弥合“知道错在哪”和“具体怎么修动作”的距离。",en:"It supports using motion instructions as a bridge from semantic reflection to high-frequency action correction via a motion-conditioned diffusion policy."},
    notProved:{zh:"仍需要专家/纠错轨迹训练低层策略，真实世界任务规模有限；不能直接推出完全自主、开放世界的 lifelong robot evolution。",en:"It still relies on expert/correction trajectories and limited real-world tasks, so it does not establish fully autonomous open-world lifelong robot evolution."},
    source:{zh:"已核：CVPR 2025 正式页面 / 项目实验",en:"Checked: CVPR 2025 proceedings / project experiments"}
  }
});
