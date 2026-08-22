window.PAPER_EXTERNAL_REVIEW = {
  schema_version:"1.0",
  source:"Stanford Agentic Reviewer · paperreview.ai",
  verified_at:"2026-08-22",
  venue:"ICLR",
  policy:{
    read_only_external_review_overlay:true,
    score_is_not_official_iclr_score:true,
    reviewer_text_is_summarized_not_republished:true,
    tokens_and_email_are_private:true,
    cannot_change_paper_state:true,
    cannot_change_scientific_state:true,
    cannot_grant_experiment_or_gpu_authority:true,
    cannot_grant_submission_authority:true
  },
  repair_priority:[
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
    "STRI",
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
    "AGENT-SAFETY-R9",
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
  ],
  papers:{
    "STRI":{
      score:5.8,
      recommendation:{zh:"Weak Accept · 弱接收倾向",en:"Weak Accept"},
      verdict_tone:"weak_accept",
      burden:{zh:"低–中",en:"LOW–MEDIUM"},
      repair_priority:"P2",
      reviewer_take:{zh:"Reviewer 认可 representation-invariance 这个问题本身、R*(A) 的精确诊断价值和正/负机制证据；主要担心控制类范围较窄、数学工具本身较标准，以及缺少 downstream utility。",en:"The reviewer accepts the representation-invariance question, the exact diagnostic value of R*(A), and the positive/negative mechanism evidence. Main concerns are scope of the audited controller class, standard mathematical machinery, and limited downstream utility evidence."},
      strengths:{zh:["把技能 packaging 引起的 representation-dependent control 明确成一个可审计的系统不变量问题。","R*(A) 精确 certificate、factor-2 witness 和 Level-1 / Level-3 / logical-compiler 正负边界共同支持“support geometry 而不是 overlap prevalence”。","使用一手 validator/compiler 冻结 support truth，SkillRL fresh-ID witness 提供独立 identity sensitivity 证据。"],en:["Frames packaging-induced representation dependence as an auditable systems invariant.","R*(A), the factor-2 witness, and positive/negative regimes support support geometry rather than overlap prevalence.","First-party validators freeze support truth and SkillRL provides an independent identity-sensitivity witness."]},
      concerns:{zh:["certificate 只覆盖 package-only、pre-task、nonnegative additive exposure；需要更清楚说明它在真实 controller 版图中的位置。","Theorem 的数学工具较标准；论文不能把 LP / cone feasibility 本身卖成主要理论创新。","缺少 end-to-end utility；SkillRL 只有 12 个技能，且还可补 synthetic split/merge、solver/tolerance、uncovered-row robustness。"],en:["The certificate covers a restricted package-only pre-task additive controller class.","The mathematical tools are standard; LP/cone feasibility should not be sold as the main theoretical novelty.","End-to-end utility is absent and the SkillRL witness is small; synthetic repackaging and solver/coverage robustness would help."]},
      reviewer_questions:{zh:["uncovered row、solver tolerance、degeneracy 与 R* stability 如何处理？","fresh-ID clone 是否真的只改 ID；能否做纯 rename ablation？","能否做 semantics-preserving synthetic split/merge，以及 support-pattern / semantic-cell mitigation demo？"],en:["How are uncovered rows, solver tolerance, degeneracy, and R* stability handled?","Are fresh-ID clones identical except for IDs, and can a pure rename ablation be shown?","Can synthetic semantics-preserving split/merge and a support-pattern/semantic-cell mitigation be demonstrated?"]},
      repair:{
        manuscript:{zh:["把主贡献重写成 new systems invariant + exact audit object，而不是新 LP 算法。","补 exposure fairness / ranking fairness / matrix balancing / Farkas-cone 相关工作，并明确差异。","主文补 uncovered rows、solver/tolerance/runtime 和 scope box；清理格式/图表 artifacts。"],en:["Reposition around a new systems invariant and audit object rather than LP novelty.","Add exposure-fairness, matrix-balancing, and cone-feasibility context.","Clarify uncovered rows, solver/tolerance/runtime, scope, and presentation artifacts."]},
        analysis:{zh:["在冻结 support matrix 上做 synthetic split/merge、column perturbation 与 validator/dedup sensitivity；不需要新 GPU。","如果现有 SkillRL artifact 足够，补纯 ID rename / budget sensitivity。"],en:["Run synthetic split/merge and support perturbation sensitivity on frozen matrices without new GPU work.","If existing SkillRL artifacts suffice, add pure-ID rename and budget sensitivity."]},
        experiment:{zh:["只考虑一个小型 semantic-cell/support-pattern mitigation demo；优先复用现有 released artifacts。","不要为了追 Reviewer 分数重开此前已经失败的 dynamic P0 大实验。"],en:["Consider only a small semantic-cell/support-pattern mitigation demo using released artifacts when possible.","Do not reopen the failed dynamic P0 lane merely to chase review score."]}
      }
    },
    "AGENT-SAFETY-R9":{
      score:6.5,
      recommendation:{zh:"Weak Reject · 主会弱拒（数值与文字倾向不一致）",en:"Weak Reject for main track (numerical/textual inconsistency)"},
      verdict_tone:"weak_reject",
      burden:{zh:"高",en:"HIGH"},
      repair_priority:"P4",
      reviewer_take:{zh:"Reviewer 认可“static pass ≠ temporal certificate”、same-schedule paired control 和 first-violation framing；拒稿倾向主要来自 small-N、单 evaluator、短 horizon 和缺 NullMemory，而不是主问题不成立。",en:"The reviewer accepts the static-pass versus temporal-certificate question, same-schedule paired control, and first-violation framing. The weak-reject leaning is driven mainly by scale, single-evaluator measurement, short horizon, and missing NullMemory rather than rejection of the scientific question."},
      strengths:{zh:["0/12 当前 clean 与未来 first-violation 的逻辑反例直接支持主命题。","同 schedule、step-0 workflow fixed 的配对控制把 update-associated contrast 局部化得很清楚。","first-event / horizon 表达和固定 probe snapshot panel 对长期安全评测方法有直接复用价值。"],en:["The 0/12 current-clean versus future first-violation contrast directly tests the central implication.","The same-schedule step-0-workflow control localizes an update-associated contrast.","First-event timing and fixed-probe snapshots provide a reusable longitudinal safety evaluation lens."]},
      concerns:{zh:["只有一个 Qwen3-8B、一种 AWM、4 个 state、12 个 branch、H=3，外部效度不足。","单一 HarmBench evaluator，没有 threshold sensitivity、第二 judge 或人工 spot-check。","fixed-workflow control 不是 NullMemory；也缺 replicate / permutation robustness 和 violation taxonomy。"],en:["One backbone, one memory system, four states, 12 branches, and H=3 constrain external validity.","A single HarmBench evaluator lacks threshold sensitivity, second-judge, or human spot-check validation.","The fixed-workflow control is not NullMemory; replicate robustness and violation taxonomy are also missing."]},
      reviewer_questions:{zh:["四个 state / 三个 branch 如何预选，是否存在 outcome-based selection？","违规类型是什么，HarmBench threshold / alternative judge 是否稳健？","为什么不用 NullMemory；更长 H=5–10 会怎样？"],en:["How were states/branches selected and was there outcome-based preselection?","What violation types occur and how robust are labels to thresholds or alternate judges?","Why not add NullMemory, and what happens at longer H=5–10?"]},
      repair:{
        manuscript:{zh:["把有限 case-study scope 写得更明确，同时突出 paired same-schedule + first-event 是方法贡献。","补 ST-WebAgentBench / governance / evaluator calibration 相关工作，并给出 violation taxonomy 图例。"],en:["State the finite case-study scope more explicitly while emphasizing the paired same-schedule and first-event methodology.","Add policy-aware evaluation/governance context and a violation taxonomy." ]},
        analysis:{zh:["优先用已有轨迹做 6–10 个代表 episode 的定性错误分析。","若保留了 evaluator logits/score，做 threshold sweep；增加第二 judge / 小规模人工核验，尽量不新增环境 rollout。","检查 fixed-probe violation 的 revert 是 evaluator noise、non-monotone retrieval 还是 state dependence。"],en:["Use existing trajectories for qualitative episode analysis.","If evaluator scores are retained, run threshold sensitivity and add a second judge or small human audit without new environment rollouts where possible.","Analyze reverted fixed-probe events for evaluator noise versus state dependence."]},
        experiment:{zh:["新增 NullMemory/no-memory 对照，明确 memory presence vs workflow update。","更长 horizon 和更多 backbone/memory 只允许在 fresh preregistered substrate 下开展；禁止根据已暴露开发结果继续 guard shopping。"],en:["Add a NullMemory/no-memory control to separate memory presence from workflow update.","Longer horizons and more backbones/memory systems require a fresh preregistered substrate; do not tune guards against exposed outcomes."]}
      }
    },
    "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE":{
      score:6.7,
      recommendation:{zh:"Lean Accept · 接收倾向",en:"Lean Accept"},
      verdict_tone:"accept",
      burden:{zh:"中",en:"MEDIUM"},
      repair_priority:"P1",
      reviewer_take:{zh:"这是五篇中 Reviewer 最明确看好的：paired write intervention、prompt-rewording control、256-rollout terminal confirmation 和 variance story 都被认可。主要缺口是 no-memory、跨模型/域、写入端仅 4 个完整 pair，以及 effect heterogeneity。",en:"This is the clearest positive review among the five. The paired write intervention, prompt-rewording control, 256-rollout terminal confirmation, and variance story are all recognized. Main gaps are no-memory, broader replication, only four complete write pairs, and heterogeneous effects."},
      strengths:{zh:["同一 byte-identical trajectory 只翻 reward-conditioned reflection mode，write channel 因果控制干净。","更强 lexical rewording control 仍低于 reward-mode divergence，并有显著 paired excess。","256 个未来 rollout 的 terminal effect 显著，把 memory text divergence 连接到了实际 outcome variance。"],en:["Byte-identical trajectories with only reward-conditioned reflection mode flipped isolate the write channel.","The stronger lexical rewording control remains below reward-mode divergence with significant paired excess.","The 256-rollout terminal confirmation connects memory divergence to real outcome differences and variance."]},
      concerns:{zh:["写入端只有 4 个完整 paired source trajectory；两个 failure-arm incomplete 可能产生 completion bias。","terminal effect 由少数 cell 主导，且没有 no-memory arm，无法判断两种 memory 相对“不用 memory”谁更好/更坏。","单 WebArena Shopping + ReasoningBank + 单 writer/policy，Jaccard 仍偏 lexical。"],en:["Only four complete paired source trajectories exist and two failure-arm incompletions may create completion bias.","Terminal effects are concentrated in a few cells and there is no no-memory arm.","The study uses one domain/pipeline and Jaccard remains a largely lexical diagnostic."]},
      reviewer_questions:{zh:["不同 writer / policy family 下是否复现？","能否补 embedding / strategy / structural slot 等 memory divergence 指标？","两个 incomplete failure-arm 输出为什么失败；no-memory arm 和 effect heterogeneity 会怎样？"],en:["Do effects replicate across writer/policy families?","Can semantic/strategy/structural diagnostics complement Jaccard?","Why did the two failure-arm outputs fail, and what do no-memory and heterogeneity analyses show?"]},
      repair:{
        manuscript:{zh:["把“reward reliability 是 state-consistency requirement”作为主故事，明确 variance curve 是 plug-in decomposition，不冒充真实 corruption sweep。","补 Plan-RewardBench、label-agnostic write / retrieval-time gating、MEMRL 等定位。"],en:["Center the story on reward reliability as a state-consistency requirement and clearly label the variance curve as a plug-in decomposition.","Strengthen positioning around reward-judge failure and alternative memory designs."]},
        analysis:{zh:["补 embedding cosine、strategy/topic、structural slot overlap 等语义/结构指标。","对 4×4 terminal matrix 做 heterogeneity 分析：source-future similarity、任务结构、horizon、retrieval relevance 哪些预测大 effect。","把两个 provider-incomplete failure-arm response 的失败原因与 GET-only recovery 证据写清楚，量化 selection concern。"],en:["Add semantic and structural memory diagnostics.","Analyze heterogeneity in the 4×4 terminal matrix to identify predictors of large effects.","Document the two provider-incomplete failure-arm outputs and quantify the selection concern."]},
        experiment:{zh:["最高收益新增实验：terminal confirmation 加 no-memory arm。","如果成本可控，再做一个 writer 或 policy family replication；不要先做大规模 corruption sweep。"],en:["Highest-value new experiment: add a no-memory arm to terminal confirmation.","If cheap, replicate with one additional writer or policy family before attempting a large corruption sweep."]}
      }
    },
    "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK":{
      score:5.8,
      recommendation:{zh:"Borderline Reject · 边缘拒稿",en:"Borderline Reject"},
      verdict_tone:"borderline_reject",
      burden:{zh:"高",en:"HIGH"},
      repair_priority:"P3",
      reviewer_take:{zh:"Reviewer 很认可 targeted / matched-generic / no-skill 三臂设计和 no-skill anchor 揭示 two-arm false positive；主要问题是 generic control 可能本身伤害行为、部分 endpoint 太少、condition order 未 counterbalance，以及没有和强 temporal-RAG baseline 正面对比。",en:"The reviewer strongly values the targeted/matched-generic/no-skill design and the no-skill anchor exposing a two-arm false positive. Main concerns are potentially harmful generic controls, small endpoint counts, lack of counterbalancing, and missing strong temporal-RAG baselines."},
      strengths:{zh:["三臂 intervention-defined bottleneck 比单纯“有 skill vs 无 skill”更能做机制归因。","generic helper 做 lexical/AST complexity matching，并保持 content-addressed provenance。","BEA/NOAA + EIA、DeepSeek/Kimi/mini-model 的正负 regime 支持“机制依赖具体 model-task cell”。"],en:["The three-arm intervention supports mechanism attribution beyond simple skill/no-skill comparisons.","Generic helpers are complexity-matched and artifacts are provenance-locked.","BEA/NOAA plus EIA and multiple model regimes support conditional mechanism effects."]},
      concerns:{zh:["generic control 有时会主动 surface distractor，因此 targeted > generic 可能部分来自 generic 被做坏。","grounding/alignment 某些 held-out endpoint 数很少，post-review EIA selection 也存在轻微 selection-bias 风险。","没有 MRAG / TempRetriever / Chronos / TG-RAG 等 retrieval-side temporal baseline；condition order 也未随机/counterbalance。"],en:["Generic controls can themselves be behaviorally harmful.","Several mechanism cells have few held-out endpoints and the informed EIA expansion leaves some selection-bias risk.","Strong temporal-RAG baselines and randomized/counterbalanced condition order are missing."]},
      reviewer_questions:{zh:["每个 mechanism 换一个 alternative generic / strict no-op，结论还成立吗？","三臂顺序是否随机/counterbalance；skill 实际调用率是多少？","retrieval-side cutoff prefilter、更多 temporal distractor、更大 endpoint pool 下结果如何？"],en:["Do conclusions survive alternative generic or strict no-op controls?","Were arm orders counterbalanced and what were actual skill invocation rates?","How do retrieval-side cutoff filters, heavier distractors, and larger endpoint pools compare?"]},
      repair:{
        manuscript:{zh:["把核心贡献明确成“如何证明 reusable procedure 是 binding repair”，而不是 claim 一个全新的 temporal algorithm。","补 MRAG / TempRetriever / Chronos / TG-RAG / LDAR / QAMR 的 mechanism-level 对比，并增加一张全流程 schematic。"],en:["Position the paper around identifying reusable procedures as binding repairs rather than a new temporal algorithm.","Deepen temporal-RAG/release-aware related work and add a compact experimental schematic."]},
        analysis:{zh:["统计每个 condition/model 的 skill invocation / tool-use rate，判断是否是直接 skill use 还是 prompt-context effect。","检查现有 repeats 是否存在 order trend；若当前 schedule 可分析，先做 per-repeat / slot trend。"],en:["Report skill invocation/tool-use rates by condition and model.","Analyze existing repeats for order or slot trends before adding new runs."]},
        experiment:{zh:["每个机制至少补一个 behavior-neutral alternative generic（如 strict no-op / structure-only）并保留 no-skill。","增加 retrieval-side temporal filter baseline，尤其 cutoff family；这是最高价值的定位实验。","如果仍需扩展，再做 counterbalanced/interleaved order 和更多 endpoints / distractors。"],en:["Add at least one behavior-neutral alternative generic control per mechanism while retaining no-skill.","Add a retrieval-side temporal filter baseline, especially for cutoff.","If still needed, counterbalance/interleave arm order and broaden endpoints/distractors."]}
      }
    },
    "D2-PAPER-FAILURE-MEMORY-PROVENANCE":{
      score:5.6,
      recommendation:{zh:"Weak Reject · 弱拒",en:"Weak Reject"},
      verdict_tone:"weak_reject",
      burden:{zh:"很高",en:"VERY HIGH"},
      repair_priority:"P5",
      reviewer_take:{zh:"Reviewer 认可 provenance 作为独立于 semantic content 的 causal variable，Question Importance 和 Originality 都是正向；拒稿原因几乎完全是当前 controlled evidence 不决定：terminal n=4、early-action 不是 validated surrogate、两端方向混合，而且最干净的 metadata-only intervention 没跑成。",en:"The reviewer accepts provenance as a causal variable distinct from semantic content, with positive importance and originality signals. The rejection is driven almost entirely by non-decisive controlled evidence: terminal n=4, an unvalidated early-action surrogate, mixed directions, and the missing metadata-only intervention."},
      strengths:{zh:["把 memory provenance 从“文本内容”中分离出来，提出 matched-provenance intervention。","信息等价 inclusion gate、disjoint cohorts、task-level permutation 和明确 power floor 都很严谨。","没有把 observational financial audit 冒充 causal conclusion，科学边界诚实。"],en:["Separates memory provenance from semantic content with a matched-provenance intervention.","Information-equivalence gates, disjoint cohorts, task-level permutation, and power-floor accounting are rigorous.","The paper does not misrepresent the observational financial audit as a causal conclusion."]},
      concerns:{zh:["terminal n=4 在结构上无法达到决定性 permutation p；seed replication 不能替代独立 task unit。","embedding + 单 verifier 的 information-equivalence 仍可能漏掉 tone、hedging、verbosity、imperative mood 等 style confound。","early-action reference-match 不是 terminal-success surrogate，且方向与 terminal endpoint 相反；source-faithful AgentDojo replication 和 metadata-only intervention 均缺失。"],en:["Terminal n=4 structurally prevents decisive task-level inference.","Embedding plus one verifier may miss stylistic/pragmatic confounds.","Reference-action match is not a validated success surrogate and points in the opposite direction; source-faithful replication and metadata-only intervention are missing."]},
      reviewer_questions:{zh:["如何校准 actionable-guidance equivalence；能否 multi-verifier / inter-rater？","要达到决定性 terminal test 需要多少 task unit？","能否 style-normalized rewrite、metadata-only provenance、AgentDojo source-faithful replication？"],en:["How is actionable-guidance equivalence calibrated and can multiple verifiers/inter-rater checks be added?","How many task units are required for a decisive terminal test?","Can style-normalized, metadata-only, and source-faithful AgentDojo tests be run?"]},
      repair:{
        manuscript:{zh:["当前正文继续保持“causal sign unresolved”，不要把 +0.1667 或 early-action 结果升级成方向性结论。","把 contribution 明确拆成：新 causal variable + identification protocol + 当前 inconclusive result；弱化 ledger 式叙事。","补 memory poisoning / provenance governance / positive-negative experience separation 相关工作。"],en:["Keep the causal sign explicitly unresolved.","Separate the contribution into a new causal variable, identification protocol, and currently inconclusive result; reduce ledger-like narration.","Expand provenance-governance and positive/negative-memory related work."]},
        analysis:{zh:["先做正式 power/resolution 设计：确定 terminal task-level n 与可检测 effect。","对现有 matched pairs 做 style / modality / verbosity / prescriptive-strength diagnostics；增加 multi-verifier equivalence sweep。","验证 reference-action match 与 terminal success 的相关性；若不稳定，就不要继续把它当 mechanism surrogate。"],en:["Design the required task-level sample size and detectable effect before rerunning terminal tests.","Audit style/pragmatic features and add multiple equivalence verifiers.","Validate whether reference-action match predicts terminal success; drop it as a mechanism surrogate if unstable."]},
        experiment:{zh:["第一优先：扩大独立 terminal task units，跨过 permutation resolution floor。","第二优先：真正执行 metadata-only provenance intervention（actionable text byte-identical，只变 provenance metadata/history）。","第三优先：style-controlled matched rewrite；随后才考虑回 AgentDojo/financial source-faithful replication和多 backbone/retrieval stack。"],en:["First, enlarge independent terminal task units beyond the permutation resolution floor.","Second, run a true metadata-only provenance intervention with byte-identical actionable text.","Third, add style-controlled matched rewrites, then source-faithful AgentDojo and broader backbone/retrieval replication."]}
      }
    }
  }
};
