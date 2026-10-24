"""Actual Stage 1–2 Practice browser QA against an existing production preview.

No app edits or picture/canvas substitution. Explicit fault cases are labelled.
Chromium uses real software WebGL2; WebKit uses its actual Linux WPE renderer.
Neither is a physical iPad Safari verdict. Set FRETLINE_QA_URL and QA_ENGINE.
"""
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
import json
import math
import os
import re
import traceback

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(os.environ.get('FRETLINE_QA_OUTPUT_DIR', str(ROOT / 'docs/practice-stage1-2')))
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5410').rstrip('/')
ENGINE = os.environ.get('FRETLINE_QA_ENGINE', 'chromium')
SELECT = os.environ.get('FRETLINE_QA_CASES', '').split(',')
SELECT = [s for s in SELECT if s]
VIEWPORTS = [(1440, 1000, 'desktop'), (1024, 768, 'tablet-landscape'),
             (768, 1024, 'tablet'), (390, 844, 'mobile'), (320, 740, 'small-mobile')]
OUT.mkdir(parents=True, exist_ok=True)
REPORT = {'engine': ENGINE, 'baseURL': BASE, 'checks': [], 'consoleErrors': [],
          'runtimeErrors': [], 'failedRequests': [], 'badResponses': [],
          'expectedFaultErrors': [], 'contextWarnings': [], 'screenshots': [],
          'limitations': ['Actual Linux browser engines, not physical iPad Safari.',
                          'Chromium uses SwiftShader software WebGL; iPad GPU and thermal behavior are not covered.']}
CANVAS = 'canvas[data-practice-canvas]'
STATUS = '[data-practice-status]'


def context_for(browser, case, width=1440, height=1000, fault=False, touch=False):
    context = browser.new_context(viewport={'width': width, 'height': height},
                                  has_touch=touch or width <= 1024,
                                  locale='th-TH', reduced_motion='reduce')
    page = context.new_page()
    def module_fault(url):
        return fault == 'module' and bool(re.search(r'/practice-three-[^/]+\.js(?:\?.*)?$',url))
    def console(msg):
        if msg.type=='warning' and re.search(r'too many active webgl|context creation failed',msg.text,re.I):
            REPORT['contextWarnings'].append({'case':case,'text':msg.text})
        if msg.type != 'error': return
        row = {'case': case, 'text': msg.text}
        expected = bool(fault and any(s in msg.text.lower() for s in ['webgl', 'context_lost', 'context lost'])) or module_fault(msg.location.get('url',''))
        (REPORT['expectedFaultErrors'] if expected else REPORT['consoleErrors']).append(row)
    def failed(request):
        row={'case':case,'url':request.url,'failure':request.failure}
        (REPORT['expectedFaultErrors'] if module_fault(request.url) else REPORT['failedRequests']).append(row)
    def response(result):
        if result.status<400:return
        row={'case':case,'url':result.url,'status':result.status}
        (REPORT['expectedFaultErrors'] if module_fault(result.url) else REPORT['badResponses']).append(row)
    page.on('console', console)
    page.on('pageerror', lambda e: REPORT['runtimeErrors'].append({'case': case, 'text': str(e)}))
    page.on('requestfailed', failed)
    page.on('response', response)
    return context, page


def go(page):
    page.goto(BASE + '/practice', wait_until='networkidle')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=30000)
    expect(page.locator(CANVAS)).to_be_visible()
    page.evaluate('document.fonts.ready')


def camera(page):
    data = json.loads(page.locator(CANVAS).get_attribute('data-camera'))
    assert set(data) >= {'position', 'target', 'distance'}, data
    assert len(data['position']) == len(data['target']) == 3 and data['distance'] > 0, data
    assert all(math.isfinite(n) for n in data['position'] + data['target']), data
    return data


def changed(page, before):
    page.wait_for_function('''([selector,old])=>{const raw=document.querySelector(selector)?.getAttribute('data-camera');
      if(!raw)return false;const now=JSON.parse(raw);
      return now.position.some((value,index)=>Math.abs(value-old.position[index])>0.0001);}''',
                           arg=[CANVAS, before], timeout=5000)
    now = camera(page)
    assert any(abs(a-b) > 0.0001 for a,b in zip(now['position'], before['position'])), (before, now)
    return now


