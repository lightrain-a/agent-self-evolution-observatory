/* Progressive enhancement: all content and anchors work without JavaScript. */
(() => {
  'use strict';
  let activeController;
  function initialize() {
  // Rebind page-specific controls after a soft navigation. Global listeners
  // from the previous page must never accumulate across visits.
  activeController?.abort();
  activeController=new AbortController();
  const params=new URLSearchParams(location.search);
  function revealTarget(){
    if(!location.hash)return;
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
    const target=document.getElementById(id);
    if(!target)return;
    for(let node=target;node;node=node.parentElement){
      if(node.tagName==='DETAILS')node.open=true;
    }
  }
  revealTarget();addEventListener('hashchange',revealTarget,{signal:activeController.signal});
  const query=document.querySelector('#reference-query');
  const scope=document.querySelector('#reference-function');
  if(query&&scope){
    const cards=[...document.querySelectorAll('.source-card')];
    const count=document.querySelector('#reference-count');
    const requested=params.get('function');
    if([...scope.options].some(o=>o.value===requested))scope.value=requested;
    const refresh=()=>{
      const terms=query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
      let shown=0;
      for(const card of cards){
        const visible=(scope.value==='all'||card.dataset.primaryFunction===scope.value)&&terms.every(t=>card.textContent.toLocaleLowerCase().includes(t));
        card.hidden=!visible;if(visible)shown++;
      }
      for(const section of document.querySelectorAll('.research-section[id^="function-"]')){
        section.hidden=![...section.querySelectorAll('.source-card')].some(c=>!c.hidden);
      }
      count.textContent='显示 '+shown+' / '+cards.length+' 项';
    };
    query.addEventListener('input',refresh);scope.addEventListener('change',refresh);refresh();
    const showSource=()=>{
      let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
      const target=document.getElementById(id);
      if(target?.classList.contains('source-card')&&target.hidden){scope.value='all';query.value='';refresh();}
    };
    showSource();addEventListener('hashchange',showSource,{signal:activeController.signal});
  }
  const readingQuery=document.querySelector('#reading-card-filter');
  const readingFunction=document.querySelector('#reading-function-filter');
  const readingRelation=document.querySelector('#reading-relation-filter');
  if(readingQuery&&readingFunction){
    const cards=[...document.querySelectorAll('.reading-card')];
    const requested=params.get('function');
    if([...readingFunction.options].some(o=>o.value===requested))readingFunction.value=requested;
    const refresh=()=>{
      const terms=readingQuery.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const f=readingFunction.value,relation=readingRelation.value;
      let shown=0;
      cards.forEach(card=>{
        const primary=card.dataset.primaryFunction;
        const related=(card.dataset.relatedFunctions||'').split('|');
        const matching=f==='all'||(relation==='primary'?primary===f:relation==='related'?related.includes(f):primary===f||related.includes(f));
        card.hidden=!(matching&&terms.every(t=>card.textContent.toLocaleLowerCase().includes(t)));
        if(!card.hidden)shown++;
      });
      document.querySelector('#reading-card-count').textContent='显示 '+shown+' / '+cards.length+' 篇';
      document.querySelector('#reading-empty').hidden=shown!==0;
    };
    readingQuery.addEventListener('input',refresh);
    readingFunction.addEventListener('change',refresh);
    readingRelation.addEventListener('change',refresh);refresh();
    const showCard=()=>{
      let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
      const target=document.getElementById(id);
      if(target?.classList.contains('reading-card')&&target.hidden){readingFunction.value='all';readingQuery.value='';refresh();}
    };
    showCard();addEventListener('hashchange',showCard,{signal:activeController.signal});
  }
  }
  window.RSIFrameworkInitialize=initialize;
  window.RSIFrameworkCleanup=()=>{activeController?.abort();activeController=null;};
  initialize();
})();
