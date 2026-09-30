const fs=require('fs'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..');
const data=fs.readFileSync(path.join(root,'data.js'),'utf8');
for(const page of ['experiment-data-preparation.html','figure-knowledge-base.html','paper-writing-workflow.html']){
  assert(data.includes(page), 'missing nav page '+page);
  assert(fs.existsSync(path.join(root,page)), 'missing page '+page);
}
const gallery=fs.readFileSync(path.join(root,'figure-gallery.html'),'utf8');
assert(gallery.includes('figure-knowledge-base.html'));
const prep=fs.readFileSync(path.join(root,'data-preparation-view.js'),'utf8');
assert(prep.includes('yjz211/vivid-figures-skill'));
assert(prep.includes('ChenLiu-1996/figures4papers'));
console.log('PASS: homepage nav exposes paper production; legacy figure-gallery aliases full knowledge base; both figure repos remain source-linked');
