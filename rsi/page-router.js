/* RSI soft navigation — progressive enhancement of the existing static website.
 *
 * A navigation keeps the old document, sidebar, search bar and article visible
 * until the next page is fully fetched. Only the article/TOC/footer change.
 * The canonical HTML pages remain independent, linkable and usable without JS.
 * Errors fall back to native navigation; external links and downloads stay native.
 */
(() => {
  'use strict';
  if (!document.body.dataset.rsiPage || !window.fetch || !window.DOMParser ||
      !window.history?.pushState || !document.querySelector('#research-main .content')) return;

  const cache = new Map();
  const maxCachedPages = 3;
  let sequence = 0;
  let inFlight = false;
  let loadingTimeout = 0;
  let currentController = null;
  let lastPath = location.pathname;

  const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = () => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    return Boolean(connection?.saveData || /2g/.test(connection?.effectiveType || '') ||
      matchMedia('(prefers-reduced-data: reduce)').matches);
  };
  const normalizedURL = (href) => {
    let next;
    try { next = new URL(href, location.href); } catch (_) { return null; }
    if (next.origin !== location.origin || !/^\/rsi\/(?:[a-z0-9-]+\.html)?$/.test(next.pathname)) return null;
    return next;
  };
  const documentKey = (url) => (url.pathname === '/rsi/' ? '/rsi/index.html' : url.pathname) + url.search;

  function fetchDocument(url) {
    const key = documentKey(url);
    if (cache.has(key)) return cache.get(key);
    const task = fetch(key, {
      credentials:'same-origin',
      headers:{Accept:'text/html'}
    }).then((response) => {
      if (!response.ok || !response.headers.get('content-type')?.includes('text/html')) {
        throw new Error('Document unavailable: ' + response.status);
      }
      return response.text();
    }).then((source) => {
      const doc = new DOMParser().parseFromString(source, 'text/html');
      if (!doc.body?.dataset.rsiPage ||
          !doc.querySelector('#research-main .content .research-hero') ||
          !doc.querySelector('#research-nav')) {
        throw new Error('Destination is not an RSI document');
      }
      return doc;
    }).catch((error) => {
      cache.delete(key);
      throw error;
    });
    cache.set(key, task);
    while (cache.size > maxCachedPages) {
      const first = cache.keys().next().value;
      cache.delete(first);
    }
    return task;
  }

  function prefetch(href) {
    if (saveData()) return;
    const url = normalizedURL(href);
    if (!url || documentKey(url) === documentKey(new URL(location.href))) return;
    // A hover is only a hint; failed requests must not throw into the UI.
    fetchDocument(url).catch(() => {});
  }

  async function ensureStyles(nextDoc) {
    const hrefs = [...nextDoc.querySelectorAll('link[rel="stylesheet"][href]')]
      .map((link) => new URL(link.getAttribute('href'), location.href))
      .filter((url) => url.origin === location.origin && /^\/rsi\/[a-z0-9-]+\.css$/.test(url.pathname));
    const known = new Set([...document.querySelectorAll('head link[rel="stylesheet"][href]')]
      .map((node) => new URL(node.getAttribute('href'), location.href).pathname));
    const additions = [];
    for (const url of hrefs) {
      if (known.has(url.pathname)) continue;
      known.add(url.pathname);
      const node = document.createElement('link');
      node.rel = 'stylesheet';
      node.href = url.href;
      additions.push(new Promise((resolve, reject) => {
        node.addEventListener('load', resolve, {once:true});
        node.addEventListener('error', () => reject(new Error('Stylesheet failed: '+url.pathname)), {once:true});
      }));
      document.head.append(node);
    }
    await Promise.all(additions);
  }

  async function initializePageScripts(nextDoc) {
    // framework.js is included on all RSI pages and initialized once at startup.
    // It exposes explicit rebind/cleanup for page-local filters and hash listeners.
    window.RSIFrameworkInitialize?.();
    const scripts = [...nextDoc.querySelectorAll('script[src]')]
      .map((node) => new URL(node.getAttribute('src'), location.href))
      .filter((url) => url.origin === location.origin &&
             /^\/rsi\/(?:research-map|timeline-view|experimental-atlas)\.js$/.test(url.pathname));
    for (const url of scripts) {
      await new Promise((resolve, reject) => {
        const node = document.createElement('script');
        node.src = url.href;
        node.async = false;
        node.onload = () => {node.remove(); resolve();};
        node.onerror = () => {node.remove(); reject(new Error('Script failed: '+url.pathname));};
        document.body.append(node);
      });
    }
  }

  function swapDocument(nextDoc) {
    const main = document.querySelector('#research-main');
    const currentContent = main.querySelector('.content');
    const sourceContent = nextDoc.querySelector('#research-main .content');
    const results = currentContent.querySelector('#search-results');
    const content = document.createDocumentFragment();
    // Keep the live search-results node: the persistent search bar's handlers
    // use it. Everything else comes directly from the reviewed static HTML.
    for (const node of [...sourceContent.children]) {
      if (node.id !== 'search-results') content.append(document.importNode(node, true));
    }
    currentContent.replaceChildren(results, content);
    const freshToc = nextDoc.querySelector('.sidebar .page-toc');
    const toc = document.querySelector('.sidebar .page-toc');
    if (toc && freshToc) toc.innerHTML = freshToc.innerHTML;
    const freshFooter = nextDoc.querySelector('#research-main > footer');
    const footer = main.querySelector(':scope > footer');
    if (footer && freshFooter) footer.innerHTML = freshFooter.innerHTML;

    for (const attr of [...document.body.attributes]) {
      if (attr.name.startsWith('data-')) document.body.removeAttribute(attr.name);
    }
    for (const attr of [...nextDoc.body.attributes]) {
      if (attr.name.startsWith('data-')) document.body.setAttribute(attr.name, attr.value);
    }
    document.title = nextDoc.title;
    const description = document.head.querySelector('meta[name="description"]');
    if (description) description.content = nextDoc.querySelector('meta[name="description"]')?.content || '';
    const canonical = document.head.querySelector('link[rel="canonical"]');
    if (canonical) canonical.href = nextDoc.querySelector('link[rel="canonical"]')?.href || location.href;
    window.RSIShellRefresh?.();
  }

  async function navigate(href, {restore=false, savedScroll=0}={}) {
    const url = normalizedURL(href);
    if (!url) { location.assign(href); return; }
    const id = ++sequence;
    // Leave the current page completely visible while the new HTML downloads.
    currentController?.abort();
    const controller = new AbortController();
    currentController = controller;
    clearTimeout(loadingTimeout);
    loadingTimeout = setTimeout(() => document.body.classList.add('rsi-soft-pending'), 170);
    inFlight = true;
    try {
      const doc = await fetchDocument(url);
      if (controller.signal.aborted || id !== sequence) return;
      await ensureStyles(doc);
      if (controller.signal.aborted || id !== sequence) return;

      if (!restore) {
        history.replaceState({...history.state, __rsiScrollY:scrollY}, '', location.href);
        history.pushState({__rsiSoftPage:true, __rsiScrollY:0}, '', url.href);
      }
      const update = async () => {
        if (controller.signal.aborted || id !== sequence) return;
        window.RSITimelineCleanup?.();
        window.RSIResearchMapCleanup?.();
        window.RSITimelineCleanup = null;
        window.RSIResearchMapCleanup = null;
        window.RSIFrameworkCleanup?.();
        swapDocument(doc);
        await initializePageScripts(doc);
        // Position the destination before its view-transition snapshot is
        // captured, not a frame afterward (which could reveal empty space).
        if (url.hash) {
          let fragment='';
          try {fragment=decodeURIComponent(url.hash.slice(1));} catch (_) {}
          const target=fragment && document.getElementById(fragment);
          if (target) {
            for (let p=target; p; p=p.parentElement) if (p.tagName==='DETAILS') p.open=true;
            target.scrollIntoView({block:'start',behavior:'instant'});
          } else window.scrollTo(0,0);
        } else {
          window.scrollTo({top:restore ? savedScroll : 0,behavior:'instant'});
        }
      };
      if (document.startViewTransition && !reducedMotion()) {
        const view = document.startViewTransition(update);
        await view.updateCallbackDone;
        // The transition animation is cosmetic and must never block the
        // visitor from interacting with the new research page.
      } else {
        await update();
      }
      if (controller.signal.aborted || id !== sequence) return;
      currentController = null;
      lastPath = location.pathname;
      const hash = url.hash;
      requestAnimationFrame(() => {
        if (hash) {
          let id = '';
          try {id = decodeURIComponent(hash.slice(1));} catch (_) {}
          const target = id && document.getElementById(id);
          if (target) {
            for (let item=target; item; item=item.parentElement) {
              if (item.tagName === 'DETAILS') item.open = true;
            }
            target.scrollIntoView({block:'start',behavior:'instant'});
          } else window.scrollTo(0,0);
        } else {
          window.scrollTo({top:restore ? savedScroll : 0,behavior:'instant'});
        }
        const heading = document.querySelector('.content h1');
        if (heading) {
          heading.tabIndex = -1;
          heading.focus({preventScroll:true});
        }
      });
      document.dispatchEvent(new CustomEvent('rsi:pagechange',{detail:{path:location.pathname}}));
    } catch (error) {
      if (!controller.signal.aborted && id === sequence) {
        // URL may already have changed; ordinary navigation remains a safe,
        // complete fallback if a static asset or page-local script fails.
        location.assign(url.href);
      }
    } finally {
      if (id === sequence) {
        inFlight = false;
        clearTimeout(loadingTimeout);
        document.body.classList.remove('rsi-soft-pending');
      }
    }
  }

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0 ||
        event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const anchor = event.target?.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download') ||
        (anchor.target && anchor.target !== '_self')) return;
    const url = normalizedURL(anchor.href);
    if (!url) return;
    // Same-document fragments use native behavior so no filter or scroll
    // semantics change. URLs outside RSI still use ordinary navigation.
    if (url.pathname === location.pathname && url.search === location.search) return;
    event.preventDefault();
    navigate(url.href);
  });

  window.addEventListener('popstate', (event) => {
    if (location.pathname === lastPath) return; // hash/query-only history
    navigate(location.href,{restore:true,savedScroll:event.state?.__rsiScrollY || 0});
  });
  // Avoid the browser restoring the old page's scroll position *after* the
  // asynchronously swapped page has already positioned its target anchor.
  history.scrollRestoration = 'manual';

  const status = document.createElement('span');
  status.className='sr-only';
  status.setAttribute('role','status');
  status.setAttribute('aria-live','polite');
  status.id='rsi-softnav-status';
  document.querySelector('.topbar')?.append(status);
  document.addEventListener('rsi:pagechange', () => {
    status.textContent = '已打开' + (document.querySelector('.content h1')?.textContent || '研究页面');
  });

  window.RSIPageRouter = {
    navigate, prefetch,
    isCached:(href)=>{const url=normalizedURL(href);return Boolean(url && cache.has(documentKey(url)));},
    get inFlight(){return inFlight;}
  };
})();
