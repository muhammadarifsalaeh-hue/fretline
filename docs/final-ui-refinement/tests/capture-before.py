from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/final-ui-refinement/tests/before'
report={'baselineCommit':'985d0c4898bb02961d25752d8ad0d2dc2ccd1588','physicalIPadSafariTested':False,'screenshots':[],'errors':[],'observations':[]}
SIZES={'desktop':(1440,1000),'landscape':(1194,834),'tablet':(768,1024),'mobile':(390,844)}
REGIONS=[('home','/','#featured'),('catalog','/guitars','.catalog-heading'),('quiz','/find-my-guitar','.premium-quiz'),('quiz-question','/find-my-guitar?step=1','.quiz-studio-panel'),('compare-empty','/compare?ids=','.pc-workspace'),('compare-selected','/compare?ids=yamaha-fg820-12,martin-d-28','.pc-workspace'),('practice','/practice','.practice-studio')]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
  report.setdefault('browserVersions',{})[engine]=browser.version
  for size,(w,h) in SIZES.items():
   context=browser.new_context(viewport={'width':w,'height':h},has_touch=w<1024,reduced_motion='reduce')
   page=context.new_page(); page.on('pageerror',lambda e:report['errors'].append(str(e)))
   for name,path,selector in REGIONS:
    page.goto('http://127.0.0.1:5488'+path,wait_until='networkidle');page.evaluate('document.fonts.ready')
    el=page.locator(selector);el.wait_for(state='visible')
    for im in el.locator('img').all():
     if im.is_visible():
      im.scroll_into_view_if_needed()
      try: im.evaluate('(i)=>i.decode()')
      except Exception as e: report['errors'].append({'route':path,'image':str(e)})
    if name in ['quiz','catalog']:page.evaluate('scrollTo(0,0)')
    else:el.evaluate('e=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector(".site-header").getBoundingClientRect().height-12)')
    filename=f'{engine}-{size}-{name}.png';page.screenshot(path=str(OUT/filename),animations='disabled')
    report['screenshots'].append(filename)
    report['observations'].append({'engine':engine,'viewport':size,'route':path,**page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,canvas:!!document.querySelector("canvas")})')})
   context.close()
  browser.close()
report['captureCount']=len(report['screenshots'])
(OUT/'capture-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Before actual screenshots:',len(report['screenshots']),'errors:',len(report['errors']))
