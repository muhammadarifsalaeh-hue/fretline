"""Stage 3.3 actual-application camera acceptance; never human/arm approval.
Uses actual Three.js diagnostic anchors, independent projection math, live
screenshots and working keyboard/buttons. No source or Canvas substitution.
"""
from pathlib import Path
from io import BytesIO
import argparse, json, math, traceback
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--engine', choices=['chromium', 'webkit'], required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--projection-attribute', default='data-practice-projection')
args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
BASE = args.url.rstrip('/'); CANVAS = 'canvas[data-practice-canvas]'; STATUS = '[data-practice-status]'
VIEWPORTS = [(1440,1000,'desktop'), (1024,768,'tablet-landscape'), (768,1024,'tablet'), (390,844,'mobile'), (320,740,'small-mobile')]
report = {'engine':args.engine, 'url':BASE, 'scope':'Camera/projection only, not hand/arm, sleeve or physical C fingering approval', 'checks':[], 'consoleErrors':[], 'runtimeErrors':[], 'failedRequests':[], 'badResponses':[], 'consoleWarnings':[], 'screenshots':[], 'limitations':['Linux engines, not physical iPadOS Safari.', 'Chromium uses SwiftShader.', 'Direction/angle checks are structural requirements, not a visual-fidelity score.']}

def read(page, attribute):
    raw = page.locator(CANVAS).get_attribute(attribute)
    assert raw, f'Missing actual Three.js diagnostic {attribute}'
    return json.loads(raw)

