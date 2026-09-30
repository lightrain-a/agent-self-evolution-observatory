/* Only the reviewed compact catalogue enters this page; the raw archive is never loaded. */
(() => {
'use strict';
const data=window.FIGURE_CURATED, el=id=>document.getElementById(id);
if(!data){el('curated-grid').textContent='精选目录未加载，请刷新。';return;}
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safe=u=>{try{const x=new URL(u);return x.protocol==='https:'&&['github.com','raw.githubusercontent.com'].includes(x.hostname)?x.href:''}catch(_){return ''}};
const records=new Map(data.entries.map(e=>[e.id,e]));let lang='zh',selected=new Set(),visible=[];
const pick=(zh,en)=>lang==='zh'?zh:en;
const storageKey='publication-figure-shortlist-v2';
try{const s=JSON.parse(localStorage.getItem(storageKey)||'null');if(s?.catalog_version===data.catalog_version&&Array.isArray(s.ids))selected=new Set(s.ids.filter(i=>records.has(i)).slice(0,2));}catch(_){}
function status(message){el('selection-status').textContent=message;}
function save(){try{localStorage.setItem(storageKey,JSON.stringify({catalog_version:data.catalog_version,ids:[...selected]}));}catch(_){status(pick('浏览器存储不可用；仍可导出。','Browser storage unavailable; export is still available.'));}}
function bindImages(root){root.querySelectorAll('img[data-reference]').forEach(img=>img.addEventListener('error',()=>{img.hidden=true;const note=img.parentElement.querySelector('.preview-note');if(note)note.hidden=false;},{once:true}));}
function render(){
 const q=el('curated-search').value.toLowerCase().trim(),group=el('curated-group').value;
 visible=data.entries.filter(e=>(!group||e.group===group)&&(!q||[e.title,e.title_en,e.question,e.question_en,e.chart].join(' ').toLowerCase().includes(q)));
 el('curated-grid').innerHTML=visible.map(e=>`<article class="reference-card${selected.has(e.id)?' selected':''}" data-id="${esc(e.id)}"><button class="preview" data-open="${esc(e.id)}" aria-label="${esc(pick(e.title,e.title_en))}"><img src="${esc(safe(e.preview_url))}" alt="${esc(e.title_en)} — Figures4Papers original reference" loading="lazy" decoding="async" referrerpolicy="no-referrer" data-reference="${esc(e.id)}"><span class="preview-note" hidden>${pick('原站预览暂不可用；点下方原图链接查看。','Upstream preview unavailable; use the source link.')}</span><span class="preview-label">${pick('参考原图 · 点击放大','Reference · click to enlarge')}</span></button><div class="card-body"><div class="card-meta">FIGURES4PAPERS / ${esc(e.chart.replaceAll('_',' '))}</div><h3>${esc(pick(e.title,e.title_en))}</h3><p class="card-question">${esc(pick(e.question,e.question_en))}</p><p class="card-learn">${esc(pick(e.learn,e.learn_en))}</p><div class="card-fields">${pick('输入','Inputs')}: ${esc(e.required_fields.join(' · '))}</div><div class="card-footer"><span><a href="${esc(safe(e.source_url))}" target="_blank" rel="noopener noreferrer">${pick('原图','Original')}</a> · <a href="${esc(safe(e.code_url))}" target="_blank" rel="noopener noreferrer">${pick('对应代码','Script')}</a></span><button data-select="${esc(e.id)}" aria-pressed="${selected.has(e.id)}">${selected.has(e.id)?pick('✓ 已选','✓ Selected'):pick('选作参考','Select reference')}</button></div></div></article>`).join('')||'<p>'+pick('没有符合条件的精选项。不要为了补数量自动打开完整档案。','No curated match. The archive is not opened automatically.')+'</p>';
 el('result-count').textContent=pick(`${visible.length} 个精选参考 · 按表达用途筛选，不按文件数量排序`,`${visible.length} curated references · organized by purpose, not file count`);
 el('selection-count').textContent=pick(`已选 ${selected.size} / 2 个参考`,`${selected.size} / 2 references selected`);
 bindImages(el('curated-grid'));
}
function labels(){
 document.documentElement.lang=lang;el('language-toggle').textContent=pick('English','中文');
 el('gallery-title').innerHTML=pick('少量好图，<br>让比较关系更清楚。','Fewer references.<br>Clearer comparisons.');
 el('gallery-intro').textContent=pick('从完整目录中收紧到真正可能用到的论文图参考。先确定要回答的问题，再选一种主方案和一种备选；不是让 AI 在上千张图片里碰运气。','A focused set of publication examples. Start with the scientific question, then one preferred encoding and one meaningful alternative—not thousands of images.');
 el('references-title').textContent=pick('论文里真正用得上的结构','Structures that serve a paper');
 el('selection-heading').textContent=pick('这张图要回答什么？','What should this figure answer?');
 el('selection-help').textContent=pick('例如：提高成功率的同时，是否增加了评估成本？','For example: does higher success require more evaluations?');
 el('question-label').textContent=pick('读者问题','Reader question');
 el('reader-question').placeholder=pick('用一句话写下问题；不是图型名称','One scientific question, not a chart name');
 el('export-brief').textContent=pick('导出给 Agent','Export for agent');
 el('curated-metrics').innerHTML=[[data.summary.active_examples,pick('精选参考原图','curated originals')],[2,pick('每次最多引用','references per task')],[0,pick('默认载入的归档条目','archive entries loaded')]].map(([v,t])=>`<span><b>${v}</b>${t}</span>`).join('');
 el('audit-counts').innerHTML='<table>'+Object.entries(data.exclusion_counts).map(([key,value])=>`<tr><td>${esc(key)}</td><td>${value}</td></tr>`).join('')+'</table>';
}
function detail(id){const e=records.get(id);if(!e)return;el('figure-detail').innerHTML=`<h2>${esc(pick(e.title,e.title_en))}</h2><p>${esc(pick(e.question,e.question_en))}</p><div><img class="detail-image" data-reference="${esc(e.id)}" src="${esc(safe(e.preview_url))}" alt="${esc(e.title_en)}" referrerpolicy="no-referrer"><p class="preview-note" hidden>${pick('预览不可用，请打开原图。','Preview unavailable; open the original.')}</p></div><div class="detail-notes"><p>${esc(pick(e.learn,e.learn_en))}</p><p>${pick('这是上游设计参考，不是本项目实验结果。保留既有论文的字体、指标定义和颜色语义；不可直接照抄刻度、误差条或数值。','This is an upstream design reference, not project evidence. Keep the manuscript’s established typography, metrics and method encoding; do not copy scales, error bars or values.')}</p><p>Source commit: <code>${esc(e.commit)}</code><br>${esc(e.license)}</p><a href="${esc(safe(e.source_url))}" target="_blank" rel="noopener noreferrer">${pick('查看原图','Original image')}</a> · <a href="${esc(safe(e.code_url))}" target="_blank" rel="noopener noreferrer">${pick('查看脚本','Source script')}</a> · <a href="${esc(safe(e.license_url))}" target="_blank" rel="noopener noreferrer">License</a></div>`;bindImages(el('figure-detail'));el('figure-dialog').showModal();}
function toggle(id){if(!records.has(id))return;if(selected.has(id))selected.delete(id);else if(selected.size>=2){status(pick('每次最多选 2 个参考。先取消一个，再加入新参考。','Select at most two references; remove one before adding another.'));return;}else selected.add(id);save();render();}
function exportBrief(){const question=el('reader-question').value.trim();if(!question||selected.size===0){status(pick('先写下读者问题，并选择 1–2 个参考。','Enter a reader question and select 1–2 references.'));return null;}
 const brief={schema_version:'2.0',origin:'BROWSER_DRAFT_NOT_SERVER_APPROVAL',catalog_version:data.catalog_version,reader_question:question,reference_limit:2,reference_scope:'curated_only',entries:[...selected].map(id=>{const e=records.get(id);return {entry_id:e.id,content_version:e.content_version,title:e.title,chart:e.chart,required_fields:e.required_fields,source_url:e.source_url,code_url:e.code_url,commit:e.commit,reference_only:true};}),requires_project_evidence:true,visual_review:'NOT_RUN',scientific_authority:false};
 const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify(brief,null,2)],{type:'application/json'}));a.href=url;a.download='curated-figure-brief.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),500);status(pick('已导出；下一步结合项目数据和现有脚本核验。','Exported; validate against project evidence and the existing builder.'));return brief;
}
document.addEventListener('click',event=>{const a=event.target.closest('[data-open]');if(a){detail(a.dataset.open);return;}const s=event.target.closest('[data-select]');if(s)toggle(s.dataset.select);});
el('curated-search').addEventListener('input',render);el('curated-group').addEventListener('change',render);
el('language-toggle').onclick=()=>{lang=lang==='zh'?'en':'zh';labels();render();};el('close-dialog').onclick=()=>el('figure-dialog').close();el('export-brief').onclick=exportBrief;
labels();render();window.curatedFigureUI={getVisible:()=>visible.map(e=>e.id),getSelected:()=>[...selected],toggle,exportBrief};
})();
