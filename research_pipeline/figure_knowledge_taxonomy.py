"""Independent selection knowledge. Families are not a count of upstream examples.

Filename matches are explicitly provisional; a schema fit is not scientific approval.
Upstream cards, images and source code retain their own provenance and licenses.
"""
from __future__ import annotations
import re

# id, Chinese name, group, search terms, data kinds, required inputs, reader question, caveat, local recipe
SPECS = [
 ('raincloud','雨云图','分布','raincloud|rain cloud|雨云', ['samples'],['group','raw_samples'],'组间分布、离群点和密度如何不同？','密度与箱线必须来自原始样本；带宽和抖动要说明。',None),
 ('ridgeline','山脊图','分布','ridgeline|ridgeplot|joyplot|山脊',['samples'],['group','raw_samples'],'多组分布位置和形状如何变化？','共享尺度；不要把均值列表伪装成分布。',None),
 ('violin','小提琴与分组小提琴','分布','violin|小提琴',['samples'],['group','raw_samples'],'组内密度是否多峰或偏斜？','小样本密度估计可能不稳；显示样本量。',None),
 ('ecdf','经验累积分布','分布','ecdf|empirical cumulative|累积分布',['samples'],['group','raw_samples'],'尾部概率和整体分布在哪里不同？','明确横轴变量和累计概率方向。','ecdf'),
 ('box','箱线图','分布','boxplot|box plot|boxen|箱线',['samples'],['group','raw_samples'],'中位数、四分位和离散程度如何？','声明须线规则；须线不自动等于置信区间。','box'),
 ('histogram','直方图','分布','histogram|hist|直方',['samples'],['raw_samples','bins'],'频数或密度集中在哪里？','跨组保持分箱与归一化可比。','histogram'),
 ('density','密度曲线','分布','density|kde|核密度',['samples'],['raw_samples'],'分布有几个峰、宽度多大？','声明带宽；不要从单个汇总值估计分布。',None),
 ('strip','样本散点与蜂群','分布','strip|swarm|beeswarm|jitter|蜂群',['samples'],['group','raw_samples'],'每个样本的位置如何？','抖动不代表另一个测量维度。','strip'),
 ('dumbbell','哑铃图','配对与差值','dumbbell|哑铃',['paired'],['pair_id','before','after'],'同一对象的前后差异有多大？','必须是真正配对，不能任意连接。','dumbbell'),
 ('slope','斜率图','配对与差值','slope|斜率',['paired'],['pair_id','before','after'],'对象的变化方向及交叉关系是什么？','不要把连接线误解为观测过的时间轨迹。','slope'),
 ('paired','配对点图','配对与差值','paired dot|paired_dot|paired|配对',['paired'],['pair_id','before','after'],'哪些对象改善、保持或回归？','保留对象身份和负向变化。','delta'),
 ('bland_altman','Bland–Altman 一致性图','配对与差值','bland altman|bland_altman',['paired'],['pair_id','measurement_a','measurement_b'],'两个测量的偏差是否随水平变化？','一致性界限不是无条件可解释为置信区间。',None),
 ('diverging_bar','发散条形图','比较与排序','diverging|tornado|back to back|back_to_back|龙卷风|发散',['categorical','paired'],['category','signed_value'],'相对参考点的正负效应如何？','声明参考值和正负含义；不能隐藏负值。','delta'),
 ('bump','排名变化图','比较与排序','bump|ranked arcs|ranked_arcs|排名',['series'],['entity','ordered_condition','rank'],'名次随条件如何变化？','展示并列规则；排名不等于绝对效果差。',None),
 ('lollipop','棒棒糖图','比较与排序','lollipop|lolipop|棒棒糖',['categorical'],['category','value'],'哪个类别更高，差多少？','固定基线与类别排序。','lollipop'),
 ('dot','点图','比较与排序','dot plot|dot_plot|dotplot|dot ci|dot_ci|点图',['categorical','interval'],['category','value'],'类别间的水平差异是什么？','区间必须另有统计依据。','dot'),
 ('grouped_bar','分组柱状图','比较与排序','grouped bar|grouped_bar|barplot|bars|bar chart|bar plots|柱状|条形',['categorical'],['category','series','value'],'不同方法在同一条件下如何比较？','柱高编码绝对量时从零起；组内口径一致。','bar'),
 ('waterfall','瀑布与贡献分解','组成与贡献','waterfall|瀑布',['categorical'],['ordered_component','signed_contribution','reference'],'各部分怎样累积为总变化？','分量必须能按明确规则相加。',None),
 ('stacked','堆叠图','组成与贡献','stacked bar|stacked_bar|stacked area|stacked_area|peak_stacked|堆叠',['categorical','series'],['category','component','value'],'总量及组成随类别或时间如何变化？','明确总量还是百分比；组成要有同一分母。',None),
 ('donut','环形与嵌套环形图','组成与贡献','donut|doughnut|concentric|环形',['categorical'],['component','nonnegative_value'],'整体由哪些部分组成？','组成应共享整体；小差异优先点图。',None),
 ('pie','饼图','组成与贡献','pieplot|pie chart|pie_chart|饼图',['categorical'],['component','nonnegative_value'],'少量类别占比如何？','份额分母一致；类别过多难比较。',None),
 ('treemap','矩形树图','组成与贡献','treemap|矩形树',['hierarchy'],['parent','child','nonnegative_value'],'层级组成的面积分配是什么？','面积比较不适合精细差异。',None),
 ('sunburst','旭日图','组成与贡献','sunburst|旭日',['hierarchy'],['hierarchy_path','value'],'层级份额怎样分解？','层级聚合必须守恒。',None),
 ('waffle','华夫图','组成与贡献','waffle|华夫',['categorical'],['component','count_or_share'],'离散份额如何直观表示？','说明每格代表什么和取整误差。',None),
 ('line','折线与训练趋势','趋势与过程','lineplot|line plot|line chart|training curves|training_curves|convergence|learning rate|learning_rate|time series|time_series|trend|curve|折线|收敛',['series'],['series','ordered_x','y'],'趋势、收敛或边际收益是什么？','只连接已观测点；区分开发与确认数据。','line'),
 ('step','阶梯图','趋势与过程','step plot|step_plot|interval steps|interval_steps|阶梯',['series'],['ordered_x','y'],'状态何时离散改变？','拐角是编码约定，不额外标成观测点。','step'),
 ('area','面积与流带','趋势与过程','area plot|area chart|area_plot|depreciation|面积',['series'],['ordered_x','y'],'总量如何随有序变量变化？','填充面积易放大差别；说明基线。',None),
 ('streamgraph','河流图','趋势与过程','streamgraph|stream graph|河流',['series'],['time','group','value'],'多个组成的相对变化模式是什么？','漂移基线不适合精确读绝对量。',None),
 ('horizon','地平线图','趋势与过程','horizon|地平线',['series'],['time','signed_value'],'多条长序列的异常位置在哪里？','颜色分层和折叠规则必须解释。',None),
 ('fan','扇形预测区间','趋势与过程','fan chart|fan_chart|prediction ci|prediction_ci|扇形预测',['interval','series'],['ordered_x','estimate','intervals'],'预测不确定性怎样随时间变化？','区间水平与计算方法要明确。',None),
 ('gantt','甘特图','趋势与过程','gantt|甘特',['interval'],['task','start','end'],'任务或阶段怎样并行与衔接？','阶段时间应来自真实记录。',None),
 ('scatter','散点与拟合关系','相关与权衡','scatter|散点|regression|prediction_actual',['xy','paired'],['x','y','observation_id'],'两个变量怎样共同变化？','相关不等于因果；拟合与区间需有依据。','scatter'),
 ('bubble','气泡图','相关与权衡','bubble|气泡',['xy'],['x','y','nonnegative_size'],'第三个量如何与二维位置共同变化？','面积而非半径编码 size，标单位。','bubble'),
 ('hexbin','六边形密度图','相关与权衡','hexbin|hexagonal|六边形',['xy','samples'],['raw_x','raw_y'],'大量点聚集在哪里？','网格分辨率和颜色是计数或密度要说明。',None),
 ('joint','联合与边缘分布','相关与权衡','joint|marginal|marginals|边缘分布',['xy','samples'],['raw_x','raw_y'],'联合关系与各边缘分布怎样对应？','各层必须来自同一配对样本。',None),
 ('pairplot','成对关系矩阵','相关与权衡','pair plot|pair_plot|pairplot|correlogram',['matrix','samples'],['sample_id','numeric_feature_columns'],'多个变量的两两关系是什么？','不要混用不同样本子集。',None),
 ('parallel','平行坐标','相关与权衡','parallel coordinates|parallel_coordinates|parrallele|平行坐标',['matrix'],['entity','multiple_numeric_features'],'多维性能模式和取舍是什么？','需要说明归一化和各轴方向。',None),
 ('radar','雷达图','相关与权衡','radar|spider|雷达',['matrix','categorical'],['entity','metrics','normalization'],'多指标轮廓如何不同？','轴顺序、方向和尺度会影响面积印象。',None),
 ('pareto','Pareto 性能—成本图','相关与权衡','pareto|帕累托',['xy'],['measured_cost','measured_utility'],'哪些实测点是非支配取舍？','不能编造连续前沿或漏记成本。','scatter'),
 ('heatmap','热力矩阵','矩阵与结构','heatmap|heat map|matrix|热力|热图',['matrix'],['row_id','column_id','value'],'哪些交叉条件高或低？','缺失不是零；同一比较保持色阶。','heatmap'),
 ('cluster_heatmap','聚类热图','矩阵与结构','cluster heatmap|cluster_heatmap|clustermap|聚类热',['matrix'],['matrix','distance','linkage'],'哪些行列具有共同模式？','聚类度量与顺序要能复现。',None),
 ('calendar','日历热图','矩阵与结构','calendar|日历',['series'],['date','value'],'时间周期和局部异常在哪里？','不能把缺测天当作零。',None),
 ('network','关系网络','关系与流动','network|graph network|correlation_network|网络',['network'],['node_id','edge_source','edge_target','weight'],'对象之间的关系和结构是什么？','边的统计/因果含义要明确。',None),
 ('sankey','桑基与流向图','关系与流动','sankey|alluvial|桑基|流向',['flow'],['source','target','flow_weight'],'同一总体在阶段之间如何流动？','仅有边际量不能恢复流量。',None),
 ('chord','弦图','关系与流动','chord|弦图',['flow','network'],['source','target','weight'],'类别之间的双向关系有多强？','边过多会遮挡；需要实际关系量。',None),
 ('arc','弧线网络','关系与流动','arc diagram|arc_diagram|arcdiagram',['network'],['node_order','source','target'],'在固定顺序上的关系跨度是什么？','节点顺序与边存在性须有依据。',None),
 ('venn','Venn 与集合交集','集合与覆盖','venn|维恩',['sets'],['set_membership','entity_id'],'哪些对象属于共同集合？','交集不能从各集合大小推测。',None),
 ('upset','UpSet 交集图','集合与覆盖','upset|交集',['sets'],['set_membership_matrix'],'多个集合的组合交集多大？','必须有对象级集合归属。',None),
 ('map','地理与分区地图','空间与三维','map|choropleth|geopandas|china|lisa|moran|地图|地理',['spatial'],['coordinates_or_region_ids','value','geometry'],'空间分布与邻域关系是什么？','投影和面积可能影响读图。',None),
 ('contour','等值线','空间与三维','contour|等值线',['grid'],['x_grid','y_grid','z'],'二维空间内水平线如何分布？','插值区域必须区别于观测位置。',None),
 ('surface','三维曲面与网格','空间与三维','surface|mesh|wireframe|3d|3 d|三维|manifold|swiss_roll',['grid','xyz'],['x','y','z'],'实际采样的空间结构是什么？','透视和插值不能代替新测量。',None),
 ('volume','体积与等值面','空间与三维','volume|isosurface|体积|等值面',['volume'],['x','y','z','scalar_field'],'三维标量场内部结构是什么？','阈值与采样分辨率需明确。',None),
 ('vector','向量场与轨迹','空间与三维','quiver|streamplot|vortex|vector field|gravity|向量场',['vector'],['position','vector_components'],'方向、速度或迁移轨迹如何？','向量长度和路径必须来自数据。',None),
 ('polar','极坐标与径向图','空间与三维','polar|radial|rose|极坐标|玫瑰',['polar','categorical'],['angle_or_category','radius_or_value'],'周期性、方向性或环形排序是什么？','角度不能任意充当测量方向。',None),
 ('forest','Forest 效应区间','效应与不确定性','forest|confidence interval|errorbar|error bar|dot_ci|森林',['interval'],['estimate','lower','upper','interval_definition'],'效应方向、大小及不确定性是什么？','SD、SE、CI 不能互换。','forest'),
 ('event_study','事件研究与平行趋势','效应与不确定性','event study|event_study|parallel_trends|placebo|impulse_response|事件研究',['series','interval'],['event_time','estimate','comparison','uncertainty'],'干预前后变化与对照如何？','因果解释还需识别假设与对照设计。',None),
 ('survival','生存曲线','效应与不确定性','kaplan meier|kaplan_meier|survival|生存',['survival'],['event_time','event_indicator','group'],'事件发生时间和删失如何分布？','处理删失，不把它当未发生。',None),
 ('posterior','后验轨迹与密度','效应与不确定性','posterior|mcmc|trace density|trace_density|后验',['samples','series'],['chain_id','iteration','parameter_sample'],'采样收敛与后验形态如何？','后验区间不同于频率学置信区间。',None),
 ('roc','ROC/PR 评价曲线','模型诊断','roc|precision recall|precision_recall|pr curve',['predictions'],['true_labels','continuous_scores'],'阈值变化时如何权衡错误？','必须有评分与真值，不能从一个准确率生成。',None),
 ('calibration','校准与可靠性','模型诊断','calibration|reliability|校准',['predictions'],['probability','label','binning'],'置信度与实际正确率一致吗？','分箱、样本量与区间需说明。',None),
 ('confusion','混淆矩阵','模型诊断','confusion|混淆',['matrix','predictions'],['true_label','predicted_label'],'错误集中在哪些类别对？','归一化按行、列或总体要明确。','heatmap'),
 ('residual','残差诊断','模型诊断','residual|qq plot|qqplot|error_analysis|残差',['predictions','xy'],['observed','predicted'],'误差偏差、异方差或尾部如何？','有序/配对关系不能丢失。',None),
 ('ablation','消融与敏感性','模型诊断','ablation|sensitivity|hyperparameter|sweep|消融|敏感性',['categorical','series','matrix'],['configuration','outcome','controlled_factors'],'组件或超参数变化是否改变结果？','控制信息和预算；不把所有变化都称为因果。',None),
 ('embedding','嵌入与降维','模型诊断','tsne|t sne|umap|pca|kmeans|cluster_3d|嵌入|降维',['samples','matrix'],['sample_id','feature_matrix','labels_optional'],'样本的低维结构和分组如何？','距离可能被投影扭曲；算法参数需保存。',None),
 ('shap','SHAP 与特征贡献','解释与机制','shap|feature importance|feature_importance|贡献环',['attribution'],['sample_id','feature_values','attribution_values'],'特征在样本上的贡献如何分布？','必须有实际归因值，不能用相关系数冒充。',None),
 ('pdp','PDP/ICE 依赖图','解释与机制','pdp|ice_pdp|partial dependence',['predictions','attribution'],['feature_grid','model_predictions','conditioning'],'模型输出如何随特征变化？','相关特征会影响反事实解释。',None),
 ('volcano','火山图','解释与机制','volcano|火山',['xy'],['effect_size','p_or_q_value'],'效应大小与统计证据怎样共同变化？','需要真实检验与多重比较处理。',None),
 ('taylor','Taylor 统计比较','模型诊断','taylor|泰勒',['summary_statistics'],['correlation','standard_deviation','reference'],'模型相关性与离散程度如何比较？','各统计量必须来自同一评价样本。',None),
 ('performance_profile','性能剖面','模型诊断','performance profile|performance_profile',['matrix'],['task','method','cost_or_performance'],'方法在多任务上的相对表现怎样？','定义比率、失败任务和阈值规则。',None),
 ('table','结果表与分组表','表格','benchmark table|benchmark_table|table|tabular|latex|summary rows|summary_rows|表格',['table','categorical','matrix'],['row_ids','columns','units','missing_status'],'如何读精确值、分组均值与注释？','显示格式不能改变分母与计算口径。',None),
 ('schematic','机制示意与流程','示意与组合','schematic|concept|illustration|idea|teaser|workflow|brute_force|motivation|流程|示意',['conceptual'],['entities','relations','caption'],'对象、流程和作用关系是什么？','示意关系不能伪装成实测结果。',None),
 ('multipanel','多面板组合','示意与组合','multipanel|triptych|template.|observation|distillation|多面板|组合',['mixed'],['panel_sources','panel_questions','shared_encodings'],'互补证据怎样共同回答科学问题？','逐面板绑定数据；候选板不等于最终论文版式。',None),
 ('palette','配色与视觉样式','配套资源','palette|color|theme|style|配色',['design'],['encoding_semantics','accessibility'],'颜色、线型与层次怎样更易辨识？','风格变体不是新的科学证据。',None),
 ('unclassified','待核对原图','待核对','',[],[],'需要打开原图和脚本后确定用途。','文件名不足以确定数据与图型；不能自动用于科学结论。',None),
]
SPECS += [
 ('funnel','漏斗图','比较与排序','funnel|漏斗',['categorical'],['ordered_stage','count'],'各阶段损耗如何？','阶段应对应同一总体，不能将无关计数串联。',None),
 ('hovmoller','Hovmöller 时空图','矩阵与结构','hovmoller',['grid'],['time','space','value'],'随空间与时间共同变化的模式是什么？','标清空间轴和时间采样。',None),
 ('feasible','可行域与约束边界','空间与三维','feasible region|feasible_region',['grid','xy'],['constraints','coordinates','feasibility'],'哪些区域满足约束？','边界应由明确约束计算，不能凭视觉推断。',None),
 ('state_grid','状态网格','矩阵与结构','state grid|state_grid',['matrix'],['state_coordinates','state_value'],'离散状态的可达性或评价如何？','颜色对应离散状态还是数值必须说明。',None),
 ('coefficient','系数稳定与平衡诊断','效应与不确定性','coefficient|psm balance|psm_balance',['interval','matrix'],['specification','estimate','balance_metric'],'估计随设定变化是否稳定、组间是否平衡？','诊断不自动证明因果可识别。',None),
 ('variance','方差与误差分解','组成与贡献','variance decomposition|variance_decomposition',['categorical','series'],['component','decomposition_rule','value'],'不同来源贡献了多少变异？','分解依赖统计定义，不能把任意分数相加。',None),
 ('latent','潜空间插值','模型诊断','latent interpolation|latent_interpolation',['mixed'],['latent_path','decoded_outputs'],'沿潜空间路径输出如何变化？','生成样本与真实观测必须区分。',None),
 ('dendrogram','层次树与树状聚类','矩阵与结构','dendrogram|hierarchical clustering',['matrix','hierarchy'],['distance_matrix','linkage'],'对象如何逐级合并为组？','距离与联接规则影响树结构。',None),
 ('wordcloud','词云','组成与贡献','wordcloud|word cloud|词云',['categorical'],['token','frequency_or_weight'],'高频词或关键词是什么？','词云不适合精确比较；需记录分词与权重。',None),
 ('animation','动态图','趋势与过程','animation|animated|gapminder',['series','xy','spatial'],['frame_id','stable_entity_id','observations'],'状态随帧如何连续或离散变化？','转场插值不是新的观测。',None),
 ('layout','标注、图例与排版示例','配套资源','annotation|annotate|marker|axis|axes|title|margin|subplot|customizing',['design'],['labels','units','legend_semantics'],'如何让图例、标签和布局更清晰？','这些是样式教程，不是独立研究证据。',None),
 ('dual_axis','双轴与多轴图','示意与组合','dual axis|dual_axis|multi y|multi_y',['series','mixed'],['x','separate_y_units','axis_mapping'],'不同量纲如何沿同一横轴对照？','多轴缩放容易制造相关印象，优先检查是否可拆图。',None),
]
SPECS += [
 ('circle_packing','圆形打包图','组成与贡献','circular packing|circle packing|circlepack|packing',['hierarchy'],['parent','child','nonnegative_value'],'层级内的大小如何比较？','面积编码而非半径；空间间隙没有数值含义。',None),
 ('candlestick','蜡烛与区间范围图','趋势与过程','candle stick|candlestick|ohlc',['series'],['ordered_x','open','close','high','low'],'每个时间段的范围与始末值如何？','四个统计量需来自同一时间窗。',None),
 ('quantiles','分位数分布图','分布','quantile|quantiles|distribution plot',['samples','interval'],['raw_samples_or_quantiles','group'],'分布各位置怎样随条件变化？','区分原始样本、估计分位数和回归系数。',None),
 ('test_visual','统计检验可视化','效应与不确定性','t test|anova|student t',['samples'],['samples','design','test_definition'],'组间差异及检验依据如何？','图示不能替代假设检验条件与多重比较控制。',None),
 ('cartogram','变形统计地图','空间与三维','cartogram|bubblemap|folium|mercator|chloro',['spatial'],['region_id','geometry','value'],'统计量如何与地理区域对应？','面积变形改变地理关系，需要图例。',None),
]
FAMILIES = {r[0]:{'id':r[0],'label':r[1],'group':r[2],'terms':r[3].split('|') if r[3] else [],'data_kinds':r[4],'required_fields':r[5],'question':r[6],'caution':r[7],'local_recipe':r[8]} for r in SPECS}

