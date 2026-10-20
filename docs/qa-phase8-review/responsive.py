"""Production screenshots and layout audit at the five requested CSS widths."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json,os
OUT=Path(__file__).parent
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4188')
paths=[('home','/'),('catalog','/guitars'),('detail','/guitars/fender-player-ii-telecaster'),('photo-detail','/guitars/yamaha-fg820-12'),('compare','/compare?ids=yamaha-fg820-12,fender-player-ii-telecaster,ibanez-sr300e,taylor-gs-mini'),('quiz','/find-my-guitar?type=acoustic&step=1'),('quiz-results','/find-my-guitar?type=acoustic&level=intermediate&style=folk&budget=mid&priority=versatile'),('brands','/brands'),('brand-detail','/brands/yamaha'),('wishlist','/wishlist')]
report={'browser':'Chromium on Linux; CSS viewports, not physical Safari/iPad', 'checks':[], 'screenshots':[], 'console_errors':[], 'page_errors':[], 'failed_requests':[], 'broken_images':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
 page=browser.new_page(reduced_motion='reduce')
 page.set_default_timeout(15000)
 page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
 page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
 page.on('requestfailed',lambda r:report['failed_requests'].append({'url':r.url,'error':r.failure}))
 page.goto(BASE,wait_until='networkidle')
 page.evaluate('localStorage.setItem("fretline:wishlist",JSON.stringify(["yamaha-fg820-12","fender-player-ii-telecaster","yamaha-c40"]))')
 for width,height in [(1440,1000),(1024,768),(768,1024),(390,844),(320,800)]:
  page.set_viewport_size({'width':width,'height':height})
  for name,path in paths:
   page.goto(BASE+path,wait_until='networkidle')
   expect(page.locator('main h1')).to_be_visible(timeout=15000)
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   bad=page.locator('img').evaluate_all('(images)=>images.filter(i=>i.complete&&!i.naturalWidth).map(i=>i.currentSrc||i.src)')
   report['broken_images'].extend(bad)
   check={'name':name,'route':path,'width':width,'height':height,'noDocumentOverflow':not overflow,'noBrokenImages':not bad}
   if name=='compare':
    region=page.locator('.compare-table-scroll')
    check['tableScrollContained']=region.evaluate('(el)=>el.scrollWidth>el.clientWidth') if width<1024 else True
   report['checks'].append(check)
   screenshot=f'{name}-{width}.png'
   page.screenshot(path=str(OUT/screenshot),animations='disabled')
   report['screenshots'].append(screenshot)
   print(name,width,'overflow',overflow,'broken images',len(bad),flush=True)
 # Full-page views supplement viewport screenshots for review.
 for name,path,width,height in [('catalog','/guitars',1440,1000),('catalog','/guitars',390,844),('compare',paths[4][1],390,844)]:
  page.set_viewport_size({'width':width,'height':height});page.goto(BASE+path,wait_until='networkidle')
  screenshot=f'{name}-{width}-full.png';page.screenshot(path=str(OUT/screenshot),full_page=True,animations='disabled');report['screenshots'].append(screenshot)
 report['passed']=all(c['noDocumentOverflow'] and c['noBrokenImages'] and c.get('tableScrollContained',True) for c in report['checks']) and not any(report[k] for k in ['console_errors','page_errors','failed_requests'])
 browser.close()
(OUT/'responsive-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
