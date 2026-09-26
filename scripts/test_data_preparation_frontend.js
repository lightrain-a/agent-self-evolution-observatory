/* Deterministic UI behavior checks; not a substitute for actual-size visual review. */
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
async function main(){
  const nodes={'prep-main':{innerHTML:''},'prep-language':{},'shape-filter':{}};
  const doc={getElementById:id=>nodes[id],querySelectorAll:()=>[],documentElement:{}};
  const box={window:{},document:doc};vm.createContext(box);
  for(const p of ['generated/experiment-data-preparation.js','generated/data-preparation-demo.js','data-preparation-view.js'])vm.runInContext(read(p),box);
  assert(nodes['prep-main'].innerHTML.includes('实验数据准备'));
  assert.equal((nodes['prep-main'].innerHTML.match(/class="type-card"/g)||[]).length,19);
  assert.equal((nodes['prep-main'].innerHTML.match(/<img /g)||[]).length,12);
  nodes['prep-language'].onclick();assert.equal(doc.documentElement.lang,'en');
  assert(nodes['prep-main'].innerHTML.includes('Prepare the evidence'));
  const meta=JSON.parse(read('generated/data-preparation-demo.json')),html=read(meta.url);
  const bundle=JSON.parse(html.match(/<script id="bundle-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
  const code=html.match(/<script>([\s\S]*?)<\/script><\/body>/)[1];
  const controls={},storage={};let exported;
  for(const c of bundle.candidates){
    controls['[data-candidate="'+c.id+'"]']={value:'',addEventListener(name,fn){this[name]=fn}};
    controls['[data-note="'+c.id+'"]']={value:'',addEventListener(name,fn){this[name]=fn}};
  }
  const demoNodes={'bundle-data':{textContent:JSON.stringify(bundle)},'save-state':{},'export-feedback':{}};
  const demo={document:{getElementById:id=>demoNodes[id],querySelector:q=>controls[q],createElement:()=>({click(){}})},
    localStorage:{getItem:k=>storage[k],setItem:(k,v)=>storage[k]=v},
    URL:{createObjectURL:b=>{exported=b;return 'blob:test'},revokeObjectURL:()=>{}},Blob,setTimeout:fn=>fn()};
  vm.createContext(demo);vm.runInContext(code,demo);
  const id=bundle.candidates[0].id,s=controls['[data-candidate="'+id+'"]'];s.value='KEEP';s.change();
  const n=controls['[data-note="'+id+'"]'];n.value='Keep data, move legend';n.input();
  assert(demoNodes['save-state'].textContent.includes('尚未写服务器'));
  demoNodes['export-feedback'].onclick();const feedback=JSON.parse(await exported.text());
  assert.equal(feedback.events.length,1);assert.equal(feedback.events[0].action,'KEEP');
  assert.equal(feedback.snapshot_sha256,bundle.snapshot_sha256);
  assert.equal(feedback.origin,'BROWSER_DRAFT_NOT_SERVER_ACCEPTED');
  assert.equal(feedback.events[0].note,'Keep data, move legend');
  console.log('PASS: bilingual page, 19 types, 12 previews, local draft, version-bound feedback export');
}
main().catch(e=>{console.error(e);process.exitCode=1});