ALIASES = {
 'line':['line','lines','line plot','lineplot','linechart','linecharts','spaghetti','multistep decay'],
 'area':['area'], 'fan':['fan'], 'scatter':['scatterplot','scatter plot','pointplot'],
 'grouped_bar':['bar','barplots','bars','bar plot'], 'violin':['violinplot'],
 'strip':['swarmplot','stripplot','overplotting'], 'network':['networkx'], 'parallel':['parallel plot'],
 'box':['box','boxplots','boxenplot'], 'histogram':['histograms','histplot'],
 'density':['densityplot'], 'joint':['jointplot'], 'heatmap':['heat','heatmaps'],
 'radar':['radarchart'], 'streamgraph':['streamchart'], 'lollipop':['lolliplot'],
 'layout':['layout','annotations','labels','label','legend','fonts','font','hatch','texture','arrows','arrow','flexitext','markers','coordinate system'],
 'table':['plottable','tables','timetable'],
 'palette':['palettes','colour','colourmap','colorbar','colours','theme','themes','colors','colormap','cmap'],
 'map':['basemap','choropleth','geographic','setbounding'],
 'multipanel':['small multiples','small multiple','multiple subplots','faceting'],
}
for family, aliases in ALIASES.items(): FAMILIES[family]['terms'].extend(aliases)

def normalized(value: str) -> str:
    value=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',str(value))
    value=re.sub(r'([a-zA-Z])\d+(?=[^a-zA-Z]|$)',r'\1',value)
    return re.sub(r'[^\w\u4e00-\u9fff]+',' ',value.lower().replace('_',' ')).strip()

def classify(title: str, path: str = '') -> list[str]:
    text=normalized(title+' '+path)
    matches=[]
    for fid,f in FAMILIES.items():
        for alias in f['terms']:
            token=normalized(alias)
            if token and ((re.search(r'[\u4e00-\u9fff]',token) and token in text) or (' '+token+' ') in (' '+text+' ')):
                matches.append((len(token),fid));break
    # Preserve composite structure; the first label is the most specific lexical match.
    ordered=[]
    for _,fid in sorted(matches,reverse=True):
        if fid not in ordered: ordered.append(fid)
    return ordered[:6] or ['unclassified']
