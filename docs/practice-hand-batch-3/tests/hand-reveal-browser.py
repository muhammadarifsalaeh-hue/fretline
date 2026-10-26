"""Real rendering of a hand-only reveal; no physical chord-path approval.

A browser-local held performance.now clock permits repeatable half-opacity
screenshots on software GPUs. Actual production WebGL, materials and saved bone
poses are unchanged. Separate native-clock and reduced-motion cases also run.
"""
from pathlib import Path
from io import BytesIO
import argparse, hashlib, json, traceback
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
CANVAS='canvas[data-practice-canvas]';REVIEW='[data-practice-hand-review]'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
 return {p.name:sha(p) for pattern in ['practice-three-*.js','hand-poses-*.json','PracticePage-*.js','makehuman-left-arm-sleeved-*.glb'] for p in (ROOT/'dist/assets').glob(pattern)}
start=snapshot()
report={'scope':'Actual WebGL visibility/material reveal and cancellation; no swept bone motion or anatomical approval',
 'checks':[],'consoleErrors':[],'runtimeErrors':[],'networkErrors':[],'productionArtifactSHA256':start,
 'limitations':['Controlled half-opacity captures hold performance.now locally in this test, without altering production sources.','Linux WebKit and Chromium software rendering are not physical iPad Safari or GPU performance measurements.']}

def state(c):
 return c.evaluate('c=>({phase:c.dataset.handRevealState,progress:Number(c.dataset.handRevealProgress),visible:c.dataset.handVisible,review:c.dataset.handReviewMode,signature:c.dataset.handPoseSignature,chord:c.dataset.handChordId,geometry:JSON.parse(c.dataset.practiceProjection).geometrySignature,count:Number(c.dataset.renderCount)})')
def settle(page):page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
def image(c):return Image.open(BytesIO(c.screenshot(timeout=60000))).convert('RGB')
def difference(a,b):
 assert a.size==b.size
 return sum(max(v)>3 for v in ImageChops.difference(a,b).get_flattened_data())
def stable_idle(page,c):
 settle(page);page.wait_for_timeout(250);before=state(c);page.wait_for_timeout(800);after=state(c)
 assert before['count']==after['count'],('Idle must stop rendering',before,after)
 return {'before':before['count'],'after':after['count'],'idleMilliseconds':800}
def hold_clock(page):
 return page.evaluate('''()=>{const original=performance.now.bind(performance);window.__revealNativeNow=original;window.__revealNow=original();performance.now=()=>window.__revealNow;return window.__revealNow;}''')
def advance(page,base,elapsed):
 page.evaluate('value=>window.__revealNow=value',base+elapsed)
 settle(page)
def restore_clock(page):page.evaluate('()=>{if(window.__revealNativeNow){performance.now=window.__revealNativeNow;delete window.__revealNativeNow;delete window.__revealNow;}}')
def ready(page):
 page.goto(args.url.rstrip('/')+'/practice?chord=Em7',wait_until='networkidle')
 c=page.locator(CANVAS);expect(c).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
 page.evaluate('document.fonts.ready');c.scroll_into_view_if_needed();settle(page)
 assert state(c)['visible']=='false'
 return c

