/* All upstream entries, rather than the 19 local renderers. No remote code executes. */
(() => {
  'use strict';
  const kb=window.FIGURE_KNOWLEDGE_BASE;
  const el=id=>document.getElementById(id);
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl=value=>{try{const u=new URL(value);return u.protocol==='https:'&&['github.com','raw.githubusercontent.com','python-graph-gallery.com'].includes(u.hostname)?u.href:''}catch(_){return ''}};
  if(!kb){el('kb-error').hidden=false;el('kb-error').textContent='图表知识索引未加载，请刷新或查看仓库源文件。';return}
  let lang='zh',limit=48,filtered=[],favoriteOnly=false;
  const pick=(a,b)=>lang==='zh'?a:b;
  const families=Object.fromEntries(kb.families.map(f=>[f.id,f]));
  const records=Object.fromEntries(kb.entries.map(e=>[e.id,e]));
  const kindNames={RECIPE_CARD:['配方与组合模板','Recipe / composite template'],FIGURE_EXAMPLE:['具体图例','Figure example'],TABLE_EXAMPLE:['表格图例','Table example'],TUTORIAL:['教程与代码入口','Tutorial / code entry'],TABLE_GUIDE:['表格教程','Table guide'],SUPPORT_ASSET:['配套图片与资源','Supporting image / resource']};
  const storageKey='research-figure-kb-shortlist-v1';let favorites={};
  try{favorites=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(_){favorites={}}
  if(!favorites||Array.isArray(favorites)||typeof favorites!=='object')favorites={};
  const corpus=kb.entries.map(e=>({entry:e,text:[e.id,e.title,e.path,e.source_name,...e.families.flatMap(id=>{const f=families[id];return[f.label,f.group,f.question,...f.terms,...f.required_fields]})].join(' ').toLowerCase().replace(/[_-]/g,' ')}));
  function options(target,values,empty){const previous=target.value;target.innerHTML='<option value="">'+esc(empty)+'</option>'+values.map(([value,label])=>`<option value="${esc(value)}">${esc(label)}</option>`).join('');target.value=previous}
  function saveFavorites(){try{localStorage.setItem(storageKey,JSON.stringify(favorites));el('kb-storage').textContent=pick('收藏已保存到本机浏览器；尚未写入服务器。导出选图包可交给后续绘图流程。','Shortlist saved in this browser, not on the server. Export a selection brief for the plotting workflow.')}catch(_){el('kb-storage').textContent=pick('浏览器存储不可用，请导出选图包。','Browser storage unavailable. Export your selection brief.')}}
  function thumb(e){
    if(!e.previews.length)return `<div class="no-preview">${pick('上游未提供可显示预览','No released preview')}<small>${e.documents.length?pick('有 PDF 原文件','Original PDF available'):pick('打开源文件查看','Open the source file')}</small></div>`;
    const image=e.previews[0];
    return `<img src="${esc(safeUrl(image.thumbnail_url||image.url))}" loading="lazy" decoding="async" referrerpolicy="no-referrer" alt="${esc(e.title)}" data-preview="${esc(e.id)}"><span class="image-failed" hidden>${pick('原站图片暂未加载，请打开来源','Source image unavailable; open original')}</span>`;
  }
  function card(e){
    const chosen=!!favorites[e.id],old=chosen&&favorites[e.id].content_version!==e.content_version;
    return `<article class="card${chosen?' selected':''}" data-id="${esc(e.id)}"><button class="preview" data-open="${esc(e.id)}" aria-label="${esc(e.title)}">${thumb(e)}<span class="preview-count">${e.previews.length||e.documents.length} ${pick('预览/文件','views/files')}</span></button><div class="card-body"><div class="card-kicker"><span>${esc(e.source_name)}</span><span>${pick(...kindNames[e.kind])}</span></div><h3><button data-open="${esc(e.id)}">${esc(e.title)}</button></h3><div class="tags">${e.families.slice(0,3).map(id=>`<button data-family="${esc(id)}">${esc(pick(families[id].label,id.replaceAll('_',' ')))}</button>`).join('')}</div><p class="question">${esc(families[e.families[0]].question)}</p><p class="annotation">${e.families.includes('unclassified')?pick('文件名不足以判断：需看原图','Unclassified: inspect original'):pick('分类与要求为规则注释，需核对原图','Rule-based annotation; inspect original')}${e.exact_duplicate_of?pick(' · 有相同内容副本',' · identical-content alias'):''}</p><footer><a href="${esc(safeUrl(e.source_url))}" target="_blank" rel="noopener noreferrer">${pick('原图/来源','Source')}</a><button class="star" data-star="${esc(e.id)}" aria-pressed="${chosen}">${old?pick('版本已变 · 重选','Changed · reselect'):chosen?pick('★ 已收藏','★ Saved'):pick('☆ 收藏','☆ Save')}</button></footer><small class="credit">${esc(e.author)} · <a href="${esc(safeUrl(e.license_url))}" target="_blank" rel="noopener noreferrer">${esc(e.license)}</a></small></div></article>`;
  }
  function bindImages(root){root.querySelectorAll('img[data-preview]').forEach(img=>img.addEventListener('error',()=>{img.hidden=true;const note=img.parentElement.querySelector('.image-failed');if(note)note.hidden=false},{once:true}))}
  function show(){
    const query=el('kb-search').value.toLowerCase().replace(/[_-]/g,' ').trim().split(/\s+/).filter(Boolean);
    const source=el('kb-source').value,family=el('kb-family').value,kind=el('kb-kind').value,data=el('kb-data').value;
    filtered=corpus.filter(({entry:e,text})=>(!source||source===e.source_id)&&(!family||e.families.includes(family))&&(!kind||kind===e.kind)&&(!data||e.data_kinds.includes(data))&&(!el('kb-preview-only').checked||e.previews.length)&&(!el('kb-favorites-only').checked||favorites[e.id])&&query.every(q=>/[\u4e00-\u9fff]/.test(q)?text.includes(q):text.split(/[\s./|]+/).includes(q))).map(r=>r.entry);
    const visible=filtered.slice(0,limit);
    el('kb-grid').innerHTML=visible.length?visible.map(card).join(''):`<p class="empty">${pick('没有匹配项；试试较短的图名、用途或清空筛选。','No matches. Try a shorter term or reset the filters.')}</p>`;
    el('kb-result-count').textContent=pick(`找到 ${filtered.length} 项 · 当前显示 ${visible.length} 项`,`Found ${filtered.length} · showing ${visible.length}`);
    el('kb-page-count').textContent=pick(`${visible.length} / ${filtered.length} · 图片随滚动加载，不截断目录`,`${visible.length} / ${filtered.length} · lazy images, complete inventory`);
    el('kb-more').hidden=visible.length>=filtered.length;
    el('kb-show-all').disabled=visible.length>=filtered.length;
    el('kb-export').textContent=pick(`导出选图包（${Object.keys(favorites).length}）`,`Export shortlist (${Object.keys(favorites).length})`);
    bindImages(el('kb-grid'));
    const url=new URL(location.href);for(const [k,v] of [['q',el('kb-search').value],['source',source],['family',family],['data',data],['kind',kind]]){if(v)url.searchParams.set(k,v);else url.searchParams.delete(k)}
    history.replaceState(null,'',url.toString());
  }
  function detail(id){
    const e=records[id];if(!e)return;
    const guide=e.families.map(fid=>{const f=families[fid];return `<section><h3>${esc(f.label)}</h3><p><b>${pick('想回答的问题','Question')}: </b>${esc(f.question)}</p><p><b>${pick('所需数据','Required inputs')}: </b>${esc(f.required_fields.join(' / ')||pick('需核对','Inspect source'))}</p><p><b>${pick('注意','Caution')}: </b>${esc(f.caution)}</p></section>`}).join('');
    const views=e.previews.map((image,i)=>`<figure><a href="${esc(safeUrl(image.source_url))}" target="_blank" rel="noopener noreferrer"><img src="${esc(safeUrl(image.url))}" loading="lazy" referrerpolicy="no-referrer" alt="${esc(e.title)} ${i+1}" data-preview="${esc(e.id)}"><span class="image-failed" hidden>${pick('预览加载失败，请打开原图','Preview unavailable; open source')}</span></a><figcaption>${esc(image.path)} · ${image.bytes??'?'} bytes · ${esc(image.blob_sha.slice(0,12))}</figcaption></figure>`).join('');
    el('kb-detail-body').innerHTML=`<h2>${esc(e.title)}</h2><p>${esc(e.source_name)} · <code>${esc(e.id)}</code></p><p>${pick('图片由浏览器直接读取上游地址；本系统未复制或重新托管图像。','Images are fetched directly from upstream, not mirrored by this system.')}</p><div class="detail-previews">${views||'<p>'+pick('此条目没有发布的图像预览，源文件仍完整收录。','No released image preview. The source entry is still indexed.')+'</p>'}</div>${e.documents.map(d=>`<a href="${esc(safeUrl(d.source_url))}" target="_blank" rel="noopener noreferrer">${esc(d.path)}</a>`).join('<br>')}<div class="detail-guide">${guide}</div><h3>${pick('代码 / 教程入口','Code / tutorial references')}</h3>${e.related_code.length?e.related_code.map(c=>`<p><a href="${esc(safeUrl(c.url))}" target="_blank" rel="noopener noreferrer">${esc(c.path)}</a><small> ${esc(c.relation)}</small></p>`).join(''):'<p>'+pick('没有可确认的同目录脚本；先读源条目，不自动猜实现。','No matching source script identified; inspect the source entry first.')+'</p>'}<p><b>${pick('重要区别','Important distinction')}: </b>${pick('收录不等于已经安装或能直接运行。文件名关联的脚本只是候选，需查看后确认；图例中的结果不是本项目的数据。','Indexed does not mean installed or executable. Filename-associated scripts require inspection; example values are not our experimental data.')}</p><p>${esc(e.author)} · <a href="${esc(safeUrl(e.license_url))}" target="_blank" rel="noopener noreferrer">${esc(e.license)}</a></p><p>commit <code>${esc(e.commit)}</code></p><button data-star="${esc(e.id)}">${favorites[e.id]?pick('取消收藏','Remove from shortlist'):pick('加入选图包','Add to shortlist')}</button>`;
    bindImages(el('kb-detail-body'));if(!el('kb-detail').open)el('kb-detail').showModal();
  }
  function labels(){
    document.documentElement.lang=lang;
    document.querySelectorAll('[data-zh]').forEach(n=>n.textContent=lang==='zh'?n.dataset.zh:n.dataset.en);
    el('language-toggle').textContent=pick('English','中文');el('kb-title').textContent=pick('完整科研图表知识库','Research figure knowledge base');
    el('kb-intro').textContent=pick('不再把上游图库压成19种本地模板。逐仓库收录配方、具体图例、所有视觉文件与教程，按数据结构和研究问题检索；不同设计变体全部保留。','The full upstream libraries, not just 19 local recipes: recipe cards, individual examples, visual assets and tutorials, searchable by data shape and research question. Design variants stay available.');
    const s=kb.summary;
    el('kb-metrics').innerHTML=[[s.repositories,pick('参考仓库','repositories')],[s.entries,pick('可检索条目','indexed entries')],[s.visual_files,pick('视觉文件逐一覆盖','visual files accounted for')],[s.selectable_examples,pick('配方与具体图例','recipes / visual examples')],[s.tutorial_entries,pick('教程条目','tutorial entries')]].map(([v,l])=>`<span><b>${v}</b>${l}</span>`).join('');
    options(el('kb-source'),kb.sources.map(s=>[s.id,s.name]),pick('全部仓库','All repositories'));
    const familyCounts={};kb.entries.forEach(e=>e.families.forEach(f=>familyCounts[f]=(familyCounts[f]||0)+1));
    options(el('kb-family'),kb.families.map(f=>[f.id,`${pick(f.label,f.id.replaceAll('_',' '))} (${familyCounts[f.id]||0})`]),pick('全部图型与用途','All families / purposes'));
    options(el('kb-data'),Array.from(new Set(kb.entries.flatMap(e=>e.data_kinds))).sort().map(k=>[k,k]),pick('全部数据结构','All data shapes'));
    options(el('kb-kind'),Object.entries(kindNames).map(([k,v])=>[k,pick(...v)]),pick('全部（含教程和配套）','All, including tutorials/support'));
    el('kb-clear').textContent=pick('清空筛选','Reset filters');el('kb-show-all').textContent=pick('展开全部结果','Show all matches');el('kb-more').textContent=pick('再看48项','48 more');
    el('kb-annotation-note').textContent=pick(' · 数量不是独立图型数；分类注释不等于逐图人工审查。',' · Counts are not unique chart types; rule tags are not human visual review.');
    el('kb-boundary').textContent=pick('目录完整收录不代表所有外部配方都已安装。后续先按问题与数据选图，再读取固定版本源文件、核对许可和真实数据要求，决定使用本地渲染器还是编写适配器。原站图像加载失败会明确提示，不用合成图替代。','Indexing does not install upstream recipes. Select by question and data, inspect pinned source and license, then use a local renderer or create an adapter. Failed upstream previews are reported, never replaced with invented images.');
    el('kb-storage').textContent=pick('收藏只在本机浏览器；导出包含条目ID、源版本、图型、数据要求与许可，供后续选图使用。','Shortlists are local to this browser. Exports contain entry IDs, source versions, families, input requirements and licenses.');
    el('kb-family-guide').innerHTML=kb.families.map(f=>`<section><h3>${esc(f.label)}</h3><p>${esc(f.question)}</p><code>${esc(f.required_fields.join(' / '))}</code><p>${esc(f.caution)}</p><button data-family="${esc(f.id)}">${pick('查看全部相关图例','Browse all matching examples')} (${familyCounts[f.id]||0})</button></section>`).join('');
    el('kb-coverage-body').innerHTML='<table><thead><tr><th>Repository</th><th>Entries</th><th>Previews available</th><th>Commit</th></tr></thead><tbody>'+kb.sources.map(s=>{const rows=kb.entries.filter(e=>e.source_id===s.id);return `<tr><td>${esc(s.name)}</td><td>${rows.length}</td><td>${rows.filter(e=>e.previews.length).length}</td><td><a href="https://github.com/${esc(s.repo)}/tree/${esc(s.commit)}">${esc(s.commit.slice(0,12))}</a></td></tr>`}).join('')+'</tbody></table><p>'+pick('完整 Git tree 未截断；所有图片/PDF 文件都对应条目。配套资源、相同文件副本、不同导出格式和教程单列，不能合并称为“这么多种图”。','Complete, non-truncated Git trees. Every image/PDF maps to an entry. Support assets, exact duplicates, formats and tutorials are distinguished from chart types.')+'</p><a href="generated/figure-knowledge-coverage.json" download>'+pick('下载逐文件覆盖审计','Download path-level coverage audit')+'</a>';
  }
  document.addEventListener('click',event=>{
    const open=event.target.closest('[data-open]');if(open){detail(open.dataset.open);return}
    const star=event.target.closest('[data-star]');if(star){const e=records[star.dataset.star];if(!e)return;const same=favorites[e.id]?.content_version===e.content_version;if(same)delete favorites[e.id];else favorites[e.id]={id:e.id,content_version:e.content_version,saved_at:new Date().toISOString()};saveFavorites();show();if(el('kb-detail').open)detail(e.id);return}
    const family=event.target.closest('[data-family]');if(family){el('kb-family').value=family.dataset.family;limit=48;show();el('kb-search').focus()}
  });
  el('kb-close').onclick=()=>el('kb-detail').close();el('kb-detail').addEventListener('click',e=>{if(e.target===el('kb-detail'))el('kb-detail').close()});
  let timer;el('kb-search').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{limit=48;show()},180)});
  ['kb-source','kb-family','kb-data','kb-kind','kb-preview-only','kb-favorites-only'].forEach(id=>el(id).addEventListener('change',()=>{limit=48;show()}));
  el('kb-more').onclick=()=>{limit+=48;show()};el('kb-show-all').onclick=()=>{limit=kb.entries.length;show()};
  el('kb-clear').onclick=()=>{['kb-search','kb-source','kb-family','kb-data','kb-kind'].forEach(id=>el(id).value='');el('kb-preview-only').checked=false;el('kb-favorites-only').checked=false;limit=48;show()};
  el('language-toggle').onclick=()=>{lang=lang==='zh'?'en':'zh';labels();show()};
  el('kb-export').onclick=()=>{
    const selected=Object.keys(favorites).map(id=>records[id]).filter(Boolean);
    const out={schema_version:'1.0',origin:'BROWSER_SHORTLIST_NOT_SERVER_APPROVAL',checked_on:kb.checked_on,columns:4,entries:selected.map(e=>({entry_id:e.id,content_version:e.content_version,selection_current:favorites[e.id].content_version===e.content_version,title:e.title,source_url:e.source_url,commit:e.commit,preview_urls:e.previews.map(p=>p.url),families:e.families.map(f=>families[f]),code_candidates:e.related_code,license:e.license,annotation_status:e.annotation_status,implementation_status:e.implementation_status})),scientific_authority:false};
    const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));a.href=url;a.download='figure-selection-brief.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),500);
  };
  labels();const initial=new URL(location.href);for(const[k,id]of[['q','kb-search'],['source','kb-source'],['family','kb-family'],['data','kb-data'],['kind','kb-kind']])if(initial.searchParams.has(k))el(id).value=initial.searchParams.get(k);show();
  window.figureKnowledgeUI={filter:show,getFiltered:()=>filtered.map(e=>e.id),showAll:()=>{limit=kb.entries.length;show()}};
})();
