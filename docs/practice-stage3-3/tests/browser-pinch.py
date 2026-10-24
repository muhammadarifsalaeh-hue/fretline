"""Actual Chromium WebGL and synthetic two-contact CDP input; no physical hardware claim."""
from pathlib import Path
from io import BytesIO
import json,math,traceback
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright,expect
OUT=Path('/tmp/fretline-stage33-assets/browser-review/touch');OUT.mkdir(exist_ok=True)
CANVAS='canvas[data-practice-canvas]';BASE='http://127.0.0.1:5430'
report={'engine':'Chromium Linux SwiftShader','url':BASE,'input':'Synthetic two-contact CDP Input.dispatchTouchEvent into actual browser','checks':[],'consoleErrors':[],'runtimeErrors':[],'failedRequests':[],'badResponses':[],'limitations':['Not physical touch hardware.','Not physical iPadOS Safari.','No human hand/arm/black sleeve or C fingering approval.']}
def read(page,attr):return json.loads(page.locator(CANVAS).get_attribute(attr))
def anchors(d):return [(s['number'],s['note'],s['radius'],s['world']) for s in d['strings']]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);report['version']=browser.version
  context=browser.new_context(viewport={'width':768,'height':1024},has_touch=True,locale='th-TH');page=context.new_page()
  page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None);page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}));page.on('response',lambda r:report['badResponses'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
  page.goto(BASE+'/practice',wait_until='networkidle');expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=60000);canvas=page.locator(CANVAS);canvas.evaluate('c=>c.scrollIntoView({block:"center",behavior:"instant"})');canvas.focus();page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  before=read(page,'data-camera');model=read(page,'data-practice-projection');canvas.screenshot(path=str(OUT/'chromium-tablet-before-pinch.png'))
  box=canvas.bounding_box();cx,cy=box['x']+box['width']/2,box['y']+box['height']/2
  session=context.new_cdp_session(page)
  def points(d):return [{'id':1,'x':cx-d,'y':cy,'radiusX':3,'radiusY':3},{'id':2,'x':cx+d,'y':cy,'radiusX':3,'radiusY':3}]
  session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':points(30)})
  for distance in [35,40,45,50,55,60]:session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':points(distance)})
  session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});session.detach()
  page.wait_for_function('([s,b])=>JSON.parse(document.querySelector(s).dataset.camera).distance<b',arg=[CANVAS,before['distance']]);page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  after=read(page,'data-camera');after_model=read(page,'data-practice-projection');assert after['distance']<before['distance'];assert model['geometrySignature']==after_model['geometrySignature'];assert anchors(model)==anchors(after_model);canvas.screenshot(path=str(OUT/'chromium-tablet-after-pinch.png'))
  a=Image.open(OUT/'chromium-tablet-before-pinch.png').convert('RGB');b=Image.open(OUT/'chromium-tablet-after-pinch.png').convert('RGB');diff=ImageChops.difference(a,b);count=sum(1 for pixel in diff.get_flattened_data() if max(pixel)>3);assert count>100
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');report['checks'].append({'case':'synthetic-two-contact-pinch','passed':True,'beforeCamera':before,'afterCamera':after,'loadedSceneChunks':page.evaluate('performance.getEntriesByType("resource").filter(r=>r.name.includes("practice-three-")).map(r=>r.name)'),'geometrySignature':model['geometrySignature'],'actualWorldStringAnchorsUnchanged':True,'pixelChangeCount':count});browser.close()
except Exception:report['failure']=traceback.format_exc()
report['passed']=bool(report['checks']) and not report.get('failure') and not any(report[k] for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses']);(OUT/'touch-geometry.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
