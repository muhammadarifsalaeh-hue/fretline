"""Local production builds + Vercel-rule emulator; no real Supabase/SQL.
Supabase HTTP is intercepted with an explicit 200-model contract fixture.
Chromium/WebKit viewports are not physical iPad certification or a Vercel deploy.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from urllib.parse import urlparse
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
from PIL import Image
import base64, io, json, re, threading, time, traceback

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/deployment/tests'
OUT.mkdir(parents=True,exist_ok=True)
CONFIG=json.loads((ROOT/'vercel.json').read_text())
CATALOG=json.loads((ROOT/'.local-preview/release-catalog-fixture.json').read_text())
REWRITE=re.compile('^'+CONFIG['rewrites'][0]['source']+'$')
QR_URL='https://fretline-release-fixture.vercel.app'
SIZES={'desktop':(1440,1000),'landscape':(1194,834),'portrait':(768,1024),'mobile':(390,844)}
report={'scope':'production builds on local Vercel-rule emulator; Supabase Auth/catalog HTTP fixtures only', 'realSupabaseTested':False,'realVercelTested':False,'physicalIPadTested':False,'databaseChanged':False,'checks':[],'runtimeErrors':[],'consoleErrors':[],'screenshots':[]}

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        route=urlparse(self.path).path
        if not Path(self.translate_path(self.path)).is_file() and REWRITE.match(route): self.path='/index.html'
        super().do_GET()
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()

servers=[]
def serve(path):
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(path)))
    threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
    return 'http://127.0.0.1:'+str(server.server_port)

BASE=serve(ROOT/'.local-preview/release-build')
STATIC=serve(ROOT/'dist')
def record(name,fn):
    try:
        result=fn();report['checks'].append({'name':name,'passed':True,'evidence':result});print('PASS',name,flush=True)
    except Exception:
        error=traceback.format_exc();report['checks'].append({'name':name,'passed':False,'error':error});print('FAIL',name,error,flush=True)
    (OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def overflow(page):
    result=page.evaluate('({viewport:innerWidth,content:document.documentElement.scrollWidth})')
    assert result['content']<=result['viewport']+1,result
    return result

def shot(page,name):
    page.screenshot(path=str(OUT/name),animations='disabled');report['screenshots'].append(name)

def jwt(user):
    encode=lambda data:base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b'=').decode()
    return encode({'alg':'HS256','typ':'JWT'})+'.'+encode({'sub':user['id'],'role':'authenticated','aud':'authenticated','exp':int(time.time())+3600})+'.fixture-signature'

def bridge(state):
    def route_handler(route):
        request=route.request;path=urlparse(request.url).path
        def answer(data,status=200): route.fulfill(status=status,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps(data))
        if request.method=='OPTIONS':route.fulfill(status=204,headers={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'});return
        state['requests'].append(path)
        if path=='/rest/v1/rpc/get_published_catalog':
            if state.get('unavailable'):answer({'message':'fixture outage'},503);return
            answer({'ready':True,'guitars':state['catalog']});return
        if path=='/auth/v1/token':
            email=json.loads(request.post_data)['email'];state['member']=email=='owner@example.test'
            state['user']={'id':'11111111-1111-1111-1111-111111111111','email':email,'aud':'authenticated','role':'authenticated','app_metadata':{},'user_metadata':{},'created_at':'2026-10-29T00:00:00Z'}
            answer({'access_token':jwt(state['user']),'refresh_token':'fixture-refresh','expires_in':3600,'token_type':'bearer','user':state['user']});return
        if path=='/auth/v1/user':answer(state['user']);return
        if path=='/auth/v1/logout':answer({});return
        if path=='/rest/v1/rpc/fretline_is_admin':answer(state['member']);return
        if path=='/rest/v1/guitars':answer([{'id':g['id'],'position':i,'status':'published','revision':1,'draft':g,'published':g} for i,g in enumerate(CATALOG)]);return
        if path=='/rest/v1/brands':answer([{'id':n.lower(),'name':n} for n in sorted({g['brand'] for g in CATALOG})]);return
        raise RuntimeError('Unexpected fixture request: '+path)
    return route_handler

with sync_playwright() as playwright:
  for engine in ['chromium','webkit']:
    browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else playwright.webkit.launch()
    for size,(width,height) in SIZES.items():
      context=browser.new_context(viewport={'width':width,'height':height},has_touch=size!='desktop',reduced_motion='reduce',accept_downloads=True)
      state={'member':False,'user':None,'requests':[],'catalog':CATALOG}
      context.route('https://qa.supabase.co/**',bridge(state))
      page=context.new_page()
      page.on('pageerror',lambda error:report['runtimeErrors'].append(str(error)))
      page.on('console',lambda msg:report['consoleErrors'].append(msg.text) if msg.type=='error' else None)
      prefix=engine+'-'+size
      def go(path):
        response=page.goto(BASE+path,wait_until='networkidle');assert response.status==200
        expect(page.locator('main h1')).to_be_visible();overflow(page)
      def public_navigation():
        go('/')
        assert '/rest/v1/rpc/get_published_catalog' in state['requests']
        expect(page.locator('a[href="/admin"]')).to_have_count(0)
        # A forged local flag must not create an admin menu.
        page.evaluate('localStorage.setItem("fretline:is-admin","true")')
        go('/admin');expect(page.get_by_role('heading',name='เข้าสู่ระบบผู้ดูแล')).to_be_visible()
        expect(page.locator('a[href="/admin"]')).to_have_count(0)
        return {'deepLinkStatus':200,'adminMenuForAnonymous':False}
      record(prefix+'-anonymous-and-spa-admin',public_navigation)
      def admin_navigation():
        def login(email):
          page.get_by_label('อีเมล',exact=True).fill(email);page.get_by_label('รหัสผ่าน',exact=True).fill('fixture-password-only')
          page.get_by_role('button',name='เข้าสู่ระบบ',exact=True).click()
        login('visitor@example.test');expect(page.get_by_role('heading',name='บัญชีนี้ไม่มีสิทธิ์แอดมิน')).to_be_visible()
        expect(page.locator('a[href="/admin"]')).to_have_count(0)
        page.get_by_role('button',name='ออกจากระบบ',exact=True).click()
        expect(page.get_by_role('heading',name='เข้าสู่ระบบผู้ดูแล')).to_be_visible()
        login('owner@example.test');expect(page.get_by_role('button',name='+ เพิ่มกีตาร์',exact=True)).to_be_visible()
        expect(page.locator('.site-nav a[href="/admin"]')).to_have_count(1)
        if width<1024:
          page.locator('.site-header-actions button[aria-controls="mobile-navigation"]').click()
          expect(page.locator('#mobile-navigation a[href="/admin"]')).to_be_visible()
          overflow(page);shot(page,prefix+'-admin-menu.png')
          page.locator('#mobile-navigation a[href="/admin"]').click()
        else:
          expect(page.locator('.site-nav a[href="/admin"]')).to_be_visible()
          assert page.locator('.site-nav').bounding_box()['x']+page.locator('.site-nav').bounding_box()['width']<=page.locator('.site-header-actions').bounding_box()['x']+1
          shot(page,prefix+'-admin-menu.png')
        # Revoked roles hide the link after a new remote check.
        state['member']=False;page.evaluate('window.dispatchEvent(new Event("focus"))')
        expect(page.locator('a[href="/admin"]')).to_have_count(0)
        state['member']=True;page.evaluate('window.dispatchEvent(new Event("focus"))')
        expect(page.locator('.site-nav a[href="/admin"]')).to_have_count(1)
        page.get_by_role('button',name='ออกจากระบบ',exact=True).click()
        expect(page.locator('a[href="/admin"]')).to_have_count(0)
        assert '/auth/v1/user' in state['requests']
        return {'getUserVerified':True,'membershipVerified':True,'nonAdminDenied':True,'revokedRoleHidden':True,'logoutHidden':True}
      record(prefix+'-verified-admin-and-logout',admin_navigation)
      def catalog_regression():
        go('/guitars?q=612VIIFM');expect(page.locator('[data-guitar-id="yamaha-pacifica-612viifm"]')).to_be_visible()
        page.locator('#catalog-search').fill('fg820');page.locator('.catalog-search-submit').click()
        expect(page.locator('[data-guitar-id="yamaha-fg820"]')).to_be_visible()
        go('/brands/fender');expect(page.locator('main h1')).to_contain_text('Fender')
        go('/guitars/yamaha-pacifica-612viifm');expect(page.locator('main h1')).to_contain_text('612VIIFM')
        go('/compare?ids=fender-player-ii-stratocaster,fender-player-ii-telecaster-hh,yamaha-pacifica-612viifm,martin-d-18')
        expect(page.locator('[data-compare-row="price"]')).to_contain_text('฿34,000')
        go('/find-my-guitar');expect(page.locator('main')).to_contain_text('Find My')
        go('/practice');expect(page.locator('[data-chord-diagram="C"]').first).to_be_visible()
        # Wait for async GLTF textures before navigating away; aborting mid-load
        # otherwise produces loader messages unrelated to a persistent failure.
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000)
        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
        for button in page.locator('.practice-camera-controls button').all():
          expect(button).to_be_enabled();button.click()
        return {'publishedFixtureCount':len(CATALOG),'brands':len({g['brand'] for g in CATALOG}),'search':True,'brand':True,'detail':True,'compareFour':True,'quiz':True,'practice':True}
      record(prefix+'-published-catalog-and-existing-features',catalog_regression)
      def qr_check():
        go('/qr');expect(page.locator('.qr-image img')).to_be_visible()
        expect(page.locator('.qr-url')).to_have_attribute('href',QR_URL)
        shot(page,prefix+'-fixture-qr.png')
        with page.expect_download() as download:
          page.get_by_role('link',name='ดาวน์โหลด QR Code').click()
        path=download.value.path();image=Image.open(path).convert('RGB')
        import zxingcpp
        decoded=zxingcpp.read_barcode(image);assert decoded and decoded.text==QR_URL
        assert download.value.suggested_filename=='fretline-qr.png'
        return {'downloadDecoded':True,'url':'fixture production URL only; not a deployed site','dimensions':image.size}
      record(prefix+'-qr-download-and-independent-decode',qr_check)
      if size=='portrait':
        def publication_refresh():
          updated=[dict(g) for g in CATALOG]
          target=next(g for g in updated if g['id']=='yamaha-pacifica-612viifm');target['price']=34567
          state['catalog']=updated;go('/guitars/yamaha-pacifica-612viifm')
          expect(page.locator('main')).to_contain_text('34,567')
          state['catalog']=CATALOG
          return 'Refresh consumes changed Published HTTP fixture; no database write'
        record(prefix+'-published-refresh',publication_refresh)
      context.close()
    # Missing DB must not silently present the bundled stale static data.
    context=browser.new_context(viewport={'width':390,'height':844})
    unavailable={'unavailable':True,'catalog':CATALOG,'requests':[],'member':False,'user':None}
    context.route('https://qa.supabase.co/**',bridge(unavailable))
    page=context.new_page()
    def outage():
      page.goto(BASE+'/guitars',wait_until='networkidle');expect(page.get_by_role('heading',name='โหลดข้อมูลกีตาร์ไม่สำเร็จ')).to_be_visible()
      expect(page.locator('[data-guitar-id]')).to_have_count(0)
      page.goto(BASE+'/admin',wait_until='networkidle');expect(page.get_by_role('heading',name='เข้าสู่ระบบผู้ดูแล')).to_be_visible()
      page.goto(BASE+'/qr',wait_until='networkidle');expect(page.locator('.qr-image img')).to_be_visible()
      page.locator('.qr-home').click();expect(page.get_by_role('heading',name='โหลดข้อมูลกีตาร์ไม่สำเร็จ')).to_be_visible()
    record(engine+'-catalog-outage-and-recovery-routes',outage)
    context.close()
    context=browser.new_context();page=context.new_page()
    def pending_qr():
      page.goto(STATIC+'/qr',wait_until='networkidle')
      expect(page.locator('.qr-pending')).to_be_visible();expect(page.locator('.qr-image img')).to_have_count(0)
      return 'No production URL configured: no QR from localhost/Codespaces'
    record(engine+'-unconfigured-qr-stays-unavailable',pending_qr)
    context.close();browser.close()

for path in ['/admin','/qr','/brands/fender','/guitars/yamaha-pacifica-612viifm']:
  def deep_link(path=path):
    with urlopen(BASE+path) as response:
      assert response.status==200;assert '<div id="root"></div>' in response.read().decode()
  record('http-spa-'+path,deep_link)
for server in servers:server.shutdown()
report['passed']=all(check['passed'] for check in report['checks']) and not report['runtimeErrors'] and not report['consoleErrors']
(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('FINAL',report['passed'],len(report['checks']),'runtime errors',len(report['runtimeErrors']),'console errors',len(report['consoleErrors']),flush=True)
raise SystemExit(0 if report['passed'] else 1)
