/* Functional page checks, not a claim of PDF or scientific review. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ROOT=path.resolve(__dirname,'..');
const state=JSON.parse(fs.readFileSync(path.join(ROOT,'generated/paper-writing-workflow.json'),'utf8'));
const nodes={'writing-main':{innerHTML:''},'writing-lang':{}};
const box={window:{PAPER_WRITING_WORKFLOW:state},document:{getElementById:id=>nodes[id],documentElement:{}}};
vm.createContext(box);vm.runInContext(fs.readFileSync(path.join(ROOT,'paper-writing-workflow.js'),'utf8'),box);
assert.equal(state.stages.length,10);assert.equal(Object.keys(state.section_roles).length,9);assert.equal(Object.keys(state.modes).length,7);
assert(nodes['writing-main'].innerHTML.includes('为什么这个问题值得研究'));
assert(nodes['writing-main'].innerHTML.includes('experiment-data-preparation.html'));
assert(nodes['writing-main'].innerHTML.includes('figure-knowledge-base.html'));
assert(!/<details[^>]*\bopen\b/.test(nodes['writing-main'].innerHTML));
nodes['writing-lang'].onclick();assert.equal(box.document.documentElement.lang,'en');
assert(nodes['writing-main'].innerHTML.includes('Writing papers from evidence'));
assert.equal(state.boundaries.live_heirs_rewritten,false);
console.log('PASS: writing workflow, section roles, figure/table links, scoped tasks and explicit review boundaries');
