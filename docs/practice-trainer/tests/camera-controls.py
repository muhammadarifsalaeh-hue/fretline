"""Exercise every real camera preset/button, including the new full-neck view.

Runs against a frozen production preview. Never certifies hand anatomy or iPad
hardware. Independent physical screen projections and real pixel changes are
checked rather than accepting a changed button label.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import math
import traceback
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright,expect

parser=argparse.ArgumentParser()
parser.add_argument('--url',required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[3]
CANVAS='canvas[data-practice-canvas]'
PRESETS=['front','head','side','back','player','angle','overview']
report={'scope':'Actual seven camera presets, four orbit/zoom buttons, and reset; not anatomical hand approval',
        'url':args.url,'checks':[],'consoleErrors':[],'runtimeErrors':[],'networkErrors':[],
        'limitations':['Linux Chromium/SwiftShader and Linux WebKit are not physical iPad Safari or iPad GPU evidence.']}
def snapshot():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'dist/assets').glob('practice-three-*.js')}
start=snapshot()
def read(page):
    return page.locator(CANVAS).evaluate('c=>({camera:JSON.parse(c.dataset.camera),projection:JSON.parse(c.dataset.practiceProjection),frets:Number(c.dataset.fretCount)})')
def same_camera(a,b):
    return all(abs(x-y)<2e-5 for key in ['position','target','up'] for x,y in zip(a[key],b[key])) and abs(a['distance']-b['distance'])<2e-5

def pixels(page):
    page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    return Image.open(BytesIO(page.locator(CANVAS).screenshot(timeout=60000))).convert('RGB')
def changed(a,b):
    assert a.size==b.size
    delta=ImageChops.difference(a,b)
    count=sum(max(value)>3 for value in delta.get_flattened_data())
    assert count>100,('A real camera control must change rendered pixels',count)
    return count

def physical_default(state):
    projection=state['projection'];head,body=projection['headstock'],projection['body']
    assert head[0]>body[0] and head[1]>body[1]
    strings=projection['strings']
    assert [item['number'] for item in strings]==[6,5,4,3,2,1]
    assert [item['note'] for item in strings]==['E2','A2','D3','G3','B3','E4']
    assert all(strings[i]['radius']>strings[i+1]['radius']>0 for i in range(5))
    assert all(strings[i]['ndc'][1]>strings[i+1]['ndc'][1] for i in range(5))
    assert state['frets']==12

with sync_playwright() as p:
    for engine in ['chromium','webkit']:
        browser=None;context=None
        try:
            browser=(p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch())
            context=browser.new_context(viewport={'width':768,'height':1024},has_touch=True,reduced_motion='reduce',locale='th-TH')
            page=context.new_page()
            page.on('console',lambda msg,engine=engine:report['consoleErrors'].append({'engine':engine,'text':msg.text}) if msg.type=='error' else None)
            page.on('pageerror',lambda error,engine=engine:report['runtimeErrors'].append({'engine':engine,'text':str(error)}))
            page.on('requestfailed',lambda request,engine=engine:report['networkErrors'].append({'engine':engine,'url':request.url,'error':request.failure}))
            page.on('response',lambda response,engine=engine:report['networkErrors'].append({'engine':engine,'url':response.url,'status':response.status}) if response.status>=400 else None)
            page.goto(args.url.rstrip('/')+'/practice',wait_until='networkidle')
            expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=45000)
            expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','ready',timeout=45000)
            page.evaluate('document.fonts.ready');page.locator(CANVAS).scroll_into_view_if_needed()
            initial=read(page);physical_default(initial)
            before=initial;before_pixels=pixels(page);rows=[]
            assert set(page.locator('[data-camera-preset]').evaluate_all('nodes=>nodes.map(n=>n.dataset.cameraPreset)'))==set(PRESETS)
            for preset in PRESETS:
                button=page.locator('[data-camera-preset="'+preset+'"]');button.tap()
                expect(button).to_have_attribute('aria-pressed','true')
                now=read(page);after=pixels(page)
                assert not same_camera(before['camera'],now['camera']),('No-op preset',preset)
                assert now['projection']['geometrySignature']==initial['projection']['geometrySignature']
                count=changed(before_pixels,after)
                if preset=='angle':
                    assert same_camera(initial['camera'],now['camera']);physical_default(now)
                if preset=='overview':
                    physical_default(now)
                    for anchor in ['headstock','nut','body']:
                        assert all(abs(now['projection'][anchor][axis])<1 for axis in [0,1]),('Full-neck frame excludes',anchor,now['projection'][anchor])
                    page.locator(CANVAS).screenshot(path=str(args.output/(engine+'-full-neck.png')),timeout=60000)
                rows.append({'preset':preset,'changedPixels':count,'camera':now['camera']})
                before,before_pixels=now,after
            page.locator(CANVAS).focus();page.keyboard.press('0');after=pixels(page)
            assert same_camera(initial['camera'],read(page)['camera']);changed(before_pixels,after)
            controls=[]
            for label,kind in [('หมุนไปทางซ้าย','rotate'),('หมุนไปทางขวา','rotate'),('ซูมเข้า','in'),('ซูมออก','out')]:
                old=read(page);old_pixels=pixels(page)
                page.get_by_role('button',name=label,exact=True).tap()
                new=read(page);new_pixels=pixels(page)
                assert not same_camera(old['camera'],new['camera']),('No-op camera button',label)
                assert new['projection']['geometrySignature']==initial['projection']['geometrySignature']
                if kind=='in':assert new['camera']['distance']<old['camera']['distance']
                if kind=='out':assert new['camera']['distance']>old['camera']['distance']
                controls.append({'button':label,'changedPixels':changed(old_pixels,new_pixels)})
            page.get_by_role('button',name='รีเซ็ตกล้อง',exact=True).tap();pixels(page)
            reset=read(page);assert same_camera(initial['camera'],reset['camera']);physical_default(reset)
            page.locator(CANVAS).screenshot(path=str(args.output/(engine+'-reset.png')),timeout=60000)
            report['checks'].append({'engine':engine,'browserVersion':browser.version,'passed':True,'viewport':[768,1024],
                                     'presets':rows,'buttons':controls,'keyboardAndButtonReset':True,'fullNeckFrameContainsHeadNutBody':True})
            print('PASS',engine,'all 7 presets, 4 orbit/zoom buttons, keyboard/button reset',flush=True)
        except Exception:
            failure=traceback.format_exc();report['checks'].append({'engine':engine,'passed':False,'failure':failure});print('FAIL',engine,failure,flush=True)
        finally:
            if context:context.close()
            if browser:browser.close()
report['productionSceneSHA256']=start
report['buildArtifactsUnchangedDuringRun']=start==snapshot()
report['passed']=len(report['checks'])==2 and all(row['passed'] for row in report['checks']) and report['buildArtifactsUnchangedDuringRun'] and not any(report[key] for key in ['consoleErrors','runtimeErrors','networkErrors'])
(args.output/'camera-controls.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