def camera_near(a,b):
    return all(abs(x-y)<0.0001 for key in ['position','target'] for x,y in zip(a[key],b[key])) and abs(a['distance']-b['distance'])<0.0001


def shot(page, name, full=True, canvas=False):
    target = OUT / 'screenshots' / ENGINE / (name + '.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    if canvas: page.locator(CANVAS).screenshot(path=str(target))
    else: page.screenshot(path=str(target), full_page=full, animations='allow')
    REPORT['screenshots'].append(str(target.relative_to(OUT)))
    return target


def pixel_evidence(page):
    image = Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')
    image.thumbnail((400, 400))
    colors = len(image.getcolors(image.width * image.height) or [])
    lit = sum(1 for r,g,b in image.getdata() if max(r,g,b) > 70 and max(r,g,b)-min(r,g,b)>10)
    assert colors > 300 and lit > 250, {'colors': colors, 'litPixels': lit}
    return {'sampleDimensions': image.size, 'colors': colors, 'litColoredPixels': lit}


def metadata(page):
    canvas = page.locator(CANVAS)
    assert canvas.get_attribute('data-string-count') == '6'
    assert canvas.get_attribute('data-fret-count') == '12'
    assert canvas.get_attribute('data-chord-id') == 'C'
    assert canvas.get_attribute('tabindex') == '0'
    dims = canvas.evaluate('c=>({width:c.width,height:c.height,rect:{width:c.getBoundingClientRect().width,height:c.getBoundingClientRect().height},gl:Boolean(c.getContext("webgl2")),touchAction:getComputedStyle(c).touchAction})')
    assert dims['gl'] and dims['width'] > 100 and dims['height'] > 100, dims
    assert dims['rect']['width'] > 200 and dims['rect']['height'] > 200, dims
    assert dims['touchAction'] == 'none', dims
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    return {'canvas': dims, 'camera': camera(page), 'paint': pixel_evidence(page)}


def rendering(page, label):
    go(page)
    data = metadata(page)
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    shot(page, 'practice-' + label)
    if label in {'desktop', 'tablet', 'mobile'}:
        page.locator(CANVAS).scroll_into_view_if_needed()
        shot(page, 'neck-' + label, canvas=True)
    return data


def camera_controls(page):
    go(page)
    default = camera(page)
    before_pixels = Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')
    movements = []
    for name in ['หมุนไปทางซ้าย', 'หมุนไปทางขวา', 'ซูมเข้า', 'ซูมออก']:
        before = camera(page)
        page.get_by_role('button', name=name, exact=True).click()
        now = changed(page, before)
        if name == 'ซูมเข้า': assert now['distance'] < before['distance']
        if name == 'ซูมออก': assert now['distance'] > before['distance']
        movements.append({'action': name, 'before': before, 'after': now})
    page.get_by_role('button', name='รีเซ็ตกล้อง', exact=True).click()
    page.wait_for_timeout(100)
    assert camera_near(camera(page),default), (default, camera(page))
    presets = []
    for preset in ['front', 'head', 'angle']:
        before = camera(page)
        page.locator('[data-camera-preset="' + preset + '"]').click()
        now = changed(page, before)
        presets.append({'preset': preset, 'camera': now})
    page.get_by_role('button', name='หมุนไปทางซ้าย', exact=True).click()
    after_pixels = Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')
    assert before_pixels.size == after_pixels.size
    assert ImageChops.difference(before_pixels, after_pixels).getbbox(), 'Actual canvas pixels did not change with camera'
    shot(page, 'neck-rotated', canvas=True)
    return {'movements': movements, 'presets': presets, 'canvasPixelsChanged': True}


def keyboard_pointer(page):
    go(page)
    canvas = page.locator(CANVAS)
    canvas.scroll_into_view_if_needed()
    canvas.focus()
    default = camera(page)
    sequence = []
    for key in ['ArrowLeft', 'ArrowUp', '=', '-']:
        before = camera(page); page.keyboard.press(key); sequence.append({'key': key, 'camera': changed(page, before)})
    page.keyboard.press('Home'); page.wait_for_timeout(80)
    assert camera_near(camera(page),default)
    before = camera(page)
    box = canvas.bounding_box()
    x,y = box['x']+box['width']*.45, box['y']+box['height']*.5
    page.mouse.move(x,y); page.mouse.down(); page.mouse.move(x+70,y+25,steps=10); page.mouse.up()
    dragged = changed(page, before)
    # Browser/device shortcuts must remain available while the canvas has focus.
    for modifier in ['ctrlKey','metaKey','altKey']:
        before=camera(page)
        result=canvas.evaluate('''(canvas,modifier)=>{
          const event=new KeyboardEvent('keydown',{key:'0',bubbles:true,cancelable:true,[modifier]:true});
          canvas.dispatchEvent(event);return {defaultPrevented:event.defaultPrevented};
        }''',modifier)
        assert not result['defaultPrevented'],{'modifier':modifier,**result}
        assert camera_near(camera(page),before),'Modified shortcut changed the practice camera'
    canvas.focus(); page.keyboard.press('Tab')
    assert page.evaluate('document.activeElement?.tagName') != 'CANVAS', 'Canvas traps keyboard Tab'
    return {'keyboard': sequence, 'pointerDrag': dragged, 'browserModifierShortcutsPreserved':True,'tabEscapesCanvas': True}


def chord_switching(page):
    go(page)
    page.evaluate('window.__practiceNavigationSentinel="same-document"')
    ids = ['C','G','D','Em','Am','C']
    expected = {'C': [None,3,2,0,1,0], 'G': [3,2,0,0,0,3], 'D': [None,None,0,2,3,2],
                'Em': [0,2,2,0,0,0], 'Am': [None,0,2,2,1,0]}
    states = []
    for value in ids:
        button = page.locator('[data-practice-chord="' + value + '"]')
        button.click()
        expect(button).to_have_attribute('aria-pressed','true')
        expect(page.locator(CANVAS)).to_have_attribute('data-chord-id',value)
        detail=page.locator('[data-practice-active-chord="'+value+'"]')
        expect(detail).to_be_visible()
        diagram=detail.locator('svg[role="img"][data-chord-diagram="'+value+'"]')
        lines=diagram.locator('line').evaluate_all('nodes=>nodes.map(n=>({x1:n.x1.baseVal.value,x2:n.x2.baseVal.value,y1:n.y1.baseVal.value,y2:n.y2.baseVal.value}))')
        vertical=[line for line in lines if line['x1']==line['x2'] and line['y1']!=line['y2']]
        horizontal=[line for line in lines if line['y1']==line['y2'] and line['x1']!=line['x2']]
        assert len(lines)==12 and len(vertical)==len(horizontal)==6,{'chord':value,'lines':lines}
        assert [line['y1'] for line in horizontal]==[37,59,81,103,125,147],horizontal
        assert all(line['y1']==37 and line['y2']==147 for line in vertical),vertical
        description=diagram.locator('title').text_content()
        for index,fret in enumerate(expected[value]):
            target=f'{6-index}: '+('mute' if fret is None else 'open' if fret==0 else 'fret '+str(fret)+', finger ')
            assert target in description, {'chord':value,'missing':target,'title':description}
        assert diagram.locator('circle.practice-diagram-dot').count()==sum(fret is not None and fret>0 for fret in expected[value])
        assert page.evaluate('window.__practiceNavigationSentinel') == 'same-document'
        states.append({'chord': value, 'selected': True, 'renderedDiagramDescription':description,'verifiedVoicingLowToHigh': expected[value]})
    return {'states': states, 'sameDocument': True}


def lazy_routes(page):
    rows = []
    for route in ['/', '/brands', '/guitars']:
        page.goto(BASE + route, wait_until='networkidle')
        scripts = page.evaluate('performance.getEntriesByType("resource").filter(r=>r.initiatorType==="script"||r.name.endsWith(".js")).map(r=>r.name)')
        practice = [s for s in scripts if re.search(r'(practice-three|GuitarNeckViewer|neckScene|PracticePage)-',s,re.I)]
        assert not practice, {'route': route, 'unexpected3DScripts': practice}
        assert page.locator(CANVAS).count() == 0
        rows.append({'route':route,'practiceScripts':practice,'scriptCount':len(scripts)})
    go(page)
    scripts = page.evaluate('performance.getEntriesByType("resource").filter(r=>r.name.endsWith(".js")).map(r=>r.name)')
    assert any('practice-three-' in s for s in scripts), scripts
    rows.append({'route':'/practice','threeChunks':[s for s in scripts if 'practice-three-' in s]})
    return {'routes':rows}


def loading(page):
    held = []
    page.route(re.compile(r'.*/practice-three-[^/]+\.js(?:\?.*)?$'), lambda route: held.append(route))
    page.goto(BASE + '/practice',wait_until='domcontentloaded')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','loading',timeout=15000)
    expect(page.get_by_role('status').last).to_be_visible()
    page.wait_for_timeout(150)
    assert held, 'Three chunk was not independently deferred'
    shot(page,'intentional-loading')
    for route in held: route.continue_()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    return {'deferredChunkCount':len(held),'loadingVisible':True,'eventualReady':True}


def unsupported(page):
    page.add_init_script('''window.__qaNativeGetContext=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(type,...args){
        return /^(webgl2?|experimental-webgl)$/.test(type)?null:window.__qaNativeGetContext.call(this,type,...args);
      };''')
    page.goto(BASE + '/practice',wait_until='networkidle')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','error')
    expect(page.get_by_role('alert')).to_be_visible()
    expect(page.locator('[data-practice-retry]')).to_be_visible()
    shot(page,'intentional-webgl-unavailable')
    page.evaluate('()=>{HTMLCanvasElement.prototype.getContext=window.__qaNativeGetContext;}')
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    return {'intentionalFault':'WebGL context factory unavailable before route load','visibleFallback':True,'retryRecovered':True}


def context_loss(page):
    go(page)
    supported = page.locator(CANVAS).evaluate('''c=>{const gl=c.getContext('webgl2');const ext=gl.getExtension('WEBGL_lose_context');if(!ext)return false;ext.loseContext();return true;}''')
    assert supported, 'Runtime does not expose WEBGL_lose_context; do not call loss covered'
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','error')
    expect(page.get_by_role('alert')).to_be_visible()
    shot(page,'intentional-context-lost')
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    return {'intentionalFault':'Actual WEBGL_lose_context extension','visibleFallback':True,'retryRecovered':True}


def module_failure(page):
    pattern=re.compile(r'.*/practice-three-[^/]+\.js(?:\?.*)?$')
    blocked=[];responses=[]
    page.on('response',lambda response:responses.append({'url':response.url,'status':response.status}) if pattern.match(response.url) else None)
    def reject(route):
        blocked.append(route.request.url)
        route.fulfill(status=503,content_type='text/plain',headers={'Cache-Control':'no-store'},body='Deliberate QA scene-module failure')
    page.route(pattern,reject)
    page.goto(BASE+'/practice',wait_until='networkidle')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','error')
    expect(page.get_by_role('alert')).to_be_visible()
    assert blocked,'Scene module failure was not injected'
    page.locator('[data-practice-chord="G"]').click()
    expect(page.locator('[data-practice-active-chord="G"]')).to_be_visible()
    shot(page,'intentional-scene-module-503')
    page.evaluate('window.__qaBeforeModuleRetry="failed-document"')
    page.unroute(pattern,reject)
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    expect(page).to_have_url(BASE+'/practice')
    # WebKit retains a rejected module URL even across a plain page reload.
    # Recovery must obtain the real bundle from a distinct URL, retaining UI state.
    assert page.evaluate('window.__qaBeforeModuleRetry')=='failed-document'
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id','G')
    successful=[r for r in responses if r['status']==200]
    assert successful and any(r['url'] not in blocked and urlparse(r['url']).query for r in successful),responses
    supported=page.locator(CANVAS).evaluate('''c=>{const ext=c.getContext('webgl2').getExtension('WEBGL_lose_context');if(!ext)return false;ext.loseContext();return true;}''')
    assert supported
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','error')
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id','G')
    assert page.evaluate('window.__qaBeforeModuleRetry')=='failed-document'
    page.reload(wait_until='networkidle')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id','C')
    return {'intentionalFault':'HTTP503 for real combined scene/Three chunk','blockedURLs':blocked,'moduleResponses':responses,
            'visibleFallback':True,'distinctURLRecoveredInSameDocument':True,'selectedChordPreserved':'G',
            'subsequentContextLossRetryRecovered':True,'laterDocumentReloadRecoveredWithDefaultChord':'C'}


def spa_cleanup(page):
    page.goto(BASE+'/',wait_until='networkidle')
    page.evaluate('window.__qaSpaSentinel="same-document"')
    page.locator('.site-nav a[href="/practice"]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
    cycles=[]
    for cycle in range(2):
        assert page.locator(CANVAS).count()==1
        assert page.evaluate('window.__qaSpaSentinel')=='same-document'
        page.locator('.practice-model-note a[href="/guitars"]').click()
        expect(page.locator('#catalog-search')).to_be_visible()
        assert page.locator(CANVAS).count()==0
        assert page.evaluate('window.__qaSpaSentinel')=='same-document'
        page.go_back(wait_until='domcontentloaded')
        expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000)
        assert page.locator(CANVAS).count()==1
        assert page.evaluate('window.__qaSpaSentinel')=='same-document'
        cycles.append({'cycle':cycle+1,'canvasCountOutsidePractice':0,'canvasCountAfterBack':1,'sameDocument':True})
    return {'cycles':cycles,'cameraAfterBack':camera(page)}


def touch(page, browser):
    go(page)
    before = camera(page)
    page.get_by_role('button',name='ซูมเข้า',exact=True).tap()
    tapped = changed(page,before)
    assert tapped['distance'] < before['distance']
    result = {'nativeTouchTapZoom':True}
    if ENGINE == 'chromium':
        canvas=page.locator(CANVAS);canvas.scroll_into_view_if_needed();box=canvas.bounding_box()
        center_x,center_y=box['x']+box['width']/2,box['y']+box['height']/2
        session=page.context.new_cdp_session(page)
        def points(distance):return [{'id':1,'x':center_x-distance,'y':center_y,'radiusX':3,'radiusY':3},{'id':2,'x':center_x+distance,'y':center_y,'radiusX':3,'radiusY':3}]
        before=camera(page)
        session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':points(30)})
        for distance in [35,40,45,50,55,60]:session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':points(distance)})
        session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        after=changed(page,before)
        assert after['distance'] < before['distance'],(before,after)
        session.detach();result['nativeMultiTouchPinchZoom']=True
    else: result['pinchLimitation']='No CDP touch injection in WebKit; physical iPad pinch remains untested.'
    return result


try:
    with sync_playwright() as playwright:
        if ENGINE=='chromium':
            browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        elif ENGINE=='webkit':browser=playwright.webkit.launch()
        else:raise ValueError(ENGINE)
        REPORT['browserVersion']=browser.version
        cases=[('rendering-'+label,lambda p,label=label:rendering(p,label),w,h,False) for w,h,label in VIEWPORTS]
        cases += [('camera-controls',camera_controls,1440,1000,False),('keyboard-pointer',keyboard_pointer,1440,1000,False),
                  ('chords',chord_switching,1440,1000,False),('lazy-routes',lazy_routes,1440,1000,False),
                  ('loading',loading,768,1024,False),('unsupported',unsupported,390,844,True),
                  ('context-loss',context_loss,768,1024,True),('touch',lambda p:touch(p,browser),768,1024,False),
                  ('module-failure',module_failure,768,1024,'module'),('spa-cleanup',spa_cleanup,1440,1000,False)]
        for name,fn,w,h,fault in cases:
            if SELECT and not any(name.startswith(prefix) for prefix in SELECT):continue
            context,page=context_for(browser,name,w,h,fault=fault,touch=name=='touch')
            try:
                details=fn(page)
                REPORT['checks'].append({'case':name,'passed':True,'details':details})
                print('PASS '+ENGINE+' '+name,flush=True)
            except Exception:
                failure=traceback.format_exc()
                REPORT['checks'].append({'case':name,'passed':False,'failure':failure})
                try:shot(page,'failure-'+name)
                except Exception:pass
                print('FAIL '+ENGINE+' '+name+'\n'+failure,flush=True)
            finally:context.close()
        browser.close()
except Exception:
    REPORT['harnessFailure']=traceback.format_exc()
    print(REPORT['harnessFailure'],flush=True)
finally:
    REPORT['passed']=bool(REPORT['checks']) and all(c['passed'] for c in REPORT['checks']) and not REPORT.get('harnessFailure') and not any(REPORT[k] for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses','contextWarnings'])
    suffix='-'+('-'.join(SELECT)) if SELECT else ''
    (OUT/('browser-'+ENGINE+suffix+'.json')).write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if REPORT['passed'] else 1)
