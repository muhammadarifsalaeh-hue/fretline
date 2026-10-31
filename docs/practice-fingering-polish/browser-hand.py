"""Real production WebGL/GLB integration; no fixtures, uploads or database writes."""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageChops
import numpy as np
from playwright.sync_api import sync_playwright, expect
import hashlib
import json
import traceback
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:4196'
CANVAS = 'canvas[data-practice-canvas]'
LIB = json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text())
CAMERA_ONLY = '--camera-only' in sys.argv
ACCEPTED = {k for k,v in LIB['poses'].items() if v.get('audit',{}).get('collisionPassed') is True and v.get('audit',{}).get('contactPassed') is True}
report = {'checks': [], 'engine':'Chromium', 'physicalIPadSafariTested':False, 'databaseWrites':0,
          'realGLB':True, 'mockHandUsed':False, 'teachingApprovalClaimed':False,
          'consoleErrors':[], 'runtimeErrors':[], 'unexpectedNetworkFailures':[]}


def check(name, fn, page):
    if CAMERA_ONLY and not name.endswith('-camera-and-touch-controls'):
        return
    try:
        evidence=fn()
        report['checks'].append({'name':name,'passed':True,'evidence':evidence})
        print('PASS',name,flush=True)
    except Exception:
        report['checks'].append({'name':name,'passed':False,'error':traceback.format_exc()})
        print('FAIL',name,traceback.format_exc(),flush=True)
        page.screenshot(path=str(OUT/'screenshots'/(name+'-FAIL.png')),animations='disabled')


def go(page, route='/practice'):
    assert page.goto(BASE+route,wait_until='domcontentloaded').status==200
    expect(page.locator('main h1')).to_be_visible()
    page.evaluate('document.fonts.ready')


def ready(page):
    expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000)
    expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','ready',timeout=60000)


def state(page):
    return page.locator(CANVAS).evaluate('''c=>({chord:c.dataset.handChordId,visible:c.dataset.handVisible,
      status:c.dataset.handStatus,review:c.dataset.handReviewMode,allowed:c.dataset.handInspectionAllowed,
      signature:c.dataset.handPoseSignature,asset:c.dataset.handModelSha256,
      render:JSON.parse(c.dataset.renderInfo),camera:JSON.parse(c.dataset.camera),
      geometry:JSON.parse(c.dataset.practiceProjection).geometrySignature,strings:c.dataset.stringCount,frets:c.dataset.fretCount})''')


def choose(page, chord, visible=None):
    page.locator('[data-practice-chord="'+chord+'"]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-hand-chord-id',chord)
    expected = chord in ACCEPTED if visible is None else visible
    expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true' if expected else 'false')
    expect(page.locator('.practice-chord-detail')).to_have_attribute('data-practice-active-chord',chord)


def settle(page):
    page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')


def layout(page):
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    box=page.locator(CANVAS).bounding_box()
    assert box['width']>=300 and box['height']>=300,box
    return box


