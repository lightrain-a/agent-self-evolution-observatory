# 科研图表知识库：完整来源索引

> 图例数量、图片文件数、图型家族和本地渲染器数量分别统计。所有具体条目可在前端查看；文件名标签尚需逐图核对。

页面： https://agent-evolution.lightrain.asia/figure-knowledge-base.html

## 覆盖范围

| 仓库 | 条目 | 视觉文件 | 已索引 | 版本 |
|---|---:|---:|---:|---|
| yjz211/vivid-figures-skill | 191 | 355 | 355 | `c043f0553c7c` |
| ChenLiu-1996/figures4papers | 45 | 42 | 42 | `f0bb7559abe9` |
| holtzy/The-Python-Graph-Gallery | 1649 | 1303 | 1303 | `64424bccec3d` |
| posit-dev/great-tables | 196 | 145 | 145 | `f870830578dd` |

## 选图知识

### 雨云图
用途：组间分布、离群点和密度如何不同？
输入：group, raw_samples
注意：密度与箱线必须来自原始样本；带宽和抖动要说明。

### 山脊图
用途：多组分布位置和形状如何变化？
输入：group, raw_samples
注意：共享尺度；不要把均值列表伪装成分布。

### 小提琴与分组小提琴
用途：组内密度是否多峰或偏斜？
输入：group, raw_samples
注意：小样本密度估计可能不稳；显示样本量。

### 经验累积分布
用途：尾部概率和整体分布在哪里不同？
输入：group, raw_samples
注意：明确横轴变量和累计概率方向。

### 箱线图
用途：中位数、四分位和离散程度如何？
输入：group, raw_samples
注意：声明须线规则；须线不自动等于置信区间。

### 直方图
用途：频数或密度集中在哪里？
输入：raw_samples, bins
注意：跨组保持分箱与归一化可比。

### 密度曲线
用途：分布有几个峰、宽度多大？
输入：raw_samples
注意：声明带宽；不要从单个汇总值估计分布。

### 样本散点与蜂群
用途：每个样本的位置如何？
输入：group, raw_samples
注意：抖动不代表另一个测量维度。

### 哑铃图
用途：同一对象的前后差异有多大？
输入：pair_id, before, after
注意：必须是真正配对，不能任意连接。

### 斜率图
用途：对象的变化方向及交叉关系是什么？
输入：pair_id, before, after
注意：不要把连接线误解为观测过的时间轨迹。

### 配对点图
用途：哪些对象改善、保持或回归？
输入：pair_id, before, after
注意：保留对象身份和负向变化。

### Bland–Altman 一致性图
用途：两个测量的偏差是否随水平变化？
输入：pair_id, measurement_a, measurement_b
注意：一致性界限不是无条件可解释为置信区间。

### 发散条形图
用途：相对参考点的正负效应如何？
输入：category, signed_value
注意：声明参考值和正负含义；不能隐藏负值。

### 排名变化图
用途：名次随条件如何变化？
输入：entity, ordered_condition, rank
注意：展示并列规则；排名不等于绝对效果差。

### 棒棒糖图
用途：哪个类别更高，差多少？
输入：category, value
注意：固定基线与类别排序。

### 点图
用途：类别间的水平差异是什么？
输入：category, value
注意：区间必须另有统计依据。

### 分组柱状图
用途：不同方法在同一条件下如何比较？
输入：category, series, value
注意：柱高编码绝对量时从零起；组内口径一致。

### 瀑布与贡献分解
用途：各部分怎样累积为总变化？
输入：ordered_component, signed_contribution, reference
注意：分量必须能按明确规则相加。

### 堆叠图
用途：总量及组成随类别或时间如何变化？
输入：category, component, value
注意：明确总量还是百分比；组成要有同一分母。

### 环形与嵌套环形图
用途：整体由哪些部分组成？
输入：component, nonnegative_value
注意：组成应共享整体；小差异优先点图。

### 饼图
用途：少量类别占比如何？
输入：component, nonnegative_value
注意：份额分母一致；类别过多难比较。

### 矩形树图
用途：层级组成的面积分配是什么？
输入：parent, child, nonnegative_value
注意：面积比较不适合精细差异。

### 旭日图
用途：层级份额怎样分解？
输入：hierarchy_path, value
注意：层级聚合必须守恒。

### 华夫图
用途：离散份额如何直观表示？
输入：component, count_or_share
注意：说明每格代表什么和取整误差。

### 折线与训练趋势
用途：趋势、收敛或边际收益是什么？
输入：series, ordered_x, y
注意：只连接已观测点；区分开发与确认数据。

### 阶梯图
用途：状态何时离散改变？
输入：ordered_x, y
注意：拐角是编码约定，不额外标成观测点。

### 面积与流带
用途：总量如何随有序变量变化？
输入：ordered_x, y
注意：填充面积易放大差别；说明基线。

### 河流图
用途：多个组成的相对变化模式是什么？
输入：time, group, value
注意：漂移基线不适合精确读绝对量。

### 地平线图
用途：多条长序列的异常位置在哪里？
输入：time, signed_value
注意：颜色分层和折叠规则必须解释。

### 扇形预测区间
用途：预测不确定性怎样随时间变化？
输入：ordered_x, estimate, intervals
注意：区间水平与计算方法要明确。

### 甘特图
用途：任务或阶段怎样并行与衔接？
输入：task, start, end
注意：阶段时间应来自真实记录。

### 散点与拟合关系
用途：两个变量怎样共同变化？
输入：x, y, observation_id
注意：相关不等于因果；拟合与区间需有依据。

### 气泡图
用途：第三个量如何与二维位置共同变化？
输入：x, y, nonnegative_size
注意：面积而非半径编码 size，标单位。

### 六边形密度图
用途：大量点聚集在哪里？
输入：raw_x, raw_y
注意：网格分辨率和颜色是计数或密度要说明。

### 联合与边缘分布
用途：联合关系与各边缘分布怎样对应？
输入：raw_x, raw_y
注意：各层必须来自同一配对样本。

### 成对关系矩阵
用途：多个变量的两两关系是什么？
输入：sample_id, numeric_feature_columns
注意：不要混用不同样本子集。

### 平行坐标
用途：多维性能模式和取舍是什么？
输入：entity, multiple_numeric_features
注意：需要说明归一化和各轴方向。

### 雷达图
用途：多指标轮廓如何不同？
输入：entity, metrics, normalization
注意：轴顺序、方向和尺度会影响面积印象。

### Pareto 性能—成本图
用途：哪些实测点是非支配取舍？
输入：measured_cost, measured_utility
注意：不能编造连续前沿或漏记成本。

### 热力矩阵
用途：哪些交叉条件高或低？
输入：row_id, column_id, value
注意：缺失不是零；同一比较保持色阶。

### 聚类热图
用途：哪些行列具有共同模式？
输入：matrix, distance, linkage
注意：聚类度量与顺序要能复现。

### 日历热图
用途：时间周期和局部异常在哪里？
输入：date, value
注意：不能把缺测天当作零。

### 关系网络
用途：对象之间的关系和结构是什么？
输入：node_id, edge_source, edge_target, weight
注意：边的统计/因果含义要明确。

### 桑基与流向图
用途：同一总体在阶段之间如何流动？
输入：source, target, flow_weight
注意：仅有边际量不能恢复流量。

### 弦图
用途：类别之间的双向关系有多强？
输入：source, target, weight
注意：边过多会遮挡；需要实际关系量。

### 弧线网络
用途：在固定顺序上的关系跨度是什么？
输入：node_order, source, target
注意：节点顺序与边存在性须有依据。

### Venn 与集合交集
用途：哪些对象属于共同集合？
输入：set_membership, entity_id
注意：交集不能从各集合大小推测。

### UpSet 交集图
用途：多个集合的组合交集多大？
输入：set_membership_matrix
注意：必须有对象级集合归属。

### 地理与分区地图
用途：空间分布与邻域关系是什么？
输入：coordinates_or_region_ids, value, geometry
注意：投影和面积可能影响读图。

### 等值线
用途：二维空间内水平线如何分布？
输入：x_grid, y_grid, z
注意：插值区域必须区别于观测位置。

### 三维曲面与网格
用途：实际采样的空间结构是什么？
输入：x, y, z
注意：透视和插值不能代替新测量。

### 体积与等值面
用途：三维标量场内部结构是什么？
输入：x, y, z, scalar_field
注意：阈值与采样分辨率需明确。

### 向量场与轨迹
用途：方向、速度或迁移轨迹如何？
输入：position, vector_components
注意：向量长度和路径必须来自数据。

### 极坐标与径向图
用途：周期性、方向性或环形排序是什么？
输入：angle_or_category, radius_or_value
注意：角度不能任意充当测量方向。

### Forest 效应区间
用途：效应方向、大小及不确定性是什么？
输入：estimate, lower, upper, interval_definition
注意：SD、SE、CI 不能互换。

### 事件研究与平行趋势
用途：干预前后变化与对照如何？
输入：event_time, estimate, comparison, uncertainty
注意：因果解释还需识别假设与对照设计。

### 生存曲线
用途：事件发生时间和删失如何分布？
输入：event_time, event_indicator, group
注意：处理删失，不把它当未发生。

### 后验轨迹与密度
用途：采样收敛与后验形态如何？
输入：chain_id, iteration, parameter_sample
注意：后验区间不同于频率学置信区间。

### ROC/PR 评价曲线
用途：阈值变化时如何权衡错误？
输入：true_labels, continuous_scores
注意：必须有评分与真值，不能从一个准确率生成。

### 校准与可靠性
用途：置信度与实际正确率一致吗？
输入：probability, label, binning
注意：分箱、样本量与区间需说明。

### 混淆矩阵
用途：错误集中在哪些类别对？
输入：true_label, predicted_label
注意：归一化按行、列或总体要明确。

### 残差诊断
用途：误差偏差、异方差或尾部如何？
输入：observed, predicted
注意：有序/配对关系不能丢失。

### 消融与敏感性
用途：组件或超参数变化是否改变结果？
输入：configuration, outcome, controlled_factors
注意：控制信息和预算；不把所有变化都称为因果。

### 嵌入与降维
用途：样本的低维结构和分组如何？
输入：sample_id, feature_matrix, labels_optional
注意：距离可能被投影扭曲；算法参数需保存。

### SHAP 与特征贡献
用途：特征在样本上的贡献如何分布？
输入：sample_id, feature_values, attribution_values
注意：必须有实际归因值，不能用相关系数冒充。

### PDP/ICE 依赖图
用途：模型输出如何随特征变化？
输入：feature_grid, model_predictions, conditioning
注意：相关特征会影响反事实解释。

### 火山图
用途：效应大小与统计证据怎样共同变化？
输入：effect_size, p_or_q_value
注意：需要真实检验与多重比较处理。

### Taylor 统计比较
用途：模型相关性与离散程度如何比较？
输入：correlation, standard_deviation, reference
注意：各统计量必须来自同一评价样本。

### 性能剖面
用途：方法在多任务上的相对表现怎样？
输入：task, method, cost_or_performance
注意：定义比率、失败任务和阈值规则。

### 结果表与分组表
用途：如何读精确值、分组均值与注释？
输入：row_ids, columns, units, missing_status
注意：显示格式不能改变分母与计算口径。

### 机制示意与流程
用途：对象、流程和作用关系是什么？
输入：entities, relations, caption
注意：示意关系不能伪装成实测结果。

### 多面板组合
用途：互补证据怎样共同回答科学问题？
输入：panel_sources, panel_questions, shared_encodings
注意：逐面板绑定数据；候选板不等于最终论文版式。

### 配色与视觉样式
用途：颜色、线型与层次怎样更易辨识？
输入：encoding_semantics, accessibility
注意：风格变体不是新的科学证据。

### 待核对原图
用途：需要打开原图和脚本后确定用途。
输入：需查看具体资料
注意：文件名不足以确定数据与图型；不能自动用于科学结论。

### 漏斗图
用途：各阶段损耗如何？
输入：ordered_stage, count
注意：阶段应对应同一总体，不能将无关计数串联。

### Hovmöller 时空图
用途：随空间与时间共同变化的模式是什么？
输入：time, space, value
注意：标清空间轴和时间采样。

### 可行域与约束边界
用途：哪些区域满足约束？
输入：constraints, coordinates, feasibility
注意：边界应由明确约束计算，不能凭视觉推断。

### 状态网格
用途：离散状态的可达性或评价如何？
输入：state_coordinates, state_value
注意：颜色对应离散状态还是数值必须说明。

### 系数稳定与平衡诊断
用途：估计随设定变化是否稳定、组间是否平衡？
输入：specification, estimate, balance_metric
注意：诊断不自动证明因果可识别。

### 方差与误差分解
用途：不同来源贡献了多少变异？
输入：component, decomposition_rule, value
注意：分解依赖统计定义，不能把任意分数相加。

### 潜空间插值
用途：沿潜空间路径输出如何变化？
输入：latent_path, decoded_outputs
注意：生成样本与真实观测必须区分。

### 层次树与树状聚类
用途：对象如何逐级合并为组？
输入：distance_matrix, linkage
注意：距离与联接规则影响树结构。

### 词云
用途：高频词或关键词是什么？
输入：token, frequency_or_weight
注意：词云不适合精确比较；需记录分词与权重。

### 动态图
用途：状态随帧如何连续或离散变化？
输入：frame_id, stable_entity_id, observations
注意：转场插值不是新的观测。

### 标注、图例与排版示例
用途：如何让图例、标签和布局更清晰？
输入：labels, units, legend_semantics
注意：这些是样式教程，不是独立研究证据。

### 双轴与多轴图
用途：不同量纲如何沿同一横轴对照？
输入：x, separate_y_units, axis_mapping
注意：多轴缩放容易制造相关印象，优先检查是否可拆图。

### 圆形打包图
用途：层级内的大小如何比较？
输入：parent, child, nonnegative_value
注意：面积编码而非半径；空间间隙没有数值含义。

### 蜡烛与区间范围图
用途：每个时间段的范围与始末值如何？
输入：ordered_x, open, close, high, low
注意：四个统计量需来自同一时间窗。

### 分位数分布图
用途：分布各位置怎样随条件变化？
输入：raw_samples_or_quantiles, group
注意：区分原始样本、估计分位数和回归系数。

### 统计检验可视化
用途：组间差异及检验依据如何？
输入：samples, design, test_definition
注意：图示不能替代假设检验条件与多重比较控制。

### 变形统计地图
用途：统计量如何与地理区域对应？
输入：region_id, geometry, value
注意：面积变形改变地理关系，需要图例。

## 全部条目

### Vivid Figures
来源版本：`c043f0553c7c3188b1bb8dcbf7db76d2adf98375`。许可：Personal Non-Commercial License; restrictive; no template/code redistribution。

