"""Actual screenshots after scrolling/decode of native lazy images; no DOM/image substitution."""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import subprocess,os,signal,time,urllib.request,json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/yamaha-import/tests/screenshots';OUT.mkdir(exist_ok=True);BASE='http://127.0.0.1:5435'
report={'physicalIPadSafariTested':False,'captures':[],'errors':[],'method':'Scroll actual native lazy images into view; wait for original decode and opacity=1, then return to top. No DOM alteration or compositing.'}
def capture(page,name):
 for im in page.locator('main img').all():
  im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()');expect(im).to_have_css('opacity','1')
 page.evaluate('document.fonts.ready');page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/name),full_page=True,animations='disabled');report['captures'].append({'file':name,'url':page.url,'width':page.viewport_size['width'],'height':page.viewport_size['height']});print('SHOT',name,flush=True)
def go(page,path):
 page.goto(BASE+path,wait_until='networkidle');expect(page.locator('main h1')).to_be_visible()
with (OUT/'server.txt').open('w') as log:
 server=subprocess.Popen(['npm','run','dev:yamaha-preview','--','--host','0.0.0.0','--port','5435','--strictPort'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  for _ in range(100):
   if server.poll() is not None:raise RuntimeError('Capture preview server failed to start')
   try:
    with urllib.request.urlopen(BASE,timeout=1) as r:
     if r.status==200:break
   except OSError:pass
   time.sleep(.1)
  else:raise RuntimeError('Capture preview not ready')
  with sync_playwright() as p:
   for engine,viewports in [('chromium',[('desktop',1440,1000)]),('webkit',[('tablet',768,1024),('mobile',390,844)])]:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) if engine=='chromium' else p.webkit.launch()
    for label,w,h in viewports:
     context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce');page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
     go(page,'/guitars?brand=Yamaha');capture(page,f'{engine}-{label}-catalog-1.png')
     if label=='desktop':
      for index in [2,3]:
       page.locator('.catalog-pagination').get_by_role('button',name='หน้าถัดไป',exact=True).click();page.wait_for_load_state('networkidle');capture(page,f'{engine}-{label}-catalog-{index}.png')
     go(page,'/guitars/yamaha-fsx830c');capture(page,f'{engine}-{label}-fsx830c.png')
     if label=='desktop':
      go(page,'/guitars/yamaha-fg800')
      for index,color in enumerate(['natural','black','sunburst']):
       page.locator('.gallery-thumbnails button').nth(index).click();capture(page,f'{engine}-{label}-fg800-{color}.png')
      go(page,'/guitars/yamaha-fg820-12');capture(page,f'{engine}-{label}-fg820-12-licensed-primary.png');page.locator('.gallery-thumbnails button').nth(1).click();capture(page,f'{engine}-{label}-fg820-12-uploaded-preview.png')
      go(page,'/guitars/yamaha-fsx830c');page.get_by_role('tab',name='สเปก',exact=True).click();capture(page,f'{engine}-{label}-fsx830c-specifications.png')
     context.close()
    browser.close()
  report['passed']=len(report['captures'])==14 and not report['errors'];(OUT/'captures.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert report['passed'],report
 finally:
  if server.poll() is None:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