def camera(page): return read(page, 'data-camera')
def projection(page): return read(page, args.projection_attribute)
def frames(page): page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
def finite(v): return len(v)>=3 and all(isinstance(n,(int,float)) and math.isfinite(n) for n in v)
def near(a,b,tol=2e-5): return len(a)==len(b) and all(abs(x-y)<tol for x,y in zip(a,b))
def subtract(a,b): return [x-y for x,y in zip(a,b)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(v):
    length=math.sqrt(dot(v,v)); assert length>1e-8
    return [n/length for n in v]
def same_camera(a,b):
    return all(near(a[k],b[k]) for k in ['position','target','up']) and abs(a['distance']-b['distance'])<2e-5

def actual_pixels(page):
    page.locator(CANVAS).evaluate('c=>c.scrollIntoView({block:"center",behavior:"instant"})');page.locator(CANVAS).focus(); frames(page)
    return Image.open(BytesIO(page.locator(CANVAS).screenshot())).convert('RGB')

def pixel_change(before, after):
    assert before.size==after.size
    diff=ImageChops.difference(before,after)
    changed=sum(1 for px in diff.get_flattened_data() if max(px)>3)
    assert changed>100, {'reason':'Actual camera must alter more than a focus outline/noise', 'changedPixels':changed}
    return changed

def shot(page,name,canvas=True):
    path=args.output/(name+'.png')
    if canvas:
        page.locator(CANVAS).evaluate('c=>c.scrollIntoView({block:"center",behavior:"instant"})');page.locator(CANVAS).screenshot(path=str(path))
    else: page.screenshot(path=str(path),full_page=True)
    report['screenshots'].append(path.name)

def model_anchors(d):
    # Fresh world anchors, not an allegedly immutable signature alone.
    return [(s['number'],s['radius'],s['world']) for s in d['strings']]

def unchanged_model(before,after):
    assert before['geometrySignature']==after['geometrySignature']
    aa,bb=model_anchors(before),model_anchors(after)
    assert len(aa)==len(bb)
    for a,b in zip(aa,bb):
        assert a[0]==b[0] and abs(a[1]-b[1])<1e-9 and near(a[2],b[2],1e-8)

def same_projection(a,b):
    for key in ['headstock','body','nut']: assert near(a[key],b[key]), (key,a[key],b[key])
    for aa,bb in zip(a['strings'],b['strings']): assert near(aa['ndc'],bb['ndc'])

def independently_project(c,world):
    forward=unit(subtract(c['target'],c['position']))
    right=unit(cross(forward,c['up'])); up=cross(right,forward)
    delta=subtract(world,c['position']); depth=dot(delta,forward)
    assert depth>0, {'reason':'Anchor is behind camera','world':world,'camera':c}
    scale=depth*math.tan(math.radians(c['fov'])/2)
    return [dot(delta,right)/(scale*c['aspect']),dot(delta,up)/scale]

def physical_strings(page):
    d,c=projection(page),camera(page)
    strings=d['strings']
    assert [s['number'] for s in strings]==[6,5,4,3,2,1]
    assert [s['note'] for s in strings]==['E2','A2','D3','G3','B3','E4']
    assert all(strings[i]['ndc'][1]>strings[i+1]['ndc'][1]+1e-5 for i in range(5)), {'reason':'Physical strings must stay E A D G B e from top to bottom','strings':strings}
    assert all(strings[i]['radius']>strings[i+1]['radius']>0 for i in range(5))
    for s in strings:
        assert finite(s['world']) and finite(s['ndc'])
        assert near(independently_project(c,s['world']),s['ndc'][:2],6e-5)
    return {'physicalOrder':['E2','A2','D3','G3','B3','E4'],'independentProjectionMatches':True}

def orientation(page):
    d,c=projection(page),camera(page)
    assert all(finite(c[k]) for k in ['position','target','up'])
    actual_distance=math.sqrt(dot(subtract(c['position'],c['target']),subtract(c['position'],c['target'])))
    assert abs(actual_distance-c['distance'])<2e-4
    head,body,nut=d['headstock'],d['body'],d['nut']
    assert all(finite(v) for v in [head,body,nut])
    assert head[0]>body[0]+.1, {'reason':'Head must be right of body','head':head,'body':body}
    assert head[1]>body[1]+.025, {'reason':'Head must be above body','head':head,'body':body}
    box=page.locator(CANVAS).bounding_box(); dx=(head[0]-body[0])*box['width']/2; dy=(head[1]-body[1])*box['height']/2
    angle=math.degrees(math.atan2(dy,dx)); assert 4<angle<40, {'diagonalDegrees':angle}
    assert all(abs(head[i])<1 for i in [0,1]) and -1<head[2]<1, {'reason':'Headstock center must be visible','head':head}
    assert all(abs(nut[i])<1 for i in [0,1]) and -1<nut[2]<1
    strings=d['strings']
    assert [s['number'] for s in strings]==[6,5,4,3,2,1]
    assert [s['note'] for s in strings]==['E2','A2','D3','G3','B3','E4']
    assert all(finite(s['ndc']) and finite(s['world']) for s in strings)
    assert all(strings[i]['ndc'][1]>strings[i+1]['ndc'][1]+1e-5 for i in range(5)), {'reason':'Rendered order must be E A D G B e','strings':strings}
    assert all(strings[i]['radius']>strings[i+1]['radius']>0 for i in range(5))
    for s in strings:
        assert all(abs(s['ndc'][i])<1 for i in [0,1]) and -1<s['ndc'][2]<1
        expected=independently_project(c,s['world'])
        assert near(expected,s['ndc'][:2],6e-5), {'actualThreeProjection':s['ndc'],'independentProjection':expected,'camera':c}
    assert isinstance(d['geometrySignature'],str) and len(d['geometrySignature'])>=6
    return {'diagonalDegrees':angle,'projection':d,'camera':c}

def changed(page,before):
    page.wait_for_function('([s,old])=>JSON.parse(document.querySelector(s).dataset.camera).position.some((v,i)=>Math.abs(v-old[i])>1e-5)',arg=[CANVAS,before['position']])
    frames(page)

try:
    with sync_playwright() as p:
        browser=(p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']) if args.engine=='chromium' else p.webkit.launch())
        report['browserVersion']=browser.version
        for width,height,label in VIEWPORTS:
            context=browser.new_context(viewport={'width':width,'height':height},has_touch=width<=1024,reduced_motion='reduce',locale='th-TH');page=context.new_page()
            page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
            page.on('console',lambda m:report['consoleWarnings'].append(m.text) if m.type=='warning' else None)
            page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)))
            page.on('requestfailed',lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}))
            page.on('response',lambda r:report['badResponses'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
            try:
                page.goto(BASE+'/practice',wait_until='networkidle');expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=30000);page.evaluate('document.fonts.ready');page.locator(CANVAS).scroll_into_view_if_needed()
                expect(page.locator('[data-camera-preset=\"angle\"]')).to_have_attribute('aria-pressed','true');initial_pixels=actual_pixels(page);assert len(initial_pixels.getcolors(initial_pixels.width*initial_pixels.height) or [])>300;assert page.locator(CANVAS).evaluate('c=>Boolean(c.getContext(\"webgl2\"))');default=orientation(page);initial=default['camera'];initial_projection=default['projection']
                shot(page,f'{args.engine}-{label}-default')
                page.evaluate('document.activeElement?.blur();window.scrollTo({top:0,behavior:"instant"})');shot(page,f'{args.engine}-{label}-page',False)
                workspace=args.output/(f'{args.engine}-{label}-workspace.png');clip=page.locator('.practice-studio').evaluate('e=>{const r=e.getBoundingClientRect();return{x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height}}');page.screenshot(path=str(workspace),full_page=True,clip=clip);report['screenshots'].append(workspace.name)
                page.locator(CANVAS).evaluate('c=>c.scrollIntoView({block:"center",behavior:"instant"})');page.locator(CANVAS).focus()
                page.keyboard.press('ArrowLeft');changed(page,initial);unchanged_model(initial_projection,projection(page));orbit_pixels=pixel_change(initial_pixels,actual_pixels(page))
                before=camera(page);before_pixels=actual_pixels(page);page.keyboard.press('+');changed(page,before);assert camera(page)['distance']<before['distance'];zoom_pixels=pixel_change(before_pixels,actual_pixels(page));unchanged_model(initial_projection,projection(page))
                page.keyboard.press('Home');changed(page,before);reset=orientation(page);assert same_camera(reset['camera'],initial);same_projection(initial_projection,reset['projection']);unchanged_model(initial_projection,reset['projection'])
                presets=[];last_camera=camera(page);last_pixels=actual_pixels(page)
                for name in ['side','back','player']:
                    button=page.locator('[data-camera-preset="'+name+'"]');assert button.count()==1,'Missing working preset '+name
                    button.tap() if width<=1024 else button.click();frames(page);expect(button).to_have_attribute('aria-pressed','true')
                    now=camera(page);assert not same_camera(now,last_camera), {'reason':'Preset cannot be a no-op','preset':name}
                    unchanged_model(initial_projection,projection(page));string_check=physical_strings(page);pixels=actual_pixels(page);delta=pixel_change(last_pixels,pixels);shot(page,f'{args.engine}-{label}-{name}')
                    presets.append({'preset':name,'camera':now,'projection':projection(page),'differentPixels':delta,'strings':string_check});last_camera=now;last_pixels=pixels
                page.locator('[data-camera-preset=\"angle\"]').click();frames(page);expect(page.locator('[data-camera-preset=\"angle\"]')).to_have_attribute('aria-pressed','true');shot(page,f'{args.engine}-{label}-angle-button');physical_strings(page);
                page.get_by_role('button',name='รีเซ็ตกล้อง',exact=True).click();frames(page);final=orientation(page);assert same_camera(final['camera'],initial);same_projection(initial_projection,final['projection']);unchanged_model(initial_projection,final['projection'])
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                report['checks'].append({'case':label,'passed':True,'loadedSceneChunks':page.evaluate('performance.getEntriesByType("resource").filter(r=>r.name.includes("practice-three-")).map(r=>r.name)'),'default':default,'reset':reset,'presets':presets,'orbitDifferentPixels':orbit_pixels,'zoomDifferentPixels':zoom_pixels,'sampledWorldGeometryUnchanged':True})
                print('PASS',args.engine,label,flush=True)
            except Exception:
                try: shot(page,f'{args.engine}-{label}-failure',False)
                except Exception: pass
                report['checks'].append({'case':label,'passed':False,'failure':traceback.format_exc()});print('FAIL',args.engine,label,traceback.format_exc(),flush=True)
            finally: context.close()
        browser.close()
except Exception:
    report['harnessFailure']=traceback.format_exc();print(report['harnessFailure'],flush=True)
finally:
    report['passed']=len(report['checks'])==len(VIEWPORTS) and all(c['passed'] for c in report['checks']) and not report.get('harnessFailure') and not any(report[k] for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses'])
    (args.output/f'camera-orientation-{args.engine}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
