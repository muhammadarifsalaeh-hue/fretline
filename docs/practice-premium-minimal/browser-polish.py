"""Final presentation-only checks: real touch targets, idle rendering, motion and captures."""
from pathlib import Path
import json,traceback
from playwright.sync_api import sync_playwright,expect
OUT=Path(__file__).resolve().parent
BASE='http://127.0.0.1:4198'
report={'checks':[],'errors':[],'physicalIPadSafariTested':False}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 for name,w,h,touch in [('desktop',1440,1000,False),('ipad-landscape',1194,834,True),('ipad-portrait',768,1024,True),('mobile',390,844,True),('small-mobile',320,740,True),('tablet',1024,768,True),('wide-desktop',1920,1080,False)]:
  context=browser.new_context(viewport={'width':w,'height':h},has_touch=touch,reduced_motion='reduce');page=context.new_page()
  page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
  try:
   page.goto(BASE+'/practice?chord=C');page.evaluate('document.fonts.ready');canvas=page.locator('canvas[data-practice-canvas]');expect(canvas).to_have_attribute('data-hand-visible','true',timeout=60000)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   bounds=[]
   for b in page.locator('.practice-control-bar button').all():
    box=b.bounding_box();assert box['x']>=0 and box['x']+box['width']<=w+1
    if touch:assert box['width']>=44 and box['height']>=44,box
    bounds.append(box)
   styles=page.locator('[data-practice-chord=C]').evaluate('n=>({transition:getComputedStyle(n).transitionDuration,animation:getComputedStyle(n).animationName})');assert styles=={'transition':'0s','animation':'none'},styles
   page.locator('[data-practice-markers]').focus();outline=page.locator('[data-practice-markers]').evaluate('n=>getComputedStyle(n).outlineStyle');assert outline not in ['none','hidden']
   page.locator('h1').click();page.evaluate('scrollTo(0,0)');page.wait_for_timeout(400);frames=canvas.get_attribute('data-render-count');page.wait_for_timeout(350);assert canvas.get_attribute('data-render-count')==frames
   page.screenshot(path=str(OUT/'screenshots'/('after-'+name+'.png')),full_page=True,animations='disabled')
   evidence={'viewport':[w,h],'touchTargets':bounds,'reducedMotion':styles,'keyboardFocusOutline':outline,'idleRenderCountStable':True,'fullPage':True}
   report['checks'].append({'name':name+'-final-polish','passed':True,'evidence':evidence});print('PASS',name,flush=True)
  except Exception:
   report['checks'].append({'name':name+'-final-polish','passed':False,'failure':traceback.format_exc()});print('FAIL',name,traceback.format_exc(),flush=True)
  context.close()
 context=browser.new_context(viewport={'width':1194,'height':834},has_touch=True,reduced_motion='no-preference');page=context.new_page()
 try:
  page.goto(BASE+'/practice?chord=C');canvas=page.locator('canvas[data-practice-canvas]');expect(canvas).to_have_attribute('data-hand-visible','true',timeout=60000);first=canvas.get_attribute('data-hand-pose-signature')
  page.locator('[data-practice-chord=Dm]').click();expect(canvas).to_have_attribute('data-hand-chord-id','Dm');expect(canvas).to_have_attribute('data-hand-visible','true');assert first!=canvas.get_attribute('data-hand-pose-signature')
  page.wait_for_timeout(800);frames=canvas.get_attribute('data-render-count');page.wait_for_timeout(350);assert canvas.get_attribute('data-render-count')==frames
  report['checks'].append({'name':'normal-motion-real-hand-change-and-idle','passed':True,'evidence':{'realBoneSignatureChanged':True,'idleAfterTransition':True,'heavyAnimationDependencyAdded':False}});print('PASS normal-motion',flush=True)
 except Exception:report['checks'].append({'name':'normal-motion-real-hand-change-and-idle','passed':False,'failure':traceback.format_exc()});print('FAIL normal-motion',traceback.format_exc(),flush=True)
 context.close();browser.close()
report['passed']=all(r['passed']for r in report['checks'])and not report['errors']
(OUT/'tests/browser-polish.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks'])}));raise SystemExit(0 if report['passed']else 1)
