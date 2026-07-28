window.PAGE_CONTENT["direction-board"].sections.push(
  {title:{en:"Unified matrix of the twenty retained ideas",zh:"二十个保留 Idea 的统一矩阵"},body:{en:`<table class="matrix comparison-table"><thead><tr><th>#</th><th>Direction</th><th>Subfield</th><th>Novelty</th><th>CVPR fit</th><th>Feasibility</th><th>Compute</th><th>Tier</th></tr></thead><tbody>
<tr><td>1</td><td><strong>GroundEvo-Admission</strong></td><td>Experience admission</td><td>8</td><td>9</td><td>8</td><td>Low–medium</td><td>A</td></tr>
<tr><td>2</td><td><strong>NegEvoBench-V</strong></td><td>Negative evolution benchmark</td><td>8</td><td>9</td><td>9</td><td>Low</td><td>A</td></tr>
<tr><td>3</td><td><strong>ViMEvo-Repair</strong></td><td>Visual memory repair</td><td>7</td><td>9</td><td>9</td><td>Low–medium</td><td>A</td></tr>
<tr><td>4</td><td><strong>EgoShift</strong></td><td>Embodiment drift</td><td>9</td><td>10</td><td>5</td><td>High</td><td>A</td></tr>
<tr><td>5</td><td><strong>RelianceGuard-V</strong></td><td>Grounding preservation</td><td>8</td><td>10</td><td>7</td><td>Medium</td><td>A</td></tr>
<tr><td>6</td><td><strong>EvoValue-V</strong></td><td>Experience acquisition</td><td>8</td><td>8</td><td>8</td><td>Low–medium</td><td>A</td></tr>
<tr><td>7</td><td><strong>MemoryFormRouter-V</strong></td><td>Memory representation</td><td>8</td><td>9</td><td>7</td><td>Medium</td><td>B</td></tr>
<tr><td>8</td><td><strong>SkillProof-V</strong></td><td>Verified visual skills</td><td>8</td><td>8</td><td>6</td><td>Medium</td><td>B</td></tr>
<tr><td>9</td><td><strong>SkillUnlearn-V</strong></td><td>Skill repair/unlearning</td><td>9</td><td>8</td><td>6</td><td>Medium–high</td><td>B</td></tr>
<tr><td>10</td><td><strong>UpdateRoute-V</strong></td><td>Update-surface routing</td><td>8</td><td>7</td><td>5</td><td>High</td><td>B</td></tr>
<tr><td>11</td><td><strong>BudgetEvolve-V</strong></td><td>Cost-aware evolution</td><td>8</td><td>7</td><td>8</td><td>Low–medium</td><td>B</td></tr>
<tr><td>12</td><td><strong>WorldPatch-V</strong></td><td>World-model repair</td><td>8</td><td>9</td><td>6</td><td>Medium–high</td><td>B</td></tr>
<tr><td>13</td><td><strong>SimEvo-CF</strong></td><td>Environment co-evolution</td><td>9</td><td>9</td><td>4</td><td>Very high</td><td>B</td></tr>
<tr><td>14</td><td><strong>ExploreRepair-V</strong></td><td>Memory-driven exploration</td><td>8</td><td>9</td><td>6</td><td>Medium–high</td><td>B</td></tr>
<tr><td>15</td><td><strong>EvalRedQueen-V</strong></td><td>Evaluator co-evolution</td><td>8</td><td>8</td><td>6</td><td>Medium–high</td><td>C</td></tr>
<tr><td>16</td><td><strong>EvoProvenance-V</strong></td><td>Lineage and rollback</td><td>8</td><td>6</td><td>8</td><td>Low–medium</td><td>C</td></tr>
<tr><td>17</td><td><strong>ProcessCredit-V</strong></td><td>Visual credit assignment</td><td>8</td><td>8</td><td>6</td><td>Medium–high</td><td>C</td></tr>
<tr><td>18</td><td><strong>CrossAgentTransfer-V</strong></td><td>Cross-agent experience transfer</td><td>8</td><td>7</td><td>6</td><td>Medium–high</td><td>C</td></tr>
<tr><td>19</td><td><strong>PersonaShift-V</strong></td><td>Preference-drift repair</td><td>7</td><td>8</td><td>8</td><td>Low–medium</td><td>C</td></tr>
<tr><td>20</td><td><strong>DiversityGuard-MAS</strong></td><td>Multi-agent diversity</td><td>7</td><td>6</td><td>6</td><td>Medium</td><td>C</td></tr>
</tbody></table>`,zh:`<table class="matrix comparison-table"><thead><tr><th>#</th><th>方向</th><th>小方向</th><th>新颖性</th><th>CVPR 契合</th><th>可行性</th><th>算力</th><th>分级</th></tr></thead><tbody>
<tr><td>1</td><td><strong>GroundEvo-Admission</strong></td><td>经验准入</td><td>8</td><td>9</td><td>8</td><td>低–中</td><td>A</td></tr>
<tr><td>2</td><td><strong>NegEvoBench-V</strong></td><td>负向进化基准</td><td>8</td><td>9</td><td>9</td><td>低</td><td>A</td></tr>
<tr><td>3</td><td><strong>ViMEvo-Repair</strong></td><td>视觉记忆修复</td><td>7</td><td>9</td><td>9</td><td>低–中</td><td>A</td></tr>
<tr><td>4</td><td><strong>EgoShift</strong></td><td>具身漂移</td><td>9</td><td>10</td><td>5</td><td>高</td><td>A</td></tr>
<tr><td>5</td><td><strong>RelianceGuard-V</strong></td><td>Grounding 保持</td><td>8</td><td>10</td><td>7</td><td>中</td><td>A</td></tr>
<tr><td>6</td><td><strong>EvoValue-V</strong></td><td>经验获取</td><td>8</td><td>8</td><td>8</td><td>低–中</td><td>A</td></tr>
<tr><td>7</td><td><strong>MemoryFormRouter-V</strong></td><td>记忆表示选择</td><td>8</td><td>9</td><td>7</td><td>中</td><td>B</td></tr>
<tr><td>8</td><td><strong>SkillProof-V</strong></td><td>可验证视觉技能</td><td>8</td><td>8</td><td>6</td><td>中</td><td>B</td></tr>
<tr><td>9</td><td><strong>SkillUnlearn-V</strong></td><td>技能修复／遗忘</td><td>9</td><td>8</td><td>6</td><td>中–高</td><td>B</td></tr>
<tr><td>10</td><td><strong>UpdateRoute-V</strong></td><td>更新表面路由</td><td>8</td><td>7</td><td>5</td><td>高</td><td>B</td></tr>
<tr><td>11</td><td><strong>BudgetEvolve-V</strong></td><td>成本感知进化</td><td>8</td><td>7</td><td>8</td><td>低–中</td><td>B</td></tr>
<tr><td>12</td><td><strong>WorldPatch-V</strong></td><td>世界模型修复</td><td>8</td><td>9</td><td>6</td><td>中–高</td><td>B</td></tr>
<tr><td>13</td><td><strong>SimEvo-CF</strong></td><td>环境共进化</td><td>9</td><td>9</td><td>4</td><td>很高</td><td>B</td></tr>
<tr><td>14</td><td><strong>ExploreRepair-V</strong></td><td>记忆驱动探索</td><td>8</td><td>9</td><td>6</td><td>中–高</td><td>B</td></tr>
<tr><td>15</td><td><strong>EvalRedQueen-V</strong></td><td>评价器共进化</td><td>8</td><td>8</td><td>6</td><td>中–高</td><td>C</td></tr>
<tr><td>16</td><td><strong>EvoProvenance-V</strong></td><td>溯源与回滚</td><td>8</td><td>6</td><td>8</td><td>低–中</td><td>C</td></tr>
<tr><td>17</td><td><strong>ProcessCredit-V</strong></td><td>视觉过程归因</td><td>8</td><td>8</td><td>6</td><td>中–高</td><td>C</td></tr>
<tr><td>18</td><td><strong>CrossAgentTransfer-V</strong></td><td>跨 Agent 经验迁移</td><td>8</td><td>7</td><td>6</td><td>中–高</td><td>C</td></tr>
<tr><td>19</td><td><strong>PersonaShift-V</strong></td><td>偏好漂移修复</td><td>7</td><td>8</td><td>8</td><td>低–中</td><td>C</td></tr>
<tr><td>20</td><td><strong>DiversityGuard-MAS</strong></td><td>多 Agent 多样性</td><td>7</td><td>6</td><td>6</td><td>中</td><td>C</td></tr>
</tbody></table>`}},
  {title:{en:"Tier A: six directions worth immediate pilots",zh:"A 级：六个值得立即做 Pilot 的方向"},body:{en:`<div class="property-grid">
<div class="property-card"><b>1 · GroundEvo-Admission</b><span><strong>Variable:</strong> whether one visual lesson enters persistent memory.<br><strong>Demo:</strong> frozen VLM + controlled GUI counterfactuals.<br><strong>Go:</strong> higher lesson precision and lower harmful commits than critic/outcome gates.<br><strong>Stop:</strong> counterfactuals cannot isolate the visual factor.</span></div>
<div class="property-card"><b>2 · NegEvoBench-V</b><span><strong>Variable:</strong> harmful visual evolution and hidden grounding drift.<br><strong>Demo:</strong> stale, poisoned, shortcut, and evaluator-error task streams.<br><strong>Go:</strong> standard success metrics miss harmful updates.<br><strong>Stop:</strong> old-task accuracy captures the failures.</span></div>
<div class="property-card"><b>3 · ViMEvo-Repair</b><span><strong>Variable:</strong> visual evidence freshness under changing state.<br><strong>Demo:</strong> multi-session GUI + dual visual–text memory.<br><strong>Go:</strong> repair beats long context and retrieval.<br><strong>Stop:</strong> visual evidence adds no value at equal budget.</span></div>
<div class="property-card"><b>4 · EgoShift</b><span><strong>Variable:</strong> deployment-time camera/sensor/action drift.<br><strong>Demo:</strong> simulator shifts in extrinsics, FOV, latency, and action scale.<br><strong>Go:</strong> active diagnosis beats static robustness.<br><strong>Stop:</strong> calibration-free policies already cover the shifts.</span></div>
<div class="property-card"><b>5 · RelianceGuard-V</b><span><strong>Variable:</strong> whether updates preserve dependence on causal regions/frames.<br><strong>Demo:</strong> update memory or LoRA under shortcut-confounded visual tasks.<br><strong>Go:</strong> equal accuracy with better evidence reliance.<br><strong>Stop:</strong> reliance drift is rare or inseparable from accuracy.</span></div>
<div class="property-card"><b>6 · EvoValue-V</b><span><strong>Variable:</strong> future value of verifying or learning from an experience.<br><strong>Demo:</strong> bandit chooses skip, cheap check, or counterfactual replay.<br><strong>Go:</strong> lower cost at matched harmful-update rate.<br><strong>Stop:</strong> uncertainty or heuristics match the learned policy.</span></div>
</div>`,zh:`<div class="property-grid">
<div class="property-card"><b>1 · GroundEvo-Admission</b><span><strong>变量：</strong>一段视觉经验是否进入持久记忆。<br><strong>Demo：</strong>冻结 VLM + 受控 GUI 反事实。<br><strong>继续：</strong>经验精度更高、有害提交更少。<br><strong>停止：</strong>反事实无法隔离视觉因素。</span></div>
<div class="property-card"><b>2 · NegEvoBench-V</b><span><strong>变量：</strong>有害视觉进化与隐性 grounding 漂移。<br><strong>Demo：</strong>过期、投毒、捷径和评价器错误任务流。<br><strong>继续：</strong>标准成功率遗漏有害更新。<br><strong>停止：</strong>旧任务准确率已捕获失败。</span></div>
<div class="property-card"><b>3 · ViMEvo-Repair</b><span><strong>变量：</strong>状态变化下视觉证据是否保持新鲜。<br><strong>Demo：</strong>多会话 GUI + 视觉／文本双通道记忆。<br><strong>继续：</strong>修复优于长上下文与检索。<br><strong>停止：</strong>等预算下视觉证据无额外价值。</span></div>
<div class="property-card"><b>4 · EgoShift</b><span><strong>变量：</strong>部署期相机／传感器／动作漂移。<br><strong>Demo：</strong>模拟器中改变外参、FOV、延迟和动作尺度。<br><strong>继续：</strong>主动诊断优于静态鲁棒。<br><strong>停止：</strong>免标定策略已覆盖漂移。</span></div>
<div class="property-card"><b>5 · RelianceGuard-V</b><span><strong>变量：</strong>更新后是否仍依赖因果区域／帧。<br><strong>Demo：</strong>在捷径混杂任务中更新记忆或 LoRA。<br><strong>继续：</strong>准确率相当但证据依赖更好。<br><strong>停止：</strong>依赖漂移很少或无法与准确率分离。</span></div>
<div class="property-card"><b>6 · EvoValue-V</b><span><strong>变量：</strong>验证或学习一段经验的未来价值。<br><strong>Demo：</strong>bandit 选择跳过、廉价检查或反事实重放。<br><strong>继续：</strong>匹配有害更新率下降低成本。<br><strong>停止：</strong>不确定性或启发式与学习策略持平。</span></div>
</div>`}}
);
