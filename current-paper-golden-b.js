window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-b"]={
 scenario:{title:{zh:"为什么 embodied Agent 需要把‘当前用了 memory’和‘长期自我进化’分开？",en:"Why is memory-conditioned control not yet self-evolution?"},lead:{zh:"机器人每个 episode 都会遇到局部失败和偶然成功。工程上如果看到一次好结果就永久写 memory，噪声会直接变成长期状态；因此真实 self-evolution 必须有写入、验证、提交和未来复用的生命周期。",en:"Embodied agents need a memory lifecycle rather than immediate write-back."},reasons:[
  {t:{zh:"一次成功可能是偶然",en:"One success may be accidental"},d:{zh:"环境随机性、动作噪声或碰巧恢复都可能让结果看起来很好。",en:"Noise or luck can produce a good episode."}},
  {t:{zh:"错误 credit 会被永久放大",en:"Bad credit persists"},d:{zh:"把偶然成功归给错误经验并写入，会让后续 episode 反复复用错误 memory。",en:"Misattributed memories can persist across episodes."}},
  {t:{zh:"当前 recovery 不等于长期 benefit",en:"Recovery is not future benefit"},d:{zh:"这一次动作变好，不能证明下一次遇到相似状态还能检索并受益。",en:"Current recovery says nothing about future reuse."}},
  {t:{zh:"长期状态需要可撤销治理",en:"Persistent state needs governance"},d:{zh:"真实系统需要 candidate / provisional / verified / downgrade / revoke 等状态，而不是 always-write。",en:"Persistent memories need admission, verification, and revocation states."}}
 ],why:{zh:"‘memory-on 后成功一次’和‘Agent 真正通过经验长期变强’是两个完全不同的科学主张。Paper B 把中间缺失的闭环补出来。",en:"One memory-conditioned success is far weaker than persistent self-evolution."}},
 worked:{title:{zh:"一个具体例子：机器人这一次绕开障碍成功了，为什么还不能马上把这招永久学进去？",en:"Worked example: when should one recovery become persistent memory?"},lead:{zh:"教学示例，不是当前最终确证实验。假设机器人第一次遇到抽屉前方被物体挡住。",en:"Teaching example for a cross-episode robot task."},steps:[
  {k:"01",t:{zh:"先看当前这一回合有没有真的受益",en:"Current experience"},d:{zh:"机器人读到过去经验后从左侧绕行，成功接近目标。到这里最多只能说‘这次这段经验有影响’。",en:"A recovery produces a candidate memory."}},
  {k:"02",t:{zh:"把经验先暂存，不马上永久写入",en:"Keep it provisional"},d:{zh:"系统先记下‘从左侧绕行可能有效’，但把它当成待验证候选，而不是长期规则。",en:"Do not immediately commit the experience."}},
  {k:"03",t:{zh:"确认成功真的是这段经验带来的",en:"Verify the effect"},d:{zh:"在同一个机器人状态下比较‘给这段经验 / 不给这段经验’，或用独立检查器判断，排除只是碰巧成功。",en:"Verify attribution before commitment."}},
  {k:"04",t:{zh:"未来再次遇到类似情况，还要重新证明有用",en:"Future re-exposure"},d:{zh:"另一次任务再遇到类似遮挡时，之前的经验必须能被重新取出、再次使用，并带来可验证收益，才有资格叫长期自我进化。",en:"Later related episodes must retrieve and benefit from it."}}
 ],compare:[
  {a:{zh:"当前这一回合是否真的受益",en:"Fast loop"},b:{zh:"取出经验 → 动作改变 → 当前任务恢复",en:"Current retrieval→action→recovery"},d:{zh:"只回答‘这一次，这段经验有没有帮到机器人’。",en:"Current behavioral effect."}},
  {a:{zh:"这段经验是否值得长期学进去",en:"Slow loop"},b:{zh:"先暂存 → 验证 → 永久写入 → 未来再次受益",en:"write→verify→commit→future reuse"},d:{zh:"回答的才是‘系统有没有真的通过经验形成长期能力变化’。",en:"Persistent self-evolution."}}
 ],note:{zh:"所以 Paper B 的最终硬门不是‘某一步动作变了’，而是：经验经过验证写入后，未来再次遇到类似状态时还能被复用并真正带来收益。",en:"The final gate is cross-episode write→reuse→benefit."}},
 spotlight:{title:"Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents",problem:{zh:"Agent 同时需要短期工作记忆和长期经验，但固定规则很难决定什么该保留、更新或忘记。",en:"Agents need coordinated short- and long-term memory management."},added:{zh:"ACL 2026 的 Agentic Memory 把长期/短期 memory management 统一成可学习的管理问题，是‘memory lifecycle’的直接近邻。",en:"Agentic Memory learns unified long/short-term memory management."},method:{zh:"它强调怎样管理 memory state；Paper B 则把 embodied self-evolution 的科学硬门放到 future re-exposure 上。",en:"It focuses on memory management; Paper B requires future re-exposure evidence."},bridge:{zh:"两者都反对‘存进去就算记住’。Paper B 更进一步要求：候选经验经过验证和提交后，必须在未来机器人 episode 中再次被检索并产生收益，才叫长期自进化。",en:"Paper B requires verified future reuse in embodied episodes."}},
 architecture:{lead:{zh:"Paper B 不是换了一套机器人数据，而是在同一个 LIBERO / MemoryVLA 底座上，把问题从‘这一次动作有没有受记忆影响’一路扩展到‘什么经验值得永久学进去、以后还能不能再次受益’。",en:"Paper B extends the same embodied substrate into a longitudinal lifecycle."},layers:[
  {k:"A",t:"LIBERO / LIBERO-Plus",d:{zh:"提供机器人要完成的语言指令任务，以及相机、机器人状态、噪声、布局等受控变化。",en:"Robot tasks and perturbations."}},
  {k:"B",t:"MemoryVLA",d:{zh:"提供真实的‘机器人可以读取过去经验并让动作改变’这条通道。",en:"Memory-conditioned VLA carrier."}},
  {k:"C",t:{zh:"24 个开发场景",en:"24 development scopes"},d:{zh:"用 task0–2 × 四类扰动 × 两档难度，把‘动作有影响’继续拆成：有没有修回来、能不能持续回到正确轨迹、最后任务是否成功、这段经验是否值得写入。",en:"Development scopes for robustness and write-back logic."}},
  {k:"D",t:{zh:"跨任务回合的最终验证",en:"Longitudinal stream"},d:{zh:"早期任务产生经验 → 验证后决定是否写入 → 未来相关任务再次遇到类似状态 → 检查是否真的再次受益。",en:"Confirmatory source→update→future-reuse stream."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先确认机器人底座真的跑对",en:"Substrate reproduction"},q:{zh:"官方 MemoryVLA 路线能不能稳定复现？",en:"Is the base carrier reliable?"},found:{zh:"task0 官方复现通过。",en:"Task0 reproduction passes."},meaning:{zh:"先确保后面看到的现象不是环境或模型加载错了。",en:"Qualifies the carrier."}},
  {k:"B",t:{zh:"确认当前这一回合，记忆真的会改变动作",en:"Current influence"},q:{zh:"保持机器人看到的场景完全一样，只开关过去经验，动作会不会变？",en:"Does memory change action?"},found:{zh:"同状态动作差异 ||Δa||₂≈0.5541。",en:"Same-state action shift ≈0.5541."},meaning:{zh:"说明记忆通道真的有影响，但还只能证明‘这次动作受影响’。",en:"Fast-loop prerequisite only."}},
  {k:"C",t:{zh:"再检查：动作变了以后，任务真的被修好了吗？",en:"24-scope development"},q:{zh:"在相机、机器人状态、噪声、布局变化下，记忆影响能不能稳定变成恢复、回到正确轨迹和最终成功？",en:"Can influence become robust recovery?"},found:{zh:"24 个测试场景已经冻结，但这只是测试空间，不能提前写成‘稳健性已经证明’。",en:"The test space is frozen; robustness is not yet established."},meaning:{zh:"同时也用这些场景开发‘什么经验值得永久写入’的验证规则。",en:"Develops slow-loop admission/verification."}},
  {k:"D",t:{zh:"最后才检查：永久学进去以后，未来还会不会再次受益",en:"Future-reuse confirmation"},q:{zh:"一段经验经过验证并永久写入后，未来另一个相关任务还能不能重新取出并带来收益？",en:"Does committed memory help later?"},found:{zh:"这层完整证据目前还没有闭合。",en:"Confirmatory evidence is pending."},meaning:{zh:"所以现在还不能把一次 memory-conditioned action 写成已经完成的长期自我进化。",en:"Longitudinal claim remains pending."}}
 ]
};
