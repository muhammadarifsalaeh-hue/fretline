'''Capture unchanged 82fbe9b before redesign. Chromium emulation, not Safari.'''
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os, traceback

OUT=Path(__file__).resolve().parent/'before'
OUT.mkdir(parents=True,exist_ok=True)
BASE=os.environ.get('FRETLINE_AUDIT_URL','http://127.0.0.1:5192')
ID='yamaha-pacifica-612viifm'
ROUTES={
 'home':'/', 'catalog':'/guitars', 'detail':'/guitars/'+ID,
 'brands':'/brands', 'brand-detail':'/brands/yamaha',
 'compare':'/compare?ids='+ID+',yamaha-fg800',
 'quiz-welcome':'/find-my-guitar', 'quiz-question':'/find-my-guitar?step=2&type=electric',
 'quiz-results':'/find-my-guitar?type=electric&level=intermediate&style=rock&budget=high&priority=versatile',
 'wishlist':'/wishlist'}
report={'baseline':'82fbe9b','browser':'Chromium on Linux; physical Safari/iPad not tested',
        'measurements':[],'screenshots':[],'consoleErrors':[],'runtimeErrors':[],'failedRequests':[]}

def measure(page):
 return page.evaluate('''()=>{
  const visible=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'};
  const describe=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {text:(e.getAttribute('aria-label')||e.textContent).trim().slice(0,100),width:Math.round(r.width*10)/10,height:Math.round(r.height*10)/10,font:s.fontSize,lineHeight:s.lineHeight,tag:e.tagName}};
  return {overflow:document.documentElement.scrollWidth>innerWidth+1,scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,
   h1:[...document.querySelectorAll('h1')].filter(visible).map(describe),
   smallVisibleControls:[...document.querySelectorAll('a,button,input,select')].filter(e=>visible(e)&&e.getBoundingClientRect().top>=0&&e.getBoundingClientRect().bottom<=innerHeight).map(describe).filter(e=>e.width<44||e.height<44),
   smallText:[...document.querySelectorAll('h1,h2,h3,p,label,button,a')].filter(visible).map(describe).filter(e=>parseFloat(e.font)<12).slice(0,60),
   brokenVisibleImages:[...document.images].filter(e=>visible(e)&&e.complete&&e.currentSrc&&e.naturalWidth===0).map(e=>e.currentSrc),
   cards:[...document.querySelectorAll('.catalog-product-card,.guitar-card')].slice(0,12).map(describe),
   internalLinks:[...new Set([...document.querySelectorAll('a[href^="/"]')].map(e=>e.getAttribute('href')))]};}''')

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height,label in [(1440,1000,'desktop'),(768,1024,'tablet'),(390,844,'mobile'),(1024,768,'ipad-landscape'),(320,740,'small-mobile')]:
   for name,route in ROUTES.items():
    context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
    saved=[ID] if name=='wishlist' else []
    context.add_init_script('localStorage.setItem("fretline:compare","[]");localStorage.setItem("fretline:wishlist",'+json.dumps(json.dumps(saved))+');')
    page=context.new_page()
    page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)))
    page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
    page.on('requestfailed',lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}))
    page.goto(BASE+route,wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    page.evaluate('window.scrollTo(0,0);document.activeElement?.blur()')
    metrics=measure(page);metrics.update(route=name,path=route,width=width,height=height)
    report['measurements'].append(metrics)
    if width in [1440,768,390]:
     filename=f'{name}-{label}.png'
     page.screenshot(path=str(OUT/filename),animations='disabled')
     report['screenshots'].append(filename)
     if width==1440 and name in ['home','catalog','detail']:
      filename=f'{name}-{label}-full.png';page.screenshot(path=str(OUT/filename),full_page=True,animations='disabled');report['screenshots'].append(filename)
    print(f'{name} {width}px: overflow={metrics["overflow"]}, smallControls={len(metrics["smallVisibleControls"])}',flush=True)
    context.close()
  for name,route in [('catalog-empty','/guitars?q=unmatched-audit-query-947'),('wishlist-empty','/wishlist'),('compare-empty','/compare')]:
   context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
   page=context.new_page();page.goto(BASE+route,wait_until='networkidle')
   filename=name+'-mobile.png';page.screenshot(path=str(OUT/filename),animations='disabled');report['screenshots'].append(filename)
   metrics=measure(page);metrics.update(route=name,path=route,width=390,height=844);report['measurements'].append(metrics)
   context.close()
  browser.close()
 report['completed']=True
except Exception:
 report['completed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
finally:
 (OUT/'measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['completed'] else 1)
