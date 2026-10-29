#!/usr/bin/env python3
"""Verify RSI navigation stays on one live document, including slow networks.

Uses the standalone generated Pages artifacts, a local delayed static server,
and Firefox WebDriver. Run after both Agent and RSI site builds.
"""
from __future__ import annotations

import base64
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp' / 'rsi-soft-navigation-qa'


def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def main():
    firefox = shutil.which('firefox')
    gecko = shutil.which('geckodriver')
    if not firefox or not gecko:
        raise SystemExit('SKIP: Firefox and geckodriver required')
    OUT.mkdir(parents=True, exist_ok=True)
    http_port, driver_port = port(), port()
    while driver_port == http_port:
        driver_port = port()

    class DelayedHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT / '_site'), **kwargs)

        def do_GET(self):
            if self.path.startswith('/rsi/reading-notes.html'):
                time.sleep(.95)
            return super().do_GET()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', http_port), DelayedHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    log = (OUT / 'webdriver.log').open('w')
    driver = subprocess.Popen([gecko, '--port', str(driver_port)], stdout=log, stderr=log)
    session = ''

    def req(method, path, payload=None):
        data = json.dumps(payload if payload is not None else {}).encode() if method == 'POST' else None
        request = urllib.request.Request(
            f'http://127.0.0.1:{driver_port}' + path,
            data=data, method=method, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return json.load(response)['value']
        except urllib.error.HTTPError as error:
            raise AssertionError(error.read().decode('utf-8', errors='replace')[:1400]) from error

    def js(code):
        return req('POST', f'/session/{session}/execute/sync', {'script': code, 'args': []})

    def check(value, msg):
        if not value:
            raise AssertionError(msg)

    def wait_for(condition, label, timeout=15):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if js(condition):
                return
            time.sleep(.13)
        raise AssertionError('Timeout while waiting for ' + label)

    def click(href):
        js("document.querySelector('#research-nav a[href=" +
           json.dumps(href) + "]').click()")

    def navigate_full(href):
        req('POST', f'/session/{session}/url',
            {'url': f'http://127.0.0.1:{http_port}/rsi/' + href})
        time.sleep(.3)

    def snapshot(name):
        data = req('GET', f'/session/{session}/screenshot')
        (OUT / name).write_bytes(base64.b64decode(data))

    try:
        for _ in range(35):
            try:
                if req('GET', '/status'):
                    break
            except Exception:
                time.sleep(.3)
        session = req('POST', '/session', {'capabilities': {
            'alwaysMatch': {
                'acceptInsecureCerts': True,
                'moz:firefoxOptions': {'args': ['-headless']}
            }}})['sessionId']
        req('POST', f'/session/{session}/window/rect', {'width': 1440, 'height': 980})
        navigate_full('index.html')
        check(js("return Boolean(window.RSIPageRouter)"), 'Router missing from RSI page')
        js("""window.__rsiTestMarker = {shell:document.querySelector('#sidebar'),
                  toolbar:document.querySelector('.topbar'), start:performance.now()};""")

        # A slow response must not clear or replace the currently displayed page.
        click('reading-notes.html')
        time.sleep(.22)
        check(js("""return document.body.dataset.rsiPage==='index' &&
          document.querySelector('.content h1')?.textContent.includes('RSI') &&
          document.querySelector('#sidebar') === window.__rsiTestMarker.shell &&
          document.querySelector('.topbar') === window.__rsiTestMarker.toolbar"""),
          'Previous article or navigation shell vanished before slow page finished')
        snapshot('slow-network-old-content-still-visible.png')
        wait_for("return document.body.dataset.rsiPage==='reading-notes'", 'slow page')
        check(js("""return window.__rsiTestMarker?.shell===document.querySelector('#sidebar') &&
          window.__rsiTestMarker?.toolbar===document.querySelector('.topbar')"""),
          'Sidebar/topbar were recreated during soft navigation')
        check(js("return performance.getEntriesByType('navigation').length===1"),
              'Navigating reading-notes caused a full document navigation')
        snapshot('reading-notes-after-softnav.png')

        # Long-form article -> paper cards. Filtering must initialize on the new content.
        click('reading-cards.html')
        wait_for("return document.body.dataset.rsiPage==='reading-cards'", 'reading cards')
        check(js("return !!document.querySelector('#reading-card-filter')"), 'Reading card UI missing')
        js("""const q=document.querySelector('#reading-card-filter');
          q.value='test-unknown-paper';q.dispatchEvent(new Event('input',{bubbles:true}));""")
        check(js("return document.querySelectorAll('.reading-card:not([hidden])').length===0"),
              'Reading-card filter was not reinitialized after soft nav')

        # Timeline: timers and calendar require page-local script execution.
        click('timeline.html')
        wait_for("return document.body.dataset.rsiPage==='timeline'", 'timeline')
        wait_for("return document.querySelectorAll('[data-calendar-day]').length>0", 'calendar')
        check(js("return document.querySelector('#rsi-rt-next-countdown').textContent.includes('秒')"),
              'Timeline timers did not initialize after a soft route')
        now = js("return document.querySelector('#rsi-rt-next-countdown').textContent")
        time.sleep(1.15)
        later = js("return document.querySelector('#rsi-rt-next-countdown').textContent")
        check(now != later, 'Countdown stopped ticking after soft nav')

        # Research map: filters, collapsible chapters and colored outline.
        click('research-map.html')
        wait_for("return document.body.dataset.rsiPage==='research-map'", 'research map')
        check(js("return document.querySelectorAll('.rm-outline [data-chapter]').length===8"),
              'Research map not rendered')
        js("""const s=document.querySelector('#rm-function');
             s.value='signal';s.dispatchEvent(new Event('change',{bubbles:true}));""")
        check(js("return [...document.querySelectorAll('.rm-group:not([hidden])')].length===1"),
              'Map filter did not initialize on soft nav')

        # Native browser history should move between documents without reloading.
        req('POST', f'/session/{session}/back')
        wait_for("return document.body.dataset.rsiPage==='timeline'", 'back to timeline')
        check(js("return document.querySelectorAll('[data-calendar-day]').length>0"),
              'History back failed to initialize the timeline')
        req('POST', f'/session/{session}/forward')
        wait_for("return document.body.dataset.rsiPage==='research-map'", 'forward to map')
        check(js("return document.querySelectorAll('.rm-group').length===4"),
              'History forward lost the research map')

        # Race: slow reading-notes followed by fast timeline. Late response
        # must never overwrite the more recent navigation.
        click('reading-notes.html')
        time.sleep(.1)
        click('timeline.html')
        wait_for("return document.body.dataset.rsiPage==='timeline'", 'fast second click')
        time.sleep(1.15)
        check(js("return document.body.dataset.rsiPage==='timeline'"),
              'Stale slow navigation overwrote the newer target')
        check(js("return document.querySelectorAll('[data-calendar-day]').length>0"),
              'Fast subsequent route left a noninteractive calendar')
        check(js("return !document.body.classList.contains('rsi-soft-pending')"),
              'Loading indicator remained after navigation')
        check(js("return performance.getEntriesByType('navigation').length===1"),
              'A soft navigation unexpectedly reloaded the document')
        snapshot('timeline-after-race.png')
        print(json.dumps({
            'status':'PASS',
            'slow_network_preserves_old_content':True,
            'persistent_sidebar':True,
            'persistent_toolbar':True,
            'history_back_forward':'PASS',
            'paper_filter':'PASS',
            'timeline_live_calendar':'PASS',
            'research_map_filter':'PASS',
            'race_cancellation':'PASS',
            'full_document_navigations':1
        }, ensure_ascii=False, indent=2))
    finally:
        if session:
            try:
                req('DELETE', f'/session/{session}')
            except Exception:
                pass
        driver.terminate()
        try:
            driver.wait(timeout=6)
        except subprocess.TimeoutExpired:
            driver.kill()
        server.shutdown()
        server.server_close()
        log.close()


if __name__ == '__main__':
    main()