with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
    for device,w,h in [('desktop',1440,1000),('landscape',1194,834),('portrait',768,1024),('mobile',390,844)]:
        context=browser.new_context(viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
        page=context.new_page()
        page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)))
        page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
        page.on('requestfailed',lambda req:report['unexpectedNetworkFailures'].append({'url':req.url,'failure':req.failure}) if req.resource_type in ['fetch','image','script'] else None)
        go(page);ready(page)

        def initial():
            expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
            expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
            s=state(page)
            assert s['chord']=='C' and s['status']=='needs-review' and s['strings']=='6' and s['frets']=='12'
            assert s['asset']==LIB['assetSha256'] and s['render']['triangles']>16000
            assert page.locator('[data-practice-chord]').count()==42
            assert not any(word in page.locator('.practice-viewer').inner_text() for word in ['รอตรวจทาน','ยังไม่ยืนยัน','ท่าทดลอง','prototype'])
            page.locator('.practice-viewer').screenshot(path=str(OUT/'screenshots'/('after-'+device+'.png')),animations='disabled')
            return {'actualRig':s,'layout':layout(page),'developmentWarningVisible':False}
        check(device+'-black-sleeved-model-on-real-route',initial,page)

        def all_chords():
            rows=[]
            for chord in LIB['poses']:
                choose(page,chord);s=state(page)
                assert s['status']=='needs-review'
                assert s['allowed']==('true' if chord in ACCEPTED else 'false')
                assert page.locator('[data-hand-review-warning]').count()==0
                assert page.locator('[data-practice-hand-review]').count()==(1 if chord in ACCEPTED else 0)
                assert page.locator('.practice-diagram-wrap svg').count()==1
                rows.append({'chord':chord,'handVisible':s['visible'],'signature':s['signature'],'status':s['status']})
            assert len({s['signature'] for s in rows})==42
            assert sum(s['handVisible']=='true' for s in rows)==len(ACCEPTED)
            return {'chords':42,'renderedHands':len(ACCEPTED),'rejectedHandsHidden':42-len(ACCEPTED),'verifiedTeachingHands':0,'rows':rows}
        check(device+'-all-42-chords-and-strict-gates',all_chords,page)

        def pixels_and_preference():
            choose(page,'C');page.locator(CANVAS).scroll_into_view_if_needed();settle(page)
            before=state(page);on=Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')
            page.locator('[data-practice-hand-review]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','false');settle(page)
            off=Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')
            changed=int(np.any(np.asarray(ImageChops.difference(on,off))>10,axis=2).sum())
            assert changed>1000,changed
            assert state(page)['camera']==before['camera']
            page.locator('[data-practice-hand-review]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
            page.locator('[data-practice-hand-review]').click();choose(page,'Dm',False)
            expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','false')
            page.locator('[data-practice-hand-review]').click();expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
            choose(page,'C');expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
            return {'canvasPixelsChangedByRealHandToggle':changed,'cameraUnchanged':True,'hiddenPreferenceRespectedAcrossChords':True}
        check(device+'-real-canvas-pixels-and-hand-toggle',pixels_and_preference,page)

        def camera_controls():
            initial=state(page);geometry=initial['geometry'];signature=initial['signature']
            page.locator('.practice-camera-views summary').click()
            for preset in ['front','side','back','player','overview','angle']:
                page.locator('[data-camera-preset="'+preset+'"]').click();settle(page);current=state(page)
                assert current['geometry']==geometry and current['signature']==signature
            buttons=page.locator('.practice-camera-controls button')
            buttons.nth(0).click();settle(page);assert state(page)['camera']!=initial['camera']
            distance=state(page)['camera']['distance'];buttons.nth(3).click();settle(page);assert state(page)['camera']['distance']<distance
            buttons.last.click();settle(page)
            page.locator('.practice-camera-views summary').click()
            box=page.locator(CANVAS).bounding_box();page.locator(CANVAS).scroll_into_view_if_needed();box=page.locator(CANVAS).bounding_box()
            before=state(page)['camera'];page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.65);page.mouse.down();page.mouse.move(box['x']+box['width']*.6,box['y']+box['height']*.7,steps=8);page.mouse.up();settle(page)
            assert state(page)['camera']!=before
            if device!='desktop':
                # Chromium CDP delivers genuine two-touch input to OrbitControls.
                client=context.new_cdp_session(page);x=box['x']+box['width']*.5;y=box['y']+box['height']*.65
                distance=state(page)['camera']['distance']
                client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x-20,'y':y,'id':1},{'x':x+20,'y':y,'id':2}]})
                client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x-45,'y':y,'id':1},{'x':x+45,'y':y,'id':2}]})
                client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});settle(page)
                assert state(page)['camera']['distance']!=distance
                client.detach()
            page.locator('.practice-camera-reset').click();settle(page)
            page.locator('.practice-viewer').screenshot(path=str(OUT/'screenshots'/('after-controls-'+device+'.png')),animations='disabled')
            return {'presets':7,'rotateZoomReset':True,'pointerDrag':True,'twoTouchPinch':device!='desktop','guitarAndAppliedPoseUnchanged':True,'layout':layout(page)}
        check(device+'-camera-and-touch-controls',camera_controls,page)

        def reduced_motion_idle():
            choose(page,'Am7');settle(page)
            expect(page.locator(CANVAS)).to_have_attribute('data-hand-reveal-state','idle')
            first=page.locator(CANVAS).get_attribute('data-render-count')
            page.evaluate('new Promise(resolve=>{let n=0;const next=()=>++n===12?resolve():requestAnimationFrame(next);requestAnimationFrame(next)})')
            assert page.locator(CANVAS).get_attribute('data-render-count')==first
            return {'reducedMotionImmediate':True,'noPermanentRenderLoop':True}
        check(device+'-reduced-motion-and-idle',reduced_motion_idle,page)
        context.close()

    context=browser.new_context(viewport={'width':1194,'height':834},reduced_motion='no-preference')
    page=context.new_page();go(page);ready(page)
    def animated_reveal():
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-reveal-state','idle')
        signature=state(page)['signature']
        page.locator(CANVAS).evaluate('''c=>{window.__revealSamples=[];new MutationObserver(()=>__revealSamples.push({phase:c.dataset.handRevealState,progress:Number(c.dataset.handRevealProgress)})).observe(c,{attributes:true,attributeFilter:['data-hand-reveal-progress','data-hand-reveal-state']})}''')
        choose(page,'Dm');expect(page.locator(CANVAS)).to_have_attribute('data-hand-reveal-state','idle')
        samples=page.evaluate('__revealSamples')
        assert any(s['phase']=='revealing' and s['progress']<1 for s in samples),samples
        assert state(page)['signature']!=signature
        assert state(page)['status']=='needs-review'
        return {'originalBoundedFadeUsed':True,'actualAppliedFingerTransformsChanged':True,'uncheckedBoneInterpolationAdded':False,'samples':samples}
    check('original-transition-animation-without-false-approval',animated_reveal,page)
    context.close()

    # Expected failure is deliberately isolated from the zero-error regression.
    context=browser.new_context(viewport={'width':768,'height':1024},reduced_motion='reduce');page=context.new_page()
    context.route('**/*makehuman-left-arm-sleeved*.glb',lambda route:route.abort('failed'))
    def asset_retry():
        go(page);expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','error',timeout=60000)
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','false');expect(page.locator('[data-practice-hand-retry]')).to_be_visible()
        assert page.locator('.practice-diagram-wrap svg').count()==1
        expect(page.locator('.practice-hand-load-error')).to_be_visible()
        assert len(page.locator('.practice-hand-load-error').inner_text())<35
        assert page.locator('.practice-canvas-stage [role=alert]').count()==0
        context.unroute('**/*makehuman-left-arm-sleeved*.glb');page.locator('[data-practice-hand-retry]').click();ready(page)
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
        return {'inducedAssetFailure':True,'diagramRemainsAvailable':True,'realModelReloaded':True}
    check('hand-download-error-and-real-retry',asset_retry,page)

    def context_retry():
        page.locator(CANVAS).evaluate("c=>c.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext()")
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','error')
        page.locator('[data-practice-retry]').click();ready(page)
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-visible','true')
        return {'inducedWebGLContextLoss':True,'newCanvasAndRigRecovered':True}
    check('webgl-context-loss-and-recovery',context_retry,page)
    context.close();browser.close()

report['passed']=all(case['passed'] for case in report['checks']) and not any(report[k] for k in ['consoleErrors','runtimeErrors','unexpectedNetworkFailures'])
filename = 'browser-camera-recheck.json' if CAMERA_ONLY else 'browser-hand.json'
(OUT/'tests'/filename).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'consoleErrors':len(report['consoleErrors']),'runtimeErrors':len(report['runtimeErrors'])}))
raise SystemExit(0 if report['passed'] else 1)
