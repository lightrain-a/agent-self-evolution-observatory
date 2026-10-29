/* DOM interaction checks. This does not claim browser layout verification. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const ROOT=path.resolve(__dirname,'..'),SITE=path.join(ROOT,'rsi');
const {JSDOM,VirtualConsole}=require(process.env.RSI_JSDOM_PATH || path.join(ROOT,'.rsi-qa-deps/node_modules/jsdom'));
const taxonomy=JSON.parse(fs.readFileSync(path.join(SITE,'taxonomy.json'),'utf8'));
const papers=JSON.parse(fs.readFileSync(path.join(SITE,'reading-cards.json'),'utf8')).papers;
const sources=JSON.parse(fs.readFileSync(path.join(SITE,'sources.json'),'utf8')).sources;
const functions=taxonomy.functions.map(f=>f.id);
const pending=[];
async function load(file){
  const url=new URL(file,'https://rsi.test/rsi/');
  const errors=[];
  const vc=new VirtualConsole();
  vc.on('jsdomError',e=>errors.push(e.message));
  const dom=new JSDOM(fs.readFileSync(path.join(SITE,path.basename(url.pathname)),'utf8'),{url:url.href,runScripts:'outside-only',virtualConsole:vc});
  const w=dom.window;
  w.HTMLElement.prototype.scrollIntoView=function(){};
  w.scrollTo=()=>{};
  w.matchMedia=media=>({matches:false,media,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
  w.fetch=async href=>{
    const target=path.join(SITE,path.basename(new URL(href,w.location.href).pathname));
    return {ok:fs.existsSync(target),json:async()=>JSON.parse(fs.readFileSync(target,'utf8'))};
  };
  w.addEventListener('error',e=>errors.push(e.message));
  for(const script of [...w.document.querySelectorAll('script[src]')]){
    const src=script.getAttribute('src');
    if(/^(https?:)?\/\//.test(src))continue;
    const f=path.join(SITE,src.split('?')[0]);
    if(fs.existsSync(f))w.eval(fs.readFileSync(f,'utf8'));
  }
  await new Promise(resolve=>setTimeout(resolve,20));
  assert.deepEqual(errors,[],file+': runtime errors');
  return {dom,w,d:w.document,errors};
}
function select(w,d,id,value){
  const el=d.getElementById(id);assert(el,'Missing control '+id);
  el.value=value;assert.equal(el.value,value,'Invalid option '+value);
  el.dispatchEvent(new w.Event('change',{bubbles:true}));
}
function input(w,d,id,value){
  const el=d.getElementById(id);el.value=value;el.dispatchEvent(new w.Event('input',{bubbles:true}));
}
function visible(d,selector){return [...d.querySelectorAll(selector)].filter(e=>!e.hidden);}
(async()=>{
  let env=await load('reading-cards.html'),{w,d}=env;
  assert.equal(d.querySelectorAll('.reading-card').length,papers.length);
  for(const f of functions)for(const relation of ['primary','related','all']){
    select(w,d,'reading-function-filter',f);select(w,d,'reading-relation-filter',relation);
    const expected=papers.filter(p=>relation==='primary'?p.primary_function===f:relation==='related'?p.related_functions.includes(f):p.primary_function===f||p.related_functions.includes(f)).map(p=>p.id).sort();
    assert.deepEqual(visible(d,'.reading-card').map(e=>e.id).sort(),expected,'Reading '+f+'/'+relation);
  }
  input(w,d,'reading-card-filter','no_such_paper_20261029');assert.equal(visible(d,'.reading-card').length,0);
  assert.equal(d.getElementById('reading-empty').hidden,false);env.dom.window.close();
  env=await load('reading-cards.html?function=capability');({w,d}=env);
  assert.equal(visible(d,'.reading-card').length,papers.filter(p=>p.primary_function==='capability').length);
  env.dom.window.close();
  env=await load('references.html');({w,d}=env);
  assert.equal(d.querySelectorAll('.source-card').length,sources.length);
  for(const f of [...functions,'support']){
    select(w,d,'reference-function',f);
    assert.equal(visible(d,'.source-card').length,sources.filter(s=>(s.primary_function||'support')===f).length,'Sources '+f);
  }
  select(w,d,'reference-function','all');input(w,d,'reference-query','E100');
  assert(visible(d,'.source-card').some(e=>e.id==='E100'));
  input(w,d,'reference-query','no_such_source_20261029');assert.equal(visible(d,'.source-card').length,0);
  env.dom.window.close();
  env=await load('ideas.html#idea-1');({w,d}=env);
  assert.equal(d.querySelectorAll('.framework-idea-detail').length,14);
  assert(d.querySelector('#idea-1').open,'Stable I1 anchor must open details');
  assert.equal(d.querySelector('#research-nav a[aria-current="page"]').getAttribute('href'),'ideas.html#idea-1');
  for(const [iid,idea] of Object.entries(taxonomy.ideas)){
    const details=d.getElementById('idea-'+iid.slice(1));
    assert.equal(details.dataset.primaryFunction,idea.primary,iid+' overview classification');
  }
  env.dom.window.close();
  // The research map must use the same four functions and stable Idea identities.
  env=await load('research-map.html');({w,d}=env);
  const mapGroups=[...d.querySelectorAll('.rm-group')];
  assert.deepEqual(mapGroups.map(e=>e.dataset.function),functions,'Map functions must match the canonical taxonomy');
  assert.equal(mapGroups.length,4,'Map has exactly four primary functions');
  assert.equal(d.querySelectorAll('.rm-idea').length,Object.keys(taxonomy.ideas).length,'Map retains every stable Idea');
  for(const [iid,idea] of Object.entries(taxonomy.ideas)){
    const link=[...d.querySelectorAll('.rm-idea')].find(e=>e.querySelector('.rm-idea-id').textContent===iid);
    assert(link,'Missing map Idea '+iid);
    assert.equal(link.closest('.rm-group').dataset.function,idea.primary,iid+' map classification');
    assert.equal(link.getAttribute('href'),idea.href,iid+' map destination');
  }
  for(const f of functions){
    select(w,d,'rm-function',f);
    assert.deepEqual(visible(d,'.rm-group').map(e=>e.dataset.function),[f],'Map function filter '+f);
    assert.equal(new URL(w.location.href).searchParams.get('function'),f,'Map selection persists in URL');
  }
  select(w,d,'rm-function','all');
  d.getElementById('rm-collapse').click();assert(mapGroups.every(e=>!e.open),'Map collapses all visible functions');
  d.getElementById('rm-expand').click();assert(mapGroups.every(e=>e.open),'Map expands all visible functions');
  // Search reveals a collapsed match and restores the earlier fold state when cleared.
  d.getElementById('rm-collapse').click();
  input(w,d,'rm-search','I14');
  assert.deepEqual(visible(d,'.rm-group').map(e=>e.dataset.function),[taxonomy.ideas.I14.primary],'Map finds I14 in its primary function');
  assert(visible(d,'.rm-group')[0].open,'Map opens a matched group during search');
  assert.deepEqual(visible(d,'.rm-idea').map(e=>e.querySelector('.rm-idea-id').textContent),['I14'],'Map search hides nonmatching Ideas');
  assert.equal(new URL(w.location.href).searchParams.get('q'),'I14','Map query persists in URL');
  input(w,d,'rm-search','');assert(mapGroups.every(e=>!e.open),'Clearing search restores prior folds');
  d.getElementById('rm-expand').click();
  const firstPaper=d.querySelector('.rm-paper'),paperTitle=firstPaper.querySelector('a').textContent.replace(/\s*↗\s*$/,'').trim();
  input(w,d,'rm-search',paperTitle);
  assert(!firstPaper.hidden&&!firstPaper.closest('.rm-group').hidden,'Map search finds a representative paper by title');
  assert(d.getElementById('rm-result').textContent.includes('找到'),'Map announces search results');
  input(w,d,'rm-search','I14');select(w,d,'rm-function','experience');
  assert.equal(visible(d,'.rm-group').length,0,'Map combines query and function filters');
  assert.equal(d.getElementById('rm-empty').hidden,false,'Map shows empty state for conflicting filters');
  d.querySelector('#rm-empty [data-map-reset]').click();
  assert.equal(visible(d,'.rm-group').length,4,'Empty-state reset restores every function');
  assert.equal(d.getElementById('rm-function').value,'all');assert.equal(d.getElementById('rm-search').value,'');
  assert.equal(d.getElementById('rm-empty').hidden,true);
  assert.equal(new URL(w.location.href).searchParams.get('function'),null);assert.equal(new URL(w.location.href).searchParams.get('q'),null);
  input(w,d,'rm-search','no_such_map_entry_20261029');
  assert.equal(visible(d,'.rm-group').length,0);assert.equal(d.getElementById('rm-empty').hidden,false);
  d.getElementById('rm-reset').click();assert.equal(visible(d,'.rm-group').length,4,'Toolbar reset restores map');
  // jsdom has no rendering media environment; supply only the API used by scroll behavior.
  w.matchMedia=media=>({matches:true,media});
  d.querySelector('[data-map-select="signal"]').click();
  assert.equal(d.getElementById('rm-function').value,'signal');
  assert.deepEqual(visible(d,'.rm-group').map(e=>e.dataset.function),['signal'],'Function index updates filter');
  assert(visible(d,'.rm-group')[0].open,'Function index opens its target');
  assert.equal(d.querySelector('[data-map-select="signal"]').getAttribute('aria-current'),'true');
  const outlineReset=d.querySelector('.rm-outline [data-map-reset]');
  if(outlineReset) outlineReset.click(); else d.getElementById('rm-reset').click();
  assert.equal(visible(d,'.rm-group').length,4,'Chapter outline or toolbar clears filtering');
  assert.deepEqual(env.errors,[],'Map interaction runtime errors');env.dom.window.close();
  env=await load('research-map.html?function=regulation&q=I14');({w,d}=env);
  assert.equal(d.getElementById('rm-function').value,'regulation');assert.equal(d.getElementById('rm-search').value,'I14');
  assert.deepEqual(visible(d,'.rm-group').map(e=>e.dataset.function),['regulation'],'Map restores function and query from URL');
  assert.deepEqual(visible(d,'.rm-idea').map(e=>e.querySelector('.rm-idea-id').textContent),['I14']);
  w.history.replaceState(null,'','research-map.html?function=experience');w.dispatchEvent(new w.PopStateEvent('popstate'));
  assert.equal(d.getElementById('rm-search').value,'','History restoration clears the old query');
  assert.deepEqual(visible(d,'.rm-group').map(e=>e.dataset.function),['experience'],'Map restores history state');
  assert.deepEqual(env.errors,[],'Map URL restoration runtime errors');env.dom.window.close();
  env=await load('research-map.html?function=unknown_function');({w,d}=env);
  assert.equal(d.getElementById('rm-function').value,'all');assert.equal(visible(d,'.rm-group').length,4,'Unknown URL function falls back to all');
  env.dom.window.close();
  env=await load('timeline.html');({w,d}=env);
  const events=[...d.querySelectorAll('.rsi-tl-item')];
  for(const f of functions){
    select(w,d,'rsi-tl-function',f);
    assert.equal(visible(d,'.rsi-tl-item').length,events.filter(e=>(e.dataset.functions||'').split('|').includes(f)).length,'Timeline '+f);
  }
  d.getElementById('rsi-tl-reset').click();assert.equal(visible(d,'.rsi-tl-item').length,events.length);
  const dayRows=[...d.querySelectorAll('tr.rsi-rt-day[data-day]')];
  assert.equal(dayRows.length,new Set(events.map(e=>e.dataset.date)).size,'Timeline retains one table row per research day');
  assert(d.querySelector('.rsi-summary-tags span'),'Timeline retains summary tags');
  assert(d.querySelector('.rt-week-summary-row'),'Timeline retains weekly summaries');
  d.getElementById('rsi-tl-collapse-all').click();
  assert([...d.querySelectorAll('.rsi-tl-month')].every(e=>!e.open));
  assert(dayRows.every(e=>e.getAttribute('aria-expanded')==='false'),'Collapse all updates day-row accessibility state');
  assert([...d.querySelectorAll('tr[data-day-detail]')].every(e=>e.hidden),'Collapse all hides day detail rows');
  d.getElementById('rsi-tl-expand-all').click();
  assert([...d.querySelectorAll('.rsi-tl-month')].every(e=>e.open));
  assert(dayRows.every(e=>e.getAttribute('aria-expanded')==='true'),'Expand all updates day-row accessibility state');
  assert([...d.querySelectorAll('tr[data-day-detail]')].every(e=>!e.hidden),'Expand all reveals day detail rows');
  const firstDay=dayRows[0],firstDetail=d.getElementById(firstDay.getAttribute('aria-controls'));
  firstDay.querySelector('.rt-day-toggle').click();
  assert.equal(firstDay.getAttribute('aria-expanded'),'false');assert(firstDetail.hidden,'Individual toggle hides its detail row');
  firstDay.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
  assert.equal(firstDay.getAttribute('aria-expanded'),'true');assert(!firstDetail.hidden,'Keyboard Enter reopens a day');
  assert.equal(firstDay.querySelector('.rt-day-toggle').getAttribute('aria-expanded'),'true','Day button stays synchronized');
  const calendar=d.getElementById('rsi-tl-calendar-grid'),calendarMode=d.getElementById('rsi-tl-calendar-mode');
  assert.equal(calendar.dataset.calendarView,'activity');assert.equal(calendarMode.getAttribute('aria-pressed'),'false');
  const activityDayCount=calendar.querySelectorAll('.rsi-tl-cal-day').length;
  calendarMode.click();
  assert.equal(calendar.dataset.calendarView,'full');assert.equal(calendarMode.getAttribute('aria-pressed'),'true');
  for(const month of calendar.querySelectorAll('[data-calendar-month]')){
    const [year,number]=month.dataset.calendarMonth.split('-').map(Number);
    assert.equal(month.querySelectorAll('.rsi-tl-cal-day').length,new Date(Date.UTC(year,number,0)).getUTCDate(),'Full calendar shows every date in '+month.dataset.calendarMonth);
  }
  assert(calendar.querySelectorAll('.rsi-tl-cal-day').length>activityDayCount,'Full calendar includes dates outside recorded activity ranges');
  calendarMode.click();
  assert.equal(calendar.dataset.calendarView,'activity');assert.equal(calendarMode.getAttribute('aria-pressed'),'false');
  assert.equal(calendar.querySelectorAll('.rsi-tl-cal-day').length,activityDayCount,'Calendar switches back to recorded date ranges');
  assert.equal(visible(d,'.rsi-tl-item').length,events.length,'Calendar display mode preserves event filters');
  assert.deepEqual(env.errors,[],'Timeline table and calendar interaction errors');
  const clock=d.querySelector('#rsi-rt-next-countdown')||d.querySelector('[data-countdown]');
  assert(clock,'Timeline must expose at least one countdown');
  const before=clock.textContent;
  await new Promise(resolve=>setTimeout(resolve,1150));
  if(before.includes('秒'))assert.notEqual(clock.textContent,before,'Live countdown must tick');
  env.dom.window.close();
  env=await load('index.html');({w,d}=env);
  const navCount=d.querySelectorAll('#research-nav .nav-level2').length;
  d.getElementById('nav-language').click();assert.equal(d.querySelectorAll('#research-nav .nav-level2').length,navCount);
  d.getElementById('menu-toggle').click();assert.equal(d.getElementById('menu-toggle').getAttribute('aria-expanded'),'true');
  d.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));assert.equal(d.getElementById('menu-toggle').getAttribute('aria-expanded'),'false');
  input(w,d,'research-search','学习调控');await new Promise(resolve=>setTimeout(resolve,20));
  assert(d.querySelectorAll('#search-results .search-hit').length>0,'Search should include functional taxonomy');
  env.dom.window.close();
  // Every page executes its own scripts against its actual generated DOM.
  const pages=fs.readdirSync(SITE).filter(f=>f.endsWith('.html'));
  for(const filename of pages){
    const page=await load(filename);
    assert.equal(page.d.querySelectorAll('h1').length,1,filename+' H1');
    assert.equal(page.d.querySelectorAll('#research-nav a[aria-current="page"]').length,1,filename+' navigation');
    assert.equal(page.d.querySelectorAll('#research-nav details.nav-group').length,7,filename+' groups');
    assert.deepEqual(page.errors,[],filename+' script errors');
    page.dom.window.close();
  }
  console.log(JSON.stringify({status:'PASS',pages:pages.length,papers:papers.length,sources:sources.length,
    checks:['four-function paper filters','source filters','stable Idea anchors','map canonical functions and Ideas','map search and combined filters','map empty state and reset','map folding and index navigation','map URL and history restoration','timeline filters','timeline day-row folding','timeline full-calendar toggle','folding','live countdown','navigation language','mobile menu state','local search','all-page script execution'],
    limitation:'DOM checks do not measure visual layout or screenshots'},null,2));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
