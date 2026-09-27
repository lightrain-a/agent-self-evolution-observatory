/* Public survey behavior only. No private research or upstream code is loaded. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ROOT=path.resolve(__dirname,'..');
const state=JSON.parse(fs.readFileSync(path.join(ROOT,'generated/skill-security-round1.json'),'utf8'));
const nodes={'skill-security-main':{innerHTML:''},'security-query':{value:'',tagName:'INPUT',events:{},addEventListener(k,f){this.events[k]=f}},'security-stage':{value:'',tagName:'SELECT',events:{},addEventListener(k,f){this.events[k]=f}},'security-kind':{value:'',tagName:'SELECT',events:{},addEventListener(k,f){this.events[k]=f}},'security-count':{textContent:''}};
const cards=state.sources.map(s=>({dataset:{sourceId:s.id},hidden:false}));
const context={window:{SKILL_SECURITY_ROUND1:state},document:{getElementById:id=>nodes[id],querySelectorAll:()=>cards}};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(ROOT,'skill-security-research.js'),'utf8'),context);
assert.equal(state.sources.length,39);assert.equal(state.surfaces.length,12);
assert.equal(cards.filter(c=>!c.hidden).length,39);
nodes['security-kind'].value='PAPER';nodes['security-kind'].events.change();assert.equal(cards.filter(c=>!c.hidden).length,24);
nodes['security-query'].value='ClosureBound';nodes['security-query'].events.input();assert.equal(cards.filter(c=>!c.hidden).length,1);
nodes['security-query'].value='';nodes['security-kind'].value='';nodes['security-stage'].value='secrets';nodes['security-stage'].events.change();assert(cards.some(c=>!c.hidden));
assert(!nodes['skill-security-main'].innerHTML.includes('SS-R1-01'));assert(!nodes['skill-security-main'].innerHTML.includes('PRIVATE_SENTINEL'));
assert(nodes['skill-security-main'].innerHTML.includes('未发表Idea'));
assert.equal(state.summary.reproduced_vulnerabilities,0);assert.equal(state.private_candidates.published,false);
console.log('PASS: 39 sources, 24 papers, 12 surfaces, source/stage search, zero reproduction claims, no private candidate details');
