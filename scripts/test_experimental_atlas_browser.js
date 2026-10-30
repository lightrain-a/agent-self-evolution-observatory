#!/usr/bin/env node
/* Local-only browser test. Uses installed Chromium + ws; does not install software. */
'use strict';
const fs=require('fs'),path=require('path'),os=require('os'),http=require('http');
const {spawn}=require('child_process');
const WebSocket=require('ws');
const ROOT=path.resolve(__dirname,'..');
const SITE=path.join(ROOT,'_site');
let browser,server,ws,profile;
function cleanup(){
  if(ws)try{ws.close()}catch{}
  if(browser)try{process.kill(-browser.pid,'SIGKILL')}catch{}
  if(server)try{server.close()}catch{}
  if(profile)try{fs.rmSync(profile,{recursive:true,force:true})}catch{}
}
process.on('SIGTERM',()=>{cleanup();process.exit(143)});
const watchdog=setTimeout(()=>{console.error('Browser test deadline exceeded');cleanup();process.exit(1)},55000);
async function port(){const s=http.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p;}
async function main(){
  const cache=path.join(os.homedir(),'.cache','ms-playwright');
  const candidates=fs.existsSync(cache)?fs.readdirSync(cache).filter(x=>x.startsWith('chromium-')).sort().reverse().map(x=>path.join(cache,x,'chrome-linux','chrome')):[];
  const chrome=process.env.RSI_CHROME||candidates.find(x=>fs.existsSync(x));
  if(!chrome)throw Error('Set RSI_CHROME to an installed Chromium executable');
  server=http.createServer((req,res)=>{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=path.resolve(SITE,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
    if(!file.startsWith(SITE+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end('not found');return;}
    res.setHeader('Content-Type',({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const origin='http://127.0.0.1:'+server.address().port;
  const debug=await port();profile=fs.mkdtempSync(path.join(os.tmpdir(),'rsi-atlas-chrome-'));
  browser=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--no-first-run','--remote-debugging-address=127.0.0.1','--remote-debugging-port='+debug,'--user-data-dir='+profile,'about:blank'],{detached:true,stdio:'ignore'});
  let pages;
  for(let i=0;i<80;i++){try{pages=await (await fetch('http://127.0.0.1:'+debug+'/json/list')).json();if(pages[0])break;}catch{}await new Promise(r=>setTimeout(r,100));}
  if(!pages?.[0])throw Error('Chromium did not start');
  ws=new WebSocket(pages[0].webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.once('open',resolve);ws.once('error',reject)});
  let id=0;const pending=new Map(),exceptions=[];
  ws.on('message',raw=>{const x=JSON.parse(raw);if(x.method==='Runtime.exceptionThrown')exceptions.push(x.params.exceptionDetails.text);const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.timer);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}});
  function rpc(method,params={}){return new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>{pending.delete(n);reject(Error('CDP timeout '+method))},8000);pending.set(n,{resolve,reject,timer});ws.send(JSON.stringify({id:n,method,params}));})}
  async function ev(expression){const x=await rpc('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(x.exceptionDetails)throw Error(JSON.stringify(x.exceptionDetails));return x.result.value;}
  async function wait(expression){for(let i=0;i<70;i++){if(await ev(expression))return;await new Promise(r=>setTimeout(r,80));}throw Error('Wait failed: '+expression);}
  function assert(x,msg){if(!x)throw Error(msg);}
  await rpc('Runtime.enable');await rpc('Page.enable');
  await rpc('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
  await rpc('Page.navigate',{url:origin+'/rsi/experimental-atlas.html'});
  await wait("document.querySelector('#experimental-atlas-app')?.dataset.atlasReady==='true'");
  const count="document.querySelectorAll('[data-atlas-panel]:not([hidden]) [data-atlas-item]:not([hidden])').length";
  assert(await ev(count)===54,'initial dataset count');
  await ev("document.querySelector('#atlas-search').value='LoCoMo';document.querySelector('#atlas-search').dispatchEvent(new Event('input'))");
  assert(await ev(count)===1,'dataset search');
  await ev("document.querySelector('#dataset-locomo details').open=true;document.querySelector('#dataset-locomo [data-record-target=\"W16\"]').click()");
  assert(await ev("document.querySelector('#record-W16 details').open"),'dataset to paper');
  await ev("document.querySelector('#record-W16 [data-dataset-target=\"locomo\"]').click()");
  assert(await ev("document.querySelector('#dataset-locomo details').open"),'paper to dataset');
  await ev("document.querySelector('[data-atlas-question=\"judge\"]').click()");
  const filtered=await ev(count);assert(filtered>0&&filtered<54,'question filter');
  await ev("document.querySelector('#atlas-search').value='not-a-real-resource-987';document.querySelector('#atlas-search').dispatchEvent(new Event('input'))");
  assert(await ev(count)===0&&await ev("!document.querySelector('#atlas-empty').hidden"),'empty state');
  await ev("document.querySelector('#atlas-reset').click();document.querySelector('[data-atlas-view=\"metric\"]').click()");
  assert(await ev(count)===64,'metric view');
  await ev("document.querySelector('#atlas-search').value='遗忘';document.querySelector('#atlas-search').dispatchEvent(new Event('input'))");
  assert(await ev(count)>0,'Chinese search aliases');
  await ev("document.querySelector('[data-atlas-view=\"control\"]').click()");assert(await ev(count)===18,'control view');
  await ev("document.querySelector('[data-atlas-view=\"family\"]').click()");assert(await ev(count)===38,'family view');
  await ev("document.querySelector('[data-atlas-view=\"paper\"]').click()");assert(await ev(count)===60,'paper view');
  await ev("document.querySelector('#research-nav a[href=\"evidence.html\"]').click()");
  await wait("document.body.dataset.rsiPage==='evidence'");
  await ev('history.back()');
  await wait("document.body.dataset.rsiPage==='experimental-atlas' && document.querySelector('#experimental-atlas-app')?.dataset.atlasReady==='true'");
  assert(await ev(count)===60,'soft-navigation back restores view');
  await ev("document.querySelector('[data-atlas-view=\"datasets\"]').click();window.scrollTo(0,0)");
  await new Promise(r=>setTimeout(r,350));
  let shot=await rpc('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(ROOT,'atlas-browser-desktop.png'),Buffer.from(shot.data,'base64'));
  await rpc('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await ev('window.scrollTo(0,0)');await new Promise(r=>setTimeout(r,200));
  assert(await ev('document.documentElement.scrollWidth<=innerWidth+1'),'mobile horizontal overflow');
  shot=await rpc('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(ROOT,'atlas-browser-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(exceptions.length===0,'Uncaught browser exception: '+exceptions.join('; '));
  console.log('PASS browser: dataset/question search, reverse links, 5 views, Chinese aliases, empty state, soft navigation/back, desktop/mobile bounds; no uncaught exceptions.');
}
main().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(()=>{clearTimeout(watchdog);cleanup()});
