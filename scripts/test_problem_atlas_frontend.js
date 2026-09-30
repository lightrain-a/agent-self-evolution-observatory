/* Published contract checks; browser interactions are tested separately. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const site = fs.existsSync(path.join(root, '_site')) ? path.join(root, '_site') : root;
const read = p => fs.readFileSync(path.join(site, p), 'utf8');
const data = JSON.parse(read('generated/agent-safety-atlas.json'));
assert.equal(data.problems.length, 24);
assert.equal(data.themes.length, 8);
assert.equal(data.sources.filter(s=>s.kind==='paper').length, 14);
assert.equal(data.human_workflow.problem_confirmation, false);
assert.equal(data.human_workflow.solution_confirmation, false);
assert.equal(data.human_workflow.experiment_count, 0);
const ids = new Set(data.sources.map(s=>s.id));
for (const p of data.problems) {
  assert.ok(p.example && p.why_it_matters && p.existing_progress && p.open_question);
  assert.ok(p.source_refs.every(id=>ids.has(id)));
  assert.equal(p.human_confirmed, false);
}
const html = read('agent-safety-atlas.html');
for (const text of ['主题地图','逐项阅读','证据覆盖','并排比较','复制给聊天确认','不是服务器确认']) assert.ok(html.includes(text), text);
for (const name of ['agent-safety-atlas.css','agent-safety-atlas.js']) assert.ok(fs.existsSync(path.join(site,name)));
assert.ok(read('data.js').includes('agent-safety-atlas.html'));
assert.ok(read('skill-security-research.html').includes('agent-safety-atlas.html'));
const script = read('agent-safety-atlas.js');
assert.ok(script.includes('REVIEW_DRAFT_NOT_CONFIRMATION'));
assert.ok(script.includes('saved?.revision===data.revision'));
assert.ok(!script.includes('method: \'POST\''));
console.log('PASS problem-atlas public reading contract: 24 problems, 8 themes, 18 sources; zero confirmations and experiments');
