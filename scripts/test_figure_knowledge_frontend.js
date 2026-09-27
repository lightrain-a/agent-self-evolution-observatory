/* Test complete rendering/filtering/export behavior without fetching upstream images. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ROOT=path.resolve(__dirname,'..');
const kb=JSON.parse(fs.readFileSync(path.join(ROOT,'generated/figure-knowledge-base.json'),'utf8'));
const names=['kb-error','kb-grid','kb-search','kb-source','kb-family','kb-data','kb-kind','kb-preview-only','kb-favorites-only','kb-result-count','kb-page-count','kb-more','kb-show-all','kb-export','kb-clear','kb-title','kb-intro','kb-metrics','kb-annotation-note','kb-boundary','kb-storage','kb-family-guide','kb-coverage-body','kb-close','kb-detail','kb-detail-body','language-toggle'];
const nodes=Object.fromEntries(names.map(id=>[id,{value:'',checked:false,hidden:false,innerHTML:'',textContent:'',open:false,events:{},addEventListener(k,f){this.events[k]=f},querySelectorAll(){return []},focus(){},showModal(){this.open=true},close(){this.open=false}}]));
const storage={};let exported,clickHandler;let currentUrl='https://agent-evolution.lightrain.asia/figure-knowledge-base.html';
class ExportURL extends URL {static createObjectURL(blob){exported=blob;return 'blob:fixture'}static revokeObjectURL(){}}
const context={window:{FIGURE_KNOWLEDGE_BASE:kb},document:{getElementById:id=>nodes[id],querySelectorAll:()=>[],documentElement:{},addEventListener:(name,f)=>{if(name==='click')clickHandler=f},createElement:()=>({click(){}})},localStorage:{getItem:k=>storage[k],setItem:(k,v)=>storage[k]=v},URL:ExportURL,Blob,location:{get href(){return currentUrl}},history:{replaceState:(_,__,url)=>{currentUrl=url}},setTimeout:fn=>{fn();return 1},clearTimeout(){},console};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(ROOT,'figure-knowledge-base.js'),'utf8'),context);
const count=()=> (nodes['kb-grid'].innerHTML.match(/<article class="card/g)||[]).length;
assert.equal(count(),48);assert.equal(context.window.figureKnowledgeUI.getFiltered().length,kb.entries.length);
nodes['kb-show-all'].onclick();assert.equal(count(),kb.entries.length);
nodes['kb-source'].value='vivid';nodes['kb-source'].events.change();
assert.equal(context.window.figureKnowledgeUI.getFiltered().length,kb.entries.filter(e=>e.source_id==='vivid').length);
nodes['kb-family'].value='shap';nodes['kb-family'].events.change();
assert(context.window.figureKnowledgeUI.getFiltered().length>0);
assert(context.window.figureKnowledgeUI.getFiltered().every(id=>kb.entries.find(e=>e.id===id).families.includes('shap')));
nodes['kb-clear'].onclick();nodes['kb-search'].value='雨云';nodes['kb-search'].events.input();assert(context.window.figureKnowledgeUI.getFiltered().length>0);
const chosen=context.window.figureKnowledgeUI.getFiltered()[0];
clickHandler({target:{closest:selector=>selector==='[data-star]'?{dataset:{star:chosen}}:null}});
assert(nodes['kb-export'].textContent.includes('1'));
nodes['kb-export'].onclick();
exported.text().then(text=>{
 const brief=JSON.parse(text);assert.equal(brief.entries.length,1);assert.equal(brief.entries[0].entry_id,chosen);
 assert(brief.entries[0].selection_current);assert(brief.entries[0].families[0].required_fields.length);assert(brief.entries[0].license);
 assert.equal(brief.scientific_authority,false);assert.equal(brief.origin,'BROWSER_SHORTLIST_NOT_SERVER_APPROVAL');
 nodes['language-toggle'].onclick();assert.equal(context.document.documentElement.lang,'en');
 assert(!nodes['kb-grid'].innerHTML.includes('undefined'));
 console.log(JSON.stringify({status:'PASS',full_entries:kb.entries.length,default_cards:48,show_all:true,repository_and_family_filters:true,chinese_search:true,shortlist_export:true,bilingual:true,upstream_image_network_tested:false}));
}).catch(e=>{console.error(e);process.exitCode=1});