- `vivid-8639d6fa616f62` [academic.ablation](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.ablation.md) · RECIPE_CARD · 预览 1 · 消融与敏感性
- `vivid-226494ef92ce7e` [academic.attention_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.attention_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-c39f1ad078f091` [academic.benchmark_table](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.benchmark_table.md) · RECIPE_CARD · 预览 1 · 结果表与分组表
- `vivid-29917fef5bc488` [academic.confusion_matrix](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.confusion_matrix.md) · RECIPE_CARD · 预览 1 · 混淆矩阵 / 热力矩阵
- `vivid-874dfebd6c71ee` [academic.error_analysis](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.error_analysis.md) · RECIPE_CARD · 预览 1 · 残差诊断
- `vivid-f683da99cc9fd1` [academic.feature_importance](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.feature_importance.md) · RECIPE_CARD · 预览 1 · SHAP 与特征贡献
- `vivid-640a112b1ab44e` [academic.hyperparameter_sensitivity](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.hyperparameter_sensitivity.md) · RECIPE_CARD · 预览 1 · 消融与敏感性
- `vivid-4eaea1c692b356` [academic.latent_interpolation](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.latent_interpolation.md) · RECIPE_CARD · 预览 1 · 潜空间插值
- `vivid-7897ab2de6b1e0` [academic.learning_rate](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.learning_rate.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-cfb1d15124b6d4` [academic.radar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.radar.md) · RECIPE_CARD · 预览 1 · 雷达图
- `vivid-34a9bb57744445` [academic.training_curves](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.training_curves.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-0a0be657bd7c26` [academic.tsne_umap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/academic.tsne_umap.md) · RECIPE_CARD · 预览 1 · 嵌入与降维
- `vivid-9dbcc51abcb094` [advanced.back_to_back_bar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.back_to_back_bar.md) · RECIPE_CARD · 预览 1 · 发散条形图 / 分组柱状图
- `vivid-abe420d4135967` [advanced.bivariate_choropleth](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.bivariate_choropleth.md) · RECIPE_CARD · 预览 1 · 地理与分区地图
- `vivid-2cc64a8a7d7978` [advanced.bland_altman](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.bland_altman.md) · RECIPE_CARD · 预览 1 · Bland–Altman 一致性图
- `vivid-5c4f1fd4c5a72f` [advanced.bump](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.bump.md) · RECIPE_CARD · 预览 1 · 排名变化图
- `vivid-398a962997d3c2` [advanced.calendar_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.calendar_heatmap.md) · RECIPE_CARD · 预览 1 · 日历热图 / 热力矩阵
- `vivid-aa035912bed898` [advanced.calibration](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.calibration.md) · RECIPE_CARD · 预览 1 · 校准与可靠性
- `vivid-0ec9ca0f1b7b11` [advanced.cluster_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.cluster_heatmap.md) · RECIPE_CARD · 预览 1 · 聚类热图 / 热力矩阵
- `vivid-2ca83483a1b3bf` [advanced.diverging_bar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.diverging_bar.md) · RECIPE_CARD · 预览 1 · 发散条形图 / 分组柱状图
- `vivid-a9b89d206f9958` [advanced.dot_ci](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.dot_ci.md) · RECIPE_CARD · 预览 1 · Forest 效应区间 / 点图
- `vivid-605bd426d7ebe3` [advanced.dumbbell](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.dumbbell.md) · RECIPE_CARD · 预览 1 · 哑铃图
- `vivid-fa074007f53c2c` [advanced.fan](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.fan.md) · RECIPE_CARD · 预览 1 · 扇形预测区间
- `vivid-e59dac09bb1369` [advanced.funnel](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.funnel.md) · RECIPE_CARD · 预览 1 · 漏斗图
- `vivid-c8e6a4b67ef7ad` [advanced.grouped_bar_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.grouped_bar_3d.md) · RECIPE_CARD · 预览 1 · 分组柱状图 / 三维曲面与网格
- `vivid-73043a5ac00ab0` [advanced.grouped_violin](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.grouped_violin.md) · RECIPE_CARD · 预览 1 · 小提琴与分组小提琴
- `vivid-eb52b620660ae7` [advanced.hovmoller](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.hovmoller.md) · RECIPE_CARD · 预览 1 · Hovmöller 时空图
- `vivid-f7c1e2b52113cc` [advanced.ice_pdp](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.ice_pdp.md) · RECIPE_CARD · 预览 1 · PDP/ICE 依赖图
- `vivid-d7479e4140d1fc` [advanced.kaplan_meier](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.kaplan_meier.md) · RECIPE_CARD · 预览 1 · 生存曲线
- `vivid-c51e5f9cc51eed` [advanced.lollipop](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.lollipop.md) · RECIPE_CARD · 预览 1 · 棒棒糖图
- `vivid-37d3d66eeeb7fd` [advanced.method_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.method_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-d6134d23ade950` [advanced.multi_y_gradient_hist](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.multi_y_gradient_hist.md) · RECIPE_CARD · 预览 1 · 双轴与多轴图 / 直方图
- `vivid-76e9e13b043b56` [advanced.network](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.network.md) · RECIPE_CARD · 预览 1 · 关系网络
- `vivid-b1e18c23b8c62e` [advanced.pair_plot](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.pair_plot.md) · RECIPE_CARD · 预览 1 · 成对关系矩阵
- `vivid-25ad9d9fa05ebf` [advanced.paired_dot](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.paired_dot.md) · RECIPE_CARD · 预览 1 · 配对点图
- `vivid-26bdbaea6413a1` [advanced.parallel_coordinates](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.parallel_coordinates.md) · RECIPE_CARD · 预览 1 · 平行坐标
- `vivid-9faf671fc50bab` [advanced.pca_biplot](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.pca_biplot.md) · RECIPE_CARD · 预览 1 · 嵌入与降维
- `vivid-52d9f7863d8dc4` [advanced.performance_profile](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.performance_profile.md) · RECIPE_CARD · 预览 1 · 性能剖面
- `vivid-a80bbfb7d6a997` [advanced.posterior_trace_density](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.posterior_trace_density.md) · RECIPE_CARD · 预览 1 · 后验轨迹与密度 / 密度曲线
- `vivid-9777bbd731e0e8` [advanced.relief_correlation_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.relief_correlation_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-7f8bff0cd3e859` [advanced.ridgeline](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.ridgeline.md) · RECIPE_CARD · 预览 1 · 山脊图
- `vivid-884ce123d38396` [advanced.sankey](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.sankey.md) · RECIPE_CARD · 预览 3 · 桑基与流向图
- `vivid-a6f588999a21fe` [advanced.shap_summary](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.shap_summary.md) · RECIPE_CARD · 预览 1 · SHAP 与特征贡献
- `vivid-ee03243a221594` [advanced.slope](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.slope.md) · RECIPE_CARD · 预览 1 · 斜率图
- `vivid-35d9ee04bbc762` [advanced.streamgraph](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.streamgraph.md) · RECIPE_CARD · 预览 1 · 河流图
- `vivid-565ce795119747` [advanced.taylor](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.taylor.md) · RECIPE_CARD · 预览 1 · Taylor 统计比较
- `vivid-3592d6b2637710` [advanced.triptych](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.triptych.md) · RECIPE_CARD · 预览 1 · 多面板组合
- `vivid-3c5f8b9b64f63f` [advanced.volcano](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.volcano.md) · RECIPE_CARD · 预览 1 · 火山图
- `vivid-c8ea566fbe7c3b` [advanced.waterfall](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/advanced.waterfall.md) · RECIPE_CARD · 预览 1 · 瀑布与贡献分解
- `vivid-3faf74f589659d` [basic.area](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.area.md) · RECIPE_CARD · 预览 1 · 面积与流带
- `vivid-791cfcb2ca5f78` [basic.donut](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.donut.md) · RECIPE_CARD · 预览 1 · 环形与嵌套环形图
- `vivid-aa5c67376b09ed` [basic.dual_axis](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.dual_axis.md) · RECIPE_CARD · 预览 1 · 双轴与多轴图 / 标注、图例与排版示例
- `vivid-fdf5ca679a5499` [basic.grouped_bar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.grouped_bar.md) · RECIPE_CARD · 预览 1 · 分组柱状图
- `vivid-1418db9abc7a13` [basic.heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-cf2048e2c98099` [basic.line](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.line.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-3e75d59e95d308` [basic.multipanel](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.multipanel.md) · RECIPE_CARD · 预览 1 · 多面板组合
- `vivid-5e6e275ef3a8a1` [basic.pareto](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.pareto.md) · RECIPE_CARD · 预览 1 · Pareto 性能—成本图
- `vivid-fa37099eff1235` [basic.raincloud](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.raincloud.md) · RECIPE_CARD · 预览 1 · 雨云图
- `vivid-a8c8dd90440399` [basic.raincloud_violin](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.raincloud_violin.md) · RECIPE_CARD · 预览 1 · 雨云图 / 小提琴与分组小提琴
- `vivid-e9733e5c00a6b6` [basic.scatter_regression](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.scatter_regression.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系
- `vivid-47f51371e71ae0` [basic.stacked_bar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/basic.stacked_bar.md) · RECIPE_CARD · 预览 1 · 堆叠图 / 分组柱状图
- `vivid-7fa17147f621ef` [competition.bubble_joint](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.bubble_joint.md) · RECIPE_CARD · 预览 1 · 气泡图 / 联合与边缘分布
- `vivid-0a721f26e5f1f2` [competition.bubble_kde](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.bubble_kde.md) · RECIPE_CARD · 预览 1 · 气泡图 / 密度曲线
- `vivid-fe4aba526be579` [competition.china_choropleth](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.china_choropleth.md) · RECIPE_CARD · 预览 1 · 地理与分区地图
- `vivid-156f0b4bbdf134` [competition.cluster_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.cluster_3d.md) · RECIPE_CARD · 预览 1 · 嵌入与降维 / 三维曲面与网格
- `vivid-5617ea07f97268` [competition.confusion_matrix](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.confusion_matrix.md) · RECIPE_CARD · 预览 1 · 混淆矩阵 / 热力矩阵
- `vivid-4e27ab5170a0f7` [competition.contour](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.contour.md) · RECIPE_CARD · 预览 1 · 等值线
- `vivid-3245fbb5058cff` [competition.convergence](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.convergence.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-4ed574d4195ec8` [competition.correlation_matrix](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.correlation_matrix.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-8db9eeca1d5432` [competition.feasible_region](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.feasible_region.md) · RECIPE_CARD · 预览 1 · 可行域与约束边界
- `vivid-517f847495b4c8` [competition.feature_importance](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.feature_importance.md) · RECIPE_CARD · 预览 1 · SHAP 与特征贡献
- `vivid-615142ee3a45ce` [competition.gantt](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.gantt.md) · RECIPE_CARD · 预览 1 · 甘特图
- `vivid-3b148b36fa6cb5` [competition.gravity_migration](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.gravity_migration.md) · RECIPE_CARD · 预览 1 · 向量场与轨迹
- `vivid-f48e80866cdb95` [competition.hexbin_joint](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.hexbin_joint.md) · RECIPE_CARD · 预览 1 · 六边形密度图 / 联合与边缘分布
- `vivid-9152ceb81db28c` [competition.kde_joint](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.kde_joint.md) · RECIPE_CARD · 预览 1 · 联合与边缘分布 / 密度曲线
- `vivid-549e7640048643` [competition.kmeans](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.kmeans.md) · RECIPE_CARD · 预览 1 · 嵌入与降维
- `vivid-2fd8dde2e598cd` [competition.multistep_decay](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.multistep_decay.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-d99dbf9344f7f8` [competition.network_path](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.network_path.md) · RECIPE_CARD · 预览 1 · 关系网络
- `vivid-67f58e84855b61` [competition.pareto_front](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.pareto_front.md) · RECIPE_CARD · 预览 1 · Pareto 性能—成本图
- `vivid-3379a2eb804c60` [competition.pareto_surface_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.pareto_surface_3d.md) · RECIPE_CARD · 预览 1 · 三维曲面与网格 / Pareto 性能—成本图
- `vivid-7227278cf4b929` [competition.prediction_actual](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.prediction_actual.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系
- `vivid-f58bc14a772f43` [competition.radar](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.radar.md) · RECIPE_CARD · 预览 1 · 雷达图
- `vivid-b45ea26d821f9c` [competition.residual_diagnostics](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.residual_diagnostics.md) · RECIPE_CARD · 预览 1 · 残差诊断
- `vivid-a5153377d7a296` [competition.roc](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.roc.md) · RECIPE_CARD · 预览 1 · ROC/PR 评价曲线
- `vivid-220f3a3afa8b3b` [competition.scatter_regression_marginals](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.scatter_regression_marginals.md) · RECIPE_CARD · 预览 1 · 联合与边缘分布 / 散点与拟合关系
- `vivid-0e0f06fe75b012` [competition.spatiotemporal_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.spatiotemporal_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-cd9f3944e6f59b` [competition.state_grid](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.state_grid.md) · RECIPE_CARD · 预览 1 · 状态网格
- `vivid-a03c9f9127bbf7` [competition.surface_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.surface_3d.md) · RECIPE_CARD · 预览 1 · 三维曲面与网格
- `vivid-af343735e08434` [competition.tornado](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.tornado.md) · RECIPE_CARD · 预览 1 · 发散条形图
- `vivid-093b52ade7a122` [competition.waterfall](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/competition.waterfall.md) · RECIPE_CARD · 预览 1 · 瀑布与贡献分解
- `vivid-e1b8079167ffab` [empirical.coefficient_stability](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.coefficient_stability.md) · RECIPE_CARD · 预览 1 · 系数稳定与平衡诊断
- `vivid-6a597fbf9ed031` [empirical.correlation_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.correlation_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-bd693e6b58a94e` [empirical.event_study](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.event_study.md) · RECIPE_CARD · 预览 1 · 事件研究与平行趋势
- `vivid-d08fbea9d7369c` [empirical.forest](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.forest.md) · RECIPE_CARD · 预览 1 · Forest 效应区间
- `vivid-614f6c14e185cf` [empirical.impulse_response](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.impulse_response.md) · RECIPE_CARD · 预览 1 · 事件研究与平行趋势
- `vivid-a203d8df7403c7` [empirical.lisa_map](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.lisa_map.md) · RECIPE_CARD · 预览 1 · 地理与分区地图
- `vivid-09a10f6a333462` [empirical.marginal_effects](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.marginal_effects.md) · RECIPE_CARD · 预览 1 · 联合与边缘分布
- `vivid-9d9755bd72aead` [empirical.moran_scatter](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.moran_scatter.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系 / 地理与分区地图
- `vivid-9f6cfb6b0c064f` [empirical.multistep_decay](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.multistep_decay.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-94de996154613f` [empirical.parallel_trends](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.parallel_trends.md) · RECIPE_CARD · 预览 1 · 事件研究与平行趋势
- `vivid-7360abee717389` [empirical.placebo](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.placebo.md) · RECIPE_CARD · 预览 1 · 事件研究与平行趋势
- `vivid-18fa8c8ba805f2` [empirical.prediction_accuracy_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.prediction_accuracy_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-210eb8ebcea93e` [empirical.prediction_ci](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.prediction_ci.md) · RECIPE_CARD · 预览 1 · 扇形预测区间
- `vivid-afcfd6b448cd49` [empirical.prediction_error_raincloud](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.prediction_error_raincloud.md) · RECIPE_CARD · 预览 1 · 雨云图
- `vivid-32f0c0e8550e9b` [empirical.psm_balance](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.psm_balance.md) · RECIPE_CARD · 预览 1 · 系数稳定与平衡诊断
- `vivid-f63b11719d4597` [empirical.quantile_regression](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.quantile_regression.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系 / 分位数分布图
- `vivid-27b04a69404bde` [empirical.raincloud](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.raincloud.md) · RECIPE_CARD · 预览 1 · 雨云图
- `vivid-39141a466d01e3` [empirical.residual_diagnostics](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.residual_diagnostics.md) · RECIPE_CARD · 预览 1 · 残差诊断
- `vivid-18078941977143` [empirical.subgroup_forest](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.subgroup_forest.md) · RECIPE_CARD · 预览 1 · Forest 效应区间
- `vivid-40bef5109d7884` [empirical.time_series](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.time_series.md) · RECIPE_CARD · 预览 1 · 折线与训练趋势
- `vivid-c8f71e30adedc5` [empirical.variance_decomposition](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/empirical.variance_decomposition.md) · RECIPE_CARD · 预览 1 · 方差与误差分解
- `vivid-de96ecdff03721` [screenshot.block_surface_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.block_surface_3d.md) · RECIPE_CARD · 预览 1 · 三维曲面与网格
- `vivid-4c0c52455758c6` [screenshot.chord](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.chord.md) · RECIPE_CARD · 预览 1 · 弦图
- `vivid-05e55f6b23ef57` [screenshot.classified_scatter](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.classified_scatter.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系
- `vivid-489259b6ef238c` [screenshot.concentric_bars](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.concentric_bars.md) · RECIPE_CARD · 预览 1 · 环形与嵌套环形图 / 分组柱状图
- `vivid-5062fb9fcd92d8` [screenshot.cone_vortex](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.cone_vortex.md) · RECIPE_CARD · 预览 1 · 向量场与轨迹
- `vivid-93b30ddd868251` [screenshot.contour_lines_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.contour_lines_3d.md) · RECIPE_CARD · 预览 1 · 等值线 / 折线与训练趋势 / 三维曲面与网格
- `vivid-d7c67575a55acd` [screenshot.correlation_network](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.correlation_network.md) · RECIPE_CARD · 预览 1 · 关系网络
- `vivid-82945bb14191a1` [screenshot.depreciation_area](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.depreciation_area.md) · RECIPE_CARD · 预览 1 · 面积与流带
- `vivid-327761340662f3` [screenshot.fan_violin_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.fan_violin_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵 / 小提琴与分组小提琴 / 扇形预测区间
- `vivid-28668490c956ca` [screenshot.gridded_scatter_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.gridded_scatter_3d.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系 / 三维曲面与网格
- `vivid-9cfd62294c629e` [screenshot.heatmap_slabs_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.heatmap_slabs_3d.md) · RECIPE_CARD · 预览 1 · 热力矩阵 / 三维曲面与网格
- `vivid-69dbd87f780665` [screenshot.hexbin](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.hexbin.md) · RECIPE_CARD · 预览 1 · 六边形密度图
- `vivid-053c5eac571341` [screenshot.horizon](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.horizon.md) · RECIPE_CARD · 预览 1 · 地平线图
- `vivid-e0bac1f11d4c7e` [screenshot.interval_steps](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.interval_steps.md) · RECIPE_CARD · 预览 1 · 阶梯图
- `vivid-f940e8210173e9` [screenshot.isosurface](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.isosurface.md) · RECIPE_CARD · 预览 1 · 体积与等值面
- `vivid-f8bef0b6493d71` [screenshot.layered_area_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.layered_area_3d.md) · RECIPE_CARD · 预览 1 · 面积与流带 / 三维曲面与网格
- `vivid-5387bc74296640` [screenshot.marginal_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.marginal_heatmap.md) · RECIPE_CARD · 预览 1 · 联合与边缘分布 / 热力矩阵
- `vivid-1e5175190b4f2f` [screenshot.mesh_surface_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.mesh_surface_3d.md) · RECIPE_CARD · 预览 1 · 三维曲面与网格
- `vivid-4a64b79e7262e4` [screenshot.nested_donut](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.nested_donut.md) · RECIPE_CARD · 预览 1 · 环形与嵌套环形图
- `vivid-b12d5f8dccc7ec` [screenshot.peak_stacked_area](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.peak_stacked_area.md) · RECIPE_CARD · 预览 1 · 堆叠图 / 面积与流带
- `vivid-6d4c5f519d44e3` [screenshot.polar_area](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.polar_area.md) · RECIPE_CARD · 预览 1 · 极坐标与径向图 / 面积与流带
- `vivid-ca1979a86c69ee` [screenshot.polar_scatter](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.polar_scatter.md) · RECIPE_CARD · 预览 1 · 散点与拟合关系 / 极坐标与径向图
- `vivid-928798c13d5798` [screenshot.polar_step_area](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.polar_step_area.md) · RECIPE_CARD · 预览 1 · 极坐标与径向图 / 面积与流带
- `vivid-1d37dd32d6c648` [screenshot.radial_bars](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.radial_bars.md) · RECIPE_CARD · 预览 1 · 极坐标与径向图 / 分组柱状图
- `vivid-028876126cdef0` [screenshot.radial_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.radial_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵 / 极坐标与径向图
- `vivid-04d33201670a9a` [screenshot.ranked_arcs](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.ranked_arcs.md) · RECIPE_CARD · 预览 1 · 排名变化图
- `vivid-b3d45056302bad` [screenshot.rose](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.rose.md) · RECIPE_CARD · 预览 1 · 极坐标与径向图
- `vivid-2fd8602004be3c` [screenshot.spiral_bubbles_3d](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.spiral_bubbles_3d.md) · RECIPE_CARD · 预览 1 · 三维曲面与网格
- `vivid-93d2a59bc21b91` [screenshot.streamgraph](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.streamgraph.md) · RECIPE_CARD · 预览 1 · 河流图
- `vivid-9057cdb76fe9dc` [screenshot.sunburst](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.sunburst.md) · RECIPE_CARD · 预览 1 · 旭日图
- `vivid-5e49a59f4b7b42` [screenshot.triangle_heatmap](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.triangle_heatmap.md) · RECIPE_CARD · 预览 1 · 热力矩阵
- `vivid-c54fcca45883be` [screenshot.volume](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/screenshot.volume.md) · RECIPE_CARD · 预览 1 · 体积与等值面
- `vivid-784dd48e27f318` [template.sem_violin_pearson](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/template.sem_violin_pearson.md) · RECIPE_CARD · 预览 1 · 多面板组合 / 小提琴与分组小提琴
- `vivid-f7a2ab5b2203cd` [template.shap_contribution](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/template.shap_contribution.md) · RECIPE_CARD · 预览 1 · 多面板组合 / SHAP 与特征贡献
- `vivid-0684bb07880024` [template.shap_dependence](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/cards/template.shap_dependence.md) · RECIPE_CARD · 预览 1 · 多面板组合 / SHAP 与特征贡献
- `vivid-d5d3b15e8f8339` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/advanced.grouped_bar_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 分组柱状图 / 三维曲面与网格
- `vivid-411e182fdc5ecc` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/advanced.multi_y_gradient_hist/reference.jpg) · SUPPORT_ASSET · 预览 1 · 双轴与多轴图 / 直方图
- `vivid-388f0ee1745a81` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/advanced.relief_correlation_heatmap/reference.jpg) · SUPPORT_ASSET · 预览 1 · 热力矩阵
- `vivid-55e2b4908a72db` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.block_surface_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `vivid-4c061aafd0c751` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.chord/reference.jpg) · SUPPORT_ASSET · 预览 1 · 弦图
- `vivid-70856053431e13` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.classified_scatter/reference.jpg) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `vivid-14e636654b8ca4` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.concentric_bars/reference.jpg) · SUPPORT_ASSET · 预览 1 · 环形与嵌套环形图 / 分组柱状图
- `vivid-3713332057df1a` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.cone_vortex/reference.jpg) · SUPPORT_ASSET · 预览 1 · 向量场与轨迹
- `vivid-088248ce9c7e32` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.contour_lines_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 等值线 / 折线与训练趋势 / 三维曲面与网格
- `vivid-12ecb87601cdcb` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.correlation_network/reference.jpg) · SUPPORT_ASSET · 预览 1 · 关系网络
- `vivid-e19db4b78ca650` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.depreciation_area/reference.jpg) · SUPPORT_ASSET · 预览 1 · 面积与流带
- `vivid-a32cd0a8ff9fa3` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.fan_violin_heatmap/reference.jpg) · SUPPORT_ASSET · 预览 1 · 热力矩阵 / 小提琴与分组小提琴 / 扇形预测区间
- `vivid-362abb90e87b0c` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.gridded_scatter_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系 / 三维曲面与网格
- `vivid-20f600ccf164be` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.heatmap_slabs_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 热力矩阵 / 三维曲面与网格
- `vivid-3a509d573c1f61` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.hexbin/reference.jpg) · SUPPORT_ASSET · 预览 1 · 六边形密度图
- `vivid-40d854fdf1f9d6` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.horizon/reference.jpg) · SUPPORT_ASSET · 预览 1 · 地平线图
- `vivid-599a1319e7cb0a` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.interval_steps/reference.jpg) · SUPPORT_ASSET · 预览 1 · 阶梯图
- `vivid-05ec00e9735089` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.isosurface/reference.jpg) · SUPPORT_ASSET · 预览 1 · 体积与等值面
- `vivid-64a66f5551104a` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.layered_area_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 面积与流带 / 三维曲面与网格
- `vivid-3c54c6ed22b46b` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.marginal_heatmap/reference.jpg) · SUPPORT_ASSET · 预览 1 · 联合与边缘分布 / 热力矩阵
- `vivid-d1abbd8f409e86` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.mesh_surface_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `vivid-1f1c7951898f52` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.nested_donut/reference.jpg) · SUPPORT_ASSET · 预览 1 · 环形与嵌套环形图
- `vivid-4911962ae5c5f1` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.peak_stacked_area/reference.jpg) · SUPPORT_ASSET · 预览 1 · 堆叠图 / 面积与流带
- `vivid-38ece430960e90` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.polar_area/reference.jpg) · SUPPORT_ASSET · 预览 1 · 极坐标与径向图 / 面积与流带
- `vivid-5069eb76116416` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.polar_scatter/reference.jpg) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系 / 极坐标与径向图
- `vivid-8cc913e6a6b926` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.polar_step_area/reference.jpg) · SUPPORT_ASSET · 预览 1 · 极坐标与径向图 / 面积与流带
- `vivid-40e75c9f74b795` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.radial_bars/reference.jpg) · SUPPORT_ASSET · 预览 1 · 极坐标与径向图 / 分组柱状图
- `vivid-64c6c8961d1ddb` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.radial_heatmap/reference.jpg) · SUPPORT_ASSET · 预览 1 · 热力矩阵 / 极坐标与径向图
- `vivid-b0a520213ed3b5` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.ranked_arcs/reference.jpg) · SUPPORT_ASSET · 预览 1 · 排名变化图
- `vivid-281f883933ce1e` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.rose/reference.jpg) · SUPPORT_ASSET · 预览 1 · 极坐标与径向图
- `vivid-b5e1d47a3351e5` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.spiral_bubbles_3d/reference.jpg) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `vivid-c7fb1c470b6416` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.streamgraph/reference.jpg) · SUPPORT_ASSET · 预览 1 · 河流图
- `vivid-b9217f9e80224c` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.sunburst/reference.jpg) · SUPPORT_ASSET · 预览 1 · 旭日图
- `vivid-e2ff0afbef6fc5` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.triangle_heatmap/reference.jpg) · SUPPORT_ASSET · 预览 1 · 热力矩阵
- `vivid-508c066a23f418` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/screenshot.volume/reference.jpg) · SUPPORT_ASSET · 预览 1 · 体积与等值面
- `vivid-6838f727ccedc3` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/template.shap_contribution/reference.jpg) · SUPPORT_ASSET · 预览 1 · 多面板组合 / SHAP 与特征贡献
- `vivid-a49b972c85db3e` [reference](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/catalog/sources/template.shap_dependence/reference.jpg) · SUPPORT_ASSET · 预览 1 · 多面板组合 / SHAP 与特征贡献
- `vivid-f73ad12247f616` [coral](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/coral.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `vivid-dbbd52197bb5cf` [blue pink](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/blue-pink.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-0b620c7b10488e` [blue sky](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/blue-sky.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-50621c90743967` [coral teal](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/coral-teal.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-cdbcabab46594d` [ocean breeze](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/ocean-breeze.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-e4fc02c80af5a8` [olive apricot](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/olive-apricot.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-b208db1c53f2bc` [pastel girl](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/pastel-girl.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式
- `vivid-ae27d14ab15ae0` [soft forest](https://github.com/yjz211/vivid-figures-skill/blob/c043f0553c7c3188b1bb8dcbf7db76d2adf98375/docs/images/palettes/soft-forest.pdf) · SUPPORT_ASSET · 预览 2 · 配色与视觉样式 / Forest 效应区间
### figures4papers
来源版本：`f0bb7559abe90f5e1828797126d4d133c1bd47d7`。许可：CC BY-NC 4.0。

- `f4p-d7390f48fca221` [Dispersion motivation](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/Dispersion_motivation.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-e58841e406975d` [Dispersion observation](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/Dispersion_observation.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合
- `f4p-2c6b301f708917` [Dispersion observation distillation](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/Dispersion_observation_distillation.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合
- `f4p-9c7f92b643866a` [ImmunoStruct contrastive](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/ImmunoStruct_contrastive.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-b57d7056584e82` [ImmunoStruct results CEDAR](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/ImmunoStruct_results_CEDAR.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-5679827eba6ddc` [ImmunoStruct results IEDB](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/ImmunoStruct_results_IEDB.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-de87e7f27da125` [ImmunoStruct schematic](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/ImmunoStruct_schematic.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-dbbd87d1af476e` [RNAGenScape schematic](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/RNAGenScape_schematic.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-0ed7646d514b8d` [RNAGenScape teaser](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/RNAGenScape_teaser.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-6d58f7ac7841bb` [VIGIL teaser](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/assets/VIGIL_teaser.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-8bf502e13ce156` [brute force](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Brainteaser/figures/brute_force.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-52caded0a3f18f` [correctness by category](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Brainteaser/figures/correctness_by_category.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-1ca20ecdcf2384` [correctness by subcategory](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Brainteaser/figures/correctness_by_subcategory.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-e5205039921fea` [rewriting](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Brainteaser/figures/rewriting.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-a4f0a3686db990` [selfcorrection math](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Brainteaser/figures/selfcorrection_math.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-95f2e8c63ee37a` [ablation](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_CellSpliceNet/figures/ablation.png) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性
- `f4p-365fa692fdd8d8` [comparison human](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_CellSpliceNet/figures/comparison_human.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-66f142fddc1526` [comparison worm](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_CellSpliceNet/figures/comparison_worm.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-4533ae9251ea6a` [diffusion swiss roll](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Cflows/figures/diffusion_swiss_roll.png) · FIGURE_EXAMPLE · 预览 1 · 三维曲面与网格
- `f4p-d92ec902e1b800` [fig2 comparison GeneRegulatory](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Cflows/figures/fig2_comparison_GeneRegulatory.pdf) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-c7bfc92b5805c8` [fig2 comparison Trajectory](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Cflows/figures/fig2_comparison_Trajectory.pdf) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-641a478e5ac03f` [figX comparison Ablation](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Cflows/figures/figX_comparison_Ablation.pdf) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性
- `f4p-86e028d0a9f2cf` [idea](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Dispersion/figures/idea.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-eaf50935f05b96` [illustration](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_Dispersion/figures/illustration.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-99e2694cf70089` [bars ablation Cancer](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ImmunoStruct/figures/bars_ablation_Cancer.png) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性 / 分组柱状图
- `f4p-eb2509a8afeb21` [bars ablation IEDB](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ImmunoStruct/figures/bars_ablation_IEDB.png) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性 / 分组柱状图
- `f4p-97fd470b02e3ce` [bars comparison Cancer](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ImmunoStruct/figures/bars_comparison_Cancer.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-9bc7ebf4612d6e` [bars comparison IEDB](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ImmunoStruct/figures/bars_comparison_IEDB.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-7b8b84e0f2b4f1` [manifold](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_RNAGenScape/figures/manifold.png) · FIGURE_EXAMPLE · 预览 1 · 三维曲面与网格
- `f4p-b44832a7684c70` [manifold holes](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_RNAGenScape/figures/manifold_holes.png) · FIGURE_EXAMPLE · 预览 1 · 三维曲面与网格
- `f4p-fe9942e9f53095` [results comparison optimization](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_RNAGenScape/figures/results_comparison_optimization.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-35a1cf904b0987` [results comparison speed](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_RNAGenScape/figures/results_comparison_speed.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-6f16029887c7be` [results sweep](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_RNAGenScape/figures/results_sweep.png) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性
- `f4p-0bbfcc5dd7f9a8` [ablation curves](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_VIGIL/figures/ablation_curves.png) · FIGURE_EXAMPLE · 预览 1 · 消融与敏感性
- `f4p-f1e5ddbcc161b3` [comparison posttraining](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_VIGIL/figures/comparison_posttraining.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `f4p-5ec1f5b3c31604` [comparison radar](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_VIGIL/figures/comparison_radar.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `f4p-f41b2bef57d7a7` [concept](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_VIGIL/figures/concept.png) · FIGURE_EXAMPLE · 预览 1 · 机制示意与流程
- `f4p-25b81d41a820af` [composition heatmap](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ophthal_review/figures/composition_heatmap.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `f4p-85b5d7116a5831` [trend by month](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/figure_ophthal_review/figures/trend_by_month.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `f4p-6db85189722888` [SKILL](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/SKILL.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `f4p-29a4149d989cc9` [api](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/references/api.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `f4p-acdceec23753f7` [common patterns](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/references/common-patterns.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `f4p-914ac0d99c0a75` [demos](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/references/demos.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `f4p-17d6f68d121d76` [design theory](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/references/design-theory.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `f4p-9663c5f3ba550d` [tutorials](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/scientific-figure-making/references/tutorials.md) · TUTORIAL · 预览 0 · 标注、图例与排版示例
### Python Graph Gallery
来源版本：`64424bccec3d0340a6dcf7763b37a78e468d45c9`。许可：0BSD at repository level; individual examples may contain third-party content。

- `pgg-7bdc6b6a23ab0b` [evolution ansgar ridgeline](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/evolution-ansgar-ridgeline.gif) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-4c5166778da7ab` [evolution bubble maps earthquakes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/evolution-bubble-maps-earthquakes.gif) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-3ce0b16d7a8f24` [evolution europe map co2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/evolution-europe-map-co2.gif) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-18f2c20c93dffb` [evolution natural disasters](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/evolution-natural-disasters.gif) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-9f2fa73709dea9` [evolution small multiples](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/evolution-small-multiples.gif) · FIGURE_EXAMPLE · 预览 1 · 多面板组合
- `pgg-deb4acc7c3ebab` [gapminder 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/gapminder-1.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-00b85d16382e74` [gapminder 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/gapminder-2.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-9425bea7e2ec10` [mercator](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/mercator.gif) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-03772fadb13ea4` [scatter](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/scatter.gif) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-f226cc643f0c7c` [volcano](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/volcano.gif) · FIGURE_EXAMPLE · 预览 1 · 火山图
- `pgg-32914102773989` [web animated line chart with text 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-1.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-6f4f586c618ac1` [web animated line chart with text 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-2.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-12e18cbd7302e4` [web animated line chart with text 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-3.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-433d40e00991e8` [web animated line chart with text 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-4.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-b3b645c665951d` [web animated line chart with text 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-5.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-88034fb26d4631` [web animated line chart with text 6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animated-line-chart-with-text-6.gif) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 动态图
- `pgg-25f1a8ac1835f8` [web animation with text](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-9ac871bba98b91` [web animation with text2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text2.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-6814e30f942f30` [web animation with text3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text3.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-ccd8d98a3d54ee` [web animation with text4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text4.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-37a19e43cf9eac` [web animation with text5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text5.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-1f73a5b9963f83` [web animation with text6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text6.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-88cf3428afcb98` [web animation with text7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text7.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-a645b383c3e114` [web animation with text8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/animations/web-animation-with-text8.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-778570d7233af2` [100 Color names python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/100_Color_names_python.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-5ff12ea06e2305` [101 seaborn palette1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-5883512d795abd` [101 seaborn palette2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-89869d782606b5` [101 seaborn palette3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-e8e931f70efbc3` [101 seaborn palette4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-39e220eb590e0e` [101 seaborn palette5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette5.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-7e5e04c869936f` [101 seaborn palette6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/101_seaborn_palette6.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-46c857c325ae12` [104 seaborn themes1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes1-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-d3ae9c53d30ac4` [104 seaborn themes1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-d4e0d1440061bd` [104 seaborn themes2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes2-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-76dcb86c1bcb09` [104 seaborn themes2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-973ef326500835` [104 seaborn themes3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes3-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-f178d9ecb738dc` [104 seaborn themes3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-b52defe6396094` [104 seaborn themes4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes4-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-9dabb0a38bebe1` [104 seaborn themes4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-284741ba79c3fd` [104 seaborn themes5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes5-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-195897fc278be6` [104 seaborn themes5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/104_seaborn_themes5.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-26e8569a5bd046` [106 seaborn style on plt1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/106_seaborn_style_on_plt1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-654523afbba951` [106 seaborn style on plt2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/106_seaborn_style_on_plt2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-14143e6a358818` [10 barplot with number of observations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/10_barplot_with_number_of_observations.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-2accd73bc20756` [110 Basic Correlogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/110_Basic_Correlogram.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-33200a85982541` [111 Correlogram custom1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom1.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-8a208f9fd216e6` [111 Correlogram custom2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom2.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-6519f9787623ab` [111 Correlogram custom3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom3.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-ec39f8ceba5d06` [111 Correlogram custom4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom4.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-381f38184199ba` [111 Correlogram custom5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom5.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-ccbc197f66d885` [111 Correlogram custom6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom6.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-77974321034135` [111 Correlogram custom7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/111_Correlogram_custom7.png) · FIGURE_EXAMPLE · 预览 1 · 成对关系矩阵
- `pgg-1fba0e96c039fe` [120 Basic lineplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/120_Basic_lineplot1.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-2c97836c4ee126` [120 Basic lineplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/120_Basic_lineplot2.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-b2f80da2b97f45` [120 Basic lineplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/120_Basic_lineplot3.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-80922f7cd10f1f` [121 Custom line plot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/121_Custom_line_plot1.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-cc8f0785d8cb50` [121 Custom line plot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/121_Custom_line_plot2.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-0936d566bb460c` [121 Custom line plot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/121_Custom_line_plot3.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-9d697e8fa49895` [121 Custom line plot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/121_Custom_line_plot4.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-5de04f36082108` [121 Custom line plot5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/121_Custom_line_plot5.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-38a6f92e59a499` [122 Multiple line plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/122_Multiple_line_plot.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-b5ac3b4934ef89` [123 Highlight a line](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/123_Highlight_a_line.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-dabf713e2498dd` [124 Spaghetti plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/124_Spaghetti_plot.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-8a51f164ca18f8` [125 Lineplot small multiple](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/125_Lineplot_small_multiple.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-78b88e72186c8c` [125 Lineplot small multiple v2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/125_Lineplot_small_multiple_v2.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-9a7195aa60948d` [12 grouped barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/12_grouped_barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-44f297a7776fd8` [12 stacked barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/12_stacked_barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-445f921839ccca` [12 stacked percent barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/12_stacked_percent_barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-8969c131ffb2a6` [130 Basic Matplotlib Scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/130_Basic_Matplotlib_Scatterplot.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-44693db31022b4` [131 Custom Matplotlib Scatterplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/131_Custom_Matplotlib_Scatterplot1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-a71ef728f4618a` [131 Custom Matplotlib Scatterplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/131_Custom_Matplotlib_Scatterplot2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-15ec898800e5bf` [131 Custom Matplotlib Scatterplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/131_Custom_Matplotlib_Scatterplot3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-abf5d0d49d4705` [131 Custom Matplotlib Scatterplot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/131_Custom_Matplotlib_Scatterplot4.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-778d5bdf43cef6` [131 Custom Matplotlib Scatterplot5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/131_Custom_Matplotlib_Scatterplot5.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-269e578d10a22c` [132 basic connected scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/132-basic-connected-scatterplot.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-3c11029c45395d` [132 Matplotlib connected scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/132_Matplotlib-connected-scatterplot.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-07c038aaf53235` [134 Fighting overplotting1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting1.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-5f311ad02deb69` [134 Fighting overplotting10](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting10.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-631a01f88f2bb7` [134 Fighting overplotting11](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting11.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-01acbd37ad1f03` [134 Fighting overplotting12](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting12.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-1dd4ac96576f14` [134 Fighting overplotting2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting2.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-14367e6a8e047d` [134 Fighting overplotting3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting3.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-c2c290684d4519` [134 Fighting overplotting4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting4.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-a78ec6f4238539` [134 Fighting overplotting5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting5.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-a7684ecc0b149f` [134 Fighting overplotting6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting6.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-8a7dbada1e1eea` [134 Fighting overplotting7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting7.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-0ae4e3df7e5382` [134 Fighting overplotting8 300x99](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting8-300x99.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-017fcc52c4181b` [134 Fighting overplotting8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting8.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-72f2bd1df46fb6` [134 Fighting overplotting9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/134_Fighting_overplotting9.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-21b127f3553b2b` [140 basic pieplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/140_basic_pieplot1.png) · FIGURE_EXAMPLE · 预览 1 · 饼图
- `pgg-882c0f719f16c4` [140 basic pieplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/140_basic_pieplot2.png) · FIGURE_EXAMPLE · 预览 1 · 饼图
- `pgg-f651a19eaad59c` [150 Parrallele plot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/150_Parrallele_plot_with_pandas.png) · FIGURE_EXAMPLE · 预览 1 · 平行坐标
- `pgg-cff77af57ffd6f` [160 Basic donut plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/160_Basic_donut_plot.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-667da417bbbc62` [161 custom donut plot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot1.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-7d702c10dd6fe1` [161 custom donut plot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot2.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-d2c9b82ed33785` [161 custom donut plot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot3.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-70108510d01c88` [161 custom donut plot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot4.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-6ebb3dc154f2ea` [161 custom donut plot5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot5.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-a5eb0ad608dcd2` [161 custom donut plot6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/161_custom_donut_plot6.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-eaa2df2e10c3a7` [162 Background color donut](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/162_Background_color_donut.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 环形与嵌套环形图
- `pgg-0477deb7faaab3` [163 Double Donut Chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/163_Double_Donut_Chart.png) · FIGURE_EXAMPLE · 预览 1 · 环形与嵌套环形图
- `pgg-85907370e0ba1d` [170 Basic Venn Diagram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/170_Basic_Venn_Diagram.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-a0f60fa29ce75b` [171 Basic Venn 3 groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/171_Basic_Venn_3-groups.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-27ef83e864e327` [172 custom venn diagram1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/172_custom_venn_diagram1.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-5fa921ac316c95` [172 custom venn diagram2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/172_custom_venn_diagram2.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-e4e8601431d4bc` [172 custom venn diagram3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/172_custom_venn_diagram3.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-13afd581e46b0e` [173 elaborated Venn diagram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/173_elaborated_Venn_diagram.png) · FIGURE_EXAMPLE · 预览 1 · Venn 与集合交集
- `pgg-bf71481667d2cf` [174 Change Background color venn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/174_Change_Background_color_venn.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / Venn 与集合交集
- `pgg-84668074354a5b` [180 Basic lolipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/180_Basic_lolipop_plot.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-8b8b8dfff49409` [180 Basic lolipop plot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/180_Basic_lolipop_plot2.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-481897db0c3c47` [180 Basic lolipop plot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/180_Basic_lolipop_plot3.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-70886653fa8c27` [180 Basic lolipop plot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/180_Basic_lolipop_plot4.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-523a10bc91b358` [181 custom lolliplot 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_1.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-5876023909b8e7` [181 custom lolliplot 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_2.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-6cd230d5382a53` [181 custom lolliplot 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_3.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-d55c92167db652` [181 custom lolliplot 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_4.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-2e3bafc42b08a1` [181 custom lolliplot 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_5.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-c1c32702321c6f` [181 custom lolliplot 6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/181_custom_lolliplot_6.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-81be39a4dc1332` [182 vertical lolipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/182_vertical_lolipop_plot.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-0cc85c8be3c8ce` [183 highlight a group in lolipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/183_highlight_a_group_in_lolipop_plot.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-1f6e25baf483db` [184 lolipop plot with 2 groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/184_lolipop_plot_with_2_groups.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-c26cdb87d8c470` [185 lolipop plot with conditional color](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/185_lolipop_plot_with_conditional_color.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图 / 配色与视觉样式
- `pgg-7b67a47868fc65` [190 Custom title1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-867849c0fd8612` [190 Custom title2 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title2-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-83027b86a2b46c` [190 Custom title2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-e183b53e0d35f0` [190 Custom title3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-1582804ca47afe` [190 Custom title4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-b959408c8e30f8` [190 Custom title5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-fc0a1d2533646f` [190 Custom title6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title6.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-866003ab070860` [190 Custom title7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title7.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-f49c1580e8fe8a` [190 Custom title8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title8.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-700239f47d5267` [190 Custom title9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/190_Custom_title9.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-b5666cd70d0d1d` [191 Custom axis1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-61dce432e32587` [191 Custom axis2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-64b82c3f343688` [191 Custom axis3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-c2151975f6744e` [191 Custom axis4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-1d6747d96b3b7a` [191 Custom axis5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-3b03928b109d7f` [191 Custom axis6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/191_Custom_axis6.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-ef43425e7d48b0` [192 increase margin1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/192_increase_margin1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-15e1bf862da410` [192 increase margin2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/192_increase_margin2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-7b3d8d72a7a51b` [192 increase margin3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/192_increase_margin3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-e37f65ef4247ed` [192 increase margin4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/192_increase_margin4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-c952269f9c4a51` [193 annotate1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-c0f5c0b115c422` [193 annotate2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-5aa1e3d9786c6d` [193 annotate3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-080bb28a8abda4` [193 annotate4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-893fe23df0af3e` [193 annotate5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-e04e2fae570d86` [193 annotate6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate6.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-867ce99bd1ca7d` [193 annotate7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/193_annotate7.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-b014417d8389b3` [194 matplotlib subplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-fc274809903802` [194 matplotlib subplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-fc74568ab5402b` [194 matplotlib subplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-ae836fcefe2c18` [194 matplotlib subplot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-9eb1d2fb7476b9` [194 matplotlib subplot5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-1ba71ef6a91160` [194 matplotlib subplot6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot6.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-1a8c203f952968` [194 matplotlib subplot8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot8.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-444b0c3665a241` [194 matplotlib subplot9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/194_matplotlib_subplot9.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-49dfeb26e52fa7` [196 matplotlib call one colour1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-03b5cb5a541a3e` [196 matplotlib call one colour2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-9fe3a037659862` [196 matplotlib call one colour3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-bcc3977412a014` [196 matplotlib call one colour4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-4e9d9f61802137` [196 matplotlib call one colour5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour5.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-32cdcf1ff66046` [196 matplotlib call one colour6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/196_matplotlib_call_one_colour6.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-0fb01ed5795a91` [197 matplotlib color palette1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-4ec38a82117afb` [197 matplotlib color palette2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-133156802c0635` [197 matplotlib color palette3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-fc95ab74440047` [197 matplotlib color palette4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-0e12076529bb2f` [197 matplotlib color palette5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette5.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-e74bbb6282d069` [197 matplotlib color palette9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/197_matplotlib_color_palette9.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-7d5bf93f9928d4` [199 matplotlib style sheets 538 full](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/199-matplotlib-style-sheets-538-full.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-dca65078ddf529` [199 matplotlib style sheets 538](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/199-matplotlib-style-sheets-538.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-ec015fa730e607` [199 Matplotlib style sheet](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/199_Matplotlib_style_sheet.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-c1ab1ff2e1068f` [1 basic barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/1_basic_barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-467f5b8f45bde9` [200 Basic Treemap with squarify](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/200_Basic_Treemap_with_squarify.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-1016ec22774992` [201 Custom Treemap1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/201_Custom_Treemap1.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-d8bcd89cdd0087` [202 Treemap map color to size](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/202_Treemap_map_color_to_size.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图 / 配色与视觉样式 / 地理与分区地图
- `pgg-d5fe256ad96d5b` [20 Basic Histogram seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/20_Basic_Histogram_seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-b8002ab4e243ad` [20 Basic Histogram seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/20_Basic_Histogram_seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-9d2f73566db304` [21 Display Rug and distribution on hist1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/21_Display_Rug_and_distribution_on_hist1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-a428c2ddd162ec` [21 Display Rug and distribution on hist2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/21_Display_Rug_and_distribution_on_hist2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-52c532998b6177` [21 Display Rug and distribution on hist3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/21_Display_Rug_and_distribution_on_hist3.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-67172c165511c8` [21 Display Rug and distribution on hist4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/21_Display_Rug_and_distribution_on_hist4.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-c6c64044aca6fe` [220 Sankey Matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/220_Sankey_Matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 桑基与流向图
- `pgg-4afc4c62bfcf87` [23 90degree rotated histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/23-90degree-rotated-histogram.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-0f2015ebad1d4b` [230 Chord with plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/230_Chord_with_plotly.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-a88648db86dde2` [231 Chord Bokeh](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/231_Chord_Bokeh.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-d6f0c1d39a1d6f` [240 basic area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/240_basic_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-79d391cfaae5f3` [241 custom area chart1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/241_custom_area_chart1.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-df5a3174c90133` [241 custom area chart2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/241_custom_area_chart2.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-a74cfc68506cf1` [241 custom area chart3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/241_custom_area_chart3.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-18e1c290490ed9` [242 area chart and faceting](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/242_area_chart_and_faceting.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带 / 多面板组合
- `pgg-697e564db5f586` [243 another area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/243_another_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-996b59dbd4ca46` [24 Histogram with boxplot on top](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/24_Histogram_with_boxplot_on_top.png) · FIGURE_EXAMPLE · 预览 1 · 直方图 / 箱线图
- `pgg-10f5f77595d16a` [250 basic stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/250_basic_stacked_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带
- `pgg-85e9a97c5a9cdc` [251 seaborn style on stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/251_seaborn_style_on_stacked_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-4dd8aea842ad5f` [252 baseline and stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/252_baseline_and_stacked_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带
- `pgg-5566478eaa842c` [253 control the color in stacked area chart 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253-control-the-color-in-stacked-area-chart-1.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-3044f8d696f64d` [253 control the color in stacked area chart 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253-control-the-color-in-stacked-area-chart-2.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-3baa2446baecc1` [253 control the color in stacked area chart 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253-control-the-color-in-stacked-area-chart-3.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-2525a7c3493a0d` [253 control the color in stacked area chart 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253-control-the-color-in-stacked-area-chart-4.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-c4f3589825d874` [253 control the color in stacked area chart 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253-control-the-color-in-stacked-area-chart-5.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-58fc856ba854d9` [253 color and stacked area chart1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253_color_and_stacked_area_chart1.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-78eb89d7f48178` [253 color and stacked area chart2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/253_color_and_stacked_area_chart2.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-caf1b7786099a9` [254 pandas stacked area chart2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/254_pandas_stacked_area_chart2.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带
- `pgg-064379c5ba6456` [255 percent stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/255_percent_stacked_area_chart.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带
- `pgg-9e8dee90cfa857` [25 Histogram of several variables1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/25_Histogram_of_several_variables1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-38888e7849cb7a` [25 Histogram of several variables2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/25_Histogram_of_several_variables2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-97514d741114f9` [260 basic wordcloud 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/260-basic-wordcloud-1.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-44a30436ff3283` [261 custom python wordcloud 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/261-custom-python-wordcloud-1.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-75a97020500d4e` [261 custom python wordcloud 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/261-custom-python-wordcloud-2.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-0cb5ce3b6b1106` [261 custom python wordcloud 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/261-custom-python-wordcloud-3.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-59e93a4562c165` [261 custom python wordcloud 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/261-custom-python-wordcloud-4.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-df4dda9e7279ed` [262 wordcloud with specific shape 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/262-wordcloud-with-specific-shape-1.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-93a7cb7050adc1` [262 wordcloud with specific shape 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/262-wordcloud-with-specific-shape-2.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-47ed9a101af58d` [263 alice wordcloud](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/263_alice_wordcloud.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-103bd966c48f8b` [263 parrot wordcloud](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/263_parrot_wordcloud.png) · FIGURE_EXAMPLE · 预览 1 · 词云
- `pgg-c76b72c5d0aaff` [270 Basic Bubble plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/270_Basic_Bubble_plot.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-26c1087344f75a` [271 Bubble plot customization1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/271_Bubble_plot_customization1.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-25eefb070658a9` [271 Bubble plot customization2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/271_Bubble_plot_customization2.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-40f07c4b5e09f9` [271 Bubble plot customization3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/271_Bubble_plot_customization3.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-b4e3957e21fca5` [271 Bubble plot customization4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/271_Bubble_plot_customization4.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-78d4f67969c2a8` [271 Bubble plot customization5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/271_Bubble_plot_customization5.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-cf633b8077aaa4` [272 Bubble plot with mapped color](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/272_Bubble_plot_with_mapped_color.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图 / 配色与视觉样式
- `pgg-98ff07cc2c2878` [281 basic map with basemap1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap1.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-ab770cc630f161` [281 basic map with basemap2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap2.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-eb43e05f313b91` [281 basic map with basemap3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap3.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-58a2c04e68b24c` [281 basic map with basemap4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap4.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-3abef26385f48b` [281 basic map with basemap5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap5.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-ca913d5b3f70f7` [281 basic map with basemap6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281-basic-map-with-basemap6.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-470e33615cda62` [281 First Basemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/281_First-Basemap.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-5e48d15deecf9e` [282 Custom Basemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/282_Custom_Basemap.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-0bda4296fec720` [283 Setbounding1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/283_Setbounding1.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-487026c0c09bdb` [284 Basemap Projections1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections1.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-b8365cc79f644c` [284 Basemap Projections2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections2.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-55a8ca982ce1ac` [284 Basemap Projections3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections3.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-c8f629ceba988b` [284 Basemap Projections4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections4.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-47cc7c37879191` [284 Basemap Projections5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections5.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-3c2d83f895fbf8` [284 Basemap Projections6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/284_Basemap_Projections6.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-ece0aa5d080542` [285 Back Layout1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/285_Back_Layout1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-b1d1896a9c341c` [285 Back Layout2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/285_Back_Layout2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-9bafcc77e10bd8` [285 Back Layout3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/285_Back_Layout3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-a0e5b7f5e215b5` [285 Back Layout4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/285_Back_Layout4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-cf9a1870470acd` [285 Back Layout5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/285_Back_Layout5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-f92625195a78cd` [286 boundaries1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/286_boundaries1.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-9032d5ba906bef` [286 boundaries2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/286_boundaries2.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-7a26199229d984` [286 boundaries3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/286_boundaries3.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-8e729906b3f7d1` [288 basic map folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/288_basic_map_folium.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图 / 地理与分区地图
- `pgg-6d124d6c8cfe49` [292 Chloro folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/292_Chloro_folium.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-4d1320368bf713` [2 horizontal barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/2_horizontal_barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-4190fc9ee7a757` [300 draw a connection line1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/300-draw-a-connection-line1.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-7df5eb04774942` [300 draw a connection line2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/300-draw-a-connection-line2.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-c0c0497744b332` [300 draw a connection line3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/300-draw-a-connection-line3.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-d7a741f8e48231` [30 Basic Box seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/30_Basic_Box_seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-99908d85f1a4ce` [30 Basic Box seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/30_Basic_Box_seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-d408dac95eb019` [30 Basic Box seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/30_Basic_Box_seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-09b0f0eb90a0d7` [31 horizontal boxplot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/31-horizontal-boxplot-with-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-6ce13833d31477` [310 basic map with markers 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/310-basic-map-with-markers-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-0d7d1e36648bbc` [310 basic map with markers 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/310-basic-map-with-markers-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-a72af292f3f2d7` [310 basic map with markers 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/310-basic-map-with-markers-3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-813575d1bfeecb` [310 basic bubblemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/310_basic_bubblemap.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-768fe2a95d4920` [312 add markers on folium map1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/312-add-markers-on-folium-map1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 变形统计地图 / 地理与分区地图
- `pgg-68dcabb45fd99e` [312 add markers on folium map2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/312-add-markers-on-folium-map2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 变形统计地图 / 地理与分区地图
- `pgg-180a2d01c556ba` [312 Markers on folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/312_Markers_on_folium.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 变形统计地图
- `pgg-f3f1f28be30a11` [313 Bubble on folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/313_Bubble_on_folium.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图 / 气泡图
- `pgg-5c7fed4a2f0441` [315 a world map of surf tweets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/315-a-world-map-of-surf-tweets.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-347b0f35c65144` [315 Tweet Surf Bubble map1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/315_Tweet_Surf_Bubble_map1.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图 / 地理与分区地图
- `pgg-d8781dde17de9b` [31 Horizontal Boxplot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/31_Horizontal_Boxplot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-81c2d9209b5161` [320 Network start simple](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/320_Network_start_simple.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-54068df45b664b` [321 Network custom look1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/321_Network_custom_look1.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-101e4fba0588dc` [321 Network custom look2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/321_Network_custom_look2.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-8166a804fe2c4c` [321 Network custom look3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/321_Network_custom_look3.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-faa1dadf7fe836` [321 Network custom look4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/321_Network_custom_look4.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-31ce5aa44f2b4a` [322 Network layout1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/322_Network_layout1.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 标注、图例与排版示例
- `pgg-8bfb1dc97de371` [322 Network layout2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/322_Network_layout2.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 标注、图例与排版示例
- `pgg-72fbda40c4069f` [322 Network layout3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/322_Network_layout3.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 标注、图例与排版示例
- `pgg-fda129cde577cb` [322 Network layout4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/322_Network_layout4.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 标注、图例与排版示例
- `pgg-aaab342790b0e9` [322 Network layout5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/322_Network_layout5.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 标注、图例与排版示例
- `pgg-5b6ae84fe7cb86` [323 Network direction1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/323_Network_direction1.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-ffccd85f4dbe0f` [323 Network direction2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/323_Network_direction2.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-dcf3fb6202ff7b` [324 Network mapcolor1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/324_Network_mapcolor1.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-d33b290eb8bb1b` [324 Network mapcolor2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/324_Network_mapcolor2.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-c6d29adf712c86` [325 Network mapcolorttoedge1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/325_Network_mapcolorttoedge1.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-40fbf3f7a5d867` [325 Network mapcolorttoedge2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/325_Network_mapcolorttoedge2.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-5fe84be3ddd165` [326 Network background color](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/326_Network_background_color.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络 / 配色与视觉样式
- `pgg-ab09fe8d6b7e26` [327 Network from correlation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/327_Network_from_correlation.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-3a6f51100456fe` [32 Custom Boxplot Appearance Seaborn1 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/32_Custom_Boxplot_Appearance_Seaborn1-1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-12cb9df61fcd76` [32 Custom Boxplot Appearance Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/32_Custom_Boxplot_Appearance_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-416d10081dbcd2` [32 Custom Boxplot Appearance Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/32_Custom_Boxplot_Appearance_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-4fce88f7c7b5ab` [32 Custom Boxplot Appearance Seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/32_Custom_Boxplot_Appearance_Seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-ef8f390d94d1f7` [33 Custom Boxplot color Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/33_Custom_Boxplot_color_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 配色与视觉样式
- `pgg-4fd3feb24bda61` [33 Custom Boxplot color Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/33_Custom_Boxplot_color_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 配色与视觉样式
- `pgg-c946b7257ddeda` [33 Custom Boxplot color Seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/33_Custom_Boxplot_color_Seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 配色与视觉样式
- `pgg-762a40532fb1a9` [33 Custom Boxplot color Seaborn4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/33_Custom_Boxplot_color_Seaborn4.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 配色与视觉样式
- `pgg-1d61538a82f07d` [33 Custom Boxplot color Seaborn5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/33_Custom_Boxplot_color_Seaborn5.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 配色与视觉样式
- `pgg-8f72a8c778e2de` [34 Grouped Boxplot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/34_Grouped_Boxplot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-b097f804461d91` [35 Specific order Boxplot Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/35_Specific_order_Boxplot_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-e265b6d8e0a007` [35 Specific order Boxplot Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/35_Specific_order_Boxplot_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-36b88f454dc447` [365 data science banner](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/365_data_science_banner.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-eb0ff24d9eef58` [36 Boxplot with Jitter Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/36_Boxplot_with_Jitter_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图 / 样本散点与蜂群
- `pgg-adc5851df38fc6` [370 3D scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/370_3D_scatterplot.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 三维曲面与网格
- `pgg-628118fad89098` [371 3D Surface plot volcano 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/371_3D_Surface_plot_volcano_1.png) · FIGURE_EXAMPLE · 预览 1 · 火山图 / 三维曲面与网格
- `pgg-d9d47f98c99fe4` [371 3D Surface plot volcano 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/371_3D_Surface_plot_volcano_2.png) · FIGURE_EXAMPLE · 预览 1 · 火山图 / 三维曲面与网格
- `pgg-7aad2dcc13a205` [371 3D Surface plot volcano 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/371_3D_Surface_plot_volcano_3.png) · FIGURE_EXAMPLE · 预览 1 · 火山图 / 三维曲面与网格
- `pgg-6ea52d30c05277` [371 3D Surface plot volcano 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/371_3D_Surface_plot_volcano_4.png) · FIGURE_EXAMPLE · 预览 1 · 火山图 / 三维曲面与网格
- `pgg-190b5710c83d4e` [372 3D PCA result](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/372_3D_PCA_result.png) · FIGURE_EXAMPLE · 预览 1 · 嵌入与降维 / 三维曲面与网格
- `pgg-8adfb2d54bbea3` [38 Number of obs on boxplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/38_Number_of_obs_on_boxplot_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-42b192958b28af` [390 basic Radarchart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/390_basic_Radarchart.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `pgg-ea2f2d64c52c0d` [391 Several indiv Radarchart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/391_Several_indiv_Radarchart.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `pgg-8f4db539ec0f61` [393 Faceting and Radarchart 300x80](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/393_Faceting_and_Radarchart-300x80.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图 / 多面板组合
- `pgg-7dc83f1f829b3a` [393 Faceting and Radarchart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/393_Faceting_and_Radarchart.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图 / 多面板组合
- `pgg-5742de1210378b` [393 Faceting and Radarchart2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/393_Faceting_and_Radarchart2.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图 / 多面板组合
- `pgg-ebb4d76b706689` [39 Bad boxplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/39_Bad_boxplot1.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-d106e6f93b3429` [39 Bad boxplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/39_Bad_boxplot2.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-82bc0d3d15e889` [39 Bad boxplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/39_Bad_boxplot3.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-58eec592297c45` [39 Bad boxplot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/39_Bad_boxplot4.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-084a5a6ddab52e` [3 control color barplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/3_control_color_barplot1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-21321b4949e736` [3 control color barplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/3_control_color_barplot2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-254fd3fd931e19` [3 control color barplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/3_control_color_barplot3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-2504034c76fd6c` [3 control color barplot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/3_control_color_barplot4.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-028f68b0b0a6fb` [3d is bad](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/3d_is_bad.png) · FIGURE_EXAMPLE · 预览 1 · 三维曲面与网格
- `pgg-f64ac8bdd425da` [400 Basic Dendrogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/400_Basic_Dendrogram.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-1950fb504060a5` [401 custom Dendrogram1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram1.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-279042b94977b1` [401 custom Dendrogram2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram2.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-8bf7e28bf0dc12` [401 custom Dendrogram3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram3.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-ce1a33cdc2e86a` [401 custom Dendrogram4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram4.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-7d0c02a906a937` [401 custom Dendrogram5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram5.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-0802ab7f695601` [401 custom Dendrogram6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram6.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-8023e8bee29074` [401 custom Dendrogram7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/401_custom_Dendrogram7.png) · FIGURE_EXAMPLE · 预览 1 · 层次树与树状聚类
- `pgg-63dd6ae96dd0ee` [402 leaf labal color](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/402_leaf_labal_color.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-9145c57130a992` [404 Dendro and heatmap1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-07d5412b2031d8` [404 Dendro and heatmap10](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap10.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-b917965b9ee09c` [404 Dendro and heatmap11](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap11.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-394db8b6f7c517` [404 Dendro and heatmap12](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap12.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-fa64918b8d9df4` [404 Dendro and heatmap2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-581112de2609f6` [404 Dendro and heatmap3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap3.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-418733f98806fe` [404 Dendro and heatmap4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap4.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-00384507664175` [404 Dendro and heatmap5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap5.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-6378de40af571f` [404 Dendro and heatmap6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap6.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-5219be56e06d3a` [404 Dendro and heatmap7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap7.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-213a86352649b3` [404 Dendro and heatmap8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap8.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-65a0ec91d67ad3` [404 Dendro and heatmap9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/404_Dendro_and_heatmap9.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-47f545ee3f4a34` [405 Dendro and heatmap and rowcolor](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/405_Dendro_and_heatmap_and_rowcolor.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-2fee3d953e7681` [406 chord diagram mne1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/406-chord-diagram_mne1.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-0c6a6eca47f2e5` [406 chord diagram mne2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/406-chord-diagram_mne2.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-5d8e3df537ca48` [406 chord diagram mne3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/406-chord-diagram_mne3.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-e940bfa82d3e50` [40 Basic Scatterplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/40_Basic_Scatterplot_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-a6155c7245deb0` [40 Scatterplot with regression fit seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/40_Scatterplot_with_regression_fit_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-d13768531b1069` [41 Scatterplot change marker color seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/41_Scatterplot_change_marker_color_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例 / 配色与视觉样式
- `pgg-6f24c7dcb7fbb7` [41 Scatterplot change marker shape seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/41_Scatterplot_change_marker_shape_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-6309d933c535e3` [42 Scatterplot custom linear fit seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/42_Scatterplot_custom_linear_fit_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-e447dc4fc84369` [43 use categorical variable to color scatterplot seaborn pypalettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/43-use-categorical-variable-to-color-scatterplot-seaborn-pypalettes.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 配色与视觉样式
- `pgg-829f8878df898b` [43 seaborn map color to a avariable1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/43_seaborn_map_color_to_a_avariable1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-12af27c6e50f68` [43 seaborn map color to a avariable2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/43_seaborn_map_color_to_a_avariable2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-bb9da173d57775` [43 seaborn map color to a avariable3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/43_seaborn_map_color_to_a_avariable3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-e3616c72fec28c` [43 seaborn map color to a avariable4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/43_seaborn_map_color_to_a_avariable4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-3f6e328c2904c2` [44 seaborn control axis limits](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/44_seaborn_control_axis_limits.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-7c456816176779` [45 set color of each point in scatterplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/45_set_color_of_each_point_in_scatterplot_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 配色与视觉样式
- `pgg-d2849a6a588206` [46 add text annotation scatterplot seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/46_add_text_annotation_scatterplot_seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-90ba51d4f9c5b3` [46 add text annotation scatterplot seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/46_add_text_annotation_scatterplot_seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-fa66748b2de2f7` [46 add text annotation scatterplot seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/46_add_text_annotation_scatterplot_seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-65552df8fcc4c1` [47 faceted scatter plot with seaborn 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/47-faceted-scatter-plot-with-seaborn-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-df8653b5f31f1b` [47 faceted scatter plot with seaborn 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/47-faceted-scatter-plot-with-seaborn-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-9f2bf356eab60d` [4 add title and axe labels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/4_add_title_and_axe_labels.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-89b3f94cad5642` [500 network chart with edge bundling](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/500-network-chart-with-edge-bundling.png) · FIGURE_EXAMPLE · 预览 1 · 关系网络
- `pgg-1dd402f370555f` [501 parallel plot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/501-parallel-plot-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 平行坐标
- `pgg-ee15240f9ac63d` [502 violinplot and swarmplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/502-violinplot-and-swarmplot.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴 / 样本散点与蜂群
- `pgg-035a7e4eb4f740` [503 waffle chart introduction 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/503-waffle-chart-introduction-1.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-55ccac786c8caa` [503 waffle chart introduction 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/503-waffle-chart-introduction-2.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-fb3247ce3bf77d` [503 waffle chart introduction 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/503-waffle-chart-introduction-3.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-b6ce8ac9891c7d` [504 histogram with colored tails](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/504-histogram-with-colored-tails.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-aabbd6220733f0` [505 Introduction to swarm plot in seaborn 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/505-Introduction-to-swarm-plot-in-seaborn-1.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-0e89fb873e3b56` [505 Introduction to swarm plot in seaborn 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/505-Introduction-to-swarm-plot-in-seaborn-2.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-699cd0948e4b41` [505 Introduction to swarm plot in seaborn 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/505-Introduction-to-swarm-plot-in-seaborn-3.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-d7334db6ea3903` [506 histogram with small mutliples](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/506-histogram-with-small-mutliples.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-e37e1a160a4277` [508 connected scatter plot seaborn 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/508-connected-scatter-plot-seaborn-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-c3ca9c1453bdfe` [508 connected scatter plot seaborn 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/508-connected-scatter-plot-seaborn-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-4caf9189c91edd` [508 connected scatter plot seaborn 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/508-connected-scatter-plot-seaborn-3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-c1426257d7cb44` [508 connected scatter plot seaborn 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/508-connected-scatter-plot-seaborn-4.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-d36f5979abf9dd` [509 introduction to swarm plot in matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/509-introduction-to-swarm-plot-in-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-c9fcf40b7fdfc5` [509 introduction to swarm plot in matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/509-introduction-to-swarm-plot-in-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-2f9926f1918061` [509 introduction to swarm plot in matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/509-introduction-to-swarm-plot-in-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-b6f243a2e3ae85` [50 Basic Violin seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/50_Basic_Violin_seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-edda74b5e9d203` [50 Basic Violin seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/50_Basic_Violin_seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-17ef7607ce4c4e` [50 Basic Violin seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/50_Basic_Violin_seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-fde3a1779f5de5` [511 interactive scatterplot with plotly 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/511-interactive-scatterplot-with-plotly-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-115dc1cf1daf3c` [511 interactive scatterplot with plotly 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/511-interactive-scatterplot-with-plotly-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-b95f8e436acb9e` [511 interactive scatterplot with plotly 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/511-interactive-scatterplot-with-plotly-3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-3f6a62dd610644` [513 add logo matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/513-add-logo-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-c52d8c6dfe4ea9` [514 interactive line chart plotly 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/514-interactive-line-chart-plotly-1.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-aadf789bd8ac93` [514 interactive line chart plotly 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/514-interactive-line-chart-plotly-2.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-9580addca5d019` [514 interactive line chart plotly 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/514-interactive-line-chart-plotly-3.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-9a19b34bd1d3e1` [515 intro pca graph python 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/515-intro-pca-graph-python-1.png) · FIGURE_EXAMPLE · 预览 1 · 嵌入与降维
- `pgg-6eb7445327d199` [515 intro pca graph python 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/515-intro-pca-graph-python-2.png) · FIGURE_EXAMPLE · 预览 1 · 嵌入与降维
- `pgg-4c3accb22c0780` [515 intro pca graph python 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/515-intro-pca-graph-python-3.png) · FIGURE_EXAMPLE · 预览 1 · 嵌入与降维
- `pgg-c758bdc72e5329` [516 line chart with annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/516-line-chart-with-annotations.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 折线与训练趋势
- `pgg-bd2f83f960bba4` [51 Horizontal violinplot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/51_Horizontal_violinplot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-35282c8418231f` [520 interactive barplot with plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/520-interactive-barplot-with-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-33e0a6b3e4a316` [522 plotly customize title](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/522-plotly-customize-title.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-376193a3c6e8a9` [523 plotly add annotation 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/523-plotly-add-annotation-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-1b6a693580fe27` [523 plotly add annotation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/523-plotly-add-annotation.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-8ef3c81b5f913b` [524 area over flexible baseline](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/524-area-over-flexible-baseline.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-8dde9022716f5f` [524 area over flexible baseline square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/524-area-over-flexible-baseline_square.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-0f9c2aaf280891` [525 line chart log transform](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/525-line-chart-log-transform.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-93acbe90a60acb` [527 introduction to histogram with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/527-introduction-to-histogram-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-c15f254ccad4e1` [528 customizing histogram with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/528-customizing-histogram-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 直方图
- `pgg-0e38dd732291e0` [529 multi group histogram pandas 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/529-multi-group-histogram-pandas-1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-f2bdfd87725a5c` [529 multi group histogram pandas 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/529-multi-group-histogram-pandas-2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-7b4da9850cf553` [529 multi group histogram pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/529-multi-group-histogram-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-79df806d3544b9` [52 Custom violinplot Appearance Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/52_Custom_violinplot_Appearance_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-06be68c5b71094` [52 Custom violinplot Appearance Seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/52_Custom_violinplot_Appearance_Seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-0af58de7bef9c5` [530 introduction to linechart with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/530-introduction-to-linechart-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-3be706c84162b0` [531 customizing linecharts with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/531-customizing-linecharts-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 折线与训练趋势
- `pgg-0970df69f0aa3f` [532 episode1 each line anakin square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/532-episode1-each-line-anakin-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-6d07cf24abaec6` [532 episode1 each line anakin](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/532-episode1-each-line-anakin.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-7c73339b2a2cc7` [532 linecharts mutliple groups with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/532-linecharts-mutliple-groups-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-bccc72b5700c8c` [533 introduction boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/533-introduction-boxplots-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-edb6e402430b11` [534 highly customized layout](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/534-highly-customized-layout.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-331f6e15114408` [535 introduction to scatter plot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/535-introduction-to-scatter-plot-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-e2a7f85e650138` [536 customizing scatter plots with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/536-customizing-scatter-plots-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 散点与拟合关系
- `pgg-d4a1452054ac44` [537 scatter plots grouped by color with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/537-scatter-plots-grouped-by-color-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 配色与视觉样式
- `pgg-8b16073e20cb39` [538 introduction to barplot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/538-introduction-to-barplot-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-b9c8f8c440f557` [539 customizing barplot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/539-customizing-barplot-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 分组柱状图
- `pgg-e0c8aa1900e015` [53 Custom violinplot color Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/53_Custom_violinplot_color_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴 / 配色与视觉样式
- `pgg-3b719a96c2cc1e` [53 Custom violinplot color Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/53_Custom_violinplot_color_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴 / 配色与视觉样式
- `pgg-40a9417286d97f` [53 Custom violinplot color Seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/53_Custom_violinplot_color_Seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴 / 配色与视觉样式
- `pgg-40d4673806d206` [53 Custom violinplot color Seaborn4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/53_Custom_violinplot_color_Seaborn4.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴 / 配色与视觉样式
- `pgg-8b19bc30545cf0` [54 grouped violinplot Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/54-grouped-violinplot-Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-77ce7485d78a27` [540 barplots grouped by color with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/540-barplots-grouped-by-color-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-3a4f9c01bc4c70` [541 waffle chart with additionnal grouping](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/541-waffle-chart-with-additionnal-grouping.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-b69cedc79df359` [542 custom boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/542-custom-boxplots-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-b0728ccfa503e4` [543 grouped boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/543-grouped-boxplots-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-3a23d50bc5814c` [547 stacked barplots with pandas 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/547-stacked-barplots-with-pandas-1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-9cf78c8cbaedec` [547 stacked barplots with pandas 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/547-stacked-barplots-with-pandas-2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-07ecddc293cde6` [548 intro candle stick matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/548-intro-candle-stick-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 蜡烛与区间范围图
- `pgg-fbeed1c9be5552` [549 candle stick with moving average](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/549-candle-stick-with-moving-average.png) · FIGURE_EXAMPLE · 预览 1 · 蜡烛与区间范围图
- `pgg-a8d1f6d21749ac` [54 Grouped violinplot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/54_Grouped_violinplot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-e73a9df0cfcb1c` [550 intro table with pandas 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/550-intro-table-with-pandas-1.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-35ded25e27cfc6` [550 intro table with pandas 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/550-intro-table-with-pandas-2.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-e4b36a5dea0a5e` [551 student t test visualization 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/551-student-t-test-visualization-1.png) · FIGURE_EXAMPLE · 预览 1 · 统计检验可视化
- `pgg-a41347bbf553fe` [551 student t test visualization 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/551-student-t-test-visualization-2.png) · FIGURE_EXAMPLE · 预览 1 · 统计检验可视化
- `pgg-22a2f549b66969` [552 table combined with plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/552-table-combined-with-plot.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-978e0e8809c9c8` [553 intro candle stick plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/553-intro-candle-stick-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 蜡烛与区间范围图
- `pgg-4406fb2339c8ed` [554 custom candle stick plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/554-custom-candle-stick-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 蜡烛与区间范围图
- `pgg-dccc7479df51e1` [555 candle stick with moving average plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/555-candle-stick-with-moving-average-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 蜡烛与区间范围图
- `pgg-e4a96eec3a8859` [556 visualize linear regression 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/556-visualize-linear-regression-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-d6e38e387de7e7` [556 visualize linear regression 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/556-visualize-linear-regression-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-32e66a7b620a9f` [557 anova visualization with matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/557-anova-visualization-with-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 统计检验可视化
- `pgg-151951e9b9ce0a` [557 anova visualization with matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/557-anova-visualization-with-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 统计检验可视化
- `pgg-09fa39be497b97` [557 anova visualization with matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/557-anova-visualization-with-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 统计检验可视化
- `pgg-3650694ebfb06e` [558 waffle bar chart 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/558-waffle-bar-chart-1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 华夫图
- `pgg-7e5891110fa4be` [558 waffle bar chart 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/558-waffle-bar-chart-2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 华夫图
- `pgg-eadbd5b0d19b6a` [558 waffle bar chart 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/558-waffle-bar-chart-3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 华夫图
- `pgg-8065f2c5940e23` [55 Specific order violinplot Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/55_Specific_order_violinplot_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-25a4caeb47e683` [55 Specific order violinplot Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/55_Specific_order_violinplot_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-c4959a64dd53cc` [560 introduction plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/560-introduction-plottable.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-4900c92ba25c2c` [561 control colors in plottable 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/561-control-colors-in-plottable-1.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表 / 配色与视觉样式
- `pgg-3dd80ee88cfab2` [561 control colors in plottable 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/561-control-colors-in-plottable-2.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表 / 配色与视觉样式
- `pgg-7242c33c84ad7f` [561 control colors in plottable 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/561-control-colors-in-plottable-3.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表 / 配色与视觉样式
- `pgg-9d540f38de70cb` [561 control colors in plottable 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/561-control-colors-in-plottable-4.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表 / 配色与视觉样式
- `pgg-e784ac04be1c79` [561 control colors in plottable 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/561-control-colors-in-plottable-5.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表 / 配色与视觉样式
- `pgg-37cdc2cd861d55` [562 add images in plottable 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/562-add-images-in-plottable-1.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-b9f0772deaa40b` [562 add images in plottable 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/562-add-images-in-plottable-2.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-09756237dda7e0` [563 graph in plottable 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/563-graph-in-plottable-1.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-3bec7d709bf045` [563 graph in plottable 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/563-graph-in-plottable-2.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-c9f9f242f90072` [563 graph in plottable 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/563-graph-in-plottable-3.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-3ac53a9ab50b5f` [563 graph in plottable 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/563-graph-in-plottable-4.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-1ddabbbb129f05` [563 graph in plottable 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/563-graph-in-plottable-5.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-38054b06ededb9` [564 publication ready table with plottable square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/564-publication-ready-table-with-plottable-square.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-44946f10540b47` [564 publication ready table with plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/564-publication-ready-table-with-plottable.jpeg) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-57e3d500948848` [565 arc diagram with arcplot 0](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/565-arc-diagram-with-arcplot-0.png) · FIGURE_EXAMPLE · 预览 1 · 弧线网络
- `pgg-45c998c9a5ee8d` [565 arc diagram with arcplot 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/565-arc-diagram-with-arcplot-1.png) · FIGURE_EXAMPLE · 预览 1 · 弧线网络
- `pgg-09123d4c518de0` [565 arc diagram with arcplot 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/565-arc-diagram-with-arcplot-2.png) · FIGURE_EXAMPLE · 预览 1 · 弧线网络
- `pgg-356a5d9653e901` [565 arc diagram with arcplot 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/565-arc-diagram-with-arcplot-3.png) · FIGURE_EXAMPLE · 预览 1 · 弧线网络
- `pgg-d6cfb1560b1b1e` [565 arc diagram with arcplot 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/565-arc-diagram-with-arcplot-4.png) · FIGURE_EXAMPLE · 预览 1 · 弧线网络
- `pgg-34c9db0a0b2d3e` [570 custom streamchart 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/570-custom-streamchart-2.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-0a4e4cb0fd7cd2` [570 custom streamchart 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/570-custom-streamchart-3.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-922f7651692634` [570 custom streamchart 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/570-custom-streamchart-4.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-f7241c9a2dd19a` [570 custom streamchart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/570-custom-streamchart.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-471e07f80d6f74` [571 radar chart with plotly 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/571-radar-chart-with-plotly-1.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `pgg-1252cfad8dd96b` [571 radar chart with plotly 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/571-radar-chart-with-plotly-2.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `pgg-01879b08a23215` [573 introduction scatterplot plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/573-introduction-scatterplot-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-a4577332d3d6d5` [573 introduction scatterplot plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/573-introduction-scatterplot-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-0c78851c781c37` [573 introduction scatterplot plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/573-introduction-scatterplot-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-1390ed73460fef` [574 custom marker scatter plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/574-custom-marker-scatter-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-8e03b68c499610` [574 custom marker scatter plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/574-custom-marker-scatter-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-a38a9e0ccb5747` [574 custom marker scatter plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/574-custom-marker-scatter-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-cdb92e017dd4fc` [574 custom marker scatter plotnine 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/574-custom-marker-scatter-plotnine-4.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-a6989dd90c694b` [575 custom theme plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-43f67bbd7d366a` [575 custom theme plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-50d103b2a7f43c` [575 custom theme plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-dc6fc08057a0fe` [575 custom theme plotnine 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-4.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-f8e50d70eeefad` [575 custom theme plotnine 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-5.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-d3b5f63fdd558e` [575 custom theme plotnine 6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-custom-theme-plotnine-6.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-7b96ff1f334fad` [575 distribution plot with quantiles 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-distribution-plot-with-quantiles-1.png) · FIGURE_EXAMPLE · 预览 1 · 分位数分布图
- `pgg-009493bec1d547` [575 distribution plot with quantiles 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-distribution-plot-with-quantiles-2.png) · FIGURE_EXAMPLE · 预览 1 · 分位数分布图
- `pgg-880ffc2f24a540` [575 distribution plot with quantiles](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/575-distribution-plot-with-quantiles.png) · FIGURE_EXAMPLE · 预览 1 · 分位数分布图
- `pgg-e063703e47d91a` [576 introduction barplot plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/576-introduction-barplot-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-9f612a2ac2c6d4` [576 introduction barplot plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/576-introduction-barplot-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-0f2cafaff9ec7b` [576 introduction barplot plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/576-introduction-barplot-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-39c5650f5e3cde` [577 customize barplot plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/577-customize-barplot-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-53fde1ee9f97f1` [577 customize barplot plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/577-customize-barplot-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-6b6a7eb2a9865f` [577 customize barplot plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/577-customize-barplot-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-6174f2e5ffda5e` [578 introduction histogram plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/578-introduction-histogram-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-0049c665886be0` [578 introduction histogram plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/578-introduction-histogram-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-b923490ac9bd7f` [578 introduction histogram plotnine 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/578-introduction-histogram-plotnine-3.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-22887d7e56bf4c` [579 multiple histograms plotnine 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/579-multiple-histograms-plotnine-1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-cb421f72f556fb` [579 multiple histograms plotnine 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/579-multiple-histograms-plotnine-2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-3d75520cfdc9cb` [582 simple barplot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/582-simple-barplot-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-f3e77a1bfc5185` [583 stacked barplot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/583-stacked-barplot-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-3179616f6c7f1f` [584 introduction hatch matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/584-introduction-hatch-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-9598c29a159647` [584 introduction hatch matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/584-introduction-hatch-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-d1c6104676daf6` [584 introduction hatch matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/584-introduction-hatch-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-d7bdf7ad4b4c5a` [584 introduction hatch matplotlib 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/584-introduction-hatch-matplotlib-4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-26a054872b9862` [585 introduction great tables 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-introduction-great-tables-1.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-8949151bf96a81` [585 introduction great tables 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-introduction-great-tables-2.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-5798a1f33aaf57` [585 introduction great tables 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-introduction-great-tables-3.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-6f246234d49c3d` [585 legend for categorical data matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-legend-for-categorical-data-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-935d1a0873041f` [585 legend for categorical data matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-legend-for-categorical-data-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-ba8184e829a2f3` [585 legend for categorical data matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-legend-for-categorical-data-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-45fbf77fa7e4fe` [585 legend for categorical data matplotlib 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/585-legend-for-categorical-data-matplotlib-4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-22c8791727a697` [586 customization great tables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/586-customization-great-tables.png) · FIGURE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-a836b3ebcef4ec` [587 how to use colormap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/587-how-to-use-colormap.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-53425a3981c378` [589 how to change coordinate system](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/589-how-to-change-coordinate-system.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-708c7ab9e8986a` [58 Number of obs on violinplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/58_Number_of_obs_on_violinplot_seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-b6e28a3f95c682` [590 advanced treemap 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/590-advanced-treemap-1.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-965f47cb66a73c` [590 advanced treemap 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/590-advanced-treemap-2.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-add5b584788ab2` [590 advanced treemap 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/590-advanced-treemap-3.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-f4cdf499118511` [590 advanced treemap 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/590-advanced-treemap-4.png) · FIGURE_EXAMPLE · 预览 1 · 矩形树图
- `pgg-e6648469ca8ad1` [591 arrows with inflexion point 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/591-arrows-with-inflexion-point-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-39c4fd1d99c86b` [591 arrows with inflexion point 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/591-arrows-with-inflexion-point-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-ecd8137bf39349` [592 non contiguous cartogram in python square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/592-non-contiguous-cartogram-in-python-square.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-c963f0a00bf41d` [592 non contiguous cartogram in python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/592-non-contiguous-cartogram-in-python.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-0ef505f27f04b2` [593 customize bubble map with folium 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/593-customize-bubble-map-with-folium-1.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图 / 气泡图 / 地理与分区地图
- `pgg-47b3f173184693` [593 customize bubble map with folium 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/593-customize-bubble-map-with-folium-2.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图 / 气泡图 / 地理与分区地图
- `pgg-9f46cd05a09077` [594 introduction flexitext](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/594-introduction-flexitext.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-782986389b80b7` [595 advanced flexitext features 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/595-advanced-flexitext-features-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-4b9aa3461a1619` [595 advanced flexitext features 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/595-advanced-flexitext-features-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-d2cd1b869088e7` [5 custom space between bars](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/5_custom_space_between_bars.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-fcee7877e300c0` [5 custom width of bars](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/5_custom_width_of_bars.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-31523da34eb3d7` [6 change texture](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/6_change_texture.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-08fbf04583d259` [70 basic density plot with seaborn 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/70-basic-density-plot-with-seaborn-2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-c295077c4203c6` [70 Basic density plot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/70_Basic_density_plot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-fbd6792bbd93ba` [71 Shaded density plot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/71_Shaded_density_plot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-c371d84aede1d8` [72 Horizontal density plot Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/72_Horizontal_density_plot_Seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-aaca8ce67ead2d` [73 Control bandwidth densityplot Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/73_Control_bandwidth_densityplot_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-587d9252268b34` [73 Control bandwidth densityplot Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/73_Control_bandwidth_densityplot_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-30733c22c7d57e` [74 density plot multi variables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/74_density_plot_multi_variables.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-5178d04dd61a58` [7 custom axis name](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/7_custom_axis_name.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-d4027020d30343` [7 custom label](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/7_custom_label.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-5555fa264141d3` [7 increase margin](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/7_increase_margin.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-cb965d86e83836` [80 bivariate kernel density plot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/80_bivariate_kernel_density_plot1.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-62aa0289267d77` [80 bivariate kernel density plot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/80_bivariate_kernel_density_plot2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-4f30bf119259f1` [80 bivariate kernel density plot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/80_bivariate_kernel_density_plot3.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-9e9b908cec8b1b` [82 seaborn jointplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot1.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-ca1ac33ba24e6f` [82 seaborn jointplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot2.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-1120e49177265e` [82 seaborn jointplot3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot3.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-ebe35da833d2e3` [82 seaborn jointplot4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot4.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-078806f403db30` [82 seaborn jointplot5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot5.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-cc5a613abf2542` [82 seaborn jointplot6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot6.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-78d071789f57c2` [82 seaborn jointplot7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot7.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-5661ab81822a28` [82 seaborn jointplot8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot8.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-69a218d21f6a14` [82 seaborn jointplot9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/82_seaborn_jointplot9.png) · FIGURE_EXAMPLE · 预览 1 · 联合与边缘分布
- `pgg-4d517aa5cbdce3` [83 basic 2d histograms with matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83-basic-2d-histograms-with-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-9ede51eed9124b` [83 basic 2d histograms with matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83-basic-2d-histograms-with-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-ae20089db637a8` [83 basic 2d histograms with matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83-basic-2d-histograms-with-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-04354bb759fd39` [83 2D Histogram matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_1.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-6fbc52d72cf1eb` [83 2D Histogram matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-f893032b89e428` [83 2D Histogram matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_3.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-5981dd13bccd8f` [83 2D Histogram matplotlib 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_4.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-e93dae84fe10c6` [83 2D Histogram matplotlib 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_5.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-dc470ecd68cafc` [83 2D Histogram matplotlib 6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/83_2D_Histogram_matplotlib_6.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-48ac96ddc4f8a5` [84 hexbin plot with matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84-hexbin-plot-with-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-566e35eabce3bc` [84 hexbin plot with matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84-hexbin-plot-with-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-1f40f99ae5b617` [84 hexbin plot with matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84-hexbin-plot-with-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-a520d5f2f70292` [84 hexbin matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84_hexbin_matplotlib_1.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-5898df047c1fc9` [84 hexbin matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84_hexbin_matplotlib_2.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-2c6608d965719b` [84 hexbin matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84_hexbin_matplotlib_3.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-4891b5052b67b4` [84 hexbin matplotlib 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84_hexbin_matplotlib_4.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-0de37a4f57f549` [84 hexbin matplotlib 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/84_hexbin_matplotlib_5.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图
- `pgg-6ed7825757a522` [85 density plot with matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85-density-plot-with-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-05a6299c2901ff` [85 density plot with matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85-density-plot-with-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-6f212dfffe9aea` [85 density plot with matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85-density-plot-with-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-cdb251140b7953` [85 2D density plot matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85_2D_density_plot_matplotlib_1.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-511d1fe0f13d68` [85 2D density plot matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85_2D_density_plot_matplotlib_2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-621f6423df5231` [85 2D density plot matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/85_2D_density_plot_matplotlib_3.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-cb4fe9f66a1a13` [86 2D density plot explanation 300x71](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/86_2D_density_plot_explanation-300x71.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-ecf223e421c5eb` [86 2D density plot explanation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/86_2D_density_plot_explanation.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-8e91caec7daf87` [8 confidence interval](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/8_confidence_interval.png) · FIGURE_EXAMPLE · 预览 1 · Forest 效应区间
- `pgg-c2cf360694cd8a` [90 Input format for heatmap1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/90_Input_format_for_heatmap1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-7214eaf70da0b8` [90 Input format for heatmap2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/90_Input_format_for_heatmap2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-2d8a49fcc3ad99` [90 Input format for heatmap2bis](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/90_Input_format_for_heatmap2bis.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-b290ee0c80c31d` [90 Input format for heatmap3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/90_Input_format_for_heatmap3.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-988a5fe5916c32` [91 Custom heat annotate cells](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/91_Custom_heat_annotate_cells.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 热力矩阵
- `pgg-7e732038c84954` [91 Custom heat control lines](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/91_Custom_heat_control_lines.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 热力矩阵
- `pgg-3cb41583fd7f68` [91 Custom heat hide axis label](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/91_Custom_heat_hide_axis_label.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 热力矩阵
- `pgg-2414b21048734a` [91 Custom heat hide colorbar](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/91_Custom_heat_hide_colorbar.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 热力矩阵
- `pgg-64e61608299a0f` [91 Custom heat hide some axis label](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/91_Custom_heat_hide_some_axis_label.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 热力矩阵
- `pgg-d05ffdddbc5a8f` [92 control color in seaborn heatmaps square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92-control-color-in-seaborn-heatmaps-square.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-a8cdc3aab56c51` [92 control color in seaborn heatmaps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92-control-color-in-seaborn-heatmaps.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-574b5592107bee` [92 Control color heatmap1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-0e1bcb40be8bdd` [92 Control color heatmap2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-eadc3aa586027d` [92 Control color heatmap3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap3.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-8ba068c25bc975` [92 Control color heatmap4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap4.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-d0c2da73e8c898` [92 Control color heatmap5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap5.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-32d4440bc03d4a` [92 Control color heatmap6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap6.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-fe85ca29aef6b4` [92 Control color heatmap7](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap7.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-f2572965e5f1a9` [92 Control color heatmap8](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap8.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-6a16527da417d9` [92 Control color heatmap9](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/92_Control_color_heatmap9.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 配色与视觉样式
- `pgg-01c8b41f88fc8e` [94 Heatmap Normalization Seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/94_Heatmap_Normalization_Seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-33733833872d0e` [94 Heatmap Normalization Seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/94_Heatmap_Normalization_Seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-86be86d0859670` [94 Heatmap Normalization Seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/94_Heatmap_Normalization_Seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-4d0509040082d8` [94 Heatmap Normalization Seaborn4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/94_Heatmap_Normalization_Seaborn4.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-9495db0d1ff30c` [9 plotting factor vs factor](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/9_plotting_factor_vs_factor.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-555eac4b8af062` [AqueminiOutKast](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/AqueminiOutKast.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-56834e5c0b59ec` [BONUS area facet](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/BONUS_area_facet.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-64ebf754fe18d9` [BoxDanger Overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/BoxDanger_Overview.png) · FIGURE_EXAMPLE · 预览 1 · 箱线图
- `pgg-7c22b6367c4e3f` [Logo PGG light](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Logo_PGG_light.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5eba75dcc6a90b` [Missy Elliott Supa Dupa Fly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Missy_Elliott_Supa_Dupa_Fly.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-2849036523a6ff` [Overplot Overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Overplot_Overview.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-cba2f70b8e3365` [Pandas Cheat Datacamp](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Pandas_Cheat_Datacamp.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-ecf0f54ef56171` [Seaborn Cheatsheet Datacamp](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Seaborn_Cheatsheet_Datacamp.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-4b9406a7b2f08a` [Spaghetti Overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/Spaghetti_Overview.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-54d5da1fe49dff` [advanced custom annotations matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/advanced-custom-annotations-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-f5064374a60be0` [advanced custom annotations matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/advanced-custom-annotations-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-2706f403c39de9` [advanced custom annotations matplotlib 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/advanced-custom-annotations-matplotlib-3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-34e678b8242491` [animated chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/animated_chart.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-c491d3280d8aa3` [animated gapminder](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/animated_gapminder.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图
- `pgg-0c16ef604f7a7b` [animated scatter](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/animated_scatter.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图 / 散点与拟合关系
- `pgg-879e195d7b5350` [animated volcano](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/animated_volcano.gif) · FIGURE_EXAMPLE · 预览 1 · 动态图 / 火山图
- `pgg-13d9290129b09e` [area fill between two lines in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/area-fill-between-two-lines-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 面积与流带
- `pgg-635e47751c8e24` [background](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/background.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-ff1dc54d23f175` [basic barplot with seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-barplot-with-seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-81950077374cfa` [basic barplot with seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-barplot-with-seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-50bed0dfcefd77` [basic barplot with seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-barplot-with-seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-abd8090fac1a9b` [basic histogram in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-histogram-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-fa70fee45b2de4` [basic histogram in matplotlib2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-histogram-in-matplotlib2.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-8a9367e871ac78` [basic histogram with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-histogram-with-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-98a9abb5433ee4` [basic sankey diagram with pysankey 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-sankey-diagram-with-pysankey-1.png) · FIGURE_EXAMPLE · 预览 1 · 桑基与流向图
- `pgg-69ff7112a3bf68` [basic sankey diagram with pysankey 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-sankey-diagram-with-pysankey-2.png) · FIGURE_EXAMPLE · 预览 1 · 桑基与流向图
- `pgg-2a5a5d1f96a101` [basic time series with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/basic-time-series-with-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-627c33c446003e` [bubble plot gapminder](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/bubble-plot-gapminder.png) · FIGURE_EXAMPLE · 预览 1 · 动态图 / 气泡图
- `pgg-eac10f25b688ee` [bubble plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/bubble-plot-with-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 气泡图
- `pgg-1cbf3f9877a3a4` [bump chart square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/bump-chart-square.png) · FIGURE_EXAMPLE · 预览 1 · 排名变化图
- `pgg-1b6a5e8b155b40` [bump chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/bump-chart.png) · FIGURE_EXAMPLE · 预览 1 · 排名变化图
- `pgg-a97caf4612390c` [calendar heatmap square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/calendar-heatmap-square.png) · FIGURE_EXAMPLE · 预览 1 · 日历热图 / 热力矩阵
- `pgg-ba645ba820ad4a` [calendar heatmap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/calendar-heatmap.png) · FIGURE_EXAMPLE · 预览 1 · 日历热图 / 热力矩阵
- `pgg-0109f1cf7ea871` [categorical palettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/categorical_palettes.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-16f100150e434e` [chord diagram chord library](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/chord-diagram-chord-library.png) · FIGURE_EXAMPLE · 预览 1 · 弦图
- `pgg-deeda80a520b11` [choropleth map geopandas python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/choropleth-map-geopandas-python.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-8cb66f5897bacb` [circular barplot basic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-basic.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-6a7ab861980195` [circular barplot basic1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-basic1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-9d86d58cf56d4c` [circular barplot basic2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-basic2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-60032ae0b1c206` [circular barplot basic3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-basic3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-eb4c07fe08e40a` [circular barplot basic4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-basic4.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-37d9c296dfadcb` [circular barplot with groups1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-with-groups1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-18657285b945ff` [circular barplot with groups2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-with-groups2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-fbe19679f1ae3f` [circular barplot with groups3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-with-groups3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-8c1d8850b2eb0b` [circular barplot with groups4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-with-groups4.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-3f962bf22d4d32` [circular barplot with groups4big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-barplot-with-groups4big.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-768a6875b57806` [circular packing 1 level hierarchy1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-packing-1-level-hierarchy1.png) · FIGURE_EXAMPLE · 预览 1 · 圆形打包图
- `pgg-62188f1490539c` [circular packing 1 level hierarchy2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-packing-1-level-hierarchy2.png) · FIGURE_EXAMPLE · 预览 1 · 圆形打包图
- `pgg-0f43a0795900eb` [circular packing 1 level hierarchy3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-packing-1-level-hierarchy3.png) · FIGURE_EXAMPLE · 预览 1 · 圆形打包图
- `pgg-081838d2d63e63` [circular packing several levels of hierarchy large](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-packing-several-levels-of-hierarchy-large.png) · FIGURE_EXAMPLE · 预览 1 · 圆形打包图
- `pgg-a977e0c321f08e` [circular packing several levels of hierarchy](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/circular-packing-several-levels-of-hierarchy.png) · FIGURE_EXAMPLE · 预览 1 · 圆形打包图
- `pgg-c1ad77f696fc18` [color names matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/color_names_matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-c3ff41694f66df` [connected scatterplot for evolution](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/connected-scatterplot-for-evolution.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-9034278a54da47` [continuous palettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/continuous_palettes.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-d0fc71c0be2668` [custom fonts in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-fonts-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-f27062a7fc7c98` [custom legend with matplotlib1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-07e78dfb405279` [custom legend with matplotlib2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-b348ca4f6005d1` [custom legend with matplotlib3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-cc716ac9066505` [custom legend with matplotlib4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib4.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-7fd242e1f0fc98` [custom legend with matplotlib5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib5.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-842431fdab40c6` [custom legend with matplotlib6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/custom-legend-with-matplotlib6.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-3127e3cd85ce6e` [density chart matplotlib csv](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-matplotlib-csv.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-70442a597e4238` [density chart matplotlib vector](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-matplotlib-vector.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-ebebac1b97c8bb` [density chart multiple groups seaborn1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn1.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-27434f7b683ec3` [density chart multiple groups seaborn2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn2.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-1d06b76394cb60` [density chart multiple groups seaborn3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn3.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-961bf1ca9df893` [density chart multiple groups seaborn4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn4.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-aab2c6327a15d6` [density chart multiple groups seaborn5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn5.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-f577fc18121346` [density chart multiple groups seaborn6](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-chart-multiple-groups-seaborn6.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-d6071a9874939c` [density mirror histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-mirror-histogram.png) · FIGURE_EXAMPLE · 预览 1 · 直方图 / 密度曲线
- `pgg-4463c17fe7c99e` [density mirror](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/density-mirror.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-262808d7f5ea24` [diff eucl cor](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/diff_eucl_cor.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-16bcd8267faaf2` [diverging palettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/diverging_palettes.png) · FIGURE_EXAMPLE · 预览 1 · 发散条形图 / 配色与视觉样式
- `pgg-bf9cf13eebe559` [error bars on barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/error-bars-on-barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-878f6a49bc98ef` [figure explanations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/figure-explanations.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-e2e0d49889adbd` [github](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/github.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-26a9833343c3b8` [grouped barplot with the total of each group represented as a grey rectangle 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-a824d37e600ba0` [grouped barplot with the total of each group represented as a grey rectangle 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle-2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-40c99a2dec6a67` [grouped barplot with the total of each group represented as a grey rectangle 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-7292830101274b` [grouped barplot with the total of each group represented as a grey rectangle 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle-3.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-4f7f8d549bd6c4` [grouped barplot with the total of each group represented as a grey rectangle square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-49627d940c0b6e` [grouped barplot with the total of each group represented as a grey rectangle](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-e1d6ea7cc2c0d7` [grouped barplot1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot1.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-cea1b97055b8a5` [grouped barplot2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/grouped-barplot2.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-d7c88230f1b629` [heatmap for timeseries matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/heatmap-for-timeseries-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-8add9c25a4db5d` [heatmap for timeseries matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/heatmap-for-timeseries-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-2f80d68b12242b` [hexbin map from geojson python 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/hexbin-map-from-geojson-python-1.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-71d49a64116a8b` [hexbin map from geojson python 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/hexbin-map-from-geojson-python-2.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-721352125f5b43` [hexbin map from geojson python 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/hexbin-map-from-geojson-python-3.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-81d2284bdabfaa` [hexbin map from geojson python orig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/hexbin-map-from-geojson-python-orig.png) · FIGURE_EXAMPLE · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-d6647c979a7707` [hierarchical edge bundling R](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/hierarchical-edge-bundling-R.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5857db3f1f562c` [how to add plot inside plot 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-add-plot-inside-plot-1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f598a9f972e14e` [how to add plot inside plot 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-add-plot-inside-plot-2.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-45739558e12925` [how to add plot inside plot 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-add-plot-inside-plot-3.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-fb34e03eee70cd` [how to create and custom arrows matplotlib 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-create-and-custom-arrows-matplotlib-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-75e016049f1878` [how to create and custom arrows matplotlib 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-create-and-custom-arrows-matplotlib-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-779855e219ffa6` [how to custom annotations matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-custom-annotations-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-25d51fcdc31f7d` [how to remove axis in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-remove-axis-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-187aedc4708512` [how to use rectangles in matplotlib legends](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/how-to-use-rectangles-in-matplotlib-legends.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-e0a022d080418a` [introduction drawarrow 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-bf76db7328a208` [introduction drawarrow 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-2.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5cc84eea382e7c` [introduction drawarrow 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-3.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-95caf75521ff4b` [introduction drawarrow 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-4.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-cbeccd59d5bc1c` [introduction drawarrow arg0 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg0-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-38dc082b286ef9` [introduction drawarrow arg1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg1-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b763e2861ebbd0` [introduction drawarrow arg10 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg10-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-6ad44fbef0a250` [introduction drawarrow arg11 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg11-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-4cc649d4e9f3ef` [introduction drawarrow arg12 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg12-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-aecbd74afe0eba` [introduction drawarrow arg13 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg13-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-984e1b04f4d2d3` [introduction drawarrow arg14 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg14-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a0a75a300210e1` [introduction drawarrow arg15 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg15-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-03edc99a38f4cc` [introduction drawarrow arg2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg2-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-4e5026e8e979f5` [introduction drawarrow arg3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg3-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a7046d770e0d6a` [introduction drawarrow arg4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg4-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-fa4cff088fcc14` [introduction drawarrow arg5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg5-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-1d3451a3fa86c1` [introduction drawarrow arg6 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg6-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-d2c95950892eba` [introduction drawarrow arg7 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg7-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b22f24a01d0dd7` [introduction drawarrow arg8 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg8-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f8e39d2679fac7` [introduction drawarrow arg9 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/introduction-drawarrow-arg9-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-41fe832452dd1b` [issue with stacking](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/issue-with-stacking.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f1b454f4fdfbdb` [jay z the blueprint](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/jay-z-the-blueprint.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-226b78b1a9e02e` [line chart dual y axis with matplotlib1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/line-chart-dual-y-axis-with-matplotlib1.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-6db693ce967985` [line chart dual y axis with matplotlib2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/line-chart-dual-y-axis-with-matplotlib2.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-c907674f25cba8` [line chart dual y axis with matplotlib3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/line-chart-dual-y-axis-with-matplotlib3.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-bc8599f38a7834` [logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/logo.png) · FIGURE_EXAMPLE · 预览 2 · 待核对原图
- `pgg-fc4a296bceb1e9` [manhattan plot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/manhattan-plot-with-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-dfcba5eaf9c09e` [map read geojson with python geopandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/map-read-geojson-with-python-geopandas.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-72f55ab38bd7fe` [matplotlib python official cheatsheet1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/matplotlib-python-official-cheatsheet1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-6473f281fa073c` [matplotlib python official cheatsheet2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/matplotlib-python-official-cheatsheet2.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-00943f528c59f3` [matplotlib cheat sheet](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/matplotlib_cheat_sheet.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f336fbdd06104a` [matplotlib vocabulary](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/matplotlib_vocabulary.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-271df1a2257e82` [matplotlib vocabulary new](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/matplotlib_vocabulary_new.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-14c2f8ff988308` [nas illmatic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/nas-illmatic.jpg) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-132d5e368756eb` [new 0](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/new-0.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-d1c3854c786912` [new 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/new-1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3efad9a90b390d` [pandas cheat sheet](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pandas_cheat_sheet.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a9fa486cd61eb3` [parallel coordinate plot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/parallel-coordinate-plot-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-8b9368a63438b6` [pie plot matplotlib basic add labels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pie-plot-matplotlib-basic-add-labels.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-2b93cd831f75de` [pie plot matplotlib basic add padding](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pie-plot-matplotlib-basic-add-padding.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-eadd835133fa97` [pie plot matplotlib basic colors](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pie-plot-matplotlib-basic-colors.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-7734f6b94973a6` [pie plot matplotlib basic1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pie-plot-matplotlib-basic1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-2d1b06bc373a5a` [pieChartIssue](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pieChartIssue.png) · FIGURE_EXAMPLE · 预览 1 · 饼图
- `pgg-24ed03966253c1` [projection Aitoff](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Aitoff.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-db273f607e9c51` [projection AzimuthalEquidistant](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-AzimuthalEquidistant.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-0d431b71c1a0cf` [projection EckertI](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertI.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b335f042eab933` [projection EckertII](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertII.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-952faf5466f5af` [projection EckertIII](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertIII.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-ef35b636017c4d` [projection EckertIV](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertIV.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-23f79dda7ba5c2` [projection EckertV](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertV.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-141d17e0601681` [projection EckertVI](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EckertVI.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-0e3791a1c2c199` [projection EqualEarth](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EqualEarth.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-017466d54f4f1b` [projection EuroPP](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-EuroPP.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f23320bd914b07` [projection Geostationary](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Geostationary.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-32ea3c0a93a646` [projection Gnomonic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Gnomonic.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-127c6a040b5ee6` [projection Hammer](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Hammer.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-c4a1434287e550` [projection InterruptedGoodeHomolosine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-InterruptedGoodeHomolosine.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-8c9c0da793149f` [projection LambertAzimuthalEqualArea](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-LambertAzimuthalEqualArea.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-22b910bb320cfc` [projection LambertCylindrical](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-LambertCylindrical.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a153dcc8b6df1c` [projection Mercator](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Mercator.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-31cbaa836ff991` [projection Miller](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Miller.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3ff9149bf1feee` [projection Mollweide](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Mollweide.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-14d26d04f7a145` [projection NearsidePerspective](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-NearsidePerspective.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-c1fa7722f1ac37` [projection OSGB](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-OSGB.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-833dcb52dff3e2` [projection OSNI](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-OSNI.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-011ac095405375` [projection ObliqueMercator](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-ObliqueMercator.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-ae1a5fb77125b9` [projection Orthographic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Orthographic.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-91a69ef879020f` [projection PlateCarree](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-PlateCarree.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3342f08776861d` [projection Robinson](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Robinson.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-abea3ffbb266de` [projection Sinusoidal](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Sinusoidal.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5e7542f9ee3f2d` [projection SouthPolarStereo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-SouthPolarStereo.png) · FIGURE_EXAMPLE · 预览 1 · 极坐标与径向图
- `pgg-5e69c4e0831aea` [projection Stereographic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-Stereographic.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3ffbef4fa6111b` [projection TransverseMercator](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection-TransverseMercator.png) · FIGURE_EXAMPLE · 预览 1 · 变形统计地图
- `pgg-78ab32d4c1dd25` [projection maps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/projection_maps.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-ee03fdbec2bf3f` [pypalettes preview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/pypalettes-preview.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-4791d97e880b90` [quick code img plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/quick-code-img-plotnine.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5344a98997a5b7` [quick pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/quick-pandas.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-340d6b44d68438` [quickstart pyfonts square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/quickstart-pyfonts-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5f932120a9cca3` [quickstart pyfonts](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/quickstart-pyfonts.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-710b58a2f6bf63` [raincloud plot with matplotlib and ptitprince](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/raincloud-plot-with-matplotlib-and-ptitprince.png) · FIGURE_EXAMPLE · 预览 1 · 雨云图
- `pgg-b6d1873cbb4dc6` [ridgeline graph plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/ridgeline-graph-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-3e5dac0a9458b7` [ridgeline graph seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/ridgeline-graph-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-39cf791fcde474` [sankey diagram with python and plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/sankey-diagram-with-python-and-plotly.png) · FIGURE_EXAMPLE · 预览 1 · 桑基与流向图
- `pgg-885ffd895c7aca` [scatterplot and log scale in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/scatterplot-and-log-scale-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-e9c8bf1ccc9ce0` [scatterplot with regression fit in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/scatterplot-with-regression-fit-in-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-7df10570e59c95` [schema spatial plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/schema-spatial-plot.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-9ec378878ff1a7` [seaborn title customization](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/seaborn-title-customization.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例
- `pgg-6aab58ffc81439` [seaborn cheat sheet](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/seaborn_cheat_sheet.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-160a9b4ae87930` [sequential palettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/sequential_palettes.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-b363eef059da60` [short color names matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/short_color_names_matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式
- `pgg-2b5bbf36d9ea1e` [stacked barplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/stacked-barplot-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-9756e047c009ca` [stacked percent barplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/stacked-percent-barplot-seaborn.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-cd8d46963b89b5` [streamchart basic altair](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/streamchart-basic-altair.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-ee99991e7c289c` [streamchart basic matplotlib1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/streamchart-basic-matplotlib1.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-0db21be859a3ec` [streamchart basic matplotlib2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/streamchart-basic-matplotlib2.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-1097be858f4508` [streamchart basic matplotlib3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/streamchart-basic-matplotlib3.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-a2ab417c807389` [streamchart basic matplotlib4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/streamchart-basic-matplotlib4.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-7dcd58814af264` [tuto barplot 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-barplot-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-562719717619f4` [tuto barplot 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-barplot-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-fd943392ce36d7` [tuto barplot 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-barplot-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-bc774221e72fc5` [tuto barplot 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-barplot-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-c81fab7ac5cbdc` [tuto barplot 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-barplot-4.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-ccc3d70171d5d1` [tuto hist 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-64976f967895c1` [tuto hist 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-bd25ce4c5fcf6c` [tuto hist 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-297dbc06e54bfe` [tuto hist 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-d5fa0cd7eb634b` [tuto hist 5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-5-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-78bbd70cca92a6` [tuto hist 6 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-hist-6-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图
- `pgg-173e988fe3896c` [tuto plot 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-98d7bcc9d4994c` [tuto plot 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-72e9808d70666b` [tuto plot 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a34be2cbde5cfb` [tuto plot 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-c8825d16b8f47d` [tuto plot 5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-5-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a0ef6f5dca4601` [tuto plot 6 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-6-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-97b8d328ddeb96` [tuto plot 7 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-plot-7-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-25956166e20681` [tuto stackplot 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b023bef68faa0b` [tuto stackplot 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-38f2a3fd208aa5` [tuto stackplot 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-9f97f1653f5fb4` [tuto stackplot 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-0e5bb015eb77fd` [tuto stackplot 5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-5-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-804c4f52439018` [tuto stackplot 6 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-6-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f09376c799cc57` [tuto stackplot 7 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-7-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-5d71767b043eb1` [tuto stackplot 8 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-stackplot-8-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f3eb638a271957` [tuto swarmplot 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-swarmplot-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-622870708baa30` [tuto swarmplot 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-swarmplot-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-c5f6884c3d11b1` [tuto swarmplot 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-swarmplot-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-00206602baf87c` [tuto swarmplot 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-swarmplot-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 样本散点与蜂群
- `pgg-a551ae097a4091` [tuto violinplot 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-41853c085294cc` [tuto violinplot 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-9c4fcf756f1fad` [tuto violinplot 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-00a9c3bc08baa3` [tuto violinplot 4 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-4-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-4966f1c366174e` [tuto violinplot 5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-5-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-0c868d76e01b5a` [tuto violinplot 6 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/tuto-violinplot-6-square.png) · FIGURE_EXAMPLE · 预览 1 · 小提琴与分组小提琴
- `pgg-22a3d4570996a4` [twitter](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/twitter.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3b35fa200105cf` [usecase pyfonts 1 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-1-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-10aa631280eaf2` [usecase pyfonts 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-1.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b8bfc9375b6cc6` [usecase pyfonts 2 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-2-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-1d364de823bb3b` [usecase pyfonts 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-2.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-1b42c54968c95a` [usecase pyfonts 3 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-3-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-8ea2b2aa14ae0f` [usecase pyfonts 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/usecase-pyfonts-3.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-e5607453bc8802` [web area chart with different colors for positive and negative values square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-area-chart-with-different-colors-for-positive-and-negative-values-square.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带 / 配色与视觉样式
- `pgg-3886070f717b6e` [web area chart with different colors for positive and negative values](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-area-chart-with-different-colors-for-positive-and-negative-values.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带 / 配色与视觉样式
- `pgg-11e40574796b77` [web barplot with annotations and arrows highres](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-barplot-with-annotations-and-arrows-highres.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 分组柱状图
- `pgg-636e145299ce47` [web barplot with annotations and arrows square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-barplot-with-annotations-and-arrows-square.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 分组柱状图
- `pgg-98315323c8d06e` [web bubble map with arrows 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-map-with-arrows-1.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-e2720c13c90031` [web bubble map with arrows 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-map-with-arrows-2.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-36846af50e7e91` [web bubble map with arrows 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-map-with-arrows-3.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-2fdae5c6eea695` [web bubble map with arrows square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-map-with-arrows-square.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-c3fa808c94ba3a` [web bubble map with arrows](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-map-with-arrows.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-4fb89285dccbd5` [web bubble plot with annotations and custom features](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-bubble-plot-with-annotations-and-custom-features.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 气泡图
- `pgg-82e43e36abd965` [web choropleth map with barplot square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-choropleth-map-with-barplot-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-026ef8be943fed` [web choropleth map with barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-choropleth-map-with-barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-d3706faf08d4d2` [web choropleth map with histogram square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-choropleth-map-with-histogram-square.png) · FIGURE_EXAMPLE · 预览 1 · 直方图 / 地理与分区地图
- `pgg-26ba2b0a3fe604` [web choropleth map with histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-choropleth-map-with-histogram.png) · FIGURE_EXAMPLE · 预览 1 · 直方图 / 地理与分区地图
- `pgg-3abcd26c07ff77` [web circular barplot with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-circular-barplot-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-c1c90f434824de` [web circular lollipop plot with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-circular-lollipop-plot-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-707a20fc7f337d` [web combine choropleth map with barplot square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-combine-choropleth-map-with-barplot-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-1991b024e7ebeb` [web combine choropleth map with barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-combine-choropleth-map-with-barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-598810572e16f2` [web dumbell chart square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-dumbell-chart-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3fbe250a5619d7` [web dumbell chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-dumbell-chart.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-24a6dc5e9b04b3` [web ggbetweenstats with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-ggbetweenstats-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-add71342ee47a0` [web heatmap and radial barchart plastics square1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-and-radial-barchart-plastics-square1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 极坐标与径向图
- `pgg-432dbda7caf08f` [web heatmap and radial barchart plastics square2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-and-radial-barchart-plastics-square2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 极坐标与径向图
- `pgg-37e98009472478` [web heatmap and radial barchart plastics](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-and-radial-barchart-plastics.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵 / 极坐标与径向图
- `pgg-fecc3789933022` [web heatmap comparison 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-1.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-de5fba082cbac5` [web heatmap comparison 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-2.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-88c020fa59430e` [web heatmap comparison 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-3.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-c609073c6a3417` [web heatmap comparison 4](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-4.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-1304b34f4e0783` [web heatmap comparison 5 square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-5-square.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-2ed0d161c1446d` [web heatmap comparison 5](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-5.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-20712449c035b0` [web heatmap comparison square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-heatmap-comparison-square.png) · FIGURE_EXAMPLE · 预览 1 · 热力矩阵
- `pgg-1fb331d9fa8912` [web highlighted lineplot with faceting medium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-highlighted-lineplot-with-faceting-medium.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-c31f87c6cb6d67` [web highlighted lineplot with faceting square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-highlighted-lineplot-with-faceting-square.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-e5cbaf19ecd3ea` [web highlighted lineplot with faceting](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-highlighted-lineplot-with-faceting.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-f6b50de2ea21a0` [web histogram with annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-histogram-with-annotations.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 直方图
- `pgg-a91a26f593fc94` [web horizontal barplot with labels the economist square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-horizontal-barplot-with-labels-the-economist-square.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 标注、图例与排版示例
- `pgg-5603408e1c50fb` [web horizontal barplot with labels the economist](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-horizontal-barplot-with-labels-the-economist.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图 / 标注、图例与排版示例
- `pgg-31bacefa1ba966` [web lemurs parallel chart square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lemurs-parallel-chart-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-4b64b676121dfb` [web lemurs parallel chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lemurs-parallel-chart.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b671b3b76f910a` [web line chart small multiple square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-line-chart-small-multiple-square.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-9d4101f3ae3f06` [web line chart small multiple](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-line-chart-small-multiple.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-f8b998bf6acb77` [web line chart with labels at line end square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-line-chart-with-labels-at-line-end-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-ce34b628372db8` [web line chart with labels at line end](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-line-chart-with-labels-at-line-end.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-68cd8b65232e7d` [web lineplots and area chart the economist square1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lineplots-and-area-chart-the-economist-square1.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-7512f2c902a7c1` [web lineplots and area chart the economist square2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lineplots-and-area-chart-the-economist-square2.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-6ea23aaf91d988` [web lineplots and area chart the economist](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lineplots-and-area-chart-the-economist.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-8845b47e3a669a` [web lollipop plot with python mario kart 64 world records square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-plot-with-python-mario-kart-64-world-records-square.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-4d95983e9378bf` [web lollipop plot with python mario kart 64 world records](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-plot-with-python-mario-kart-64-world-records.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-0dfcbcf1732877` [web lollipop plot with python the office square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-plot-with-python-the-office-square.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-ff15d207575905` [web lollipop with background image square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-with-background-image-square.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-e6c356bd5e5633` [web lollipop with background image](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-with-background-image.png) · FIGURE_EXAMPLE · 预览 1 · 棒棒糖图
- `pgg-ca117b158ad0bf` [web lollipop with colormap and arrow square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-with-colormap-and-arrow-square.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 棒棒糖图 / 标注、图例与排版示例
- `pgg-77e26ba38c85a6` [web lollipop with colormap and arrow](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-lollipop-with-colormap-and-arrow.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 棒棒糖图 / 标注、图例与排版示例
- `pgg-37a21717a5f5ab` [web map europe with color by country highres](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-europe-with-color-by-country-highres.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-d2b9f473d8d2ef` [web map europe with color by country](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-europe-with-color-by-country.png) · FIGURE_EXAMPLE · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-6dfd97fd9c40b8` [web map usa with scatter plot on top square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-usa-with-scatter-plot-on-top-square.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 地理与分区地图
- `pgg-e75fe25c9ea6bc` [web map usa with scatter plot on top](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-usa-with-scatter-plot-on-top.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 地理与分区地图
- `pgg-0f7740bd3bc3b7` [web map with custom legend square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-with-custom-legend-square.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-c54c4d1d38f0ed` [web map with custom legend](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-map-with-custom-legend.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-a1d7381a9a5110` [web minimalist black and white line chart square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-minimalist-black-and-white-line-chart-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-763811a5a3fb9b` [web minimalist black and white line chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-minimalist-black-and-white-line-chart.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-192d504c2a3548` [web multiple lines and panels square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-multiple-lines-and-panels-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-b3c5c79b25568a` [web multiple lines and panels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-multiple-lines-and-panels.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-0aef25d6ad5c35` [web multiple maps square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-multiple-maps-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-f5a2b61f90df40` [web multiple maps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-multiple-maps.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-e2502ef3dc7051` [web ordered mirror barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-ordered-mirror-barplot.png) · FIGURE_EXAMPLE · 预览 1 · 分组柱状图
- `pgg-e5af38459e47b5` [web overlapped area chart with zoom outsets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-overlapped-area-chart-with-zoom-outsets.png) · FIGURE_EXAMPLE · 预览 1 · 面积与流带
- `pgg-cb4f936100cf67` [web polar chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-polar-chart.png) · FIGURE_EXAMPLE · 预览 1 · 极坐标与径向图
- `pgg-d2793afe407910` [web polygon map to compare distances square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-polygon-map-to-compare-distances-square.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-c7ae9c2257372c` [web polygon map to compare distances](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-polygon-map-to-compare-distances.png) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-95ec6c045d3bd9` [web population pyramid](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-population-pyramid.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-eba07006b918ee` [web radar chart with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-radar-chart-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 雷达图
- `pgg-03809a605da620` [web ridgeline by text 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-ridgeline-by-text-1.png) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-75d445c37db890` [web ridgeline by text square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-ridgeline-by-text-square.png) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-a1f4d77b343530` [web ridgeline by text](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-ridgeline-by-text.png) · FIGURE_EXAMPLE · 预览 1 · 山脊图
- `pgg-cf444d5ac50799` [web scatter with customized annotations square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatter-with-customized-annotations-square.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 散点与拟合关系
- `pgg-84fbe813e0d49b` [web scatter with customized annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatter-with-customized-annotations.png) · FIGURE_EXAMPLE · 预览 1 · 标注、图例与排版示例 / 散点与拟合关系
- `pgg-f29db9048326d7` [web scatterplot astronaut square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-astronaut-square.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-7afeca2702f56b` [web scatterplot astronaut](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-astronaut.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-afbd7b64480cce` [web scatterplot text annotation and regression matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-text-annotation-and-regression-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-b10eb53368307b` [web scatterplot text annotation and regression matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-text-annotation-and-regression-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-4367fb396d1d8e` [web scatterplot with categorical zoom facets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-with-categorical-zoom-facets.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-69531d0b6b2480` [web scatterplot with images in circles](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-scatterplot-with-images-in-circles.png) · FIGURE_EXAMPLE · 预览 1 · 散点与拟合关系
- `pgg-f01697ccf17e99` [web slope chart matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-slope-chart-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 斜率图
- `pgg-7e81c01bab126a` [web slope chart matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-slope-chart-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 斜率图
- `pgg-e65add4ee618ab` [web small multiple with highlights square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-small-multiple-with-highlights-square.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合
- `pgg-af080054c70780` [web small multiple with highlights](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-small-multiple-with-highlights.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合
- `pgg-d24580410541a4` [web stacked area charts on a map](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-area-charts-on-a-map.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 面积与流带 / 地理与分区地图
- `pgg-6cee8cc6634096` [web stacked area with inflexion arrows square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-area-with-inflexion-arrows-square.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 标注、图例与排版示例 / 面积与流带
- `pgg-1d97bf77a365cc` [web stacked area with inflexion arrows](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-area-with-inflexion-arrows.png) · FIGURE_EXAMPLE · 预览 1 · 堆叠图 / 标注、图例与排版示例 / 面积与流带
- `pgg-552fc1ac22de15` [web stacked charts square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-charts-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-b4fb173ed1cb43` [web stacked charts](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-charts.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-a04883a2e408d6` [web stacked line chart with labels square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-line-chart-with-labels-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-44b91170163fe0` [web stacked line chart with labels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-stacked-line-chart-with-labels.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-ec26d426de3679` [web streamchart with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-streamchart-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-0a274d09100785` [web streamchart with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-streamchart-with-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 河流图
- `pgg-d2e66c38b51e5e` [web text repel with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-text-repel-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-3902ddb6c3b162` [web text repel with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-text-repel-with-matplotlib.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-80fb415027ebe2` [web time series and facetting with matplotlib square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-time-series-and-facetting-with-matplotlib-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势
- `pgg-fdd85b761d83ae` [web tornado chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-tornado-chart.png) · FIGURE_EXAMPLE · 预览 1 · 发散条形图
- `pgg-7be2c9fcaf85a4` [web two maps with different granulaties square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-two-maps-with-different-granulaties-square.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-2b88595b7ded6f` [web two maps with different granulaties](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-two-maps-with-different-granulaties.png) · FIGURE_EXAMPLE · 预览 1 · 待核对原图
- `pgg-039d0442f9e527` [web waffle chart as share square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-chart-as-share-square.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-88d733bf276d6b` [web waffle chart as share](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-chart-as-share.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-b1bed4ddd51385` [web waffle chart for time series square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-chart-for-time-series-square.png) · FIGURE_EXAMPLE · 预览 1 · 折线与训练趋势 / 华夫图
- `pgg-27eec61f74b27f` [web waffle chart with groups evolution square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-chart-with-groups-evolution-square.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-291f876b2759d8` [web waffle chart with groups evolution](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-chart-with-groups-evolution.png) · FIGURE_EXAMPLE · 预览 1 · 华夫图
- `pgg-682a221c389142` [web waffle with small multiples square](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-with-small-multiples-square.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 华夫图
- `pgg-74c35cce571e32` [web waffle with small multiples](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/web-waffle-with-small-multiples.png) · FIGURE_EXAMPLE · 预览 1 · 多面板组合 / 华夫图
- `pgg-c35169d391beeb` [what is density chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/what-is-density-chart.png) · FIGURE_EXAMPLE · 预览 1 · 密度曲线
- `pgg-a5fa72ae736bdd` [world physical map](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph/world-physical-map.jpg) · FIGURE_EXAMPLE · 预览 1 · 地理与分区地图
- `pgg-23dd8738eb9834` [1num](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-a774a0000f39e5` [1num 1group](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1group.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-c6e90693407440` [1num 1group subgroup](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1group_subgroup.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-d62bdca2fe0936` [1num 1pseudonum 1group long](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1pseudonum_1group_long.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-90c560a48df7fe` [1num 1pseudonum 1group wide 150x80](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1pseudonum_1group_wide-150x80.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-723f28f968ec28` [1num 1pseudonum 1group wide 300x62](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1pseudonum_1group_wide-300x62.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-7217a83241c5d0` [1num 1pseudonum 1group wide](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/1num_1pseudonum_1group_wide.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-cd6d6a16f3123b` [2 numeric Variable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/2_numeric_Variable.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-65e61b0f8ed806` [2 numeric Variable2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/2_numeric_Variable2.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-a8969809e0218e` [2num](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/2num.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-fd4a1c9a14f198` [2num 1cat](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/2num_1cat.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-904426025937ef` [Several Numerical Variable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/table/Several_Numerical_Variable.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `pgg-cfe9a86bed67a6` [1 basic barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/1-basic-barplot.ipynb) · TUTORIAL · 预览 8 · 分组柱状图
- `pgg-70e0e7b24f21d2` [10 barplot with number of observation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/10-barplot-with-number-of-observation.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 分组柱状图
- `pgg-157b42505695e0` [100 calling a color with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/100-calling-a-color-with-seaborn.ipynb) · TUTORIAL · 预览 1 · 配色与视觉样式
- `pgg-468bcca6f97936` [101 make a color palette with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/101-make-a-color-palette-with-seaborn.ipynb) · TUTORIAL · 预览 6 · 配色与视觉样式
- `pgg-5f5e094d903b68` [104 seaborn themes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/104-seaborn-themes.ipynb) · TUTORIAL · 预览 10 · 配色与视觉样式
- `pgg-cd86a64711c916` [106 seaborn style on matplotlib plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/106-seaborn-style-on-matplotlib-plot.ipynb) · TUTORIAL · 预览 2 · 配色与视觉样式
- `pgg-a63857639c2d28` [11 grouped barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/11-grouped-barplot.ipynb) · TUTORIAL · 预览 0 · 分组柱状图
- `pgg-ddf996089f9577` [110 basic correlation matrix with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/110-basic-correlation-matrix-with-seaborn.ipynb) · TUTORIAL · 预览 1 · 热力矩阵
- `pgg-a1a63d5f26c059` [111 custom correlogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/111-custom-correlogram.ipynb) · TUTORIAL · 预览 7 · 成对关系矩阵
- `pgg-e4005741f39798` [12 stacked barplot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/12-stacked-barplot-with-matplotlib.ipynb) · TUTORIAL · 预览 3 · 分组柱状图
- `pgg-c8d0bd0689183f` [120 line chart with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/120-line-chart-with-matplotlib.ipynb) · TUTORIAL · 预览 3 · 折线与训练趋势
- `pgg-60493a70f7048d` [121 line chart customization](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/121-line-chart-customization.ipynb) · TUTORIAL · 预览 5 · 折线与训练趋势
- `pgg-9fe6aa070b7b94` [122 multiple lines chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/122-multiple-lines-chart.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-38820cfa547dec` [123 highlight a line in line plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/123-highlight-a-line-in-line-plot.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-96641352e4324b` [124 spaghetti plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/124-spaghetti-plot.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-47eacbb5063862` [125 small multiples for line chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/125-small-multiples-for-line-chart.ipynb) · TUTORIAL · 预览 2 · 多面板组合 / 折线与训练趋势
- `pgg-a50422593437a4` [13 percent stacked barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/13-percent-stacked-barplot.ipynb) · TUTORIAL · 预览 0 · 分组柱状图
- `pgg-0052e3bed55ff5` [130 basic matplotlib scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/130-basic-matplotlib-scatterplot.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-9e86e7cc739d76` [131 custom a matplotlib scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/131-custom-a-matplotlib-scatterplot.ipynb) · TUTORIAL · 预览 5 · 散点与拟合关系
- `pgg-f4c24ecdfa222b` [132 basic connected scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/132-basic-connected-scatterplot.ipynb) · TUTORIAL · 预览 2 · 散点与拟合关系
- `pgg-e982f02258c516` [134 how to avoid overplotting with python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/134-how-to-avoid-overplotting-with-python.ipynb) · TUTORIAL · 预览 13 · 样本散点与蜂群
- `pgg-a4f01f924107c9` [140 basic pieplot with panda](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/140-basic-pieplot-with-panda.ipynb) · TUTORIAL · 预览 2 · 饼图
- `pgg-deb2e4e22d98c3` [150 parallel plot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/150-parallel-plot-with-pandas.ipynb) · TUTORIAL · 预览 1 · 平行坐标
- `pgg-d8bb6f4eb1310a` [160 basic donut plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/160-basic-donut-plot.ipynb) · TUTORIAL · 预览 1 · 环形与嵌套环形图
- `pgg-645f52441011ca` [161 custom matplotlib donut plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/161-custom-matplotlib-donut-plot.ipynb) · TUTORIAL · 预览 6 · 环形与嵌套环形图
- `pgg-efae15c7e062a6` [162 change background of donut plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/162-change-background-of-donut-plot.ipynb) · TUTORIAL · 预览 1 · 环形与嵌套环形图
- `pgg-c4687e75760aac` [163 donut plot with subgroups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/163-donut-plot-with-subgroups.ipynb) · TUTORIAL · 预览 1 · 环形与嵌套环形图
- `pgg-b18ca5c6a8ff5c` [170 basic venn diagram with 2 groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/170-basic-venn-diagram-with-2-groups.ipynb) · TUTORIAL · 预览 1 · Venn 与集合交集
- `pgg-060b8fd74a53f2` [171 basic venn diagram with 3 groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/171-basic-venn-diagram-with-3-groups.ipynb) · TUTORIAL · 预览 1 · Venn 与集合交集
- `pgg-b66454fb9b13c4` [172 custom venn diagram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/172-custom-venn-diagram.ipynb) · TUTORIAL · 预览 3 · Venn 与集合交集
- `pgg-4f37cda5526da7` [173 elaborated venn diagram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/173-elaborated-venn-diagram.ipynb) · TUTORIAL · 预览 1 · Venn 与集合交集
- `pgg-0769a88027c56e` [174 change background colour of venn diagram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/174-change-background-colour-of-venn-diagram.ipynb) · TUTORIAL · 预览 1 · 配色与视觉样式 / Venn 与集合交集
- `pgg-8662718d5ff8ea` [180 basic lollipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/180-basic-lollipop-plot.ipynb) · TUTORIAL · 预览 4 · 棒棒糖图
- `pgg-36f3cd4cb4124f` [181 custom lollipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/181-custom-lollipop-plot.ipynb) · TUTORIAL · 预览 6 · 棒棒糖图
- `pgg-a5ccde34297ae7` [182 vertical lollipop plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/182-vertical-lollipop-plot.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图
- `pgg-84d2bde202df94` [183 highlight a group in lollipop](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/183-highlight-a-group-in-lollipop.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图
- `pgg-6d219c5ce2beec` [184 lollipop plot with 2 groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/184-lollipop-plot-with-2-groups.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图
- `pgg-6f25523ff8782f` [185 lollipop plot with conditional color](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/185-lollipop-plot-with-conditional-color.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图 / 配色与视觉样式
- `pgg-68c0243f28bbff` [190 custom matplotlib title](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/190-custom-matplotlib-title.ipynb) · TUTORIAL · 预览 10 · 标注、图例与排版示例
- `pgg-7ffc83f47ff1ff` [191 custom axis on matplotlib chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/191-custom-axis-on-matplotlib-chart.ipynb) · TUTORIAL · 预览 6 · 标注、图例与排版示例
- `pgg-52cce60dea799a` [192 about matplotlib margins](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/192-about-matplotlib-margins.ipynb) · TUTORIAL · 预览 4 · 待核对原图
- `pgg-e50c815ad66000` [193 annotate matplotlib chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/193-annotate-matplotlib-chart.ipynb) · TUTORIAL · 预览 7 · 标注、图例与排版示例
- `pgg-9de7e9a5bd85c5` [194 split the graphic window with subplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/194-split-the-graphic-window-with-subplot.ipynb) · TUTORIAL · 预览 8 · 标注、图例与排版示例
- `pgg-19eed64f5fb61b` [196 select one color with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/196-select-one-color-with-matplotlib.ipynb) · TUTORIAL · 预览 6 · 配色与视觉样式
- `pgg-104ea1fb64691f` [197 available color palettes with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/197-available-color-palettes-with-matplotlib.ipynb) · TUTORIAL · 预览 6 · 配色与视觉样式
- `pgg-373131f8fb224c` [199 matplotlib style sheets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/199-matplotlib-style-sheets.ipynb) · TUTORIAL · 预览 3 · 配色与视觉样式
- `pgg-fc92f4cce5a877` [2 horizontal barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/2-horizontal-barplot.ipynb) · TUTORIAL · 预览 8 · 分组柱状图
- `pgg-0e58481f1ebeea` [20 basic histogram seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/20-basic-histogram-seaborn.ipynb) · TUTORIAL · 预览 2 · 直方图
- `pgg-958fd88c518496` [200 basic treemap with python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/200-basic-treemap-with-python.ipynb) · TUTORIAL · 预览 1 · 矩形树图
- `pgg-37dedfcc859c7e` [201 control the color of treemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/201-control-the-color-of-treemap.ipynb) · TUTORIAL · 预览 1 · 矩形树图 / 配色与视觉样式
- `pgg-8aff2ef3eb825a` [202 treemap with colors mapped on values](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/202-treemap-with-colors-mapped-on-values.ipynb) · TUTORIAL · 预览 1 · 矩形树图 / 配色与视觉样式
- `pgg-e5d627bed26bd5` [21 control rug and density on seaborn histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/21-control-rug-and-density-on-seaborn-histogram.ipynb) · TUTORIAL · 预览 4 · 直方图 / 密度曲线
- `pgg-d970478db30fa4` [220 sankey diagram with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/220-sankey-diagram-with-matplotlib.ipynb) · TUTORIAL · 预览 1 · 桑基与流向图
- `pgg-ddeab8a05233a3` [23 90degree rotated histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/23-90degree-rotated-histogram.ipynb) · TUTORIAL · 预览 1 · 直方图
- `pgg-8535b88b620e7a` [231 chord diagram with bokeh](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/231-chord-diagram-with-bokeh.ipynb) · TUTORIAL · 预览 1 · 弦图
- `pgg-f4bdf3433f96fc` [24 histogram with a boxplot on top seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/24-histogram-with-a-boxplot-on-top-seaborn.ipynb) · TUTORIAL · 预览 1 · 直方图 / 箱线图
- `pgg-5b573698fdb5ec` [240 basic area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/240-basic-area-chart.ipynb) · TUTORIAL · 预览 1 · 面积与流带
- `pgg-4008277c77e971` [241 improve area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/241-improve-area-chart.ipynb) · TUTORIAL · 预览 3 · 面积与流带
- `pgg-7574ddad4e6cb1` [242 area chart and faceting](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/242-area-chart-and-faceting.ipynb) · TUTORIAL · 预览 1 · 面积与流带 / 多面板组合
- `pgg-2500d9f2c214b9` [243 area chart with white grid](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/243-area-chart-with-white-grid.ipynb) · TUTORIAL · 预览 1 · 面积与流带
- `pgg-82c2619ba35846` [25 histogram with several variables seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/25-histogram-with-several-variables-seaborn.ipynb) · TUTORIAL · 预览 2 · 直方图
- `pgg-7e0f83b365c76d` [250 basic stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/250-basic-stacked-area-chart.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带
- `pgg-534e21dd689da3` [251 stacked area chart with seaborn style](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/251-stacked-area-chart-with-seaborn-style.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-487365c775899f` [252 baseline options for stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/252-baseline-options-for-stacked-area-chart.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带
- `pgg-f6390f2dbac59a` [253 control the color in stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/253-control-the-color-in-stacked-area-chart.ipynb) · TUTORIAL · 预览 7 · 堆叠图 / 面积与流带 / 配色与视觉样式
- `pgg-643370e4b19f19` [254 pandas stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/254-pandas-stacked-area-chart.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带
- `pgg-f6c7c830f61bf9` [255 percentage stacked area chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/255-percentage-stacked-area-chart.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带
- `pgg-da1cb557da4e2b` [260 basic wordcloud](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/260-basic-wordcloud.ipynb) · TUTORIAL · 预览 1 · 词云
- `pgg-af4f00b70749f9` [261 custom python wordcloud](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/261-custom-python-wordcloud.ipynb) · TUTORIAL · 预览 4 · 词云
- `pgg-74eb146e9fd3cd` [262 wordcloud with specific shape](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/262-wordcloud-with-specific-shape.ipynb) · TUTORIAL · 预览 2 · 词云
- `pgg-0987c93941d928` [270 basic bubble plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/270-basic-bubble-plot.ipynb) · TUTORIAL · 预览 1 · 气泡图
- `pgg-57d38c788ce556` [271 custom your bubble plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/271-custom-your-bubble-plot.ipynb) · TUTORIAL · 预览 5 · 气泡图
- `pgg-ee0c49b50bf720` [272 map a color to bubble plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/272-map-a-color-to-bubble-plot.ipynb) · TUTORIAL · 预览 1 · 气泡图 / 配色与视觉样式 / 地理与分区地图
- `pgg-88e1aa63e46606` [281 basic map with basemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/281-basic-map-with-basemap.ipynb) · TUTORIAL · 预览 7 · 地理与分区地图
- `pgg-13bb0f686b92d6` [286 boundaries provided in basemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/286-boundaries-provided-in-basemap.ipynb) · TUTORIAL · 预览 3 · 地理与分区地图
- `pgg-5e573c7004615d` [288 map background with folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/288-map-background-with-folium.ipynb) · TUTORIAL · 预览 1 · 变形统计地图 / 地理与分区地图
- `pgg-5de986b77a7ecb` [292 choropleth map with folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/292-choropleth-map-with-folium.ipynb) · TUTORIAL · 预览 1 · 变形统计地图 / 地理与分区地图
- `pgg-29ed94a5a6a1b7` [3 control color of barplots](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/3-control-color-of-barplots.ipynb) · TUTORIAL · 预览 10 · 分组柱状图 / 配色与视觉样式
- `pgg-4a05ed999540d6` [30 basic boxplot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/30-basic-boxplot-with-seaborn.ipynb) · TUTORIAL · 预览 3 · 箱线图
- `pgg-379d12d446b7d7` [300 draw a connection line](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/300-draw-a-connection-line.ipynb) · TUTORIAL · 预览 3 · 折线与训练趋势
- `pgg-01f5c0ffafe3a3` [31 horizontal boxplot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/31-horizontal-boxplot-with-seaborn.ipynb) · TUTORIAL · 预览 2 · 箱线图
- `pgg-a6edf6ed99c7aa` [310 basic map with markers](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/310-basic-map-with-markers.ipynb) · TUTORIAL · 预览 4 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-eb66f261e87d91` [312 add markers on folium map](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/312-add-markers-on-folium-map.ipynb) · TUTORIAL · 预览 3 · 标注、图例与排版示例 / 变形统计地图 / 地理与分区地图
- `pgg-3b89063c6d8607` [313 bubble map with folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/313-bubble-map-with-folium.ipynb) · TUTORIAL · 预览 1 · 变形统计地图 / 气泡图 / 地理与分区地图
- `pgg-daac7a72c29cb8` [315 a world map of surf tweets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/315-a-world-map-of-surf-tweets.ipynb) · TUTORIAL · 预览 2 · 地理与分区地图
- `pgg-5ac244e74f93b9` [32 custom boxplot appearance seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/32-custom-boxplot-appearance-seaborn.ipynb) · TUTORIAL · 预览 4 · 箱线图
- `pgg-e1683e53c68664` [320 basic network from pandas data frame](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/320-basic-network-from-pandas-data-frame.ipynb) · TUTORIAL · 预览 1 · 关系网络
- `pgg-20a65abea90690` [321 custom networkx graph appearance](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/321-custom-networkx-graph-appearance.ipynb) · TUTORIAL · 预览 4 · 关系网络
- `pgg-07ae9a77c0e285` [322 network layout possibilities](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/322-network-layout-possibilities.ipynb) · TUTORIAL · 预览 5 · 关系网络 / 标注、图例与排版示例
- `pgg-1efd65bd5a409c` [323 directed or undirected network](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/323-directed-or-undirected-network.ipynb) · TUTORIAL · 预览 2 · 关系网络
- `pgg-a54cafabfa5d8b` [324 map a color to network nodes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/324-map-a-color-to-network-nodes.ipynb) · TUTORIAL · 预览 2 · 关系网络 / 配色与视觉样式 / 地理与分区地图
- `pgg-5e4addde484582` [325 map colour to the edges of a network](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/325-map-colour-to-the-edges-of-a-network.ipynb) · TUTORIAL · 预览 2 · 关系网络 / 配色与视觉样式 / 地理与分区地图
- `pgg-a1ee843a162e18` [326 background colour of network chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/326-background-colour-of-network-chart.ipynb) · TUTORIAL · 预览 1 · 关系网络 / 配色与视觉样式
- `pgg-b2b9d5122a53a1` [327 network from correlation matrix](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/327-network-from-correlation-matrix.ipynb) · TUTORIAL · 预览 1 · 关系网络 / 热力矩阵
- `pgg-96dae955148e49` [33 control colors of boxplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/33-control-colors-of-boxplot-seaborn.ipynb) · TUTORIAL · 预览 5 · 箱线图 / 配色与视觉样式
- `pgg-98a09a30ace4f5` [34 grouped boxplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/34-grouped-boxplot.ipynb) · TUTORIAL · 预览 1 · 箱线图
- `pgg-87552bd1cabc6e` [340 scatterplot animation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/340-scatterplot-animation.ipynb) · TUTORIAL · 预览 0 · 散点与拟合关系 / 动态图
- `pgg-079d7e6517742b` [341 python gapminder animation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/341-python-gapminder-animation.ipynb) · TUTORIAL · 预览 0 · 动态图
- `pgg-ef81a92fd20f03` [342 animation on 3d plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/342-animation-on-3d-plot.ipynb) · TUTORIAL · 预览 0 · 动态图 / 三维曲面与网格
- `pgg-3fc88105eca084` [35 control order of boxplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/35-control-order-of-boxplot.ipynb) · TUTORIAL · 预览 2 · 箱线图
- `pgg-0a2a7731789275` [36 add jitter over boxplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/36-add-jitter-over-boxplot-seaborn.ipynb) · TUTORIAL · 预览 1 · 箱线图 / 样本散点与蜂群
- `pgg-e59d605f359ea1` [370 3d scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/370-3d-scatterplot.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系 / 三维曲面与网格
- `pgg-b6d37a455a6165` [371 surface plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/371-surface-plot.ipynb) · TUTORIAL · 预览 4 · 三维曲面与网格
- `pgg-24d499b07502ba` [372 3d pca result](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/372-3d-pca-result.ipynb) · TUTORIAL · 预览 1 · 嵌入与降维 / 三维曲面与网格
- `pgg-f0b7bc89948a18` [38 show number of observation on boxplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/38-show-number-of-observation-on-boxplot.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 箱线图
- `pgg-ccc701e4b29a0c` [39 hidden data under boxplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/39-hidden-data-under-boxplot.ipynb) · TUTORIAL · 预览 4 · 箱线图
- `pgg-40428c50bff097` [390 basic radar chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/390-basic-radar-chart.ipynb) · TUTORIAL · 预览 1 · 雷达图
- `pgg-4bf05a6db8ea6d` [391 radar chart with several individuals](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/391-radar-chart-with-several-individuals.ipynb) · TUTORIAL · 预览 1 · 雷达图
- `pgg-2c0e3553cee291` [392 use faceting for radar chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/392-use-faceting-for-radar-chart.ipynb) · TUTORIAL · 预览 0 · 多面板组合 / 雷达图
- `pgg-7c600e06b1e6bd` [4 add title and axis label](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/4-add-title-and-axis-label.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-0fec97c0b078cf` [40 basic scatterplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/40-basic-scatterplot-seaborn.ipynb) · TUTORIAL · 预览 2 · 散点与拟合关系
- `pgg-ce514cc0bb8a1d` [400 basic dendrogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/400-basic-dendrogram.ipynb) · TUTORIAL · 预览 1 · 层次树与树状聚类
- `pgg-c96afc82249e04` [401 customised dendrogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/401-customised-dendrogram.ipynb) · TUTORIAL · 预览 7 · 层次树与树状聚类
- `pgg-533a5fb0ff7ae2` [402 color dendrogram labels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/402-color-dendrogram-labels.ipynb) · TUTORIAL · 预览 1 · 层次树与树状聚类 / 标注、图例与排版示例 / 配色与视觉样式
- `pgg-685f85c5cd6b4e` [404 dendrogram with heat map](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/404-dendrogram-with-heat-map.ipynb) · TUTORIAL · 预览 12 · 层次树与树状聚类 / 热力矩阵 / 地理与分区地图
- `pgg-25588e0accabd5` [405 dendrogram with heatmap and coloured leaves](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/405-dendrogram-with-heatmap-and-coloured-leaves.ipynb) · TUTORIAL · 预览 1 · 层次树与树状聚类 / 热力矩阵
- `pgg-d15fa837a9444e` [406 chord diagram mne](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/406-chord-diagram_mne.ipynb) · TUTORIAL · 预览 3 · 弦图
- `pgg-1f9c3a036c0169` [41 control marker features](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/41-control-marker-features.ipynb) · TUTORIAL · 预览 2 · 标注、图例与排版示例
- `pgg-a2944b3bf377ae` [42 custom linear regression fit seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/42-custom-linear-regression-fit-seaborn.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-eb9b1250753be6` [43 use categorical variable to color scatterplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/43-use-categorical-variable-to-color-scatterplot-seaborn.ipynb) · TUTORIAL · 预览 5 · 散点与拟合关系 / 配色与视觉样式
- `pgg-5434b6fed9dfcb` [44 control axis limits of plot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/44-control-axis-limits-of-plot-seaborn.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-d2a2d31ff01093` [45 control color of each marker seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/45-control-color-of-each-marker-seaborn.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 配色与视觉样式
- `pgg-00e1dd8068e0b5` [46 add text annotation on scatterplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/46-add-text-annotation-on-scatterplot.ipynb) · TUTORIAL · 预览 3 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-8a0db263a47240` [47 faceted scatter plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/47-faceted-scatter-plot-with-seaborn.ipynb) · TUTORIAL · 预览 2 · 散点与拟合关系
- `pgg-c502eb251ab78c` [5 control width and space in barplots](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/5-control-width-and-space-in-barplots.ipynb) · TUTORIAL · 预览 2 · 分组柱状图
- `pgg-395958fd7ce3f8` [50 basic violinplot and input formats](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/50-basic-violinplot-and-input-formats.ipynb) · TUTORIAL · 预览 3 · 小提琴与分组小提琴
- `pgg-8b19dff28af341` [500 network chart with edge bundling](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/500-network-chart-with-edge-bundling.ipynb) · TUTORIAL · 预览 1 · 关系网络
- `pgg-0c124662317edd` [501 parallel plot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/501-parallel-plot-seaborn.ipynb) · TUTORIAL · 预览 1 · 平行坐标
- `pgg-d10375c34b412b` [502 violinplot and swarmplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/502-violinplot-and-swarmplot.ipynb) · TUTORIAL · 预览 1 · 小提琴与分组小提琴 / 样本散点与蜂群
- `pgg-5fb4743a335043` [503 waffle chart introduction](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/503-waffle-chart-introduction.ipynb) · TUTORIAL · 预览 3 · 华夫图
- `pgg-f8105b10f341ff` [504 histogram with colored tails](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/504-histogram-with-colored-tails.ipynb) · TUTORIAL · 预览 1 · 直方图
- `pgg-2521bd52a45c35` [505 Introduction to swarm plot in seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/505-Introduction-to-swarm-plot-in-seaborn.ipynb) · TUTORIAL · 预览 3 · 样本散点与蜂群
- `pgg-c3a4c3406195ca` [506 histogram with small mutliples](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/506-histogram-with-small-mutliples.ipynb) · TUTORIAL · 预览 1 · 直方图
- `pgg-eae1cf52c3f6b4` [508 connected scatter plot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/508-connected-scatter-plot-seaborn.ipynb) · TUTORIAL · 预览 4 · 散点与拟合关系
- `pgg-aa395a01a6ba71` [509 introduction to swarm plot in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/509-introduction-to-swarm-plot-in-matplotlib.ipynb) · TUTORIAL · 预览 3 · 样本散点与蜂群
- `pgg-4a3fa6c1a212f4` [51 horizontal violinplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/51-horizontal-violinplot.ipynb) · TUTORIAL · 预览 1 · 小提琴与分组小提琴
- `pgg-de6dd0928bf27f` [511 interactive scatterplot with plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/511-interactive-scatterplot-with-plotly.ipynb) · TUTORIAL · 预览 3 · 散点与拟合关系
- `pgg-fa7b4484a3b81a` [512 line chart seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/512-line-chart-seaborn.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势
- `pgg-601902b7b36797` [513 add logo matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/513-add-logo-matplotlib.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-00b0551e776cdb` [514 interactive line chart plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/514-interactive-line-chart-plotly.ipynb) · TUTORIAL · 预览 3 · 折线与训练趋势
- `pgg-ba249d11481cfc` [515 intro pca graph python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/515-intro-pca-graph-python.ipynb) · TUTORIAL · 预览 3 · 嵌入与降维
- `pgg-6ffe4961c38524` [516 line chart with annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/516-line-chart-with-annotations.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 折线与训练趋势
- `pgg-d10e1f03457ddc` [52 custom seaborn violinplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/52-custom-seaborn-violinplot.ipynb) · TUTORIAL · 预览 2 · 小提琴与分组小提琴
- `pgg-6fb19292e5027f` [520 the two plotly APIs](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/520-the-two-plotly-APIs.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-0082a51487c319` [521 interactive line chart with plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/521-interactive-line-chart-with-plotly.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势
- `pgg-5b0923ae9bd883` [522 plotly customize title](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/522-plotly-customize-title.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-9e6d961e4defbf` [523 plotly add annotation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/523-plotly-add-annotation.ipynb) · TUTORIAL · 预览 2 · 标注、图例与排版示例
- `pgg-7d83e741e9fa33` [524 area chart over flexible baseline](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/524-area-chart-over-flexible-baseline.ipynb) · TUTORIAL · 预览 2 · 面积与流带
- `pgg-2f0b9a04a6d5a8` [525 line chart log transform](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/525-line-chart-log-transform.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-8696362cf606f3` [527 introduction to histogram with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/527-introduction-to-histogram-with-pandas.ipynb) · TUTORIAL · 预览 1 · 直方图
- `pgg-fb5d6c5fd69815` [528 customizing histogram with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/528-customizing-histogram-with-pandas.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 直方图
- `pgg-80b2e1ff8f0db1` [529 multi group histogram pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/529-multi-group-histogram-pandas.ipynb) · TUTORIAL · 预览 3 · 直方图
- `pgg-9159c1de738c74` [53 control color of seaborn violinplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/53-control-color-of-seaborn-violinplot.ipynb) · TUTORIAL · 预览 4 · 小提琴与分组小提琴 / 配色与视觉样式
- `pgg-5b19f85ea8618a` [530 introduction to linechart with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/530-introduction-to-linechart-with-pandas.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-995ad674adc14d` [531 customizing linecharts with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/531-customizing-linecharts-with-pandas.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 折线与训练趋势
- `pgg-99733b9ec8cac4` [532 customizing circular barplot in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/532-customizing-circular-barplot-in-matplotlib.ipynb) · TUTORIAL · 预览 3 · 标注、图例与排版示例 / 分组柱状图
- `pgg-832f37738e4868` [532 linecharts mutliple groups with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/532-linecharts-mutliple-groups-with-pandas.ipynb) · TUTORIAL · 预览 3 · 折线与训练趋势
- `pgg-c6c573f4b208d6` [533 introduction boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/533-introduction-boxplots-matplotlib.ipynb) · TUTORIAL · 预览 1 · 箱线图
- `pgg-60b0cd67eb2d6c` [534 highly customized layout](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/534-highly-customized-layout.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-6d38c2f430d02a` [535 introduction to scatter plot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/535-introduction-to-scatter-plot-with-pandas.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-3f88656af0b017` [536 customizing scatter plots with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/536-customizing-scatter-plots-with-pandas.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 散点与拟合关系
- `pgg-9d6f1c9030e84b` [537 scatter plots grouped by color with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/537-scatter-plots-grouped-by-color-with-pandas.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系 / 配色与视觉样式
- `pgg-06855226b78153` [538 introduction to barplot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/538-introduction-to-barplot-with-pandas.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-42367b6a75fe5d` [539 customizing barplot with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/539-customizing-barplot-with-pandas.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 分组柱状图
- `pgg-3c2fb4418f2ebd` [54 grouped violinplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/54-grouped-violinplot.ipynb) · TUTORIAL · 预览 2 · 小提琴与分组小提琴
- `pgg-589c9c0a733acb` [540 barplots grouped by color with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/540-barplots-grouped-by-color-with-pandas.ipynb) · TUTORIAL · 预览 1 · 分组柱状图 / 配色与视觉样式
- `pgg-32ca36a2656040` [541 waffle chart with additionnal grouping](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/541-waffle-chart-with-additionnal-grouping.ipynb) · TUTORIAL · 预览 1 · 华夫图
- `pgg-ea9a11313b378f` [542 custom boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/542-custom-boxplots-matplotlib.ipynb) · TUTORIAL · 预览 1 · 箱线图
- `pgg-b384a94776c7e6` [543 grouped boxplots matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/543-grouped-boxplots-matplotlib.ipynb) · TUTORIAL · 预览 1 · 箱线图
- `pgg-920af3aa43ee3f` [547 stacked barplots with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/547-stacked-barplots-with-pandas.ipynb) · TUTORIAL · 预览 2 · 分组柱状图
- `pgg-996389bfc92a5e` [548 intro candle stick matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/548-intro-candle-stick-matplotlib.ipynb) · TUTORIAL · 预览 1 · 蜡烛与区间范围图
- `pgg-6693510a0c595d` [549 candle stick with moving average](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/549-candle-stick-with-moving-average.ipynb) · TUTORIAL · 预览 1 · 蜡烛与区间范围图
- `pgg-112d7d455efd4c` [55 control order of groups in violinplot seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/55-control-order-of-groups-in-violinplot-seaborn.ipynb) · TUTORIAL · 预览 2 · 小提琴与分组小提琴
- `pgg-96e86120b4c233` [550 intro table with pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/550-intro-table-with-pandas.ipynb) · TUTORIAL · 预览 2 · 结果表与分组表
- `pgg-29f70424f75e31` [551 student t test visualization](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/551-student-t-test-visualization.ipynb) · TUTORIAL · 预览 2 · 统计检验可视化
- `pgg-cc9b1735a0d692` [552 table combined with plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/552-table-combined-with-plot.ipynb) · TUTORIAL · 预览 1 · 结果表与分组表
- `pgg-b120e4dbd828c6` [553 intro candle stick plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/553-intro-candle-stick-plotly.ipynb) · TUTORIAL · 预览 1 · 蜡烛与区间范围图
- `pgg-217f5bdf90bec2` [554 custom candle stick plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/554-custom-candle-stick-plotly.ipynb) · TUTORIAL · 预览 1 · 蜡烛与区间范围图
- `pgg-4c163ee4ba48b7` [555 candle stick with moving average plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/555-candle-stick-with-moving-average-plotly.ipynb) · TUTORIAL · 预览 1 · 蜡烛与区间范围图
- `pgg-88a104050046ca` [556 visualize linear regression](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/556-visualize-linear-regression.ipynb) · TUTORIAL · 预览 2 · 散点与拟合关系
- `pgg-27722f9f9732c6` [557 anova visualization with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/557-anova-visualization-with-matplotlib.ipynb) · TUTORIAL · 预览 3 · 统计检验可视化
- `pgg-57f0a1fed9a201` [558 waffle bar chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/558-waffle-bar-chart.ipynb) · TUTORIAL · 预览 3 · 分组柱状图 / 华夫图
- `pgg-5c0ec4ef7706a3` [560 introduction plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/560-introduction-plottable.ipynb) · TUTORIAL · 预览 1 · 结果表与分组表
- `pgg-7436d21fa3ebd6` [561 control colors in plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/561-control-colors-in-plottable.ipynb) · TUTORIAL · 预览 5 · 结果表与分组表 / 配色与视觉样式
- `pgg-4712f075c52342` [562 add images in plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/562-add-images-in-plottable.ipynb) · TUTORIAL · 预览 2 · 结果表与分组表
- `pgg-a5ead3907c813f` [563 graph in plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/563-graph-in-plottable.ipynb) · TUTORIAL · 预览 5 · 结果表与分组表
- `pgg-813e07f9c3238e` [564 publication ready table with plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/564-publication-ready-table-with-plottable.ipynb) · TUTORIAL · 预览 2 · 结果表与分组表
- `pgg-0c1b8312afcb3c` [565 arc diagram with arcplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/565-arc-diagram-with-arcplot.ipynb) · TUTORIAL · 预览 5 · 弧线网络
- `pgg-ec90c1fa9ceee0` [570 custom streamchart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/570-custom-streamchart.ipynb) · TUTORIAL · 预览 4 · 河流图
- `pgg-5851029f96b242` [571 radar chart with plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/571-radar-chart-with-plotly.ipynb) · TUTORIAL · 预览 2 · 雷达图
- `pgg-d7216f9919da81` [573 introduction scatterplot plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/573-introduction-scatterplot-plotnine.ipynb) · TUTORIAL · 预览 3 · 散点与拟合关系
- `pgg-c5f973820eb227` [574 custom marker scatter plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/574-custom-marker-scatter-plotnine.ipynb) · TUTORIAL · 预览 4 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-6f273211a464a3` [575 custom theme plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/575-custom-theme-plotnine.ipynb) · TUTORIAL · 预览 9 · 配色与视觉样式
- `pgg-717467951f6337` [575 distribution plot with quantiles](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/575-distribution-plot-with-quantiles.ipynb) · TUTORIAL · 预览 9 · 分位数分布图
- `pgg-38b0e81253b9f3` [576 introduction barplot plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/576-introduction-barplot-plotnine.ipynb) · TUTORIAL · 预览 3 · 分组柱状图
- `pgg-380e42738ca792` [577 customize barplot plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/577-customize-barplot-plotnine.ipynb) · TUTORIAL · 预览 3 · 分组柱状图
- `pgg-3cd253b659ecf5` [578 introduction histogram plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/578-introduction-histogram-plotnine.ipynb) · TUTORIAL · 预览 3 · 直方图
- `pgg-028ce959f25864` [579 multiple histograms plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/579-multiple-histograms-plotnine.ipynb) · TUTORIAL · 预览 2 · 直方图
- `pgg-75e4726fd17c8c` [58 show number of observation on violinplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/58-show-number-of-observation-on-violinplot.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 小提琴与分组小提琴
- `pgg-f2b8f0fc111fb1` [580 simple interactive treemap plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/580-simple-interactive-treemap-plotly.ipynb) · TUTORIAL · 预览 0 · 矩形树图
- `pgg-bbc6cfec1357fd` [581 custom treemap plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/581-custom-treemap-plotly.ipynb) · TUTORIAL · 预览 0 · 矩形树图
- `pgg-7600f1071d1384` [582 simple barplot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/582-simple-barplot-plotly.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-31b6a817670f22` [583 stacked barplot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/583-stacked-barplot-plotly.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-bd38d3db119c1b` [584 introduction hatch matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/584-introduction-hatch-matplotlib.ipynb) · TUTORIAL · 预览 4 · 标注、图例与排版示例
- `pgg-637f9010009011` [585 introduction great tables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/585-introduction-great-tables.ipynb) · TUTORIAL · 预览 7 · 结果表与分组表
- `pgg-cb4133c530d8c4` [585 legend for categorical data matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/585-legend-for-categorical-data-matplotlib.ipynb) · TUTORIAL · 预览 7 · 标注、图例与排版示例
- `pgg-a22c67f0cd174a` [586 customization great tables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/586-customization-great-tables.ipynb) · TUTORIAL · 预览 1 · 结果表与分组表
- `pgg-c26771d00e5254` [587 how to use colormap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/587-how-to-use-colormap.ipynb) · TUTORIAL · 预览 1 · 配色与视觉样式
- `pgg-940eca30fb93cb` [588 change map projection in python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/588-change-map-projection-in-python.ipynb) · TUTORIAL · 预览 0 · 地理与分区地图
- `pgg-cd496bc0696219` [589 how to change coordinate system](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/589-how-to-change-coordinate-system.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-2769ba1715b0a6` [590 advanced treemap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/590-advanced-treemap.ipynb) · TUTORIAL · 预览 4 · 矩形树图
- `pgg-fea9dbc168c10f` [591 arrows with inflexion point](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/591-arrows-with-inflexion-point.ipynb) · TUTORIAL · 预览 2 · 标注、图例与排版示例
- `pgg-fafd5948acd757` [592 non contiguous cartogram in python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/592-non-contiguous-cartogram-in-python.ipynb) · TUTORIAL · 预览 2 · 变形统计地图
- `pgg-470d510a704c3c` [593 customize bubble map with folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/593-customize-bubble-map-with-folium.ipynb) · TUTORIAL · 预览 2 · 变形统计地图 / 气泡图 / 地理与分区地图
- `pgg-dcee6ef193ec11` [594 introduction flexitext](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/594-introduction-flexitext.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-b63e2a24123cea` [595 advanced flexitext features](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/595-advanced-flexitext-features.ipynb) · TUTORIAL · 预览 2 · 标注、图例与排版示例
- `pgg-617b2713e95e84` [597 introduction to geopandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/597-introduction-to-geopandas.ipynb) · TUTORIAL · 预览 0 · 地理与分区地图
- `pgg-5c07744f732989` [6 change bars texture](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/6-change-bars-texture.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 分组柱状图
- `pgg-ed1f2da71de137` [601 bump chart with bumplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/601-bump-chart-with-bumplot.ipynb) · TUTORIAL · 预览 0 · 排名变化图
- `pgg-01ea483bbc2e23` [7 custom barplot layout](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/7-custom-barplot-layout.ipynb) · TUTORIAL · 预览 3 · 分组柱状图 / 标注、图例与排版示例
- `pgg-db29134ea336fb` [70 basic density plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/70-basic-density-plot-with-seaborn.ipynb) · TUTORIAL · 预览 2 · 密度曲线
- `pgg-119856385be2a8` [71 density plot with shade seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/71-density-plot-with-shade-seaborn.ipynb) · TUTORIAL · 预览 1 · 密度曲线
- `pgg-f73c126fae9d6f` [72 horizontal density plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/72-horizontal-density-plot.ipynb) · TUTORIAL · 预览 1 · 密度曲线
- `pgg-7f880a4ca4c825` [73 control bandwidth of seaborn density plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/73-control-bandwidth-of-seaborn-density-plot.ipynb) · TUTORIAL · 预览 2 · 密度曲线
- `pgg-d8ca864c4f6fce` [74 density plot of several variables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/74-density-plot-of-several-variables.ipynb) · TUTORIAL · 预览 1 · 密度曲线
- `pgg-3c5c4e47136899` [8 add confidence interval on barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/8-add-confidence-interval-on-barplot.ipynb) · TUTORIAL · 预览 1 · Forest 效应区间 / 分组柱状图
- `pgg-87185e2f615073` [80 contour plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/80-contour-plot-with-seaborn.ipynb) · TUTORIAL · 预览 3 · 等值线
- `pgg-2b935e8082cfce` [82 marginal plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/82-marginal-plot-with-seaborn.ipynb) · TUTORIAL · 预览 9 · 联合与边缘分布
- `pgg-2fcd93373b9989` [83 basic 2d histograms with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/83-basic-2d-histograms-with-matplotlib.ipynb) · TUTORIAL · 预览 9 · 直方图
- `pgg-ad7ccaaaf626dc` [84 hexbin plot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/84-hexbin-plot-with-matplotlib.ipynb) · TUTORIAL · 预览 8 · 六边形密度图
- `pgg-110f5791c4f52a` [85 density plot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/85-density-plot-with-matplotlib.ipynb) · TUTORIAL · 预览 6 · 密度曲线
- `pgg-e504671b707c35` [86 avoid overlapping in scatterplot with 2d density](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/86-avoid-overlapping-in-scatterplot-with-2d-density.ipynb) · TUTORIAL · 预览 2 · 散点与拟合关系 / 密度曲线
- `pgg-c49b1c1421c01f` [90 heatmaps with various input format](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/90-heatmaps-with-various-input-format.ipynb) · TUTORIAL · 预览 4 · 热力矩阵
- `pgg-82b13cd6628274` [91 customize seaborn heatmap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/91-customize-seaborn-heatmap.ipynb) · TUTORIAL · 预览 5 · 热力矩阵
- `pgg-b4c91db4d2be30` [92 control color in seaborn heatmaps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/92-control-color-in-seaborn-heatmaps.ipynb) · TUTORIAL · 预览 11 · 热力矩阵 / 配色与视觉样式
- `pgg-0e59aded4961a2` [94 use normalization on seaborn heatmap](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/94-use-normalization-on-seaborn-heatmap.ipynb) · TUTORIAL · 预览 4 · 热力矩阵
- `pgg-bb8cc2e60e3d54` [template](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/_template.ipynb) · TUTORIAL · 预览 0 · 多面板组合
- `pgg-4a326976e6665d` [advanced custom annotations matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/advanced-custom-annotations-matplotlib.ipynb) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `pgg-8d8bfd4c4f2e01` [area fill between two lines in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/area-fill-between-two-lines-in-matplotlib.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势 / 面积与流带
- `pgg-5715c297affdb3` [available colors in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/available-colors-in-matplotlib.ipynb) · TUTORIAL · 预览 0 · 配色与视觉样式
- `pgg-896eef594e55bf` [basic barplot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/basic-barplot-with-seaborn.ipynb) · TUTORIAL · 预览 3 · 分组柱状图
- `pgg-04b239d3339570` [basic histogram in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/basic-histogram-in-matplotlib.ipynb) · TUTORIAL · 预览 2 · 直方图
- `pgg-84a81e4deffc5c` [basic sankey diagram with pysankey](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/basic-sankey-diagram-with-pysankey.ipynb) · TUTORIAL · 预览 0 · 桑基与流向图
- `pgg-da10990ffba20a` [basic time series with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/basic-time-series-with-matplotlib.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-0f0251bdeabb91` [bubble plot with seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/bubble-plot-with-seaborn.ipynb) · TUTORIAL · 预览 1 · 气泡图
- `pgg-d650b588e91fee` [calendar heatmaps with python and matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/calendar-heatmaps-with-python-and-matplotlib.ipynb) · TUTORIAL · 预览 0 · 热力矩阵 / 日历热图
- `pgg-32d72cb976f959` [categorical color palette](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/categorical-color-palette.ipynb) · TUTORIAL · 预览 0 · 配色与视觉样式
- `pgg-087a78b78055f9` [chord diagram python chord](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/chord-diagram-python-chord.ipynb) · TUTORIAL · 预览 0 · 弦图
- `pgg-66aba56805d849` [choropleth map geopandas python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/choropleth-map-geopandas-python.ipynb) · TUTORIAL · 预览 1 · 地理与分区地图
- `pgg-ef017cc989ec2d` [choropleth map plotly python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/choropleth-map-plotly-python.ipynb) · TUTORIAL · 预览 0 · 地理与分区地图
- `pgg-2c0e6489d09620` [circular barplot basic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/circular-barplot-basic.ipynb) · TUTORIAL · 预览 5 · 分组柱状图
- `pgg-032b6b4a809340` [circular barplot with groups](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/circular-barplot-with-groups.ipynb) · TUTORIAL · 预览 4 · 分组柱状图
- `pgg-4a34f7c4309640` [circular packing 1 level hierarchy](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/circular-packing-1-level-hierarchy.ipynb) · TUTORIAL · 预览 3 · 圆形打包图
- `pgg-59477d95f7e3c7` [circular packing several levels of hierarchy](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/circular-packing-several-levels-of-hierarchy.ipynb) · TUTORIAL · 预览 1 · 圆形打包图
- `pgg-b36f633a434e03` [connected scatterplot for evolution](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/connected-scatterplot-for-evolution.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-4c77f177ed7547` [continuous color palette](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/continuous-color-palette.ipynb) · TUTORIAL · 预览 0 · 配色与视觉样式
- `pgg-c0db381fe12ad6` [create your own color maps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/create-your-own-color-maps.ipynb) · TUTORIAL · 预览 0 · 配色与视觉样式
- `pgg-d45c077f534403` [custom fonts in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/custom-fonts-in-matplotlib.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-0c5407aba465f9` [custom legend with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/custom-legend-with-matplotlib.ipynb) · TUTORIAL · 预览 6 · 标注、图例与排版示例
- `pgg-e4fc6789dc0922` [custom matplotlib theme with morethemes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/custom-matplotlib-theme-with-morethemes.ipynb) · TUTORIAL · 预览 0 · 配色与视觉样式
- `pgg-66afdada0635cf` [density chart matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/density-chart-matplotlib.ipynb) · TUTORIAL · 预览 0 · 密度曲线
- `pgg-1b04a2ed888d65` [density chart multiple groups seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/density-chart-multiple-groups-seaborn.ipynb) · TUTORIAL · 预览 6 · 密度曲线
- `pgg-e72b716995e81f` [density mirror](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/density-mirror.ipynb) · TUTORIAL · 预览 1 · 密度曲线
- `pgg-a5270aa8f1f53d` [error bars on barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/error-bars-on-barplot.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-8640a05cf17e7b` [grouped barplot with the total of each group represented as a grey rectangle](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/grouped-barplot-with-the-total-of-each-group-represented-as-a-grey-rectangle.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-2d545467fda97c` [grouped barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/grouped-barplot.ipynb) · TUTORIAL · 预览 2 · 分组柱状图
- `pgg-78335960e8909d` [heatmap for timeseries matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/heatmap-for-timeseries-matplotlib.ipynb) · TUTORIAL · 预览 1 · 热力矩阵
- `pgg-3853d7845d2655` [hexbin map from geojson python](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/hexbin-map-from-geojson-python.ipynb) · TUTORIAL · 预览 0 · 六边形密度图 / 地理与分区地图
- `pgg-cb52cac11b5848` [how to add plot inside plot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/how-to-add-plot-inside-plot.ipynb) · TUTORIAL · 预览 0 · 待核对原图
- `pgg-d8c833b67b3537` [how to create and custom arrows matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/how-to-create-and-custom-arrows-matplotlib.ipynb) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `pgg-a7a092210460c9` [how to custom title matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/how-to-custom-title-matplotlib.ipynb) · TUTORIAL · 预览 0 · 标注、图例与排版示例
- `pgg-732c79445ec7ed` [how to remove axis in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/how-to-remove-axis-in-matplotlib.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-cddb577f37d9c3` [how to use rectangles in matplotlib legends](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/how-to-use-rectangles-in-matplotlib-legends.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-0a517643b2a2cc` [introduction to pypalettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/introduction-to-pypalettes.ipynb) · TUTORIAL · 预览 0 · 待核对原图
- `pgg-f556181e0e8536` [line chart dual y axis with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/line-chart-dual-y-axis-with-matplotlib.ipynb) · TUTORIAL · 预览 3 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-6a8709080de934` [manhattan plot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/manhattan-plot-with-matplotlib.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-9f25580a42fb55` [map read geojson with python geopandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/map-read-geojson-with-python-geopandas.ipynb) · TUTORIAL · 预览 1 · 地理与分区地图
- `pgg-842b88fdba4bd6` [parallel coordinate plot plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/parallel-coordinate-plot-plotly.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-11ae841b31c3f9` [pie plot matplotlib basic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/pie-plot-matplotlib-basic.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-5d0848e1067f69` [raincloud plot with matplotlib and ptitprince](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/raincloud-plot-with-matplotlib-and-ptitprince.ipynb) · TUTORIAL · 预览 1 · 雨云图
- `pgg-2a44feae575fcd` [ridgeline graph plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/ridgeline-graph-plotly.ipynb) · TUTORIAL · 预览 1 · 山脊图
- `pgg-456d8d4f16696d` [ridgeline graph seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/ridgeline-graph-seaborn.ipynb) · TUTORIAL · 预览 1 · 山脊图
- `pgg-328be48d38bfff` [sankey diagram with python and plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/sankey-diagram-with-python-and-plotly.ipynb) · TUTORIAL · 预览 1 · 桑基与流向图
- `pgg-fb031d39857559` [scatterplot and log scale in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/scatterplot-and-log-scale-in-matplotlib.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-ef43174e77fcfd` [scatterplot with regression fit in matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/scatterplot-with-regression-fit-in-matplotlib.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-11cda721cdf09f` [seaborn title customization](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/seaborn-title-customization.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例
- `pgg-d029bd91c8906e` [stacked and percent stacked barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/stacked-and-percent-stacked-barplot.ipynb) · TUTORIAL · 预览 0 · 分组柱状图
- `pgg-57778f9f373f24` [streamchart basic matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/streamchart-basic-matplotlib.ipynb) · TUTORIAL · 预览 4 · 河流图
- `pgg-e74606beab6ba1` [web animated line chart with annotation](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-animated-line-chart-with-annotation.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势 / 标注、图例与排版示例 / 动态图
- `pgg-639f82221e1d14` [web animated line chart with text](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-animated-line-chart-with-text.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势 / 动态图
- `pgg-8f1be4cb0b808c` [web area chart with different colors for positive and negative values](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-area-chart-with-different-colors-for-positive-and-negative-values.ipynb) · TUTORIAL · 预览 1 · 面积与流带 / 配色与视觉样式
- `pgg-08686824eb6a41` [web barplot with annotations and arrows](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-barplot-with-annotations-and-arrows.ipynb) · TUTORIAL · 预览 0 · 标注、图例与排版示例 / 分组柱状图
- `pgg-01bcd33117fe3e` [web bubble map with arrows](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-bubble-map-with-arrows.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 气泡图 / 地理与分区地图
- `pgg-6d34199367c8a6` [web bubble plot with annotations and custom features](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-bubble-plot-with-annotations-and-custom-features.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 气泡图
- `pgg-72206a9edf8853` [web choropleth map with barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-choropleth-map-with-barplot.ipynb) · TUTORIAL · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-75af96b8354a46` [web choropleth map with histogram](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-choropleth-map-with-histogram.ipynb) · TUTORIAL · 预览 1 · 直方图 / 地理与分区地图
- `pgg-f533821fa283af` [web circular barplot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-circular-barplot-with-matplotlib.ipynb) · TUTORIAL · 预览 0 · 分组柱状图
- `pgg-2623ed2c9468e6` [web circular lollipop plot with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-circular-lollipop-plot-with-matplotlib.ipynb) · TUTORIAL · 预览 0 · 棒棒糖图
- `pgg-7ec7642d7d5f5b` [web combine choropleth map with barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-combine-choropleth-map-with-barplot.ipynb) · TUTORIAL · 预览 1 · 分组柱状图 / 地理与分区地图
- `pgg-9e3f33b6f531d3` [web dumbell chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-dumbell-chart.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-04175d526abbef` [web ggbetweenstats with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-ggbetweenstats-with-matplotlib.ipynb) · TUTORIAL · 预览 0 · 待核对原图
- `pgg-fca80ac6aad489` [web heatmap and radial barchart plastics](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-heatmap-and-radial-barchart-plastics.ipynb) · TUTORIAL · 预览 1 · 热力矩阵 / 极坐标与径向图
- `pgg-2537781e6e4f5d` [web heatmap comparison](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-heatmap-comparison.ipynb) · TUTORIAL · 预览 0 · 热力矩阵
- `pgg-02bdffd5f212c5` [web highlighted lineplot with faceting](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-highlighted-lineplot-with-faceting.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-40a6b154499415` [web histogram with annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-histogram-with-annotations.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 直方图
- `pgg-32645fbc79882a` [web horizontal barplot with labels the economist](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-horizontal-barplot-with-labels-the-economist.ipynb) · TUTORIAL · 预览 1 · 分组柱状图 / 标注、图例与排版示例
- `pgg-34d9cff28ebd6a` [web lemurs parallel chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lemurs-parallel-chart.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-4f168b97ab7aea` [web line chart small multiple](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-line-chart-small-multiple.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 折线与训练趋势
- `pgg-1e946712ca815d` [web line chart with labels at line end](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-line-chart-with-labels-at-line-end.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-94fe55de595444` [web lineplots and area chart the economist](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lineplots-and-area-chart-the-economist.ipynb) · TUTORIAL · 预览 1 · 面积与流带
- `pgg-abca447777c202` [web lollipop plot with python mario kart 64 world records](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lollipop-plot-with-python-mario-kart-64-world-records.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图
- `pgg-1ff2d9f6b3f499` [web lollipop plot with python the office](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lollipop-plot-with-python-the-office.ipynb) · TUTORIAL · 预览 0 · 棒棒糖图
- `pgg-19e3ae1578ea6c` [web lollipop with background image](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lollipop-with-background-image.ipynb) · TUTORIAL · 预览 1 · 棒棒糖图
- `pgg-97451f34bf537e` [web lollipop with colormap and arrow](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-lollipop-with-colormap-and-arrow.ipynb) · TUTORIAL · 预览 1 · 配色与视觉样式 / 棒棒糖图 / 标注、图例与排版示例
- `pgg-c038553eb2e05a` [web map europe with color by country](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-map-europe-with-color-by-country.ipynb) · TUTORIAL · 预览 1 · 配色与视觉样式 / 地理与分区地图
- `pgg-523940db95f54d` [web map usa with scatter plot on top](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-map-usa-with-scatter-plot-on-top.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系 / 地理与分区地图
- `pgg-b03485b5fdd425` [web map with custom legend](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-map-with-custom-legend.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 地理与分区地图
- `pgg-c047a9ac8ebd81` [web minimalist black and white line chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-minimalist-black-and-white-line-chart.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-fbc6a00acabda2` [web multiple lines and panels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-multiple-lines-and-panels.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势
- `pgg-e4ae67f92dc9a8` [web multiple maps](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-multiple-maps.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-d73a7fe94a6918` [web ordered mirror barplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-ordered-mirror-barplot.ipynb) · TUTORIAL · 预览 1 · 分组柱状图
- `pgg-7bb4f74b209475` [web overlapped area chart with zoom outsets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-overlapped-area-chart-with-zoom-outsets.ipynb) · TUTORIAL · 预览 1 · 面积与流带
- `pgg-f63ab309143268` [web polar chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-polar-chart.ipynb) · TUTORIAL · 预览 1 · 极坐标与径向图
- `pgg-f0035d389537c5` [web polygon map to compare distances](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-polygon-map-to-compare-distances.ipynb) · TUTORIAL · 预览 1 · 地理与分区地图
- `pgg-780ca9da1b1269` [web population pyramid](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-population-pyramid.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-c2b53ec4089e5b` [web radar chart with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-radar-chart-with-matplotlib.ipynb) · TUTORIAL · 预览 0 · 雷达图
- `pgg-611998b6df3477` [web ridgeline by text](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-ridgeline-by-text.ipynb) · TUTORIAL · 预览 1 · 山脊图
- `pgg-12bc2a27fa58b5` [web scatter with customized annotations](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-scatter-with-customized-annotations.ipynb) · TUTORIAL · 预览 1 · 标注、图例与排版示例 / 散点与拟合关系
- `pgg-057f9d28dd3a70` [web scatterplot astronaut](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-scatterplot-astronaut.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-57f8966e63d702` [web scatterplot text annotation and regression matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-scatterplot-text-annotation-and-regression-matplotlib.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系 / 标注、图例与排版示例
- `pgg-c566af305c7cef` [web scatterplot with categorical zoom facets](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-scatterplot-with-categorical-zoom-facets.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-e715671c9b0809` [web scatterplot with images in circles](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-scatterplot-with-images-in-circles.ipynb) · TUTORIAL · 预览 1 · 散点与拟合关系
- `pgg-ece2475c216c66` [web slope chart matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-slope-chart-matplotlib.ipynb) · TUTORIAL · 预览 1 · 斜率图
- `pgg-90ee863497a29c` [web small multiple with highlights](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-small-multiple-with-highlights.ipynb) · TUTORIAL · 预览 1 · 多面板组合
- `pgg-9339154186ff42` [web stacked area charts on a map](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-stacked-area-charts-on-a-map.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 面积与流带 / 地理与分区地图
- `pgg-03ff96872249c0` [web stacked area with inflexion arrows](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-stacked-area-with-inflexion-arrows.ipynb) · TUTORIAL · 预览 1 · 堆叠图 / 标注、图例与排版示例 / 面积与流带
- `pgg-d25cdf3966661b` [web stacked charts](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-stacked-charts.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-19c8bad8ddf9a7` [web stacked line chart with labels](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-stacked-line-chart-with-labels.ipynb) · TUTORIAL · 预览 1 · 折线与训练趋势 / 标注、图例与排版示例
- `pgg-b58a48d1d5e63c` [web streamchart with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-streamchart-with-matplotlib.ipynb) · TUTORIAL · 预览 1 · 河流图
- `pgg-48e2eecabd9702` [web text repel with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-text-repel-with-matplotlib.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-d970deb82a12bf` [web time series and facetting with matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-time-series-and-facetting-with-matplotlib.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势
- `pgg-65b9af5e094100` [web tornado chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-tornado-chart.ipynb) · TUTORIAL · 预览 1 · 发散条形图
- `pgg-0a41d0a1045e02` [web two maps with different granulaties](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-two-maps-with-different-granulaties.ipynb) · TUTORIAL · 预览 1 · 待核对原图
- `pgg-16ce96ee4f6c97` [web waffle chart as share](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-waffle-chart-as-share.ipynb) · TUTORIAL · 预览 1 · 华夫图
- `pgg-08ad551c079991` [web waffle chart for time series](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-waffle-chart-for-time-series.ipynb) · TUTORIAL · 预览 0 · 折线与训练趋势 / 华夫图
- `pgg-78fb2e8926eb5d` [web waffle chart with groups evolution](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-waffle-chart-with-groups-evolution.ipynb) · TUTORIAL · 预览 1 · 华夫图
- `pgg-a14cede79a6c64` [web waffle with small multiples](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/web-waffle-with-small-multiples.ipynb) · TUTORIAL · 预览 1 · 多面板组合 / 华夫图
- `pgg-2b2690eacba4bb` [Matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/Matplotlib.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-f15392bf7a7c1d` [MatplotlibSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/MatplotlibSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-227daeb717b442` [Pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/Pandas.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0c4a1ff9952052` [PandasSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/PandasSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-09872d9a36c87b` [PandasSmallClean](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/PandasSmallClean.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-cfb9a0b823dae2` [Plotly](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/Plotly.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c9d11bd5f29573` [PlotlySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/PlotlySmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1da82932fd3098` [Seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/Seaborn.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-494f3edc671d79` [SeabornSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/SeabornSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-74d97169c4481a` [handout beginner](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/handout-beginner.webp) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0a45ba60fc7887` [handout intermediate](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/handout-intermediate.webp) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6d9f89184dada7` [handout tips](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/handout-tips.webp) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-4d619d09c21faf` [matplotlib journey overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/matplotlib-journey-overview.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6ca861ddec816c` [plotnine small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/plotnine-small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-b730afaa07b5d8` [plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/plotnine.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7d80acf256473d` [poster small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/poster_small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-9865a088e0856b` [poster zoom fadded](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/poster_zoom_fadded.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-69d87b338fb025` [story fading](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/img/story_fading.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-282757ee2f5988` [dataviz hiking](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/dataviz_hiking.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-05b80f7cf8c572` [linkedin logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/linkedin-logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-bae9ea388360aa` [mario kart 64 world records](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/mario-kart-64-world-records.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0dced213a42579` [quick anim](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/quick-anim.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-4e74b318cad5e8` [the office](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/the-office.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-04bc1b3cfb9339` [twitter logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/twitter-logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-23d9cd9a4d3159` [uncannyxmen](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/uncannyxmen.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3305227efa291c` [wave](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/src/notebooks/wave.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-42938320782336` [dataviz inspiration overview low opacity](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/asset/dataviz-inspiration-overview-low-opacity.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-9f0a08b0086c5a` [dataviz inspiration overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/asset/dataviz-inspiration-overview.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e369571355119e` [palette finder overview](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/asset/palette-finder-overview.png) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `pgg-a53de0e739a6e0` [pypalettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/asset/pypalettes.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1062e7bc661b8c` [365 data science](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/banner/365_data_science.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7774cb3a763ccc` [data vis ad](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/banner/data-vis-ad.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-10b11bff7826e7` [datacamp](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/banner/datacamp.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-743a598f53b7f8` [stackabuse](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/banner/stackabuse.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1cbdbb7440d703` [godfather for chart](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/data/godfather-for-chart.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-266638023ae61b` [Amanza](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Amanza.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-dfa4860d983cbb` [Brett](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Brett.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a6aacbc818e7b6` [Chelsea](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Chelsea.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2245efae6f3170` [Chrishell](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Chrishell.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-56120dc1db39dd` [Christine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Christine.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3d0f0506421141` [Davina](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Davina.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-957adccebcdae4` [Emma](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Emma.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-fb67716670b1d5` [Heather](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Heather.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-fab985f17ad561` [Jason](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Jason.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-721ff75114e16e` [Mary](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Mary.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-00757879eb2392` [Maya](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Maya.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-43dd75a855fa77` [Vanessa](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/graph_assets/Vanessa.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-88543ca2c63cf6` [D3 full medium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/D3_full_medium.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-51bb2bfbee9354` [D3 single small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/D3_single_small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-b4323c56c2f17e` [Home single big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Home_single_big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e22adc3f103980` [Logo PGG full 1](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Logo_PGG_full-1.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ff34eb8d15e990` [Logo PGG full 2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Logo_PGG_full-2.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-bc36038576205d` [Logo PGG full 3](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Logo_PGG_full-3.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-46090b8ad693c3` [Logo PGG full](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Logo_PGG_full.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7385f6de18d58e` [Logo PGG light 70x70](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Logo_PGG_light-70x70.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a44a4a8fafd6cb` [bokeh](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/bokeh.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-160dbf28a172a9` [bumplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/bumplot.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c08e9de123f79d` [cartopy](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/cartopy.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2d6784ff788ee4` [dayplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/dayplot.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c7a2160f9fd5b3` [drawarrow](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/drawarrow.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-70bbac547dba57` [flexitext](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/flexitext.png) · SUPPORT_ASSET · 预览 1 · 标注、图例与排版示例
- `pgg-dc094b1e3e6ef4` [folium](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/folium.png) · SUPPORT_ASSET · 预览 1 · 变形统计地图
- `pgg-b2269b61df8eac` [geopandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/geopandas.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-ecc7420d057396` [geoplot](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/geoplot.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1b3b7fbe7f3a8e` [great tables](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/great_tables.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `pgg-4f82a98829821f` [highlight text](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/highlight_text.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2051331f98c4cd` [matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/matplotlib.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a042fb10171744` [matplotlibLogoHighRes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/matplotlibLogoHighRes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7d001c22e31e6b` [morethemes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/morethemes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-04108b6ccececd` [networkx](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/networkx.png) · SUPPORT_ASSET · 预览 1 · 关系网络
- `pgg-3a0892e6af2ca3` [plotlyLogoHighRes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/plotlyLogoHighRes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e5aa6bfb35ffc9` [plotnineLogoHighRes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/plotnineLogoHighRes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-23d44c87373c0e` [plottable](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/plottable.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `pgg-0c87d8bcd6a372` [pyfonts](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/pyfonts.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-943671e11db834` [pypalettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/pypalettes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2f505ab66a3c97` [pywaffle](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/pywaffle.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3d25c28b9da20c` [seabornLogoHighRes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/seabornLogoHighRes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-32f2757af46587` [vega altair](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/vega-altair.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-56bfa03d7dba10` [wordcloud](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/logo/Other/wordcloud.png) · SUPPORT_ASSET · 预览 1 · 词云
- `pgg-bf9e5d01f69b5e` [overview PGG](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/overview_PGG.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d8f67a76a4b564` [overview PGG2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/overview_PGG2.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-936df117d1099c` [2dDensity150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/2dDensity150.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-a02574a2d031c0` [2dDensityBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/2dDensityBig.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-ed1b03e0ab9451` [2dDensitySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/2dDensitySmall.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-1ae5c4a0817c49` [3d150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/3d150.png) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `pgg-d080a971083730` [3dBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/3dBig.png) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `pgg-cccadad5eb3760` [3dRoundBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/3dRoundBig.png) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `pgg-ae5ba87c76a3ff` [3dRoundSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/3dRoundSmall.png) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `pgg-39b6c8603e0cbb` [3dSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/3dSmall.png) · SUPPORT_ASSET · 预览 1 · 三维曲面与网格
- `pgg-808789cbcaaf17` [AnimBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/AnimBig.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e497b5d94e8369` [AnimSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/AnimSmall.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-73bf7a3fd291c9` [Arc150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Arc150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1598781c40649a` [ArcBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ArcBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-65c0a6330104ba` [ArcSmal](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ArcSmal.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-22964148b18808` [Area150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Area150.png) · SUPPORT_ASSET · 预览 1 · 面积与流带
- `pgg-6f794652993305` [AreaBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/AreaBig.png) · SUPPORT_ASSET · 预览 1 · 面积与流带
- `pgg-4023741d344cbf` [AreaSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/AreaSmall.png) · SUPPORT_ASSET · 预览 1 · 面积与流带
- `pgg-cf7d66e4b4a46c` [Bad150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Bad150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-cf402985e5aadd` [BadBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BadBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-054ce4d8daad6c` [BadSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BadSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c1986f11c0d445` [Bar150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Bar150.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-9149402b3b29f9` [BarBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BarBig.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-98b0a870842fdc` [BarSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BarSmall.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-8ad8509133a07b` [Baser150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Baser150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6fe38d3c3002da` [BaserBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BaserBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-41067ba16921e8` [BaserSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BaserSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-718c642313b6ce` [Basic150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Basic150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-62e5d9cc4fcaed` [Basic150 black](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Basic150_black.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1a43c146fac401` [BasicSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BasicSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2f66a45daf3fab` [Beeswarm2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Beeswarm2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-beafdbffd1485f` [Beeswarm2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Beeswarm2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-278141a9c87448` [BeeswarmBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BeeswarmBig.png) · SUPPORT_ASSET · 预览 1 · 样本散点与蜂群
- `pgg-68eef671ff57f2` [BeeswarmSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BeeswarmSmall.png) · SUPPORT_ASSET · 预览 1 · 样本散点与蜂群
- `pgg-4042c0c11136de` [Box1150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box1150.png) · SUPPORT_ASSET · 预览 1 · 箱线图
- `pgg-c2beec2635f929` [Box1Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box1Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c1c052e32fc35e` [Box1Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box1Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e073089672a3d7` [Box2150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box2150.png) · SUPPORT_ASSET · 预览 1 · 箱线图
- `pgg-27450d08ee12d1` [Box2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7b73fbabce9f6e` [Box2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Box2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-dfe9cbcaf85bce` [BubbleMap150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubbleMap150.png) · SUPPORT_ASSET · 预览 1 · 气泡图 / 地理与分区地图
- `pgg-0011973fff9234` [BubbleMapBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubbleMapBig.png) · SUPPORT_ASSET · 预览 1 · 气泡图 / 地理与分区地图
- `pgg-74ff9109040e65` [BubbleMapSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubbleMapSmall.png) · SUPPORT_ASSET · 预览 1 · 气泡图 / 地理与分区地图
- `pgg-0fe2c5b87c66e0` [BubblePlot150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubblePlot150.png) · SUPPORT_ASSET · 预览 1 · 气泡图
- `pgg-5e8bd54599f4d0` [BubblePlotBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubblePlotBig.png) · SUPPORT_ASSET · 预览 1 · 气泡图
- `pgg-16bfff3c5b72a0` [BubblePlotSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BubblePlotSmall.png) · SUPPORT_ASSET · 预览 1 · 气泡图
- `pgg-04aaf600e941e2` [Bundle150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Bundle150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-df287e3953e840` [BundleBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BundleBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e92dc03998bf9d` [BundleSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/BundleSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-71435cac38d19b` [CandleStick2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CandleStick2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a699c264f22a3f` [CandleStick2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CandleStick2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-49e7d7c403877f` [Cartogram150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Cartogram150.png) · SUPPORT_ASSET · 预览 1 · 变形统计地图
- `pgg-e1225eb405fbe9` [CartogramSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CartogramSmall.png) · SUPPORT_ASSET · 预览 1 · 变形统计地图
- `pgg-6965ea6d588d3c` [Cheat150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Cheat150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-8599224b6f0bc7` [CheatBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CheatBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-f1ed514ad0581e` [CheatSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CheatSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e59f72bfeef485` [Chord150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Chord150.png) · SUPPORT_ASSET · 预览 1 · 弦图
- `pgg-7c2db2c264baa5` [ChordBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ChordBig.png) · SUPPORT_ASSET · 预览 1 · 弦图
- `pgg-318b6f0791e7cc` [ChordSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ChordSmall.png) · SUPPORT_ASSET · 预览 1 · 弦图
- `pgg-cc699aba3c0f9f` [Choropleth150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Choropleth150.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-fd57c749b5e5ca` [ChoroplethBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ChoroplethBig.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-30732e73e40d6c` [ChoroplethSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ChoroplethSmall.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-b05b4ad6d6687a` [Circular150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Circular150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-18c1c35ef9c387` [CircularBarplot150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularBarplot150.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-dcfa136b583bef` [CircularBarplotBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularBarplotBig.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-312965be9bdb60` [CircularBarplotSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularBarplotSmall.png) · SUPPORT_ASSET · 预览 1 · 分组柱状图
- `pgg-eb619638ad8264` [CircularBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-9df5633a88c0ba` [CircularPacking150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularPacking150.png) · SUPPORT_ASSET · 预览 1 · 圆形打包图
- `pgg-7dfdec5680b0a9` [CircularPackingBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularPackingBig.png) · SUPPORT_ASSET · 预览 1 · 圆形打包图
- `pgg-523f3f625f7bd5` [CircularPackingSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularPackingSmall.png) · SUPPORT_ASSET · 预览 1 · 圆形打包图
- `pgg-8267a51a192270` [CircularSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CircularSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-b3821635376ee7` [Colours150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Colours150.png) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `pgg-e72c922f5575c1` [ColoursBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ColoursBig.png) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `pgg-d0abf1f0063c00` [ColoursSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ColoursSmall.png) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `pgg-60fa6cbe5db8e5` [Confidence150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Confidence150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-13a98d26051402` [ConfidenceBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ConfidenceBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-cc25b27436d522` [ConfidenceSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ConfidenceSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-da831f787eb076` [ConnectedMap150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ConnectedMap150.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-9990ced2c3c652` [ConnectedMapBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ConnectedMapBig.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-b9a559af30dbf5` [ConnectedMapSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ConnectedMapSmall.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-cbe75ead6e7fa4` [Correlogram150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Correlogram150.png) · SUPPORT_ASSET · 预览 1 · 成对关系矩阵
- `pgg-6c86e0fc7ee0b4` [CorrelogramBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CorrelogramBig.png) · SUPPORT_ASSET · 预览 1 · 成对关系矩阵
- `pgg-24b6a48ff9ccee` [CorrelogramSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/CorrelogramSmall.png) · SUPPORT_ASSET · 预览 1 · 成对关系矩阵
- `pgg-686584068a0acb` [DataArt1150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt1150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3fab01e18e9490` [DataArt1Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt1Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-114d2edcb341d7` [DataArt1Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt1Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-efe0679acfd62d` [DataArt2150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt2150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e44d5f47aca574` [DataArt2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c124598aa8289a` [DataArt2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DataArt2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6572a501a28af8` [Dendrogram150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Dendrogram150.png) · SUPPORT_ASSET · 预览 1 · 层次树与树状聚类
- `pgg-879ee8a52ed099` [DendrogramBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DendrogramBig.png) · SUPPORT_ASSET · 预览 1 · 层次树与树状聚类
- `pgg-4a1c5f83683fce` [DendrogramSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DendrogramSmall.png) · SUPPORT_ASSET · 预览 1 · 层次树与树状聚类
- `pgg-9560150661d54a` [Density150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Density150.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-0dd816b92ea98a` [DensityBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DensityBig.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-6c766c541df83d` [DensitySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DensitySmall.png) · SUPPORT_ASSET · 预览 1 · 密度曲线
- `pgg-26f51fea942439` [Doughnut150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Doughnut150.png) · SUPPORT_ASSET · 预览 1 · 环形与嵌套环形图
- `pgg-073c0b5101ba45` [DoughnutBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DoughnutBig.png) · SUPPORT_ASSET · 预览 1 · 环形与嵌套环形图
- `pgg-8725023ab6a859` [DougnutSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/DougnutSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0cd13bdb6f4946` [Ggplot2150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Ggplot2150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c126cc3fb63a3e` [Ggplot2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Ggplot2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-acb1428c2987ca` [Ggplot2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Ggplot2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e7e6d8fb8a5a73` [GroupedGreen150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedGreen150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-b0a6f7216715b7` [GroupedGreenBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedGreenBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-14742fff8bd89b` [GroupedGreenSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedGreenSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-4b04f65cac38d8` [GroupedRed150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedRed150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-31ad08318a352a` [GroupedRedBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedRedBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d3bdbf29ad7c4d` [GroupedRedSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/GroupedRedSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d1bc20da9fdcad` [Heatmap150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Heatmap150.png) · SUPPORT_ASSET · 预览 1 · 热力矩阵
- `pgg-1251636702a753` [HeatmapBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HeatmapBig.png) · SUPPORT_ASSET · 预览 1 · 热力矩阵
- `pgg-d1ddc963406024` [HeatmapSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HeatmapSmall.png) · SUPPORT_ASSET · 预览 1 · 热力矩阵
- `pgg-019bba7fa7f739` [Histogram150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Histogram150.png) · SUPPORT_ASSET · 预览 1 · 直方图
- `pgg-3e47b40d527422` [HistogramBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HistogramBig.png) · SUPPORT_ASSET · 预览 1 · 直方图
- `pgg-81566f04886c9c` [HistogramSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HistogramSmall.png) · SUPPORT_ASSET · 预览 1 · 直方图
- `pgg-60ddb02fa671cf` [Hive150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Hive150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-02884f683a01bd` [HiveBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HiveBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-cf6500efb12add` [HiveSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/HiveSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a2c8d84207056b` [Interactive150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Interactive150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-8645d6ad5df82a` [InteractiveBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/InteractiveBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ca4d1131a502bb` [InteractiveSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/InteractiveSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-bbccf6866ae9c1` [Joint150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Joint150.png) · SUPPORT_ASSET · 预览 1 · 联合与边缘分布
- `pgg-2c78e207092840` [JointBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/JointBig.png) · SUPPORT_ASSET · 预览 1 · 联合与边缘分布
- `pgg-0fecfa72d8b2e7` [JointSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/JointSmall.png) · SUPPORT_ASSET · 预览 1 · 联合与边缘分布
- `pgg-0e1b2dd201e688` [Joyplot150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Joyplot150.png) · SUPPORT_ASSET · 预览 1 · 山脊图
- `pgg-deb06a8021962a` [JoyplotBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/JoyplotBig.png) · SUPPORT_ASSET · 预览 1 · 山脊图
- `pgg-b4eea6dffbba2f` [JoyplotSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/JoyplotSmall.png) · SUPPORT_ASSET · 预览 1 · 山脊图
- `pgg-4cf8c599bbb18b` [Line150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Line150.png) · SUPPORT_ASSET · 预览 1 · 折线与训练趋势
- `pgg-4f9aeae1b66759` [LineBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/LineBig.png) · SUPPORT_ASSET · 预览 1 · 折线与训练趋势
- `pgg-ce96ec454319e1` [LineSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/LineSmall.png) · SUPPORT_ASSET · 预览 1 · 折线与训练趋势
- `pgg-ca4886cd846f76` [Lollipop150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Lollipop150.png) · SUPPORT_ASSET · 预览 1 · 棒棒糖图
- `pgg-b9db3eb2c88ed3` [LollipopBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/LollipopBig.png) · SUPPORT_ASSET · 预览 1 · 棒棒糖图
- `pgg-cb89fd23311c82` [LollipopSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/LollipopSmall.png) · SUPPORT_ASSET · 预览 1 · 棒棒糖图
- `pgg-eb4464af14f5dd` [Map150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Map150.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-d460a9f043d4e2` [MapBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MapBig.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-f1cb6a69751c4f` [MapHexbin150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MapHexbin150.png) · SUPPORT_ASSET · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-39199860b32dbb` [MapHexbinBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MapHexbinBig.png) · SUPPORT_ASSET · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-3754c014f1d1b1` [MapHexbinSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MapHexbinSmall.png) · SUPPORT_ASSET · 预览 1 · 六边形密度图 / 地理与分区地图
- `pgg-36656684c66ebf` [MapSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MapSmall.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `pgg-602efbba1bc5ce` [Matplotlib150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Matplotlib150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0148d3506552af` [MatplotlibBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MatplotlibBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-264482da9d69d5` [MatplotlibSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MatplotlibSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-97b85762035785` [Multiple150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Multiple150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ddbe783ac6a1b0` [MultipleBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MultipleBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-53ea7beb087e31` [MultipleSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/MultipleSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-37f80a4ba94be0` [Network150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Network150.png) · SUPPORT_ASSET · 预览 1 · 关系网络
- `pgg-f92d6cce75c5d3` [NetworkBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/NetworkBig.png) · SUPPORT_ASSET · 预览 1 · 关系网络
- `pgg-cd75f10aa385cc` [NetworkSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/NetworkSmall.png) · SUPPORT_ASSET · 预览 1 · 关系网络
- `pgg-8310793fa0d6d4` [NewMap3Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/NewMap3Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-54e62ddb0d7ca8` [NewMap3Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/NewMap3Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ce538e493ea9c0` [PCAbig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PCAbig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-bdccb963d6135d` [PCAsmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PCAsmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3ac7479b56df15` [Pandas150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Pandas150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-80f6fa9bd7faa9` [PandasBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PandasBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c144f7190c2c86` [PandasSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PandasSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-568b768f3a909e` [Parallel1150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel1150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0648b32ff1e349` [Parallel1Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel1Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0e79dd4e4027c6` [Parallel1Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel1Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d5a468abf5068a` [Parallel2150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel2150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-59ba71669213c1` [Parallel2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-0a262bd05940a4` [Parallel2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-8da75119524e59` [Parallel3150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel3150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-be188d67f53a62` [Parallel3Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel3Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-e27629e85efd05` [Parallel3Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Parallel3Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a0a4b0cef1a865` [Pie150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Pie150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-1518809b22b401` [PieBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PieBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-bed7e56501c1f4` [PieSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PieSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-896d544239784f` [Plotly150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Plotly150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-077a6cf3d89157` [PlotlyBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PlotlyBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d65d1b3e055989` [PlotlySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/PlotlySmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-06bf6436697376` [Presentation2](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Presentation2.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-edc9923044f8a2` [Sankey150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Sankey150.png) · SUPPORT_ASSET · 预览 1 · 桑基与流向图
- `pgg-ced796f1f562a8` [SankeyBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SankeyBig.png) · SUPPORT_ASSET · 预览 1 · 桑基与流向图
- `pgg-76f5fb94d32728` [SankeySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SankeySmall.png) · SUPPORT_ASSET · 预览 1 · 桑基与流向图
- `pgg-ee6fb641dc764e` [ScatterConnected150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterConnected150.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-e227618d5190c3` [ScatterConnectedBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterConnectedBig.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-d62afe55df3612` [ScatterConnectedSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterConnectedSmall.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-57389ff46b0a1d` [ScatterGroup150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterGroup150.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-a75529f4641ed2` [ScatterGroupBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterGroupBig.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-22d23ec0aa29ec` [ScatterGroupSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterGroupSmall.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-4fdec6f11fb08c` [ScatterPlot150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterPlot150.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-bef75a5f20496a` [ScatterPlotBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterPlotBig.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-86e6a2c12bf2fe` [ScatterPlotSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ScatterPlotSmall.png) · SUPPORT_ASSET · 预览 1 · 散点与拟合关系
- `pgg-f0852bb2acf691` [SeaBorn150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SeaBorn150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-cba82044fe1170` [SeaBornBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SeaBornBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-d7bab4cc349fb8` [SeabornSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SeabornSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-39732c9185833b` [Shapehelper150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Shapehelper150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ed2d1f7b4b652b` [Shapehelper150 black](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Shapehelper150_black.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2d72217fc84bb5` [Shiny150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Shiny150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6b6782a2c7ecef` [ShinyBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ShinyBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-42b4714228176d` [ShinySmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ShinySmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-4837924cc15e7e` [Spider150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Spider150.png) · SUPPORT_ASSET · 预览 1 · 雷达图
- `pgg-69295ac6f5a367` [SpiderBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SpiderBig.png) · SUPPORT_ASSET · 预览 1 · 雷达图
- `pgg-b36f6e657934c4` [SpiderSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SpiderSmall.png) · SUPPORT_ASSET · 预览 1 · 雷达图
- `pgg-ab0fa91a350ce9` [Stacked150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Stacked150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-afe58119b55709` [StackedArea150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StackedArea150.png) · SUPPORT_ASSET · 预览 1 · 堆叠图 / 面积与流带
- `pgg-0f004167669585` [StackedAreaBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StackedAreaBig.png) · SUPPORT_ASSET · 预览 1 · 堆叠图 / 面积与流带
- `pgg-90616e12442b23` [StackedAreaSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StackedAreaSmall.png) · SUPPORT_ASSET · 预览 1 · 堆叠图 / 面积与流带
- `pgg-ca92b3e08f3b7d` [StackedBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StackedBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-32e3eb66614d45` [StackedSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StackedSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-f32f3ce5d9069e` [Stats150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Stats150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-363ae82ad3175e` [StatsBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StatsBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3619ed9b9500a3` [StatsSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StatsSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-c33a6e8e387825` [Stream150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Stream150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-6e7a22c13df0d5` [StreamBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StreamBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-958d4661e9b105` [StreamSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/StreamSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-aad93678ae1e2b` [Sunburst150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Sunburst150.png) · SUPPORT_ASSET · 预览 1 · 旭日图
- `pgg-729e11603d26b3` [SunburstBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SunburstBig.png) · SUPPORT_ASSET · 预览 1 · 旭日图
- `pgg-50c21f966104a1` [SunburstSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/SunburstSmall.png) · SUPPORT_ASSET · 预览 1 · 旭日图
- `pgg-55591115bec707` [TableBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TableBig.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `pgg-3a98e2303f7b07` [TableSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TableSmall.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `pgg-5dbb9dd84e24c3` [TimeBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TimeBig.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-82023f14c11d00` [TimeSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TimeSmall.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-3fa43dbe57de0d` [Tree150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Tree150.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-5da780a8f38d86` [TreeBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TreeBig.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-33f8fbbd3cdccc` [TreeSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/TreeSmall.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-818b874cc838c0` [Venn150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Venn150.png) · SUPPORT_ASSET · 预览 1 · Venn 与集合交集
- `pgg-9b5f8d81f23111` [VennBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/VennBig.png) · SUPPORT_ASSET · 预览 1 · Venn 与集合交集
- `pgg-78e97932ece8a9` [VennSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/VennSmall.png) · SUPPORT_ASSET · 预览 1 · Venn 与集合交集
- `pgg-4bef7b37011421` [Violin150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Violin150.png) · SUPPORT_ASSET · 预览 1 · 小提琴与分组小提琴
- `pgg-c0a05fa6d2e85a` [ViolinBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ViolinBig.png) · SUPPORT_ASSET · 预览 1 · 小提琴与分组小提琴
- `pgg-bf67157d6e76ca` [ViolinSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/ViolinSmall.png) · SUPPORT_ASSET · 预览 1 · 小提琴与分组小提琴
- `pgg-eb61da702ca2d4` [Waffle2Big](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Waffle2Big.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-44a902264dc428` [Waffle2Small](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Waffle2Small.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-8916add7bbc8d2` [WaffleBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/WaffleBig.png) · SUPPORT_ASSET · 预览 1 · 华夫图
- `pgg-17652d92c82dc4` [WaffleSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/WaffleSmall.png) · SUPPORT_ASSET · 预览 1 · 华夫图
- `pgg-be77a8716bc6d6` [WordCloudSmall](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/WordCloudSmall.png) · SUPPORT_ASSET · 预览 1 · 词云
- `pgg-1a73a5a698b678` [Wordcloud150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/Wordcloud150.png) · SUPPORT_ASSET · 预览 1 · 词云
- `pgg-8349b5804177c7` [WordcloudBig](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/WordcloudBig.png) · SUPPORT_ASSET · 预览 1 · 词云
- `pgg-31fe649f30fecd` [anim150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/anim150.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-58311a1d94669b` [drawarrow](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/drawarrow.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-b84e7dc9a641b4` [matplotlib](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/matplotlib.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ea53272d25911e` [pandas](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/pandas.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-02c5fd4ff861a3` [plotnine](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/plotnine.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-a25836c6439a9d` [pyfonts](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/pyfonts.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-fb985dab347cfc` [pypalettes](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/pypalettes.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-adf846f5bafa6b` [seaborn](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/seaborn.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-427bb6dd072adf` [time150](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/section/time150.gif) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-93c75db59316b0` [365 data science logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/365_data_science_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-190071283f290a` [EARL logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/EARL_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-7b7681e87cbe6b` [HighStat logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/HighStat_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-2e63231cdb0c18` [MangoSolution logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/MangoSolution_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-019a6263fe3c05` [data society logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/data_society_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-40ab2618933bf9` [datacamp logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/datacamp_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-13f8916ba4e191` [datamatic](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/datamatic.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-ddfc22da79d4bb` [dataquest logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/dataquest_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-799deeb0e1abb1` [eoda logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/eoda_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-697d846ff00f41` [jumping river logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/jumping_river_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-5d54e16019ce79` [stack abuse logo](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/stack_abuse_logo.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `pgg-f30af47df8f8ee` [udemy](https://github.com/holtzy/The-Python-Graph-Gallery/blob/64424bccec3d0340a6dcf7763b37a78e468d45c9/static/sponsor/udemy.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
### Great Tables
来源版本：`f870830578dd32ed27624604a8c774c4d2d60f50`。许可：MIT at repository level; third-party illustrations retain their rights。

- `gt-33393e0067ab4c` [datasets](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/datasets.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-bd663cb5e7820d` [gt parts of a table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/gt_parts_of_a_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-bf4e977abcab64` [gt sp500 table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/gt_sp500_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-d49853a89b6e1a` [gt workflow diagram](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/gt_workflow_diagram.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-f7c7990e4d0365` [tables from the web](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/tables_from_the_web.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-ca9c7c2af98c03` [the components of a table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/the_components_of_a_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-cef4806a111b5f` [a simple table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/a_simple_table.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-56709fa39e9740` [composition of a table in GT](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/composition_of_a_table_in_GT.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-37f039c9ade68c` [snippets from manual tablular presentation](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/snippets_from_manual_tablular_presentation.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-ad62c49bf33c46` [GT html latex](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/latex-output-tables/GT_html_latex.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-637b8f9bb3cbff` [GT html typst](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/latex-output-tables/GT_html_typst.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-15859428716b4a` [gtcars latex table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/latex-output-tables/gtcars_latex_table.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-b28726ab3a8531` [gt marimo](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/marimo-and-great-tables/gt_marimo.gif) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-10000886be98ea` [table of your dreams](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/table-of-your-dreams.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-ede05de0cf5236` [table preview](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-styling/table-preview.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-49f3a230e17faf` [example timetable](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/septa-timetables/example-timetable.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-11394938182551` [datasets](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/datasets.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-a032a55f13f0ed` [gt parts of a table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/gt_parts_of_a_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-046d51edc9bf9f` [gt sp500 table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/gt_sp500_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-0eedaab3a52718` [gt workflow diagram](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/gt_workflow_diagram.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-9f1059442cbc3f` [tables from the web](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/tables_from_the_web.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-4edfbf41e190e5` [the components of a table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/the_components_of_a_table.svg) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-4295453e38bc37` [a simple table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/a_simple_table.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-10814173b2be48` [composition of a table in GT](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/composition_of_a_table_in_GT.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-6fb9c25df8d4ce` [snippets from manual tablular presentation](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/snippets_from_manual_tablular_presentation.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-575a172f725f19` [GT html latex](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/latex-output-tables/GT_html_latex.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-1bd22053c1257b` [GT html typst](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/latex-output-tables/GT_html_typst.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-c3a2fecafec9e5` [gtcars latex table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/latex-output-tables/gtcars_latex_table.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-cf3c03d0fe6667` [gt marimo](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/marimo-and-great-tables/gt_marimo.gif) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-7311e32e9abaca` [table of your dreams](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-dot-style/table-of-your-dreams.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-264e2e058615ae` [table preview](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-styling/table-preview.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-bd236ea6849c0f` [example timetable](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/septa-timetables/example-timetable.png) · TABLE_EXAMPLE · 预览 1 · 结果表与分组表
- `gt-a35ccd529259c3` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/bring-your-own-df/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-a1db2f4b0e7551` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/index.qmd) · TABLE_GUIDE · 预览 8 · 结果表与分组表
- `gt-4cdd7a06b3bc62` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-b596ae7760994b` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.12.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-bf795c551ed5e0` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.13.0/index.qmd) · TABLE_GUIDE · 预览 1 · 结果表与分组表
- `gt-ec55dd5f451348` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.15.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-5777013523d096` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.18.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-711862a2148bb2` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.2.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-b791f62cf5b65d` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.3.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-c9af96671d0f64` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.4.0/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-08fbbeccba8d6a` [introduction great tables](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction_great_tables.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-c03aa7c12f2324` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/latex-output-tables/index.qmd) · TABLE_GUIDE · 预览 3 · 结果表与分组表
- `gt-aebbbb5013e14e` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/locbody-mask/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-06b5c92682c21c` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/marimo-and-great-tables/index.qmd) · TABLE_GUIDE · 预览 1 · 结果表与分组表
- `gt-a2e325bbd6f788` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/open-transit-tools/index.qmd) · TABLE_GUIDE · 预览 2 · 结果表与分组表
- `gt-6ea04e4e56b33b` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/plots-in-tables/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-fca56781ef1879` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/pointblank-intro/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-75e9d394af2805` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/index.qmd) · TABLE_GUIDE · 预览 5 · 结果表与分组表
- `gt-3dce968805fb35` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-styling/index.qmd) · TABLE_GUIDE · 预览 1 · 结果表与分组表
- `gt-6ea86e199d8a65` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/pycon-2024-great-tables-are-possible/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-2d732e14680d8c` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/rendering-images/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-ccba25e5f2f112` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/septa-timetables/index.qmd) · TABLE_GUIDE · 预览 4 · 结果表与分组表
- `gt-c1d47a6eba8ab8` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/superbowl-squares/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-1d1e13689fb7e3` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/tables-for-scientific-publishing/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-38c3830adb79c0` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/gt-extras-gini/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-fe9d1931085f96` [index](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/index.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-888edd67ea7868` [00 introduction](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/00-introduction.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-73658867775f5e` [01 datasets](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/01-datasets.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-efa83274069cea` [02 header footer stub](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/02-header-footer-stub.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-3d79edd57c52b3` [03 column labels](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/03-column-labels.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-cb4c962a637bab` [04 merging columns](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/04-merging-columns.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-0be2e4b1af789a` [05 footnotes](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/05-footnotes.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-f63e7ffa4cefed` [06 summary rows](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/06-summary-rows.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-711e9ab07ef95f` [07 formatting values](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/07-formatting-values.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-a58d8ade846881` [08 removing parts](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/08-removing-parts.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-59552f6acff691` [09 more formatting](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/09-more-formatting.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-090af86a235999` [10 substituting values](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/10-substituting-values.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-fb39678ad459ab` [11 text transforms](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/11-text-transforms.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-ceacac7cd4bf1d` [12 styling the table body](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/12-styling-the-table-body.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-970aeb4b39cf69` [13 styling the whole table](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/13-styling-the-whole-table.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-369284e6d226d0` [14 colorizing with data](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/14-colorizing-with-data.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-8a1282e2f14d39` [15 table theme options](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/15-table-theme-options.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-26c0e28398d7b0` [16 premade themes](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/16-premade-themes.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-b0242934c6347d` [17 nanoplots](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/17-nanoplots.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-3662aa11ba54ed` [18 column selection](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/18-column-selection.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-5c93b19c281c48` [19 row selection](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/19-row-selection.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-2c1196c03b83cc` [20 location selection](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/20-location-selection.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-c1c02b84396e51` [21 interactive tables](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/21-interactive-tables.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-0b50cf7fc40814` [22 exporting and saving](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/22-exporting-and-saving.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-0512d1152700a5` [23 extensions](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/23-extensions.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-8653440227bfcb` [24 glossary](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/user_guide/24-glossary.qmd) · TABLE_GUIDE · 预览 0 · 结果表与分组表
- `gt-9e2e472133891c` [GT logo](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/assets/GT_logo.svg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-1ec36c54187c71` [cave grids](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/cave_grids.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-5205b613c011d6` [computer tables](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/computer_tables.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-330b9a590c0443` [nippur cuneiform tablet](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/nippur_cuneiform_tablet.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-384b8983bc57be` [uruk tablet with annotations](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/uruk_tablet_with_annotations.png) · SUPPORT_ASSET · 预览 1 · 标注、图例与排版示例
- `gt-4db7e4b5b58f29` [visicalc](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/design-philosophy/visicalc.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-3e9c0b3c3d3831` [GT locations map](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/introduction-0.13.0/GT-locations-map.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `gt-f63386833f5a7c` [amtrak routes](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/open-transit-tools/amtrak-routes.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-166d434c71870c` [calitp service patterns](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/open-transit-tools/calitp-service-patterns.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-13ecfea299b20c` [discord feedback](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/discord-feedback.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-125159cf22ad11` [discord why pandas](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/discord-why-pandas.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-af57b16151ab41` [linkedin jerry](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/linkedin-jerry.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-77ea927fc07615` [pr jerry](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/polars-dot-style/pr-jerry.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-f5cdc42b9ab0d7` [metrotransit route2](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/septa-timetables/metrotransit-route2.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-9387d37495300a` [mta route bx1](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/septa-timetables/mta-route-bx1.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-00f43cb101267e` [septa routing](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/blog/septa-timetables/septa-routing.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-6dd529dd2309f5` [GT logo](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/assets/GT_logo.svg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-13c5f07181e575` [cave grids](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/cave_grids.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-4ec02b6470dd4e` [computer tables](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/computer_tables.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-574c8338f8abac` [nippur cuneiform tablet](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/nippur_cuneiform_tablet.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-0fcf190dc345cb` [uruk tablet with annotations](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/uruk_tablet_with_annotations.png) · SUPPORT_ASSET · 预览 1 · 标注、图例与排版示例
- `gt-49d9d53dff0d82` [visicalc](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/design-philosophy/visicalc.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-a414ca822b9fc3` [GT locations map](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/introduction-0.13.0/GT-locations-map.png) · SUPPORT_ASSET · 预览 1 · 地理与分区地图
- `gt-db594a7530cbfb` [amtrak routes](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/open-transit-tools/amtrak-routes.jpg) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-4d868b0d28180f` [calitp service patterns](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/open-transit-tools/calitp-service-patterns.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-1f3d266aab1108` [discord feedback](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-dot-style/discord-feedback.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-7045b6ecebb2d9` [discord why pandas](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-dot-style/discord-why-pandas.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-b007aabf9948fb` [linkedin jerry](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-dot-style/linkedin-jerry.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-8518d180764508` [pr jerry](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/polars-dot-style/pr-jerry.jpg) · SUPPORT_ASSET · 预览 1 · 配色与视觉样式
- `gt-40953faac8c2d2` [metrotransit route2](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/septa-timetables/metrotransit-route2.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-40310ffcaa368e` [mta route bx1](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/septa-timetables/mta-route-bx1.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-229466c4ceb90a` [septa routing](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/blog/septa-timetables/septa-routing.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-ade54c0f5714f8` [aeropress](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/aeropress.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-e0cf855539f368` [cezve](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/cezve.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-cdd76345eed19e` [chemex](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/chemex.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-20e5812059c4e2` [cold brew](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/cold-brew.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-dc9d04869d1605` [drip machine](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/drip-machine.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-aebc0641e2c394` [espresso machine](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/espresso-machine.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-350eeff8fc355e` [filter](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/filter.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-700c7417e5e3f3` [french press](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/french-press.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-672d2b231f2d56` [grinder](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/grinder.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-4748198e3bed92` [kettle](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/kettle.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-cb5218ea9595a1` [moka pot](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/moka-pot.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-11789520c8692e` [noun drip machine 6065915](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/noun-drip-machine-6065915.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-b8360760c4d733` [pour over](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/pour-over.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-3d3f4fe242b26a` [scale](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/scale.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-fb1d77657f62b1` [total](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/_data/coffee-table-icons/total.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-665114b4cd34fe` [basketball](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/sports-earnings/basketball.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-223646a62caf1f` [boxing](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/sports-earnings/boxing.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-01fc6015b58a86` [golf](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/sports-earnings/golf.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-e1577996428640` [soccer](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/sports-earnings/soccer.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-c0c7ec6b303137` [tennis](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/docs/examples/sports-earnings/tennis.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-051dcdbea58aeb` [aeropress](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/aeropress.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-ecc7c442ac1e21` [cezve](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/cezve.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-961adb36f39fc2` [chemex](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/chemex.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-9756bb1f4d5521` [cold brew](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/cold-brew.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-92c9a818e00b32` [drip machine](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/drip-machine.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-f15c092d0c5dbf` [espresso machine](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/espresso-machine.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-998500b95e746c` [filter](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/filter.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-a702c65ed219a1` [french press](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/french-press.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-7c2742eddd04d2` [grinder](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/grinder.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-a58232ad6c5b2d` [kettle](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/kettle.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-f725b90aac75f7` [moka pot](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/moka-pot.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-fe7a65d6e14ab4` [noun drip machine 6065915](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/noun-drip-machine-6065915.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-3550c2de5c9f48` [pour over](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/pour-over.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-0bcdd3aa5b38db` [scale](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/scale.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-beed10fd09a5de` [total](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/_data/coffee-table-icons/total.png) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-7e9e2848c2930e` [basketball](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/sports-earnings/basketball.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-3841e9780c295c` [boxing](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/sports-earnings/boxing.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-2e01fc48748aaa` [golf](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/sports-earnings/golf.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-f17bcd72e3f10f` [soccer](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/sports-earnings/soccer.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-030b0af966dee6` [tennis](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/examples/sports-earnings/tennis.png) · SUPPORT_ASSET · 预览 1 · 待核对原图
- `gt-7f5c5ef41d2732` [metro 1](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_1.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-4d7356e012ec70` [metro 10](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_10.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-7498ad1415f27a` [metro 11](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_11.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-ac8fd991ffa74b` [metro 12](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_12.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-265947f47891af` [metro 13](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_13.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-c0adfdbeedceae` [metro 14](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_14.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-164a58701b4581` [metro 2](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_2.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-d90573702203b8` [metro 3](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_3.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-5a8e5de4c88326` [metro 3bis](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_3bis.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-a6e3be1fd94dc6` [metro 4](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_4.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-2b2cec543b06e7` [metro 5](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_5.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-41c4977959cb97` [metro 6](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_6.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-2107cee007881c` [metro 7](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_7.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-b2a6ce5c02bc4d` [metro 7bis](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_7bis.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-d2fe0a6b5de584` [metro 8](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_8.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-01d588c3173ff5` [metro 9](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/metro_9.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-46c1280bfc7307` [rer A](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/rer_A.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-a9b60d638232b0` [rer B](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/rer_B.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-e504a6f779be5c` [rer C](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/rer_C.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-327c65475944c4` [rer D](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/rer_D.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-59d2e202db1a5c` [rer E](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/rer_E.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-1660797d2380e1` [tram T1](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T1.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-1be71d20b61830` [tram T11](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T11.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-a4cefae78df9b4` [tram T13](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T13.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-92217bb30e5b86` [tram T2](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T2.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-6aa7b4f20dc61e` [tram T3a](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T3a.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-bb1c38c9b169d2` [tram T3b](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T3b.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-5f586a835e15ce` [tram T4](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T4.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-15dbc1cc149806` [tram T5](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T5.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-60c6d452f10c29` [tram T6](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T6.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-fa098c06f1fc71` [tram T7](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T7.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-83aeccdf7d4d9e` [tram T8](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T8.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-9c0aa21210f3ff` [tram T9](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/tram_T9.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-0d88569b87c398` [transilien H](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_H.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-7777e44e945823` [transilien J](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_J.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-370c5a0932e181` [transilien K](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_K.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-f551d5782a334b` [transilien L](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_L.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-8b975a0e010b77` [transilien N](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_N.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-8a850e37e1c555` [transilien P](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_P.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-823000eb3346fa` [transilien R](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_R.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
- `gt-47f5471bdbe5e8` [transilien U](https://github.com/posit-dev/great-tables/blob/f870830578dd32ed27624604a8c774c4d2d60f50/great_tables/data/metro_images/transilien_U.svg) · SUPPORT_ASSET · 预览 1 · 结果表与分组表