with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=None
  try:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
   for motion in ['no-preference','reduce']:
    context=browser.new_context(viewport={'width':1024,'height':900},has_touch=True,reduced_motion=motion,locale='th-TH')
    try:
     page=context.new_page()
     page.on('console',lambda msg,e=engine:report['consoleErrors'].append({'engine':e,'text':msg.text}) if msg.type=='error' else None)
     page.on('pageerror',lambda err,e=engine:report['runtimeErrors'].append({'engine':e,'text':str(err)}))
     page.on('requestfailed',lambda req,e=engine:report['networkErrors'].append({'engine':e,'url':req.url,'error':req.failure}))
     page.on('response',lambda res,e=engine:report['networkErrors'].append({'engine':e,'url':res.url,'status':res.status}) if res.status>=400 else None)
     c=ready(page);hidden=image(c);source=state(c)['signature'];details={}
     if motion=='no-preference':
      # Hold time only for deterministic real half-opacity pixel evidence.
      base=hold_clock(page);page.locator(REVIEW).click();expect(c).to_have_attribute('data-hand-reveal-state','revealing')
      zero=state(c);assert zero['progress']==0 and zero['signature']==source
      advance(page,base,80);expect(c).to_have_attribute('data-hand-reveal-progress','0.5')
      halfway=state(c);mid=image(c)
      c.screenshot(path=str(args.output/(engine+'-controlled-half-reveal.png')),timeout=60000)
      assert halfway['signature']==source and halfway['visible']=='true'
      advance(page,base,160);expect(c).to_have_attribute('data-hand-reveal-state','idle')
      final=state(c);assert final['progress']==1 and final['signature']==source
      final_pixels=image(c);c.screenshot(path=str(args.output/(engine+'-completed-reveal.png')),timeout=60000)
      assert halfway['geometry']==final['geometry'], 'Opacity must not mutate geometry or pressed strings'
      delta=difference(mid,final_pixels);assert delta>100,('Intermediate and final actual WebGL pixels must differ',delta)
      restore_clock(page);details['controlledClock']={'zero':zero,'half':halfway,'final':final,'halfToFinalChangedPixels':delta}
      details['completedIdle']=stable_idle(page,c)
      # A normal native-clock opening must finish, retain its exact pose, and stop.
      page.locator(REVIEW).click();expect(c).to_have_attribute('data-hand-visible','false')
      page.locator(REVIEW).click();expect(c).to_have_attribute('data-hand-reveal-state','idle',timeout=15000)
      assert state(c)['signature']==source and state(c)['progress']==1
      details['nativeClockIdle']=stable_idle(page,c)
      # Chord changes close inspection, including while half-revealed.
      page.locator(REVIEW).click();base=hold_clock(page);page.locator(REVIEW).click();advance(page,base,80)
      expect(c).to_have_attribute('data-hand-reveal-progress','0.5')
      page.locator('[data-practice-chord="Am7"]').click();expect(c).to_have_attribute('data-hand-chord-id','Am7')
      cancelled=state(c);assert cancelled['phase']=='idle' and cancelled['progress']==1 and cancelled['visible']=='false' and cancelled['review']=='false'
      assert cancelled['signature']!=source
      restore_clock(page);details['changeChordCancels']=cancelled;details['cancelledIdle']=stable_idle(page,c)
      # Navigation disposes the in-flight reveal; retained detached canvas must stop.
      base=hold_clock(page);page.locator(REVIEW).click();advance(page,base,80)
      expect(c).to_have_attribute('data-hand-reveal-progress','0.5')
      page.evaluate('selector=>window.__oldPracticeCanvas=document.querySelector(selector)',CANVAS)
      page.locator('.practice-model-note a[href="/guitars"]').click();expect(page.locator('#catalog-search')).to_be_visible()
      assert page.locator(CANVAS).count()==0
      restore_clock(page);before=page.evaluate('Number(window.__oldPracticeCanvas.dataset.renderCount)');page.wait_for_timeout(800)
      after=page.evaluate('Number(window.__oldPracticeCanvas.dataset.renderCount)');assert before==after
      details['navigationDisposesInFlightReveal']={'detachedCanvasFramesBefore':before,'after':after}
     else:
      page.locator(REVIEW).click();shown=state(c)
      assert shown['phase']=='idle' and shown['progress']==1 and shown['visible']=='true' and shown['signature']==source
      settle(page);pixels=image(c);delta=difference(hidden,pixels);assert delta>100
      c.screenshot(path=str(args.output/(engine+'-reduced-motion-immediate.png')),timeout=60000)
      details={'immediate':shown,'changedWebGLPixels':delta,'idle':stable_idle(page,c)}
      page.locator(REVIEW).click();assert state(c)['visible']=='false'
     report['checks'].append({'engine':engine,'browserVersion':browser.version,'motion':motion,'passed':True,'details':details})
     print('PASS',engine,motion,'real hand-only reveal and cancellation',flush=True)
    except Exception:
     failure=traceback.format_exc();report['checks'].append({'engine':engine,'motion':motion,'passed':False,'failure':failure});print('FAIL',engine,motion,failure,flush=True)
    finally:context.close()
  finally:
   if browser:browser.close()
report['buildArtifactsUnchangedDuringRun']=start==snapshot()
report['passed']=len(report['checks'])==4 and all(r['passed'] for r in report['checks']) and report['buildArtifactsUnchangedDuringRun'] and not any(report[k] for k in ['consoleErrors','runtimeErrors','networkErrors'])
(args.output/'hand-reveal-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
