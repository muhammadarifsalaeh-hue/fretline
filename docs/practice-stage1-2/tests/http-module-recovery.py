"""Real HTTP503/recovery proof, without Playwright request interception.

Serves the existing immutable production dist at loopback on an ephemeral port.
Only the combined practice module initially responds503; actual Retry must fetch
a distinct URL after the server recovers. No app files or browser DOM are edited.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import hashlib
import json
import os
import traceback

from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[3]
DIST=Path(os.environ.get('FRETLINE_QA_DIST',str(ROOT/'dist')))
OUT=Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR',str(ROOT/'docs/practice-stage1-2')))
ENGINE=os.environ.get('FRETLINE_QA_ENGINE','webkit')
OUT.mkdir(parents=True,exist_ok=True)
STATE={'blocked':True,'moduleRequests':[]}
REPORT={'engine':ENGINE,'method':'Actual local HTTP server using unchanged production dist bytes; no Playwright routing, canvas replacement or source edits.',
        'consoleErrors':[],'runtimeErrors':[],'failedRequests':[],'badResponses':[],'expectedFaultErrors':[],
        'limitations':['Actual Linux WebKit/Chromium engine, not physical Safari on iPad.']}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        path=urlsplit(self.path).path
        if '/practice-three-' in path:
            STATE['moduleRequests'].append({'path':self.path,'blocked':STATE['blocked']})
            if STATE['blocked']:
                body=b'Deliberate QA real HTTP scene failure'
                self.send_response(503)
                self.send_header('Content-Type','text/plain')
                self.send_header('Content-Length',str(len(body)))
                self.send_header('Cache-Control','no-store')
                super().end_headers();self.wfile.write(body);return
        if path=='/practice':self.path='/index.html'
        super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control','no-cache');super().end_headers()


def hashes():
    return {str(file.relative_to(DIST)):hashlib.sha256(file.read_bytes()).hexdigest()
            for file in DIST.rglob('*') if file.is_file()}


server=None
try:
    before=hashes();assert before and 'index.html' in before
    bundles=[path for path in before if Path(path).name.startswith('practice-three-') and path.endswith('.js')]
    assert len(bundles)==1,bundles
    REPORT['buildEvidence']={'fileCount':len(before),'indexSHA256':before['index.html'],'module':bundles[0],'moduleSHA256':before[bundles[0]]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(DIST)))
    Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port);REPORT['baseURL']=base
    with sync_playwright() as playwright:
        browser=(playwright.webkit.launch() if ENGINE=='webkit' else playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']))
        REPORT['browserVersion']=browser.version
        page=browser.new_page(viewport={'width':768,'height':1024},reduced_motion='reduce')
        def console(message):
            if message.type!='error':return
            row={'text':message.text,'location':message.location}
            expected='/practice-three-' in message.location.get('url','') and '503' in message.text
            (REPORT['expectedFaultErrors'] if expected else REPORT['consoleErrors']).append(row)
        def failed(request):
            row={'url':request.url,'failure':request.failure}
            (REPORT['expectedFaultErrors'] if '/practice-three-' in request.url else REPORT['failedRequests']).append(row)
        def response(result):
            if result.status<400:return
            row={'url':result.url,'status':result.status}
            (REPORT['expectedFaultErrors'] if '/practice-three-' in result.url and result.status==503 else REPORT['badResponses']).append(row)
        page.on('console',console);page.on('requestfailed',failed);page.on('response',response)
        page.on('pageerror',lambda error:REPORT['runtimeErrors'].append(str(error)))
        page.goto(base+'/practice',wait_until='networkidle')
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','error')
        expect(page.get_by_role('alert')).to_be_visible()
        page.locator('[data-practice-chord="G"]').click()
        page.evaluate('window.__httpRecoverySentinel="same-document"')
        STATE['blocked']=False
        page.locator('[data-practice-retry]').click()
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=30000)
        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-chord-id','G')
        assert page.evaluate('window.__httpRecoverySentinel')=='same-document'
        original=[r for r in STATE['moduleRequests'] if r['blocked']]
        retries=[r for r in STATE['moduleRequests'] if not r['blocked']]
        assert original and retries and urlsplit(retries[0]['path']).query,STATE
        page.reload(wait_until='networkidle')
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=30000)
        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-chord-id','C')
        assert page.locator('canvas[data-practice-canvas]').evaluate('c=>Boolean(c.getContext("webgl2"))')
        REPORT.update({'visibleFallback':True,'actualHTTPModuleRequests':STATE['moduleRequests'],
            'sameDocumentRecoveryWithSelectedG':True,'laterDocumentReloadReadyWithDefaultC':True})
        browser.close()
    assert hashes()==before,'The production build changed during real HTTP verification'
    REPORT['buildUnchanged']=True
    REPORT['passed']=not any(REPORT[k] for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses'])
except Exception:
    REPORT['passed']=False;REPORT['failure']=traceback.format_exc();print(REPORT['failure'],flush=True)
finally:
    if server:server.shutdown();server.server_close()
    (OUT/('http-module-recovery-'+ENGINE+'.json')).write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
print(('PASS' if REPORT['passed'] else 'FAIL')+' '+ENGINE+' actual-http-module-recovery',flush=True)
raise SystemExit(0 if REPORT['passed'] else 1)
